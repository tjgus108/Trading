"""
E1. HMMRegimeDetector: 2-state HMM 기반 bull/bear 레짐 탐지.

hmmlearn 없으면 볼린저 밴드 기반 fallback 사용.
- bull=1, bear=0
- 피처: log_return, volatility_5, rsi_change
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

BEAR = 0
BULL = 1


class HMMRegimeDetector:
    """
    2-state HMM으로 bull/bear 레짐 탐지.

    fit(df) → 학습
    predict(df) → int (0=bear, 1=bull)
    predict_sequence(df) → pd.Series (전체 레짐 시퀀스)
    """

    def __init__(self, n_states: int = 2, n_iter: int = 100, random_state: int = 42):
        self.n_states = n_states
        self.n_iter = n_iter
        self.random_state = random_state
        self._model = None
        self._fitted = False
        self._use_fallback = False
        self._bull_state: Optional[int] = None  # HMM 내부 상태 중 bull에 해당하는 인덱스

        # hmmlearn 가용 여부 확인
        try:
            from hmmlearn import hmm  # noqa: F401
            self._hmmlearn_available = True
        except ImportError:
            logger.info("hmmlearn 없음 — Bollinger Band fallback 사용")
            self._hmmlearn_available = False
            self._use_fallback = True

    # ------------------------------------------------------------------
    # Feature extraction
    # ------------------------------------------------------------------

    def _build_features(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """log_return, volatility_5, rsi_change 3개 피처 반환."""
        if len(df) < 10:
            return None

        close = df["close"]
        log_ret = np.log(close / close.shift(1))

        vol5 = log_ret.rolling(5).std().fillna(0.0)

        if "rsi14" in df.columns:
            rsi = df["rsi14"].fillna(50.0)
        else:
            # RSI 직접 계산
            delta = close.diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = (-delta.clip(upper=0)).rolling(14).mean()
            rs = gain / (loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            rsi = rsi.fillna(50.0)

        rsi_change = rsi.diff().fillna(0.0)

        feat = pd.DataFrame({
            "log_return": log_ret,
            "volatility_5": vol5,
            "rsi_change": rsi_change,
        }).dropna()

        if len(feat) < 5:
            return None

        return feat.values

    # ------------------------------------------------------------------
    # Fit / Predict (HMM)
    # ------------------------------------------------------------------

    def fit(self, df: pd.DataFrame) -> "HMMRegimeDetector":
        """HMM 학습. hmmlearn 없으면 fallback 모드로 설정."""
        if self._use_fallback:
            self._fitted = True
            return self

        X = self._build_features(df)
        if X is None:
            logger.warning("HMM fit: 피처 계산 실패, fallback 전환")
            self._use_fallback = True
            self._fitted = True
            return self

        try:
            from hmmlearn import hmm
            model = hmm.GaussianHMM(
                n_components=self.n_states,
                covariance_type="diag",
                n_iter=self.n_iter,
                random_state=self.random_state,
            )
            model.fit(X)
            self._model = model

            # bull 상태 판별: 평균 log_return이 더 높은 상태 = bull
            means = model.means_[:, 0]  # log_return 컬럼
            self._bull_state = int(np.argmax(means))
            self._fitted = True
            logger.info("HMM fit 완료. bull_state=%d", self._bull_state)
        except Exception as e:
            logger.warning("HMM fit 실패: %s — fallback 전환", e)
            self._use_fallback = True
            self._fitted = True

        return self

    def predict(self, df: pd.DataFrame) -> int:
        """현재 레짐 반환. 0=bear, 1=bull."""
        seq = self.predict_sequence(df)
        if seq is None or len(seq) == 0:
            return BULL  # 불확실 시 중립(bull) 기본값
        return int(seq.iloc[-1])

    def predict_sequence(self, df: pd.DataFrame) -> Optional[pd.Series]:
        """전체 레짐 시퀀스 반환 (pd.Series, index=df.index 일부)."""
        if not self._fitted:
            self.fit(df)

        if self._use_fallback:
            return self._fallback_sequence(df)

        X = self._build_features(df)
        if X is None:
            return self._fallback_sequence(df)

        try:
            hidden = self._model.predict(X)
            # 내부 상태 → bull/bear 매핑
            regime = np.where(hidden == self._bull_state, BULL, BEAR)
            # index 맞추기: dropna 후 인덱스 사용
            close = df["close"]
            log_ret = np.log(close / close.shift(1)).dropna()
            if len(regime) == len(log_ret):
                return pd.Series(regime, index=log_ret.index, dtype=int)
            else:
                return pd.Series(regime, dtype=int)
        except Exception as e:
            logger.warning("HMM predict 실패: %s — fallback", e)
            return self._fallback_sequence(df)

    # ------------------------------------------------------------------
    # Fallback: Bollinger Band width
    # ------------------------------------------------------------------

    def _fallback_sequence(self, df: pd.DataFrame) -> pd.Series:
        """볼린저 밴드 너비 기반 fallback. BB width < 20th percentile = bear."""
        close = df["close"]
        if len(close) < 20:
            # 데이터 부족 — 모두 bull 반환
            return pd.Series([BULL] * len(close), index=df.index, dtype=int)

        rolling_mean = close.rolling(20).mean()
        rolling_std = close.rolling(20).std()
        bb_width = (2 * rolling_std / rolling_mean).fillna(0.0)

        threshold = bb_width.quantile(0.20)
        regime = np.where(bb_width < threshold, BEAR, BULL)
        return pd.Series(regime, index=df.index, dtype=int)
