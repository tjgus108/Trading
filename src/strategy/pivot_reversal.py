"""
Pivot Reversal 전략:
- Pivot High = 이전봉의 high가 앞뒤 2봉보다 높을 때
- Pivot Low  = 이전봉의 low가 앞뒤 2봉보다 낮을 때
- BUY:  최근 5봉 내 Pivot Low 발생 AND close > recent_pivot_low * 1.005
- SELL: 최근 5봉 내 Pivot High 발생 AND close < recent_pivot_high * 0.995
- confidence: HIGH if 반등/반락폭 > 1%, MEDIUM 그 외
- 최소 데이터: 15행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 15
LOOKBACK = 5


def _find_pivot_high(df: pd.DataFrame, idx: int) -> bool:
    """idx 위치의 봉이 Pivot High인지 확인 (앞뒤 2봉보다 high가 높아야 함)."""
    if idx < 2 or idx >= len(df) - 2:
        return False
    h = df["high"].iloc[idx]
    return (
        h > df["high"].iloc[idx - 2]
        and h > df["high"].iloc[idx - 1]
        and h > df["high"].iloc[idx + 1]
        and h > df["high"].iloc[idx + 2]
    )


def _find_pivot_low(df: pd.DataFrame, idx: int) -> bool:
    """idx 위치의 봉이 Pivot Low인지 확인 (앞뒤 2봉보다 low가 낮아야 함)."""
    if idx < 2 or idx >= len(df) - 2:
        return False
    l = df["low"].iloc[idx]
    return (
        l < df["low"].iloc[idx - 2]
        and l < df["low"].iloc[idx - 1]
        and l < df["low"].iloc[idx + 1]
        and l < df["low"].iloc[idx + 2]
    )


def _recent_pivot_low(df: pd.DataFrame, last_idx: int) -> Optional[float]:
    """last_idx 기준 최근 LOOKBACK봉 내 Pivot Low 값 반환 (없으면 None)."""
    # 이전봉(last_idx) 기준, 과거 LOOKBACK개 봉에서 pivot 탐색
    # pivot 판별에 앞뒤 2봉이 필요하므로 last_idx-1 까지 확인
    for i in range(last_idx - 1, max(last_idx - LOOKBACK - 1, 1), -1):
        if _find_pivot_low(df, i):
            return float(df["low"].iloc[i])
    return None


def _recent_pivot_high(df: pd.DataFrame, last_idx: int) -> Optional[float]:
    """last_idx 기준 최근 LOOKBACK봉 내 Pivot High 값 반환 (없으면 None)."""
    for i in range(last_idx - 1, max(last_idx - LOOKBACK - 1, 1), -1):
        if _find_pivot_high(df, i):
            return float(df["high"].iloc[i])
    return None


class PivotReversalStrategy(BaseStrategy):
    name = "pivot_reversal"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last = df.iloc[-1]
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last["close"]),
                reasoning=f"데이터 부족: {len(df)} < {MIN_ROWS}",
                invalidation="",
            )

        last = self._last(df)  # df.iloc[-2]
        last_idx = len(df) - 2
        close = float(last["close"])

        pivot_low = _recent_pivot_low(df, last_idx)
        pivot_high = _recent_pivot_high(df, last_idx)

        # BUY 조건
        if pivot_low is not None:
            bounce_ratio = close / pivot_low - 1.0
            if close > pivot_low * 1.005:
                conf = Confidence.HIGH if bounce_ratio > 0.01 else Confidence.MEDIUM
                return Signal(
                    action=Action.BUY,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"최근 {LOOKBACK}봉 내 Pivot Low={pivot_low:.4f} 발생, "
                        f"close={close:.4f} > pivot_low*1.005={pivot_low * 1.005:.4f} "
                        f"(반등폭={bounce_ratio*100:.2f}%)"
                    ),
                    invalidation=f"Close below pivot low {pivot_low:.4f}",
                    bull_case=f"Pivot Low 반등 확인, 반등폭={bounce_ratio*100:.2f}%",
                    bear_case=f"Pivot High={pivot_high:.4f}" if pivot_high else "No recent pivot high",
                )

        # SELL 조건
        if pivot_high is not None:
            drop_ratio = 1.0 - close / pivot_high
            if close < pivot_high * 0.995:
                conf = Confidence.HIGH if drop_ratio > 0.01 else Confidence.MEDIUM
                return Signal(
                    action=Action.SELL,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"최근 {LOOKBACK}봉 내 Pivot High={pivot_high:.4f} 발생, "
                        f"close={close:.4f} < pivot_high*0.995={pivot_high * 0.995:.4f} "
                        f"(반락폭={drop_ratio*100:.2f}%)"
                    ),
                    invalidation=f"Close above pivot high {pivot_high:.4f}",
                    bull_case=f"Pivot Low={pivot_low:.4f}" if pivot_low else "No recent pivot low",
                    bear_case=f"Pivot High 반락 확인, 반락폭={drop_ratio*100:.2f}%",
                )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning="최근 Pivot 신호 없음 또는 반등/반락 조건 미충족",
            invalidation="",
            bull_case=f"Pivot Low={pivot_low:.4f}" if pivot_low else "No recent pivot low",
            bear_case=f"Pivot High={pivot_high:.4f}" if pivot_high else "No recent pivot high",
        )
