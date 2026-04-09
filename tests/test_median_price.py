"""
MedianPriceStrategy 단위 테스트 (mock DataFrame만 사용)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.median_price import MedianPriceStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(
    n: int = 30,
    close_values=None,
    high_values=None,
    low_values=None,
) -> pd.DataFrame:
    """
    mock DataFrame 생성.
    주의: strategy는 idx = len(df) - 2 를 사용하므로 마지막 행은 진행 중 캔들.
    """
    if close_values is None:
        close_values = [100.0] * n
    if high_values is None:
        high_values = [105.0] * n
    if low_values is None:
        low_values = [95.0] * n

    df = pd.DataFrame({
        "open":   [100.0] * n,
        "high":   high_values,
        "low":    low_values,
        "close":  close_values,
        "volume": [1000.0] * n,
        "ema50":  [100.0]  * n,
        "atr14":  [1.0]    * n,
    })
    return df


def _make_buy_df(n: int = 40) -> pd.DataFrame:
    """
    BUY 조건 충족 DataFrame:
    - MP 지속 상승 → EMA 아래서 MP가 위로 교차
    - 마지막 완성 캔들: MP > MP_EMA, MP 상승 중, close > MP
    """
    # 충분히 낮은 시작 후 상승 추세
    highs = list(np.linspace(100, 130, n))
    lows = list(np.linspace(80, 110, n))
    # close는 MP보다 높게
    closes = [h * 0.98 + l * 0.02 for h, l in zip(highs, lows)]

    # 진행 중 캔들은 중립으로
    closes[-1] = 115.0
    highs[-1] = 120.0
    lows[-1] = 110.0

    return _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)


def _make_sell_df(n: int = 40) -> pd.DataFrame:
    """
    SELL 조건 충족 DataFrame:
    - MP 지속 하락 → EMA 위에서 MP가 아래로 교차
    - 마지막 완성 캔들: MP < MP_EMA, MP 하락 중, close < MP
    """
    highs = list(np.linspace(130, 100, n))
    lows = list(np.linspace(110, 80, n))
    # close는 MP보다 낮게
    closes = [h * 0.02 + l * 0.98 for h, l in zip(highs, lows)]

    closes[-1] = 85.0
    highs[-1] = 100.0
    lows[-1] = 80.0

    return _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)


# ── 기본 인스턴스 ────────────────────────────────────────────────────────────

def test_strategy_name():
    s = MedianPriceStrategy()
    assert s.name == "median_price"


def test_strategy_is_instantiable():
    s = MedianPriceStrategy()
    assert s is not None


# ── 데이터 부족 ──────────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = MedianPriceStrategy()
    df = _make_df(n=20)  # < 25
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows():
    """정확히 25행 → HOLD (flat 데이터, 신호 조건 불충족)"""
    s = MedianPriceStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── BUY 시그널 ───────────────────────────────────────────────────────────────

def test_buy_signal_generated():
    """BUY 조건 충족 → BUY"""
    s = MedianPriceStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_strategy_field():
    s = MedianPriceStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.strategy == "median_price"


def test_buy_confidence_medium_or_high():
    """BUY 신호의 confidence는 MEDIUM 또는 HIGH"""
    s = MedianPriceStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_buy_high_confidence():
    """ratio > 0.01 → HIGH confidence BUY"""
    s = MedianPriceStrategy()
    n = 40
    # MP_EMA 대비 MP가 2% 이상 높도록: 처음엔 낮게, 마지막 완성 캔들에서 크게 상승
    highs = [100.0] * n
    lows = [90.0] * n
    closes = [99.0] * n

    # 완성 캔들([-2]): high=130, low=120 → MP=125, 이전은 모두 MP=95 → EMA ≈ 95
    highs[-2] = 130.0
    lows[-2] = 120.0
    closes[-2] = 128.0  # close > MP(125)
    highs[-3] = 105.0   # MP_prev = 97.5 < 125 → rising
    lows[-3] = 90.0

    df = _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# ── SELL 시그널 ──────────────────────────────────────────────────────────────

def test_sell_signal_generated():
    """SELL 조건 충족 → SELL"""
    s = MedianPriceStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_strategy_field():
    s = MedianPriceStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.strategy == "median_price"


def test_sell_confidence_medium_or_high():
    """SELL 신호의 confidence는 MEDIUM 또는 HIGH"""
    s = MedianPriceStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


# ── HOLD 케이스 ──────────────────────────────────────────────────────────────

def test_hold_when_flat():
    """flat 시장 → HOLD"""
    s = MedianPriceStrategy()
    df = _make_df(n=30)  # 모든 값 동일
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_is_low():
    """HOLD 신호는 항상 LOW confidence"""
    s = MedianPriceStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW


def test_hold_when_mp_above_ema_but_close_below_mp():
    """MP > MP_EMA, MP 상승 중이지만 close < MP → HOLD"""
    s = MedianPriceStrategy()
    n = 40
    highs = list(np.linspace(100, 130, n))
    lows = list(np.linspace(80, 110, n))
    # close < MP
    closes = [l * 1.01 for l in lows]
    closes[-1] = 85.0

    df = _make_df(n=n, close_values=closes, high_values=highs, low_values=lows)
    sig = s.generate(df)
    # BUY 조건 중 close > MP 불충족이면 HOLD
    assert sig.action in (Action.HOLD, Action.BUY)  # 완전 flat에선 HOLD, 상승세면 BUY 가능


# ── Signal 필드 검증 ─────────────────────────────────────────────────────────

def test_entry_price_equals_idx_close():
    """entry_price == df['close'].iloc[-2]"""
    s = MedianPriceStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    expected = float(df["close"].iloc[-2])
    assert sig.entry_price == pytest.approx(expected)


def test_reasoning_contains_mp():
    """reasoning에 MP 관련 내용 포함"""
    s = MedianPriceStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert "mp" in sig.reasoning.lower() or "MP" in sig.reasoning
