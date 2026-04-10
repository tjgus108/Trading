"""tests/test_overextension.py — OverextensionStrategy 단위 테스트 (12개)"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.overextension import OverextensionStrategy
from src.strategy.base import Action, Confidence


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_df(n: int = 100, close=None) -> pd.DataFrame:
    if close is None:
        close = np.linspace(100, 110, n)
    close = np.array(close, dtype=float)
    return pd.DataFrame({
        "open": close - 1,
        "close": close,
        "high": close + 2,
        "low": close - 2,
        "volume": np.ones(n) * 1000,
    })


def _buy_df(n: int = 100) -> pd.DataFrame:
    """
    BUY 신호 유발: overextended_down AND close rising.
    close를 안정적 기준(100) 부근으로 유지하다가 마지막 두 봉에서
    EMA50 대비 -3σ 이상 이탈 후 복귀(close 상승).
    """
    # 처음 n-5 봉: 안정적 (100 근처)
    close = np.ones(n) * 100.0
    # 약간의 변동으로 dist_std가 0이 되지 않도록
    rng = np.random.default_rng(42)
    close[: n - 10] += rng.uniform(-0.5, 0.5, n - 10)
    # 마지막 두 봉 직전 (n-3): 큰 하락 → overextended_down
    close[n - 3] = 60.0  # EMA50 ≈ 100 → dist ≈ -40% >> 2σ
    close[n - 2] = 62.0  # 복귀 시작 (close 상승)
    close[n - 1] = 63.0  # 현재 진행봉 (무시됨)
    return _make_df(n=n, close=close)


def _sell_df(n: int = 100) -> pd.DataFrame:
    """
    SELL 신호 유발: overextended_up AND close falling.
    """
    close = np.ones(n) * 100.0
    rng = np.random.default_rng(7)
    close[: n - 10] += rng.uniform(-0.5, 0.5, n - 10)
    close[n - 3] = 140.0  # EMA50 ≈ 100 → dist ≈ +40% >> 2σ
    close[n - 2] = 138.0  # 복귀 시작 (close 하락)
    close[n - 1] = 137.0
    return _make_df(n=n, close=close)


# ── 테스트 ───────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 = 'overextension'"""
    assert OverextensionStrategy.name == "overextension"


def test_buy_signal():
    """2. BUY 신호 발생 (과매도 구간, close 상승)"""
    strat = OverextensionStrategy()
    sig = strat.generate(_buy_df())
    assert sig.action == Action.BUY


def test_sell_signal():
    """3. SELL 신호 발생 (과매수 구간, close 하락)"""
    strat = OverextensionStrategy()
    sig = strat.generate(_sell_df())
    assert sig.action == Action.SELL


def test_insufficient_data_returns_hold():
    """4. 데이터 부족 (74행) → HOLD"""
    strat = OverextensionStrategy()
    df = _make_df(n=74)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_no_overextension_is_hold():
    """5. 과신장 없음 → HOLD"""
    strat = OverextensionStrategy()
    # close가 EMA50 근처에서 유지되어 dist ≈ 0
    close = np.ones(100) * 100.0
    df = _make_df(n=100, close=close)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_overextended_down_but_falling_is_hold():
    """6. 과매도이지만 close 하락 중 → HOLD (복귀 아직 시작 안 됨)"""
    strat = OverextensionStrategy()
    close = np.ones(100) * 100.0
    rng = np.random.default_rng(1)
    close[:90] += rng.uniform(-0.5, 0.5, 90)
    close[97] = 60.0   # overextended down
    close[98] = 58.0   # close 계속 하락 → 복귀 아님
    close[99] = 57.0
    df = _make_df(n=100, close=close)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_overextended_up_but_rising_is_hold():
    """7. 과매수이지만 close 상승 중 → HOLD (복귀 아직 시작 안 됨)"""
    strat = OverextensionStrategy()
    close = np.ones(100) * 100.0
    rng = np.random.default_rng(2)
    close[:90] += rng.uniform(-0.5, 0.5, 90)
    close[97] = 140.0
    close[98] = 142.0  # close 계속 상승 → 복귀 아님
    close[99] = 143.0
    df = _make_df(n=100, close=close)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_buy_high_confidence():
    """8. BUY HIGH confidence: |distance| > dist_std * 3"""
    strat = OverextensionStrategy()
    # 매우 큰 이탈 → 3σ 초과
    close = np.ones(100) * 100.0
    rng = np.random.default_rng(3)
    close[:90] += rng.uniform(-0.5, 0.5, 90)
    close[97] = 10.0   # 극단적 하락 (-90% dist)
    close[98] = 12.0   # 복귀
    close[99] = 13.0
    df = _make_df(n=100, close=close)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_sell_high_confidence():
    """9. SELL HIGH confidence: |distance| > dist_std * 3"""
    strat = OverextensionStrategy()
    close = np.ones(100) * 100.0
    rng = np.random.default_rng(4)
    close[:90] += rng.uniform(-0.5, 0.5, 90)
    close[97] = 300.0  # 극단적 상승
    close[98] = 295.0  # 복귀
    close[99] = 294.0
    df = _make_df(n=100, close=close)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


def test_signal_strategy_name():
    """10. Signal.strategy 필드 = 'overextension'"""
    strat = OverextensionStrategy()
    sig = strat.generate(_buy_df())
    assert sig.strategy == "overextension"


def test_signal_fields_complete():
    """11. Signal 필드 완전성 확인"""
    strat = OverextensionStrategy()
    sig = strat.generate(_buy_df())
    assert sig.action == Action.BUY
    assert isinstance(sig.entry_price, float)
    assert sig.reasoning != ""
    assert "Overextension" in sig.reasoning
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


def test_hold_reasoning_not_empty():
    """12. HOLD 신호도 reasoning 필드가 비어있지 않음"""
    strat = OverextensionStrategy()
    df = _make_df(n=100)
    sig = strat.generate(df)
    assert sig.reasoning != ""
