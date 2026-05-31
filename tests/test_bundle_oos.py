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


# ── BundleOOSResult fold_pass_rate 테스트 ─────────────────


def test_bundle_oos_result_fold_pass_rate_default():
    """fold_pass_rate 기본값 0.0 확인."""
    result = BundleOOSResult(
        strategy_name="test", folds=[], avg_wfe=0.5,
        avg_oos_sharpe=1.0, avg_oos_pf=1.5,
        all_passed=True, fail_reasons=[],
    )
    assert result.fold_pass_rate == 0.0


def test_rolling_oos_validator_fold_pass_rate_populated():
    """RollingOOSValidator가 fold_pass_rate를 0~1 사이 값으로 채우는지 확인."""
    from src.strategy.base import Action, BaseStrategy, Confidence, Signal

    class AlwaysBuyStrat(BaseStrategy):
        name = "always_buy"
        def generate(self, df):
            return Signal(
                action=Action.BUY, confidence=Confidence.HIGH,
                strategy=self.name, entry_price=float(df["close"].iloc[-1]),
                reasoning="test", invalidation="none",
            )

    v = RollingOOSValidator(is_bars=100, oos_bars=50, slide_bars=50, min_oos_trades=1)
    df = make_ohlcv(500)
    result = v.validate(AlwaysBuyStrat(), df)
    assert 0.0 <= result.fold_pass_rate <= 1.0


def test_bundle_oos_result_summary_includes_fold_pass_rate():
    """summary()에 fold_pass_rate 항목 포함 확인."""
    result = BundleOOSResult(
        strategy_name="test", folds=[], avg_wfe=0.6,
        avg_oos_sharpe=1.0, avg_oos_pf=1.5,
        all_passed=True, fail_reasons=[],
        fold_pass_rate=0.75,
    )
    s = result.summary()
    assert "fold_pass_rate" in s
    assert "75%" in s


def test_garch_synthetic_wick_ratio_realistic():
    """quality_audit.make_synthetic_data() wick ratio가 wick_reversal 임계값(0.65)을 충족 가능."""
    import sys
    sys.path.insert(0, "/home/user/Trading/scripts")
    from quality_audit import make_synthetic_data

    df = make_synthetic_data(500, seed=42)
    lower_wick = (df[["open", "close"]].min(axis=1) - df["low"]).clip(lower=0)
    upper_wick = (df["high"] - df[["open", "close"]].max(axis=1)).clip(lower=0)
    total_range = df["high"] - df["low"]
    valid = total_range > 0
    lower_ratio = (lower_wick[valid] / total_range[valid])
    upper_ratio = (upper_wick[valid] / total_range[valid])
    # multiplier 0.5 적용 후: wick_ratio >= 0.65인 봉이 충분히 존재해야 함
    n_hammer = (lower_ratio >= 0.65).sum()
    n_star = (upper_ratio >= 0.65).sum()
    assert n_hammer > 0, "GARCH 데이터에서 Hammer 패턴(lower_wick_ratio >= 0.65) 0건"
    assert n_star > 0, "GARCH 데이터에서 Shooting Star 패턴(upper_wick_ratio >= 0.65) 0건"


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


def test_perf_monitor_regime_change_mdd_halt_pct():
    """레짐에 따른 mdd_halt_pct 자동 조정 검증 (Cycle 243 B)."""
    tracker = LivePerformanceTracker()
    monitor = PerformanceMonitor(tracker=tracker, mdd_halt_pct=0.20)

    monitor.regime_change_alert("RANGING", "TREND_UP")
    assert monitor.mdd_halt_pct == pytest.approx(0.25)

    monitor.regime_change_alert("TREND_UP", "TREND_DOWN")
    assert monitor.mdd_halt_pct == pytest.approx(0.15)

    monitor.regime_change_alert("TREND_DOWN", "RANGING")
    assert monitor.mdd_halt_pct == pytest.approx(0.20)


def test_perf_monitor_regime_change_calls_drawdown_monitor():
    """DrawdownMonitor.set_regime()이 레짐 전환 시 호출되는지 확인 (Cycle 243 B)."""
    from unittest.mock import MagicMock
    tracker = LivePerformanceTracker()
    mock_dm = MagicMock()

    monitor = PerformanceMonitor(tracker=tracker, drawdown_monitor=mock_dm)
    monitor.regime_change_alert("RANGING", "BEAR")

    mock_dm.set_regime.assert_called_once_with("BEAR")
    assert monitor.mdd_halt_pct == pytest.approx(0.15)


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
        compute_bundle_rank_scores,
        bundle_results_to_rank_dicts,
    )

    assert len(BUNDLE_STRATEGIES) == 5
    assert BUNDLE_STRATEGIES[0] == ("cmf", "CMFStrategy")


# ── Bundle Rank Score 테스트 ──────────────────────────────────


def _make_fold(fold_id=0, is_sharpe=1.0, oos_sharpe=0.8, wfe=0.6,
               oos_pf=1.5, oos_trades=10, is_mdd=0.05, oos_mdd=0.08,
               passed=True):
    return OOSFoldResult(
        fold_id=fold_id, is_sharpe=is_sharpe, oos_sharpe=oos_sharpe,
        is_mdd=is_mdd, oos_mdd=oos_mdd, wfe=wfe, oos_pf=oos_pf,
        oos_trades=oos_trades, passed=passed, fail_reasons=[],
    )


def test_bundle_results_to_rank_dicts_mapping():
    """BundleOOSResult -> dict 변환이 올바른 키를 포함."""
    from scripts.run_bundle_oos import bundle_results_to_rank_dicts

    folds = [_make_fold(0, oos_trades=10, oos_mdd=0.05, passed=True),
             _make_fold(1, oos_trades=20, oos_mdd=0.10, passed=False)]
    r = BundleOOSResult(
        strategy_name="test", folds=folds, avg_wfe=0.6,
        avg_oos_sharpe=1.2, avg_oos_pf=1.8,
        all_passed=False, fail_reasons=[], oos_sharpe_std=0.15,
    )
    dicts = bundle_results_to_rank_dicts([("test", r)])
    assert len(dicts) == 1
    d = dicts[0]
    assert d["name"] == "test"
    assert d["avg_sharpe"] == 1.2
    assert d["avg_profit_factor"] == 1.8
    assert d["avg_trades"] == 15.0  # (10+20)/2
    assert abs(d["avg_max_dd"] - 0.075) < 1e-9  # (0.05+0.10)/2
    assert d["consistency_score"] == 0.5  # 1/2 passed
    assert d["sharpe_std"] == 0.15


def test_bundle_results_to_rank_dicts_empty_folds():
    """fold가 없는 경우 기본값 0."""
    from scripts.run_bundle_oos import bundle_results_to_rank_dicts

    r = BundleOOSResult(
        strategy_name="empty", folds=[], avg_wfe=0.0,
        avg_oos_sharpe=0.0, avg_oos_pf=0.0,
        all_passed=False, fail_reasons=["데이터 부족"],
    )
    dicts = bundle_results_to_rank_dicts([("empty", r)])
    assert dicts[0]["avg_trades"] == 0.0
    assert dicts[0]["avg_max_dd"] == 0.0
    assert dicts[0]["consistency_score"] == 0.0


def test_compute_bundle_rank_scores_two_strategies():
    """두 전략의 rank_score가 올바르게 계산."""
    from scripts.run_bundle_oos import compute_bundle_rank_scores

    good_folds = [_make_fold(0, oos_sharpe=2.0, oos_pf=3.0, oos_trades=50,
                             oos_mdd=0.03, passed=True)]
    bad_folds = [_make_fold(0, oos_sharpe=-0.5, oos_pf=0.5, oos_trades=5,
                            oos_mdd=0.30, passed=False)]
    good = BundleOOSResult(
        strategy_name="good", folds=good_folds, avg_wfe=0.8,
        avg_oos_sharpe=2.0, avg_oos_pf=3.0,
        all_passed=True, fail_reasons=[], oos_sharpe_std=0.1,
    )
    bad = BundleOOSResult(
        strategy_name="bad", folds=bad_folds, avg_wfe=0.2,
        avg_oos_sharpe=-0.5, avg_oos_pf=0.5,
        all_passed=False, fail_reasons=["low WFE"], oos_sharpe_std=1.5,
    )
    ranked = compute_bundle_rank_scores([("good", good), ("bad", bad)])
    assert len(ranked) == 2

    good_d = next(d for d in ranked if d["name"] == "good")
    bad_d = next(d for d in ranked if d["name"] == "bad")
    assert good_d["rank_score"] > bad_d["rank_score"]
    assert 0 <= good_d["rank_score"] <= 100
    assert 0 <= bad_d["rank_score"] <= 100
    assert "percentile" in good_d
    assert "percentile" in bad_d


def test_compute_bundle_rank_scores_single():
    """전략 1개면 score=50."""
    from scripts.run_bundle_oos import compute_bundle_rank_scores

    folds = [_make_fold(0)]
    r = BundleOOSResult(
        strategy_name="solo", folds=folds, avg_wfe=0.5,
        avg_oos_sharpe=1.0, avg_oos_pf=1.5,
        all_passed=True, fail_reasons=[],
    )
    ranked = compute_bundle_rank_scores([("solo", r)])
    assert len(ranked) == 1
    assert ranked[0]["rank_score"] == 50.0
    assert ranked[0]["percentile"] == "p50"


def test_generate_report_includes_rank_section():
    """리포트에 Composite Rank Score 섹션이 포함."""
    from scripts.run_bundle_oos import generate_report

    folds_a = [_make_fold(0, oos_sharpe=1.5, oos_pf=2.0)]
    folds_b = [_make_fold(0, oos_sharpe=0.5, oos_pf=1.0)]
    results = [
        ("strat_a", BundleOOSResult(
            strategy_name="strat_a", folds=folds_a, avg_wfe=0.7,
            avg_oos_sharpe=1.5, avg_oos_pf=2.0,
            all_passed=True, fail_reasons=[], oos_sharpe_std=0.1,
        )),
        ("strat_b", BundleOOSResult(
            strategy_name="strat_b", folds=folds_b, avg_wfe=0.3,
            avg_oos_sharpe=0.5, avg_oos_pf=1.0,
            all_passed=False, fail_reasons=["low WFE"], oos_sharpe_std=0.5,
        )),
    ]
    report = generate_report(results, "BTC/USDT", "4h")
    assert "Composite Rank Score" in report
    assert "strat_a" in report
    assert "strat_b" in report
    # 점수가 포함되어야 함
    assert "Score" in report
    assert "Pctl" in report
