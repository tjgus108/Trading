"""
BalanceOfPowerStrategy:
- Balance of Power = (close - open) / (high - low) — 매수/매도 압력 측정
- 지표:
  - bop = (close - open) / (high - low), high==low인 경우 0
  - bop_sma = bop.rolling(14).mean()
  - bop_signal = bop_sma.rolling(9).mean()
- BUY: bop_sma crosses above bop_signal AND bop_sma < 0 (음수 구간 상향 교차)
- SELL: bop_sma crosses below bop_signal AND bop_sma > 0 (양수 구간 하향 교차)
- HOLD: 그 외
- confidence: HIGH if |bop_sma| > 0.3 else MEDIUM
- 최소 데이터: 30행
"""

from typing import Optional, Tuple

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_CROSS_THRESHOLD = 0.3


def _calc_bop_lines(df: pd.DataFrame) -> "Tuple[float, float, float, float]":
    """idx = len(df) - 2 기준 bop_sma_now, bop_sma_prev, bop_sig_now, bop_sig_prev 반환."""
    idx = len(df) - 2

    hl_diff = df["high"] - df["low"]
    bop_raw = (df["close"] - df["open"]) / hl_diff.where(hl_diff != 0)
    bop_raw = bop_raw.fillna(0.0)

    bop_sma = bop_raw.rolling(14).mean()
    bop_signal = bop_sma.rolling(9).mean()

    return (
        float(bop_sma.iloc[idx]),
        float(bop_sma.iloc[idx - 1]),
        float(bop_signal.iloc[idx]),
        float(bop_signal.iloc[idx - 1]),
    )


class BalanceOfPowerStrategy(BaseStrategy):
    name = "balance_of_power"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            n = 0 if df is None else len(df)
            close = 0.0 if df is None else float(df["close"].iloc[-2])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Insufficient data: {n} < {_MIN_ROWS}",
                invalidation="데이터 충분 시 재평가",
            )

        idx = len(df) - 2
        bop_sma_now, bop_sma_prev, bop_sig_now, bop_sig_prev = _calc_bop_lines(df)

        if any(pd.isna(v) for v in [bop_sma_now, bop_sma_prev, bop_sig_now, bop_sig_prev]):
            entry = float(df["close"].iloc[idx])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in BOP lines — 계산 불가",
                invalidation="데이터 안정화 후 재평가",
            )

        entry = float(df["close"].iloc[idx])

        # 상향 교차: 이전 bop_sma < signal, 현재 bop_sma > signal, AND bop_sma < 0
        cross_above = bop_sma_prev < bop_sig_prev and bop_sma_now > bop_sig_now and bop_sma_now < 0
        # 하향 교차: 이전 bop_sma > signal, 현재 bop_sma < signal, AND bop_sma > 0
        cross_below = bop_sma_prev > bop_sig_prev and bop_sma_now < bop_sig_now and bop_sma_now > 0

        if cross_above:
            confidence = Confidence.HIGH if abs(bop_sma_now) > _CROSS_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"BOP 음수 구간 상향 교차: bop_sma={bop_sma_now:.3f} > signal={bop_sig_now:.3f} (이전 {bop_sma_prev:.3f} < {bop_sig_prev:.3f})",
                invalidation="bop_sma 재하향 교차 또는 0 상향 이탈 시",
                bull_case=f"매수 압력 회복 중 (BOP SMA={bop_sma_now:.3f})",
                bear_case="음수 구간이라 상승 여력 제한적",
            )

        if cross_below:
            confidence = Confidence.HIGH if abs(bop_sma_now) > _CROSS_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"BOP 양수 구간 하향 교차: bop_sma={bop_sma_now:.3f} < signal={bop_sig_now:.3f} (이전 {bop_sma_prev:.3f} > {bop_sig_prev:.3f})",
                invalidation="bop_sma 재상향 교차 또는 0 하향 이탈 시",
                bull_case="양수 구간이라 하락 제한적",
                bear_case=f"매도 압력 우위 (BOP SMA={bop_sma_now:.3f})",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"교차 없음: bop_sma={bop_sma_now:.3f}, signal={bop_sig_now:.3f}",
            invalidation="BOP SMA/Signal 교차 시 재평가",
        )
