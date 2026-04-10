"""
MultiFactorScoreStrategy: 7개 팩터 점수화 후 임계값 기반 신호 생성.

점수 계산:
  RSI14 > 55: +1, < 45: -1
  MACD hist > 0: +1, < 0: -1
  close > EMA20: +1, < EMA20: -1
  volume > avg20: +0.5, < avg20: -0.5
  BB: close < lower = +1, close > upper = -1 (반전)
  ATR trending: ATR14 > avg_ATR = +0.5
  Price trend: close > close.shift(10) = +1, < = -1

BUY: total_score >= 4.0
SELL: total_score <= -4.0
confidence: score >= 5.0 or score <= -5.0 → HIGH
최소 행: 25
"""

import pandas as pd
import numpy as np
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal


class MultiFactorScoreStrategy(BaseStrategy):
    name = "multi_factor"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 25:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="데이터 부족 (최소 25봉 필요)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        close_series = df["close"]
        last_idx = -2  # _last(df) = df.iloc[-2]
        close = float(close_series.iloc[last_idx])

        # RSI14
        delta = close_series.diff()
        gain = delta.where(delta > 0, 0.0).ewm(span=14, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0.0)).ewm(span=14, adjust=False).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = float((100 - 100 / (1 + rs)).fillna(50).iloc[last_idx])

        # MACD histogram
        ema12 = close_series.ewm(span=12, adjust=False).mean()
        ema26 = close_series.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_hist = float((macd_line - signal_line).iloc[last_idx])

        # EMA20
        ema20 = float(close_series.ewm(span=20, adjust=False).mean().iloc[last_idx])

        # Volume avg20
        vol = float(df["volume"].iloc[last_idx])
        lookback = min(20, len(df) - 1)
        avg_vol = float(df["volume"].iloc[-lookback - 1:last_idx].mean())

        # BB (SMA20 ± 2σ)
        sma20 = float(close_series.rolling(20).mean().iloc[last_idx])
        std20 = float(close_series.rolling(20).std().iloc[last_idx])
        bb_upper = sma20 + 2 * std20
        bb_lower = sma20 - 2 * std20

        # ATR14
        high = df["high"]
        low = df["low"]
        tr = pd.concat([
            high - low,
            (high - close_series.shift()).abs(),
            (low - close_series.shift()).abs(),
        ], axis=1).max(axis=1)
        atr14 = float(tr.ewm(span=14, adjust=False).mean().iloc[last_idx])
        atr_lookback = min(20, len(df) - 1)
        avg_atr = float(tr.ewm(span=14, adjust=False).mean().iloc[-atr_lookback - 1:last_idx].mean())

        # Price trend: close vs 10 bars ago
        price_10ago_idx = last_idx - 10
        if abs(price_10ago_idx) <= len(df):
            price_10ago = float(close_series.iloc[price_10ago_idx])
        else:
            price_10ago = close

        # 점수 계산
        score = 0.0

        # 1. RSI
        if rsi > 55:
            score += 1
        elif rsi < 45:
            score -= 1

        # 2. MACD hist
        if macd_hist > 0:
            score += 1
        elif macd_hist < 0:
            score -= 1

        # 3. EMA20
        if close > ema20:
            score += 1
        elif close < ema20:
            score -= 1

        # 4. Volume
        if vol > avg_vol:
            score += 0.5
        elif vol < avg_vol:
            score -= 0.5

        # 5. BB 반전
        if close < bb_lower:
            score += 1
        elif close > bb_upper:
            score -= 1

        # 6. ATR trending
        if atr14 > avg_atr:
            score += 0.5

        # 7. Price trend
        if close > price_10ago:
            score += 1
        elif close < price_10ago:
            score -= 1

        confidence = Confidence.HIGH if (score >= 5.0 or score <= -5.0) else Confidence.MEDIUM

        bull_case = (
            f"score={score:.1f}, RSI={rsi:.1f}, MACD_hist={macd_hist:.4f}, "
            f"EMA20={ema20:.2f}, vol_ratio={vol/avg_vol:.2f}"
        )
        bear_case = (
            f"score={score:.1f}, BB_lower={bb_lower:.2f}, BB_upper={bb_upper:.2f}, "
            f"ATR={atr14:.4f}, price_10ago={price_10ago:.2f}"
        )

        if score >= 4.0:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"MultiFactorScore={score:.1f} >= 4.0 (BUY threshold)",
                invalidation=f"score 하락 또는 EMA20 ({ema20:.2f}) 하향 이탈",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if score <= -4.0:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"MultiFactorScore={score:.1f} <= -4.0 (SELL threshold)",
                invalidation=f"score 반등 또는 EMA20 ({ema20:.2f}) 상향 돌파",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=confidence,
            strategy=self.name,
            entry_price=close,
            reasoning=f"MultiFactorScore={score:.1f} — 임계값 미달 (|score| < 4)",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
