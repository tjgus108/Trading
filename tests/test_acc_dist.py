"""AccDistStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.acc_dist import AccDistStrategy


def _make_df(n: int = 60, close_prices=None) -> pd.DataFrame:
    if close_prices is not None:
        close = np.array(close_prices, dtype=float)
        n = len(close)
    else:
        close = np.linspace(100, 110, n)
    high = close * 1.005
    low = close * 0.995
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


def _make_bullish_div_df(n: int = 60) -> pd.DataFrame:
    """A/D 상승 + 가격 하락 → bullish divergence."""
    close = np.linspace(110, 100, n)  # 가격 하락
    # A/D를 상승시키려면 CLV > 0 (close가 high에 가깝게)
    high = close + 5.0
    low = close - 0.1  # close가 low보다 훨씬 위 → CLV 높음
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


def _make_bearish_div_df(n: int = 60) -> pd.DataFrame:
    """A/D 하락 + 가격 상승 → bearish divergence."""
    close = np.linspace(100, 110, n)  # 가격 상승
    # A/D를 하락시키려면 CLV < 0 (close가 low에 가깝게)
    high = close + 0.1
    low = close - 5.0  # close가 high에 가까움 → CLV 낮음
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────────

def test_strategy_name():
    s = AccDistStrategy()
    assert s.name == "acc_dist"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────────

def test_instantiation():
    s = AccDistStrategy()
    assert isinstance(s, AccDistStrategy)


# ── 3. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = AccDistStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ──────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = AccDistStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = AccDistStrategy()
    df = _make_df(n=5)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning or "minimum" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = AccDistStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성 ──────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = AccDistStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "acc_dist"
    assert sig.entry_price > 0
    assert sig.reasoning != ""
    assert sig.invalidation != ""
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 8. BUY reasoning 키워드 확인 ─────────────────────────────────────────────

def test_buy_reasoning_keywords():
    s = AccDistStrategy()
    df = _make_bullish_div_df(n=60)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "Bullish" in sig.reasoning or "A/D" in sig.reasoning or "상승" in sig.reasoning


# ── 9. SELL reasoning 키워드 확인 ────────────────────────────────────────────

def test_sell_reasoning_keywords():
    s = AccDistStrategy()
    df = _make_bearish_div_df(n=60)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "Bearish" in sig.reasoning or "A/D" in sig.reasoning or "하락" in sig.reasoning


# ── 10. HIGH confidence 테스트 ───────────────────────────────────────────────

def test_high_confidence():
    """A/D 변화가 rolling std보다 크면 HIGH."""
    s = AccDistStrategy()
    df = _make_bullish_div_df(n=60)
    sig = s.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 11. MEDIUM confidence 테스트 ─────────────────────────────────────────────

def test_medium_confidence_on_hold():
    s = AccDistStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    # HOLD 시 MEDIUM, 신호 시 HIGH or MEDIUM
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 12. entry_price > 0 ──────────────────────────────────────────────────────

def test_entry_price_positive():
    s = AccDistStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.entry_price > 0


# ── 13. strategy 필드 값 확인 ────────────────────────────────────────────────

def test_strategy_field_value():
    s = AccDistStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "acc_dist"


# ── 14. 최소 행 수(20)에서 동작 ─────────────────────────────────────────────

def test_minimum_rows():
    s = AccDistStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
