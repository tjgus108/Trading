"""
Kelly Quarter-Cap + MDD Step-Down 통합 테스트.

Quarter-Kelly cap: fractional_f = min(kelly_f * fraction, kelly_cap)
MDD step-down: compute()에 mdd_size_multiplier를 전달하여 DrawdownMonitor 연동.
"""

import pytest
import numpy as np

from src.risk.kelly_sizer import KellySizer
from src.risk.drawdown_monitor import DrawdownMonitor, MddLevel


# ── Quarter-Cap 기본 동작 ────────────────────────────────────────────────────


class TestQuarterCap:
    """kelly_cap 파라미터가 fractional Kelly를 올바르게 제한하는지 검증."""

    def test_default_kelly_cap_is_025(self):
        """기본 kelly_cap=0.25 확인."""
        sizer = KellySizer()
        assert sizer.kelly_cap == 0.25

    def test_quarter_cap_limits_high_kelly(self):
        """극단적 edge에서 fractional_f가 kelly_cap(0.25)을 초과하지 않음."""
        # fraction=1.0 (Full Kelly), kelly_f ≈ 0.98 → fractional_f=0.98
        # kelly_cap=0.25 → min(0.98, 0.25) = 0.25
        # max_fraction=1.0 → clip 안 걸림
        sizer = KellySizer(fraction=1.0, max_fraction=1.0, kelly_cap=0.25)
        qty = sizer.compute(
            win_rate=0.99, avg_win=0.50, avg_loss=0.01,
            capital=100_000, price=1.0,
        )
        # position_capital = 100_000 * 0.25 = 25_000
        assert abs(qty - 25_000.0) < 1e-6

    def test_quarter_cap_not_binding_when_low_kelly(self):
        """Kelly fraction이 cap 이하일 때 cap이 영향을 주지 않음."""
        # win_rate=0.55, avg_win=0.02, avg_loss=0.01
        # kelly_f = (0.55*0.02 - 0.45*0.01)/0.02 = (0.011-0.0045)/0.02 = 0.325
        # fractional_f = 0.325 * 0.5 = 0.1625 < 0.25 → cap 미적용
        sizer_with_cap = KellySizer(fraction=0.5, max_fraction=0.50, kelly_cap=0.25)
        sizer_no_cap = KellySizer(fraction=0.5, max_fraction=0.50, kelly_cap=1.0)

        qty_cap = sizer_with_cap.compute(
            win_rate=0.55, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
        )
        qty_no_cap = sizer_no_cap.compute(
            win_rate=0.55, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
        )
        assert abs(qty_cap - qty_no_cap) < 1e-9

    def test_custom_kelly_cap(self):
        """kelly_cap=0.10 커스텀 값 동작 확인."""
        sizer = KellySizer(fraction=1.0, max_fraction=1.0, kelly_cap=0.10)
        qty = sizer.compute(
            win_rate=0.99, avg_win=0.50, avg_loss=0.01,
            capital=100_000, price=1.0,
        )
        # fractional_f = min(~0.98, 0.10) = 0.10
        assert abs(qty - 10_000.0) < 1e-6

    def test_kelly_cap_applied_before_regime_scale(self):
        """kelly_cap은 regime 스케일 적용 전에 적용됨.

        순서: fractional_f → cap → DD 제약 → regime → clip → ATR → MDD mult
        """
        sizer = KellySizer(fraction=1.0, max_fraction=1.0, kelly_cap=0.20)
        # HIGH_VOL regime: 0.3x
        qty = sizer.compute(
            win_rate=0.99, avg_win=0.50, avg_loss=0.01,
            capital=100_000, price=1.0,
            regime="HIGH_VOL",
        )
        # fractional_f = min(~0.98, 0.20) = 0.20
        # regime: 0.20 * 0.3 = 0.06
        # clip: max(0.001, min(0.06, 1.0)) = 0.06
        assert abs(qty - 6_000.0) < 1e-6

    def test_quarter_cap_from_trade_history(self):
        """from_trade_history에서 kelly_cap 전달 동작."""
        trades = [{"pnl": 500}] * 20 + [{"pnl": -10}] * 2
        # 높은 win_rate, 큰 avg_win → full kelly 크다
        qty_capped = KellySizer.from_trade_history(
            trades, capital=100_000, price=1.0,
            fraction=1.0, max_fraction=1.0, kelly_cap=0.15,
        )
        qty_uncapped = KellySizer.from_trade_history(
            trades, capital=100_000, price=1.0,
            fraction=1.0, max_fraction=1.0, kelly_cap=1.0,
        )
        assert qty_capped <= qty_uncapped
        # cap이 binding: position_capital <= 100_000 * 0.15
        assert qty_capped <= 100_000 * 0.15 + 1e-6


# ── MDD Step-Down 통합 ──────────────────────────────────────────────────────


class TestMddStepDown:
    """DrawdownMonitor의 mdd_size_multiplier와 KellySizer 연동 검증."""

    def _make_sizer(self, **kwargs):
        defaults = dict(fraction=0.5, max_fraction=0.10, kelly_cap=0.25)
        defaults.update(kwargs)
        return KellySizer(**defaults)

    def test_mdd_multiplier_1_no_effect(self):
        """mdd_size_multiplier=1.0 → 정상 사이즈."""
        sizer = self._make_sizer()
        qty_normal = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
            mdd_size_multiplier=1.0,
        )
        qty_default = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
        )
        assert abs(qty_normal - qty_default) < 1e-9

    def test_mdd_multiplier_05_halves_size(self):
        """mdd_size_multiplier=0.5 → 사이즈 50% 축소."""
        sizer = self._make_sizer()
        qty_full = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
            mdd_size_multiplier=1.0,
        )
        qty_half = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
            mdd_size_multiplier=0.5,
        )
        assert abs(qty_half / qty_full - 0.5) < 1e-9

    def test_mdd_multiplier_0_blocks_entry(self):
        """mdd_size_multiplier=0.0 → 진입 차단 (0 반환)."""
        sizer = self._make_sizer()
        qty = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
            mdd_size_multiplier=0.0,
        )
        assert qty == 0.0

    def test_mdd_multiplier_negative_blocks_entry(self):
        """mdd_size_multiplier < 0 → 0으로 클리핑, 진입 차단."""
        sizer = self._make_sizer()
        qty = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
            mdd_size_multiplier=-0.5,
        )
        assert qty == 0.0

    def test_mdd_multiplier_above_1_clamped(self):
        """mdd_size_multiplier > 1.0 → 1.0으로 클리핑 (확대 방지)."""
        sizer = self._make_sizer()
        qty_normal = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
            mdd_size_multiplier=1.0,
        )
        qty_over = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
            mdd_size_multiplier=2.0,
        )
        assert abs(qty_normal - qty_over) < 1e-9


# ── DrawdownMonitor 실제 연동 시나리오 ───────────────────────────────────────


class TestDrawdownMonitorKellyIntegration:
    """DrawdownMonitor에서 get_mdd_size_multiplier()를 받아 Kelly에 전달하는 E2E 시나리오."""

    def test_normal_mdd_full_kelly(self):
        """MDD NORMAL → multiplier=1.0 → 정상 사이즈."""
        monitor = DrawdownMonitor()
        monitor.update(10_000)  # peak = 10_000
        monitor.update(9_800)   # DD = 2% < 5%(warn)

        mult = monitor.get_mdd_size_multiplier()
        assert mult == 1.0
        assert monitor.get_mdd_level() == MddLevel.NORMAL

        sizer = KellySizer(fraction=0.5, max_fraction=0.10, kelly_cap=0.25)
        qty = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=9_800, price=100.0,
            mdd_size_multiplier=mult,
        )
        assert qty > 0

    def test_warn_mdd_halves_kelly(self):
        """MDD WARN (5~10%) → multiplier=0.5 → 사이즈 절반."""
        monitor = DrawdownMonitor()
        monitor.update(10_000)
        monitor.update(9_300)   # DD = 7% → WARN

        mult = monitor.get_mdd_size_multiplier()
        assert mult == 0.5
        assert monitor.get_mdd_level() == MddLevel.WARN

        sizer = KellySizer(fraction=0.5, max_fraction=0.10, kelly_cap=0.25)
        qty_full = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=9_300, price=100.0,
            mdd_size_multiplier=1.0,
        )
        qty_warn = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=9_300, price=100.0,
            mdd_size_multiplier=mult,
        )
        assert abs(qty_warn / qty_full - 0.5) < 1e-9

    def test_block_entry_mdd_zero_kelly(self):
        """MDD BLOCK_ENTRY (10~15%) → multiplier=0.0 → 진입 차단."""
        monitor = DrawdownMonitor()
        monitor.update(10_000)
        monitor.update(8_800)   # DD = 12% → BLOCK_ENTRY

        mult = monitor.get_mdd_size_multiplier()
        assert mult == 0.0
        assert monitor.get_mdd_level() == MddLevel.BLOCK_ENTRY

        sizer = KellySizer(fraction=0.5, max_fraction=0.10, kelly_cap=0.25)
        qty = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=8_800, price=100.0,
            mdd_size_multiplier=mult,
        )
        assert qty == 0.0

    def test_full_halt_mdd_zero_kelly(self):
        """MDD FULL_HALT (>=20%) → multiplier=0.0 → 완전 차단."""
        monitor = DrawdownMonitor()
        monitor.update(10_000)
        monitor.update(7_800)   # DD = 22% → FULL_HALT

        mult = monitor.get_mdd_size_multiplier()
        assert mult == 0.0
        assert monitor.get_mdd_level() == MddLevel.FULL_HALT

        sizer = KellySizer(fraction=0.5, max_fraction=0.10, kelly_cap=0.25)
        qty = sizer.compute(
            win_rate=0.9, avg_win=0.10, avg_loss=0.01,
            capital=7_800, price=100.0,
            mdd_size_multiplier=mult,
        )
        assert qty == 0.0

    def test_from_trade_history_with_mdd_multiplier(self):
        """from_trade_history에서 mdd_size_multiplier 전달 동작."""
        trades = [{"pnl": 100}, {"pnl": 150}, {"pnl": -50}] * 5

        qty_full = KellySizer.from_trade_history(
            trades, capital=10_000, price=1000.0,
            mdd_size_multiplier=1.0,
        )
        qty_warn = KellySizer.from_trade_history(
            trades, capital=10_000, price=1000.0,
            mdd_size_multiplier=0.5,
        )
        qty_block = KellySizer.from_trade_history(
            trades, capital=10_000, price=1000.0,
            mdd_size_multiplier=0.0,
        )

        assert qty_full > 0
        assert abs(qty_warn / qty_full - 0.5) < 1e-9
        assert qty_block == 0.0

    def test_mdd_recovery_restores_full_size(self):
        """MDD WARN → NORMAL 복귀 시 사이즈 복원."""
        monitor = DrawdownMonitor()
        monitor.update(10_000)
        monitor.update(9_300)   # WARN (7%)
        assert monitor.get_mdd_level() == MddLevel.WARN

        # 회복
        monitor.update(9_700)   # DD = 3% → NORMAL
        assert monitor.get_mdd_level() == MddLevel.NORMAL
        assert monitor.get_mdd_size_multiplier() == 1.0


# ── Quarter-Cap + Step-Down 복합 시나리오 ────────────────────────────────────


class TestQuarterCapAndStepDown:
    """kelly_cap과 mdd_size_multiplier가 동시에 적용되는 시나리오."""

    def test_cap_then_stepdown(self):
        """kelly_cap → mdd_multiplier 순서로 모두 적용됨."""
        # fraction=1.0, kelly_f≈0.98 → cap at 0.25
        # mdd_multiplier=0.5 → final = 0.25 * 0.5 = 0.125
        sizer = KellySizer(fraction=1.0, max_fraction=1.0, kelly_cap=0.25)
        qty = sizer.compute(
            win_rate=0.99, avg_win=0.50, avg_loss=0.01,
            capital=100_000, price=1.0,
            mdd_size_multiplier=0.5,
        )
        # position_capital = 100_000 * 0.25 * 0.5 = 12_500
        assert abs(qty - 12_500.0) < 1e-6

    def test_cap_regime_and_stepdown_combined(self):
        """kelly_cap + regime(HIGH_VOL) + mdd_multiplier 복합 시나리오."""
        sizer = KellySizer(fraction=1.0, max_fraction=1.0, kelly_cap=0.20)
        qty = sizer.compute(
            win_rate=0.99, avg_win=0.50, avg_loss=0.01,
            capital=100_000, price=1.0,
            regime="HIGH_VOL",       # 0.3x
            mdd_size_multiplier=0.5, # 0.5x
        )
        # cap: min(0.98, 0.20) = 0.20
        # regime: 0.20 * 0.3 = 0.06
        # clip: 0.06
        # mdd: 0.06 * 0.5 = 0.03
        # qty = 100_000 * 0.03 = 3_000
        assert abs(qty - 3_000.0) < 1e-6

    def test_all_protections_stack(self):
        """cap + DD 제약 + regime + mdd_multiplier 모두 적층 시 최소값 연쇄 적용."""
        sizer = KellySizer(
            fraction=1.0, max_fraction=1.0, kelly_cap=0.25,
            max_drawdown=0.05, leverage=2.0,
        )
        # kelly_f ≈ 0.98
        # cap: min(0.98, 0.25) = 0.25
        # DD: max_dd_constrained = 0.05 / (0.01 * 2) = 2.5 → 0.25 < 2.5 → no effect
        # regime RANGING: 0.25 * 0.5 = 0.125
        # clip: 0.125
        # mdd_mult: 0.125 * 0.5 = 0.0625
        qty = sizer.compute(
            win_rate=0.99, avg_win=0.50, avg_loss=0.01,
            capital=100_000, price=1.0,
            regime="RANGING",
            mdd_size_multiplier=0.5,
        )
        assert abs(qty - 6_250.0) < 1e-6


# ── Stress Test: 극단 시나리오 ───────────────────────────────────────────────


class TestKellyStressExtreme:
    """극단 입력값에서 KellySizer 안전성 및 MDD step-down 정확성 검증."""

    # ── win_rate 경계값 ─────────────────────────────────────────────────────

    def test_win_rate_zero_returns_zero(self):
        """win_rate=0.0: kelly_f = (0*avg_win - 1*avg_loss)/avg_win < 0 → 0 반환."""
        sizer = KellySizer(fraction=0.5, max_fraction=0.10, kelly_cap=0.25)
        qty = sizer.compute(
            win_rate=0.0, avg_win=0.05, avg_loss=0.02,
            capital=100_000, price=1.0,
        )
        assert qty == 0.0

    def test_win_rate_one_uses_cap(self):
        """win_rate=1.0: kelly_f = 1.0 (avg_win - 0)/avg_win = 1.0 → cap at kelly_cap=0.25."""
        sizer = KellySizer(fraction=1.0, max_fraction=1.0, kelly_cap=0.25)
        qty = sizer.compute(
            win_rate=1.0, avg_win=0.05, avg_loss=0.02,
            capital=100_000, price=1.0,
        )
        # kelly_f = 1.0, fractional_f = min(1.0, 0.25) = 0.25
        # position_capital = 100_000 * 0.25 = 25_000
        assert abs(qty - 25_000.0) < 1e-6

    def test_win_rate_slightly_above_breakeven(self):
        """win_rate가 손익분기 바로 위: 소규모지만 양수 포지션 반환."""
        # avg_win=0.01, avg_loss=0.01 → breakeven at win_rate=0.5
        # win_rate=0.51 → kelly_f = (0.51*0.01 - 0.49*0.01)/0.01 = 0.02 > 0
        sizer = KellySizer(fraction=0.5, max_fraction=0.10, kelly_cap=0.25)
        qty = sizer.compute(
            win_rate=0.51, avg_win=0.01, avg_loss=0.01,
            capital=100_000, price=1.0,
        )
        assert qty > 0.0

    # ── 극단 변동성 ─────────────────────────────────────────────────────────

    def test_extreme_volatility_high_atr_shrinks_size(self):
        """변동성 100%+: ATR이 target_atr의 10배이면 포지션 1/10으로 축소."""
        sizer = KellySizer(fraction=0.5, max_fraction=0.10, kelly_cap=0.25)
        qty_normal = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
            atr=0.01, target_atr=0.01,  # ATR == target → factor=1.0
        )
        qty_extreme = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
            atr=0.10, target_atr=0.01,  # ATR 10배 → factor=0.1
        )
        # atr_factor = min(0.01/0.10, 1.0) = 0.1 → qty_extreme = qty_normal * 0.1
        assert abs(qty_extreme / qty_normal - 0.1) < 1e-9

    def test_extreme_volatility_atr_gt_target_capped_at_one(self):
        """target_atr > current_atr: atr_factor는 1.0으로 상한 (포지션 확대 방지)."""
        sizer = KellySizer(fraction=0.5, max_fraction=0.10, kelly_cap=0.25)
        qty_no_atr = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
        )
        qty_low_atr = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=100_000, price=1.0,
            atr=0.005, target_atr=0.01,  # atr < target → factor = min(2.0, 1.0) = 1.0
        )
        # atr_factor 상한=1.0 → qty 동일
        assert abs(qty_low_atr - qty_no_atr) < 1e-9

    def test_high_vol_regime_extreme_shrink(self):
        """HIGH_VOL 레짐 + 극단 ATR 조합: 포지션이 min_fraction까지 내려갈 수 있음."""
        sizer = KellySizer(
            fraction=0.5, max_fraction=0.10, min_fraction=0.001, kelly_cap=0.25
        )
        qty = sizer.compute(
            win_rate=0.51, avg_win=0.01, avg_loss=0.01,
            capital=100_000, price=1.0,
            atr=1.0, target_atr=0.01,   # atr_factor=0.01
            regime="HIGH_VOL",           # regime_scale=0.3
        )
        # kelly_f=0.02, fractional_f=0.02*0.5=0.01, cap=0.01 (< 0.25)
        # regime: 0.01 * 0.3 = 0.003, clip: max(0.001, min(0.003, 0.10)) = 0.003
        # atr_factor=0.01 → position_capital = 100_000 * 0.003 * 0.01 = 3.0
        # qty=3.0 (after atr shrink; min_fraction only limits fractional_f, not final qty)
        assert qty >= 0.0
        assert qty <= 100_000 * 0.10  # 절대 max_fraction 초과 불가

    # ── 연속 손실 10회 후 MDD step-down ────────────────────────────────────

    def test_consecutive_losses_10_triggers_mdd_stepdown(self):
        """연속 손실 10회 → peak 대비 낙폭이 WARN/BLOCK_ENTRY 수준에 도달 시 step-down 작동."""
        monitor = DrawdownMonitor()
        equity = 10_000.0
        monitor.update(equity)  # peak = 10_000

        # 연속 손실 10회: 각 회 1% 손실
        for _ in range(10):
            equity *= 0.99
            monitor.update(equity)

        # ~9.56% 낙폭 → WARN 수준 (5~10%)
        mdd_level = monitor.get_mdd_level()
        mult = monitor.get_mdd_size_multiplier()

        assert mdd_level in (MddLevel.WARN, MddLevel.BLOCK_ENTRY, MddLevel.FULL_HALT)
        assert mult < 1.0  # 정상보다 반드시 축소

        sizer = KellySizer(fraction=0.5, max_fraction=0.10, kelly_cap=0.25)
        qty_with_mdd = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=equity, price=1.0,
            mdd_size_multiplier=mult,
        )
        qty_without_mdd = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=equity, price=1.0,
            mdd_size_multiplier=1.0,
        )
        assert qty_with_mdd < qty_without_mdd

    def test_severe_consecutive_losses_blocks_entry(self):
        """연속 손실로 낙폭 15%+ → BLOCK_ENTRY or FULL_HALT → mdd_multiplier=0 → qty=0."""
        monitor = DrawdownMonitor()
        equity = 10_000.0
        monitor.update(equity)

        # 연속 손실 20회: 각 1% → 약 18% 낙폭 → BLOCK_ENTRY 또는 FULL_HALT
        for _ in range(20):
            equity *= 0.99
            monitor.update(equity)

        mult = monitor.get_mdd_size_multiplier()
        level = monitor.get_mdd_level()

        # 18%+ 낙폭은 BLOCK_ENTRY(10~15%) 또는 LIQUIDATE(15~20%) 또는 FULL_HALT(>=20%)
        assert level in (MddLevel.BLOCK_ENTRY, MddLevel.LIQUIDATE, MddLevel.FULL_HALT)

        sizer = KellySizer(fraction=0.5, max_fraction=0.10, kelly_cap=0.25)
        qty = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=equity, price=1.0,
            mdd_size_multiplier=mult,
        )
        # BLOCK_ENTRY 이상이면 mult=0.0 → qty=0
        if mult == 0.0:
            assert qty == 0.0
        else:
            assert qty < 100_000 * 0.10

    # ── 레짐 전환 직후 포지션 급변 방지 (EMA 스무딩) ─────────────────────

    def test_bull_to_crash_regime_smoothing_prevents_sharp_drop(self):
        """BULL → CRASH 레짐 전환 시 EMA 스무딩(alpha=0.3)이 급격한 포지션 축소 완화."""
        # alpha=0.3: 새 레짐 70% + 이전 30%
        sizer_smooth = KellySizer(
            fraction=0.5, max_fraction=1.0, kelly_cap=0.25,
            regime_smooth_alpha=0.3
        )
        sizer_instant = KellySizer(
            fraction=0.5, max_fraction=1.0, kelly_cap=0.25,
            regime_smooth_alpha=0.0  # 즉시 전환
        )

        params = dict(win_rate=0.6, avg_win=0.02, avg_loss=0.01,
                      capital=100_000, price=1.0)

        # Step 1: 두 sizer 모두 TREND_UP(scale=1.0)으로 초기화
        sizer_smooth.compute(**params, regime="TREND_UP")
        sizer_instant.compute(**params, regime="TREND_UP")

        # Step 2: 레짐 전환 TREND_UP → HIGH_VOL (scale=0.3)
        qty_smooth = sizer_smooth.compute(**params, regime="HIGH_VOL")
        qty_instant = sizer_instant.compute(**params, regime="HIGH_VOL")

        # 스무딩 있으면 즉시전환보다 포지션이 커야 함 (급변 완화)
        assert qty_smooth > qty_instant, (
            f"Smoothed {qty_smooth:.2f} should be > instant {qty_instant:.2f}"
        )

    def test_same_regime_no_smoothing_effect(self):
        """동일 레짐 연속 호출: 스무딩과 무관하게 동일한 포지션 사이즈."""
        sizer = KellySizer(
            fraction=0.5, max_fraction=1.0, kelly_cap=0.25,
            regime_smooth_alpha=0.5
        )
        params = dict(win_rate=0.6, avg_win=0.02, avg_loss=0.01,
                      capital=100_000, price=1.0)

        qty_first = sizer.compute(**params, regime="RANGING")
        qty_second = sizer.compute(**params, regime="RANGING")  # 동일 레짐
        # 동일 레짐 유지 → 스무딩 미적용 → 완전히 동일한 포지션
        assert abs(qty_first - qty_second) < 1e-9

    def test_regime_transition_blending_formula(self):
        """레짐 전환 시 EMA 블렌딩 수식 검증: effective = (1-alpha)*target + alpha*prev."""
        alpha = 0.3
        sizer = KellySizer(
            fraction=0.5, max_fraction=1.0, kelly_cap=0.25,
            regime_smooth_alpha=alpha,
        )
        params = dict(win_rate=0.6, avg_win=0.02, avg_loss=0.01,
                      capital=100_000, price=1.0)

        # TREND_UP (scale=1.0) 초기화
        sizer.compute(**params, regime="TREND_UP")
        prev_scale = 1.0  # TREND_UP scale after first call

        # RANGING (scale=0.5) 전환
        qty_blended = sizer.compute(**params, regime="RANGING")

        # 기대 effective_scale = (1-0.3)*0.5 + 0.3*1.0 = 0.35 + 0.30 = 0.65
        target_scale = 0.5
        expected_scale = (1.0 - alpha) * target_scale + alpha * prev_scale  # 0.65

        # kelly_f = (0.6*0.02 - 0.4*0.01)/0.02 = (0.012-0.004)/0.02 = 0.4
        # fractional_f = 0.4 * 0.5 = 0.2 < 0.25 (cap 미적용)
        # after regime scale: 0.2 * 0.65 = 0.13
        # clip: max(0.001, min(0.13, 1.0)) = 0.13
        # qty = 100_000 * 0.13 = 13_000
        expected_qty = 100_000 * 0.2 * expected_scale
        assert abs(qty_blended - expected_qty) < 1e-6
