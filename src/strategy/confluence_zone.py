"""
ConfluenceZoneStrategy: 여러 기술 지표가 동일 가격대를 지지/저항으로 가리킬 때 신호 생성.

레벨:
  - SMA20, SMA50 (동적 지지/저항)
  - Pivot = (prev_high + prev_low + prev_close) / 3
  - BB 중간선 = SMA20 (동일)
  - Round number = round(close, -int(log10(close)))

zone_tolerance = ATR14 * 0.5
confluence_count >= 2 → 신호 조건
confluence_count >= 3 → HIGH confidence
최소 55행 필요
"""

import math
from typing import List, Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 55


def _round_level(close: float) -> float:
    if close <= 0:
        return close
    mag = int(math.log10(close))
    return round(close, -mag)


class ConfluenceZoneStrategy(BaseStrategy):
    name = "confluence_zone"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: 최소 55행 필요",
                invalidation="",
            )

        last = self._last(df)
        prev = df.iloc[-3]  # 직전 완성봉 (Pivot 계산용 prev bar)

        close = float(last["close"])
        open_ = float(last["open"])
        atr14 = float(last["atr14"]) if "atr14" in df.columns else _calc_atr(df)

        tolerance = atr14 * 0.5

        # ── 레벨 계산 ─────────────────────────────────────────────────────────
        sma20 = float(df["close"].iloc[:-1].rolling(20).mean().iloc[-1])
        sma50 = float(df["close"].iloc[:-1].rolling(50).mean().iloc[-1])
        pivot = (float(prev["high"]) + float(prev["low"]) + float(prev["close"])) / 3.0
        round_num = _round_level(close)

        # BB 중간선 = SMA20 (이미 포함됨 → 레벨 목록에서 중복 추가 안 함)
        levels = [sma20, sma50, pivot, round_num]

        # ── Confluence 계산 ───────────────────────────────────────────────────
        def count_near(target: float) -> int:
            return sum(1 for lv in levels if abs(lv - target) <= tolerance)

        # 지지/저항 후보: 레벨들 중 close 근처인 것
        support_levels = [lv for lv in levels if abs(close - lv) <= tolerance and lv <= close + tolerance]
        resistance_levels = [lv for lv in levels if abs(close - lv) <= tolerance and lv >= close - tolerance]

        # 각 레벨에 대해 해당 zone 내 confluence_count 구하기
        best_support_count = 0
        best_support_level = sma20
        for lv in support_levels:
            cnt = count_near(lv)
            if cnt > best_support_count:
                best_support_count = cnt
                best_support_level = lv

        best_resistance_count = 0
        best_resistance_level = sma20
        for lv in resistance_levels:
            cnt = count_near(lv)
            if cnt > best_resistance_count:
                best_resistance_count = cnt
                best_resistance_level = lv

        bull_case = (
            f"SMA20={sma20:.2f} SMA50={sma50:.2f} Pivot={pivot:.2f} "
            f"Round={round_num:.2f} ATR={atr14:.2f} tol={tolerance:.2f}"
        )
        bear_case = bull_case

        # ── BUY 조건 ─────────────────────────────────────────────────────────
        if (
            best_support_count >= 2
            and close > open_
            and support_levels
        ):
            conf = Confidence.HIGH if best_support_count >= 3 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Confluence support: count={best_support_count} "
                    f"near {best_support_level:.2f} (±{tolerance:.2f}). "
                    f"Bullish candle (close > open)."
                ),
                invalidation=f"Close below {best_support_level - tolerance:.2f}",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # ── SELL 조건 ─────────────────────────────────────────────────────────
        if (
            best_resistance_count >= 2
            and close < open_
            and resistance_levels
        ):
            conf = Confidence.HIGH if best_resistance_count >= 3 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Confluence resistance: count={best_resistance_count} "
                    f"near {best_resistance_level:.2f} (±{tolerance:.2f}). "
                    f"Bearish candle (close < open)."
                ),
                invalidation=f"Close above {best_resistance_level + tolerance:.2f}",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"No confluence zone signal. support_count={best_support_count} "
                f"resistance_count={best_resistance_count}."
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )


def _calc_atr(df: pd.DataFrame, period: int = 14) -> float:
    """atr14 컬럼 없을 때 간단 계산."""
    high = df["high"]
    low = df["low"]
    close = df["close"]
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    return float(tr.rolling(period).mean().iloc[-2])
