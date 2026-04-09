"""
BidAskImbalanceStrategy: OHLCV 기반 매수/매도 압력 불균형 전략.

- Buy volume 추정: volume * (close - low) / (high - low)
- Sell volume 추정: volume * (high - close) / (high - low)
- Imbalance = (buy_vol - sell_vol) / (buy_vol + sell_vol)  → [-1, 1]
- Imbalance EMA(span=10)
- BUY: imbalance_ema > 0.2 AND close > EMA20
- SELL: imbalance_ema < -0.2 AND close < EMA20
- confidence: |imbalance_ema| > 0.4 → HIGH
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

BUY_THRESHOLD = 0.2
SELL_THRESHOLD = -0.2
HIGH_CONF_ABS = 0.4
EMA_SPAN = 10
EMA_PERIOD = 20
MIN_ROWS = 20


class BidAskImbalanceStrategy(BaseStrategy):
    name = "bid_ask_imbalance"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning=f"데이터 부족 (최소 {MIN_ROWS}봉 필요)",
                invalidation="",
            )

        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        hl_range = high - low
        # 0으로 나누기 방지
        safe_range = hl_range.where(hl_range > 0, other=None)

        buy_vol = volume * (close - low) / safe_range
        sell_vol = volume * (high - close) / safe_range

        # range == 0인 봉: volume * 0.5
        mask_zero = hl_range == 0
        buy_vol = buy_vol.where(~mask_zero, other=volume * 0.5)
        sell_vol = sell_vol.where(~mask_zero, other=volume * 0.5)

        total = buy_vol + sell_vol
        imbalance = (buy_vol - sell_vol) / total.where(total > 0, other=1.0)
        imbalance_ema = imbalance.ewm(span=EMA_SPAN).mean()

        ema20 = close.ewm(span=EMA_PERIOD).mean()

        last = self._last(df)
        idx = len(df) - 2

        cur_imb_ema = float(imbalance_ema.iloc[idx])
        cur_close = float(last["close"])
        cur_ema20 = float(ema20.iloc[idx])

        conf = Confidence.HIGH if abs(cur_imb_ema) > HIGH_CONF_ABS else Confidence.MEDIUM

        if cur_imb_ema > BUY_THRESHOLD and cur_close > cur_ema20:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=cur_close,
                reasoning=(
                    f"imbalance_ema={cur_imb_ema:.3f} > {BUY_THRESHOLD} "
                    f"AND close={cur_close:.4f} > EMA20={cur_ema20:.4f}"
                ),
                invalidation=f"imbalance_ema < 0 or close < EMA20({cur_ema20:.4f})",
                bull_case=f"매수 압력 우세 (ema={cur_imb_ema:.3f}), 추세 상방",
                bear_case="imbalance 반전 시 빠른 손절 필요",
            )

        if cur_imb_ema < SELL_THRESHOLD and cur_close < cur_ema20:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=cur_close,
                reasoning=(
                    f"imbalance_ema={cur_imb_ema:.3f} < {SELL_THRESHOLD} "
                    f"AND close={cur_close:.4f} < EMA20={cur_ema20:.4f}"
                ),
                invalidation=f"imbalance_ema > 0 or close > EMA20({cur_ema20:.4f})",
                bull_case="imbalance 반전 시 커버 필요",
                bear_case=f"매도 압력 우세 (ema={cur_imb_ema:.3f}), 추세 하방",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=cur_close,
            reasoning=(
                f"조건 미충족. imbalance_ema={cur_imb_ema:.3f}, "
                f"close={cur_close:.4f}, EMA20={cur_ema20:.4f}"
            ),
            invalidation="",
            bull_case=f"imbalance_ema > {BUY_THRESHOLD} AND close > EMA20 시 BUY",
            bear_case=f"imbalance_ema < {SELL_THRESHOLD} AND close < EMA20 시 SELL",
        )
