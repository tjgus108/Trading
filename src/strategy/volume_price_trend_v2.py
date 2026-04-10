"""
VolumePriceTrendV2 전략:
- VPT v2 + 시그널 크로스 (히스토그램 기반)
- BUY: vpt_hist > 0 AND vpt_hist > vpt_hist.shift(1) AND vpt > vpt_signal
- SELL: vpt_hist < 0 AND vpt_hist < vpt_hist.shift(1) AND vpt < vpt_signal
- Confidence: HIGH if abs(vpt_hist) > rolling(20) std, else MEDIUM
- 최소 20행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class VolumePriceTrendV2Strategy(BaseStrategy):
    name = "volume_price_trend_v2"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for volume_price_trend_v2",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        close = df["close"]
        volume = df["volume"]

        vpt = (volume * close.pct_change(fill_method=None).fillna(0)).cumsum()
        vpt_signal = vpt.ewm(span=9, adjust=False).mean()
        vpt_hist = vpt - vpt_signal
        vpt_hist_ma = vpt_hist.rolling(3, min_periods=1).mean()  # noqa: F841
        vpt_hist_std = vpt_hist.rolling(20, min_periods=1).std()

        h_now = vpt_hist.iloc[idx]
        h_prev = vpt_hist.iloc[idx - 1]
        vpt_now = vpt.iloc[idx]
        sig_now = vpt_signal.iloc[idx]
        h_std = vpt_hist_std.iloc[idx]

        # NaN 체크
        if any(pd.isna(v) for v in [h_now, h_prev, vpt_now, sig_now, h_std]):
            entry = float(df["close"].iloc[idx])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in vpt_v2 indicators",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        entry = float(df["close"].iloc[idx])
        conf = Confidence.HIGH if abs(h_now) > h_std else Confidence.MEDIUM

        buy_cond = h_now > 0 and h_now > h_prev and vpt_now > sig_now
        sell_cond = h_now < 0 and h_now < h_prev and vpt_now < sig_now

        if buy_cond:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"VPT_v2 히스토그램 상승: "
                    f"vpt_hist={h_now:.4f} > prev={h_prev:.4f}, vpt > signal"
                ),
                invalidation="vpt_hist가 0 아래로 하락",
                bull_case="VPT 히스토그램 양수 확장",
                bear_case="단기 모멘텀 소진 가능",
            )

        if sell_cond:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"VPT_v2 히스토그램 하락: "
                    f"vpt_hist={h_now:.4f} < prev={h_prev:.4f}, vpt < signal"
                ),
                invalidation="vpt_hist가 0 위로 반등",
                bull_case="단기 반등 가능",
                bear_case="VPT 히스토그램 음수 확장",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"VPT_v2 조건 미충족: "
                f"vpt_hist={h_now:.4f}, prev={h_prev:.4f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
