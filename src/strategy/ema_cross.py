"""
EMA Cross 전략: EMA20이 EMA50을 상향 돌파 시 BUY, 하향 돌파 시 SELL.
필터:
  - ATR 필터: atr14 > 최근 20봉 평균 atr의 0.8배 (변동성 최소 확보)
  - VWAP 방향 필터: BUY는 close > vwap, SELL은 close < vwap
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class EmaCrossStrategy(BaseStrategy):
    name = "ema_cross"

    def generate(self, df: pd.DataFrame) -> Signal:
        prev = df.iloc[-3]
        last = self._last(df)

        ema20_crossed_up = prev["ema20"] <= prev["ema50"] and last["ema20"] > last["ema50"]
        ema20_crossed_down = prev["ema20"] >= prev["ema50"] and last["ema20"] < last["ema50"]

        rsi = last["rsi14"]
        entry = last["close"]
        atr = last["atr14"]
        vwap = last["vwap"]

        # ATR 필터: 최근 20봉(또는 가용 봉) 평균의 0.8배 이상이어야 진입
        lookback = min(20, len(df) - 1)
        avg_atr = df["atr14"].iloc[-lookback - 1 : -1].mean()
        atr_ok = atr >= avg_atr * 0.8

        # VWAP 방향 필터
        vwap_bull = entry > vwap
        vwap_bear = entry < vwap

        bull_case = (
            f"EMA20 ({last['ema20']:.2f}) > EMA50 ({last['ema50']:.2f}), "
            f"RSI={rsi:.1f}, ATR={atr:.2f}, VWAP={vwap:.2f}"
        )
        bear_case = (
            f"EMA20 ({last['ema20']:.2f}) < EMA50 ({last['ema50']:.2f}), "
            f"RSI={rsi:.1f}, ATR={atr:.2f}, VWAP={vwap:.2f}"
        )

        if ema20_crossed_up and rsi < 70 and atr_ok and vwap_bull:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if rsi > 50 else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"EMA20 crossed above EMA50. RSI={rsi:.1f} not overbought. "
                    f"ATR={atr:.2f} >= {avg_atr * 0.8:.2f}. Close above VWAP."
                ),
                invalidation=f"Close below EMA50 ({last['ema50']:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if ema20_crossed_down and rsi > 30 and atr_ok and vwap_bear:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH if rsi < 50 else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"EMA20 crossed below EMA50. RSI={rsi:.1f} not oversold. "
                    f"ATR={atr:.2f} >= {avg_atr * 0.8:.2f}. Close below VWAP."
                ),
                invalidation=f"Close above EMA50 ({last['ema50']:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        reasons = []
        if ema20_crossed_up or ema20_crossed_down:
            if not atr_ok:
                reasons.append(f"ATR={atr:.2f} below threshold {avg_atr * 0.8:.2f}")
            if ema20_crossed_up and not vwap_bull:
                reasons.append("Close below VWAP (no bull confirmation)")
            if ema20_crossed_down and not vwap_bear:
                reasons.append("Close above VWAP (no bear confirmation)")
        hold_reason = "; ".join(reasons) if reasons else "No EMA crossover detected."

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=entry,
            reasoning=hold_reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
