"""tests/test_price_pattern_recog.py — PricePatternRecogStrategy 단위 테스트."""

import pandas as pd
import pytest

from src.strategy.price_pattern_recog import PricePatternRecogStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(rows):
    n = len(rows)
    data = {
        "open":   [r[0] for r in rows],
        "high":   [r[1] for r in rows],
        "low":    [r[2] for r in rows],
        "close":  [r[3] for r in rows],
        "volume": [1000.0] * n,
    }
    return pd.DataFrame(data)


def _neutral(n=10):
    """Flat candles with range giving body_ratio ~0.5 (border case avoidance)."""
    # body=1, range=4 → ratio=0.25 < 0.3 (small candle suitable for doji)
    return [(100.0, 102.0, 98.0, 101.0)] * n


def _big_bear():
    """Big bearish candle: body=8, range=8 → ratio=1.0 > 0.5."""
    return (110.0, 110.0, 102.0, 102.0)


def _big_bull():
    """Big bullish candle: body=8, range=8 → ratio=1.0 > 0.5."""
    return (102.0, 110.0, 102.0, 110.0)


def _doji():
    """Small body candle: body=0.2, range=4.0 → ratio=0.05 < 0.3."""
    return (104.0, 106.0, 102.0, 104.2)


def _morning_star_rows():
    """
    idx-2: big bear (110→102, midpoint=106)
    idx-1: doji
    idx: big bull closing above midpoint (c0=108 > 106)
    Trailing row at end so idx = len-2 points to big bull.
    """
    rows = list(_neutral(7))
    rows.append(_big_bear())    # idx-2
    rows.append(_doji())        # idx-1
    rows.append((102.0, 110.0, 102.0, 108.0))  # idx: big bull, c0=108 > midpoint(106)
    rows.append((108.0, 109.0, 107.0, 108.5))  # trailing (not used)
    return rows


def _evening_star_rows():
    """
    idx-2: big bull (102→110, midpoint=106)
    idx-1: doji
    idx: big bear closing below midpoint (c0=104 < 106)
    """
    rows = list(_neutral(7))
    rows.append(_big_bull())    # idx-2: 102→110
    rows.append(_doji())        # idx-1
    rows.append((110.0, 110.0, 102.0, 104.0))  # idx: big bear, c0=104 < midpoint(106)
    rows.append((104.0, 105.0, 103.0, 104.5))  # trailing
    return rows


def _three_white_rows():
    """Three successive strong bullish candles each closing higher."""
    rows = list(_neutral(7))
    # idx-3 (c2_prev): close=100
    rows.append((99.0, 101.5, 99.0, 100.0))   # c2_prev
    # idx-2: bull, body=4, range=4 (ratio=1.0), close=104 > c2_prev=100
    rows.append((100.0, 104.0, 100.0, 104.0))
    # idx-1: bull, body=4, range=4, close=108 > 104
    rows.append((104.0, 108.0, 104.0, 108.0))
    # idx: bull, body=4, range=4, close=112 > 108
    rows.append((108.0, 112.0, 108.0, 112.0))
    rows.append((112.0, 113.0, 111.0, 112.5))  # trailing
    return rows


def _three_black_rows():
    """Three successive strong bearish candles each closing lower."""
    rows = list(_neutral(7))
    # idx-3 (c2_prev): close=112
    rows.append((113.0, 113.0, 111.5, 112.0))  # c2_prev
    # idx-2: bear, body=4, range=4, close=108 < c2_prev=112
    rows.append((112.0, 112.0, 108.0, 108.0))
    # idx-1: bear, body=4, range=4, close=104 < 108
    rows.append((108.0, 108.0, 104.0, 104.0))
    # idx: bear, body=4, range=4, close=100 < 104
    rows.append((104.0, 104.0, 100.0, 100.0))
    rows.append((100.0, 101.0, 99.0, 100.5))   # trailing
    return rows


strat = PricePatternRecogStrategy()


# 1. 전략 이름
def test_strategy_name():
    assert strat.name == "price_pattern_recog"


# 2. 인스턴스 확인
def test_instance():
    from src.strategy.base import BaseStrategy
    assert isinstance(strat, BaseStrategy)


# 3. 데이터 부족 (7행) → HOLD LOW
def test_insufficient_data_hold():
    df = _make_df(_neutral(7))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 4. None 없음 — Signal 반환
def test_signal_not_none():
    df = _make_df(_neutral(10))
    sig = strat.generate(df)
    assert sig is not None


# 5. reasoning 필드 존재
def test_reasoning_field():
    df = _make_df(_neutral(10))
    sig = strat.generate(df)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0


# 6. 패턴 없음 → HOLD
def test_no_pattern_hold():
    df = _make_df(_neutral(12))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 7. Signal 필드 완전성 (strategy, entry_price, invalidation)
def test_signal_fields():
    df = _make_df(_neutral(10))
    sig = strat.generate(df)
    assert sig.strategy == "price_pattern_recog"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.invalidation, str)


# 8. Morning Star → BUY
def test_morning_star_buy():
    df = _make_df(_morning_star_rows())
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# 9. Morning Star reasoning에 "Morning Star" 포함
def test_morning_star_reasoning():
    df = _make_df(_morning_star_rows())
    sig = strat.generate(df)
    assert "Morning Star" in sig.reasoning


# 10. Evening Star → SELL
def test_evening_star_sell():
    df = _make_df(_evening_star_rows())
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# 11. Evening Star reasoning에 "Evening Star" 포함
def test_evening_star_reasoning():
    df = _make_df(_evening_star_rows())
    sig = strat.generate(df)
    assert "Evening Star" in sig.reasoning


# 12. Three White Soldiers → BUY HIGH
def test_three_white_soldiers_buy_high():
    df = _make_df(_three_white_rows())
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# 13. Three Black Crows → SELL HIGH
def test_three_black_crows_sell_high():
    df = _make_df(_three_black_rows())
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# 14. entry_price > 0
def test_entry_price_positive():
    df = _make_df(_morning_star_rows())
    sig = strat.generate(df)
    assert sig.entry_price > 0
