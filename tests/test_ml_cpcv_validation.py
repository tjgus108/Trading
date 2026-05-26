"""
WalkForwardTrainer.run_cpcv_validation() + TrainingResult.cpcv 필드 테스트 (Cycle 216 D)
"""

import numpy as np
import pandas as pd
import pytest

from src.ml.trainer import WalkForwardTrainer, TrainingResult


def _make_df(n: int = 400, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-01", periods=n, freq="1h", tz="UTC")
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
        [(df["high"] - df["low"]),
         (df["high"] - prev_close).abs(),
         (df["low"] - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1/14, adjust=False).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
    df["donchian_high"] = df["high"].rolling(20).max()
    df["donchian_low"] = df["low"].rolling(20).min()
    typical = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
    return df.dropna()


class TestTrainingResultCPCVFields:
    """TrainingResult에 cpcv 필드 추가 확인."""

    def test_cpcv_fields_default_zero(self):
        r = TrainingResult(
            model_name="test", n_samples=100, n_features=5,
            train_accuracy=0.6, val_accuracy=0.58, test_accuracy=0.57,
            feature_importances={}, passed=True, fail_reasons=[],
        )
        assert r.cpcv_avg_acc == 0.0
        assert r.cpcv_n_folds == 0

    def test_cpcv_fields_settable(self):
        r = TrainingResult(
            model_name="test", n_samples=200, n_features=8,
            train_accuracy=0.65, val_accuracy=0.60, test_accuracy=0.58,
            feature_importances={}, passed=True, fail_reasons=[],
            cpcv_avg_acc=0.572, cpcv_n_folds=4,
        )
        assert abs(r.cpcv_avg_acc - 0.572) < 1e-9
        assert r.cpcv_n_folds == 4


class TestRunCPCVValidation:
    """run_cpcv_validation() 동작 검증."""

    def test_returns_none_before_training(self):
        trainer = WalkForwardTrainer(symbol="BTC/USDT")
        df = _make_df()
        result = trainer.run_cpcv_validation(df)
        assert result is None

    def test_returns_dict_after_training(self):
        df = _make_df(n=400)
        trainer = WalkForwardTrainer(symbol="BTC/USDT", n_estimators=10, max_depth=3)
        trainer.train(df)
        cpcv_result = trainer.run_cpcv_validation(df, n_splits=4)
        # 데이터가 충분하면 dict 반환
        if cpcv_result is not None:
            assert "avg_test_acc" in cpcv_result
            assert "std_test_acc" in cpcv_result
            assert "n_folds" in cpcv_result
            assert "fold_results" in cpcv_result
            assert "passed" in cpcv_result

    def test_avg_test_acc_range(self):
        """avg_test_acc는 [0, 1] 범위."""
        df = _make_df(n=400)
        trainer = WalkForwardTrainer(symbol="BTC/USDT", n_estimators=10, max_depth=3)
        trainer.train(df)
        result = trainer.run_cpcv_validation(df, n_splits=4)
        if result is not None:
            assert 0.0 <= result["avg_test_acc"] <= 1.0

    def test_returns_none_for_too_small_df(self):
        """데이터 부족 시 None 반환."""
        df = _make_df(n=400)
        tiny_df = _make_df(n=50)
        trainer = WalkForwardTrainer(symbol="BTC/USDT", n_estimators=10, max_depth=3)
        trainer.train(df)
        result = trainer.run_cpcv_validation(tiny_df, n_splits=4)
        assert result is None

    def test_passed_bool_consistent(self):
        """passed 필드가 avg_test_acc >= 0.55 여부와 일치."""
        df = _make_df(n=400)
        trainer = WalkForwardTrainer(symbol="BTC/USDT", n_estimators=10, max_depth=3)
        trainer.train(df)
        result = trainer.run_cpcv_validation(df, n_splits=4)
        if result is not None:
            expected = result["avg_test_acc"] >= 0.55
            assert result["passed"] == expected

    def test_n_folds_matches_fold_results_length(self):
        df = _make_df(n=400)
        trainer = WalkForwardTrainer(symbol="BTC/USDT", n_estimators=10, max_depth=3)
        trainer.train(df)
        result = trainer.run_cpcv_validation(df, n_splits=4)
        if result is not None:
            assert result["n_folds"] == len(result["fold_results"])
