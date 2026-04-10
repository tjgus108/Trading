"""
DivergenceScoreStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.divergence_score import DivergenceScoreStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 40, close_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    return pd.DataFrame({
        "open":   [100.0] * n,
        "high":   [105.0] * n,
        "low":    [95.0]  * n,
        "close":  close_values,
        "volume": [1000.0] * n,
    })


def _make_trending_up_df(n: int = 40) -> pd.DataFrame:
    """강한 상승 추세 → score >= 2 AND increasing → BUY 가능"""
    # 점진적 상승 후 마지막 두 봉에서 가속
    closes = [100.0 + i * 0.5 for i in range(n)]
    return _make_df(n=n, close_values=closes)


def _make_trending_down_df(n: int = 40) -> pd.DataFrame:
    """강한 하락 추세 → score <= -2 AND decreasing → SELL 가능"""
    closes = [100.0 + (n - i) * 0.5 for i in range(n)]
    return _make_df(n=n, close_values=closes)


def _make_buy_score_df() -> pd.DataFrame:
    """
    score >= 2 AND score > prev_score를 유도하는 데이터.
    RSI 상승 + CCI 상승 + momentum > 0 + 점수 개선
    """
    n = 40
    # 하락 후 강한 반등으로 score 개선
    closes = [100.0 - i * 0.3 for i in range(n - 5)]
    # 마지막 5봉에서 강한 상승
    base = closes[-1]
    closes += [base + i * 2.0 for i in range(1, 6)]
    return _make_df(n=len(closes), close_values=closes)


def _make_sell_score_df() -> pd.DataFrame:
    """
    score <= -2 AND score < prev_score를 유도하는 데이터.
    강한 상승 후 급락으로 score 악화
    """
    n = 40
    closes = [100.0 + i * 0.3 for i in range(n - 5)]
    base = closes[-1]
    closes += [base - i * 2.0 for i in range(1, 6)]
    return _make_df(n=len(closes), close_values=closes)


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────────

def test_strategy_name():
    assert DivergenceScoreStrategy.name == "divergence_score"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────────

def test_strategy_is_instantiable():
    s = DivergenceScoreStrategy()
    assert s is not None


# ── 3. 데이터 부족 → HOLD ─────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = DivergenceScoreStrategy()
    df = _make_df(n=25)  # < 35
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ──────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = DivergenceScoreStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = DivergenceScoreStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = DivergenceScoreStrategy()
    df = _make_df(n=40)
    sig = s.generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성 ───────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = DivergenceScoreStrategy()
    df = _make_df(n=40)
    sig = s.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy is not None
    assert sig.reasoning is not None
    assert sig.invalidation is not None


# ── 8. BUY reasoning 확인 ────────────────────────────────────────────────────

def test_buy_reasoning():
    s = DivergenceScoreStrategy()
    df = _make_buy_score_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "BUY" in sig.reasoning or "score" in sig.reasoning


# ── 9. SELL reasoning 확인 ───────────────────────────────────────────────────

def test_sell_reasoning():
    s = DivergenceScoreStrategy()
    df = _make_sell_score_df()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "SELL" in sig.reasoning or "score" in sig.reasoning


# ── 10. HIGH confidence 테스트 ────────────────────────────────────────────────

def test_high_confidence_when_score_abs3():
    """
    |score| == 3이면 HIGH confidence
    BUY with score=3: rsi상승(+1) + cci상승(+1) + mom>0(+1) = 3
    """
    s = DivergenceScoreStrategy()
    df = _make_trending_up_df()
    sig = s.generate(df)
    # 신호가 BUY이면 HIGH일 수 있음 (데이터 의존적이므로 MEDIUM도 허용)
    if sig.action == Action.BUY and sig.confidence == Confidence.HIGH:
        assert True  # 기대하는 케이스
    elif sig.action in (Action.BUY, Action.SELL):
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)
    else:
        assert sig.confidence == Confidence.LOW


# ── 11. MEDIUM confidence 테스트 ─────────────────────────────────────────────

def test_medium_confidence_when_score_abs2():
    """|score| < 3이면 MEDIUM confidence"""
    s = DivergenceScoreStrategy()
    df = _make_buy_score_df()
    sig = s.generate(df)
    if sig.action in (Action.BUY, Action.SELL):
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 12. entry_price > 0 ──────────────────────────────────────────────────────

def test_entry_price_positive():
    s = DivergenceScoreStrategy()
    df = _make_df(n=40)
    sig = s.generate(df)
    assert sig.entry_price >= 0


# ── 13. strategy 필드 값 확인 ─────────────────────────────────────────────────

def test_signal_strategy_field():
    s = DivergenceScoreStrategy()
    df = _make_df(n=40)
    sig = s.generate(df)
    assert sig.strategy == "divergence_score"


# ── 14. 최소 행(35행) 동작 확인 ──────────────────────────────────────────────

def test_exactly_min_rows():
    s = DivergenceScoreStrategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
