"""HMMRegimeDetector fallback tests (hmmlearn 미설치 환경 포함)."""
import sys
import types

import numpy as np
import pandas as pd
import pytest

from src.ml.hmm_model import HMMRegimeDetector, BULL, BEAR


def _make_df(n: int = 100, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 50000 + np.cumsum(rng.standard_normal(n) * 200)
    close = np.abs(close)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame({"close": close, "open": close, "high": close * 1.001,
                         "low": close * 0.999, "volume": 1.0}, index=idx)


class TestHMMFallback:
    def test_fallback_flag_when_hmmlearn_missing(self, monkeypatch):
        """hmmlearn import 실패 시 _use_fallback=True."""
        import builtins
        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "hmmlearn":
                raise ImportError("mocked missing")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        det = HMMRegimeDetector()
        assert det._use_fallback is True
        assert det._hmmlearn_available is False

    def test_fallback_predict_returns_valid(self):
        """fallback 모드에서 predict()가 BULL 또는 BEAR 반환."""
        det = HMMRegimeDetector()
        det._use_fallback = True
        det._fitted = True
        df = _make_df(100)
        result = det.predict(df)
        assert result in (BULL, BEAR)

    def test_fallback_sequence_length(self):
        """fallback sequence 길이 = df 길이."""
        det = HMMRegimeDetector()
        det._use_fallback = True
        det._fitted = True
        df = _make_df(80)
        seq = det.predict_sequence(df)
        assert seq is not None
        assert len(seq) == len(df)
        assert set(seq.unique()).issubset({BULL, BEAR})

    def test_fallback_short_data(self):
        """데이터 < 20행이면 모두 BULL 반환."""
        det = HMMRegimeDetector()
        det._use_fallback = True
        det._fitted = True
        df = _make_df(10)
        seq = det.predict_sequence(df)
        assert (seq == BULL).all()

    def test_fit_when_fallback(self):
        """fallback 모드에서 fit()은 에러 없이 self 반환."""
        det = HMMRegimeDetector()
        det._use_fallback = True
        df = _make_df(100)
        result = det.fit(df)
        assert result is det
        assert det._fitted is True
