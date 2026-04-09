"""
BOP (Balance of Power) 전략:
- BOP: 매수/매도 세력 균형 측정
- 계산:
  - BOP = (close - open) / (high - low + 1e-10)
  - Smoothed BOP = EMA(BOP, 14)
- BUY:  Smoothed BOP > 0.1 AND 상승 중 (현재 > 이전) AND close > ema50
- SELL: Smoothed BOP < -0.1 AND 하락 중 (현재 < 이전) AND close < ema50
- confidence: HIGH if |Smoothed BOP| > 0.3, MEDIUM otherwise
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


def _calc_bop(df: pd.DataFrame) -> "tuple[float, float]":
    """idx = len(df) - 2 기준 bop_now, bop_prev 계산."""
    idx = len(df) - 2

    bop_raw = (df["close"] - df["open"]) / (df["high"] - df["low"] + 1e-10)
    bop = bop_raw.ewm(span=14, adjust=False).mean()

    bop_now = float(bop.iloc[idx])
    bop_prev = float(bop.iloc[idx - 1])
    return bop_now, bop_prev


class BOPStrategy(BaseStrategy):
    name = "bop"

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

        bop_now, bop_prev = _calc_bop(df)
        entry = float(df["close"].iloc[-2])
        close_now = float(df["close"].iloc[len(df) - 2])
        ema50_now = float(df["ema50"].iloc[len(df) - 2])

        rising = bop_now > bop_prev
        falling = bop_now < bop_prev
        above_ema = close_now > ema50_now
        below_ema = close_now < ema50_now

        is_buy = bop_now > 0.1 and rising and above_ema
        is_sell = bop_now < -0.1 and falling and below_ema

        if is_buy:
            confidence = Confidence.HIGH if abs(bop_now) > 0.3 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"BOP={bop_now:.3f} > 0.1, 상승 중, close({close_now:.2f}) > EMA50({ema50_now:.2f})",
                invalidation="BOP 0.1 하향 이탈 또는 EMA50 하향 이탈 시",
                bull_case=f"매수 세력 우위(BOP={bop_now:.3f}), EMA50 상회",
                bear_case="BOP 반전 시 매도 전환 가능",
            )

        if is_sell:
            confidence = Confidence.HIGH if abs(bop_now) > 0.3 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"BOP={bop_now:.3f} < -0.1, 하락 중, close({close_now:.2f}) < EMA50({ema50_now:.2f})",
                invalidation="BOP -0.1 상향 돌파 또는 EMA50 상향 돌파 시",
                bull_case="매도 세력 소진 후 반등 가능",
                bear_case=f"매도 세력 우위(BOP={bop_now:.3f}), EMA50 하회",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"BOP={bop_now:.3f} — 조건 미충족",
            invalidation="BOP 임계값 돌파 시 재평가",
        )
