"""DoubleTopBottomStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.double_top_bottom import DoubleTopBottomStrategy

strategy = DoubleTopBottomStrategy()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _base_df(n=60):
    """평탄한 기본 DataFrame."""
    np.random.seed(42)
    base = np.full(n, 100.0)
    df = pd.DataFrame({
        "open":   base,
        "close":  base + np.random.uniform(-0.05, 0.05, n),
        "high":   base + 0.5,
        "low":    base - 0.5,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_double_bottom_df():
    """
    Double Bottom 패턴 DataFrame (n=60).
    window = iloc[-22:-1] = abs indices 38-58 → relative 0-20 (21 rows).
    pivot low1 at relative idx=5 (abs=43), pivot low2 at relative idx=13 (abs=51).
    neckline = max(close[5:14]) ~ 102, placed at relative idx 9 (abs=47).
    iloc[-2] (abs=58, relative=20) close=103.5 → 넥라인 돌파 (>1%).
    """
    n = 60
    # 기본값: 100
    close = np.full(n, 100.0)
    high  = np.full(n, 101.0)
    low   = np.full(n, 99.0)

    # window starts at abs index 38
    # relative positions within window (0-20)
    # abs = 38 + rel

    # low1 at relative=5 (abs=43): clear valley, lows[5]=93, surrounding higher
    # set abs 40-46 with valley at 43
    for rel in range(2, 9):   # abs 40-46
        ab = 38 + rel
        v = 93.0 + abs(rel - 5) * 2.0  # valley at rel=5 → 93
        close[ab] = v
        low[ab]   = v - 0.3
        high[ab]  = v + 0.3

    # neckline zone at relative 9 (abs=47): close=102
    for rel in range(8, 10):  # abs 46-47
        ab = 38 + rel
        close[ab] = 102.0
        high[ab]  = 102.5
        low[ab]   = 101.5

    # low2 at relative=13 (abs=51): clear valley similar to low1
    for rel in range(10, 17):  # abs 48-54
        ab = 38 + rel
        v = 93.5 + abs(rel - 13) * 2.0
        close[ab] = v
        low[ab]   = v - 0.3
        high[ab]  = v + 0.3

    # abs 55-57 (rel 17-19): rise toward neckline
    for ab in range(55, 58):
        close[ab] = 100.0
        high[ab]  = 100.5
        low[ab]   = 99.5

    # iloc[-2] = abs 58 (rel 20): close=103.5, well above neckline 102
    close[58] = 103.5
    high[58]  = 104.0
    low[58]   = 103.0

    # iloc[-1] = abs 59 (ongoing)
    close[59] = 103.6
    high[59]  = 104.1
    low[59]   = 103.1

    # abs 0-37: flat at 100
    for ab in range(0, 38):
        close[ab] = 100.0
        high[ab]  = 100.5
        low[ab]   = 99.5

    return pd.DataFrame({
        "open":   close - 0.1,
        "close":  close,
        "high":   high,
        "low":    low,
        "volume": np.ones(n) * 1000,
    })


def _make_double_top_df():
    """
    Double Top 패턴 DataFrame (n=60).
    window = iloc[-22:-1] = abs indices 38-58 → relative 0-20 (21 rows).
    pivot high1 at relative=5 (abs=43), pivot high2 at relative=13 (abs=51).
    neckline = min(close[5:14]) ~ 98, placed at relative idx 9 (abs=47).
    iloc[-2] (abs=58) close=96.5 → 넥라인 하향 돌파 (>1%).
    """
    n = 60
    close = np.full(n, 100.0)
    high  = np.full(n, 101.0)
    low   = np.full(n, 99.0)

    # high1 at relative=5 (abs=43): clear peak, highs[5]=108
    for rel in range(2, 9):
        ab = 38 + rel
        v = 108.0 - abs(rel - 5) * 2.0
        close[ab] = v
        high[ab]  = v + 0.3
        low[ab]   = v - 0.3

    # neckline zone at relative 9 (abs=47): close=98
    for rel in range(8, 10):
        ab = 38 + rel
        close[ab] = 98.0
        high[ab]  = 98.5
        low[ab]   = 97.5

    # high2 at relative=13 (abs=51): clear peak similar to high1
    for rel in range(10, 17):
        ab = 38 + rel
        v = 108.5 - abs(rel - 13) * 2.0
        close[ab] = v
        high[ab]  = v + 0.3
        low[ab]   = v - 0.3

    # abs 55-57 (rel 17-19): drop toward neckline
    for ab in range(55, 58):
        close[ab] = 100.0
        high[ab]  = 100.5
        low[ab]   = 99.5

    # iloc[-2] = abs 58 (rel 20): close=96.5, well below neckline 98
    close[58] = 96.5
    high[58]  = 97.0
    low[58]   = 96.0

    # iloc[-1] = abs 59 (ongoing)
    close[59] = 96.4
    high[59]  = 96.9
    low[59]   = 95.9

    # abs 0-37: flat at 100
    for ab in range(0, 38):
        close[ab] = 100.0
        high[ab]  = 100.5
        low[ab]   = 99.5

    return pd.DataFrame({
        "open":   close - 0.1,
        "close":  close,
        "high":   high,
        "low":    low,
        "volume": np.ones(n) * 1000,
    })


# ── 테스트 ────────────────────────────────────────────────────────────────────

# 1. 전략 이름
def test_strategy_name():
    assert strategy.name == "double_top_bottom"


# 2. 데이터 부족 → HOLD
def test_insufficient_data_returns_hold():
    df = _base_df(10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# 3. 최소 경계 데이터 (24행) → HOLD
def test_min_boundary_returns_hold():
    df = _base_df(24)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# 4. None 입력 → HOLD
def test_none_input_returns_hold():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# 5. 평탄한 데이터 → HOLD (패턴 없음)
def test_flat_data_returns_hold():
    df = _base_df(60)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# 6. Double Bottom → BUY
def test_double_bottom_returns_buy():
    df = _make_double_bottom_df()
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# 7. Double Bottom → strategy 이름 확인
def test_double_bottom_strategy_name():
    df = _make_double_bottom_df()
    sig = strategy.generate(df)
    assert sig.strategy == "double_top_bottom"


# 8. Double Bottom → entry_price 양수
def test_double_bottom_entry_price_positive():
    df = _make_double_bottom_df()
    sig = strategy.generate(df)
    assert sig.entry_price > 0


# 9. Double Top → SELL
def test_double_top_returns_sell():
    df = _make_double_top_df()
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# 10. Double Top → strategy 이름 확인
def test_double_top_strategy_name():
    df = _make_double_top_df()
    sig = strategy.generate(df)
    assert sig.strategy == "double_top_bottom"


# 11. Double Top → entry_price 양수
def test_double_top_entry_price_positive():
    df = _make_double_top_df()
    sig = strategy.generate(df)
    assert sig.entry_price > 0


# 12. Signal 필드 완전성 확인 (BUY)
def test_buy_signal_has_required_fields():
    df = _make_double_bottom_df()
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert sig.reasoning != ""
    assert sig.strategy == "double_top_bottom"


# 13. Signal 필드 완전성 확인 (SELL)
def test_sell_signal_has_required_fields():
    df = _make_double_top_df()
    sig = strategy.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert sig.reasoning != ""


# 14. _last(df) 패턴 확인 (df.iloc[-2])
def test_last_returns_second_to_last():
    df = _base_df(10)
    last = strategy._last(df)
    pd.testing.assert_series_equal(last, df.iloc[-2])


# 15. 단조 상승 데이터 → HOLD
def test_monotone_rising_returns_hold():
    n = 60
    close = np.linspace(90, 110, n)
    df = pd.DataFrame({
        "open":   close,
        "close":  close,
        "high":   close + 1,
        "low":    close - 1,
        "volume": np.ones(n) * 1000,
    })
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
