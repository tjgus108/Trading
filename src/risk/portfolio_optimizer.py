"""
G3. 멀티에셋 포트폴리오 최적화기.

3가지 방법론 (numpy only, scipy 금지):
  1. Mean-Variance (Markowitz): 최대 Sharpe 포트폴리오
  2. Risk Parity: 각 자산의 리스크 기여도 균등화 (iterative)
  3. Equal Weight: 동일 비중 (기준선)

입력: 심볼별 수익률 Series dict → 최적 비중 dict

사용:
  opt = PortfolioOptimizer(method="risk_parity")
  weights = opt.optimize(returns_dict)  # {"BTC": 0.4, "ETH": 0.35, "SOL": 0.25}
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, Literal, Optional


@dataclass
class OptimizationResult:
    weights: Dict[str, float]       # 심볼 → 비중 (합=1.0)
    method: str
    expected_return: float          # 연환산 기대수익률
    expected_volatility: float      # 연환산 변동성
    sharpe_ratio: float
    var_95: float = 0.0             # 일간 95% VaR (손실, 양수)
    cvar_95: float = 0.0            # 일간 95% CVaR / Expected Shortfall

    def summary(self) -> str:
        w_str = ", ".join(f"{s}: {v:.4f}" for s, v in self.weights.items())
        return (
            f"Method: {self.method} | "
            f"Weights: {{{w_str}}} | "
            f"E[R]: {self.expected_return:.4f} | "
            f"Vol: {self.expected_volatility:.4f} | "
            f"Sharpe: {self.sharpe_ratio:.4f} | "
            f"VaR95: {self.var_95:.4f} | "
            f"CVaR95: {self.cvar_95:.4f}"
        )


class PortfolioOptimizer:
    def __init__(
        self,
        method: Literal["mean_variance", "risk_parity", "equal_weight"] = "risk_parity",
        risk_free_rate: float = 0.05,   # 연 5%
        annualization: int = 252 * 24,  # 1h 기준
        max_weight: float = 0.5,        # 단일 자산 최대 50%
        min_weight: float = 0.05,       # 단일 자산 최소 5%
        n_simulations: int = 2000,      # mean_variance 몬테카를로 샘플 수
    ):
        self.method = method
        self.risk_free_rate = risk_free_rate
        self.annualization = annualization
        self.max_weight = max_weight
        self.min_weight = min_weight
        self.n_simulations = n_simulations

    def optimize(self, returns_dict: Dict[str, pd.Series]) -> OptimizationResult:
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
            r = returns_dict[sym].dropna().values
            ann_r = float(r.mean()) * self.annualization
            ann_v = float(r.std()) * np.sqrt(self.annualization)
            sharpe = (ann_r - self.risk_free_rate) / ann_v if ann_v > 0 else 0.0
            var_95, cvar_95 = self._compute_var_cvar(r) if len(r) >= 2 else (0.0, 0.0)
            return OptimizationResult(
                weights={sym: 1.0},
                method="equal_weight",
                expected_return=ann_r,
                expected_volatility=ann_v,
                sharpe_ratio=sharpe,
                var_95=var_95,
                cvar_95=cvar_95,
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

        # VaR / CVaR (95%, 일간, 손실은 양수)
        var_95, cvar_95 = self._compute_var_cvar(port_returns, confidence=0.95)

        weights_dict = {sym: float(w) for sym, w in zip(symbols, weights_arr)}

        return OptimizationResult(
            weights=weights_dict,
            method=method,
            expected_return=ann_r,
            expected_volatility=ann_v,
            sharpe_ratio=sharpe,
            var_95=var_95,
            cvar_95=cvar_95,
        )

    @staticmethod
    def _compute_var_cvar(
        port_returns: np.ndarray, confidence: float = 0.95
    ) -> tuple:
        """VaR과 CVaR 계산 (손실 기준, 양수 반환).

        Args:
            port_returns: 포트폴리오 수익률 배열
            confidence: 신뢰 수준 (0.95 = 95%)

        Returns:
            (var, cvar) — 양수 (손실)
        """
        if len(port_returns) == 0:
            return 0.0, 0.0
        sorted_r = np.sort(port_returns)
        T = len(sorted_r)
        # 하위 (1-confidence) 분위수 인덱스
        cutoff_idx = max(1, int(T * (1 - confidence)))
        # VaR: 5번째 퍼센타일 (cutoff_idx - 1번째 값)
        var = -float(sorted_r[cutoff_idx - 1])
        # CVaR: 하위 cutoff_idx개 수익률의 평균
        cvar = -float(sorted_r[:cutoff_idx].mean())
        return max(0.0, var), max(0.0, cvar)

    def _apply_constraints(self, weights: np.ndarray) -> np.ndarray:
        """min/max 제약을 유지하면서 합=1.0 보장 (iterative projection).
        
        수치 불안정(NaN/inf) 입력 방어: 유효하지 않은 값은 equal_weight로 대체.
        최종 반환 전 합=1, 모든 가중치>=0 강제 검증.
        """
        n = len(weights)
        w = weights.copy()
        # NaN / inf 방어: 수치 불안정 입력은 equal_weight로 대체
        if not np.all(np.isfinite(w)) or w.sum() <= 0:
            return np.ones(n) / n
        for _ in range(500):
            total = w.sum()
            if total <= 0:
                return np.ones(n) / n
            w = w / total
            w_clipped = np.clip(w, self.min_weight, self.max_weight)
            if np.max(np.abs(w_clipped - w)) < 1e-12:
                w = w_clipped
                break
            w = w_clipped
        # 수렴 실패 시: 마지막으로 클리핑 후 정규화를 충분히 반복
        for _ in range(100):
            w = np.clip(w, self.min_weight, self.max_weight)
            total = w.sum()
            if total <= 0:
                return np.ones(n) / n
            w = w / total
            if np.all(w <= self.max_weight + 1e-12) and np.all(w >= self.min_weight - 1e-12):
                break
        # 최종 합=1, 음수 제거 보장
        w = np.clip(w, 0.0, None)
        total = w.sum()
        if total <= 0:
            return np.ones(n) / n
        return w / total

    def _mean_variance(self, returns_matrix: np.ndarray, symbols: list) -> np.ndarray:
        """몬테카를로: n_simulations개 랜덤 포트폴리오 중 최대 Sharpe 선택.

        Dirichlet 분포로 샘플링하여 제약 전 분포를 더 균일하게 탐색.
        """
        T, n = returns_matrix.shape
        per_period_rf = self.risk_free_rate / self.annualization

        best_sharpe = -np.inf
        best_weights = np.ones(n) / n

        rng = np.random.default_rng(42)
        for _ in range(self.n_simulations):
            # Dirichlet(1,...,1) = Uniform on simplex → 더 고른 탐색
            raw = rng.exponential(scale=1.0, size=n)
            w = raw / raw.sum()
            # min/max 제약 적용
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
        """Risk Parity: 각 자산의 리스크 기여도(MRC) 균등화 (iterative).

        공분산 행렬 기반 MRC를 반복 수렴시켜 역변동성보다 정확한 RP 비중 산출.
        수렴 실패 시 역변동성 초기값 반환.
        """
        T, n = returns_matrix.shape
        cov = np.cov(returns_matrix.T)  # (n, n)
        if cov.ndim == 0:
            cov = np.array([[cov]])

        # 0 분산 방지
        vols = np.sqrt(np.diag(cov))
        vols = np.where(vols <= 0, 1e-8, vols)

        # 초기값: 역변동성
        inv_vol = 1.0 / vols
        w = inv_vol / inv_vol.sum()

        # Iterative Risk Parity (최대 200회)
        tol = 1e-8
        for _ in range(200):
            port_var = float(w @ cov @ w)
            if port_var <= 0:
                break
            # 한계 리스크 기여도 (MRC)
            mrc = cov @ w / np.sqrt(port_var)
            # 리스크 기여도 (RC = w * MRC)
            rc = w * mrc
            rc_mean = rc.mean()
            # 리스크 기여도 균등화를 위한 비중 업데이트
            w_new = w * rc_mean / np.where(mrc > 0, mrc, 1e-8)
            w_new = np.clip(w_new, 1e-10, None)
            w_new = w_new / w_new.sum()
            if np.max(np.abs(w_new - w)) < tol:
                w = w_new
                break
            w = w_new

        return self._apply_constraints(w)

    def _equal_weight(self, n: int) -> np.ndarray:
        return np.ones(n) / n
