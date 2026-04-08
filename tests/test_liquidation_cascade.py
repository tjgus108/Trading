"""
LiquidationCascadeStrategy 단위 테스트.
모든 테스트는 mock 사용 — 실제 API 호출 없음.
"""

import time
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.data.liquidation_feed import LiquidationFetcher, LiquidationPressure
from src.strategy.base import Action, Confidence
from src.strategy.liquidation_cascade import LiquidationCascadeStrategy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df(rsi: float = 50.0, close: float = 50000.0, n: int = 5) -> pd.DataFrame:
    """최소 generate() 실행에 필요한 DataFrame 생성 (인덱스 -2 참조)."""
    data = {
        "close": [close] * n,
        "rsi14": [rsi] * n,
    }
    return pd.DataFrame(data)


def _pressure(long_liq: float = 1_000_000, short_liq: float = 200_000,
              cascade_risk: bool = False) -> LiquidationPressure:
    total = long_liq + short_liq
    ratio = long_liq / (total + 1e-9)
    score = max(-3.0, min(3.0, (0.5 - ratio) * 6.0))
    return LiquidationPressure(
        long_liq_usd=long_liq,
        short_liq_usd=short_liq,
        liq_ratio=ratio,
        total_liq_usd=total,
        cascade_risk=cascade_risk,
        score=score,
    )


# ---------------------------------------------------------------------------
# 1. name
# ---------------------------------------------------------------------------

def test_name():
    strategy = LiquidationCascadeStrategy()
    assert strategy.name == "liquidation_cascade"


# ---------------------------------------------------------------------------
# 2. LiquidationFetcher.compute_pressure — long liq dominant
# ---------------------------------------------------------------------------

def test_pressure_long_liq_dominant():
    fetcher = LiquidationFetcher.mock(long_liq=1_000_000, short_liq=50_000)
    p = fetcher.compute_pressure()
    assert p.liq_ratio > 0.75, f"Expected ratio > 0.75, got {p.liq_ratio}"
    assert p.long_liq_usd > p.short_liq_usd


# ---------------------------------------------------------------------------
# 3. LiquidationFetcher.compute_pressure — short liq dominant
# ---------------------------------------------------------------------------

def test_pressure_short_liq_dominant():
    fetcher = LiquidationFetcher.mock(long_liq=50_000, short_liq=1_000_000)
    p = fetcher.compute_pressure()
    assert p.liq_ratio < 0.25, f"Expected ratio < 0.25, got {p.liq_ratio}"
    assert p.short_liq_usd > p.long_liq_usd


# ---------------------------------------------------------------------------
# 4. score range -3 ~ +3
# ---------------------------------------------------------------------------

def test_pressure_score_range():
    for long_liq, short_liq in [
        (1_000_000, 0),
        (0, 1_000_000),
        (500_000, 500_000),
        (1_000_000, 1_000_000),
    ]:
        fetcher = LiquidationFetcher.mock(long_liq=long_liq, short_liq=short_liq)
        p = fetcher.compute_pressure()
        assert -3.0 <= p.score <= 3.0, f"score out of range: {p.score}"


# ---------------------------------------------------------------------------
# 5. BUY HIGH on long cascade + RSI < 35
# ---------------------------------------------------------------------------

def test_strategy_buy_on_long_cascade():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=30.0)

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=900_000, short_liq=100_000)):
        signal = strategy.generate(df)

    assert signal.action == Action.BUY
    assert signal.confidence == Confidence.HIGH


# ---------------------------------------------------------------------------
# 6. SELL HIGH on short cascade + RSI > 65
# ---------------------------------------------------------------------------

def test_strategy_sell_on_short_cascade():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=70.0)

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=100_000, short_liq=900_000)):
        signal = strategy.generate(df)

    assert signal.action == Action.SELL
    assert signal.confidence == Confidence.HIGH


# ---------------------------------------------------------------------------
# 7. HOLD on cascade_risk=True
# ---------------------------------------------------------------------------

def test_strategy_hold_on_cascade_risk():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=30.0)  # RSI would normally trigger BUY

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=900_000, short_liq=100_000,
                                             cascade_risk=True)):
        signal = strategy.generate(df)

    assert signal.action == Action.HOLD


# ---------------------------------------------------------------------------
# 8. HOLD on neutral liq_ratio ≈ 0.5
# ---------------------------------------------------------------------------

def test_strategy_hold_neutral():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=50.0)

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=500_000, short_liq=500_000)):
        signal = strategy.generate(df)

    assert signal.action == Action.HOLD


# ---------------------------------------------------------------------------
# 9. reasoning contains liq data
# ---------------------------------------------------------------------------

def test_reasoning_contains_liq_data():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=30.0)

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=900_000, short_liq=100_000)):
        signal = strategy.generate(df)

    assert "long_liq" in signal.reasoning


# ---------------------------------------------------------------------------
# 10. STRATEGY_REGISTRY contains liquidation_cascade
# ---------------------------------------------------------------------------

def test_registry_contains_liquidation_cascade():
    from src.orchestrator import STRATEGY_REGISTRY
    assert "liquidation_cascade" in STRATEGY_REGISTRY
    assert STRATEGY_REGISTRY["liquidation_cascade"] is LiquidationCascadeStrategy


# ---------------------------------------------------------------------------
# 11. BUY MEDIUM when only liq_ratio > 0.75 but RSI not oversold
# ---------------------------------------------------------------------------

def test_strategy_buy_medium_when_rsi_not_oversold():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=55.0)  # not < 35

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=900_000, short_liq=100_000)):
        signal = strategy.generate(df)

    assert signal.action == Action.BUY
    assert signal.confidence == Confidence.MEDIUM


# ---------------------------------------------------------------------------
# 12. SELL MEDIUM when only liq_ratio < 0.25 but RSI not overbought
# ---------------------------------------------------------------------------

def test_strategy_sell_medium_when_rsi_not_overbought():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=50.0)  # not > 65

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=100_000, short_liq=900_000)):
        signal = strategy.generate(df)

    assert signal.action == Action.SELL
    assert signal.confidence == Confidence.MEDIUM


# ---------------------------------------------------------------------------
# 13. get_recent returns [] on HTTP error (no exception propagation)
# ---------------------------------------------------------------------------

def test_get_recent_returns_empty_on_error():
    fetcher = LiquidationFetcher(symbol="BTC/USDT")
    with patch("src.data.liquidation_feed._requests") as mock_req:
        mock_req.get.side_effect = Exception("network error")
        result = fetcher.get_recent()
    assert result == []


# ---------------------------------------------------------------------------
# 14. mock factory produces correct liq_ratio
# ---------------------------------------------------------------------------

def test_mock_factory_ratio():
    fetcher = LiquidationFetcher.mock(long_liq=750_000, short_liq=250_000)
    p = fetcher.compute_pressure()
    assert abs(p.liq_ratio - 0.75) < 0.01
