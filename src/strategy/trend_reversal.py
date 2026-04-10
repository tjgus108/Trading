"""
TrendReversalPatternStrategy: 복합 반전 패턴 감지.

- 조건 1: 20봉 신고점/신저점 (extreme)
- 조건 2: RSI divergence (가격 고점/저점 갱신 + RSI 미갱신)
- 조건 3: 반전 캔들 (close vs open 방향 전환)
- Bearish reversal: high == high.rolling(20).max() AND RSI14 < RSI14.shift(5) AND close < open
- Bullish reversal: low == low.rolling(20).min() AND RSI14 > RSI14.shift(5) AND close > open
- BUY: bullish_reversal
- SELL: bearish_reversal
- confidence: volume > avg_vol * 1.5 AND RSI divergence > 10 → HIGH
- 최소 행: 25
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class TrendReversalPatternStrategy(BaseStrategy):
    name = "trend_reversal"

    def _compute_rsi(self, close: pd.Series, period: int = 14) -> pd.Series:
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
        avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        return 100 - 100 / (1 + rs)

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        high = df["high"]
        low = df["low"]
        close = df["close"]
        open_ = df["open"]
        volume = df["volume"]

        rsi14 = self._compute_rsi(close, 14)
        avg_vol = volume.rolling(20).mean()

        rolling_max_high = high.rolling(20).max()
        rolling_min_low = low.rolling(20).min()

        bearish_reversal = (
            (high == rolling_max_high)
            & (rsi14 < rsi14.shift(5))
            & (close < open_)
        )
        bullish_reversal = (
            (low == rolling_min_low)
            & (rsi14 > rsi14.shift(5))
            & (close > open_)
        )

        rsi_div_magnitude = (rsi14 - rsi14.shift(5)).abs()
        high_volume = volume > avg_vol * 1.5

        result = df.copy()
        result["_rsi14"] = rsi14
        result["_rsi14_shift5"] = rsi14.shift(5)
        result["_bearish_reversal"] = bearish_reversal
        result["_bullish_reversal"] = bullish_reversal
        result["_rsi_div_mag"] = rsi_div_magnitude
        result["_high_volume"] = high_volume
        return result

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 25:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"데이터 부족: {len(df)} < 25",
                invalidation="",
            )

        computed = self._compute(df)
        row = computed.iloc[-2]
        entry = float(df["close"].iloc[-2])

        rsi = row["_rsi14"]
        rsi_prev = row["_rsi14_shift5"]
        bearish = bool(row["_bearish_reversal"])
        bullish = bool(row["_bullish_reversal"])
        rsi_div = float(row["_rsi_div_mag"]) if not pd.isna(row["_rsi_div_mag"]) else 0.0
        high_vol = bool(row["_high_volume"])

        if pd.isna(rsi) or pd.isna(rsi_prev):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="지표 계산 중 NaN 발생.",
                invalidation="",
            )

        is_high_conf = high_vol and rsi_div > 10

        if bullish:
            conf = Confidence.HIGH if is_high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bullish reversal: 20봉 신저점 + RSI divergence({rsi:.1f}>{rsi_prev:.1f}) "
                    f"+ 반전 캔들. RSI_div={rsi_div:.1f}, high_vol={high_vol}."
                ),
                invalidation="저점 갱신 또는 RSI 하락 시 무효.",
                bull_case="극단적 저점에서 RSI divergence 확인, 반전 가능성 높음.",
                bear_case="추세 지속 가능성 존재.",
            )

        if bearish:
            conf = Confidence.HIGH if is_high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bearish reversal: 20봉 신고점 + RSI divergence({rsi:.1f}<{rsi_prev:.1f}) "
                    f"+ 반전 캔들. RSI_div={rsi_div:.1f}, high_vol={high_vol}."
                ),
                invalidation="고점 갱신 또는 RSI 상승 시 무효.",
                bull_case="추세 지속 가능성 존재.",
                bear_case="극단적 고점에서 RSI divergence 확인, 반전 가능성 높음.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"RSI={rsi:.1f}. 반전 패턴 미감지.",
            invalidation="",
        )
