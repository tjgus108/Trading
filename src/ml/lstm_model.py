"""
C1 고도화. LSTMSignalGenerator: 시계열 패턴 학습 기반 신호 생성.

구현:
  - PyTorch LSTM (torch 설치 시 자동 사용)
  - torch 없으면 numpy SimpleRNN fallback (기본 동작 보장)
  - MLSignalGenerator와 동일 인터페이스 (predict → MLPrediction)

모델 구조 (PyTorch):
  LSTM(input=15피처, hidden=64, layers=2) → FC(64→3) → Softmax

학습:
  - 시계열 윈도우: 20 캔들 → 다음 방향 예측
  - Train/val/test: 60/20/20
  - Early stopping (val_loss 기준)
  - 모델 파일: models/lstm_<symbol>_<date>.pt

numpy fallback:
  - 단순 이동 평균 방향성 예측
  - 정확도 낮음 (기본 동작 보장용)
"""

import logging
import os
import pickle
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from src.ml.features import FeatureBuilder
from src.ml.model import MLPrediction

logger = logging.getLogger(__name__)

MODELS_DIR = Path("models")
SEQUENCE_LEN = 20       # LSTM 입력 시퀀스 길이
HIDDEN_SIZE = 64
N_LAYERS = 2
EPOCHS = 50
LEARNING_RATE = 0.001
BATCH_SIZE = 32
EARLY_STOP_PATIENCE = 10
MIN_ACCURACY = 0.54


def _torch_available() -> bool:
    try:
        import torch  # noqa
        return True
    except ImportError:
        return False


class LSTMSignalGenerator:
    """
    LSTM 기반 신호 생성기.

    torch 설치 시: LSTM 모델 학습/추론
    torch 없음: numpy SimpleRNN fallback

    인터페이스: MLSignalGenerator와 동일
    """

    name = "lstm"

    def __init__(self, symbol: str = "BTC/USDT", sequence_len: int = SEQUENCE_LEN):
        self.symbol = symbol
        self.sequence_len = sequence_len
        self.feature_builder = FeatureBuilder(forward_n=5, threshold=0.003)
        self._model = None
        self._scaler = None
        self._model_name = "no model"
        self._use_torch = _torch_available()
        logger.info("LSTMSignalGenerator: torch=%s", self._use_torch)

    def load(self, path: str) -> bool:
        try:
            if self._use_torch:
                return self._load_torch(path)
            else:
                return self._load_numpy(path)
        except Exception as e:
            logger.warning("LSTM model load failed (%s): %s", path, e)
            return False

    def load_latest(self) -> bool:
        MODELS_DIR.mkdir(exist_ok=True)
        pattern = "lstm_*.pt" if self._use_torch else "lstm_*.pkl"
        pkls = sorted(MODELS_DIR.glob(pattern), reverse=True)
        if not pkls:
            logger.info("No LSTM model found")
            return False
        return self.load(str(pkls[0]))

    def predict(self, df: pd.DataFrame) -> MLPrediction:
        """마지막 완성 캔들 기준 예측."""
        if self._model is None:
            return MLPrediction(
                action="HOLD", confidence=0.0,
                proba_buy=0.0, proba_sell=0.0, proba_hold=1.0,
                model_name="no LSTM model",
                note="LSTM 모델 미학습 — LSTMTrainer로 학습 필요",
            )

        feat = self.feature_builder.build_features_only(df).dropna()
        if len(feat) < self.sequence_len + 1:
            return MLPrediction(
                action="HOLD", confidence=0.0,
                proba_buy=0.0, proba_sell=0.0, proba_hold=1.0,
                model_name=self._model_name,
                note="시퀀스 데이터 부족",
            )

        if self._use_torch:
            return self._predict_torch(feat)
        return self._predict_numpy(feat)

    def train(self, df: pd.DataFrame) -> dict:
        """
        모델 학습.
        Returns: {"passed": bool, "test_accuracy": float, "model_path": str or None}
        """
        if self._use_torch:
            return self._train_torch(df)
        return self._train_numpy(df)

    # ------------------------------------------------------------------
    # PyTorch 구현
    # ------------------------------------------------------------------

    def _build_torch_model(self, n_features: int):
        import torch
        import torch.nn as nn

        class LSTMClassifier(nn.Module):
            def __init__(self):
                super().__init__()
                self.lstm = nn.LSTM(
                    n_features, HIDDEN_SIZE, N_LAYERS,
                    batch_first=True, dropout=0.2,
                )
                self.fc = nn.Linear(HIDDEN_SIZE, 3)  # {-1, 0, 1}

            def forward(self, x):
                out, _ = self.lstm(x)
                return self.fc(out[:, -1, :])  # 마지막 타임스텝

        return LSTMClassifier()

    def _prepare_sequences(self, X: np.ndarray, y: np.ndarray):
        """슬라이딩 윈도우로 시퀀스 생성."""
        seq_X, seq_y = [], []
        for i in range(self.sequence_len, len(X)):
            seq_X.append(X[i - self.sequence_len:i])
            seq_y.append(y[i])
        return np.array(seq_X), np.array(seq_y)

    def _train_torch(self, df: pd.DataFrame) -> dict:
        try:
            import torch
            import torch.nn as nn
            from torch.utils.data import DataLoader, TensorDataset
        except ImportError:
            return {"passed": False, "test_accuracy": 0.0, "model_path": None,
                    "fail_reasons": ["torch 미설치"]}

        feat_df, label_s = self.feature_builder.build(df)
        if len(feat_df) < self.sequence_len + 50:
            return {"passed": False, "test_accuracy": 0.0, "model_path": None,
                    "fail_reasons": ["데이터 부족"]}

        # 정규화
        from sklearn.preprocessing import StandardScaler  # type: ignore
        scaler = StandardScaler()
        X = scaler.fit_transform(feat_df.values).astype(np.float32)
        # 레이블 {-1,0,1} → {0,1,2}
        y_raw = label_s.values
        y = (y_raw + 1).astype(np.int64)  # -1→0, 0→1, 1→2

        seq_X, seq_y = self._prepare_sequences(X, y)
        n = len(seq_X)
        tr_e, va_e = int(n * 0.6), int(n * 0.8)

        def make_loader(X_, y_, shuffle):
            ds = TensorDataset(torch.FloatTensor(X_), torch.LongTensor(y_))
            return DataLoader(ds, batch_size=BATCH_SIZE, shuffle=shuffle)

        tr_loader = make_loader(seq_X[:tr_e], seq_y[:tr_e], True)
        va_loader = make_loader(seq_X[tr_e:va_e], seq_y[tr_e:va_e], False)
        te_loader = make_loader(seq_X[va_e:], seq_y[va_e:], False)

        model = self._build_torch_model(X.shape[1])
        optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
        criterion = nn.CrossEntropyLoss()

        best_val_loss = float("inf")
        best_state = {k: v.clone() for k, v in model.state_dict().items()}
        patience = 0

        for epoch in range(EPOCHS):
            model.train()
            for xb, yb in tr_loader:
                optimizer.zero_grad()
                loss = criterion(model(xb), yb)
                loss.backward()
                optimizer.step()

            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for xb, yb in va_loader:
                    val_loss += criterion(model(xb), yb).item()

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience = 0
                best_state = {k: v.clone() for k, v in model.state_dict().items()}
            else:
                patience += 1
                if patience >= EARLY_STOP_PATIENCE:
                    logger.info("LSTM early stop at epoch %d", epoch)
                    break

        model.load_state_dict(best_state)

        # Test accuracy
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for xb, yb in te_loader:
                preds = model(xb).argmax(dim=1)
                correct += (preds == yb).sum().item()
                total += len(yb)
        test_acc = correct / total if total > 0 else 0.0
        passed = test_acc >= MIN_ACCURACY

        self._model = model
        self._scaler = scaler
        self._model_name = f"lstm_{self.symbol.replace('/', '').lower()}_{date.today()}"

        model_path = None
        if passed:
            MODELS_DIR.mkdir(exist_ok=True)
            model_path = str(MODELS_DIR / f"{self._model_name}.pt")
            torch.save({"model_state": best_state, "scaler": scaler,
                        "n_features": X.shape[1], "name": self._model_name}, model_path)
            logger.info("LSTM model saved: %s (acc=%.3f)", model_path, test_acc)

        return {
            "passed": passed, "test_accuracy": round(test_acc, 4),
            "model_path": model_path,
            "fail_reasons": [] if passed else [f"test_acc {test_acc:.3f} < {MIN_ACCURACY}"],
        }

    def _predict_torch(self, feat: pd.DataFrame) -> MLPrediction:
        import torch

        X = self._scaler.transform(feat.values).astype(np.float32)
        seq = torch.FloatTensor(X[-self.sequence_len:]).unsqueeze(0)

        self._model.eval()
        with torch.no_grad():
            logits = self._model(seq)[0]
            proba = torch.softmax(logits, dim=0).numpy()

        p_sell, p_hold, p_buy = float(proba[0]), float(proba[1]), float(proba[2])
        pred = int(proba.argmax()) - 1  # {0,1,2} → {-1,0,1}
        action_map = {1: "BUY", -1: "SELL", 0: "HOLD"}
        action = action_map[pred]
        confidence = float(proba.max())

        return MLPrediction(
            action=action, confidence=confidence,
            proba_buy=p_buy, proba_sell=p_sell, proba_hold=p_hold,
            model_name=self._model_name,
        )

    def _load_torch(self, path: str) -> bool:
        import torch
        from sklearn.preprocessing import StandardScaler  # type: ignore

        data = torch.load(path, map_location="cpu", weights_only=False)
        n_features = data["n_features"]
        model = self._build_torch_model(n_features)
        model.load_state_dict(data["model_state"])
        model.eval()
        self._model = model
        self._scaler = data["scaler"]
        self._model_name = data.get("name", Path(path).stem)
        return True

    # ------------------------------------------------------------------
    # Numpy SimpleRNN fallback (torch 없을 때)
    # ------------------------------------------------------------------

    def _train_numpy(self, df: pd.DataFrame) -> dict:
        """단순 이동평균 방향성 모델 (torch 없을 때)."""
        feat_df, label_s = self.feature_builder.build(df)
        if len(feat_df) < 100:
            return {"passed": False, "test_accuracy": 0.0, "model_path": None,
                    "fail_reasons": ["데이터 부족"]}

        # 단순 모멘텀 모델: return_5 부호로 방향 예측
        n = len(feat_df)
        test_start = int(n * 0.8)
        X_test = feat_df.iloc[test_start:]
        y_test = label_s.iloc[test_start:]

        preds = np.sign(X_test["return_5"].values).astype(int)
        correct = (preds == y_test.values).sum()
        test_acc = correct / len(y_test) if len(y_test) > 0 else 0.0
        passed = test_acc >= MIN_ACCURACY

        self._model = {"type": "numpy_momentum"}
        self._model_name = f"lstm_numpy_{self.symbol.replace('/', '').lower()}_{date.today()}"

        return {
            "passed": passed,
            "test_accuracy": round(test_acc, 4),
            "model_path": None,
            "fail_reasons": [] if passed else [f"numpy fallback acc {test_acc:.3f} < {MIN_ACCURACY}"],
        }

    def _predict_numpy(self, feat: pd.DataFrame) -> MLPrediction:
        """numpy fallback 예측."""
        recent_ret = feat["return_5"].iloc[-1] if "return_5" in feat.columns else 0.0
        if recent_ret > 0.002:
            action, p_buy, p_sell = "BUY", 0.6, 0.2
        elif recent_ret < -0.002:
            action, p_buy, p_sell = "SELL", 0.2, 0.6
        else:
            action, p_buy, p_sell = "HOLD", 0.3, 0.3

        return MLPrediction(
            action=action, confidence=0.55,
            proba_buy=p_buy, proba_sell=p_sell, proba_hold=1 - p_buy - p_sell,
            model_name=self._model_name + "(numpy_fallback)",
            note="torch 없음 — numpy fallback 사용",
        )

    def _load_numpy(self, path: str) -> bool:
        with open(path, "rb") as f:
            data = pickle.load(f)
        self._model = data.get("model", {"type": "numpy_momentum"})
        self._model_name = data.get("name", "lstm_numpy")
        return True
