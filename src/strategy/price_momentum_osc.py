"""
PriceMomentumOscStrategy: PPO(Percentage Price Oscillator) — MACD의 퍼센트 버전.

계산:
  ema12      = close.ewm(span=12, adjust=False).mean()
  ema26      = close.ewm(span=26, adjust=False).mean()
  ppo        = 100 * (ema12 - ema26) / ema26
  ppo_signal = ppo.ewm(span=9, adjust=False).mean()
  ppo_hist   = ppo - ppo_signal

신호:
  BUY  : ppo_hist crosses above 0 (이전 < 0, 현재 >= 0) AND ppo < 0 (과매도 구간)
  SELL : ppo_hist crosses below 0 (이전 >= 0, 현재 < 0) AND ppo > 0
  HOLD : 그 외
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class PriceMomentumOscStrategy(BaseStrategy):
    """PPO 히스토그램 크로스 기반 모멘텀 전략."""

    name: str = "price_momentum_osc"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < 35:
            return self._hold(df, "Insufficient data (minimum 35 rows required)")

        close = df["close"]
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        ppo = 100 * (ema12 - ema26) / ema26
        ppo_signal = ppo.ewm(span=9, adjust=False).mean()
        ppo_hist = ppo - ppo_signal

        idx = len(df) - 2

        hist_now = float(ppo_hist.iloc[idx])
        hist_prev = float(ppo_hist.iloc[idx - 1]) if idx >= 1 else 0.0
        ppo_now = float(ppo.iloc[idx])
        entry_price = float(self._last(df)["close"])

        if any(pd.isna(v) for v in [hist_now, hist_prev, ppo_now]):
            return self._hold(df, "NaN detected in indicators")

        confidence = Confidence.HIGH if abs(ppo_now) > 2.0 else Confidence.MEDIUM

        cross_above = hist_prev < 0 and hist_now >= 0
        cross_below = hist_prev >= 0 and hist_now < 0

        if cross_above and ppo_now < 0:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"PPO 히스토그램 상향 크로스 0 (prev={hist_prev:.3f}→now={hist_now:.3f}), "
                    f"PPO={ppo_now:.3f} < 0 (과매도 구간)"
                ),
                invalidation="PPO 히스토그램이 다시 0 아래로 하락 시 무효",
                bull_case=f"과매도 구간에서 모멘텀 반전 (PPO={ppo_now:.3f}%)",
                bear_case="추세 약세 지속 가능성",
            )

        if cross_below and ppo_now > 0:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"PPO 히스토그램 하향 크로스 0 (prev={hist_prev:.3f}→now={hist_now:.3f}), "
                    f"PPO={ppo_now:.3f} > 0 (과매수 구간)"
                ),
                invalidation="PPO 히스토그램이 다시 0 위로 반등 시 무효",
                bull_case="추세 강세 지속 가능성",
                bear_case=f"과매수 구간에서 모멘텀 반전 (PPO={ppo_now:.3f}%)",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"크로스 없음 (ppo_hist={hist_now:.3f}, PPO={ppo_now:.3f})"
            ),
            invalidation="PPO 히스토그램 크로스 발생 시 재평가",
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
