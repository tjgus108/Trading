"""
G2. GEX Signal + CME Basis Spread 전략 테스트 (12개 이상).
"""

import numpy as np
import pandas as pd
import pytest

from src.data.options_feed import CMEBasisFeed, GEXFeed
from src.strategy.base import Action, Confidence
from src.strategy.cme_basis_strategy import CMEBasisStrategy
from src.strategy.gex_strategy import GEXStrategy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df(
    close: float = 50000.0,
    rsi14: float = 50.0,
    ema20=None,
    n: int = 10,
) -> pd.DataFrame:
    """최소한의 DataFrame 생성 (인덱스 -2가 'last' 캔들)."""
    if ema20 is None:
        ema20 = close
    rows = [{"close": close, "rsi14": rsi14, "ema20": ema20}] * n
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 1. Strategy name
# ---------------------------------------------------------------------------

def test_gex_strategy_name():
    assert GEXStrategy().name == "gex_signal"


def test_cme_strategy_name():
    assert CMEBasisStrategy().name == "cme_basis"


# ---------------------------------------------------------------------------
# 2. GEXStrategy — Positive GEX (mean-revert)
# ---------------------------------------------------------------------------

def test_gex_positive_rsi_overbought_sell():
    """Positive GEX + RSI>65 → SELL."""
    feed = GEXFeed.mock(net_gex=2e9, positive=True)
    strategy = GEXStrategy(feed=feed)
    df = _make_df(rsi14=70.0)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


def test_gex_positive_rsi_oversold_buy():
    """Positive GEX + RSI<35 → BUY."""
    feed = GEXFeed.mock(net_gex=2e9, positive=True)
    strategy = GEXStrategy(feed=feed)
    df = _make_df(rsi14=30.0)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ---------------------------------------------------------------------------
# 3. GEXStrategy — Negative GEX (trend-following)
# ---------------------------------------------------------------------------

def test_gex_negative_trending_buy():
    """Negative GEX + close > EMA20 → BUY."""
    feed = GEXFeed.mock(net_gex=2e9, positive=False)
    strategy = GEXStrategy(feed=feed)
    df = _make_df(close=52000.0, ema20=50000.0)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


def test_gex_negative_trending_sell():
    """Negative GEX + close < EMA20 → SELL."""
    feed = GEXFeed.mock(net_gex=2e9, positive=False)
    strategy = GEXStrategy(feed=feed)
    df = _make_df(close=48000.0, ema20=50000.0)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ---------------------------------------------------------------------------
# 4. GEXStrategy — 데이터 없을 때 HOLD
# ---------------------------------------------------------------------------

def test_gex_no_data_hold():
    """GEX 조회 실패(net_gex=0, score=0) → HOLD."""
    # GEXFeed 기본 실패 반환값: {"net_gex": 0.0, "positive": True, "score": 0.0}
    feed = GEXFeed.mock(net_gex=0.0, positive=True)
    # mock()에서 net_gex=0이면 score=0 → HOLD 분기
    strategy = GEXStrategy(feed=feed)
    df = _make_df()
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ---------------------------------------------------------------------------
# 5. CMEBasisStrategy
# ---------------------------------------------------------------------------

def test_cme_high_basis_buy():
    """basis_annual=25% → BUY, confidence=HIGH."""
    feed = CMEBasisFeed.mock(basis_annual=25.0)
    strategy = CMEBasisStrategy(feed=feed)
    df = _make_df()
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_cme_low_basis_sell():
    """basis_annual=1% → SELL."""
    feed = CMEBasisFeed.mock(basis_annual=1.0)
    strategy = CMEBasisStrategy(feed=feed)
    df = _make_df()
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


def test_cme_neutral_hold():
    """basis_annual=8% → HOLD."""
    feed = CMEBasisFeed.mock(basis_annual=8.0)
    strategy = CMEBasisStrategy(feed=feed)
    df = _make_df()
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ---------------------------------------------------------------------------
# 6. CMEBasisFeed.mock() 반환값 확인
# ---------------------------------------------------------------------------

def test_cme_mock_feed():
    """mock(basis_annual=15.0) → get_basis()가 해당 basis_annual 반환."""
    feed = CMEBasisFeed.mock(basis_annual=15.0)
    result = feed.get_basis()
    assert abs(result["basis_annual"] - 15.0) < 1e-6


def test_gex_mock_feed():
    """mock(net_gex=3e9, positive=True) → get_gex()가 positive=True 반환."""
    feed = GEXFeed.mock(net_gex=3e9, positive=True)
    result = feed.get_gex()
    assert result["positive"] is True
    assert result["net_gex"] > 0


# ---------------------------------------------------------------------------
# 7. STRATEGY_REGISTRY 등록 확인
# ---------------------------------------------------------------------------

def test_gex_registry():
    """STRATEGY_REGISTRY에 gex_signal 등록 확인."""
    from src.orchestrator import STRATEGY_REGISTRY
    assert "gex_signal" in STRATEGY_REGISTRY
    assert STRATEGY_REGISTRY["gex_signal"] is GEXStrategy


def test_cme_registry():
    """STRATEGY_REGISTRY에 cme_basis 등록 확인."""
    from src.orchestrator import STRATEGY_REGISTRY
    assert "cme_basis" in STRATEGY_REGISTRY
    assert STRATEGY_REGISTRY["cme_basis"] is CMEBasisStrategy


# ---------------------------------------------------------------------------
# 8. CMEBasisStrategy confidence levels
# ---------------------------------------------------------------------------

def test_cme_confidence_medium():
    """|basis_annual|=12% → MEDIUM confidence."""
    feed = CMEBasisFeed.mock(basis_annual=12.0)
    strategy = CMEBasisStrategy(feed=feed)
    df = _make_df()
    sig = strategy.generate(df)
    assert sig.confidence == Confidence.MEDIUM


def test_cme_confidence_low():
    """|basis_annual|=6% → LOW confidence (HOLD 구간)."""
    feed = CMEBasisFeed.mock(basis_annual=6.0)
    strategy = CMEBasisStrategy(feed=feed)
    df = _make_df()
    sig = strategy.generate(df)
    assert sig.confidence == Confidence.LOW
