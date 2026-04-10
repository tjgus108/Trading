"""
TrendFollowFilterStrategy: 추세 필터 강화 전략 (ADX + EMA 다중 필터).

간소화 ADX 계산:
  tr = high - low
  dm_up / dm_down → 14봉 평균 DI → ADX

BUY : adx > 20 AND di_up > di_down AND close > ema20 AND ema20 > ema50
SELL: adx > 20 AND di_down > di_up AND close < ema20 AND ema20 < ema50
Confidence HIGH: adx > 35
최소 행: 30
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class TrendFollowFilterStrategy(BaseStrategy):
    name = "trend_follow_filter"

    MIN_ROWS = 30

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

        # ADX 계산
        tr = high - low
        dm_up = (high - high.shift(1)).clip(lower=0)
        dm_down = (low.shift(1) - low).clip(lower=0)
        dm_up = dm_up.where(dm_up > dm_down, 0)
        dm_down = dm_down.where(dm_down > dm_up, 0)

        atr = tr.rolling(14, min_periods=1).mean()
        di_up = dm_up.rolling(14, min_periods=1).mean() / (atr + 1e-10) * 100
        di_down = dm_down.rolling(14, min_periods=1).mean() / (atr + 1e-10) * 100
        adx = (
            (abs(di_up - di_down) / (di_up + di_down + 1e-10) * 100)
            .rolling(14, min_periods=1)
            .mean()
        )

        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()

        idx = len(df) - 2  # 마지막 완성봉

        curr_close = float(close.iloc[idx])
        adx_val = float(adx.iloc[idx])
        di_up_val = float(di_up.iloc[idx])
        di_down_val = float(di_down.iloc[idx])
        ema20_val = float(ema20.iloc[idx])
        ema50_val = float(ema50.iloc[idx])

        if any(
            pd.isna(v) for v in [adx_val, di_up_val, di_down_val, ema20_val, ema50_val]
        ):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=curr_close,
                reasoning="지표 NaN",
                invalidation="N/A",
            )

        confidence = Confidence.HIGH if adx_val > 35 else Confidence.MEDIUM

        buy_signal = (
            adx_val > 20
            and di_up_val > di_down_val
            and curr_close > ema20_val
            and ema20_val > ema50_val
        )
        sell_signal = (
            adx_val > 20
            and di_down_val > di_up_val
            and curr_close < ema20_val
            and ema20_val < ema50_val
        )

        if buy_signal:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"강한 상승 추세 — adx={adx_val:.1f}, "
                    f"di+={di_up_val:.1f}, di-={di_down_val:.1f}, "
                    f"close={curr_close:.4f}>ema20={ema20_val:.4f}>ema50={ema50_val:.4f}"
                ),
                invalidation=f"ema20({ema20_val:.4f}) 하향 이탈 또는 di- 역전 시 청산",
                bull_case=f"adx={adx_val:.1f} 강한 추세 + EMA 정렬",
                bear_case="추세 약화 시 반전 가능",
            )

        if sell_signal:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"강한 하락 추세 — adx={adx_val:.1f}, "
                    f"di+={di_up_val:.1f}, di-={di_down_val:.1f}, "
                    f"close={curr_close:.4f}<ema20={ema20_val:.4f}<ema50={ema50_val:.4f}"
                ),
                invalidation=f"ema20({ema20_val:.4f}) 상향 돌파 또는 di+ 역전 시 청산",
                bull_case="지지 반등 시 추세 전환 가능",
                bear_case=f"adx={adx_val:.1f} 강한 하락 추세 + EMA 역정렬",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=curr_close,
            reasoning=(
                f"추세 조건 미충족 — adx={adx_val:.1f}, "
                f"di+={di_up_val:.1f}, di-={di_down_val:.1f}, "
                f"ema20={ema20_val:.4f}, ema50={ema50_val:.4f}"
            ),
            invalidation="ADX>20 + DI 정렬 + EMA 정렬 시 재평가",
        )
