"""
VolatilityMeanReversionStrategy 단위 테스트 (mock DataFrame만 사용)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.vol_mean_rev import VolatilityMeanReversionStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, close_vals=None) -> pd.DataFrame:
    """기본 mock DataFrame. iloc[-2]가 완성 캔들."""
    if close_vals is None:
        # 모두 동일하면 hist_vol=0, vol_ratio=NaN → HOLD 보장
        close_vals = [100.0] * n
    opens = [c * 0.999 for c in close_vals]
    highs = [c * 1.001 for c in close_vals]
    lows  = [c * 0.998 for c in close_vals]
    df = pd.DataFrame({
        "open":   opens,
        "high":   highs,
        "low":    lows,
        "close":  close_vals,
        "volume": [1000.0] * n,
    })
    return df


def _make_neutral_vol_df(n: int = 80) -> pd.DataFrame:
    """
    vol_ratio가 0.5~2 범위(중간 변동성) + RSI 40~60 → HOLD 조건.
    """
    np.random.seed(7)
    closes = []
    price = 100.0
    # 균일한 작은 진동 (일정한 변동성)
    for i in range(n):
        price += np.random.uniform(-0.5, 0.5)
        closes.append(max(price, 50.0))
    return _make_df(n=n, close_vals=closes)


def _make_low_vol_bull_df(n: int = 80) -> pd.DataFrame:
    """
    저변동성 + 상승 추세 → BUY 조건.
    hist_vol을 낮추기 위해 close 변화 거의 없음.
    vol_ratio < 0.5: 앞부분 변동성 높게, 뒷부분 낮게.
    close > SMA20 유지.
    """
    # 앞 50봉: 큰 변동 (높은 hist_vol 평균 만들기)
    np.random.seed(42)
    closes = []
    price = 100.0
    for i in range(50):
        price += np.random.choice([-5.0, 5.0])
        closes.append(price)

    # 뒤 n-50봉: 작은 변동 + 상승 추세 (낮은 hist_vol)
    price = max(closes) + 10  # SMA20보다 높은 수준 시작
    for i in range(n - 50):
        price += 0.01  # 거의 변화 없음
        closes.append(price)

    return _make_df(n=n, close_vals=closes)


def _make_low_vol_bear_df(n: int = 80) -> pd.DataFrame:
    """
    저변동성 + 하락 추세 → SELL 조건.
    """
    np.random.seed(42)
    closes = []
    price = 200.0
    for i in range(50):
        price += np.random.choice([-5.0, 5.0])
        closes.append(price)

    # 뒷부분 하락 + 낮은 변동성
    price = min(closes) - 10  # SMA20보다 낮게
    for i in range(n - 50):
        price -= 0.01
        closes.append(price)

    return _make_df(n=n, close_vals=closes)


def _make_high_vol_oversold_df(n: int = 100) -> pd.DataFrame:
    """
    고변동성 + RSI < 40 → BUY 조건.
    전략 로직: vol_ratio > 2 AND rsi14 < 40.
    앞 n-15봉: 매우 안정적(hist_vol 평균 낮게),
    마지막 15봉: 급격한 하락(RSI < 40)이면서 큰 진동(vol_ratio 높게).
    """
    closes = []
    price = 200.0
    stable_count = n - 15
    # 안정적 구간
    for i in range(stable_count):
        price += 0.01
        closes.append(price)
    # 큰 하락 진동 (RSI < 40 + vol_ratio > 2)
    # 급격한 하락 후 반등 패턴: 하락 폭이 커서 RSI 낮음, 변동도 큼
    for i in range(15):
        if i % 3 == 0:
            price -= 20.0  # 급락
        elif i % 3 == 1:
            price += 5.0   # 소폭 반등
        else:
            price -= 10.0  # 재하락
        closes.append(max(price, 10.0))

    return _make_df(n=n, close_vals=closes)


def _make_high_vol_overbought_df(n: int = 120) -> pd.DataFrame:
    """
    고변동성 + RSI > 60 → SELL 조건.
    전략 로직: vol_ratio > 2 AND rsi14 > 60.
    설계:
    - 앞 n-11봉: 소폭 일정 상승(hist_vol 낮고 일정 → vol_mean 작음)
    - 마지막 11봉: 불규칙 급상승(hist_vol >> vol_mean → vol_ratio >> 2, RSI > 60)
    완성봉(-2)은 10번째 진동봉.
    """
    np.random.seed(55)
    closes = []
    price = 100.0
    stable_count = n - 11
    # 안정적 소폭 상승 (pct_change ≈ 0.001씩 일정 → std≈0 → hist_vol 낮음)
    for i in range(stable_count):
        price *= 1.001
        closes.append(price)
    # 마지막 11봉: 큰 불규칙 상승
    for i in range(11):
        change = np.random.uniform(0.10, 0.25) if i % 5 != 4 else -0.05
        price *= (1 + change)
        closes.append(price)

    return _make_df(n=n, close_vals=closes)


# ── 기본 ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    s = VolatilityMeanReversionStrategy()
    assert s.name == "vol_mean_rev"


def test_instantiable():
    assert VolatilityMeanReversionStrategy() is not None


# ── 데이터 부족 ──────────────────────────────────────────────────────────────

def test_insufficient_data_hold():
    s = VolatilityMeanReversionStrategy()
    df = _make_df(n=40)  # < 45
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows():
    """정확히 45행 → 데이터 부족 아님, 신호 생성 시도"""
    s = VolatilityMeanReversionStrategy()
    df = _make_df(n=45)
    sig = s.generate(df)
    # 45행에서 NaN으로 인해 HOLD 또는 어떤 신호든 크래시 없이 반환
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


# ── BUY 신호 ─────────────────────────────────────────────────────────────────

def test_low_vol_buy_signal():
    """저변동성 + close > SMA20 → BUY"""
    s = VolatilityMeanReversionStrategy()
    df = _make_low_vol_bull_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_low_vol_buy_confidence():
    s = VolatilityMeanReversionStrategy()
    df = _make_low_vol_bull_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_high_vol_buy_signal():
    """고변동성 + RSI < 40 → BUY"""
    s = VolatilityMeanReversionStrategy()
    df = _make_high_vol_oversold_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_high_vol_buy_confidence_not_low():
    s = VolatilityMeanReversionStrategy()
    df = _make_high_vol_oversold_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


# ── SELL 신호 ────────────────────────────────────────────────────────────────

def test_low_vol_sell_signal():
    """저변동성 + close < SMA20 → SELL"""
    s = VolatilityMeanReversionStrategy()
    df = _make_low_vol_bear_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_low_vol_sell_confidence():
    s = VolatilityMeanReversionStrategy()
    df = _make_low_vol_bear_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_high_vol_sell_signal():
    """고변동성 + RSI > 60 → SELL"""
    s = VolatilityMeanReversionStrategy()
    df = _make_high_vol_overbought_df(n=100)
    sig = s.generate(df)
    assert sig.action == Action.SELL, f"expected SELL but got {sig.action}, reasoning={sig.reasoning}"


# ── HOLD ─────────────────────────────────────────────────────────────────────

def test_hold_neutral():
    """중간 변동성, vol_ratio 0.5~2 구간 → HOLD"""
    s = VolatilityMeanReversionStrategy()
    df = _make_neutral_vol_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_low():
    s = VolatilityMeanReversionStrategy()
    df = _make_neutral_vol_df(n=80)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW


# ── Signal 필드 검증 ─────────────────────────────────────────────────────────

def test_entry_price_equals_last_close():
    s = VolatilityMeanReversionStrategy()
    df = _make_low_vol_bull_df(n=80)
    sig = s.generate(df)
    expected = float(df["close"].iloc[-2])
    assert sig.entry_price == pytest.approx(expected)


def test_signal_strategy_field():
    s = VolatilityMeanReversionStrategy()
    df = _make_low_vol_bull_df(n=80)
    sig = s.generate(df)
    assert sig.strategy == "vol_mean_rev"


def test_reasoning_not_empty():
    s = VolatilityMeanReversionStrategy()
    df = _make_low_vol_bull_df(n=80)
    sig = s.generate(df)
    assert len(sig.reasoning) > 0
