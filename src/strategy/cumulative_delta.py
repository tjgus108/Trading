"""
CumulativeDelta 전략:
- 봉 구조로 매수/매도 거래량 추정 후 누적 델타 계산
- BUY: cum_delta가 cum_delta_ma를 상향 돌파 AND cum_delta < 0 (음수에서 회복)
- SELL: cum_delta가 cum_delta_ma를 하향 돌파 AND cum_delta > 0
- Confidence: HIGH if abs(cum_delta) > rolling std, else MEDIUM
- 최소 30행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


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
        open_p = df["open"]
        high = df["high"]
        low = df["low"]
        vol = df["volume"]

        # 봉 구조로 매수/매도 거래량 추정
        body_ratio = (close - open_p) / (high - low + 1e-10)
        buy_vol = vol * (0.5 + body_ratio.clip(-1, 1) / 2)
        sell_vol = vol - buy_vol

        delta = buy_vol - sell_vol
        cum_delta = delta.rolling(20).sum()
        cum_delta_ma = cum_delta.rolling(5).mean()
        cum_delta_std = cum_delta.rolling(20).std()

        cd_now = cum_delta.iloc[idx]
        cd_prev = cum_delta.iloc[idx - 1]
        ma_now = cum_delta_ma.iloc[idx]
        ma_prev = cum_delta_ma.iloc[idx - 1]
        cd_std = cum_delta_std.iloc[idx]

        # NaN 체크
        if any(
            pd.isna(v) for v in [cd_now, cd_prev, ma_now, ma_prev, cd_std]
        ):
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

        cross_up = cd_prev <= ma_prev and cd_now > ma_now
        cross_down = cd_prev >= ma_prev and cd_now < ma_now

        entry = float(df["close"].iloc[idx])
        conf = Confidence.HIGH if abs(cd_now) > cd_std else Confidence.MEDIUM

        if cross_up and cd_now < 0:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"CumDelta 상향 돌파 (음수 회복): "
                    f"cum_delta={cd_now:.2f} > ma={ma_now:.2f}, cum_delta<0"
                ),
                invalidation="cum_delta가 다시 ma 아래로",
                bull_case="누적 델타 음수에서 매수 전환",
                bear_case="단기 반등일 수 있음",
            )

        if cross_down and cd_now > 0:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"CumDelta 하향 돌파 (양수에서 하락): "
                    f"cum_delta={cd_now:.2f} < ma={ma_now:.2f}, cum_delta>0"
                ),
                invalidation="cum_delta가 다시 ma 위로",
                bull_case="단기 반등일 수 있음",
                bear_case="누적 델타 양수에서 매도 전환",
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
