"""
MeanReversionEntryStrategy 단위 테스트 (mock DataFrame만 사용)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.mr_entry import MeanReversionEntryStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 30, close_vals=None, open_vals=None, volume_vals=None) -> pd.DataFrame:
    """기본 mock DataFrame 생성. iloc[-2]가 완성 캔들."""
    if close_vals is None:
        close_vals = [100.0] * n
    if open_vals is None:
        open_vals = [100.0] * n
    if volume_vals is None:
        volume_vals = [1000.0] * n
    df = pd.DataFrame({
        "open":   open_vals,
        "high":   [max(c, o) + 1 for c, o in zip(close_vals, open_vals)],
        "low":    [min(c, o) - 1 for c, o in zip(close_vals, open_vals)],
        "close":  close_vals,
        "volume": volume_vals,
    })
    return df


def _make_buy_df(n: int = 30) -> pd.DataFrame:
    """
    BUY 조건 충족:
    - 최근 5봉 중 3봉 이상 음봉 (close < open)
    - rsi14 < 40 (연속 하락으로 유도)
    - volume > avg_vol (마지막 완성봉에서 볼륨 급등)
    """
    # 기본은 상승봉 (open=100, close=101), 마지막 완성봉 앞 5봉은 하락
    opens = [100.0] * n
    closes = [101.0] * n  # 기본 상승

    # 인덱스 [-2]가 완성봉. [-2], [-3], [-4], [-5], [-6] = 5봉
    # 이 중 3봉 음봉: [-2], [-3], [-4]
    for i in [-2, -3, -4, -5, -6]:
        closes[i] = 90.0   # 음봉 (close < open=100)

    # RSI를 낮추기 위해 앞부분도 하락 추세 추가
    for i in range(n - 10):
        opens[i] = 100.0
        closes[i] = 99.0   # 음봉

    # 볼륨: 기본 1000, 완성봉은 2000
    vols = [1000.0] * n
    vols[-2] = 2000.0

    return _make_df(n=n, close_vals=closes, open_vals=opens, volume_vals=vols)


def _make_sell_df(n: int = 30) -> pd.DataFrame:
    """
    SELL 조건 충족:
    - 최근 5봉 중 3봉 이상 양봉
    - rsi14 > 60
    - volume > avg_vol
    """
    opens = [100.0] * n
    closes = [99.0] * n  # 기본 하락

    # 앞부분 상승 추세 (RSI 높이기)
    for i in range(n - 10):
        closes[i] = 101.0

    # 마지막 5봉 중 3봉 양봉
    for i in [-2, -3, -4, -5, -6]:
        closes[i] = 110.0   # 양봉 (close > open=100)

    vols = [1000.0] * n
    vols[-2] = 2000.0

    return _make_df(n=n, close_vals=closes, open_vals=opens, volume_vals=vols)


# ── 기본 ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    s = MeanReversionEntryStrategy()
    assert s.name == "mr_entry"


def test_instantiable():
    assert MeanReversionEntryStrategy() is not None


# ── 데이터 부족 ──────────────────────────────────────────────────────────────

def test_insufficient_data_hold():
    s = MeanReversionEntryStrategy()
    df = _make_df(n=15)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows():
    """정확히 20행, 조건 미충족 → HOLD"""
    s = MeanReversionEntryStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    # 모두 동일가 → 신호 없음
    assert sig.action == Action.HOLD


# ── BUY 신호 ─────────────────────────────────────────────────────────────────

def test_buy_signal_generated():
    s = MeanReversionEntryStrategy()
    df = _make_buy_df(n=40)
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_confidence_not_low():
    s = MeanReversionEntryStrategy()
    df = _make_buy_df(n=40)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_buy_high_confidence_strong_conditions():
    """consecutive_down >= 4 AND rsi14 < 30 → HIGH"""
    n = 50
    opens = [100.0] * n
    closes = [99.0] * n  # 전체 하락으로 RSI 낮춤

    # 마지막 5봉 모두 음봉 (consecutive_down = 5 >= 4)
    for i in [-2, -3, -4, -5, -6]:
        closes[i] = 60.0  # 크게 내려서 rsi < 30

    vols = [1000.0] * n
    vols[-2] = 2000.0

    df = _make_df(n=n, close_vals=closes, open_vals=opens, volume_vals=vols)
    s = MeanReversionEntryStrategy()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_buy_no_signal_low_volume():
    """볼륨 미충족 → BUY 신호 없음"""
    n = 40
    opens = [100.0] * n
    closes = [99.0] * n
    for i in [-2, -3, -4, -5, -6]:
        closes[i] = 90.0
    # volume 낮게 (평균보다 작음)
    vols = [1000.0] * n
    vols[-2] = 500.0  # 평균보다 낮음

    df = _make_df(n=n, close_vals=closes, open_vals=opens, volume_vals=vols)
    s = MeanReversionEntryStrategy()
    sig = s.generate(df)
    # BUY가 아니거나 조건 미충족으로 HOLD
    assert sig.action != Action.BUY


# ── SELL 신호 ────────────────────────────────────────────────────────────────

def test_sell_signal_generated():
    s = MeanReversionEntryStrategy()
    df = _make_sell_df(n=40)
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_confidence_not_low():
    s = MeanReversionEntryStrategy()
    df = _make_sell_df(n=40)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


# ── HOLD ─────────────────────────────────────────────────────────────────────

def test_hold_neutral_market():
    """변화 없는 시장 → HOLD"""
    s = MeanReversionEntryStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_low():
    s = MeanReversionEntryStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW


# ── Signal 필드 검증 ─────────────────────────────────────────────────────────

def test_entry_price_equals_last_close():
    s = MeanReversionEntryStrategy()
    df = _make_buy_df(n=40)
    sig = s.generate(df)
    expected = float(df["close"].iloc[-2])
    assert sig.entry_price == pytest.approx(expected)


def test_signal_strategy_field():
    s = MeanReversionEntryStrategy()
    df = _make_buy_df(n=40)
    sig = s.generate(df)
    assert sig.strategy == "mr_entry"


def test_reasoning_not_empty():
    s = MeanReversionEntryStrategy()
    df = _make_buy_df(n=40)
    sig = s.generate(df)
    assert len(sig.reasoning) > 0
