"""
PriceDivergenceIndexStrategy:
- RSI + OBV 와 가격 간의 divergence를 합산한 인덱스 기반 신호
- Bullish: 가격 하락 + RSI 상승 + OBV 상승 → BUY
- Bearish: 가격 상승 + RSI 하락 + OBV 하락 → SELL
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_LOOKBACK = 10


class PriceDivergenceIndexStrategy(BaseStrategy):
    name = "price_divergence_index"

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

        close = df["close"]
        volume = df["volume"]

        # RSI(14)
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14, min_periods=1).mean()
        loss = (-delta.clip(upper=0)).rolling(14, min_periods=1).mean()
        rsi = 100 - 100 / (1 + gain / (loss + 1e-10))

        # OBV
        obv = (volume * (close.diff() > 0).astype(float) * 2 - volume).cumsum()

        # Divergence scores
        price_change = close - close.shift(_LOOKBACK)
        rsi_change = rsi - rsi.shift(_LOOKBACK)
        obv_change = obv - obv.shift(_LOOKBACK)
        obv_norm = obv_change / (volume.rolling(_LOOKBACK, min_periods=1).sum() + 1e-10)

        bull_div_score = (
            ((price_change < 0) & (rsi_change > 0)).astype(int)
            + ((price_change < 0) & (obv_norm > 0)).astype(int)
        )
        bear_div_score = (
            ((price_change > 0) & (rsi_change < 0)).astype(int)
            + ((price_change > 0) & (obv_norm < 0)).astype(int)
        )

        idx = len(df) - 2
        last = self._last(df)
        entry = float(last["close"])

        rsi_val = rsi.iloc[idx]
        bull_score = bull_div_score.iloc[idx]
        bear_score = bear_div_score.iloc[idx]

        # NaN 체크
        if pd.isna(rsi_val) or pd.isna(bull_score) or pd.isna(bear_score):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="지표 NaN",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        bull_case = f"bull_div_score={int(bull_score)}, RSI={rsi_val:.1f}"
        bear_case = f"bear_div_score={int(bear_score)}, RSI={rsi_val:.1f}"

        if bull_score >= 2 and rsi_val < 50:
            conf = Confidence.HIGH if bull_score == 2 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"강한 불리시 다이버전스: bull_div_score={int(bull_score)}, RSI={rsi_val:.1f}",
                invalidation="최근 저점 하향 돌파",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if bear_score >= 2 and rsi_val > 50:
            conf = Confidence.HIGH if bear_score == 2 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"강한 베어리시 다이버전스: bear_div_score={int(bear_score)}, RSI={rsi_val:.1f}",
                invalidation="최근 고점 상향 돌파",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning="다이버전스 없음",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
