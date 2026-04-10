"""
CompositeMomentumStrategy:
- 여러 모멘텀 지표(RSI14, ROC10, MACD방향)를 정규화하여 합성 점수 생성
- BUY: comp_score > 0.65 AND comp_score > comp_ma
- SELL: comp_score < 0.35 AND comp_score < comp_ma
- HOLD: 그 외
- confidence: HIGH(score>0.8 or score<0.2), MEDIUM 그 외
- 최소 데이터: 35행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35
_BUY_THRESHOLD = 0.65
_SELL_THRESHOLD = 0.35
_HIGH_CONF_BUY = 0.8
_HIGH_CONF_SELL = 0.2


class CompositeMomentumStrategy(BaseStrategy):
    name = "composite_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for composite_momentum (need 35 rows)")

        close = df["close"]

        # RSI(14)
        delta = close.diff()
        gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
        rsi14 = 100 - 100 / (1 + gain / loss.replace(0, 1e-10))

        # ROC(10)
        roc10 = close.pct_change(10) * 100

        # Normalization
        rsi_norm = rsi14 / 100

        roc_min = roc10.rolling(20).min()
        roc_max = roc10.rolling(20).max()
        roc_norm = (roc10 - roc_min) / (roc_max - roc_min + 1e-10)

        # MACD direction
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd_dir = (ema12 > ema26).astype(float)

        # Composite score
        comp_score = (rsi_norm + roc_norm + macd_dir) / 3
        comp_ma = comp_score.rolling(5).mean()

        # Signal row is iloc[-2]
        idx = len(df) - 2
        score = comp_score.iloc[idx]
        ma = comp_ma.iloc[idx]
        entry = float(close.iloc[idx])

        # NaN check
        if pd.isna(score) or pd.isna(ma):
            return self._hold(df, "Insufficient data for composite_momentum (NaN in score)")

        context = f"comp_score={score:.4f} comp_ma={ma:.4f}"

        if score > _BUY_THRESHOLD and score > ma:
            confidence = Confidence.HIGH if score > _HIGH_CONF_BUY else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Composite momentum BUY: score={score:.4f}>{_BUY_THRESHOLD}, score>ma({ma:.4f})",
                invalidation=f"comp_score drops below {_BUY_THRESHOLD} or below comp_ma",
                bull_case=context,
                bear_case=context,
            )

        if score < _SELL_THRESHOLD and score < ma:
            confidence = Confidence.HIGH if score < _HIGH_CONF_SELL else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Composite momentum SELL: score={score:.4f}<{_SELL_THRESHOLD}, score<ma({ma:.4f})",
                invalidation=f"comp_score rises above {_SELL_THRESHOLD} or above comp_ma",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: comp_score={score:.4f} in neutral zone", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
