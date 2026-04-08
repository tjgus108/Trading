"""
G3. 멀티에셋 포트폴리오 최적화기.

3가지 방법론 (numpy only, scipy 금지):
  1. Mean-Variance (Markowitz): 최대 Sharpe 포트폴리오
  2. Risk Parity: 각 자산의 리스크 기여도 균등화
  3. Equal Weight: 동일 비중 (기준선)

입력: 심볼별 수익률 Series dict → 최적 비중 dict

사용:
  opt = PortfolioOptimizer(method="risk_parity")
  weights = opt.optimize(returns_dict)  # {"BTC": 0.4, "ETH": 0.35, "SOL": 0.25}
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Literal


@dataclass
class OptimizationResult:
    weights: dict[str, float]       # 심볼 → 비중 (합=1.0)
    method: str
    expected_return: float          # 연환산 기대수익률
    expected_volatility: float      # 연환산 변동성
    sharpe_ratio: float

    def summary(self) -> str:
        w_str = ", ".join(f"{s}: {v:.4f}" for s, v in self.weights.items())
        return (
            f"Method: {self.method} | "
            f"Weights: {{{w_str}}} | "
            f"E[R]: {self.expected_return:.4f} | "
            f"Vol: {self.expected_volatility:.4f} | "
            f"Sharpe: {self.sharpe_ratio:.4f}"
        )


class PortfolioOptimizer:
    def __init__(
        self,
        method: Literal["mean_variance", "risk_parity", "equal_weight"] = "risk_parity",
        risk_free_rate: float = 0.05,   # 연 5%
        annualization: int = 252 * 24,  # 1h 기준
        max_weight: float = 0.5,        # 단일 자산 최대 50%
        min_weight: float = 0.05,       # 단일 자산 최소 5%
    ):
        self.method = method
        self.risk_free_rate = risk_free_rate
        self.annualization = annualization
        self.max_weight = max_weight
        self.min_weight = min_weight

    def optimize(self, returns_dict: dict[str, pd.Series]) -> OptimizationResult:
        """심볼별 수익률 Series → 최적 비중. 데이터 1개 또는 부족 시 equal_weight fallback."""
        symbols = list(returns_dict.keys())
        n = len(symbols)

        # fallback: 자산 없음
        if n == 0:
            return OptimizationResult(
                weights={},
                method="equal_weight",
                expected_return=0.0,
                expected_volatility=0.0,
                sharpe_ratio=0.0,
            )

        # fallback: 자산 1개
        if n == 1:
            sym = symbols[0]
            r = returns_dict[sym].dropna()
            ann_r = float(r.mean()) * self.annualization
            ann_v = float(r.std()) * np.sqrt(self.annualization)
            sharpe = (ann_r - self.risk_free_rate) / ann_v if ann_v > 0 else 0.0
            return OptimizationResult(
                weights={sym: 1.0},
                method="equal_weight",
                expected_return=ann_r,
                expected_volatility=ann_v,
                sharpe_ratio=sharpe,
            )

        # 공통 인덱스로 수익률 행렬 구성
        df = pd.DataFrame(returns_dict).dropna()

        # 데이터 부족 시 equal_weight fallback (최소 2개 행 필요)
        if len(df) < 2:
            weights_arr = self._equal_weight(n)
            weights_dict = dict(zip(symbols, weights_arr.tolist()))
            return OptimizationResult(
                weights=weights_dict,
                method="equal_weight",
                expected_return=0.0,
                expected_volatility=0.0,
                sharpe_ratio=0.0,
            )

        returns_matrix = df.values  # shape: (T, n)

        method = self.method
        if method == "mean_variance":
            weights_arr = self._mean_variance(returns_matrix, symbols)
        elif method == "risk_parity":
            weights_arr = self._risk_parity(returns_matrix, symbols)
        else:
            weights_arr = self._equal_weight(n)

        # 포트폴리오 성과 계산
        port_returns = returns_matrix @ weights_arr
        ann_r = float(port_returns.mean()) * self.annualization
        ann_v = float(port_returns.std()) * np.sqrt(self.annualization)
        sharpe = (ann_r - self.risk_free_rate) / ann_v if ann_v > 0 else 0.0

        weights_dict = {sym: float(w) for sym, w in zip(symbols, weights_arr)}

        return OptimizationResult(
            weights=weights_dict,
            method=method,
            expected_return=ann_r,
            expected_volatility=ann_v,
            sharpe_ratio=sharpe,
        )

    def _apply_constraints(self, weights: np.ndarray) -> np.ndarray:
        """min/max clipping 후 반복 재정규화 (수렴 보장)."""
        n = len(weights)
        w = weights.copy()
        for _ in range(50):  # 최대 50회 반복으로 수렴
            total = w.sum()
            if total <= 0:
                return np.ones(n) / n
            w = w / total
            w = np.clip(w, self.min_weight, self.max_weight)
            if np.allclose(w.sum(), 1.0, atol=1e-9) and np.all(w <= self.max_weight + 1e-9):
                break
        total = w.sum()
        w = w / total if total > 0 else np.ones(n) / n
        # 부동소수점 오차 보정
        w = np.clip(w, self.min_weight, self.max_weight)
        return w / w.sum()

    def _mean_variance(self, returns_matrix: np.ndarray, symbols: list) -> np.ndarray:
        """그리드 서치: 1000개 랜덤 포트폴리오 중 최대 Sharpe 선택."""
        T, n = returns_matrix.shape
        per_period_rf = self.risk_free_rate / self.annualization

        best_sharpe = -np.inf
        best_weights = np.ones(n) / n

        rng = np.random.default_rng(42)
        for _ in range(1000):
            raw = rng.random(n)
            w = raw / raw.sum()
            # 제약 적용
            w = self._apply_constraints(w)

            port_r = returns_matrix @ w
            mean_r = port_r.mean()
            std_r = port_r.std()
            if std_r <= 0:
                continue
            sharpe = (mean_r - per_period_rf) / std_r
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_weights = w.copy()

        return best_weights

    def _risk_parity(self, returns_matrix: np.ndarray, symbols: list) -> np.ndarray:
        """Risk Parity: 각 자산 변동성 역수 비중."""
        vols = returns_matrix.std(axis=0)
        # 0 변동성 방지
        vols = np.where(vols <= 0, 1e-8, vols)
        inv_vol = 1.0 / vols
        weights = inv_vol / inv_vol.sum()
        return self._apply_constraints(weights)

    def _equal_weight(self, n: int) -> np.ndarray:
        return np.ones(n) / n
