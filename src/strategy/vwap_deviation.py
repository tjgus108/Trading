"""
VWAPDeviationStrategy:
- VWAP 대비 가격 편차 기반 평균회귀
- 지표:
  - vwap = (close * volume).rolling(20).sum() / volume.rolling(20).sum()
  - deviation = (close - vwap) / vwap * 100  # % deviation
  - dev_std = deviation.rolling(20).std()
  - dev_zscore = deviation / dev_std
- BUY: dev_zscore < -1.5 AND dev_zscore > dev_zscore.shift(1) (VWAP 아래 + 회복)
- SELL: dev_zscore > 1.5 AND dev_zscore < dev_zscore.shift(1) (VWAP 위 + 하락)
- HOLD: |dev_zscore| <= 1.5
- confidence: HIGH if |dev_zscore| > 2.0 else MEDIUM
- 최소 데이터: 25행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_ZSCORE_THRESHOLD = 1.5
_ZSCORE_HIGH = 2.0


def _calc_zscore(df: pd.DataFrame) -> "tuple[float, float]":
    """idx = len(df) - 2 기준 zscore_now, zscore_prev 반환."""
    idx = len(df) - 2

    vwap = (df["close"] * df["volume"]).rolling(20).sum() / df["volume"].rolling(20).sum()
    deviation = (df["close"] - vwap) / vwap * 100
    dev_std = deviation.rolling(20).std()
    dev_zscore = deviation / dev_std

    zscore_now = float(dev_zscore.iloc[idx])
    zscore_prev = float(dev_zscore.iloc[idx - 1])
    return zscore_now, zscore_prev


class VWAPDeviationStrategy(BaseStrategy):
    name = "vwap_deviation"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            n = 0 if df is None else len(df)
            close = 0.0 if df is None else float(df["close"].iloc[-2])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Insufficient data: {n} < {_MIN_ROWS}",
                invalidation="데이터 충분 시 재평가",
            )

        idx = len(df) - 2
        zscore_now, zscore_prev = _calc_zscore(df)

        if pd.isna(zscore_now) or pd.isna(zscore_prev):
            entry = float(df["close"].iloc[idx])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in zscore — 계산 불가",
                invalidation="데이터 안정화 후 재평가",
            )

        entry = float(df["close"].iloc[idx])
        recovering = zscore_now > zscore_prev
        falling = zscore_now < zscore_prev

        is_buy = zscore_now < -_ZSCORE_THRESHOLD and recovering
        is_sell = zscore_now > _ZSCORE_THRESHOLD and falling

        if is_buy:
            confidence = Confidence.HIGH if abs(zscore_now) > _ZSCORE_HIGH else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"VWAP 하방 편차 회복: dev_zscore={zscore_now:.3f} < -{_ZSCORE_THRESHOLD}, 이전={zscore_prev:.3f}",
                invalidation=f"dev_zscore -{_ZSCORE_THRESHOLD} 이하 지속 또는 추가 하락 시",
                bull_case=f"VWAP 대비 과도한 하락({zscore_now:.2f}σ) 후 회복 신호",
                bear_case="추세적 하락 구간일 경우 평균회귀 실패 가능",
            )

        if is_sell:
            confidence = Confidence.HIGH if abs(zscore_now) > _ZSCORE_HIGH else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"VWAP 상방 편차 하락: dev_zscore={zscore_now:.3f} > {_ZSCORE_THRESHOLD}, 이전={zscore_prev:.3f}",
                invalidation=f"dev_zscore {_ZSCORE_THRESHOLD} 이상 지속 또는 추가 상승 시",
                bull_case="추세적 상승 구간일 경우 과매수 지속 가능",
                bear_case=f"VWAP 대비 과도한 상승({zscore_now:.2f}σ) 후 하락 신호",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"편차 중립: dev_zscore={zscore_now:.3f} (|z| <= {_ZSCORE_THRESHOLD})",
            invalidation=f"|dev_zscore| > {_ZSCORE_THRESHOLD} 돌파 시 재평가",
        )
