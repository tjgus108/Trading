"""
ROCDivergenceStrategy: 가격과 ROC(Rate of Change) 사이의 divergence 전략.

- Bullish divergence BUY: 가격 새 저점 + ROC는 새 저점 아님 + ROC 상승 중
- Bearish divergence SELL: 가격 새 고점 + ROC는 새 고점 아님 + ROC 하락 중
- confidence: HIGH if |roc10 - roc10.shift(5)| > roc10.rolling(20).std() else MEDIUM
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


class ROCDivergenceStrategy(BaseStrategy):
    name = "roc_divergence"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data (최소 25행 필요)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2
        close = df["close"]

        roc10 = close.pct_change(10) * 100
        roc10_ma = roc10.rolling(5).mean()  # noqa: F841 (계산은 하되 직접 사용 안 함)
        price_high10 = close.rolling(10).max()
        price_low10 = close.rolling(10).min()
        roc_high10 = roc10.rolling(10).max()
        roc_low10 = roc10.rolling(10).min()

        roc_now = roc10.iloc[idx]
        roc_prev = roc10.iloc[idx - 1]
        price_now = close.iloc[idx]
        p_low = price_low10.iloc[idx]
        p_high = price_high10.iloc[idx]
        r_low = roc_low10.iloc[idx]
        r_high = roc_high10.iloc[idx]

        # NaN 체크
        if any(
            pd.isna(v) for v in [roc_now, roc_prev, price_now, p_low, p_high, r_low, r_high]
        ):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data (NaN 값 존재)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        entry = float(price_now)

        # confidence 계산
        roc_shift5 = roc10.iloc[idx - 5] if idx >= 5 else float("nan")
        roc_std20 = roc10.rolling(20).std().iloc[idx]
        if pd.isna(roc_shift5) or pd.isna(roc_std20) or roc_std20 == 0:
            conf = Confidence.MEDIUM
        else:
            conf = (
                Confidence.HIGH
                if abs(float(roc_now) - float(roc_shift5)) > float(roc_std20)
                else Confidence.MEDIUM
            )

        # Bullish divergence BUY
        bullish = (
            float(price_now) <= float(p_low)
            and float(roc_now) > float(r_low) * 0.9
            and float(roc_now) > float(roc_prev)
        )
        if bullish:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bullish divergence: 가격 새 저점({price_now:.2f}<={p_low:.2f}) "
                    f"but ROC({roc_now:.2f}) > roc_low({r_low:.2f})*0.9, ROC 상승 중"
                ),
                invalidation="가격이 저점 아래로 추가 하락 시",
                bull_case="ROC 다이버전스 — 하락 모멘텀 약화",
                bear_case="추세 반전 실패 가능",
            )

        # Bearish divergence SELL
        bearish = (
            float(price_now) >= float(p_high)
            and float(roc_now) < float(r_high) * 0.9
            and float(roc_now) < float(roc_prev)
        )
        if bearish:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bearish divergence: 가격 새 고점({price_now:.2f}>={p_high:.2f}) "
                    f"but ROC({roc_now:.2f}) < roc_high({r_high:.2f})*0.9, ROC 하락 중"
                ),
                invalidation="가격이 고점 위로 추가 상승 시",
                bull_case="단순 조정일 수 있음",
                bear_case="ROC 다이버전스 — 상승 모멘텀 약화",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"다이버전스 없음: price={price_now:.2f}, ROC={roc_now:.2f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
