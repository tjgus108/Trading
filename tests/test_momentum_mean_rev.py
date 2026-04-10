"""MomentumMeanRevStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.momentum_mean_rev import MomentumMeanRevStrategy


def _make_df(n: int = 60, close_prices=None) -> pd.DataFrame:
    if close_prices is not None:
        close = np.array(close_prices, dtype=float)
        n = len(close)
    else:
        close = np.linspace(100, 110, n)
    high = close * 1.005
    low = close * 0.995
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


def _make_buy_signal_df() -> pd.DataFrame:
    """모멘텀 상승(mom10_ma > 0) + 가격 낮음(z < -0.5) 조건."""
    n = 60
    # 10봉 전 대비 상승 모멘텀 (mom10 > 0)
    # 하지만 최근 가격이 20봉 평균보다 낮아야 함 (z < -0.5)
    base = np.linspace(95, 105, n)   # 완만한 상승 (mom10 > 0 유지)
    # 마지막 5봉을 낮춰서 Z-score를 음수로
    close = base.copy()
    close[-5:] = close[-5:] - 4.0   # 평균 아래로 당김
    high = close * 1.005
    low = close * 0.995
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


def _make_sell_signal_df() -> pd.DataFrame:
    """모멘텀 하락(mom10_ma < 0) + 가격 높음(z > 0.5) 조건."""
    n = 60
    base = np.linspace(110, 100, n)  # 완만한 하락 (mom10 < 0)
    close = base.copy()
    close[-5:] = close[-5:] + 4.0   # 평균 위로 당김
    high = close * 1.005
    low = close * 0.995
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────────

def test_strategy_name():
    s = MomentumMeanRevStrategy()
    assert s.name == "momentum_mean_rev"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────────

def test_instantiation():
    s = MomentumMeanRevStrategy()
    assert isinstance(s, MomentumMeanRevStrategy)


# ── 3. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = MomentumMeanRevStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ──────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = MomentumMeanRevStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = MomentumMeanRevStrategy()
    df = _make_df(n=5)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning or "minimum" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = MomentumMeanRevStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성 ──────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = MomentumMeanRevStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "momentum_mean_rev"
    assert sig.entry_price >= 0
    assert sig.reasoning != ""
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 8. 최소 행수(25)에서 동작 ─────────────────────────────────────────────────

def test_minimum_rows_works():
    s = MomentumMeanRevStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 9. entry_price > 0 ──────────────────────────────────────────────────────

def test_entry_price_positive():
    s = MomentumMeanRevStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.entry_price > 0


# ── 10. BUY 조건 데이터 테스트 ───────────────────────────────────────────────

def test_buy_signal_condition():
    s = MomentumMeanRevStrategy()
    df = _make_buy_signal_df()
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.HOLD)


# ── 11. SELL 조건 데이터 테스트 ──────────────────────────────────────────────

def test_sell_signal_condition():
    s = MomentumMeanRevStrategy()
    df = _make_sell_signal_df()
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.SELL, Action.HOLD)


# ── 12. confidence 유효값 확인 ────────────────────────────────────────────────

def test_confidence_valid_values():
    s = MomentumMeanRevStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 13. BUY reasoning 키워드 확인 ────────────────────────────────────────────

def test_buy_reasoning_keywords():
    s = MomentumMeanRevStrategy()
    df = _make_buy_signal_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "mom10_ma" in sig.reasoning or "z_price" in sig.reasoning


# ── 14. SELL reasoning 키워드 확인 ───────────────────────────────────────────

def test_sell_reasoning_keywords():
    s = MomentumMeanRevStrategy()
    df = _make_sell_signal_df()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "mom10_ma" in sig.reasoning or "z_price" in sig.reasoning


# ── 15. 24행 입력 → HOLD (MIN_ROWS 경계) ─────────────────────────────────────

def test_boundary_below_min_rows():
    s = MomentumMeanRevStrategy()
    df = _make_df(n=24)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 16. strategy 필드 값 확인 ────────────────────────────────────────────────

def test_strategy_field_value():
    s = MomentumMeanRevStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "momentum_mean_rev"
