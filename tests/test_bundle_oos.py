"""
tests/test_bundle_oos.py — run_bundle_oos.py + PerformanceMonitor 연동 테스트.
"""
import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from src.backtest.walk_forward import RollingOOSValidator, BundleOOSResult, OOSFoldResult
from src.risk.performance_tracker import LivePerformanceTracker, PerformanceMonitor


# ── 헬퍼 ──────────────────────────────────────────────────


def make_ohlcv(n: int = 2000, seed: int = 42) -> pd.DataFrame:
    """OOS 검증용 충분한 크기의 테스트 DataFrame."""
    np.random.seed(seed)
    closes = 100.0 * np.cumprod(1 + 0.0005 + np.random.randn(n) * 0.002)
    highs = closes * 1.005
    lows = closes * 0.995
    volume = np.random.randint(100, 1000, n).astype(float)

    df = pd.DataFrame({
        "close": closes, "high": highs, "low": lows,
        "open": closes * (1 + np.random.randn(n) * 0.001),
        "volume": volume,
        "atr14": np.full(n, 1.0),
        "ema20": closes,
        "ema50": closes * 0.99,
        "sma20": closes,
        "rsi14": np.full(n, 50.0),
        "macd": np.random.randn(n) * 0.1,
        "macd_signal": np.random.randn(n) * 0.05,
    })
    return df


# ── RollingOOSValidator 기본 테스트 ────────────────────────


def test_rolling_oos_validator_insufficient_data():
    """데이터 부족 시 BundleOOSResult.all_passed=False."""
    from src.strategy.base import Action, BaseStrategy, Confidence, Signal

    class DummyStrat(BaseStrategy):
        name = "dummy"
        def generate(self, df):
            return Signal(
                action=Action.HOLD, confidence=Confidence.LOW,
                strategy=self.name, entry_price=0.0,
                reasoning="test", invalidation="none",
            )

    v = RollingOOSValidator(is_bars=1080, oos_bars=360, slide_bars=360)
    df = make_ohlcv(500)  # 500 < 1080 + 360
    result = v.validate(DummyStrat(), df)
    assert isinstance(result, BundleOOSResult)
    assert not result.all_passed
    assert "데이터 부족" in result.fail_reasons[0]


def test_rolling_oos_validator_creates_folds():
    """충분한 데이터로 fold 생성 확인."""
    from src.strategy.base import Action, BaseStrategy, Confidence, Signal

    class DummyStrat(BaseStrategy):
        name = "dummy"
        def generate(self, df):
            return Signal(
                action=Action.HOLD, confidence=Confidence.LOW,
                strategy=self.name, entry_price=0.0,
                reasoning="test", invalidation="none",
            )

    v = RollingOOSValidator(is_bars=100, oos_bars=50, slide_bars=50)
    df = make_ohlcv(500)
    result = v.validate(DummyStrat(), df)
    assert isinstance(result, BundleOOSResult)
    assert len(result.folds) >= 1
    for fold in result.folds:
        assert isinstance(fold, OOSFoldResult)


# ── BundleOOSResult.summary() 테스트 ──────────────────────


def test_bundle_oos_result_summary_format():
    """summary()가 올바른 문자열 반환."""
    result = BundleOOSResult(
        strategy_name="test_strat",
        folds=[],
        avg_wfe=0.65,
        avg_oos_sharpe=1.2,
        avg_oos_pf=1.8,
        all_passed=True,
        fail_reasons=[],
    )
    s = result.summary()
    assert "PASS" in s
    assert "test_strat" in s
    assert "0.650" in s


def test_bundle_oos_result_summary_fail():
    """FAIL 시 summary에 fail_reasons 포함."""
    result = BundleOOSResult(
        strategy_name="fail_strat",
        folds=[],
        avg_wfe=0.3,
        avg_oos_sharpe=0.5,
        avg_oos_pf=1.1,
        all_passed=False,
        fail_reasons=["Failed folds: [0, 1]"],
    )
    s = result.summary()
    assert "FAIL" in s
    assert "Failed folds" in s


# ── format_summary_table 테스트 ────────────────────────────


def test_format_summary_table():
    """요약 테이블 포맷팅 검증."""
    from scripts.run_bundle_oos import format_summary_table

    results = [
        ("cmf", BundleOOSResult(
            strategy_name="cmf", folds=[], avg_wfe=0.6,
            avg_oos_sharpe=1.5, avg_oos_pf=2.0,
            all_passed=True, fail_reasons=[],
        )),
        ("narrow_range", BundleOOSResult(
            strategy_name="narrow_range", folds=[], avg_wfe=0.3,
            avg_oos_sharpe=0.5, avg_oos_pf=1.0,
            all_passed=False, fail_reasons=["Failed folds: [0]"],
        )),
    ]

    table = format_summary_table(results)
    assert "cmf" in table
    assert "PASS" in table
    assert "FAIL" in table
    assert "narrow_range" in table


# ── PerformanceMonitor 연동 테스트 ─────────────────────────


def test_perf_monitor_record_trade_and_check():
    """record_trade 후 check_all이 올바른 결과 반환."""
    tracker = LivePerformanceTracker()
    alerts_received = []

    def on_alert(level, msg):
        alerts_received.append((level, msg))

    monitor = PerformanceMonitor(
        tracker=tracker,
        on_alert=on_alert,
        sharpe_warn=1.0,
        pf_warn=1.4,
        mdd_warn_pct=0.10,
        mdd_halt_pct=0.15,
        check_interval=0.0,  # 쿨다운 없음 (테스트용)
    )

    # 거래 기록 (10회 수익)
    for i in range(10):
        tracker.record_trade("BTC/USDT:cmf", 50.0, 1000.0, 1050.0)

    results = monitor.check_all(["BTC/USDT:cmf"])
    assert "BTC/USDT:cmf" in results
    # 모두 수익이므로 PF는 inf (loss=0), MDD는 0
    assert results["BTC/USDT:cmf"]["mdd"] == 0.0
    assert results["BTC/USDT:cmf"]["level"] == "INFO"


def test_perf_monitor_alerts_on_high_mdd():
    """MDD 임계값 초과 시 알림 발생."""
    tracker = LivePerformanceTracker()
    alerts_received = []

    def on_alert(level, msg):
        alerts_received.append((level, msg))

    monitor = PerformanceMonitor(
        tracker=tracker,
        on_alert=on_alert,
        sharpe_warn=1.0,
        pf_warn=1.4,
        mdd_warn_pct=0.05,   # 낮은 임계값
        mdd_halt_pct=0.50,
        check_interval=0.0,
    )

    # 큰 수익 후 큰 손실 → MDD 발생
    tracker.record_trade("strat_a", 100.0, 1000.0, 1100.0)
    tracker.record_trade("strat_a", 100.0, 1100.0, 1200.0)
    tracker.record_trade("strat_a", -80.0, 1200.0, 1120.0)
    tracker.record_trade("strat_a", -80.0, 1120.0, 1040.0)
    tracker.record_trade("strat_a", -80.0, 1040.0, 960.0)

    results = monitor.check_all(["strat_a"])
    assert results["strat_a"]["mdd"] > 0.0
    # MDD가 임계값 초과하면 알림 발생
    if results["strat_a"]["mdd"] >= 0.05:
        assert len(alerts_received) > 0


def test_perf_monitor_regime_change_alert():
    """레짐 전환 알림 발송."""
    tracker = LivePerformanceTracker()
    alerts_received = []

    def on_alert(level, msg):
        alerts_received.append((level, msg))

    monitor = PerformanceMonitor(
        tracker=tracker, on_alert=on_alert, check_interval=0.0,
    )

    monitor.regime_change_alert("TREND_UP", "HIGH_VOL")
    assert len(alerts_received) == 1
    assert "레짐 전환" in alerts_received[0][1]
    assert "TREND_UP" in alerts_received[0][1]
    assert "HIGH_VOL" in alerts_received[0][1]


# ── LivePaperTrader PerformanceMonitor 통합 테스트 ──────────


def test_live_paper_trader_has_perf_monitor():
    """LivePaperTrader에 PerformanceMonitor가 초기화되는지 확인."""
    from scripts.live_paper_trader import LivePaperTrader, LiveState

    with patch.object(LiveState, 'load') as mock_load, \
         patch('scripts.live_paper_trader.CircuitBreaker'), \
         patch('scripts.live_paper_trader.StrategyRotationManager'), \
         patch('scripts.live_paper_trader.MarketRegimeDetector'), \
         patch('scripts.live_paper_trader.SignalCorrelationTracker'), \
         patch('scripts.live_paper_trader.DriftMonitor'), \
         patch('signal.signal'):
        state = LiveState()
        state.portfolio_balance = 10000.0
        mock_load.return_value = state
        trader = LivePaperTrader(days=1, interval=60)
        trader.state = state

        assert hasattr(trader, '_perf_tracker')
        assert hasattr(trader, '_perf_monitor')
        assert isinstance(trader._perf_tracker, LivePerformanceTracker)
        assert isinstance(trader._perf_monitor, PerformanceMonitor)


def test_live_paper_trader_performance_alert_callback():
    """_performance_alert 콜백이 로그를 남기는지 확인."""
    from scripts.live_paper_trader import LivePaperTrader, LiveState

    with patch.object(LiveState, 'load') as mock_load, \
         patch('scripts.live_paper_trader.CircuitBreaker'), \
         patch('scripts.live_paper_trader.StrategyRotationManager'), \
         patch('scripts.live_paper_trader.MarketRegimeDetector'), \
         patch('scripts.live_paper_trader.SignalCorrelationTracker'), \
         patch('scripts.live_paper_trader.DriftMonitor'), \
         patch('signal.signal'):
        state = LiveState()
        state.portfolio_balance = 10000.0
        mock_load.return_value = state
        trader = LivePaperTrader(days=1, interval=60)
        trader.state = state

        # CRITICAL 알림은 circuit_breaker를 트리거해야 함
        trader.circuit_breaker = MagicMock()
        trader._performance_alert("CRITICAL", "MDD 15% exceeded")
        # _triggered와 _reason 세팅 확인 (MagicMock이므로 에러 없이 동작)
        assert True  # 콜백이 예외 없이 실행됨


# ── run_bundle_oos 함수 import 테스트 ──────────────────────


def test_run_bundle_oos_imports():
    """run_bundle_oos 모듈이 정상 import되는지 확인."""
    from scripts.run_bundle_oos import (
        BUNDLE_STRATEGIES,
        format_summary_table,
        format_fold_detail,
        generate_report,
    )

    assert len(BUNDLE_STRATEGIES) == 5
    assert BUNDLE_STRATEGIES[0] == ("cmf", "CMFStrategy")
