"""
SRBounceStrategy: 동적 지지/저항 레벨에서의 반등/저항 감지.

- Pivot 계산: 최근 50봉 내 고점/저점 (좌우 5봉 기준)
- Support = 가장 가까운 하방 pivot low
- Resistance = 가장 가까운 상방 pivot high
- BUY: close가 support ±1% 내 터치 AND volume > avg_vol * 1.1
- SELL: close가 resistance ±1% 내 터치 AND volume > avg_vol * 1.1
- confidence: 터치 횟수 >= 3 → HIGH
- 최소 행: 60
"""

from typing import List, Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class SRBounceStrategy(BaseStrategy):
    name = "sr_bounce"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 60:
            return self._hold(df, "데이터 부족")

        idx = len(df) - 2
        window = df.iloc[max(0, idx - 50): idx]

        high = window["high"].values
        low = window["low"].values
        n = len(high)

        pivot_high_indices = self._find_pivot_highs(high, n)
        pivot_low_indices = self._find_pivot_lows(low, n)

        if not pivot_high_indices and not pivot_low_indices:
            return self._hold(df, "Pivot 없음")

        pivot_highs = [float(high[i]) for i in pivot_high_indices]
        pivot_lows = [float(low[i]) for i in pivot_low_indices]

        close = float(df["close"].iloc[idx])

        # 가장 가까운 하방 support, 상방 resistance
        support = self._nearest_below(pivot_lows, close)
        resistance = self._nearest_above(pivot_highs, close)

        # 볼륨 필터
        vol_window = df["volume"].iloc[max(0, idx - 20): idx]
        avg_vol = float(vol_window.mean()) if len(vol_window) > 0 else 0.0
        vol_confirm = avg_vol > 0 and float(df["volume"].iloc[idx]) > avg_vol * 1.1

        entry = close

        # BUY: support 레벨 터치
        if support is not None:
            near_support = close > support * 0.99 and close < support * 1.01
            if near_support and vol_confirm:
                touch_count = self._count_touches(df, support, idx)
                conf = Confidence.HIGH if touch_count >= 3 else Confidence.MEDIUM
                return Signal(
                    action=Action.BUY,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"Support 레벨 터치: close={close:.2f}, support={support:.2f}, "
                        f"touches={touch_count}, vol_confirm={vol_confirm}"
                    ),
                    invalidation=f"Close below support ({support:.2f} * 0.99)",
                    bull_case=f"Support {support:.2f} 반등 기대, 터치 횟수={touch_count}",
                    bear_case=f"Support 이탈 시 추가 하락 가능",
                )

        # SELL: resistance 레벨 터치
        if resistance is not None:
            near_resistance = close > resistance * 0.99 and close < resistance * 1.01
            if near_resistance and vol_confirm:
                touch_count = self._count_touches(df, resistance, idx)
                conf = Confidence.HIGH if touch_count >= 3 else Confidence.MEDIUM
                return Signal(
                    action=Action.SELL,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"Resistance 레벨 터치: close={close:.2f}, resistance={resistance:.2f}, "
                        f"touches={touch_count}, vol_confirm={vol_confirm}"
                    ),
                    invalidation=f"Close above resistance ({resistance:.2f} * 1.01)",
                    bull_case=f"Resistance 돌파 시 추가 상승 가능",
                    bear_case=f"Resistance {resistance:.2f} 저항 기대, 터치 횟수={touch_count}",
                )

        sr_info = ""
        if support is not None:
            sr_info += f"Support={support:.2f} "
        if resistance is not None:
            sr_info += f"Resistance={resistance:.2f}"
        return self._hold(df, f"SR 레벨 미접근 또는 볼륨 미확인. {sr_info.strip()}")

    def _find_pivot_highs(self, high: "np.ndarray", n: int) -> List[int]:
        return [
            i for i in range(5, n - 5)
            if high[i] == high[i - 5: i + 6].max()
        ]

    def _find_pivot_lows(self, low: "np.ndarray", n: int) -> List[int]:
        return [
            i for i in range(5, n - 5)
            if low[i] == low[i - 5: i + 6].min()
        ]

    def _nearest_below(self, levels: List[float], price: float) -> Optional[float]:
        candidates = [lv for lv in levels if lv <= price]
        return max(candidates) if candidates else None

    def _nearest_above(self, levels: List[float], price: float) -> Optional[float]:
        candidates = [lv for lv in levels if lv >= price]
        return min(candidates) if candidates else None

    def _count_touches(self, df: pd.DataFrame, level: float, idx: int) -> int:
        window = df["close"].iloc[max(0, idx - 50): idx]
        return int(((window > level * 0.99) & (window < level * 1.01)).sum())

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        entry = float(df["close"].iloc[-2]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
