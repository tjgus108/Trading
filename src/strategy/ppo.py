"""
PPOStrategy: Percentage Price Oscillator 기반 모멘텀 전략.
MACD의 % 버전으로, 절대값 대신 비율로 모멘텀을 측정한다.

계산:
  EMA12     = EMA(close, 12)
  EMA26     = EMA(close, 26)
  PPO       = (EMA12 - EMA26) / EMA26 * 100
  Signal    = EMA(PPO, 9)
  Histogram = PPO - Signal
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class PPOStrategy(BaseStrategy):
    """
    PPO 기반 모멘텀 전략.

    BUY  조건: PPO > Signal AND PPO > 0 AND Histogram 증가 (상향 크로스)
    SELL 조건: PPO < Signal AND PPO < 0 AND Histogram 감소 (하향 크로스)
    HOLD: 그 외

    confidence:
      HIGH   if |PPO| > 1.0 (1% 이상 이격)
      MEDIUM otherwise
    """

    name: str = "ppo"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 35:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="데이터 부족 (최소 35행 필요)",
                invalidation="충분한 데이터 확보 후 재실행",
            )

        ema12 = df["close"].ewm(span=12, adjust=False).mean()
        ema26 = df["close"].ewm(span=26, adjust=False).mean()
        ppo = (ema12 - ema26) / ema26 * 100
        signal_line = ppo.ewm(span=9, adjust=False).mean()
        histogram = ppo - signal_line

        idx = len(df) - 2
        ppo_now = float(ppo.iloc[idx])
        ppo_prev = float(ppo.iloc[idx - 1])
        sig_now = float(signal_line.iloc[idx])
        sig_prev = float(signal_line.iloc[idx - 1])
        hist_now = float(histogram.iloc[idx])
        hist_prev = float(histogram.iloc[idx - 1])

        entry_price = float(self._last(df)["close"])

        cross_up = ppo_prev <= sig_prev and ppo_now > sig_now
        cross_down = ppo_prev >= sig_prev and ppo_now < sig_now

        confidence = Confidence.HIGH if abs(ppo_now) > 1.0 else Confidence.MEDIUM

        if cross_up and ppo_now > 0 and hist_now > hist_prev:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"PPO 상향 크로스 (PPO={ppo_now:.3f} > Signal={sig_now:.3f}), "
                    f"PPO>0, 히스토그램 증가 ({hist_prev:.3f}→{hist_now:.3f})"
                ),
                invalidation=f"PPO가 Signal 아래로 하락 시 무효",
                bull_case=f"PPO 모멘텀 상승 중 ({ppo_now:.3f}%)",
                bear_case="PPO가 재하락 시 신호 취소",
            )

        if cross_down and ppo_now < 0 and hist_now < hist_prev:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"PPO 하향 크로스 (PPO={ppo_now:.3f} < Signal={sig_now:.3f}), "
                    f"PPO<0, 히스토그램 감소 ({hist_prev:.3f}→{hist_now:.3f})"
                ),
                invalidation=f"PPO가 Signal 위로 반등 시 무효",
                bull_case="PPO 반등 시 신호 취소",
                bear_case=f"PPO 모멘텀 하락 중 ({ppo_now:.3f}%)",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"명확한 크로스 없음 (PPO={ppo_now:.3f}, Signal={sig_now:.3f}, "
                f"Hist={hist_now:.3f})"
            ),
            invalidation="PPO 크로스 발생 시 재평가",
        )
