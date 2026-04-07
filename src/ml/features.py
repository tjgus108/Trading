"""
C1. FeatureBuilder: OHLCV + 기술 지표 → ML 학습 피처.

피처 목록:
  - 수익률: return_1, return_3, return_5, return_10, return_20
  - 모멘텀: rsi14, rsi_zscore
  - 변동성: atr_pct (ATR / close), volatility_20
  - 추세: ema_ratio (ema20/ema50), price_vs_ema20, price_vs_ema50
  - 볼륨: volume_ratio_20 (현재/20일 평균)
  - Donchian: donchian_pct (현재 가격의 채널 내 위치)

타겟 레이블:
  - forward_return_n 캔들 후 수익률 기준
  - BUY(+1): > threshold (기본 +0.3%)
  - SELL(-1): < -threshold
  - HOLD(0): 중립

walk-forward validation: 시계열 순서 반드시 유지.
"""

import numpy as np
import pandas as pd
from typing import Optional


DEFAULT_FORWARD_N = 5       # 5캔들 후 수익률로 레이블 생성
DEFAULT_THRESHOLD = 0.003   # 0.3% 초과 시 BUY/SELL


class FeatureBuilder:
    """
    DataFeed.fetch()의 DataFrame → 학습 피처 + 레이블 생성.
    """

    def __init__(
        self,
        forward_n: int = DEFAULT_FORWARD_N,
        threshold: float = DEFAULT_THRESHOLD,
    ):
        self.forward_n = forward_n
        self.threshold = threshold

    def build(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
        """
        피처 + 레이블 반환.

        Returns:
            X (pd.DataFrame): 피처 행렬 (NaN 행 제거됨)
            y (pd.Series): 레이블 {-1: SELL, 0: HOLD, 1: BUY}
        """
        feat = self._compute_features(df)
        labels = self._compute_labels(df)

        # 공통 인덱스 정렬 + NaN 제거
        combined = feat.join(labels, how="inner").dropna()
        X = combined.drop(columns=["label"])
        y = combined["label"]
        return X, y

    def build_features_only(self, df: pd.DataFrame) -> pd.DataFrame:
        """레이블 없이 피처만 반환 (추론용)."""
        return self._compute_features(df).dropna()

    # ------------------------------------------------------------------
    # Feature computation
    # ------------------------------------------------------------------

    def _compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]
        volume = df["volume"]
        high = df["high"]
        low = df["low"]

        feat = pd.DataFrame(index=df.index)

        # 수익률 (로그 수익률)
        log_ret = np.log(close / close.shift(1))
        feat["return_1"] = log_ret
        feat["return_3"] = np.log(close / close.shift(3))
        feat["return_5"] = np.log(close / close.shift(5))
        feat["return_10"] = np.log(close / close.shift(10))
        feat["return_20"] = np.log(close / close.shift(20))

        # RSI
        if "rsi14" in df.columns:
            feat["rsi14"] = df["rsi14"] / 100.0  # 0~1 정규화
            feat["rsi_zscore"] = (df["rsi14"] - df["rsi14"].rolling(20).mean()) / (
                df["rsi14"].rolling(20).std() + 1e-9
            )
        else:
            feat["rsi14"] = 0.5
            feat["rsi_zscore"] = 0.0

        # ATR 변동성
        if "atr14" in df.columns:
            feat["atr_pct"] = df["atr14"] / close
        else:
            feat["atr_pct"] = (high - low) / close

        feat["volatility_20"] = log_ret.rolling(20).std()

        # EMA 비율
        if "ema20" in df.columns and "ema50" in df.columns:
            feat["ema_ratio"] = df["ema20"] / df["ema50"]
            feat["price_vs_ema20"] = (close - df["ema20"]) / (df["ema20"] + 1e-9)
            feat["price_vs_ema50"] = (close - df["ema50"]) / (df["ema50"] + 1e-9)
        else:
            ema20 = close.ewm(span=20, adjust=False).mean()
            ema50 = close.ewm(span=50, adjust=False).mean()
            feat["ema_ratio"] = ema20 / ema50
            feat["price_vs_ema20"] = (close - ema20) / (ema20 + 1e-9)
            feat["price_vs_ema50"] = (close - ema50) / (ema50 + 1e-9)

        # 볼륨
        vol_ma20 = volume.rolling(20).mean()
        feat["volume_ratio_20"] = volume / (vol_ma20 + 1e-9)

        # Donchian 채널 위치 (0~1)
        if "donchian_high" in df.columns and "donchian_low" in df.columns:
            chan_range = df["donchian_high"] - df["donchian_low"]
            feat["donchian_pct"] = (close - df["donchian_low"]) / (chan_range + 1e-9)
        else:
            high20 = high.rolling(20).max()
            low20 = low.rolling(20).min()
            chan_range = high20 - low20
            feat["donchian_pct"] = (close - low20) / (chan_range + 1e-9)

        # VWAP 관계
        if "vwap" in df.columns:
            feat["price_vs_vwap"] = (close - df["vwap"]) / (df["vwap"] + 1e-9)
        else:
            feat["price_vs_vwap"] = 0.0

        return feat

    def _compute_labels(self, df: pd.DataFrame) -> pd.Series:
        """forward_n 캔들 후 수익률 기반 레이블."""
        close = df["close"]
        fwd_ret = close.shift(-self.forward_n) / close - 1.0
        label = pd.Series(0, index=df.index, name="label", dtype=int)
        label[fwd_ret > self.threshold] = 1
        label[fwd_ret < -self.threshold] = -1
        return label

    @property
    def feature_names(self) -> list[str]:
        return [
            "return_1", "return_3", "return_5", "return_10", "return_20",
            "rsi14", "rsi_zscore",
            "atr_pct", "volatility_20",
            "ema_ratio", "price_vs_ema20", "price_vs_ema50",
            "volume_ratio_20",
            "donchian_pct",
            "price_vs_vwap",
        ]
