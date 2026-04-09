"""
FlagPennantStrategy:
  Flag & Pennant 패턴 탐지.

  Pole: 10봉 내 5% 이상 급등(BUY pole) 또는 5% 이상 급락(SELL pole)
  Consolidation: pole 이후 5~15봉 동안 변동폭 감소
  BUY: Bullish pole + consolidation 후 돌파
  SELL: Bearish pole + consolidation 후 하향 돌파
  confidence: pole 크기 > 8% → HIGH, 그 외 MEDIUM
  최소 행: 30
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 30
POLE_BARS = 10
POLE_THRESHOLD = 0.05   # 5%
HIGH_CONF_THRESHOLD = 0.08  # 8%
CONSOL_MIN = 5
CONSOL_MAX = 15


class FlagPennantStrategy(BaseStrategy):
    name = "flag_pennant"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: Flag/Pennant 계산에 최소 30행 필요",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        last = self._last(df)  # df.iloc[-2]
        close = float(last["close"])
        last_idx = len(df) - 2  # _last 기준 인덱스

        result = self._find_flag_pennant(df, last_idx)

        if result is None:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning="Flag/Pennant 패턴 미감지",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        direction, pole_pct, pole_end_idx, consol_high, consol_low = result
        high_conf = abs(pole_pct) > HIGH_CONF_THRESHOLD

        if direction == "bull" and close > consol_high:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if high_conf else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Flag/Pennant BUY: Bullish pole={pole_pct:.1%}, "
                    f"consolidation 상단({consol_high:.4f}) 돌파, close={close:.4f}"
                ),
                invalidation=f"Close below consolidation low {consol_low:.4f}",
                bull_case=(
                    f"Pole 크기={pole_pct:.1%}, 상단={consol_high:.4f} 돌파"
                ),
                bear_case=f"Consolidation low {consol_low:.4f} 이탈 시 패턴 무효화",
            )

        if direction == "bear" and close < consol_low:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH if high_conf else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Flag/Pennant SELL: Bearish pole={pole_pct:.1%}, "
                    f"consolidation 하단({consol_low:.4f}) 이탈, close={close:.4f}"
                ),
                invalidation=f"Close above consolidation high {consol_high:.4f}",
                bull_case=f"Consolidation high {consol_high:.4f} 회복 시 패턴 무효화",
                bear_case=(
                    f"Pole 크기={pole_pct:.1%}, 하단={consol_low:.4f} 이탈"
                ),
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"Flag/Pennant 감지됐으나 돌파 미완 (direction={direction}): "
                f"close={close:.4f}, 상단={consol_high:.4f}, 하단={consol_low:.4f}"
            ),
            invalidation="",
            bull_case=f"상단 {consol_high:.4f} 돌파 시 BUY" if direction == "bull" else "",
            bear_case=f"하단 {consol_low:.4f} 이탈 시 SELL" if direction == "bear" else "",
        )

    def _find_flag_pennant(
        self, df: pd.DataFrame, last_idx: int
    ) -> Optional[Tuple[str, float, int, float, float]]:
        """
        Pole + Consolidation 탐지.
        Returns (direction, pole_pct, pole_end_idx, consol_high, consol_low)
        또는 None.
        """
        closes = df["close"].values

        # consolidation 길이 순서로 탐색 (짧은 것 우선)
        for consol_len in range(CONSOL_MIN, CONSOL_MAX + 1):
            pole_end_idx = last_idx - consol_len
            if pole_end_idx < POLE_BARS:
                break

            pole_start_idx = pole_end_idx - POLE_BARS
            if pole_start_idx < 0:
                continue

            pole_start_price = float(closes[pole_start_idx])
            pole_end_price = float(closes[pole_end_idx])

            if pole_start_price <= 0:
                continue

            pole_pct = (pole_end_price - pole_start_price) / pole_start_price

            # Pole 조건: 5% 이상 급등 또는 급락
            if abs(pole_pct) < POLE_THRESHOLD:
                continue

            direction = "bull" if pole_pct > 0 else "bear"

            # Consolidation 구간
            consol_slice = closes[pole_end_idx: last_idx + 1]
            if len(consol_slice) < CONSOL_MIN:
                continue

            consol_high = float(np.max(consol_slice))
            consol_low = float(np.min(consol_slice))
            consol_range = consol_high - consol_low

            # Pole 범위
            pole_range = abs(pole_end_price - pole_start_price)
            if pole_range <= 0:
                continue

            # Consolidation 변동폭이 pole보다 작아야 함
            if consol_range >= pole_range * 0.6:
                continue

            # Bullish: consolidation이 pole_end 아래에 있어야 함 (조정)
            # Bearish: consolidation이 pole_end 위에 있어야 함 (반등 조정)
            if direction == "bull" and consol_high > pole_end_price * 1.02:
                continue
            if direction == "bear" and consol_low < pole_end_price * 0.98:
                continue

            return (direction, pole_pct, pole_end_idx, consol_high, consol_low)

        return None
