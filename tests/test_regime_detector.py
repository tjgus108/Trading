"""
SimpleRegimeDetector 단위 테스트.
"""

import numpy as np
import pandas as pd
import pytest

from src.analysis.regime_detector import SimpleRegimeDetector


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n: int = 100, trend: str = "flat", slope: float = 1.0) -> pd.DataFrame:
    """테스트용 OHLCV DataFrame 생성."""
    np.random.seed(0)
    if trend == "bull":
        close = np.linspace(100, 100 * (1 + slope), n)
    elif trend == "bear":
        close = np.linspace(100, 100 * (1 - slope), n)
    else:
        close = np.full(n, 100.0) + np.random.randn(n) * 0.01

    return pd.DataFrame({
        "open": close * 0.999,
        "high": close * 1.002,
        "low": close * 0.998,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

def test_detect_bull():
    """강한 상승 추세 → 'bull'."""
    df = _make_df(n=100, trend="bull", slope=0.10)  # 10% 상승
    result = SimpleRegimeDetector.detect(df)
    assert result == "bull"


def test_detect_bear():
    """강한 하락 추세 → 'bear'."""
    df = _make_df(n=100, trend="bear", slope=0.10)  # 10% 하락
    result = SimpleRegimeDetector.detect(df)
    assert result == "bear"


def test_detect_sideways():
    """횡보 → 'sideways'."""
    df = _make_df(n=100, trend="flat")
    result = SimpleRegimeDetector.detect(df)
    assert result == "sideways"


def test_detect_insufficient_data():
    """봉 수 < 50 → 'unknown'."""
    df = _make_df(n=30, trend="bull", slope=0.10)
    result = SimpleRegimeDetector.detect(df)
    assert result == "unknown"


def test_detect_none_df():
    """None DataFrame → 'unknown'."""
    result = SimpleRegimeDetector.detect(None)
    assert result == "unknown"
