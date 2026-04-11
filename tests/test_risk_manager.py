"""
RiskManager / CircuitBreaker 단위 테스트.
"""

import math
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from src.risk.manager import CircuitBreaker, RiskManager, RiskStatus


# ── CircuitBreaker ────────────────────────────────────────────────────────────

def _make_cb(**kwargs) -> CircuitBreaker:
    defaults = dict(max_daily_loss=0.05, max_drawdown=0.10, max_consecutive_losses=3)
    defaults.update(kwargs)
    return CircuitBreaker(**defaults)


def test_circuit_breaker_no_trigger():
    cb = _make_cb()
    result = cb.check(current_balance=10000, last_candle_pct_change=0.01)
    assert result is None


def test_circuit_breaker_daily_loss_trigger():
    cb = _make_cb(max_daily_loss=0.05)
    cb._daily_loss = 0.06
    result = cb.check(current_balance=10000, last_candle_pct_change=0.0)
    assert result is not None
    assert "daily_loss" in result


def test_circuit_breaker_drawdown_trigger():
    cb = _make_cb(max_drawdown=0.10)
    cb._peak_balance = 10000
    result = cb.check(current_balance=8900, last_candle_pct_change=0.0)
    assert result is not None
    assert "drawdown" in result


def test_circuit_breaker_consecutive_losses_trigger():
    cb = _make_cb(max_consecutive_losses=3)
    cb._consecutive_losses = 3
    result = cb.check(current_balance=10000, last_candle_pct_change=0.0)
    assert result is not None
    assert "consecutive_losses" in result


def test_circuit_breaker_flash_crash_trigger():
    cb = _make_cb(flash_crash_pct=0.10)
    result = cb.check(current_balance=10000, last_candle_pct_change=-0.15)
    assert result is not None
    assert "flash crash" in result


def test_circuit_breaker_record_trade_result_loss():
    cb = _make_cb()
    cb.record_trade_result(pnl=-500, account_balance=10000)
    assert cb._daily_loss == pytest.approx(0.05)
    assert cb._consecutive_losses == 1


def test_circuit_breaker_record_trade_result_profit():
    cb = _make_cb()
    cb._consecutive_losses = 2
    cb.record_trade_result(pnl=200, account_balance=10000)
    assert cb._consecutive_losses == 0


def test_circuit_breaker_reset_daily():
    """reset_daily() 후 _daily_loss == 0, _consecutive_losses == 0"""
    cb = _make_cb()
    cb._daily_loss = 0.08
    cb._consecutive_losses = 3
    cb.reset_daily()
    assert cb._daily_loss == 0.0
    assert cb._consecutive_losses == 0


# ── RiskManager ───────────────────────────────────────────────────────────────

def _make_rm(**kwargs) -> RiskManager:
    return RiskManager(**kwargs)


def test_risk_manager_hold_approved():
    rm = _make_rm()
    result = rm.evaluate(action="HOLD", entry_price=50000, atr=500, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert result.position_size == 0


def test_risk_manager_buy_approved():
    rm = _make_rm(risk_per_trade=0.01, atr_multiplier_sl=1.5)
    result = rm.evaluate(action="BUY", entry_price=50000, atr=500, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert result.position_size > 0
    assert result.stop_loss < 50000
    assert result.take_profit > 50000


def test_risk_manager_sell_approved():
    rm = _make_rm()
    result = rm.evaluate(action="SELL", entry_price=50000, atr=500, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert result.stop_loss > 50000
    assert result.take_profit < 50000


def test_risk_manager_circuit_breaker_blocks():
    cb = _make_cb()
    cb._daily_loss = 0.10  # 한도 초과
    rm = _make_rm(circuit_breaker=cb)
    result = rm.evaluate(action="BUY", entry_price=50000, atr=500, account_balance=10000)
    assert result.status == RiskStatus.BLOCKED
    assert "Circuit breaker" in result.reason


def test_risk_manager_reset_daily_delegates():
    """RiskManager.reset_daily() → CircuitBreaker.reset_daily() 위임"""
    cb = _make_cb()
    cb._daily_loss = 0.09
    cb._consecutive_losses = 2
    rm = _make_rm(circuit_breaker=cb)
    rm.reset_daily()
    assert cb._daily_loss == 0.0
    assert cb._consecutive_losses == 0


def test_risk_manager_reset_daily_no_cb():
    """circuit_breaker 없을 때 reset_daily()가 예외 없이 실행"""
    rm = _make_rm(circuit_breaker=None)
    rm.reset_daily()  # 예외 없어야 함


# ── adaptive_stop_multiplier ──────────────────────────────────────────────────

def _make_df_with_vol(target_annualized_vol: float, n: int = 25) -> pd.DataFrame:
    """연환산 변동성이 target_annualized_vol에 근접하는 캔들 DataFrame 생성.

    시간봉 annualization = 252*24 = 6048.
    per-bar std = target_annualized_vol / sqrt(6048)
    """
    rng = np.random.default_rng(42)
    per_bar_std = target_annualized_vol / math.sqrt(252 * 24)
    log_returns = rng.normal(0, per_bar_std, n)
    closes = 50000.0 * np.exp(np.cumsum(log_returns))
    return pd.DataFrame({"close": closes})


def test_adaptive_stop_multiplier_low_vol():
    """저변동(vol < 0.3) → multiplier 1.2"""
    df = _make_df_with_vol(0.15)
    mult = RiskManager.adaptive_stop_multiplier(df)
    assert mult == pytest.approx(1.2)


def test_adaptive_stop_multiplier_mid_vol():
    """중변동(0.3 <= vol < 0.6) → multiplier 1.5"""
    df = _make_df_with_vol(0.45)
    mult = RiskManager.adaptive_stop_multiplier(df)
    assert mult == pytest.approx(1.5)


def test_adaptive_stop_multiplier_high_vol():
    """고변동(vol >= 0.6) → multiplier 2.5"""
    df = _make_df_with_vol(0.9)
    mult = RiskManager.adaptive_stop_multiplier(df)
    assert mult == pytest.approx(2.5)


def test_adaptive_stop_multiplier_none_df():
    """df=None → 기본값 1.5"""
    mult = RiskManager.adaptive_stop_multiplier(None)
    assert mult == pytest.approx(1.5)


def test_adaptive_stop_multiplier_too_short():
    """캔들 1개 → 기본값 1.5"""
    df = pd.DataFrame({"close": [50000.0]})
    mult = RiskManager.adaptive_stop_multiplier(df)
    assert mult == pytest.approx(1.5)


def test_evaluate_uses_adaptive_multiplier():
    """candle_df 전달 시 adaptive multiplier가 sl_distance에 반영됨."""
    rm = _make_rm(risk_per_trade=0.01, atr_multiplier_sl=1.5)

    # 저변동 df → multiplier=1.2 (기존 1.5보다 타이트)
    df_low = _make_df_with_vol(0.15)
    result_adaptive = rm.evaluate(
        action="BUY", entry_price=50000, atr=500,
        account_balance=10000, candle_df=df_low,
    )
    # 기존 고정 multiplier 결과 (candle_df 없음)
    result_fixed = rm.evaluate(
        action="BUY", entry_price=50000, atr=500,
        account_balance=10000,
    )

    # 저변동 → SL이 entry에 더 가까워야 함 (multiplier 1.2 < 1.5)
    assert result_adaptive.stop_loss > result_fixed.stop_loss
    assert result_adaptive.status == RiskStatus.APPROVED


# ── Order Jitter ──────────────────────────────────────────────────────────────

def test_jitter_varies_position_size():
    """jitter_pct > 0 이면 동일 입력에서 position_size가 매 호출마다 달라진다."""
    import random as _random
    rm = _make_rm(jitter_pct=0.05)
    sizes = set()
    _random.seed(None)  # 시드 고정 해제
    for _ in range(30):
        result = rm.evaluate(action="BUY", entry_price=50000, atr=500, account_balance=10000)
        assert result.status == RiskStatus.APPROVED
        sizes.add(result.position_size)
    # 30번 중 최소 2개 이상 다른 값이 나와야 함
    assert len(sizes) >= 2


def test_jitter_within_bounds():
    """jitter_pct=0.05 → position_size가 기준값 ±5% 범위 이내여야 한다."""
    # jitter 없는 기준값 계산
    rm_base = _make_rm(jitter_pct=0.0)
    base_result = rm_base.evaluate(action="BUY", entry_price=50000, atr=500, account_balance=10000)
    base_size = base_result.position_size

    rm_jitter = _make_rm(jitter_pct=0.05)
    for _ in range(50):
        result = rm_jitter.evaluate(action="BUY", entry_price=50000, atr=500, account_balance=10000)
        assert result.status == RiskStatus.APPROVED
        assert result.position_size <= base_size * 1.05 + 1e-9
        assert result.position_size >= base_size * 0.95 - 1e-9


def test_jitter_zero_is_deterministic():
    """jitter_pct=0.0 (기본값) 이면 동일 입력에 항상 같은 position_size."""
    rm = _make_rm(jitter_pct=0.0)
    results = [
        rm.evaluate(action="BUY", entry_price=50000, atr=500, account_balance=10000).position_size
        for _ in range(10)
    ]
    assert len(set(results)) == 1


def test_jitter_pct_clamped_at_five_percent():
    """jitter_pct > 0.05 전달 시 내부적으로 0.05로 클램프된다."""
    rm = _make_rm(jitter_pct=0.99)
    assert rm.jitter_pct == pytest.approx(0.05)


# ── Session Filter ────────────────────────────────────────────────────────────

def test_session_filter_reduced_asia_halves_position():
    """session_filter=True + 아시아(평일 REDUCED) 세션 → 50% 축소."""
    from datetime import timezone
    rm = _make_rm(session_filter=True)
    rm_off = _make_rm(session_filter=False)

    # 평일 09:00 UTC → REDUCED (아시아 세션)
    ts = datetime(2026, 4, 13, 9, 0, 0, tzinfo=timezone.utc)  # Monday

    base = rm_off.evaluate(action="BUY", entry_price=50000, atr=500, account_balance=10000)
    filtered = rm.evaluate(action="BUY", entry_price=50000, atr=500, account_balance=10000, timestamp=ts)

    assert filtered.status == RiskStatus.APPROVED
    assert abs(filtered.position_size - base.position_size * 0.50) < 1e-5


def test_session_filter_weekend_scales_to_30_pct():
    """session_filter=True + 주말 → 30% 축소."""
    from datetime import timezone
    rm = _make_rm(session_filter=True)
    rm_off = _make_rm(session_filter=False)

    # Saturday 14:00 UTC
    ts = datetime(2026, 4, 11, 14, 0, 0, tzinfo=timezone.utc)  # Saturday

    base = rm_off.evaluate(action="BUY", entry_price=50000, atr=500, account_balance=10000)
    filtered = rm.evaluate(action="BUY", entry_price=50000, atr=500, account_balance=10000, timestamp=ts)

    assert filtered.status == RiskStatus.APPROVED
    assert abs(filtered.position_size - base.position_size * 0.30) < 1e-5


# ── Integration Tests ─────────────────────────────────────────────────────────

def _make_cb_from_config() -> CircuitBreaker:
    """config/config.yaml 기준 CircuitBreaker 생성."""
    return CircuitBreaker(
        max_daily_loss=0.03,
        max_drawdown=0.05,
        max_consecutive_losses=5,
        flash_crash_pct=0.10,
    )


def test_integration_all_features_approved():
    """jitter + session_filter + max_total_exposure + VaR(adaptive ATR) 모두 활성화 — 정상 시나리오."""
    from datetime import timezone

    cb = _make_cb_from_config()
    rm = RiskManager(
        risk_per_trade=0.01,
        atr_multiplier_sl=1.5,
        atr_multiplier_tp=3.0,
        max_position_size=0.10,
        circuit_breaker=cb,
        jitter_pct=0.02,
        session_filter=True,
        max_total_exposure=0.30,
    )

    # 중변동 candle_df → adaptive multiplier 1.5
    df = _make_df_with_vol(0.45)

    # 기존 포지션: 총 노출 20% (한도 30% 미만)
    open_positions = [{"size": 0.04, "price": 50000}]  # 0.04 * 50000 = 2000, 20% of 10000

    # 평일 London session (14:00 UTC) → ACTIVE → 축소 없음
    ts = datetime(2026, 4, 13, 14, 0, 0, tzinfo=timezone.utc)

    result = rm.evaluate(
        action="BUY",
        entry_price=50000,
        atr=500,
        account_balance=10000,
        last_candle_pct_change=0.02,
        candle_df=df,
        timestamp=ts,
        open_positions=open_positions,
    )

    assert result.status == RiskStatus.APPROVED
    assert result.position_size > 0
    assert result.stop_loss < 50000
    assert result.take_profit > 50000
    assert result.risk_amount == pytest.approx(100.0)  # 10000 * 0.01
    # max_position_size=10% → max_size = 10000*0.10/50000 = 0.02
    assert result.position_size <= 0.02 * 1.05 + 1e-9  # jitter 상한 포함


def test_integration_boundary_circuit_and_exposure_blocked():
    """경계 시나리오: daily_loss 한계치 + total_exposure 한계치 동시 — 서킷 브레이커가 먼저 BLOCK."""
    from datetime import timezone

    cb = _make_cb_from_config()
    cb._daily_loss = 0.03  # 정확히 한도(>=) → BLOCKED
    rm = RiskManager(
        risk_per_trade=0.01,
        atr_multiplier_sl=1.5,
        atr_multiplier_tp=3.0,
        max_position_size=0.10,
        circuit_breaker=cb,
        jitter_pct=0.02,
        session_filter=True,
        max_total_exposure=0.30,
    )

    df = _make_df_with_vol(0.45)
    # total_exposure도 한계치 초과 (30%)
    open_positions = [{"size": 0.06, "price": 50000}]  # 3000/10000 = 30%

    ts = datetime(2026, 4, 11, 14, 0, 0, tzinfo=timezone.utc)  # Saturday

    result = rm.evaluate(
        action="BUY",
        entry_price=50000,
        atr=500,
        account_balance=10000,
        last_candle_pct_change=0.05,
        candle_df=df,
        timestamp=ts,
        open_positions=open_positions,
    )

    assert result.status == RiskStatus.BLOCKED
    assert "Circuit breaker" in result.reason
    assert "daily_loss" in result.reason
    assert result.position_size is None


def test_integration_drawdown_session_exposure_near_limits_approved():
    """통합: 드로다운·세션·exposure 모두 한계 근처이지만 미초과 → APPROVED + 포지션 축소 확인."""
    from datetime import timezone

    cb = _make_cb_from_config()
    # 드로다운 4.9% (한도 5% 미만)
    cb._peak_balance = 10000
    rm = RiskManager(
        risk_per_trade=0.01,
        atr_multiplier_sl=1.5,
        atr_multiplier_tp=3.0,
        max_position_size=0.10,
        circuit_breaker=cb,
        jitter_pct=0.0,
        session_filter=True,
        max_total_exposure=0.30,
    )

    df = _make_df_with_vol(0.45)  # 중변동 → adaptive multiplier 1.5

    # 총 노출 29% (한도 30% 미만)
    open_positions = [{"size": 0.056, "price": 50000}]  # 0.056*50000=2800, ~29.4% of 9510

    # 아시아 세션 평일 (REDUCED → 50% 축소)
    ts = datetime(2026, 4, 13, 9, 0, 0, tzinfo=timezone.utc)  # Monday 09:00 UTC

    result = rm.evaluate(
        action="BUY",
        entry_price=50000,
        atr=500,
        account_balance=9510,          # peak 10000 대비 4.9% 드로다운
        last_candle_pct_change=0.03,   # 플래시크래시 기준 10% 미만
        candle_df=df,
        timestamp=ts,
        open_positions=open_positions,
    )

    assert result.status == RiskStatus.APPROVED
    assert result.position_size > 0

    # 세션 50% 축소 + max_position_size 클램프 반영된 포지션이어야 함
    # max_size = 9510 * 0.10 / 50000 = 0.01902, then *0.5 = 0.00951
    expected_max = (9510 * 0.10 / 50000) * 0.50
    assert result.position_size <= expected_max + 1e-9
    assert result.stop_loss < 50000
    assert result.take_profit > 50000


def test_integration_kelly_constrained_exposure_blocked():
    """Risk-Constrained Kelly 시나리오: 고승률이라도 exposure 한도 초과 시 BLOCKED."""
    from datetime import timezone

    cb = _make_cb_from_config()
    # Kelly 기법으로 risk_per_trade를 높게 설정 (승률 60%, R:R 2 → Kelly=0.20)
    # 그러나 max_total_exposure 한도(20%)가 이미 채워진 상황
    rm = RiskManager(
        risk_per_trade=0.20,          # Kelly fraction (공격적)
        atr_multiplier_sl=1.5,
        atr_multiplier_tp=3.0,
        max_position_size=0.20,       # Kelly 반영한 상한
        circuit_breaker=cb,
        jitter_pct=0.0,
        session_filter=False,
        max_total_exposure=0.20,      # 보수적 총 노출 한도 20%
    )

    # 기존 포지션이 이미 노출 20% 정확히 채움 → 추가 진입 BLOCKED
    open_positions = [{"size": 0.04, "price": 50000}]  # 0.04*50000=2000, 20%

    ts = datetime(2026, 4, 14, 14, 0, 0, tzinfo=timezone.utc)

    result = rm.evaluate(
        action="BUY",
        entry_price=50000,
        atr=500,
        account_balance=10000,
        last_candle_pct_change=0.01,
        timestamp=ts,
        open_positions=open_positions,
    )

    assert result.status == RiskStatus.BLOCKED
    assert "Total exposure limit" in result.reason
    assert "total_exposure" in result.reason
    assert result.position_size is None


# ── Multi-Position Boundary Scenarios ────────────────────────────────────────

def test_same_direction_multi_position_boundary_approved_then_blocked():
    """동일 방향(BUY) 포지션 누적: 한도 직전 APPROVED, 초과 시 BLOCKED."""
    cb = _make_cb_from_config()
    rm = RiskManager(
        risk_per_trade=0.01,
        atr_multiplier_sl=1.5,
        atr_multiplier_tp=3.0,
        max_position_size=0.10,
        circuit_breaker=cb,
        max_total_exposure=0.30,
    )

    # 경우 1: 기존 BUY 포지션 2개, 총 노출 29.9% → 한도 미만 → APPROVED
    open_positions_under = [
        {"size": 0.02, "price": 50000},  # 1000 = 10%
        {"size": 0.0199, "price": 50000},  # 995 = 9.95%  → 합 19.95%
        {"size": 0.02, "price": 50000},  # 1000 = 10%  → 합 29.95%
    ]
    # 총 노출: (0.02+0.0199+0.02)*50000 = 2995 / 10000 = 29.95% < 30% → APPROVED
    result_under = rm.evaluate(
        action="BUY",
        entry_price=50000,
        atr=500,
        account_balance=10000,
        last_candle_pct_change=0.01,
        open_positions=open_positions_under,
    )
    assert result_under.status == RiskStatus.APPROVED, (
        f"Expected APPROVED but got BLOCKED: {result_under.reason}"
    )

    # 경우 2: 기존 포지션 총 노출 정확히 30% → 한도 도달(>=) → BLOCKED
    open_positions_at = [
        {"size": 0.02, "price": 50000},  # 10%
        {"size": 0.02, "price": 50000},  # 10%
        {"size": 0.02, "price": 50000},  # 10%  → 합 30%
    ]
    result_at = rm.evaluate(
        action="BUY",
        entry_price=50000,
        atr=500,
        account_balance=10000,
        last_candle_pct_change=0.01,
        open_positions=open_positions_at,
    )
    assert result_at.status == RiskStatus.BLOCKED
    assert "total_exposure" in result_at.reason


def test_mixed_direction_positions_total_exposure_is_gross_not_net():
    """반대 방향 포지션 혼합: check_total_exposure는 net이 아닌 gross 합산 → 한도 초과 시 BLOCKED.

    BUY 포지션 20% + SELL 포지션 15% = gross 35% > 30% 한도 → BLOCKED.
    net 기준이라면 5%로 통과할 수 있으나, 현재 구현은 gross 합산 방식이어야 한다.
    """
    cb = _make_cb_from_config()
    rm = RiskManager(
        risk_per_trade=0.01,
        atr_multiplier_sl=1.5,
        atr_multiplier_tp=3.0,
        max_position_size=0.10,
        circuit_breaker=cb,
        max_total_exposure=0.30,
    )

    # BUY 포지션 20% + SELL 포지션 15% → gross 35% > 30%
    open_positions_mixed = [
        {"size": 0.04, "price": 50000},   # 2000 = 20%  (long)
        {"size": 0.03, "price": 50000},   # 1500 = 15%  (short, size는 양수로 전달)
    ]
    # gross total: (0.04+0.03)*50000 = 3500 / 10000 = 35% ≥ 30% → BLOCKED
    result = rm.evaluate(
        action="BUY",
        entry_price=50000,
        atr=500,
        account_balance=10000,
        last_candle_pct_change=0.01,
        open_positions=open_positions_mixed,
    )
    assert result.status == RiskStatus.BLOCKED
    assert "total_exposure" in result.reason

    # 반대: net이 낮아도 gross가 한도 미만이면 APPROVED
    open_positions_small = [
        {"size": 0.02, "price": 50000},   # 10%
        {"size": 0.015, "price": 50000},  # 7.5%  → gross 17.5% < 30%
    ]
    result_small = rm.evaluate(
        action="BUY",
        entry_price=50000,
        atr=500,
        account_balance=10000,
        last_candle_pct_change=0.01,
        open_positions=open_positions_small,
    )
    assert result_small.status == RiskStatus.APPROVED
