"""Tests for G3 Multi-Asset Portfolio Optimizer."""

import numpy as np
import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.risk.portfolio_optimizer import PortfolioOptimizer, OptimizationResult


# ── 공통 픽스처 ──────────────────────────────────────────────────────────────

def make_returns(seed: int = 0, n_periods: int = 500):
    rng = np.random.default_rng(seed)
    symbols = ["BTC", "ETH", "SOL", "BNB"]
    data = {
        "BTC": pd.Series(rng.normal(0.0002, 0.01, n_periods)),
        "ETH": pd.Series(rng.normal(0.0002, 0.015, n_periods)),
        "SOL": pd.Series(rng.normal(0.0003, 0.025, n_periods)),
        "BNB": pd.Series(rng.normal(0.0001, 0.008, n_periods)),
    }
    return data


# ── Equal Weight ─────────────────────────────────────────────────────────────

def test_equal_weight_sums_to_one():
    opt = PortfolioOptimizer(method="equal_weight")
    result = opt.optimize(make_returns())
    assert abs(sum(result.weights.values()) - 1.0) < 1e-9


def test_equal_weight_uniform():
    rng = np.random.default_rng(1)
    data = {s: pd.Series(rng.normal(0, 0.01, 300)) for s in ["A", "B", "C", "D"]}
    opt = PortfolioOptimizer(method="equal_weight")
    result = opt.optimize(data)
    for w in result.weights.values():
        assert abs(w - 0.25) < 1e-9


# ── Risk Parity ───────────────────────────────────────────────────────────────

def test_risk_parity_sums_to_one():
    opt = PortfolioOptimizer(method="risk_parity")
    result = opt.optimize(make_returns())
    assert abs(sum(result.weights.values()) - 1.0) < 1e-9


def test_risk_parity_lower_vol_higher_weight():
    """BNB(낮은 변동성) > SOL(높은 변동성) 비중이어야 함."""
    opt = PortfolioOptimizer(method="risk_parity", min_weight=0.0, max_weight=1.0)
    result = opt.optimize(make_returns())
    assert result.weights["BNB"] > result.weights["SOL"]


# ── Mean Variance ─────────────────────────────────────────────────────────────

def test_mean_variance_sums_to_one():
    opt = PortfolioOptimizer(method="mean_variance")
    result = opt.optimize(make_returns())
    assert abs(sum(result.weights.values()) - 1.0) < 1e-9


def test_mean_variance_sharpe_positive():
    rng = np.random.default_rng(42)
    # 양의 기대수익률 보장
    data = {
        "BTC": pd.Series(rng.normal(0.001, 0.01, 500)),
        "ETH": pd.Series(rng.normal(0.001, 0.015, 500)),
        "SOL": pd.Series(rng.normal(0.001, 0.02, 500)),
    }
    opt = PortfolioOptimizer(method="mean_variance", risk_free_rate=0.0)
    result = opt.optimize(data)
    assert result.sharpe_ratio >= 0


# ── Constraints ───────────────────────────────────────────────────────────────

def test_max_weight_constraint():
    data = make_returns()
    for method in ["mean_variance", "risk_parity", "equal_weight"]:
        opt = PortfolioOptimizer(method=method, max_weight=0.5)
        result = opt.optimize(data)
        for w in result.weights.values():
            assert w <= 0.5 + 1e-9, f"{method}: weight {w} exceeds max_weight"


def test_min_weight_constraint():
    data = make_returns()
    for method in ["mean_variance", "risk_parity", "equal_weight"]:
        opt = PortfolioOptimizer(method=method, min_weight=0.05, max_weight=0.5)
        result = opt.optimize(data)
        for sym, w in result.weights.items():
            assert w >= 0.05 - 1e-6, f"{method}: {sym} weight {w} below min_weight"


# ── Fallback ──────────────────────────────────────────────────────────────────

def test_single_asset_fallback():
    rng = np.random.default_rng(0)
    data = {"BTC": pd.Series(rng.normal(0.0002, 0.01, 300))}
    for method in ["mean_variance", "risk_parity", "equal_weight"]:
        opt = PortfolioOptimizer(method=method)
        result = opt.optimize(data)
        assert abs(result.weights["BTC"] - 1.0) < 1e-9


def test_insufficient_data_fallback():
    """빈 returns dict → equal_weight fallback."""
    opt = PortfolioOptimizer(method="risk_parity")
    result = opt.optimize({})
    assert result.method == "equal_weight"
    assert result.weights == {}
    assert result.expected_return == 0.0


# ── Result Structure ──────────────────────────────────────────────────────────

def test_result_fields():
    opt = PortfolioOptimizer(method="risk_parity")
    result = opt.optimize(make_returns())
    assert hasattr(result, "weights")
    assert hasattr(result, "method")
    assert hasattr(result, "expected_return")
    assert hasattr(result, "expected_volatility")
    assert hasattr(result, "sharpe_ratio")
    assert isinstance(result.weights, dict)
    assert isinstance(result.method, str)
    assert isinstance(result.expected_return, float)
    assert isinstance(result.expected_volatility, float)
    assert isinstance(result.sharpe_ratio, float)


def test_summary_string():
    opt = PortfolioOptimizer(method="equal_weight")
    result = opt.optimize(make_returns())
    s = result.summary()
    assert isinstance(s, str)
    assert len(s) > 0
    assert "equal_weight" in s


# ── VaR / CVaR ───────────────────────────────────────────────────────────────

def test_var_cvar_fields():
    """OptimizationResult에 var_95, cvar_95 필드 존재 확인."""
    opt = PortfolioOptimizer(method="equal_weight")
    result = opt.optimize(make_returns())
    assert hasattr(result, "var_95")
    assert hasattr(result, "cvar_95")
    assert isinstance(result.var_95, float)
    assert isinstance(result.cvar_95, float)


def test_var_non_negative():
    """VaR, CVaR는 항상 0 이상."""
    opt = PortfolioOptimizer(method="risk_parity")
    result = opt.optimize(make_returns())
    assert result.var_95 >= 0.0
    assert result.cvar_95 >= 0.0


def test_cvar_gte_var():
    """CVaR(Expected Shortfall) >= VaR 이어야 함."""
    opt = PortfolioOptimizer(method="mean_variance")
    result = opt.optimize(make_returns())
    assert result.cvar_95 >= result.var_95 - 1e-9


def test_var_summary_contains_var():
    """summary() 문자열에 VaR95 포함."""
    opt = PortfolioOptimizer(method="equal_weight")
    result = opt.optimize(make_returns())
    assert "VaR95" in result.summary()
    assert "CVaR95" in result.summary()


def test_var_cvar_small_sample_boundary():
    """T=20 (cutoff_idx=1) 경계: CVaR==VaR이 되는 케이스 명시적 검증.

    cutoff_idx = max(1, int(20 * 0.05)) = 1
    → sorted_r[:1].mean() == sorted_r[0]  (CVaR == VaR, 허용된 경계)
    """
    rng = np.random.default_rng(7)
    r = rng.normal(0.0, 0.01, 20)
    var, cvar = PortfolioOptimizer._compute_var_cvar(r, confidence=0.95)
    # 경계에서 CVaR >= VaR 관계 유지
    assert cvar >= var - 1e-12
    # VaR은 실제 최솟값의 음수여야 함 (cutoff_idx=1 → sorted_r[0])
    sorted_r = np.sort(r)
    expected_var = max(0.0, -float(sorted_r[0]))
    assert abs(var - expected_var) < 1e-12


def test_var_cvar_all_positive_returns():
    """모든 수익률이 양수인 경우 VaR=0, CVaR=0 (max(0,x) 처리 확인)."""
    r = np.array([0.01, 0.02, 0.03, 0.005, 0.015, 0.008, 0.012, 0.007,
                  0.011, 0.009, 0.014, 0.006, 0.013, 0.016, 0.004,
                  0.018, 0.019, 0.003, 0.017, 0.010])
    var, cvar = PortfolioOptimizer._compute_var_cvar(r, confidence=0.95)
    assert var == 0.0
    assert cvar == 0.0


# ── Boundary: zero correlation, all-NaN, single data point ───────────────────

def test_zero_correlation_all_methods():
    """모든 자산이 독립(zero correlation)일 때 세 방법 모두 합=1, 비중>0."""
    rng = np.random.default_rng(99)
    # 각 자산을 독립 시드로 생성 → correlation ≈ 0
    data = {
        "A": pd.Series(rng.normal(0, 0.01, 500)),
        "B": pd.Series(rng.normal(0, 0.01, 500)),
        "C": pd.Series(rng.normal(0, 0.01, 500)),
    }
    for method in ["mean_variance", "risk_parity", "equal_weight"]:
        opt = PortfolioOptimizer(method=method, min_weight=0.0, max_weight=1.0)
        result = opt.optimize(data)
        assert abs(sum(result.weights.values()) - 1.0) < 1e-9, f"{method}: weights don't sum to 1"
        for sym, w in result.weights.items():
            assert w >= 0.0, f"{method}: {sym} weight {w} is negative"


def test_all_nan_returns_fallback():
    """모든 값이 NaN인 경우 dropna() 후 len<2 → equal_weight fallback."""
    data = {
        "BTC": pd.Series([np.nan, np.nan, np.nan]),
        "ETH": pd.Series([np.nan, np.nan, np.nan]),
    }
    for method in ["mean_variance", "risk_parity", "equal_weight"]:
        opt = PortfolioOptimizer(method=method)
        result = opt.optimize(data)
        assert result.method == "equal_weight"
        assert abs(sum(result.weights.values()) - 1.0) < 1e-9


def test_single_data_point_fallback():
    """공통 인덱스 1행만 있을 때 equal_weight fallback."""
    data = {
        "BTC": pd.Series([0.01]),
        "ETH": pd.Series([0.02]),
        "SOL": pd.Series([0.005]),
    }
    for method in ["mean_variance", "risk_parity"]:
        opt = PortfolioOptimizer(method=method)
        result = opt.optimize(data)
        assert result.method == "equal_weight"
        assert abs(sum(result.weights.values()) - 1.0) < 1e-9


# ── Numerical Instability ─────────────────────────────────────────────────────

def test_nan_weights_to_apply_constraints_returns_equal_weight():
    """NaN 포함 weights 입력 시 _apply_constraints가 equal_weight 반환."""
    opt = PortfolioOptimizer(method="risk_parity", min_weight=0.05, max_weight=0.5)
    nan_w = np.array([np.nan, 0.5, 0.3])
    result = opt._apply_constraints(nan_w)
    # NaN 없어야 하고 합=1, 모든 값>=0
    assert not np.any(np.isnan(result)), "NaN in output weights"
    assert abs(result.sum() - 1.0) < 1e-9
    assert np.all(result >= 0.0)


def test_inf_weights_to_apply_constraints_returns_equal_weight():
    """inf 포함 weights 입력 시 _apply_constraints가 equal_weight 반환."""
    opt = PortfolioOptimizer(method="risk_parity", min_weight=0.05, max_weight=0.5)
    inf_w = np.array([np.inf, 0.3, 0.2])
    result = opt._apply_constraints(inf_w)
    assert not np.any(np.isnan(result))
    assert not np.any(np.isinf(result))
    assert abs(result.sum() - 1.0) < 1e-9
    assert np.all(result >= 0.0)
