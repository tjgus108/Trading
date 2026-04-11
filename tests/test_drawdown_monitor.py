"""tests/test_drawdown_monitor.py — DrawdownMonitor 3층 서킷브레이커 테스트."""
import pytest
from src.risk.drawdown_monitor import AlertLevel, DrawdownMonitor


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
