"""ZLEMACrossStrategy 단위 테스트 (12개)."""

import pandas as pd
import pytest
from unittest.mock import patch

import src.strategy.zlema_cross as zlema_module
from src.strategy.base import Action, Confidence
from src.strategy.zlema_cross import ZLEMACrossStrategy, _zlema


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

N = 40


def _make_df(n: int = N, base: float = 100.0) -> pd.DataFrame:
    prices = [base] * n
    data = {
        "open": prices[:],
        "high": [p * 1.001 for p in prices],
        "low": [p * 0.999 for p in prices],
        "close": prices[:],
        "volume": [1000.0] * n,
        "ema50": prices[:],
        "atr14": [1.0] * n,
    }
    return pd.DataFrame(data)


def _mock_zlema(cross_up: bool, separation: float = 0.01):
    """
    원하는 크로스 방향과 이격을 반환하는 _zlema mock 생성.

    cross_up=True  → prev: z9 <= z21, now: z9 > z21
    cross_up=False → prev: z9 >= z21, now: z9 < z21
    """
    base = 100.0
    if cross_up:
        z9_prev = base - 1.0
        z21_prev = base
        z9_now = base * (1 + separation)
        z21_now = base
    else:
        z9_prev = base + 1.0
        z21_prev = base
        z9_now = base * (1 - separation)
        z21_now = base

    def _fake_zlema(series: pd.Series, period: int) -> pd.Series:
        n = len(series)
        idx = n - 2
        result = pd.Series([base] * n, dtype=float)
        if period == 9:
            result.iloc[idx - 1] = z9_prev
            result.iloc[idx] = z9_now
        else:  # period == 21
            result.iloc[idx - 1] = z21_prev
            result.iloc[idx] = z21_now
        return result

    return _fake_zlema


strat = ZLEMACrossStrategy()


# ── 테스트 ────────────────────────────────────────────────────────────────────

# 1. 전략 이름
def test_strategy_name():
    assert strat.name == "zlema_cross"


# 2. BUY 신호
def test_buy_signal():
    df = _make_df()
    with patch.object(zlema_module, "_zlema", side_effect=_mock_zlema(cross_up=True)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# 3. SELL 신호
def test_sell_signal():
    df = _make_df()
    with patch.object(zlema_module, "_zlema", side_effect=_mock_zlema(cross_up=False)):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# 4. BUY HIGH confidence (이격 > 0.5%)
def test_buy_high_confidence():
    df = _make_df()
    with patch.object(zlema_module, "_zlema", side_effect=_mock_zlema(cross_up=True, separation=0.01)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# 5. BUY MEDIUM confidence (이격 < 0.5%)
def test_buy_medium_confidence():
    df = _make_df()
    with patch.object(zlema_module, "_zlema", side_effect=_mock_zlema(cross_up=True, separation=0.002)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# 6. SELL HIGH confidence
def test_sell_high_confidence():
    df = _make_df()
    with patch.object(zlema_module, "_zlema", side_effect=_mock_zlema(cross_up=False, separation=0.01)):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# 7. SELL MEDIUM confidence
def test_sell_medium_confidence():
    df = _make_df()
    with patch.object(zlema_module, "_zlema", side_effect=_mock_zlema(cross_up=False, separation=0.002)):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# 8. 크로스 없음 → HOLD
def test_no_cross_hold():
    """flat 데이터: ZLEMA9 == ZLEMA21 → 크로스 없음 → HOLD."""
    df = _make_df(n=N)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 9. 데이터 부족 → HOLD
def test_insufficient_data_hold():
    prices = [100.0] * 20
    data = {
        "open": prices, "high": prices, "low": prices, "close": prices,
        "volume": [1000.0] * 20, "ema50": prices, "atr14": [1.0] * 20,
    }
    df = pd.DataFrame(data)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 10. Signal 필드 완전성
def test_signal_fields():
    df = _make_df()
    with patch.object(zlema_module, "_zlema", side_effect=_mock_zlema(cross_up=True)):
        sig = strat.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "zlema_cross"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and sig.reasoning
    assert isinstance(sig.invalidation, str) and sig.invalidation


# 11. BUY reasoning에 "ZLEMA" 포함
def test_buy_reasoning_contains_zlema():
    df = _make_df()
    with patch.object(zlema_module, "_zlema", side_effect=_mock_zlema(cross_up=True)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert "ZLEMA" in sig.reasoning


# 12. SELL reasoning에 "ZLEMA" 포함
def test_sell_reasoning_contains_zlema():
    df = _make_df()
    with patch.object(zlema_module, "_zlema", side_effect=_mock_zlema(cross_up=False)):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert "ZLEMA" in sig.reasoning


# 13. _zlema 함수: lag 계산 및 반환 타입 확인
def test_zlema_function_returns_series():
    prices = pd.Series([float(i) for i in range(1, 51)])
    result = _zlema(prices, 21)
    assert isinstance(result, pd.Series)
    assert len(result) == 50


# 14. _zlema period=9 lag 적용 확인 (lag = (9-1)//2 = 4)
def test_zlema_lag_applied():
    prices = pd.Series([100.0] * 30)
    z9 = _zlema(prices, 9)
    z21 = _zlema(prices, 21)
    # flat 데이터에서 ZLEMA는 close와 동일해야 함
    assert abs(float(z9.iloc[-1]) - 100.0) < 1e-6
    assert abs(float(z21.iloc[-1]) - 100.0) < 1e-6
