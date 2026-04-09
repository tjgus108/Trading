"""
ATR Trailing Stop Strategy: ATR 기반 트레일링 스탑 추세 전략.

- Trailing Stop (상승): close - ATR14 * 2.0
- Trailing Stop (하락): close + ATR14 * 2.0
- 추세 판단: EMA50 기울기 (현재 vs 5봉 전)
- BUY: EMA50 상승 AND close > EMA50 AND trailing stop 상승 중
- SELL: EMA50 하락 AND close < EMA50 AND trailing stop 하락 중
- HIGH: close > EMA50 * 1.01 (1% 이상 위), MEDIUM otherwise
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class ATRTrailingStrategy(BaseStrategy):
    name = "atr_trailing"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 20:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="Not enough data (need 20+ bars).",
                invalidation="",
            )

        idx = len(df) - 2
        atr = df["atr14"]
        trail_bull = df["close"] - atr * 2.0
        trail_bear = df["close"] + atr * 2.0

        close_now = float(df["close"].iloc[idx])
        ema50_now = float(df["ema50"].iloc[idx])
        ema50_prev5 = float(df["ema50"].iloc[idx - 5])
        trail_bull_now = float(trail_bull.iloc[idx])
        trail_bull_prev = float(trail_bull.iloc[idx - 1])
        trail_bear_now = float(trail_bear.iloc[idx])
        trail_bear_prev = float(trail_bear.iloc[idx - 1])

        trend_up = ema50_now > ema50_prev5
        trend_down = ema50_now < ema50_prev5
        trail_rising = trail_bull_now > trail_bull_prev
        trail_falling = trail_bear_now < trail_bear_prev

        entry = close_now

        if trend_up and close_now > ema50_now and trail_rising:
            conf = Confidence.HIGH if close_now > ema50_now * 1.01 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"ATR Trailing BUY: EMA50 rising ({ema50_prev5:.4f}→{ema50_now:.4f}), "
                    f"close ({close_now:.4f}) > EMA50 ({ema50_now:.4f}), "
                    f"trail_bull rising ({trail_bull_prev:.4f}→{trail_bull_now:.4f})."
                ),
                invalidation=f"Close below trailing stop ({trail_bull_now:.4f}) or EMA50 turns down.",
                bull_case=f"Uptrend intact. Trail stop={trail_bull_now:.4f} rising.",
                bear_case=f"Trail stop reversal or EMA50 slope turns negative.",
            )

        if trend_down and close_now < ema50_now and trail_falling:
            conf = Confidence.HIGH if close_now < ema50_now * 0.99 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"ATR Trailing SELL: EMA50 falling ({ema50_prev5:.4f}→{ema50_now:.4f}), "
                    f"close ({close_now:.4f}) < EMA50 ({ema50_now:.4f}), "
                    f"trail_bear falling ({trail_bear_prev:.4f}→{trail_bear_now:.4f})."
                ),
                invalidation=f"Close above trailing stop ({trail_bear_now:.4f}) or EMA50 turns up.",
                bull_case=f"EMA50 slope reversal or price reclaim above EMA50.",
                bear_case=f"Downtrend intact. Trail stop={trail_bear_now:.4f} falling.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"No ATR trailing signal. trend_up={trend_up}, trend_down={trend_down}, "
                f"close_vs_ema50={close_now - ema50_now:.4f}, "
                f"trail_rising={trail_rising}, trail_falling={trail_falling}."
            ),
            invalidation="",
            bull_case=f"EMA50 turns up and close > EMA50 with rising trail stop.",
            bear_case=f"EMA50 turns down and close < EMA50 with falling trail stop.",
        )
