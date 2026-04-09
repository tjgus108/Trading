"""
Kelly Criterion 통합 테스트.
position_sizer.kelly_position_size() 및 KellySizer 연결 검증.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.risk.position_sizer import kelly_position_size, kelly_position_size_from_sizer
from src.risk.kelly_sizer import KellySizer


# ── kelly_position_size 테스트 ───────────────────────────────────────────────

def test_basic_calculation():
    """kelly_position_size(0.6, 2.0, 10000) 기본 계산 검증."""
    # Full Kelly = (0.6*2 - 0.4*1) / 2 = (1.2-0.4)/2 = 0.4
    # Fractional (0.25) = 0.4 * 0.25 = 0.1
    # Position = 10000 * 0.1 = 1000
    result = kelly_position_size(0.6, 2.0, 10000)
    assert abs(result - 1000.0) < 1e-6


def test_win_rate_zero_returns_zero():
    """win_rate=0 시 0 반환."""
    result = kelly_position_size(0.0, 2.0, 10000)
    assert result == 0.0


def test_negative_kelly_returns_zero():
    """기대값이 음수일 때 0 반환 (win_rate 너무 낮음)."""
    # win_rate=0.2, ratio=1.0 → Full Kelly = (0.2-0.8)/1 = -0.6 → 0
    result = kelly_position_size(0.2, 1.0, 10000)
    assert result == 0.0


def test_kelly_fraction_parameter():
    """kelly_fraction 파라미터가 결과에 반영됨."""
    r_25 = kelly_position_size(0.6, 2.0, 10000, kelly_fraction=0.25)
    r_50 = kelly_position_size(0.6, 2.0, 10000, kelly_fraction=0.50)
    assert abs(r_50 - r_25 * 2) < 1e-6


def test_kelly_fraction_half_vs_quarter():
    """fraction=0.5는 fraction=0.25의 정확히 2배."""
    base = kelly_position_size(0.55, 1.5, 5000, kelly_fraction=0.25)
    double = kelly_position_size(0.55, 1.5, 5000, kelly_fraction=0.50)
    assert abs(double / base - 2.0) < 1e-9


def test_capital_scales_linearly():
    """자본이 2배면 포지션도 2배."""
    r1 = kelly_position_size(0.6, 2.0, 10000)
    r2 = kelly_position_size(0.6, 2.0, 20000)
    assert abs(r2 / r1 - 2.0) < 1e-9


def test_zero_capital_returns_zero():
    """capital=0 시 0 반환."""
    result = kelly_position_size(0.6, 2.0, 0)
    assert result == 0.0


def test_zero_win_loss_ratio_returns_zero():
    """win_loss_ratio=0 시 0 반환."""
    result = kelly_position_size(0.6, 0.0, 10000)
    assert result == 0.0


def test_max_cap_25_percent():
    """포지션이 자본의 25%를 초과하지 않음."""
    # 매우 높은 win_rate로 큰 kelly 값 유도
    result = kelly_position_size(0.99, 10.0, 10000, kelly_fraction=1.0)
    assert result <= 10000 * 0.25 + 1e-9


# ── KellySizer 직접 통합 테스트 ─────────────────────────────────────────────

def test_kelly_sizer_compute_basic():
    """KellySizer.compute() 기본 동작."""
    sizer = KellySizer(fraction=0.25, max_fraction=0.10)
    qty = sizer.compute(win_rate=0.6, avg_win=0.02, avg_loss=0.01, capital=10000, price=100)
    assert qty > 0


def test_kelly_position_size_from_sizer_returns_units():
    """kelly_position_size_from_sizer는 수량(units)을 반환."""
    qty = kelly_position_size_from_sizer(
        win_rate=0.6, avg_win=0.02, avg_loss=0.01,
        capital=10000, price=50000, kelly_fraction=0.25,
    )
    assert qty > 0
    # 수량 * 가격 <= 자본의 25%
    assert qty * 50000 <= 10000 * 0.25 + 1e-6


def test_kelly_sizer_from_trade_history():
    """from_trade_history 클래스 메서드 정상 동작."""
    trades = [
        {"pnl": 100}, {"pnl": 150}, {"pnl": -50},
        {"pnl": 80}, {"pnl": -30}, {"pnl": 120},
    ]
    qty = KellySizer.from_trade_history(trades, capital=10000, price=1000)
    assert qty >= 0
