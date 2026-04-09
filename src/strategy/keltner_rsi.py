"""
KeltnerRSIStrategy: Keltner Channel + RSI14 기반 평균 회귀 전략.

로직:
  - Keltner Channel: EMA20 ± 2*ATR14
  - ATR: max(high-low, |high-prev_close|, |low-prev_close|), 14기간 EWM
  - RSI: ewm 방식 (gains/losses ewm span=14)
  - BUY:  close < lower_band AND RSI14 < 35
  - SELL: close > upper_band AND RSI14 > 65
  - confidence: RSI < 25 or RSI > 75 → HIGH, 그 외 MEDIUM
  - 최소 행: 25
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_EMA_PERIOD = 20
_ATR_PERIOD = 14
_ATR_MULT = 2.0
_RSI_BUY = 35
_RSI_SELL = 65
_RSI_HIGH_BUY = 25
_RSI_HIGH_SELL = 75


def _calc_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()


def _calc_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    diff = close.diff()
    gains = diff.clip(lower=0)
    losses = (-diff).clip(lower=0)
    avg_gain = gains.ewm(span=period, adjust=False).mean()
    avg_loss = losses.ewm(span=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    return 100 - 100 / (1 + rs)


class KeltnerRSIStrategy(BaseStrategy):
    name = "keltner_rsi"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = float(last["close"])

        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="데이터 부족 (최소 25행 필요)",
                invalidation="N/A",
            )

        # 완성 캔들만 사용 (마지막 진행 중 캔들 제외)
        work = df.iloc[: len(df) - 1]

        ema20 = float(work["close"].ewm(span=_EMA_PERIOD, adjust=False).mean().iloc[-1])
        atr14 = float(_calc_atr(work, _ATR_PERIOD).iloc[-1])
        rsi14 = float(_calc_rsi(work["close"], _ATR_PERIOD).iloc[-1])

        upper_band = ema20 + _ATR_MULT * atr14
        lower_band = ema20 - _ATR_MULT * atr14
        close = float(work["close"].iloc[-1])

        context = (
            f"close={close:.2f} ema20={ema20:.2f} "
            f"upper={upper_band:.2f} lower={lower_band:.2f} "
            f"atr14={atr14:.4f} rsi14={rsi14:.1f}"
        )

        if close < lower_band and rsi14 < _RSI_BUY:
            confidence = Confidence.HIGH if rsi14 < _RSI_HIGH_BUY else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Keltner 하단 이탈 + 과매도: "
                    f"close({close:.2f}) < lower({lower_band:.2f}), "
                    f"RSI={rsi14:.1f} < {_RSI_BUY}"
                ),
                invalidation=f"close가 lower band({lower_band:.2f}) 위로 복귀 시 무효",
                bull_case=context,
                bear_case=context,
            )

        if close > upper_band and rsi14 > _RSI_SELL:
            confidence = Confidence.HIGH if rsi14 > _RSI_HIGH_SELL else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Keltner 상단 돌파 + 과매수: "
                    f"close({close:.2f}) > upper({upper_band:.2f}), "
                    f"RSI={rsi14:.1f} > {_RSI_SELL}"
                ),
                invalidation=f"close가 upper band({upper_band:.2f}) 아래로 복귀 시 무효",
                bull_case=context,
                bear_case=context,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"Keltner+RSI 조건 미충족 (HOLD). {context}",
            invalidation="N/A",
        )
