"""
SeasonalCycleStrategy: 가격의 주기적 패턴(선형 회귀 디트렌딩) 기반 사이클 위치 전략.

- 선형 회귀로 추세 제거 후 정규화된 사이클 위치(cycle_pos) 계산
- BUY:  cycle_pos crosses above -1.0 (사이클 저점 탈출)
- SELL: cycle_pos crosses below  1.0 (사이클 고점 이탈)
- HOLD: 그 외
- confidence: HIGH if |cycle_pos| > 1.5 else MEDIUM
- 최소 30행 필요
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_PERIOD = 20
_STD_WINDOW = 20
_BUY_THRESHOLD = -1.0
_SELL_THRESHOLD = 1.0
_HIGH_CONF_ABS = 1.5


class SeasonalCycleStrategy(BaseStrategy):
    """선형 회귀 디트렌딩 + 정규화 사이클 위치 기반 전략."""

    name = "seasonal_cycle"

    def __init__(self, period: int = _PERIOD, std_window: int = _STD_WINDOW):
        self.period = period
        self.std_window = std_window

    def _compute_cycle_pos(self, close: pd.Series) -> pd.Series:
        """선형 추세 제거 후 정규화된 사이클 위치 반환."""
        n = len(close)
        x = np.arange(n)
        coeffs = np.polyfit(x, close.values.astype(float), 1)
        linear_trend = np.polyval(coeffs, x)
        detrended = close - linear_trend
        std = detrended.rolling(self.std_window).std()
        cycle_pos = detrended / std.replace(0, np.nan)
        return cycle_pos

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            n = len(df) if df is not None else 0
            entry = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Insufficient data: {n}행 < {_MIN_ROWS}행 필요",
                invalidation="충분한 데이터 확보 후 재평가",
            )

        idx = len(df) - 2  # 마지막 완성봉 인덱스
        close = df["close"]

        cycle_pos = self._compute_cycle_pos(close)

        curr_cycle_pos = cycle_pos.iloc[idx]
        prev_cycle_pos = cycle_pos.iloc[idx - 1]

        if pd.isna(curr_cycle_pos) or pd.isna(prev_cycle_pos):
            entry = float(close.iloc[idx])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="cycle_pos NaN — 데이터 부족 또는 분산 0",
                invalidation="정상 데이터 확보 후 재평가",
            )

        entry = float(close.iloc[idx])
        abs_pos = abs(curr_cycle_pos)
        confidence = Confidence.HIGH if abs_pos > _HIGH_CONF_ABS else Confidence.MEDIUM

        reasoning_base = (
            f"cycle_pos={curr_cycle_pos:.3f}, prev={prev_cycle_pos:.3f}, "
            f"entry={entry:.4f}"
        )

        # BUY: 이전 < -1.0 AND 현재 >= -1.0 (저점 탈출 크로스오버)
        if prev_cycle_pos < _BUY_THRESHOLD and curr_cycle_pos >= _BUY_THRESHOLD:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"사이클 저점 탈출: cycle_pos -{_BUY_THRESHOLD} 상향 돌파. {reasoning_base}",
                invalidation="cycle_pos가 다시 -1.0 하방 이탈 시 무효",
                bull_case="사이클 저점 반등 — 상승 사이클 진입 기대",
                bear_case="추세 회귀 가능 — 사이클 고점 주의",
            )

        # SELL: 이전 > 1.0 AND 현재 <= 1.0 (고점 이탈 크로스오버)
        if prev_cycle_pos > _SELL_THRESHOLD and curr_cycle_pos <= _SELL_THRESHOLD:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"사이클 고점 이탈: cycle_pos {_SELL_THRESHOLD} 하향 이탈. {reasoning_base}",
                invalidation="cycle_pos가 다시 1.0 상방 돌파 시 무효",
                bull_case="단기 조정 후 반등 가능",
                bear_case="사이클 하락 구간 — 추가 하락 압력 지속",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"사이클 크로스오버 미발생 (HOLD). {reasoning_base}",
            invalidation="cycle_pos 임계값 크로스오버 시 신호 발생",
        )
