"""TrendExhaustionSignalStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.trend_exhaustion_signal import TrendExhaustionSignalStrategy


def _make_df(n: int = 60, close_prices=None, high_prices=None, low_prices=None) -> pd.DataFrame:
    if close_prices is not None:
        close = np.array(close_prices, dtype=float)
        n = len(close)
    else:
        close = np.linspace(100, 110, n)
    high = np.array(high_prices, dtype=float) if high_prices is not None else close * 1.005
    low = np.array(low_prices, dtype=float) if low_prices is not None else close * 0.995
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


def _make_oversold_df(n: int = 60) -> pd.DataFrame:
    """20봉 중 상승봉이 4개 이하 + 큰 낙폭 후 반등."""
    # 계속 하락하다가 마지막 2봉에서 반등
    close = np.linspace(130, 90, n)
    # 마지막 2봉 반등
    close[-2] = close[-3] + 3.0
    close[-1] = close[-2] + 1.0
    high = close * 1.01
    low = close * 0.95  # 넓은 고저폭 → atr 크게, stretch 크게
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


def _make_overbought_df(n: int = 60) -> pd.DataFrame:
    """20봉 중 상승봉이 16개 이상 + 큰 상승 후 반락."""
    close = np.linspace(90, 130, n)
    # 마지막 2봉 반락
    close[-2] = close[-3] - 3.0
    close[-1] = close[-2] - 1.0
    high = close * 1.05
    low = close * 0.99
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────────

def test_strategy_name():
    s = TrendExhaustionSignalStrategy()
    assert s.name == "trend_exhaustion_signal"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────────

def test_instantiation():
    s = TrendExhaustionSignalStrategy()
    assert isinstance(s, TrendExhaustionSignalStrategy)


# ── 3. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = TrendExhaustionSignalStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ──────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = TrendExhaustionSignalStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = TrendExhaustionSignalStrategy()
    df = _make_df(n=5)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = TrendExhaustionSignalStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성 ──────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = TrendExhaustionSignalStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "trend_exhaustion_signal"
    assert sig.entry_price > 0
    assert sig.reasoning != ""
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 8. 과매도 + 반등 → BUY 가능성 ────────────────────────────────────────────

def test_oversold_may_produce_buy():
    s = TrendExhaustionSignalStrategy()
    df = _make_oversold_df(n=60)
    sig = s.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)


# ── 9. 과매수 + 반락 → SELL 가능성 ──────────────────────────────────────────

def test_overbought_may_produce_sell():
    s = TrendExhaustionSignalStrategy()
    df = _make_overbought_df(n=60)
    sig = s.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


# ── 10. BUY 신호 시 reasoning 키워드 ─────────────────────────────────────────

def test_buy_reasoning_keyword():
    s = TrendExhaustionSignalStrategy()
    df = _make_oversold_df(n=60)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "exhaustion" in sig.reasoning.lower() or "oversold" in sig.reasoning.lower()


# ── 11. SELL 신호 시 reasoning 키워드 ────────────────────────────────────────

def test_sell_reasoning_keyword():
    s = TrendExhaustionSignalStrategy()
    df = _make_overbought_df(n=60)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "exhaustion" in sig.reasoning.lower() or "overbought" in sig.reasoning.lower()


# ── 12. entry_price > 0 ──────────────────────────────────────────────────────

def test_entry_price_positive():
    s = TrendExhaustionSignalStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.entry_price > 0


# ── 13. strategy 필드 값 확인 ────────────────────────────────────────────────

def test_strategy_field_value():
    s = TrendExhaustionSignalStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "trend_exhaustion_signal"


# ── 14. 최소 행 수(25)에서 동작 ─────────────────────────────────────────────

def test_minimum_rows():
    s = TrendExhaustionSignalStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 15. confidence 값 유효 범위 ──────────────────────────────────────────────

def test_confidence_valid_range():
    s = TrendExhaustionSignalStrategy()
    df = _make_overbought_df(n=60)
    sig = s.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 16. 중립 시장 → HOLD ─────────────────────────────────────────────────────

def test_neutral_market_hold():
    s = TrendExhaustionSignalStrategy()
    # 가격이 거의 변동 없음 → trend_bars ≈ 50%, stretch 작음
    close = np.ones(60) * 100.0
    df = _make_df(close_prices=close)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
