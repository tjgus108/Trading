"""
Volatility Contraction Pattern (VCP):
  N개 연속적으로 변동성이 줄어드는 패턴 탐지.

  week_highs[i] = max(high, last 5 candles ending at i)
  week_lows[i]  = min(low, last 5 candles ending at i)
  contraction[i] = week_highs[i] - week_lows[i]

  수축 패턴 = 최근 3개의 5봉 레인지가 연속으로 줄어듦
  (contraction[-3] > contraction[-2] > contraction[-1])

  BUY:  수축 패턴 감지 AND close > week_highs[-1] * 0.99
  SELL: 수축 패턴 감지 AND close < week_lows[-1] * 1.01

  confidence: HIGH if 수축률 > 30% (마지막 range < 최초 range * 0.7), MEDIUM 그 외
  최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 20


class VCPStrategy(BaseStrategy):
    name = "vcp"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: VCP 계산에 최소 20행 필요",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        highs = df["high"].values
        lows = df["low"].values
        closes = df["close"].values
        n = len(df)

        # 5봉 롤링 최고/최저 계산 (인덱스 i는 마지막 5봉 ending at i 포함)
        week_highs = []
        week_lows = []
        for i in range(n):
            start = max(0, i - 4)
            week_highs.append(max(highs[start: i + 1]))
            week_lows.append(min(lows[start: i + 1]))

        contractions = [week_highs[i] - week_lows[i] for i in range(n)]

        # 최근 3개 수축값: [-3], [-2], [-1] (인덱스 기준 -2 = _last)
        c1 = contractions[-3]
        c2 = contractions[-2]
        c3 = contractions[-1]

        contraction_pattern = c1 > c2 > c3

        last = self._last(df)  # df.iloc[-2]
        close = float(last["close"])
        wh = week_highs[-2]  # _last 기준
        wl = week_lows[-2]

        # 수축률: 마지막 range < 최초 range(c1) * 0.7
        high_confidence = c3 < c1 * 0.7 if c1 > 0 else False

        bull_case = (
            f"VCP 수축 패턴: range {c1:.4f} → {c2:.4f} → {c3:.4f}, "
            f"상단={wh:.4f}, 하단={wl:.4f}, close={close:.4f}"
        )
        bear_case = bull_case

        if contraction_pattern and close > wh * 0.99:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if high_confidence else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"VCP BUY: 수축 패턴 감지 ({c1:.4f}>{c2:.4f}>{c3:.4f}), "
                    f"close={close:.4f} > 수축 상단 {wh * 0.99:.4f}"
                ),
                invalidation=f"Close below week_low {wl:.4f}",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if contraction_pattern and close < wl * 1.01:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH if high_confidence else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"VCP SELL: 수축 패턴 감지 ({c1:.4f}>{c2:.4f}>{c3:.4f}), "
                    f"close={close:.4f} < 수축 하단 {wl * 1.01:.4f}"
                ),
                invalidation=f"Close above week_high {wh:.4f}",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        reason = (
            f"수축 패턴 미감지: range [{c1:.4f}, {c2:.4f}, {c3:.4f}]"
            if not contraction_pattern
            else f"수축 패턴 감지됐으나 돌파/붕괴 없음 (close={close:.4f}, 상단={wh:.4f}, 하단={wl:.4f})"
        )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
