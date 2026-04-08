"""
BBReversionStrategy 단위 테스트 (mock DataFrame만 사용)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.bb_reversion import BBReversionStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 30, close_values=None, rsi_values=None) -> pd.DataFrame:
    """
    간단한 mock DataFrame 생성.
    close_values / rsi_values: 마지막 n개 값(리스트). None이면 flat 기본값.
    주의: strategy._last()는 iloc[-2]를 사용하므로 마지막 행은 진행 중 캔들.
    """
    if close_values is None:
        close_values = [100.0] * n
    if rsi_values is None:
        rsi_values = [50.0] * n

    df = pd.DataFrame({
        "open":   [100.0] * n,
        "high":   [105.0] * n,
        "low":    [95.0]  * n,
        "close":  close_values,
        "volume": [1000.0] * n,
        "ema20":  [100.0]  * n,
        "rsi14":  rsi_values,
    })
    return df


def _flat_then(base: float, n: int, last_val: float) -> list:
    """마지막 두 값만 달라지는 리스트 생성. [-2]가 last_val, [-1]은 base."""
    vals = [base] * n
    vals[-2] = last_val
    vals[-1] = base  # 진행 중 캔들은 base
    return vals


# ── 기본 인스턴스 ────────────────────────────────────────────────────────────

def test_strategy_name():
    s = BBReversionStrategy()
    assert s.name == "bb_reversion"


# ── 데이터 부족 ──────────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = BBReversionStrategy()
    df = _make_df(n=20)  # < 25
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# ── BUY 시그널 ───────────────────────────────────────────────────────────────

def test_buy_medium_confidence():
    """close < lower_band AND 30 <= rsi < 40 → BUY MEDIUM"""
    s = BBReversionStrategy()
    n = 30

    # BB lower = mean - 2*std. flat 가격에서 한 캔들만 크게 낮추면 lower보다 더 낮음.
    # 대신 BB를 직접 제어하기 쉽게: 안정적 값 후 마지막 완성 캔들을 급락시킴.
    base = 100.0
    closes = [base] * n
    # iloc[-2] (완성 캔들) = 매우 낮은 값 → BB lower 아래
    closes[-2] = 75.0  # 평균 ~100, std~0에 가까우나 이 값만 극단적

    rsis = [35.0] * n  # 30 <= rsi < 40

    df = _make_df(n=n, close_values=closes, rsi_values=rsis)
    sig = s.generate(df)

    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM
    assert sig.strategy == "bb_reversion"


def test_buy_high_confidence():
    """close < lower_band AND rsi < 30 → BUY HIGH"""
    s = BBReversionStrategy()
    n = 30
    closes = [100.0] * n
    closes[-2] = 75.0
    rsis = [25.0] * n

    df = _make_df(n=n, close_values=closes, rsi_values=rsis)
    sig = s.generate(df)

    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── SELL 시그널 ──────────────────────────────────────────────────────────────

def test_sell_medium_confidence():
    """close > upper_band AND 60 < rsi <= 70 → SELL MEDIUM"""
    s = BBReversionStrategy()
    n = 30
    closes = [100.0] * n
    closes[-2] = 125.0  # 평균~100, 이 값만 상단 위
    rsis = [65.0] * n  # 60 < rsi <= 70

    df = _make_df(n=n, close_values=closes, rsi_values=rsis)
    sig = s.generate(df)

    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM
    assert sig.strategy == "bb_reversion"


def test_sell_high_confidence():
    """close > upper_band AND rsi > 70 → SELL HIGH"""
    s = BBReversionStrategy()
    n = 30
    closes = [100.0] * n
    closes[-2] = 125.0
    rsis = [75.0] * n

    df = _make_df(n=n, close_values=closes, rsi_values=rsis)
    sig = s.generate(df)

    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── HOLD 케이스 ──────────────────────────────────────────────────────────────

def test_hold_when_close_below_band_but_rsi_neutral():
    """close < lower_band이지만 rsi >= 40 → HOLD"""
    s = BBReversionStrategy()
    n = 30
    closes = [100.0] * n
    closes[-2] = 75.0  # lower band 아래
    rsis = [50.0] * n  # rsi >= 40 → BUY 조건 불충족

    df = _make_df(n=n, close_values=closes, rsi_values=rsis)
    sig = s.generate(df)

    assert sig.action == Action.HOLD


def test_hold_when_rsi_oversold_but_price_in_band():
    """rsi < 40이지만 close가 band 안쪽 → HOLD"""
    s = BBReversionStrategy()
    n = 30
    # 모든 가격 동일 → std≈0 → band가 거의 mid와 같음
    # 하지만 완성 캔들 close=100이면 lower와 같거나 위 → BUY 안 됨
    closes = [100.0] * n
    rsis = [35.0] * n

    df = _make_df(n=n, close_values=closes, rsi_values=rsis)
    sig = s.generate(df)

    assert sig.action == Action.HOLD


def test_hold_normal_conditions():
    """정상 시장 (close 밴드 내, rsi 중립) → HOLD"""
    s = BBReversionStrategy()
    n = 30

    # 가격 변동이 있어야 std > 0, band가 의미 있음
    closes = list(np.linspace(95, 105, n))
    closes[-1] = 100.0  # 진행 중 캔들
    # 완성 캔들([-2])은 midband 근처 → HOLD
    rsis = [50.0] * n

    df = _make_df(n=n, close_values=closes, rsi_values=rsis)
    sig = s.generate(df)

    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── entry_price 확인 ─────────────────────────────────────────────────────────

def test_entry_price_equals_last_close():
    """entry_price는 항상 iloc[-2]의 close 값이어야 함"""
    s = BBReversionStrategy()
    n = 30
    closes = [100.0] * n
    closes[-2] = 75.0
    rsis = [25.0] * n

    df = _make_df(n=n, close_values=closes, rsi_values=rsis)
    sig = s.generate(df)

    assert sig.entry_price == pytest.approx(75.0)
