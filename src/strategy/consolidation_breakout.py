"""
ConsolidationBreakout 전략:
- 최근 10봉이 좁은 범위(3% 이내)를 형성한 후 돌파 시 진입.
- BUY: consolidation + close > consol_high * 1.001
- SELL: consolidation + close < consol_low * 0.999
- confidence: volume > avg_vol * 2.0 → HIGH, 그 외 MEDIUM
- 최소 행: 15
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_CONSOL_WINDOW = 10       # consolidation 판단 봉 수
_RANGE_THRESHOLD = 0.03   # 3% 이내 → consolidation
_BUY_BREAKOUT_MULT = 1.001
_SELL_BREAKOUT_MULT = 0.999
_VOL_HIGH_MULT = 2.0
_MIN_ROWS = 15


class ConsolidationBreakoutStrategy(BaseStrategy):
    name = "consolidation_breakout"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        last = self._last(df)  # df.iloc[-2]
        entry = float(last["close"])

        # consolidation window: 3~10봉 이전 (last 기준 인덱스 -2)
        # df.iloc[-2] = last completed candle (index len-2)
        # consol window: iloc[-(2+10) : -2] → 10봉
        consol = df.iloc[-(2 + _CONSOL_WINDOW):-2]
        if len(consol) < _CONSOL_WINDOW:
            return self._hold(entry, "Consolidation 데이터 부족", "", "")

        consol_high = float(consol["high"].max())
        consol_low = float(consol["low"].min())
        consol_range = (consol_high - consol_low) / float(consol["close"].iloc[-1]) if consol["close"].iloc[-1] != 0 else 1.0

        is_consolidation = consol_range < _RANGE_THRESHOLD

        # 볼륨 필터: 최근 20봉 평균 (last 이전)
        vol_window = df["volume"].iloc[-(2 + 20):-2]
        avg_vol = float(vol_window.mean()) if len(vol_window) > 0 else 0.0
        curr_vol = float(last["volume"])
        vol_high = avg_vol > 0 and curr_vol > avg_vol * _VOL_HIGH_MULT

        bull_case = (
            f"Consolidation range {consol_range:.2%} < 3%, "
            f"consol_high={consol_high:.4f}, close={entry:.4f}"
        )
        bear_case = (
            f"Consolidation range {consol_range:.2%} < 3%, "
            f"consol_low={consol_low:.4f}, close={entry:.4f}"
        )

        if is_consolidation and entry > consol_high * _BUY_BREAKOUT_MULT:
            conf = Confidence.HIGH if vol_high else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Consolidation breakout UP: range={consol_range:.2%}, "
                    f"close={entry:.4f} > consol_high*1.001={consol_high * _BUY_BREAKOUT_MULT:.4f}, "
                    f"vol_high={vol_high}"
                ),
                invalidation=f"Close back below consolidation high ({consol_high:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if is_consolidation and entry < consol_low * _SELL_BREAKOUT_MULT:
            conf = Confidence.HIGH if vol_high else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Consolidation breakout DOWN: range={consol_range:.2%}, "
                    f"close={entry:.4f} < consol_low*0.999={consol_low * _SELL_BREAKOUT_MULT:.4f}, "
                    f"vol_high={vol_high}"
                ),
                invalidation=f"Close back above consolidation low ({consol_low:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        reason = (
            f"No breakout. consolidation={is_consolidation}, range={consol_range:.2%}, "
            f"close={entry:.4f}, consol_high={consol_high:.4f}, consol_low={consol_low:.4f}"
        )
        return self._hold(entry, reason, bull_case, bear_case)

    def _hold(self, entry: float, reason: str, bull_case: str, bear_case: str) -> Signal:
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
