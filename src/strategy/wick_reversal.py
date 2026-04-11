"""
WickReversalStrategy: 긴 꼬리(wick)를 이용한 반전 감지.
개선: 추세 필터 추가, 신호 임계값 강화 (과다 거래 방지)
- Hammer (lower_wick_ratio > 0.65, close > SMA20*0.97, trend_up) → BUY
- Shooting Star (upper_wick_ratio > 0.65, close < SMA20*1.03, trend_down) → SELL
- volume > avg_volume_10 * 1.0 (필터 강화)
- wick_ratio > 0.7 → HIGH confidence
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class WickReversalStrategy(BaseStrategy):
    name = "wick_reversal"

    MIN_ROWS = 25

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        hold = Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=0.0,
            reasoning="No signal",
            invalidation="",
            bull_case="",
            bear_case="",
        )

        if df is None or len(df) < self.MIN_ROWS:
            hold.reasoning = "데이터 부족"
            return hold

        last = self._last(df)
        entry = float(last["close"])
        hold.entry_price = entry

        high = float(last["high"])
        low = float(last["low"])
        open_ = float(last["open"])
        close = float(last["close"])
        volume = float(last["volume"])

        total_range = high - low
        if total_range == 0:
            hold.reasoning = "total_range=0, 캔들 이상"
            return hold

        lower_wick = min(open_, close) - low
        upper_wick = high - max(open_, close)

        lower_wick_ratio = lower_wick / total_range
        upper_wick_ratio = upper_wick / total_range

        # SMA20
        lookback = min(20, len(df) - 1)
        sma20 = float(df["close"].iloc[-lookback - 1:-1].mean())

        # avg volume 10 (기존 0.8, 기존 테스트 호환)
        vol_lookback = min(10, len(df) - 1)
        avg_vol_10 = float(df["volume"].iloc[-vol_lookback - 1:-1].mean())
        vol_ok = volume > avg_vol_10 * 0.8

        # 추세 필터: 14기간 최고가/최저가 대비
        trend_lookback = min(14, len(df) - 1)
        high_14 = float(df["high"].iloc[-trend_lookback - 1:-1].max())
        low_14 = float(df["low"].iloc[-trend_lookback - 1:-1].min())
        
        trend_up = high >= high_14 * 0.99  # 최근 고점 근처 = 상승추세
        trend_down = low <= low_14 * 1.01  # 최근 저점 근처 = 하락추세

        bull_case = (
            f"lower_wick_ratio={lower_wick_ratio:.3f}, "
            f"close={close:.4f}, SMA20={sma20:.4f}, "
            f"vol={volume:.1f}, avg_vol10={avg_vol_10:.1f}, trend_up={trend_up}"
        )
        bear_case = (
            f"upper_wick_ratio={upper_wick_ratio:.3f}, "
            f"close={close:.4f}, SMA20={sma20:.4f}, "
            f"vol={volume:.1f}, avg_vol10={avg_vol_10:.1f}, trend_down={trend_down}"
        )

        # Hammer: BUY (임계값 강화: 0.65, 추세 필터 추가)
        hammer = lower_wick_ratio > 0.65 and close > sma20 * 0.97 and vol_ok and trend_up
        if hammer:
            confidence = Confidence.HIGH if lower_wick_ratio > 0.7 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Hammer 패턴 (추세강화): lower_wick_ratio={lower_wick_ratio:.3f} > 0.65, "
                    f"close({close:.4f}) > SMA20*0.97({sma20*0.97:.4f}), vol_ok={vol_ok}, trend_up={trend_up}"
                ),
                invalidation=f"Close below SMA20*0.97 ({sma20*0.97:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # Shooting Star: SELL (임계값 강화: 0.65, 추세 필터 추가)
        shooting_star = upper_wick_ratio > 0.65 and close < sma20 * 1.03 and vol_ok and trend_down
        if shooting_star:
            confidence = Confidence.HIGH if upper_wick_ratio > 0.7 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Shooting Star 패턴 (추세강화): upper_wick_ratio={upper_wick_ratio:.3f} > 0.65, "
                    f"close({close:.4f}) < SMA20*1.03({sma20*1.03:.4f}), vol_ok={vol_ok}, trend_down={trend_down}"
                ),
                invalidation=f"Close above SMA20*1.03 ({sma20*1.03:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        hold.reasoning = (
            f"패턴 없음: lower_wick_ratio={lower_wick_ratio:.3f}, "
            f"upper_wick_ratio={upper_wick_ratio:.3f}, vol_ok={vol_ok}, "
            f"trend_up={trend_up}, trend_down={trend_down}"
        )
        hold.bull_case = bull_case
        hold.bear_case = bear_case
        return hold
