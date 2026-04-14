"""
I1. Multi-Strategy Signal Aggregator.

여러 전략을 동시에 실행하고, confidence 가중 투표로 최종 신호를 결정한다.
- 과반수 BUY/SELL → 해당 방향 (가중 confidence 평균)
- 동수 또는 충돌 → HOLD
- 단일 전략 → 해당 전략 신호 그대로 반환

Confidence 가중치:
  HIGH=3, MEDIUM=2, LOW=1

동적 가중치:
  record_outcome()으로 최근 N개 신호 적중률을 기록하면,
  정적 weights 위에 성과 기반 배율(0.5~2.0)이 추가로 곱해진다.
  데이터가 부족하면(< min_samples) 배율=1.0 (무영향).
"""

import logging
from collections import deque
from typing import Optional, Tuple, List, Dict

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

logger = logging.getLogger(__name__)

_CONF_WEIGHT = {
    Confidence.HIGH: 3,
    Confidence.MEDIUM: 2,
    Confidence.LOW: 1,
}

# 동적 가중치 범위
_PERF_WEIGHT_MIN = 0.5
_PERF_WEIGHT_MAX = 2.0


class MultiStrategyAggregator:
    """
    복수 전략 신호 집계기.

    사용:
        agg = MultiStrategyAggregator(strategies, weights={"ema_cross": 1.5},
                                       perf_window=20)
        signal = agg.generate(df)
        # 거래 결과 반영 (outcome: 1=정답, 0=오답)
        agg.record_outcome("ema_cross", 1)
    """

    MIN_PERF_SAMPLES = 5  # 동적 가중치 활성화 최소 샘플 수

    def __init__(
        self,
        strategies: List[BaseStrategy],
        weights: Optional[Dict[str, float]] = None,
        perf_window: int = 20,
    ) -> None:
        """
        Args:
            strategies: BaseStrategy 리스트
            weights: 전략별 정적 가중치 overrides (없으면 모두 1.0)
            perf_window: 성과 추적 rolling window 크기
        """
        self._strategies = strategies
        self._weights = weights or {}
        self._perf_window = perf_window
        # {strategy_name: deque of 0/1 (0=오답, 1=정답)}
        self._outcomes: Dict[str, deque] = {
            s.name: deque(maxlen=perf_window) for s in strategies
        }

    # ── 성과 기록 ──────────────────────────────────────────────────────────

    def record_outcome(self, strategy_name: str, correct: int) -> None:
        """
        신호 적중 여부 기록.

        Args:
            strategy_name: 전략 이름
            correct: 1=정답(예측 방향과 실제 방향 일치), 0=오답
        """
        if strategy_name in self._outcomes:
            self._outcomes[strategy_name].append(int(bool(correct)))
            logger.debug(
                "MultiAgg outcome: %s correct=%d acc=%.2f",
                strategy_name, correct,
                self._accuracy(strategy_name),
            )

    def _accuracy(self, strategy_name: str) -> float:
        """최근 N개 신호 적중률 반환. 데이터 부족 시 -1.0."""
        hist = list(self._outcomes.get(strategy_name, []))
        if len(hist) < self.MIN_PERF_SAMPLES:
            return -1.0
        return sum(hist) / len(hist)

    def _perf_weight(self, strategy_name: str) -> float:
        """
        성과 기반 동적 배율 계산.

        적중률 → 배율 선형 매핑:
          acc=0.0  → 0.5 (최소)
          acc=0.5  → 1.0 (기준)
          acc=1.0  → 2.0 (최대)
        데이터 부족 시 1.0 (무영향).
        """
        acc = self._accuracy(strategy_name)
        if acc < 0:
            return 1.0
        # acc in [0,1] → perf_weight in [0.5, 2.0]
        # linear: 0.5 + acc * 1.5
        weight = _PERF_WEIGHT_MIN + acc * (_PERF_WEIGHT_MAX - _PERF_WEIGHT_MIN)
        return float(weight)

    def performance_summary(self) -> Dict[str, dict]:
        """전략별 성과 요약 반환."""
        result = {}
        for s in self._strategies:
            acc = self._accuracy(s.name)
            result[s.name] = {
                "accuracy": acc if acc >= 0 else None,
                "samples": len(self._outcomes.get(s.name, [])),
                "perf_weight": self._perf_weight(s.name),
            }
        return result

    def generate(self, df: pd.DataFrame) -> Signal:
        """모든 전략 실행 → 가중 투표 → 최종 Signal 반환."""
        if not self._strategies:
            return self._hold(df, "No strategies configured")

        votes: List[Tuple[str, Action, Confidence, float]] = []  # (name, action, conf, weight)

        for strat in self._strategies:
            try:
                sig = strat.generate(df)
                static_w = self._weights.get(strat.name, 1.0)
                perf_w = self._perf_weight(strat.name)
                weight = static_w * perf_w
                votes.append((strat.name, sig.action, sig.confidence, weight))
                logger.debug(
                    "MultiAgg: %s → %s (conf=%s, static_w=%.2f, perf_w=%.2f, w=%.2f)",
                    strat.name, sig.action.value, sig.confidence.value,
                    static_w, perf_w, weight,
                )
            except Exception as e:
                logger.warning("Strategy %s failed: %s", getattr(strat, "name", "?"), e)

        if not votes:
            return self._hold(df, "All strategies failed")

        return self._aggregate(df, votes)

    def _aggregate(
        self,
        df: pd.DataFrame,
        votes: List[Tuple[str, Action, Confidence, float]],
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
