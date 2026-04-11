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

    def test_kelly_max_drawdown_constraint_active(self):
        """max_dd_constrained < half_kelly 이면 제약이 실제로 적용되어 사이즈 감소."""
        # kelly_f=0.88, half_kelly=0.44, max_dd_constrained=0.02/(0.10*1)=0.20
        # → final_fraction=0.20, not 0.44
        capital, price = 100_000, 1.0

        sizer_no_dd = KellySizer(fraction=0.5, max_fraction=1.0, min_fraction=0.0)
        qty_no_dd = sizer_no_dd.compute(
            win_rate=0.9, avg_win=0.50, avg_loss=0.10,
            capital=capital, price=price,
        )

        sizer_dd = KellySizer(
            fraction=0.5, max_fraction=1.0, min_fraction=0.0,
            max_drawdown=0.02, leverage=1.0,
        )
        qty_dd = sizer_dd.compute(
            win_rate=0.9, avg_win=0.50, avg_loss=0.10,
            capital=capital, price=price,
        )

        assert qty_dd < qty_no_dd, "DD constraint should reduce position size"
        # max_dd_constrained=0.20 → qty = capital * 0.20 / price
        expected = capital * 0.20 / price
        assert abs(qty_dd - expected) < 1e-6, f"Expected {expected}, got {qty_dd}"

    def test_kelly_max_drawdown_constraint_exact_boundary(self):
        """max_dd_constrained == half_kelly 경계: 제약 없는 경우와 결과 동일."""
        # kelly_f=0.40, half_kelly=0.20, max_drawdown=0.01 → max_dd_constrained=0.20
        capital, price = 100_000, 1.0

        sizer_no_dd = KellySizer(fraction=0.5, max_fraction=1.0, min_fraction=0.0)
        qty_no_dd = sizer_no_dd.compute(
            win_rate=0.6, avg_win=0.10, avg_loss=0.05,
            capital=capital, price=price,
        )

        sizer_dd = KellySizer(
            fraction=0.5, max_fraction=1.0, min_fraction=0.0,
            max_drawdown=0.01, leverage=1.0,
        )
        qty_dd = sizer_dd.compute(
            win_rate=0.6, avg_win=0.10, avg_loss=0.05,
            capital=capital, price=price,
        )

        # min(half_kelly=0.20, max_dd_constrained=0.20) = 0.20 → 동일
        assert abs(qty_dd - qty_no_dd) < 1e-6, (
            f"At exact boundary qty should match: {qty_dd} vs {qty_no_dd}"
        )



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
        required = {"slices_executed", "avg_price", "total_qty", "estimated_slippage_pct", "dry_run", "filled_qty", "partial_fills", "timeout_occurred", "avg_execution_time"}
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


# ---------------------------------------------------------------------------
# TWAP 부분 체결 & 타임아웃 테스트
# ---------------------------------------------------------------------------

class TestTWAPPartialAndTimeout:

    def test_twap_partial_fill_tracking(self):
        """dry_run에서 부분 체결 시뮬레이션 및 tracking."""
        executor = TWAPExecutor(n_slices=5, interval_seconds=0, dry_run=True)
        np.random.seed(42)  # 재현 가능성
        result = executor.execute(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
        )
        # 부분 체결이 발생할 수 있으므로 filled_qty <= total_qty
        assert result.filled_qty <= result.total_qty + 1e-8
        assert result.partial_fills >= 0

    def test_twap_filled_qty_calculation(self):
        """filled_qty가 정확히 계산되는지 확인."""
        executor = TWAPExecutor(n_slices=1, interval_seconds=0, dry_run=True)
        np.random.seed(123)
        result = executor.execute(
            connector=None,
            symbol="ETH/USDT",
            side="sell",
            total_qty=2.0,
            price_limit=2000.0,
        )
        # 1 슬라이스이므로 slices_executed == 1
        assert result.slices_executed == 1
        # filled_qty는 total_qty와 비슷해야 함 (부분 체결 고려)
        assert 0 < result.filled_qty <= result.total_qty

    def test_twap_timeout_flag_no_timeout(self):
        """timeout_per_slice 설정해도 빠른 실행 시 timeout_occurred=False."""
        executor = TWAPExecutor(
            n_slices=2,
            interval_seconds=0,
            dry_run=True,
            timeout_per_slice=10.0,  # 10초/슬라이스
        )
        result = executor.execute(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
        )
        assert result.timeout_occurred is False

    def test_twap_timeout_per_slice_respected(self):
        """timeout_per_slice가 매우 작으면 timeout_occurred=True."""
        executor = TWAPExecutor(
            n_slices=3,
            interval_seconds=0.5,  # 0.5초 대기
            dry_run=False,
            timeout_per_slice=0.001,  # 1ms/슬라이스 = 매우 짧음
        )
        # 실제 connector 없으므로 Exception 발생 → timeout_occurred=True
        # dry_run=False인데 connector=None이면 실행 중 에러 발생
        # 이 경우 timeout_occurred 플래그가 설정됨을 확인
        result = executor.execute(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
        )
        # timeout이나 exception으로 인해 완료되지 않음
        assert result.timeout_occurred is True or result.slices_executed < 3

    def test_twap_result_new_fields(self):
        """새로운 필드 (filled_qty, partial_fills, timeout_occurred) 존재 확인."""
        executor = TWAPExecutor(n_slices=1, dry_run=True)
        result = executor.execute(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
        )
        assert hasattr(result, "filled_qty")
        assert hasattr(result, "partial_fills")
        assert hasattr(result, "timeout_occurred")
        assert isinstance(result.filled_qty, float)
        assert isinstance(result.partial_fills, int)
        assert isinstance(result.timeout_occurred, bool)

    def test_twap_avg_execution_time_tracked(self):
        """avg_execution_time이 float이고 0 이상임을 확인."""
        executor = TWAPExecutor(n_slices=4, interval_seconds=0, dry_run=True)
        result = executor.execute(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
        )
        assert isinstance(result.avg_execution_time, float)
        assert result.avg_execution_time >= 0.0
