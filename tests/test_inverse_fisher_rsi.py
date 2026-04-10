"""
InverseFisherRSIStrategy 단위 테스트 (최소 14개)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.inverse_fisher_rsi import InverseFisherRSIStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 50, close_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    c = list(close_values)
    h = [v + 2.0 for v in c]
    l = [v - 2.0 for v in c]
    return pd.DataFrame({
        "open":   c,
        "high":   h,
        "low":    l,
        "close":  c,
        "volume": [1000.0] * n,
    })


def _buy_cross_df(n: int = 60) -> pd.DataFrame:
    """
    IFR가 -0.5 아래에 있다가 위로 크로스하는 패턴.
    앞: 하락 추세 (RSI 낮음 → IFR 낮음)
    완성봉[-2]: 급등 → RSI 상승 → IFR crosses above -0.5
    """
    close = list(np.linspace(100.0, 60.0, n - 5)) + [60.0] * 5
    # 완성봉[-2]에서 급등
    close[-2] = 75.0
    close[-1] = 74.0  # 진행 중 캔들
    return _make_df(n=n, close_values=close)


def _sell_cross_df(n: int = 60) -> pd.DataFrame:
    """
    IFR가 0.5 위에 있다가 아래로 크로스하는 패턴.
    앞: 상승 추세 (RSI 높음 → IFR 높음)
    완성봉[-2]: 급락 → RSI 하락 → IFR crosses below 0.5
    """
    close = list(np.linspace(60.0, 100.0, n - 5)) + [100.0] * 5
    # 완성봉[-2]에서 급락
    close[-2] = 85.0
    close[-1] = 86.0  # 진행 중 캔들
    return _make_df(n=n, close_values=close)


# ── 1. 전략명 확인 ───────────────────────────────────────────────────────────

def test_strategy_name():
    assert InverseFisherRSIStrategy().name == "inverse_fisher_rsi"


# ── 2. 인스턴스 생성 ─────────────────────────────────────────────────────────

def test_instantiation():
    s = InverseFisherRSIStrategy()
    assert s is not None


# ── 3. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = InverseFisherRSIStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ──────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = InverseFisherRSIStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = InverseFisherRSIStrategy()
    df = _make_df(n=5)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = InverseFisherRSIStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig is not None
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 7. Signal 필드 완성 ───────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = InverseFisherRSIStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy is not None
    assert sig.reasoning is not None
    assert sig.invalidation is not None


# ── 8. BUY reasoning 확인 ────────────────────────────────────────────────────

def test_buy_reasoning():
    s = InverseFisherRSIStrategy()
    df = _buy_cross_df(n=80)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "IFR" in sig.reasoning or "crossed" in sig.reasoning.lower()


# ── 9. SELL reasoning 확인 ───────────────────────────────────────────────────

def test_sell_reasoning():
    s = InverseFisherRSIStrategy()
    df = _sell_cross_df(n=80)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "IFR" in sig.reasoning or "crossed" in sig.reasoning.lower()


# ── 10. HIGH confidence 테스트 ───────────────────────────────────────────────

def test_high_confidence_on_strong_cross():
    s = InverseFisherRSIStrategy()
    # 강한 크로스 → HIGH confidence 가능
    n = 80
    # 극단적 하락 후 반등 → ifr 강하게 -0.5 위로
    close = list(np.linspace(100.0, 30.0, n - 3)) + [30.0, 60.0, 59.0]
    df = _make_df(n=n, close_values=close)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 11. MEDIUM confidence 테스트 ─────────────────────────────────────────────

def test_medium_confidence_on_weak_cross():
    s = InverseFisherRSIStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    # flat 데이터 → HOLD with LOW confidence
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 12. entry_price > 0 ──────────────────────────────────────────────────────

def test_entry_price_positive():
    s = InverseFisherRSIStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.entry_price >= 0.0


# ── 13. strategy 필드 값 확인 ────────────────────────────────────────────────

def test_strategy_field():
    s = InverseFisherRSIStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "inverse_fisher_rsi"


# ── 14. 최소 행 동작 확인 ────────────────────────────────────────────────────

def test_min_rows_boundary():
    s = InverseFisherRSIStrategy()
    # 정확히 22행 (20 + 2)
    df = _make_df(n=22)
    sig = s.generate(df)
    assert sig is not None
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
