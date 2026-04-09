"""
Support Resistance Breakout 전략: 스윙 고점/저점 기반 지지/저항선 돌파 전략.

- 저항선: 최근 20봉 중 swing high (±2봉 기준 최고점)
- 지지선: 최근 20봉 중 swing low (±2봉 기준 최저점)
- BUY: close > resistance AND 이전 close <= resistance AND 볼륨 > 20봉 평균
- SELL: close < support AND 이전 close >= support AND 볼륨 > 20봉 평균
- confidence: HIGH if 이격률 > 0.5%, MEDIUM otherwise
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class SRBreakoutStrategy(BaseStrategy):
    name = "sr_breakout"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 25:
            return self._hold(df, "데이터 부족")

        idx = len(df) - 2
        period = 20

        # swing high/low 탐지 (idx-1 제외: 미래 참조 방지)
        window = df.iloc[idx - period: idx - 1]

        swing_highs = []
        swing_lows = []
        for i in range(2, len(window) - 2):
            h = float(window["high"].iloc[i])
            if (h > float(window["high"].iloc[i - 1]) and h > float(window["high"].iloc[i - 2])
                    and h > float(window["high"].iloc[i + 1]) and h > float(window["high"].iloc[i + 2])):
                swing_highs.append(h)
            l = float(window["low"].iloc[i])
            if (l < float(window["low"].iloc[i - 1]) and l < float(window["low"].iloc[i - 2])
                    and l < float(window["low"].iloc[i + 1]) and l < float(window["low"].iloc[i + 2])):
                swing_lows.append(l)

        if not swing_highs or not swing_lows:
            return self._hold(df, "No swing points found")

        resistance = max(swing_highs)
        support = min(swing_lows)

        close = float(df["close"].iloc[idx])
        prev_close = float(df["close"].iloc[idx - 1])

        # 볼륨 필터
        vol_window = df["volume"].iloc[idx - period: idx]
        avg_vol = float(vol_window.mean()) if len(vol_window) > 0 else 0.0
        vol_confirm = avg_vol > 0 and float(df["volume"].iloc[idx]) > avg_vol

        entry = close

        bull_case = (
            f"Price ({close:.2f}) broke above resistance ({resistance:.2f}). "
            f"Support={support:.2f}, VolConfirm={vol_confirm}"
        )
        bear_case = (
            f"Price ({close:.2f}) broke below support ({support:.2f}). "
            f"Resistance={resistance:.2f}, VolConfirm={vol_confirm}"
        )

        # BUY: 저항선 돌파
        if close > resistance and prev_close <= resistance and vol_confirm:
            gap_pct = (close - resistance) / resistance * 100
            conf = Confidence.HIGH if gap_pct > 0.5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Breakout above resistance {resistance:.2f}. "
                    f"Gap={gap_pct:.2f}%, VolConfirm={vol_confirm}."
                ),
                invalidation=f"Close back below resistance ({resistance:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: 지지선 이탈
        if close < support and prev_close >= support and vol_confirm:
            gap_pct = (support - close) / support * 100
            conf = Confidence.HIGH if gap_pct > 0.5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Breakdown below support {support:.2f}. "
                    f"Gap={gap_pct:.2f}%, VolConfirm={vol_confirm}."
                ),
                invalidation=f"Close back above support ({support:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(df, f"No breakout. Resistance={resistance:.2f}, Support={support:.2f}")

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
