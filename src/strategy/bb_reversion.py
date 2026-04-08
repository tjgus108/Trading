"""
Bollinger Band Mean Reversion 전략:
- BB 직접 계산 (period=20, std=2.0)
- BUY:  close < lower_band AND rsi14 < 40 (하단 터치 + 과매도 → 반등 기대)
- SELL: close > upper_band AND rsi14 > 60 (상단 터치 + 과매수 → 하락 기대)
- HOLD: 그 외
- confidence: HIGH(rsi<30 or rsi>70), MEDIUM(rsi<40 or rsi>60)
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_BB_PERIOD = 20
_BB_STD = 2.0
_RSI_BUY_THRESH = 40
_RSI_SELL_THRESH = 60
_RSI_HIGH_BUY = 30
_RSI_HIGH_SELL = 70


class BBReversionStrategy(BaseStrategy):
    name = "bb_reversion"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        close = float(last["close"])
        rsi = float(last["rsi14"])

        # Bollinger Band 계산 (마지막 완성 캔들 기준 BB_PERIOD 윈도우)
        close_series = df["close"].iloc[: len(df) - 1]  # 진행 중 캔들 제외
        rolling = close_series.rolling(_BB_PERIOD)
        mid = float(rolling.mean().iloc[-1])
        std = float(rolling.std(ddof=1).iloc[-1])
        upper_band = mid + _BB_STD * std
        lower_band = mid - _BB_STD * std

        context = (
            f"close={close:.2f} lower={lower_band:.2f} upper={upper_band:.2f} "
            f"mid={mid:.2f} rsi14={rsi:.1f}"
        )

        if close < lower_band and rsi < _RSI_BUY_THRESH:
            confidence = Confidence.HIGH if rsi < _RSI_HIGH_BUY else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"BB 하단 터치 + 과매도: close({close:.2f})<lower({lower_band:.2f}), "
                    f"rsi14={rsi:.1f}<{_RSI_BUY_THRESH}"
                ),
                invalidation=f"Close below lower band without recovery ({lower_band:.2f})",
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
                    f"BB 상단 터치 + 과매수: close({close:.2f})>upper({upper_band:.2f}), "
                    f"rsi14={rsi:.1f}>{_RSI_SELL_THRESH}"
                ),
                invalidation=f"Close above upper band without reversal ({upper_band:.2f})",
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
