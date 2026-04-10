"""
BreakoutRetestStrategy: 돌파 후 되돌림(retest) 시 진입.

resistance = close.rolling(20).max().shift(3)
support    = close.rolling(20).min().shift(3)

Step 1: 5봉 이내에 resistance 돌파 확인 (prev_close 중 하나가 > resistance)
Step 2: 현재 close가 resistance 근방으로 복귀 (close ≈ resistance ±0.5%)
Step 3: 반등 확인 (close > open)

BUY : 상방 돌파 후 resistance retest + 양봉
SELL: 하방 이탈 후 support retest + 음봉
Confidence HIGH: retest 시 volume < avg_vol (낮은 볼륨 pullback → 매수세 유지)
최소 행: 30
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class BreakoutRetestStrategy(BaseStrategy):
    name = "breakout_retest"

    MIN_ROWS = 30
    ROLLING = 20
    SHIFT = 3
    LOOKBACK = 5      # 돌파 확인 봉 수
    RETEST_TOL = 0.005  # ±0.5%

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
        open_ = df["open"]
        volume = df["volume"]

        resistance = close.rolling(self.ROLLING).max().shift(self.SHIFT)
        support = close.rolling(self.ROLLING).min().shift(self.SHIFT)

        idx = len(df) - 2  # 마지막 완성봉

        curr_close = float(close.iloc[idx])
        curr_open = float(open_.iloc[idx])
        curr_vol = float(volume.iloc[idx])

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

        # 평균 볼륨: 최근 20봉 (완성봉 기준)
        lookback = min(self.ROLLING, idx)
        avg_vol = float(volume.iloc[idx - lookback:idx].mean())

        # 5봉 이내 prev_close 목록 (idx-5 ~ idx-1)
        start = max(0, idx - self.LOOKBACK)
        prev_closes = [float(close.iloc[i]) for i in range(start, idx)]

        # Step 1 + 2 + 3: 상방 돌파 후 retest + 양봉
        breakout_up = any(c > res_val for c in prev_closes)
        retest_res = abs(curr_close - res_val) / res_val <= self.RETEST_TOL
        bullish_candle = curr_close > curr_open

        # Step 1 + 2 + 3: 하방 이탈 후 retest + 음봉
        breakout_down = any(c < sup_val for c in prev_closes)
        retest_sup = abs(curr_close - sup_val) / sup_val <= self.RETEST_TOL
        bearish_candle = curr_close < curr_open

        # confidence: 낮은 볼륨 pullback → HIGH
        low_vol_pullback = curr_vol < avg_vol
        confidence = Confidence.HIGH if low_vol_pullback else Confidence.MEDIUM

        if breakout_up and retest_res and bullish_candle:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"저항({res_val:.4f}) 돌파 후 retest — "
                    f"curr={curr_close:.4f}, 양봉, "
                    f"vol={curr_vol:.1f}/avg={avg_vol:.1f}"
                ),
                invalidation=f"저항선({res_val:.4f}) 하향 이탈 시 청산",
                bull_case=f"retest 성공 + {'저볼륨 pullback' if low_vol_pullback else '볼륨 정상'}",
                bear_case="retest 실패 시 fakeout 가능성",
            )

        if breakout_down and retest_sup and bearish_candle:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"지지({sup_val:.4f}) 이탈 후 retest — "
                    f"curr={curr_close:.4f}, 음봉, "
                    f"vol={curr_vol:.1f}/avg={avg_vol:.1f}"
                ),
                invalidation=f"지지선({sup_val:.4f}) 상향 회복 시 청산",
                bull_case="지지 회복 시 반등 가능",
                bear_case=f"retest 실패 + 하락 지속",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=curr_close,
            reasoning=(
                f"retest 조건 미충족 — close={curr_close:.4f}, "
                f"resistance={res_val:.4f}, support={sup_val:.4f}"
            ),
            invalidation="돌파 + retest + 캔들 확인 시 재평가",
        )
