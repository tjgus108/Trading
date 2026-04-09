"""
Mass Index 전략:
- 고저 범위의 EMA 비율로 추세 전환 포착 (기간=25)
- Reversal Bulge: Mass Index > 27 → < 26.5 로 하향 시 추세 전환
- BUY: bulge 하향 + close > ema50
- SELL: bulge 하향 + close < ema50
- Confidence: HIGH if 이전 Mass Index > 27.5, MEDIUM if > 27
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 40
_EMA_PERIOD = 9
_MI_PERIOD = 25
_BULGE_HIGH = 27.0
_BULGE_LOW = 26.5
_HIGH_CONF_THRESHOLD = 27.5


def _calc_mass_index(df: pd.DataFrame) -> pd.Series:
    """Mass Index 계산."""
    hl = df["high"] - df["low"]
    ema9 = hl.ewm(span=_EMA_PERIOD, adjust=False).mean()
    ema9_ema9 = ema9.ewm(span=_EMA_PERIOD, adjust=False).mean()
    # 0 나누기 방지
    ratio = ema9 / ema9_ema9.replace(0, float("nan"))
    mi = ratio.rolling(window=_MI_PERIOD).sum()
    return mi


class MassIndexStrategy(BaseStrategy):
    name = "mass_index"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2  # 마지막 완성 캔들
        last = df.iloc[idx]
        close = float(last["close"])
        ema50 = float(last["ema50"])

        mi = _calc_mass_index(df)
        mi_now = float(mi.iloc[idx])
        mi_prev = float(mi.iloc[idx - 1])

        bull_case = f"Mass Index prev={mi_prev:.3f}, now={mi_now:.3f}, close={close:.4f}, ema50={ema50:.4f}"
        bear_case = bull_case

        # Reversal Bulge: 이전 > 27 (팽창) → 현재 < 26.5 (수축)
        is_bulge_reversal = (mi_prev > _BULGE_HIGH) and (mi_now < _BULGE_LOW)

        if not is_bulge_reversal:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Reversal Bulge 미발생 (MI prev={mi_prev:.3f}, now={mi_now:.3f})",
                invalidation="",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # Confidence 결정
        if mi_prev > _HIGH_CONF_THRESHOLD:
            conf = Confidence.HIGH
        else:
            conf = Confidence.MEDIUM

        # BUY: bulge 하향 + close > ema50
        if close > ema50:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Mass Index Reversal Bulge BUY: MI {mi_prev:.3f}→{mi_now:.3f}, close > ema50",
                invalidation=f"Close below ema50 {ema50:.4f}",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: bulge 하향 + close < ema50
        if close < ema50:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Mass Index Reversal Bulge SELL: MI {mi_prev:.3f}→{mi_now:.3f}, close < ema50",
                invalidation=f"Close above ema50 {ema50:.4f}",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # close == ema50 (이론상 드묾)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning="Reversal Bulge 발생, 방향 불명확 (close == ema50)",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
