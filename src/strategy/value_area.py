"""
ValueArea 전략 (개선):
- VWAP 기반 Value Area(VA) 이탈 후 재진입 시 매매
- 개선: 추세 필터 + 거래량 확인 + VA 간격 확인 (false signals 감소)
- BUY:  prev_close < va_low AND curr_close > va_low AND trend_up (ema20>ema50) AND vol_ok
- SELL: prev_close > va_high AND curr_close < va_high AND trend_down (ema20<ema50) AND vol_ok
- confidence: HIGH if breach is significant (3σ+) + volume spike + trend
- 최소 데이터: 55행 (20 기간 EMA + 20 기간 volume 필요)
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 55
_VA_PERIOD = 20
_VA_MULT = 0.7
_HIGH_CONF_MULT = 0.3
_EMA_SHORT = 20
_EMA_LONG = 50
_MIN_BREACH = 1.5  # 최소 breach width: std * 1.5


class ValueAreaStrategy(BaseStrategy):
    name = "value_area"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold_safe(df, f"Insufficient data for ValueArea (need {_MIN_ROWS} rows)")

        close = df["close"]
        volume = df["volume"]

        # VWAP + Value Area
        vwap = (close * volume).rolling(_VA_PERIOD).sum() / volume.rolling(_VA_PERIOD).sum()
        std = close.rolling(_VA_PERIOD).std()
        va_high = vwap + std * _VA_MULT
        va_low = vwap - std * _VA_MULT

        # Trend filters: EMA20 vs EMA50
        ema20 = close.ewm(span=_EMA_SHORT, adjust=False).mean()
        ema50 = close.ewm(span=_EMA_LONG, adjust=False).mean()

        # Volume filter
        vol_ma = volume.rolling(20).mean()

        idx = len(df) - 2

        # NaN guard
        if idx < 1:
            return self._hold_safe(df, "Insufficient data for ValueArea (idx < 1)")

        for val, label in [
            (vwap.iloc[idx], "vwap"),
            (std.iloc[idx], "std"),
            (vwap.iloc[idx - 1], "prev_vwap"),
            (std.iloc[idx - 1], "prev_std"),
            (ema20.iloc[idx], "ema20"),
            (ema50.iloc[idx], "ema50"),
            (vol_ma.iloc[idx], "vol_ma"),
        ]:
            if pd.isna(val):
                return self._hold_safe(df, f"Insufficient data for ValueArea ({label} is NaN)")

        curr_close = float(close.iloc[idx])
        prev_close = float(close.iloc[idx - 1])
        curr_vwap = float(vwap.iloc[idx])
        curr_std = float(std.iloc[idx])
        curr_va_high = float(va_high.iloc[idx])
        curr_va_low = float(va_low.iloc[idx])
        prev_va_high = float(va_high.iloc[idx - 1])
        prev_va_low = float(va_low.iloc[idx - 1])
        curr_ema20 = float(ema20.iloc[idx])
        curr_ema50 = float(ema50.iloc[idx])
        curr_vol = float(volume.iloc[idx])
        curr_vol_ma = float(vol_ma.iloc[idx])

        # Trend flags
        trend_up = curr_ema20 > curr_ema50
        trend_down = curr_ema20 < curr_ema50
        
        # Volume confirmation
        volume_ok = curr_vol > curr_vol_ma

        # Breach gap: how much price breached VA
        buy_breach_gap = curr_close - curr_va_low
        sell_breach_gap = curr_va_high - curr_close
        
        bull_ctx = f"close={curr_close:.2f} vwap={curr_vwap:.2f} va_low={curr_va_low:.2f} ema20={curr_ema20:.2f}"
        bear_ctx = f"close={curr_close:.2f} vwap={curr_vwap:.2f} va_high={curr_va_high:.2f} ema20={curr_ema20:.2f}"

        # BUY: VA 하단 재진입 + 추세 up + 거래량
        if prev_close < prev_va_low and curr_close > curr_va_low and trend_up and volume_ok:
            # HIGH confidence: 큰 breach + close near VWAP + strong volume
            conf = Confidence.MEDIUM
            if (buy_breach_gap > curr_std * _MIN_BREACH and 
                abs(curr_close - curr_vwap) < curr_std * _HIGH_CONF_MULT and
                curr_vol > curr_vol_ma * 1.3):
                conf = Confidence.HIGH

            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"VA 하단 재진입 (추세필터): prev_close({prev_close:.2f}) < va_low({prev_va_low:.2f}), "
                    f"curr_close({curr_close:.2f}) > va_low({curr_va_low:.2f}), "
                    f"ema20({curr_ema20:.2f}) > ema50({curr_ema50:.2f}) — 상승 재진입"
                ),
                invalidation=f"Close falls below va_low ({curr_va_low:.2f}) or EMA20 < EMA50",
                bull_case=bull_ctx,
                bear_case=bear_ctx,
            )

        # SELL: VA 상단 재진입 + 추세 down + 거래량
        if prev_close > prev_va_high and curr_close < curr_va_high and trend_down and volume_ok:
            # HIGH confidence: 큰 breach + close near VWAP + strong volume
            conf = Confidence.MEDIUM
            if (sell_breach_gap > curr_std * _MIN_BREACH and 
                abs(curr_close - curr_vwap) < curr_std * _HIGH_CONF_MULT and
                curr_vol > curr_vol_ma * 1.3):
                conf = Confidence.HIGH

            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"VA 상단 재진입 (추세필터): prev_close({prev_close:.2f}) > va_high({prev_va_high:.2f}), "
                    f"curr_close({curr_close:.2f}) < va_high({curr_va_high:.2f}), "
                    f"ema20({curr_ema20:.2f}) < ema50({curr_ema50:.2f}) — 하락 재진입"
                ),
                invalidation=f"Close rises above va_high ({curr_va_high:.2f}) or EMA20 > EMA50",
                bull_case=bull_ctx,
                bear_case=bear_ctx,
            )

        return self._hold_safe(
            df,
            f"No signal: buy_cond={prev_close < prev_va_low and curr_close > curr_va_low and trend_up and volume_ok}, "
            f"sell_cond={prev_close > prev_va_high and curr_close < curr_va_high and trend_down and volume_ok}",
        )

    def _hold_safe(self, df: Optional[pd.DataFrame], reason: str) -> Signal:
        if df is None or len(df) < 2:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=reason,
                invalidation="",
            )
        idx = len(df) - 2
        close = float(df["close"].iloc[idx])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
        )
