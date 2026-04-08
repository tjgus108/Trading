"""
I3. Volatility-Targeted Position Sizing.

목표 변동성(target_vol) 대비 현재 실현 변동성 비율로
position_size를 자동 조절한다.

공식:
  vol_scalar = target_vol / realized_vol
  adjusted_size = base_size * min(vol_scalar, max_scalar)

realized_vol: 최근 window 개 캔들의 수익률 표준편차 * sqrt(annualization)
target_vol: 연환산 목표 변동성 (e.g. 0.20 = 20% p.a.)

사용:
    vt = VolTargeting(target_vol=0.20)
    size = vt.adjust(base_size=0.01, df=candle_df)
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class VolTargeting:
    """목표 변동성 기반 포지션 사이즈 조정기."""

    def __init__(
        self,
        target_vol: float = 0.20,       # 연환산 목표 변동성 (20%)
        window: int = 20,               # 실현 변동성 계산 창
        annualization: int = 252 * 24,  # 1h 기준
        max_scalar: float = 2.0,        # 최대 스케일 배수 (레버리지 한계)
        min_scalar: float = 0.1,        # 최소 스케일 배수
    ) -> None:
        self.target_vol = target_vol
        self.window = window
        self.annualization = annualization
        self.max_scalar = max_scalar
        self.min_scalar = min_scalar

    def realized_vol(self, df: pd.DataFrame) -> float:
        """최근 window 개 캔들의 연환산 실현 변동성."""
        if len(df) < 2:
            return self.target_vol  # fallback → scalar=1.0

        closes = df["close"].values[-self.window:]
        if len(closes) < 2:
            return self.target_vol

        log_returns = np.diff(np.log(closes.astype(float)))
        std = float(np.std(log_returns, ddof=1))
        return std * np.sqrt(self.annualization)

    def scalar(self, df: pd.DataFrame) -> float:
        """vol_scalar = target_vol / realized_vol, [min_scalar, max_scalar] 클리핑."""
        rv = self.realized_vol(df)
        if rv <= 0:
            return 1.0
        s = self.target_vol / rv
        return float(np.clip(s, self.min_scalar, self.max_scalar))

    def adjust(self, base_size: float, df: pd.DataFrame) -> float:
        """base_size * vol_scalar 반환."""
        s = self.scalar(df)
        adjusted = base_size * s
        logger.debug(
            "VolTargeting: rv=%.4f target=%.4f scalar=%.4f base=%.6f → %.6f",
            self.realized_vol(df), self.target_vol, s, base_size, adjusted,
        )
        return adjusted
