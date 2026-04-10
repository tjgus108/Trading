"""LaguerreRSIStrategy 단위 테스트 (14개)."""

import pandas as pd
import pytest
from unittest.mock import patch

import src.strategy.laguerre_rsi as laguerre_module
from src.strategy.base import Action, Confidence
from src.strategy.laguerre_rsi import LaguerreRSIStrategy, _laguerre_rsi


# ── 헬퍼 ─────────────────────────────────────────────────────────────────────

N = 20


def _make_df(n: int = N, base: float = 100.0) -> pd.DataFrame:
    prices = [base] * n
    return pd.DataFrame({
        "open": prices[:],
        "high": [p * 1.001 for p in prices],
        "low": [p * 0.999 for p in prices],
        "close": prices[:],
        "volume": [1000.0] * n,
    })


def _make_lrsi_patch(lrsi_prev: float, lrsi_now: float, n: int = N):
    """_laguerre_rsi를 원하는 값으로 픽스."""
    def _fake(close: pd.Series, gamma: float = 0.5) -> pd.Series:
        result = pd.Series([0.5] * len(close), dtype=float)
        idx = len(close) - 2
        result.iloc[idx - 1] = lrsi_prev
        result.iloc[idx] = lrsi_now
        return result
    return _fake


strat = LaguerreRSIStrategy()


# ── 테스트 ────────────────────────────────────────────────────────────────────

# 1. 전략명
def test_strategy_name():
    assert strat.name == "laguerre_rsi"


# 2. 인스턴스 타입
def test_instance():
    assert isinstance(strat, LaguerreRSIStrategy)


# 3. 데이터 부족 → HOLD
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 4. 최소 행 경계 (MIN_ROWS - 1 = 14행 → HOLD)
def test_min_rows_boundary():
    df = _make_df(n=14)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 5. reasoning 문자열 비어있지 않음
def test_reasoning_not_empty():
    df = _make_df()
    sig = strat.generate(df)
    assert isinstance(sig.reasoning, str) and sig.reasoning


# 6. BUY 신호 (cross above 0.2)
def test_buy_signal():
    df = _make_df()
    with patch.object(laguerre_module, "_laguerre_rsi", side_effect=_make_lrsi_patch(0.15, 0.25)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# 7. SELL 신호 (cross below 0.8)
def test_sell_signal():
    df = _make_df()
    with patch.object(laguerre_module, "_laguerre_rsi", side_effect=_make_lrsi_patch(0.85, 0.75)):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# 8. BUY Signal 필드 완전성
def test_buy_signal_fields():
    df = _make_df()
    with patch.object(laguerre_module, "_laguerre_rsi", side_effect=_make_lrsi_patch(0.15, 0.25)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence is not None
    assert sig.strategy == "laguerre_rsi"
    assert sig.entry_price > 0
    assert isinstance(sig.reasoning, str) and sig.reasoning
    assert isinstance(sig.invalidation, str) and sig.invalidation


# 9. BUY reasoning에 "Laguerre RSI" 포함
def test_buy_reasoning_contains_laguerre():
    df = _make_df()
    with patch.object(laguerre_module, "_laguerre_rsi", side_effect=_make_lrsi_patch(0.15, 0.25)):
        sig = strat.generate(df)
    assert "Laguerre RSI" in sig.reasoning


# 10. SELL reasoning에 "Laguerre RSI" 포함
def test_sell_reasoning_contains_laguerre():
    df = _make_df()
    with patch.object(laguerre_module, "_laguerre_rsi", side_effect=_make_lrsi_patch(0.85, 0.75)):
        sig = strat.generate(df)
    assert "Laguerre RSI" in sig.reasoning


# 11. BUY HIGH confidence (lrsi_now < 0.1이어야 HIGH, cross above 0.2는 불가 — 실제로 < 0.1 < 0.2이므로 MEDIUM)
# lrsi_now < 0.1이고 이전이 < 0.2이면 cross above 0.2가 안 됨 → 스펙 재확인:
# HIGH if lrsi < 0.1 (BUY), 하지만 cross above 0.2는 prev<0.2 & now>=0.2 이므로 now>=0.2
# 따라서 BUY 시 always MEDIUM (now >= 0.2 이므로 < 0.1 불가)
def test_buy_medium_confidence():
    df = _make_df()
    with patch.object(laguerre_module, "_laguerre_rsi", side_effect=_make_lrsi_patch(0.15, 0.22)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# 12. SELL HIGH confidence (lrsi_now > 0.9이어야 HIGH, cross below 0.8는 now<=0.8이므로 불가)
# 따라서 SELL 시 always MEDIUM
def test_sell_medium_confidence():
    df = _make_df()
    with patch.object(laguerre_module, "_laguerre_rsi", side_effect=_make_lrsi_patch(0.85, 0.78)):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# 13. entry_price > 0 (정상 데이터)
def test_entry_price_positive():
    df = _make_df(base=200.0)
    sig = strat.generate(df)
    assert sig.entry_price > 0


# 14. strategy 필드 확인
def test_strategy_field():
    df = _make_df()
    sig = strat.generate(df)
    assert sig.strategy == "laguerre_rsi"
