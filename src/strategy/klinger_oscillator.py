"""
KlingerOscillatorStrategy:
- BUY: KVO crosses above Signal AND KVO < 0
- SELL: KVO crosses below Signal AND KVO > 0
- Confidence: HIGH if |KVO| > KVO.rolling(20).std(), else MEDIUM
- 최소 70행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 70


class KlingerOscillatorStrategy(BaseStrategy):
    name = "klinger_oscillator"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for KlingerOscillator (need 70 rows)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        typical = (df["high"] + df["low"] + df["close"]) / 3
        trend = typical.diff()
        trend_dir = trend.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
        vf = df["volume"] * trend_dir

        ema34 = vf.ewm(span=34, adjust=False).mean()
        ema55 = vf.ewm(span=55, adjust=False).mean()
        kvo = ema34 - ema55
        signal_line = kvo.ewm(span=13, adjust=False).mean()

        idx = len(df) - 2
        kvo_now = float(kvo.iloc[idx])
        kvo_prev = float(kvo.iloc[idx - 1])
        sig_now = float(signal_line.iloc[idx])
        sig_prev = float(signal_line.iloc[idx - 1])

        if any(pd.isna(v) for v in [kvo_now, kvo_prev, sig_now, sig_prev]):
            entry = float(df["close"].iloc[idx])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="KlingerOscillator: NaN 값 존재",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        kvo_std = float(kvo.rolling(20).std().iloc[idx])
        conf = Confidence.HIGH if abs(kvo_now) > kvo_std else Confidence.MEDIUM
        entry = float(df["close"].iloc[idx])

        # BUY: kvo crosses above signal AND kvo < 0
        if kvo_prev < sig_prev and kvo_now >= sig_now and kvo_now < 0:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"KVO 상향 크로스 (음수 구간): KVO {kvo_prev:.2f} → {kvo_now:.2f}, "
                    f"Signal {sig_prev:.2f} → {sig_now:.2f}"
                ),
                invalidation="KVO가 다시 Signal 하향 크로스 시",
                bull_case=f"KVO {kvo_now:.2f} < 0 구간에서 상향 전환, 반등 가능성",
                bear_case="단기 반등일 수 있음",
            )

        # SELL: kvo crosses below signal AND kvo > 0
        if kvo_prev > sig_prev and kvo_now <= sig_now and kvo_now > 0:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"KVO 하향 크로스 (양수 구간): KVO {kvo_prev:.2f} → {kvo_now:.2f}, "
                    f"Signal {sig_prev:.2f} → {sig_now:.2f}"
                ),
                invalidation="KVO가 다시 Signal 상향 크로스 시",
                bull_case="단기 반등일 수 있음",
                bear_case=f"KVO {kvo_now:.2f} > 0 구간에서 하향 전환, 하락 가능성",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"KlingerOscillator 중립: KVO={kvo_now:.2f}, Signal={sig_now:.2f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
