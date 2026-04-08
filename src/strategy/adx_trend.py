"""
ADXTrendStrategy: ADX 기반 추세 강도 전략.
ADX >= 25일 때 +DI/-DI 방향과 EMA50 위치로 BUY/SELL 신호 생성.
ADX < 25 (횡보장)이면 HOLD.
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class ADXTrendStrategy(BaseStrategy):
    name = "adx_trend"

    def __init__(self, period: int = 14, adx_threshold: float = 25.0, adx_high: float = 40.0):
        self.period = period
        self.adx_threshold = adx_threshold
        self.adx_high = adx_high

    def _compute_adx(self, df: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
        """
        Returns (adx, plus_di, minus_di) as pandas Series.
        """
        high = df["high"].values.astype(float)
        low = df["low"].values.astype(float)
        close = df["close"].values.astype(float)
        n = len(high)
        p = self.period

        plus_dm = np.zeros(n)
        minus_dm = np.zeros(n)
        tr = np.zeros(n)

        for i in range(1, n):
            up_move = high[i] - high[i - 1]
            down_move = low[i - 1] - low[i]

            plus_dm[i] = up_move if up_move > 0 and up_move > down_move else 0.0
            minus_dm[i] = down_move if down_move > 0 and down_move > up_move else 0.0

            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1]),
            )

        # Wilder smoothing (14-period)
        def wilder_smooth(arr: np.ndarray) -> np.ndarray:
            smoothed = np.zeros(n)
            smoothed[p] = arr[1: p + 1].sum()
            for i in range(p + 1, n):
                smoothed[i] = smoothed[i - 1] - smoothed[i - 1] / p + arr[i]
            return smoothed

        tr14 = wilder_smooth(tr)
        plus_dm14 = wilder_smooth(plus_dm)
        minus_dm14 = wilder_smooth(minus_dm)

        with np.errstate(divide="ignore", invalid="ignore"):
            plus_di = np.where(tr14 > 0, 100.0 * plus_dm14 / tr14, 0.0)
            minus_di = np.where(tr14 > 0, 100.0 * minus_dm14 / tr14, 0.0)
            dx = np.where(
                (plus_di + minus_di) > 0,
                100.0 * np.abs(plus_di - minus_di) / (plus_di + minus_di),
                0.0,
            )

        # ADX = 14-period EMA of DX (Wilder smoothing)
        adx = np.zeros(n)
        # First ADX value: average of first `p` DX values starting at index p
        start = 2 * p  # need enough DX values
        if start < n:
            adx[start] = dx[p + 1: start + 1].mean()
            for i in range(start + 1, n):
                adx[i] = (adx[i - 1] * (p - 1) + dx[i]) / p

        idx = df.index
        return (
            pd.Series(adx, index=idx),
            pd.Series(plus_di, index=idx),
            pd.Series(minus_di, index=idx),
        )

    def generate(self, df: pd.DataFrame) -> Signal:
        min_rows = 40
        if len(df) < min_rows:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="ADX 계산에 필요한 데이터 부족 (최소 40행).",
                invalidation="",
            )

        adx_s, plus_di_s, minus_di_s = self._compute_adx(df)

        last = self._last(df)  # df.iloc[-2]
        idx = df.index[-2]

        adx_val = float(adx_s.loc[idx])
        plus_di_val = float(plus_di_s.loc[idx])
        minus_di_val = float(minus_di_s.loc[idx])
        close_val = float(last["close"])
        ema50_val = float(last["ema50"])
        entry = close_val

        reasoning_base = (
            f"ADX={adx_val:.1f}, +DI={plus_di_val:.1f}, -DI={minus_di_val:.1f}, "
            f"close={close_val:.4f}, ema50={ema50_val:.4f}"
        )

        if adx_val < self.adx_threshold:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"ADX < {self.adx_threshold} (횡보장, 추세 없음). {reasoning_base}",
                invalidation=f"ADX >= {self.adx_threshold} 돌파 시 재평가.",
            )

        confidence = Confidence.HIGH if adx_val >= self.adx_high else Confidence.MEDIUM

        if plus_di_val > minus_di_val and close_val > ema50_val:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"ADX 강한 상승 추세. {reasoning_base}",
                invalidation="+DI < -DI 또는 close < ema50 전환 시 무효.",
                bull_case="ADX 상승 추세 지속 및 EMA50 상방 유지.",
                bear_case="+DI/-DI 역전 시 추세 반전 위험.",
            )

        if minus_di_val > plus_di_val and close_val < ema50_val:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"ADX 강한 하락 추세. {reasoning_base}",
                invalidation="-DI < +DI 또는 close > ema50 전환 시 무효.",
                bull_case="-DI/+DI 역전 시 추세 반전 가능.",
                bear_case="ADX 하락 추세 지속 및 EMA50 하방 유지.",
            )

        # ADX >= 25이지만 방향과 EMA50이 불일치
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"ADX >= {self.adx_threshold}이나 DI 방향과 EMA50 위치 불일치. {reasoning_base}",
            invalidation="DI 방향과 가격 위치 일치 시 신호 발생.",
        )
