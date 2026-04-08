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
