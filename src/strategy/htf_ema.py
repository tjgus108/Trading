"""
Higher Timeframe EMA Strategy (Cycle 119 - Tight Cross Filter).
개선 사항:
1. Cross 거리 필터 강화: 0.3 → 0.5 (거짓 신호 제거)
2. RSI extreme 필터: BUY <= 75, SELL >= 25
3. 볼륨 필터: 거래량 > 1.3배면 신뢰도 상향
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
        volume = df["volume"].reset_index(drop=True)

        # HTF: positional index 기준으로 4봉마다 샘플링
        htf_close = close.iloc[::4]
        htf_ema = htf_close.ewm(span=21, adjust=False).mean()

        # EMA9 (current timeframe)
        ema9 = close.ewm(span=9, adjust=False).mean()

        # RSI 계산 (14기간)
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(span=14, adjust=False).mean()
        avg_loss = loss.ewm(span=14, adjust=False).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))

        # 볼륨 필터
        vol_ma = volume.rolling(window=20).mean()
        vol_ratio = volume / (vol_ma + 1e-10)

        # 변동성 (ATR-like)
        high_low_range = (df["high"] - df["low"]).rolling(window=20).mean()

        # 포지션
        last_pos = len(df) - 2
        prev_pos = len(df) - 3

        last_close_val: float = float(close.iloc[last_pos])
        prev_close_val: float = float(close.iloc[prev_pos])
        last_ema9: float = float(ema9.iloc[last_pos])
        prev_ema9: float = float(ema9.iloc[prev_pos])
        last_rsi: float = float(rsi.iloc[last_pos]) if last_pos < len(rsi) else 50.0
        last_vol_ratio: float = float(vol_ratio.iloc[last_pos]) if last_pos < len(vol_ratio) else 1.0
        last_hl_range: float = float(high_low_range.iloc[last_pos]) if last_pos < len(high_low_range) else 1.0

        # HTF EMA
        htf_ema_at_or_before = htf_ema[htf_ema.index <= last_pos]
        if len(htf_ema_at_or_before) < 4:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close_val,
                reasoning="HTF EMA 계산 불가",
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
        htf_3up = htf_last > htf_prev > htf_prev2
        htf_3down = htf_last < htf_prev < htf_prev2

        # Cross
        cross_above = (prev_close_val <= prev_ema9) and (last_close_val > last_ema9)
        cross_below = (prev_close_val >= prev_ema9) and (last_close_val < last_ema9)

        # 거리 필터 강화: 0.5배 변동성 이상 이동 필요
        cross_distance_threshold = last_hl_range * 0.5
        if cross_above:
            cross_valid = (last_close_val - last_ema9) >= cross_distance_threshold * 0.5  # 강화됨
        elif cross_below:
            cross_valid = (last_ema9 - last_close_val) >= cross_distance_threshold * 0.5
        else:
            cross_valid = True

        # RSI extreme 필터
        rsi_buy_ok = last_rsi <= 75
        rsi_sell_ok = last_rsi >= 25

        vol_boost = last_vol_ratio > 1.3

        bull_case = (
            f"HTF EMA rising ({htf_prev:.4f} → {htf_last:.4f}), "
            f"close={last_close_val:.4f} crossed above EMA9={last_ema9:.4f}, "
            f"RSI={last_rsi:.1f}, Vol={last_vol_ratio:.2f}x"
        )
        bear_case = (
            f"HTF EMA falling ({htf_prev:.4f} → {htf_last:.4f}), "
            f"close={last_close_val:.4f} crossed below EMA9={last_ema9:.4f}, "
            f"RSI={last_rsi:.1f}, Vol={last_vol_ratio:.2f}x"
        )

        if htf_rising and cross_above and cross_valid and rsi_buy_ok:
            if (vol_boost and htf_3up) or (htf_3up and last_rsi < 60):
                confidence = Confidence.HIGH
            else:
                confidence = Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close_val,
                reasoning=(
                    f"HTF EMA uptrend ({htf_prev:.4f}→{htf_last:.4f}), "
                    f"close crossed above EMA9={last_ema9:.4f}, "
                    f"distance={abs(last_close_val - last_ema9):.4f} (threshold={cross_distance_threshold * 0.5:.4f}), "
                    f"RSI={last_rsi:.1f}"
                    + (f" [Vol spike {last_vol_ratio:.2f}x]" if vol_boost else "")
                    + (" [3-bar]" if htf_3up else "")
                ),
                invalidation=f"Close below EMA9 ({last_ema9:.4f}) or HTF EMA turns down",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if htf_falling and cross_below and cross_valid and rsi_sell_ok:
            if (vol_boost and htf_3down) or (htf_3down and last_rsi > 40):
                confidence = Confidence.HIGH
            else:
                confidence = Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close_val,
                reasoning=(
                    f"HTF EMA downtrend ({htf_prev:.4f}→{htf_last:.4f}), "
                    f"close crossed below EMA9={last_ema9:.4f}, "
                    f"distance={abs(last_ema9 - last_close_val):.4f} (threshold={cross_distance_threshold * 0.5:.4f}), "
                    f"RSI={last_rsi:.1f}"
                    + (f" [Vol spike {last_vol_ratio:.2f}x]" if vol_boost else "")
                    + (" [3-bar]" if htf_3down else "")
                ),
                invalidation=f"Close above EMA9 ({last_ema9:.4f}) or HTF EMA turns up",
                bull_case=bear_case,
                bear_case=bull_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=last_close_val,
            reasoning=(
                f"No cross signal. HTF EMA={'rising' if htf_rising else 'falling' if htf_falling else 'flat'}, "
                f"cross_above={cross_above}, cross_below={cross_below}, cross_valid={cross_valid}, "
                f"RSI={last_rsi:.1f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
