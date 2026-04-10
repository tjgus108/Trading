"""
CCIDivergenceStrategy:
- CCI와 가격의 다이버전스 감지
- Bullish divergence: price makes lower low, CCI makes higher low (CCI < -100)
- Bearish divergence: price makes higher high, CCI makes lower high (CCI > 100)
- confidence: CCI divergence gap > 30 → HIGH
- 최소 20행 필요
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_PERIOD = 14
_UPPER = 100
_LOWER = -100
_HIGH_CONF_DIV = 30


def _calc_cci(df: pd.DataFrame, period: int = _PERIOD) -> pd.Series:
    tp = (df["high"] + df["low"] + df["close"]) / 3
    sma = tp.rolling(period).mean()
    mean_dev = (tp - sma).abs().rolling(period).mean()
    cci = (tp - sma) / (0.015 * mean_dev)
    return cci


class CCIDivergenceStrategy(BaseStrategy):
    name = "cci_divergence"

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

        cci = _calc_cci(df)

        # 마지막 완성봉 인덱스
        idx = len(df) - 2
        # 이전 봉
        idx_prev = idx - 1

        price_now = float(df["close"].iloc[idx])
        price_prev = float(df["close"].iloc[idx_prev])

        low_now = float(df["low"].iloc[idx])
        low_prev = float(df["low"].iloc[idx_prev])
        high_now = float(df["high"].iloc[idx])
        high_prev = float(df["high"].iloc[idx_prev])

        cci_now = float(cci.iloc[idx])
        cci_prev = float(cci.iloc[idx_prev])

        entry = price_now

        # Bullish divergence: price makes lower low, CCI makes higher low (oversold zone)
        # prev low > now low (price lower low) but cci_now > cci_prev (CCI higher low)
        # both in oversold zone (CCI < -100)
        if (
            low_prev > low_now  # price makes lower low (prev_low > curr_low)
            and cci_now > cci_prev  # CCI makes higher low
            and cci_now < _LOWER  # still oversold
        ):
            div_gap = abs(cci_now - cci_prev)
            conf = Confidence.HIGH if div_gap > _HIGH_CONF_DIV else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bullish CCI divergence: price lower low ({low_prev:.2f}→{low_now:.2f}), "
                    f"CCI higher low ({cci_prev:.1f}→{cci_now:.1f}), divergence={div_gap:.1f}"
                ),
                invalidation="가격 추가 하락 및 CCI 재하락 시",
                bull_case=f"CCI oversold divergence, gap={div_gap:.1f}",
                bear_case="단순 반등 가능성",
            )

        # Bearish divergence: price makes higher high, CCI makes lower high (overbought zone)
        if (
            high_prev < high_now  # price makes higher high
            and cci_now < cci_prev  # CCI makes lower high
            and cci_now > _UPPER  # still overbought
        ):
            div_gap = abs(cci_now - cci_prev)
            conf = Confidence.HIGH if div_gap > _HIGH_CONF_DIV else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bearish CCI divergence: price higher high ({high_prev:.2f}→{high_now:.2f}), "
                    f"CCI lower high ({cci_prev:.1f}→{cci_now:.1f}), divergence={div_gap:.1f}"
                ),
                invalidation="가격 추가 상승 및 CCI 재상승 시",
                bull_case="단순 조정 가능성",
                bear_case=f"CCI overbought divergence, gap={div_gap:.1f}",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"CCI divergence 없음: CCI={cci_now:.1f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
