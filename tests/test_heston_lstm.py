"""
F2. HestonLSTMStrategy 테스트.
최소 10개 테스트.
"""

import numpy as np
import pandas as pd
import pytest

from src.ml.heston_model import HestonVolatilityModel
from src.strategy.heston_lstm_strategy import HestonLSTMStrategy
from src.strategy.base import Action, Signal
from src.orchestrator import STRATEGY_REGISTRY


# ──────────────────────────────────────────────
# 헬퍼: 테스트용 OHLCV DataFrame 생성
# ──────────────────────────────────────────────

def _make_df(n: int = 60, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 30000.0 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    high = close * (1 + rng.uniform(0, 0.005, n))
    low = close * (1 - rng.uniform(0, 0.005, n))
    volume = rng.uniform(100, 1000, n)
    return pd.DataFrame({
        "open": close * (1 + rng.normal(0, 0.002, n)),
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


def _make_low_vol_df(n: int = 60) -> pd.DataFrame:
    """v0 < 0.0001 유도: 매우 작은 수익률."""
    close = np.linspace(30000, 30001, n)
    return pd.DataFrame({
        "open": close,
        "high": close * 1.00001,
        "low": close * 0.99999,
        "close": close,
        "volume": np.ones(n) * 500,
    })


def _make_high_vol_df(n: int = 60) -> pd.DataFrame:
    """v0 > 0.001 유도: 매우 큰 수익률."""
    rng = np.random.default_rng(0)
    close = 30000.0 * np.exp(np.cumsum(rng.normal(0, 0.1, n)))
    return pd.DataFrame({
        "open": close,
        "high": close * 1.05,
        "low": close * 0.95,
        "close": close,
        "volume": np.ones(n) * 500,
    })


# ──────────────────────────────────────────────
# HestonVolatilityModel 테스트
# ──────────────────────────────────────────────

def test_heston_estimate_returns_dict():
    """estimate() → dict with kappa/theta/sigma/rho/v0"""
    model = HestonVolatilityModel()
    df = _make_df()
    result = model.estimate(df)
    assert isinstance(result, dict)
    for key in ("kappa", "theta", "sigma", "rho", "v0"):
        assert key in result, f"Missing key: {key}"


def test_heston_v0_positive():
    """v0 >= 0"""
    model = HestonVolatilityModel()
    df = _make_df()
    result = model.estimate(df)
    assert result["v0"] >= 0.0


def test_heston_build_features_shape():
    """build_features() → len == len(df)"""
    model = HestonVolatilityModel()
    df = _make_df(n=60)
    feat = model.build_features(df)
    assert len(feat) == len(df)


def test_heston_build_features_columns():
    """5개 컬럼 존재"""
    model = HestonVolatilityModel()
    df = _make_df(n=60)
    feat = model.build_features(df)
    expected = {"heston_kappa", "heston_theta", "heston_sigma", "heston_rho", "heston_v0"}
    assert expected.issubset(set(feat.columns))


def test_heston_estimate_default_on_small_data():
    """데이터 부족 시 기본값 반환 (오류 없음)."""
    model = HestonVolatilityModel(window=20)
    df = _make_df(n=5)  # window=20보다 작음
    result = model.estimate(df)
    assert isinstance(result, dict)
    assert "v0" in result


# ──────────────────────────────────────────────
# HestonLSTMStrategy 테스트
# ──────────────────────────────────────────────

def test_heston_lstm_name():
    """name == 'heston_lstm'"""
    strategy = HestonLSTMStrategy()
    assert strategy.name == "heston_lstm"


def test_heston_lstm_generate_returns_signal():
    """generate() → Signal 반환"""
    strategy = HestonLSTMStrategy()
    df = _make_df(n=60)
    signal = strategy.generate(df)
    assert isinstance(signal, Signal)
    assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_heston_lstm_fallback_high_vol():
    """v0 극히 높을 때 (고변동성) → HOLD"""
    strategy = HestonLSTMStrategy()
    # LSTM 모델 없음을 확인 후 고변동성 데이터로 테스트
    assert not strategy._model_loaded, "모델이 없어야 fallback 테스트 가능"
    df = _make_high_vol_df(n=60)
    signal = strategy.generate(df)
    # 고변동성 → HOLD
    assert signal.action == Action.HOLD


def test_heston_lstm_fallback_low_vol():
    """v0 극히 낮을 때 → BUY or HOLD (SELL 아님)"""
    strategy = HestonLSTMStrategy()
    assert not strategy._model_loaded
    df = _make_low_vol_df(n=60)
    signal = strategy.generate(df)
    assert signal.action != Action.SELL


def test_heston_lstm_insufficient_data():
    """데이터 부족 → HOLD"""
    strategy = HestonLSTMStrategy()
    df = _make_df(n=5)  # 너무 적은 데이터
    signal = strategy.generate(df)
    # 데이터 부족 시 fallback은 기본값(HOLD) 반환
    assert isinstance(signal, Signal)
    assert signal.action == Action.HOLD


def test_registry_contains_heston_lstm():
    """STRATEGY_REGISTRY에 'heston_lstm' 등록 확인"""
    assert "heston_lstm" in STRATEGY_REGISTRY
    assert STRATEGY_REGISTRY["heston_lstm"] is HestonLSTMStrategy
