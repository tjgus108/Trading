"""
PriceCycleDetector 전략:
- 가격의 자기상관(autocorrelation)으로 주기 감지 후 사이클 위치 판단.
- BUY: best_corr > 0.5 AND cycle_momentum > 0.01
- SELL: best_corr > 0.5 AND cycle_momentum < -0.01
- HOLD: |best_corr| < 0.5 또는 |cycle_momentum| <= 0.01
- confidence: HIGH if best_corr > 0.7 else MEDIUM
- 최소 행: 35
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35


class PriceCycleDetectorStrategy(BaseStrategy):
    name = "price_cycle_detector"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, f"Insufficient data: {len(df)} < {_MIN_ROWS}")

        idx = len(df) - 2  # _last index

        n = 30
        close_vals = df["close"].iloc[idx - n + 1 : idx + 1].values.astype(float)

        # NaN 체크
        if np.any(np.isnan(close_vals)):
            return self._hold(df, "Insufficient data: NaN in close values")

        # 자기상관 (lag 1~10에서 최대 상관 찾기)
        if close_vals.std() > 0:
            normalized = (close_vals - close_vals.mean()) / close_vals.std()
            best_lag = 1
            best_corr = 0.0
            for lag in range(2, 11):
                if lag < len(normalized):
                    corr = float(np.corrcoef(normalized[:-lag], normalized[lag:])[0, 1])
                    if abs(corr) > abs(best_corr):
                        best_corr = corr
                        best_lag = lag
        else:
            best_lag = 5
            best_corr = 0.0

        # 현재 사이클 위치
        curr_close = float(df["close"].iloc[idx])
        lag_close = float(df["close"].iloc[idx - best_lag]) if idx >= best_lag else curr_close
        cycle_momentum = (curr_close - lag_close) / lag_close if lag_close != 0 else 0.0

        context = (
            f"best_corr={best_corr:.3f} best_lag={best_lag} "
            f"cycle_momentum={cycle_momentum:.4f} curr_close={curr_close:.4f}"
        )

        if best_corr > 0.5 and cycle_momentum > 0.01:
            conf = Confidence.HIGH if best_corr > 0.7 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"강한 양의 자기상관 + 상승 위상: {context}",
                invalidation="best_corr < 0.5 또는 cycle_momentum <= 0.01",
                bull_case=f"주기 상승 위상 (corr={best_corr:.3f}, lag={best_lag})",
                bear_case="사이클 반전 시 빠른 청산",
            )

        if best_corr > 0.5 and cycle_momentum < -0.01:
            conf = Confidence.HIGH if best_corr > 0.7 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"강한 양의 자기상관 + 하락 위상: {context}",
                invalidation="best_corr < 0.5 또는 cycle_momentum >= -0.01",
                bull_case="사이클 반전 시 숏 포지션 청산",
                bear_case=f"주기 하락 위상 (corr={best_corr:.3f}, lag={best_lag})",
            )

        return self._hold(df, f"사이클 신호 없음: {context}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        try:
            price = float(self._last(df)["close"])
        except Exception:
            price = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
        )
