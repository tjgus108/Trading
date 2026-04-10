"""
MomentumDivergenceV2Strategy: MACD와 가격 divergence 기반 전략.

- ema12 = close.ewm(span=12, adjust=False).mean()
- ema26 = close.ewm(span=26, adjust=False).mean()
- macd = ema12 - ema26
- signal = macd.ewm(span=9, adjust=False).mean()
- hist = macd - signal
- lookback = 10
- Bullish divergence: close.iloc[idx] < price_low.iloc[idx-5] AND macd.iloc[idx] > macd_low.iloc[idx-5]
- Bearish divergence: close.iloc[idx] > price_high.iloc[idx-5] AND macd.iloc[idx] < macd_high.iloc[idx-5]
- confidence: HIGH if hist > 0 (bullish) or hist < 0 (bearish) else MEDIUM
- 최소 행: 30
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_LOOKBACK = 10
_LAG = 5


class MomentumDivergenceV2Strategy(BaseStrategy):
    name = "momentum_divergence_v2"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]) if len(df) > 0 else 0.0,
                reasoning="데이터 부족: MACD divergence 계산 불가",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        close = df["close"]

        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal_line = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal_line

        price_high = close.rolling(_LOOKBACK, min_periods=1).max()
        price_low = close.rolling(_LOOKBACK, min_periods=1).min()
        macd_high = macd.rolling(_LOOKBACK, min_periods=1).max()
        macd_low = macd.rolling(_LOOKBACK, min_periods=1).min()

        idx = len(df) - 2  # 마지막 완성 캔들

        if idx < _LAG:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(close.iloc[-1]),
                reasoning="인덱스 부족: lag 계산 불가",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        close_val = float(close.iloc[idx])
        macd_val = float(macd.iloc[idx])
        hist_val = float(hist.iloc[idx])

        # NaN 체크
        if pd.isna(macd_val) or pd.isna(hist_val):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close_val,
                reasoning="MACD NaN: 계산 불가",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        price_low_lag = float(price_low.iloc[idx - _LAG])
        price_high_lag = float(price_high.iloc[idx - _LAG])
        macd_low_lag = float(macd_low.iloc[idx - _LAG])
        macd_high_lag = float(macd_high.iloc[idx - _LAG])

        if pd.isna(price_low_lag) or pd.isna(price_high_lag) or pd.isna(macd_low_lag) or pd.isna(macd_high_lag):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close_val,
                reasoning="rolling NaN: 계산 불가",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        info = (
            f"close={close_val:.4f}, macd={macd_val:.6f}, hist={hist_val:.6f}, "
            f"price_low_lag={price_low_lag:.4f}, macd_low_lag={macd_low_lag:.6f}"
        )

        # Bullish divergence: 가격 저점↓, MACD 저점↑
        bullish_div = close_val < price_low_lag and macd_val > macd_low_lag

        # Bearish divergence: 가격 고점↑, MACD 고점↓
        bearish_div = close_val > price_high_lag and macd_val < macd_high_lag

        if bullish_div:
            conf = Confidence.HIGH if hist_val > 0 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Bullish divergence: 가격 저점 하락, MACD 저점 상승. {info}",
                invalidation="가격이 신저점 경신 + MACD도 신저점 시 무효",
                bull_case="MACD 모멘텀 회복으로 상승 반전 기대",
                bear_case="추세 지속 시 추가 하락 가능",
            )

        if bearish_div:
            conf = Confidence.HIGH if hist_val < 0 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Bearish divergence: 가격 고점 상승, MACD 고점 하락. {info}",
                invalidation="가격 + MACD 모두 신고점 경신 시 무효",
                bull_case="강한 모멘텀 지속 시 상승 돌파 가능",
                bear_case="MACD 모멘텀 약화로 하락 반전 기대",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_val,
            reasoning=f"divergence 조건 미충족. {info}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
