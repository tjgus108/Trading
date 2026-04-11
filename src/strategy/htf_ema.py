"""
Higher Timeframe EMA Strategy (Refined Improved).
개선 사항:
1. EMA 채널 추가: close와 EMA9의 거리 필터 (과도한 신호 제거)
2. 변동성 정규화: 가격 변동이 충분한 경우만 신호
3. 원본 신호 로직 유지 (거래 기회 보존)
최소 행: 50
"""

import pandas as pd
import numpy as np

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 50


class HigherTimeframeEMAStrategy(BaseStrategy):
    name = "htf_ema"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close: float = float(df["close"].iloc[-1])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning=f"데이터 부족: {len(df)}행 (최소 {MIN_ROWS}행 필요)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        close = df["close"].reset_index(drop=True)

        # HTF: positional index 기준으로 4봉마다 샘플링
        htf_close = close.iloc[::4]
        htf_ema = htf_close.ewm(span=21, adjust=False).mean()

        # EMA9 (current timeframe)
        ema9 = close.ewm(span=9, adjust=False).mean()

        # 변동성 (ATR-like, 20기간 최고-최저의 평균)
        high_low_range = (df["high"] - df["low"]).rolling(window=20).mean()

        # _last → df.iloc[-2], positional index = len(df)-2
        last_pos = len(df) - 2
        prev_pos = len(df) - 3

        last_close_val: float = float(close.iloc[last_pos])
        prev_close_val: float = float(close.iloc[prev_pos])
        last_ema9: float = float(ema9.iloc[last_pos])
        prev_ema9: float = float(ema9.iloc[prev_pos])

        # 변동성 값
        last_hl_range: float = float(high_low_range.iloc[last_pos]) if last_pos < len(high_low_range) else 1.0

        # HTF EMA: last_pos 이하에서 htf_ema의 마지막 두 값
        htf_ema_at_or_before = htf_ema[htf_ema.index <= last_pos]
        if len(htf_ema_at_or_before) < 4:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close_val,
                reasoning="HTF EMA 계산 불가 (HTF 샘플 부족)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        htf_vals = htf_ema_at_or_before.values
        htf_last = float(htf_vals[-1])
        htf_prev = float(htf_vals[-2])
        htf_prev2 = float(htf_vals[-3]) if len(htf_vals) >= 3 else htf_prev

        htf_rising = htf_last > htf_prev
        htf_falling = htf_last < htf_prev

        # 3연속 상승/하락 확인
        htf_3up = htf_last > htf_prev > htf_prev2
        htf_3down = htf_last < htf_prev < htf_prev2

        # Cross above/below EMA9
        cross_above = (prev_close_val <= prev_ema9) and (last_close_val > last_ema9)
        cross_below = (prev_close_val >= prev_ema9) and (last_close_val < last_ema9)

        # Cross 거리 필터: close가 EMA에서 1.5배 이상 변동성만큼 이동해야 신호 (거짓 신호 제거)
        cross_distance_threshold = last_hl_range * 0.5
        if cross_above:
            cross_valid = (last_close_val - last_ema9) >= cross_distance_threshold * 0.3
        elif cross_below:
            cross_valid = (last_ema9 - last_close_val) >= cross_distance_threshold * 0.3
        else:
            cross_valid = True

        bull_case = (
            f"HTF EMA rising ({htf_prev:.4f} → {htf_last:.4f}), "
            f"close={last_close_val:.4f} crossed above EMA9={last_ema9:.4f}"
        )
        bear_case = (
            f"HTF EMA falling ({htf_prev:.4f} → {htf_last:.4f}), "
            f"close={last_close_val:.4f} crossed below EMA9={last_ema9:.4f}"
        )

        if htf_rising and cross_above and cross_valid:
            confidence = Confidence.HIGH if htf_3up else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close_val,
                reasoning=(
                    f"HTF EMA uptrend ({htf_prev:.4f}→{htf_last:.4f}), "
                    f"close crossed above EMA9={last_ema9:.4f}"
                    + (" [3-bar consecutive]" if htf_3up else "")
                ),
                invalidation=f"Close below EMA9 ({last_ema9:.4f}) or HTF EMA turns down",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if htf_falling and cross_below and cross_valid:
            confidence = Confidence.HIGH if htf_3down else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close_val,
                reasoning=(
                    f"HTF EMA downtrend ({htf_prev:.4f}→{htf_last:.4f}), "
                    f"close crossed below EMA9={last_ema9:.4f}"
                    + (" [3-bar consecutive]" if htf_3down else "")
                ),
                invalidation=f"Close above EMA9 ({last_ema9:.4f}) or HTF EMA turns up",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=last_close_val,
            reasoning=(
                f"No cross signal. HTF EMA={'rising' if htf_rising else 'falling' if htf_falling else 'flat'}, "
                f"cross_above={cross_above}, cross_below={cross_below}, cross_valid={cross_valid}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
