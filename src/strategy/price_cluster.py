"""
PriceClusterStrategy:
- 최근 50봉의 close 가격을 5개 bin으로 나누기
- 가장 많이 방문한 bin = price cluster
- BUY: close가 cluster 하단 이탈 후 복귀 (cluster bounce)
- SELL: close가 cluster 상단 돌파 후 복귀
- confidence: 빈도 > 평균의 2배 이상 → HIGH
- 최소 데이터: 55행
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 55
_CLOSE_WINDOW = 50
_N_BINS = 5
_HIGH_CONF_FREQ_MULT = 2.0


def _find_cluster(
    closes: pd.Series,
    n_bins: int = _N_BINS,
) -> Tuple[float, float, float, int, float]:
    """
    closes를 n_bins로 나누어 최빈 bin의 (low, high, center, count, avg_count)를 반환.
    """
    price_min = float(closes.min())
    price_max = float(closes.max())

    if price_max == price_min:
        center = price_min
        return center, center, center, len(closes), float(len(closes))

    bin_width = (price_max - price_min) / n_bins
    counts = [0] * n_bins

    for c in closes:
        idx = int((c - price_min) / bin_width)
        if idx >= n_bins:
            idx = n_bins - 1
        counts[idx] += 1

    max_count = max(counts)
    best_bin = counts.index(max_count)
    avg_count = float(sum(counts)) / n_bins

    cluster_low = price_min + best_bin * bin_width
    cluster_high = price_min + (best_bin + 1) * bin_width
    cluster_center = (cluster_low + cluster_high) / 2.0

    return cluster_low, cluster_high, cluster_center, max_count, avg_count


class PriceClusterStrategy(BaseStrategy):
    name = "price_cluster"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        curr_close = float(last["close"])

        completed = df.iloc[:-1]

        # 신호봉 직전봉 = completed.iloc[-2]
        if len(completed) < 2:
            return self._hold(df, "Not enough completed candles")
        prev_close = float(completed.iloc[-2]["close"])

        # cluster 계산용 50봉 (신호봉 제외)
        window_closes = completed["close"].iloc[-_CLOSE_WINDOW:]

        cluster_low, cluster_high, cluster_center, max_count, avg_count = _find_cluster(window_closes)

        context = (
            f"close={curr_close:.4f} prev={prev_close:.4f} "
            f"cluster=[{cluster_low:.4f}, {cluster_high:.4f}] center={cluster_center:.4f} "
            f"count={max_count} avg={avg_count:.1f}"
        )

        confidence = (
            Confidence.HIGH
            if max_count >= avg_count * _HIGH_CONF_FREQ_MULT
            else Confidence.MEDIUM
        )

        # BUY: 이전 봉이 cluster_low 아래, 현재 봉이 cluster_low 이상 (반등 복귀)
        if prev_close < cluster_low and curr_close >= cluster_low:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"Cluster bounce BUY: {context}",
                invalidation=f"close < cluster_low={cluster_low:.4f}",
                bull_case=f"Price cluster 하단 반등, {context}",
                bear_case=f"Cluster 하향 이탈 지속 시 하락",
            )

        # SELL: 이전 봉이 cluster_high 위, 현재 봉이 cluster_high 이하 (돌파 후 복귀)
        if prev_close > cluster_high and curr_close <= cluster_high:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"Cluster rejection SELL: {context}",
                invalidation=f"close > cluster_high={cluster_high:.4f}",
                bull_case=f"Cluster 상향 재돌파 시 상승",
                bear_case=f"Price cluster 상단 저항, {context}",
            )

        return self._hold(df, f"No cluster signal: {context}")

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
