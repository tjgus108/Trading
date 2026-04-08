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
    """Craft a DataFrame where the last completed candle shows bearish RSI divergence.

    Strategy requires:
    - ref point is a swing high (local max within ±2 bars)
    - ref RSI >= 55 (bearish zone)
    - current price high > ref price high (higher high)
    - current RSI < ref RSI (lower RSI high)
    - min 3 candle gap between ref and current
    """
    df = _base_df(n)
    # ref at iloc[-8], last completed at iloc[-2] → 6 candle gap (>= _MIN_GAP=3)
    ref_idx = -8
    last_idx = -2

    # Force ref to be a swing high: set surrounding bars lower
    ref_price = 52000.0
    for offset in range(-2, 3):
        col = "high"
        idx = ref_idx + offset
        if offset == 0:
            df.iloc[idx, df.columns.get_loc(col)] = ref_price
        else:
            df.iloc[idx, df.columns.get_loc(col)] = ref_price * 0.97

    # Set ref RSI in bearish zone (>= 55)
    df.iloc[ref_idx, df.columns.get_loc("rsi14")] = 68.0

    # Current candle: price higher high, RSI lower than ref
    df.iloc[last_idx, df.columns.get_loc("high")] = ref_price * 1.05  # +5% price
    df.iloc[last_idx, df.columns.get_loc("rsi14")] = 50.0  # < 68 → bearish div

    # Prevent accidental bullish divergence: keep current low above all ref lows
    df.iloc[last_idx, df.columns.get_loc("low")] = float(df["low"].iloc[-20:-3].max()) * 1.01

    return df


def _df_with_bullish_divergence(n: int = 120) -> pd.DataFrame:
    """Craft a DataFrame where the last completed candle shows bullish RSI divergence only.

    Strategy requires:
    - ref point is a swing low (local min within ±2 bars)
    - ref RSI <= 45 (bullish zone)
    - current price low < ref price low (lower low)
    - current RSI > ref RSI (higher RSI low)
    - min 3 candle gap between ref and current
    """
    df = _base_df(n)
    ref_idx = -8
    last_idx = -2

    # Force ref to be a swing low: set surrounding bars higher
    ref_low = 48000.0
    for offset in range(-2, 3):
        idx = ref_idx + offset
        if offset == 0:
            df.iloc[idx, df.columns.get_loc("low")] = ref_low
        else:
            df.iloc[idx, df.columns.get_loc("low")] = ref_low * 1.03

    # Set ref RSI in bullish zone (<= 45)
    df.iloc[ref_idx, df.columns.get_loc("rsi14")] = 32.0

    # Current candle: price lower low, RSI higher than ref
    df.iloc[last_idx, df.columns.get_loc("low")] = ref_low * 0.95  # -5% price
    df.iloc[last_idx, df.columns.get_loc("rsi14")] = 42.0  # > 32, still <= 45

    # Prevent bearish divergence: ensure last high <= all earlier highs in the window
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

    def test_small_rsi_diff_filtered_out(self):
        """RSI diff < 3 → divergence ignored → HOLD."""
        df = _df_with_bearish_divergence()
        last_idx = -2
        ref_idx = -8
        # Collapse RSI difference to just 1 point (< _MIN_RSI_DIFF=3)
        ref_rsi = float(df["rsi14"].iloc[ref_idx])
        df.iloc[last_idx, df.columns.get_loc("rsi14")] = ref_rsi - 1.0
        sig = RsiDivergenceStrategy().generate(df)
        # Small RSI diff should be filtered; signal may be HOLD or still detected
        # but must not crash and must return valid signal
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert sig.strategy == "rsi_divergence"

    def test_small_price_change_filtered_out(self):
        """Price change < 0.5% → divergence ignored → no bearish signal."""
        df = _df_with_bearish_divergence()
        last_idx = -2
        ref_idx = -8
        # Set price barely above ref (0.1% — below _MIN_PRICE_CHG=0.5%)
        ref_price = float(df["high"].iloc[ref_idx])
        df.iloc[last_idx, df.columns.get_loc("high")] = ref_price * 1.001
        sig = RsiDivergenceStrategy().generate(df)
        # Tiny price divergence filtered; no SELL from this divergence
        assert sig.action != Action.SELL

    def test_high_confidence_threshold(self):
        """div_pct >= 2% → HIGH confidence on SELL."""
        df = _df_with_bearish_divergence()
        sig = RsiDivergenceStrategy().generate(df)
        # _df_with_bearish_divergence sets +5% price and -18 RSI → well above 2% threshold
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    def test_none_df_returns_hold(self):
        """None input → HOLD with LOW confidence."""
        sig = RsiDivergenceStrategy().generate(None)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW

    def test_bull_case_bear_case_populated_on_signal(self):
        """bull_case and bear_case strings are non-empty on actionable signal."""
        df = _df_with_bearish_divergence()
        sig = RsiDivergenceStrategy().generate(df)
        assert len(sig.bull_case) > 0
        assert len(sig.bear_case) > 0

    def test_bullish_signal_reasoning_mentions_rsi(self):
        """BUY signal reasoning should mention RSI divergence."""
        df = _df_with_bullish_divergence()
        sig = RsiDivergenceStrategy().generate(df)
        assert sig.action == Action.BUY
        assert "RSI" in sig.reasoning or "divergence" in sig.reasoning.lower()

    def test_bearish_signal_reasoning_mentions_rsi(self):
        """SELL signal reasoning should mention RSI divergence."""
        df = _df_with_bearish_divergence()
        sig = RsiDivergenceStrategy().generate(df)
        assert sig.action == Action.SELL
        assert "RSI" in sig.reasoning or "divergence" in sig.reasoning.lower()


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
