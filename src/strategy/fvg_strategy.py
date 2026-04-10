"""
FairValueGapStrategy: Fair Value Gap (FVG) / 가격 불균형 기반 전략.

- Bullish FVG: candle[i-2].high < candle[i].low  (갭업, 미채워진 상승 갭)
  → 갭 존 = (candle[i-2].high, candle[i].low)
  SELL: close가 bullish FVG 존에 진입 (mean reversion: 갭 채우러 옴)

- Bearish FVG: candle[i-2].low > candle[i].high  (갭다운)
  → 갭 존 = (candle[i].high, candle[i-2].low)
  BUY: close가 bearish FVG 존에 진입 (mean reversion: 갭 채우러 옴)

- 최근 10봉 내 FVG 탐색
- confidence: gap 크기 > ATR14 * 1.5 → HIGH, 그 외 MEDIUM
- 최소 행: 15
"""

from typing import Optional, Tuple

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 15
_LOOKBACK = 10


def _atr14(df: pd.DataFrame, idx: int) -> float:
    if "atr14" in df.columns:
        return float(df.iloc[idx]["atr14"])
    start = max(0, idx - 14)
    sub = df.iloc[start:idx + 1]
    tr = (sub["high"] - sub["low"]).abs()
    return float(tr.mean()) if len(tr) > 0 else 1.0


def _find_bearish_fvg(
    df: pd.DataFrame, idx: int
) -> Optional[Tuple[float, float]]:
    """
    최근 _LOOKBACK봉 내에서 bearish FVG 탐색.
    candle[i-2].low > candle[i].high → (candle[i].high, candle[i-2].low)
    """
    start = max(2, idx - _LOOKBACK + 1)
    for i in range(idx, start - 1, -1):
        prev_prev = df.iloc[i - 2]
        curr = df.iloc[i]
        fvg_low = float(curr["high"])
        fvg_high = float(prev_prev["low"])
        if fvg_high > fvg_low:
            return (fvg_low, fvg_high)
    return None


def _find_bullish_fvg(
    df: pd.DataFrame, idx: int
) -> Optional[Tuple[float, float]]:
    """
    최근 _LOOKBACK봉 내에서 bullish FVG 탐색.
    candle[i-2].high < candle[i].low → (candle[i-2].high, candle[i].low)
    """
    start = max(2, idx - _LOOKBACK + 1)
    for i in range(idx, start - 1, -1):
        prev_prev = df.iloc[i - 2]
        curr = df.iloc[i]
        fvg_low = float(prev_prev["high"])
        fvg_high = float(curr["low"])
        if fvg_high > fvg_low:
            return (fvg_low, fvg_high)
    return None


class FairValueGapStrategy(BaseStrategy):
    name = "fvg_strategy"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        last = df.iloc[idx]
        close = float(last["close"])
        atr = _atr14(df, idx)

        # Bearish FVG → BUY (갭 채움 mean reversion)
        bear_fvg = _find_bearish_fvg(df, idx)
        if bear_fvg is not None:
            fvg_low, fvg_high = bear_fvg
            if fvg_low <= close <= fvg_high:
                gap_size = fvg_high - fvg_low
                confidence = Confidence.HIGH if gap_size > atr * 1.5 else Confidence.MEDIUM
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"Bearish FVG 갭 채움 BUY: close={close:.4f} in [{fvg_low:.4f}, {fvg_high:.4f}], "
                        f"gap={gap_size:.4f}, ATR14={atr:.4f}"
                    ),
                    invalidation=f"Close below FVG low ({fvg_low:.4f})",
                    bull_case=f"Mean reversion: FVG gap fill [{fvg_low:.4f}, {fvg_high:.4f}]",
                    bear_case="Gap may not fill if trend continues",
                )

        # Bullish FVG → SELL (갭 채움 mean reversion)
        bull_fvg = _find_bullish_fvg(df, idx)
        if bull_fvg is not None:
            fvg_low, fvg_high = bull_fvg
            if fvg_low <= close <= fvg_high:
                gap_size = fvg_high - fvg_low
                confidence = Confidence.HIGH if gap_size > atr * 1.5 else Confidence.MEDIUM
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"Bullish FVG 갭 채움 SELL: close={close:.4f} in [{fvg_low:.4f}, {fvg_high:.4f}], "
                        f"gap={gap_size:.4f}, ATR14={atr:.4f}"
                    ),
                    invalidation=f"Close above FVG high ({fvg_high:.4f})",
                    bull_case="Gap may not fill if trend continues",
                    bear_case=f"Mean reversion: FVG gap fill [{fvg_low:.4f}, {fvg_high:.4f}]",
                )

        return self._hold(
            df,
            f"No FVG signal: close={close:.4f}, bear_fvg={bear_fvg}, bull_fvg={bull_fvg}",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        price = float(df.iloc[-2]["close"]) if len(df) >= 2 else float(df.iloc[-1]["close"])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
