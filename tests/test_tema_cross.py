"""TEMACrossStrategy 단위 테스트 (12개)."""

import pandas as pd
import pytest
from unittest.mock import patch

import src.strategy.tema_cross as tema_module
from src.strategy.base import Action, Confidence
from src.strategy.tema_cross import TEMACrossStrategy, _tema


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

N = 40  # 기본 DataFrame 길이


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


def _mock_tema(cross_up: bool, separation: float = 0.01):
    """
    원하는 크로스 방향과 이격을 반환하는 _tema mock을 생성.

    cross_up=True  → prev: t8 <= t21, now: t8 > t21
    cross_up=False → prev: t8 >= t21, now: t8 < t21
    """
    base = 100.0
    if cross_up:
        # prev: t8_prev = 99, t21_prev = 100 (t8 < t21)
        # now:  t8_now = base*(1+sep), t21_now = base
        t8_prev = base - 1.0
        t21_prev = base
        t8_now = base * (1 + separation)
        t21_now = base
    else:
        t8_prev = base + 1.0
        t21_prev = base
        t8_now = base * (1 - separation)
        t21_now = base

    call_count = [0]

    def _fake_tema(series: pd.Series, period: int) -> pd.Series:
        n = len(series)
        idx = n - 2  # 전략이 사용하는 "현재" 위치

        result = pd.Series([base] * n, dtype=float)
        if period == 8:
            result.iloc[idx - 1] = t8_prev
            result.iloc[idx] = t8_now
        else:  # period == 21
            result.iloc[idx - 1] = t21_prev
            result.iloc[idx] = t21_now
        return result

    return _fake_tema


strat = TEMACrossStrategy()


# ── 테스트 ────────────────────────────────────────────────────────────────────

# 1. 전략 이름
def test_strategy_name():
    assert strat.name == "tema_cross"


# 2. BUY 신호
def test_buy_signal():
    df = _make_df()
    with patch.object(tema_module, "_tema", side_effect=_mock_tema(cross_up=True)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# 3. SELL 신호
def test_sell_signal():
    df = _make_df()
    with patch.object(tema_module, "_tema", side_effect=_mock_tema(cross_up=False)):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# 4. BUY HIGH confidence (이격 > 0.8%)
def test_buy_high_confidence():
    df = _make_df()
    with patch.object(tema_module, "_tema", side_effect=_mock_tema(cross_up=True, separation=0.015)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# 5. BUY MEDIUM confidence (이격 < 0.8%)
def test_buy_medium_confidence():
    df = _make_df()
    with patch.object(tema_module, "_tema", side_effect=_mock_tema(cross_up=True, separation=0.003)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# 6. SELL HIGH confidence
def test_sell_high_confidence():
    df = _make_df()
    with patch.object(tema_module, "_tema", side_effect=_mock_tema(cross_up=False, separation=0.015)):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# 7. SELL MEDIUM confidence
def test_sell_medium_confidence():
    df = _make_df()
    with patch.object(tema_module, "_tema", side_effect=_mock_tema(cross_up=False, separation=0.003)):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# 8. 크로스 없음 → HOLD
def test_no_cross_hold():
    """flat 데이터: TEMA8 == TEMA21 → 크로스 없음 → HOLD."""
    prices = [100.0] * N
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
    with patch.object(tema_module, "_tema", side_effect=_mock_tema(cross_up=True)):
        sig = strat.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "tema_cross"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and sig.reasoning
    assert isinstance(sig.invalidation, str) and sig.invalidation


# 11. BUY reasoning에 "TEMA" 포함
def test_buy_reasoning_contains_tema():
    df = _make_df()
    with patch.object(tema_module, "_tema", side_effect=_mock_tema(cross_up=True)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert "TEMA" in sig.reasoning


# 12. SELL reasoning에 "TEMA" 포함
def test_sell_reasoning_contains_tema():
    df = _make_df()
    with patch.object(tema_module, "_tema", side_effect=_mock_tema(cross_up=False)):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert "TEMA" in sig.reasoning
