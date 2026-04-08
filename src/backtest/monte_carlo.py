"""
J1. Monte Carlo 백테스트 시뮬레이터.

수익률 시계열을 n_simulations번 부트스트랩 리샘플링하여
전략 성과 분포를 추정한다.

방법: Block Bootstrap (블록 길이 = block_size 캔들)
- 시계열 의존성 보존을 위해 단순 IID 리샘플 대신 블록 단위 샘플링

출력:
  - 각 시뮬레이션의 최종 누적수익률, Sharpe, MDD 분포
  - 5th/50th/95th percentile 요약

사용:
  mc = MonteCarlo(n_simulations=1000, block_size=20)
  result = mc.run(returns_series)
  print(result.summary())
"""

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class MonteCarloResult:
    n_simulations: int
    final_returns: np.ndarray       # 최종 누적수익률 배열
    sharpes: np.ndarray             # Sharpe 배열
    max_drawdowns: np.ndarray       # MDD 배열 (양수)
    annualization: int

    @property
    def p5_return(self) -> float:
        return float(np.percentile(self.final_returns, 5))

    @property
    def p50_return(self) -> float:
        return float(np.percentile(self.final_returns, 50))

    @property
    def p95_return(self) -> float:
        return float(np.percentile(self.final_returns, 95))

    @property
    def p5_sharpe(self) -> float:
        return float(np.percentile(self.sharpes, 5))

    @property
    def median_sharpe(self) -> float:
        return float(np.percentile(self.sharpes, 50))

    @property
    def median_mdd(self) -> float:
        return float(np.percentile(self.max_drawdowns, 50))

    @property
    def p95_mdd(self) -> float:
        return float(np.percentile(self.max_drawdowns, 95))

    def prob_positive(self) -> float:
        """양의 수익률 확률."""
        return float(np.mean(self.final_returns > 0))

    def summary(self) -> str:
        return (
            f"MonteCarlo(n={self.n_simulations}) | "
            f"Return [p5={self.p5_return:.2%} p50={self.p50_return:.2%} p95={self.p95_return:.2%}] | "
            f"Sharpe [p5={self.p5_sharpe:.2f} p50={self.median_sharpe:.2f}] | "
            f"MDD [p50={self.median_mdd:.2%} p95={self.p95_mdd:.2%}] | "
            f"P(return>0)={self.prob_positive():.1%}"
        )


class MonteCarlo:
    """Block Bootstrap Monte Carlo 시뮬레이터."""

    def __init__(
        self,
        n_simulations: int = 500,
        block_size: int = 20,
        annualization: int = 252 * 24,  # 1h 기준
        risk_free_rate: float = 0.05,
        seed: Optional[int] = None,
    ) -> None:
        self.n_simulations = n_simulations
        self.block_size = block_size
        self.annualization = annualization
        self.risk_free_rate = risk_free_rate
        self._rng = np.random.default_rng(seed)

    def run(self, returns: pd.Series) -> MonteCarloResult:
        """
        Args:
            returns: 거래 수익률 시계열 (per-period, e.g. 0.001 = 0.1%)

        Returns:
            MonteCarloResult
        """
        r = returns.dropna().values.astype(float)
        n = len(r)

        if n < self.block_size:
            logger.warning("MC: data(%d) < block_size(%d), using block_size=1", n, self.block_size)
            self.block_size = 1

        final_returns = np.empty(self.n_simulations)
        sharpes = np.empty(self.n_simulations)
        mdds = np.empty(self.n_simulations)

        for i in range(self.n_simulations):
            sim_r = self._block_bootstrap(r, n)
            final_returns[i] = float(np.prod(1 + sim_r) - 1)
            sharpes[i] = self._sharpe(sim_r)
            mdds[i] = self._max_drawdown(sim_r)

        return MonteCarloResult(
            n_simulations=self.n_simulations,
            final_returns=final_returns,
            sharpes=sharpes,
            max_drawdowns=mdds,
            annualization=self.annualization,
        )

    def _block_bootstrap(self, r: np.ndarray, target_len: int) -> np.ndarray:
        """Block bootstrap 리샘플링."""
        n = len(r)
        blocks = []
        while sum(len(b) for b in blocks) < target_len:
            start = self._rng.integers(0, max(1, n - self.block_size + 1))
            block = r[start: start + self.block_size]
            blocks.append(block)
        combined = np.concatenate(blocks)[:target_len]
        return combined

    def _sharpe(self, r: np.ndarray) -> float:
        ann_r = r.mean() * self.annualization
        ann_v = r.std() * np.sqrt(self.annualization)
        if ann_v <= 0:
            return 0.0
        return float((ann_r - self.risk_free_rate) / ann_v)

    @staticmethod
    def _max_drawdown(r: np.ndarray) -> float:
        equity = np.cumprod(1 + r)
        peak = np.maximum.accumulate(equity)
        dd = (peak - equity) / np.where(peak > 0, peak, 1)
        return float(dd.max())
