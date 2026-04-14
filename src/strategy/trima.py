"""
TRIMA (Triangular Moving Average) 전략:
- TRIMA = SMA(SMA(close, 20), 20) — SMA의 SMA, 더 부드러운 이동평균
- BUY:  close가 TRIMA를 상향 크로스 AND 볼륨 증가 (현재 > 20봉 평균)
- SELL: close가 TRIMA를 하향 크로스 AND 볼륨 증가
- confidence: HIGH if 이격률 > 1%, MEDIUM otherwise
- 최소 데이터: 45행
"""

import math

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 45
_PERIOD = 20
_HIGH_CONF_GAP = 0.01  # 1% 이격률


def _calc_trima(df: pd.DataFrame) -> "Tuple[float, float, float, float, bool, bool, bool]":
    """idx = len(df) - 2 기준 TRIMA 관련 값 계산."""
    period = _PERIOD
    idx = len(df) - 2

    trima = df["close"].rolling(period).mean().rolling(period).mean()
    trima_now = float(trima.iloc[idx])
    trima_prev = float(trima.iloc[idx - 1])
    close_now = float(df["close"].iloc[idx])
    close_prev = float(df["close"].iloc[idx - 1])

    cross_up = close_prev <= trima_prev and close_now > trima_now
    cross_down = close_prev >= trima_prev and close_now < trima_now

    avg_vol = float(df["volume"].iloc[idx - period: idx].mean())
    vol_surge = float(df["volume"].iloc[idx]) > avg_vol

    return trima_now, trima_prev, close_now, close_prev, cross_up, cross_down, vol_surge


class TRIMAStrategy(BaseStrategy):
    name = "trima"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-2]),
                reasoning=f"데이터 부족: {len(df)} < {_MIN_ROWS}",
                invalidation="데이터 충분 시 재평가",
            )

        trima_now, trima_prev, close_now, close_prev, cross_up, cross_down, vol_surge = _calc_trima(df)
        entry = close_now

        # NaN 방어: 지표 계산이 아직 수렴하지 않은 경우
        if any(not math.isfinite(v) for v in (trima_now, trima_prev, close_now, close_prev)):
            return Signal(
                action=Action.HOLD, confidence=Confidence.LOW,
                strategy=self.name, entry_price=entry if math.isfinite(entry) else 0.0,
                reasoning="NaN detected in TRIMA indicators",
                invalidation="지표 수렴 후 재평가",
            )

        # 이격률 계산
        gap_pct = abs(close_now - trima_now) / trima_now if trima_now != 0 else 0.0

        if cross_up and vol_surge:
            confidence = Confidence.HIGH if gap_pct > _HIGH_CONF_GAP else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"TRIMA 상향 크로스(close={close_now:.4f} > TRIMA={trima_now:.4f}) + 볼륨 증가",
                invalidation=f"close < TRIMA({trima_now:.4f}) 재이탈",
                bull_case=f"이격률={gap_pct*100:.2f}%, 볼륨 서지 확인",
                bear_case="크로스 후 되돌림 가능",
            )

        if cross_down and vol_surge:
            confidence = Confidence.HIGH if gap_pct > _HIGH_CONF_GAP else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"TRIMA 하향 크로스(close={close_now:.4f} < TRIMA={trima_now:.4f}) + 볼륨 증가",
                invalidation=f"close > TRIMA({trima_now:.4f}) 재돌파",
                bull_case="하향 후 지지 반등 가능",
                bear_case=f"이격률={gap_pct*100:.2f}%, 볼륨 서지 확인",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"TRIMA={trima_now:.4f}, close={close_now:.4f} — 크로스 또는 볼륨 조건 미충족",
            invalidation="크로스 + 볼륨 동시 충족 시 재평가",
        )
