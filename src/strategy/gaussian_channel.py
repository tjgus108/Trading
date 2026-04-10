"""
GaussianChannelStrategy: 4-pole Gaussian 필터 기반 채널 전략.
일반 SMA보다 부드러운 채널로 가격 복귀/이탈 감지.
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class GaussianChannelStrategy(BaseStrategy):
    name = "gaussian_channel"

    def __init__(self, lookback: int = 14, multiplier: float = 1.5):
        self.lookback = lookback
        self.multiplier = multiplier

    def _compute_atr(self, df: pd.DataFrame) -> pd.Series:
        high = df["high"]
        low = df["low"]
        prev_close = df["close"].shift(1)
        tr = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
            axis=1,
        ).max(axis=1)
        return tr.rolling(self.lookback).mean()

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 20:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return self._hold(df, "Insufficient data for GaussianChannel (need 20)")

        alpha_g = 2.0 / (self.lookback + 1)

        g1 = df["close"].ewm(alpha=alpha_g, adjust=False).mean()
        g2 = g1.ewm(alpha=alpha_g, adjust=False).mean()
        g3 = g2.ewm(alpha=alpha_g, adjust=False).mean()
        g4 = g3.ewm(alpha=alpha_g, adjust=False).mean()

        gauss = g4
        atr = self._compute_atr(df)

        upper = gauss + self.multiplier * atr
        lower = gauss - self.multiplier * atr

        idx = len(df) - 2

        if idx < 1:
            return self._hold(df, "Insufficient data for GaussianChannel (need 20)")

        # NaN check
        if (
            pd.isna(gauss.iloc[idx])
            or pd.isna(upper.iloc[idx])
            or pd.isna(lower.iloc[idx])
        ):
            return self._hold(df, "GaussianChannel: NaN in indicators")

        curr_close = float(df["close"].iloc[idx])
        prev_close = float(df["close"].iloc[idx - 1])
        curr_upper = float(upper.iloc[idx])
        curr_lower = float(lower.iloc[idx])
        entry_price = curr_close

        # Confidence: gauss rising = HIGH for BUY
        gauss_rising = (
            not pd.isna(gauss.iloc[idx - 1])
            and float(gauss.iloc[idx]) > float(gauss.iloc[idx - 1])
        )

        # BUY: prev_close < lower AND curr_close > lower (하단 채널 복귀)
        if prev_close < curr_lower and curr_close > curr_lower:
            conf = Confidence.HIGH if gauss_rising else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"GaussianChannel: 하단 채널 복귀. "
                    f"prev={prev_close:.2f} < lower={curr_lower:.2f}, "
                    f"curr={curr_close:.2f} > lower={curr_lower:.2f}. "
                    f"Gauss={'상승' if gauss_rising else '하락'} 추세."
                ),
                invalidation=f"close < lower={curr_lower:.2f} 재이탈 시 무효.",
                bull_case="Gaussian 하단 채널 복귀 — 반등 기대.",
                bear_case="추세 전환 실패 가능성 존재.",
            )

        # SELL: prev_close > upper AND curr_close < upper (상단 채널 이탈)
        if prev_close > curr_upper and curr_close < curr_upper:
            conf = Confidence.HIGH if not gauss_rising else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"GaussianChannel: 상단 채널 이탈. "
                    f"prev={prev_close:.2f} > upper={curr_upper:.2f}, "
                    f"curr={curr_close:.2f} < upper={curr_upper:.2f}."
                ),
                invalidation=f"close > upper={curr_upper:.2f} 재돌파 시 무효.",
                bull_case="추세 전환 실패 가능성 존재.",
                bear_case="Gaussian 상단 채널 이탈 — 하락 기대.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"GaussianChannel: 채널 내부. "
                f"gauss={float(gauss.iloc[idx]):.2f}, "
                f"upper={curr_upper:.2f}, lower={curr_lower:.2f}."
            ),
            invalidation="",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
        )
