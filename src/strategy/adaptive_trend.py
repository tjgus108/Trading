"""
AdaptiveTrendStrategy: 시장 변동성에 따라 EMA span을 조정하는 적응형 추세 전략.

- volatility percentile 기반으로 adaptive_ema span 5~50 범위 동적 조정
- BUY: fast_ema > adaptive_ema > slow_ema AND close > fast_ema
- SELL: fast_ema < adaptive_ema < slow_ema AND close < fast_ema
- confidence: vol_percentile < 0.3 → HIGH (저변동성 추세), 그 외 MEDIUM
- 최소 행: 30
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class AdaptiveTrendStrategy(BaseStrategy):
    name = "adaptive_trend"
    MIN_ROWS = 30

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return self._hold(df, f"데이터 부족: {len(df)} < {self.MIN_ROWS}")

        close = df["close"]

        volatility = close.pct_change(fill_method=None).rolling(20, min_periods=1).std()
        vol_percentile = volatility.rank(pct=True)
        adaptive_span = (5 + (vol_percentile.fillna(0.5) * 45).round()).astype(int)  # 5~50

        adaptive_ema = close.ewm(span=20, adjust=False).mean()
        fast_ema = close.ewm(span=5, adjust=False).mean()
        slow_ema = close.ewm(span=50, adjust=False).mean()

        idx = len(df) - 2
        row = df.iloc[idx]

        c = float(close.iloc[idx])
        fe = float(fast_ema.iloc[idx])
        ae = float(adaptive_ema.iloc[idx])
        se = float(slow_ema.iloc[idx])
        vp = float(vol_percentile.iloc[idx])
        asp = int(adaptive_span.iloc[idx])

        # NaN 체크
        if any(pd.isna(v) for v in [c, fe, ae, se, vp]):
            return self._hold(df, "NaN 값 감지")

        conf = Confidence.HIGH if vp < 0.3 else Confidence.MEDIUM

        bull_case = (
            f"fast_ema={fe:.4f} > adaptive_ema={ae:.4f} > slow_ema={se:.4f}, "
            f"close={c:.4f} > fast_ema={fe:.4f}, vol_pct={vp:.2f}, span={asp}"
        )
        bear_case = (
            f"fast_ema={fe:.4f} < adaptive_ema={ae:.4f} < slow_ema={se:.4f}, "
            f"close={c:.4f} < fast_ema={fe:.4f}, vol_pct={vp:.2f}, span={asp}"
        )

        # BUY: 상승 정렬 + 가격이 fast_ema 위
        if fe > ae and ae > se and c > fe:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"적응형 추세 상승: fast({fe:.4f}) > adaptive({ae:.4f}) > slow({se:.4f}), "
                    f"close({c:.4f}) > fast, vol_pct={vp:.2f}, span={asp}"
                ),
                invalidation=f"fast_ema({fe:.4f}) < adaptive_ema({ae:.4f}) 역전 시 무효",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: 하락 정렬 + 가격이 fast_ema 아래
        if fe < ae and ae < se and c < fe:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"적응형 추세 하락: fast({fe:.4f}) < adaptive({ae:.4f}) < slow({se:.4f}), "
                    f"close({c:.4f}) < fast, vol_pct={vp:.2f}, span={asp}"
                ),
                invalidation=f"fast_ema({fe:.4f}) > adaptive_ema({ae:.4f}) 역전 시 무효",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(
            df,
            f"추세 미정렬: fast={fe:.4f}, adaptive={ae:.4f}, slow={se:.4f}, close={c:.4f}",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = self._last(df)
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
