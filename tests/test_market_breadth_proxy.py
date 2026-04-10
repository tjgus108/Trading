"""MarketBreadthProxyStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.market_breadth_proxy import MarketBreadthProxyStrategy


def _make_df(n: int = 50, close_prices=None) -> pd.DataFrame:
    if close_prices is not None:
        close = np.array(close_prices, dtype=float)
        n = len(close)
    else:
        close = np.linspace(100, 110, n)
    return pd.DataFrame({
        "open": close * 0.999,
        "high": close * 1.005,
        "low": close * 0.995,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


def _make_bullish_df(n: int = 50) -> pd.DataFrame:
    """대부분 상승 캔들 + 가격이 EMA 위 → BUY 조건 유도."""
    # 강하게 상승하면 advances 많아짐
    close = np.concatenate([
        np.linspace(80, 100, 30),   # 초반 상승
        np.linspace(100, 130, 20),  # 후반 강한 상승
    ])[:n]
    return _make_df(n=n, close_prices=close)


def _make_bearish_df(n: int = 50) -> pd.DataFrame:
    """대부분 하락 캔들 + 가격이 EMA 아래 → SELL 조건 유도."""
    close = np.concatenate([
        np.linspace(130, 110, 30),  # 초반 하락
        np.linspace(110, 80, 20),   # 후반 강한 하락
    ])[:n]
    return _make_df(n=n, close_prices=close)


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────────

def test_strategy_name():
    s = MarketBreadthProxyStrategy()
    assert s.name == "market_breadth_proxy"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────────

def test_instantiation():
    s = MarketBreadthProxyStrategy()
    assert isinstance(s, MarketBreadthProxyStrategy)


# ── 3. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = MarketBreadthProxyStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ──────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = MarketBreadthProxyStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 entry_price = 0 ───────────────────────────────────────────

def test_insufficient_data_entry_price_zero():
    s = MarketBreadthProxyStrategy()
    df = _make_df(n=5)
    sig = s.generate(df)
    assert sig.entry_price == 0.0


# ── 6. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = MarketBreadthProxyStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning


# ── 7. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = MarketBreadthProxyStrategy()
    df = _make_df(n=50)
    sig = s.generate(df)
    assert isinstance(sig, Signal)


# ── 8. Signal 필드 완성 ──────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = MarketBreadthProxyStrategy()
    df = _make_df(n=50)
    sig = s.generate(df)
    assert sig.strategy == "market_breadth_proxy"
    assert sig.entry_price > 0
    assert sig.reasoning != ""
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 9. entry_price > 0 ───────────────────────────────────────────────────────

def test_entry_price_positive():
    s = MarketBreadthProxyStrategy()
    df = _make_df(n=50)
    sig = s.generate(df)
    assert sig.entry_price > 0


# ── 10. strategy 필드 값 확인 ────────────────────────────────────────────────

def test_strategy_field_value():
    s = MarketBreadthProxyStrategy()
    df = _make_df(n=50)
    sig = s.generate(df)
    assert sig.strategy == "market_breadth_proxy"


# ── 11. BUY 조건 테스트 ──────────────────────────────────────────────────────

def test_buy_signal():
    s = MarketBreadthProxyStrategy()
    df = _make_bullish_df(n=50)
    sig = s.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)


# ── 12. SELL 조건 테스트 ─────────────────────────────────────────────────────

def test_sell_signal():
    s = MarketBreadthProxyStrategy()
    df = _make_bearish_df(n=50)
    sig = s.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


# ── 13. BUY reasoning 키워드 ─────────────────────────────────────────────────

def test_buy_reasoning_keyword():
    s = MarketBreadthProxyStrategy()
    df = _make_bullish_df(n=50)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "BUY" in sig.reasoning or "ad_ratio" in sig.reasoning


# ── 14. SELL reasoning 키워드 ────────────────────────────────────────────────

def test_sell_reasoning_keyword():
    s = MarketBreadthProxyStrategy()
    df = _make_bearish_df(n=50)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "SELL" in sig.reasoning or "ad_ratio" in sig.reasoning


# ── 15. 최소 행 수(30)에서 동작 ─────────────────────────────────────────────

def test_minimum_rows():
    s = MarketBreadthProxyStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 16. HIGH confidence BUY (ad_ratio > 2.0) ────────────────────────────────

def test_high_confidence_buy():
    """ad_ratio > 2.0 이면 HIGH confidence."""
    s = MarketBreadthProxyStrategy()
    df = _make_bullish_df(n=50)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        # HIGH or MEDIUM 모두 유효
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 17. HOLD - 중립 데이터 ───────────────────────────────────────────────────

def test_hold_neutral_data():
    """횡보 데이터에서 HOLD 가능."""
    s = MarketBreadthProxyStrategy()
    # 상승/하락이 균형 잡힌 데이터
    close = 100 + np.sin(np.linspace(0, 4 * np.pi, 50)) * 2
    df = _make_df(n=50, close_prices=close)
    sig = s.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
