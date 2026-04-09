"""
GuppyStrategy (Guppy Multiple Moving Average):
- 단기(6개) + 장기(6개) EMA 그룹으로 추세 판단
- 계산:
  - 단기 EMA: 3, 5, 8, 10, 12, 15기간
  - 장기 EMA: 30, 35, 40, 45, 50, 60기간
  - Short Group Avg = 단기 EMA 6개 평균
  - Long Group Avg = 장기 EMA 6개 평균
- BUY:  Short Avg > Long Avg AND Short Avg 상승 중
- SELL: Short Avg < Long Avg AND Short Avg 하락 중
- confidence: HIGH if (Short Avg - Long Avg) / Long Avg > 0.01, MEDIUM otherwise
- 최소 데이터: 65행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 65
_SHORT_PERIODS = [3, 5, 8, 10, 12, 15]
_LONG_PERIODS = [30, 35, 40, 45, 50, 60]


def _calc_guppy(df: pd.DataFrame):
    """idx = len(df) - 2 기준 short_avg, long_avg (now, prev) 계산."""
    idx = len(df) - 2

    short_emas = [df["close"].ewm(span=p, adjust=False).mean() for p in _SHORT_PERIODS]
    long_emas = [df["close"].ewm(span=p, adjust=False).mean() for p in _LONG_PERIODS]

    short_avg = pd.concat(short_emas, axis=1).mean(axis=1)
    long_avg = pd.concat(long_emas, axis=1).mean(axis=1)

    sa_now = float(short_avg.iloc[idx])
    sa_prev = float(short_avg.iloc[idx - 1])
    la_now = float(long_avg.iloc[idx])

    return sa_now, sa_prev, la_now


class GuppyStrategy(BaseStrategy):
    name = "guppy"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-2]),
                reasoning=f"데이터 부족: {len(df)} < {_MIN_ROWS}",
                invalidation="데이터 충분 시 재평가",
            )

        sa_now, sa_prev, la_now = _calc_guppy(df)
        entry = float(df["close"].iloc[-2])

        sa_rising = sa_now > sa_prev
        sa_falling = sa_now < sa_prev
        short_above_long = sa_now > la_now
        short_below_long = sa_now < la_now

        separation = (sa_now - la_now) / (la_now + 1e-10)

        is_buy = short_above_long and sa_rising
        is_sell = short_below_long and sa_falling

        if is_buy:
            confidence = Confidence.HIGH if separation > 0.01 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Short Avg({sa_now:.4f}) > Long Avg({la_now:.4f}), "
                    f"Short Avg 상승 중 (이전={sa_prev:.4f}), "
                    f"분리도={separation*100:.2f}%"
                ),
                invalidation="Short Avg가 Long Avg 하향 이탈 또는 Short Avg 하락 전환 시",
                bull_case=f"단기 EMA 그룹 완전 정렬 상승, 분리도={separation*100:.2f}%",
                bear_case="단기/장기 EMA 수렴 시 추세 약화 가능",
            )

        if is_sell:
            confidence = Confidence.HIGH if separation < -0.01 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Short Avg({sa_now:.4f}) < Long Avg({la_now:.4f}), "
                    f"Short Avg 하락 중 (이전={sa_prev:.4f}), "
                    f"분리도={separation*100:.2f}%"
                ),
                invalidation="Short Avg가 Long Avg 상향 돌파 또는 Short Avg 상승 전환 시",
                bull_case="단기 EMA 소진 후 반등 가능",
                bear_case=f"단기 EMA 그룹 하락 정렬, 분리도={separation*100:.2f}%",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"Short Avg({sa_now:.4f}), Long Avg({la_now:.4f}) — 조건 미충족 "
                f"(above={short_above_long}, rising={sa_rising})"
            ),
            invalidation="EMA 그룹 정렬 및 방향 일치 시 재평가",
        )
