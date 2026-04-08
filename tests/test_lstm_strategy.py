"""
Tests for MLLSTMStrategy and scripts/train_ml.py.
"""

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.strategy.lstm_strategy import MLLSTMStrategy
from src.strategy.base import Action, Confidence, Signal


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
# Tests
# ---------------------------------------------------------------------------

class TestMLLSTMStrategy:

    def test_name(self):
        assert MLLSTMStrategy.name == "ml_lstm"

    def test_generate_hold_without_model(self):
        """모델 없을 때 HOLD 반환."""
        strategy = MLLSTMStrategy()
        # 모델이 없으면 generator._model is None → HOLD
        assert strategy._generator._model is None
        df = _make_df(300)
        signal = strategy.generate(df)
        assert signal.action == Action.HOLD
        assert signal.confidence == Confidence.LOW

    def test_generate_returns_signal(self):
        """generate()가 올바른 Signal 반환."""
        strategy = MLLSTMStrategy()
        df = _make_df(300)
        signal = strategy.generate(df)

        assert isinstance(signal, Signal)
        assert signal.strategy == "ml_lstm"
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.entry_price > 0
        assert signal.bull_case is not None
        assert signal.bear_case is not None

    def test_generate_after_numpy_train(self):
        """numpy fallback train 후 generate() — 모델 로드 여부와 무관하게 Signal 반환."""
        strategy = MLLSTMStrategy()
        df = _make_df(300)
        # numpy train
        result = strategy._generator.train(df)
        # 학습 후에도 generate가 정상 동작
        signal = strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.strategy == "ml_lstm"

    def test_registry_contains_ml_lstm(self):
        """STRATEGY_REGISTRY에 ml_lstm 등록 확인."""
        from src.orchestrator import STRATEGY_REGISTRY
        assert "ml_lstm" in STRATEGY_REGISTRY
        assert STRATEGY_REGISTRY["ml_lstm"] is MLLSTMStrategy


class TestTrainMlScript:

    def test_script_runs_demo(self):
        """scripts/train_ml.py --demo --model rf 가 exit code 0으로 종료."""
        script = Path(__file__).parent.parent / "scripts" / "train_ml.py"
        result = subprocess.run(
            ["/usr/bin/python3", str(script), "--demo", "--model", "rf", "--limit", "200"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(Path(__file__).parent.parent),
        )
        assert result.returncode == 0, (
            f"Script exited {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        # 결과 출력 확인
        assert "ML_TRAINING_RESULT" in result.stdout

    def test_script_runs_demo_lstm(self):
        """scripts/train_ml.py --demo --model lstm 가 exit code 0으로 종료."""
        script = Path(__file__).parent.parent / "scripts" / "train_ml.py"
        result = subprocess.run(
            ["/usr/bin/python3", str(script), "--demo", "--model", "lstm", "--limit", "200"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(Path(__file__).parent.parent),
        )
        assert result.returncode == 0, (
            f"Script exited {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "ML_TRAINING_RESULT" in result.stdout
