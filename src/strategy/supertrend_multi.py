"""
SupertrendMultiStrategy: 3개의 Supertrend 지표를 조합한 추세 추종 전략.

- Supertrend 3개: (ATR10, mult=1.5), (ATR14, mult=2.0), (ATR20, mult=3.0)
- BUY:  3개 모두 bullish (trend == 1)
- SELL: 3개 모두 bearish (trend == -1)
- confidence: 3개 모두 일치 AND volume > avg_vol * 1.1 → HIGH, 아니면 MEDIUM
- 최소 행: 25
"""

from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class SupertrendMultiStrategy(BaseStrategy):
    name = "supertrend_multi"

    # (atr_period, multiplier)
    CONFIGS: List[Tuple[int, float]] = [
        (10, 1.5),
        (14, 2.0),
        (20, 3.0),
    ]
    MIN_ROWS = 25

    def _compute_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """True Range 기반 ATR 계산."""
        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1)
        tr = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
            axis=1,
        ).max(axis=1)
        atr = tr.ewm(alpha=1.0 / period, adjust=False).mean()
        return atr

    def _compute_supertrend_trend(
        self, df: pd.DataFrame, atr_period: int, mult: float
    ) -> pd.Series:
        """
        trend 시리즈 반환: 1 = bullish, -1 = bearish.

        Supertrend 계산:
          basic_upper = (high+low)/2 + mult * atr
          basic_lower = (high+low)/2 - mult * atr
          final_upper/lower 추적 후 trend 결정.
        """
        hl2 = (df["high"] + df["low"]) / 2.0
        atr = self._compute_atr(df, atr_period)

        basic_upper = hl2 + mult * atr
        basic_lower = hl2 - mult * atr

        n = len(df)
        final_upper = basic_upper.copy()
        final_lower = basic_lower.copy()
        trend = pd.Series(1, index=df.index, dtype=int)

        close = df["close"]

        for i in range(1, n):
            # final_upper: 현재 basic_upper가 이전 final_upper보다 작거나
            # 이전 close가 이전 final_upper보다 작으면 갱신
            bu = float(basic_upper.iloc[i])
            fu_prev = float(final_upper.iloc[i - 1])
            c_prev = float(close.iloc[i - 1])

            if bu < fu_prev or c_prev < fu_prev:
                final_upper.iloc[i] = bu
            else:
                final_upper.iloc[i] = fu_prev

            # final_lower: 현재 basic_lower가 이전 final_lower보다 크거나
            # 이전 close가 이전 final_lower보다 크면 갱신
            bl = float(basic_lower.iloc[i])
            fl_prev = float(final_lower.iloc[i - 1])

            if bl > fl_prev or c_prev > fl_prev:
                final_lower.iloc[i] = bl
            else:
                final_lower.iloc[i] = fl_prev

            # trend 결정: close vs final_upper_prev / final_lower_prev
            c = float(close.iloc[i])
            fu_prev_val = float(final_upper.iloc[i - 1])
            fl_prev_val = float(final_lower.iloc[i - 1])
            prev_trend = int(trend.iloc[i - 1])

            if c > fu_prev_val:
                trend.iloc[i] = 1
            elif c < fl_prev_val:
                trend.iloc[i] = -1
            else:
                trend.iloc[i] = prev_trend

        return trend

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return self._hold(df, f"데이터 부족: {len(df)} < {self.MIN_ROWS}")

        # 각 Supertrend의 마지막 완성봉(-2) trend 값 계산
        trends: List[int] = []
        for atr_period, mult in self.CONFIGS:
            t = self._compute_supertrend_trend(df, atr_period, mult)
            trends.append(int(t.iloc[-2]))

        all_bullish = all(t == 1 for t in trends)
        all_bearish = all(t == -1 for t in trends)

        last = self._last(df)
        entry = float(last["close"])

        # 볼륨 필터
        vol_high = False
        vol_info = ""
        if "volume" in df.columns:
            lookback = min(20, len(df) - 2)
            avg_vol = float(df["volume"].iloc[-lookback - 2: -2].mean())
            cur_vol = float(df["volume"].iloc[-2])
            vol_high = avg_vol > 0 and cur_vol > avg_vol * 1.1
            vol_info = f" vol={cur_vol:.0f} avg={avg_vol:.0f}"

        trend_str = str(trends)

        if all_bullish:
            conf = Confidence.HIGH if vol_high else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"3개 Supertrend 모두 bullish{vol_info}. trends={trend_str}",
                invalidation="Supertrend 중 하나라도 bearish 전환 시 무효",
                bull_case=f"ATR 기반 3중 bullish 확인. trends={trend_str}",
                bear_case="추세 반전 가능성 존재",
            )

        if all_bearish:
            conf = Confidence.HIGH if vol_high else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"3개 Supertrend 모두 bearish{vol_info}. trends={trend_str}",
                invalidation="Supertrend 중 하나라도 bullish 전환 시 무효",
                bull_case="추세 반전 가능성 존재",
                bear_case=f"ATR 기반 3중 bearish 확인. trends={trend_str}",
            )

        return self._hold(df, f"Supertrend 불일치: trends={trend_str}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
