"""
BullishEngulfingZoneStrategy: 지지/저항 존 근처의 Engulfing 패턴 전략.
IMPROVED v3: Relaxed RSI thresholds (55/45) + lower body ratio (1.2) for more signals.
- Bullish: RSI < 55 (less oversold), vol >= 1.5x avg
- Bearish: RSI > 45 (less overbought), vol >= 1.5x avg
- Body ratio: > 1.2 (reduced from 1.3)
"""

from typing import List, Optional

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


def _find_pivots(df: pd.DataFrame, window: int = 20, side: int = 3):
    """
    최근 window봉 내에서 pivot high/low를 찾는다.
    side: 좌우 각 side봉이 모두 낮은/높은 점이어야 함.
    Returns (pivot_lows, pivot_highs): list of float
    """
    pivot_lows: List[float] = []
    pivot_highs: List[float] = []

    end = len(df) - 2  # 마지막 완성봉 인덱스
    start = max(side, end - window + 1)

    for i in range(start, end - side + 1):
        low_i = float(df["low"].iloc[i])
        high_i = float(df["high"].iloc[i])

        # pivot low: 좌우 side봉 모두 현재봉보다 high
        is_pivot_low = all(
            float(df["low"].iloc[i + j]) > low_i
            for j in range(-side, side + 1)
            if j != 0
        )
        # pivot high: 좌우 side봉 모두 현재봉보다 low
        is_pivot_high = all(
            float(df["high"].iloc[i + j]) < high_i
            for j in range(-side, side + 1)
            if j != 0
        )

        if is_pivot_low:
            pivot_lows.append(low_i)
        if is_pivot_high:
            pivot_highs.append(high_i)

    return pivot_lows, pivot_highs


def _near_level(price: float, levels: List[float], pct: float = 0.005) -> Optional[float]:
    """price가 levels 중 하나의 ±pct 내에 있으면 해당 level 반환, 없으면 None.
    IMPROVED: 기본값을 0.5%로 축소 (지지/저항 근처를 더 엄격하게 정의)."""
    for level in levels:
        if level > 0 and abs(price - level) / level <= pct:
            return level
    return None


class BullishEngulfingZoneStrategy(BaseStrategy):
    name = "engulfing_zone"

    MIN_ROWS = 25

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = float(last["close"])

        if len(df) < self.MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"데이터 부족 (최소 {self.MIN_ROWS}행 필요)",
                invalidation="N/A",
            )

        idx = len(df) - 2   # 현재봉 (마지막 완성봉)
        prev_idx = idx - 1  # 이전봉

        open_curr = float(df["open"].iloc[idx])
        close_curr = float(df["close"].iloc[idx])
        open_prev = float(df["open"].iloc[prev_idx])
        close_prev = float(df["close"].iloc[prev_idx])

        body_curr = abs(close_curr - open_curr)
        body_prev = abs(close_prev - open_prev)

        # pivot 탐색
        pivot_lows, pivot_highs = _find_pivots(df, window=20, side=3)

        # ── Bullish Engulfing ─────────────────────────────────────────────
        # 이전봉 음봉, 현재봉 양봉, body 비율 > 1.2 (RELAXED from 1.3)
        is_bearish_prev = close_prev < open_prev
        is_bullish_curr = close_curr > open_curr
        ratio_bull = (body_curr / body_prev) if body_prev > 0 else 0.0
        support_level = _near_level(close_curr, pivot_lows, pct=0.005)  # ±0.5%

        is_bullish_engulfing = (
            is_bearish_prev
            and is_bullish_curr
            and ratio_bull > 1.2
        )

        # ── Bearish Engulfing ─────────────────────────────────────────────
        # 이전봉 양봉, 현재봉 음봉, body 비율 > 1.2 (RELAXED from 1.3)
        is_bullish_prev = close_prev > open_prev
        is_bearish_curr = close_curr < open_curr
        ratio_bear = (body_curr / body_prev) if body_prev > 0 else 0.0
        resistance_level = _near_level(close_curr, pivot_highs, pct=0.005)  # ±0.5%

        is_bearish_engulfing = (
            is_bullish_prev
            and is_bearish_curr
            and ratio_bear > 1.2
        )

        # ── Volume Surge Filter (1.5x average) ────────────────────────────
        vol_curr = float(df["volume"].iloc[idx])
        vol_avg = float(df["volume_sma20"].iloc[idx]) if "volume_sma20" in df.columns else 1.0
        vol_surge = vol_curr >= 1.5 * vol_avg if vol_avg > 0 else True

        # ── RSI Position Filter (RELAXED thresholds) ──────────────────────
        rsi_curr = float(df["rsi14"].iloc[idx]) if "rsi14" in df.columns else 50.0
        # Bullish: RSI < 55 (was < 50), Bearish: RSI > 45 (was > 50)
        rsi_bullish_ok = rsi_curr < 55
        rsi_bearish_ok = rsi_curr > 45

        # ── Confidence ────────────────────────────────────────────────────
        def _get_confidence(ratio: float, near_level: bool = False) -> Confidence:
            # engulfing ratio > 1.7 이면 HIGH (boost if near support/resistance)
            if ratio > 1.7 or (ratio > 1.5 and near_level):
                return Confidence.HIGH
            return Confidence.MEDIUM

        if is_bullish_engulfing and vol_surge and rsi_bullish_ok:
            conf = _get_confidence(ratio_bull, support_level is not None)
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bullish Engulfing Pattern (RSI<55, vol surge). "
                    f"prev_body={body_prev:.2f}, curr_body={body_curr:.2f}, ratio={ratio_bull:.2f}x. "
                    f"RSI={rsi_curr:.1f}, vol_ratio={vol_curr/vol_avg:.2f}x"
                    + (f", near support {support_level:.4f}" if support_level else "")
                ),
                invalidation=f"close {close_curr:.4f} 하회 시 무효",
                bull_case="지지 존에서 강한 매수 반전",
                bear_case="지지 존 이탈 시 추가 하락 위험",
            )

        if is_bearish_engulfing and vol_surge and rsi_bearish_ok:
            conf = _get_confidence(ratio_bear, resistance_level is not None)
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bearish Engulfing Pattern (RSI>45, vol surge). "
                    f"prev_body={body_prev:.2f}, curr_body={body_curr:.2f}, ratio={ratio_bear:.2f}x. "
                    f"RSI={rsi_curr:.1f}, vol_ratio={vol_curr/vol_avg:.2f}x"
                    + (f", near resistance {resistance_level:.4f}" if resistance_level else "")
                ),
                invalidation=f"close {close_curr:.4f} 상회 시 무효",
                bull_case="저항 존 돌파 시 추가 상승 가능",
                bear_case="저항 존에서 강한 매도 반전",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning="Engulfing Zone 패턴 미감지 (HOLD)",
            invalidation="N/A",
        )
