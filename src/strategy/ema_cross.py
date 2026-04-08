"""
EMA Cross 전략: EMA20이 EMA50을 상향 돌파 시 BUY, 하향 돌파 시 SELL.
필터:
  - ATR 필터: atr14 > 최근 20봉 평균 atr의 0.8배 (변동성 최소 확보)
  - VWAP 방향 필터: BUY는 close > vwap, SELL은 close < vwap

개선 (ema9/ema21 컬럼이 있을 때 추가 활성화):
  - EMA9/21 크로스 확인: 현재 봉에서 크로스 발생 여부 체크
  - 볼륨 필터: 20봉 평균의 1.2배 이상
  - EMA50 방향 필터: close > ema50 (BUY) / close < ema50 (SELL)
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

        # EMA9/21 기반 강화 필터 (컬럼이 존재할 때만 활성화)
        has_ema9_21 = "ema9" in df.columns and "ema21" in df.columns
        enhanced_bull_ok = True
        enhanced_bear_ok = True
        enhanced_info = ""

        if has_ema9_21:
            prev2 = df.iloc[-3]
            # 크로스 확인: 이전 봉에서 반전
            cross_up = (prev2["ema9"] < prev2["ema21"]) and (last["ema9"] > last["ema21"])
            cross_down = (prev2["ema9"] > prev2["ema21"]) and (last["ema9"] < last["ema21"])

            # EMA50 방향 필터
            ema50_bull = entry > last["ema50"]
            ema50_bear = entry < last["ema50"]

            # 볼륨 필터: 20봉 평균의 1.2배 이상
            vol_lookback = min(20, len(df) - 1)
            avg_vol = df["volume"].iloc[-vol_lookback - 1 : -1].mean()
            vol_ok = last["volume"] >= avg_vol * 1.2

            enhanced_bull_ok = cross_up and ema50_bull and vol_ok
            enhanced_bear_ok = cross_down and ema50_bear and vol_ok
            enhanced_info = (
                f" | EMA9={last['ema9']:.2f} EMA21={last['ema21']:.2f}"
                f" Vol={last['volume']:.1f} AvgVol={avg_vol:.1f}"
            )

        bull_case = (
            f"EMA20 ({last['ema20']:.2f}) > EMA50 ({last['ema50']:.2f}), "
            f"RSI={rsi:.1f}, ATR={atr:.2f}, VWAP={vwap:.2f}{enhanced_info}"
        )
        bear_case = (
            f"EMA20 ({last['ema20']:.2f}) < EMA50 ({last['ema50']:.2f}), "
            f"RSI={rsi:.1f}, ATR={atr:.2f}, VWAP={vwap:.2f}{enhanced_info}"
        )

        buy_ok = ema20_crossed_up and rsi < 70 and atr_ok and vwap_bull
        if has_ema9_21:
            buy_ok = buy_ok and enhanced_bull_ok

        if buy_ok:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if rsi > 50 else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"EMA20 crossed above EMA50. RSI={rsi:.1f} not overbought. "
                    f"ATR={atr:.2f} >= {avg_atr * 0.8:.2f}. Close above VWAP."
                    + (f" EMA9/21 cross_up confirmed, vol & EMA50 ok." if has_ema9_21 else "")
                ),
                invalidation=f"Close below EMA50 ({last['ema50']:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        sell_ok = ema20_crossed_down and rsi > 30 and atr_ok and vwap_bear
        if has_ema9_21:
            sell_ok = sell_ok and enhanced_bear_ok

        if sell_ok:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH if rsi < 50 else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"EMA20 crossed below EMA50. RSI={rsi:.1f} not oversold. "
                    f"ATR={atr:.2f} >= {avg_atr * 0.8:.2f}. Close below VWAP."
                    + (f" EMA9/21 cross_down confirmed, vol & EMA50 ok." if has_ema9_21 else "")
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
            if has_ema9_21:
                if ema20_crossed_up and not enhanced_bull_ok:
                    reasons.append("EMA9/21 cross_up or vol/EMA50 filter not met")
                if ema20_crossed_down and not enhanced_bear_ok:
                    reasons.append("EMA9/21 cross_down or vol/EMA50 filter not met")
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
