"""
OpeningMomentumStrategy: 첫 N봉의 모멘텀으로 당일 방향 결정.
- bull_streak: 최근 3봉 연속 양봉 (close > open)
- bear_streak: 최근 3봉 연속 음봉
- mom_5: 5봉 모멘텀
- EMA21 기준 위/아래
- BUY: bull_streak >= 2 AND mom_5 > 0.01 AND close > EMA21
- SELL: bear_streak >= 2 AND mom_5 < -0.01 AND close < EMA21
- confidence: bull_streak == 3 AND mom_5 > 0.02 → HIGH (BUY), 반대 SELL
- 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_MOM_THRESHOLD = 0.01
_MOM_HIGH = 0.02
_STREAK_BUY = 2
_STREAK_HIGH = 3


class OpeningMomentumStrategy(BaseStrategy):
    name = "opening_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2  # 마지막 완성봉 인덱스

        close_series = df["close"]
        open_series = df["open"]

        close_now = float(close_series.iloc[idx])

        # EMA21 계산
        ema21_series = close_series.ewm(span=21, adjust=False).mean()
        ema21 = float(ema21_series.iloc[idx])

        # 5봉 모멘텀
        if idx < 5:
            return self._hold(df, "Not enough data for mom_5")
        close_5ago = float(close_series.iloc[idx - 5])
        if abs(close_5ago) < 1e-10:
            return self._hold(df, "Invalid close_5ago")
        mom_5 = (close_now - close_5ago) / close_5ago

        # 연속 양봉/음봉 streak (최대 3봉 확인)
        bull_streak = 0
        bear_streak = 0
        for i in range(3):
            c = float(close_series.iloc[idx - i])
            o = float(open_series.iloc[idx - i])
            if c > o:
                if i == 0 or bull_streak == i:
                    bull_streak += 1
                else:
                    break
            else:
                break

        for i in range(3):
            c = float(close_series.iloc[idx - i])
            o = float(open_series.iloc[idx - i])
            if c <= o:
                if i == 0 or bear_streak == i:
                    bear_streak += 1
                else:
                    break
            else:
                break

        above_ema = close_now > ema21

        # BUY
        if bull_streak >= _STREAK_BUY and mom_5 > _MOM_THRESHOLD and above_ema:
            if bull_streak >= _STREAK_HIGH and mom_5 > _MOM_HIGH:
                confidence = Confidence.HIGH
            else:
                confidence = Confidence.MEDIUM
            reason = (
                f"bull_streak={bull_streak}, mom_5={mom_5*100:.2f}%, "
                f"close={close_now:.4f} > ema21={ema21:.4f}"
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=reason,
                invalidation=f"Close below EMA21 ({ema21:.4f})",
                bull_case=f"Opening momentum: {bull_streak} consecutive bull candles",
                bear_case="Momentum may fade",
            )

        # SELL
        if bear_streak >= _STREAK_BUY and mom_5 < -_MOM_THRESHOLD and not above_ema:
            if bear_streak >= _STREAK_HIGH and mom_5 < -_MOM_HIGH:
                confidence = Confidence.HIGH
            else:
                confidence = Confidence.MEDIUM
            reason = (
                f"bear_streak={bear_streak}, mom_5={mom_5*100:.2f}%, "
                f"close={close_now:.4f} < ema21={ema21:.4f}"
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=reason,
                invalidation=f"Close above EMA21 ({ema21:.4f})",
                bull_case="Downtrend may reverse",
                bear_case=f"Opening momentum: {bear_streak} consecutive bear candles",
            )

        reason = (
            f"No momentum signal: bull_streak={bull_streak}, bear_streak={bear_streak}, "
            f"mom_5={mom_5*100:.2f}%, above_ema={above_ema}"
        )
        return self._hold(df, reason)

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
