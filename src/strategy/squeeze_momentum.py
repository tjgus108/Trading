"""
SqueezeMomentumStrategy: Lazybear's Squeeze Momentum.

로직:
  - BB: sma20 ± 2*std20
  - KC: ema20 ± 1.5*atr14 (rolling ATR)
  - squeeze_on = BB upper < KC upper AND BB lower > KC lower
  - momentum = close - (rolling(20,high).max() + rolling(20,low).min()) / 2 - sma20
  - momentum_ma = momentum.rolling(5).mean()
  - BUY:  NOT squeeze_on (이전 squeeze_on이었다가 해제) AND momentum > 0 AND momentum > momentum.shift(1)
  - SELL: NOT squeeze_on AND momentum < 0 AND momentum < momentum.shift(1)
  - confidence: HIGH if abs(momentum) > momentum.rolling(20).std() else MEDIUM
  - 최소 행: 30
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_BB_PERIOD = 20
_BB_MULT = 2.0
_KC_MULT = 1.5
_ATR_PERIOD = 14
_MOM_MA_PERIOD = 5
_MOM_STD_PERIOD = 20


def _calc_atr(df: pd.DataFrame, period: int = _ATR_PERIOD) -> pd.Series:
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period).mean()


def _calc_indicators(df: pd.DataFrame):
    close = df["close"]
    high = df["high"]
    low = df["low"]

    # Bollinger Bands
    sma20 = close.rolling(_BB_PERIOD).mean()
    std20 = close.rolling(_BB_PERIOD).std()
    bb_upper = sma20 + _BB_MULT * std20
    bb_lower = sma20 - _BB_MULT * std20

    # Keltner Channel
    ema20 = close.ewm(span=_BB_PERIOD, adjust=False).mean()
    atr14 = _calc_atr(df, _ATR_PERIOD)
    kc_upper = ema20 + _KC_MULT * atr14
    kc_lower = ema20 - _KC_MULT * atr14

    # Squeeze
    squeeze_on = (bb_upper < kc_upper) & (bb_lower > kc_lower)

    # Momentum = close - (rolling_high_max + rolling_low_min) / 2 - sma20
    rolling_high = high.rolling(_BB_PERIOD).max()
    rolling_low = low.rolling(_BB_PERIOD).min()
    momentum = close - (rolling_high + rolling_low) / 2 - sma20

    # Momentum MA
    momentum_ma = momentum.rolling(_MOM_MA_PERIOD).mean()

    return squeeze_on, momentum, momentum_ma


class SqueezeMomentumStrategy(BaseStrategy):
    name = "squeeze_momentum"

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

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            if df is None:
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.LOW,
                    strategy=self.name,
                    entry_price=0.0,
                    reasoning="Insufficient data (minimum 30 rows required)",
                    invalidation="",
                )
            return self._hold(df, "Insufficient data (minimum 30 rows required)")

        # use completed candles only (exclude last in-progress candle)
        work = df.iloc[: len(df) - 1]
        idx = len(work) - 1   # current (last completed candle in work)
        prev_idx = idx - 1

        if prev_idx < 0:
            return self._hold(df, "Insufficient data (minimum 30 rows required)")

        squeeze_on, momentum, momentum_ma = _calc_indicators(work)

        sq_curr = bool(squeeze_on.iloc[idx])
        sq_prev = bool(squeeze_on.iloc[prev_idx])
        mom_curr = float(momentum.iloc[idx])
        mom_prev = float(momentum.iloc[prev_idx])

        if pd.isna(mom_curr) or pd.isna(mom_prev):
            return self._hold(df, "Insufficient data (minimum 30 rows required)")

        entry = float(work["close"].iloc[idx])

        # squeeze just released: prev was ON, curr is OFF
        squeeze_released = sq_prev and not sq_curr

        # confidence: HIGH if |momentum| > momentum.rolling(20).std()
        mom_std_series = momentum.rolling(_MOM_STD_PERIOD).std()
        mom_std = float(mom_std_series.iloc[idx])
        if pd.isna(mom_std) or mom_std == 0:
            mom_std = 0.0
        high_conf = mom_std > 0 and abs(mom_curr) > mom_std
        confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM

        context = (
            f"squeeze_on={sq_curr} prev_squeeze={sq_prev} "
            f"momentum={mom_curr:.4f} prev_momentum={mom_prev:.4f}"
        )

        # BUY: squeeze released AND momentum > 0 AND momentum > prev momentum
        if squeeze_released and mom_curr > 0 and mom_curr > mom_prev:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Squeeze 해제 + 양의 모멘텀 증가: "
                    f"momentum={mom_curr:.4f} > 0, momentum > prev({mom_prev:.4f})"
                ),
                invalidation="모멘텀 음전환 또는 squeeze 재진입",
                bull_case=context,
                bear_case=context,
            )

        # SELL: squeeze released AND momentum < 0 AND momentum < prev momentum
        if squeeze_released and mom_curr < 0 and mom_curr < mom_prev:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Squeeze 해제 + 음의 모멘텀 감소: "
                    f"momentum={mom_curr:.4f} < 0, momentum < prev({mom_prev:.4f})"
                ),
                invalidation="모멘텀 양전환 또는 squeeze 재진입",
                bull_case=context,
                bear_case=context,
            )

        sq_state = "ON" if sq_curr else "OFF"
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"Squeeze={sq_state}, momentum={mom_curr:.4f}, 신호 없음. {context}",
            invalidation="",
        )
