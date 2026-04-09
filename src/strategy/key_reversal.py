"""
KeyReversalStrategy: Key Reversal Bar 패턴 감지.
- Bullish Key Reversal: new 20봉 저점 + close > prev_close → BUY
- Bearish Key Reversal: new 20봉 고점 + close < prev_close → SELL
- 추가 조건: volume > avg_vol * 1.5
- confidence: 52주 저점/고점 돌파 시 HIGH
- 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_LOOKBACK = 20
_VOL_LOOKBACK = 20
_VOL_MULT = 1.5
_YEARLY = 260


class KeyReversalStrategy(BaseStrategy):
    name = "key_reversal"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        signal_idx = len(df) - 2
        last = self._last(df)
        prev = df.iloc[signal_idx - 1]

        close = float(last["close"])
        low = float(last["low"])
        high = float(last["high"])
        volume = float(last["volume"])
        prev_close = float(prev["close"])

        # 볼륨 평균
        vol_window = df["volume"].iloc[max(0, signal_idx - _VOL_LOOKBACK):signal_idx]
        vol_avg = float(vol_window.mean()) if len(vol_window) > 0 else 1.0
        vol_ok = volume > vol_avg * _VOL_MULT

        # 20봉 저점/고점 (shift 1 = 신호 봉 직전 20개)
        low_window = df["low"].iloc[max(0, signal_idx - _LOOKBACK):signal_idx]
        high_window = df["high"].iloc[max(0, signal_idx - _LOOKBACK):signal_idx]
        low_20_min = float(low_window.min()) if len(low_window) > 0 else float("inf")
        high_20_max = float(high_window.max()) if len(high_window) > 0 else 0.0

        new_low_20 = low < low_20_min
        new_high_20 = high > high_20_max

        # Bullish / Bearish Key Reversal
        bullish_kr = new_low_20 and close > prev_close
        bearish_kr = new_high_20 and close < prev_close

        # 52주 저점/고점 (260봉)
        yearly_window_low = df["low"].iloc[max(0, signal_idx - _YEARLY):signal_idx]
        yearly_window_high = df["high"].iloc[max(0, signal_idx - _YEARLY):signal_idx]
        yearly_low = float(yearly_window_low.min()) if len(yearly_window_low) > 0 else float("inf")
        yearly_high = float(yearly_window_high.max()) if len(yearly_window_high) > 0 else 0.0

        info = (
            f"low={low:.4f} high={high:.4f} close={close:.4f} "
            f"prev_close={prev_close:.4f} vol_ratio={volume/vol_avg:.2f} "
            f"low20min={low_20_min:.4f} high20max={high_20_max:.4f}"
        )

        if bullish_kr and vol_ok:
            high_conf = low < yearly_low
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Bullish Key Reversal: {info}",
                invalidation=f"Close below today's low ({low:.4f})",
                bull_case=f"20봉 신저점 후 반등, {'52주 저점 돌파' if high_conf else '볼륨 확인'}",
                bear_case="단기 반등 실패 가능성",
            )

        if bearish_kr and vol_ok:
            high_conf = high > yearly_high
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Bearish Key Reversal: {info}",
                invalidation=f"Close above today's high ({high:.4f})",
                bull_case="단기 하락 실패 가능성",
                bear_case=f"20봉 신고점 후 반전, {'52주 고점 돌파' if high_conf else '볼륨 확인'}",
            )

        return self._hold(df, f"No key reversal: {info}", info, info)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        close = float(df.iloc[-2]["close"]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
