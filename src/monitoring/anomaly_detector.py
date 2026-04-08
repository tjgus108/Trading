"""
K1. Anomaly Detector — 가격/거래량 이상치 실시간 감지.

방법:
  1. Z-score: |z| > threshold → 이상치
  2. IQR: value < Q1 - k*IQR 또는 > Q3 + k*IQR → 이상치
  3. Return spike: |single candle return| > spike_threshold → 이상치

이상치 발생 시 AnomalyEvent 반환.

사용:
  detector = AnomalyDetector(z_threshold=3.0, iqr_k=3.0)
  events = detector.detect(df)
  for e in events:
      print(e.summary())
"""

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class AnomalyEvent:
    column: str
    method: str        # "zscore" | "iqr" | "return_spike"
    value: float       # 이상치 값
    score: float       # z-score 또는 IQR 배수
    index: int         # DataFrame 행 인덱스
    severity: str      # "LOW" | "MEDIUM" | "HIGH"

    def summary(self) -> str:
        return (
            f"[{self.severity}] Anomaly({self.method}) "
            f"col={self.column} val={self.value:.4f} "
            f"score={self.score:.2f} idx={self.index}"
        )


class AnomalyDetector:
    """가격/거래량 이상치 감지기."""

    def __init__(
        self,
        z_threshold: float = 3.0,       # Z-score 이상치 임계값
        iqr_k: float = 3.0,             # IQR 이상치 배수
        return_spike_threshold: float = 0.05,  # 단일 캔들 수익률 5% 초과
        columns: Optional[list[str]] = None,   # 감지할 컬럼 (None=자동)
        window: int = 50,               # rolling 통계 창
    ) -> None:
        self.z_threshold = z_threshold
        self.iqr_k = iqr_k
        self.return_spike_threshold = return_spike_threshold
        self.columns = columns
        self.window = window

    def detect(self, df: pd.DataFrame) -> list[AnomalyEvent]:
        """DataFrame에서 이상치 감지. 이상치 이벤트 리스트 반환."""
        events: list[AnomalyEvent] = []

        # 감지 대상 컬럼 결정
        cols = self.columns or [c for c in ["close", "volume"] if c in df.columns]

        for col in cols:
            if col not in df.columns:
                continue
            series = df[col].dropna()
            if len(series) < max(10, self.window // 2):
                continue

            events.extend(self._detect_zscore(series, col, df))
            events.extend(self._detect_iqr(series, col, df))

        # 수익률 스파이크
        if "close" in df.columns:
            events.extend(self._detect_return_spike(df))

        return events

    def detect_latest(self, df: pd.DataFrame) -> list[AnomalyEvent]:
        """최신 캔들만 감지 (실시간 스캔용)."""
        all_events = self.detect(df)
        last_idx = len(df) - 2  # _last 패턴과 동일
        return [e for e in all_events if e.index >= last_idx]

    def _detect_zscore(
        self, series: pd.Series, col: str, df: pd.DataFrame
    ) -> list[AnomalyEvent]:
        events = []
        # rolling mean/std
        rolling_mean = series.rolling(self.window, min_periods=5).mean()
        rolling_std = series.rolling(self.window, min_periods=5).std()

        for i in range(len(series)):
            mu = rolling_mean.iloc[i]
            sigma = rolling_std.iloc[i]
            if pd.isna(mu) or pd.isna(sigma) or sigma <= 0:
                continue
            val = series.iloc[i]
            z = abs(val - mu) / sigma
            if z > self.z_threshold:
                severity = "HIGH" if z > self.z_threshold * 1.5 else "MEDIUM"
                events.append(AnomalyEvent(
                    column=col, method="zscore",
                    value=float(val), score=float(z),
                    index=i, severity=severity,
                ))
        return events

    def _detect_iqr(
        self, series: pd.Series, col: str, df: pd.DataFrame
    ) -> list[AnomalyEvent]:
        events = []
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr <= 0:
            return events

        lower = q1 - self.iqr_k * iqr
        upper = q3 + self.iqr_k * iqr

        for i, val in enumerate(series):
            if val < lower or val > upper:
                distance = max(abs(val - lower), abs(val - upper)) / iqr
                severity = "HIGH" if distance > self.iqr_k * 2 else "MEDIUM"
                events.append(AnomalyEvent(
                    column=col, method="iqr",
                    value=float(val), score=float(distance),
                    index=i, severity=severity,
                ))
        return events

    def _detect_return_spike(self, df: pd.DataFrame) -> list[AnomalyEvent]:
        events = []
        closes = df["close"].values
        for i in range(1, len(closes)):
            if closes[i - 1] <= 0:
                continue
            ret = abs((closes[i] - closes[i - 1]) / closes[i - 1])
            if ret >= self.return_spike_threshold:
                severity = "HIGH" if ret >= self.return_spike_threshold * 2 else "LOW"
                events.append(AnomalyEvent(
                    column="close_return", method="return_spike",
                    value=float(closes[i]),
                    score=float(ret),
                    index=i, severity=severity,
                ))
        return events
