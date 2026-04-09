"""
APOStrategy (Absolute Price Oscillator):
- MACD의 절대값 버전
- 계산:
  - EMA10 = EMA(close, 10)
  - EMA20 = EMA(close, 20)
  - APO = EMA10 - EMA20 (절대 차이, %가 아님)
  - Signal = EMA(APO, 9)
- BUY:  APO > 0 AND APO 상향 크로스 Signal (이전 APO <= Signal, 현재 APO > Signal)
- SELL: APO < 0 AND APO 하향 크로스 Signal (이전 APO >= Signal, 현재 APO < Signal)
- confidence: HIGH if |APO / close| > 0.005, MEDIUM otherwise
- 최소 데이터: 30행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


def _calc_apo(df: pd.DataFrame):
    """idx = len(df) - 2 기준 apo_now, apo_prev, signal_now, signal_prev 계산."""
    idx = len(df) - 2

    ema10 = df["close"].ewm(span=10, adjust=False).mean()
    ema20 = df["close"].ewm(span=20, adjust=False).mean()
    apo = ema10 - ema20
    signal = apo.ewm(span=9, adjust=False).mean()

    apo_now = float(apo.iloc[idx])
    apo_prev = float(apo.iloc[idx - 1])
    signal_now = float(signal.iloc[idx])
    signal_prev = float(signal.iloc[idx - 1])

    return apo_now, apo_prev, signal_now, signal_prev


class APOStrategy(BaseStrategy):
    name = "apo"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-2]),
                reasoning=f"데이터 부족: {len(df)} < {_MIN_ROWS}",
                invalidation="데이터 충분 시 재평가",
            )

        apo_now, apo_prev, signal_now, signal_prev = _calc_apo(df)
        entry = float(df["close"].iloc[-2])
        close_now = float(df["close"].iloc[len(df) - 2])

        bull_cross = apo_prev <= signal_prev and apo_now > signal_now
        bear_cross = apo_prev >= signal_prev and apo_now < signal_now

        separation = abs(apo_now / (close_now + 1e-10))

        is_buy = apo_now > 0 and bull_cross
        is_sell = apo_now < 0 and bear_cross

        if is_buy:
            confidence = Confidence.HIGH if separation > 0.005 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"APO({apo_now:.4f}) > 0, Signal 상향 크로스 "
                    f"(이전 APO={apo_prev:.4f} <= Signal={signal_prev:.4f}), "
                    f"이격={separation*100:.3f}%"
                ),
                invalidation="APO가 0 하향 이탈 또는 Signal 하향 크로스 시",
                bull_case=f"APO Signal 상향 돌파, EMA10 > EMA20 확인, 이격={separation*100:.3f}%",
                bear_case="APO 반전 시 매도 전환 가능",
            )

        if is_sell:
            confidence = Confidence.HIGH if separation > 0.005 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"APO({apo_now:.4f}) < 0, Signal 하향 크로스 "
                    f"(이전 APO={apo_prev:.4f} >= Signal={signal_prev:.4f}), "
                    f"이격={separation*100:.3f}%"
                ),
                invalidation="APO가 0 상향 돌파 또는 Signal 상향 크로스 시",
                bull_case="APO 소진 후 반등 가능",
                bear_case=f"APO Signal 하향 돌파, EMA10 < EMA20 확인, 이격={separation*100:.3f}%",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"APO={apo_now:.4f}, Signal={signal_now:.4f} — 조건 미충족 "
                f"(bull_cross={bull_cross}, bear_cross={bear_cross})"
            ),
            invalidation="APO 크로스 신호 발생 시 재평가",
        )
