"""
OscillatorBandStrategy:
- RSI(14) + Stochastic(14)을 결합한 합성 오실레이터 밴드 (0~100)
- BUY:  osc < 30 AND osc > osc.shift(1) AND stoch_k > stoch_d
- SELL: osc > 70 AND osc < osc.shift(1) AND stoch_k < stoch_d
- HOLD: 30 <= osc <= 70
- confidence: HIGH if osc < 20 (BUY) or osc > 80 (SELL) else MEDIUM
- 최소 데이터: 20행
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


def _calc_indicators(df: pd.DataFrame) -> "Optional[Tuple[pd.Series, pd.Series, pd.Series]]":
    """osc, stoch_k, stoch_d 시리즈 반환. 실패 시 None."""
    close = df["close"].astype(float)

    # RSI(14)
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
    rsi = 100 - 100 / (1 + gain / loss.replace(0, 1e-10))

    # Stochastic(14)
    low14 = df["low"].astype(float).rolling(14).min()
    high14 = df["high"].astype(float).rolling(14).max()
    stoch_k = 100 * (close - low14) / (high14 - low14 + 1e-10)
    stoch_d = stoch_k.rolling(3).mean()

    # 합성 오실레이터 밴드
    osc = (rsi + stoch_k) / 2

    return osc, stoch_k, stoch_d


class OscillatorBandStrategy(BaseStrategy):
    name = "oscillator_band"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for OscillatorBand (need 20 rows)")

        # high/low 컬럼 없으면 close로 대체
        df = df.copy()
        if "high" not in df.columns:
            df["high"] = df["close"]
        if "low" not in df.columns:
            df["low"] = df["close"]

        osc, stoch_k, stoch_d = _calc_indicators(df)

        idx = len(df) - 2

        osc_val = float(osc.iloc[idx]) if not np.isnan(osc.iloc[idx]) else 50.0
        osc_prev = float(osc.iloc[idx - 1]) if idx >= 1 and not np.isnan(osc.iloc[idx - 1]) else osc_val
        k_val = float(stoch_k.iloc[idx]) if not np.isnan(stoch_k.iloc[idx]) else 50.0
        d_val = float(stoch_d.iloc[idx]) if not np.isnan(stoch_d.iloc[idx]) else 50.0

        last = self._last(df)
        close = float(last["close"])

        context = f"osc={osc_val:.1f} osc_prev={osc_prev:.1f} K={k_val:.1f} D={d_val:.1f} close={close:.4f}"

        # BUY
        if osc_val < 30 and osc_val > osc_prev and k_val > d_val:
            confidence = Confidence.HIGH if osc_val < 20 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"OscillatorBand 과매도 반등: {context}",
                invalidation="osc 재하락 또는 K < D 전환 시",
                bull_case=context,
                bear_case=context,
            )

        # SELL
        if osc_val > 70 and osc_val < osc_prev and k_val < d_val:
            confidence = Confidence.HIGH if osc_val > 80 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"OscillatorBand 과매수 하락: {context}",
                invalidation="osc 재상승 또는 K > D 전환 시",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"OscillatorBand no signal: {context}")

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
