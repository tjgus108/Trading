"""
E1. RegimeAdaptiveStrategy 단위 테스트.
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.regime_adaptive import RegimeAdaptiveStrategy
from src.ml.hmm_model import HMMRegimeDetector, BULL, BEAR


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n=60, trend="bull") -> pd.DataFrame:
    """테스트용 OHLCV DataFrame 생성."""
    np.random.seed(42)
    if trend == "bull":
        close = 100.0 + np.cumsum(np.abs(np.random.randn(n)) * 0.5)
    else:
        close = 100.0 + np.cumsum(-np.abs(np.random.randn(n)) * 0.5)

    df = pd.DataFrame({
        "open": close * 0.999,
        "high": close * 1.002,
        "low": close * 0.998,
        "close": close,
        "volume": np.random.rand(n) * 1000 + 100,
        "rsi14": np.clip(50.0 + np.random.randn(n) * 10, 10, 90),
        "atr14": np.abs(np.random.randn(n)) * 0.5 + 0.5,
    })
    return df


def _make_small_df(n=5) -> pd.DataFrame:
    """데이터 부족 시나리오용."""
    close = [100.0 + i for i in range(n)]
    return pd.DataFrame({
        "close": close,
        "rsi14": [50.0] * n,
        "atr14": [1.0] * n,
    })


# ── 기본 속성 ─────────────────────────────────────────────────────────────────

def test_name():
    """name == 'regime_adaptive'"""
    assert RegimeAdaptiveStrategy.name == "regime_adaptive"


# ── Signal 반환 ───────────────────────────────────────────────────────────────

def test_generate_returns_signal():
    """충분한 df로 Signal 객체 반환"""
    from src.strategy.base import Signal
    strat = RegimeAdaptiveStrategy()
    df = _make_df(n=60)
    sig = strat.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.strategy == "regime_adaptive"


# ── 데이터 부족 → HOLD ────────────────────────────────────────────────────────

def test_generate_hold_without_model():
    """데이터 행 수 부족 시 HOLD 반환"""
    strat = RegimeAdaptiveStrategy()
    df = _make_small_df(n=5)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── HMM fallback ─────────────────────────────────────────────────────────────

def test_hmm_detector_fallback():
    """hmmlearn 없어도 Bollinger Band fallback으로 predict_sequence 반환"""
    detector = HMMRegimeDetector()
    # fallback 강제
    detector._use_fallback = True
    detector._fitted = True

    df = _make_df(n=60)
    seq = detector.predict_sequence(df)
    assert seq is not None
    assert len(seq) > 0
    assert set(seq.unique()).issubset({BULL, BEAR})


def test_hmm_predict_returns_int():
    """predict() → 0 또는 1 반환"""
    detector = HMMRegimeDetector()
    df = _make_df(n=60)
    result = detector.predict(df)
    assert result in (0, 1)
    assert isinstance(result, int)


# ── 레짐 전환 시 LOW confidence ──────────────────────────────────────────────

def test_regime_switch_low_confidence():
    """레짐 전환 시 confidence == LOW"""
    strat = RegimeAdaptiveStrategy()
    df = _make_df(n=60)

    # 첫 번째 호출로 prev_regime 세팅
    strat.generate(df)

    # _prev_regime을 현재와 다른 값으로 강제 설정
    current_seq = strat._hmm.predict_sequence(df)
    if current_seq is not None and len(current_seq) >= 2:
        current = int(current_seq.iloc[-2])
        strat._prev_regime = 1 - current  # 반대 레짐으로 설정

    sig = strat.generate(df)
    assert sig.confidence == Confidence.LOW


# ── STRATEGY_REGISTRY 등록 확인 ───────────────────────────────────────────────

def test_registry_contains_regime_adaptive():
    """STRATEGY_REGISTRY에 'regime_adaptive' 키 존재"""
    from src.orchestrator import STRATEGY_REGISTRY
    assert "regime_adaptive" in STRATEGY_REGISTRY
    assert STRATEGY_REGISTRY["regime_adaptive"] is RegimeAdaptiveStrategy


# ── bull 레짐 신호 검증 ───────────────────────────────────────────────────────

def test_generate_bull_regime():
    """bull 레짐에서 SELL 신호 없음 (BUY 또는 HOLD)"""
    strat = RegimeAdaptiveStrategy()

    # HMM을 bull 레짐으로 강제
    df = _make_df(n=60, trend="bull")

    # predict_sequence를 mock하여 항상 bull 반환
    original_predict_sequence = strat._hmm.predict_sequence

    def mock_bull_seq(d):
        seq = original_predict_sequence(d)
        if seq is None:
            return pd.Series([BULL] * len(d), index=d.index, dtype=int)
        return pd.Series([BULL] * len(seq), index=seq.index, dtype=int)

    strat._hmm.predict_sequence = mock_bull_seq
    strat._prev_regime = BULL  # 전환 없음

    sig = strat.generate(df)
    # bull 레짐에서는 SELL 아님 (BUY 또는 HOLD)
    assert sig.action != Action.SELL
