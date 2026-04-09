"""
Turtle Trading Strategy (Richard Dennis): 20봉/55봉 채널 돌파 전략.

- System 1 Entry: 20봉 최고가/최저가 돌파 + 볼륨 필터
- System 2 Confidence: 55봉 채널도 돌파 시 HIGH
- Exit Channel: 10봉 저가(BUY 청산) / 10봉 고가(SELL 청산)
- ATR 기반 포지션 사이징 기준 reasoning에 포함
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class TurtleTradingStrategy(BaseStrategy):
    name = "turtle_trading"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 60:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="Not enough data (need 60+ bars).",
                invalidation="",
            )

        idx = len(df) - 2

        h20 = float(df["high"].iloc[idx - 20:idx].max())
        l20 = float(df["low"].iloc[idx - 20:idx].min())
        h55 = float(df["high"].iloc[idx - 55:idx].max())
        l55 = float(df["low"].iloc[idx - 55:idx].min())

        close = float(df["close"].iloc[idx])
        avg_vol = float(df["volume"].iloc[idx - 20:idx].mean())
        vol_ok = float(df["volume"].iloc[idx]) > avg_vol

        # Exit channels
        exit_low10 = float(df["low"].iloc[idx - 10:idx].min())   # BUY 청산 기준
        exit_high10 = float(df["high"].iloc[idx - 10:idx].max())  # SELL 청산 기준

        # ATR for position sizing reference
        atr = float(df["atr14"].iloc[idx]) if "atr14" in df.columns else 0.0

        buy20 = close > h20
        sell20 = close < l20
        buy55 = close > h55
        sell55 = close < l55

        entry = close

        if buy20 and vol_ok:
            conf = Confidence.HIGH if buy55 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Turtle BUY: close ({close:.4f}) > 20-bar high ({h20:.4f}). "
                    f"55-bar break={buy55}. Vol OK. "
                    f"Exit channel (10-bar low): {exit_low10:.4f}. "
                    f"ATR14={atr:.4f} (position sizing ref)."
                ),
                invalidation=f"Close below 10-bar low ({exit_low10:.4f})",
                bull_case=f"55-bar high={h55:.4f} {'also broken' if buy55 else 'not yet broken'}. Strong uptrend.",
                bear_case=f"Reversal back below 20-bar high ({h20:.4f}).",
            )

        if sell20 and vol_ok:
            conf = Confidence.HIGH if sell55 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Turtle SELL: close ({close:.4f}) < 20-bar low ({l20:.4f}). "
                    f"55-bar break={sell55}. Vol OK. "
                    f"Exit channel (10-bar high): {exit_high10:.4f}. "
                    f"ATR14={atr:.4f} (position sizing ref)."
                ),
                invalidation=f"Close above 10-bar high ({exit_high10:.4f})",
                bull_case=f"Reversal back above 20-bar low ({l20:.4f}).",
                bear_case=f"55-bar low={l55:.4f} {'also broken' if sell55 else 'not yet broken'}. Strong downtrend.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"No Turtle breakout. close={close:.4f}, "
                f"20-bar range=[{l20:.4f}, {h20:.4f}], vol_ok={vol_ok}."
            ),
            invalidation="",
            bull_case=f"Break above 20-bar high ({h20:.4f}) with volume.",
            bear_case=f"Break below 20-bar low ({l20:.4f}) with volume.",
        )
