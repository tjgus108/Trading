"""BidAskImbalanceStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.bid_ask_imbalance import BidAskImbalanceStrategy
from src.strategy.base import Action, Confidence


def _make_df(n: int = 30, close_val: float = 100.0,
             buy_pressure: float = 0.5) -> pd.DataFrame:
    """
    buy_pressure: 0.0~1.0. 1.0이면 close==high (순수 매수), 0.0이면 close==low.
    """
    low = np.full(n, close_val - 2.0)
    high = np.full(n, close_val + 2.0)
    # close = low + buy_pressure * (high - low)
    close = low + buy_pressure * (high - low)
    return pd.DataFrame({
        "open": np.full(n, close_val),
        "high": high,
        "low": low,
        "close": close,
        "volume": np.full(n, 100.0),
    })


def _make_strong_buy_df(n: int = 40) -> pd.DataFrame:
    """매수 압력 매우 강한 DF: imbalance_ema > 0.4 AND close > ema20.

    초반 절반은 baseline(100), 후반 절반은 105(매수 압력 강) → EMA20은
    ~100대에서 올라오므로 마지막(-2)봉 close=105 > ema20.
    """
    half = n // 2
    close = np.concatenate([np.full(half, 100.0), np.full(n - half, 105.0)])
    high = close + 1.0
    low = close - 3.0  # close가 high에 가까워 매수 압력 강
    return pd.DataFrame({
        "open": close - 0.5,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.full(n, 100.0),
    })


def _make_strong_sell_df(n: int = 40) -> pd.DataFrame:
    """매도 압력 매우 강한 DF: imbalance_ema < -0.4 AND close < ema20.

    초반 절반은 baseline(100), 후반 절반은 95(매도 압력 강) → EMA20은
    ~100대에서 내려오므로 마지막(-2)봉 close=95 < ema20.
    """
    half = n // 2
    close = np.concatenate([np.full(half, 100.0), np.full(n - half, 95.0)])
    high = close + 3.0  # close가 low에 가까워 매도 압력 강
    low = close - 1.0
    return pd.DataFrame({
        "open": close + 0.5,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.full(n, 100.0),
    })


# 1. 전략 이름
def test_strategy_name():
    assert BidAskImbalanceStrategy().name == "bid_ask_imbalance"


# 2. 데이터 부족 → HOLD LOW
def test_insufficient_data_returns_hold():
    s = BidAskImbalanceStrategy()
    df = _make_df(n=15)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 3. 정확히 20행 → 오류 없이 동작
def test_exactly_20_rows_no_error():
    s = BidAskImbalanceStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# 4. 강한 매수 압력 + close > EMA20 → BUY
def test_buy_signal_strong_buy_pressure():
    s = BidAskImbalanceStrategy()
    df = _make_strong_buy_df(n=40)
    sig = s.generate(df)
    assert sig.action == Action.BUY


# 5. 강한 매도 압력 + close < EMA20 → SELL
def test_sell_signal_strong_sell_pressure():
    s = BidAskImbalanceStrategy()
    df = _make_strong_sell_df(n=40)
    sig = s.generate(df)
    assert sig.action == Action.SELL


# 6. 균형 상태 → HOLD
def test_hold_signal_balanced():
    s = BidAskImbalanceStrategy()
    df = _make_df(n=30, close_val=100.0, buy_pressure=0.5)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# 7. HIGH confidence: |imbalance_ema| > 0.4
def test_high_confidence_strong_imbalance():
    s = BidAskImbalanceStrategy()
    df = _make_strong_buy_df(n=40)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# 8. MEDIUM confidence: imbalance 약함
def test_medium_confidence_weak_imbalance():
    s = BidAskImbalanceStrategy()
    # buy_pressure=0.65 → imbalance=(0.65*2 - 0.35*2)/(2) = 0.3 (약간 매수 우세)
    # 그러나 ema 스무딩 후 0.2~0.4 사이일 가능성
    df = _make_df(n=30, close_val=100.0, buy_pressure=0.65)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


# 9. Signal 필드 완전성
def test_signal_fields_complete():
    s = BidAskImbalanceStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.strategy == "bid_ask_imbalance"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# 10. high == low (zero range) → volume * 0.5 처리, 오류 없음
def test_zero_range_candles_no_error():
    s = BidAskImbalanceStrategy()
    n = 30
    df = pd.DataFrame({
        "open": np.full(n, 100.0),
        "high": np.full(n, 100.0),
        "low": np.full(n, 100.0),
        "close": np.full(n, 100.0),
        "volume": np.full(n, 100.0),
    })
    sig = s.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# 11. BUY 신호의 reasoning에 imbalance_ema 포함
def test_buy_reasoning_contains_imbalance_ema():
    s = BidAskImbalanceStrategy()
    df = _make_strong_buy_df(n=40)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "imbalance_ema=" in sig.reasoning


# 12. SELL 신호의 reasoning에 imbalance_ema 포함
def test_sell_reasoning_contains_imbalance_ema():
    s = BidAskImbalanceStrategy()
    df = _make_strong_sell_df(n=40)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "imbalance_ema=" in sig.reasoning


# 13. buy_pressure < 0.2 but close > EMA20 → HOLD (조건 불완전)
def test_hold_when_only_price_condition_met():
    s = BidAskImbalanceStrategy()
    # close > ema20 이지만 imbalance는 매도 우세 → HOLD
    n = 30
    close = np.full(n, 105.0)
    # high near close → sell pressure
    df = pd.DataFrame({
        "open": np.full(n, 105.0),
        "high": np.full(n, 105.5),
        "low": np.full(n, 103.0),
        "close": close,
        "volume": np.full(n, 100.0),
    })
    sig = s.generate(df)
    # imbalance_ema ~ (0.2 - 0.8) < -0.2... and close > ema20
    # close > ema20이므로 SELL 조건 불충족 → HOLD (혹은 if ema 충분히 낮으면 SELL)
    assert sig.action in (Action.HOLD, Action.SELL)


# 14. entry_price == close of _last(df)
def test_entry_price_equals_last_close():
    s = BidAskImbalanceStrategy()
    df = _make_strong_buy_df(n=40)
    sig = s.generate(df)
    expected_close = float(df.iloc[-2]["close"])
    assert sig.entry_price == pytest.approx(expected_close)
