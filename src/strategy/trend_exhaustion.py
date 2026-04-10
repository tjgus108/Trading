"""
TrendExhaustionStrategy:
- 추세 소진 감지 — 가격이 계속 같은 방향이지만 모멘텀이 약해질 때
- BUY:  bars_up <= 3 AND roc5 > 0 AND roc5 > roc5_ma
- SELL: bars_up >= 8 AND trend_up AND mom_weak_up (roc5 < roc5_ma * 0.5)
- confidence: HIGH if bars_up >= 9 (SELL) or bars_up <= 2 (BUY) else MEDIUM
- 최소 데이터: 25행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 25


def _calc_atr14(df: pd.DataFrame) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(14).mean()


class TrendExhaustionStrategy(BaseStrategy):
    name = "trend_exhaustion"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning=f"Insufficient data: {len(df)} < {MIN_ROWS}",
                invalidation="",
            )

        idx = len(df) - 2
        last = self._last(df)  # df.iloc[-2]
        close = df["close"]

        ema20 = close.ewm(span=20, adjust=False).mean()
        roc5 = close.pct_change(5)
        roc5_ma = roc5.rolling(10).mean()
        atr14 = _calc_atr14(df)

        roc5_val = roc5.iloc[idx]
        roc5_ma_val = roc5_ma.iloc[idx]
        trend_up_val = bool(close.iloc[idx] > ema20.iloc[idx])
        atr_val = atr14.iloc[idx]

        # bars_up: 최근 10봉 중 ema20 위에 있는 봉 수
        bars_up_val = int(
            (
                close.iloc[max(0, idx - 9):idx + 1]
                > ema20.iloc[max(0, idx - 9):idx + 1]
            ).sum()
        )

        # NaN 체크
        if pd.isna(roc5_val) or pd.isna(roc5_ma_val) or pd.isna(atr_val):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last["close"]),
                reasoning="NaN in indicators",
                invalidation="",
            )

        entry_price = float(last["close"])
        mom_weak_up = roc5_val < roc5_ma_val * 0.5

        # SELL: 상승 추세 소진
        if bars_up_val >= 8 and trend_up_val and mom_weak_up:
            conf = Confidence.HIGH if bars_up_val >= 9 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"추세 소진: bars_up={bars_up_val}/10, trend_up=True, "
                    f"roc5={roc5_val:.4f} < roc5_ma*0.5={roc5_ma_val*0.5:.4f}"
                ),
                invalidation=f"Close above EMA20={ema20.iloc[idx]:.4f}",
                bull_case="",
                bear_case=f"Momentum weakening, ATR={atr_val:.4f}",
            )

        # BUY: 추세 바닥에서 반등 초기
        if bars_up_val <= 3 and roc5_val > 0 and roc5_val > roc5_ma_val:
            conf = Confidence.HIGH if bars_up_val <= 2 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"추세 반등 초기: bars_up={bars_up_val}/10, "
                    f"roc5={roc5_val:.4f} > roc5_ma={roc5_ma_val:.4f}"
                ),
                invalidation=f"Close below EMA20={ema20.iloc[idx]:.4f}",
                bull_case=f"Momentum recovering, ATR={atr_val:.4f}",
                bear_case="",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"추세 소진 조건 미충족: bars_up={bars_up_val}/10, "
                f"roc5={roc5_val:.4f}, roc5_ma={roc5_ma_val:.4f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
