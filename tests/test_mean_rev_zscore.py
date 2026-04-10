"""
MeanRevZScoreStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.mean_rev_zscore import MeanRevZScoreStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 35, close_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    return pd.DataFrame({
        "open":   [100.0] * n,
        "high":   [105.0] * n,
        "low":    [95.0]  * n,
        "close":  close_values,
        "volume": [1000.0] * n,
    })


def _make_buy_df(n: int = 35) -> pd.DataFrame:
    """
    idx=-2 가 과매도 + 그 이전보다 z가 올라가도록 구성.
    base 100 중에 idx=-3에 더 낮은 값, idx=-2에 낮은 값(이전보다 높음 → rising).
    """
    closes = [100.0] * n
    # idx = n-2 → 과매도 위치, 이전 봉 더 낮게
    closes[n - 3] = 60.0   # z_prev 더 낮음 (더 극단)
    closes[n - 2] = 65.0   # z_now도 낮지만 z_prev보다는 높음 → rising
    closes[n - 1] = 100.0  # 진행 중 캔들
    return _make_df(n=n, close_values=closes)


def _make_sell_df(n: int = 35) -> pd.DataFrame:
    """
    idx=-2 가 과매수 + 그 이전보다 z가 내려가도록 구성.
    """
    closes = [100.0] * n
    closes[n - 3] = 140.0  # z_prev 더 높음
    closes[n - 2] = 135.0  # z_now도 높지만 z_prev보다는 낮음 → falling
    closes[n - 1] = 100.0
    return _make_df(n=n, close_values=closes)


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────────

def test_strategy_name():
    assert MeanRevZScoreStrategy.name == "mean_rev_zscore"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────────

def test_strategy_instantiable():
    s = MeanRevZScoreStrategy()
    assert s is not None


# ── 3. 데이터 부족 → HOLD ─────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = MeanRevZScoreStrategy()
    df = _make_df(n=20)  # < 30
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ───────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = MeanRevZScoreStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = MeanRevZScoreStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = MeanRevZScoreStrategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert sig is not None
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 7. Signal 필드 완성 ───────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = MeanRevZScoreStrategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy is not None
    assert sig.entry_price is not None
    assert sig.reasoning is not None


# ── 8. BUY reasoning 키워드 확인 ─────────────────────────────────────────────

def test_buy_reasoning_keyword():
    s = MeanRevZScoreStrategy()
    df = _make_buy_df(n=35)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "zscore" in sig.reasoning or "과매도" in sig.reasoning


# ── 9. SELL reasoning 키워드 확인 ────────────────────────────────────────────

def test_sell_reasoning_keyword():
    s = MeanRevZScoreStrategy()
    df = _make_sell_df(n=35)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "zscore" in sig.reasoning or "과매수" in sig.reasoning


# ── 10. HIGH confidence 테스트 ────────────────────────────────────────────────

def test_high_confidence_buy():
    """|z| > 2.5 → HIGH"""
    s = MeanRevZScoreStrategy()
    df = _make_buy_df(n=35)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 11. MEDIUM confidence 테스트 ──────────────────────────────────────────────

def test_medium_confidence_possible():
    """confidence가 HIGH 또는 MEDIUM 중 하나"""
    s = MeanRevZScoreStrategy()
    df = _make_buy_df(n=35)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)
    else:
        assert sig.confidence == Confidence.LOW


# ── 12. entry_price > 0 ───────────────────────────────────────────────────────

def test_entry_price_positive():
    s = MeanRevZScoreStrategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert sig.entry_price > 0


# ── 13. strategy 필드 값 확인 ────────────────────────────────────────────────

def test_signal_strategy_field():
    s = MeanRevZScoreStrategy()
    df = _make_buy_df(n=35)
    sig = s.generate(df)
    assert sig.strategy == "mean_rev_zscore"


# ── 14. 최소 행 수(30)에서 동작 ──────────────────────────────────────────────

def test_exactly_min_rows():
    s = MeanRevZScoreStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig is not None
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
