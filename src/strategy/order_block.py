"""
OrderBlockStrategy: Smart Money 오더 블록 기반 전략.

- Bullish OB: 최근 3봉 내 5% 이상 상승 직전의 마지막 음봉
  BUY: close가 OB 존(ob_low ~ ob_high)에 진입
- Bearish OB: 최근 3봉 내 5% 이상 하락 직전의 마지막 양봉
  SELL: close가 OB 존에 진입
- confidence: OB 크기 > ATR14 * 1.0 → HIGH, 그 외 MEDIUM
- 최소 행: 15
"""

from typing import Optional, Tuple

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 15
_MOVE_PCT = 5.0  # 강한 이동 기준 (%)
_LOOKBACK = 3    # 큰 이동 탐색 범위


def _atr14(df: pd.DataFrame, idx: int) -> float:
    """ATR14 컬럼이 있으면 사용, 없으면 최근 14봉 TR 평균."""
    if "atr14" in df.columns:
        return float(df.iloc[idx]["atr14"])
    start = max(0, idx - 14)
    sub = df.iloc[start:idx + 1]
    tr = (sub["high"] - sub["low"]).abs()
    return float(tr.mean()) if len(tr) > 0 else 1.0


def _find_bullish_ob(
    df: pd.DataFrame, idx: int
) -> Optional[Tuple[float, float]]:
    """
    최근 _LOOKBACK봉 내에서 5% 이상 상승한 봉을 찾고,
    그 직전 마지막 음봉의 (low, high)를 반환.
    """
    for i in range(idx, max(idx - _LOOKBACK, 1), -1):
        curr = df.iloc[i]
        prev = df.iloc[i - 1]
        # i봉이 강한 상승봉인지 확인
        if float(prev["close"]) == 0:
            continue
        move = (float(curr["close"]) - float(prev["close"])) / abs(float(prev["close"])) * 100
        if move >= _MOVE_PCT:
            # 직전 마지막 음봉 탐색 (i-1 부터 역방향)
            for j in range(i - 1, max(i - 5, -1), -1):
                c = df.iloc[j]
                if float(c["close"]) < float(c["open"]):  # 음봉
                    return (float(c["low"]), float(c["high"]))
    return None


def _find_bearish_ob(
    df: pd.DataFrame, idx: int
) -> Optional[Tuple[float, float]]:
    """
    최근 _LOOKBACK봉 내에서 5% 이상 하락한 봉을 찾고,
    그 직전 마지막 양봉의 (low, high)를 반환.
    """
    for i in range(idx, max(idx - _LOOKBACK, 1), -1):
        curr = df.iloc[i]
        prev = df.iloc[i - 1]
        if float(prev["close"]) == 0:
            continue
        move = (float(curr["close"]) - float(prev["close"])) / abs(float(prev["close"])) * 100
        if move <= -_MOVE_PCT:
            # 직전 마지막 양봉 탐색
            for j in range(i - 1, max(i - 5, -1), -1):
                c = df.iloc[j]
                if float(c["close"]) > float(c["open"]):  # 양봉
                    return (float(c["low"]), float(c["high"]))
    return None


class OrderBlockStrategy(BaseStrategy):
    name = "order_block"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        last = df.iloc[idx]
        close = float(last["close"])
        atr = _atr14(df, idx)

        # Bullish OB 확인
        bull_ob = _find_bullish_ob(df, idx)
        if bull_ob is not None:
            ob_low, ob_high = bull_ob
            if ob_low <= close <= ob_high:
                ob_size = ob_high - ob_low
                confidence = Confidence.HIGH if ob_size > atr * 1.0 else Confidence.MEDIUM
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"Bullish OB 진입: close={close:.4f} in [{ob_low:.4f}, {ob_high:.4f}], "
                        f"OB size={ob_size:.4f}, ATR14={atr:.4f}"
                    ),
                    invalidation=f"Close below OB low ({ob_low:.4f})",
                    bull_case=f"Smart money bullish OB at [{ob_low:.4f}, {ob_high:.4f}]",
                    bear_case="OB invalidated if price breaks below",
                )

        # Bearish OB 확인
        bear_ob = _find_bearish_ob(df, idx)
        if bear_ob is not None:
            ob_low, ob_high = bear_ob
            if ob_low <= close <= ob_high:
                ob_size = ob_high - ob_low
                confidence = Confidence.HIGH if ob_size > atr * 1.0 else Confidence.MEDIUM
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"Bearish OB 진입: close={close:.4f} in [{ob_low:.4f}, {ob_high:.4f}], "
                        f"OB size={ob_size:.4f}, ATR14={atr:.4f}"
                    ),
                    invalidation=f"Close above OB high ({ob_high:.4f})",
                    bull_case="OB invalidated if price breaks above",
                    bear_case=f"Smart money bearish OB at [{ob_low:.4f}, {ob_high:.4f}]",
                )

        return self._hold(
            df,
            f"No OB signal: close={close:.4f}, bull_ob={bull_ob}, bear_ob={bear_ob}",
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
