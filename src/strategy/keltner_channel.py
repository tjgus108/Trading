"""
Keltner Channel 변동성 돌파 전략:
- Middle = EMA(close, 20)
- ATR14 = df["atr14"] 컬럼 직접 사용
- Upper = Middle + 2.0 * ATR14
- Lower = Middle - 2.0 * ATR14
- BUY:  close < Lower AND rsi14 < 40
- SELL: close > Upper AND rsi14 > 60
- HOLD: 그 외
- confidence: HIGH(rsi<30 or rsi>70), MEDIUM otherwise
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_EMA_PERIOD = 20
_ATR_MULT = 2.0
_RSI_BUY_THRESH = 40
_RSI_SELL_THRESH = 60
_RSI_HIGH_BUY = 30
_RSI_HIGH_SELL = 70


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


class KeltnerChannelStrategy(BaseStrategy):
    name = "keltner_channel"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        close = float(last["close"])
        atr14 = float(last["atr14"])

        # EMA20 계산 (완성 캔들만 사용)
        close_series = df["close"].iloc[: len(df) - 1]
        ema = float(close_series.ewm(span=_EMA_PERIOD, adjust=False).mean().iloc[-1])

        upper_band = ema + _ATR_MULT * atr14
        lower_band = ema - _ATR_MULT * atr14

        # RSI14 계산
        rsi_series = _rsi(close_series)
        rsi = float(rsi_series.iloc[-1])

        context = (
            f"close={close:.2f} ema={ema:.2f} "
            f"upper={upper_band:.2f} lower={lower_band:.2f} "
            f"atr14={atr14:.2f} rsi14={rsi:.1f}"
        )

        if close < lower_band and rsi < _RSI_BUY_THRESH:
            confidence = Confidence.HIGH if rsi < _RSI_HIGH_BUY else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Keltner Channel 하단 돌파 + 과매도: "
                    f"close({close:.2f})<lower({lower_band:.2f}), "
                    f"rsi14={rsi:.1f}<{_RSI_BUY_THRESH}"
                ),
                invalidation=f"Close rebounds above lower band ({lower_band:.2f})",
                bull_case=context,
                bear_case=context,
            )

        if close > upper_band and rsi > _RSI_SELL_THRESH:
            confidence = Confidence.HIGH if rsi > _RSI_HIGH_SELL else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Keltner Channel 상단 돌파 + 과매수: "
                    f"close({close:.2f})>upper({upper_band:.2f}), "
                    f"rsi14={rsi:.1f}>{_RSI_SELL_THRESH}"
                ),
                invalidation=f"Close pulls back below upper band ({upper_band:.2f})",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(
            df,
            f"No signal: close={close:.2f} lower={lower_band:.2f} upper={upper_band:.2f} rsi14={rsi:.1f}",
            context,
            context,
        )

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
