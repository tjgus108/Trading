"""tests/test_drawdown_monitor.py — DrawdownMonitor 3층 서킷브레이커 테스트."""
import time
from unittest.mock import patch

import pytest
from src.risk.drawdown_monitor import AlertLevel, DrawdownMonitor, MddLevel


# ── set_ranging_macro_neutral — RANGING 레짐 cooldown 배수 ──────

def test_set_ranging_macro_neutral_neutral_slope():
    """|ema50_slope| <= threshold → _ranging_macro_neutral=True (cooldown 단축 0.9x)."""
    m = DrawdownMonitor()
    m.set_ranging_macro_neutral(ema50_slope=0.0003, threshold=0.0005)
    assert m._ranging_macro_neutral is True


def test_set_ranging_macro_neutral_directional_slope():
    """|ema50_slope| > threshold → _ranging_macro_neutral=False (cooldown 연장 1.5x)."""
    m = DrawdownMonitor()
    m.set_ranging_macro_neutral(ema50_slope=0.0008, threshold=0.0005)
    assert m._ranging_macro_neutral is False


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


# ── 롤링 윈도우 MDD ─────────────────────────────────────────

def test_rolling_mdd_zero_on_init():
    """초기 상태: 롤링 MDD = 0."""
    m = DrawdownMonitor()
    assert m.rolling_mdd() == 0.0


def test_rolling_mdd_zero_no_decline():
    """계속 상승하는 경우 롤링 MDD = 0."""
    m = DrawdownMonitor()
    for eq in [10000, 10100, 10200, 10300]:
        m.update(eq)
    assert m.rolling_mdd() == 0.0


def test_rolling_mdd_simple():
    """10000 → 9000: 10% 롤링 MDD."""
    m = DrawdownMonitor()
    m.update(10000)
    m.update(9000)
    assert abs(m.rolling_mdd() - 0.10) < 1e-6


def test_rolling_mdd_partial_recovery():
    """10000 → 9000 → 9500: 최대 낙폭 10% 유지."""
    m = DrawdownMonitor()
    for eq in [10000, 9000, 9500]:
        m.update(eq)
    assert abs(m.rolling_mdd() - 0.10) < 1e-6


def test_rolling_mdd_in_status():
    """DrawdownStatus.rolling_mdd_pct에 값이 반영된다."""
    m = DrawdownMonitor()
    m.update(10000)
    status = m.update(8000)   # 20% 낙폭
    assert abs(status.rolling_mdd_pct - 0.20) < 1e-6


def test_rolling_mdd_window_param():
    """window 파라미터로 최근 N개만 계산."""
    m = DrawdownMonitor()
    # 초반: 10000 → 8000 (20% 낙폭)
    m.update(10000)
    m.update(8000)
    # 회복 후 새로운 최근 구간: 9000 → 8800 (약 2.2% 낙폭)
    m.update(9000)
    status = m.update(8800)
    # 전체 윈도우 MDD는 20%
    assert m.rolling_mdd() >= 0.20
    # 최근 2개 윈도우 MDD는 약 2.2%
    recent_mdd = m.rolling_mdd(window=2)
    assert recent_mdd < 0.05


def test_rolling_mdd_resets_on_reset():
    """reset() 후 롤링 MDD = 0."""
    m = DrawdownMonitor()
    m.update(10000)
    m.update(8000)
    m.reset()
    assert m.rolling_mdd() == 0.0


# ── [B1] Cycle 201: to_dict/from_dict 복원 후 rolling_mdd 정확성 ──────────────

def test_to_dict_includes_equity_history():
    """to_dict()가 _equity_history를 포함해야 한다."""
    m = DrawdownMonitor(rolling_window=10)
    for eq in [10000, 9800, 9600, 10100]:
        m.update(eq)
    d = m.to_dict()
    assert "_equity_history" in d
    assert d["_equity_history"] == [10000.0, 9800.0, 9600.0, 10100.0]


def test_from_dict_restores_rolling_mdd():
    """from_dict() 복원 후 rolling_mdd()가 0이 아닌 올바른 값을 반환해야 한다."""
    m = DrawdownMonitor(rolling_window=10)
    for eq in [10000, 9500, 9200, 9800]:
        m.update(eq)
    expected_mdd = m.rolling_mdd()
    assert expected_mdd > 0.0, "기준 rolling_mdd가 양수여야 함"

    restored = DrawdownMonitor.from_dict(m.to_dict())
    assert abs(restored.rolling_mdd() - expected_mdd) < 1e-9


def test_from_dict_without_equity_history_key_is_safe():
    """이전 버전 직렬화 데이터(_equity_history 키 없음)도 안전하게 복원."""
    m = DrawdownMonitor()
    m.update(10000)
    d = m.to_dict()
    del d["_equity_history"]
    restored = DrawdownMonitor.from_dict(d)
    assert restored.rolling_mdd() == 0.0


# ── streak_recovery_grace_seconds 통합 테스트 ────────────────────────────────


class TestStreakRecoveryGraceSeconds:
    """streak_recovery_grace_seconds 파라미터 통합 테스트.

    마지막 손실 후 grace_seconds 경과 시 consecutive_losses가 자동 초기화되어
    size_multiplier가 0.5 → 1.0으로 복원되는지 검증.
    time.monotonic()을 모킹하여 시간 경과를 시뮬레이션.
    """

    def test_grace_disabled_by_default(self):
        """streak_recovery_grace_seconds=0 (기본값): 시간 경과로 복원 안 됨.

        연속 손실 threshold 도달 후 아무리 시간이 지나도
        win 없이는 consecutive_losses 초기화 안 됨.
        """
        m = DrawdownMonitor(
            loss_streak_threshold=3,
            streak_recovery_grace_seconds=0.0,  # 비활성 (기본)
        )
        # 연속 손실 3회 → size_multiplier=0.5
        for i in range(3):
            m.record_trade_result(pnl=-100, equity=10000 - (i + 1) * 100)
        assert m.consecutive_losses == 3
        assert m.get_size_multiplier() == 0.5

        # 시간이 아무리 지나도 복원 안 됨 (grace 비활성)
        # monotonic을 크게 앞으로 밀어도 복원 없음
        future_time = time.monotonic() + 999999
        with patch("time.monotonic", return_value=future_time):
            assert m.get_size_multiplier() == 0.5
            assert m.consecutive_losses == 3  # 변화 없음

    def test_grace_resets_after_elapsed(self):
        """streak_recovery_grace_seconds=14400 (4시간): 마지막 손실 후 4시간 경과 시 초기화."""
        m = DrawdownMonitor(
            loss_streak_threshold=3,
            streak_recovery_grace_seconds=14400.0,  # 4시간
        )
        # 연속 손실 3회
        base_time = 100000.0  # fixed value avoids float precision loss with large monotonic values
        with patch("time.monotonic", return_value=base_time):
            for i in range(3):
                m.record_trade_result(pnl=-100, equity=10000 - (i + 1) * 100)

        # 마지막 손실 직후: size_multiplier=0.5
        with patch("time.monotonic", return_value=base_time + 1):
            assert m.consecutive_losses == 3
            assert m.get_size_multiplier() == 0.5

        # 2시간 경과: 아직 복원 안 됨 (14400초 미만)
        with patch("time.monotonic", return_value=base_time + 7200):
            assert m.get_size_multiplier() == 0.5
            assert m.consecutive_losses == 3

        # 4시간 경과: 자동 초기화 → size_multiplier=1.0
        with patch("time.monotonic", return_value=base_time + 14400):
            mult = m.get_size_multiplier()
            assert mult == 1.0, f"Expected 1.0 after grace period, got {mult}"
            assert m.consecutive_losses == 0

    def test_grace_not_triggered_below_threshold(self):
        """연속 손실이 threshold 미만이면 grace 로직 미적용."""
        m = DrawdownMonitor(
            loss_streak_threshold=3,
            streak_recovery_grace_seconds=14400.0,
        )
        # 연속 손실 2회 (threshold 미만)
        base_time = 100000.0  # fixed value avoids float precision loss with large monotonic values
        with patch("time.monotonic", return_value=base_time):
            m.record_trade_result(pnl=-100, equity=9900)
            m.record_trade_result(pnl=-100, equity=9800)

        assert m.consecutive_losses == 2
        # threshold 미만이므로 이미 size_multiplier=1.0
        assert m.get_size_multiplier() == 1.0

        # 시간 경과해도 consecutive_losses는 2 유지 (grace 트리거 조건 미충족)
        with patch("time.monotonic", return_value=base_time + 14400):
            assert m.get_size_multiplier() == 1.0
            assert m.consecutive_losses == 2  # 초기화 안 됨

    def test_grace_win_resets_before_time(self):
        """grace 시간 만료 전에 win이 먼저 발생하면 win으로 초기화."""
        m = DrawdownMonitor(
            loss_streak_threshold=3,
            streak_recovery_grace_seconds=14400.0,
        )
        base_time = 100000.0  # fixed value avoids float precision loss with large monotonic values
        with patch("time.monotonic", return_value=base_time):
            for i in range(3):
                m.record_trade_result(pnl=-100, equity=10000 - (i + 1) * 100)

        assert m.consecutive_losses == 3
        # 1시간 후 win 발생 → 즉시 초기화 (grace 만료 전)
        with patch("time.monotonic", return_value=base_time + 3600):
            m.record_trade_result(pnl=200, equity=9900)
            assert m.consecutive_losses == 0
            assert m.get_size_multiplier() == 1.0

    def test_grace_with_update_status_reflects_recovery(self):
        """grace 복원 후 update() 호출 시 DrawdownStatus에 올바르게 반영."""
        m = DrawdownMonitor(
            loss_streak_threshold=3,
            streak_recovery_grace_seconds=14400.0,
        )
        base_time = 100000.0  # fixed value avoids float precision loss with large monotonic values
        with patch("time.monotonic", return_value=base_time):
            m.update(10000)
            for i in range(3):
                m.record_trade_result(pnl=-100, equity=10000 - (i + 1) * 100)

        # grace 전: size_multiplier=0.5
        with patch("time.monotonic", return_value=base_time + 100):
            status_before = m.update(9700)
            assert status_before.size_multiplier == 0.5
            assert status_before.consecutive_losses == 3

        # grace 후: size_multiplier=1.0, consecutive_losses는 get_size_multiplier() 호출 시
        # 초기화되므로 update() 이후 내부 상태는 0이 됨
        with patch("time.monotonic", return_value=base_time + 14400):
            status_after = m.update(9700)
            assert status_after.size_multiplier == 1.0
            # Note: DrawdownStatus.consecutive_losses는 get_size_multiplier() 호출 전에 캡처되므로
            # 첫 번째 update()에서는 아직 3일 수 있음. 핵심은 size_multiplier=1.0 복원.
            # 이후 다시 update()하면 내부 _consecutive_losses=0이 반영됨.
            assert m.consecutive_losses == 0  # 내부 상태는 초기화됨

    def test_grace_new_loss_after_recovery_restarts_count(self):
        """grace로 초기화 후 새 손실 발생 시 consecutive_losses 1부터 재시작."""
        m = DrawdownMonitor(
            loss_streak_threshold=3,
            streak_recovery_grace_seconds=14400.0,
        )
        base_time = 100000.0  # fixed value avoids float precision loss with large monotonic values
        with patch("time.monotonic", return_value=base_time):
            for i in range(3):
                m.record_trade_result(pnl=-100, equity=10000 - (i + 1) * 100)

        # grace 경과 → 초기화
        with patch("time.monotonic", return_value=base_time + 14400):
            assert m.get_size_multiplier() == 1.0
            assert m.consecutive_losses == 0

        # 새 손실 발생 → consecutive_losses=1
        with patch("time.monotonic", return_value=base_time + 14500):
            m.record_trade_result(pnl=-50, equity=9650)
            assert m.consecutive_losses == 1
            assert m.get_size_multiplier() == 1.0  # threshold 미만

    def test_grace_serialization_roundtrip(self):
        """streak_recovery_grace_seconds가 to_dict/from_dict에서 보존."""
        m = DrawdownMonitor(
            loss_streak_threshold=3,
            streak_recovery_grace_seconds=14400.0,
        )
        m.update(10000)
        d = m.to_dict()
        m2 = DrawdownMonitor.from_dict(d)
        assert m2.streak_recovery_grace_seconds == 14400.0


class TestTrailingStopSignal:
    """trailing_stop_signal() — 단기/장기 rolling MDD 가속 감지."""

    def test_no_signal_on_empty_history(self):
        """이력 없으면 항상 False."""
        m = DrawdownMonitor(rolling_window=50)
        assert m.trailing_stop_signal() is False

    def test_no_signal_when_flat(self):
        """equity가 일정하면 short/long MDD 둘 다 0 → False."""
        m = DrawdownMonitor(rolling_window=50)
        for _ in range(60):
            m.update(10000)
        assert m.trailing_stop_signal() is False

    def test_signal_when_short_mdd_accelerates(self):
        """안정 후 급락: 단기 낙폭 속도(short_mdd/20) >> 장기 속도(long_mdd/50) → True."""
        m = DrawdownMonitor(rolling_window=50)
        # 처음 30봉: 완전 안정 (long MDD 기반 분모)
        for _ in range(30):
            m.update(10000)
        # 이후 20봉: 급락 (단기에서만 낙폭 발생)
        for i in range(20):
            m.update(10000 - (i + 1) * 250)  # 5000까지 하락 (50% 단기 낙폭)
        # short_rate = 50%/20 = 2.5%, long_rate = 50%/50 = 1.0% → ratio=2.5 > 1.5
        assert m.trailing_stop_signal(accel_threshold=1.5) is True

    def test_no_signal_when_gradual_decline(self):
        """균일 하락: short_rate ≈ long_rate → accel_threshold=2.0 기준 미달."""
        m = DrawdownMonitor(rolling_window=50)
        # 50봉 균일 하락 (전체 구간에서 동일한 속도)
        for i in range(50):
            m.update(10000 - i * 20)
        # short_rate / long_rate ≈ 1.0 < 2.0 → 신호 없음
        assert m.trailing_stop_signal(accel_threshold=2.0) is False


# ── reset_weekly / reset_monthly 테스트 ───────────────────────


def test_reset_weekly_clears_halt():
    """reset_weekly() 호출 시 HALT 레벨 해제 + weekly_start 갱신."""
    m = DrawdownMonitor(weekly_limit=0.05)
    m.set_weekly_start(10000)
    m.update(9400)  # 6% 주간 낙폭 → HALT
    assert m.is_halted() is True
    assert m.alert_level() == AlertLevel.HALT

    m.reset_weekly(9400)
    assert m.is_halted() is False
    assert m.alert_level() == AlertLevel.NONE


def test_reset_weekly_does_not_clear_force_liquidate():
    """reset_weekly()는 FORCE_LIQUIDATE 상태를 해제하지 않는다."""
    m = DrawdownMonitor(monthly_limit=0.10)
    m.set_monthly_start(10000)
    m.update(8900)  # 11% 월간 낙폭 → FORCE_LIQUIDATE
    assert m.alert_level() == AlertLevel.FORCE_LIQUIDATE

    m.reset_weekly(8900)  # 주간 리셋 시도
    assert m.is_halted() is True
    assert m.alert_level() == AlertLevel.FORCE_LIQUIDATE


def test_reset_weekly_does_not_clear_warning():
    """reset_weekly()는 WARNING 레벨을 해제하지 않는다 (reset_daily()만 해제)."""
    m = DrawdownMonitor(daily_limit=0.05)
    m.set_daily_start(10000)
    m.update(9400)  # 6% 일일 낙폭 → WARNING
    assert m.alert_level() == AlertLevel.WARNING

    m.reset_weekly(9400)
    assert m.is_halted() is True
    assert m.alert_level() == AlertLevel.WARNING


def test_set_regime_high_vol_tightens_daily_limit():
    """HIGH_VOL 레짐 설정 시 일일 DD 한도가 2%로 강화된다."""
    # 기본 daily_limit=0.03 — 2% 손실은 WARNING 미발생
    m = DrawdownMonitor(daily_limit=0.03)
    m.set_daily_start(10000)
    m.update(9800)  # 2% 일일 낙폭
    assert m.alert_level() == AlertLevel.NONE

    # HIGH_VOL 전환 후 동일 2% 손실 → _high_vol_daily_limit=0.02 → WARNING 발생
    m.reset_daily(10000)
    m.set_regime("HIGH_VOL")
    m.update(9800)  # 2% 일일 낙폭 ≥ 2% 한도
    assert m.alert_level() == AlertLevel.WARNING


def test_reset_monthly_updates_start_only():
    """reset_monthly()는 monthly_start만 갱신, FORCE_LIQUIDATE는 유지."""
    m = DrawdownMonitor(monthly_limit=0.10)
    m.set_monthly_start(10000)
    m.update(8900)  # FORCE_LIQUIDATE 트리거
    assert m.alert_level() == AlertLevel.FORCE_LIQUIDATE

    m.reset_monthly(8900)  # 자동 해제 안 됨
    assert m.is_halted() is True
    assert m.alert_level() == AlertLevel.FORCE_LIQUIDATE

    # force_resume으로만 해제 가능
    m.force_resume()
    assert m.is_halted() is False


# ── MDD Kill Switch 테스트 ────────────────────────────────────


class TestMddKillSwitch:
    """should_kill_strategy / get_kill_switch_status 테스트."""

    def test_kill_when_exceeds_multiplier(self):
        """current_mdd > backtest_mdd * 1.5 → kill."""
        m = DrawdownMonitor()
        # backtest_mdd=0.10, current_mdd=0.16 → 0.16 > 0.15 → True
        assert m.should_kill_strategy(0.16, 0.10, multiplier=1.5) is True

    def test_no_kill_when_below_multiplier(self):
        """current_mdd <= backtest_mdd * 1.5 → no kill."""
        m = DrawdownMonitor()
        # backtest_mdd=0.10, current_mdd=0.14 → 0.14 < 0.15 → False
        assert m.should_kill_strategy(0.14, 0.10, multiplier=1.5) is False

    def test_no_kill_at_exact_threshold(self):
        """current_mdd == backtest_mdd * multiplier → False (> 가 아닌 ==)."""
        m = DrawdownMonitor()
        assert m.should_kill_strategy(0.15, 0.10, multiplier=1.5) is False

    def test_negative_inputs_abs_processed(self):
        """음수 입력은 abs() 처리."""
        m = DrawdownMonitor()
        # abs(-0.16) > abs(-0.10) * 1.5 → 0.16 > 0.15 → True
        assert m.should_kill_strategy(-0.16, -0.10, multiplier=1.5) is True

    def test_zero_backtest_mdd(self):
        """backtest_mdd=0이면 threshold=0, current_mdd>0이면 kill."""
        m = DrawdownMonitor()
        assert m.should_kill_strategy(0.01, 0.0) is True
        assert m.should_kill_strategy(0.0, 0.0) is False

    def test_custom_multiplier(self):
        """multiplier=2.0 기준."""
        m = DrawdownMonitor()
        # backtest_mdd=0.10, threshold=0.20
        assert m.should_kill_strategy(0.21, 0.10, multiplier=2.0) is True
        assert m.should_kill_strategy(0.19, 0.10, multiplier=2.0) is False

    def test_get_kill_switch_status_basic(self):
        """get_kill_switch_status dict 구조 및 값 검증."""
        m = DrawdownMonitor()
        status = m.get_kill_switch_status(0.16, 0.10, multiplier=1.5)
        assert status["should_kill"] is True
        assert abs(status["current_mdd"] - 0.16) < 1e-9
        assert abs(status["threshold"] - 0.15) < 1e-9
        assert abs(status["ratio"] - 1.6) < 1e-9

    def test_get_kill_switch_status_no_kill(self):
        """threshold 미달 시 should_kill=False."""
        m = DrawdownMonitor()
        status = m.get_kill_switch_status(0.10, 0.10, multiplier=1.5)
        assert status["should_kill"] is False
        assert abs(status["ratio"] - 1.0) < 1e-9

    def test_get_kill_switch_status_zero_backtest(self):
        """backtest_mdd=0일 때 ratio=inf (current>0) 또는 0 (current=0)."""
        m = DrawdownMonitor()
        status = m.get_kill_switch_status(0.05, 0.0)
        assert status["should_kill"] is True
        assert status["ratio"] == float('inf')

        status2 = m.get_kill_switch_status(0.0, 0.0)
        assert status2["should_kill"] is False
        assert status2["ratio"] == 0.0

    def test_get_kill_switch_status_negative_inputs(self):
        """음수 입력이 abs() 처리되어 dict에 양수로 반환."""
        m = DrawdownMonitor()
        status = m.get_kill_switch_status(-0.16, -0.10, multiplier=1.5)
        assert status["current_mdd"] == pytest.approx(0.16)
        assert status["threshold"] == pytest.approx(0.15)

    def test_regime_bear_tightens_kill_threshold(self):
        """BEAR 레짐 시 multiplier가 1.2x로 축소 → 더 빨리 kill."""
        m = DrawdownMonitor()
        # backtest_mdd=0.10, current_mdd=0.13
        # 기본(1.5): threshold=0.15 → no kill
        assert m.should_kill_strategy(0.13, 0.10, multiplier=1.5) is False
        # BEAR(1.2): threshold=0.12 → kill
        assert m.should_kill_strategy(0.13, 0.10, multiplier=1.5, regime="BEAR") is True

    def test_regime_crisis_kills_at_backtest_mdd(self):
        """CRISIS 레짐 시 multiplier=1.0 → backtest MDD 초과 즉시 kill."""
        m = DrawdownMonitor()
        # backtest_mdd=0.10, current_mdd=0.11 (backtest 대비 110%)
        assert m.should_kill_strategy(0.11, 0.10, multiplier=1.5, regime="CRISIS") is True

    def test_regime_bull_unchanged_threshold(self):
        """BULL 레짐 시 multiplier 변화 없음."""
        m = DrawdownMonitor()
        # 기본과 동일: threshold=0.15
        assert m.should_kill_strategy(0.13, 0.10, multiplier=1.5, regime="BULL") is False
        assert m.should_kill_strategy(0.16, 0.10, multiplier=1.5, regime="BULL") is True

    def test_get_kill_switch_status_includes_effective_multiplier(self):
        """get_kill_switch_status에 effective_multiplier 필드 포함."""
        m = DrawdownMonitor()
        status = m.get_kill_switch_status(0.13, 0.10, multiplier=1.5, regime="BEAR")
        assert "effective_multiplier" in status
        assert status["effective_multiplier"] == pytest.approx(1.2)
        assert status["threshold"] == pytest.approx(0.12)
        assert status["should_kill"] is True

    def test_regime_high_vol_kills_at_backtest_mdd(self):
        """HIGH_VOL 레짐 시 effective_mult=1.0 → backtest MDD 초과 즉시 kill."""
        m = DrawdownMonitor()
        # HIGH_VOL cap=1.0 → min(1.5, 1.0)=1.0 → threshold=0.10
        assert m.should_kill_strategy(0.11, 0.10, multiplier=1.5, regime="HIGH_VOL") is True
        assert m.should_kill_strategy(0.10, 0.10, multiplier=1.5, regime="HIGH_VOL") is False

    def test_regime_ranging_tightens_kill_threshold(self):
        """RANGING 레짐 시 cap=1.2 → threshold=0.12."""
        m = DrawdownMonitor()
        # min(1.5, 1.2)=1.2 → threshold=0.12
        assert m.should_kill_strategy(0.13, 0.10, multiplier=1.5, regime="RANGING") is True
        assert m.should_kill_strategy(0.12, 0.10, multiplier=1.5, regime="RANGING") is False

    def test_regime_trend_down_tightens_kill_threshold(self):
        """TREND_DOWN 레짐 시 cap=1.2 → threshold=0.12."""
        m = DrawdownMonitor()
        # min(1.5, 1.2)=1.2 → threshold=0.12
        assert m.should_kill_strategy(0.13, 0.10, multiplier=1.5, regime="TREND_DOWN") is True
        assert m.should_kill_strategy(0.12, 0.10, multiplier=1.5, regime="TREND_DOWN") is False

    def test_regime_unknown_falls_back_to_multiplier(self):
        """알 수 없는 레짐은 multiplier를 그대로 사용."""
        m = DrawdownMonitor()
        # 알 수 없는 레짐 → cap = multiplier → threshold=0.15
        assert m.should_kill_strategy(0.16, 0.10, multiplier=1.5, regime="UNKNOWN") is True
        assert m.should_kill_strategy(0.14, 0.10, multiplier=1.5, regime="UNKNOWN") is False

    def test_get_size_multiplier_mdd_warn_plus_atr_elevated(self):
        """MDD WARN(0.5) + ATR elevated(0.5) → get_size_multiplier = min=0.5."""
        m = DrawdownMonitor(mdd_warn_pct=0.05)
        m.update(10000)
        m.update(9400)  # 6% MDD → WARN → mdd_mult=0.5
        m.set_atr_state(atr=200.0, atr_ma=100.0, threshold=1.5)  # atr_vol_mult=0.5
        # min(streak=1.0, mdd=0.5, atr=0.5, sharpe=1.0) = 0.5
        assert m.get_size_multiplier() == pytest.approx(0.5)

    def test_get_size_multiplier_mdd_block_overrides_streak(self):
        """MDD BLOCK(0.0)은 연속 손실 streak(0.5)보다 우선."""
        m = DrawdownMonitor(mdd_block_pct=0.10, loss_streak_threshold=3)
        m.update(10000)
        m.update(8900)  # 11% MDD → BLOCK_ENTRY → mdd_mult=0.0
        for _ in range(3):
            m.record_trade_result(pnl=-100, equity=8800)  # streak=3 → streak_mult=0.5
        # min(streak=0.5, mdd=0.0, atr=1.0, sharpe=1.0) = 0.0
        assert m.get_size_multiplier() == pytest.approx(0.0)


# ── kelly_reduce_at_mdd 단위 테스트 ──────────────────────────────────────


def test_kelly_fraction_multiplier_normal():
    """MDD < kelly_reduce_at_mdd(8%) → kelly_fraction_multiplier = 1.0."""
    m = DrawdownMonitor(kelly_reduce_at_mdd=0.08)
    m.update(10000)
    m.update(9300)  # 7% MDD < 8%
    assert m.get_kelly_fraction_multiplier() == 1.0
    status = m.update(9300)
    assert status.kelly_fraction_multiplier == 1.0


def test_kelly_fraction_multiplier_reduced():
    """MDD > kelly_reduce_at_mdd(8%) → kelly_fraction_multiplier = 0.5."""
    m = DrawdownMonitor(kelly_reduce_at_mdd=0.08)
    m.update(10000)
    m.update(9100)  # 9% MDD > 8%
    assert m.get_kelly_fraction_multiplier() == 0.5
    status = m.update(9100)
    assert status.kelly_fraction_multiplier == 0.5


def test_kelly_fraction_multiplier_boundary():
    """MDD 정확히 kelly_reduce_at_mdd → 경계에서 0.5 반환 (> 비교, 같으면 1.0)."""
    m = DrawdownMonitor(kelly_reduce_at_mdd=0.08)
    m.update(10000)
    # 정확히 8%: 10000 → 9200 = 8% DD. 조건이 > 이므로 1.0 반환
    m.update(9200)
    assert m.get_kelly_fraction_multiplier() == 1.0


def test_kelly_fraction_multiplier_custom_threshold():
    """custom kelly_reduce_at_mdd=0.12 설정 시 동작 검증."""
    m = DrawdownMonitor(kelly_reduce_at_mdd=0.12)
    m.update(10000)
    m.update(8900)  # 11% < 12% → 1.0
    assert m.get_kelly_fraction_multiplier() == 1.0
    m.update(8700)  # 13% > 12% → 0.5
    assert m.get_kelly_fraction_multiplier() == 0.5


def test_kelly_reduce_at_mdd_to_dict_roundtrip():
    """to_dict/from_dict round-trip이 kelly_reduce_at_mdd 보존."""
    m = DrawdownMonitor(kelly_reduce_at_mdd=0.10)
    m.update(10000)
    d = m.to_dict()
    m2 = DrawdownMonitor.from_dict(d)
    assert m2.kelly_reduce_at_mdd == pytest.approx(0.10)


# ── Transition Cushion ─────────────────────────────────────────

class TestTransitionCushion:
    def test_cushion_disabled_by_default(self):
        """transition_cushion_enabled=False(기본) → 항상 1.0."""
        m = DrawdownMonitor()
        assert m.get_transition_cushion_multiplier(0.5) == 1.0
        assert m.get_transition_cushion_multiplier(0.0) == 1.0

    def test_cushion_low_confidence(self):
        """confidence=0.5 < threshold=0.70 → 0.5."""
        m = DrawdownMonitor(transition_cushion_enabled=True, transition_cushion_threshold=0.70)
        assert m.get_transition_cushion_multiplier(0.5) == 0.5

    def test_cushion_high_confidence(self):
        """confidence=0.8 >= threshold=0.70 → 1.0."""
        m = DrawdownMonitor(transition_cushion_enabled=True, transition_cushion_threshold=0.70)
        assert m.get_transition_cushion_multiplier(0.8) == 1.0

    def test_cushion_boundary(self):
        """confidence=0.70 (경계, 같음) → 1.0 (미만일 때만 적용)."""
        m = DrawdownMonitor(transition_cushion_enabled=True, transition_cushion_threshold=0.70)
        assert m.get_transition_cushion_multiplier(0.70) == 1.0


# ── tiered halt 회복 로직 테스트 (Cycle302 수정 검증) ─────────────────────────


def test_tiered_halt_recovery_faster_than_legacy():
    """tiered(주간) halt가 total_dd > max_drawdown_pct에서 발생하면
    tiered 회복 임계값(halt_drawdown - recovery_pct)이 legacy 임계값보다 낮아
    더 빠른 재개가 가능함을 검증.

    시나리오:
      peak=10000, weekly_start=9500 (이전 주 고점 이후 회복 상태)
      max_drawdown_pct=10%, recovery_pct=2%, weekly_limit=7%
      equity=8835 → weekly_dd=7%, total_dd=11.65% → HALT
      equity=9100 → weekly_dd=4.2%(tiered 해소), total_dd=9%
        tiered: 9% < halt_dd(11.65%) - 2% = 9.65% → RESUME (빠른 재개)
        legacy만: 9% < max_dd(10%) - 2% = 8% → False → 재개 불가
    """
    m = DrawdownMonitor(max_drawdown_pct=0.10, recovery_pct=0.02, weekly_limit=0.07)
    m.update(10000)               # peak = 10000
    m.set_weekly_start(9500)      # weekly_start을 peak 아래로 설정 (mid-week 상태)

    # weekly halt: weekly_dd = (9500-8835)/9500 = 7%, total_dd ≈ 11.65%
    m.update(8835)
    assert m.is_halted() is True
    assert m._tiered_halt is True
    halt_dd = (10000 - 8835) / 10000  # ≈ 0.1165
    assert m._halt_drawdown == pytest.approx(halt_dd, rel=1e-4)

    # equity=9100: weekly_dd=4.2% (tiered 해소), total_dd=9%
    # tiered_recovery_threshold = 11.65% - 2% = 9.65% > 9% → resume
    # legacy 기준(10%-2%=8%) 단독으로는 9% < 8% = False → resume 불가
    m.update(9100)
    assert m.is_halted() is False, (
        "tiered halt should resume when drawdown < halt_drawdown - recovery_pct"
    )


def test_legacy_halt_recovery_unchanged():
    """legacy MDD halt(_tiered_halt=False)는 기존 (max_drawdown_pct - recovery_pct)
    기준만 사용하며, tiered 회복 임계값의 영향을 받지 않음을 검증."""
    m = DrawdownMonitor(max_drawdown_pct=0.10, recovery_pct=0.02)
    m.update(10000)   # peak = 10000

    # legacy MDD halt: daily/weekly/monthly 미설정, total_dd=11% > max_dd(10%)
    m.update(8900)
    assert m.is_halted() is True
    assert m._tiered_halt is False

    # equity=9185: drawdown=8.15%, legacy_threshold=8% → 8.15% > 8% → still halted
    m.update(9185)
    assert m.is_halted() is True, "drawdown 8.15% should still be halted (threshold=8%)"

    # equity=9220: drawdown=7.8% < 8% → resume
    m.update(9220)
    assert m.is_halted() is False, "drawdown 7.8% < legacy threshold 8% → should resume"


def test_tiered_halt_roundtrip_recovery():
    """to_dict → from_dict 직렬화 후 tiered halt의 recovery 동작이 정확한지 검증.

    시나리오:
      1. tiered(주간) halt 유발
      2. to_dict → from_dict로 재시작 시뮬레이션
      3. 복원된 인스턴스에서 recovery 조건 확인
         - halt_drawdown/tiered_halt 정확히 복원됐으면 동일하게 빠른 recovery 작동해야 함
    """
    m = DrawdownMonitor(max_drawdown_pct=0.10, recovery_pct=0.02, weekly_limit=0.07)
    m.update(10000)
    m.set_weekly_start(9500)

    # weekly_dd=7% → tiered HALT
    m.update(8835)
    assert m.is_halted() is True
    assert m._tiered_halt is True
    halt_dd = m._halt_drawdown

    # 직렬화 → 복원
    state = m.to_dict()
    m2 = DrawdownMonitor.from_dict(state)

    # 복원 상태 검증
    assert m2.is_halted() is True
    assert m2._tiered_halt is True
    assert m2._halt_drawdown == pytest.approx(halt_dd, rel=1e-6)

    # 복원된 인스턴스에서 recovery: equity=9100 (weekly_dd=4.2% → tiered 해소, total_dd=9%)
    # tiered_recovery_threshold = halt_dd - 0.02 ≈ 9.65% → 9% < 9.65% → RESUME
    m2.update(9100)
    assert m2.is_halted() is False, (
        "from_dict 복원 후 tiered halt은 동일한 recovery 기준으로 resume되어야 함"
    )


# ── [B] Cycle 308: WARN 히스테리시스 테스트 ─────────────────────────────────────

def test_mdd_warn_hysteresis_prevents_oscillation():
    """MDD가 5% 경계를 반복 교차할 때 WARN → NORMAL 즉각 전환 방지."""
    m = DrawdownMonitor(mdd_warn_pct=0.05, mdd_warn_hysteresis_pct=0.015)
    m.update(10000)

    # MDD 5.1% → WARN 진입
    m.update(9490)  # dd = 5.1%
    assert m.get_mdd_level() == MddLevel.WARN
    assert m.get_mdd_size_multiplier() == 0.5

    # MDD 4.9%로 소폭 회복 → 히스테리시스로 여전히 WARN 유지
    m.update(9510)  # dd = 4.9% (< 5% 이지만 > 5% - 1.5% = 3.5%)
    assert m.get_mdd_level() == MddLevel.WARN, "히스테리시스: 4.9%는 복귀 임계값(3.5%) 미달"
    assert m.get_mdd_size_multiplier() == 0.5

    # MDD 3.4%로 완전 회복 → NORMAL 복귀
    m.update(9660)  # dd = 3.4% (< 3.5%)
    assert m.get_mdd_level() == MddLevel.NORMAL
    assert m.get_mdd_size_multiplier() == 1.0


def test_mdd_warn_hysteresis_no_hysteresis_without_warn_entry():
    """WARN 진입 없이 5% 미만이면 히스테리시스 없이 즉시 NORMAL."""
    m = DrawdownMonitor(mdd_warn_pct=0.05, mdd_warn_hysteresis_pct=0.015)
    m.update(10000)
    m.update(9510)  # dd = 4.9% — WARN 진입 없음
    assert m.get_mdd_level() == MddLevel.NORMAL
    assert m._in_warn_mode is False


def test_mdd_warn_hysteresis_from_dict_preserves_state():
    """to_dict/from_dict 후 _in_warn_mode 및 hysteresis 파라미터 보존."""
    m = DrawdownMonitor(mdd_warn_pct=0.05, mdd_warn_hysteresis_pct=0.02)
    m.update(10000)
    m.update(9490)  # dd=5.1% → WARN
    assert m._in_warn_mode is True

    d = m.to_dict()
    assert d["mdd_warn_hysteresis_pct"] == pytest.approx(0.02)
    assert d["_in_warn_mode"] is True

    m2 = DrawdownMonitor.from_dict(d)
    assert m2.mdd_warn_hysteresis_pct == pytest.approx(0.02)
    assert m2._in_warn_mode is True
    # 복원 후도 히스테리시스 동작: 4.5%는 NORMAL 복귀 임계값(5%-2%=3%) 미달
    m2.update(9550)  # dd=4.5%
    assert m2.get_mdd_level() == MddLevel.WARN


# ── 일중 DD 회복 시나리오 (Cycle366 B 추가) ─────────────────────────────────


def test_daily_dd_halt_releases_when_equity_recovers_intraday():
    """일중 DD가 한도 초과 후 당일 회복 시 halt 자동 해제.

    Cycle366 B: BTC 1h 데이터에서 일중 3%+ 급락 후 반등 시
    WARNING halt가 자동 해제되는지 검증.
    """
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_daily_start(10000)
    m.set_weekly_start(10000)
    m.set_monthly_start(10000)

    # 초기 정상
    m.update(10000)
    assert m.is_halted() is False

    # 일중 3.1% 급락 → WARNING halt
    status = m.update(9690)
    assert status.halted is True
    assert status.alert_level == AlertLevel.WARNING
    assert abs(status.daily_drawdown_pct - 0.031) < 0.001

    # 당일 반등 → daily_dd 2.5%로 회복 → halt 해제
    status_recovered = m.update(9750)
    assert status_recovered.halted is False, (
        "일중 DD 회복 시 WARNING halt가 자동 해제되어야 함"
    )
    assert status_recovered.alert_level == AlertLevel.NONE


def test_weekly_dd_halt_persists_while_dd_exceeds_limit():
    """주간 DD가 한도 초과 상태를 유지하는 동안 HALT가 지속된다.

    Cycle366 B: weekly_dd가 7% 이상인 구간에서 소폭 반등해도 HALT가 유지되고,
    reset_weekly()로 weekly_start를 갱신해야 해제됨을 검증.
    """
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.update(10000)  # peak=10000 설정
    m.set_daily_start(10000)
    m.set_weekly_start(10000)
    m.set_monthly_start(10000)

    # 주간 7.2% 급락 → HALT
    status = m.update(9280)
    assert status.halted is True
    assert status.alert_level == AlertLevel.HALT

    # 소폭 반등 (weekly_dd 여전히 7.1%+) → tiered 체크 여전히 HALT
    status2 = m.update(9290)   # weekly_dd=(10000-9290)/10000=7.1% > 7%
    assert status2.halted is True, "weekly_dd 7.1% 초과 → HALT 유지"
    assert status2.alert_level == AlertLevel.HALT

    # reset_weekly() + reset_daily() 후 weekly/daily start 갱신 → HALT 해제
    m.reset_weekly(9290)
    m.reset_daily(9290)   # daily_start도 갱신해야 daily_dd가 한도 초과 안 함
    status3 = m.update(9300)
    assert status3.halted is False, "reset_weekly() 후 HALT 해제"
    assert status3.alert_level == AlertLevel.NONE


# ── transition_cushion 직렬화/역직렬화 (Cycle357 B 추가, Cycle373 B 검증) ─────

def test_transition_cushion_to_dict_includes_fields():
    """transition_cushion 두 필드가 to_dict()에 포함된다."""
    m = DrawdownMonitor(
        transition_cushion_enabled=True,
        transition_cushion_threshold=0.65,
    )
    d = m.to_dict()
    assert d["transition_cushion_enabled"] is True
    assert abs(d["transition_cushion_threshold"] - 0.65) < 1e-9


def test_transition_cushion_from_dict_roundtrip():
    """from_dict()로 transition_cushion 필드가 정확히 복원된다."""
    m = DrawdownMonitor(
        transition_cushion_enabled=True,
        transition_cushion_threshold=0.65,
    )
    m2 = DrawdownMonitor.from_dict(m.to_dict())
    assert m2.transition_cushion_enabled is True
    assert abs(m2.transition_cushion_threshold - 0.65) < 1e-9


def test_transition_cushion_multiplier_after_restore():
    """복원된 인스턴스에서 get_transition_cushion_multiplier()가 정상 동작한다."""
    m = DrawdownMonitor(
        transition_cushion_enabled=True,
        transition_cushion_threshold=0.70,
    )
    m2 = DrawdownMonitor.from_dict(m.to_dict())
    # confidence < threshold → 0.5x 감쇠
    assert m2.get_transition_cushion_multiplier(0.50) == 0.5
    # confidence >= threshold → 1.0
    assert m2.get_transition_cushion_multiplier(0.90) == 1.0


def test_transition_cushion_disabled_default_after_restore():
    """기본값 transition_cushion_enabled=False: from_dict() 복원 후 항상 1.0 반환."""
    m = DrawdownMonitor()  # transition_cushion_enabled=False 기본값
    m2 = DrawdownMonitor.from_dict(m.to_dict())
    assert m2.transition_cushion_enabled is False
    assert m2.get_transition_cushion_multiplier(0.0) == 1.0
    assert m2.get_transition_cushion_multiplier(0.5) == 1.0
    assert m2.get_transition_cushion_multiplier(1.0) == 1.0


# ── set_atr_state / ATR 변동성 필터 ─────────────────────────────

class TestAtrVolFilter:
    """Cycle386 B(리스크): set_atr_state + atr_vol_multiplier 단위 테스트."""

    def test_normal_atr_returns_1x(self):
        """ATR이 ATR_MA의 1.5배 미만이면 atr_vol_multiplier=1.0."""
        m = DrawdownMonitor()
        m.set_atr_state(atr=100.0, atr_ma=100.0, threshold=1.5)
        assert m.get_atr_vol_multiplier() == 1.0

    def test_elevated_atr_returns_05x(self):
        """ATR이 ATR_MA의 1.5배 이상이면 atr_vol_multiplier=0.5."""
        m = DrawdownMonitor()
        m.set_atr_state(atr=160.0, atr_ma=100.0, threshold=1.5)
        assert m.get_atr_vol_multiplier() == 0.5

    def test_exact_threshold_triggers(self):
        """ATR/ATR_MA == threshold(경계값)이면 elevated로 판정 (>=)."""
        m = DrawdownMonitor()
        m.set_atr_state(atr=150.0, atr_ma=100.0, threshold=1.5)
        assert m.get_atr_vol_multiplier() == 0.5

    def test_zero_atr_ma_resets_to_normal(self):
        """atr_ma=0이면 elevated 불가 — 1.0 반환."""
        m = DrawdownMonitor()
        m.set_atr_state(atr=999.0, atr_ma=0.0, threshold=1.5)
        assert m.get_atr_vol_multiplier() == 1.0

    def test_atr_pct_absolute_trigger(self):
        """atr_pct > atr_pct_threshold이면 상대 배수 무관하게 elevated."""
        m = DrawdownMonitor()
        # atr/atr_ma = 1.1 (threshold=1.5 미만이지만 atr_pct가 임계값 초과)
        m.set_atr_state(atr=110.0, atr_ma=100.0, threshold=1.5,
                        atr_pct=0.07, atr_pct_threshold=0.06)
        assert m.get_atr_vol_multiplier() == 0.5

    def test_atr_pct_below_threshold_no_trigger(self):
        """atr_pct <= atr_pct_threshold이면 절댓값 경로 미작동."""
        m = DrawdownMonitor()
        m.set_atr_state(atr=110.0, atr_ma=100.0, threshold=1.5,
                        atr_pct=0.05, atr_pct_threshold=0.06)
        assert m.get_atr_vol_multiplier() == 1.0

    def test_atr_elevated_reduces_get_size_multiplier(self):
        """ATR elevated 시 get_size_multiplier()도 min()으로 0.5 적용."""
        m = DrawdownMonitor()
        m.update(10000)  # peak=10000, no MDD
        m.set_atr_state(atr=200.0, atr_ma=100.0, threshold=1.5)
        assert m.get_size_multiplier() == 0.5

    def test_atr_status_field_reflects_multiplier(self):
        """DrawdownStatus.atr_vol_multiplier 필드가 set_atr_state 결과와 일치."""
        m = DrawdownMonitor()
        m.set_atr_state(atr=200.0, atr_ma=100.0, threshold=1.5)
        status = m.update(10000)
        assert status.atr_vol_multiplier == 0.5


# ── set_sharpe_decay / Sharpe decay 필터 ────────────────────────

class TestSharpDecayFilter:
    """Cycle386 B(리스크): set_sharpe_decay + sharpe_decay_multiplier 단위 테스트."""

    def test_normal_sharpe_returns_1x(self):
        """OOS/IS 비율이 threshold 이상이면 sharpe_decay_multiplier=1.0."""
        m = DrawdownMonitor()
        m.set_sharpe_decay(recent_sharpe=0.8, historical_sharpe=1.0, threshold=0.50)
        assert m.get_sharpe_decay_multiplier() == 1.0

    def test_decayed_sharpe_returns_05x(self):
        """OOS/IS 비율이 threshold 미만이면 sharpe_decay_multiplier=0.5."""
        m = DrawdownMonitor()
        m.set_sharpe_decay(recent_sharpe=0.3, historical_sharpe=1.0, threshold=0.50)
        assert m.get_sharpe_decay_multiplier() == 0.5

    def test_historical_sharpe_zero_no_decay(self):
        """IS Sharpe=0이면 decay 판정 불가 → 1.0."""
        m = DrawdownMonitor()
        m.set_sharpe_decay(recent_sharpe=-0.5, historical_sharpe=0.0, threshold=0.50)
        assert m.get_sharpe_decay_multiplier() == 1.0

    def test_historical_sharpe_negative_no_decay(self):
        """IS Sharpe 음수이면 decay 판정 불가 → 1.0."""
        m = DrawdownMonitor()
        m.set_sharpe_decay(recent_sharpe=0.1, historical_sharpe=-1.0, threshold=0.50)
        assert m.get_sharpe_decay_multiplier() == 1.0

    def test_exact_threshold_no_decay(self):
        """OOS/IS 비율 == threshold이면 decay 아님 (< threshold 조건)."""
        m = DrawdownMonitor()
        m.set_sharpe_decay(recent_sharpe=0.5, historical_sharpe=1.0, threshold=0.50)
        assert m.get_sharpe_decay_multiplier() == 1.0

    def test_sharpe_decay_reduces_size_multiplier(self):
        """Sharpe decay 시 get_size_multiplier()도 min()으로 0.5 적용."""
        m = DrawdownMonitor()
        m.update(10000)
        m.set_sharpe_decay(recent_sharpe=0.2, historical_sharpe=1.0, threshold=0.50)
        assert m.get_size_multiplier() == 0.5

    def test_sharpe_decay_status_field(self):
        """DrawdownStatus.sharpe_decay_multiplier 필드가 정확히 반영."""
        m = DrawdownMonitor()
        m.set_sharpe_decay(recent_sharpe=0.1, historical_sharpe=1.0, threshold=0.50)
        status = m.update(10000)
        assert status.sharpe_decay_multiplier == 0.5

    def test_sharpe_decay_serialization(self):
        """to_dict/from_dict 후 sharpe_decay_multiplier 상태 보존."""
        m = DrawdownMonitor()
        m.set_sharpe_decay(recent_sharpe=0.1, historical_sharpe=1.0, threshold=0.50)
        assert m.get_sharpe_decay_multiplier() == 0.5
        m2 = DrawdownMonitor.from_dict(m.to_dict())
        assert m2.get_sharpe_decay_multiplier() == 0.5


# ── should_kill_strategy 레짐별 multiplier — RANGING / HIGH_VOL (Cycle 393 B) ─


def test_regime_ranging_tightens_kill_threshold():
    """RANGING 레짐: cap=1.2 → multiplier=1.5가 1.2로 축소되어 더 빨리 kill."""
    m = DrawdownMonitor()
    # backtest_mdd=0.10, current_mdd=0.13
    # 기본(1.5): threshold=0.15 → no kill
    assert m.should_kill_strategy(0.13, 0.10, multiplier=1.5) is False
    # RANGING(cap=1.2): threshold=0.12 → kill
    assert m.should_kill_strategy(0.13, 0.10, multiplier=1.5, regime="RANGING") is True


def test_regime_high_vol_kills_at_backtest_mdd():
    """HIGH_VOL 레짐: cap=1.0 → backtest MDD 초과 즉시 kill."""
    m = DrawdownMonitor()
    # backtest_mdd=0.10, current_mdd=0.11 → threshold=0.10*1.0=0.10 → 0.11 > 0.10 → kill
    assert m.should_kill_strategy(0.11, 0.10, multiplier=1.5, regime="HIGH_VOL") is True
    # current_mdd=0.09 → 0.09 < 0.10 → no kill
    assert m.should_kill_strategy(0.09, 0.10, multiplier=1.5, regime="HIGH_VOL") is False


# ── trailing_stop_signal 회복 시 신호 해제 (Cycle 393 B) ──────────────────────


def test_trailing_stop_signal_recovery_resets():
    """급락 후 완전 회복하면 long_mdd=0 → trailing_stop_signal=False."""
    m = DrawdownMonitor(rolling_window=50)
    # 30봉 안정
    for _ in range(30):
        m.update(10000)
    # 20봉 급락 → signal=True
    for i in range(20):
        m.update(10000 - (i + 1) * 250)
    assert m.trailing_stop_signal(accel_threshold=1.5) is True

    # 51봉 이상 완전 회복 (새로운 고점) → maxlen=50으로 구 이력 밀려남
    for i in range(51):
        m.update(10001 + i * 100)  # 지속 상승
    # 최근 50봉이 모두 상승 구간 → MDD≈0 → False
    assert m.trailing_stop_signal(accel_threshold=1.5) is False


# ── Cycle 397 B(리스크): get_transition_cushion_multiplier 경계값 + should_liquidate_all ──


def test_transition_cushion_confidence_zero_returns_half():
    """enabled=True, regime_confidence=0 → threshold=0.70 미만이므로 0.5 반환."""
    m = DrawdownMonitor(transition_cushion_enabled=True, transition_cushion_threshold=0.70)
    assert m.get_transition_cushion_multiplier(0.0) == 0.5


def test_transition_cushion_confidence_at_exact_threshold_returns_one():
    """regime_confidence == threshold(=0.70): < 조건 불성립 → 1.0 반환."""
    m = DrawdownMonitor(transition_cushion_enabled=True, transition_cushion_threshold=0.70)
    assert m.get_transition_cushion_multiplier(0.70) == 1.0


def test_transition_cushion_confidence_one_returns_one():
    """enabled=True, regime_confidence=1.0 → threshold=0.70 이상 → 1.0 반환."""
    m = DrawdownMonitor(transition_cushion_enabled=True, transition_cushion_threshold=0.70)
    assert m.get_transition_cushion_multiplier(1.0) == 1.0


def test_should_liquidate_all_at_liquidate_level():
    """MDD >= mdd_liquidate_pct(15%) → LIQUIDATE 단계 → should_liquidate_all=True."""
    m = DrawdownMonitor(mdd_liquidate_pct=0.15, mdd_halt_pct=0.20)
    m.update(10000)
    m.update(8450)  # 15.5% 낙폭 → LIQUIDATE
    assert m.should_liquidate_all() is True


def test_should_liquidate_all_at_full_halt_level():
    """MDD >= mdd_halt_pct(20%) → FULL_HALT 단계 → should_liquidate_all=True."""
    m = DrawdownMonitor(mdd_halt_pct=0.20)
    m.update(10000)
    m.update(7900)  # 21% 낙폭 → FULL_HALT
    assert m.should_liquidate_all() is True


def test_should_liquidate_all_at_block_entry_is_false():
    """MDD 10-15% → BLOCK_ENTRY 단계 → should_liquidate_all=False."""
    m = DrawdownMonitor(mdd_block_pct=0.10, mdd_liquidate_pct=0.15)
    m.update(10000)
    m.update(8900)  # 11% 낙폭 → BLOCK_ENTRY (< 15%)
    assert m.should_liquidate_all() is False


# ── Cycle 401 B(리스크): set_sharpe_decay 복합 조합 케이스 ─────────────────────


def test_sharpe_decay_and_atr_elevated_compound():
    """ATR elevated + Sharpe decay 동시 활성 → get_size_multiplier() = 0.5."""
    m = DrawdownMonitor()
    m.update(10000)
    m.set_atr_state(atr=2.5, atr_ma=1.5, threshold=1.5)       # elevated: 2.5/1.5 = 1.67x ≥ 1.5
    m.set_sharpe_decay(recent_sharpe=0.3, historical_sharpe=1.0, threshold=0.50)  # decayed
    assert m.get_atr_vol_multiplier() == 0.5
    assert m.get_sharpe_decay_multiplier() == 0.5
    assert m.get_size_multiplier() == 0.5  # min(1.0, 1.0, 0.5, 0.5)


def test_sharpe_decay_negative_recent_sharpe_is_decayed():
    """recent_sharpe < 0 → ratio 음수 < threshold(0.50) → decayed=True."""
    m = DrawdownMonitor()
    m.set_sharpe_decay(recent_sharpe=-0.5, historical_sharpe=1.0, threshold=0.50)
    assert m.get_sharpe_decay_multiplier() == 0.5


def test_sharpe_decay_recovery_resets_multiplier():
    """decay 상태에서 OOS Sharpe 회복 → get_sharpe_decay_multiplier() = 1.0."""
    m = DrawdownMonitor()
    m.set_sharpe_decay(recent_sharpe=0.2, historical_sharpe=1.0, threshold=0.50)
    assert m.get_sharpe_decay_multiplier() == 0.5
    m.set_sharpe_decay(recent_sharpe=0.8, historical_sharpe=1.0, threshold=0.50)
    assert m.get_sharpe_decay_multiplier() == 1.0


def test_sharpe_decay_zero_recent_sharpe():
    """recent_sharpe=0 → ratio=0 < threshold(0.50) → decayed=True."""
    m = DrawdownMonitor()
    m.set_sharpe_decay(recent_sharpe=0.0, historical_sharpe=1.0, threshold=0.50)
    assert m.get_sharpe_decay_multiplier() == 0.5


def test_sharpe_decay_custom_threshold_boundary():
    """custom threshold=0.80, ratio=0.80 → exactly threshold → not decayed."""
    m = DrawdownMonitor()
    m.set_sharpe_decay(recent_sharpe=0.8, historical_sharpe=1.0, threshold=0.80)
    assert m.get_sharpe_decay_multiplier() == 1.0  # ratio==threshold: < 조건 불성립


def test_sharpe_decay_and_mdd_warn_compound():
    """MDD WARN(0.5) + Sharpe decay(0.5) 복합 → get_size_multiplier() = 0.5."""
    m = DrawdownMonitor(mdd_warn_pct=0.05, mdd_block_pct=0.10)
    m.update(10000)
    m.update(9400)   # 6% MDD → WARN → mdd_size_multiplier=0.5
    m.set_sharpe_decay(recent_sharpe=0.2, historical_sharpe=1.0, threshold=0.50)
    assert m.get_mdd_size_multiplier() == 0.5
    assert m.get_sharpe_decay_multiplier() == 0.5
    assert m.get_size_multiplier() == 0.5  # min(1.0, 0.5, 1.0, 0.5)


# ── Cycle403 B(리스크): reset_daily 복합 케이스 ──────────────────────────────


def test_reset_daily_not_halted_updates_daily_start():
    """미정지 상태에서 reset_daily → daily_start만 갱신, 상태 변화 없음."""
    m = DrawdownMonitor(daily_limit=0.03)
    m.set_daily_start(10000)
    # halted 상태 아님
    assert not m.is_halted()
    m.reset_daily(9500)   # 새 equity로 daily_start 갱신
    # 여전히 halted 아님
    assert not m.is_halted()
    # 갱신된 daily_start 기준으로 일일 DD 계산됨
    # 9500 * 0.97 = 9215 아래로 가야 WARNING
    status = m.update(9250)  # (9500 - 9250) / 9500 = 2.6% < 3% → WARNING 없음
    assert not status.halted


def test_reset_daily_halt_level_not_cleared():
    """HALT 레벨 정지 상태에서 reset_daily → HALT 해제 안 됨 (WARNING만 해제)."""
    m = DrawdownMonitor(weekly_limit=0.05)
    m.set_weekly_start(10000)
    m.update(10000)
    m.update(9400)   # 6% 주간 DD → HALT
    assert m.is_halted()
    assert m._alert_level == AlertLevel.HALT
    # reset_daily는 WARNING만 해제 — HALT는 유지
    m.reset_daily(9400)
    assert m.is_halted(), "HALT 레벨은 reset_daily로 해제 안 됨"
    assert m._alert_level == AlertLevel.HALT


def test_reset_daily_force_liquidate_not_cleared():
    """FORCE_LIQUIDATE 레벨에서 reset_daily → 정지 유지."""
    m = DrawdownMonitor(monthly_limit=0.10)
    m.set_monthly_start(10000)
    m.update(10000)
    m.update(8900)   # 11% 월간 DD → FORCE_LIQUIDATE
    assert m.is_halted()
    assert m._alert_level == AlertLevel.FORCE_LIQUIDATE
    m.reset_daily(8900)
    assert m.is_halted(), "FORCE_LIQUIDATE는 reset_daily로 해제 안 됨"
    assert m._alert_level == AlertLevel.FORCE_LIQUIDATE


# ── Cycle406 B(리스크): set_regime + transition_cushion 복합 케이스 ───────────


def test_crisis_regime_tightens_daily_limit():
    """CRISIS 레짐 → HIGH_VOL과 동일하게 _high_vol_daily_limit(2%) 적용."""
    m = DrawdownMonitor(daily_limit=0.03)
    m.set_daily_start(10000)
    # 기본 한도(3%): 2% 손실 → WARNING 없음
    m.update(9800)
    assert m.alert_level() == AlertLevel.NONE

    # CRISIS 전환 → _effective_daily_limit = 2%
    m.reset_daily(10000)
    m.set_regime("CRISIS")
    m.update(9800)  # 2% 손실 ≥ 2% 한도 → WARNING
    assert m.alert_level() == AlertLevel.WARNING


def test_high_vol_regime_and_transition_cushion_compound():
    """HIGH_VOL 레짐(일일 한도 강화) + transition_cushion(저신뢰도→0.5x) 동시 활성."""
    m = DrawdownMonitor(
        daily_limit=0.03,
        transition_cushion_enabled=True,
        transition_cushion_threshold=0.70,
    )
    m.set_regime("HIGH_VOL")
    m.set_daily_start(10000)

    # HIGH_VOL: 일일 한도 2%로 강화 → 2% 손실 시 WARNING
    m.update(9800)
    assert m.alert_level() == AlertLevel.WARNING

    # transition_cushion: 저신뢰도(0.5 < threshold=0.70) → 0.5x 반환
    cushion = m.get_transition_cushion_multiplier(0.5)
    assert cushion == pytest.approx(0.5)

    # 고신뢰도(0.80 > threshold) → 1.0x (정상)
    assert m.get_transition_cushion_multiplier(0.80) == pytest.approx(1.0)


def test_regime_reset_reverts_daily_limit():
    """HIGH_VOL 레짐 이후 TREND_UP 전환 → 일일 한도 원복."""
    m = DrawdownMonitor(daily_limit=0.03)
    m.set_daily_start(10000)

    # HIGH_VOL: 2% 손실 → WARNING
    m.set_regime("HIGH_VOL")
    m.update(9800)
    assert m.alert_level() == AlertLevel.WARNING

    # TREND_UP 전환 후 daily 리셋 → 한도 3% 복원 → 2% 손실은 WARNING 미발생
    m.reset_daily(10000)
    m.set_regime("TREND_UP")
    m.update(9800)  # 2% 손실 < 3% 한도 → NONE
    assert m.alert_level() == AlertLevel.NONE


# ── Cycle408 B(리스크): get_size_multiplier 복합 케이스 ──────────────────────


def test_atr_elevated_and_mdd_warn_compound():
    """ATR elevated(0.5x) + MDD WARN(0.5x) 동시 활성 → get_size_multiplier() = 0.5."""
    m = DrawdownMonitor(mdd_warn_pct=0.05)
    m.update(10000)   # peak 설정
    # MDD WARN 유발: 6% 낙폭 → WARN (0.5x)
    m.update(9400)
    assert m.get_mdd_size_multiplier() == 0.5
    # ATR elevated (2x MA) → _atr_vol_mult = 0.5
    m.set_atr_state(atr=200.0, atr_ma=100.0, threshold=1.5)
    assert m.get_atr_vol_multiplier() == 0.5
    # 두 인자가 모두 0.5 → min(1.0, 0.5, 0.5, 1.0) = 0.5
    assert m.get_size_multiplier() == pytest.approx(0.5)


def test_get_size_multiplier_all_four_factors_compound():
    """streak(0.5) + MDD WARN(0.5) + ATR elevated(0.5) + Sharpe decay(0.5) 동시 → 0.5."""
    m = DrawdownMonitor(mdd_warn_pct=0.05, loss_streak_threshold=2)
    m.update(10000)   # peak 설정
    # MDD WARN
    m.update(9400)   # 6% → WARN
    assert m.get_mdd_size_multiplier() == 0.5
    # streak: 2연속 손실
    m.record_trade_result(pnl=-50.0, equity=9400)
    m.record_trade_result(pnl=-50.0, equity=9350)
    assert m._consecutive_losses >= 2
    # ATR elevated
    m.set_atr_state(atr=200.0, atr_ma=100.0, threshold=1.5)
    assert m.get_atr_vol_multiplier() == 0.5
    # Sharpe decay
    m.set_sharpe_decay(recent_sharpe=0.2, historical_sharpe=1.0, threshold=0.50)
    assert m.get_sharpe_decay_multiplier() == 0.5
    # 4인자 모두 0.5 → min(0.5, 0.5, 0.5, 0.5) = 0.5
    assert m.get_size_multiplier() == pytest.approx(0.5)


def test_trend_down_regime_does_not_change_daily_limit():
    """TREND_DOWN 레짐은 일일 DD 한도를 강화하지 않음 (HIGH_VOL/CRISIS만 강화)."""
    m = DrawdownMonitor(daily_limit=0.03)
    m.set_daily_start(10000)
    # TREND_DOWN 설정 → 한도는 여전히 3%
    m.set_regime("TREND_DOWN")
    m.update(9800)   # 2% 손실 < 3% 한도 → WARNING 없음
    assert m.alert_level() == AlertLevel.NONE
    # 3% 경계 테스트: 3% 손실 → WARNING 발생
    m.reset_daily(10000)
    m.set_regime("TREND_DOWN")
    m.update(9700)   # 3% 손실 ≥ 3% 한도 → WARNING
    assert m.alert_level() == AlertLevel.WARNING


# ── Cycle411 B(리스크): transition_cushion + set_regime 복합 케이스 ──────────

def test_transition_cushion_disabled_by_default_returns_one():
    """transition_cushion_enabled=False(기본값) → confidence 무관하게 1.0 반환."""
    m = DrawdownMonitor()
    assert not m.transition_cushion_enabled
    # confidence=0.0 (최저) 이어도 disabled이면 1.0
    assert m.get_transition_cushion_multiplier(0.0) == pytest.approx(1.0)
    assert m.get_transition_cushion_multiplier(0.5) == pytest.approx(1.0)
    assert m.get_transition_cushion_multiplier(1.0) == pytest.approx(1.0)


def test_transition_cushion_enabled_crisis_regime_compound():
    """CRISIS 레짐 + transition_cushion 활성화 + 낮은 confidence → 일일 한도 강화 + cushion 0.5."""
    m = DrawdownMonitor(
        daily_limit=0.03,
        transition_cushion_enabled=True,
        transition_cushion_threshold=0.6,
    )
    m.set_daily_start(10000)
    m.set_regime("CRISIS")
    # CRISIS → 일일 한도 2%로 강화 (HIGH_VOL과 동일)
    m.update(9810)   # 1.9% 손실 < 2% 한도 → NONE
    assert m.alert_level() == AlertLevel.NONE
    m.reset_daily(10000)
    m.set_regime("CRISIS")
    m.update(9790)   # 2.1% 손실 ≥ 2% 한도 → WARNING
    assert m.alert_level() == AlertLevel.WARNING
    # cushion: confidence=0.3 < threshold=0.6 → 0.5
    assert m.get_transition_cushion_multiplier(0.3) == pytest.approx(0.5)
    # cushion: confidence=0.7 ≥ threshold=0.6 → 1.0
    assert m.get_transition_cushion_multiplier(0.7) == pytest.approx(1.0)


def test_get_size_multiplier_atr_and_sharpe_decay_no_streak_mdd():
    """ATR elevated(0.5) + Sharpe decay(0.5), streak/MDD 없음 → get_size_multiplier=0.5."""
    m = DrawdownMonitor(mdd_warn_pct=0.10, loss_streak_threshold=5)
    m.update(10000)   # peak 설정
    # MDD 없음: equity=9700 → 3% < mdd_warn_pct=10%
    m.update(9700)
    assert m.get_mdd_level() == MddLevel.NORMAL
    # streak 없음
    assert m._consecutive_losses == 0
    # ATR elevated
    m.set_atr_state(atr=200.0, atr_ma=100.0, threshold=1.5)
    assert m.get_atr_vol_multiplier() == pytest.approx(0.5)
    # Sharpe decay
    m.set_sharpe_decay(recent_sharpe=0.2, historical_sharpe=1.0, threshold=0.50)
    assert m.get_sharpe_decay_multiplier() == pytest.approx(0.5)
    # min(1.0 streak, 1.0 mdd, 0.5 atr, 0.5 sharpe) = 0.5
    assert m.get_size_multiplier() == pytest.approx(0.5)


# ── Cycle403 B(리스크): reset_daily() 복합 케이스 ────────────────────────────


def test_reset_daily_does_not_clear_halt_level():
    """reset_daily()는 WARNING만 해제하고 HALT 레벨은 해제하지 않는다."""
    m = DrawdownMonitor(daily_limit=0.03, weekly_limit=0.07, monthly_limit=0.15)
    m.set_weekly_start(10000)
    m.set_daily_start(9400)   # 일일 기준 낮게 설정 — daily_dd < 3%
    m.update(9200)            # 주간 8% 낙폭 → HALT
    assert m.is_halted()
    assert m.alert_level() == AlertLevel.HALT

    m.reset_daily(9200)       # 일일 리셋 시도
    # HALT는 reset_daily()로 해제 불가 — reset_weekly()만 가능
    assert m.is_halted()
    assert m.alert_level() == AlertLevel.HALT


def test_reset_daily_none_state_updates_daily_start():
    """halted=False(NONE) 상태에서 reset_daily()는 daily_start만 갱신하고 크래시 없음."""
    m = DrawdownMonitor(daily_limit=0.03)
    m.set_daily_start(10000)
    m.update(9800)            # 2% 낙폭 — WARNING 미달

    assert not m.is_halted()
    m.reset_daily(9800)       # 경고 없는 상태에서 리셋

    assert not m.is_halted()
    assert m._daily_start == 9800  # 새 daily_start로 갱신됨


# ── Cycle413 B(리스크): trailing_stop_signal 경계 + kelly+mdd_warn 복합 ────────


def test_trailing_stop_signal_short_window_boundary():
    """rolling_window=40 → short_window=min(20, 40//2)=20 boundary 검증."""
    m = DrawdownMonitor(rolling_window=40)
    # 20봉 안정
    for _ in range(20):
        m.update(10000)
    # 20봉 급락: 단기(20봉) 낙폭 집중
    for i in range(20):
        m.update(10000 - (i + 1) * 200)  # 4000 → 40% 낙폭
    # short_window = min(20, 40//2) = 20 = long_window//2
    # short_mdd: 최근 20봉에서 40% / 20 = 2% per bar
    # long_mdd: 전체 40봉 기준 더 낮은 rate → short_rate > long_rate * 1.5
    assert m.trailing_stop_signal(accel_threshold=1.5) is True


def test_trailing_stop_signal_threshold_one_uniform_decline():
    """accel_threshold=1.0 → short_rate >= long_rate 이면 신호 발생 (균일 낙폭에서도)."""
    m = DrawdownMonitor(rolling_window=50)
    # 50봉 균일 하락: short_rate ≈ long_rate → accel_threshold=1.0 에서 >= 성립
    for i in range(50):
        m.update(10000 - i * 20)
    # short_rate / long_rate ≈ 1.0, accel_threshold=1.0 → short_rate >= long_rate * 1.0 → True
    assert m.trailing_stop_signal(accel_threshold=1.0) is True


def test_kelly_fraction_multiplier_and_mdd_warn_compound():
    """MDD 9% (warn_pct=8%, block_pct=10%): kelly=0.5 + mdd_level=WARN 동시 발생."""
    m = DrawdownMonitor(
        mdd_warn_pct=0.08,
        mdd_block_pct=0.10,
        kelly_reduce_at_mdd=0.08,
    )
    m.update(10000)          # peak
    m.update(9100)           # 9% 낙폭 → warn_pct(8%) 초과, block_pct(10%) 미만 → WARN
    # kelly_fraction_multiplier: 9% > kelly_reduce_at_mdd(8%) → 0.5
    assert m.get_kelly_fraction_multiplier() == pytest.approx(0.5)
    # mdd_level: 9% ∈ [8%, 10%) → WARN
    assert m.get_mdd_level() == MddLevel.WARN
    # get_mdd_size_multiplier: WARN → 0.5
    assert m.get_mdd_size_multiplier() == pytest.approx(0.5)


# ── Cycle416 B(리스크): kelly_fraction+sharpe_decay 복합, streak+sharpe_decay 복합 ──


def test_kelly_fraction_and_sharpe_decay_compound():
    """kelly_fraction_multiplier(0.5) + sharpe_decay(0.5) 동시 활성화.

    kelly_fraction_multiplier는 get_size_multiplier()와 독립(포트폴리오 배분 레이어).
    sharpe_decay는 get_size_multiplier()에 포함 → size_mult=0.5, kelly=0.5 각자 독립.
    """
    m = DrawdownMonitor(
        mdd_warn_pct=0.10,
        mdd_block_pct=0.15,
        kelly_reduce_at_mdd=0.08,
    )
    m.update(10000)
    m.update(9100)  # 9% MDD → kelly_reduce_at_mdd(8%) 초과 → kelly=0.5; WARN(10%) 미달 → mdd_size=1.0
    assert m.get_kelly_fraction_multiplier() == pytest.approx(0.5)
    assert m.get_mdd_size_multiplier() == pytest.approx(1.0)
    # sharpe decay 활성화
    m.set_sharpe_decay(recent_sharpe=0.2, historical_sharpe=1.0, threshold=0.50)
    assert m.get_sharpe_decay_multiplier() == pytest.approx(0.5)
    # get_size_multiplier: min(1.0 streak, 1.0 mdd, 1.0 atr, 0.5 sharpe_decay) = 0.5
    assert m.get_size_multiplier() == pytest.approx(0.5)
    # kelly는 get_size_multiplier와 독립 — 둘 다 0.5이나 별개 축소
    assert m.get_kelly_fraction_multiplier() == pytest.approx(0.5)


def test_streak_and_sharpe_decay_no_mdd_atr():
    """streak(0.5, consecutive_losses >= threshold) + sharpe_decay(0.5), MDD/ATR 정상 → get_size_multiplier=0.5."""
    m = DrawdownMonitor(mdd_warn_pct=0.20, loss_streak_threshold=3)
    m.update(10000)
    # streak 활성: 3연속 손실
    m.record_trade_result(pnl=-10.0, equity=9990)
    m.record_trade_result(pnl=-10.0, equity=9980)
    m.record_trade_result(pnl=-10.0, equity=9970)
    assert m._consecutive_losses >= 3
    # MDD: 0.3% < mdd_warn_pct(20%) → NORMAL
    assert m.get_mdd_level() == MddLevel.NORMAL
    # ATR: 기본값 1.0 (정상)
    assert m.get_atr_vol_multiplier() == pytest.approx(1.0)
    # sharpe decay 활성
    m.set_sharpe_decay(recent_sharpe=0.1, historical_sharpe=1.0, threshold=0.50)
    assert m.get_sharpe_decay_multiplier() == pytest.approx(0.5)
    # get_size_multiplier: min(0.5 streak, 1.0 mdd, 1.0 atr, 0.5 sharpe_decay) = 0.5
    assert m.get_size_multiplier() == pytest.approx(0.5)


def test_sharpe_decay_recovery_while_high_vol_daily_limit_remains():
    """HIGH_VOL 레짐 유지 + sharpe_decay 회복 → size_mult 복원(1.0), 일일 한도는 HIGH_VOL 유지(2%)."""
    m = DrawdownMonitor(
        daily_limit=0.03,
        mdd_warn_pct=0.20,
    )
    m.set_daily_start(10000)
    m.set_regime("HIGH_VOL")
    # sharpe decay 활성
    m.set_sharpe_decay(recent_sharpe=0.2, historical_sharpe=1.0, threshold=0.50)
    assert m.get_sharpe_decay_multiplier() == pytest.approx(0.5)
    assert m.get_size_multiplier() == pytest.approx(0.5)
    # sharpe decay 회복 → size_mult 복원
    m.set_sharpe_decay(recent_sharpe=0.8, historical_sharpe=1.0, threshold=0.50)
    assert m.get_sharpe_decay_multiplier() == pytest.approx(1.0)
    assert m.get_size_multiplier() == pytest.approx(1.0)
    # HIGH_VOL 레짐은 여전히 활성 → 일일 한도 2% 유지
    m.update(9800)  # 2% 손실 ≥ HIGH_VOL 한도(2%) → WARNING
    assert m.alert_level() == AlertLevel.WARNING


# ── Cycle418 B(리스크): BLOCK_ENTRY+sharpe_decay, streak+ATR, BLOCK+ATR 복합 ──


def test_block_entry_and_sharpe_decay_block_dominates():
    """BLOCK_ENTRY(mdd_mult=0.0) + sharpe_decay(0.5) → get_size_multiplier=0.0 (BLOCK 지배)."""
    m = DrawdownMonitor(mdd_block_pct=0.10, mdd_warn_pct=0.05)
    m.update(10000)
    m.update(8900)  # 11% → BLOCK_ENTRY → mdd_size_multiplier=0.0
    assert m.get_mdd_level() == MddLevel.BLOCK_ENTRY
    assert m.get_mdd_size_multiplier() == 0.0
    # sharpe decay 추가 (0.5 배수)
    m.set_sharpe_decay(recent_sharpe=0.2, historical_sharpe=1.0, threshold=0.50)
    assert m.get_sharpe_decay_multiplier() == 0.5
    # min(1.0 streak, 0.0 block, 1.0 atr, 0.5 sharpe) = 0.0 — BLOCK이 decay 무력화
    assert m.get_size_multiplier() == pytest.approx(0.0)


def test_streak_and_atr_elevated_no_mdd_no_sharpe():
    """streak(0.5) + ATR elevated(0.5), MDD/sharpe 정상 → get_size_multiplier=0.5."""
    m = DrawdownMonitor(mdd_warn_pct=0.15, loss_streak_threshold=2)
    m.update(10000)
    m.update(9700)  # 3% MDD < mdd_warn_pct=15% → NORMAL
    assert m.get_mdd_level() == MddLevel.NORMAL
    # streak: 2연속 손실
    m.record_trade_result(pnl=-100.0, equity=9700)
    m.record_trade_result(pnl=-100.0, equity=9600)
    assert m._consecutive_losses >= 2
    streak_mult = 0.5 if m._consecutive_losses >= m.loss_streak_threshold else 1.0
    assert streak_mult == 0.5
    # ATR elevated
    m.set_atr_state(atr=300.0, atr_ma=100.0, threshold=1.5)
    assert m.get_atr_vol_multiplier() == 0.5
    # sharpe 정상 (decay 없음)
    assert m.get_sharpe_decay_multiplier() == pytest.approx(1.0)
    # min(0.5 streak, 1.0 mdd, 0.5 atr, 1.0 sharpe) = 0.5
    assert m.get_size_multiplier() == pytest.approx(0.5)


def test_block_entry_and_atr_elevated_block_dominates():
    """BLOCK_ENTRY(0.0) + ATR elevated(0.5) → get_size_multiplier=0.0 (BLOCK 지배)."""
    m = DrawdownMonitor(mdd_block_pct=0.10)
    m.update(10000)
    m.update(8900)  # 11% → BLOCK_ENTRY → 0.0
    assert m.get_mdd_size_multiplier() == 0.0
    # ATR elevated 추가
    m.set_atr_state(atr=200.0, atr_ma=100.0, threshold=1.5)
    assert m.get_atr_vol_multiplier() == 0.5
    # min(1.0, 0.0, 0.5, 1.0) = 0.0
    assert m.get_size_multiplier() == pytest.approx(0.0)
