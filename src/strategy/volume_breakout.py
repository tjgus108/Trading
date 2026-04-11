"""
Volume Breakout 전략 (개선):
- 스파이크 기준 2.0x → 1.8x 완화 (거래 빈도 증가)
- BUY: volume spike(>1.8x 평균) AND 양봉(close>open) AND close > ema20
- SELL: volume spike(>1.8x 평균) AND 음봉(close<open) AND close < ema20
- confidence: HIGH(volume > 2.5x 평균), MEDIUM(volume > 1.8x 평균)
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_VOL_LOOKBACK = 20
_SPIKE_MULT = 1.8  # 2.0 → 1.8 (거래 증가)
_HIGH_CONF_MULT = 2.5  # 3.0 → 2.5


class VolumeBreakoutStrategy(BaseStrategy):
    name = "volume_breakout"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        close = float(last["close"])
        open_ = float(last["open"])
        volume = float(last["volume"])
        ema20 = float(last["ema20"])

        avg_vol = float(df["volume"].iloc[-_VOL_LOOKBACK - 2 : -2].mean())
        spike = volume > avg_vol * _SPIKE_MULT
        bull_candle = close > open_
        bear_candle = close < open_
        above_ema = close > ema20
        below_ema = close < ema20

        bull_case = f"close={close:.2f} open={open_:.2f} ema20={ema20:.2f} vol={volume:.0f} avg_vol={avg_vol:.0f}"
        bear_case = bull_case

        if spike and bull_candle and above_ema:
            confidence = Confidence.HIGH if volume > avg_vol * _HIGH_CONF_MULT else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Volume breakout 상승: vol={volume:.0f} > avg*{_SPIKE_MULT}({avg_vol*_SPIKE_MULT:.0f}), 양봉, close({close:.2f})>ema20({ema20:.2f})",
                invalidation=f"Close below EMA20 ({ema20:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if spike and bear_candle and below_ema:
            confidence = Confidence.HIGH if volume > avg_vol * _HIGH_CONF_MULT else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Volume breakout 하락: vol={volume:.0f} > avg*{_SPIKE_MULT}({avg_vol*_SPIKE_MULT:.0f}), 음봉, close({close:.2f})<ema20({ema20:.2f})",
                invalidation=f"Close above EMA20 ({ema20:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(df, f"No signal: vol={volume:.0f} avg={avg_vol:.0f} spike={spike}", bull_case, bear_case)

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
