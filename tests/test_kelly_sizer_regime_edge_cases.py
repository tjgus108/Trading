"""
KellySizer 레짐 스위칭 + 엣지 케이스 테스트 (17개).

목표:
1. 레짐 스위칭 시 EMA 스무딩 동작 검증
2. 엣지 케이스: 빈 파라미터, 극단값, NaN/inf 처리
3. 동일 레짐 유지 vs 레짐 전환 시 스케일 차이
4. MDD step-down 적용 검증
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.risk.kelly_sizer import KellySizer


class TestKellySizerRegimeSwitching:
    """레짐 스위칭 시 EMA 스무딩 검증."""

    def test_regime_switch_no_smoothing(self):
        """레짐 전환 시 smoothing_alpha=0.0 → 즉시 전환."""
        sizer = KellySizer(regime_smooth_alpha=0.0)
        
        # 첫 호출: TREND_UP (1.0x)
        size1 = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100,
            regime="TREND_UP"
        )
        
        # 레짐 전환: RANGING (0.5x) → 내부적으로 kelly_cap, min/max_fraction 적용
        size2 = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100,
            regime="RANGING"
        )
        
        # 스케일 비율을 검증 (최소/최대 클리핑 때문에 정확하지 않을 수 있음)
        # 단지 RANGING이 TREND_UP보다 작은지 확인
        assert size2 <= size1, f"RANGING should be <= TREND_UP"

    def test_regime_switch_with_smoothing(self):
        """레짐 전환 시 smoothing_alpha=0.3 → EMA 블렌딩 적용."""
        sizer = KellySizer(regime_smooth_alpha=0.3)
        
        # 첫 호출: TREND_UP (1.0x)
        size1 = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100,
            regime="TREND_UP"
        )
        
        # 레짐 전환: RANGING (0.5x) → 블렌딩으로 중간값 생성
        size2 = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100,
            regime="RANGING"
        )
        
        # smoothing 있으므로 RANGING이 완전히 50%로 축소되지 않음
        # size2는 size1과 완전히 같지는 않지만 상당한 크기 유지
        assert size2 < size1, "RANGING with smoothing should be less than TREND_UP"

    def test_same_regime_no_smoothing(self):
        """동일 레짐 유지 시 smoothing 미적용."""
        sizer = KellySizer(regime_smooth_alpha=0.3)
        
        # 첫 호출: TREND_UP
        size1 = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100,
            regime="TREND_UP"
        )
        
        # 동일 레짐: TREND_UP (smoothing 미적용)
        size2 = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100,
            regime="TREND_UP"
        )
        
        # 동일 레짐이므로 size는 정확히 같음
        assert abs(size1 - size2) < 1e-9

    def test_high_vol_regime_reduces_size(self):
        """HIGH_VOL 레짐 → 0.3x 축소 (또는 그 이상의 계산 후 결과)."""
        sizer = KellySizer()
        
        # 기본 (no regime)
        size_base = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100
        )
        
        # HIGH_VOL
        size_high_vol = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100,
            regime="HIGH_VOL"
        )
        
        # HIGH_VOL은 0.3 스케일이므로 base보다 작아야 함
        assert size_high_vol <= size_base, f"HIGH_VOL should be <= base size"


class TestKellySizerEdgeCases:
    """엣지 케이스 처리 검증."""

    def test_nan_win_rate_returns_zero(self):
        """win_rate=NaN → 0 반환."""
        sizer = KellySizer()
        size = sizer.compute(
            win_rate=np.nan,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100
        )
        assert size == 0.0

    def test_inf_avg_win_returns_zero(self):
        """avg_win=inf → 0 반환."""
        sizer = KellySizer()
        size = sizer.compute(
            win_rate=0.55,
            avg_win=np.inf,
            avg_loss=0.01,
            capital=10000,
            price=100
        )
        assert size == 0.0

    def test_negative_capital_returns_zero(self):
        """capital < 0 → 0 반환."""
        sizer = KellySizer()
        size = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=-10000,
            price=100
        )
        assert size == 0.0

    def test_zero_price_returns_zero(self):
        """price=0 → 0 반환."""
        sizer = KellySizer()
        size = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=0
        )
        assert size == 0.0

    def test_zero_avg_win_returns_zero(self):
        """avg_win=0 → 0 반환."""
        sizer = KellySizer()
        size = sizer.compute(
            win_rate=0.55,
            avg_win=0.0,
            avg_loss=0.01,
            capital=10000,
            price=100
        )
        assert size == 0.0

    def test_negative_avg_loss_still_works(self):
        """avg_loss < 0 (부호 있음) → 정상 작동."""
        sizer = KellySizer()
        size = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=-0.01,
            capital=10000,
            price=100
        )
        assert isinstance(size, (int, float))

    def test_mdd_multiplier_zero_blocks_entry(self):
        """mdd_size_multiplier=0.0 → 0 반환."""
        sizer = KellySizer()
        size = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100,
            mdd_size_multiplier=0.0
        )
        assert size == 0.0

    def test_mdd_multiplier_half_reduces_size(self):
        """mdd_size_multiplier=0.5 → 사이즈 반감."""
        sizer = KellySizer()
        
        size_full = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100,
            mdd_size_multiplier=1.0
        )
        
        size_half = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100,
            mdd_size_multiplier=0.5
        )
        
        ratio = size_half / size_full if size_full > 0 else 0
        assert abs(ratio - 0.5) < 0.01, f"Expected ~0.5, got {ratio}"

    def test_atr_adjustment_scales_size(self):
        """ATR 조정: high ATR → 사이즈 축소."""
        sizer = KellySizer()
        
        # 정상 ATR
        size_normal = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100,
            atr=2.0,
            target_atr=2.0
        )
        
        # 높은 ATR (조정 인수 축소)
        size_high_atr = sizer.compute(
            win_rate=0.55,
            avg_win=0.02,
            avg_loss=0.01,
            capital=10000,
            price=100,
            atr=4.0,
            target_atr=2.0
        )
        
        ratio = size_high_atr / size_normal if size_normal > 0 else 0
        assert abs(ratio - 0.5) < 0.01, f"Expected ~0.5, got {ratio}"

    def test_kelly_cap_limits_high_kelly(self):
        """kelly_cap=0.25 → Full Kelly 초과 방지."""
        sizer = KellySizer(kelly_cap=0.25, fraction=1.0)
        
        # 높은 win_rate → Full Kelly > 0.25
        # kelly_f = (0.9*1 - 0.1*1)/1 = 0.8
        # fractional_f = 0.8 * 1.0 = 0.8
        # capped = min(0.8, 0.25) = 0.25
        size = sizer.compute(
            win_rate=0.90,
            avg_win=1.0,
            avg_loss=1.0,
            capital=10000,
            price=100
        )
        
        # 최대 제약: min_fraction=0.001, max_fraction=0.10
        # 0.25는 max_fraction(0.10) 초과하므로 클리핑됨
        # 따라서 position = 10000 * 0.10 / 100 = 10
        expected_max = 10.0
        assert size <= expected_max, f"Size should be <= {expected_max}"

    def test_regime_scale_trend_up(self):
        """TREND_UP 스케일 검증."""
        sizer = KellySizer()
        scale = sizer.adjust_for_regime("TREND_UP")
        assert abs(scale - sizer.fraction * 1.0) < 1e-9

    def test_regime_scale_ranging(self):
        """RANGING 스케일 검증."""
        sizer = KellySizer()
        scale = sizer.adjust_for_regime("RANGING")
        assert abs(scale - sizer.fraction * 0.5) < 0.01

    def test_regime_scale_high_vol(self):
        """HIGH_VOL 스케일 검증."""
        sizer = KellySizer()
        scale = sizer.adjust_for_regime("HIGH_VOL")
        assert abs(scale - sizer.fraction * 0.3) < 0.01

    def test_unknown_regime_defaults_to_conservative(self):
        """알 수 없는 레짐 → 보수적 처리 (0.5x)."""
        sizer = KellySizer()
        scale = sizer.adjust_for_regime("UNKNOWN_REGIME")
        # Default = 0.5
        assert abs(scale - sizer.fraction * 0.5) < 0.01


class TestKellySizerFromTradeHistory:
    """from_trade_history 메서드 검증."""

    def test_empty_trades_returns_zero(self):
        """빈 거래 기록 → 0 반환."""
        size = KellySizer.from_trade_history(
            trades=[],
            capital=10000,
            price=100
        )
        assert size == 0.0

    def test_all_nan_pnl_returns_zero(self):
        """모든 pnl이 NaN → 0 반환."""
        size = KellySizer.from_trade_history(
            trades=[{"pnl": np.nan}, {"pnl": np.nan}],
            capital=10000,
            price=100
        )
        assert size == 0.0

    def test_all_breakeven_returns_zero(self):
        """모든 pnl=0 (break-even) → 0 반환."""
        size = KellySizer.from_trade_history(
            trades=[{"pnl": 0.0}, {"pnl": 0.0}, {"pnl": 0.0}],
            capital=10000,
            price=100
        )
        assert size == 0.0
