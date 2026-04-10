"""
VolatilityExpansionStrategy: 수축 후 팽창으로 추세 시작 감지.

hist_vol_5  = close.pct_change().rolling(5).std()
hist_vol_20 = close.pct_change().rolling(20).std()
expansion   = hist_vol_5 / hist_vol_20

Contraction phase: expansion < 0.7 (이전 3봉 중 2봉 이상)
Expansion trigger: expansion > 1.2 (현재봉)

BUY : contraction → expansion AND close > close.shift(3) (상방 이동)
SELL: contraction → expansion AND close < close.shift(3)
Confidence HIGH: expansion > 1.8
최소 행: 25
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class VolatilityExpansionStrategy(BaseStrategy):
    name = "volatility_expansion"

    MIN_ROWS = 25
    VOL_SHORT = 5
    VOL_LONG = 20
    CONTRACT_THRESH = 0.7
    EXPAND_THRESH = 1.2
    HIGH_CONF_THRESH = 1.8
    CONTRACT_LOOKBACK = 3   # 이전 3봉
    CONTRACT_MIN = 2        # 2봉 이상

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=f"데이터 부족 (최소 {self.MIN_ROWS}행 필요)",
                invalidation="N/A",
            )

        close = df["close"]
        ret = close.pct_change()
        hist_vol_5 = ret.rolling(self.VOL_SHORT).std()
        hist_vol_20 = ret.rolling(self.VOL_LONG).std()
        expansion = hist_vol_5 / hist_vol_20

        idx = len(df) - 2  # 마지막 완성봉

        curr_close = float(close.iloc[idx])
        curr_expansion = float(expansion.iloc[idx])

        if pd.isna(curr_expansion):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=curr_close,
                reasoning="expansion NaN",
                invalidation="N/A",
            )

        # 이전 3봉 중 2봉 이상 contraction
        prev_contractions = 0
        for i in range(1, self.CONTRACT_LOOKBACK + 1):
            prev_idx = idx - i
            if prev_idx < 0:
                break
            val = float(expansion.iloc[prev_idx])
            if not pd.isna(val) and val < self.CONTRACT_THRESH:
                prev_contractions += 1

        contracted = prev_contractions >= self.CONTRACT_MIN
        expanded = curr_expansion > self.EXPAND_THRESH

        # close vs close.shift(3)
        shift3_idx = idx - 3
        if shift3_idx < 0:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=curr_close,
                reasoning="shift(3) 데이터 부족",
                invalidation="N/A",
            )
        close_3ago = float(close.iloc[shift3_idx])

        confidence = Confidence.HIGH if curr_expansion > self.HIGH_CONF_THRESH else Confidence.MEDIUM

        if contracted and expanded:
            if curr_close > close_3ago:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=curr_close,
                    reasoning=(
                        f"변동성 수축→팽창 + 상방 이동 — "
                        f"expansion={curr_expansion:.3f}(>{self.EXPAND_THRESH}), "
                        f"수축봉={prev_contractions}/{self.CONTRACT_LOOKBACK}, "
                        f"close={curr_close:.4f}>close_3ago={close_3ago:.4f}"
                    ),
                    invalidation=f"expansion < {self.CONTRACT_THRESH} 복귀 또는 close < close_3ago 시 청산",
                    bull_case=f"팽창 강도={curr_expansion:.2f}x, 상방 돌파",
                    bear_case="팽창이 하방으로 반전될 경우 손실",
                )
            elif curr_close < close_3ago:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=curr_close,
                    reasoning=(
                        f"변동성 수축→팽창 + 하방 이동 — "
                        f"expansion={curr_expansion:.3f}(>{self.EXPAND_THRESH}), "
                        f"수축봉={prev_contractions}/{self.CONTRACT_LOOKBACK}, "
                        f"close={curr_close:.4f}<close_3ago={close_3ago:.4f}"
                    ),
                    invalidation=f"expansion < {self.CONTRACT_THRESH} 복귀 또는 close > close_3ago 시 청산",
                    bull_case="팽창이 상방으로 반전될 경우 반등 가능",
                    bear_case=f"팽창 강도={curr_expansion:.2f}x, 하방 지속",
                )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=curr_close,
            reasoning=(
                f"조건 미충족 — expansion={curr_expansion:.3f}, "
                f"contracted={contracted}({prev_contractions}봉), "
                f"expanded={expanded}"
            ),
            invalidation="수축 후 팽창 + 방향성 확인 시 재평가",
        )
