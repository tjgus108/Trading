"""
G2. GEX Signal + CME Basis Spread 전략 테스트 (12개 이상).
"""

import unittest.mock as mock
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


# ---------------------------------------------------------------------------
# 9. GEXFeed — 재시도 및 fallback 테스트 (Cycle 6 패턴) — mock 최적화
# ---------------------------------------------------------------------------

def test_gex_fallback_after_failure():
    """GEX API 실패 후 fallback(이전 성공) 데이터 반환."""
    feed = GEXFeed()
    feed._last_successful = {"net_gex": 1.5e9, "positive": True, "score": 1.5}
    
    # mock으로 API 호출 제거 (빠른 실행)
    with mock.patch.object(feed, '_fetch_gex_with_retry', return_value=None):
        result = feed.get_gex("BTC")
        assert result["net_gex"] == 1.5e9
        assert result["positive"] is True


def test_gex_neutral_without_fallback():
    """GEX API 실패 + fallback 없음 → 중립 데이터 반환."""
    feed = GEXFeed()
    assert feed._last_successful is None
    
    # mock으로 API 호출 제거 (빠른 실행)
    with mock.patch.object(feed, '_fetch_gex_with_retry', return_value=None):
        result = feed.get_gex("INVALID_SYMBOL")
        assert result["net_gex"] == 0.0
        assert result["score"] == 0.0


def test_gex_max_retries_parameter():
    """GEXFeed max_retries 파라미터 설정 확인."""
    feed = GEXFeed(max_retries=3)
    assert feed.max_retries == 3


# ---------------------------------------------------------------------------
# 10. CMEBasisFeed — 재시도 및 fallback 테스트 (Cycle 6 패턴) — mock 최적화
# ---------------------------------------------------------------------------

def test_cme_fallback_after_failure():
    """CME Basis API 실패 후 fallback(이전 성공) 데이터 반환."""
    feed = CMEBasisFeed()
    feed._last_successful = {"basis_pct": 0.82, "basis_annual": 10.0, "score": 0.0}
    
    # mock으로 API 호출 제거 (빠른 실행)
    with mock.patch.object(feed, '_fetch_basis_with_retry', return_value=None):
        result = feed.get_basis("BTCUSDT")
        assert abs(result["basis_annual"] - 10.0) < 1e-6


def test_cme_neutral_without_fallback():
    """CME Basis API 실패 + fallback 없음 → 중립 데이터 반환."""
    feed = CMEBasisFeed()
    assert feed._last_successful is None
    
    # mock으로 API 호출 제거 (빠른 실행)
    with mock.patch.object(feed, '_fetch_basis_with_retry', return_value=None):
        result = feed.get_basis("INVALID_SYMBOL")
        assert result["basis_pct"] == 0.0
        assert result["basis_annual"] == 0.0


def test_cme_max_retries_parameter():
    """CMEBasisFeed max_retries 파라미터 설정 확인."""
    feed = CMEBasisFeed(max_retries=1)
    assert feed.max_retries == 1


# ---------------------------------------------------------------------------
# 11. Boundary conditions: Empty/malformed responses
# ---------------------------------------------------------------------------

def test_gex_parse_empty_result():
    """GEX 응답이 빈 result[] → net_gex=0, score=0."""
    feed = GEXFeed()
    data = {"result": []}
    result = feed._parse_gex(data)
    assert result["net_gex"] == 0.0
    assert result["score"] == 0.0
    assert result["positive"] is True


def test_gex_parse_missing_result_key():
    """GEX 응답에 'result' 키 없음 → net_gex=0, score=0."""
    feed = GEXFeed()
    data = {}  # no 'result' key
    result = feed._parse_gex(data)
    assert result["net_gex"] == 0.0
    assert result["score"] == 0.0


def test_cme_parse_zero_index_price():
    """CME index_price=0 → None 반환 (division guard)."""
    feed = CMEBasisFeed()
    data = {"markPrice": "50000.0", "indexPrice": "0.0"}
    result = feed._parse_basis(data)
    assert result is None


def test_cme_parse_missing_keys():
    """CME 응답에 markPrice/indexPrice 없음 → 0.0으로 처리."""
    feed = CMEBasisFeed()
    data = {}  # missing both keys
    result = feed._parse_basis(data)
    assert result is None  # index_price 기본값 0.0


def test_gex_parse_items_with_zero_values():
    """GEX 아이템들이 gamma/oi/spot=0 → 모두 skip, net_gex=0."""
    feed = GEXFeed()
    data = {
        "result": [
            {"instrument_name": "BTC-C", "gamma": 0.0, "open_interest": 100.0, "mark_price": 50000.0},
            {"instrument_name": "BTC-P", "gamma": 0.001, "open_interest": 0.0, "mark_price": 50000.0},
            {"instrument_name": "BTC-C", "gamma": 0.001, "open_interest": 100.0, "mark_price": 0.0},
        ]
    }
    result = feed._parse_gex(data)
    assert result["net_gex"] == 0.0
    assert result["score"] == 0.0
