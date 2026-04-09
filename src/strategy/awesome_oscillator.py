"""
Awesome Oscillator 전략:
- Midpoint = (high + low) / 2
- AO = SMA(Midpoint, 5) - SMA(Midpoint, 34)
- Zero Cross BUY: 이전 AO <= 0, 현재 AO > 0
- Zero Cross SELL: 이전 AO >= 0, 현재 AO < 0
- Bull Saucer: AO > 0 AND 현재 AO > 이전 AND 이전 AO < 이전이전 (오목)
- Bear Saucer: AO < 0 AND 현재 AO < 이전 AND 이전 AO > 이전이전
- BUY: Zero Cross 또는 Bull Saucer
- SELL: Zero Cross 또는 Bear Saucer (Zero Cross 우선)
- confidence: HIGH if Zero Cross, MEDIUM if Saucer only
- 최소 40행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 40
_FAST = 5
_SLOW = 34


class AwesomeOscillatorStrategy(BaseStrategy):
    name = "awesome_oscillator"

    def generate(self, df: pd.DataFrame) -> Signal:
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

        idx = len(df) - 2

        midpoint = (df["high"] + df["low"]) / 2
        ao = midpoint.rolling(_FAST).mean() - midpoint.rolling(_SLOW).mean()

        ao_now = float(ao.iloc[idx])
        ao_prev = float(ao.iloc[idx - 1])
        ao_prev2 = float(ao.iloc[idx - 2])

        entry = float(df["close"].iloc[idx])

        # Zero Cross 판별
        zero_cross_buy = ao_prev <= 0 and ao_now > 0
        zero_cross_sell = ao_prev >= 0 and ao_now < 0

        # Saucer 판별
        bull_saucer = ao_now > 0 and ao_now > ao_prev and ao_prev < ao_prev2
        bear_saucer = ao_now < 0 and ao_now < ao_prev and ao_prev > ao_prev2

        # BUY: Zero Cross 우선
        if zero_cross_buy:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"AO Zero Cross 상향: AO {ao_prev:.4f} → {ao_now:.4f} (0선 돌파)",
                invalidation="AO가 0선 아래로 재하락 시",
                bull_case=f"AO {ao_now:.4f}, 강한 상승 모멘텀",
                bear_case="거짓 돌파 가능성",
            )

        # BUY: Bull Saucer
        if bull_saucer:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"AO Bull Saucer: AO {ao_prev2:.4f} → {ao_prev:.4f} → {ao_now:.4f} (AO > 0, 오목 후 상승)",
                invalidation="AO가 0선 아래로 하락 시",
                bull_case=f"AO {ao_now:.4f}, 양수 구간 반등",
                bear_case="모멘텀 약화 가능",
            )

        # SELL: Zero Cross 우선
        if zero_cross_sell:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"AO Zero Cross 하향: AO {ao_prev:.4f} → {ao_now:.4f} (0선 하향 돌파)",
                invalidation="AO가 0선 위로 재상승 시",
                bull_case="단순 조정일 수 있음",
                bear_case=f"AO {ao_now:.4f}, 강한 하락 모멘텀",
            )

        # SELL: Bear Saucer
        if bear_saucer:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"AO Bear Saucer: AO {ao_prev2:.4f} → {ao_prev:.4f} → {ao_now:.4f} (AO < 0, 오목 후 하락)",
                invalidation="AO가 0선 위로 상승 시",
                bull_case="단순 조정일 수 있음",
                bear_case=f"AO {ao_now:.4f}, 음수 구간 추가 하락",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"AO 중립: AO {ao_now:.4f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
