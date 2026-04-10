"""
DeMarker 전략:
- DeMarker = DeMax_sum / (DeMax_sum + DeMin_sum)
  DeMax = max(high - prev_high, 0)
  DeMin = max(prev_low - low, 0)
  period = 14

- BUY:  dem crosses above 0.3 (이전 < 0.3, 현재 >= 0.3) — 과매도 탈출
- SELL: dem crosses below 0.7 (이전 > 0.7, 현재 <= 0.7) — 과매수 이탈
- confidence: HIGH if dem < 0.2 (BUY) or dem > 0.8 (SELL) else MEDIUM
- 최소 데이터: 20행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_PERIOD = 14
_BUY_CROSS = 0.3
_SELL_CROSS = 0.7
_HIGH_CONF_LOW = 0.2
_HIGH_CONF_HIGH = 0.8


def _compute_demarker(df: pd.DataFrame, period: int = _PERIOD) -> pd.Series:
    demax = (df["high"] - df["high"].shift(1)).clip(lower=0)
    demin = (df["low"].shift(1) - df["low"]).clip(lower=0)
    demax_sum = demax.rolling(period).mean()
    demin_sum = demin.rolling(period).mean()
    dem = demax_sum / (demax_sum + demin_sum + 1e-10)
    return dem


class DeMarkerStrategy(BaseStrategy):
    """DeMarker 과매수/과매도 크로스오버 전략."""

    name = "demarker"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            rows = len(df) if df is not None else 0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=f"Insufficient data: {rows} rows < {_MIN_ROWS} required",
                invalidation="충분한 히스토리 데이터 확보 후 재시도",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2
        dem = _compute_demarker(df)

        current = float(dem.iloc[idx])
        prev = float(dem.iloc[idx - 1])
        close = float(df["close"].iloc[idx])

        if pd.isna(current) or pd.isna(prev):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning="DeMarker 계산 불가 (NaN)",
                invalidation="지표 계산 가능 시점까지 대기",
                bull_case="",
                bear_case="",
            )

        # BUY: crosses above 0.3
        if prev < _BUY_CROSS and current >= _BUY_CROSS:
            conf = Confidence.HIGH if current < _HIGH_CONF_LOW else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"DeMarker 과매도 탈출: dem={current:.3f} crosses above {_BUY_CROSS} "
                    f"(prev={prev:.3f})"
                ),
                invalidation=f"dem이 다시 {_BUY_CROSS} 아래로 하락 시 무효",
                bull_case=f"DeMarker {current:.3f} 과매도 영역 탈출 — 반등 기대",
                bear_case="크로스가 노이즈일 가능성",
            )

        # SELL: crosses below 0.7
        if prev > _SELL_CROSS and current <= _SELL_CROSS:
            conf = Confidence.HIGH if current > _HIGH_CONF_HIGH else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"DeMarker 과매수 이탈: dem={current:.3f} crosses below {_SELL_CROSS} "
                    f"(prev={prev:.3f})"
                ),
                invalidation=f"dem이 다시 {_SELL_CROSS} 위로 상승 시 무효",
                bull_case="단기 눌림 후 재상승 가능성",
                bear_case=f"DeMarker {current:.3f} 과매수 이탈 — 하락 기대",
            )

        # HOLD
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"DeMarker={current:.3f}: 크로스 조건 미충족 (prev={prev:.3f})"
            ),
            invalidation="dem < 0.3 탈출 또는 dem > 0.7 이탈 시 재평가",
            bull_case="",
            bear_case="",
        )
