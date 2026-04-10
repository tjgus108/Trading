"""
AdaptiveRSIThresholdStrategy: 시장 레짐에 따라 RSI 임계값을 자동 조정하는 전략.
- RSI14 (EWM Wilder 방식)
- ADX EWM14 방식으로 레짐 판단
- Trending (ADX > 25): buy < 40, sell > 60
- Range (ADX <= 25): buy < 30, sell > 70
- BUY: RSI < buy_threshold AND RSI crosses above threshold (이전 봉보다 RSI 상승)
- SELL: RSI > sell_threshold AND RSI crosses below threshold (이전 봉보다 RSI 하락)
- confidence: RSI < 20 (trending BUY) or RSI > 80 (trending SELL) → HIGH
- 최소 데이터: 20행
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_RSI_PERIOD = 14
_ADX_PERIOD = 14


def _wilder_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta.clip(upper=0))
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def _calc_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]

    prev_high = high.shift(1)
    prev_low = low.shift(1)
    prev_close = close.shift(1)

    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)

    dm_plus = np.where(
        (high - prev_high) > (prev_low - low),
        np.maximum(high - prev_high, 0),
        0
    )
    dm_minus = np.where(
        (prev_low - low) > (high - prev_high),
        np.maximum(prev_low - low, 0),
        0
    )

    dm_plus_s = pd.Series(dm_plus, index=df.index, dtype=float)
    dm_minus_s = pd.Series(dm_minus, index=df.index, dtype=float)

    alpha = 1 / period
    atr_ewm = tr.ewm(alpha=alpha, adjust=False).mean()
    dmp_ewm = dm_plus_s.ewm(alpha=alpha, adjust=False).mean()
    dmm_ewm = dm_minus_s.ewm(alpha=alpha, adjust=False).mean()

    dip = 100 * dmp_ewm / atr_ewm.replace(0, 1e-10)
    dim = 100 * dmm_ewm / atr_ewm.replace(0, 1e-10)

    dx = 100 * (dip - dim).abs() / (dip + dim).replace(0, 1e-10)
    adx = dx.ewm(alpha=alpha, adjust=False).mean()
    return adx


class AdaptiveRSIThresholdStrategy(BaseStrategy):
    name = "adaptive_rsi_thresh"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        rsi = _wilder_rsi(df["close"], _RSI_PERIOD)
        adx = _calc_adx(df, _ADX_PERIOD)

        rsi_val = float(rsi.iloc[idx])
        rsi_prev = float(rsi.iloc[idx - 1])
        adx_val = float(adx.iloc[idx])

        if np.isnan(rsi_val) or np.isnan(adx_val):
            return self._hold(df, "RSI or ADX NaN — 데이터 부족")

        close = float(df["close"].iloc[idx])
        trending = adx_val > 25

        if trending:
            buy_thresh = 40.0
            sell_thresh = 60.0
        else:
            buy_thresh = 30.0
            sell_thresh = 70.0

        regime = "trending" if trending else "range"
        context = f"RSI={rsi_val:.2f} ADX={adx_val:.2f} regime={regime} buy<{buy_thresh} sell>{sell_thresh}"

        # BUY: RSI < buy_threshold AND RSI crosses above (rising)
        if rsi_val < buy_thresh and rsi_val > rsi_prev:
            if trending and rsi_val < 20:
                confidence = Confidence.HIGH
            else:
                confidence = Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"AdaptiveRSIThresh BUY: RSI={rsi_val:.2f}<{buy_thresh}(cross up), ADX={adx_val:.2f}({regime})",
                invalidation=f"RSI > {buy_thresh}",
                bull_case=context,
                bear_case=context,
            )

        # SELL: RSI > sell_threshold AND RSI crosses below (falling)
        if rsi_val > sell_thresh and rsi_val < rsi_prev:
            if trending and rsi_val > 80:
                confidence = Confidence.HIGH
            else:
                confidence = Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"AdaptiveRSIThresh SELL: RSI={rsi_val:.2f}>{sell_thresh}(cross down), ADX={adx_val:.2f}({regime})",
                invalidation=f"RSI < {sell_thresh}",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        idx = len(df) - 2
        close = float(df["close"].iloc[idx]) if len(df) >= 2 else 0.0
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
