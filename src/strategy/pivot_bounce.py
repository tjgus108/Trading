"""
PivotBounce 전략:
- Daily Pivot (표준 피봇) 레벨 계산 후, 지지(S1/S2)에서의 반등 또는 저항(R1/R2)에서의 반전을 포착.
- "전일" 기준: prev_high = high.iloc[-26:-20].max(), prev_low = low.iloc[-26:-20].min(), prev_close = close.iloc[-21]
- BUY:  close가 S1 or S2 ±0.3% 범위 내 AND close > prev_close
- SELL: close가 R1 or R2 ±0.3% 범위 내 AND close < prev_close
- confidence: S2/R2 레벨 터치 → HIGH, S1/R1 → MEDIUM
- 최소 행: 30
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_BAND = 0.003  # ±0.3%


def _near(price: float, level: float) -> bool:
    """price가 level의 ±_BAND 범위 내인지 확인."""
    if abs(level) < 1e-10:
        return False
    return abs(price - level) / abs(level) <= _BAND


class PivotBounceStrategy(BaseStrategy):
    name = "pivot_bounce"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, f"데이터 부족: {len(df)} < {_MIN_ROWS}")

        last = self._last(df)  # df.iloc[-2]
        close = float(last["close"])

        # 전일 기준 고/저/종가
        prev_high = float(df["high"].iloc[-26:-20].max())
        prev_low = float(df["low"].iloc[-26:-20].min())
        prev_close = float(df["close"].iloc[-21])

        # 피봇 계산
        p = (prev_high + prev_low + prev_close) / 3.0
        r1 = 2.0 * p - prev_low
        r2 = p + (prev_high - prev_low)
        s1 = 2.0 * p - prev_high
        s2 = p - (prev_high - prev_low)

        context = (
            f"close={close:.4f} P={p:.4f} "
            f"S1={s1:.4f} S2={s2:.4f} R1={r1:.4f} R2={r2:.4f} "
            f"prev_close={prev_close:.4f}"
        )

        # BUY 조건: S1 또는 S2 근방 AND 반등 확인
        near_s2 = _near(close, s2)
        near_s1 = _near(close, s1)
        if (near_s1 or near_s2) and close > prev_close:
            conf = Confidence.HIGH if near_s2 else Confidence.MEDIUM
            level_hit = f"S2={s2:.4f}" if near_s2 else f"S1={s1:.4f}"
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Pivot 지지 반등: close ≈ {level_hit} (±0.3%), "
                    f"close={close:.4f} > prev_close={prev_close:.4f}. {context}"
                ),
                invalidation=f"close < {level_hit} 하향 이탈 시",
                bull_case=f"{level_hit} 지지 반등 기대",
                bear_case=f"지지 이탈 시 추가 하락",
            )

        # SELL 조건: R1 또는 R2 근방 AND 반전 확인
        near_r2 = _near(close, r2)
        near_r1 = _near(close, r1)
        if (near_r1 or near_r2) and close < prev_close:
            conf = Confidence.HIGH if near_r2 else Confidence.MEDIUM
            level_hit = f"R2={r2:.4f}" if near_r2 else f"R1={r1:.4f}"
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Pivot 저항 반전: close ≈ {level_hit} (±0.3%), "
                    f"close={close:.4f} < prev_close={prev_close:.4f}. {context}"
                ),
                invalidation=f"close > {level_hit} 상향 돌파 시",
                bull_case=f"저항 돌파 시 추가 상승",
                bear_case=f"{level_hit} 저항 반락 기대",
            )

        return self._hold(df, f"No Pivot Bounce signal: {context}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        try:
            price = float(self._last(df)["close"])
        except Exception:
            price = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
        )
