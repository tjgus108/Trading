"""Phase I: MultiStrategyAggregator, DrawdownMonitor, VolTargeting 테스트."""

import sys
import os
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock

from src.strategy.base import Action, Confidence, Signal
from src.strategy.multi_signal import MultiStrategyAggregator
from src.risk.drawdown_monitor import DrawdownMonitor
from src.risk.vol_targeting import VolTargeting


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 10, close: float = 50000.0) -> pd.DataFrame:
    return pd.DataFrame({
        "open": [close] * n,
        "high": [close * 1.01] * n,
        "low": [close * 0.99] * n,
        "close": [close + i for i in range(n)],
        "volume": [100.0] * n,
    })


def _make_strategy(action: Action, confidence: Confidence = Confidence.MEDIUM, name: str = "test") -> MagicMock:
    s = MagicMock()
    s.name = name
    s.generate.return_value = Signal(
        action=action, confidence=confidence, strategy=name,
        entry_price=50100.0, reasoning="test", invalidation="",
        bull_case="", bear_case="",
    )
    return s


# ═══════════════════════════════════════════════════════════════════════════
# I1. MultiStrategyAggregator
# ═══════════════════════════════════════════════════════════════════════════

class TestMultiStrategyAggregator:

    def test_unanimous_buy(self):
        strategies = [
            _make_strategy(Action.BUY, name="a"),
            _make_strategy(Action.BUY, name="b"),
            _make_strategy(Action.BUY, name="c"),
        ]
        agg = MultiStrategyAggregator(strategies)
        sig = agg.generate(_make_df())
        assert sig.action == Action.BUY

    def test_unanimous_sell(self):
        strategies = [
            _make_strategy(Action.SELL, name="a"),
            _make_strategy(Action.SELL, name="b"),
        ]
        agg = MultiStrategyAggregator(strategies)
        sig = agg.generate(_make_df())
        assert sig.action == Action.SELL

    def test_majority_buy(self):
        strategies = [
            _make_strategy(Action.BUY, name="a"),
            _make_strategy(Action.BUY, name="b"),
            _make_strategy(Action.SELL, name="c"),
        ]
        agg = MultiStrategyAggregator(strategies)
        sig = agg.generate(_make_df())
        assert sig.action == Action.BUY

    def test_tie_returns_hold(self):
        strategies = [
            _make_strategy(Action.BUY, name="a"),
            _make_strategy(Action.SELL, name="b"),
        ]
        agg = MultiStrategyAggregator(strategies)
        sig = agg.generate(_make_df())
        assert sig.action == Action.HOLD

    def test_all_hold(self):
        strategies = [
            _make_strategy(Action.HOLD, name="a"),
            _make_strategy(Action.HOLD, name="b"),
        ]
        agg = MultiStrategyAggregator(strategies)
        sig = agg.generate(_make_df())
        assert sig.action == Action.HOLD

    def test_empty_strategies(self):
        agg = MultiStrategyAggregator([])
        sig = agg.generate(_make_df())
        assert sig.action == Action.HOLD

    def test_strategy_name(self):
        strategies = [_make_strategy(Action.BUY, name="a")]
        agg = MultiStrategyAggregator(strategies)
        sig = agg.generate(_make_df())
        assert sig.strategy == "multi_aggregator"

    def test_high_confidence_buy_weight(self):
        """HIGH confidence BUY + LOW confidence SELL → BUY 우세."""
        strategies = [
            _make_strategy(Action.BUY, Confidence.HIGH, name="a"),
            _make_strategy(Action.SELL, Confidence.LOW, name="b"),
        ]
        agg = MultiStrategyAggregator(strategies)
        sig = agg.generate(_make_df())
        assert sig.action == Action.BUY

    def test_custom_weights(self):
        """custom weight으로 SELL 전략 우세."""
        strategies = [
            _make_strategy(Action.BUY, Confidence.HIGH, name="weak"),
            _make_strategy(Action.SELL, Confidence.LOW, name="strong"),
        ]
        agg = MultiStrategyAggregator(strategies, weights={"strong": 10.0})
        sig = agg.generate(_make_df())
        assert sig.action == Action.SELL

    def test_strategy_exception_handled(self):
        """실패하는 전략이 있어도 다른 전략으로 동작."""
        bad = MagicMock()
        bad.name = "bad"
        bad.generate.side_effect = RuntimeError("broken")
        good = _make_strategy(Action.BUY, name="good")
        agg = MultiStrategyAggregator([bad, good])
        sig = agg.generate(_make_df())
        assert sig.action == Action.BUY


# ═══════════════════════════════════════════════════════════════════════════
# I2. DrawdownMonitor
# ═══════════════════════════════════════════════════════════════════════════

class TestDrawdownMonitor:

    def test_no_drawdown_not_halted(self):
        monitor = DrawdownMonitor(max_drawdown_pct=0.15)
        status = monitor.update(10000)
        assert not status.halted
        assert status.drawdown_pct == 0.0

    def test_drawdown_below_limit(self):
        monitor = DrawdownMonitor(max_drawdown_pct=0.15)
        monitor.update(10000)
        status = monitor.update(9000)   # 10% 낙폭
        assert not status.halted
        assert abs(status.drawdown_pct - 0.10) < 1e-6

    def test_drawdown_exceeds_limit_halted(self):
        monitor = DrawdownMonitor(max_drawdown_pct=0.10)
        monitor.update(10000)
        status = monitor.update(8900)   # 11% 낙폭 > 10%
        assert status.halted

    def test_is_halted(self):
        monitor = DrawdownMonitor(max_drawdown_pct=0.10)
        monitor.update(10000)
        monitor.update(8900)
        assert monitor.is_halted()

    def test_recovery_resumes(self):
        monitor = DrawdownMonitor(max_drawdown_pct=0.10, recovery_pct=0.03)
        monitor.update(10000)
        monitor.update(8900)   # 11% → halted
        assert monitor.is_halted()
        monitor.update(9800)   # 2% 낙폭 < (10% - 3%) = 7%
        assert not monitor.is_halted()

    def test_peak_update(self):
        monitor = DrawdownMonitor(max_drawdown_pct=0.20)
        monitor.update(10000)
        status = monitor.update(12000)  # 새 고점
        assert status.peak_equity == 12000
        assert status.drawdown_pct == 0.0

    def test_reset(self):
        monitor = DrawdownMonitor(max_drawdown_pct=0.10)
        monitor.update(10000)
        monitor.update(8000)
        assert monitor.is_halted()
        monitor.reset()
        assert not monitor.is_halted()
        assert monitor.current_drawdown() == 0.0

    def test_force_halt_and_resume(self):
        monitor = DrawdownMonitor(max_drawdown_pct=0.20)
        monitor.force_halt("manual test")
        assert monitor.is_halted()
        monitor.force_resume()
        assert not monitor.is_halted()


# ═══════════════════════════════════════════════════════════════════════════
# I3. VolTargeting
# ═══════════════════════════════════════════════════════════════════════════

class TestVolTargeting:

    def _make_volatile_df(self, vol: float = 0.02, n: int = 30) -> pd.DataFrame:
        """주어진 수익률 변동성의 가격 시리즈 생성."""
        rng = np.random.default_rng(42)
        returns = rng.normal(0, vol, n - 1)
        closes = [50000.0]
        for r in returns:
            closes.append(closes[-1] * (1 + r))
        return pd.DataFrame({"close": closes})

    def test_high_vol_reduces_size(self):
        """고변동성 → size 축소."""
        vt = VolTargeting(target_vol=0.20, annualization=252 * 24)
        high_vol_df = self._make_volatile_df(vol=0.05)  # 높은 일별 변동성
        size = vt.adjust(1.0, high_vol_df)
        assert size < 1.0, f"고변동성에서 size 축소 필요: {size}"

    def test_low_vol_increases_size(self):
        """저변동성 → size 확대 (최대 max_scalar)."""
        vt = VolTargeting(target_vol=0.20, annualization=252 * 24, max_scalar=3.0)
        low_vol_df = self._make_volatile_df(vol=0.001)  # 낮은 일별 변동성
        size = vt.adjust(1.0, low_vol_df)
        assert size > 1.0, f"저변동성에서 size 확대 필요: {size}"

    def test_max_scalar_cap(self):
        """max_scalar 초과하지 않음."""
        vt = VolTargeting(target_vol=0.20, max_scalar=2.0)
        df = self._make_volatile_df(vol=0.0001)  # 극저변동성
        size = vt.adjust(1.0, df)
        assert size <= 2.0 + 1e-9

    def test_min_scalar_floor(self):
        """min_scalar 미만으로 내려가지 않음."""
        vt = VolTargeting(target_vol=0.05, min_scalar=0.1)
        df = self._make_volatile_df(vol=0.10)  # 극고변동성
        size = vt.adjust(1.0, df)
        assert size >= 0.1 - 1e-9

    def test_insufficient_data_returns_base(self):
        """데이터 1개 → scalar=1.0 → base_size 그대로."""
        vt = VolTargeting(target_vol=0.20)
        df = pd.DataFrame({"close": [50000.0]})
        size = vt.adjust(0.5, df)
        assert size == 0.5

    def test_realized_vol_positive(self):
        vt = VolTargeting()
        df = self._make_volatile_df(vol=0.02)
        rv = vt.realized_vol(df)
        assert rv > 0

    def test_scalar_near_one_when_vol_matches(self):
        """목표 변동성 == 실현 변동성 → scalar ≈ 1.0."""
        # 연환산 20% 변동성 재현 (1h 기준)
        annualization = 252 * 24
        target_vol = 0.20
        per_period_vol = target_vol / np.sqrt(annualization)
        rng = np.random.default_rng(0)
        closes = [50000.0]
        for _ in range(200):
            closes.append(closes[-1] * (1 + rng.normal(0, per_period_vol)))
        df = pd.DataFrame({"close": closes})
        vt = VolTargeting(target_vol=target_vol, annualization=annualization, window=200)
        s = vt.scalar(df)
        assert 0.5 < s < 2.0, f"scalar={s} should be near 1.0"
