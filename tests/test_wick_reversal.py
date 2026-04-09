"""WickReversalStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.wick_reversal import WickReversalStrategy

strategy = WickReversalStrategy()


def _make_df(n=30, pattern="hammer", wick_ratio=0.65, close_near_sma=True, vol_ok=True):
    """
    OHLCV DataFrame 생성.
    pattern:
      "hammer"       → 긴 아래꼬리
      "shooting_star" → 긴 위꼬리
      "none"          → 꼬리 없음 (도지형)
    wick_ratio: 목표 wick 비율 (0.0~1.0)
    close_near_sma: True → close ≈ SMA20, False → close far from SMA
    vol_ok: True → volume > avg_vol_10 * 0.8
    """
    np.random.seed(0)
    sma_val = 100.0

    # 앞 n-1봉: close=sma_val, 평범한 캔들
    closes = np.full(n, sma_val, dtype=float)
    highs = closes + 1.0
    lows = closes - 1.0
    opens = closes.copy()
    volumes = np.full(n, 1000.0)

    # 마지막 완성봉 = index n-2
    idx = n - 2
    body = 0.2  # 작은 몸통
    total = 2.0  # total_range 고정

    if pattern == "hammer":
        # lower_wick = wick_ratio * total
        # body is small, upper_wick fills the rest
        # total_range = lower_wick + body + upper_wick = total
        lower_wick = wick_ratio * total
        body_size = 0.1
        upper_wick = total - lower_wick - body_size
        if upper_wick < 0:
            upper_wick = 0.0
            body_size = total - lower_wick
        low_val = sma_val - lower_wick
        open_val = sma_val
        close_val = sma_val + body_size
        high_val = close_val + upper_wick
    elif pattern == "shooting_star":
        upper_wick = wick_ratio * total
        body_size = 0.1
        lower_wick = total - upper_wick - body_size
        if lower_wick < 0:
            lower_wick = 0.0
            body_size = total - upper_wick
        close_val = sma_val
        open_val = sma_val - body_size
        low_val = open_val - lower_wick
        high_val = sma_val + upper_wick
    else:  # none
        open_val = sma_val
        close_val = sma_val
        high_val = sma_val + 0.3
        low_val = sma_val - 0.3

    if not close_near_sma:
        # close를 SMA20에서 멀리 (BUY: close < SMA20*0.97)
        if pattern == "hammer":
            offset = sma_val * 0.10
            open_val -= offset
            close_val -= offset
            high_val -= offset
            low_val -= offset
        elif pattern == "shooting_star":
            offset = sma_val * 0.10
            open_val += offset
            close_val += offset
            high_val += offset
            low_val += offset

    closes[idx] = close_val
    opens[idx] = open_val
    highs[idx] = high_val
    lows[idx] = low_val

    if vol_ok:
        volumes[idx] = 1000.0  # avg_vol_10 * 0.8 = 800 < 1000
    else:
        volumes[idx] = 100.0   # 너무 낮은 볼륨

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })
    return df


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "wick_reversal"


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


# ── 4. Hammer 패턴 → BUY ─────────────────────────────────────────────────
def test_hammer_buy_signal():
    df = _make_df(n=30, pattern="hammer", wick_ratio=0.65, close_near_sma=True, vol_ok=True)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 5. Shooting Star 패턴 → SELL ─────────────────────────────────────────
def test_shooting_star_sell_signal():
    df = _make_df(n=30, pattern="shooting_star", wick_ratio=0.65, close_near_sma=True, vol_ok=True)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 6. Hammer + wick_ratio > 0.7 → HIGH confidence ──────────────────────
def test_hammer_high_confidence():
    df = _make_df(n=30, pattern="hammer", wick_ratio=0.75, close_near_sma=True, vol_ok=True)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 7. Shooting Star + wick_ratio > 0.7 → HIGH confidence ───────────────
def test_shooting_star_high_confidence():
    df = _make_df(n=30, pattern="shooting_star", wick_ratio=0.75, close_near_sma=True, vol_ok=True)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 8. Hammer + volume 부족 → HOLD ───────────────────────────────────────
def test_hammer_low_volume_hold():
    df = _make_df(n=30, pattern="hammer", wick_ratio=0.65, close_near_sma=True, vol_ok=False)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 9. total_range == 0 → HOLD ───────────────────────────────────────────
def test_zero_total_range():
    df = _make_df(n=30, pattern="none")
    idx = len(df) - 2
    df.at[idx, "high"] = 100.0
    df.at[idx, "low"] = 100.0
    df.at[idx, "open"] = 100.0
    df.at[idx, "close"] = 100.0
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "total_range" in sig.reasoning


# ── 10. 패턴 없음 → HOLD ─────────────────────────────────────────────────
def test_no_pattern_hold():
    df = _make_df(n=30, pattern="none")
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 11. Signal 필드 완전성 ────────────────────────────────────────────────
def test_signal_fields():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "wick_reversal"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 12. BUY reasoning에 "Hammer" 포함 ────────────────────────────────────
def test_buy_reasoning_contains_hammer():
    df = _make_df(n=30, pattern="hammer", wick_ratio=0.65, close_near_sma=True, vol_ok=True)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "Hammer" in sig.reasoning


# ── 13. SELL reasoning에 "Shooting Star" 포함 ────────────────────────────
def test_sell_reasoning_contains_shooting_star():
    df = _make_df(n=30, pattern="shooting_star", wick_ratio=0.65, close_near_sma=True, vol_ok=True)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "Shooting Star" in sig.reasoning


# ── 14. entry_price = last close ─────────────────────────────────────────
def test_entry_price_is_last_close():
    df = _make_df(n=30, pattern="hammer", wick_ratio=0.65, close_near_sma=True, vol_ok=True)
    sig = strategy.generate(df)
    expected = float(df.iloc[-2]["close"])
    assert sig.entry_price == expected


# ── 15. MIN_ROWS 경계 → 오류 없이 Signal 반환 ────────────────────────────
def test_min_rows_boundary():
    df = _make_df(n=strategy.MIN_ROWS)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)
