"""
Volume Breakout 전략 (개선 v2):
- ATR 필터: 극단적 변동성만 필터 (범위 확대)
- 추세 필터: EMA20 > EMA50 (상승) / EMA20 < EMA50 (하강)
- Volume Spike: 1.5x (더 공격적, 거래 빈도 증가)
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 50  # EMA50 필요
_VOL_LOOKBACK = 20
_SPIKE_MULT = 1.5  # 1.8 → 1.5 (더 공격적)
_HIGH_CONF_MULT = 2.2  # 2.5 → 2.2
_ATR_LOW = 0.3  # ATR 최소 (극단적으로 낮은 경우만)
_ATR_HIGH = 5.0  # ATR 최대 (극단적으로 높은 경우만)


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
        ema50 = float(last.get("ema50", close))
        atr14 = float(last.get("atr14", 1.0))

        avg_vol = float(df["volume"].iloc[-_VOL_LOOKBACK - 2 : -2].mean())
        spike = volume > avg_vol * _SPIKE_MULT
        bull_candle = close > open_
        bear_candle = close < open_
        above_ema = close > ema20
        below_ema = close < ema20
        
        # ATR 필터: 매우 극단적인 경우만 필터
        atr_valid = _ATR_LOW <= atr14 <= _ATR_HIGH
        
        # 추세 필터
        uptrend = ema20 > ema50
        downtrend = ema20 < ema50

        bull_case = f"close={close:.2f} open={open_:.2f} ema20={ema20:.2f} ema50={ema50:.2f} vol={volume:.0f} atr={atr14:.2f}"
        bear_case = bull_case

        # BUY: spike + 양봉 + close>ema20 + ATR 유효 + 상승 추세
        if spike and bull_candle and above_ema and atr_valid and uptrend:
            confidence = Confidence.HIGH if volume > avg_vol * _HIGH_CONF_MULT else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Volume breakout 상승: vol={volume:.0f}>avg*{_SPIKE_MULT}({avg_vol*_SPIKE_MULT:.0f}), 양봉, close({close:.2f})>ema20({ema20:.2f}), uptrend, atr={atr14:.2f}",
                invalidation=f"Close below EMA20 ({ema20:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: spike + 음봉 + close<ema20 + ATR 유효 + 하락 추세
        if spike and bear_candle and below_ema and atr_valid and downtrend:
            confidence = Confidence.HIGH if volume > avg_vol * _HIGH_CONF_MULT else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Volume breakout 하락: vol={volume:.0f}>avg*{_SPIKE_MULT}({avg_vol*_SPIKE_MULT:.0f}), 음봉, close({close:.2f})<ema20({ema20:.2f}), downtrend, atr={atr14:.2f}",
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
