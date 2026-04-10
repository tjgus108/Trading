"""
RegimeMomentumStrategy: 시장 레짐(추세/횡보) 판단 후 레짐에 맞는 전략 적용.
- 추세장: EMA10/EMA20 크로스 모멘텀 추종
- 횡보장: 볼린저 밴드 반전 전략
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class RegimeMomentumStrategy(BaseStrategy):
    name = "regime_momentum"

    MIN_ROWS = 30

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: 최소 30행 필요",
                invalidation="",
            )

        close = df["close"]
        high = df["high"]
        low = df["low"]

        # 레짐 판단
        atr = (high - low).rolling(14, min_periods=1).mean()
        close_range = close.rolling(20, min_periods=1).max() - close.rolling(20, min_periods=1).min()
        efficiency_ratio = abs(close - close.shift(20)) / (close_range + 1e-10)
        trending = efficiency_ratio > 0.4

        row = self._last(df)
        idx = len(df) - 2

        entry = float(row["close"])

        er_val = float(efficiency_ratio.iloc[idx])
        if pd.isna(er_val):
            er_val = 0.0

        is_trending = bool(trending.iloc[idx])

        # Confidence
        if er_val > 0.6 or er_val < 0.2:
            conf = Confidence.HIGH
        else:
            conf = Confidence.MEDIUM

        if is_trending:
            # 추세장: EMA 크로스 모멘텀
            ema10 = close.ewm(span=10).mean()
            ema20 = close.ewm(span=20).mean()

            ema10_val = float(ema10.iloc[idx])
            ema20_val = float(ema20.iloc[idx])

            if pd.isna(ema10_val) or pd.isna(ema20_val):
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.LOW,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning="EMA NaN",
                    invalidation="",
                )

            bull_case = f"추세장(ER={er_val:.3f}), EMA10={ema10_val:.4f} > EMA20={ema20_val:.4f}"
            bear_case = f"추세장(ER={er_val:.3f}), EMA10={ema10_val:.4f} < EMA20={ema20_val:.4f}"

            if ema10_val > ema20_val:
                return Signal(
                    action=Action.BUY,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=f"추세장 모멘텀 BUY: ER={er_val:.3f}, EMA10={ema10_val:.4f} > EMA20={ema20_val:.4f}",
                    invalidation=f"EMA10 < EMA20 ({ema20_val:.4f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            else:
                return Signal(
                    action=Action.SELL,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=f"추세장 모멘텀 SELL: ER={er_val:.3f}, EMA10={ema10_val:.4f} < EMA20={ema20_val:.4f}",
                    invalidation=f"EMA10 > EMA20 ({ema20_val:.4f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
        else:
            # 횡보장: 볼린저 밴드 반전
            bb_mid = close.rolling(20, min_periods=1).mean()
            bb_std = close.rolling(20, min_periods=1).std()

            bb_mid_val = float(bb_mid.iloc[idx])
            bb_std_val = float(bb_std.iloc[idx])

            if pd.isna(bb_mid_val) or pd.isna(bb_std_val):
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.LOW,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning="BB NaN",
                    invalidation="",
                )

            upper = bb_mid_val + bb_std_val
            lower = bb_mid_val - bb_std_val

            bull_case = f"횡보장(ER={er_val:.3f}), close={entry:.4f} < BB하단={lower:.4f}"
            bear_case = f"횡보장(ER={er_val:.3f}), close={entry:.4f} > BB상단={upper:.4f}"

            if entry < lower:
                return Signal(
                    action=Action.BUY,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=f"횡보장 반전 BUY: ER={er_val:.3f}, close={entry:.4f} < BB하단={lower:.4f}",
                    invalidation=f"Close < BB하단 ({lower:.4f}) 지속",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            elif entry > upper:
                return Signal(
                    action=Action.SELL,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=f"횡보장 반전 SELL: ER={er_val:.3f}, close={entry:.4f} > BB상단={upper:.4f}",
                    invalidation=f"Close > BB상단 ({upper:.4f}) 지속",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            else:
                return Signal(
                    action=Action.HOLD,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=f"횡보장 중립: ER={er_val:.3f}, close={entry:.4f} BB내({lower:.4f}~{upper:.4f})",
                    invalidation="",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
