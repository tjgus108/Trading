"""
tests/test_paper_trader_regime.py — RegimeDetector + PaperTrader 통합 테스트
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd
import pytest

from src.exchange.paper_trader import PaperTrader
from src.ml.regime_detector import RegimeDetector
from src.strategy.regime_router import RegimeStrategyRouter


# ── helpers ────────────────────────────────────────────────────────────────────

def _make_ohlcv(n: int = 100, regime: str = "TREND") -> pd.DataFrame:
    """테스트용 OHLCV DataFrame 생성. regime에 맞는 ADX/ATR 특성 부여."""
    np.random.seed(42)
    if regime == "TREND":
        # 강한 추세 → ADX > 25 유발
        close = np.linspace(100.0, 140.0, n)  # 40% 상승 추세
    elif regime == "CRISIS":
        # 고변동성 → ATR > 2*MA(ATR)
        close = 100.0 + np.cumsum(np.random.randn(n) * 5.0)  # 큰 변동폭
    else:  # RANGE
        close = 100.0 + np.random.randn(n) * 0.05  # 매우 좁은 횡보
    high = close * 1.002
    low = close * 0.998
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000.0,
    })


def _make_trader_with_regime(regime_detector=None, regime_router=None,
                              performance_monitor=None) -> PaperTrader:
    return PaperTrader(
        initial_balance=10000.0,
        fee_rate=0.0,
        slippage_pct=0.0,
        partial_fill_prob=0.0,
        timeout_prob=0.0,
        regime_detector=regime_detector,
        regime_router=regime_router,
        performance_monitor=performance_monitor,
    )


# ── 1. 기본 동작 (RegimeDetector 없음) ────────────────────────────────────────

def test_no_regime_detector_default_regime():
    """RegimeDetector 없이 생성 시 current_regime='RANGE'."""
    pt = _make_trader_with_regime()
    assert pt.current_regime == "RANGE"


def test_no_regime_detector_update_returns_default():
    """RegimeDetector 없을 때 update_regime()은 현재 레짐 그대로 반환."""
    pt = _make_trader_with_regime()
    df = _make_ohlcv()
    result = pt.update_regime(df)
    assert result == "RANGE"


def test_no_regime_scale_is_1():
    """RegimeDetector 없을 때 position scale = 1.0."""
    pt = _make_trader_with_regime()
    assert pt.get_position_scale() == 1.0


def test_no_regime_router_skip_is_false():
    """RegimeRouter 없을 때 should_skip_strategy = False."""
    pt = _make_trader_with_regime()
    assert pt.should_skip_strategy("any_strategy") is False


# ── 2. update_regime 동작 ──────────────────────────────────────────────────────

def test_update_regime_calls_detector():
    """update_regime()이 RegimeDetector.detect()를 호출."""
    mock_detector = MagicMock()
    mock_detector.detect.return_value = "TREND"
    pt = _make_trader_with_regime(regime_detector=mock_detector)
    df = _make_ohlcv()
    regime = pt.update_regime(df)
    mock_detector.detect.assert_called_once_with(df)
    assert regime == "TREND"


def test_update_regime_updates_current_regime():
    """update_regime() 후 current_regime이 갱신됨."""
    mock_detector = MagicMock()
    mock_detector.detect.return_value = "CRISIS"
    pt = _make_trader_with_regime(regime_detector=mock_detector)
    assert pt.current_regime == "RANGE"
    pt.update_regime(_make_ohlcv())
    assert pt.current_regime == "CRISIS"


def test_update_regime_no_change_no_callback():
    """레짐이 바뀌지 않으면 performance_monitor 콜백 호출 안 됨."""
    mock_detector = MagicMock()
    mock_detector.detect.return_value = "RANGE"  # 초기값과 같음
    mock_monitor = MagicMock()
    pt = _make_trader_with_regime(regime_detector=mock_detector,
                                  performance_monitor=mock_monitor)
    pt.update_regime(_make_ohlcv())
    mock_monitor.regime_change_alert.assert_not_called()


def test_update_regime_change_triggers_callback():
    """레짐 전환 시 PerformanceMonitor.regime_change_alert() 호출."""
    mock_detector = MagicMock()
    mock_detector.detect.return_value = "TREND"
    mock_monitor = MagicMock()
    pt = _make_trader_with_regime(regime_detector=mock_detector,
                                  performance_monitor=mock_monitor)
    pt.update_regime(_make_ohlcv())
    mock_monitor.regime_change_alert.assert_called_once_with("RANGE", "TREND")


def test_update_regime_crisis_transition():
    """TREND → CRISIS 전환 시 콜백 인자 확인."""
    mock_detector = MagicMock()
    mock_monitor = MagicMock()
    pt = _make_trader_with_regime(regime_detector=mock_detector,
                                  performance_monitor=mock_monitor)

    mock_detector.detect.return_value = "TREND"
    pt.update_regime(_make_ohlcv())
    assert pt.current_regime == "TREND"

    mock_detector.detect.return_value = "CRISIS"
    pt.update_regime(_make_ohlcv())
    assert pt.current_regime == "CRISIS"
    assert mock_monitor.regime_change_alert.call_count == 2
    last_call = mock_monitor.regime_change_alert.call_args_list[-1]
    # Python 3.7 compatible: call_args is a (args, kwargs) tuple
    assert last_call[0] == ("TREND", "CRISIS")


# ── 3. CRISIS 포지션 스케일링 ──────────────────────────────────────────────────

def test_crisis_position_scale_is_half():
    """CRISIS 레짐 시 get_position_scale() = 0.5."""
    mock_detector = MagicMock()
    mock_detector.detect.return_value = "CRISIS"
    pt = _make_trader_with_regime(regime_detector=mock_detector)
    pt.update_regime(_make_ohlcv())
    assert pt.get_position_scale() == 0.5


def test_trend_position_scale_is_one():
    """TREND 레짐 시 get_position_scale() = 1.0."""
    mock_detector = MagicMock()
    mock_detector.detect.return_value = "TREND"
    pt = _make_trader_with_regime(regime_detector=mock_detector)
    pt.update_regime(_make_ohlcv())
    assert pt.get_position_scale() == 1.0


def test_crisis_halves_buy_quantity():
    """CRISIS 레짐에서 BUY 수량이 자동으로 0.5배 적용됨."""
    mock_detector = MagicMock()
    mock_detector.detect.return_value = "CRISIS"
    pt = _make_trader_with_regime(regime_detector=mock_detector)
    pt._current_regime = "CRISIS"  # 직접 강제 설정

    result = pt.execute_signal("BTC/USDT", "BUY", price=100.0, quantity=10.0,
                               strategy="cmf", confidence="HIGH")
    assert result["status"] == "filled"
    # actual_quantity should be 5.0 (10 * 0.5)
    assert abs(result["actual_quantity"] - 5.0) < 1e-6


def test_trend_buy_quantity_unchanged():
    """TREND 레짐에서 BUY 수량 변경 없음."""
    mock_detector = MagicMock()
    mock_detector.detect.return_value = "TREND"
    pt = _make_trader_with_regime(regime_detector=mock_detector)
    pt._current_regime = "TREND"

    result = pt.execute_signal("BTC/USDT", "BUY", price=100.0, quantity=10.0,
                               strategy="cmf", confidence="HIGH")
    assert result["status"] == "filled"
    assert abs(result["actual_quantity"] - 10.0) < 1e-6


def test_crisis_sell_quantity_not_scaled():
    """CRISIS 레짐에서 SELL은 스케일링 적용 안 됨."""
    pt = PaperTrader(
        initial_balance=50000.0, fee_rate=0.0, slippage_pct=0.0,
        partial_fill_prob=0.0, timeout_prob=0.0,
    )
    pt._current_regime = "CRISIS"
    # Buy first (no detector to scale)
    pt.execute_signal("BTC/USDT", "BUY", price=100.0, quantity=5.0,
                      strategy="cmf", confidence="H")
    result = pt.execute_signal("BTC/USDT", "SELL", price=110.0, quantity=5.0,
                               strategy="cmf", confidence="H")
    assert result["status"] == "filled"
    assert result["actual_quantity"] == 5.0  # SELL 수량 그대로


# ── 4. RegimeStrategyRouter 통합 ──────────────────────────────────────────────

def test_range_strategy_skipped_in_trend():
    """TREND 레짐에서 RANGE 전략은 스킵됨."""
    router = RegimeStrategyRouter()
    pt = _make_trader_with_regime(regime_router=router)
    pt._current_regime = "TREND"

    result = pt.execute_signal("BTC/USDT", "BUY", price=100.0, quantity=1.0,
                               strategy="wick_reversal",  # RANGE 전략
                               confidence="HIGH")
    assert result["status"] == "skipped"
    assert "wick_reversal" in result["reason"]
    assert result["regime"] == "TREND"


def test_trend_strategy_active_in_trend():
    """TREND 레짐에서 TREND 전략은 실행됨."""
    router = RegimeStrategyRouter()
    pt = _make_trader_with_regime(regime_router=router)
    pt._current_regime = "TREND"

    result = pt.execute_signal("BTC/USDT", "BUY", price=100.0, quantity=1.0,
                               strategy="cmf",  # TREND 전략
                               confidence="HIGH")
    assert result["status"] == "filled"


def test_crisis_no_strategy_skipped():
    """CRISIS 레짐에서는 어떤 전략도 스킵되지 않음 (position scale만 적용)."""
    router = RegimeStrategyRouter()
    pt = _make_trader_with_regime(regime_router=router)
    pt._current_regime = "CRISIS"

    result = pt.execute_signal("BTC/USDT", "BUY", price=100.0, quantity=1.0,
                               strategy="wick_reversal",
                               confidence="HIGH")
    # CRISIS는 skip 없음 (regime_router.should_skip returns False for CRISIS)
    assert result["status"] == "filled"


def test_sell_not_skipped_in_any_regime():
    """SELL은 레짐 라우터와 무관하게 항상 실행됨."""
    router = RegimeStrategyRouter()
    pt = _make_trader_with_regime(regime_router=router)
    pt._current_regime = "TREND"

    # 먼저 포지션 생성 (라우터 우회)
    pt._regime_router = None
    pt.execute_signal("BTC/USDT", "BUY", price=100.0, quantity=1.0,
                      strategy="wick_reversal", confidence="H")
    pt._regime_router = router

    result = pt.execute_signal("BTC/USDT", "SELL", price=110.0, quantity=1.0,
                               strategy="wick_reversal", confidence="H")
    assert result["status"] == "filled"


# ── 5. execute_signal 반환값에 regime 포함 ────────────────────────────────────

def test_execute_signal_includes_regime():
    """execute_signal() 반환값에 'regime' 키 포함."""
    pt = PaperTrader(
        initial_balance=10000.0, fee_rate=0.0, slippage_pct=0.0,
        partial_fill_prob=0.0, timeout_prob=0.0,
    )
    result = pt.execute_signal("BTC/USDT", "BUY", price=100.0, quantity=1.0,
                               strategy="s", confidence="H")
    assert "regime" in result
    assert result["regime"] == "RANGE"


def test_execute_signal_regime_reflects_current():
    """execute_signal() 반환값의 'regime'이 current_regime과 일치."""
    mock_detector = MagicMock()
    mock_detector.detect.return_value = "TREND"
    pt = _make_trader_with_regime(regime_detector=mock_detector)
    pt.update_regime(_make_ohlcv())

    result = pt.execute_signal("BTC/USDT", "BUY", price=100.0, quantity=1.0,
                               strategy="cmf", confidence="H")
    assert result["regime"] == "TREND"


# ── 6. 실제 RegimeDetector 통합 (E2E) ────────────────────────────────────────

def test_real_regime_detector_update_regime():
    """실제 RegimeDetector 인스턴스로 update_regime() E2E 테스트."""
    detector = RegimeDetector()
    pt = _make_trader_with_regime(regime_detector=detector)

    df = _make_ohlcv(n=100)
    regime = pt.update_regime(df)
    assert regime in ("TREND", "RANGE", "CRISIS")
    assert pt.current_regime == regime


def test_real_regime_router_get_active_strategies():
    """실제 RegimeStrategyRouter로 get_active_strategies() 반환 확인."""
    router = RegimeStrategyRouter()
    pt = _make_trader_with_regime(regime_router=router)
    pt._current_regime = "TREND"

    active = pt.get_active_strategies()
    assert "cmf" in active
    assert "wick_reversal" not in active


def test_full_integration_regime_router_monitor():
    """RegimeDetector + Router + Monitor 전체 통합 시나리오."""
    from src.risk.performance_tracker import PerformanceMonitor, LivePerformanceTracker

    alerts = []

    def on_alert(level: str, msg: str):
        alerts.append((level, msg))

    tracker = LivePerformanceTracker()
    monitor = PerformanceMonitor(tracker=tracker, on_alert=on_alert)
    detector = RegimeDetector()
    router = RegimeStrategyRouter()

    pt = PaperTrader(
        initial_balance=10000.0, fee_rate=0.0, slippage_pct=0.0,
        partial_fill_prob=0.0, timeout_prob=0.0,
        regime_detector=detector,
        regime_router=router,
        performance_monitor=monitor,
    )

    # 초기 레짐 업데이트
    df = _make_ohlcv(n=100, regime="RANGE")
    pt.update_regime(df)

    # TREND 전략 실행 시도 — 라우터에 따라 스킵 여부 결정
    result = pt.execute_signal("BTC/USDT", "BUY", price=100.0, quantity=2.0,
                               strategy="cmf", confidence="H")
    # cmf는 TREND 전략 — 현재 레짐에 따라 filled or skipped
    assert result["status"] in ("filled", "skipped")
    assert "regime" in result
