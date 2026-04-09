"""
전략별 성과 추적 및 순위 매기기.
리서치 기반: 어느 전략이 실제로 수익을 내는지 파악.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time


@dataclass
class StrategyMetrics:
    name: str
    total_trades: int = 0
    winning_trades: int = 0
    total_pnl: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    last_updated: float = field(default_factory=time.time)

    @property
    def win_rate(self) -> float:
        if self.total_trades == 0:
            return 0.0
        return self.winning_trades / self.total_trades

    @property
    def avg_pnl_per_trade(self) -> float:
        if self.total_trades == 0:
            return 0.0
        return self.total_pnl / self.total_trades


class StrategyPerformanceTracker:
    def __init__(self):
        self._metrics: Dict[str, StrategyMetrics] = {}

    def record_trade(self, strategy_name: str, pnl: float, is_win: bool):
        """개별 트레이드 결과 기록"""
        if strategy_name not in self._metrics:
            self._metrics[strategy_name] = StrategyMetrics(name=strategy_name)
        m = self._metrics[strategy_name]
        m.total_trades += 1
        m.total_pnl += pnl
        if is_win:
            m.winning_trades += 1
        m.last_updated = time.time()

    def get_ranking(self, sort_by: str = "total_pnl") -> List[StrategyMetrics]:
        """성과 기준 순위 반환. sort_by: 'total_pnl', 'win_rate', 'avg_pnl_per_trade'"""
        valid = {"total_pnl", "win_rate", "avg_pnl_per_trade"}
        if sort_by not in valid:
            raise ValueError(f"sort_by must be one of {valid}")
        return sorted(
            self._metrics.values(),
            key=lambda m: getattr(m, sort_by),
            reverse=True,
        )

    def get_top_n(self, n: int = 10, sort_by: str = "total_pnl") -> List[StrategyMetrics]:
        """상위 N개 전략 반환"""
        return self.get_ranking(sort_by=sort_by)[:n]

    def get_bottom_n(self, n: int = 10, sort_by: str = "total_pnl") -> List[StrategyMetrics]:
        """하위 N개 전략 (비활성화 후보)"""
        return self.get_ranking(sort_by=sort_by)[-n:]

    def to_dict(self) -> Dict[str, dict]:
        """직렬화"""
        return {
            name: {
                "name": m.name,
                "total_trades": m.total_trades,
                "winning_trades": m.winning_trades,
                "total_pnl": m.total_pnl,
                "max_drawdown": m.max_drawdown,
                "sharpe_ratio": m.sharpe_ratio,
                "last_updated": m.last_updated,
            }
            for name, m in self._metrics.items()
        }

    def from_dict(self, data: Dict[str, dict]):
        """역직렬화"""
        self._metrics = {}
        for name, d in data.items():
            m = StrategyMetrics(
                name=d["name"],
                total_trades=d["total_trades"],
                winning_trades=d["winning_trades"],
                total_pnl=d["total_pnl"],
                max_drawdown=d.get("max_drawdown", 0.0),
                sharpe_ratio=d.get("sharpe_ratio", 0.0),
                last_updated=d.get("last_updated", time.time()),
            )
            self._metrics[name] = m
