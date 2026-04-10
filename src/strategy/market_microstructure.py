"""
MarketMicrostructureStrategy:
- 시장 미시구조 기반 (bid-ask spread 대리 + 가격 충격)
- effective_spread = (high - low) / (close + 1e-10)
- price_impact = abs(close.pct_change()) / (volume / (volume.rolling(20, min_periods=1).mean() + 1e-10) + 1e-10)
- good_liquidity = effective_spread < spread_ma * 0.8
- BUY: good_liquidity AND close > close.shift(1) AND price_impact < impact_ma
- SELL: good_liquidity AND close < close.shift(1) AND price_impact < impact_ma
- confidence: HIGH if effective_spread < spread_ma * 0.5 else MEDIUM
- 최소 데이터: 20행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class MarketMicrostructureStrategy(BaseStrategy):
    name = "market_microstructure"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            reason = "Insufficient data for market microstructure"
            if df is not None and len(df) >= 2:
                last = self._last(df)
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.LOW,
                    strategy=self.name,
                    entry_price=float(last["close"]),
                    reasoning=reason,
                    invalidation="",
                )
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=reason,
                invalidation="",
            )

        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        volume = df["volume"].astype(float)

        effective_spread = (high - low) / (close + 1e-10)
        vol_ratio = volume / (volume.rolling(20, min_periods=1).mean() + 1e-10)
        price_impact = close.pct_change().abs() / (vol_ratio + 1e-10)
        spread_ma = effective_spread.rolling(10, min_periods=1).mean()
        impact_ma = price_impact.rolling(10, min_periods=1).mean()

        idx = len(df) - 2
        es_val = float(effective_spread.iloc[idx])
        es_ma_val = spread_ma.iloc[idx]
        pi_val = price_impact.iloc[idx]
        pi_ma_val = impact_ma.iloc[idx]
        close_val = float(close.iloc[idx])
        prev_close_val = float(close.iloc[idx - 1]) if idx >= 1 else close_val

        if pd.isna(es_val) or pd.isna(es_ma_val) or pd.isna(pi_val) or pd.isna(pi_ma_val):
            return self._hold(df, "NaN in microstructure calculation")

        es_ma = float(es_ma_val)
        pi_ma = float(pi_ma_val)
        pi = float(pi_val)

        good_liquidity = es_val < es_ma * 0.8
        low_impact = pi < pi_ma

        confidence = Confidence.HIGH if es_val < es_ma * 0.5 else Confidence.MEDIUM

        if good_liquidity and close_val > prev_close_val and low_impact:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"유동성 좋음+상승: spread={es_val:.4f} < ma*0.8={es_ma*0.8:.4f}, price_impact={pi:.4f} < ma={pi_ma:.4f}",
                invalidation="Spread rises above spread_ma * 0.8 or price_impact > impact_ma",
                bull_case=f"spread={es_val:.4f} spread_ma={es_ma:.4f} impact={pi:.4f}",
                bear_case=f"spread={es_val:.4f}",
            )

        if good_liquidity and close_val < prev_close_val and low_impact:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"유동성 좋음+하락: spread={es_val:.4f} < ma*0.8={es_ma*0.8:.4f}, price_impact={pi:.4f} < ma={pi_ma:.4f}",
                invalidation="Spread rises above spread_ma * 0.8 or price_impact > impact_ma",
                bull_case=f"spread={es_val:.4f}",
                bear_case=f"spread={es_val:.4f} spread_ma={es_ma:.4f} impact={pi:.4f}",
            )

        return self._hold(df, f"유동성 미충족 또는 방향 불명: spread={es_val:.4f} ma={es_ma:.4f} good_liq={good_liquidity}")

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        if df is None or len(df) < 2:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=reason,
                invalidation="",
                bull_case=bull_case,
                bear_case=bear_case,
            )
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
