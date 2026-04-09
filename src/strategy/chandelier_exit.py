"""
ChandelierExit 전략: ATR 기반 동적 스탑 레벨로 추세 전환 감지.

- ATR22 = EWM(True Range, span=22)
- chandelier_long  = highest_high_22 - 3 * ATR22
- chandelier_short = lowest_low_22  + 3 * ATR22
- BUY:  이전봉 short_mode AND 현재봉 long_mode  (숏 → 롱 전환)
- SELL: 이전봉 long_mode  AND 현재봉 short_mode (롱 → 숏 전환)
- confidence: HIGH if 전환폭 > ATR22 * 0.5, MEDIUM 그 외
- 최소 데이터: 30행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class ChandelierExitStrategy(BaseStrategy):
    name = "chandelier_exit"

    def __init__(self, period: int = 22, multiplier: float = 3.0):
        self.period = period
        self.multiplier = multiplier

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        high = df["high"]
        low = df["low"]
        close = df["close"]

        # True Range
        prev_close = close.shift(1)
        tr = pd.concat(
            [
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

        atr = tr.ewm(span=self.period, adjust=False).mean()

        highest_high = high.rolling(self.period).max()
        lowest_low = low.rolling(self.period).min()

        chandelier_long = highest_high - self.multiplier * atr
        chandelier_short = lowest_low + self.multiplier * atr

        long_mode = close > chandelier_long
        short_mode = close < chandelier_short

        result = df.copy()
        result["_atr22"] = atr
        result["_chandelier_long"] = chandelier_long
        result["_chandelier_short"] = chandelier_short
        result["_long_mode"] = long_mode
        result["_short_mode"] = short_mode
        return result

    def generate(self, df: pd.DataFrame) -> Signal:
        min_rows = max(self.period + 2, 30)
        if len(df) < min_rows:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"데이터 부족: {len(df)} < {min_rows}",
                invalidation="",
            )

        computed = self._compute(df)

        # 마지막 완성 캔들 인덱스 = -2, 그 전 = -3
        prev_long = bool(computed["_long_mode"].iloc[-3])
        prev_short = bool(computed["_short_mode"].iloc[-3])
        cur_long = bool(computed["_long_mode"].iloc[-2])
        cur_short = bool(computed["_short_mode"].iloc[-2])

        entry = float(df["close"].iloc[-2])
        atr_val = float(computed["_atr22"].iloc[-2])
        cl_val = float(computed["_chandelier_long"].iloc[-2])
        cs_val = float(computed["_chandelier_short"].iloc[-2])

        # 전환폭 계산
        switch_magnitude = abs(entry - cl_val) if cur_long else abs(cs_val - entry)
        conf = (
            Confidence.HIGH
            if switch_magnitude > atr_val * 0.5
            else Confidence.MEDIUM
        )

        # BUY: 이전봉 short_mode AND 현재봉 long_mode
        if prev_short and cur_long:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Chandelier short→long 전환. "
                    f"CL={cl_val:.4f} ATR={atr_val:.4f}"
                ),
                invalidation=f"close < chandelier_long({cl_val:.4f}) 시 무효.",
                bull_case="22봉 최고점 기반 상단 지지선 돌파 확인.",
                bear_case="전환 실패 가능성 존재.",
            )

        # SELL: 이전봉 long_mode AND 현재봉 short_mode
        if prev_long and cur_short:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Chandelier long→short 전환. "
                    f"CS={cs_val:.4f} ATR={atr_val:.4f}"
                ),
                invalidation=f"close > chandelier_short({cs_val:.4f}) 시 무효.",
                bull_case="전환 실패 가능성 존재.",
                bear_case="22봉 최저점 기반 하단 저항선 하향 이탈 확인.",
            )

        direction = "long" if cur_long else ("short" if cur_short else "neutral")
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"Chandelier {direction} 모드 유지 중. ATR={atr_val:.4f}",
            invalidation="",
        )
