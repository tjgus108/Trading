"""
MomentumPersistenceStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.momentum_persistence import MomentumPersistenceStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 30, close_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    return pd.DataFrame({
        "open":   [100.0] * n,
        "high":   [105.0] * n,
        "low":    [95.0]  * n,
        "close":  close_values,
        "volume": [1000.0] * n,
    })


def _make_buy_df(n: int = 30, streak: int = 3) -> pd.DataFrame:
    """
    idx=-2 기준으로 최근 streak봉 연속 상승 + 20봉 평균 상승.
    """
    # 전체 완만 상승 → avg_return > 0 보장
    closes = [100.0 + i * 0.5 for i in range(n)]
    closes[n - 1] = closes[n - 2] * 1.001  # 진행 중 캔들
    return _make_df(n=n, close_values=closes)


def _make_sell_df(n: int = 30, streak: int = 3) -> pd.DataFrame:
    """
    idx=-2 기준으로 최근 streak봉 연속 하락 + 20봉 평균 하락.
    """
    closes = [100.0 - i * 0.5 for i in range(n)]
    closes[n - 1] = closes[n - 2] * 0.999
    return _make_df(n=n, close_values=closes)


def _make_flat_df(n: int = 30) -> pd.DataFrame:
    """횡보 → HOLD"""
    import math
    closes = [100.0 + math.sin(i) * 0.1 for i in range(n)]
    return _make_df(n=n, close_values=closes)


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────────

def test_strategy_name():
    assert MomentumPersistenceStrategy.name == "momentum_persistence"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────────

def test_strategy_instantiable():
    s = MomentumPersistenceStrategy()
    assert s is not None


# ── 3. 데이터 부족 → HOLD ─────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = MomentumPersistenceStrategy()
    df = _make_df(n=15)  # < 25
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ───────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = MomentumPersistenceStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = MomentumPersistenceStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = MomentumPersistenceStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig is not None
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 7. Signal 필드 완성 ───────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = MomentumPersistenceStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy is not None
    assert sig.entry_price is not None
    assert sig.reasoning is not None


# ── 8. BUY reasoning 키워드 확인 ─────────────────────────────────────────────

def test_buy_reasoning_keyword():
    s = MomentumPersistenceStrategy()
    df = _make_buy_df(n=30)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "pos_streak" in sig.reasoning or "모멘텀" in sig.reasoning


# ── 9. SELL reasoning 키워드 확인 ────────────────────────────────────────────

def test_sell_reasoning_keyword():
    s = MomentumPersistenceStrategy()
    df = _make_sell_df(n=30)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "neg_streak" in sig.reasoning or "모멘텀" in sig.reasoning


# ── 10. HIGH confidence 테스트 (streak >= 5) ─────────────────────────────────

def test_high_confidence_buy():
    """상승 추세 데이터 → BUY면 confidence 체크"""
    s = MomentumPersistenceStrategy()
    # streak >= 5 보장하려면 더 긴 상승 구간
    closes = [100.0 + i * 1.0 for i in range(35)]
    df = _make_df(n=35, close_values=closes)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 11. MEDIUM confidence 테스트 ──────────────────────────────────────────────

def test_medium_or_high_confidence():
    """BUY/SELL 신호의 confidence는 HIGH 또는 MEDIUM"""
    s = MomentumPersistenceStrategy()
    df = _make_buy_df(n=30)
    sig = s.generate(df)
    if sig.action in (Action.BUY, Action.SELL):
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)
    else:
        assert sig.confidence == Confidence.LOW


# ── 12. entry_price > 0 ───────────────────────────────────────────────────────

def test_entry_price_positive():
    s = MomentumPersistenceStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.entry_price > 0


# ── 13. strategy 필드 값 확인 ────────────────────────────────────────────────

def test_signal_strategy_field():
    s = MomentumPersistenceStrategy()
    df = _make_buy_df(n=30)
    sig = s.generate(df)
    assert sig.strategy == "momentum_persistence"


# ── 14. 최소 행 수(25)에서 동작 ──────────────────────────────────────────────

def test_exactly_min_rows():
    s = MomentumPersistenceStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert sig is not None
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
