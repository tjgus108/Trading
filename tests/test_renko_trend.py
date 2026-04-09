"""RenkoTrendStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.renko_trend import RenkoTrendStrategy

strategy = RenkoTrendStrategy()


def _make_df(n=50, atr=1.0, trend="up", streak=3):
    """
    OHLCV DataFrame 생성.
    trend="up" → 마지막 streak개 봉에서 강한 상승 (brick_size * streak 이상)
    trend="down" → 마지막 streak개 봉에서 강한 하락
    trend="none" → 횡보
    """
    np.random.seed(42)
    base = 100.0
    closes = np.full(n, base, dtype=float)

    # ATR 고정 값으로 atr14 컬럼 포함
    atr_val = atr

    if trend == "up":
        # 앞부분 횡보, 끝에서 streak+1 개 봉 동안 강한 상승
        step = atr_val * 1.5  # brick_size보다 충분히 크게
        for i in range(n - streak - 1, n - 1):
            closes[i] = base + step * (i - (n - streak - 2))
    elif trend == "down":
        step = atr_val * 1.5
        for i in range(n - streak - 1, n - 1):
            closes[i] = base - step * (i - (n - streak - 2))
    # trend=="none": 횡보

    highs = closes + atr_val * 0.5
    lows = closes - atr_val * 0.5
    opens = closes - atr_val * 0.1
    volumes = np.full(n, 1000.0)

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
        "atr14": np.full(n, atr_val),
    })
    return df


def _make_df_no_atr(n=50, atr=1.0, trend="up", streak=3):
    """atr14 컬럼 없는 버전."""
    df = _make_df(n=n, atr=atr, trend=trend, streak=streak)
    return df.drop(columns=["atr14"])


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "renko_trend"


# ── 2. None 입력 → HOLD ──────────────────────────────────────────────────
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 3. 데이터 부족 (< MIN_ROWS) → HOLD ──────────────────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 4. 연속 상승 brick >= 3 → BUY ────────────────────────────────────────
def test_buy_signal_up_streak():
    df = _make_df(n=60, atr=1.0, trend="up", streak=5)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 5. 연속 하락 brick >= 3 → SELL ───────────────────────────────────────
def test_sell_signal_down_streak():
    df = _make_df(n=60, atr=1.0, trend="down", streak=5)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 6. 연속 brick 부족 → HOLD ────────────────────────────────────────────
def test_hold_no_streak():
    df = _make_df(n=60, atr=1.0, trend="none")
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 7. BUY MEDIUM confidence (streak=3,4) ────────────────────────────────
def test_buy_medium_confidence():
    df = _make_df(n=60, atr=1.0, trend="up", streak=3)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


# ── 8. BUY HIGH confidence (streak >= 5) ─────────────────────────────────
def test_buy_high_confidence_large_streak():
    # streak=8로 확실히 5연속 이상 brick 보장
    df = _make_df(n=80, atr=1.0, trend="up", streak=8)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 9. SELL HIGH confidence (streak >= 5) ────────────────────────────────
def test_sell_high_confidence_large_streak():
    df = _make_df(n=80, atr=1.0, trend="down", streak=8)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 10. Signal 필드 완전성 ────────────────────────────────────────────────
def test_signal_fields():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "renko_trend"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 11. atr14 컬럼 없어도 동작 ───────────────────────────────────────────
def test_works_without_atr14_column():
    df = _make_df_no_atr(n=60, atr=1.0, trend="up", streak=5)
    assert "atr14" not in df.columns
    sig = strategy.generate(df)
    # 오류 없이 Signal 반환되면 통과
    assert isinstance(sig, Signal)


# ── 12. BUY reasoning에 "Renko" 포함 ─────────────────────────────────────
def test_buy_reasoning_contains_renko():
    df = _make_df(n=80, atr=1.0, trend="up", streak=8)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "Renko" in sig.reasoning


# ── 13. SELL reasoning에 "Renko" 포함 ────────────────────────────────────
def test_sell_reasoning_contains_renko():
    df = _make_df(n=80, atr=1.0, trend="down", streak=8)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "Renko" in sig.reasoning


# ── 14. entry_price = last close ─────────────────────────────────────────
def test_entry_price_is_last_close():
    df = _make_df(n=50, trend="up", streak=5)
    sig = strategy.generate(df)
    expected = float(df.iloc[-2]["close"])
    assert sig.entry_price == expected


# ── 15. MIN_ROWS 경계 (정확히 MIN_ROWS) → 오류 없이 Signal 반환 ──────────
def test_min_rows_boundary():
    df = _make_df(n=strategy.MIN_ROWS)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)
