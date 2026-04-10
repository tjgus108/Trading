"""
DualThrustStrategy: 최근 N봉 고가/저가 범위 기반 돌파 전략.

계산 (N=4, k=0.5):
  hh = rolling(N) 최고 고가
  hc = rolling(N) 최고 종가
  lc = rolling(N) 최저 종가
  ll = rolling(N) 최저 저가
  range_val = max(hh - lc, hc - ll)
  upper_level = open + k * range_val
  lower_level = open - k * range_val

BUY:  curr_close > upper_level (상단 돌파)
SELL: curr_close < lower_level (하단 붕괴)
HOLD: 그 외

confidence: HIGH if (curr_close - upper_level) / range_val > 0.02 else MEDIUM
최소 10행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 10
_N = 4
_K = 0.5
_HIGH_CONF_THRESHOLD = 0.02


class DualThrustStrategy(BaseStrategy):
    name = "dual_thrust"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for DualThrust",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        hh = df["high"].rolling(_N).max()
        hc = df["close"].rolling(_N).max()
        lc = df["close"].rolling(_N).min()
        ll = df["low"].rolling(_N).min()

        range_val = pd.concat([hh - lc, hc - ll], axis=1).max(axis=1)

        upper_level = df["open"] + _K * range_val
        lower_level = df["open"] - _K * range_val

        curr_close = float(df["close"].iloc[idx])
        rv = float(range_val.iloc[idx])
        ul = float(upper_level.iloc[idx])
        ll_val = float(lower_level.iloc[idx])

        if pd.isna(rv) or rv <= 0:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=curr_close,
                reasoning="range_val NaN or <= 0, no signal",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        if curr_close > ul:
            ratio = (curr_close - ul) / rv
            conf = Confidence.HIGH if ratio > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"상단 돌파: close {curr_close:.2f} > upper_level {ul:.2f}, "
                    f"range {rv:.2f}, ratio {ratio:.3f}"
                ),
                invalidation=f"close falls below upper_level {ul:.2f}",
                bull_case=f"range 대비 {ratio:.1%} 돌파",
                bear_case="False breakout 가능",
            )

        if curr_close < ll_val:
            ratio = (ll_val - curr_close) / rv
            conf = Confidence.HIGH if ratio > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"하단 붕괴: close {curr_close:.2f} < lower_level {ll_val:.2f}, "
                    f"range {rv:.2f}, ratio {ratio:.3f}"
                ),
                invalidation=f"close rises above lower_level {ll_val:.2f}",
                bull_case="단순 조정일 수 있음",
                bear_case=f"range 대비 {ratio:.1%} 하단 돌파",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=curr_close,
            reasoning=(
                f"돌파 없음: close {curr_close:.2f}, "
                f"upper {ul:.2f}, lower {ll_val:.2f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
