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


# ── Risk-Constrained Kelly 테스트 ────────────────────────────────────────────

def test_dd_constraint_reduces_size():
    """max_drawdown 제약이 있을 때 size가 unconstrained보다 작거나 같음."""
    # avg_loss=0.10 (10%), leverage=1 → max_dd_constrained = 0.05/0.10 = 0.50
    # Half-Kelly가 0.50을 초과할 만큼 win_rate를 높게 설정
    sizer_unconstrained = KellySizer(fraction=0.5, max_fraction=0.10)
    sizer_constrained = KellySizer(fraction=0.5, max_fraction=0.10, max_drawdown=0.05, leverage=1.0)

    qty_unc = sizer_unconstrained.compute(
        win_rate=0.9, avg_win=0.20, avg_loss=0.10, capital=10000, price=100
    )
    qty_con = sizer_constrained.compute(
        win_rate=0.9, avg_win=0.20, avg_loss=0.10, capital=10000, price=100
    )
    assert qty_con <= qty_unc


def test_dd_constraint_binding():
    """max_dd_constrained < half_kelly 일 때 DD 값이 실제로 binding됨."""
    # avg_loss=0.02, leverage=2 → max_dd_constrained = 0.05 / (0.02 * 2) = 1.25 → clipped at max_fraction=0.10
    # avg_loss=0.50, leverage=2 → max_dd_constrained = 0.05 / (0.50 * 2) = 0.05
    # Half-Kelly(win_rate=0.7, avg_win=0.5, avg_loss=0.5) = (0.7*0.5 - 0.3*0.5)/0.5 * 0.5 = 0.4 * 0.5 = 0.20
    # DD constrained = 0.05 / (0.50*2) = 0.05 → binding (0.05 < 0.20), clipped at max_fraction=0.10 → min(0.05, 0.10)=0.05
    sizer = KellySizer(fraction=0.5, max_fraction=0.10, max_drawdown=0.05, leverage=2.0)
    qty = sizer.compute(
        win_rate=0.7, avg_win=0.50, avg_loss=0.50, capital=10000, price=100
    )
    # position_capital = 10000 * 0.05 = 500, qty = 500/100 = 5.0
    assert abs(qty - 5.0) < 1e-6


def test_dd_constraint_none_no_effect():
    """max_drawdown=None이면 기존 동작과 동일."""
    sizer_default = KellySizer(fraction=0.5, max_fraction=0.10)
    sizer_none_dd = KellySizer(fraction=0.5, max_fraction=0.10, max_drawdown=None)

    qty_d = sizer_default.compute(
        win_rate=0.6, avg_win=0.02, avg_loss=0.01, capital=10000, price=100
    )
    qty_n = sizer_none_dd.compute(
        win_rate=0.6, avg_win=0.02, avg_loss=0.01, capital=10000, price=100
    )
    assert abs(qty_d - qty_n) < 1e-9


# ── avg_loss = 0 경계 테스트 ─────────────────────────────────────────────────

def test_avg_loss_zero_no_division_error():
    """avg_loss=0 시 ZeroDivisionError 없이 양수 반환 (all-win 기록)."""
    sizer = KellySizer(fraction=0.5, max_fraction=0.10)
    qty = sizer.compute(win_rate=1.0, avg_win=0.05, avg_loss=0.0, capital=10000, price=100)
    assert qty > 0  # kelly_f = 1.0 → fractional=0.5 → clipped at 0.10

def test_from_trade_history_all_wins_no_error():
    """손실 거래 없는 기록 → avg_loss=0 → 정상 수량 반환."""
    trades = [{"pnl": 100}, {"pnl": 200}, {"pnl": 50}]
    qty = KellySizer.from_trade_history(trades, capital=10000, price=1000)
    assert qty >= 0


def test_kelly_sizer_default_fraction_is_half_kelly():
    """KellySizer 기본 fraction=0.5 (Half-Kelly) 확인 및 Quarter-Kelly(0.25)는 정확히 절반."""
    # max_fraction을 높여서 clip 없이 ratio 확인
    half = KellySizer(fraction=0.5, max_fraction=0.50)
    quarter = KellySizer(fraction=0.25, max_fraction=0.50)
    assert half.fraction == 0.5
    qty_half = half.compute(win_rate=0.6, avg_win=0.02, avg_loss=0.01, capital=10000, price=100)
    qty_quarter = quarter.compute(win_rate=0.6, avg_win=0.02, avg_loss=0.01, capital=10000, price=100)
    # Half은 Quarter의 2배여야 함
    assert abs(qty_half / qty_quarter - 2.0) < 1e-9


# ── Kelly input validation 테스트 ──────────────────────────────────────────────

def test_compute_clips_win_rate_above_one():
    """win_rate > 1.0 전달 시 1.0으로 클리핑되어 정상 수량 반환."""
    sizer = KellySizer(fraction=0.5, max_fraction=0.10)
    qty_clipped = sizer.compute(win_rate=1.5, avg_win=0.02, avg_loss=0.01,
                                capital=10000, price=100)
    qty_one = sizer.compute(win_rate=1.0, avg_win=0.02, avg_loss=0.01,
                            capital=10000, price=100)
    assert qty_clipped == pytest.approx(qty_one)
    assert qty_clipped > 0


def test_compute_clips_win_rate_below_zero():
    """win_rate < 0 전달 시 0.0으로 클리핑 → kelly_f <= 0 → 0 반환."""
    sizer = KellySizer(fraction=0.5, max_fraction=0.10)
    qty = sizer.compute(win_rate=-0.5, avg_win=0.02, avg_loss=0.01,
                        capital=10000, price=100)
    assert qty == 0.0


def test_compute_nan_inputs_return_zero():
    """NaN 입력 시 0 반환 (예외 없음)."""
    sizer = KellySizer()
    assert sizer.compute(float("nan"), 0.02, 0.01, 10000, 100) == 0.0
    assert sizer.compute(0.6, float("nan"), 0.01, 10000, 100) == 0.0
    assert sizer.compute(0.6, 0.02, float("nan"), 10000, 100) == 0.0


def test_compute_inf_inputs_return_zero():
    """inf 입력 시 0 반환 (예외 없음)."""
    sizer = KellySizer()
    assert sizer.compute(float("inf"), 0.02, 0.01, 10000, 100) == 0.0
    assert sizer.compute(0.6, float("inf"), 0.01, 10000, 100) == 0.0


def test_compute_negative_capital_returns_zero():
    """capital <= 0 시 0 반환."""
    sizer = KellySizer()
    assert sizer.compute(0.6, 0.02, 0.01, -100, 100) == 0.0
    assert sizer.compute(0.6, 0.02, 0.01, 0, 100) == 0.0


def test_compute_negative_price_returns_zero():
    """price <= 0 시 0 반환."""
    sizer = KellySizer()
    assert sizer.compute(0.6, 0.02, 0.01, 10000, -50) == 0.0
    assert sizer.compute(0.6, 0.02, 0.01, 10000, 0) == 0.0


# ── from_trade_history 소표본 shrinkage 테스트 ────────────────────────────────

def test_small_sample_shrinks_win_rate():
    """거래 수 < MIN_TRADES_FOR_KELLY(10): Bayesian shrinkage로 size가 줄어야 함."""
    # 3개 거래(전부 승) → raw win_rate=1.0
    # shrinkage: 3/(3+10)*1.0 + 7/10*0.5 = 0.231 + 0.385 = 약 0.615
    small_trades = [{"pnl": 100}, {"pnl": 200}, {"pnl": 50}]
    qty_small = KellySizer.from_trade_history(
        small_trades, capital=10000, price=1000,
        fraction=0.5, max_fraction=0.50,
    )

    # 30개 거래(전부 승) → raw win_rate=1.0, shrinkage 미적용
    # shrink_factor = 30/(30+10) = 0.75 → 적용 안됨 (n >= threshold)
    large_trades = [{"pnl": 100}] * 30
    qty_large = KellySizer.from_trade_history(
        large_trades, capital=10000, price=1000,
        fraction=0.5, max_fraction=0.50,
    )

    # 소표본은 win_rate shrinkage로 인해 대표본보다 작거나 같아야 함
    assert qty_small <= qty_large + 1e-9


def test_all_breakeven_returns_zero():
    """모든 거래가 pnl=0(break-even) → edge 없음 → 0 반환."""
    trades = [{"pnl": 0.0}, {"pnl": 0.0}, {"pnl": 0.0}]
    qty = KellySizer.from_trade_history(trades, capital=10000, price=1000)
    assert qty == 0.0


def test_nan_pnl_filtered():
    """pnl에 NaN이 포함되면 해당 거래는 제외되어야 함."""
    trades = [
        {"pnl": 100}, {"pnl": float("nan")}, {"pnl": -50}, {"pnl": 80},
    ]
    # NaN 제거 후 3개 거래로 계산
    qty = KellySizer.from_trade_history(trades, capital=10000, price=1000)
    assert qty >= 0  # 예외 없이 정상 반환


def test_custom_min_trades():
    """min_trades 파라미터로 shrinkage 임계값 조정."""
    trades = [{"pnl": 100}, {"pnl": 200}, {"pnl": 150}, {"pnl": -30}, {"pnl": 80}]
    # min_trades=5 → n=5, shrink_factor=5/(5+5)=0.5
    qty_strict = KellySizer.from_trade_history(
        trades, capital=10000, price=1000,
        fraction=0.5, max_fraction=0.50, min_trades=5,
    )
    # min_trades=3 → n=5 >= 3 → shrinkage 미적용
    qty_lenient = KellySizer.from_trade_history(
        trades, capital=10000, price=1000,
        fraction=0.5, max_fraction=0.50, min_trades=3,
    )
    # strict 버전은 shrinkage로 인해 더 작거나 같아야 함
    assert qty_strict <= qty_lenient + 1e-9
