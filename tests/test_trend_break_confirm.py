"""TrendBreakConfirmStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.trend_break_confirm import TrendBreakConfirmStrategy


def _make_df(n: int = 60, close_prices=None, volume_mul=1.0) -> pd.DataFrame:
    if close_prices is not None:
        close = np.array(close_prices, dtype=float)
        n = len(close)
    else:
        close = np.linspace(100, 110, n)
    high = close * 1.005
    low = close * 0.995
    volume = np.ones(n) * 1000 * volume_mul
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


def _make_bull_breakout_df() -> pd.DataFrame:
    """EMA20 상향 돌파 + EMA20 > EMA50 + 거래량 확인 조건 생성."""
    n = 60
    # 먼저 하락해서 EMA 아래로 내리다가 마지막에 강하게 상승
    close = np.concatenate([
        np.linspace(105, 90, 40),   # 하락: EMA 아래로
        np.linspace(90, 120, 20),   # 급상승: EMA20 돌파
    ])
    high = close * 1.005
    low = close * 0.995
    # 마지막 봉들의 거래량을 높게 설정
    volume = np.ones(n) * 500
    volume[-10:] = 3000  # 마지막 10봉 거래량 급증
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


def _make_bear_breakout_df() -> pd.DataFrame:
    """EMA20 하향 돌파 + EMA20 < EMA50 + 거래량 확인 조건 생성."""
    n = 60
    close = np.concatenate([
        np.linspace(90, 110, 40),   # 상승: EMA 위로
        np.linspace(110, 80, 20),   # 급하락: EMA20 하향 돌파
    ])
    high = close * 1.005
    low = close * 0.995
    volume = np.ones(n) * 500
    volume[-10:] = 3000
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────────

def test_strategy_name():
    s = TrendBreakConfirmStrategy()
    assert s.name == "trend_break_confirm"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────────

def test_instantiation():
    s = TrendBreakConfirmStrategy()
    assert isinstance(s, TrendBreakConfirmStrategy)


# ── 3. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = TrendBreakConfirmStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ──────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = TrendBreakConfirmStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = TrendBreakConfirmStrategy()
    df = _make_df(n=5)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning or "minimum" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = TrendBreakConfirmStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성 ──────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = TrendBreakConfirmStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "trend_break_confirm"
    assert sig.entry_price >= 0
    assert sig.reasoning != ""
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 8. 최소 행수(25)에서 동작 ─────────────────────────────────────────────────

def test_minimum_rows_works():
    s = TrendBreakConfirmStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 9. entry_price > 0 ──────────────────────────────────────────────────────

def test_entry_price_positive():
    s = TrendBreakConfirmStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.entry_price > 0


# ── 10. 상승 추세 데이터에서 signal ───────────────────────────────────────────

def test_bull_breakout_signal():
    s = TrendBreakConfirmStrategy()
    df = _make_bull_breakout_df()
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    # BUY 또는 HOLD (조건 충족 여부에 따라)
    assert sig.action in (Action.BUY, Action.HOLD)


# ── 11. 하락 추세 데이터에서 signal ───────────────────────────────────────────

def test_bear_breakout_signal():
    s = TrendBreakConfirmStrategy()
    df = _make_bear_breakout_df()
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.SELL, Action.HOLD)


# ── 12. confidence는 HIGH or MEDIUM ──────────────────────────────────────────

def test_confidence_valid_values():
    s = TrendBreakConfirmStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 13. BUY 시 invalidation에 EMA20 언급 ─────────────────────────────────────

def test_buy_invalidation_mentions_ema20():
    s = TrendBreakConfirmStrategy()
    df = _make_bull_breakout_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "EMA20" in sig.invalidation


# ── 14. strategy 필드 값 확인 ────────────────────────────────────────────────

def test_strategy_field_value():
    s = TrendBreakConfirmStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "trend_break_confirm"


# ── 15. 24행 입력 → HOLD (MIN_ROWS 경계) ─────────────────────────────────────

def test_boundary_below_min_rows():
    s = TrendBreakConfirmStrategy()
    df = _make_df(n=24)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 16. HOLD reasoning 키워드 확인 ───────────────────────────────────────────

def test_hold_reasoning_keywords():
    s = TrendBreakConfirmStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    if sig.action == Action.HOLD:
        assert sig.reasoning != ""
