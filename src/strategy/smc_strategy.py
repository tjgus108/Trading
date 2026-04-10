"""
SmartMoneyConceptStrategy: Change of Character (CHoCH) 기반 전략.

- Bearish structure: 5봉 연속 하락 (close.rolling(5): 마지막 < 첫 번째)
- Bullish structure: 5봉 연속 상승
- recent_hh = high.rolling(10).max().shift(1)  (전봉 기준 10봉 최고)
- recent_ll = low.rolling(10).min().shift(1)   (전봉 기준 10봉 최저)
- CHoCH BUY:  prev_structure_down AND close > recent_hh
- CHoCH SELL: prev_structure_up   AND close < recent_ll
- confidence: volume > avg_vol * 1.5 → HIGH, 그 외 MEDIUM
- 최소 행: 15
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 15


class SmartMoneyConceptStrategy(BaseStrategy):
    name = "smc_strategy"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        # rolling 지표 계산
        recent_hh = high.rolling(10).max().shift(1)
        recent_ll = low.rolling(10).min().shift(1)

        # 5봉 구조: apply → 마지막 값이 첫 값보다 작으면 하락
        prev_structure_down = close.rolling(5).apply(
            lambda x: float(x[-1] < x[0]), raw=True
        )
        prev_structure_up = close.rolling(5).apply(
            lambda x: float(x[-1] > x[0]), raw=True
        )

        avg_vol = volume.rolling(20, min_periods=1).mean()

        last = self._last(df)
        idx = len(df) - 2

        c = float(last["close"])
        hh = float(recent_hh.iloc[idx]) if not pd.isna(recent_hh.iloc[idx]) else None
        ll = float(recent_ll.iloc[idx]) if not pd.isna(recent_ll.iloc[idx]) else None
        str_down = float(prev_structure_down.iloc[idx]) if not pd.isna(prev_structure_down.iloc[idx]) else 0.0
        str_up = float(prev_structure_up.iloc[idx]) if not pd.isna(prev_structure_up.iloc[idx]) else 0.0
        vol = float(last["volume"])
        avg = float(avg_vol.iloc[idx]) if not pd.isna(avg_vol.iloc[idx]) else vol

        confidence = Confidence.HIGH if (avg > 0 and vol > avg * 1.5) else Confidence.MEDIUM

        # CHoCH BUY
        if str_down == 1.0 and hh is not None and c > hh:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"CHoCH BUY: bearish structure 파괴, close={c:.4f} > recent_hh={hh:.4f}"
                ),
                invalidation=f"Close 재하락 → recent_ll={ll:.4f} 이탈",
                bull_case=f"구조 전환: bearish→bullish, CHoCH at {c:.4f}",
                bear_case="False breakout 가능, 재하락 위험",
            )

        # CHoCH SELL
        if str_up == 1.0 and ll is not None and c < ll:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"CHoCH SELL: bullish structure 파괴, close={c:.4f} < recent_ll={ll:.4f}"
                ),
                invalidation=f"Close 재상승 → recent_hh={f'{hh:.4f}' if hh is not None else 'N/A'} 돌파",
                bull_case="False breakout 가능, 재상승 위험",
                bear_case=f"구조 전환: bullish→bearish, CHoCH at {c:.4f}",
            )

        return self._hold(
            df,
            f"No CHoCH: close={c:.4f}, str_down={str_down}, str_up={str_up}, hh={hh}, ll={ll}",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        price = float(df.iloc[-2]["close"]) if len(df) >= 2 else float(df.iloc[-1]["close"])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
