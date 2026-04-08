"""tests/test_lob_strategy.py — LOBOFIStrategy + VPINCalculator 단위 테스트"""

import math
import numpy as np
import pandas as pd
import pytest

from src.strategy.lob_strategy import LOBOFIStrategy
from src.strategy.base import Action, Confidence, Signal
from src.data.order_flow import VPINCalculator


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 100, bias: float = 0.0) -> pd.DataFrame:
    """기본 OHLCV DataFrame. bias > 0 → 전반적으로 close > open."""
    rng = np.random.default_rng(42)
    close = 100.0 + np.cumsum(rng.normal(bias, 0.5, n))
    open_ = close - rng.normal(0.0, 0.3, n)
    high = np.maximum(close, open_) + rng.uniform(0.1, 0.5, n)
    low = np.minimum(close, open_) - rng.uniform(0.1, 0.5, n)
    volume = rng.uniform(10.0, 100.0, n)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume}
    )


def _make_strong_buy_df(n: int = 100) -> pd.DataFrame:
    """마지막 캔들(인덱스 -2)을 극단적 buy 압력으로 설정."""
    df = _make_df(n)
    # 마지막 완성 캔들(인덱스 -2): open << close, 큰 볼륨
    idx = n - 2
    df.loc[idx, "open"] = 50.0
    df.loc[idx, "close"] = 100.0
    df.loc[idx, "high"] = 101.0
    df.loc[idx, "low"] = 49.0
    df.loc[idx, "volume"] = 1000.0
    return df


def _make_strong_sell_df(n: int = 100) -> pd.DataFrame:
    """마지막 캔들(인덱스 -2)을 극단적 sell 압력으로 설정."""
    df = _make_df(n)
    idx = n - 2
    df.loc[idx, "open"] = 100.0
    df.loc[idx, "close"] = 50.0
    df.loc[idx, "high"] = 101.0
    df.loc[idx, "low"] = 49.0
    df.loc[idx, "volume"] = 1000.0
    return df


# ── 테스트 ────────────────────────────────────────────────────────────────────

def test_name():
    strat = LOBOFIStrategy()
    assert strat.name == "lob_maker"


def test_generate_returns_signal():
    strat = LOBOFIStrategy()
    df = _make_df(100)
    signal = strat.generate(df)
    assert isinstance(signal, Signal)
    assert isinstance(signal.action, Action)
    assert isinstance(signal.confidence, Confidence)


def test_buy_on_high_ofi():
    """극단적 buy OFI proxy → BUY 신호"""
    strat = LOBOFIStrategy(ofi_buy_threshold=0.3)
    df = _make_strong_buy_df(100)
    signal = strat.generate(df)
    assert signal.action == Action.BUY


def test_sell_on_low_ofi():
    """극단적 sell OFI proxy → SELL 신호"""
    strat = LOBOFIStrategy(ofi_sell_threshold=-0.3)
    df = _make_strong_sell_df(100)
    signal = strat.generate(df)
    assert signal.action == Action.SELL


def test_vpin_compute_range():
    """VPIN 값이 항상 0~1 범위 내"""
    calc = VPINCalculator(n_buckets=10)
    df = _make_df(100)
    result = calc.compute(df)
    valid = result.dropna()
    assert len(valid) > 0
    assert float(valid.min()) >= 0.0
    assert float(valid.max()) <= 1.0


def test_vpin_insufficient_data():
    """데이터 부족(n < n_buckets) 시 get_latest() → 0.5"""
    calc = VPINCalculator(n_buckets=50)
    small_df = _make_df(10)
    val = calc.get_latest(small_df)
    assert val == pytest.approx(0.5)


def test_reasoning_contains_ofi_vpin():
    """reasoning 필드에 'OFI'와 'VPIN' 문자열 포함"""
    strat = LOBOFIStrategy()
    df = _make_df(100)
    signal = strat.generate(df)
    assert "OFI" in signal.reasoning
    assert "VPIN" in signal.reasoning


def test_registry_contains_lob_maker():
    """STRATEGY_REGISTRY에 'lob_maker' 등록 확인"""
    from src.orchestrator import STRATEGY_REGISTRY
    assert "lob_maker" in STRATEGY_REGISTRY
    assert STRATEGY_REGISTRY["lob_maker"] is LOBOFIStrategy
