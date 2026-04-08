"""
STCStrategy 테스트 (12개)
"""

import numpy as np
import pandas as pd
import pytest

import src.strategy.stc as stc_module
from src.strategy.stc import STCStrategy
from src.strategy.base import Action, Confidence


def _make_df(n: int = 100, close_val: float = 100.0) -> pd.DataFrame:
    """기본 OHLCV DataFrame 생성."""
    close = np.full(n, close_val, dtype=float)
    return pd.DataFrame({
        "open": close * 0.999,
        "high": close * 1.001,
        "low": close * 0.999,
        "close": close,
        "volume": np.full(n, 1000.0),
        "ema50": close,
        "atr14": np.full(n, 1.0),
    })


def _patch_stc(monkeypatch, values: list):
    """stc_series를 주입. values[-2]가 stc_now, values[-3]이 stc_prev."""
    n = len(values)
    stc_series = pd.Series(values)

    def fake_calc(d):
        return stc_series

    monkeypatch.setattr(stc_module, "_calc_stc", fake_calc)


@pytest.fixture
def strategy():
    return STCStrategy()


# 1. 전략 이름
def test_strategy_name(strategy):
    assert strategy.name == "stc"


# 2. BUY 신호 (STC<25, 상승 중)
def test_buy_signal(monkeypatch, strategy):
    df = _make_df(100)
    # idx = len(df)-2 = 98, idx-1 = 97
    # stc_now = series[98] = 22, stc_prev = series[97] = 18 → 상승
    values = [50.0] * 97 + [18.0, 22.0, 0.0]  # len=100, idx=98→22, idx=97→18
    _patch_stc(monkeypatch, values)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# 3. SELL 신호 (STC>75, 하락 중)
def test_sell_signal(monkeypatch, strategy):
    df = _make_df(100)
    # stc_now=80 (idx=98), stc_prev=85 (idx=97) → 하락
    values = [50.0] * 97 + [85.0, 80.0, 0.0]
    _patch_stc(monkeypatch, values)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# 4. BUY HIGH confidence (STC<10)
def test_buy_high_confidence(monkeypatch, strategy):
    df = _make_df(100)
    # stc_now=9 (idx=98), stc_prev=7 (idx=97) → 상승, <10
    values = [5.0] * 97 + [7.0, 9.0, 0.0]
    _patch_stc(monkeypatch, values)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# 5. BUY MEDIUM confidence (10<=STC<25)
def test_buy_medium_confidence(monkeypatch, strategy):
    df = _make_df(100)
    # stc_now=15 (idx=98), stc_prev=12 (idx=97) → 상승, 10<=15<25
    values = [12.0] * 97 + [12.0, 15.0, 0.0]
    _patch_stc(monkeypatch, values)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# 6. SELL HIGH confidence (STC>90)
def test_sell_high_confidence(monkeypatch, strategy):
    df = _make_df(100)
    # stc_now=92 (idx=98), stc_prev=95 (idx=97) → 하락, >90
    values = [95.0] * 97 + [95.0, 92.0, 0.0]
    _patch_stc(monkeypatch, values)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# 7. SELL MEDIUM confidence (75<STC<=90)
def test_sell_medium_confidence(monkeypatch, strategy):
    df = _make_df(100)
    # stc_now=82 (idx=98), stc_prev=85 (idx=97) → 하락, 75<82<=90
    values = [85.0] * 97 + [85.0, 82.0, 0.0]
    _patch_stc(monkeypatch, values)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# 8. STC<25이지만 하락 중 → HOLD
def test_buy_condition_but_falling_is_hold(monkeypatch, strategy):
    df = _make_df(100)
    # stc_now=18 (idx=98), stc_prev=22 (idx=97) → 하락 → HOLD
    values = [22.0] * 97 + [22.0, 18.0, 0.0]
    _patch_stc(monkeypatch, values)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# 9. 데이터 부족 → HOLD
def test_insufficient_data(strategy):
    df = _make_df(50)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 10. Signal 필드 완전성
def test_signal_fields_complete(monkeypatch, strategy):
    df = _make_df(100)
    values = [50.0] * 100
    _patch_stc(monkeypatch, values)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "stc"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


# 11. BUY reasoning에 "STC" 포함
def test_buy_reasoning_contains_stc(monkeypatch, strategy):
    df = _make_df(100)
    values = [18.0] * 97 + [18.0, 22.0, 0.0]
    _patch_stc(monkeypatch, values)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "STC" in sig.reasoning


# 12. SELL reasoning에 "STC" 포함
def test_sell_reasoning_contains_stc(monkeypatch, strategy):
    df = _make_df(100)
    values = [85.0] * 97 + [85.0, 80.0, 0.0]
    _patch_stc(monkeypatch, values)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "STC" in sig.reasoning
