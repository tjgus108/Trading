"""WickAnalysisStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.wick_analysis import WickAnalysisStrategy

strategy = WickAnalysisStrategy()


def _make_df(n=30, pattern="neutral", imbalance=0.0):
    """
    OHLCV DataFrame 생성.
    pattern:
      "buy"      → 하단 꼬리 우세 (wick_imbalance > 0.2)
      "sell"     → 상단 꼬리 우세 (wick_imbalance < -0.2)
      "neutral"  → 균형 꼬리
    imbalance: 직접 wick_imbalance 값을 설정할 때 사용 (0이면 pattern만 사용)
    """
    np.random.seed(42)
    base = 100.0
    opens = np.full(n, base)
    closes = np.full(n, base)
    highs = np.full(n, base + 0.5)
    lows = np.full(n, base - 0.5)
    volumes = np.full(n, 1000.0)

    idx = n - 2

    if pattern == "buy":
        # 하단 꼬리 크게: lower_wick >> upper_wick
        # open=close=base (도지형 몸통), high=base+0.3, low=base-2.0
        # total_range = 2.3, lower_wick=2.0, upper_wick=0.3
        # lower_ratio≈0.87, upper_ratio≈0.13, wick_imbalance≈0.74
        opens[idx] = base
        closes[idx] = base
        highs[idx] = base + 0.3
        lows[idx] = base - 2.0
    elif pattern == "sell":
        # 상단 꼬리 크게: upper_wick >> lower_wick
        opens[idx] = base
        closes[idx] = base
        highs[idx] = base + 2.0
        lows[idx] = base - 0.3
    else:
        # 균형
        opens[idx] = base
        closes[idx] = base
        highs[idx] = base + 0.5
        lows[idx] = base - 0.5

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })
    return df


def _make_mild_buy_df(n=30):
    """wick_imbalance ≈ 0.25 (>0.2 but <=0.4) → MEDIUM confidence BUY."""
    base = 100.0
    opens = np.full(n, base)
    closes = np.full(n, base)
    highs = np.full(n, base + 0.5)
    lows = np.full(n, base - 0.5)
    volumes = np.full(n, 1000.0)

    idx = n - 2
    # lower=1.0, upper=0.6, total=1.6+body(0.1)=1.7? simplify:
    # open=close=base (zero body), high=base+0.6, low=base-1.0
    # total=1.6, lower_ratio=1.0/1.6≈0.625, upper_ratio=0.6/1.6=0.375
    # wick_imbalance=0.625-0.375=0.25
    opens[idx] = base
    closes[idx] = base
    highs[idx] = base + 0.6
    lows[idx] = base - 1.0

    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    })


def _make_mild_sell_df(n=30):
    """wick_imbalance ≈ -0.25 → MEDIUM confidence SELL."""
    base = 100.0
    opens = np.full(n, base)
    closes = np.full(n, base)
    highs = np.full(n, base + 0.5)
    lows = np.full(n, base - 0.5)
    volumes = np.full(n, 1000.0)

    idx = n - 2
    opens[idx] = base
    closes[idx] = base
    highs[idx] = base + 1.0
    lows[idx] = base - 0.6

    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    })


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "wick_analysis"


# ── 2. None 입력 → HOLD ──────────────────────────────────────────────────
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 3. 데이터 부족 → HOLD ────────────────────────────────────────────────
def test_insufficient_data():
    df = _make_df(n=5)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 4. MIN_ROWS 경계 확인 ────────────────────────────────────────────────
def test_min_rows_boundary():
    df = _make_df(n=strategy.MIN_ROWS)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)


# ── 5. 하단 꼬리 우세 → BUY ─────────────────────────────────────────────
def test_buy_signal_lower_wick_dominant():
    df = _make_df(n=30, pattern="buy")
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 6. 상단 꼬리 우세 → SELL ────────────────────────────────────────────
def test_sell_signal_upper_wick_dominant():
    df = _make_df(n=30, pattern="sell")
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 7. BUY HIGH confidence (abs(wi) > 0.4) ───────────────────────────────
def test_buy_high_confidence():
    df = _make_df(n=30, pattern="buy")
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 8. SELL HIGH confidence ──────────────────────────────────────────────
def test_sell_high_confidence():
    df = _make_df(n=30, pattern="sell")
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 9. BUY MEDIUM confidence (0.2 < wi <= 0.4) ───────────────────────────
def test_buy_medium_confidence():
    df = _make_mild_buy_df(n=30)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 10. SELL MEDIUM confidence ───────────────────────────────────────────
def test_sell_medium_confidence():
    df = _make_mild_sell_df(n=30)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 11. 균형 꼬리 → HOLD ─────────────────────────────────────────────────
def test_neutral_hold():
    df = _make_df(n=30, pattern="neutral")
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 12. Signal 필드 완전성 ────────────────────────────────────────────────
def test_signal_fields():
    df = _make_df(n=30, pattern="buy")
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "wick_analysis"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 13. entry_price = last(-2) close ─────────────────────────────────────
def test_entry_price_is_last_close():
    df = _make_df(n=30, pattern="buy")
    sig = strategy.generate(df)
    expected = float(df.iloc[-2]["close"])
    assert sig.entry_price == expected


# ── 14. BUY reasoning에 "하단 꼬리" 포함 ─────────────────────────────────
def test_buy_reasoning_content():
    df = _make_df(n=30, pattern="buy")
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "하단 꼬리" in sig.reasoning


# ── 15. SELL reasoning에 "상단 꼬리" 포함 ────────────────────────────────
def test_sell_reasoning_content():
    df = _make_df(n=30, pattern="sell")
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "상단 꼬리" in sig.reasoning


# ── 16. HOLD reasoning에 "신호 없음" 포함 ────────────────────────────────
def test_hold_reasoning_content():
    df = _make_df(n=30, pattern="neutral")
    sig = strategy.generate(df)
    assert "신호 없음" in sig.reasoning
