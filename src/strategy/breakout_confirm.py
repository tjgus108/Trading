"""
BreakoutConfirmationStrategy: 돌파 + 다음 봉 확인으로 가짜 돌파 필터링.

resistance = close.rolling(20).max().shift(2)  (현재봉 제외 20봉 최고)
support    = close.rolling(20).min().shift(2)

Confirmed breakout up  : prev_close > resistance AND curr_close > resistance AND volume > avg_vol * 1.3
Confirmed breakdown    : prev_close < support    AND curr_close < support    AND volume > avg_vol * 1.3

BUY : confirmed breakout up
SELL: confirmed breakdown
Confidence HIGH: volume > avg_vol * 2.0
최소 행: 25
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class BreakoutConfirmationStrategy(BaseStrategy):
    name = "breakout_confirm"

    MIN_ROWS = 25
    ROLLING = 20
    VOL_MULT = 1.3
    HIGH_CONF_VOL_MULT = 2.0

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
        volume = df["volume"]

        resistance = close.rolling(self.ROLLING).max().shift(2)
        support = close.rolling(self.ROLLING).min().shift(2)

        idx = len(df) - 2  # 마지막 완성봉

        curr_close = float(close.iloc[idx])
        prev_close = float(close.iloc[idx - 1])
        curr_vol = float(volume.iloc[idx])

        res_val = float(resistance.iloc[idx])
        sup_val = float(support.iloc[idx])

        # 평균 볼륨: 최근 20봉 (현재봉 제외)
        lookback = min(self.ROLLING, len(df) - 1)
        avg_vol = float(volume.iloc[-(lookback + 1):-1].mean())

        vol_ok = curr_vol > avg_vol * self.VOL_MULT
        high_conf = curr_vol > avg_vol * self.HIGH_CONF_VOL_MULT
        confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM

        confirmed_up = (
            not pd.isna(res_val)
            and prev_close > res_val
            and curr_close > res_val
            and vol_ok
        )
        confirmed_down = (
            not pd.isna(sup_val)
            and prev_close < sup_val
            and curr_close < sup_val
            and vol_ok
        )

        if confirmed_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"저항선({res_val:.4f}) 상향 돌파 확인 — "
                    f"prev={prev_close:.4f}, curr={curr_close:.4f}, "
                    f"vol={curr_vol:.1f} > avg*{self.VOL_MULT}={avg_vol*self.VOL_MULT:.1f}"
                ),
                invalidation=f"저항선({res_val:.4f}) 하향 복귀 시 청산",
                bull_case=f"2봉 연속 저항 돌파 + 볼륨 {curr_vol/avg_vol:.1f}x",
                bear_case="돌파 후 저항이 지지로 전환 실패 시 fakeout",
            )

        if confirmed_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"지지선({sup_val:.4f}) 하향 이탈 확인 — "
                    f"prev={prev_close:.4f}, curr={curr_close:.4f}, "
                    f"vol={curr_vol:.1f} > avg*{self.VOL_MULT}={avg_vol*self.VOL_MULT:.1f}"
                ),
                invalidation=f"지지선({sup_val:.4f}) 상향 회복 시 청산",
                bull_case="이탈 후 지지 회복 시 반등 가능",
                bear_case=f"2봉 연속 지지 이탈 + 볼륨 {curr_vol/avg_vol:.1f}x",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=curr_close,
            reasoning=(
                f"돌파 미확인 — close={curr_close:.4f}, "
                f"resistance={res_val:.4f}, support={sup_val:.4f}, "
                f"vol={curr_vol:.1f}/avg={avg_vol:.1f}"
            ),
            invalidation="저항 또는 지지 돌파 + 볼륨 급증 시 재평가",
        )
