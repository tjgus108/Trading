"""
CumulativeDelta 전략:
- 누적 매수/매도 불균형 (Cumulative Delta)
- up_vol = volume * (close >= open).astype(float)
- down_vol = volume * (close < open).astype(float)
- delta = up_vol - down_vol
- cum_delta = delta.rolling(15, min_periods=1).sum()
- cum_delta_ma = cum_delta.rolling(5, min_periods=1).mean()
- BUY: cum_delta > cum_delta_ma AND cum_delta > 0 AND close > close_ma
- SELL: cum_delta < cum_delta_ma AND cum_delta < 0 AND close < close_ma
- Confidence: HIGH if abs(cum_delta) > rolling(20) std, else MEDIUM
- 최소 20행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class CumulativeDeltaStrategy(BaseStrategy):
    name = "cumulative_delta"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for cumulative_delta",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        close = df["close"]
        open_ = df["open"]
        volume = df["volume"]

        up_vol = volume * (close >= open_).astype(float)
        down_vol = volume * (close < open_).astype(float)
        delta = up_vol - down_vol

        cum_delta = delta.rolling(15, min_periods=1).sum()
        cum_delta_ma = cum_delta.rolling(5, min_periods=1).mean()
        cum_delta_std = cum_delta.rolling(20, min_periods=1).std()
        close_ma = close.ewm(span=10, adjust=False).mean()

        cd_now = cum_delta.iloc[idx]
        ma_now = cum_delta_ma.iloc[idx]
        cd_std = cum_delta_std.iloc[idx]
        cl_now = close.iloc[idx]
        cl_ma_now = close_ma.iloc[idx]

        # NaN 체크
        if any(pd.isna(v) for v in [cd_now, ma_now, cd_std, cl_now, cl_ma_now]):
            entry = float(df["close"].iloc[idx])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in cumulative delta indicators",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        entry = float(cl_now)
        conf = Confidence.HIGH if abs(cd_now) > cd_std else Confidence.MEDIUM

        buy_cond = cd_now > ma_now and cd_now > 0 and cl_now > cl_ma_now
        sell_cond = cd_now < ma_now and cd_now < 0 and cl_now < cl_ma_now

        if buy_cond:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"CumDelta 매수: cum_delta={cd_now:.2f} > ma={ma_now:.2f}, "
                    f"cum_delta>0, close={cl_now:.2f} > close_ma={cl_ma_now:.2f}"
                ),
                invalidation="cum_delta가 0 아래로 또는 close < close_ma",
                bull_case="누적 델타 양수 + 가격 MA 위",
                bear_case="단기 모멘텀 소진 가능",
            )

        if sell_cond:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"CumDelta 매도: cum_delta={cd_now:.2f} < ma={ma_now:.2f}, "
                    f"cum_delta<0, close={cl_now:.2f} < close_ma={cl_ma_now:.2f}"
                ),
                invalidation="cum_delta가 0 위로 또는 close > close_ma",
                bull_case="단기 반등 가능",
                bear_case="누적 델타 음수 + 가격 MA 아래",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"CumDelta 조건 미충족: "
                f"cum_delta={cd_now:.2f}, ma={ma_now:.2f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
