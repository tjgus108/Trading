"""AlligatorStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.alligator import AlligatorStrategy, _smma

strategy = AlligatorStrategy()


def _make_df(n=60, mode="neutral"):
    """
    mode="bull"    : lips > teeth > jaw, close > lips
    mode="bear"    : lips < teeth < jaw, close < lips
    mode="neutral" : no alignment
    mode="bull_no_close": bull aligned but close <= lips
    mode="bear_no_close": bear aligned but close >= lips
    """
    closes = np.linspace(100, 110, n) if mode in ("bull", "bull_no_close") else \
             np.linspace(110, 100, n) if mode in ("bear", "bear_no_close") else \
             np.full(n, 100.0)

    df = pd.DataFrame({
        "open": closes,
        "close": closes.copy(),
        "high": closes + 1.0,
        "low": closes - 1.0,
        "volume": np.full(n, 1000.0),
    })

    if mode == "bull_no_close":
        # close 값을 lips 아래로 강제
        lips = _smma(pd.Series(df["close"]), 5)
        lips_val = float(lips.iloc[n - 2])
        df.loc[df.index[n - 2], "close"] = lips_val - 1.0

    if mode == "bear_no_close":
        lips = _smma(pd.Series(df["close"]), 5)
        lips_val = float(lips.iloc[n - 2])
        df.loc[df.index[n - 2], "close"] = lips_val + 1.0

    return df


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "alligator"


# ── 2. BUY 신호 ──────────────────────────────────────────────────────────────
def test_buy_signal():
    df = _make_df(mode="bull")
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 ─────────────────────────────────────────────────────────────
def test_sell_signal():
    df = _make_df(mode="bear")
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 4. 정렬됐지만 close <= lips → HOLD ───────────────────────────────────────
def test_bull_aligned_close_not_above_lips_hold():
    df = _make_df(mode="bull_no_close")
    sig = strategy.generate(df)
    # lips 아래에 close 강제했으므로 BUY 조건 미충족
    assert sig.action != Action.BUY


# ── 5. bear 정렬됐지만 close >= lips → HOLD ──────────────────────────────────
def test_bear_aligned_close_not_below_lips_hold():
    df = _make_df(mode="bear_no_close")
    sig = strategy.generate(df)
    assert sig.action != Action.SELL


# ── 6. 중립 → HOLD ───────────────────────────────────────────────────────────
def test_neutral_hold():
    df = _make_df(mode="neutral")
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
    assert sig.strategy == "alligator"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 10. BUY reasoning에 "Alligator" 포함 ─────────────────────────────────────
def test_buy_reasoning_contains_alligator():
    df = _make_df(mode="bull")
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "Alligator" in sig.reasoning


# ── 11. SELL reasoning에 "Alligator" 포함 ────────────────────────────────────
def test_sell_reasoning_contains_alligator():
    df = _make_df(mode="bear")
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "Alligator" in sig.reasoning


# ── 12. SMMA 수렴 확인 ───────────────────────────────────────────────────────
def test_smma_converges():
    """SMMA(5) 마지막 값이 가장 최근 close에 수렴해야 한다."""
    closes = pd.Series(np.full(30, 100.0))
    s = _smma(closes, 5)
    assert abs(float(s.iloc[-1]) - 100.0) < 1e-6


# ── 13. BUY confidence HIGH (spread > avg) ───────────────────────────────────
def test_buy_confidence_type():
    df = _make_df(mode="bull", n=60)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 14. entry_price = _last close ────────────────────────────────────────────
def test_entry_price_is_last_close():
    df = _make_df(mode="bull")
    sig = strategy.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


# ── 15. bull 정렬 검증 (lips > teeth > jaw) ──────────────────────────────────
def test_bull_alignment_verified():
    df = _make_df(mode="bull")
    close = df["close"]
    from src.strategy.alligator import _smma
    jaw = _smma(close, 13)
    teeth = _smma(close, 8)
    lips = _smma(close, 5)
    idx = len(df) - 2
    assert float(lips.iloc[idx]) > float(teeth.iloc[idx]) > float(jaw.iloc[idx])
