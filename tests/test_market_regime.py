"""MarketRegimeDetector + StrategyRotationManager 테스트."""

import json
import numpy as np
import pandas as pd
import pytest
from pathlib import Path

from src.strategy.regime import MarketRegime, MarketRegimeDetector
from src.strategy.rotation import StrategyRotationManager


def _make_df(n=200, trend="up"):
    np.random.seed(42)
    if trend == "up":
        base = np.linspace(100, 140, n) + np.random.randn(n) * 0.3
    elif trend == "down":
        base = np.linspace(140, 100, n) + np.random.randn(n) * 0.3
    else:
        base = 120 + np.random.randn(n) * 1.0
    return pd.DataFrame({
        "open": base - 0.2,
        "high": base + np.abs(np.random.randn(n)) * 0.8,
        "low": base - np.abs(np.random.randn(n)) * 0.8,
        "close": base,
        "volume": np.random.randint(100, 1000, n).astype(float),
    })


class TestMarketRegimeDetector:
    def test_none_returns_ranging(self):
        assert MarketRegimeDetector().detect(None) == MarketRegime.RANGING

    def test_short_data_returns_ranging(self):
        assert MarketRegimeDetector().detect(_make_df(20)) == MarketRegime.RANGING

    def test_uptrend(self):
        regime = MarketRegimeDetector().detect(_make_df(200, "up"))
        assert regime in (MarketRegime.TREND_UP, MarketRegime.RANGING)

    def test_downtrend(self):
        regime = MarketRegimeDetector().detect(_make_df(200, "down"))
        assert regime in (MarketRegime.TREND_DOWN, MarketRegime.RANGING)

    def test_flat(self):
        regime = MarketRegimeDetector().detect(_make_df(200, "flat"))
        assert regime in (MarketRegime.RANGING, MarketRegime.HIGH_VOL)

    def test_regime_summary_sums_to_one(self):
        summary = MarketRegimeDetector().regime_summary(_make_df(200, "up"), 10)
        assert sum(summary.values()) == pytest.approx(1.0, abs=0.01)

    def test_detect_history_length(self):
        history = MarketRegimeDetector().detect_history(_make_df(200, "up"), 10)
        assert len(history) == 10


class TestStrategyRotationManager:
    def test_empty_state(self, tmp_path):
        mgr = StrategyRotationManager(state_file=tmp_path / "rot.json")
        assert mgr.get_active_strategies("BTC/USDT") == []

    def test_needs_revalidation_empty(self, tmp_path):
        mgr = StrategyRotationManager(state_file=tmp_path / "rot.json")
        assert mgr.needs_revalidation("BTC/USDT") is True

    def test_revalidate_adds_strategies(self, tmp_path):
        mgr = StrategyRotationManager(state_file=tmp_path / "rot.json")
        results = [
            {"name": "strat_a", "overall_passed": True, "avg_return": 0.05,
             "avg_sharpe": 1.5, "avg_pf": 2.0, "avg_trades": 20,
             "avg_mdd": 0.05, "passed_windows": 4, "total_windows": 6},
            {"name": "strat_b", "overall_passed": False, "avg_return": -0.03,
             "avg_sharpe": -0.5, "avg_pf": 0.8, "avg_trades": 15,
             "avg_mdd": 0.12, "passed_windows": 1, "total_windows": 6},
        ]
        changes = mgr.revalidate("BTC/USDT", results)
        assert "strat_a" in changes
        assert mgr.get_active_strategies("BTC/USDT") == ["strat_a"]

    def test_revalidate_persists(self, tmp_path):
        state_file = tmp_path / "rot.json"
        mgr = StrategyRotationManager(state_file=state_file)
        mgr.revalidate("ETH/USDT", [
            {"name": "s1", "overall_passed": True, "avg_return": 0.07,
             "avg_sharpe": 2.0, "avg_pf": 1.8, "avg_trades": 30,
             "avg_mdd": 0.04, "passed_windows": 5, "total_windows": 6},
        ])
        mgr2 = StrategyRotationManager(state_file=state_file)
        assert mgr2.get_active_strategies("ETH/USDT") == ["s1"]

    def test_pass_to_fail_transition(self, tmp_path):
        mgr = StrategyRotationManager(state_file=tmp_path / "rot.json")
        mgr.revalidate("BTC/USDT", [
            {"name": "s1", "overall_passed": True, "avg_return": 0.05,
             "avg_sharpe": 1.5, "avg_pf": 2.0, "avg_trades": 20,
             "avg_mdd": 0.05, "passed_windows": 4, "total_windows": 6},
        ])
        assert mgr.get_active_strategies("BTC/USDT") == ["s1"]

        changes = mgr.revalidate("BTC/USDT", [
            {"name": "s1", "overall_passed": False, "avg_return": -0.02,
             "avg_sharpe": -0.3, "avg_pf": 0.7, "avg_trades": 18,
             "avg_mdd": 0.15, "passed_windows": 1, "total_windows": 6},
        ])
        assert changes["s1"] == "PASS->FAIL"
        assert mgr.get_active_strategies("BTC/USDT") == []

    def test_recommend_for_regime(self, tmp_path):
        mgr = StrategyRotationManager(state_file=tmp_path / "rot.json")
        mgr.revalidate("BTC/USDT", [
            {"name": "momentum_quality", "overall_passed": True, "avg_return": 0.05,
             "avg_sharpe": 1.5, "avg_pf": 2.0, "avg_trades": 20,
             "avg_mdd": 0.05, "passed_windows": 4, "total_windows": 6},
            {"name": "mean_rev_band", "overall_passed": True, "avg_return": 0.03,
             "avg_sharpe": 1.2, "avg_pf": 1.6, "avg_trades": 25,
             "avg_mdd": 0.03, "passed_windows": 4, "total_windows": 6},
        ])
        trend = mgr.recommend_for_regime("BTC/USDT", "TREND_UP")
        assert "momentum_quality" in trend

        ranging = mgr.recommend_for_regime("BTC/USDT", "RANGING")
        assert "mean_rev_band" in ranging

    def test_rotation_summary(self, tmp_path):
        mgr = StrategyRotationManager(state_file=tmp_path / "rot.json")
        mgr.revalidate("BTC/USDT", [
            {"name": "s1", "overall_passed": True, "avg_return": 0.05,
             "avg_sharpe": 1.5, "avg_pf": 2.0, "avg_trades": 20,
             "avg_mdd": 0.05, "passed_windows": 4, "total_windows": 6},
        ])
        summary = mgr.rotation_summary()
        assert "BTC/USDT" in summary
        assert "1/1 PASS" in summary
