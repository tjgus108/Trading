"""
VolatilityClusterStrategy (improved):
- 원리: 변동성 군집 현상(GARCH-inspired) — 변동성이 낮은 시기 이후 급등락 예측
- 개선: Direction 확인 강화 + Momentum alignment (HOD/LOD 비교) + 신호 정제
- 지표:
  - returns = close.pct_change()
  - vol5 = returns.rolling(5).std()
  - vol20 = returns.rolling(20).std()
  - vol_ratio = vol5 / vol20
  - direction = close.rolling(10).apply(momentum)
  - momentum_strength = HOD ratio (High 대비 Close의 위치)
- 신호:
  - BUY: vol_ratio < 0.5 AND direction > 0 AND close > sma10
  - SELL: vol_ratio < 0.5 AND direction < 0 AND close < sma10
  - confidence: HIGH if vol_ratio < 0.3 + momentum_strong (close near HOD/LOD)
- 최소 데이터: 30행
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_VOL_SHORT = 5
_VOL_LONG = 20
_DIRECTION_PERIOD = 10
_LOW_VOL_THRESH = 0.5
_HIGH_CONF_THRESH = 0.3
_SMA_PERIOD = 10


class VolatilityClusterStrategy(BaseStrategy):
    name = "volatility_cluster"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            reason = (
                f"Insufficient data: need {_MIN_ROWS} rows, got {0 if df is None else len(df)}"
            )
            if df is None:
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.LOW,
                    strategy=self.name,
                    entry_price=0.0,
                    reasoning=reason,
                    invalidation="",
                    bull_case="",
                    bear_case="",
                )
            return self._hold(df, reason)

        returns = df["close"].pct_change()
        vol5 = returns.rolling(_VOL_SHORT).std()
        vol20 = returns.rolling(_VOL_LONG).std()

        # Avoid division by zero
        vol_ratio_series = vol5 / vol20.replace(0, np.nan)

        direction_series = df["close"].rolling(_DIRECTION_PERIOD).apply(
            lambda x: 1.0 if x[-1] > x[0] else -1.0, raw=True
        )

        # SMA for additional trend confirmation
        sma10 = df["close"].rolling(_SMA_PERIOD).mean()

        # Momentum strength: where close sits in the range (high-low) 
        # high_momentum = close is near high; low_momentum = close is near low
        high_low_range = df["high"] - df["low"]
        close_position = (df["close"] - df["low"]) / high_low_range.replace(0, 1e-10)

        idx = len(df) - 2

        vr = vol_ratio_series.iloc[idx]
        direction = direction_series.iloc[idx]
        close_curr = float(df["close"].iloc[idx])
        sma_curr = float(sma10.iloc[idx])
        momentum_pos = float(close_position.iloc[idx])

        # NaN 처리
        if any(
            v is None or (isinstance(v, float) and np.isnan(v))
            for v in [vr, direction, sma_curr]
        ):
            return self._hold(df, "NaN in indicators — waiting for sufficient history")

        context = (
            f"vol_ratio={vr:.4f} direction={direction:.0f} "
            f"close={close_curr:.4f} sma10={sma_curr:.4f} momentum_pos={momentum_pos:.2f}"
        )

        if vr < _LOW_VOL_THRESH:
            confidence = Confidence.MEDIUM
            
            # HIGH confidence: low vol_ratio + momentum aligned with direction
            # BUY momentum: close near high (momentum_pos > 0.6)
            # SELL momentum: close near low (momentum_pos < 0.4)
            if vr < _HIGH_CONF_THRESH:
                if direction > 0 and momentum_pos > 0.6:
                    confidence = Confidence.HIGH
                elif direction < 0 and momentum_pos < 0.4:
                    confidence = Confidence.HIGH

            if direction > 0 and close_curr > sma_curr:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close_curr,
                    reasoning=(
                        f"volatility_cluster BUY: low vol_ratio={vr:.4f}<{_LOW_VOL_THRESH} "
                        f"+ direction={direction:.0f} (상승) + close > sma10 "
                        f"— 저변동성 이후 상승 돌파 (SMA 확인)"
                    ),
                    invalidation=f"vol_ratio rises above {_LOW_VOL_THRESH} or direction turns negative",
                    bull_case=context,
                    bear_case=context,
                )
            elif direction < 0 and close_curr < sma_curr:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close_curr,
                    reasoning=(
                        f"volatility_cluster SELL: low vol_ratio={vr:.4f}<{_LOW_VOL_THRESH} "
                        f"+ direction={direction:.0f} (하락) + close < sma10 "
                        f"— 저변동성 이후 하락 돌파 (SMA 확인)"
                    ),
                    invalidation=f"vol_ratio rises above {_LOW_VOL_THRESH} or direction turns positive",
                    bull_case=context,
                    bear_case=context,
                )

        return self._hold(df, f"No signal: vol_ratio={vr:.4f}>={_LOW_VOL_THRESH} or close vs sma10 mismatch", context, context)

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
