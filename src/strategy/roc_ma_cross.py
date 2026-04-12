"""
ROCMACrossStrategy v2:
- ROC = (close / close.shift(12) - 1) * 100
- ROC_MA = ROC.rolling(3).mean()  (스무딩)
- BUY: ROC_MA crosses above 0 (prev < 0, now >= 0) AND close > EMA50
       AND ROC > 0 (양의 모멘텀 확인)
- SELL: ROC_MA crosses below 0 (prev > 0, now <= 0) AND close < EMA50
        AND ROC < 0 (음의 모멘텀 확인)
- confidence: HIGH if |ROC| > ROC.rolling(20).std() * 2.0 (상향)
- 최소 20행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_ROC_PERIOD = 12
_MA_PERIOD = 3
_STD_PERIOD = 20
_STD_MULT = 2.0  # 2.0으로 상향 (이전 1.5)


class ROCMACrossStrategy(BaseStrategy):
    name = "roc_ma_cross"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        roc = (df["close"] / df["close"].shift(_ROC_PERIOD) - 1) * 100
        roc_ma = roc.rolling(_MA_PERIOD).mean()
        roc_std = roc.rolling(_STD_PERIOD).std()

        roc_ma_now = float(roc_ma.iloc[idx])
        roc_ma_prev = float(roc_ma.iloc[idx - 1])
        roc_now = float(roc.iloc[idx])
        roc_std_now = float(roc_std.iloc[idx])

        close = float(df["close"].iloc[idx])
        ema50 = float(df["ema50"].iloc[idx])

        if pd.isna(roc_ma_now) or pd.isna(roc_ma_prev):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning="ROC_MA 계산 불가 (NaN)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        cross_above = roc_ma_prev < 0 and roc_ma_now >= 0
        cross_below = roc_ma_prev > 0 and roc_ma_now <= 0

        if not pd.isna(roc_std_now) and roc_std_now > 0:
            conf_high = abs(roc_now) > roc_std_now * _STD_MULT
        else:
            conf_high = False

        conf = Confidence.HIGH if conf_high else Confidence.MEDIUM

        # BUY: 추가 필터 - ROC > 0 확인 (양의 모멘텀)
        if cross_above and close > ema50 and roc_now > 0:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"ROC_MA 0 상향 크로스: {roc_ma_prev:.2f} → {roc_ma_now:.2f}, "
                    f"ROC={roc_now:.2f}, close={close:.4f} > EMA50={ema50:.4f}"
                ),
                invalidation="ROC_MA 0 아래 재하락 또는 close < EMA50",
                bull_case=f"ROC_MA 양전 전환, 상승 모멘텀 확인. ROC={roc_now:.2f}",
                bear_case="단순 조정 후 재하락 가능",
            )

        # SELL: 추가 필터 - ROC < 0 확인 (음의 모멘텀)
        if cross_below and close < ema50 and roc_now < 0:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"ROC_MA 0 하향 크로스: {roc_ma_prev:.2f} → {roc_ma_now:.2f}, "
                    f"ROC={roc_now:.2f}, close={close:.4f} < EMA50={ema50:.4f}"
                ),
                invalidation="ROC_MA 0 위로 재상승 또는 close > EMA50",
                bull_case="단순 조정일 수 있음",
                bear_case=f"ROC_MA 음전 전환, 하락 모멘텀 확인. ROC={roc_now:.2f}",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"ROC_MA 크로스 없음 또는 조건 미충족: "
                f"ROC_MA={roc_ma_now:.2f}, close={close:.4f}, EMA50={ema50:.4f}, ROC={roc_now:.2f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
