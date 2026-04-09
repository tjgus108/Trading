"""
FibRetracementStrategy:
- 최근 50봉의 swing_high, swing_low 계산
- Fibonacci 레벨: 0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%
- 상승 추세 (close > SMA50): close가 38.2%~61.8% 레벨에서 반등 → BUY
- 하락 추세 (close < SMA50): close가 38.2%~61.8% 레벨에서 저항 → SELL
- confidence: 61.8% 레벨 근방 ±0.5% → HIGH, 그 외 → MEDIUM
- 최소 데이터: 55행
"""

from typing import Optional, Tuple

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 55
_FIB_WINDOW = 50
_SMA_PERIOD = 50

_FIB_LEVELS = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
_ZONE_LOW = 0.382
_ZONE_HIGH = 0.618
_GOLDEN_RATIO = 0.618
_GOLDEN_TOLERANCE = 0.005  # ±0.5%
_BOUNCE_WINDOW = 3


def _calc_fibs(swing_low: float, swing_high: float) -> "dict[float, float]":
    """주어진 swing_low/swing_high로 각 Fibonacci 레벨의 가격 계산."""
    rng = swing_high - swing_low
    return {lvl: swing_low + lvl * rng for lvl in _FIB_LEVELS}


class FibRetracementStrategy(BaseStrategy):
    name = "fib_retracement"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        last = self._last(df)  # df.iloc[-2]
        close = float(last["close"])

        # SMA50 계산 (진행 중 봉 제외: df.iloc[:-1])
        completed = df.iloc[:-1]
        sma50 = float(completed["close"].iloc[-_SMA_PERIOD:].mean())

        # 최근 50봉 swing high/low
        window = completed.iloc[-_FIB_WINDOW:]
        swing_high = float(window["high"].max() if "high" in df.columns else window["close"].max())
        swing_low = float(window["low"].min() if "low" in df.columns else window["close"].min())

        rng = swing_high - swing_low
        if rng == 0:
            return self._hold(df, "No price range in window")

        fibs = _calc_fibs(swing_low, swing_high)
        fib_38 = fibs[0.382]
        fib_62 = fibs[0.618]

        uptrend = close > sma50

        # 최근 3봉 (완성봉 기준 -4:-1, 마지막이 신호봉 -2)
        recent = completed.iloc[-_BOUNCE_WINDOW:]
        recent_closes = list(recent["close"])

        in_zone = fib_38 <= close <= fib_62

        # 61.8% (황금비율) 근방 여부
        golden_price = fibs[0.618]
        near_golden = abs(close - golden_price) / golden_price <= _GOLDEN_TOLERANCE

        context = (
            f"close={close:.4f} sma50={sma50:.4f} "
            f"fib38={fib_38:.4f} fib62={fib_62:.4f} "
            f"swing_low={swing_low:.4f} swing_high={swing_high:.4f}"
        )

        if uptrend:
            # 상승 추세에서 피보나치 되돌림 후 반등: close가 존 안에 있고 최근 봉이 반등 중
            if in_zone and len(recent_closes) >= 2 and recent_closes[-1] > recent_closes[-2]:
                confidence = Confidence.HIGH if near_golden else Confidence.MEDIUM
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=f"상승추세 피보나치 되돌림 반등: {context}",
                    invalidation=f"close < fib_38={fib_38:.4f}",
                    bull_case=f"Fib 38.2%-61.8% 지지 후 반등, {context}",
                    bear_case=f"SMA50 하향 이탈 시 추세 전환",
                )
        else:
            # 하락 추세에서 피보나치 저항: close가 존 안에 있고 최근 봉이 하락 중
            if in_zone and len(recent_closes) >= 2 and recent_closes[-1] < recent_closes[-2]:
                confidence = Confidence.HIGH if near_golden else Confidence.MEDIUM
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=f"하락추세 피보나치 저항: {context}",
                    invalidation=f"close > fib_62={fib_62:.4f}",
                    bull_case=f"SMA50 상향 돌파 시 추세 전환",
                    bear_case=f"Fib 38.2%-61.8% 저항, {context}",
                )

        return self._hold(df, f"No Fib signal: {context}")

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        if len(df) < 2:
            entry = 0.0
        else:
            last = self._last(df) if len(df) >= 2 else df.iloc[-1]
            entry = float(last["close"])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
