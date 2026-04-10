"""
AccDistStrategy: Accumulation/Distribution Line과 가격의 divergence 감지.

계산:
  CLV  = ((close - low) - (high - close)) / (high - low)   # Close Location Value
         high == low 이면 0
  A/D  = (CLV * volume).cumsum()
  ad_ema    = A/D.ewm(span=10, adjust=False).mean()
  price_ema = close.ewm(span=10, adjust=False).mean()

신호:
  BUY  : ad > ad.shift(3) AND close < close.shift(3) → bullish divergence
  SELL : ad < ad.shift(3) AND close > close.shift(3) → bearish divergence
  HOLD : 그 외
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class AccDistStrategy(BaseStrategy):
    """Accumulation/Distribution divergence 전략."""

    name: str = "acc_dist"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < 20:
            entry = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return self._hold(df, "Insufficient data (minimum 20 rows required)")

        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        denom = high - low
        clv = ((close - low) - (high - close)) / denom.where(denom != 0, other=1.0)
        clv = clv.where(denom != 0, other=0.0)

        ad = (clv * volume).cumsum()
        ad_ema = ad.ewm(span=10, adjust=False).mean()
        price_ema = close.ewm(span=10, adjust=False).mean()

        idx = len(df) - 2

        ad_now = float(ad.iloc[idx])
        ad_prev3 = float(ad.iloc[idx - 3]) if idx >= 3 else float(ad.iloc[0])
        close_now = float(close.iloc[idx])
        close_prev3 = float(close.iloc[idx - 3]) if idx >= 3 else float(close.iloc[0])
        entry_price = float(self._last(df)["close"])

        ad_change = ad_now - ad_prev3
        ad_std = float(ad.rolling(20).std().iloc[idx])
        if pd.isna(ad_std) or ad_std == 0:
            ad_std = 1.0
        confidence = Confidence.HIGH if abs(ad_change) > ad_std else Confidence.MEDIUM

        if ad_now > ad_prev3 and close_now < close_prev3:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"Bullish divergence: A/D 상승 ({ad_prev3:.2f}→{ad_now:.2f}), "
                    f"가격 하락 ({close_prev3:.4f}→{close_now:.4f})"
                ),
                invalidation="A/D가 다시 하락하면 신호 무효",
                bull_case="스마트머니 누적 중, 가격 반등 예상",
                bear_case="가격 하락 추세 지속 가능성",
            )

        if ad_now < ad_prev3 and close_now > close_prev3:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"Bearish divergence: A/D 하락 ({ad_prev3:.2f}→{ad_now:.2f}), "
                    f"가격 상승 ({close_prev3:.4f}→{close_now:.4f})"
                ),
                invalidation="A/D가 다시 상승하면 신호 무효",
                bull_case="가격 상승 추세 지속 가능성",
                bear_case="스마트머니 분산 중, 가격 하락 예상",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"Divergence 없음 (A/D={ad_now:.2f}, 3봉前={ad_prev3:.2f}; "
                f"Close={close_now:.4f}, 3봉前={close_prev3:.4f})"
            ),
            invalidation="A/D-가격 divergence 발생 시 재평가",
        )

    def _hold(self, df, reason: str) -> Signal:
        if df is not None and len(df) > 0:
            entry = float(df["close"].iloc[-1])
        else:
            entry = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="충분한 데이터 확보 후 재실행",
        )
