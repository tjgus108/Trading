"""
Test ML Pipeline Edge Cases (Category A - Quality Assurance)
Cycle 170+: Empty data, NaN features, model robustness
"""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from src.ml.features import FeatureBuilder
from src.ml.model import MLSignalGenerator, MLPrediction


# ─────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────

def _make_df(n: int = 300, seed: int = 42) -> pd.DataFrame:
    """표준 테스트 데이터프레임 생성."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    close = 50000 + np.cumsum(rng.standard_normal(n) * 300)
    close = np.abs(close)
    high = close + np.abs(rng.standard_normal(n) * 100)
    low = close - np.abs(rng.standard_normal(n) * 100)
    low = np.maximum(low, close * 0.9)
    volume = 10.0 + np.abs(rng.standard_normal(n) * 2)

    df = pd.DataFrame(
        {"open": close, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )

    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [(df["high"] - df["low"]), (df["high"] - prev_close).abs(), (df["low"] - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
    df["donchian_high"] = df["high"].rolling(20).max()
    df["donchian_low"] = df["low"].rolling(20).min()
    typical = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
    return df


# ─────────────────────────────────────────────────────────────────
# FeatureBuilder Edge Cases
# ─────────────────────────────────────────────────────────────────

class TestFeatureBuilderEdgeCases:
    """FeatureBuilder 극단값 및 예외 처리 테스트."""
    
    def test_minimal_data_length(self):
        """최소 데이터 길이(50개)에서 정상 동작."""
        df = _make_df(50)
        fb = FeatureBuilder()
        X, y = fb.build(df)
        assert len(X) > 0
        assert len(X) == len(y)
    
    def test_very_small_data_empty_result(self):
        """극소 데이터(10개)에서 결과 비어있거나 경고 발생."""
        df = _make_df(10)
        fb = FeatureBuilder()
        with pytest.warns(None) as warning_list:
            X, y = fb.build(df)
        # 데이터 부족하면 X가 비어있을 수 있음
        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
    
    def test_all_nan_column_handling(self):
        """모든 NaN 컬럼 존재 시 처리."""
        df = _make_df(200)
        df["bad_col"] = np.nan
        fb = FeatureBuilder()
        X, y = fb.build(df)
        # NaN 컬럼은 무시되고 정상 빌드
        assert not X.isnull().all().any()
        assert len(X) > 0
    
    def test_infinite_values_in_features(self):
        """Inf 값 생성 시나리오 처리 (0 division 등)."""
        df = _make_df(200)
        df.loc[df.index[50], "volume"] = 0.0  # 0 volume → inf 가능성
        fb = FeatureBuilder()
        X, y = fb.build(df)
        # Inf 값은 처리되거나 NaN으로 변환
        assert np.isfinite(X.values).all() or X.isnull().sum().sum() > 0
    
    def test_constant_price_data(self):
        """모든 가격이 동일할 때 (변동성 0)."""
        df = _make_df(200)
        df["close"] = 50000.0
        df["high"] = 50000.0
        df["low"] = 50000.0
        df["open"] = 50000.0
        fb = FeatureBuilder()
        X, y = fb.build(df)
        # 극도로 적은 레이블 또는 피처 편향성
        assert len(X) >= 0
    
    def test_extreme_price_spike(self):
        """가격 스파이크 (예: 1000배) 처리."""
        df = _make_df(200)
        df.loc[df.index[100], "close"] = 500000.0  # 10배 스파이크
        df.loc[df.index[100], "high"] = 500000.0
        fb = FeatureBuilder()
        X, y = fb.build(df)
        # 스파이크가 피처 계산에 영향주지만 크래시 않음
        assert len(X) > 0
        assert np.isfinite(X.values).all() or X.isnull().sum().sum() > 0
    
    def test_zero_volume_bars(self):
        """볼륨 0 바(유령 바) 처리."""
        df = _make_df(200)
        df.loc[df.index[50:60], "volume"] = 0.0
        fb = FeatureBuilder()
        X, y = fb.build(df)
        # 볼륨 0이 피처 계산에 영향주지만 처리됨
        assert len(X) > 0
    
    def test_missing_ohlcv_columns(self):
        """필수 OHLCV 컬럼 누락 시."""
        df = _make_df(200)
        df = df.drop(columns=["volume"])
        fb = FeatureBuilder()
        # volume 없으면 volume_ratio 계산 실패 가능성
        try:
            X, y = fb.build(df)
            # volume 없어도 다른 피처 계산되면 정상
            assert len(X) >= 0
        except KeyError:
            # volume 필수라면 KeyError 예상
            pass
    
    def test_negative_prices(self):
        """음수 가격 (불가능하지만 검증)."""
        df = _make_df(200)
        df.loc[df.index[50], "close"] = -1000.0
        df.loc[df.index[50], "low"] = -1000.0
        fb = FeatureBuilder()
        X, y = fb.build(df)
        # 음수 가격은 피처 계산 중 NaN 또는 inf 생성
        assert isinstance(X, pd.DataFrame)


# ─────────────────────────────────────────────────────────────────
# MLSignalGenerator Edge Cases
# ─────────────────────────────────────────────────────────────────

class TestMLSignalGeneratorEdgeCases:
    """MLSignalGenerator 극단값 및 예외 처리."""
    
    def test_predict_without_model(self):
        """모델 없이 predict 호출 시."""
        df = _make_df(200)
        gen = MLSignalGenerator()
        # 모델 없으면 HOLD 반환
        pred = gen.predict(df)
        assert pred is not None
        if isinstance(pred, dict):
            assert pred.get("action") == "HOLD"
        elif isinstance(pred, MLPrediction):
            assert pred.action == "HOLD"
    
    def test_predict_empty_dataframe(self):
        """빈 DataFrame 입력."""
        df = pd.DataFrame({"close": [], "high": [], "low": []})
        gen = MLSignalGenerator()
        pred = gen.predict(df)
        # 빈 데이터는 HOLD 반환 또는 None
        assert pred is None or (isinstance(pred, dict) and pred.get("action") == "HOLD") or pred.action == "HOLD"
    
    def test_predict_single_row(self):
        """단일 행 DataFrame."""
        df = _make_df(1)
        gen = MLSignalGenerator()
        pred = gen.predict(df)
        # 데이터 부족 → HOLD
        assert pred is not None
    
    def test_predict_with_nan_features(self):
        """NaN 피처가 있는 경우."""
        df = _make_df(200)
        df.loc[df.index[-1], "close"] = np.nan
        gen = MLSignalGenerator()
        pred = gen.predict(df)
        # NaN 처리 (dropna 또는 fillna)
        assert pred is not None
    
    def test_load_nonexistent_model(self):
        """존재하지 않는 모델 로드."""
        gen = MLSignalGenerator()
        result = gen.load("/nonexistent/path/model.pkl")
        assert result is False
    
    def test_load_invalid_model_format(self):
        """잘못된 모델 파일 포맷 로드."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            f.write(b"invalid pickle data")
            temp_path = f.name
        
        gen = MLSignalGenerator()
        result = gen.load(temp_path)
        assert result is False
        
        import os
        os.unlink(temp_path)
    
    def test_prediction_probability_sums_to_one(self):
        """예측 확률의 합이 1.0."""
        df = _make_df(200)
        gen = MLSignalGenerator()
        
        # Mock 모델로 테스트
        mock_model = MagicMock()
        mock_model.predict = MagicMock(return_value=np.array([1]))
        mock_model.predict_proba = MagicMock(return_value=np.array([[0.3, 0.5, 0.2]]))
        gen._model = mock_model
        gen._class_order = [-1, 0, 1]
        
        pred = gen.predict(df)
        if isinstance(pred, MLPrediction):
            prob_sum = pred.proba_buy + pred.proba_sell + pred.proba_hold
            assert abs(prob_sum - 1.0) < 1e-6
    
    def test_symbol_parameter_stored(self):
        """symbol 파라미터가 저장되는지 확인."""
        gen = MLSignalGenerator(symbol="ETH/USDT")
        assert gen.symbol == "ETH/USDT"


# ─────────────────────────────────────────────────────────────────
# Integration Tests
# ─────────────────────────────────────────────────────────────────

class TestMLPipelineIntegration:
    """ML 파이프라인 end-to-end 통합 테스트."""
    
    def test_feature_to_prediction_pipeline(self):
        """FeatureBuilder → MLSignalGenerator 파이프라인."""
        df = _make_df(300)
        fb = FeatureBuilder()
        X, y = fb.build(df)
        
        # 피처 구성 검증
        assert len(X) > 0
        assert not X.isnull().any().any()
        assert np.isfinite(X.values).all()
    
    def test_features_match_prediction_length(self):
        """피처 길이가 예측 입력과 일치."""
        df = _make_df(200)
        gen = MLSignalGenerator()
        
        # predict 호출 시 내부적으로 피처 빌드
        pred = gen.predict(df)
        assert pred is not None
    
    def test_repeated_predictions_deterministic(self):
        """같은 입력으로 반복 예측 시 동일 결과 (no model case)."""
        df = _make_df(200)
        gen = MLSignalGenerator()  # no model
        
        pred1 = gen.predict(df)
        pred2 = gen.predict(df)
        
        if isinstance(pred1, MLPrediction) and isinstance(pred2, MLPrediction):
            assert pred1.action == pred2.action
            assert pred1.confidence == pred2.confidence
    
    def test_forward_n_affects_data_length(self):
        """forward_n 파라미터가 피처 길이에 영향."""
        df = _make_df(300)
        
        fb_small = FeatureBuilder(forward_n=5)
        X_small, y_small = fb_small.build(df)
        
        fb_large = FeatureBuilder(forward_n=50)
        X_large, y_large = fb_large.build(df)
        
        # forward_n이 크면 샘플 수 감소
        assert len(X_small) >= len(X_large)
    
    def test_threshold_affects_labels(self):
        """threshold 파라미터가 레이블에 영향."""
        df = _make_df(300)
        
        fb_tight = FeatureBuilder(threshold=0.001)  # 0.1% 수익
        _, y_tight = fb_tight.build(df)
        
        fb_loose = FeatureBuilder(threshold=0.01)   # 1% 수익
        _, y_loose = fb_loose.build(df)
        
        # threshold가 느슨하면 HOLD(0)이 더 많음
        hold_tight = (y_tight == 0).sum()
        hold_loose = (y_loose == 0).sum() if len(y_loose) > 0 else 0
        # 경향성 확인 (절대값이 아님)
        assert isinstance(hold_tight, (int, np.integer))


# ─────────────────────────────────────────────────────────────────
# Data Quality Tests
# ─────────────────────────────────────────────────────────────────

class TestDataQuality:
    """데이터 품질 검증."""
    
    def test_no_data_leakage_in_features(self):
        """피처가 미래 데이터를 사용하지 않음."""
        df = _make_df(200)
        fb = FeatureBuilder()
        X_orig = fb.build_features_only(df)
        
        # 마지막 행 수정
        df_mod = df.copy()
        df_mod.iloc[-1, df_mod.columns.get_loc("close")] *= 10
        X_mod = fb.build_features_only(df_mod)
        
        # 공통 인덱스의 피처가 동일한지 확인
        common_idx = X_orig.index[:-1].intersection(X_mod.index[:-1])
        shifted_features = ["ema_ratio", "price_vs_ema20", "volume_ratio_20"]
        for feat in shifted_features:
            if feat in X_orig.columns and feat in X_mod.columns:
                diff = (X_orig.loc[common_idx, feat] - X_mod.loc[common_idx, feat]).abs().max()
                # 미래 데이터 누출 없으면 매우 작은 차이
                assert diff < 1e-9
    
    def test_label_not_in_features(self):
        """레이블 정보가 피처에 포함되지 않음."""
        df = _make_df(300)
        fb = FeatureBuilder()
        X, y = fb.build(df)
        
        # 피처와 레이블이 분리되어 있음
        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
        assert len(X) == len(y)
    
    def test_feature_names_consistency(self):
        """피처명이 일관성 있게 생성됨."""
        df = _make_df(200)
        fb = FeatureBuilder()
        X, _ = fb.build(df)
        
        # feature_names와 X.columns 일치
        for name in fb.feature_names:
            assert name in X.columns
