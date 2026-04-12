"""
Volume Breakout 전략 (개선):
- ATR 필터: 변동성이 중간 정도일 때만 진입
- 추세 필터: EMA50 기준 추세 방향 확인
- Volume Spike: 1.8x (기존 유지)
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 50  # EMA50 필요
_VOL_LOOKBACK = 20
_SPIKE_MULT = 1.8
_HIGH_CONF_MULT = 2.5
_ATR_LOW = 0.8  # ATR 최소 (과도하게 낮은 변동성 필터)
_ATR_HIGH = 3.0  # ATR 최대 (과도하게 높은 변동성 필터)


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
        ema50 = float(last.get("ema50", close))  # EMA50 없으면 close 사용
        atr14 = float(last.get("atr14", 0))

        avg_vol = float(df["volume"].iloc[-_VOL_LOOKBACK - 2 : -2].mean())
        spike = volume > avg_vol * _SPIKE_MULT
        bull_candle = close > open_
        bear_candle = close < open_
        above_ema = close > ema20
        below_ema = close < ema20
        
        # ATR 필터: 변동성이 너무 낮거나 높으면 스킵
        atr_valid = _ATR_LOW <= atr14 <= _ATR_HIGH if atr14 > 0 else True
        
        # 추세 필터: EMA20 vs EMA50
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
                invalidation=f"Close below EMA20 ({ema20:.2f}) or ATR out of range",
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
                invalidation=f"Close above EMA20 ({ema20:.2f}) or ATR out of range",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(df, f"No signal: vol={volume:.0f} avg={avg_vol:.0f} spike={spike} atr_valid={atr_valid} trend_aligned={'up' if uptrend else 'down'}", bull_case, bear_case)

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
