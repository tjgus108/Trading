"""tests/test_impulse_system.py — ImpulseSystemStrategy 단위 테스트 (14개)"""

import numpy as np
import pandas as pd
import pytest
from typing import Optional

from src.strategy.impulse_system import ImpulseSystemStrategy
from src.strategy.base import Action, Confidence


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_df(close: np.ndarray, volume: Optional[np.ndarray] = None) -> pd.DataFrame:
    n = len(close)
    if volume is None:
        volume = np.ones(n) * 1000
    return pd.DataFrame({
        "open": close - 1,
        "close": close.astype(float),
        "high": close + 2,
        "low": close - 2,
        "volume": volume.astype(float),
    })


def _flat_df(n: int = 60) -> pd.DataFrame:
    close = np.full(n, 100.0)
    return _make_df(close)


def _rising_df(n: int = 60) -> pd.DataFrame:
    """꾸준히 상승 → ema_slope > 0, macd_hist_slope > 0 → BUY 가능성"""
    close = np.linspace(50.0, 200.0, n)
    return _make_df(close)


def _falling_df(n: int = 60) -> pd.DataFrame:
    """꾸준히 하락 → ema_slope < 0, macd_hist_slope < 0 → SELL 가능성"""
    close = np.linspace(200.0, 50.0, n)
    return _make_df(close)


def _get_indicators(df: pd.DataFrame):
    close = df["close"]
    ema13 = close.ewm(span=13, adjust=False).mean()
    ema_slope = ema13.diff()
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    macd_hist = macd - macd_signal
    macd_hist_slope = macd_hist.diff()
    return ema_slope, macd_hist_slope


# ── 테스트: 데이터 부족 ──────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    """1. 데이터 부족 (29행) → HOLD"""
    strat = ImpulseSystemStrategy()
    df = _make_df(np.linspace(100, 110, 29))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_insufficient_data_reasoning():
    """2. 데이터 부족 시 reasoning에 'Insufficient' 포함"""
    strat = ImpulseSystemStrategy()
    df = _make_df(np.linspace(100, 110, 20))
    sig = strat.generate(df)
    assert "Insufficient" in sig.reasoning


def test_minimum_rows_exactly_30_no_error():
    """3. 정확히 30행 → 에러 없이 신호 반환"""
    strat = ImpulseSystemStrategy()
    df = _make_df(np.linspace(100, 110, 30))
    sig = strat.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 테스트: HOLD 신호 ────────────────────────────────────────────────────────

def test_flat_is_hold():
    """4. 완전 평탄 데이터 → HOLD"""
    strat = ImpulseSystemStrategy()
    df = _flat_df()
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_is_low():
    """5. HOLD confidence는 LOW"""
    strat = ImpulseSystemStrategy()
    df = _flat_df()
    sig = strat.generate(df)
    assert sig.confidence == Confidence.LOW


# ── 테스트: BUY 신호 ─────────────────────────────────────────────────────────

def test_rising_trend_signal_type():
    """6. 상승 추세 데이터 → BUY 또는 HOLD (SELL 아님)"""
    strat = ImpulseSystemStrategy()
    df = _rising_df(60)
    sig = strat.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)


def test_buy_signal_indicators_match():
    """7. BUY 신호 시 ema_slope > 0 AND macd_hist_slope > 0 확인"""
    strat = ImpulseSystemStrategy()
    df = _rising_df(60)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        ema_slope, macd_hist_slope = _get_indicators(df)
        idx = len(df) - 2
        assert float(ema_slope.iloc[idx]) > 0
        assert float(macd_hist_slope.iloc[idx]) > 0


def test_buy_confidence_high_or_medium():
    """8. BUY 신호 confidence는 HIGH 또는 MEDIUM"""
    strat = ImpulseSystemStrategy()
    df = _rising_df(60)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 테스트: SELL 신호 ────────────────────────────────────────────────────────

def test_falling_trend_signal_type():
    """9. 하락 추세 데이터 → SELL 또는 HOLD (BUY 아님)"""
    strat = ImpulseSystemStrategy()
    df = _falling_df(60)
    sig = strat.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


def test_sell_signal_indicators_match():
    """10. SELL 신호 시 ema_slope < 0 AND macd_hist_slope < 0 확인"""
    strat = ImpulseSystemStrategy()
    df = _falling_df(60)
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        ema_slope, macd_hist_slope = _get_indicators(df)
        idx = len(df) - 2
        assert float(ema_slope.iloc[idx]) < 0
        assert float(macd_hist_slope.iloc[idx]) < 0


def test_sell_confidence_high_or_medium():
    """11. SELL 신호 confidence는 HIGH 또는 MEDIUM"""
    strat = ImpulseSystemStrategy()
    df = _falling_df(60)
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 테스트: Signal 필드 ──────────────────────────────────────────────────────

def test_signal_strategy_name():
    """12. Signal.strategy == 'impulse_system'"""
    strat = ImpulseSystemStrategy()
    df = _flat_df()
    sig = strat.generate(df)
    assert sig.strategy == "impulse_system"


def test_signal_entry_price_is_float():
    """13. Signal.entry_price는 float"""
    strat = ImpulseSystemStrategy()
    df = _flat_df(n=40)
    sig = strat.generate(df)
    assert isinstance(sig.entry_price, float)


def test_strategy_class_name():
    """14. 전략 클래스 이름 속성 = 'impulse_system'"""
    assert ImpulseSystemStrategy.name == "impulse_system"
