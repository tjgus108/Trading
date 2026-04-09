"""
VW_MACD (Volume Weighted MACD) 전략.

vw_price = close * volume
vwema12 = EWM(vw_price, span=12) / EWM(volume, span=12)
vwema26 = EWM(vw_price, span=26) / EWM(volume, span=26)
vw_macd = vwema12 - vwema26
signal   = EWM(vw_macd, span=9)
histogram = vw_macd - signal

BUY:  histogram > 0 AND 이전봉 histogram < 0 (크로스)
SELL: histogram < 0 AND 이전봉 histogram > 0
confidence: HIGH if |histogram| > std(histogram, 20), MEDIUM 그 외
최소 데이터: 35행
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 35


def _compute_vwmacd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal_span: int = 9) -> pd.DataFrame:
    """VW_MACD, signal, histogram 계산."""
    vw_price = df["close"] * df["volume"]
    vol = df["volume"]

    vwema_fast = vw_price.ewm(span=fast, adjust=False).mean() / vol.ewm(span=fast, adjust=False).mean()
    vwema_slow = vw_price.ewm(span=slow, adjust=False).mean() / vol.ewm(span=slow, adjust=False).mean()

    vw_macd = vwema_fast - vwema_slow
    signal_line = vw_macd.ewm(span=signal_span, adjust=False).mean()
    histogram = vw_macd - signal_line

    return pd.DataFrame({
        "vw_macd": vw_macd.values,
        "signal": signal_line.values,
        "histogram": histogram.values,
    }, index=df.index)


class VWMACDStrategy(BaseStrategy):
    name = "vw_macd"

    def __init__(self, fast: int = 12, slow: int = 26, signal_span: int = 9, hist_lookback: int = 20) -> None:
        self.fast = fast
        self.slow = slow
        self.signal_span = signal_span
        self.hist_lookback = hist_lookback

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: VW_MACD 계산을 위해 최소 35행 필요",
                invalidation="",
            )

        indicators = _compute_vwmacd(df, self.fast, self.slow, self.signal_span)

        last_hist = indicators["histogram"].iloc[-2]
        prev_hist = indicators["histogram"].iloc[-3]
        last_close = float(df["close"].iloc[-2])

        lookback = min(self.hist_lookback, len(indicators) - 2)
        hist_std = indicators["histogram"].iloc[-lookback - 2: -2].std()

        if np.isnan(last_hist) or np.isnan(prev_hist):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="VW_MACD 계산값 부족 (NaN)",
                invalidation="",
            )

        crossed_up = (prev_hist < 0) and (last_hist > 0)
        crossed_down = (prev_hist > 0) and (last_hist < 0)

        if hist_std > 0 and not np.isnan(hist_std):
            confidence = Confidence.HIGH if abs(last_hist) > hist_std else Confidence.MEDIUM
        else:
            confidence = Confidence.MEDIUM

        last_vwmacd = float(indicators["vw_macd"].iloc[-2])
        last_signal = float(indicators["signal"].iloc[-2])

        bull_case = f"histogram={last_hist:.6f} > 0, VW_MACD={last_vwmacd:.6f}, signal={last_signal:.6f}"
        bear_case = f"histogram={last_hist:.6f} < 0, VW_MACD={last_vwmacd:.6f}, signal={last_signal:.6f}"

        if crossed_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=(
                    f"VW_MACD histogram 상향 크로스 (0선 돌파). "
                    f"hist={last_hist:.6f}, std={hist_std:.6f}"
                ),
                invalidation="histogram < 0으로 재하향",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if crossed_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=(
                    f"VW_MACD histogram 하향 크로스 (0선 하향). "
                    f"hist={last_hist:.6f}, std={hist_std:.6f}"
                ),
                invalidation="histogram > 0으로 재상향",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=last_close,
            reasoning=(
                f"크로스 없음. histogram={last_hist:.6f} (prev={prev_hist:.6f}), "
                f"std={hist_std:.6f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
