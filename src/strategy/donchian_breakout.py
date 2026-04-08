"""
Donchian Channel Breakout 전략: 20봉 최고가 돌파 시 BUY, 최저가 하향 돌파 시 SELL.
43.8% APR 사례에서 사용된 전략. 단순하지만 트렌드 추종에 강함.

개선사항:
- 볼륨 확인 필터: 브레이크아웃 시 볼륨 > 20봉 평균의 1.5배 → HIGH confidence 부여
- ATR 이격 필터: close가 채널 경계에서 ATR * 0.5 이상 돌파 시 신호 강화
- EMA50 추세 필터: BUY는 close > ema50, SELL은 close < ema50 조건으로 confidence 상향
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class DonchianBreakoutStrategy(BaseStrategy):
    name = "donchian_breakout"

    def generate(self, df: pd.DataFrame) -> Signal:
        prev = df.iloc[-3]
        last = self._last(df)

        broke_high = prev["close"] <= prev["donchian_high"] and last["close"] > last["donchian_high"]
        broke_low = prev["close"] >= prev["donchian_low"] and last["close"] < last["donchian_low"]

        entry = last["close"]
        rsi = last["rsi14"]
        atr = last["atr14"]

        # --- 볼륨 필터 ---
        vol_window = df["volume"].iloc[-21:-1]
        avg_vol = vol_window.mean() if len(vol_window) > 0 else 0.0
        vol_surge = avg_vol > 0 and last["volume"] >= avg_vol * 1.5

        # --- ATR 이격 필터 ---
        atr_breakout_high = last["close"] - last["donchian_high"] >= atr * 0.5
        atr_breakout_low = last["donchian_low"] - last["close"] >= atr * 0.5

        # --- EMA50 추세 필터 ---
        ema50 = last.get("ema50", entry)
        trend_bull = entry > ema50
        trend_bear = entry < ema50

        bull_case = (
            f"Price ({entry:.2f}) broke above 20-bar high ({last['donchian_high']:.2f}). "
            f"ATR={atr:.2f}, RSI={rsi:.1f}, VolSurge={vol_surge}, ATRBreak={atr_breakout_high}"
        )
        bear_case = (
            f"Price ({entry:.2f}) broke below 20-bar low ({last['donchian_low']:.2f}). "
            f"ATR={atr:.2f}, RSI={rsi:.1f}, VolSurge={vol_surge}, ATRBreak={atr_breakout_low}"
        )

        if broke_high and rsi < 80:
            # HIGH confidence: RSI < 70 + (볼륨 급증 OR ATR 이격) + EMA50 상향
            strong_signal = (vol_surge or atr_breakout_high) and trend_bull
            if rsi < 70 and strong_signal:
                conf = Confidence.HIGH
            elif rsi < 70:
                conf = Confidence.MEDIUM
            else:
                conf = Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Breakout above Donchian high {last['donchian_high']:.2f}. RSI={rsi:.1f}. "
                    f"VolSurge={vol_surge}, ATRBreak={atr_breakout_high}, EMA50Trend={trend_bull}."
                ),
                invalidation=f"Close back below Donchian high ({last['donchian_high']:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if broke_low and rsi > 20:
            # HIGH confidence: RSI > 30 + (볼륨 급증 OR ATR 이격) + EMA50 하향
            strong_signal = (vol_surge or atr_breakout_low) and trend_bear
            if rsi > 30 and strong_signal:
                conf = Confidence.HIGH
            elif rsi > 30:
                conf = Confidence.MEDIUM
            else:
                conf = Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Breakdown below Donchian low {last['donchian_low']:.2f}. RSI={rsi:.1f}. "
                    f"VolSurge={vol_surge}, ATRBreak={atr_breakout_low}, EMA50Trend={trend_bear}."
                ),
                invalidation=f"Close back above Donchian low ({last['donchian_low']:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=entry,
            reasoning="No Donchian channel breakout.",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
