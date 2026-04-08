"""
H2. Adaptive Strategy Selector.

실시간 거래 결과(PnL)를 기반으로 전략별 rolling Sharpe를 추적하고,
성과 비례 가중치로 전략을 선택한다.

Tournament(백테스트 기반)와 달리 라이브 거래 성과를 반영.

사용:
    selector = AdaptiveStrategySelector(strategies, window=20)
    selector.record_pnl("ema_cross", 50.0)
    best = selector.select()
"""

import random
import logging
from collections import deque
from typing import Optional

import numpy as np

from .base import BaseStrategy

logger = logging.getLogger(__name__)


class AdaptiveStrategySelector:
    """Rolling Sharpe 기반 적응형 전략 선택기."""

    MIN_SAMPLES = 5   # Sharpe 계산을 위한 최소 거래 수

    def __init__(
        self,
        strategies: dict[str, BaseStrategy],
        window: int = 20,
    ) -> None:
        """
        Args:
            strategies: {strategy_name: BaseStrategy} 매핑
            window: rolling window 크기 (거래 수)
        """
        self._strategies = strategies
        self._window = window
        self._pnl_history: dict[str, deque] = {
            k: deque(maxlen=window) for k in strategies
        }

    def record_pnl(self, strategy_name: str, pnl: float) -> None:
        """거래 결과 기록. 알 수 없는 전략명은 무시."""
        if strategy_name in self._pnl_history:
            self._pnl_history[strategy_name].append(pnl)
            logger.debug("AdaptiveSelector: %s pnl=%.2f", strategy_name, pnl)

    def sharpe(self, strategy_name: str) -> float:
        """rolling Sharpe 반환 (데이터 부족 시 0.0)."""
        hist = list(self._pnl_history.get(strategy_name, []))
        if len(hist) < self.MIN_SAMPLES:
            return 0.0
        arr = np.array(hist, dtype=float)
        std = arr.std()
        return float(arr.mean() / std) if std > 0 else 0.0

    def select(self) -> BaseStrategy:
        """
        성과 비례 가중치로 전략 선택.
        Sharpe가 모두 0 이하이면 균등 무작위 선택.
        """
        sharpes = {k: max(0.0, self.sharpe(k)) for k in self._strategies}
        total = sum(sharpes.values())

        if total <= 0:
            return random.choice(list(self._strategies.values()))

        # 가중치 비례 확률 선택
        rand = random.uniform(0, total)
        cumulative = 0.0
        for name, s in sharpes.items():
            cumulative += s
            if rand <= cumulative:
                return self._strategies[name]
        return list(self._strategies.values())[-1]

    def best_strategy_name(self) -> str:
        """가장 높은 rolling Sharpe 전략명 반환."""
        if not self._strategies:
            raise ValueError("No strategies registered")
        return max(self._strategies, key=lambda k: self.sharpe(k))

    def summary(self) -> dict[str, float]:
        """전략별 rolling Sharpe dict 반환."""
        return {k: self.sharpe(k) for k in self._strategies}

    def strategy_names(self) -> list[str]:
        return list(self._strategies.keys())

    def add_strategy(self, name: str, strategy: BaseStrategy) -> None:
        """런타임 중 전략 추가."""
        self._strategies[name] = strategy
        if name not in self._pnl_history:
            self._pnl_history[name] = deque(maxlen=self._window)
