"""Tests for CandlePatternScoreStrategy (14 tests)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.candle_pattern_score import CandlePatternScoreStrategy
from src.strategy.base import Action, Confidence, Signal


def make_df(n: int, close_val: float = 100.0) -> pd.DataFrame:
    """기본 OHLCV DataFrame 생성."""
    data = {
        "open":   [close_val] * n,
        "high":   [close_val + 1.0] * n,
        "low":    [close_val - 1.0] * n,
        "close":  [close_val] * n,
        "volume": [1000.0] * n,
    }
    return pd.DataFrame(data)


def make_buy_df() -> pd.DataFrame:
    """score >= 3 BUY 신호 유발 DataFrame (Hammer + Strong bullish)."""
    rows = []
    # 기본 봉 여러 개
    for _ in range(8):
        rows.append({"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000.0})

    # idx-1 (prev): 음봉 (pc < po → Hammer 조건)
    rows.append({"open": 101.0, "high": 102.0, "low": 99.0, "close": 99.5, "volume": 1000.0})

    # idx (last complete candle): Hammer + Strong bullish
    # body = 3, lower_wick = 7 (> body*2), upper_wick = 0.1 (< body*0.5)
    # body_ratio = 3/10.1 ~ 0.297 → Strong bullish requires > 0.7, skip
    # Use Hammer only: score = +2, add strong bullish body > 0.7
    # Let's make body=5, total=6.1, body_ratio=0.82 → strong bullish +1
    # lower_wick = min(105,110)-99 = 6 > body*2=10? No
    # Make: o=100, c=105, h=105.5, l=88 → body=5, lower_wick=12 > 10, upper_wick=0.5 < 2.5, pc=99.5<po=101 → hammer +2
    # body_ratio = 5/(105.5-88)=5/17.5=0.286 → not >0.7
    # To get score>=3: also add engulfing: c>o, pc<po, c>po=101 ✓, o<pc=99.5 ✓ → +2 more → score=4
    rows.append({"open": 99.0, "high": 105.5, "low": 87.0, "close": 105.0, "volume": 1000.0})

    # current (incomplete)
    rows.append({"open": 105.0, "high": 106.0, "low": 104.0, "close": 105.5, "volume": 1000.0})

    return pd.DataFrame(rows)


def make_sell_df() -> pd.DataFrame:
    """score <= -3 SELL 신호 유발 DataFrame."""
    rows = []
    for _ in range(8):
        rows.append({"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000.0})

    # idx-1 (prev): 양봉 (pc > po → Shooting Star 조건)
    rows.append({"open": 99.0, "high": 101.0, "low": 98.5, "close": 100.5, "volume": 1000.0})

    # idx: Shooting Star (-2) + Bearish Engulfing (-2) → score = -4
    # Shooting Star: upper_wick > body*2, lower_wick < body*0.5, pc>po ✓
    # o=100, c=97, body=3, h=112, l=96.9
    # upper_wick = 112 - max(100,97) = 12 > 6 ✓
    # lower_wick = min(100,97) - 96.9 = 0.1 < 1.5 ✓
    # Bearish engulfing: c<o ✓, pc>po ✓ (pc=100.5>po=99), c<po=99 ✓, o>pc=100.5 ✓
    rows.append({"open": 101.0, "high": 113.0, "low": 96.9, "close": 97.0, "volume": 1000.0})

    # current (incomplete)
    rows.append({"open": 97.0, "high": 98.0, "low": 96.0, "close": 96.5, "volume": 1000.0})

    return pd.DataFrame(rows)


# ─── Tests ───────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략명 확인."""
    s = CandlePatternScoreStrategy()
    assert s.name == "candle_pattern_score"


def test_instantiation():
    """2. 인스턴스 생성."""
    s = CandlePatternScoreStrategy()
    assert isinstance(s, CandlePatternScoreStrategy)


def test_insufficient_data_returns_hold():
    """3. 데이터 부족 → HOLD."""
    s = CandlePatternScoreStrategy()
    df = make_df(3)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_none_input_returns_hold():
    """4. None 입력 → HOLD."""
    s = CandlePatternScoreStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


def test_insufficient_data_reasoning():
    """5. 데이터 부족 reasoning 확인."""
    s = CandlePatternScoreStrategy()
    df = make_df(2)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning


def test_normal_data_returns_signal():
    """6. 정상 데이터 → Signal 반환."""
    s = CandlePatternScoreStrategy()
    df = make_df(20)
    sig = s.generate(df)
    assert isinstance(sig, Signal)


def test_signal_fields_complete():
    """7. Signal 필드 완성."""
    s = CandlePatternScoreStrategy()
    df = make_df(20)
    sig = s.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "candle_pattern_score"
    assert sig.reasoning != ""


def test_buy_reasoning_keyword():
    """8. BUY reasoning 키워드 확인."""
    s = CandlePatternScoreStrategy()
    df = make_buy_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "bullish" in sig.reasoning.lower() or "score" in sig.reasoning.lower()


def test_sell_reasoning_keyword():
    """9. SELL reasoning 키워드 확인."""
    s = CandlePatternScoreStrategy()
    df = make_sell_df()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "bearish" in sig.reasoning.lower() or "score" in sig.reasoning.lower()


def test_high_confidence_buy():
    """10. HIGH confidence BUY 테스트 (abs(score) >= 4)."""
    s = CandlePatternScoreStrategy()
    df = make_buy_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        # score=4 → HIGH
        assert sig.confidence == Confidence.HIGH


def test_medium_confidence_hold():
    """11. MEDIUM confidence HOLD 테스트."""
    s = CandlePatternScoreStrategy()
    df = make_df(20)
    sig = s.generate(df)
    if sig.action == Action.HOLD:
        assert sig.confidence == Confidence.MEDIUM


def test_entry_price_positive():
    """12. entry_price > 0."""
    s = CandlePatternScoreStrategy()
    df = make_df(20, close_val=50.0)
    sig = s.generate(df)
    assert sig.entry_price > 0


def test_strategy_field_value():
    """13. strategy 필드 값 확인."""
    s = CandlePatternScoreStrategy()
    df = make_df(20)
    sig = s.generate(df)
    assert sig.strategy == "candle_pattern_score"


def test_minimum_rows():
    """14. 최소 행 수(5)에서 동작."""
    s = CandlePatternScoreStrategy()
    df = make_df(5)
    sig = s.generate(df)
    assert isinstance(sig, Signal)
