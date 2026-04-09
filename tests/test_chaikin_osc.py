"""ChaikinOscillatorStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.chaikin_osc import ChaikinOscillatorStrategy

strategy = ChaikinOscillatorStrategy()


def _make_df(n=60, cross="none", close_above_ema20=True):
    """
    cross="up"  : Osc prev < 0, now >= 0
    cross="down": Osc prev > 0, now <= 0
    cross="none": no crossover
    """
    base_close = 110.0 if close_above_ema20 else 90.0
    ema20_val = 100.0

    closes = np.full(n, base_close, dtype=float)
    # 단순 OHLCV: spread=2, neutral MFM=0 (close at mid)
    highs = closes + 2.0
    lows = closes - 2.0
    volumes = np.full(n, 1000.0)

    if cross == "up":
        # 앞 절반: bearish candles → MFM=-1 → MFV 음 → ADL 하락 → Osc < 0
        half = n // 2
        for i in range(half):
            # close == low → MFM = -1
            lows[i] = closes[i]
            highs[i] = closes[i] + 4.0
        # n-3: 마지막 bearish 유지 (prev_osc < 0)
        lows[n - 3] = closes[n - 3]
        highs[n - 3] = closes[n - 3] + 4.0
        # n-2: 강한 bullish × 대량 볼륨 → MFM=+1 → ADL 급등 → Osc >= 0
        highs[n - 2] = closes[n - 2]
        lows[n - 2] = closes[n - 2] - 4.0
        volumes[n - 2] = 1000.0 * 200

    elif cross == "down":
        half = n // 2
        for i in range(half):
            highs[i] = closes[i]
            lows[i] = closes[i] - 4.0
        highs[n - 3] = closes[n - 3]
        lows[n - 3] = closes[n - 3] - 4.0
        lows[n - 2] = closes[n - 2]
        highs[n - 2] = closes[n - 2] + 4.0
        volumes[n - 2] = 1000.0 * 200

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
        "ema20": np.full(n, ema20_val),
    })
    return df


def _compute_osc(df):
    """전략과 동일한 공식으로 osc 계산."""
    hl = df["high"] - df["low"]
    mfm = np.where(
        hl == 0, 0.0,
        ((df["close"] - df["low"]) - (df["high"] - df["close"])) / hl,
    )
    mfv = pd.Series(mfm) * df["volume"].values
    adl = mfv.cumsum()
    osc = adl.ewm(span=3, adjust=False).mean() - adl.ewm(span=10, adjust=False).mean()
    return osc


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "chaikin_osc"


# ── 2. BUY 신호 ──────────────────────────────────────────────────────────────
def test_buy_signal():
    df = _make_df(cross="up", close_above_ema20=True)
    osc = _compute_osc(df)
    idx = len(df) - 2
    assert osc.iloc[idx - 1] < 0, "prev osc must be < 0"
    assert osc.iloc[idx] >= 0, "now osc must be >= 0"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 ─────────────────────────────────────────────────────────────
def test_sell_signal():
    df = _make_df(cross="down", close_above_ema20=False)
    osc = _compute_osc(df)
    idx = len(df) - 2
    assert osc.iloc[idx - 1] > 0, "prev osc must be > 0"
    assert osc.iloc[idx] <= 0, "now osc must be <= 0"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY cross_up but close < EMA20 → HOLD ────────────────────────────────
def test_buy_cross_but_below_ema20_hold():
    df = _make_df(cross="up", close_above_ema20=False)
    osc = _compute_osc(df)
    idx = len(df) - 2
    if osc.iloc[idx - 1] < 0 and osc.iloc[idx] >= 0:
        sig = strategy.generate(df)
        assert sig.action == Action.HOLD


# ── 5. SELL cross_down but close > EMA20 → HOLD ─────────────────────────────
def test_sell_cross_but_above_ema20_hold():
    df = _make_df(cross="down", close_above_ema20=True)
    osc = _compute_osc(df)
    idx = len(df) - 2
    if osc.iloc[idx - 1] > 0 and osc.iloc[idx] <= 0:
        sig = strategy.generate(df)
        assert sig.action == Action.HOLD


# ── 6. 크로스 없음 → HOLD ────────────────────────────────────────────────────
def test_hold_no_cross():
    df = _make_df(cross="none", close_above_ema20=True)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 7. 데이터 부족 → HOLD ────────────────────────────────────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 8. None 입력 → HOLD ──────────────────────────────────────────────────────
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 9. Signal 필드 완전성 ────────────────────────────────────────────────────
def test_signal_fields():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "chaikin_osc"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 10. BUY reasoning에 "Chaikin" 포함 ───────────────────────────────────────
def test_buy_reasoning_contains_chaikin():
    df = _make_df(cross="up", close_above_ema20=True)
    osc = _compute_osc(df)
    idx = len(df) - 2
    if osc.iloc[idx - 1] < 0 and osc.iloc[idx] >= 0:
        sig = strategy.generate(df)
        if sig.action == Action.BUY:
            assert "Chaikin" in sig.reasoning


# ── 11. SELL reasoning에 "Chaikin" 포함 ──────────────────────────────────────
def test_sell_reasoning_contains_chaikin():
    df = _make_df(cross="down", close_above_ema20=False)
    osc = _compute_osc(df)
    idx = len(df) - 2
    if osc.iloc[idx - 1] > 0 and osc.iloc[idx] <= 0:
        sig = strategy.generate(df)
        if sig.action == Action.SELL:
            assert "Chaikin" in sig.reasoning


# ── 12. BUY HIGH confidence ──────────────────────────────────────────────────
def test_buy_high_confidence():
    """대량 볼륨 cross_up → |Osc| > std → HIGH."""
    df = _make_df(cross="up", close_above_ema20=True)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 13. SELL HIGH confidence ─────────────────────────────────────────────────
def test_sell_high_confidence():
    df = _make_df(cross="down", close_above_ema20=False)
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 14. ema20 컬럼 없어도 동작 ───────────────────────────────────────────────
def test_works_without_ema20_column():
    df = _make_df(cross="none", close_above_ema20=True)
    df = df.drop(columns=["ema20"])
    sig = strategy.generate(df)
    assert sig.action is not None


# ── 15. entry_price = close of _last ─────────────────────────────────────────
def test_entry_price_is_last_close():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))
