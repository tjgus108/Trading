"""
PriceDeviationStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_deviation import PriceDeviationStrategy
from src.strategy.base import Action, Confidence


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n: int = 35, close_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    df = pd.DataFrame({
        "open":   [100.0] * n,
        "high":   [105.0] * n,
        "low":    [95.0]  * n,
        "close":  close_values,
        "volume": [1000.0] * n,
    })
    return df


def _make_buy_df(n: int = 40) -> pd.DataFrame:
    """
    iloc[-2]가 강한 BUY 신호 (z < -1.5)를 만드는 DataFrame.
    앞 n-2 봉은 base=100, [-2]봉만 크게 낮춤.
    """
    closes = [100.0] * n
    closes[-2] = 60.0   # 크게 낮춰 deviation 음수 극대화
    closes[-1] = 100.0
    return _make_df(n=n, close_values=closes)


def _make_sell_df(n: int = 40) -> pd.DataFrame:
    """iloc[-2]가 강한 SELL 신호 (z > 1.5)를 만드는 DataFrame."""
    closes = [100.0] * n
    closes[-2] = 140.0
    closes[-1] = 100.0
    return _make_df(n=n, close_values=closes)


# ── 인스턴스 / 이름 ────────────────────────────────────────────────────────────

def test_strategy_name():
    assert PriceDeviationStrategy().name == "price_deviation"


def test_strategy_instantiable():
    assert PriceDeviationStrategy() is not None


# ── 데이터 부족 ───────────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = PriceDeviationStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows_no_crash():
    s = PriceDeviationStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


# ── BUY 시그널 ────────────────────────────────────────────────────────────────

def test_buy_signal_generated():
    s = PriceDeviationStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_confidence_not_low():
    s = PriceDeviationStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_buy_high_confidence():
    """|z| > 2.0 → HIGH confidence"""
    s = PriceDeviationStrategy()
    df = _make_buy_df(n=40)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── SELL 시그널 ───────────────────────────────────────────────────────────────

def test_sell_signal_generated():
    s = PriceDeviationStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_confidence_not_low():
    s = PriceDeviationStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_sell_high_confidence():
    s = PriceDeviationStrategy()
    df = _make_sell_df(n=40)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── HOLD ──────────────────────────────────────────────────────────────────────

def test_hold_when_neutral():
    s = PriceDeviationStrategy()
    df = _make_df(n=35)  # 전부 100 → deviation=0, z=0
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_is_low():
    s = PriceDeviationStrategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW


# ── Signal 필드 검증 ──────────────────────────────────────────────────────────

def test_entry_price_equals_last_close():
    s = PriceDeviationStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_signal_strategy_field():
    s = PriceDeviationStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.strategy == "price_deviation"


def test_reasoning_contains_z():
    s = PriceDeviationStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert "z=" in sig.reasoning
