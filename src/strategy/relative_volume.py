"""
RelativeVolumeStrategy (Fine-tuned Cycle 116):
- RVOL = current_volume / avg_volume_20
- VWAP = 거래량 가중 이동 평균 (rolling 20)
- RSI 14 필터 (과매수/과매도 제외)
- BUY: RVOL > 1.6 AND close > open AND close > VWAP AND RSI < 68
- SELL: RVOL > 1.6 AND close < open AND close < VWAP AND RSI > 32
- HIGH CONF: RVOL > 2.3 AND RSI extreme (< 45 or > 55) AND BB condition
- 최소 행: 25
"""

import pandas as pd
import numpy as np

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_VOL_LOOKBACK = 20
_RVOL_BUY_SELL = 1.6  # 최적점: 1.5->1.8의 중간
_RVOL_HIGH_CONF = 2.3
_BB_WINDOW = 20
_BB_STD = 2.0
_RSI_PERIOD = 14
_RSI_BUY_MAX = 68  # 약간의 과매수 허용
_RSI_SELL_MIN = 32  # 약간의 과매도 허용


class RelativeVolumeStrategy(BaseStrategy):
    name = "relative_volume"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold_signal(0.0, "Insufficient data")

        idx = len(df) - 2
        last = df.iloc[idx]
        close = float(last["close"])
        open_ = float(last["open"])
        volume = float(last["volume"])

        # RVOL: 신호 봉 직전 20봉 평균 (look-ahead 방지)
        vol_window = df["volume"].iloc[max(0, idx - _VOL_LOOKBACK):idx]
        avg_vol = float(vol_window.mean()) if len(vol_window) > 0 else 1.0
        rvol = volume / avg_vol if avg_vol > 0 else 0.0

        # VWAP (rolling 20, 신호 봉 포함)
        cv = (df["close"] * df["volume"]).rolling(_VOL_LOOKBACK).sum()
        v = df["volume"].rolling(_VOL_LOOKBACK).sum()
        vwap_series = cv / v
        vwap = float(vwap_series.iloc[idx])

        # 볼린저 밴드
        bb_mean = df["close"].rolling(_BB_WINDOW).mean()
        bb_std = df["close"].rolling(_BB_WINDOW).std()
        bb_upper = float(bb_mean.iloc[idx]) + _BB_STD * float(bb_std.iloc[idx])
        bb_lower = float(bb_mean.iloc[idx]) - _BB_STD * float(bb_std.iloc[idx])

        # RSI 14
        rsi = self._compute_rsi(df, idx, _RSI_PERIOD)

        bull_candle = close > open_
        bear_candle = close < open_

        info = (
            f"rvol={rvol:.2f} close={close:.2f} vwap={vwap:.2f} "
            f"bb_upper={bb_upper:.2f} bb_lower={bb_lower:.2f} rsi={rsi:.1f}"
        )

        # BUY: RVOL > 1.6 + 양봉 + close > VWAP + RSI < 68
        if (rvol > _RVOL_BUY_SELL and bull_candle and 
            close > vwap and rsi < _RSI_BUY_MAX):
            # HIGH CONF: RVOL > 2.3 AND (RSI < 45 OR RSI > 55) AND (close > BB upper)
            high_conf = (rvol > _RVOL_HIGH_CONF and 
                        (rsi < 45 or rsi > 55) and close > bb_upper)
            conf = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"RVOL+VWAP 돌파 (RSI {rsi:.1f}<{_RSI_BUY_MAX}): {info}",
                invalidation=f"Close ≤ VWAP or RSI ≥ {_RSI_BUY_MAX}",
                bull_case=info,
                bear_case=info,
            )

        # SELL: RVOL > 1.6 + 음봉 + close < VWAP + RSI > 32
        if (rvol > _RVOL_BUY_SELL and bear_candle and 
            close < vwap and rsi > _RSI_SELL_MIN):
            # HIGH CONF: RVOL > 2.3 AND (RSI < 45 OR RSI > 55) AND (close < BB lower)
            high_conf = (rvol > _RVOL_HIGH_CONF and 
                        (rsi < 45 or rsi > 55) and close < bb_lower)
            conf = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"RVOL+VWAP 이탈 (RSI {rsi:.1f}>{_RSI_SELL_MIN}): {info}",
                invalidation=f"Close ≥ VWAP or RSI ≤ {_RSI_SELL_MIN}",
                bull_case=info,
                bear_case=info,
            )

        return self._hold_signal(close, f"No signal (rvol={rvol:.2f}, rsi={rsi:.1f}): {info}", info, info)

    def _compute_rsi(self, df: pd.DataFrame, idx: int, period: int) -> float:
        """RSI 계산 (idx 지점)."""
        if idx < period + 1:
            return 50.0
        
        delta = df["close"].diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        
        rs = gain / loss.replace(0, np.nan)
        rsi_series = 100 - (100 / (1 + rs))
        
        try:
            rsi = float(rsi_series.iloc[idx])
            return rsi if not np.isnan(rsi) else 50.0
        except:
            return 50.0

    def _hold_signal(self, entry_price: float, reason: str,
                     bull_case: str = "", bear_case: str = "") -> Signal:
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
