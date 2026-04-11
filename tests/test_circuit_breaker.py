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



def test_reset_all_clears_consecutive_losses_and_cooldown():
    """reset_all() 후 _consecutive_losses와 _cooldown_remaining이 0으로 초기화."""
    cb = CircuitBreaker(max_consecutive_losses=3, cooldown_periods=2)
    for _ in range(3):
        cb.record_trade_result(is_loss=True)
    assert cb.consecutive_losses == 3
    assert cb.cooldown_remaining == 2
    cb.reset_all()
    assert cb.consecutive_losses == 0
    assert cb.cooldown_remaining == 0
    assert cb.is_triggered is False


def test_reset_all_allows_check_after_flash_crash_trigger():
    """플래시 크래시로 _triggered=True 된 뒤 reset_all() 하면 다음 check() 정상 통과."""
    cb = CircuitBreaker(flash_crash_pct=0.10)
    result = cb.check(
        current_balance=10000.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
        candle_open=50000.0,
        candle_close=44000.0,
    )
    assert result["triggered"] is True
    cb.reset_all()
    result2 = cb.check(
        current_balance=9900.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
    )
    assert result2["triggered"] is False
    assert result2["size_multiplier"] == 1.0

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


# ── 통합: 다중 조건 동시 트리거 ────────────────────────────────
def test_flash_crash_takes_priority_over_drawdown_and_atr_and_cooldown():
    """
    통합 시나리오 1: 플래시 크래시 + 일일 낙폭 초과 + ATR surge + 연속 손실 쿨다운 동시 발생
    → 우선순위: flash_crash 최우선, triggered=True, reason에 '플래시 크래시' 포함
    """
    cb = CircuitBreaker(
        daily_drawdown_limit=0.05,
        total_drawdown_limit=0.15,
        atr_surge_multiplier=2.0,
        flash_crash_pct=0.10,
        max_consecutive_losses=3,
        cooldown_periods=2,
    )
    # 연속 손실 쿨다운 활성화
    for _ in range(3):
        cb.record_trade_result(is_loss=True)

    result = cb.check(
        current_balance=9300.0,      # 일일 낙폭 7% (> 5% limit)
        peak_balance=10000.0,
        daily_start_balance=10000.0,
        current_atr=0.06,            # ATR surge: 6% vs baseline 2% = 3x
        baseline_atr=0.02,
        candle_open=50000.0,
        candle_close=44000.0,        # 플래시 크래시 -12%
    )
    assert result["triggered"] is True
    assert result["size_multiplier"] == 0.0
    assert "플래시 크래시" in result["reason"], f"reason={result['reason']}"


def test_drawdown_takes_priority_over_cooldown_and_atr_surge():
    """
    통합 시나리오 2: 일일 낙폭 초과 + ATR surge + 연속 손실 쿨다운 동시 발생 (플래시 크래시 없음)
    → 우선순위: drawdown > cooldown > ATR, triggered=True, reason에 '일일' 포함
    """
    cb = CircuitBreaker(
        daily_drawdown_limit=0.05,
        total_drawdown_limit=0.15,
        atr_surge_multiplier=2.0,
        flash_crash_pct=0.10,
        max_consecutive_losses=3,
        cooldown_periods=2,
    )
    # 연속 손실 쿨다운 활성화
    for _ in range(3):
        cb.record_trade_result(is_loss=True)

    result = cb.check(
        current_balance=9400.0,      # 일일 낙폭 6% (> 5% limit)
        peak_balance=10000.0,
        daily_start_balance=10000.0,
        current_atr=0.06,            # ATR surge 조건 충족
        baseline_atr=0.02,
        candle_open=50000.0,
        candle_close=50200.0,        # 캔들 변동 0.4% — 플래시 크래시 아님
    )
    assert result["triggered"] is True
    assert result["size_multiplier"] == 0.0
    assert "일일" in result["reason"], f"reason={result['reason']}"
    # ATR surge는 낙폭에 묻혀 표현되지 않음
    assert "플래시 크래시" not in result["reason"]


# ── 통합: 5가지 조건 전부 순차 검증 ───────────────────────────────
def test_all_five_conditions_integration():
    """
    통합 검증: 5가지 서킷 조건이 각각 독립적으로 정상 작동하는지 순서대로 확인.
    1) 플래시 크래시  → triggered=True, reason='플래시 크래시'
    2) 일일 낙폭 초과 → triggered=True, reason='일일'
    3) 전체 낙폭 초과 → triggered=True, reason='전체'
    4) 연속 손실 쿨다운 → triggered=True, reason='쿨다운'
    5) ATR surge     → triggered=False, volatility_surge=True, size_multiplier=0.5
    """
    BASE = dict(peak_balance=10000.0)

    # ── 조건 1: 플래시 크래시 ───────────────────────────────────────
    cb1 = CircuitBreaker(flash_crash_pct=0.10)
    r1 = cb1.check(
        current_balance=10000.0,
        daily_start_balance=10000.0,
        candle_open=50000.0,
        candle_close=44000.0,   # -12%
        **BASE,
    )
    assert r1["triggered"] is True, "조건1 실패: 플래시 크래시 미감지"
    assert r1["size_multiplier"] == 0.0
    assert "플래시 크래시" in r1["reason"]

    # ── 조건 2: 일일 낙폭 ───────────────────────────────────────────
    cb2 = CircuitBreaker(daily_drawdown_limit=0.05)
    r2 = cb2.check(
        current_balance=9490.0,  # -5.1% daily
        daily_start_balance=10000.0,
        **BASE,
    )
    assert r2["triggered"] is True, "조건2 실패: 일일 낙폭 미감지"
    assert "일일" in r2["reason"]
    assert r2["size_multiplier"] == 0.0

    # ── 조건 3: 전체 낙폭 ───────────────────────────────────────────
    cb3 = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    r3 = cb3.check(
        current_balance=8490.0,  # total dd ≈16% > 15%; daily_start 근접이므로 daily dd <5%
        daily_start_balance=8500.0,
        **BASE,
    )
    assert r3["triggered"] is True, "조건3 실패: 전체 낙폭 미감지"
    assert "전체" in r3["reason"]
    assert r3["size_multiplier"] == 0.0

    # ── 조건 4: 연속 손실 쿨다운 ────────────────────────────────────
    cb4 = CircuitBreaker(max_consecutive_losses=5, cooldown_periods=3)
    for _ in range(5):
        cb4.record_trade_result(is_loss=True)
    r4 = cb4.check(
        current_balance=9900.0,
        daily_start_balance=10000.0,
        **BASE,
    )
    assert r4["triggered"] is True, "조건4 실패: 쿨다운 미감지"
    assert "쿨다운" in r4["reason"]
    assert cb4.cooldown_remaining == 3
    assert r4["size_multiplier"] == 0.0

    # ── 조건 5: ATR 변동성 급등 (차단 아님, 축소만) ─────────────────
    cb5 = CircuitBreaker(atr_surge_multiplier=2.0)
    r5 = cb5.check(
        current_balance=9900.0,
        daily_start_balance=10000.0,
        current_atr=0.05,    # 기준 2%의 2.5배 → surge
        baseline_atr=0.02,
        **BASE,
    )
    assert r5["triggered"] is False, "조건5 실패: ATR surge가 완전 차단해선 안 됨"
    assert r5["volatility_surge"] is True
    assert r5["size_multiplier"] == 0.5
    assert "ATR 급등" in r5["reason"]
