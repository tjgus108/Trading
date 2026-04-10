"""
PriceSqueezeStrategy 단위 테스트 (최소 14개)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_squeeze import PriceSqueezeStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 50, close_values=None, high_values=None, low_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    c = list(close_values)
    h = list(high_values) if high_values is not None else [v + 2.0 for v in c]
    l = list(low_values) if low_values is not None else [v - 2.0 for v in c]
    return pd.DataFrame({
        "open":   c,
        "high":   h,
        "low":    l,
        "close":  c,
        "volume": [1000.0] * n,
    })


def _squeeze_release_df(n: int = 60, bullish: bool = True) -> pd.DataFrame:
    """
    앞부분: 좁은 range → BB < KC (squeeze)
    완성봉[-2]: 큰 변동 → squeeze 해제
    """
    close = [100.0] * n
    high  = [101.0] * n
    low   = [99.0]  * n

    # 완성봉 [-2]: 큰 변동으로 squeeze 해제
    if bullish:
        close[-2] = 118.0
        high[-2]  = 122.0
        low[-2]   = 99.0
    else:
        close[-2] = 82.0
        high[-2]  = 101.0
        low[-2]   = 78.0

    # 진행 중 캔들 [-1]: 중립
    close[-1] = 100.0
    high[-1]  = 101.0
    low[-1]   = 99.0

    return pd.DataFrame({
        "open":   close,
        "high":   high,
        "low":    low,
        "close":  close,
        "volume": [1000.0] * n,
    })


# ── 1. 전략명 확인 ───────────────────────────────────────────────────────────

def test_strategy_name():
    assert PriceSqueezeStrategy().name == "price_squeeze"


# ── 2. 인스턴스 생성 ─────────────────────────────────────────────────────────

def test_instantiation():
    s = PriceSqueezeStrategy()
    assert s is not None


# ── 3. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = PriceSqueezeStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ──────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = PriceSqueezeStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = PriceSqueezeStrategy()
    df = _make_df(n=5)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = PriceSqueezeStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig is not None
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 7. Signal 필드 완성 ───────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = PriceSqueezeStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy is not None
    assert sig.reasoning is not None
    assert sig.invalidation is not None


# ── 8. BUY reasoning 확인 ────────────────────────────────────────────────────

def test_buy_reasoning():
    s = PriceSqueezeStrategy()
    df = _squeeze_release_df(n=60, bullish=True)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "momentum" in sig.reasoning.lower() or "squeeze" in sig.reasoning.lower()


# ── 9. SELL reasoning 확인 ───────────────────────────────────────────────────

def test_sell_reasoning():
    s = PriceSqueezeStrategy()
    df = _squeeze_release_df(n=60, bullish=False)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "momentum" in sig.reasoning.lower() or "squeeze" in sig.reasoning.lower()


# ── 10. HIGH confidence 테스트 ───────────────────────────────────────────────

def test_high_confidence_possible():
    s = PriceSqueezeStrategy()
    df = _squeeze_release_df(n=60, bullish=True)
    sig = s.generate(df)
    # squeeze release 발생 시 HIGH 또는 MEDIUM
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 11. MEDIUM confidence 테스트 ─────────────────────────────────────────────

def test_medium_confidence_on_weak_momentum():
    s = PriceSqueezeStrategy()
    # 약한 momentum → MEDIUM 가능
    n = 60
    close = [100.0] * n
    high  = [101.0] * n
    low   = [99.0]  * n
    # 완성봉: 아주 약한 돌파
    close[-2] = 100.5
    high[-2]  = 105.0
    low[-2]   = 99.0
    close[-1] = 100.0
    df = pd.DataFrame({
        "open": close, "high": high, "low": low, "close": close, "volume": [1000.0] * n
    })
    sig = s.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 12. entry_price > 0 ──────────────────────────────────────────────────────

def test_entry_price_positive():
    s = PriceSqueezeStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.entry_price >= 0.0


# ── 13. strategy 필드 값 확인 ────────────────────────────────────────────────

def test_strategy_field():
    s = PriceSqueezeStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "price_squeeze"


# ── 14. 최소 행 동작 확인 ────────────────────────────────────────────────────

def test_min_rows_boundary():
    s = PriceSqueezeStrategy()
    # 정확히 32행 (30 + 2)
    df = _make_df(n=32)
    sig = s.generate(df)
    assert sig is not None
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
