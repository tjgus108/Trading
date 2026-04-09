"""
EMA Ribbon Strategy: 5개 EMA 리본 정렬 + EMA5/EMA10 크로스 감지.

리본: EMA(5), EMA(10), EMA(20), EMA(40), EMA(80)

Bullish alignment: ema5 > ema10 > ema20 > ema40 > ema80
Bearish alignment: ema5 < ema10 < ema20 < ema40 < ema80

BUY:  bullish alignment AND EMA5 just crossed above EMA10
      (prev: ema5 <= ema10, now: ema5 > ema10)
SELL: bearish alignment AND EMA5 just crossed below EMA10
      (prev: ema5 >= ema10, now: ema5 < ema10)

confidence HIGH: spread (ema5 - ema80) > 2% of close (BUY)
                 spread (ema80 - ema5) > 2% of close (SELL)
최소 행: 85
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 85


class EMARibbonStrategy(BaseStrategy):
    name = "ema_ribbon"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: EMA Ribbon 계산에 최소 85행 필요",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        ema5_s = df["close"].ewm(span=5, adjust=False).mean()
        ema10_s = df["close"].ewm(span=10, adjust=False).mean()
        ema20_s = df["close"].ewm(span=20, adjust=False).mean()
        ema40_s = df["close"].ewm(span=40, adjust=False).mean()
        ema80_s = df["close"].ewm(span=80, adjust=False).mean()

        # _last() = df.iloc[-2]
        idx = -2
        prev_idx = -3

        ema5 = float(ema5_s.iloc[idx])
        ema10 = float(ema10_s.iloc[idx])
        ema20 = float(ema20_s.iloc[idx])
        ema40 = float(ema40_s.iloc[idx])
        ema80 = float(ema80_s.iloc[idx])

        prev5 = float(ema5_s.iloc[prev_idx])
        prev10 = float(ema10_s.iloc[prev_idx])

        close = float(df["close"].iloc[idx])

        bullish_alignment = ema5 > ema10 > ema20 > ema40 > ema80
        bearish_alignment = ema5 < ema10 < ema20 < ema40 < ema80

        cross_up = (prev5 <= prev10) and (ema5 > ema10)
        cross_down = (prev5 >= prev10) and (ema5 < ema10)

        spread_pct = abs(ema5 - ema80) / close if close > 0 else 0.0
        high_conf = spread_pct > 0.02

        bull_case = (
            f"EMA5={ema5:.4f} EMA10={ema10:.4f} EMA20={ema20:.4f} "
            f"EMA40={ema40:.4f} EMA80={ema80:.4f} | "
            f"bullish_alignment={bullish_alignment} cross_up={cross_up} spread={spread_pct:.4f}"
        )
        bear_case = (
            f"EMA5={ema5:.4f} EMA10={ema10:.4f} EMA20={ema20:.4f} "
            f"EMA40={ema40:.4f} EMA80={ema80:.4f} | "
            f"bearish_alignment={bearish_alignment} cross_down={cross_down} spread={spread_pct:.4f}"
        )

        if bullish_alignment and cross_up:
            conf = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"EMA Ribbon BUY: 5-EMA 리본 완전 정렬 + EMA5({ema5:.4f}) crossed above EMA10({ema10:.4f}). "
                    f"spread={spread_pct:.4%} ({'HIGH' if high_conf else 'MEDIUM'})"
                ),
                invalidation=f"EMA5 아래로 재이탈 또는 정렬 붕괴 (ema10={ema10:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if bearish_alignment and cross_down:
            conf = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"EMA Ribbon SELL: 5-EMA 리본 완전 역정렬 + EMA5({ema5:.4f}) crossed below EMA10({ema10:.4f}). "
                    f"spread={spread_pct:.4%} ({'HIGH' if high_conf else 'MEDIUM'})"
                ),
                invalidation=f"EMA5 위로 재돌파 또는 정렬 붕괴 (ema10={ema10:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"EMA Ribbon HOLD: bullish={bullish_alignment}, bearish={bearish_alignment}, "
                f"cross_up={cross_up}, cross_down={cross_down}. "
                f"ema5={ema5:.4f}, ema10={ema10:.4f}, ema80={ema80:.4f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
