"""
TrendStrengthFilterStrategy: EMA 추세 + ADX 강도 복합 필터 전략.
- ADX 계산: EWM(span=14) 방식
- BUY:  ADX > 20 AND DI+ > DI- AND close > EMA21
- SELL: ADX > 20 AND DI- > DI+ AND close < EMA21
- confidence: ADX > 35 → HIGH, 그 외 MEDIUM
- 최소 행: 30
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_ADX_THRESHOLD = 20.0
_ADX_HIGH = 35.0
_EMA_PERIOD = 21


class TrendStrengthFilterStrategy(BaseStrategy):
    name = "trend_strength_filter"

    def _compute_adx(self, df: pd.DataFrame):
        """EWM 방식 ADX/DI+/DI- 계산."""
        high = df["high"]
        low = df["low"]
        close = df["close"]

        prev_high = high.shift(1)
        prev_low = low.shift(1)
        prev_close = close.shift(1)

        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ], axis=1).max(axis=1)

        up_move = high - prev_high
        down_move = prev_low - low

        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

        atr14 = tr.ewm(span=14, adjust=False).mean()
        plus_di = plus_dm.ewm(span=14, adjust=False).mean() / atr14 * 100
        minus_di = minus_dm.ewm(span=14, adjust=False).mean() / atr14 * 100

        di_sum = plus_di + minus_di
        dx = (plus_di - minus_di).abs() / di_sum.replace(0, float("nan")) * 100
        adx = dx.ewm(span=14, adjust=False).mean()

        return adx, plus_di, minus_di

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            entry = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"데이터 부족 (최소 {_MIN_ROWS}행).",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        adx, plus_di, minus_di = self._compute_adx(df)
        ema21 = df["close"].ewm(span=_EMA_PERIOD, adjust=False).mean()

        last = self._last(df)
        idx = df.index[-2]

        adx_val = float(adx.iloc[-2])
        di_plus = float(plus_di.iloc[-2])
        di_minus = float(minus_di.iloc[-2])
        close_val = float(last["close"])
        ema21_val = float(ema21.iloc[-2])

        reasoning_base = (
            f"ADX={adx_val:.1f}, DI+={di_plus:.1f}, DI-={di_minus:.1f}, "
            f"close={close_val:.4f}, EMA21={ema21_val:.4f}"
        )

        if adx_val <= _ADX_THRESHOLD:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"ADX={adx_val:.1f} <= {_ADX_THRESHOLD} (추세 약함). {reasoning_base}",
                invalidation=f"ADX > {_ADX_THRESHOLD} 돌파 시 재평가.",
                bull_case="",
                bear_case="",
            )

        confidence = Confidence.HIGH if adx_val > _ADX_HIGH else Confidence.MEDIUM

        if di_plus > di_minus and close_val > ema21_val:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"강한 상승 추세. {reasoning_base}",
                invalidation="DI+ < DI- 또는 close < EMA21 전환 시 무효.",
                bull_case=f"ADX={adx_val:.1f} 추세 강도 확인, DI+ 우세.",
                bear_case="ADX 하락 또는 DI 역전 시 추세 반전 위험.",
            )

        if di_minus > di_plus and close_val < ema21_val:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"강한 하락 추세. {reasoning_base}",
                invalidation="DI- < DI+ 또는 close > EMA21 전환 시 무효.",
                bull_case="DI+ 역전 시 반전 가능.",
                bear_case=f"ADX={adx_val:.1f} 하락 추세 강도 확인, DI- 우세.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close_val,
            reasoning=f"ADX 강하나 DI 방향·EMA21 위치 불일치. {reasoning_base}",
            invalidation="DI 방향과 가격 위치 일치 시 신호 발생.",
            bull_case="",
            bear_case="",
        )
