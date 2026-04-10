"""
MarketBreadthProxyStrategy:
- 단일 심볼에서 breadth 대리 지표 계산
- BUY: ad_ratio > 1.5 AND ad_ratio > ad_ma AND close > EMA(20)
- SELL: ad_ratio < 0.67 AND ad_ratio < ad_ma AND close < EMA(20)
- 최소 30행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_ROLLING_WINDOW = 20


class MarketBreadthProxyStrategy(BaseStrategy):
    name = "market_breadth_proxy"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for market_breadth_proxy",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        close = df["close"]

        advances = (close > close.shift(1)).rolling(_ROLLING_WINDOW, min_periods=1).sum()
        declines = (close < close.shift(1)).rolling(_ROLLING_WINDOW, min_periods=1).sum()
        ad_ratio = advances / (declines + 1)
        ad_ma = ad_ratio.rolling(5, min_periods=1).mean()
        ema20 = close.ewm(span=20).mean()

        adr = float(ad_ratio.iloc[idx])
        adm = float(ad_ma.iloc[idx])
        price = float(close.iloc[idx])
        ema = float(ema20.iloc[idx])
        entry = price

        if any(pd.isna(v) for v in [adr, adm, price, ema]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in market_breadth_proxy indicators",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        if adr > 1.5 and adr > adm and price > ema:
            conf = Confidence.HIGH if adr > 2.0 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"market_breadth_proxy BUY: ad_ratio={adr:.3f} > 1.5, "
                    f"ad_ratio > ad_ma={adm:.3f}, close={price:.4f} > ema20={ema:.4f}"
                ),
                invalidation="ad_ratio가 1.5 아래로 하락 또는 종가가 EMA 아래",
                bull_case="breadth 대리 지표 강세, 상승 추세 지속",
                bear_case="단일 심볼 기반 breadth 한계",
            )

        if adr < 0.67 and adr < adm and price < ema:
            conf = Confidence.HIGH if adr < 0.5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"market_breadth_proxy SELL: ad_ratio={adr:.3f} < 0.67, "
                    f"ad_ratio < ad_ma={adm:.3f}, close={price:.4f} < ema20={ema:.4f}"
                ),
                invalidation="ad_ratio가 0.67 위로 회복 또는 종가가 EMA 위",
                bull_case="단기 반등 가능",
                bear_case="breadth 대리 지표 약세, 하락 추세 지속",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"market_breadth_proxy HOLD: ad_ratio={adr:.3f}, "
                f"ad_ma={adm:.3f}, close={price:.4f}, ema20={ema:.4f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
