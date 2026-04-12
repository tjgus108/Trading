"""position_sizer / KellySizer 극단 케이스 스트레스 테스트."""

import pytest
from src.risk.position_sizer import kelly_position_size, kelly_position_size_from_sizer
from src.risk.kelly_sizer import KellySizer


# ── 1. Zero balance ──────────────────────────────────────────────────────────

def test_kelly_position_size_zero_balance():
    """자본 0 → 0 반환 (ZeroDivision 없음)."""
    result = kelly_position_size(win_rate=0.6, win_loss_ratio=2.0, capital=0.0)
    assert result == 0.0


def test_kelly_sizer_zero_balance():
    """KellySizer.compute: capital=0 → qty 0."""
    sizer = KellySizer()
    qty = sizer.compute(win_rate=0.6, avg_win=0.02, avg_loss=0.01, capital=0.0, price=50000.0)
    assert qty == 0.0


def test_kelly_from_sizer_zero_balance():
    """kelly_position_size_from_sizer: capital=0 → 0."""
    qty = kelly_position_size_from_sizer(
        win_rate=0.6, avg_win=0.02, avg_loss=0.01,
        capital=0.0, price=50000.0,
    )
    assert qty == 0.0


# ── 2. Extreme / pathological ATR (excessive volatility) ────────────────────

def test_kelly_sizer_extreme_atr_reduces_size():
    """ATR이 target_atr의 100배 → atr_factor=0.01 → 사이즈 대폭 축소."""
    sizer = KellySizer(max_fraction=0.10)
    normal_qty = sizer.compute(0.6, 0.02, 0.01, 10000.0, 50000.0,
                               atr=100.0, target_atr=100.0)
    extreme_qty = sizer.compute(0.6, 0.02, 0.01, 10000.0, 50000.0,
                                atr=10000.0, target_atr=100.0)
    assert extreme_qty < normal_qty
    assert extreme_qty >= 0.0


def test_kelly_sizer_zero_atr_skips_adjustment():
    """atr=0 → ATR 조정 스킵 (ZeroDivision 없음), 정상 수량 반환."""
    sizer = KellySizer()
    qty = sizer.compute(0.6, 0.02, 0.01, 10000.0, 50000.0,
                        atr=0.0, target_atr=100.0)
    assert qty > 0.0


# ── 3. Tiny stop distance (avg_loss ≈ 0) ────────────────────────────────────

def test_kelly_sizer_tiny_avg_loss_capped():
    """avg_loss 극소값 → max_fraction 상한에 클리핑."""
    sizer = KellySizer(max_fraction=0.10)
    qty = sizer.compute(0.6, 0.02, 1e-10, 10000.0, 50000.0)
    max_possible = 10000.0 * 0.10 / 50000.0
    assert qty <= max_possible + 1e-12


def test_kelly_sizer_avg_loss_zero_returns_zero():
    """avg_win=0 → 0 반환 (guard 조건)."""
    sizer = KellySizer()
    qty = sizer.compute(0.6, 0.0, 0.01, 10000.0, 50000.0)
    assert qty == 0.0


# ── 4. Negative / degenerate Kelly ──────────────────────────────────────────

def test_kelly_position_size_negative_kelly():
    """승률 10% + 낮은 win_loss_ratio → Kelly 음수 → 0 반환."""
    result = kelly_position_size(win_rate=0.1, win_loss_ratio=0.5, capital=10000.0)
    assert result == 0.0


def test_kelly_sizer_win_rate_zero():
    """win_rate=0 → Kelly ≤ 0 → 0 반환."""
    sizer = KellySizer()
    qty = sizer.compute(0.0, 0.02, 0.01, 10000.0, 50000.0)
    assert qty == 0.0
