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

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class VolTargeting:
    """목표 변동성 기반 포지션 사이즈 조정기."""

    # 타임프레임별 하루 캔들 수 (연환산 = 252 * candles_per_day)
    _TF_CANDLES_PER_DAY: dict = {
        "1m": 1440, "5m": 288, "15m": 96,
        "1h": 24, "4h": 6, "1d": 1,
    }

    @classmethod
    def for_timeframe(cls, timeframe: str, **kwargs) -> "VolTargeting":
        """타임프레임에 맞는 annualization 팩터로 VolTargeting 인스턴스 생성.

        기본 annualization=252*24는 1h 전용. 4h 캔들(PASS 전략 평가 기준)에서
        이 메서드 없이 생성하면 실현 변동성이 2배 과장되어 포지션이 50% 축소됨.

        Args:
            timeframe: 타임프레임 문자열 ("1m", "5m", "15m", "1h", "4h", "1d").
            **kwargs: VolTargeting 생성자 추가 파라미터 (target_vol, max_scalar 등).

        Returns:
            올바른 annualization이 적용된 VolTargeting 인스턴스.

        Examples:
            >>> vt = VolTargeting.for_timeframe("4h")
            >>> vt.annualization  # 252 * 6 = 1512
        """
        candles_per_day = cls._TF_CANDLES_PER_DAY.get(timeframe)
        if candles_per_day is None:
            raise ValueError(
                f"Unknown timeframe: {timeframe!r}. "
                f"Supported: {list(cls._TF_CANDLES_PER_DAY)}"
            )
        return cls(annualization=252 * candles_per_day, **kwargs)

    def __init__(
        self,
        target_vol: float = 0.20,       # 연환산 목표 변동성 (20%)
        window: int = 20,               # 실현 변동성 계산 창
        annualization: int = 252 * 24,  # 1h 기준
        max_scalar: float = 2.0,        # 최대 스케일 배수 (레버리지 한계)
        min_scalar: float = 0.1,        # 최소 스케일 배수
        vol_method: str = "simple",     # "simple" 또는 "ewma"
        ewma_span: int = 20,            # EWMA span (vol_method="ewma" 시 사용)
    ) -> None:
        if target_vol <= 0:
            raise ValueError(f"target_vol must be positive, got {target_vol}")
        if vol_method not in ("simple", "ewma"):
            raise ValueError(f"vol_method must be 'simple' or 'ewma', got {vol_method!r}")
        self.target_vol = target_vol
        self.window = window
        self.annualization = annualization
        self.max_scalar = max_scalar
        self.min_scalar = min_scalar
        self.vol_method = vol_method
        self.ewma_span = ewma_span

    def realized_vol(self, df: pd.DataFrame) -> float:
        """최근 window 개 캔들의 연환산 실현 변동성."""
        if len(df) < 2:
            return self.target_vol  # fallback → scalar=1.0

        closes = df["close"].values[-self.window:].astype(float)
        if len(closes) < 2:
            return self.target_vol

        # Bug fix: 비양수 가격이 포함되면 np.log가 -inf/nan을 반환하므로 방어
        if np.any(closes <= 0):
            logger.warning("VolTargeting: non-positive close price detected, using fallback vol")
            return self.target_vol

        log_returns = np.diff(np.log(closes))

        if self.vol_method == "ewma":
            std = float(
                pd.Series(log_returns).ewm(span=self.ewma_span).std().iloc[-1]
            )
        else:
            std = float(np.std(log_returns, ddof=1))

        return std * np.sqrt(self.annualization)

    def scalar(self, df: pd.DataFrame) -> float:
        """vol_scalar = target_vol / realized_vol, [min_scalar, max_scalar] 클리핑."""
        rv = self.realized_vol(df)
        return self._scalar_from_rv(rv)

    def adjust(self, base_size: float, df: pd.DataFrame) -> float:
        """base_size * vol_scalar 반환.

        Raises:
            ValueError: base_size가 0 이하인 경우.
        """
        # Bug fix: base_size <= 0이면 의미 없는 결과이므로 조기 차단
        if base_size <= 0:
            raise ValueError(f"base_size must be positive, got {base_size}")

        # Bug fix: realized_vol()을 한 번만 호출 (기존 코드는 scalar() + debug log에서 2회 호출)
        rv = self.realized_vol(df)
        s = self._scalar_from_rv(rv)
        adjusted = base_size * s
        logger.debug(
            "VolTargeting: rv=%.4f target=%.4f scalar=%.4f base=%.6f → %.6f",
            rv, self.target_vol, s, base_size, adjusted,
        )
        return adjusted

    def _scalar_from_rv(self, rv: float) -> float:
        """rv를 직접 받아 scalar 계산. adjust()의 중복 호출 방지용."""
        if rv <= 0:
            return 1.0
        s = self.target_vol / rv
        return float(np.clip(s, self.min_scalar, self.max_scalar))
