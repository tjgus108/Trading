"""
F3. CrossExchangeArbStrategy + DEXPriceFeed 테스트.
실제 HTTP 요청 없음 — mock 사용.
"""

import pandas as pd
import pytest

from src.data.dex_feed import DEXPriceFeed
from src.strategy.cross_exchange_arb import CrossExchangeArbStrategy
from src.strategy.base import Action


# ── Helper ──────────────────────────────────────────────────────────────────

def _make_df(close: float) -> pd.DataFrame:
    """close 가격만 있는 최소 DataFrame (iloc[-1] = close)."""
    return pd.DataFrame({"close": [close - 1, close]})


# ── DEXPriceFeed ─────────────────────────────────────────────────────────────

def test_dex_feed_mock():
    """mock() 후 get_price() → 설정한 price 반환."""
    feed = DEXPriceFeed.mock("BTC", price=50000.0)
    assert feed.get_price("BTC") == 50000.0


def test_spread_positive_direction():
    """DEX > CEX 0.5% → SELL_DEX."""
    cex = 50000.0
    dex = cex * 1.005  # +0.5%
    feed = DEXPriceFeed.mock("BTC", price=dex)
    result = feed.get_spread(cex, "BTC")
    assert result["arb_direction"] == "SELL_DEX"
    assert result["spread_pct"] > 0.3


def test_spread_negative_direction():
    """DEX < CEX 0.5% → BUY_DEX."""
    cex = 50000.0
    dex = cex * 0.995  # -0.5%
    feed = DEXPriceFeed.mock("BTC", price=dex)
    result = feed.get_spread(cex, "BTC")
    assert result["arb_direction"] == "BUY_DEX"
    assert result["spread_pct"] < -0.3


def test_spread_neutral():
    """spread < 0.3% → NONE."""
    cex = 50000.0
    dex = cex * 1.001  # +0.1%
    feed = DEXPriceFeed.mock("BTC", price=dex)
    result = feed.get_spread(cex, "BTC")
    assert result["arb_direction"] == "NONE"


# ── CrossExchangeArbStrategy ─────────────────────────────────────────────────

def test_name():
    """name == 'cross_exchange_arb'."""
    strategy = CrossExchangeArbStrategy()
    assert strategy.name == "cross_exchange_arb"


def test_strategy_buy_on_dex_cheaper():
    """DEX 가격 낮을 때 BUY 신호."""
    cex = 50000.0
    dex = cex * 0.995  # DEX 0.5% 저렴
    strategy = CrossExchangeArbStrategy(min_spread_pct=0.3)
    strategy._feed = DEXPriceFeed.mock("BTC", price=dex)
    signal = strategy.generate(_make_df(cex))
    assert signal.action == Action.BUY


def test_strategy_sell_on_dex_expensive():
    """DEX 가격 높을 때 SELL 신호."""
    cex = 50000.0
    dex = cex * 1.005  # DEX 0.5% 비쌈
    strategy = CrossExchangeArbStrategy(min_spread_pct=0.3)
    strategy._feed = DEXPriceFeed.mock("BTC", price=dex)
    signal = strategy.generate(_make_df(cex))
    assert signal.action == Action.SELL


def test_strategy_hold_on_no_arb():
    """차익 없을 때 HOLD."""
    cex = 50000.0
    dex = cex * 1.001  # +0.1% → 임계값 미달
    strategy = CrossExchangeArbStrategy(min_spread_pct=0.3)
    strategy._feed = DEXPriceFeed.mock("BTC", price=dex)
    signal = strategy.generate(_make_df(cex))
    assert signal.action == Action.HOLD


def test_reasoning_contains_prices():
    """reasoning에 'CEX', 'DEX', 'spread' 포함."""
    cex = 50000.0
    dex = cex * 0.995
    strategy = CrossExchangeArbStrategy(min_spread_pct=0.3)
    strategy._feed = DEXPriceFeed.mock("BTC", price=dex)
    signal = strategy.generate(_make_df(cex))
    assert "CEX" in signal.reasoning
    assert "DEX" in signal.reasoning
    assert "spread" in signal.reasoning


def test_strategy_hold_on_dex_failure():
    """DEX 가격 0.0 (조회 실패) → HOLD."""
    cex = 50000.0
    strategy = CrossExchangeArbStrategy(min_spread_pct=0.3)
    strategy._feed = DEXPriceFeed.mock("BTC", price=0.0)
    signal = strategy.generate(_make_df(cex))
    assert signal.action == Action.HOLD


def test_registry_contains_cross_exchange_arb():
    """STRATEGY_REGISTRY에 cross_exchange_arb 등록 확인."""
    from src.orchestrator import STRATEGY_REGISTRY
    assert "cross_exchange_arb" in STRATEGY_REGISTRY
    assert STRATEGY_REGISTRY["cross_exchange_arb"] is CrossExchangeArbStrategy


# ── 레짐 필터 테스트 ──────────────────────────────────────────────────────────

def _make_df_volatile(close: float, n: int = 30) -> pd.DataFrame:
    """변동성 높은 DataFrame: 매 캔들 ±6% 진동 → realized_vol > 0.03."""
    closes = [close * (1 + 0.06 * ((-1) ** i)) for i in range(n)]
    return pd.DataFrame({"close": closes})


def _make_df_large_atr(close: float, n: int = 20) -> pd.DataFrame:
    """ATR/close > 0.02인 DataFrame: high-low 범위를 close의 5%로 설정."""
    closes = [close] * n
    highs = [close * 1.03] * n
    lows = [close * 0.97] * n   # range = 6% → ATR14 ≈ 6% >> 2%
    return pd.DataFrame({"close": closes, "high": highs, "low": lows})


def test_hold_on_high_volatility_arb():
    """realized_vol > 0.03 → HOLD (변동성 레짐 필터)"""
    cex = 50000.0
    dex = cex * 0.995  # 차익 있어도
    strategy = CrossExchangeArbStrategy(min_spread_pct=0.3)
    strategy._feed = DEXPriceFeed.mock("BTC", price=dex)
    df = _make_df_volatile(cex, n=30)
    signal = strategy.generate(df)
    assert signal.action == Action.HOLD
    assert "vol" in signal.reasoning.lower() or "변동성" in signal.reasoning


def test_hold_on_large_atr_arb():
    """atr14/close > 0.02 → HOLD (ATR 정규화 필터)"""
    cex = 50000.0
    dex = cex * 0.995
    strategy = CrossExchangeArbStrategy(min_spread_pct=0.3)
    strategy._feed = DEXPriceFeed.mock("BTC", price=dex)
    df = _make_df_large_atr(cex, n=20)
    signal = strategy.generate(df)
    assert signal.action == Action.HOLD
    assert "atr" in signal.reasoning.lower() or "ATR" in signal.reasoning
