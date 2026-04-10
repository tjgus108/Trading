"""
SimplifiedGartleyStrategy:
- 최근 30봉의 swing high/low로 XABCD Gartley 패턴 근사
- Bullish: 최근 swing low가 (swing_high - swing_low) 범위의 78.6% retracement 근방 → BUY
- Bearish: 최근 swing high가 78.6% retracement 근방 → SELL
- confidence: fibonacci ratio 오차 < 1% → HIGH, 그 외 MEDIUM
- 최소 데이터: 35행
"""

from typing import Optional, Tuple

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35
_WINDOW = 30
_FIB_786 = 0.786
_HIGH_CONF_TOLERANCE = 0.01   # < 1% → HIGH
_MED_CONF_TOLERANCE = 0.02    # < 2% → 신호 유효


def _find_swing_points(
    series: pd.Series,
) -> Tuple[float, float, float, float]:
    """
    주어진 시리즈에서 전체 최고/최저, 그리고 최고점 이후 최저(swing_low)와
    최저점 이후 최고(swing_high)를 반환.
    Returns: (global_low, global_high, recent_low_after_high, recent_high_after_low)
    """
    global_high_idx = int(series.idxmax()) if hasattr(series, 'idxmax') else series.values.argmax()
    global_low_idx = int(series.idxmin()) if hasattr(series, 'idxmin') else series.values.argmin()

    # iloc 기반으로 인덱스 위치 변환
    positions = list(series.index)
    gh_pos = positions.index(global_high_idx) if global_high_idx in positions else series.values.argmax()
    gl_pos = positions.index(global_low_idx) if global_low_idx in positions else series.values.argmin()

    global_high = float(series.iloc[gh_pos])
    global_low = float(series.iloc[gl_pos])

    # 최고점 이후 구간의 최저점
    if gh_pos < len(series) - 1:
        after_high = series.iloc[gh_pos:]
        recent_low_after_high = float(after_high.min())
    else:
        recent_low_after_high = global_low

    # 최저점 이후 구간의 최고점
    if gl_pos < len(series) - 1:
        after_low = series.iloc[gl_pos:]
        recent_high_after_low = float(after_low.max())
    else:
        recent_high_after_low = global_high

    return global_low, global_high, recent_low_after_high, recent_high_after_low


class SimplifiedGartleyStrategy(BaseStrategy):
    name = "gartley_pattern"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        close = float(last["close"])

        completed = df.iloc[:-1]
        window = completed.iloc[-_WINDOW:]

        close_series = window["close"].reset_index(drop=True)

        swing_high = float(close_series.max())
        swing_low = float(close_series.min())
        rng = swing_high - swing_low

        if rng == 0:
            return self._hold(df, "No price range in window")

        # Bullish Gartley D 포인트: X에서 A까지 상승 후 78.6% 되돌림
        # D = swing_low + (swing_high - swing_low) * (1 - 0.786) = swing_high - rng * 0.786
        # 즉 D ≈ swing_low + rng * 0.214 (X에서 78.6% 되돌림)
        # 단순화: D point = swing_low + rng * (1 - _FIB_786)
        bull_d = swing_low + rng * (1.0 - _FIB_786)
        bear_d = swing_high - rng * (1.0 - _FIB_786)

        bull_ratio_err = abs(close - bull_d) / rng if rng > 0 else 1.0
        bear_ratio_err = abs(close - bear_d) / rng if rng > 0 else 1.0

        context = (
            f"close={close:.4f} swing_low={swing_low:.4f} swing_high={swing_high:.4f} "
            f"bull_D={bull_d:.4f} bear_D={bear_d:.4f}"
        )

        # Bullish: close가 bull_d 근방 (±2%)
        if bull_ratio_err <= _MED_CONF_TOLERANCE:
            confidence = Confidence.HIGH if bull_ratio_err < _HIGH_CONF_TOLERANCE else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Bullish Gartley D-point 근방 (오차={bull_ratio_err:.4f}): {context}",
                invalidation=f"close < swing_low={swing_low:.4f}",
                bull_case=f"Gartley D-point 반등, {context}",
                bear_case=f"D-point 하향 이탈 시 패턴 무효",
            )

        # Bearish: close가 bear_d 근방 (±2%)
        if bear_ratio_err <= _MED_CONF_TOLERANCE:
            confidence = Confidence.HIGH if bear_ratio_err < _HIGH_CONF_TOLERANCE else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Bearish Gartley D-point 근방 (오차={bear_ratio_err:.4f}): {context}",
                invalidation=f"close > swing_high={swing_high:.4f}",
                bull_case=f"D-point 상향 돌파 시 패턴 무효",
                bear_case=f"Gartley D-point 저항, {context}",
            )

        return self._hold(df, f"No Gartley signal: {context}")

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        if len(df) < 2:
            entry = 0.0
        else:
            last = self._last(df) if len(df) >= 2 else df.iloc[-1]
            entry = float(last["close"])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
