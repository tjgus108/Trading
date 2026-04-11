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

    def test_twap_global_timeout_triggers_on_second_slice(self):
        """전체 타임아웃(timeout_per_slice * n_slices) 초과 시 두 번째 슬라이스에서 조기 종료."""
        from unittest.mock import patch

        # start_time=0, 첫 슬라이스 진입 시 elapsed=0 → 통과
        # 두 번째 슬라이스 진입 시 elapsed=999 → 초과 → break
        call_count = 0
        base_times = [0, 0, 0, 999, 999]  # time.time() 호출 순서별 반환값

        def fake_time():
            nonlocal call_count
            val = base_times[min(call_count, len(base_times) - 1)]
            call_count += 1
            return val

        executor = TWAPExecutor(
            n_slices=3,
            interval_seconds=0,
            dry_run=True,
            timeout_per_slice=100.0,  # total budget = 300s, elapsed=999 → 초과
        )
        with patch("src.exchange.twap.time.time", side_effect=fake_time):
            result = executor.execute(
                connector=None,
                symbol="BTC/USDT",
                side="buy",
                total_qty=1.0,
                price_limit=50_000.0,
            )

        assert result.timeout_occurred is True
        assert result.slices_executed < 3, (
            f"Expected early exit, but got slices_executed={result.slices_executed}"
        )

    def test_twap_global_timeout_not_triggered_within_budget(self):
        """elapsed가 budget 이하이면 timeout_occurred=False, 모든 슬라이스 실행."""
        from unittest.mock import patch

        # 3 슬라이스: 각 슬라이스마다 time.time() 2회 호출 (루프 시작 + _slice_t0)
        # elapsed는 항상 budget(300s) 이하
        times = [0, 0, 50, 50, 100, 100, 150, 150]
        call_count = 0

        def fake_time():
            nonlocal call_count
            val = times[min(call_count, len(times) - 1)]
            call_count += 1
            return val

        executor = TWAPExecutor(
            n_slices=3,
            interval_seconds=0,
            dry_run=True,
            timeout_per_slice=200.0,  # total budget = 600s > 100s elapsed
        )
        with patch("src.exchange.twap.time.time", side_effect=fake_time):
            result = executor.execute(
                connector=None,
                symbol="BTC/USDT",
                side="buy",
                total_qty=1.0,
                price_limit=50_000.0,
            )

        assert result.timeout_occurred is False
        assert result.slices_executed == 3


# ---------------------------------------------------------------------------
# TWAP 슬라이스 합계 검증 테스트
# ---------------------------------------------------------------------------

class TestTWAPSliceSum:

    def test_slice_sum_equals_total_qty_no_partial(self):
        """부분 체결 없을 때 슬라이스 합계 == total_qty."""
        import unittest.mock as mock

        executor = TWAPExecutor(n_slices=5, interval_seconds=0, dry_run=True)
        total_qty = 10.0
        slice_qty = total_qty / executor.n_slices  # 2.0

        # fill_ratio를 항상 1.0으로 고정 (부분 체결 없음)
        with mock.patch("numpy.random.random", return_value=1.0), \
             mock.patch("numpy.random.uniform", return_value=0.0):
            result = executor.execute(
                connector=None,
                symbol="BTC/USDT",
                side="buy",
                total_qty=total_qty,
                price_limit=50_000.0,
            )

        assert result.slices_executed == 5
        assert abs(result.filled_qty - total_qty) < 1e-9, (
            f"filled_qty {result.filled_qty} != total_qty {total_qty}"
        )

    def test_slice_sum_equals_total_qty_various_sizes(self):
        """다양한 total_qty와 n_slices 조합에서 슬라이스 합계 == total_qty."""
        import unittest.mock as mock

        cases = [
            (3, 9.0),
            (7, 1.0),
            (4, 0.123456),
        ]
        for n_slices, total_qty in cases:
            executor = TWAPExecutor(n_slices=n_slices, interval_seconds=0, dry_run=True)

            with mock.patch("numpy.random.random", return_value=1.0), \
                 mock.patch("numpy.random.uniform", return_value=0.0):
                result = executor.execute(
                    connector=None,
                    symbol="ETH/USDT",
                    side="sell",
                    total_qty=total_qty,
                    price_limit=2000.0,
                )

            assert result.slices_executed == n_slices
            assert abs(result.filled_qty - total_qty) < 1e-9, (
                f"n_slices={n_slices}, total_qty={total_qty}: "
                f"filled_qty={result.filled_qty}"
            )


# ---------------------------------------------------------------------------
# Kelly + TWAP 파이프라인 통합 시나리오
# ---------------------------------------------------------------------------

class TestKellyTWAPPipelineIntegration:
    """KellySizer가 산출한 position_size를 TWAPExecutor가 실행하는 통합 경로 검증."""

    def _build_trades(self, n: int = 12, win_rate: float = 0.6) -> list[dict]:
        """재현 가능한 거래 이력 생성."""
        trades = []
        for i in range(n):
            if i % 10 < int(win_rate * 10):
                trades.append({"pnl": 200.0})
            else:
                trades.append({"pnl": -100.0})
        return trades

    def test_kelly_size_fed_into_twap_buy(self):
        """시나리오 1: Kelly size → TWAP buy 실행 → filled_qty <= kelly_size."""
        capital = 50_000.0
        price = 50_000.0
        trades = self._build_trades(n=12, win_rate=0.6)

        kelly_size = KellySizer.from_trade_history(
            trades=trades,
            capital=capital,
            price=price,
        )
        assert kelly_size > 0, "Kelly should yield positive size for profitable history"

        executor = TWAPExecutor(n_slices=5, interval_seconds=0, dry_run=True)
        np.random.seed(0)
        result = executor.execute(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=kelly_size,
            price_limit=price,
        )

        assert result.slices_executed == 5
        assert result.total_qty == kelly_size
        assert result.filled_qty <= kelly_size + 1e-8
        assert result.dry_run is True
        # avg_price는 price ±1% 이내
        assert abs(result.avg_price - price) / price < 0.01

    def test_kelly_atr_reduced_size_fed_into_twap_sell(self):
        """시나리오 2: 고변동성(ATR 3x) → Kelly 축소 → TWAP sell 슬라이스 합계 검증."""
        capital = 100_000.0
        price = 2_000.0
        target_atr = 50.0
        high_atr = 150.0  # 3x → atr_factor ≈ 0.333

        sizer = KellySizer(fraction=0.5, max_fraction=0.10, min_fraction=0.001)
        base_size = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=capital, price=price,
            atr=target_atr, target_atr=target_atr,
        )
        reduced_size = sizer.compute(
            win_rate=0.6, avg_win=0.02, avg_loss=0.01,
            capital=capital, price=price,
            atr=high_atr, target_atr=target_atr,
        )
        assert reduced_size < base_size, "High ATR must reduce Kelly size"

        import unittest.mock as mock
        executor = TWAPExecutor(n_slices=4, interval_seconds=0, dry_run=True)
        # 부분 체결 없이 실행
        with mock.patch("numpy.random.random", return_value=1.0), \
             mock.patch("numpy.random.uniform", return_value=0.0):
            result = executor.execute(
                connector=None,
                symbol="ETH/USDT",
                side="sell",
                total_qty=reduced_size,
                price_limit=price,
            )

        assert result.slices_executed == 4
        assert abs(result.filled_qty - reduced_size) < 1e-9, (
            f"filled_qty {result.filled_qty} != reduced_size {reduced_size}"
        )
        assert result.timeout_occurred is False
