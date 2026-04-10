"""
PositionalScalingStrategy: 추세 지속 중 분할 진입 전략.

- 상승 추세: EMA20 > EMA50 > EMA100 (bullish alignment)
- 하락 추세: EMA20 < EMA50 < EMA100 (bearish alignment)
- 풀백 감지 (상승): close/EMA20 - 1 in [-0.01, 0.02]
- 랠리 감지 (하락): EMA20/close - 1 in [-0.01, 0.02]  (close가 EMA20 근처)
- BUY:  bullish_alignment AND pullback AND 양봉 (close > open)
- SELL: bearish_alignment AND rally   AND 음봉 (close < open)
- confidence: vol > avg_vol * 1.2 → HIGH, 그 외 MEDIUM
- 최소 행: 105
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 105


class PositionalScalingStrategy(BaseStrategy):
    name = "positional_scaling"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        open_ = df["open"]
        volume = df["volume"]

        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()
        ema100 = close.ewm(span=100, adjust=False).mean()
        avg_vol = volume.rolling(20).mean()

        last = self._last(df)
        idx = len(df) - 2

        c = float(last["close"])
        o = float(last["open"])
        e20 = float(ema20.iloc[idx])
        e50 = float(ema50.iloc[idx])
        e100 = float(ema100.iloc[idx])
        vol = float(last["volume"])
        avg = float(avg_vol.iloc[idx]) if not pd.isna(avg_vol.iloc[idx]) else vol

        bullish_alignment = e20 > e50 > e100
        bearish_alignment = e20 < e50 < e100

        # 풀백/랠리: close가 EMA20 근처
        if e20 > 0:
            deviation = c / e20 - 1.0
        else:
            return self._hold(df, "EMA20 is zero")

        pullback = -0.01 <= deviation <= 0.02
        rally = -0.01 <= deviation <= 0.02  # 동일 범위: EMA20 근처

        bullish_candle = c > o
        bearish_candle = c < o

        confidence = Confidence.HIGH if (avg > 0 and vol > avg * 1.2) else Confidence.MEDIUM

        # BUY
        if bullish_alignment and pullback and bullish_candle:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"분할진입 BUY: EMA20({e20:.4f})>EMA50({e50:.4f})>EMA100({e100:.4f}), "
                    f"풀백={deviation:.4f}, 양봉"
                ),
                invalidation=f"EMA50({e50:.4f}) 이탈 시 무효",
                bull_case=f"상승추세 지속, EMA20 풀백 후 반등 at {c:.4f}",
                bear_case="추세 반전 시 손실 위험",
            )

        # SELL
        if bearish_alignment and rally and bearish_candle:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"분할진입 SELL: EMA20({e20:.4f})<EMA50({e50:.4f})<EMA100({e100:.4f}), "
                    f"랠리={deviation:.4f}, 음봉"
                ),
                invalidation=f"EMA50({e50:.4f}) 상향 돌파 시 무효",
                bull_case="추세 반전 시 손실 위험",
                bear_case=f"하락추세 지속, EMA20 랠리 후 재하락 at {c:.4f}",
            )

        return self._hold(
            df,
            f"No signal: bullish={bullish_alignment}, bearish={bearish_alignment}, "
            f"pullback={pullback}, dev={deviation:.4f}, bull_candle={bullish_candle}",
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
