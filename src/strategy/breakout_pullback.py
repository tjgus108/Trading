"""
BreakoutPullbackStrategy: 돌파 후 풀백 진입 전략.

resistance = high.rolling(20).max().shift(1)
support    = low.rolling(20).min().shift(1)

BUY : 최근 5봉내 상향 돌파 + 저항선 근처 풀백 + 현재 양봉
SELL: 최근 5봉내 하향 돌파 + 지지선 근처 풀백 + 현재 음봉
Confidence HIGH: volume > 10봉 평균 * 1.5
최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class BreakoutPullbackStrategy(BaseStrategy):
    name = "breakout_pullback"

    MIN_ROWS = 25

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
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        resistance = high.rolling(20, min_periods=1).max().shift(1)
        support = low.rolling(20, min_periods=1).min().shift(1)

        broke_up = close > resistance
        broke_down = close < support

        pullback_to_resistance = (close < resistance) & (close > resistance * 0.99)
        pullback_to_support = (close > support) & (close < support * 1.01)

        broke_up_recently = broke_up.rolling(5, min_periods=1).max().shift(1)
        broke_down_recently = broke_down.rolling(5, min_periods=1).max().shift(1)

        vol_avg = volume.rolling(10, min_periods=1).mean()

        idx = len(df) - 2  # 마지막 완성봉

        curr_close = float(close.iloc[idx])
        curr_vol = float(volume.iloc[idx])
        avg_vol = float(vol_avg.iloc[idx])

        res_val = float(resistance.iloc[idx])
        sup_val = float(support.iloc[idx])

        if pd.isna(res_val) or pd.isna(sup_val):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=curr_close,
                reasoning="resistance/support NaN",
                invalidation="N/A",
            )

        if pd.isna(broke_up_recently.iloc[idx]) or pd.isna(broke_down_recently.iloc[idx]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=curr_close,
                reasoning="돌파 이력 NaN",
                invalidation="N/A",
            )

        is_broke_up_recently = bool(broke_up_recently.iloc[idx])
        is_broke_down_recently = bool(broke_down_recently.iloc[idx])
        is_pullback_to_res = bool(pullback_to_resistance.iloc[idx])
        is_pullback_to_sup = bool(pullback_to_support.iloc[idx])

        prev_close = float(close.iloc[idx - 1]) if idx >= 1 else curr_close
        price_up = curr_close > prev_close
        price_down = curr_close < prev_close

        confidence = Confidence.HIGH if curr_vol > avg_vol * 1.5 else Confidence.MEDIUM

        if is_broke_up_recently and is_pullback_to_res and price_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"상향 돌파 후 저항선 풀백 — "
                    f"close={curr_close:.4f}, resistance={res_val:.4f}, "
                    f"vol={curr_vol:.1f}/avg={avg_vol:.1f}"
                ),
                invalidation=f"저항선({res_val:.4f}) 하향 이탈 시 청산",
                bull_case="저항→지지 전환 + 풀백 진입",
                bear_case="fakeout 후 재하락 가능",
            )

        if is_broke_down_recently and is_pullback_to_sup and price_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"하향 돌파 후 지지선 풀백 — "
                    f"close={curr_close:.4f}, support={sup_val:.4f}, "
                    f"vol={curr_vol:.1f}/avg={avg_vol:.1f}"
                ),
                invalidation=f"지지선({sup_val:.4f}) 상향 회복 시 청산",
                bull_case="반등 시 지지 회복 가능",
                bear_case="지지→저항 전환 + 하락 지속",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=curr_close,
            reasoning=(
                f"풀백 조건 미충족 — close={curr_close:.4f}, "
                f"resistance={res_val:.4f}, support={sup_val:.4f}"
            ),
            invalidation="돌파 + 풀백 + 방향 확인 시 재평가",
        )
