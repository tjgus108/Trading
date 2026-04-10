"""
HybridTrendReversionStrategy: 추세장/횡보장 자동 감지 후 맞는 전략 적용.

- ADX 계산 (EWM span=14)
- Trending (ADX > 25): EMA 크로스 추세 추종
  - BUY: EMA9 > EMA21 > EMA50 AND RSI14 > 50
  - SELL: EMA9 < EMA21 < EMA50 AND RSI14 < 50
- Ranging (ADX <= 25): BB 반전
  - BUY: close < BB_lower (SMA20 - 2σ)
  - SELL: close > BB_upper (SMA20 + 2σ)
- confidence: ADX > 40 (trending) or ADX < 15 (ranging) → HIGH
- 최소 행: 30
"""

import pandas as pd
import numpy as np
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal


class HybridTrendReversionStrategy(BaseStrategy):
    name = "hybrid_trend_rev"

    def _calc_adx(self, df: pd.DataFrame, span: int = 14) -> pd.Series:
        high = df["high"]
        low = df["low"]
        close = df["close"]

        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs(),
        ], axis=1).max(axis=1)

        atr_ewm = tr.ewm(span=span, adjust=False).mean()
        plus_di = 100 * plus_dm.ewm(span=span, adjust=False).mean() / atr_ewm.replace(0, np.nan)
        minus_di = 100 * minus_dm.ewm(span=span, adjust=False).mean() / atr_ewm.replace(0, np.nan)

        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
        adx = dx.ewm(span=span, adjust=False).mean()
        return adx.fillna(0)

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 30:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="데이터 부족 (최소 30봉 필요)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        last = self._last(df)
        close = float(last["close"])

        # ADX
        adx_series = self._calc_adx(df)
        adx = float(adx_series.iloc[-2])

        # EMA
        ema9 = float(df["close"].ewm(span=9, adjust=False).mean().iloc[-2])
        ema21 = float(df["close"].ewm(span=21, adjust=False).mean().iloc[-2])
        ema50 = float(df["close"].ewm(span=50, adjust=False).mean().iloc[-2])

        # RSI14
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0.0).ewm(span=14, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0.0)).ewm(span=14, adjust=False).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = float((100 - 100 / (1 + rs)).fillna(50).iloc[-2])

        # BB (SMA20 ± 2σ)
        sma20 = float(df["close"].rolling(20).mean().iloc[-2])
        std20 = float(df["close"].rolling(20).std().iloc[-2])
        bb_upper = sma20 + 2 * std20
        bb_lower = sma20 - 2 * std20

        is_trending = adx > 25
        confidence = Confidence.HIGH if (adx > 40 or adx < 15) else Confidence.MEDIUM

        bull_case = f"ADX={adx:.1f}, EMA9={ema9:.2f}, EMA21={ema21:.2f}, EMA50={ema50:.2f}, RSI={rsi:.1f}"
        bear_case = f"ADX={adx:.1f}, close={close:.2f}, BB_lower={bb_lower:.2f}, BB_upper={bb_upper:.2f}"

        if is_trending:
            mode = "trending"
            if ema9 > ema21 > ema50 and rsi > 50:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=f"[{mode}] EMA9>EMA21>EMA50 & RSI={rsi:.1f}>50, ADX={adx:.1f}",
                    invalidation=f"EMA9 < EMA21 또는 close < EMA50 ({ema50:.2f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            if ema9 < ema21 < ema50 and rsi < 50:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=f"[{mode}] EMA9<EMA21<EMA50 & RSI={rsi:.1f}<50, ADX={adx:.1f}",
                    invalidation=f"EMA9 > EMA21 또는 close > EMA50 ({ema50:.2f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
        else:
            mode = "ranging"
            if close < bb_lower:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=f"[{mode}] close={close:.2f} < BB_lower={bb_lower:.2f}, ADX={adx:.1f}",
                    invalidation=f"close > SMA20 ({sma20:.2f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            if close > bb_upper:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=f"[{mode}] close={close:.2f} > BB_upper={bb_upper:.2f}, ADX={adx:.1f}",
                    invalidation=f"close < SMA20 ({sma20:.2f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )

        return Signal(
            action=Action.HOLD,
            confidence=confidence,
            strategy=self.name,
            entry_price=close,
            reasoning=f"[{mode if is_trending else 'ranging'}] 조건 미충족. ADX={adx:.1f}",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
