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
