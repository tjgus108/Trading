"""
WickAnalysisStrategy: 꼬리(wick) 분석 기반 방향성 신호.
- 하단 꼬리 우세 → 매수 압력 → BUY
- 상단 꼬리 우세 → 매도 압력 → SELL
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class WickAnalysisStrategy(BaseStrategy):
    name = "wick_analysis"

    MIN_ROWS = 20

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        hold = Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=0.0,
            reasoning="No signal",
            invalidation="",
            bull_case="",
            bear_case="",
        )

        if df is None or len(df) < self.MIN_ROWS:
            hold.reasoning = "데이터 부족"
            return hold

        high = df["high"]
        low = df["low"]
        close = df["close"]
        open_ = df["open"]

        upper_wick = high - close.combine(open_, max)
        lower_wick = close.combine(open_, min) - low
        total_range = high - low + 1e-10

        upper_ratio = upper_wick / total_range
        lower_ratio = lower_wick / total_range

        upper_ma = upper_ratio.rolling(10, min_periods=1).mean()  # noqa: F841
        lower_ma = lower_ratio.rolling(10, min_periods=1).mean()  # noqa: F841

        wick_imbalance = lower_ratio - upper_ratio
        imbalance_ma = wick_imbalance.rolling(5, min_periods=1).mean()

        idx = len(df) - 2
        last = self._last(df)

        wi = float(wick_imbalance.iloc[idx])
        ima = float(imbalance_ma.iloc[idx])
        ur = float(upper_ratio.iloc[idx])
        lr = float(lower_ratio.iloc[idx])

        if pd.isna(wi) or pd.isna(ima) or pd.isna(ur) or pd.isna(lr):
            hold.reasoning = "NaN 값 감지"
            return hold

        entry = float(last["close"])
        hold.entry_price = entry

        bull_case = f"wick_imbalance={wi:.3f}, lower_ratio={lr:.3f}, imbalance_ma={ima:.3f}"
        bear_case = f"wick_imbalance={wi:.3f}, upper_ratio={ur:.3f}, imbalance_ma={ima:.3f}"

        # BUY: 하단 꼬리 우세 (매수 압력)
        if wi > 0.2 and wi > ima and lr > 0.3:
            confidence = Confidence.HIGH if abs(wi) > 0.4 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"하단 꼬리 우세: wick_imbalance={wi:.3f} > 0.2, "
                    f"> imbalance_ma={ima:.3f}, lower_ratio={lr:.3f} > 0.3"
                ),
                invalidation=f"wick_imbalance < 0 또는 lower_ratio < 0.3",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: 상단 꼬리 우세 (매도 압력)
        if wi < -0.2 and wi < ima and ur > 0.3:
            confidence = Confidence.HIGH if abs(wi) > 0.4 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"상단 꼬리 우세: wick_imbalance={wi:.3f} < -0.2, "
                    f"< imbalance_ma={ima:.3f}, upper_ratio={ur:.3f} > 0.3"
                ),
                invalidation=f"wick_imbalance > 0 또는 upper_ratio < 0.3",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        hold.reasoning = (
            f"신호 없음: wick_imbalance={wi:.3f}, imbalance_ma={ima:.3f}, "
            f"upper_ratio={ur:.3f}, lower_ratio={lr:.3f}"
        )
        hold.bull_case = bull_case
        hold.bear_case = bear_case
        return hold
