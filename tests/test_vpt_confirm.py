"""VolumePriceTrendConfirmStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.vpt_confirm import VolumePriceTrendConfirmStrategy


def _make_df(n=50, close_vals=None, volume_vals=None, ema20_vals=None):
    np.random.seed(7)
    base = np.linspace(100, 110, n)
    df = pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.2, 0.2, n),
        "high": base + 1.0,
        "low": base - 1.0,
        "volume": np.ones(n) * 1000,
        "ema20": base,
        "ema50": base,
        "atr14": np.ones(n) * 0.5,
    })
    if close_vals is not None:
        arr = np.asarray(close_vals, dtype=float)
        df = df.iloc[:len(arr)].copy()
        df["close"] = arr
        df["high"] = arr + 1.0
        df["low"] = arr - 1.0
    if volume_vals is not None:
        df["volume"] = np.asarray(volume_vals, dtype=float)
    if ema20_vals is not None:
        df["ema20"] = np.asarray(ema20_vals, dtype=float)
    return df


def _make_buy_df():
    """VPT > Signal, Hist 상승, close > EMA20."""
    n = 50
    # 꾸준한 상승 → VPT 상승세
    close = np.linspace(100, 130, n)
    volume = np.ones(n) * 1000
    ema20 = np.full(n, 90.0)  # close > ema20
    return _make_df(n=n, close_vals=close, volume_vals=volume, ema20_vals=ema20)


def _make_sell_df():
    """VPT < Signal, Hist 하락, close < EMA20."""
    n = 50
    # 꾸준한 하락 → VPT 하락세
    close = np.linspace(130, 100, n)
    volume = np.ones(n) * 1000
    ema20 = np.full(n, 150.0)  # close < ema20
    return _make_df(n=n, close_vals=close, volume_vals=volume, ema20_vals=ema20)


strategy = VolumePriceTrendConfirmStrategy()


# ── 1. 전략 이름 ──────────────────────────────
def test_strategy_name():
    assert strategy.name == "vpt_confirm"


# ── 2. 데이터 부족 → HOLD (LOW) ───────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW
    assert "부족" in sig.reasoning


# ── 3. None 입력 → HOLD ───────────────────────
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 4. 정상 데이터 → Signal 반환 ──────────────
def test_returns_signal_with_normal_data():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig is not None
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 5. Signal 필드 완전성 ─────────────────────
def test_signal_fields_complete():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.strategy == "vpt_confirm"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 6. BUY: 상승 데이터 → BUY 또는 HOLD ─────
def test_buy_signal_uptrend():
    df = _make_buy_df()
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)
    assert sig.entry_price >= 0.0


# ── 7. SELL: 하락 데이터 → SELL 또는 HOLD ────
def test_sell_signal_downtrend():
    df = _make_sell_df()
    sig = strategy.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)
    assert sig.entry_price >= 0.0


# ── 8. close < EMA20 시 BUY 억제 ─────────────
def test_buy_suppressed_when_close_below_ema20():
    df = _make_buy_df()
    df["ema20"] = df["close"] + 100  # close < ema20
    sig = strategy.generate(df)
    assert sig.action != Action.BUY


# ── 9. close > EMA20 시 SELL 억제 ────────────
def test_sell_suppressed_when_close_above_ema20():
    df = _make_sell_df()
    df["ema20"] = df["close"] - 100  # close > ema20
    sig = strategy.generate(df)
    assert sig.action != Action.SELL


# ── 10. Confidence 유효 값 ───────────────────
def test_confidence_is_valid():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 11. BUY reasoning에 "VPT" 포함 ───────────
def test_buy_reasoning_contains_vpt():
    df = _make_buy_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "VPT" in sig.reasoning


# ── 12. SELL reasoning에 "VPT" 포함 ──────────
def test_sell_reasoning_contains_vpt():
    df = _make_sell_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "VPT" in sig.reasoning


# ── 13. HOLD reasoning 내용 확인 ─────────────
def test_hold_reasoning_format():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    if sig.action == Action.HOLD:
        assert len(sig.reasoning) > 0


# ── 14. 인스턴스 생성 ─────────────────────────
def test_strategy_instance():
    strat = VolumePriceTrendConfirmStrategy()
    assert isinstance(strat, VolumePriceTrendConfirmStrategy)


# ── 15. 최소 행 경계값 (24행) ─────────────────
def test_boundary_rows_below_min():
    df = _make_df(n=24)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 16. 최소 행 정확히 충족 (25행) ───────────
def test_boundary_rows_at_min():
    df = _make_df(n=25)
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
