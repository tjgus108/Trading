"""
VolTargeting 통합 포지션 사이징 테스트.

1. volatility_targeted_position_size(): VolTargeting 단독 호출
2. kelly_with_vol_targeting(): Kelly + Vol 통합
3. DrawdownMonitor 연동
"""

import pytest
import numpy as np
import pandas as pd

from src.risk.position_sizer import (
    volatility_targeted_position_size,
    kelly_with_vol_targeting,
)
from src.risk.drawdown_monitor import DrawdownMonitor


def _make_df(closes):
    """DataFrame 생성 헬퍼."""
    closes = np.asarray(closes, dtype=float)
    return pd.DataFrame({"close": closes})


# ──────────────────────────────────────────────────────────────────────
# Test: volatility_targeted_position_size
# ──────────────────────────────────────────────────────────────────────

def test_volatility_targeted_base_size_zero():
    """base_size=0 → 0.0 반환 + 경고."""
    df = _make_df(np.linspace(100, 110, 25))
    result = volatility_targeted_position_size(base_size=0.0, df=df)
    assert result == 0.0


def test_volatility_targeted_base_size_negative():
    """base_size<0 → 0.0 반환 + 경고."""
    df = _make_df(np.linspace(100, 110, 25))
    result = volatility_targeted_position_size(base_size=-1.0, df=df)
    assert result == 0.0


def test_volatility_targeted_low_volatility():
    """변동성 낮음 → adjusted > base_size."""
    df = _make_df([100.0] * 24 + [100.001])  # 거의 flat
    base_size = 0.5
    result = volatility_targeted_position_size(base_size=base_size, df=df, target_vol=0.20)
    # rv ≈ 0 → fallback 또는 극소 → scalar=2.0(max) → result ≈ base_size * 2.0
    assert result >= base_size, "Low vol should increase size"


def test_volatility_targeted_high_volatility():
    """변동성 높음 → adjusted < base_size."""
    rng = np.random.default_rng(42)
    log_rets = rng.normal(0, 0.40, 24)  # 높은 변동성
    closes = 100 * np.exp(np.concatenate([[0], np.cumsum(log_rets)]))
    df = pd.DataFrame({"close": closes})
    
    base_size = 1.0
    result = volatility_targeted_position_size(
        base_size=base_size,
        df=df,
        target_vol=0.20,
        min_scalar=0.1,
    )
    # rv >> target_vol → scalar < 1.0 → result < base_size
    assert result < base_size, "High vol should reduce size"


def test_volatility_targeted_df_none():
    """df=None일 때 처리."""
    # df가 없으면 에러 발생할 수 있음 — 명시적으로 테스트
    try:
        result = volatility_targeted_position_size(base_size=1.0, df=None)
        # None을 전달했으므로 에러 또는 특정 동작
    except (TypeError, AttributeError):
        # VolTargeting이 df를 요구하므로 정상
        pass


def test_volatility_targeted_empty_df():
    """df가 비어있거나 길이 < 2."""
    df_empty = pd.DataFrame({"close": []})
    df_one = pd.DataFrame({"close": [100.0]})
    
    # 둘 다 fallback rv = target_vol → scalar = 1.0
    result_empty = volatility_targeted_position_size(base_size=0.5, df=df_empty)
    result_one = volatility_targeted_position_size(base_size=0.5, df=df_one)
    
    assert result_empty == 0.5
    assert result_one == 0.5


# ──────────────────────────────────────────────────────────────────────
# Test: kelly_with_vol_targeting
# ──────────────────────────────────────────────────────────────────────

def test_kelly_with_vol_targeting_no_df():
    """df=None → Kelly만 적용."""
    size = kelly_with_vol_targeting(
        win_rate=0.6,
        avg_win=0.02,
        avg_loss=0.01,
        capital=100_000,
        price=50_000,
        df=None,  # VolTargeting 스킵
    )
    assert size > 0, "Positive Kelly edge should yield > 0"


def test_kelly_with_vol_targeting_with_df():
    """df 제공 → Kelly + VolTargeting 순차 적용."""
    df = _make_df(np.linspace(100, 110, 25))
    
    size_no_vol = kelly_with_vol_targeting(
        win_rate=0.6,
        avg_win=0.02,
        avg_loss=0.01,
        capital=100_000,
        price=50_000,
        df=None,
    )
    
    size_with_vol = kelly_with_vol_targeting(
        win_rate=0.6,
        avg_win=0.02,
        avg_loss=0.01,
        capital=100_000,
        price=50_000,
        df=df,  # VolTargeting 활성화
    )
    
    # 결과가 모두 양수여야 함
    assert size_no_vol > 0
    assert size_with_vol > 0


def test_kelly_with_vol_targeting_drawdown_multiplier():
    """size_multiplier 적용 (DrawdownMonitor 연동)."""
    df = _make_df(np.linspace(100, 110, 25))
    
    base_size = kelly_with_vol_targeting(
        win_rate=0.6,
        avg_win=0.02,
        avg_loss=0.01,
        capital=100_000,
        price=50_000,
        df=df,
        size_multiplier=1.0,  # 정상
    )
    
    reduced_size = kelly_with_vol_targeting(
        win_rate=0.6,
        avg_win=0.02,
        avg_loss=0.01,
        capital=100_000,
        price=50_000,
        df=df,
        size_multiplier=0.5,  # 연속 손실 → 50% 축소
    )
    
    assert reduced_size < base_size
    assert abs(reduced_size - base_size * 0.5) < 1e-6


def test_kelly_with_vol_targeting_cooldown_multiplier_zero():
    """size_multiplier=0 (쿨다운) → 최종 사이즈=0."""
    df = _make_df(np.linspace(100, 110, 25))
    
    size = kelly_with_vol_targeting(
        win_rate=0.6,
        avg_win=0.02,
        avg_loss=0.01,
        capital=100_000,
        price=50_000,
        df=df,
        size_multiplier=0.0,  # 쿨다운: 주문 거부
    )
    
    assert size == 0.0


def test_kelly_with_vol_targeting_negative_kelly_edge():
    """음수 edge → kelly_size=0 → 최종=0."""
    df = _make_df(np.linspace(100, 110, 25))
    
    size = kelly_with_vol_targeting(
        win_rate=0.3,
        avg_win=0.01,
        avg_loss=0.05,  # 손실이 더 큼
        capital=100_000,
        price=50_000,
        df=df,
    )
    
    assert size == 0.0


def test_kelly_with_vol_targeting_sequence():
    """워크플로우 검증: Kelly > VolTargeting > DrawdownMultiplier."""
    df = _make_df(np.linspace(100, 105, 30))  # 상승 추세
    
    # Kelly 계산
    size1 = kelly_with_vol_targeting(
        win_rate=0.6, avg_win=0.02, avg_loss=0.01,
        capital=100_000, price=50_000,
        df=None,  # Kelly만
        size_multiplier=1.0,
    )
    
    # Kelly + VolTargeting
    size2 = kelly_with_vol_targeting(
        win_rate=0.6, avg_win=0.02, avg_loss=0.01,
        capital=100_000, price=50_000,
        df=df,  # VolTargeting 추가
        size_multiplier=1.0,
    )
    
    # Kelly + VolTargeting + DrawdownMultiplier (0.5)
    size3 = kelly_with_vol_targeting(
        win_rate=0.6, avg_win=0.02, avg_loss=0.01,
        capital=100_000, price=50_000,
        df=df,
        size_multiplier=0.5,  # 연속 손실로 축소
    )
    
    # size1 ≥ size2 또는 size1 ≤ size2 (VolTargeting 영향)
    # size3 < size2 (DrawdownMultiplier 적용)
    assert size3 < size2, "DrawdownMultiplier should reduce final size"


# ──────────────────────────────────────────────────────────────────────
# Test: DrawdownMonitor 연동
# ──────────────────────────────────────────────────────────────────────

def test_kelly_with_drawdown_monitor_normal():
    """DrawdownMonitor 정상 상태 → size_multiplier=1.0."""
    monitor = DrawdownMonitor()
    monitor.update(current_equity=10_000)
    
    assert monitor.get_size_multiplier() == 1.0


def test_kelly_with_drawdown_monitor_consecutive_losses():
    """연속 손실 3회 → size_multiplier=0.5."""
    monitor = DrawdownMonitor(loss_streak_threshold=3)
    
    # 3회 연속 손실 기록
    monitor.record_trade_result(pnl=-100, equity=9_900)
    monitor.record_trade_result(pnl=-100, equity=9_800)
    monitor.record_trade_result(pnl=-100, equity=9_700)
    
    assert monitor.get_size_multiplier() == 0.5


def test_kelly_with_drawdown_monitor_cooldown():
    """큰 손실로 쿨다운 시작 → size_multiplier=0."""
    monitor = DrawdownMonitor(single_loss_halt_pct=0.02)  # 2% 손실 시 쿨다운
    
    # 2.5% 손실 발생
    monitor.record_trade_result(pnl=-250, equity=9_750)
    
    assert monitor.is_in_cooldown() is True
    assert monitor.get_size_multiplier() == 0.0


def test_kelly_with_drawdown_monitor_integration():
    """최종 통합: Kelly + VolTargeting + DrawdownMonitor."""
    monitor = DrawdownMonitor(loss_streak_threshold=3)
    df = _make_df(np.linspace(100, 110, 25))
    
    # 정상 상태
    size_normal = kelly_with_vol_targeting(
        win_rate=0.6, avg_win=0.02, avg_loss=0.01,
        capital=100_000, price=50_000,
        df=df,
        size_multiplier=monitor.get_size_multiplier(),
    )
    
    # 연속 손실 기록
    monitor.record_trade_result(pnl=-50, equity=99_950)
    monitor.record_trade_result(pnl=-50, equity=99_900)
    monitor.record_trade_result(pnl=-50, equity=99_850)
    
    # 축소된 상태
    size_reduced = kelly_with_vol_targeting(
        win_rate=0.6, avg_win=0.02, avg_loss=0.01,
        capital=100_000, price=50_000,
        df=df,
        size_multiplier=monitor.get_size_multiplier(),
    )
    
    assert size_reduced < size_normal, "Size should reduce after consecutive losses"
    assert size_reduced == size_normal * 0.5
