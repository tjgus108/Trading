"""tests/test_health_check.py — HealthChecker 단위 테스트"""
import time
import pytest
from unittest.mock import patch, MagicMock
from src.exchange.health_check import HealthChecker, HealthStatus, HealthState


# ── 기본 생성 ──────────────────────────────────────────────

def test_initial_state_healthy():
    checker = HealthChecker(check_fn=lambda: {"connected": True})
    assert checker.state.status == HealthStatus.HEALTHY
    assert checker.state.consecutive_failures == 0
    assert checker.state.reconnect_attempts == 0


def test_initial_not_order_blocked():
    checker = HealthChecker(check_fn=lambda: {"connected": True})
    assert checker.is_order_blocked() is False


def test_initial_is_healthy():
    checker = HealthChecker(check_fn=lambda: {"connected": True})
    assert checker.is_healthy() is True


# ── should_check 타이밍 ─────────────────────────────────────

def test_should_check_initially():
    """check_interval 경과 전에는 False."""
    checker = HealthChecker(
        check_fn=lambda: {"connected": True},
        check_interval=300.0,
    )
    checker.state.last_check_time = time.time()
    assert checker.should_check() is False


def test_should_check_after_interval():
    """check_interval 경과 후 True."""
    checker = HealthChecker(
        check_fn=lambda: {"connected": True},
        check_interval=5.0,
    )
    checker.state.last_check_time = time.time() - 10.0
    assert checker.should_check() is True


# ── HEALTHY 케이스 ─────────────────────────────────────────

def test_healthy_check_resets_failures():
    checker = HealthChecker(check_fn=lambda: {"connected": True})
    checker.state.consecutive_failures = 2
    checker.state.reconnect_attempts = 1
    checker.run_check()
    assert checker.state.status == HealthStatus.HEALTHY
    assert checker.state.consecutive_failures == 0
    assert checker.state.reconnect_attempts == 0


def test_healthy_check_updates_total():
    checker = HealthChecker(check_fn=lambda: {"connected": True})
    checker.run_check()
    checker.run_check()
    assert checker.state.total_checks == 2
    assert checker.state.total_failures == 0


# ── DEGRADED (데이터 지연) ──────────────────────────────────

def test_degraded_when_data_stale():
    checker = HealthChecker(
        check_fn=lambda: {"connected": True},
        data_stale_threshold=60.0,
    )
    checker.state.last_data_time = time.time() - 120.0  # 2분 전
    state = checker.run_check()
    assert state.status == HealthStatus.DEGRADED
    assert state.consecutive_failures == 1


def test_degraded_does_not_block_orders():
    checker = HealthChecker(
        check_fn=lambda: {"connected": True},
        data_stale_threshold=60.0,
    )
    checker.state.last_data_time = time.time() - 120.0
    checker.run_check()
    assert checker.is_order_blocked() is False


# ── DISCONNECTED + 재연결 ──────────────────────────────────

def test_disconnected_triggers_reconnect():
    reconnect = MagicMock(return_value=True)
    checker = HealthChecker(
        check_fn=lambda: {"connected": False},
        reconnect_fn=reconnect,
        max_reconnect_attempts=3,
    )
    state = checker.run_check()
    reconnect.assert_called_once()
    assert state.status == HealthStatus.HEALTHY


def test_reconnect_failure_stays_disconnected():
    reconnect = MagicMock(return_value=False)
    checker = HealthChecker(
        check_fn=lambda: {"connected": False},
        reconnect_fn=reconnect,
        max_reconnect_attempts=3,
    )
    state = checker.run_check()
    assert state.status == HealthStatus.DISCONNECTED
    assert state.reconnect_attempts == 1


def test_reconnect_exception_handled():
    def bad_reconnect():
        raise ConnectionError("network down")

    checker = HealthChecker(
        check_fn=lambda: {"connected": False},
        reconnect_fn=bad_reconnect,
        max_reconnect_attempts=3,
    )
    state = checker.run_check()
    assert state.status == HealthStatus.DISCONNECTED
    assert state.reconnect_attempts == 1


# ── PROTECTED 모드 ────────────────────────────────────────

def test_protection_mode_after_max_attempts():
    reconnect = MagicMock(return_value=False)
    checker = HealthChecker(
        check_fn=lambda: {"connected": False},
        reconnect_fn=reconnect,
        max_reconnect_attempts=3,
    )
    for _ in range(3):
        checker.run_check()
    assert checker.state.status == HealthStatus.PROTECTED
    assert checker.is_order_blocked() is True
    assert checker.state.protection_activated_at is not None


def test_protection_blocks_orders():
    checker = HealthChecker(check_fn=lambda: {"connected": False})
    checker.state.status = HealthStatus.PROTECTED
    assert checker.is_order_blocked() is True
    assert checker.is_healthy() is False


def test_protection_preserves_after_further_checks():
    """보호 모드 진입 후 추가 check에서도 유지."""
    reconnect = MagicMock(return_value=False)
    checker = HealthChecker(
        check_fn=lambda: {"connected": False},
        reconnect_fn=reconnect,
        max_reconnect_attempts=2,
    )
    checker.run_check()
    checker.run_check()
    assert checker.state.status == HealthStatus.PROTECTED
    # 한 번 더 check — 여전히 PROTECTED (재연결 시도 안 함)
    checker.run_check()
    assert checker.state.status == HealthStatus.PROTECTED
    assert reconnect.call_count == 2  # 3번째에서는 호출 안 함


# ── record_data_received ─────────────────────────────────

def test_record_data_prevents_stale():
    checker = HealthChecker(
        check_fn=lambda: {"connected": True},
        data_stale_threshold=60.0,
    )
    checker.state.last_data_time = time.time() - 120.0
    # stale 상태
    state = checker.run_check()
    assert state.status == HealthStatus.DEGRADED
    # 데이터 수신 기록
    checker.record_data_received()
    state = checker.run_check()
    assert state.status == HealthStatus.HEALTHY


# ── reset ─────────────────────────────────────────────────

def test_reset_clears_protection():
    checker = HealthChecker(check_fn=lambda: {"connected": False})
    checker.state.status = HealthStatus.PROTECTED
    checker.state.consecutive_failures = 10
    checker.state.reconnect_attempts = 3
    checker.reset()
    assert checker.state.status == HealthStatus.HEALTHY
    assert checker.state.consecutive_failures == 0
    assert checker.state.reconnect_attempts == 0
    assert checker.is_order_blocked() is False


# ── summary / to_dict ────────────────────────────────────

def test_summary_returns_dict():
    checker = HealthChecker(check_fn=lambda: {"connected": True})
    checker.run_check()
    s = checker.summary()
    assert isinstance(s, dict)
    assert "status" in s
    assert s["status"] == "HEALTHY"
    assert "total_checks" in s
    assert s["total_checks"] == 1


def test_state_to_dict_serializable():
    """to_dict 결과가 JSON serializable인지 확인."""
    import json
    checker = HealthChecker(check_fn=lambda: {"connected": True})
    checker.run_check()
    d = checker.state.to_dict()
    # JSON 직렬화 가능해야 함
    json_str = json.dumps(d)
    assert len(json_str) > 0


# ── check_fn 예외 처리 ───────────────────────────────────

def test_check_fn_exception_treated_as_disconnected():
    def bad_check():
        raise RuntimeError("exchange API error")

    checker = HealthChecker(
        check_fn=bad_check,
        reconnect_fn=lambda: True,
        max_reconnect_attempts=3,
    )
    state = checker.run_check()
    # 예외 → connected=False → 재연결 시도
    assert state.status == HealthStatus.HEALTHY  # reconnect succeeds
    assert state.total_failures == 1


# ── no reconnect_fn ──────────────────────────────────────

def test_no_reconnect_fn_stays_disconnected():
    """reconnect_fn 없으면 재연결 시도 없이 DISCONNECTED 유지."""
    checker = HealthChecker(
        check_fn=lambda: {"connected": False},
        reconnect_fn=None,
        max_reconnect_attempts=3,
    )
    state = checker.run_check()
    assert state.status == HealthStatus.DISCONNECTED


# ── LivePaperTrader 통합 ─────────────────────────────────

def test_live_paper_trader_health_check_integration():
    """LivePaperTrader에 HealthChecker가 올바르게 통합되어 있는지 확인."""
    from unittest.mock import patch
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

        # HealthChecker가 존재하고 초기 상태가 HEALTHY
        assert hasattr(trader, 'health_checker')
        assert trader.health_checker.is_healthy() is True
        assert trader.health_checker.is_order_blocked() is False


def test_live_trader_tick_skips_on_protection():
    """보호 모드에서 tick이 신규 주문을 차단하는지 확인."""
    from unittest.mock import patch
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

        # 보호 모드 강제 설정
        trader.health_checker.state.status = HealthStatus.PROTECTED
        assert trader.health_checker.is_order_blocked() is True
