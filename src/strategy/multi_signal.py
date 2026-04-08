"""
I1. Multi-Strategy Signal Aggregator.

여러 전략을 동시에 실행하고, confidence 가중 투표로 최종 신호를 결정한다.
- 과반수 BUY/SELL → 해당 방향 (가중 confidence 평균)
- 동수 또는 충돌 → HOLD
- 단일 전략 → 해당 전략 신호 그대로 반환

Confidence 가중치:
  HIGH=3, MEDIUM=2, LOW=1
"""

import logging
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

logger = logging.getLogger(__name__)

_CONF_WEIGHT = {
    Confidence.HIGH: 3,
    Confidence.MEDIUM: 2,
    Confidence.LOW: 1,
}


class MultiStrategyAggregator:
    """
    복수 전략 신호 집계기.

    사용:
        agg = MultiStrategyAggregator(strategies, weights={"ema_cross": 1.5})
        signal = agg.generate(df)
    """

    def __init__(
        self,
        strategies: list[BaseStrategy],
        weights: Optional[dict[str, float]] = None,
    ) -> None:
        """
        Args:
            strategies: BaseStrategy 리스트
            weights: 전략별 가중치 overrides (없으면 모두 1.0)
        """
        self._strategies = strategies
        self._weights = weights or {}

    def generate(self, df: pd.DataFrame) -> Signal:
        """모든 전략 실행 → 가중 투표 → 최종 Signal 반환."""
        if not self._strategies:
            return self._hold(df, "No strategies configured")

        votes: list[tuple[str, Action, Confidence, float]] = []  # (name, action, conf, weight)

        for strat in self._strategies:
            try:
                sig = strat.generate(df)
                weight = self._weights.get(strat.name, 1.0)
                votes.append((strat.name, sig.action, sig.confidence, weight))
                logger.debug(
                    "MultiAgg: %s → %s (conf=%s, w=%.2f)",
                    strat.name, sig.action.value, sig.confidence.value, weight,
                )
            except Exception as e:
                logger.warning("Strategy %s failed: %s", getattr(strat, "name", "?"), e)

        if not votes:
            return self._hold(df, "All strategies failed")

        return self._aggregate(df, votes)

    def _aggregate(
        self,
        df: pd.DataFrame,
        votes: list[tuple[str, Action, Confidence, float]],
    ) -> Signal:
        buy_score = 0.0
        sell_score = 0.0
        hold_score = 0.0

        for name, action, conf, weight in votes:
            conf_w = _CONF_WEIGHT.get(conf, 1) * weight
            if action == Action.BUY:
                buy_score += conf_w
            elif action == Action.SELL:
                sell_score += conf_w
            else:
                hold_score += conf_w

        total = buy_score + sell_score + hold_score
        n_votes = len(votes)
        names = [v[0] for v in votes]

        last = df.iloc[-2] if len(df) >= 2 else df.iloc[-1]
        entry_price = float(last["close"])

        if buy_score == 0 and sell_score == 0:
            return Signal(
                action=Action.HOLD, confidence=Confidence.LOW,
                strategy="multi_aggregator", entry_price=entry_price,
                reasoning=f"모든 전략 HOLD: {names}",
                invalidation="",
            )

        if buy_score > sell_score:
            ratio = buy_score / total
            conf = Confidence.HIGH if ratio > 0.65 else (Confidence.MEDIUM if ratio > 0.45 else Confidence.LOW)
            return Signal(
                action=Action.BUY, confidence=conf,
                strategy="multi_aggregator", entry_price=entry_price,
                reasoning=(
                    f"집계 BUY (buy={buy_score:.1f} sell={sell_score:.1f} hold={hold_score:.1f}) "
                    f"n={n_votes}: {names}"
                ),
                invalidation="집계 신호 역전 시",
                bull_case=f"buy_score/total={ratio:.2f}",
                bear_case="",
            )

        if sell_score > buy_score:
            ratio = sell_score / total
            conf = Confidence.HIGH if ratio > 0.65 else (Confidence.MEDIUM if ratio > 0.45 else Confidence.LOW)
            return Signal(
                action=Action.SELL, confidence=conf,
                strategy="multi_aggregator", entry_price=entry_price,
                reasoning=(
                    f"집계 SELL (buy={buy_score:.1f} sell={sell_score:.1f} hold={hold_score:.1f}) "
                    f"n={n_votes}: {names}"
                ),
                invalidation="집계 신호 역전 시",
                bull_case="",
                bear_case=f"sell_score/total={ratio:.2f}",
            )

        # 동수
        return Signal(
            action=Action.HOLD, confidence=Confidence.LOW,
            strategy="multi_aggregator", entry_price=entry_price,
            reasoning=f"동점 HOLD (buy={buy_score:.1f} == sell={sell_score:.1f}) n={n_votes}",
            invalidation="",
        )

    @staticmethod
    def _hold(df: pd.DataFrame, reason: str) -> Signal:
        last = df.iloc[-2] if len(df) >= 2 else df.iloc[-1]
        return Signal(
            action=Action.HOLD, confidence=Confidence.LOW,
            strategy="multi_aggregator",
            entry_price=float(last["close"]),
            reasoning=reason, invalidation="",
        )
