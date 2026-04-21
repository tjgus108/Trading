"""Cycle 178 A+B+C 테스트: OOS Validator, Correlation, Performance Monitor."""
import pytest
import numpy as np
import pandas as pd

from src.backtest.walk_forward import RollingOOSValidator, BundleOOSResult
from src.risk.portfolio_optimizer import StrategyCorrelationAnalyzer, StrategyWeightResult
from src.risk.performance_tracker import LivePerformanceTracker, PerformanceMonitor


# ── Fixtures ──────────────────────────────────────────────────────


class DummyStrategy:
    """테스트용 더미 전략."""
    name = "dummy_strategy"

    def generate(self, window):
        from src.strategy.base import Signal, Action, Confidence
        return Signal(
            action=Action.HOLD, confidence=Confidence.LOW,
            strategy="dummy_strategy", entry_price=0.0,
            reasoning="test", invalidation="none",
        )


def make_ohlcv(n: int = 2000, seed: int = 42) -> pd.DataFrame:
    """테스트용 OHLCV 데이터 생성."""
    rng = np.random.default_rng(seed)
    close = 100.0 + np.cumsum(rng.normal(0, 0.5, n))
    close = np.maximum(close, 10.0)
    high = close + rng.uniform(0, 2, n)
    low = close - rng.uniform(0, 2, n)
    open_ = close + rng.normal(0, 0.3, n)
    volume = rng.uniform(100, 1000, n)
    atr14 = rng.uniform(0.5, 2.0, n)
    return pd.DataFrame({
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
        "atr14": atr14,
    })


# ── A: RollingOOSValidator Tests ──────────────────────────────────


class TestRollingOOSValidator:
    def test_insufficient_data(self):
        validator = RollingOOSValidator(is_bars=500, oos_bars=200)
        df = make_ohlcv(100)
        result = validator.validate(DummyStrategy(), df)
        assert isinstance(result, BundleOOSResult)
        assert not result.all_passed
        assert "데이터 부족" in result.fail_reasons[0]

    def test_validator_runs_with_enough_data(self):
        validator = RollingOOSValidator(is_bars=200, oos_bars=100, slide_bars=100)
        df = make_ohlcv(1000)
        result = validator.validate(DummyStrategy(), df)
        assert isinstance(result, BundleOOSResult)
        assert result.strategy_name == "dummy_strategy"

    def test_folds_generated(self):
        validator = RollingOOSValidator(is_bars=200, oos_bars=100, slide_bars=100)
        df = make_ohlcv(800)
        result = validator.validate(DummyStrategy(), df)
        assert len(result.folds) >= 1

    def test_summary_format(self):
        validator = RollingOOSValidator(is_bars=200, oos_bars=100, slide_bars=100)
        df = make_ohlcv(800)
        result = validator.validate(DummyStrategy(), df)
        summary = result.summary()
        assert "BUNDLE_OOS" in summary
        assert "dummy_strategy" in summary


# ── B: StrategyCorrelationAnalyzer Tests ──────────────────────────


class TestStrategyCorrelation:
    def test_empty_input(self):
        analyzer = StrategyCorrelationAnalyzer()
        result = analyzer.analyze({})
        assert result.method == "empty"
        assert result.weights == {}

    def test_single_strategy(self):
        analyzer = StrategyCorrelationAnalyzer()
        pnls = {"cmf": pd.Series(np.random.randn(50))}
        result = analyzer.analyze(pnls)
        assert result.weights["cmf"] == 1.0
        assert result.method == "single"

    def test_two_strategies_weights_sum_to_one(self):
        rng = np.random.default_rng(42)
        analyzer = StrategyCorrelationAnalyzer()
        pnls = {
            "cmf": pd.Series(rng.normal(0.01, 0.02, 50)),
            "wick_reversal": pd.Series(rng.normal(0.01, 0.04, 50)),
        }
        result = analyzer.analyze(pnls)
        assert abs(sum(result.weights.values()) - 1.0) < 0.01
        # inv-vol: 낮은 변동성 전략이 더 높은 가중치
        assert result.weights["cmf"] > result.weights["wick_reversal"]

    def test_five_strategies(self):
        rng = np.random.default_rng(42)
        names = ["cmf", "elder_impulse", "wick_reversal", "narrow_range", "value_area"]
        pnls = {n: pd.Series(rng.normal(0.005, 0.02 + i * 0.005, 100)) for i, n in enumerate(names)}
        analyzer = StrategyCorrelationAnalyzer()
        result = analyzer.analyze(pnls)
        assert len(result.weights) == 5
        assert abs(sum(result.weights.values()) - 1.0) < 0.01
        assert isinstance(result.correlation_matrix, dict)

    def test_high_corr_detection(self):
        rng = np.random.default_rng(42)
        base = rng.normal(0, 0.02, 100)
        pnls = {
            "strat_a": pd.Series(base + rng.normal(0, 0.001, 100)),
            "strat_b": pd.Series(base + rng.normal(0, 0.001, 100)),
        }
        analyzer = StrategyCorrelationAnalyzer(corr_threshold=0.30)
        result = analyzer.analyze(pnls)
        assert len(result.high_corr_pairs) > 0
        assert result.high_corr_pairs[0][2] > 0.30

    def test_summary_format(self):
        rng = np.random.default_rng(42)
        pnls = {
            "a": pd.Series(rng.normal(0, 0.02, 50)),
            "b": pd.Series(rng.normal(0, 0.03, 50)),
        }
        result = StrategyCorrelationAnalyzer().analyze(pnls)
        summary = result.summary()
        assert "STRATEGY_WEIGHTS" in summary


# ── C: PerformanceMonitor Tests ───────────────────────────────────


class TestPerformanceMonitor:
    def _make_tracker_with_trades(self, n=30):
        tracker = LivePerformanceTracker()
        rng = np.random.default_rng(42)
        for _ in range(n):
            pnl = rng.normal(10, 50)
            tracker.record_trade("test_strat", pnl, 100.0, 100.0 + pnl)
        return tracker

    def test_rolling_pf(self):
        tracker = self._make_tracker_with_trades(30)
        pf = tracker.get_rolling_pf("test_strat")
        assert pf is not None
        assert pf > 0

    def test_rolling_mdd(self):
        tracker = self._make_tracker_with_trades(30)
        mdd = tracker.get_rolling_mdd("test_strat")
        assert isinstance(mdd, float)
        assert mdd >= 0.0

    def test_summary_has_new_fields(self):
        tracker = self._make_tracker_with_trades(30)
        summary = tracker.get_summary("test_strat")
        assert "rolling_pf" in summary
        assert "rolling_mdd" in summary

    def test_monitor_check_all(self):
        tracker = self._make_tracker_with_trades(30)
        alerts_received = []
        def on_alert(level, msg):
            alerts_received.append((level, msg))
        monitor = PerformanceMonitor(
            tracker=tracker,
            on_alert=on_alert,
            sharpe_warn=100.0,
            pf_warn=100.0,
            check_interval=0,
        )
        results = monitor.check_all(["test_strat"])
        assert "test_strat" in results
        assert results["test_strat"]["level"] in ("WARNING", "CRITICAL")
        assert len(alerts_received) > 0

    def test_monitor_no_alert_when_good(self):
        tracker = self._make_tracker_with_trades(30)
        alerts_received = []
        def on_alert(level, msg):
            alerts_received.append((level, msg))
        monitor = PerformanceMonitor(
            tracker=tracker,
            on_alert=on_alert,
            sharpe_warn=-100.0,
            pf_warn=0.0,
            mdd_warn_pct=0.99,
        )
        results = monitor.check_all(["test_strat"])
        assert len(alerts_received) == 0

    def test_regime_change_alert(self):
        tracker = LivePerformanceTracker()
        alerts_received = []
        monitor = PerformanceMonitor(
            tracker=tracker,
            on_alert=lambda l, m: alerts_received.append((l, m)),
        )
        monitor.regime_change_alert("TREND", "CRISIS")
        assert len(alerts_received) == 1
        assert "레짐 전환" in alerts_received[0][1]

    def test_mdd_critical_alert(self):
        tracker = LivePerformanceTracker()
        # 초기 수익 후 급락 → peak 생성 후 MDD 발생
        tracker.record_trade("bad_strat", 500.0, 100.0, 105.0)
        for i in range(30):
            tracker.record_trade("bad_strat", -100.0, 100.0, 90.0)
        alerts_received = []
        monitor = PerformanceMonitor(
            tracker=tracker,
            on_alert=lambda l, m: alerts_received.append((l, m)),
            mdd_halt_pct=0.01,
            check_interval=0,
        )
        results = monitor.check_all(["bad_strat"])
        assert results["bad_strat"]["mdd"] > 0
        critical_alerts = [a for a in alerts_received if a[0] == "CRITICAL"]
        assert len(critical_alerts) > 0

    def test_empty_strategy(self):
        tracker = LivePerformanceTracker()
        summary = tracker.get_summary("nonexistent")
        assert summary["total_trades"] == 0
        assert summary["rolling_pf"] is None
        assert summary["rolling_mdd"] == 0.0


class TestRollingPfEdgeCases:
    def test_all_wins(self):
        tracker = LivePerformanceTracker()
        for _ in range(10):
            tracker.record_trade("winner", 50.0, 100.0, 150.0)
        pf = tracker.get_rolling_pf("winner")
        assert pf == float("inf")

    def test_all_losses(self):
        tracker = LivePerformanceTracker()
        for _ in range(10):
            tracker.record_trade("loser", -50.0, 100.0, 50.0)
        pf = tracker.get_rolling_pf("loser")
        assert pf == 0.0

    def test_too_few_trades(self):
        tracker = LivePerformanceTracker()
        tracker.record_trade("few", 10.0, 100.0, 110.0)
        assert tracker.get_rolling_pf("few") is None
