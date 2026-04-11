"""
VolatilityClusterStrategy (improved):
- 원리: 변동성 군집 현상(GARCH-inspired) — 변동성이 낮은 시기 이후 급등락 예측
- 개선: ATR 수축 필터 + 볼륨 확인 + 방향 모멘텀 강화
- 지표:
  - returns = close.pct_change()
  - vol5 = returns.rolling(5).std()
  - vol20 = returns.rolling(20).std()
  - vol_ratio = vol5 / vol20
  - ATR14 = (high-low).rolling(14).mean() → ATR 수축 확인
  - volume: vol > vol_ma20 (강한 거래량)
  - momentum = close.rolling(20).apply(momentum_signal) → 20기간 모멘텀 확인
- 신호:
  - BUY: vol_ratio < 0.5 AND direction > 0 AND volume > vol_ma AND atr_contracting (준비) or atr_expanding (발동)
  - SELL: vol_ratio < 0.5 AND direction < 0 AND volume > vol_ma AND atr signal
  - confidence: HIGH if vol_ratio < 0.3 + volume > vol_ma*1.3 + momentum aligned
- 최소 데이터: 40행
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 40
_VOL_SHORT = 5
_VOL_LONG = 20
_DIRECTION_PERIOD = 10
_MOMENTUM_PERIOD = 20
_LOW_VOL_THRESH = 0.5
_HIGH_CONF_THRESH = 0.3
_ATR_PERIOD = 14
_ATR_THRESHOLD = 0.02  # ATR must expand >= 2% to signal


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

        # ATR: True Range = max(high-low, abs(high-close_prev), abs(low-close_prev))
        high_low = df["high"] - df["low"]
        high_close = (df["high"] - df["close"].shift(1)).abs()
        low_close = (df["low"] - df["close"].shift(1)).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(_ATR_PERIOD).mean()
        atr_prev = atr.shift(1)

        # Volume filter: current volume vs 20-period average
        vol_ma = df["volume"].rolling(20).mean()

        # Momentum: 20기간 close 방향성 + 고점 갱신 확인
        def momentum_signal(x):
            if x[-1] > x[0]:  # 상승 구간
                return 1.0 if x[-1] > np.percentile(x, 70) else 0.5
            else:  # 하락 구간
                return -1.0 if x[-1] < np.percentile(x, 30) else -0.5

        momentum_series = df["close"].rolling(_MOMENTUM_PERIOD).apply(
            momentum_signal, raw=True
        )

        idx = len(df) - 2

        vr = vol_ratio_series.iloc[idx]
        direction = direction_series.iloc[idx]
        close_curr = float(df["close"].iloc[idx])
        atr_curr = float(atr.iloc[idx]) if idx < len(atr) else np.nan
        atr_p = float(atr_prev.iloc[idx]) if idx < len(atr_prev) else np.nan
        vol_curr = float(df["volume"].iloc[idx])
        vol_ma_curr = float(vol_ma.iloc[idx])
        momentum = float(momentum_series.iloc[idx])

        # NaN 처리
        if any(
            v is None or (isinstance(v, float) and np.isnan(v))
            for v in [vr, direction, atr_curr, atr_p, vol_ma_curr]
        ):
            return self._hold(df, "NaN in indicators — waiting for sufficient history")

        # ATR expansion: atr_curr > atr_prev (변동성 확대 = 거래량 증가 신호)
        atr_expanding = atr_curr > atr_p * (1 + _ATR_THRESHOLD)
        
        # Volume confirmation: must be above 20-period average
        volume_ok = vol_curr > vol_ma_curr

        context = (
            f"vol_ratio={vr:.4f} direction={direction:.0f} "
            f"atr={atr_curr:.6f} atr_prev={atr_p:.6f} expanding={atr_expanding} "
            f"vol={vol_curr:.0f} vol_ma={vol_ma_curr:.0f} momentum={momentum:.1f}"
        )

        if vr < _LOW_VOL_THRESH and volume_ok:
            confidence = Confidence.MEDIUM
            
            # HIGH confidence: low vol_ratio + volume spike + ATR expanding + momentum aligned
            if (vr < _HIGH_CONF_THRESH and 
                vol_curr > vol_ma_curr * 1.3 and 
                atr_expanding and
                ((direction > 0 and momentum > 0) or (direction < 0 and momentum < 0))):
                confidence = Confidence.HIGH

            if direction > 0 and atr_expanding:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close_curr,
                    reasoning=(
                        f"volatility_cluster BUY: low vol_ratio={vr:.4f}<{_LOW_VOL_THRESH} "
                        f"+ direction={direction:.0f} + ATR expanding + vol_spike "
                        f"— 저변동성 후 상승 돌파 (강한 거래량 확인)"
                    ),
                    invalidation=f"vol_ratio rises above {_LOW_VOL_THRESH} or atr contracts or vol drops",
                    bull_case=context,
                    bear_case=context,
                )
            elif direction < 0 and atr_expanding:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close_curr,
                    reasoning=(
                        f"volatility_cluster SELL: low vol_ratio={vr:.4f}<{_LOW_VOL_THRESH} "
                        f"+ direction={direction:.0f} + ATR expanding + vol_spike "
                        f"— 저변동성 후 하락 돌파 (강한 거래량 확인)"
                    ),
                    invalidation=f"vol_ratio rises above {_LOW_VOL_THRESH} or atr contracts or vol drops",
                    bull_case=context,
                    bear_case=context,
                )

        return self._hold(df, f"No signal: vol_ratio={vr:.4f}, volume_ok={volume_ok}, atr_expanding={atr_expanding}", context, context)

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
