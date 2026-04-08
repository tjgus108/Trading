"""Phase J: MonteCarlo, BacktestReport, SignalCorrelationTracker 테스트."""

import sys
import os
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.backtest.monte_carlo import MonteCarlo
from src.backtest.report import BacktestReport
from src.analysis.strategy_correlation import SignalCorrelationTracker
from src.strategy.base import Action


# ═══════════════════════════════════════════════════════════════════════════
# J1. MonteCarlo
# ═══════════════════════════════════════════════════════════════════════════

def _make_returns(n: int = 300, mean: float = 0.0002, std: float = 0.01, seed: int = 42):
    rng = np.random.default_rng(seed)
    return pd.Series(rng.normal(mean, std, n))


class TestMonteCarlo:

    def test_result_shape(self):
        mc = MonteCarlo(n_simulations=100, seed=0)
        result = mc.run(_make_returns())
        assert len(result.final_returns) == 100
        assert len(result.sharpes) == 100
        assert len(result.max_drawdowns) == 100

    def test_percentiles_ordered(self):
        mc = MonteCarlo(n_simulations=200, seed=42)
        result = mc.run(_make_returns())
        assert result.p5_return <= result.p50_return <= result.p95_return

    def test_mdd_between_0_and_1(self):
        mc = MonteCarlo(n_simulations=100, seed=0)
        result = mc.run(_make_returns())
        assert np.all(result.max_drawdowns >= 0)
        assert np.all(result.max_drawdowns <= 1.0)

    def test_prob_positive_in_range(self):
        mc = MonteCarlo(n_simulations=200, seed=0)
        result = mc.run(_make_returns(mean=0.0005))  # 양의 기대수익
        p = result.prob_positive()
        assert 0.0 <= p <= 1.0

    def test_positive_mean_mostly_positive(self):
        mc = MonteCarlo(n_simulations=300, seed=0)
        result = mc.run(_make_returns(mean=0.001, std=0.005))  # 높은 Sharpe
        assert result.prob_positive() > 0.5

    def test_summary_string(self):
        mc = MonteCarlo(n_simulations=50, seed=0)
        result = mc.run(_make_returns())
        s = result.summary()
        assert "MonteCarlo" in s
        assert "Return" in s

    def test_small_data(self):
        """데이터가 block_size보다 작아도 에러 없이 동작."""
        mc = MonteCarlo(n_simulations=50, block_size=20, seed=0)
        result = mc.run(pd.Series([0.001, 0.002, -0.001, 0.003, 0.001]))
        assert len(result.final_returns) == 50

    def test_deterministic_with_seed(self):
        mc1 = MonteCarlo(n_simulations=100, seed=42)
        mc2 = MonteCarlo(n_simulations=100, seed=42)
        r1 = mc1.run(_make_returns())
        r2 = mc2.run(_make_returns())
        np.testing.assert_array_equal(r1.final_returns, r2.final_returns)


# ═══════════════════════════════════════════════════════════════════════════
# J2. BacktestReport
# ═══════════════════════════════════════════════════════════════════════════

def _make_trades(n: int = 100, win_rate: float = 0.55, seed: int = 0):
    rng = np.random.default_rng(seed)
    trades = []
    for _ in range(n):
        if rng.random() < win_rate:
            trades.append({"pnl_pct": rng.uniform(0.005, 0.02)})
        else:
            trades.append({"pnl_pct": rng.uniform(-0.015, -0.002)})
    return trades


class TestBacktestReport:

    def test_basic_fields(self):
        report = BacktestReport.from_trades(_make_trades())
        assert hasattr(report, "total_return")
        assert hasattr(report, "sharpe_ratio")
        assert hasattr(report, "max_drawdown")
        assert hasattr(report, "win_rate")
        assert hasattr(report, "profit_factor")

    def test_win_rate_approx(self):
        report = BacktestReport.from_trades(_make_trades(n=500, win_rate=0.6))
        assert 0.5 < report.win_rate < 0.7

    def test_max_drawdown_non_negative(self):
        report = BacktestReport.from_trades(_make_trades())
        assert report.max_drawdown >= 0.0

    def test_profit_factor_positive(self):
        report = BacktestReport.from_trades(_make_trades(win_rate=0.6))
        assert report.profit_factor > 0

    def test_empty_trades(self):
        report = BacktestReport.from_trades([])
        assert report.total_trades == 0
        assert report.sharpe_ratio == 0.0

    def test_calmar_ratio(self):
        """Calmar = ann_return / mdd (mdd>0)."""
        report = BacktestReport.from_trades(_make_trades(n=200, win_rate=0.65))
        if report.max_drawdown > 0:
            expected = report.ann_return / report.max_drawdown
            assert abs(report.calmar_ratio - expected) < 1e-9
        else:
            assert report.calmar_ratio == 0.0

    def test_summary_string(self):
        report = BacktestReport.from_trades(_make_trades())
        s = report.summary()
        assert "Sharpe" in s
        assert "Win Rate" in s
        assert "Max Drawdown" in s

    def test_to_dict(self):
        report = BacktestReport.from_trades(_make_trades())
        d = report.to_dict()
        assert isinstance(d, dict)
        assert "sharpe_ratio" in d
        assert "win_rate" in d

    def test_pnl_key_fallback(self):
        """pnl_pct 없고 pnl만 있어도 동작."""
        trades = [{"pnl": 0.01}, {"pnl": -0.005}, {"pnl": 0.008}, {"pnl": 0.012}, {"pnl": -0.003}]
        report = BacktestReport.from_trades(trades)
        assert report.total_trades == 5

    def test_from_backtest_result(self):
        """BacktestResult → BacktestReport 변환."""
        from src.backtest.engine import BacktestResult
        br = BacktestResult(
            strategy="ema_cross",
            total_trades=50,
            win_rate=0.55,
            profit_factor=1.8,
            sharpe_ratio=1.4,
            max_drawdown=0.12,
            total_return=0.25,
            passed=True,
            fail_reasons=[],
        )
        report = BacktestReport.from_backtest_result(br)
        assert report.total_trades == 50
        assert report.win_rate == 0.55
        assert report.profit_factor == 1.8
        assert report.sharpe_ratio == 1.4
        assert report.max_drawdown == 0.12
        assert report.total_return == 0.25
        assert abs(report.calmar_ratio - (0.25 / 0.12)) < 1e-9


# ═══════════════════════════════════════════════════════════════════════════
# J3. SignalCorrelationTracker
# ═══════════════════════════════════════════════════════════════════════════

class TestSignalCorrelationTracker:

    def test_correlation_matrix_shape(self):
        tracker = SignalCorrelationTracker(["a", "b", "c"])
        for _ in range(10):
            tracker.record("a", Action.BUY)
            tracker.record("b", Action.BUY)
            tracker.record("c", Action.SELL)
        corr = tracker.correlation_matrix()
        assert corr is not None
        assert corr.shape == (3, 3)

    def test_diagonal_is_one(self):
        tracker = SignalCorrelationTracker(["x", "y"])
        actions = [Action.BUY, Action.SELL, Action.HOLD, Action.BUY, Action.SELL,
                   Action.BUY, Action.BUY, Action.SELL, Action.HOLD, Action.BUY]
        for a in actions:
            tracker.record("x", a)
            tracker.record("y", a)
        corr = tracker.correlation_matrix()
        assert corr is not None
        assert abs(corr.loc["x", "x"] - 1.0) < 1e-9

    def test_identical_signals_correlation_one(self):
        tracker = SignalCorrelationTracker(["p", "q"])
        actions = [Action.BUY, Action.SELL, Action.HOLD, Action.BUY, Action.SELL,
                   Action.BUY, Action.BUY, Action.SELL, Action.HOLD, Action.BUY]
        for a in actions:
            tracker.record("p", a)
            tracker.record("q", a)  # identical
        corr = tracker.correlation_matrix()
        assert corr is not None
        assert abs(corr.loc["p", "q"] - 1.0) < 1e-6

    def test_opposite_signals_negative_correlation(self):
        tracker = SignalCorrelationTracker(["u", "v"])
        actions = [Action.BUY, Action.SELL, Action.BUY, Action.SELL, Action.BUY,
                   Action.SELL, Action.BUY, Action.SELL, Action.BUY, Action.SELL]
        for a in actions:
            tracker.record("u", a)
            opp = Action.SELL if a == Action.BUY else (Action.BUY if a == Action.SELL else Action.HOLD)
            tracker.record("v", opp)
        corr = tracker.correlation_matrix()
        assert corr is not None
        assert corr.loc["u", "v"] < 0

    def test_insufficient_data_returns_none(self):
        tracker = SignalCorrelationTracker(["a", "b"])
        tracker.record("a", Action.BUY)  # 1개만 기록
        tracker.record("b", Action.BUY)
        assert tracker.correlation_matrix() is None

    def test_high_correlation_pairs(self):
        tracker = SignalCorrelationTracker(["p", "q", "r"])
        # 동일한 패턴의 신호 20번 기록 (상수가 아닌 다양한 패턴)
        pattern = [Action.BUY, Action.SELL, Action.BUY, Action.HOLD, Action.SELL] * 4
        for a in pattern:
            tracker.record("p", a)
            tracker.record("q", a)   # p와 동일 → 상관 1.0
            opp = Action.SELL if a == Action.BUY else (Action.BUY if a == Action.SELL else Action.HOLD)
            tracker.record("r", opp)  # p와 반대
        pairs = tracker.high_correlation_pairs(threshold=0.7)
        pair_names = [(a, b) for a, b, _ in pairs]
        # p-q 상관 ≈ 1.0 이어야 함
        assert ("p", "q") in pair_names or ("q", "p") in pair_names

    def test_record_many(self):
        tracker = SignalCorrelationTracker(["a", "b"])
        for _ in range(10):
            tracker.record_many({"a": Action.BUY, "b": Action.SELL})
        corr = tracker.correlation_matrix()
        assert corr is not None

    def test_summary_string(self):
        tracker = SignalCorrelationTracker(["x", "y"])
        for _ in range(10):
            tracker.record("x", Action.BUY)
            tracker.record("y", Action.BUY)
        s = tracker.summary()
        assert isinstance(s, str)
        assert len(s) > 0

    def test_window_cap(self):
        """window 초과 시 오래된 데이터 삭제."""
        tracker = SignalCorrelationTracker(["a"], window=5)
        for _ in range(20):
            tracker.record("a", Action.BUY)
        assert len(tracker._signals["a"]) <= 5
