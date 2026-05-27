"""
TWAP 엣지 케이스 테스트.

TWAPExecutor 의 경계 조건 검증.
"""

import pytest
import numpy as np

from src.exchange.twap import TWAPExecutor, TWAPResult


# ── 헬퍼 ──────────────────────────────────────────────────────────────────────

def _executor(n_slices=5, dry_run=True, timeout_per_slice=None):
    return TWAPExecutor(
        n_slices=n_slices,
        interval_seconds=0,
        dry_run=dry_run,
        timeout_per_slice=timeout_per_slice,
    )


def _run(executor, qty=1.0, price=50_000.0, side="buy", symbol="BTC/USDT"):
    return executor.execute(
        connector=None,
        symbol=symbol,
        side=side,
        total_qty=qty,
        price_limit=price,
    )


# ── 1. n_slices=1 단일 슬라이스 ───────────────────────────────────────────────

class TestSingleSlice:
    """n_slices=1 일 때 정상 동작."""

    def test_single_slice_executes_one_slice(self):
        """n_slices=1 → slices_executed == 1."""
        ex = _executor(n_slices=1)
        result = _run(ex)
        assert result.slices_executed == 1

    def test_single_slice_total_qty_preserved(self):
        """n_slices=1 → total_qty는 입력 수량과 동일."""
        ex = _executor(n_slices=1)
        result = _run(ex, qty=3.0)
        assert result.total_qty == 3.0

    def test_single_slice_filled_qty_positive(self):
        """n_slices=1 → filled_qty > 0."""
        np.random.seed(0)
        ex = _executor(n_slices=1)
        result = _run(ex, qty=2.5)
        assert result.filled_qty > 0

    def test_single_slice_avg_price_near_limit(self):
        """n_slices=1, dry_run → avg_price 는 price_limit 의 ±0.1% 이내."""
        np.random.seed(1)
        price = 50_000.0
        ex = _executor(n_slices=1)
        result = _run(ex, qty=1.0, price=price)
        assert abs(result.avg_price - price) / price < 0.001

    def test_single_slice_no_timeout(self):
        """n_slices=1 → timeout_occurred=False."""
        ex = _executor(n_slices=1)
        result = _run(ex)
        assert result.timeout_occurred is False

    def test_single_slice_dry_run_flag(self):
        """결과의 dry_run 플래그가 True."""
        ex = _executor(n_slices=1, dry_run=True)
        result = _run(ex)
        assert result.dry_run is True


# ── 2. 극단적 가격 변동 (50% 하락) ───────────────────────────────────────────

class TestExtremePriceChange:
    """슬라이스 실행 중 가격이 50% 하락해도 에러 없이 완료."""

    def _executor_live_with_dropping_price(self, initial_price, drop_factor):
        """
        live 모드 connector 시뮬레이션:
        각 place_order 호출마다 가격이 drop_factor 씩 감소.
        """

        class DroppingPriceConnector:
            def __init__(self, price, factor):
                self._price = price
                self._factor = factor

            def place_order(self, symbol, side, qty, price):
                current = self._price
                self._price *= self._factor
                return {"price": current, "filled": qty}

        return DroppingPriceConnector(initial_price, drop_factor)

    def test_50pct_drop_completes_without_error(self):
        """live 모드: 가격이 50% 급락해도 TWAPResult 반환 (에러/예외 없음)."""
        connector = self._executor_live_with_dropping_price(
            initial_price=50_000.0,
            drop_factor=0.90,  # 슬라이스마다 10%씩 → 5슬라이스 후 ~29500
        )
        ex = TWAPExecutor(n_slices=5, interval_seconds=0, dry_run=False)
        result = ex.execute(
            connector=connector,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=None,
        )
        assert isinstance(result, TWAPResult)
        assert result.slices_executed == 5
        assert result.errors == 0

    def test_50pct_drop_avg_price_is_vwap_of_filled(self):
        """가격 하락 시 avg_price 는 체결 수량 가중 평균이어야 한다."""

        prices_used = []

        class RecordingConnector:
            def place_order(self, symbol, side, qty, price):
                p = 50_000.0 * (0.5 ** (len(prices_used) / 4))  # 점진적 감소
                prices_used.append(p)
                return {"price": p, "filled": qty}

        ex = TWAPExecutor(n_slices=4, interval_seconds=0, dry_run=False)
        result = ex.execute(
            connector=RecordingConnector(),
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=None,
        )
        slice_qty = 1.0 / 4
        expected_vwap = sum(p * slice_qty for p in prices_used) / (slice_qty * 4)
        assert abs(result.avg_price - expected_vwap) < 1e-6

    def test_dry_run_extreme_low_price_limit_no_error(self):
        """dry_run 모드: price_limit=1.0(극단적 저가)도 에러 없이 완료."""
        np.random.seed(42)
        ex = _executor(n_slices=3)
        result = _run(ex, qty=0.001, price=1.0)
        assert result.slices_executed == 3
        assert result.avg_price > 0

    def test_very_high_price_limit_dry_run(self):
        """price_limit=1e9 (극단적 고가) → dry_run 정상."""
        np.random.seed(7)
        ex = _executor(n_slices=2)
        result = _run(ex, qty=0.01, price=1e9)
        assert result.slices_executed == 2
        assert result.avg_price > 0


# ── 3. timeout_per_slice 초과 ─────────────────────────────────────────────────

class TestTimeoutPerSlice:
    """timeout_per_slice 설정 시 동작 검증."""

    def test_timeout_result_has_flag_true(self):
        """
        총 허용 시간(timeout_per_slice * n_slices)을 0으로 설정하면
        즉시 timeout_occurred=True.
        """
        # timeout_per_slice=0 → total_timeout=0 → 첫 슬라이스 진입 전 타임아웃
        ex = TWAPExecutor(
            n_slices=3,
            interval_seconds=0,
            dry_run=True,
            timeout_per_slice=0.0,  # 즉시 타임아웃
        )
        # dry_run 에서는 타임아웃을 elapsed > timeout_per_slice * n_slices 로 체크
        # elapsed는 항상 양수이므로 0.0 * 3 = 0 → 즉시 break
        result = ex.execute(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
        )
        assert result.timeout_occurred is True

    def test_timeout_slices_executed_less_than_n_slices(self):
        """타임아웃 발생 시 slices_executed < n_slices."""
        ex = TWAPExecutor(
            n_slices=5,
            interval_seconds=0,
            dry_run=True,
            timeout_per_slice=0.0,
        )
        result = ex.execute(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
        )
        assert result.slices_executed < 5

    def test_large_timeout_no_timeout_flag(self):
        """충분히 큰 timeout_per_slice → timeout_occurred=False."""
        ex = TWAPExecutor(
            n_slices=3,
            interval_seconds=0,
            dry_run=True,
            timeout_per_slice=9999.0,
        )
        result = ex.execute(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
        )
        assert result.timeout_occurred is False
        assert result.slices_executed == 3

    def test_timeout_none_no_timeout_flag(self):
        """timeout_per_slice=None → timeout 체크 없음, timeout_occurred=False."""
        ex = TWAPExecutor(
            n_slices=3,
            interval_seconds=0,
            dry_run=True,
            timeout_per_slice=None,
        )
        result = ex.execute(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
        )
        assert result.timeout_occurred is False


# ── 4. 매우 큰 주문 qty=1000000 ───────────────────────────────────────────────

class TestLargeOrder:
    """qty=1000000 과 같이 매우 큰 주문 처리."""

    def test_large_qty_splits_correctly(self):
        """qty=1_000_000, n_slices=10 → 각 슬라이스는 100_000."""
        np.random.seed(42)
        ex = _executor(n_slices=10)
        result = _run(ex, qty=1_000_000.0, price=1.0)
        assert result.slices_executed == 10
        assert result.total_qty == 1_000_000.0

    def test_large_qty_filled_qty_positive(self):
        """큰 주문도 filled_qty > 0 이어야 한다."""
        np.random.seed(0)
        ex = _executor(n_slices=5)
        result = _run(ex, qty=1_000_000.0, price=0.01)
        assert result.filled_qty > 0

    def test_large_qty_avg_price_reasonable(self):
        """avg_price 는 price_limit 근방이어야 한다 (dry_run ±0.1%)."""
        np.random.seed(3)
        price = 100.0
        ex = _executor(n_slices=5)
        result = _run(ex, qty=1_000_000.0, price=price)
        assert abs(result.avg_price - price) / price < 0.001

    def test_large_qty_slippage_is_float(self):
        """슬리피지 추정값은 float 이어야 한다."""
        np.random.seed(5)
        ex = _executor(n_slices=3)
        result = _run(ex, qty=1_000_000.0, price=50_000.0)
        assert isinstance(result.estimated_slippage_pct, float)

    def test_large_qty_with_many_slices(self):
        """qty=1_000_000, n_slices=100 → 100 슬라이스 실행."""
        np.random.seed(99)
        ex = _executor(n_slices=100)
        result = _run(ex, qty=1_000_000.0, price=1.0)
        assert result.slices_executed == 100

    def test_large_qty_n_slices_1_single_execution(self):
        """n_slices=1 일 때 큰 수량도 단일 슬라이스로 처리."""
        np.random.seed(11)
        ex = _executor(n_slices=1)
        result = _run(ex, qty=1_000_000.0, price=0.001)
        assert result.slices_executed == 1
        assert result.total_qty == 1_000_000.0


# ── 5. 입력 검증 (ValueError) ─────────────────────────────────────────────────

class TestInputValidation:
    """잘못된 입력에 대한 ValueError 검증."""

    def test_invalid_total_qty_zero_raises(self):
        ex = _executor()
        with pytest.raises(ValueError, match="total_qty"):
            ex.execute(None, "BTC/USDT", "buy", 0.0, price_limit=50_000.0)

    def test_invalid_total_qty_negative_raises(self):
        ex = _executor()
        with pytest.raises(ValueError, match="total_qty"):
            ex.execute(None, "BTC/USDT", "buy", -1.0, price_limit=50_000.0)

    def test_invalid_side_raises(self):
        ex = _executor()
        with pytest.raises(ValueError, match="side"):
            ex.execute(None, "BTC/USDT", "long", 1.0, price_limit=50_000.0)

    def test_dry_run_no_price_limit_raises(self):
        ex = _executor(dry_run=True)
        with pytest.raises(ValueError, match="price_limit"):
            ex.execute(None, "BTC/USDT", "buy", 1.0, price_limit=None)

    def test_n_slices_zero_raises(self):
        with pytest.raises(ValueError, match="n_slices"):
            TWAPExecutor(n_slices=0)

    def test_n_slices_negative_raises(self):
        with pytest.raises(ValueError, match="n_slices"):
            TWAPExecutor(n_slices=-1)


# ── 6. estimate_slippage 엣지 케이스 ─────────────────────────────────────────

class TestEstimateSlippageEdgeCases:
    """estimate_slippage의 엣지 케이스 검증."""

    def test_zero_qty_returns_zero(self):
        """qty=0 → 슬리피지 0."""
        ex = _executor()
        assert ex.estimate_slippage(qty=0.0, price=50_000.0) == 0.0

    def test_negative_qty_returns_zero(self):
        """qty < 0 → 슬리피지 0 (NaN이 아님)."""
        ex = _executor()
        result = ex.estimate_slippage(qty=-1.0, price=50_000.0, daily_volume=1_000_000)
        assert result == 0.0

    def test_zero_daily_volume_uses_default(self):
        """daily_volume=0 → 기본값 0.00055."""
        ex = _executor()
        slip = ex.estimate_slippage(qty=1.0, price=50_000.0, daily_volume=0)
        # side=None이므로 비대칭 보정 없음
        assert slip == 0.00055

    def test_negative_daily_volume_uses_default(self):
        """daily_volume < 0 → 기본값 사용."""
        ex = _executor()
        slip = ex.estimate_slippage(qty=1.0, price=50_000.0, daily_volume=-100)
        assert slip == 0.00055

    def test_negative_spread_bps_ignored(self):
        """spread_bps < 0 → half_spread = 0 (음수 무시)."""
        ex = _executor()
        slip_neg = ex.estimate_slippage(qty=1.0, price=50_000.0, spread_bps=-10.0)
        slip_zero = ex.estimate_slippage(qty=1.0, price=50_000.0, spread_bps=0.0)
        assert slip_neg == slip_zero

    def test_buy_higher_than_sell(self):
        """동일 조건에서 buy 슬리피지 > sell 슬리피지 (비대칭)."""
        ex = _executor()
        buy_slip = ex.estimate_slippage(qty=100, price=50_000, daily_volume=1_000_000, side="buy")
        sell_slip = ex.estimate_slippage(qty=100, price=50_000, daily_volume=1_000_000, side="sell")
        assert buy_slip > sell_slip

    def test_result_always_non_negative(self):
        """결과가 항상 >= 0."""
        ex = _executor()
        for qty in [0, 0.001, 100, 1_000_000]:
            for dv in [None, 0, 1, 1_000_000]:
                for side in [None, "buy", "sell"]:
                    result = ex.estimate_slippage(qty=qty, price=50_000, daily_volume=dv, side=side)
                    assert result >= 0.0, f"Negative slip: qty={qty}, dv={dv}, side={side}"

    def test_spread_bps_adds_half_spread(self):
        """spread_bps > 0 → half_spread가 추가됨."""
        ex = _executor()
        slip_no_spread = ex.estimate_slippage(qty=1.0, price=50_000.0, daily_volume=1_000_000)
        slip_with_spread = ex.estimate_slippage(qty=1.0, price=50_000.0, daily_volume=1_000_000, spread_bps=20.0)
        expected_half = (20.0 / 10000.0) / 2.0  # 0.001
        assert abs((slip_with_spread - slip_no_spread) - expected_half) < 1e-10
