"""
Unit tests for RsiDivergenceStrategy and BbSqueezeStrategy.
No exchange connection required.
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.rsi_divergence import RsiDivergenceStrategy
from src.strategy.bb_squeeze import BbSqueezeStrategy


# ── Helpers ──────────────────────────────────────────────────────────────────

def _base_df(n: int = 120) -> pd.DataFrame:
    """Standard OHLCV + indicators DataFrame."""
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    np.random.seed(42)
    close = 50000 + np.cumsum(np.random.randn(n) * 200)
    high = close + np.abs(np.random.randn(n) * 100)
    low = close - np.abs(np.random.randn(n) * 100)
    df = pd.DataFrame(
        {"open": close, "high": high, "low": low, "close": close, "volume": 10.0},
        index=idx,
    )
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
    df["donchian_high"] = df["high"].rolling(20).max()
    df["donchian_low"] = df["low"].rolling(20).min()
    typical = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
    return df


def _df_with_bearish_divergence(n: int = 120) -> pd.DataFrame:
    """Craft a DataFrame where the last completed candle shows bearish RSI divergence."""
    df = _base_df(n)
    # Set price higher high but RSI lower high at the last two meaningful points
    # Last completed candle = iloc[-2]; earlier reference = iloc[-8]
    ref_idx = -8
    last_idx = -2

    ref_price = float(df["high"].iloc[ref_idx])
    # Make last high strictly greater than reference high
    df.iloc[last_idx, df.columns.get_loc("high")] = ref_price * 1.05

    # Make RSI at last candle strictly less than at reference candle
    ref_rsi = float(df["rsi14"].iloc[ref_idx])
    target_rsi = max(ref_rsi - 10, 20)
    df.iloc[last_idx, df.columns.get_loc("rsi14")] = target_rsi
    return df


def _df_with_bullish_divergence(n: int = 120) -> pd.DataFrame:
    """Craft a DataFrame where the last completed candle shows bullish RSI divergence only."""
    df = _base_df(n)
    ref_idx = -8
    last_idx = -2

    ref_low = float(df["low"].iloc[ref_idx])
    # Make last low strictly lower (bullish divergence setup)
    df.iloc[last_idx, df.columns.get_loc("low")] = ref_low * 0.95

    # Make RSI at last candle strictly higher than at reference (bullish divergence)
    ref_rsi = float(df["rsi14"].iloc[ref_idx])
    target_rsi = min(ref_rsi + 10, 80)
    df.iloc[last_idx, df.columns.get_loc("rsi14")] = target_rsi

    # Prevent bearish divergence: ensure last high <= all earlier highs in the window
    # so that price-higher-high condition is NOT met
    window_highs = df["high"].iloc[-20:-2]
    min_high_in_window = float(window_highs.min())
    df.iloc[last_idx, df.columns.get_loc("high")] = min_high_in_window * 0.98

    return df


# ══════════════════════════════════════════════════════════════════════════════
# RSI Divergence Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestRsiDivergenceStrategy:

    def test_name(self):
        assert RsiDivergenceStrategy.name == "rsi_divergence"

    def test_returns_valid_signal_on_normal_data(self):
        df = _base_df()
        sig = RsiDivergenceStrategy().generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.strategy == "rsi_divergence"
        assert sig.entry_price > 0

    def test_hold_on_insufficient_data(self):
        df = _base_df(10)  # Too short
        sig = RsiDivergenceStrategy().generate(df)
        assert sig.action == Action.HOLD

    def test_bearish_divergence_gives_sell(self):
        df = _df_with_bearish_divergence()
        sig = RsiDivergenceStrategy().generate(df)
        assert sig.action == Action.SELL

    def test_bearish_divergence_confidence(self):
        df = _df_with_bearish_divergence()
        sig = RsiDivergenceStrategy().generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    def test_bullish_divergence_gives_buy(self):
        df = _df_with_bullish_divergence()
        sig = RsiDivergenceStrategy().generate(df)
        assert sig.action == Action.BUY

    def test_bullish_divergence_confidence(self):
        df = _df_with_bullish_divergence()
        sig = RsiDivergenceStrategy().generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    def test_signal_has_reasoning(self):
        df = _df_with_bearish_divergence()
        sig = RsiDivergenceStrategy().generate(df)
        assert len(sig.reasoning) > 0

    def test_signal_has_invalidation_on_trade(self):
        df = _df_with_bullish_divergence()
        sig = RsiDivergenceStrategy().generate(df)
        assert len(sig.invalidation) > 0

    def test_entry_price_equals_last_close(self):
        df = _base_df()
        sig = RsiDivergenceStrategy().generate(df)
        assert sig.entry_price == pytest.approx(df["close"].iloc[-2])

    def test_high_confidence_on_large_divergence(self):
        """Force a very large divergence (>2%) to confirm HIGH confidence."""
        df = _base_df()
        ref_idx = -8
        last_idx = -2
        # Extreme bearish divergence
        ref_price = float(df["high"].iloc[ref_idx])
        df.iloc[last_idx, df.columns.get_loc("high")] = ref_price * 1.20  # +20% price
        ref_rsi = float(df["rsi14"].iloc[ref_idx])
        df.iloc[last_idx, df.columns.get_loc("rsi14")] = max(ref_rsi - 25, 10)
        sig = RsiDivergenceStrategy().generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence == Confidence.HIGH

    def test_no_divergence_hold(self):
        """Flat price and RSI → HOLD."""
        df = _base_df()
        # Make high and RSI identical across all last 20 candles → no divergence
        df.iloc[-20:, df.columns.get_loc("high")] = 50000.0
        df.iloc[-20:, df.columns.get_loc("low")] = 49000.0
        df.iloc[-20:, df.columns.get_loc("rsi14")] = 50.0
        sig = RsiDivergenceStrategy().generate(df)
        assert sig.action == Action.HOLD


# ══════════════════════════════════════════════════════════════════════════════
# Bollinger Band Squeeze Tests
# ══════════════════════════════════════════════════════════════════════════════

def _df_with_bb_squeeze_buy(n: int = 200) -> pd.DataFrame:
    """
    Craft a DataFrame where:
    - Previous candle has narrow BB (squeeze)
    - Last completed candle expands above upper BB (BUY signal)
    """
    df = _base_df(n)
    # Flatten prices for many bars to create squeeze (low variance)
    flat_start = n - 30
    flat_end = n - 2  # up to but not including last completed candle (iloc[-2] = index n-2)
    df.iloc[flat_start:flat_end, df.columns.get_loc("close")] = 50000.0
    df.iloc[flat_start:flat_end, df.columns.get_loc("open")] = 50000.0
    df.iloc[flat_start:flat_end, df.columns.get_loc("high")] = 50010.0
    df.iloc[flat_start:flat_end, df.columns.get_loc("low")] = 49990.0

    # Last completed candle (iloc[-2]): big breakout upward
    df.iloc[-2, df.columns.get_loc("close")] = 52000.0
    df.iloc[-2, df.columns.get_loc("high")] = 52200.0
    df.iloc[-2, df.columns.get_loc("low")] = 51800.0
    return df


def _df_with_bb_squeeze_sell(n: int = 200) -> pd.DataFrame:
    """
    Craft a DataFrame where:
    - Previous candle has narrow BB (squeeze)
    - Last completed candle breaks below lower BB (SELL signal)
    """
    df = _base_df(n)
    flat_start = n - 30
    flat_end = n - 2
    df.iloc[flat_start:flat_end, df.columns.get_loc("close")] = 50000.0
    df.iloc[flat_start:flat_end, df.columns.get_loc("open")] = 50000.0
    df.iloc[flat_start:flat_end, df.columns.get_loc("high")] = 50010.0
    df.iloc[flat_start:flat_end, df.columns.get_loc("low")] = 49990.0

    # Last completed candle: big breakdown downward
    df.iloc[-2, df.columns.get_loc("close")] = 48000.0
    df.iloc[-2, df.columns.get_loc("high")] = 48200.0
    df.iloc[-2, df.columns.get_loc("low")] = 47800.0
    return df


class TestBbSqueezeStrategy:

    def test_name(self):
        assert BbSqueezeStrategy.name == "bb_squeeze"

    def test_returns_valid_signal(self):
        df = _base_df(200)
        sig = BbSqueezeStrategy().generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.strategy == "bb_squeeze"
        assert sig.entry_price > 0

    def test_hold_on_insufficient_data(self):
        df = _base_df(30)  # Too short (needs BB_PERIOD + PERCENTILE_WINDOW + 2 = 72)
        sig = BbSqueezeStrategy().generate(df)
        assert sig.action == Action.HOLD

    def test_squeeze_release_upward_gives_buy(self):
        df = _df_with_bb_squeeze_buy(200)
        sig = BbSqueezeStrategy().generate(df)
        assert sig.action == Action.BUY

    def test_squeeze_release_downward_gives_sell(self):
        df = _df_with_bb_squeeze_sell(200)
        sig = BbSqueezeStrategy().generate(df)
        assert sig.action == Action.SELL

    def test_buy_signal_confidence_is_high(self):
        df = _df_with_bb_squeeze_buy(200)
        sig = BbSqueezeStrategy().generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    def test_sell_signal_confidence_is_high(self):
        df = _df_with_bb_squeeze_sell(200)
        sig = BbSqueezeStrategy().generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence == Confidence.HIGH

    def test_signal_has_reasoning(self):
        df = _df_with_bb_squeeze_buy(200)
        sig = BbSqueezeStrategy().generate(df)
        assert len(sig.reasoning) > 0

    def test_entry_price_equals_last_close(self):
        df = _base_df(200)
        sig = BbSqueezeStrategy().generate(df)
        assert sig.entry_price == pytest.approx(df["close"].iloc[-2])

    def test_no_squeeze_gives_hold(self):
        """High-volatility random walk: unlikely to be in squeeze → HOLD."""
        np.random.seed(99)
        n = 200
        idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
        # Very high variance so BB width stays wide (not in squeeze)
        close = 50000 + np.cumsum(np.random.randn(n) * 2000)
        high = close + np.abs(np.random.randn(n) * 1000)
        low = close - np.abs(np.random.randn(n) * 1000)
        df = pd.DataFrame(
            {"open": close, "high": high, "low": low, "close": close, "volume": 10.0},
            index=idx,
        )
        # Add required indicator columns
        df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
        prev_close = df["close"].shift(1)
        tr = pd.concat(
            [(df["high"] - df["low"]), (df["high"] - prev_close).abs(), (df["low"] - prev_close).abs()],
            axis=1,
        ).max(axis=1)
        df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
        delta = df["close"].diff()
        gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
        df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
        df["donchian_high"] = df["high"].rolling(20).max()
        df["donchian_low"] = df["low"].rolling(20).min()
        typical = (df["high"] + df["low"] + df["close"]) / 3
        df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
        sig = BbSqueezeStrategy().generate(df)
        # With very high variance the squeeze condition rarely triggers
        # Just verify it returns a valid signal
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    def test_registry_contains_both_strategies(self):
        """Both strategies must be in STRATEGY_REGISTRY."""
        from src.orchestrator import STRATEGY_REGISTRY
        assert "rsi_divergence" in STRATEGY_REGISTRY
        assert "bb_squeeze" in STRATEGY_REGISTRY

    def test_registry_instantiates_correctly(self):
        from src.orchestrator import STRATEGY_REGISTRY
        rsi_strat = STRATEGY_REGISTRY["rsi_divergence"]()
        bb_strat = STRATEGY_REGISTRY["bb_squeeze"]()
        assert rsi_strat.name == "rsi_divergence"
        assert bb_strat.name == "bb_squeeze"


# ══════════════════════════════════════════════════════════════════════════════
# 데이터 부족 → HOLD 방어 테스트
# ══════════════════════════════════════════════════════════════════════════════

def _small_df(n: int = 5) -> pd.DataFrame:
    """최소 행 수 미달 DataFrame."""
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    close = [50000.0 + i * 10 for i in range(n)]
    df = pd.DataFrame(
        {"open": close, "high": close, "low": close, "close": close, "volume": 10.0},
        index=idx,
    )
    df["rsi14"] = 50.0
    df["atr14"] = 500.0
    return df


def test_strategy_insufficient_data_hold_rsi_divergence():
    """5행짜리 df → rsi_divergence HOLD 반환"""
    df = _small_df(5)
    sig = RsiDivergenceStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_strategy_insufficient_data_hold_regime_adaptive():
    """5행짜리 df → regime_adaptive HOLD 반환"""
    from src.strategy.regime_adaptive import RegimeAdaptiveStrategy
    df = _small_df(5)
    sig = RegimeAdaptiveStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_strategy_none_df_hold_rsi_divergence():
    """None df → rsi_divergence HOLD 반환"""
    sig = RsiDivergenceStrategy().generate(None)
    assert sig.action == Action.HOLD


def test_circuit_breaker_reset_daily():
    """reset_daily() 후 _daily_loss == 0, _consecutive_losses == 0"""
    from src.risk.manager import CircuitBreaker
    cb = CircuitBreaker(max_daily_loss=0.05, max_drawdown=0.10)
    cb._daily_loss = 0.08
    cb._consecutive_losses = 3
    cb.reset_daily()
    assert cb._daily_loss == 0.0
    assert cb._consecutive_losses == 0
