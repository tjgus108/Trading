"""
MeanReversionScoreStrategy: 다중 지표 합산 평균 회귀 점수 전략.

로직:
- z_price: 가격의 20봉 z-score
- z_rsi: RSI(14) 기반 z-score (중심=50, 스케일=20)
- rev_score = -z_price - z_rsi  (음수 z = 과매도 = 높은 회귀 점수)
- vol_z: 거래량 z-score
- BUY: rev_score > 1.5 AND vol_z > 0
- SELL: rev_score < -1.5 AND vol_z > 0
- confidence: HIGH if abs(rev_score) > 2.0 else MEDIUM
"""

import math
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class MeanReversionScoreStrategy(BaseStrategy):
    name = "mean_reversion_score"

    _MIN_ROWS = 25

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self._MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="데이터 부족: 최소 25행 필요",
                invalidation="",
            )

        idx = len(df) - 2
        close = df["close"]
        volume = df["volume"]

        # z_price
        roll_mean = close.rolling(20, min_periods=1).mean()
        roll_std = close.rolling(20, min_periods=1).std()
        z_price_series = (close - roll_mean) / (roll_std + 1e-10)

        # RSI(14)
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14, min_periods=1).mean()
        loss = (-delta.clip(upper=0)).rolling(14, min_periods=1).mean()
        rsi = 100 - 100 / (1 + gain / (loss + 1e-10))
        z_rsi_series = (rsi - 50) / 20

        # vol_z
        vol_mean = volume.rolling(20, min_periods=1).mean()
        vol_std = volume.rolling(20, min_periods=1).std()
        vol_z_series = (volume - vol_mean) / (vol_std + 1e-10)

        # rev_score
        rev_score_series = -z_price_series - z_rsi_series

        z_price_val = float(z_price_series.iloc[idx])
        z_rsi_val = float(z_rsi_series.iloc[idx])
        vol_z_val = float(vol_z_series.iloc[idx])
        rev_score_val = float(rev_score_series.iloc[idx])
        rsi_val = float(rsi.iloc[idx])
        c = float(close.iloc[idx])

        # NaN 체크
        if any(math.isnan(v) for v in [z_price_val, z_rsi_val, vol_z_val, rev_score_val, c]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=c if not math.isnan(c) else 0.0,
                reasoning="NaN 값 감지: HOLD",
                invalidation="",
            )

        conf = Confidence.HIGH if abs(rev_score_val) > 2.0 else Confidence.MEDIUM

        bull_case = (
            f"rev_score={rev_score_val:.3f} (과매도), z_price={z_price_val:.3f}, "
            f"z_rsi={z_rsi_val:.3f}, RSI={rsi_val:.1f}, vol_z={vol_z_val:.3f}"
        )
        bear_case = (
            f"rev_score={rev_score_val:.3f} (과매수), z_price={z_price_val:.3f}, "
            f"z_rsi={z_rsi_val:.3f}, RSI={rsi_val:.1f}, vol_z={vol_z_val:.3f}"
        )

        # BUY: 강한 과매도 + 거래량 확인
        if rev_score_val > 1.5 and vol_z_val > 0:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"강한 과매도: rev_score={rev_score_val:.3f} > 1.5, "
                    f"vol_z={vol_z_val:.3f} > 0. "
                    f"z_price={z_price_val:.3f}, z_rsi={z_rsi_val:.3f}, RSI={rsi_val:.1f}"
                ),
                invalidation=f"rev_score drops below 0",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: 강한 과매수 + 거래량 확인
        if rev_score_val < -1.5 and vol_z_val > 0:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"강한 과매수: rev_score={rev_score_val:.3f} < -1.5, "
                    f"vol_z={vol_z_val:.3f} > 0. "
                    f"z_price={z_price_val:.3f}, z_rsi={z_rsi_val:.3f}, RSI={rsi_val:.1f}"
                ),
                invalidation=f"rev_score rises above 0",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=c,
            reasoning=(
                f"조건 미충족: rev_score={rev_score_val:.3f}, vol_z={vol_z_val:.3f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
