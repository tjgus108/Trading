"""
FractalDimensionStrategy: Fractal Efficiency Ratio 기반 추세 전략.

ER(Efficiency Ratio) 이 높을수록 효율적인 추세 (가격이 지그재그 없이 직선적으로 이동).
er > 0.6 AND er > er_ma AND 상승 → BUY
er > 0.6 AND er > er_ma AND 하락 → SELL
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 20
LOOKBACK = 10


class FractalDimensionStrategy(BaseStrategy):
    name = "fractal_dimension"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last = df.iloc[-1]
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last["close"]),
                reasoning=f"데이터 부족: 최소 {MIN_ROWS}행 필요 (현재 {len(df)}행)",
                invalidation="",
            )

        idx = len(df) - 2
        last = self._last(df)
        entry = float(last["close"])

        close = df["close"]

        # Efficiency Ratio
        direction = (close - close.shift(LOOKBACK)).abs()
        path = close.diff().abs().rolling(LOOKBACK, min_periods=1).sum()
        er = direction / (path + 1e-10)
        er_ma = er.rolling(5, min_periods=1).mean()
        trend_up = close > close.shift(LOOKBACK)

        er_val = float(er.iloc[idx]) if not pd.isna(er.iloc[idx]) else 0.0
        erma_val = float(er_ma.iloc[idx]) if not pd.isna(er_ma.iloc[idx]) else 0.0
        is_trend_up = bool(trend_up.iloc[idx]) if not pd.isna(trend_up.iloc[idx]) else False

        # NaN 체크
        if pd.isna(er.iloc[idx]) or pd.isna(er_ma.iloc[idx]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN 값 존재: 지표 계산 불가",
                invalidation="",
            )

        if er_val > 0.8:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM

        bull_case = (
            f"er={er_val:.4f}, er_ma={erma_val:.4f}, "
            f"trend_up={is_trend_up}, close={entry:.4f}"
        )
        bear_case = bull_case

        efficient_trend = er_val > 0.6 and er_val > erma_val

        if efficient_trend and is_trend_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"효율적 상승 추세: er={er_val:.4f} > 0.6 AND "
                    f"er({er_val:.4f}) > er_ma({erma_val:.4f}) AND trend_up=True"
                ),
                invalidation=f"er < 0.6 또는 er < er_ma 또는 추세 전환",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if efficient_trend and not is_trend_up:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"효율적 하락 추세: er={er_val:.4f} > 0.6 AND "
                    f"er({er_val:.4f}) > er_ma({erma_val:.4f}) AND trend_up=False"
                ),
                invalidation=f"er < 0.6 또는 er < er_ma 또는 추세 전환",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"진입 조건 미충족: er={er_val:.4f}, er_ma={erma_val:.4f}, "
                f"trend_up={is_trend_up}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
