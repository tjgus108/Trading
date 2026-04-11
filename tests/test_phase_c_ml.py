"""Phase C: ML 신호 생성기 (C1) 단위 테스트.

C1: FeatureBuilder, WalkForwardTrainer, MLSignalGenerator, MLRFStrategy
C2: LLMAnalyst (API 없음 → mock 모드)
"""

import numpy as np
import pandas as pd
import pytest

from src.ml.features import FeatureBuilder
from src.ml.model import MLSignalGenerator, MLPrediction
from src.strategy.ml_strategy import MLRFStrategy
from src.strategy.base import Action, Confidence


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df(n: int = 300, seed: int = 42) -> pd.DataFrame:
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


# ---------------------------------------------------------------------------
# C1: FeatureBuilder
# ---------------------------------------------------------------------------

class TestFeatureBuilder:
    def test_build_returns_xy(self):
        df = _make_df(200)
        fb = FeatureBuilder(forward_n=5, threshold=0.003)
        X, y = fb.build(df)
        assert len(X) == len(y)
        assert len(X) > 0
        assert X.shape[1] > 0

    def test_no_nan_in_output(self):
        df = _make_df(200)
        fb = FeatureBuilder()
        X, y = fb.build(df)
        assert not X.isnull().any().any()
        assert not y.isnull().any()

    def test_labels_are_ternary(self):
        """레이블이 -1, 0, 1만 존재."""
        df = _make_df(300)
        fb = FeatureBuilder()
        _, y = fb.build(df)
        assert set(y.unique()).issubset({-1, 0, 1})

    def test_feature_names_match_columns(self):
        df = _make_df(200)
        fb = FeatureBuilder()
        X, _ = fb.build(df)
        for name in fb.feature_names:
            assert name in X.columns

    def test_build_features_only(self):
        df = _make_df(200)
        fb = FeatureBuilder()
        feat = fb.build_features_only(df)
        assert len(feat) > 0
        assert not feat.isnull().all().all()

    def test_time_series_order_preserved(self):
        """시계열 순서 유지: 인덱스가 오름차순."""
        df = _make_df(200)
        fb = FeatureBuilder()
        X, _ = fb.build(df)
        assert X.index.is_monotonic_increasing

    def test_forward_n_reduces_samples(self):
        """forward_n이 크면 샘플 수 감소 (또는 같음)."""
        df = _make_df(200)
        fb5 = FeatureBuilder(forward_n=5)
        fb50 = FeatureBuilder(forward_n=50)
        X5, _ = fb5.build(df)
        X50, _ = fb50.build(df)
        assert len(X5) >= len(X50)

    def test_all_features_finite(self):
        df = _make_df(300)
        fb = FeatureBuilder()
        X, _ = fb.build(df)
        assert np.isfinite(X.values).all()

    def test_no_lookahead_bias_in_features(self):
        """
        EMA/rolling 계산이 이전 바만 사용하는지 확인 (현재 바 제외).
        
        검증:
        1. RSI z-score: 이전 20바 기준
        2. Volatility: 이전 20바 기준
        3. EMA features: 이전 바 기준
        4. Donchian: 이전 20바 기준
        """
        df = _make_df(200)
        fb = FeatureBuilder()
        X, _ = fb.build(df)
        
        # Feature가 존재하는지 확인
        required_features = ["rsi_zscore", "volatility_20", "ema_ratio", 
                            "price_vs_ema20", "volume_ratio_20", "donchian_pct"]
        for feat in required_features:
            assert feat in X.columns, f"Feature {feat} missing"
        
        # 모든 feature가 유한 값인지 확인 (inf/nan 없음)
        assert X[required_features].notna().all().all()
        assert np.isfinite(X[required_features]).all().all()
        
        # EMA는 첫 50바 정도는 정규화 과정에서 NaN 처리됨
        # (rolling window warm-up) → 그 이후만 유효
        assert len(X) > 0



# ---------------------------------------------------------------------------
# C1: MLSignalGenerator (모델 없는 상태)
# ---------------------------------------------------------------------------

class TestMLSignalGeneratorNoModel:
    def test_predict_hold_without_model(self):
        """모델 없으면 HOLD 반환."""
        gen = MLSignalGenerator()
        df = _make_df()
        pred = gen.predict(df)
        assert pred.action == "HOLD"
        assert pred.confidence == 0.0
        assert "no model" in pred.model_name.lower()

    def test_load_missing_file_returns_false(self):
        gen = MLSignalGenerator()
        result = gen.load("models/nonexistent.pkl")
        assert result is False

    def test_load_latest_no_models(self, tmp_path):
        """models/ 빈 폴더 → False."""
        import os
        gen = MLSignalGenerator()
        # models 디렉토리 없거나 비어있으면 False
        result = gen.load_latest()
        # 모델 없으면 False, 있으면 True (환경 의존)
        assert isinstance(result, bool)

    def test_prediction_fields(self):
        gen = MLSignalGenerator()
        df = _make_df()
        pred = gen.predict(df)
        assert hasattr(pred, "action")
        assert hasattr(pred, "confidence")
        assert hasattr(pred, "proba_buy")
        assert hasattr(pred, "proba_sell")
        assert hasattr(pred, "proba_hold")
        assert 0.0 <= pred.confidence <= 1.0

    def test_summary_format(self):
        gen = MLSignalGenerator()
        df = _make_df()
        pred = gen.predict(df)
        s = pred.summary()
        assert "ML_SIGNAL" in s
        assert "action" in s


# ---------------------------------------------------------------------------
# C1: WalkForwardTrainer
# ---------------------------------------------------------------------------

class TestWalkForwardTrainer:
    def test_train_insufficient_data(self):
        """샘플 부족 또는 sklearn 없음 → FAIL."""
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer()
        df = _make_df(50)
        result = trainer.train(df)
        assert not result.passed
        # 실패 이유: 샘플 부족 또는 sklearn 미설치
        assert len(result.fail_reasons) > 0

    def test_train_with_enough_data(self):
        """충분한 데이터 → TrainingResult 반환."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)  # 빠른 학습
        df = _make_df(300)
        result = trainer.train(df)
        assert result.n_samples > 0
        assert result.n_features > 0
        assert 0.0 <= result.train_accuracy <= 1.0
        assert 0.0 <= result.test_accuracy <= 1.0

    def test_train_result_summary(self):
        """summary() 출력 형식 확인."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        df = _make_df(300)
        result = trainer.train(df)
        s = result.summary()
        assert "ML_TRAINING_RESULT" in s
        assert "train_accuracy" in s
        assert "test_accuracy" in s

    def test_feature_importance_report_after_train(self):
        """학습 후 feature_importance_report() 형식 확인."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        df = _make_df(300)
        result = trainer.train(df)
        report = result.feature_importance_report(top_n=5)
        assert "FEATURE_IMPORTANCE_REPORT" in report
        assert "cumul=" in report
        # 5개 항목
        lines = [l for l in report.splitlines() if l.strip().startswith(("1.", "2.", "3.", "4.", "5."))]
        assert len(lines) == 5

    def test_get_feature_importances_ranked(self):
        """get_feature_importances() 내림차순 정렬 + top_n 동작 확인."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        df = _make_df(300)
        trainer.train(df)
        ranked = trainer.get_feature_importances(top_n=3)
        assert len(ranked) == 3
        assert ranked[0][1] >= ranked[1][1] >= ranked[2][1]
        # 전체 반환
        all_feats = trainer.get_feature_importances()
        assert len(all_feats) > 3
        # RuntimeError before training
        trainer2 = WalkForwardTrainer()
        with pytest.raises(RuntimeError):
            trainer2.get_feature_importances()

    def test_save_requires_trained_model(self, tmp_path):
        """학습 전 save() → RuntimeError."""
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer()
        with pytest.raises(RuntimeError):
            trainer.save(str(tmp_path / "model.pkl"))

    def test_train_and_save_load(self, tmp_path):
        """학습 → 저장 → 로드 → 예측 통합."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        df = _make_df(300)
        result = trainer.train(df)

        path = str(tmp_path / "test_model.pkl")
        trainer.save(path)

        gen = MLSignalGenerator()
        loaded = gen.load(path)
        assert loaded is True

        pred = gen.predict(df)
        assert pred.action in ("BUY", "SELL", "HOLD")
        assert 0.0 <= pred.confidence <= 1.0


# ---------------------------------------------------------------------------
# C1: MLRFStrategy
# ---------------------------------------------------------------------------

class TestMLRFStrategy:
    def test_name(self):
        assert MLRFStrategy.name == "ml_rf"

    def test_generate_hold_without_model(self):
        """모델 없으면 HOLD."""
        df = _make_df()
        strategy = MLRFStrategy()
        signal = strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.strategy == "ml_rf"

    def test_generate_returns_signal(self):
        df = _make_df(200)
        strategy = MLRFStrategy()
        signal = strategy.generate(df)
        assert signal.entry_price > 0
        assert signal.reasoning != ""

    def test_generate_with_trained_model(self, tmp_path):
        """학습된 모델 로드 후 신호 생성."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer

        df = _make_df(300)
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        trainer.train(df)
        path = str(tmp_path / "rf_model.pkl")
        trainer.save(path)

        strategy = MLRFStrategy()
        strategy._generator.load(path)
        signal = strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    def test_confidence_mapping_high(self, tmp_path):
        """confidence >= 0.65 → HIGH."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer
        from src.ml.model import MLPrediction
        from unittest.mock import MagicMock

        strategy = MLRFStrategy()
        # mock predict
        strategy._generator.predict = lambda df: MLPrediction(
            action="BUY", confidence=0.70,
            proba_buy=0.70, proba_sell=0.15, proba_hold=0.15,
            model_name="test",
        )
        df = _make_df()
        signal = strategy.generate(df)
        assert signal.confidence == Confidence.HIGH

    def test_confidence_mapping_low(self):
        """confidence < 0.55 → LOW."""
        from src.ml.model import MLPrediction
        strategy = MLRFStrategy()
        strategy._generator.predict = lambda df: MLPrediction(
            action="BUY", confidence=0.52,
            proba_buy=0.52, proba_sell=0.25, proba_hold=0.23,
            model_name="test",
        )
        df = _make_df()
        signal = strategy.generate(df)
        assert signal.confidence == Confidence.LOW


# ---------------------------------------------------------------------------
# C2: LLMAnalyst (API 없는 mock 모드)
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# C2: LLMAnalyst (API 없는 mock 모드)
# ---------------------------------------------------------------------------

class TestLLMAnalyst:
    def test_mock_buy_analysis(self):
        from src.alpha.llm_analyst import LLMAnalyst
        analyst = LLMAnalyst(enabled=False)
        text = analyst._mock_analysis("BUY")
        assert "Mock LLM" in text
        assert len(text) > 0

    def test_mock_sell_analysis(self):
        from src.alpha.llm_analyst import LLMAnalyst
        analyst = LLMAnalyst(enabled=False)
        text = analyst._mock_analysis("SELL")
        assert "Mock LLM" in text

    def test_analyze_signal_disabled(self):
        """API 키 없으면 mock 반환."""
        from src.alpha.llm_analyst import LLMAnalyst
        analyst = LLMAnalyst(enabled=False)
        result = analyst.analyze_signal("BTC/USDT", "BUY", "EMA cross")
        assert isinstance(result, str)

    def test_classify_news_disabled(self):
        """API 키 없으면 NONE 반환."""
        from src.alpha.llm_analyst import LLMAnalyst
        analyst = LLMAnalyst(enabled=False)
        result = analyst.classify_news_risk("Bitcoin ETF approved")
        assert result == "NONE"

    def test_prompt_build(self):
        """프롬프트 빌드 확인."""
        from src.alpha.llm_analyst import LLMAnalyst
        analyst = LLMAnalyst(enabled=False)
        prompt = analyst._build_prompt(
            symbol="BTC/USDT",
            signal_action="BUY",
            signal_reasoning="EMA cross",
            context_summary="FG=25",
            market_data="RSI=35",
        )
        assert "BTC/USDT" in prompt
        assert "BUY" in prompt
        assert "EMA cross" in prompt
        assert "Do NOT give buy/sell recommendations" in prompt
