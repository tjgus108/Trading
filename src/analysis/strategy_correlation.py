"""
J3. Strategy Correlation Matrix.

여러 전략의 신호(Action → +1/0/-1)를 수집하여
Pearson 상관계수 행렬을 계산한다.

높은 양의 상관(>0.7): 전략 중복 → 다각화 효과 없음
높은 음의 상관(<-0.5): 자주 충돌 → 앙상블 HOLD 빈도 높음

사용:
  tracker = SignalCorrelationTracker(strategy_names)
  tracker.record("ema_cross", Action.BUY)
  tracker.record("rsi_div", Action.SELL)
  matrix = tracker.correlation_matrix()
"""

import logging
from collections import defaultdict
from typing import Optional, Tuple, List, Dict

import numpy as np
import pandas as pd

from src.strategy.base import Action

logger = logging.getLogger(__name__)

_ACTION_VALUE = {
    Action.BUY: 1,
    Action.SELL: -1,
    Action.HOLD: 0,
}


class SignalCorrelationTracker:
    """전략별 신호 시계열을 추적하고 상관행렬을 계산."""

    def __init__(self, strategy_names: List[str], window: int = 100) -> None:
        self._names = list(strategy_names)
        self._window = window
        self._signals: Dict[str, List[int]] = defaultdict(list)

    def record(self, strategy_name: str, action: Action) -> None:
        """신호 기록. window 초과 시 오래된 항목 제거."""
        val = _ACTION_VALUE.get(action, 0)
        self._signals[strategy_name].append(val)
        if len(self._signals[strategy_name]) > self._window:
            self._signals[strategy_name].pop(0)

    def record_many(self, signals: Dict[str, Action]) -> None:
        """동시 신호 일괄 기록."""
        for name, action in signals.items():
            self.record(name, action)

    def correlation_matrix(self) -> Optional[pd.DataFrame]:
        """
        상관행렬 반환. 데이터 부족 전략은 제외.
        최소 5개 이상의 공통 데이터 포인트 필요.

        Returns:
            pd.DataFrame (strategy x strategy) | None (데이터 부족)
        """
        # 공통 길이로 정렬
        min_len = min((len(v) for v in self._signals.values()), default=0)
        if min_len < 5:
            logger.debug("SignalCorrelation: insufficient data (min_len=%d)", min_len)
            return None

        data = {
            name: self._signals[name][-min_len:]
            for name in self._signals
            if len(self._signals[name]) >= 5
        }
        if len(data) < 2:
            return None

        df = pd.DataFrame(data)
        corr = df.corr()
        return corr

    def high_correlation_pairs(self, threshold: float = 0.7) -> List[Tuple[str, str, float]]:
        """상관계수 절댓값 > threshold인 전략 쌍 반환."""
        corr = self.correlation_matrix()
        if corr is None:
            return []

        pairs = []
        names = corr.columns.tolist()
        for i, a in enumerate(names):
            for j, b in enumerate(names):
                if j <= i:
                    continue
                val = corr.loc[a, b]
                if abs(val) >= threshold:
                    pairs.append((a, b, float(val)))
        return sorted(pairs, key=lambda x: abs(x[2]), reverse=True)

    def summary(self) -> str:
        """텍스트 요약."""
        corr = self.correlation_matrix()
        if corr is None:
            return "SignalCorrelation: insufficient data"

        high_pairs = self.high_correlation_pairs(threshold=0.7)
        lines = [f"Signal Correlation Matrix ({len(corr.columns)} strategies):"]
        lines.append(corr.round(3).to_string())
        if high_pairs:
            lines.append("\nHigh correlation pairs (|r|≥0.7):")
            for a, b, r in high_pairs:
                lines.append(f"  {a} ↔ {b}: {r:+.3f}")
        return "\n".join(lines)
