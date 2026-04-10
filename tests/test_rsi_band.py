"""
RSIBandStrategy 단위 테스트 (14개)
"""

import pandas as pd
import pytest

from src.strategy.rsi_band import RSIBandStrategy
from src.strategy.base import Action, Confidence


# ── helpers ────────────────────────────────────────────────────────────────────

def _make_df(n: int = 35, close_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    highs  = [c * 1.01 for c in close_values]
    lows   = [c * 0.99 for c in close_values]
    return pd.DataFrame({
        "open":   close_values,
        "high":   highs,
        "low":    lows,
        "close":  close_values,
        "volume": [1000.0] * n,
    })


def _make_zigzag(start: float, n: int, step: float) -> list:
    """교대로 오르내리는 지그재그 가격 패턴 → RSI ≈ 50 유지."""
    closes = [start]
    for i in range(n - 1):
        if i % 2 == 0:
            closes.append(closes[-1] + step)
        else:
            closes.append(closes[-1] - step)
    return closes


def _make_oversold_bounce_df() -> pd.DataFrame:
    """
    RSI가 dynamic_os 아래가 되도록 직접 가격 패턴 설계.
    - 지그재그 50봉(step 큼): RSI ≈ 50, rsi_ma ≈ 50, rsi_std 작음 (≈ 5)
    - 급락 3봉(매우 극단): RSI → ~0 (window 20 안에 RSI 50짜리 17봉 + RSI 0짜리 3봉)
      rsi_ma ≈ (17*50 + 3*0)/20 = 42.5, rsi_std ≈ std([50]*17 + [0]*3) ≈ 21
      dynamic_os = 42.5 - 21 = 21.5
      rsi ≈ 0 < 21.5 → 조건 충족
    - [-3]=0, [-2]=0.5 (소폭 반등)
    """
    closes = _make_zigzag(100.0, 50, 5.0)
    # 매우 극단적인 급락 (RSI → 0)
    for i in range(3):
        closes.append(closes[-1] - 80.0)
    closes.append(closes[-1] - 0.5)   # [-3]
    closes.append(closes[-1] + 2.0)   # [-2]: 반등 (rsi 소폭 상승)
    closes.append(closes[-1] + 1.0)   # [-1]
    return _make_df(n=len(closes), close_values=closes)


def _make_overbought_drop_df() -> pd.DataFrame:
    """
    RSI가 dynamic_ob 위가 되도록 설계.
    - 지그재그 50봉: RSI ≈ 50, rsi_ma ≈ 50, rsi_std 작음
    - 급등 3봉(매우 극단): RSI → ~100
      rsi_ma ≈ (17*50 + 3*100)/20 = 57.5, rsi_std ≈ 21
      dynamic_ob = 57.5 + 21 = 78.5
      rsi ≈ 100 > 78.5 → 조건 충족
    - [-3]=100, [-2]=99 (소폭 하락)
    """
    closes = _make_zigzag(100.0, 50, 5.0)
    for i in range(3):
        closes.append(closes[-1] + 80.0)
    closes.append(closes[-1] + 0.5)    # [-3]: 소폭 상승
    closes.append(closes[-1] - 40.0)  # [-2]: 대폭 하락 → RSI 크게 감소
    closes.append(closes[-1] - 1.0)   # [-1]
    return _make_df(n=len(closes), close_values=closes)


# ── 기본 ───────────────────────────────────────────────────────────────────────


def test_strategy_name():
    assert RSIBandStrategy().name == "rsi_band"


def test_strategy_instantiable():
    assert RSIBandStrategy() is not None


# ── 데이터 부족 ────────────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = RSIBandStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows_no_crash():
    s = RSIBandStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


# ── BUY ────────────────────────────────────────────────────────────────────────

def test_buy_signal_oversold_bounce():
    s = RSIBandStrategy()
    df = _make_oversold_bounce_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_confidence_not_low():
    s = RSIBandStrategy()
    df = _make_oversold_bounce_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_buy_entry_price_is_last_close():
    s = RSIBandStrategy()
    df = _make_oversold_bounce_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_buy_reasoning_mentions_dynamic_os():
    s = RSIBandStrategy()
    df = _make_oversold_bounce_df()
    sig = s.generate(df)
    assert "dynamic_os" in sig.reasoning or "os" in sig.reasoning.lower()


# ── SELL ───────────────────────────────────────────────────────────────────────

def test_sell_signal_overbought_drop():
    s = RSIBandStrategy()
    df = _make_overbought_drop_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_confidence_not_low():
    s = RSIBandStrategy()
    df = _make_overbought_drop_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_sell_entry_price_is_last_close():
    s = RSIBandStrategy()
    df = _make_overbought_drop_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_sell_reasoning_mentions_dynamic_ob():
    s = RSIBandStrategy()
    df = _make_overbought_drop_df()
    sig = s.generate(df)
    assert "dynamic_ob" in sig.reasoning or "ob" in sig.reasoning.lower()


# ── HOLD ───────────────────────────────────────────────────────────────────────

def test_hold_flat_market():
    s = RSIBandStrategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_is_low():
    s = RSIBandStrategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW


def test_signal_strategy_field():
    s = RSIBandStrategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert sig.strategy == "rsi_band"
