"""tests/test_drawdown_monitor.py — DrawdownMonitor 3층 서킷브레이커 테스트."""
import pytest
from src.risk.drawdown_monitor import AlertLevel, DrawdownMonitor, MddLevel


# ── 기존 MDD 동작 유지 ────────────────────────────────────────

def test_legacy_mdd_halts():
    """기준 잔고 미설정 시 legacy MDD 로직으로 차단."""
    m = DrawdownMonitor(max_drawdown_pct=0.15)
    m.update(10000)
    status = m.update(8400)   # 16% 낙폭
    assert status.halted is True
    assert "MDD" in status.reason


def test_no_halt_within_mdd():
    m = DrawdownMonitor(max_drawdown_pct=0.15)
    m.update(10000)
    status = m.update(9000)   # 10% 낙폭 — 한계 미만
    assert status.halted is False


def test_force_resume_clears_halt():
    m = DrawdownMonitor(max_drawdown_pct=0.10)
    m.update(10000)
    m.update(8900)            # 11% → halted
    assert m.is_halted()
    m.force_resume()
    assert not m.is_halted()


# ── 일일 3% 경고 ──────────────────────────────────────────────

def test_daily_warning_triggers():
    """일일 낙폭 3% 초과 시 WARNING + halted."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_daily_start(10000)
    status = m.update(9650)   # 3.5% 일일 낙폭
    assert status.halted is True
    assert status.alert_level == AlertLevel.WARNING
    assert "일일" in status.reason


def test_daily_no_warning_below_limit():
    """일일 낙폭이 한계 미만이면 경고 없음."""
    m = DrawdownMonitor(daily_limit=0.03)
    m.set_daily_start(10000)
    status = m.update(9750)   # 2.5% — 한계 미만
    assert status.halted is False
    assert status.alert_level == AlertLevel.NONE


def test_daily_reset_clears_warning():
    """reset_daily() 호출 시 WARNING 해제."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_daily_start(10000)
    m.update(9650)            # WARNING 발생
    assert m.is_halted()
    m.reset_daily(9650)       # 다음날 시작
    assert not m.is_halted()
    assert m.alert_level() == AlertLevel.NONE


# ── 주간 7% 거래 중단 ─────────────────────────────────────────

def test_weekly_halt_triggers():
    """주간 낙폭 7% 초과 시 HALT."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_weekly_start(10000)
    m.set_daily_start(9400)   # 일일 기준 낮게 설정 — daily_dd < 3%
    status = m.update(9200)   # 주간 8% 낙폭
    assert status.halted is True
    assert status.alert_level == AlertLevel.HALT
    assert "주간" in status.reason


def test_weekly_drawdown_pct_in_status():
    """DrawdownStatus에 weekly_drawdown_pct 값이 정확히 반영."""
    m = DrawdownMonitor(weekly_limit=0.07)
    m.set_weekly_start(10000)
    status = m.update(9300)   # 7% 주간 낙폭
    assert abs(status.weekly_drawdown_pct - 0.07) < 1e-6


# ── 월간 15% 강제 청산 ────────────────────────────────────────

def test_monthly_force_liquidate_triggers():
    """월간 낙폭 15% 초과 시 FORCE_LIQUIDATE."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_monthly_start(10000)
    m.set_weekly_start(9000)   # 주간 낙폭 < 7%
    m.set_daily_start(8700)    # 일일 낙폭 < 3%
    status = m.update(8400)    # 월간 16% 낙폭
    assert status.halted is True
    assert status.alert_level == AlertLevel.FORCE_LIQUIDATE
    assert "월간" in status.reason
    assert "강제 청산" in status.reason


def test_force_liquidate_not_auto_cleared():
    """FORCE_LIQUIDATE는 자동 해제되지 않는다."""
    m = DrawdownMonitor(monthly_limit=0.15, max_drawdown_pct=0.20, recovery_pct=0.05)
    m.set_monthly_start(10000)
    m.update(8400)             # FORCE_LIQUIDATE 발생
    # 자산이 회복되어도 유지
    status = m.update(9900)
    assert status.halted is True
    assert status.alert_level == AlertLevel.FORCE_LIQUIDATE


def test_force_resume_clears_force_liquidate():
    """force_resume()은 FORCE_LIQUIDATE도 해제한다."""
    m = DrawdownMonitor(monthly_limit=0.15)
    m.set_monthly_start(10000)
    m.update(8400)
    assert m.alert_level() == AlertLevel.FORCE_LIQUIDATE
    m.force_resume()
    assert not m.is_halted()
    assert m.alert_level() == AlertLevel.NONE


# ── 우선순위: 월간 > 주간 > 일일 ────────────────────────────

def test_monthly_takes_priority_over_daily():
    """일일·주간·월간 동시 초과 시 FORCE_LIQUIDATE 우선."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_daily_start(10000)
    m.set_weekly_start(10000)
    m.set_monthly_start(10000)
    status = m.update(8000)    # 모두 초과
    assert status.alert_level == AlertLevel.FORCE_LIQUIDATE


def test_daily_weekly_simultaneous_weekly_wins():
    """일일+주간 동시 초과 시 주간(HALT)이 우선."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_daily_start(10000)
    m.set_weekly_start(10000)
    # 월간 기준 미설정 → monthly_dd=0
    status = m.update(9200)    # 일일 8% > 3%, 주간 8% > 7%
    assert status.halted is True
    assert status.alert_level == AlertLevel.HALT
    assert "주간" in status.reason
    assert status.daily_drawdown_pct > m.daily_limit
    assert status.weekly_drawdown_pct > m.weekly_limit


def test_force_liquidate_not_cleared_by_reset_daily():
    """FORCE_LIQUIDATE 상태에서 reset_daily() 호출해도 해제 안 됨."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_monthly_start(10000)
    m.set_daily_start(10000)
    m.update(8400)             # 월간 16% → FORCE_LIQUIDATE
    assert m.alert_level() == AlertLevel.FORCE_LIQUIDATE
    m.reset_daily(8400)        # 일일 리셋 시도
    assert m.is_halted() is True
    assert m.alert_level() == AlertLevel.FORCE_LIQUIDATE


# ── set_daily_start / set_weekly_start 리셋 후 새 기간 추적 ──

def test_set_daily_start_resets_tracking():
    """set_daily_start 호출 후 새 기준으로 일일 낙폭 재계산."""
    m = DrawdownMonitor(daily_limit=0.03)
    m.set_daily_start(10000)
    m.update(9650)              # 3.5% → WARNING 발생
    assert m.is_halted()

    # 다음날: set_daily_start로 기준 갱신, 경고는 reset_daily로만 해제
    m.reset_daily(9650)         # 경고 해제 + 새 일일 기준 9650
    assert not m.is_halted()

    status = m.update(9370)     # 9650 대비 ~2.9% 낙폭 → 경고 없음
    assert status.halted is False
    assert abs(status.daily_drawdown_pct - (9650 - 9370) / 9650) < 1e-6


def test_set_weekly_start_resets_tracking():
    """set_weekly_start 호출 후 새 주간 기준으로 낙폭 재계산."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_weekly_start(10000)
    m.set_daily_start(9400)
    m.update(9200)              # 주간 8% → HALT 발생
    assert m.is_halted()

    # 다음주: 수동 해제 후 새 주간 기준 설정
    m.force_resume()
    m.set_weekly_start(9200)    # 새 주간 기준
    m.set_daily_start(9200)

    status = m.update(9000)     # 9200 대비 ~2.2% — 주간 한계 미만
    assert status.halted is False
    assert abs(status.weekly_drawdown_pct - (9200 - 9000) / 9200) < 1e-6


# ── 기간별 granularity 추가 테스트 ───────────────────────────

def test_monthly_drawdown_pct_without_daily_weekly_start():
    """월간 기준만 설정 시 daily/weekly_dd=0, monthly_dd만 계산."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_monthly_start(10000)
    # daily_start, weekly_start 미설정
    status = m.update(9000)   # 월간 10% 낙폭 — 한계 미만
    assert status.daily_drawdown_pct == 0.0
    assert status.weekly_drawdown_pct == 0.0
    assert abs(status.monthly_drawdown_pct - 0.10) < 1e-6
    assert status.halted is False


def test_reset_clears_all_period_starts():
    """reset() 호출 후 기간별 기준 잔고가 모두 초기화된다."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_daily_start(10000)
    m.set_weekly_start(10000)
    m.set_monthly_start(10000)
    m.update(8000)   # 모든 기간 한계 초과 → FORCE_LIQUIDATE
    assert m.is_halted()

    m.reset()
    status = m.update(9500)   # reset 후 기준 없으므로 기간별 dd=0
    assert status.halted is False
    assert status.daily_drawdown_pct == 0.0
    assert status.weekly_drawdown_pct == 0.0
    assert status.monthly_drawdown_pct == 0.0


# ── 직렬화 round-trip ─────────────────────────────────────────

def test_to_dict_from_dict_roundtrip():
    """to_dict → from_dict 후 상태 동일."""
    m = DrawdownMonitor(max_drawdown_pct=0.15, daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_daily_start(10000)
    m.set_weekly_start(10000)
    m.set_monthly_start(10000)
    m.update(10000)
    m.update(9650)  # WARNING 발생

    d = m.to_dict()
    m2 = DrawdownMonitor.from_dict(d)

    assert m2.is_halted() == m.is_halted()
    assert m2.alert_level() == m.alert_level()
    assert m2.current_drawdown() == m.current_drawdown()
    assert m2._peak == m._peak
    assert m2._daily_start == m._daily_start
    assert m2._weekly_start == m._weekly_start
    assert m2._monthly_start == m._monthly_start


def test_from_dict_halted_force_liquidate():
    """FORCE_LIQUIDATE 상태도 복원된다."""
    m = DrawdownMonitor(monthly_limit=0.15)
    m.set_monthly_start(10000)
    m.update(8400)
    assert m.alert_level() == AlertLevel.FORCE_LIQUIDATE

    m2 = DrawdownMonitor.from_dict(m.to_dict())
    assert m2.is_halted() is True
    assert m2.alert_level() == AlertLevel.FORCE_LIQUIDATE


# ── 에스컬레이션 (WARNING -> HALT -> FORCE_LIQUIDATE) ──────────────────────────

def test_warning_escalates_to_halt():
    """WARNING 상태에서 주간 낙폭 초과 시 HALT로 에스컬레이션 (이전 버그: 잘못 해제됨)."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_daily_start(10000)
    m.set_weekly_start(10000)

    s1 = m.update(9650)   # daily 3.5% -> WARNING
    assert s1.alert_level == AlertLevel.WARNING
    assert s1.halted is True

    s2 = m.update(9200)   # weekly 8% -> 에스컬레이션 HALT
    assert s2.halted is True, "halted이어야 함 — 이전 버그: 잘못 해제됨"
    assert s2.alert_level == AlertLevel.HALT


def test_halt_escalates_to_force_liquidate():
    """HALT 상태에서 월간 낙폭 초과 시 FORCE_LIQUIDATE로 에스컬레이션."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_weekly_start(10000)
    m.set_monthly_start(10000)

    # 주간 8% -> HALT
    m.update(9200)
    assert m.alert_level() == AlertLevel.HALT

    # 월간 16% -> FORCE_LIQUIDATE
    s = m.update(8400)
    assert s.alert_level == AlertLevel.FORCE_LIQUIDATE
    assert s.halted is True


def test_no_false_resume_when_conditions_still_active():
    """기존 티어드 조건이 활성인 동안 자동 해제되지 않는다."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15,
                        max_drawdown_pct=0.20, recovery_pct=0.05)
    m.set_daily_start(10000)
    m.set_weekly_start(10000)

    m.update(9650)   # WARNING (daily 3.5%)
    s = m.update(9200)  # weekly 8% -> should escalate, NOT resume
    assert s.halted is True
    assert s.alert_level == AlertLevel.HALT


# ── 연속 손실 + 쿨다운 ────────────────────────────────────────

def test_size_multiplier_normal():
    """연속 손실 없으면 size_multiplier=1.0."""
    m = DrawdownMonitor(loss_streak_threshold=3)
    assert m.get_size_multiplier() == 1.0


def test_size_multiplier_halved_after_streak():
    """연속 손실 3회 도달 시 size_multiplier=0.5."""
    m = DrawdownMonitor(loss_streak_threshold=3)
    m.record_trade_result(pnl=-100, equity=9900)
    m.record_trade_result(pnl=-100, equity=9800)
    assert m.get_size_multiplier() == 1.0   # 2회 아직 미달
    m.record_trade_result(pnl=-100, equity=9700)
    assert m.consecutive_losses == 3
    assert m.get_size_multiplier() == 0.5


def test_size_multiplier_resets_on_win():
    """손실 후 수익 1회면 연속 손실 초기화 → size_multiplier=1.0."""
    m = DrawdownMonitor(loss_streak_threshold=3)
    for _ in range(3):
        m.record_trade_result(pnl=-100, equity=9700)
    assert m.get_size_multiplier() == 0.5
    m.record_trade_result(pnl=200, equity=9900)
    assert m.consecutive_losses == 0
    assert m.get_size_multiplier() == 1.0


def test_cooldown_blocks_trade_after_large_loss():
    """단일 손실 >= single_loss_halt_pct → 쿨다운 중 size_multiplier=0.0."""
    m = DrawdownMonitor(single_loss_halt_pct=0.02, cooldown_seconds=3600)
    # equity=10000, loss=300 → loss_pct=3% >= 2% → 쿨다운 시작
    m.record_trade_result(pnl=-300, equity=10000)
    assert m.is_in_cooldown() is True
    assert m.get_size_multiplier() == 0.0


def test_small_loss_no_cooldown():
    """단일 손실 < single_loss_halt_pct → 쿨다운 없음."""
    m = DrawdownMonitor(single_loss_halt_pct=0.02, cooldown_seconds=3600)
    m.record_trade_result(pnl=-100, equity=10000)   # 1% < 2%
    assert m.is_in_cooldown() is False


def test_update_reflects_size_multiplier():
    """update() 결과에 size_multiplier, consecutive_losses, cooldown_active 반영."""
    m = DrawdownMonitor(loss_streak_threshold=3)
    m.record_trade_result(pnl=-100, equity=9700)
    m.record_trade_result(pnl=-100, equity=9600)
    m.record_trade_result(pnl=-100, equity=9500)
    status = m.update(9500)
    assert status.consecutive_losses == 3
    assert status.size_multiplier == 0.5
    assert status.cooldown_active is False


def test_to_dict_from_dict_includes_new_state():
    """to_dict/from_dict round-trip이 새 필드 포함."""
    m = DrawdownMonitor(loss_streak_threshold=3, cooldown_seconds=1800)
    m.record_trade_result(pnl=-100, equity=9900)
    m.record_trade_result(pnl=-100, equity=9800)
    d = m.to_dict()
    m2 = DrawdownMonitor.from_dict(d)
    assert m2.consecutive_losses == 2
    assert m2.loss_streak_threshold == 3
    assert m2.cooldown_seconds == 1800


# ── 4단계 MDD 레벨 단위 테스트 ────────────────────────────────────


def test_mdd_level_normal():
    """MDD < 5% → NORMAL, multiplier=1.0."""
    m = DrawdownMonitor()
    m.update(10000)
    m.update(9600)  # 4% < 5%
    assert m.get_mdd_level() == MddLevel.NORMAL
    assert m.get_mdd_size_multiplier() == 1.0
    assert m.should_liquidate_all() is False


def test_mdd_level_warn():
    """5% <= MDD < 10% → WARN, multiplier=0.5."""
    m = DrawdownMonitor()
    m.update(10000)
    m.update(9300)  # 7%
    assert m.get_mdd_level() == MddLevel.WARN
    assert m.get_mdd_size_multiplier() == 0.5
    assert m.should_liquidate_all() is False


def test_mdd_level_block_entry():
    """10% <= MDD < 15% → BLOCK_ENTRY, multiplier=0.0."""
    m = DrawdownMonitor()
    m.update(10000)
    m.update(8800)  # 12%
    assert m.get_mdd_level() == MddLevel.BLOCK_ENTRY
    assert m.get_mdd_size_multiplier() == 0.0
    assert m.should_liquidate_all() is False


def test_mdd_level_liquidate_and_full_halt():
    """15% <= MDD < 20% → LIQUIDATE; MDD >= 20% → FULL_HALT. 둘 다 should_liquidate_all=True."""
    m = DrawdownMonitor()
    m.update(10000)
    m.update(8300)  # 17% → LIQUIDATE
    assert m.get_mdd_level() == MddLevel.LIQUIDATE
    assert m.should_liquidate_all() is True

    m.update(7900)  # 21% → FULL_HALT
    assert m.get_mdd_level() == MddLevel.FULL_HALT
    assert m.should_liquidate_all() is True


def test_to_dict_from_dict_mdd_and_streak_cooldown():
    """to_dict/from_dict round-trip이 streak_cooldown_seconds + MDD 파라미터 보존."""
    m = DrawdownMonitor(
        streak_cooldown_seconds=7200,
        mdd_warn_pct=0.06,
        mdd_block_pct=0.12,
        mdd_liquidate_pct=0.18,
        mdd_halt_pct=0.25,
    )
    m.update(10000)
    m.update(9200)  # 8% → WARN with custom thresholds (>6%)

    d = m.to_dict()
    m2 = DrawdownMonitor.from_dict(d)

    assert m2.streak_cooldown_seconds == 7200
    assert m2.mdd_warn_pct == 0.06
    assert m2.mdd_block_pct == 0.12
    assert m2.mdd_liquidate_pct == 0.18
    assert m2.mdd_halt_pct == 0.25
    assert m2.get_mdd_level() == m.get_mdd_level()
    assert m2.current_drawdown() == m.current_drawdown()
