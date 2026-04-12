"""
검증: FeatureBuilder가 inf/nan 포함 입력에서 안전한지 확인.
- close=0 → log(0) = -inf 발생 여부
- inf가 dropna()를 통과하는지 (취약점 검증)
"""
import numpy as np
import pandas as pd
import pytest

from src.ml.features import FeatureBuilder


def _base_df(n=60) -> pd.DataFrame:
    """정상 OHLCV DataFrame."""
    rng = np.random.default_rng(42)
    close = 100 + np.cumsum(rng.normal(0, 0.5, n))
    close = np.clip(close, 1, None)
    high = close * 1.005
    low = close * 0.995
    return pd.DataFrame({
        "open": close,
        "high": high,
        "low": low,
        "close": close,
        "volume": rng.uniform(1000, 5000, n),
    })


def test_inf_not_present_in_normal_input():
    """정상 입력 → 피처에 inf 없어야 함."""
    df = _base_df()
    fb = FeatureBuilder()
    X, y = fb.build(df)
    assert not np.isinf(X.values).any(), "정상 데이터에서 inf 피처 발생"
    assert not X.isna().any().any(), "정상 데이터에서 NaN 피처 발생"


def test_zero_close_inf_replaced_with_nan():
    """close=0 시 log_ret=-inf 발생 → inf→NaN 변환으로 방어됨을 검증."""
    df = _base_df()
    df.loc[df.index[10], "close"] = 0.0  # log(0/prev) = -inf

    fb = FeatureBuilder()
    feat = fb._compute_features(df)

    # inf가 NaN으로 변환되어야 함 (Cycle 108에서 수정)
    has_inf = np.isinf(feat.values).any()
    assert not has_inf, "inf가 NaN으로 변환되어야 함"


def test_inf_survives_dropna():
    """inf는 pd.DataFrame.dropna()에서 제거되지 않는 것을 확인 (취약점 검증)."""
    df = pd.DataFrame({"a": [1.0, np.inf, 3.0], "b": [np.nan, 2.0, 4.0]})
    cleaned = df.dropna()
    # NaN 행(0번)은 제거되지만 inf 행(1번)은 남음
    assert np.isinf(cleaned["a"]).any(), (
        "inf는 dropna()를 통과함 — FeatureBuilder.build()의 dropna()만으로는 inf 방어 불충분"
    )
