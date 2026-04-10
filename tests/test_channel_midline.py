"""tests/test_channel_midline.py — ChannelMidlineStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd

from src.strategy.channel_midline import ChannelMidlineStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 50, price: float = 100.0) -> pd.DataFrame:
    closes = np.full(n, price)
    return pd.DataFrame({
        "open": closes.copy(),
        "close": closes.copy(),
        "high": closes + 1.0,
        "low": closes - 1.0,
        "volume": np.ones(n) * 1000.0,
    })


def _make_buy_df(wide_channel: bool = False) -> pd.DataFrame:
    """
    prev_close < midline, curr_close > midline → BUY signal.

    Confidence logic: HIGH if channel_width > channel_width.rolling(20).mean() * 1.3.
    channel_width = highest - lowest = high.rolling(20).max() - low.rolling(20).min().

    For MEDIUM: uniform spread throughout → cw constant → cw/cw_mean=1.0 → MEDIUM.
    For HIGH: rows 0-47 narrow spread (cw≈2), rows 48-68 wide spread.
      At idx=68: highest=max(highs[49:69])=130, lowest=min(lows[49:69])=70, cw=60.
      cw_mean[68] = mean of cw[49:69]. cw[49..68] are all 60 → cw_mean=60, ratio=1.0.
      That still won't work. Instead: rows 0-47 narrow (cw≈2), last 1 row very wide.
      At idx=68 (n=70): highest[68]=max(highs[49:69]).
        highs[49:68]=102, highs[68]=200 → highest=200.
        lows[49:68]=98, lows[68]=0 → lowest=0. cw=200.
      cw[68] = 200. cw_mean[68] = mean(cw[49:69]).
        cw[49]=max(highs[30:50])-min(lows[30:50]): highs[30:49]=102, highs[49]=102 → max=102.
        lows[30:49]=98, lows[49]=98 → min=98. cw[49]=4.
        ... similarly cw[50..67] all ≈4, cw[68]=200.
        cw_mean[68] = (19*4 + 200)/20 = (76+200)/20=13.8.
        Check: 200 > 13.8*1.3=17.94 → YES → HIGH ✓
    """
    if wide_channel:
        n = 70
        closes = np.full(n, 100.0)
        highs = closes + 2.0
        lows = closes - 2.0
        idx = n - 2  # 68
        # Make row 68 have extreme spread so cw[68] >> cw_mean[68]
        highs[idx] = 200.0
        lows[idx] = 0.0
        # midline at idx=68: (200+0)/2=100
        closes[idx - 1] = 99.0   # prev_close < 100
        closes[idx] = 101.0      # curr_close > 100 (but < 200 so still valid crossover)
        # Actually midline = (highest[68] + lowest[68])/2 = (200+0)/2=100
        # prev_close=99 < 100, curr_close=101 > 100 ✓
        closes[n - 1] = 101.0
    else:
        n = 50
        closes = np.full(n, 100.0)
        highs = closes + 1.0
        lows = closes - 1.0
        # uniform → midline=100, cw=2 constant → ratio=1 → MEDIUM
        closes[47] = 99.5   # prev_close < 100
        closes[48] = 100.5  # curr_close > 100
        closes[49] = 100.5

    return pd.DataFrame({
        "open": closes.copy(),
        "close": closes.copy(),
        "high": highs,
        "low": lows,
        "volume": np.ones(n) * 1000.0,
    })


def _make_sell_df(wide_channel: bool = False) -> pd.DataFrame:
    """
    prev_close > midline, curr_close < midline → SELL signal.
    """
    if wide_channel:
        n = 70
        closes = np.full(n, 100.0)
        highs = closes + 2.0
        lows = closes - 2.0
        idx = n - 2  # 68
        highs[idx] = 200.0
        lows[idx] = 0.0
        closes[idx - 1] = 101.0
        closes[idx] = 99.0
        closes[n - 1] = 99.0
    else:
        n = 50
        closes = np.full(n, 100.0)
        highs = closes + 1.0
        lows = closes - 1.0
        closes[47] = 100.5
        closes[48] = 99.5
        closes[49] = 99.5

    return pd.DataFrame({
        "open": closes.copy(),
        "close": closes.copy(),
        "high": highs,
        "low": lows,
        "volume": np.ones(n) * 1000.0,
    })


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────
def test_strategy_name():
    assert ChannelMidlineStrategy.name == "channel_midline"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────
def test_instantiation():
    s = ChannelMidlineStrategy()
    assert isinstance(s, ChannelMidlineStrategy)


# ── 3. 데이터 부족 → HOLD ─────────────────────────────────────────────────
def test_insufficient_data_returns_hold():
    df = _make_df(n=20)
    sig = ChannelMidlineStrategy().generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ───────────────────────────────────────────────────
def test_none_input_returns_hold():
    sig = ChannelMidlineStrategy().generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────
def test_insufficient_data_reasoning():
    df = _make_df(n=10)
    sig = ChannelMidlineStrategy().generate(df)
    assert "Insufficient" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────
def test_normal_data_returns_signal():
    df = _make_df(n=50)
    sig = ChannelMidlineStrategy().generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성 ───────────────────────────────────────────────────
def test_signal_fields_complete():
    df = _make_df(n=50)
    sig = ChannelMidlineStrategy().generate(df)
    assert sig.strategy == "channel_midline"
    assert isinstance(sig.entry_price, float)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str)


# ── 8. BUY reasoning 키워드 확인 ─────────────────────────────────────────
def test_buy_reasoning_keyword():
    df = _make_buy_df(wide_channel=False)
    sig = ChannelMidlineStrategy().generate(df)
    assert sig.action == Action.BUY
    assert "midline" in sig.reasoning.lower()


# ── 9. SELL reasoning 키워드 확인 ────────────────────────────────────────
def test_sell_reasoning_keyword():
    df = _make_sell_df(wide_channel=False)
    sig = ChannelMidlineStrategy().generate(df)
    assert sig.action == Action.SELL
    assert "midline" in sig.reasoning.lower()


# ── 10. HIGH confidence 테스트 (채널 확장 시) ────────────────────────────
def test_high_confidence_wide_channel():
    df = _make_buy_df(wide_channel=True)
    sig = ChannelMidlineStrategy().generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 11. MEDIUM confidence 테스트 (채널 평범) ─────────────────────────────
def test_medium_confidence_normal_channel():
    df = _make_buy_df(wide_channel=False)
    sig = ChannelMidlineStrategy().generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 12. entry_price > 0 ───────────────────────────────────────────────────
def test_entry_price_positive():
    df = _make_buy_df(wide_channel=False)
    sig = ChannelMidlineStrategy().generate(df)
    assert sig.entry_price > 0


# ── 13. strategy 필드 값 확인 ────────────────────────────────────────────
def test_strategy_field_value():
    df = _make_df(n=50)
    sig = ChannelMidlineStrategy().generate(df)
    assert sig.strategy == "channel_midline"


# ── 14. 최소 행 수(25)에서 동작 ──────────────────────────────────────────
def test_minimum_rows_works():
    df = _make_df(n=25)
    sig = ChannelMidlineStrategy().generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
