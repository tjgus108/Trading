"""
EMADynamicSupportStrategy: EMA를 동적 지지/저항으로 활용.

- EMA21, EMA55 사용 (최소 행 60)
- Touch and bounce: close가 EMA에 닿은 후 반등
- BUY: (close ≈ EMA21 ±0.3%) AND close > EMA21 AND close > prev_close AND EMA21 > EMA55
- SELL: (close ≈ EMA21 ±0.3%) AND close < EMA21 AND close < prev_close AND EMA21 < EMA55
- EMA55 터치도 신호: |close/EMA55 - 1| < 0.005
- confidence HIGH: EMA21 > EMA55 > EMA200 (EMA200 있을 때) 또는 EMA21 > EMA55 완전 정렬
- 최소 행: 60
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class EMADynamicSupportStrategy(BaseStrategy):
    name = "ema_dynamic_support"

    MIN_ROWS = 60
    EMA21_TOUCH_PCT = 0.003   # ±0.3%
    EMA55_TOUCH_PCT = 0.005   # ±0.5%

    def _compute_ema(self, series: pd.Series, span: int) -> pd.Series:
        return series.ewm(span=span, adjust=False).mean()

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: 최소 60행 필요",
                invalidation="",
            )

        ema21_series = self._compute_ema(df["close"], 21)
        ema55_series = self._compute_ema(df["close"], 55)

        last_idx = -2  # _last == df.iloc[-2]
        last = self._last(df)
        prev = df.iloc[-3]

        close = float(last["close"])
        prev_close = float(prev["close"])
        ema21 = float(ema21_series.iloc[last_idx])
        ema55 = float(ema55_series.iloc[last_idx])

        # EMA200 (선택적)
        ema200: Optional[float] = None
        if len(df) >= 210:
            ema200 = float(self._compute_ema(df["close"], 200).iloc[last_idx])

        # EMA21 터치 여부
        ema21_touch = abs(close / ema21 - 1) < self.EMA21_TOUCH_PCT if ema21 != 0 else False
        # EMA55 터치 여부
        ema55_touch = abs(close / ema55 - 1) < self.EMA55_TOUCH_PCT if ema55 != 0 else False

        trend_up = ema21 > ema55
        trend_down = ema21 < ema55

        # confidence: 완전 정렬이면 HIGH
        if ema200 is not None:
            full_bull_align = ema21 > ema55 > ema200
            full_bear_align = ema21 < ema55 < ema200
        else:
            full_bull_align = trend_up
            full_bear_align = trend_down

        bull_case = (
            f"EMA21={ema21:.4f} EMA55={ema55:.4f}"
            + (f" EMA200={ema200:.4f}" if ema200 is not None else "")
            + f" close={close:.4f} prev={prev_close:.4f}"
        )
        bear_case = bull_case

        # BUY: EMA21 터치 + 반등 + 상승 추세
        ema21_buy = (
            ema21_touch
            and close > ema21
            and close > prev_close
            and trend_up
        )

        # SELL: EMA21 터치 + 반락 + 하락 추세
        ema21_sell = (
            ema21_touch
            and close < ema21
            and close < prev_close
            and trend_down
        )

        # EMA55 터치 BUY
        ema55_buy = (
            ema55_touch
            and close > ema55
            and close > prev_close
            and trend_up
        )

        # EMA55 터치 SELL
        ema55_sell = (
            ema55_touch
            and close < ema55
            and close < prev_close
            and trend_down
        )

        if ema21_buy or ema55_buy:
            touch_label = "EMA21" if ema21_buy else "EMA55"
            touch_val = ema21 if ema21_buy else ema55
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if full_bull_align else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"EMA Dynamic Support BUY: {touch_label} 터치({touch_val:.4f}) 후 반등, "
                    f"EMA21>{ema21:.4f} EMA55={ema55:.4f}, close={close:.4f}>prev={prev_close:.4f}"
                ),
                invalidation=f"Close below {touch_label} ({touch_val:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if ema21_sell or ema55_sell:
            touch_label = "EMA21" if ema21_sell else "EMA55"
            touch_val = ema21 if ema21_sell else ema55
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH if full_bear_align else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"EMA Dynamic Support SELL: {touch_label} 터치({touch_val:.4f}) 후 반락, "
                    f"EMA21={ema21:.4f} EMA55={ema55:.4f}, close={close:.4f}<prev={prev_close:.4f}"
                ),
                invalidation=f"Close above {touch_label} ({touch_val:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"EMA 터치 없음 또는 반등/반락 미확인. "
                f"EMA21={ema21:.4f} EMA55={ema55:.4f} close={close:.4f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
