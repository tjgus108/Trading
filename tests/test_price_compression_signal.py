"""PriceCompressionSignalStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_compression_signal import PriceCompressionSignalStrategy
from src.strategy.base import Action, Confidence


# ── 헬퍼 ──────────────────────────────────────────────────────────────────────

def _make_df(n: int = 30, base_range: float = 2.0) -> pd.DataFrame:
    """균일한 range의 기본 DataFrame."""
    close = np.linspace(100.0, 110.0, n)
    return pd.DataFrame({
        "open":  close - 0.5,
        "high":  close + base_range / 2,
        "low":   close - base_range / 2,
        "close": close,
        "volume": np.full(n, 1000.0),
    })


def _make_nr7_buy_df(n: int = 30) -> pd.DataFrame:
    """
    iloc[-2]가 NR7 + close > prev_high(rolling 3봉 max, shift 1) → BUY.
    """
    close = np.linspace(100.0, 110.0, n)
    high = close + 2.0
    low = close - 2.0

    # iloc[-2]: range를 아주 좁게 (NR7)
    nr_idx = n - 2
    high[nr_idx] = close[nr_idx] + 0.1
    low[nr_idx]  = close[nr_idx] - 0.1   # range = 0.2

    # prev_high: 이전 3봉(idx -5, -4, -3)의 최대 high
    # close를 prev_high보다 크게 설정
    prev_highs = [high[nr_idx - 3], high[nr_idx - 2], high[nr_idx - 1]]
    prev_max = max(prev_highs)
    close[nr_idx] = prev_max + 1.0
    high[nr_idx] = close[nr_idx] + 0.1
    low[nr_idx]  = close[nr_idx] - 0.1

    return pd.DataFrame({
        "open":  close - 0.3,
        "high":  high,
        "low":   low,
        "close": close,
        "volume": np.full(n, 1000.0),
    })


def _make_nr7_sell_df(n: int = 30) -> pd.DataFrame:
    """
    iloc[-2]가 NR7 + close < prev_low(rolling 3봉 min, shift 1) → SELL.
    """
    close = np.linspace(110.0, 100.0, n)
    high = close + 2.0
    low = close - 2.0

    nr_idx = n - 2
    high[nr_idx] = close[nr_idx] + 0.1
    low[nr_idx]  = close[nr_idx] - 0.1

    prev_lows = [low[nr_idx - 3], low[nr_idx - 2], low[nr_idx - 1]]
    prev_min = min(prev_lows)
    close[nr_idx] = prev_min - 1.0
    high[nr_idx] = close[nr_idx] + 0.1
    low[nr_idx]  = close[nr_idx] - 0.1

    return pd.DataFrame({
        "open":  close + 0.3,
        "high":  high,
        "low":   low,
        "close": close,
        "volume": np.full(n, 1000.0),
    })


def _make_nr7_no_breakout_df(n: int = 30) -> pd.DataFrame:
    """NR7이지만 돌파 없음 → HOLD."""
    close = np.linspace(100.0, 110.0, n)
    high = close + 2.0
    low = close - 2.0

    nr_idx = n - 2
    # NR7: range 0.2
    high[nr_idx] = close[nr_idx] + 0.1
    low[nr_idx]  = close[nr_idx] - 0.1

    # close가 prev_high 아래, prev_low 위에 있음 → 돌파 없음
    # (기본 close 값은 중간이므로 그대로 유지)

    return pd.DataFrame({
        "open":  close - 0.3,
        "high":  high,
        "low":   low,
        "close": close,
        "volume": np.full(n, 1000.0),
    })


# ── 테스트 ─────────────────────────────────────────────────────────────────────

class TestPriceCompressionSignalStrategy:

    def setup_method(self):
        self.strat = PriceCompressionSignalStrategy()

    # 1. name 확인
    def test_name(self):
        assert self.strat.name == "price_compression_signal"

    # 2. MIN_ROWS 미만 → HOLD
    def test_insufficient_rows_hold(self):
        df = _make_df(n=10)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert "데이터 부족" in sig.reasoning

    # 3. MIN_ROWS 경계값 (24행) → HOLD
    def test_boundary_24_rows(self):
        df = _make_df(n=24)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 4. MIN_ROWS 정확히 (25행) → 신호 생성 가능
    def test_boundary_25_rows(self):
        df = _make_df(n=25)
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 5. NR7 + 상향 돌파 → BUY
    def test_nr7_buy_signal(self):
        df = _make_nr7_buy_df(n=40)
        sig = self.strat.generate(df)
        assert sig.action == Action.BUY

    # 6. NR7 + 하향 돌파 → SELL
    def test_nr7_sell_signal(self):
        df = _make_nr7_sell_df(n=40)
        sig = self.strat.generate(df)
        assert sig.action == Action.SELL

    # 7. NR7 아닌 경우 → HOLD
    def test_no_nr7_hold(self):
        df = _make_df(n=30)  # 균일 range, 마지막 봉이 NR7 아님
        # 마지막 봉 range를 크게 만들어 NR7 아니게 함
        df.loc[df.index[-2], "high"] = float(df["close"].iloc[-2]) + 5.0
        df.loc[df.index[-2], "low"]  = float(df["close"].iloc[-2]) - 5.0
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 8. BUY confidence는 HIGH 또는 MEDIUM
    def test_buy_confidence_valid(self):
        df = _make_nr7_buy_df(n=40)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 9. SELL confidence는 HIGH 또는 MEDIUM
    def test_sell_confidence_valid(self):
        df = _make_nr7_sell_df(n=40)
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 10. entry_price 양수
    def test_entry_price_positive(self):
        df = _make_nr7_buy_df(n=40)
        sig = self.strat.generate(df)
        assert sig.entry_price > 0

    # 11. strategy 필드 일치
    def test_signal_strategy_field(self):
        df = _make_nr7_buy_df(n=40)
        sig = self.strat.generate(df)
        assert sig.strategy == "price_compression_signal"

    # 12. HOLD 시 LOW confidence
    def test_hold_low_confidence(self):
        df = _make_df(n=30)
        sig = self.strat.generate(df)
        if sig.action == Action.HOLD:
            assert sig.confidence == Confidence.LOW

    # 13. NaN 포함 데이터 → HOLD
    def test_nan_handling(self):
        df = _make_df(n=30)
        df.loc[df.index[-2], "high"] = float("nan")
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 14. reasoning 문자열 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_nr7_buy_df(n=40)
        sig = self.strat.generate(df)
        assert len(sig.reasoning) > 0

    # 15. 충분히 긴 데이터 (100행) → 예외 없음
    def test_long_data_no_exception(self):
        df = _make_df(n=100)
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 16. HIGH confidence: range < avg_range * 0.5
    def test_high_confidence_small_range(self):
        n = 40
        close = np.linspace(100.0, 110.0, n)
        # 큰 range 데이터 생성 후 마지막 봉만 극소 range
        high = close + 10.0
        low  = close - 10.0
        nr_idx = n - 2
        # NR7: 아주 좁은 range
        high[nr_idx] = close[nr_idx] + 0.05
        low[nr_idx]  = close[nr_idx] - 0.05
        # prev_high보다 close를 위에
        prev_max = max(high[nr_idx - 3], high[nr_idx - 2], high[nr_idx - 1])
        close[nr_idx] = prev_max + 5.0
        high[nr_idx] = close[nr_idx] + 0.05
        low[nr_idx]  = close[nr_idx] - 0.05
        df = pd.DataFrame({
            "open":  close - 0.3,
            "high":  high,
            "low":   low,
            "close": close,
            "volume": np.full(n, 1000.0),
        })
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH
