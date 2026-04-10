"""
RangeTradingStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.range_trading import RangeTradingStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 30, close_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    df = pd.DataFrame({
        "open":   [100.0] * n,
        "high":   [105.0] * n,
        "low":    [95.0]  * n,
        "close":  close_values,
        "volume": [1000.0] * n,
    })
    return df


def _make_buy_df(rsi_level: str = "medium") -> pd.DataFrame:
    """
    BUY 조건: close < range_low + range_width * 0.2  AND  rsi < 40

    RSI는 14기간 평균 gain/loss 비율. 중간 RSI(30-40)를 얻으려면
    gain과 loss가 적당히 섞여야 함.

    설계: n=30, 완성 캔들 idx=28
    - range를 확보하기 위해 윈도우 [9..28] 내에 range_high=110, range_low=75 넣기
    - 완성 캔들 close를 buy_zone 아래에 배치
    - RSI 조정: medium(30~40)은 하락 중 반등 혼합, high(<30)는 연속 하락
    """
    n = 30
    closes = [100.0] * n

    if rsi_level == "medium":
        # 앞부분 안정 구간
        for i in range(0, 9):
            closes[i] = 100.0
        # 윈도우 내: 한 번 spike up(110), 그 다음 하락, 반등 혼합
        closes[9]  = 110.0   # range_high
        closes[10] = 105.0
        closes[11] = 95.0
        closes[12] = 100.0
        closes[13] = 90.0
        closes[14] = 95.0
        closes[15] = 88.0
        closes[16] = 92.0
        closes[17] = 85.0
        closes[18] = 89.0
        closes[19] = 83.0
        closes[20] = 87.0
        closes[21] = 80.0   # range_low
        closes[22] = 84.0
        closes[23] = 80.5
        closes[24] = 83.0
        closes[25] = 79.0
        closes[26] = 82.0
        closes[27] = 78.0   # range_low 갱신
        # range_low=78, range_high=110, rw=32, buy_zone=78+6.4=84.4
        closes[-2] = 82.0   # 82 < 84.4 ✓, RSI ~35 (하락 우세)
        closes[-1] = 85.0
    else:  # high: rsi < 30 (연속 하락)
        for i in range(0, 9):
            closes[i] = 100.0
        closes[9] = 110.0   # range_high
        # 연속 하락 → RSI < 30
        for i in range(10, 28):
            closes[i] = 110.0 - (i - 9) * 2.0
        # bars 10..27: 108, 106, ... → 74
        # range_low = 74, range_high=110, rw=36, buy_zone=74+7.2=81.2
        closes[-2] = 79.0   # 79 < 81.2 ✓
        closes[-1] = 82.0

    return _make_df(n=n, close_values=closes)


def _make_sell_df(rsi_level: str = "medium") -> pd.DataFrame:
    """
    SELL 조건: close > range_high - range_width * 0.2  AND  rsi > 60
    """
    n = 30
    closes = [100.0] * n

    if rsi_level == "medium":
        for i in range(0, 9):
            closes[i] = 100.0
        # 윈도우 내: spike down(90), 그 다음 상승, 하락 혼합
        closes[9]  = 90.0    # range_low
        closes[10] = 95.0
        closes[11] = 105.0
        closes[12] = 100.0
        closes[13] = 110.0
        closes[14] = 105.0
        closes[15] = 112.0
        closes[16] = 108.0
        closes[17] = 115.0
        closes[18] = 111.0
        closes[19] = 117.0
        closes[20] = 113.0
        closes[21] = 120.0   # range_high
        closes[22] = 116.0
        closes[23] = 119.5
        closes[24] = 117.0
        closes[25] = 121.0
        closes[26] = 118.0
        closes[27] = 122.0   # range_high 갱신
        # range_high=122, range_low=90, rw=32, sell_zone=122-6.4=115.6
        closes[-2] = 118.0   # 118 > 115.6 ✓, RSI ~65 (상승 우세)
        closes[-1] = 115.0
    else:  # high: rsi > 70 (연속 상승)
        for i in range(0, 9):
            closes[i] = 100.0
        closes[9] = 90.0    # range_low
        # 연속 상승 → RSI > 70
        for i in range(10, 28):
            closes[i] = 90.0 + (i - 9) * 2.0
        # bars 10..27: 92, 94, ... → 126
        # range_high=126, range_low=90, rw=36, sell_zone=126-7.2=118.8
        closes[-2] = 121.0   # 121 > 118.8 ✓
        closes[-1] = 118.0

    return _make_df(n=n, close_values=closes)


# ── 기본 ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert RangeTradingStrategy().name == "range_trading"


def test_insufficient_data_returns_hold():
    s = RangeTradingStrategy()
    df = _make_df(n=15)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_insufficient_data_exact_boundary():
    s = RangeTradingStrategy()
    df = _make_df(n=19)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_minimum_rows_passes():
    """20행이면 처리 진행 (HOLD 혹은 신호)"""
    s = RangeTradingStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


# ── BUY 시그널 ───────────────────────────────────────────────────────────────

def test_buy_medium_confidence():
    s = RangeTradingStrategy()
    df = _make_buy_df(rsi_level="medium")
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM
    assert sig.strategy == "range_trading"


def test_buy_high_confidence():
    s = RangeTradingStrategy()
    df = _make_buy_df(rsi_level="high")
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_buy_entry_price_equals_close():
    s = RangeTradingStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_buy_reasoning_contains_keywords():
    s = RangeTradingStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "rsi" in sig.reasoning.lower() or "range" in sig.reasoning.lower()


# ── SELL 시그널 ──────────────────────────────────────────────────────────────

def test_sell_medium_confidence():
    s = RangeTradingStrategy()
    df = _make_sell_df(rsi_level="medium")
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM
    assert sig.strategy == "range_trading"


def test_sell_high_confidence():
    s = RangeTradingStrategy()
    df = _make_sell_df(rsi_level="high")
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


def test_sell_entry_price_equals_close():
    s = RangeTradingStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_sell_reasoning_contains_keywords():
    s = RangeTradingStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "rsi" in sig.reasoning.lower() or "range" in sig.reasoning.lower()


# ── HOLD 케이스 ──────────────────────────────────────────────────────────────

def test_hold_flat_prices():
    """모든 가격 동일 → range_width=0 → buy/sell zone 조건 불충족"""
    s = RangeTradingStrategy()
    df = _make_df(n=30, close_values=[100.0] * 30)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_mid_range_price():
    """close가 횡보 중간에 있으면 어떤 조건도 불충족"""
    s = RangeTradingStrategy()
    n = 30
    closes = [90.0] * 10 + [110.0] * 10 + [100.0] * 10
    closes[-1] = 100.0
    df = _make_df(n=n, close_values=closes)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_hold_action_is_hold_enum():
    s = RangeTradingStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_signal_has_all_fields():
    """Signal 객체가 필수 필드를 모두 가짐"""
    s = RangeTradingStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert hasattr(sig, "action")
    assert hasattr(sig, "confidence")
    assert hasattr(sig, "strategy")
    assert hasattr(sig, "entry_price")
    assert hasattr(sig, "reasoning")
    assert hasattr(sig, "invalidation")
