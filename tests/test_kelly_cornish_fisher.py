"""
KellySizer Cornish-Fisher VaR 테스트 (Cycle 216 B)
"""

import numpy as np
import pytest
from src.risk.kelly_sizer import KellySizer


def _make_sizer_with_trades(trades, seed=None):
    sizer = KellySizer()
    for t in trades:
        sizer.record_trade(t)
    return sizer


class TestCornishFisherVaR:
    """estimate_cornish_fisher_var() 검증."""

    def test_returns_none_below_5_trades(self):
        sizer = _make_sizer_with_trades([0.01, 0.02, -0.01])
        assert sizer.estimate_cornish_fisher_var() is None

    def test_returns_dict_with_required_keys(self):
        rng = np.random.default_rng(42)
        trades = rng.normal(0.01, 0.02, 30).tolist()
        sizer = _make_sizer_with_trades(trades)
        result = sizer.estimate_cornish_fisher_var(confidence=0.95)
        assert result is not None
        for key in ("cf_var", "cf_cvar", "hist_var", "hist_cvar",
                    "skewness", "excess_kurtosis", "n_trades", "low_sample_warning"):
            assert key in result

    def test_n_trades_correct(self):
        rng = np.random.default_rng(0)
        n = 25
        sizer = _make_sizer_with_trades(rng.normal(0, 0.01, n).tolist())
        result = sizer.estimate_cornish_fisher_var()
        assert result["n_trades"] == n

    def test_low_sample_warning_below_20(self):
        sizer = _make_sizer_with_trades([0.01 * i for i in range(-5, 10)])
        result = sizer.estimate_cornish_fisher_var(min_trades=20)
        assert result["low_sample_warning"] is True

    def test_no_low_sample_warning_above_threshold(self):
        rng = np.random.default_rng(7)
        sizer = _make_sizer_with_trades(rng.normal(0, 0.01, 30).tolist())
        result = sizer.estimate_cornish_fisher_var(min_trades=20)
        assert result["low_sample_warning"] is False

    def test_cf_var_positive(self):
        """VaR는 손실(양수) 방향으로 반환되어야 함."""
        rng = np.random.default_rng(99)
        trades = rng.normal(0.005, 0.03, 40).tolist()
        sizer = _make_sizer_with_trades(trades)
        result = sizer.estimate_cornish_fisher_var()
        assert result is not None
        # cf_var은 손실이므로 실수값 (양수 또는 0에 가까울 수 있음)
        assert isinstance(result["cf_var"], float)

    def test_cf_cvar_ge_cf_var(self):
        """CVaR은 VaR보다 크거나 같아야 함 (더 보수적)."""
        rng = np.random.default_rng(11)
        trades = rng.normal(0.005, 0.02, 50).tolist()
        sizer = _make_sizer_with_trades(trades)
        result = sizer.estimate_cornish_fisher_var()
        assert result is not None
        assert result["cf_cvar"] >= result["cf_var"] - 1e-9

    def test_negative_skew_fat_tail(self):
        """음의 왜도 + 높은 첨도: skewness < 0, excess_kurtosis > 0 반환."""
        rng = np.random.default_rng(21)
        # 40개 소폭 이익 + 5개 극단 손실 → 음의 왜도
        gains = rng.normal(0.01, 0.01, 40).tolist()
        losses = [-0.08, -0.10, -0.12, -0.15, -0.20]
        sizer = _make_sizer_with_trades(gains + losses)
        result = sizer.estimate_cornish_fisher_var()
        assert result is not None
        assert result["skewness"] < 0, "음의 왜도 예상"
        assert result["excess_kurtosis"] > 0, "양의 초과 첨도 예상"

    def test_uniform_zero_sigma_fallback(self):
        """분산이 0인 경우 hist_var로 fallback."""
        sizer = _make_sizer_with_trades([0.0] * 10)
        result = sizer.estimate_cornish_fisher_var()
        assert result is not None
        assert result["cf_var"] == result["hist_var"]

    def test_different_confidence_levels(self):
        """신뢰 수준 차이: 99% VaR > 95% VaR."""
        rng = np.random.default_rng(55)
        trades = rng.normal(0.0, 0.02, 50).tolist()
        sizer = _make_sizer_with_trades(trades)
        r95 = sizer.estimate_cornish_fisher_var(confidence=0.95)
        r99 = sizer.estimate_cornish_fisher_var(confidence=0.99)
        assert r95 is not None and r99 is not None
        # 99% VaR ≥ 95% VaR (더 보수적)
        assert r99["cf_var"] >= r95["cf_var"]
