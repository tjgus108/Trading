"""
Consecutive Candles Trend 전략:
- 최근 N봉의 연속 방향성 카운팅
- BUY:  bull_count >= 4 (4봉 연속 양봉) AND volume 증가
- SELL: bear_count >= 4 AND volume 증가
- confidence: HIGH if 연속 봉 수 >= 6, MEDIUM if >= 4
- 최소 데이터: 15행
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 15
_MIN_COUNT = 4
_HIGH_CONF_COUNT = 6


def _count_consecutive_bull(df: pd.DataFrame, idx: int) -> int:
    """idx 위치 기준으로 연속 양봉 수 카운팅 (idx 포함, 뒤로 거슬러 올라감)."""
    count = 0
    i = idx
    while i >= 1:
        if float(df["close"].iloc[i]) > float(df["open"].iloc[i]):
            count += 1
            i -= 1
        else:
            break
    return count


def _count_consecutive_bear(df: pd.DataFrame, idx: int) -> int:
    """idx 위치 기준으로 연속 음봉 수 카운팅."""
    count = 0
    i = idx
    while i >= 1:
        if float(df["close"].iloc[i]) < float(df["open"].iloc[i]):
            count += 1
            i -= 1
        else:
            break
    return count


def _volume_increasing(df: pd.DataFrame, idx: int, count: int) -> bool:
    """idx 위치부터 count봉이 각 봉의 volume > 이전봉 인지 확인."""
    if count < 2:
        return False
    start = idx - count + 1
    if start < 1:
        return False
    for i in range(start + 1, idx + 1):
        if float(df["volume"].iloc[i]) <= float(df["volume"].iloc[i - 1]):
            return False
    return True


class ConsecutiveCandlesStrategy(BaseStrategy):
    name = "consecutive_candles"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2  # _last() 기준 마지막 완성 캔들
        close = float(df["close"].iloc[idx])

        bull_count = _count_consecutive_bull(df, idx)
        bear_count = _count_consecutive_bear(df, idx)

        context = (
            f"close={close:.2f} bull_count={bull_count} bear_count={bear_count}"
        )

        # BUY: 4봉 이상 연속 양봉 AND volume 증가
        if bull_count >= _MIN_COUNT and _volume_increasing(df, idx, bull_count):
            confidence = Confidence.HIGH if bull_count >= _HIGH_CONF_COUNT else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Consecutive Candles BUY: {bull_count}봉 연속 양봉 + volume 증가"
                ),
                invalidation="음봉 발생 또는 volume 감소",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 4봉 이상 연속 음봉 AND volume 증가
        if bear_count >= _MIN_COUNT and _volume_increasing(df, idx, bear_count):
            confidence = Confidence.HIGH if bear_count >= _HIGH_CONF_COUNT else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Consecutive Candles SELL: {bear_count}봉 연속 음봉 + volume 증가"
                ),
                invalidation="양봉 발생 또는 volume 감소",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
