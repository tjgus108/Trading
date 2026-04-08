"""
KellySizer + TWAPExecutor 테스트 (최소 10개).
"""

import pytest
import numpy as np
from dataclasses import fields

from src.risk.kelly_sizer import KellySizer
from src.exchange.twap import TWAPExecutor, TWAPResult


# ---------------------------------------------------------------------------
# KellySizer 테스트
# ---------------------------------------------------------------------------

class TestKellySizer:

    def test_kelly_positive_edge(self):
        """win_rate=0.6, avg_win=2%, avg_loss=1% → kelly > 0."""
        sizer = KellySizer()
        qty = sizer.compute(
            win_rate=0.6,
            avg_win=0.02,
            avg_loss=0.01,
            capital=100_000,
            price=50_000,
        )
        assert qty > 0, "Positive edge should yield positive position size"

    def test_kelly_zero_edge(self):
        """win_rate=0.5, avg_win == avg_loss → kelly ≈ 0 (returns 0)."""
        sizer = KellySizer()
        qty = sizer.compute(
            win_rate=0.5,
            avg_win=0.02,
            avg_loss=0.02,
            capital=100_000,
            price=50_000,
        )
        # Kelly = (0.5*0.02 - 0.5*0.02) / 0.02 = 0
        assert qty == 0.0

    def test_kelly_max_cap(self):
        """극단적 edge라도 max_fraction(10%) 초과 안 함."""
        sizer = KellySizer(fraction=1.0, max_fraction=0.10)
        qty = sizer.compute(
            win_rate=0.99,
            avg_win=0.50,
            avg_loss=0.01,
            capital=100_000,
            price=1.0,  # price=1로 수량=금액
        )
        max_qty = 100_000 * 0.10 / 1.0
        assert qty <= max_qty + 1e-9, f"qty {qty} exceeds max_fraction cap {max_qty}"

    def test_kelly_min_floor(self):
        """매우 작은 positive edge라도 min_fraction 이상 반환."""
        sizer = KellySizer(fraction=0.5, min_fraction=0.001)
        # tiny edge: win=0.001, loss=0.0009
        qty = sizer.compute(
            win_rate=0.51,
            avg_win=0.001,
            avg_loss=0.0009,
            capital=100_000,
            price=1.0,
        )
        min_qty = 100_000 * 0.001 / 1.0
        assert qty >= min_qty - 1e-9, f"qty {qty} below min_fraction floor {min_qty}"

    def test_kelly_atr_adjustment(self):
        """high ATR → 사이즈 축소."""
        sizer = KellySizer()
        base_qty = sizer.compute(
            win_rate=0.6,
            avg_win=0.02,
            avg_loss=0.01,
            capital=100_000,
            price=50_000,
            atr=100,
            target_atr=100,  # atr_factor=1.0
        )
        high_atr_qty = sizer.compute(
            win_rate=0.6,
            avg_win=0.02,
            avg_loss=0.01,
            capital=100_000,
            price=50_000,
            atr=300,         # 3x ATR → atr_factor = 100/300 ≈ 0.33
            target_atr=100,
        )
        assert high_atr_qty < base_qty, "High ATR should reduce position size"

    def test_kelly_from_history(self):
        """trade history 리스트로 계산."""
        trades = [
            {"pnl": 200},
            {"pnl": -100},
            {"pnl": 150},
            {"pnl": -80},
            {"pnl": 300},
        ]
        qty = KellySizer.from_trade_history(
            trades=trades,
            capital=50_000,
            price=10_000,
        )
        assert qty > 0, "Positive-expectancy trade history should yield positive size"

    def test_kelly_negative_edge_returns_zero(self):
        """음수 edge는 0 반환."""
        sizer = KellySizer()
        qty = sizer.compute(
            win_rate=0.3,
            avg_win=0.01,
            avg_loss=0.05,
            capital=100_000,
            price=50_000,
        )
        assert qty == 0.0

    def test_kelly_from_history_empty(self):
        """빈 trade history → 0 반환."""
        qty = KellySizer.from_trade_history([], capital=100_000, price=50_000)
        assert qty == 0.0


# ---------------------------------------------------------------------------
# TWAPExecutor 테스트
# ---------------------------------------------------------------------------

class TestTWAPExecutor:

    def _make_executor(self, n_slices=5, dry_run=True):
        return TWAPExecutor(n_slices=n_slices, interval_seconds=0, dry_run=dry_run)

    def test_twap_dry_run(self):
        """dry_run=True → TWAPResult 반환, slices_executed == n_slices."""
        executor = self._make_executor(n_slices=5)
        result = executor.execute(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
        )
        assert isinstance(result, TWAPResult)
        assert result.slices_executed == 5
        assert result.dry_run is True

    def test_twap_avg_price_range(self):
        """avg_price가 입력 price ± 1% 범위 내."""
        price = 50_000.0
        executor = self._make_executor(n_slices=10)
        result = executor.execute(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=2.0,
            price_limit=price,
        )
        assert abs(result.avg_price - price) / price < 0.01, (
            f"avg_price {result.avg_price} is outside ±1% of {price}"
        )

    def test_twap_slippage_estimate(self):
        """qty가 클수록 slippage 증가."""
        executor = TWAPExecutor()
        small_slip = executor.estimate_slippage(qty=10, price=50_000, daily_volume=1_000_000)
        large_slip = executor.estimate_slippage(qty=100_000, price=50_000, daily_volume=1_000_000)
        assert large_slip > small_slip, "Larger qty should produce higher slippage"

    def test_twap_result_fields(self):
        """TWAPResult 필드 모두 존재."""
        required = {"slices_executed", "avg_price", "total_qty", "estimated_slippage_pct", "dry_run"}
        actual = {f.name for f in fields(TWAPResult)}
        assert required == actual, f"Missing fields: {required - actual}"

    def test_twap_slippage_default(self):
        """daily_volume 없으면 기본값 0.0005 반환."""
        executor = TWAPExecutor()
        slip = executor.estimate_slippage(qty=1.0, price=50_000.0)
        assert slip == 0.0005

    def test_twap_total_qty_preserved(self):
        """TWAPResult.total_qty가 입력 total_qty와 일치."""
        executor = self._make_executor(n_slices=4)
        result = executor.execute(
            connector=None,
            symbol="ETH/USDT",
            side="sell",
            total_qty=3.5,
            price_limit=2000.0,
        )
        assert result.total_qty == 3.5
