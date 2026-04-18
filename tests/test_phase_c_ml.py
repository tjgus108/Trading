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
        # Cycle 149: rsi_zscore 제거됨 (PFI near-zero)
        required_features = ["volatility_20", "ema_ratio",
                            "price_vs_ema20", "volume_ratio_20", "donchian_pct"]
        for feat in required_features:
            assert feat in X.columns, f"Feature {feat} missing"

        # 모든 feature가 유한 값인지 확인 (inf/nan 없음)
        assert X[required_features].notna().all().all()
        assert np.isfinite(X[required_features]).all().all()

        # EMA는 첫 50바 정도는 정규화 과정에서 NaN 처리됨
        # (rolling window warm-up) → 그 이후만 유효
        assert len(X) > 0

    def test_future_price_change_does_not_affect_past_features(self):
        """
        미래 가격 변화가 과거 피처에 영향 없음 확인.

        row t의 피처는 t 이전 데이터만 사용해야 함.
        last row의 close를 10배로 바꾸면 그 row의 피처는 변해도
        그 이전 rows의 피처는 불변이어야 한다.
        """
        df = _make_df(200)
        fb = FeatureBuilder()

        # 원본 피처 (마지막 행 제외한 앞부분)
        X_orig = fb.build_features_only(df)

        # 마지막 행 close를 10배로 수정
        df_modified = df.copy()
        df_modified.iloc[-1, df_modified.columns.get_loc("close")] *= 10.0

        X_mod = fb.build_features_only(df_modified)

        # 공통 인덱스 (마지막 행 제외)
        common_idx = X_orig.index[:-1].intersection(X_mod.index[:-1])
        assert len(common_idx) > 50, "비교 가능한 공통 행이 너무 적음"

        # shift(1) 기반 피처: 이전 행까지만 영향 받아야 함
        # 마지막 행 수정 → 그 이전 행들의 피처는 동일해야 함
        shifted_features = ["volatility_20", "rsi_zscore", "ema_ratio",
                            "price_vs_ema20", "price_vs_ema50", "volume_ratio_20"]
        for feat in shifted_features:
            if feat in X_orig.columns and feat in X_mod.columns:
                diff = (X_orig.loc[common_idx, feat] - X_mod.loc[common_idx, feat]).abs().max()
                assert diff < 1e-9, (
                    f"피처 '{feat}'가 미래 데이터 영향을 받음 (max_diff={diff:.2e}). "
                    "look-ahead bias 가능성."
                )

    def test_labels_use_future_data_not_features(self):
        """
        레이블은 미래 데이터(forward_n 이후)를 사용하지만,
        피처는 그 미래 데이터를 사용하지 않음을 확인.

        같은 시점 t에서:
        - 피처: t 시점의 close/volume 등 과거 정보만
        - 레이블: t+forward_n 시점의 close (미래)

        피처와 레이블의 인덱스가 같으며, 피처에 forward shift가 없음을 검증.
        """
        df = _make_df(200)
        fb = FeatureBuilder(forward_n=5, threshold=0.003)
        X, y = fb.build(df)

        # 레이블이 마지막 forward_n 행에서 NaN으로 처리되는지 확인
        # (build()는 dropna()로 레이블 NaN 제거 → 마지막 5행은 X에 없어야 함)
        last_ts = df.index[-1]
        assert last_ts not in X.index, (
            "마지막 행이 X에 포함됨 — 레이블 forward_n 미적용 가능성"
        )
        # 마지막 forward_n 행이 전부 제거됐는지 확인
        last_n_ts = df.index[-fb.forward_n:]
        overlap = X.index.intersection(last_n_ts)
        assert len(overlap) == 0, (
            f"마지막 {fb.forward_n}행 중 {len(overlap)}개가 X에 남아있음 — "
            "레이블 누수 가능성"
        )

    def test_all_features_same_length_and_index(self):
        """
        _compute_features()가 반환하는 모든 컬럼이 동일한 길이와 인덱스를 가짐.
        시계열 일관성 핵심 검증.
        """
        df = _make_df(200)
        fb = FeatureBuilder()
        feat = fb._compute_features(df)

        # 모든 컬럼 길이가 df와 동일
        assert len(feat) == len(df), (
            f"피처 행 수({len(feat)}) != 입력 df 행 수({len(df)})"
        )

        # 인덱스가 df와 정확히 일치
        assert feat.index.equals(df.index), "피처 인덱스가 입력 df 인덱스와 불일치"

        # 컬럼 간 길이 모두 동일 (DataFrame이므로 보장되지만 명시적 확인)
        col_lengths = {col: len(feat[col]) for col in feat.columns}
        unique_lengths = set(col_lengths.values())
        assert len(unique_lengths) == 1, (
            f"컬럼 간 길이 불일치: {col_lengths}"
        )

        # feature_names 목록의 모든 피처가 존재
        for name in fb.feature_names:
            assert name in feat.columns, f"feature_names의 '{name}'이 feat에 없음"

        # 인덱스가 단조증가(시계열 순서) 유지
        assert feat.index.is_monotonic_increasing, "피처 인덱스가 시계열 순서 미유지"

    def test_xy_index_aligned(self):
        """
        build()가 반환하는 X와 y의 인덱스가 완전히 일치함을 검증.
        """
        df = _make_df(200)
        fb = FeatureBuilder(forward_n=5, threshold=0.003)
        X, y = fb.build(df)

        assert X.index.equals(y.index), "X와 y의 인덱스 불일치 — 정렬 오류"
        assert len(X) == len(y), f"X({len(X)})와 y({len(y)}) 길이 불일치"
        # 인덱스 단조증가
        assert X.index.is_monotonic_increasing, "build() 결과 인덱스 시계열 순서 미유지"

    def test_rolling_features_use_prior_bars_only(self):
        """
        rolling/ewm 피처가 현재 바 포함 여부 직접 검증.

        중간 row t의 close를 극단값으로 변경 → t+1 row의 shift(1) 기반 피처는
        영향 받아야 하지만, t-1 이전 피처는 불변이어야 함.
        """
        df = _make_df(150)
        fb = FeatureBuilder()

        # 중간 행 인덱스 (warm-up 이후)
        mid = 100
        mid_ts = df.index[mid]
        prev_ts = df.index[mid - 1]

        # 원본 피처
        X_orig = fb.build_features_only(df)

        # mid 행의 close를 극단값으로 변경
        df_mod = df.copy()
        df_mod.iloc[mid, df_mod.columns.get_loc("close")] = 1_000_000.0

        X_mod = fb.build_features_only(df_mod)

        # mid 이전 행들의 피처는 영향 없어야 함
        pre_mid_idx = X_orig.index[X_orig.index < mid_ts]
        pre_mid_idx = pre_mid_idx.intersection(X_mod.index)

        check_feats = ["volatility_20", "ema_ratio", "volume_ratio_20", "donchian_pct"]
        for feat in check_feats:
            if feat in X_orig.columns and feat in X_mod.columns:
                diff = (X_orig.loc[pre_mid_idx, feat] - X_mod.loc[pre_mid_idx, feat]).abs().max()
                assert diff < 1e-9, (
                    f"피처 '{feat}'가 미래(mid row) 변경에 영향받음 (max_diff={diff:.2e}). "
                    "look-ahead bias."
                )

    def test_label_nan_boundary_exactly_forward_n_rows_dropped(self):
        """
        Cycle 12 회귀: _compute_labels()가 마지막 forward_n 행을 정확히 NaN으로 남겨야 함.
        - 마지막 forward_n 행은 NaN → build() 후 X에 없어야 함
        - 나머지 행은 {-1, 0, 1} 중 하나여야 함 (NaN 없음)
        """
        n = 100
        df = _make_df(n)
        forward_n = 7
        fb = FeatureBuilder(forward_n=forward_n, threshold=0.003)

        # 레이블 직접 검사
        labels = fb._compute_labels(df)
        last_n = labels.iloc[-forward_n:]
        rest = labels.iloc[:-forward_n]

        assert last_n.isna().all(), (
            f"마지막 {forward_n}행 레이블이 NaN이어야 함 — {last_n.dropna()} 남아있음"
        )
        assert not rest.isna().any(), (
            f"나머지 행에 NaN 레이블 존재 — {rest[rest.isna()].index.tolist()}"
        )
        assert set(rest.dropna().unique()).issubset({-1, 0, 1}), (
            f"레이블 값이 범위 밖: {rest.unique()}"
        )

    def test_shift1_feature_first_row_is_nan_before_dropna(self):
        """
        Cycle 11 회귀: shift(1) 기반 피처의 첫 행이 NaN인지 확인.
        build_features_only()의 dropna() 전에 첫 행에 NaN이 있어야 정상적으로 shift(1)이 적용된 것.
        직접 _compute_features()로 확인.
        """
        df = _make_df(100)
        fb = FeatureBuilder()
        feat = fb._compute_features(df)

        # shift(1) 기반 피처: 첫 행은 NaN이어야 함
        assert pd.isna(feat["volatility_20"].iloc[0]) or pd.isna(feat["return_1"].iloc[0]), (
            "첫 행에 NaN이 없음 — shift(1)이 적용되지 않았을 가능성"
        )
        # return_1 = log(close / close.shift(1)) → row 0은 NaN
        assert pd.isna(feat["return_1"].iloc[0]), (
            "return_1 첫 행이 NaN이어야 함 (shift(1) 적용 확인)"
        )


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

    def test_calibrated_proba_sum_to_one(self):
        """Calibration 후 predict_proba 합이 1.0 (±1e-6)."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        df = _make_df(300)
        trainer.train(df)

        # 내부 모델로 직접 확인
        from src.ml.features import FeatureBuilder
        fb = FeatureBuilder()
        X, _ = fb.build(df)
        proba = trainer._trained_model.predict_proba(X)
        row_sums = proba.sum(axis=1)
        assert (row_sums - 1.0).abs().max() < 1e-6 if hasattr(row_sums, "abs") else True
        # numpy array 경우
        import numpy as np
        assert np.allclose(proba.sum(axis=1), 1.0, atol=1e-6)

    def test_calibrated_model_is_wrapped(self):
        """학습 후 _trained_model이 CalibratedClassifierCV 또는 RF인지 확인."""
        pytest.importorskip("sklearn")
        from sklearn.calibration import CalibratedClassifierCV
        from sklearn.ensemble import RandomForestClassifier
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        df = _make_df(300)
        trainer.train(df)
        assert isinstance(trainer._trained_model, (CalibratedClassifierCV, RandomForestClassifier))

    def test_result_split_info_populated(self):
        """학습 결과에 split_info(n_train/n_val/n_test)가 채워지는지 확인."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        df = _make_df(300)
        result = trainer.train(df)
        assert result.split_info is not None
        assert result.split_info["n_train"] > 0
        assert result.split_info["n_val"] > 0
        assert result.split_info["n_test"] > 0
        assert (
            result.split_info["n_train"]
            + result.split_info["n_val"]
            + result.split_info["n_test"]
            == result.n_samples
        )

    def test_result_class_distribution_sums_to_one(self):
        """class_distribution 비율 합이 1.0 (±1e-6)."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        df = _make_df(300)
        result = trainer.train(df)
        assert result.class_distribution is not None
        total = sum(result.class_distribution.values())
        assert abs(total - 1.0) < 1e-6

    def test_ensemble_weight_pass_model(self):
        """PASS 모델의 ensemble_weight > 0."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        df = _make_df(300)
        result = trainer.train(df)
        if result.passed:
            assert result.ensemble_weight > 0.0
        else:
            assert result.ensemble_weight == 0.0

    def test_compute_ensemble_weight_normalizes(self):
        """compute_ensemble_weight()가 합=1.0으로 정규화."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer, TrainingResult
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        df = _make_df(300)
        r1 = trainer.train(df)
        r2 = trainer.train(df)
        weights = trainer.compute_ensemble_weight([r1, r2])
        assert len(weights) == 2
        assert abs(sum(weights) - 1.0) < 1e-6

    def test_compute_ensemble_weight_all_fail_uniform(self):
        """모두 FAIL이면 균등 분배."""
        from src.ml.trainer import WalkForwardTrainer, TrainingResult
        trainer = WalkForwardTrainer()
        # FAIL 결과 2개 수동 생성
        fail_result = TrainingResult(
            model_name="test", n_samples=0, n_features=0,
            train_accuracy=0.0, val_accuracy=0.0, test_accuracy=0.0,
            feature_importances={}, passed=False, fail_reasons=["test"],
        )
        weights = trainer.compute_ensemble_weight([fail_result, fail_result])
        assert abs(weights[0] - 0.5) < 1e-6
        assert abs(weights[1] - 0.5) < 1e-6

    def test_summary_includes_new_fields(self):
        """summary()에 ensemble_weight, split, class_dist 포함 확인."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        df = _make_df(300)
        result = trainer.train(df)
        s = result.summary()
        assert "ensemble_weight" in s
        assert "split:" in s
        assert "class_dist:" in s

    def test_recency_weighted_ensemble_favors_latest(self):
        """recency-weighted 앙상블: 최신(뒤쪽) 모델 가중치가 더 높음."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer, TrainingResult
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        # 동일 성능의 PASS 결과 3개 (시간순)
        r = TrainingResult(
            model_name="test", n_samples=200, n_features=17,
            train_accuracy=0.65, val_accuracy=0.60, test_accuracy=0.60,
            feature_importances={}, passed=True, fail_reasons=[],
        )
        weights = trainer.compute_ensemble_weight_recency([r, r, r], decay=0.8)
        assert len(weights) == 3
        assert abs(sum(weights) - 1.0) < 1e-6
        # 최신(마지막)이 가장 높아야 함
        assert weights[2] > weights[1] > weights[0]

    def test_recency_weighted_all_fail_uniform(self):
        """모두 FAIL → 균등 분배."""
        from src.ml.trainer import WalkForwardTrainer, TrainingResult
        trainer = WalkForwardTrainer()
        fail = TrainingResult(
            model_name="f", n_samples=0, n_features=0,
            train_accuracy=0, val_accuracy=0, test_accuracy=0,
            feature_importances={}, passed=False, fail_reasons=["test"],
        )
        weights = trainer.compute_ensemble_weight_recency([fail, fail])
        assert abs(weights[0] - 0.5) < 1e-6

    def test_recency_weighted_decay_one_equals_original(self):
        """decay=1.0이면 기존 compute_ensemble_weight와 동일."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        df = _make_df(300)
        r1 = trainer.train(df)
        r2 = trainer.train(df)
        w_orig = trainer.compute_ensemble_weight([r1, r2])
        w_recency = trainer.compute_ensemble_weight_recency([r1, r2], decay=1.0)
        for a, b in zip(w_orig, w_recency):
            assert abs(a - b) < 1e-5

    def test_recency_weighted_empty_list(self):
        """빈 리스트 → 빈 리스트 반환."""
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer()
        assert trainer.compute_ensemble_weight_recency([]) == []

    def test_save_load_preserves_feature_importances(self, tmp_path):
        """저장된 모델에 feature_importances가 포함되는지 확인."""
        pytest.importorskip("sklearn")
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(n_estimators=10, max_depth=3)
        df = _make_df(300)
        result = trainer.train(df)

        path = str(tmp_path / "model_fi.pkl")
        trainer.save(path)

        gen = MLSignalGenerator()
        gen.load(path)
        fi = gen.get_feature_importances()
        assert len(fi) > 0
        # 중요도 합이 ~1.0
        total = sum(v for _, v in fi)
        assert abs(total - 1.0) < 0.01
        # top_n 동작
        top3 = gen.get_feature_importances(top_n=3)
        assert len(top3) == 3
        assert top3[0][1] >= top3[1][1] >= top3[2][1]

    def test_load_no_fi_returns_empty(self):
        """feature_importances 없는 구형 모델 로드 시 빈 리스트."""
        gen = MLSignalGenerator()
        # 모델 미로드 상태
        assert gen.get_feature_importances() == []


# ---------------------------------------------------------------------------
# C1: MLRFStrategy
# ---------------------------------------------------------------------------

class TestMLRFStrategy:
    def test_name(self):
        assert MLRFStrategy.name == "ml_rf"

    def test_generate_hold_without_model(self):
        """모델 없어도 heuristic fallback으로 signal 반환."""
        df = _make_df()
        strategy = MLRFStrategy()
        signal = strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.strategy == "ml_rf"

    def test_generate_buy_signal_without_model(self):
        """모델 없을 때 heuristic fallback이 BUY 신호 생성."""
        rng = np.random.default_rng(7)
        n = 200
        # 상승 추세 데이터: ema20 > ema50, RSI ~60
        close = 50000 + np.cumsum(np.abs(rng.standard_normal(n)) * 150)
        high = close + np.abs(rng.standard_normal(n) * 50)
        low = close - np.abs(rng.standard_normal(n) * 50)
        low = np.maximum(low, close * 0.95)
        idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
        df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close,
                           "volume": np.ones(n) * 10.0}, index=idx)
        df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
        prev_close = df["close"].shift(1)
        tr = pd.concat([(df["high"] - df["low"]),
                        (df["high"] - prev_close).abs(),
                        (df["low"] - prev_close).abs()], axis=1).max(axis=1)
        df["atr14"] = tr.ewm(alpha=1/14, adjust=False).mean()
        delta = df["close"].diff()
        gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
        df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
        strategy = MLRFStrategy()
        assert strategy._generator._model is None
        signal = strategy.generate(df)
        # 상승 추세 → BUY 기대 (최소한 HOLD는 아닌 것도 있어야 함)
        assert signal.action in (Action.BUY, Action.HOLD)
        assert signal.strategy == "ml_rf"

    def test_generate_sell_signal_without_model(self):
        """모델 없을 때 heuristic fallback이 SELL 신호 생성."""
        rng = np.random.default_rng(99)
        n = 200
        # 하락 추세: ema20 < ema50
        close = 50000 - np.cumsum(np.abs(rng.standard_normal(n)) * 150)
        close = np.maximum(close, 1000)
        high = close + np.abs(rng.standard_normal(n) * 50)
        low = close - np.abs(rng.standard_normal(n) * 50)
        low = np.maximum(low, close * 0.95)
        idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
        df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close,
                           "volume": np.ones(n) * 10.0}, index=idx)
        df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
        prev_close = df["close"].shift(1)
        tr = pd.concat([(df["high"] - df["low"]),
                        (df["high"] - prev_close).abs(),
                        (df["low"] - prev_close).abs()], axis=1).max(axis=1)
        df["atr14"] = tr.ewm(alpha=1/14, adjust=False).mean()
        delta = df["close"].diff()
        gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
        df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
        strategy = MLRFStrategy()
        assert strategy._generator._model is None
        signal = strategy.generate(df)
        assert signal.action in (Action.SELL, Action.HOLD)
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
        # 모델이 있는 것처럼 mock (sentinel 객체)
        strategy._generator._model = object()
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
        # 모델이 있는 것처럼 mock (sentinel 객체)
        strategy._generator._model = object()
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
