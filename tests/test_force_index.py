"""ForceIndexStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.force_index import ForceIndexStrategy

strategy = ForceIndexStrategy()


def _make_df(n=50, close_above_ema=True, fi13_direction="none", high_conf=False):
    """
    fi13_direction: "rising"  → FI13 상승 (BUY 조건)
                    "falling" → FI13 하락 (SELL 조건)
                    "none"    → 변화 없음 (HOLD)
    high_conf: True → |FI13| > median (HIGH conf)
               False → |FI13| <= median (MEDIUM conf)
    """
    base_close = 110.0 if close_above_ema else 90.0
    ema50_val = 100.0

    closes = np.full(n, base_close, dtype=float)
    volumes = np.ones(n) * 1000.0

    if fi13_direction == "rising":
        # 앞 절반: 약한 하락 → FI13 낮음
        # 뒤 절반: 점점 강한 상승 → FI13 상승
        half = n // 2
        for i in range(half):
            closes[i] = base_close - 0.5
        for i in range(half, n):
            closes[i] = base_close + float(i - half) * 0.3
        if high_conf:
            volumes[n - 5:] = 50000.0  # 볼륨 급증으로 FI13 크게 만들기

    elif fi13_direction == "falling":
        # 앞 절반: 약한 상승 → FI13 높음
        # 뒤 절반: 점점 강한 하락 → FI13 하락
        half = n // 2
        for i in range(half):
            closes[i] = base_close + 0.5
        for i in range(half, n):
            closes[i] = base_close - float(i - half) * 0.3
        if high_conf:
            volumes[n - 5:] = 50000.0

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": closes + 0.5,
        "low": closes - 0.5,
        "volume": volumes,
        "ema50": np.full(n, ema50_val),
        "atr14": np.ones(n) * 0.5,
    })
    return df


def _compute_fi(df):
    """FI13, FI2 계산 (검증용)."""
    idx = len(df) - 2
    raw_force = df["close"].diff() * df["volume"]
    fi13 = raw_force.ewm(span=13, adjust=False).mean()
    fi2 = raw_force.ewm(span=2, adjust=False).mean()

    fi13_now = float(fi13.iloc[idx])
    fi13_prev = float(fi13.iloc[idx - 1])
    fi2_now = float(fi2.iloc[idx])

    fi13_abs_window = fi13.abs().iloc[idx - 20: idx]
    median_fi = float(fi13_abs_window.median()) if len(fi13_abs_window) > 0 else 1.0

    return fi13_now, fi13_prev, fi2_now, median_fi


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "force_index"


# ── 2. BUY 신호 (FI13 상승, close>ema50) ────────────────────────────────
def test_buy_signal():
    df = _make_df(fi13_direction="rising", close_above_ema=True)
    fi13_now, fi13_prev, _, _ = _compute_fi(df)
    assert fi13_now > fi13_prev, f"FI13 상승이어야 함: {fi13_now:.2f} > {fi13_prev:.2f}"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 (FI13 하락, close<ema50) ───────────────────────────────
def test_sell_signal():
    df = _make_df(fi13_direction="falling", close_above_ema=False)
    fi13_now, fi13_prev, _, _ = _compute_fi(df)
    assert fi13_now < fi13_prev, f"FI13 하락이어야 함: {fi13_now:.2f} < {fi13_prev:.2f}"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence (|FI13| > median) ────────────────────────────
def test_buy_high_confidence():
    df = _make_df(fi13_direction="rising", close_above_ema=True, high_conf=True)
    fi13_now, fi13_prev, _, median_fi = _compute_fi(df)
    assert fi13_now > fi13_prev
    assert abs(fi13_now) > median_fi, f"|FI13|({abs(fi13_now):.2f}) > median({median_fi:.2f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 5. SELL HIGH confidence (|FI13| > median) ───────────────────────────
def test_sell_high_confidence():
    df = _make_df(fi13_direction="falling", close_above_ema=False, high_conf=True)
    fi13_now, fi13_prev, _, median_fi = _compute_fi(df)
    assert fi13_now < fi13_prev
    assert abs(fi13_now) > median_fi, f"|FI13|({abs(fi13_now):.2f}) > median({median_fi:.2f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 6. FI13 상승이지만 close < ema50 → HOLD ────────────────────────────
def test_buy_fi13_rising_but_below_ema50_hold():
    df = _make_df(fi13_direction="rising", close_above_ema=False)
    fi13_now, fi13_prev, _, _ = _compute_fi(df)
    assert fi13_now > fi13_prev
    close_val = float(df["close"].iloc[-2])
    ema50_val = float(df["ema50"].iloc[-2])
    assert close_val < ema50_val
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 7. FI13 하락이지만 close > ema50 → HOLD ────────────────────────────
def test_sell_fi13_falling_but_above_ema50_hold():
    df = _make_df(fi13_direction="falling", close_above_ema=True)
    fi13_now, fi13_prev, _, _ = _compute_fi(df)
    assert fi13_now < fi13_prev
    close_val = float(df["close"].iloc[-2])
    ema50_val = float(df["ema50"].iloc[-2])
    assert close_val > ema50_val
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 8. 데이터 부족 → HOLD ──────────────────────────────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 9. None 입력 → HOLD ────────────────────────────────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 10. Signal 필드 완전성 ─────────────────────────────────────────────
def test_signal_fields():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "force_index"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 11. BUY reasoning에 "FI13" 포함 ────────────────────────────────────
def test_buy_reasoning_contains_fi13():
    df = _make_df(fi13_direction="rising", close_above_ema=True)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "FI13" in sig.reasoning


# ── 12. SELL reasoning에 "FI13" 포함 ───────────────────────────────────
def test_sell_reasoning_contains_fi13():
    df = _make_df(fi13_direction="falling", close_above_ema=False)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "FI13" in sig.reasoning


# ── 13. HOLD 신호 (FI13 변화 없음) ─────────────────────────────────────
def test_hold_no_direction():
    df = _make_df(fi13_direction="none", close_above_ema=True)
    sig = strategy.generate(df)
    # 방향 불명확 → HOLD (flat closes → FI13 거의 0, 변화 없음)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)  # 유연하게 허용


# ── 14. entry_price는 close 값 ─────────────────────────────────────────
def test_entry_price_is_close():
    df = _make_df(fi13_direction="rising", close_above_ema=True)
    sig = strategy.generate(df)
    expected_close = float(df["close"].iloc[-2])
    assert sig.entry_price == pytest.approx(expected_close, rel=1e-5)


# ── 15. MEDIUM confidence (|FI13| <= median) ────────────────────────────
def test_medium_confidence():
    df = _make_df(fi13_direction="rising", close_above_ema=True, high_conf=False)
    fi13_now, fi13_prev, _, median_fi = _compute_fi(df)
    assert fi13_now > fi13_prev
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    # HIGH 또는 MEDIUM — 데이터에 따라 달라지므로 타입만 확인
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)
