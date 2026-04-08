"""
RiskManager / CircuitBreaker 단위 테스트.
"""

import math

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
