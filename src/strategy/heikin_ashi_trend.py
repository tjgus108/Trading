"""
HeikinAshiTrendStrategy: Heikin-Ashi 캔들 기반 추세 전략 (streak 방식).
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class HeikinAshiTrendStrategy(BaseStrategy):
    name = "heikin_ashi_trend"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = float(last["close"])

        if len(df) < 20:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="데이터 부족 (최소 20행 필요)",
                invalidation="N/A",
            )

        open_ = df["open"]
        high = df["high"]
        low = df["low"]
        close = df["close"]

        # ── Heikin-Ashi 계산 ────────────────────────────────────────────
        ha_close = (open_ + high + low + close) / 4
        ha_open = ha_close.shift(1)
        ha_open.iloc[0] = open_.iloc[0]
        ha_high = pd.concat([high, ha_open, ha_close], axis=1).max(axis=1)
        ha_low = pd.concat([low, ha_open, ha_close], axis=1).min(axis=1)  # noqa: F841

        ha_bullish = ha_close > ha_open
        ha_bearish = ha_close < ha_open

        ha_bull_streak = ha_bullish.astype(int).rolling(3, min_periods=1).sum()
        ha_bear_streak = ha_bearish.astype(int).rolling(3, min_periods=1).sum()

        idx = len(df) - 2  # 마지막 완성 캔들

        bull_streak = float(ha_bull_streak.iloc[idx])
        bear_streak = float(ha_bear_streak.iloc[idx])
        ha_c = float(ha_close.iloc[idx])
        ha_c_prev = float(ha_close.iloc[idx - 1])

        # NaN 체크
        if pd.isna(ha_c) or pd.isna(ha_c_prev):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN 감지 (HOLD)",
                invalidation="N/A",
            )

        # ── 신호 판단 ────────────────────────────────────────────────────
        if bull_streak >= 2 and ha_c > ha_c_prev:
            confidence = Confidence.HIGH if bull_streak == 3 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"HA 상승 streak={int(bull_streak)}, "
                    f"HA_Close 상승 확인 ({ha_c_prev:.4f} → {ha_c:.4f})"
                ),
                invalidation=f"HA_Close 하락 시 무효. 현재 HA_Close={ha_c:.4f}",
                bull_case=f"HA 연속 상승 streak={int(bull_streak)}",
                bear_case="streak 감소 시 추세 약화",
            )

        if bear_streak >= 2 and ha_c < ha_c_prev:
            confidence = Confidence.HIGH if bear_streak == 3 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"HA 하락 streak={int(bear_streak)}, "
                    f"HA_Close 하락 확인 ({ha_c_prev:.4f} → {ha_c:.4f})"
                ),
                invalidation=f"HA_Close 상승 시 무효. 현재 HA_Close={ha_c:.4f}",
                bull_case="HA_Close 반등 시 추세 전환 가능",
                bear_case=f"HA 연속 하락 streak={int(bear_streak)}",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning="HA 추세 조건 미충족 (HOLD)",
            invalidation="N/A",
        )
