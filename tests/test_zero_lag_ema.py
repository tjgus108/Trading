"""ZeroLagEMAStrategy 단위 테스트 (14개)."""

import pandas as pd
import pytest
from unittest.mock import patch

import src.strategy.zero_lag_ema as zle_module
from src.strategy.base import Action, Confidence
from src.strategy.zero_lag_ema import ZeroLagEMAStrategy, _zlema_ec


# ── 헬퍼 ─────────────────────────────────────────────────────────────────────

N = 40


def _make_df(n: int = N, base: float = 100.0) -> pd.DataFrame:
    prices = [base] * n
    return pd.DataFrame({
        "open": prices[:],
        "high": [p * 1.001 for p in prices],
        "low": [p * 0.999 for p in prices],
        "close": prices[:],
        "volume": [1000.0] * n,
    })


def _make_zlema_patch(cross_up: bool, separation: float = 0.02, base: float = 100.0):
    """원하는 크로스를 반환하는 _zlema_ec mock 생성."""
    if cross_up:
        fast_prev = base - 1.0
        slow_prev = base
        fast_now = base * (1 + separation)
        slow_now = base
    else:
        fast_prev = base + 1.0
        slow_prev = base
        fast_now = base * (1 - separation)
        slow_now = base

    def _fake(close: pd.Series, span: int) -> pd.Series:
        n = len(close)
        idx = n - 2
        result = pd.Series([base] * n, dtype=float)
        if span == 10:  # fast
            result.iloc[idx - 1] = fast_prev
            result.iloc[idx] = fast_now
        else:  # slow
            result.iloc[idx - 1] = slow_prev
            result.iloc[idx] = slow_now
        return result

    return _fake


strat = ZeroLagEMAStrategy()


# ── 테스트 ────────────────────────────────────────────────────────────────────

# 1. 전략명
def test_strategy_name():
    assert strat.name == "zero_lag_ema"


# 2. 인스턴스 타입
def test_instance():
    assert isinstance(strat, ZeroLagEMAStrategy)


# 3. 데이터 부족 → HOLD (MIN_ROWS = 35)
def test_insufficient_data():
    df = _make_df(n=20)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 4. 최소 행 경계 (34행 → HOLD)
def test_min_rows_boundary():
    df = _make_df(n=34)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 5. reasoning 비어있지 않음
def test_reasoning_not_empty():
    df = _make_df()
    sig = strat.generate(df)
    assert isinstance(sig.reasoning, str) and sig.reasoning


# 6. BUY 신호 (fast crosses above slow)
def test_buy_signal():
    df = _make_df()
    with patch.object(zle_module, "_zlema_ec", side_effect=_make_zlema_patch(cross_up=True)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY


# 7. SELL 신호 (fast crosses below slow)
def test_sell_signal():
    df = _make_df()
    with patch.object(zle_module, "_zlema_ec", side_effect=_make_zlema_patch(cross_up=False)):
        sig = strat.generate(df)
    assert sig.action == Action.SELL


# 8. BUY Signal 필드 완전성
def test_buy_signal_fields():
    df = _make_df()
    with patch.object(zle_module, "_zlema_ec", side_effect=_make_zlema_patch(cross_up=True)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence is not None
    assert sig.strategy == "zero_lag_ema"
    assert sig.entry_price > 0
    assert isinstance(sig.reasoning, str) and sig.reasoning
    assert isinstance(sig.invalidation, str) and sig.invalidation


# 9. BUY HIGH confidence (separation > 1%)
def test_buy_high_confidence():
    df = _make_df()
    with patch.object(zle_module, "_zlema_ec", side_effect=_make_zlema_patch(cross_up=True, separation=0.02)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# 10. BUY MEDIUM confidence (separation < 1%)
def test_buy_medium_confidence():
    df = _make_df()
    with patch.object(zle_module, "_zlema_ec", side_effect=_make_zlema_patch(cross_up=True, separation=0.005)):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# 11. BUY reasoning에 "ZeroLagEMA" 포함
def test_buy_reasoning_contains_zerolagem():
    df = _make_df()
    with patch.object(zle_module, "_zlema_ec", side_effect=_make_zlema_patch(cross_up=True)):
        sig = strat.generate(df)
    assert "ZeroLagEMA" in sig.reasoning


# 12. SELL reasoning에 "ZeroLagEMA" 포함
def test_sell_reasoning_contains_zerolagem():
    df = _make_df()
    with patch.object(zle_module, "_zlema_ec", side_effect=_make_zlema_patch(cross_up=False)):
        sig = strat.generate(df)
    assert "ZeroLagEMA" in sig.reasoning


# 13. entry_price > 0
def test_entry_price_positive():
    df = _make_df(base=300.0)
    sig = strat.generate(df)
    assert sig.entry_price > 0


# 14. strategy 필드 확인
def test_strategy_field():
    df = _make_df()
    sig = strat.generate(df)
    assert sig.strategy == "zero_lag_ema"
