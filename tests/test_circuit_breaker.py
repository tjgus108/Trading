"""tests/test_circuit_breaker.py — CircuitBreaker 단위 테스트"""
import pytest
from src.risk.circuit_breaker import CircuitBreaker


# ── 기본 생성 ──────────────────────────────────────────────
def test_default_limits():
    cb = CircuitBreaker()
    assert cb.daily_drawdown_limit == 0.05
    assert cb.total_drawdown_limit == 0.15


def test_not_triggered_on_init():
    cb = CircuitBreaker()
    assert cb.is_triggered is False


# ── 정상 범위 ──────────────────────────────────────────────
def test_no_trigger_within_limits():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    result = cb.check(
        current_balance=9800.0,   # -2% daily
        peak_balance=10000.0,     # -2% total
        daily_start_balance=10000.0,
    )
    assert result["triggered"] is False
    assert result["reason"] == ""


# ── 일일 낙폭 트리거 ───────────────────────────────────────
def test_daily_drawdown_triggers_at_limit():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    result = cb.check(
        current_balance=9500.0,   # exactly -5% daily
        peak_balance=10000.0,
        daily_start_balance=10000.0,
    )
    assert result["triggered"] is True
    assert "일일" in result["reason"]


def test_daily_drawdown_triggers_above_limit():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    result = cb.check(
        current_balance=9400.0,   # -6% daily
        peak_balance=10000.0,
        daily_start_balance=10000.0,
    )
    assert result["triggered"] is True
    assert result["drawdown_pct"] > 0.05


# ── 전체 낙폭 트리거 ───────────────────────────────────────
def test_total_drawdown_triggers_at_limit():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    # daily_start=8600: daily dd = (8600-8500)/8600 ≈ 1.16% < 5%, total dd = 15%
    result = cb.check(
        current_balance=8500.0,
        peak_balance=10000.0,
        daily_start_balance=8600.0,
    )
    assert result["triggered"] is True
    assert "전체" in result["reason"]


def test_total_drawdown_triggers_above_limit():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    result = cb.check(
        current_balance=8000.0,   # -20% total
        peak_balance=10000.0,
        daily_start_balance=9800.0,
    )
    assert result["triggered"] is True


# ── reset_daily ────────────────────────────────────────────
def test_reset_daily_clears_daily_trigger():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    cb.check(current_balance=9400.0, peak_balance=10000.0, daily_start_balance=10000.0)
    assert cb.is_triggered is True
    cb.reset_daily(daily_start_balance=9400.0)
    assert cb.is_triggered is False


def test_reset_daily_keeps_total_trigger():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    # total 낙폭으로만 트리거: daily_start=8500 → daily dd=(8500-8400)/8500≈1.2%<5%
    cb.check(current_balance=8400.0, peak_balance=10000.0, daily_start_balance=8500.0)
    assert cb.is_triggered is True
    assert "전체" in cb._reason
    cb.reset_daily(daily_start_balance=8400.0)
    # 전체 낙폭 트리거는 유지
    assert cb.is_triggered is True


def test_reset_all_clears_everything():
    cb = CircuitBreaker()
    cb.check(current_balance=8000.0, peak_balance=10000.0, daily_start_balance=10000.0)
    cb.reset_all()
    assert cb.is_triggered is False
    result = cb.check(current_balance=9800.0, peak_balance=10000.0, daily_start_balance=10000.0)
    assert result["triggered"] is False


# ── 변동성 급등 (ATR surge) ────────────────────────────────
def test_atr_surge_returns_half_size_multiplier():
    """ATR이 기준의 2배 이상 → triggered=False, size_multiplier=0.5, volatility_surge=True"""
    cb = CircuitBreaker(atr_surge_multiplier=2.0)
    result = cb.check(
        current_balance=9900.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
        current_atr=0.04,   # 4% — 기준 2%의 2배
        baseline_atr=0.02,
    )
    assert result["triggered"] is False
    assert result["volatility_surge"] is True
    assert result["size_multiplier"] == 0.5
    assert "ATR 급등" in result["reason"]


def test_atr_below_surge_threshold_no_effect():
    """ATR이 기준의 1.9배 → 급등 아님, 정상 통과"""
    cb = CircuitBreaker(atr_surge_multiplier=2.0)
    result = cb.check(
        current_balance=9900.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
        current_atr=0.038,   # 1.9배 < 2.0
        baseline_atr=0.02,
    )
    assert result["triggered"] is False
    assert result["volatility_surge"] is False
    assert result["size_multiplier"] == 1.0


def test_atr_surge_does_not_override_drawdown_trigger():
    """낙폭 조건 먼저 트리거되면 ATR surge는 무관 — triggered=True, size_multiplier=0.0"""
    cb = CircuitBreaker(daily_drawdown_limit=0.05, atr_surge_multiplier=2.0)
    result = cb.check(
        current_balance=9400.0,   # -6% daily
        peak_balance=10000.0,
        daily_start_balance=10000.0,
        current_atr=0.10,
        baseline_atr=0.02,
    )
    assert result["triggered"] is True
    assert result["size_multiplier"] == 0.0
    assert "일일" in result["reason"]


def test_atr_surge_without_atr_args_no_effect():
    """current_atr/baseline_atr 미전달 시 ATR 체크 스킵"""
    cb = CircuitBreaker(atr_surge_multiplier=2.0)
    result = cb.check(
        current_balance=9900.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
    )
    assert result["triggered"] is False
    assert result["volatility_surge"] is False
    assert result["size_multiplier"] == 1.0


# ── 상관관계 축소 (Correlation Throttle) ────────────────────
def _make_tracker_with_high_corr():
    """상관계수 ≥ 0.7인 두 전략이 포함된 트래커 반환."""
    from src.analysis.strategy_correlation import SignalCorrelationTracker
    from src.strategy.base import Action

    tracker = SignalCorrelationTracker(["s1", "s2"])
    # 혼합 패턴으로 분산 확보 → 완전 양의 상관 (r=1.0)
    pattern = [Action.BUY, Action.BUY, Action.SELL, Action.BUY, Action.HOLD]
    for i in range(20):
        action = pattern[i % len(pattern)]
        tracker.record("s1", action)
        tracker.record("s2", action)
    return tracker


def test_corr_throttle_sets_07_multiplier():
    """상관계수 ≥ 0.7 → triggered=False, correlation_throttle=True, size_multiplier=0.7"""
    cb = CircuitBreaker(corr_threshold=0.7, correlation_tracker=_make_tracker_with_high_corr())
    result = cb.check(
        current_balance=9900.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
    )
    assert result["triggered"] is False
    assert result["correlation_throttle"] is True
    assert result["size_multiplier"] == 0.7
    assert "상관관계" in result["reason"]


def test_corr_throttle_no_effect_below_threshold():
    """상관계수가 threshold 미만 → 정상 통과"""
    from src.analysis.strategy_correlation import SignalCorrelationTracker
    from src.strategy.base import Action

    tracker = SignalCorrelationTracker(["s1", "s2"])
    # 교차 신호 → 낮은 상관
    for i in range(20):
        tracker.record("s1", Action.BUY if i % 2 == 0 else Action.SELL)
        tracker.record("s2", Action.SELL if i % 2 == 0 else Action.BUY)

    cb = CircuitBreaker(corr_threshold=0.7, correlation_tracker=tracker)
    result = cb.check(
        current_balance=9900.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
    )
    assert result["correlation_throttle"] is False
    assert result["size_multiplier"] == 1.0


def test_corr_throttle_and_atr_surge_uses_lower_multiplier():
    """ATR surge + correlation throttle 동시 → size_multiplier=0.5 (더 보수적)"""
    cb = CircuitBreaker(
        atr_surge_multiplier=2.0,
        corr_threshold=0.7,
        correlation_tracker=_make_tracker_with_high_corr(),
    )
    result = cb.check(
        current_balance=9900.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
        current_atr=0.04,
        baseline_atr=0.02,
    )
    assert result["triggered"] is False
    assert result["volatility_surge"] is True
    assert result["correlation_throttle"] is True
    assert result["size_multiplier"] == 0.5


# ── 플래시 크래시 감지 ──────────────────────────────────────
def test_flash_crash_down_triggers():
    """단일 캔들 10% 이상 하락 → triggered=True, size_multiplier=0.0"""
    cb = CircuitBreaker(flash_crash_pct=0.10)
    result = cb.check(
        current_balance=10000.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
        candle_open=50000.0,
        candle_close=44000.0,  # -12%
    )
    assert result["triggered"] is True
    assert result["size_multiplier"] == 0.0
    assert "플래시 크래시" in result["reason"]


def test_flash_crash_up_triggers():
    """단일 캔들 10% 이상 상승도 플래시 크래시로 감지 (abs 사용)"""
    cb = CircuitBreaker(flash_crash_pct=0.10)
    result = cb.check(
        current_balance=10000.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
        candle_open=50000.0,
        candle_close=56000.0,  # +12%
    )
    assert result["triggered"] is True
    assert "플래시 크래시" in result["reason"]


def test_flash_crash_below_threshold_no_trigger():
    """캔들 변동 9% → 한계 미만, 정상 통과"""
    cb = CircuitBreaker(flash_crash_pct=0.10)
    result = cb.check(
        current_balance=10000.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
        candle_open=50000.0,
        candle_close=45500.0,  # -9%
    )
    assert result["triggered"] is False


def test_flash_crash_omitted_no_effect():
    """candle_open/candle_close 미전달 시 플래시 크래시 체크 스킵"""
    cb = CircuitBreaker(flash_crash_pct=0.10)
    result = cb.check(
        current_balance=10000.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
    )
    assert result["triggered"] is False


# ── 연속 손실 쿨다운 ────────────────────────────────────────
def _cb_with_cooldown(max_losses: int = 3, cooldown: int = 2) -> CircuitBreaker:
    return CircuitBreaker(max_consecutive_losses=max_losses, cooldown_periods=cooldown)


def test_cooldown_blocks_after_consecutive_losses():
    """연속 손실 3회 → 쿨다운 시작, check() triggered=True"""
    cb = _cb_with_cooldown(max_losses=3, cooldown=2)
    for _ in range(3):
        cb.record_trade_result(is_loss=True)
    result = cb.check(
        current_balance=9900.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
    )
    assert result["triggered"] is True
    assert "쿨다운" in result["reason"]
    assert result["size_multiplier"] == 0.0
    assert cb.cooldown_remaining == 2


def test_cooldown_expires_after_tick():
    """tick_cooldown 2회 후 쿨다운 해제, 이후 check() 정상 통과"""
    cb = _cb_with_cooldown(max_losses=3, cooldown=2)
    for _ in range(3):
        cb.record_trade_result(is_loss=True)

    cb.tick_cooldown()
    assert cb.cooldown_remaining == 1
    cb.tick_cooldown()
    assert cb.cooldown_remaining == 0
    assert cb.consecutive_losses == 0  # 쿨다운 종료 시 초기화

    result = cb.check(
        current_balance=9900.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
    )
    assert result["triggered"] is False


def test_win_resets_consecutive_losses():
    """손실 2회 후 수익 → 연속 손실 카운터 0으로 초기화"""
    cb = _cb_with_cooldown(max_losses=3, cooldown=2)
    cb.record_trade_result(is_loss=True)
    cb.record_trade_result(is_loss=True)
    assert cb.consecutive_losses == 2
    cb.record_trade_result(is_loss=False)
    assert cb.consecutive_losses == 0
    assert cb.cooldown_remaining == 0
