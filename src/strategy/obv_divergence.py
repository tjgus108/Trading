"""
OBV Divergence 전략:
- OBV = cumsum(volume * sign(close - prev_close))
- OBV_EMA = EWM(OBV, span=20)

- Bullish Divergence (BUY):
    close < close.shift(10) * 1.01 AND OBV_EMA > OBV_EMA.shift(10)
    → 가격 하락 + OBV 상승 (매집)

- Bearish Divergence (SELL):
    close > close.shift(10) * 0.99 AND OBV_EMA < OBV_EMA.shift(10)
    → 가격 상승 + OBV 하락 (분산)

- confidence: HIGH if OBV_EMA 변화 > std(OBV_EMA, 20), MEDIUM 그 외
- 최소 데이터: 25행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_OBV_EMA_SPAN = 20
_LOOKBACK = 10


class OBVDivergenceStrategy(BaseStrategy):
    name = "obv_divergence"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2  # 마지막 완성 캔들

        # OBV 계산
        close_diff = df["close"].diff()
        sign = close_diff.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
        obv = (df["volume"] * sign).cumsum()
        obv_ema = obv.ewm(span=_OBV_EMA_SPAN, adjust=False).mean()

        close_now = float(df["close"].iloc[idx])
        close_prev = float(df["close"].iloc[idx - _LOOKBACK])
        obv_ema_now = float(obv_ema.iloc[idx])
        obv_ema_prev = float(obv_ema.iloc[idx - _LOOKBACK])

        # OBV_EMA 변화 및 std
        obv_ema_change = abs(obv_ema_now - obv_ema_prev)
        window_std = obv_ema.iloc[max(0, idx - _OBV_EMA_SPAN + 1): idx + 1]
        obv_ema_std = float(window_std.std()) if len(window_std) > 1 else 0.0

        is_high_conf = obv_ema_std > 0 and obv_ema_change > obv_ema_std

        # Bullish divergence: 가격 하락 + OBV_EMA 상승
        bullish = (close_now < close_prev * 1.01) and (obv_ema_now > obv_ema_prev)

        # Bearish divergence: 가격 상승 + OBV_EMA 하락
        bearish = (close_now > close_prev * 0.99) and (obv_ema_now < obv_ema_prev)

        if bullish and not bearish:
            conf = Confidence.HIGH if is_high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"Bullish OBV Divergence: close={close_now:.2f} < {close_prev:.2f}*1.01, "
                    f"OBV_EMA={obv_ema_now:.0f} > {obv_ema_prev:.0f} (매집)"
                ),
                invalidation="close > 10봉 전 고점 또는 OBV_EMA 하락 전환",
                bull_case="가격 하락에도 OBV 상승 — 세력 매집 신호",
                bear_case="단순 가격 조정일 수 있음",
            )

        if bearish and not bullish:
            conf = Confidence.HIGH if is_high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"Bearish OBV Divergence: close={close_now:.2f} > {close_prev:.2f}*0.99, "
                    f"OBV_EMA={obv_ema_now:.0f} < {obv_ema_prev:.0f} (분산)"
                ),
                invalidation="close < 10봉 전 저점 또는 OBV_EMA 상승 전환",
                bull_case="단순 일시적 볼륨 감소일 수 있음",
                bear_case="가격 상승에도 OBV 하락 — 세력 분산 신호",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close_now,
            reasoning=(
                f"다이버전스 없음: close={close_now:.2f}, "
                f"OBV_EMA={obv_ema_now:.0f} vs {obv_ema_prev:.0f} (10봉 전)"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
