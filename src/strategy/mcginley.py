"""
McGinleyStrategy: McGinley Dynamic 지표 기반 돌파 전략.

MD(i) = MD(i-1) + (close - MD(i-1)) / (N * (close/MD(i-1))^4)
BUY  : close > MD AND MD 상승 AND 이전 close <= 이전 MD (상향 돌파)
SELL : close < MD AND MD 하락 AND 이전 close >= 이전 MD (하향 돌파)
HOLD : 그 외
"""

import numpy as np
import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class McGinleyStrategy(BaseStrategy):
    name = "mcginley"

    MIN_ROWS = 20
    N = 14
    HIGH_CONF_THRESHOLD = 0.01  # 1% 이격

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족 (최소 20행 필요)",
                invalidation="N/A",
            )

        close_arr = df["close"].values
        md = np.zeros(len(close_arr))
        md[0] = close_arr[0]
        for i in range(1, len(close_arr)):
            ratio = close_arr[i] / md[i - 1] if md[i - 1] != 0 else 1.0
            md[i] = md[i - 1] + (close_arr[i] - md[i - 1]) / (self.N * ratio ** 4)
        md_series = pd.Series(md, index=df.index)

        idx = len(df) - 2

        md_now = float(md_series.iloc[idx])
        md_prev = float(md_series.iloc[idx - 1])
        close_now = float(df["close"].iloc[idx])
        close_prev = float(df["close"].iloc[idx - 1])

        entry_price = close_now

        md_rising = md_now > md_prev
        md_falling = md_now < md_prev
        cross_up = close_now > md_now and md_rising and close_prev <= md_prev
        cross_down = close_now < md_now and md_falling and close_prev >= md_prev

        separation = abs(close_now - md_now) / md_now if md_now != 0 else 0.0
        confidence = Confidence.HIGH if separation > self.HIGH_CONF_THRESHOLD else Confidence.MEDIUM

        if cross_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"close({close_now:.4f}) 이 McGinley({md_now:.4f}) 상향 돌파, "
                    f"MD 상승 중 (이격 {separation*100:.3f}%)"
                ),
                invalidation="close < McGinley Dynamic 시 청산",
                bull_case="McGinley 상향 돌파 — 추세 전환 상승",
                bear_case="돌파가 단기 노이즈일 수 있음",
            )

        if cross_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"close({close_now:.4f}) 이 McGinley({md_now:.4f}) 하향 돌파, "
                    f"MD 하락 중 (이격 {separation*100:.3f}%)"
                ),
                invalidation="close > McGinley Dynamic 시 청산",
                bull_case="돌파가 단기 노이즈일 수 있음",
                bear_case="McGinley 하향 돌파 — 추세 전환 하락",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"McGinley 돌파 없음 — close={close_now:.4f}, "
                f"MD={md_now:.4f}, MD_방향={'상승' if md_rising else '하락' if md_falling else '보합'}"
            ),
            invalidation="돌파 발생 시 재평가",
        )
