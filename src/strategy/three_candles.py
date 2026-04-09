"""
Three Consecutive Candles 전략:
- Three White Soldiers (BUY): 3연속 양봉 + 각 close 상승 + open이 이전 body 안 + 위꼬리 작음
- Three Black Crows (SELL): 3연속 음봉 + 각 close 하락 + open이 이전 body 안 + 아래꼬리 작음
- confidence: HIGH if 3봉 모두 완벽 조건, MEDIUM if 일부 조건 완화
- 최소 10행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 10


def _is_bullish(c: pd.Series) -> bool:
    return float(c["close"]) > float(c["open"])


def _is_bearish(c: pd.Series) -> bool:
    return float(c["close"]) < float(c["open"])


def _body(c: pd.Series) -> float:
    return abs(float(c["close"]) - float(c["open"]))


def _upper_wick(c: pd.Series) -> float:
    return float(c["high"]) - float(c["close"])


def _lower_wick(c: pd.Series) -> float:
    return float(c["open"]) - float(c["low"])


class ThreeCandlesStrategy(BaseStrategy):
    name = "three_candles"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        c1 = df.iloc[idx - 2]
        c2 = df.iloc[idx - 1]
        c3 = df.iloc[idx]

        close3 = float(c3["close"])

        # Three White Soldiers
        tws_basic = (
            _is_bullish(c1) and _is_bullish(c2) and _is_bullish(c3)
            and float(c3["close"]) > float(c2["close"]) > float(c1["close"])
            and float(c1["open"]) < float(c2["open"]) < float(c1["close"])
            and float(c2["open"]) < float(c3["open"]) < float(c2["close"])
        )

        if tws_basic:
            uw1_ok = _body(c1) > 0 and _upper_wick(c1) < _body(c1) * 0.3
            uw2_ok = _body(c2) > 0 and _upper_wick(c2) < _body(c2) * 0.3
            uw3_ok = _body(c3) > 0 and _upper_wick(c3) < _body(c3) * 0.3
            confidence = Confidence.HIGH if (uw1_ok and uw2_ok and uw3_ok) else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close3,
                reasoning=f"Three White Soldiers: c1_close={float(c1['close']):.2f} c2_close={float(c2['close']):.2f} c3_close={close3:.2f}",
                invalidation=f"Close below c1 open ({float(c1['open']):.2f})",
                bull_case="Three consecutive bullish candles with progressive closes",
                bear_case="",
            )

        # Three Black Crows
        tbc_basic = (
            _is_bearish(c1) and _is_bearish(c2) and _is_bearish(c3)
            and float(c3["close"]) < float(c2["close"]) < float(c1["close"])
            and float(c1["close"]) < float(c2["open"]) < float(c1["open"])
            and float(c2["close"]) < float(c3["open"]) < float(c2["open"])
        )

        if tbc_basic:
            lw1_ok = _body(c1) > 0 and _lower_wick(c1) < _body(c1) * 0.3
            lw2_ok = _body(c2) > 0 and _lower_wick(c2) < _body(c2) * 0.3
            lw3_ok = _body(c3) > 0 and _lower_wick(c3) < _body(c3) * 0.3
            confidence = Confidence.HIGH if (lw1_ok and lw2_ok and lw3_ok) else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close3,
                reasoning=f"Three Black Crows: c1_close={float(c1['close']):.2f} c2_close={float(c2['close']):.2f} c3_close={close3:.2f}",
                invalidation=f"Close above c1 open ({float(c1['open']):.2f})",
                bull_case="",
                bear_case="Three consecutive bearish candles with progressive closes",
            )

        return self._hold(df, f"No three-candle pattern: c1={float(c1['close']):.2f} c2={float(c2['close']):.2f} c3={close3:.2f}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = df.iloc[len(df) - 2] if len(df) >= 2 else df.iloc[-1]
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
