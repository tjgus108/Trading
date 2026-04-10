"""SpreadMomentumStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.spread_momentum import SpreadMomentumStrategy


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


def _make_bullish_df(n: int = 60) -> pd.DataFrame:
    """강한 상승 추세 → ema_fast > ema_slow, spread 확대."""
    close = np.concatenate([
        np.linspace(100, 100, n // 2),   # 횡보
        np.linspace(100, 130, n - n // 2),  # 가파른 상승
    ])
    high = close * 1.005
    low = close * 0.995
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


def _make_bearish_df(n: int = 60) -> pd.DataFrame:
    """강한 하락 추세 → ema_fast < ema_slow, spread 확대."""
    close = np.concatenate([
        np.linspace(130, 130, n // 2),
        np.linspace(130, 100, n - n // 2),
    ])
    high = close * 1.005
    low = close * 0.995
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────────

def test_strategy_name():
    s = SpreadMomentumStrategy()
    assert s.name == "spread_momentum"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────────

def test_instantiation():
    s = SpreadMomentumStrategy()
    assert isinstance(s, SpreadMomentumStrategy)


# ── 3. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = SpreadMomentumStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ──────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = SpreadMomentumStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = SpreadMomentumStrategy()
    df = _make_df(n=5)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = SpreadMomentumStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성 ──────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = SpreadMomentumStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "spread_momentum"
    assert sig.entry_price > 0
    assert sig.reasoning != ""
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 8. 상승 추세 → BUY 가능성 ────────────────────────────────────────────────

def test_bullish_trend_may_produce_buy():
    s = SpreadMomentumStrategy()
    df = _make_bullish_df(n=80)
    sig = s.generate(df)
    # 강한 상승이면 BUY가 기대되나 HOLD도 허용
    assert sig.action in (Action.BUY, Action.HOLD)


# ── 9. 하락 추세 → SELL 가능성 ───────────────────────────────────────────────

def test_bearish_trend_may_produce_sell():
    s = SpreadMomentumStrategy()
    df = _make_bearish_df(n=80)
    sig = s.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


# ── 10. BUY 신호 시 reasoning 키워드 ─────────────────────────────────────────

def test_buy_reasoning_keyword():
    s = SpreadMomentumStrategy()
    df = _make_bullish_df(n=80)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "spread" in sig.reasoning.lower() or "bullish" in sig.reasoning.lower()


# ── 11. SELL 신호 시 reasoning 키워드 ────────────────────────────────────────

def test_sell_reasoning_keyword():
    s = SpreadMomentumStrategy()
    df = _make_bearish_df(n=80)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "spread" in sig.reasoning.lower() or "bearish" in sig.reasoning.lower()


# ── 12. entry_price > 0 ──────────────────────────────────────────────────────

def test_entry_price_positive():
    s = SpreadMomentumStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.entry_price > 0


# ── 13. strategy 필드 값 확인 ────────────────────────────────────────────────

def test_strategy_field_value():
    s = SpreadMomentumStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "spread_momentum"


# ── 14. 최소 행 수(25)에서 동작 ─────────────────────────────────────────────

def test_minimum_rows():
    s = SpreadMomentumStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 15. confidence 값 유효 범위 ──────────────────────────────────────────────

def test_confidence_valid_range():
    s = SpreadMomentumStrategy()
    df = _make_bullish_df(n=80)
    sig = s.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 16. 횡보 구간 → HOLD 경향 ───────────────────────────────────────────────

def test_flat_market_hold():
    s = SpreadMomentumStrategy()
    # 가격이 거의 변동 없음
    close = np.ones(60) * 100.0
    df = _make_df(close_prices=close)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
