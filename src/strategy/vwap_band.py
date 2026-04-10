"""
VWAPBandStrategy: VWAP ± 표준편차 밴드 기반 평균 회귀 전략.

- vwap = (close * volume).rolling(20, min_periods=1).sum() / volume.rolling(20, min_periods=1).sum()
- deviation = close - vwap
- dev_std = deviation.rolling(20, min_periods=1).std()
- upper_band = vwap + dev_std * 2
- lower_band = vwap - dev_std * 2
- BUY: close < lower_band AND close > close.shift(1)  (하단 밴드 반등)
- SELL: close > upper_band AND close < close.shift(1)  (상단 밴드 반락)
- confidence: HIGH if abs(deviation) > dev_std * 2.5 else MEDIUM
- 최소 데이터: 20행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class VWAPBandStrategy(BaseStrategy):
    name = "vwap_band"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 20:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"데이터 부족: {len(df)} < 20",
                invalidation="",
            )

        close = df["close"]
        volume = df["volume"]

        vwap = (close * volume).rolling(20, min_periods=1).sum() / volume.rolling(20, min_periods=1).sum()
        deviation = close - vwap
        dev_std = deviation.rolling(20, min_periods=1).std()
        upper_band = vwap + dev_std * 2
        lower_band = vwap - dev_std * 2

        idx = len(df) - 2

        c = float(close.iloc[idx])
        c_prev = float(close.iloc[idx - 1])
        vwap_val = vwap.iloc[idx]
        dev_val = deviation.iloc[idx]
        std_val = dev_std.iloc[idx]
        ub_val = upper_band.iloc[idx]
        lb_val = lower_band.iloc[idx]

        # NaN 체크
        if (
            pd.isna(vwap_val)
            or pd.isna(dev_val)
            or pd.isna(std_val)
            or pd.isna(ub_val)
            or pd.isna(lb_val)
        ):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=c,
                reasoning="지표 NaN",
                invalidation="",
            )

        vwap_val = float(vwap_val)
        dev_val = float(dev_val)
        std_val = float(std_val)
        ub_val = float(ub_val)
        lb_val = float(lb_val)

        conf = (
            Confidence.HIGH
            if std_val > 0 and abs(dev_val) > std_val * 2.5
            else Confidence.MEDIUM
        )

        buy_cond = c < lb_val and c > c_prev
        sell_cond = c > ub_val and c < c_prev

        if buy_cond:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"VWAP Band BUY: close({c:.4f}) < lower_band({lb_val:.4f}), "
                    f"반등 확인(prev={c_prev:.4f}). VWAP={vwap_val:.4f}"
                ),
                invalidation=f"close < lower_band({lb_val:.4f}) 지속 시 무효.",
                bull_case="하단 밴드 이탈 후 VWAP 회귀 기대.",
                bear_case="추세 지속 시 추가 하락 가능.",
            )

        if sell_cond:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"VWAP Band SELL: close({c:.4f}) > upper_band({ub_val:.4f}), "
                    f"반락 확인(prev={c_prev:.4f}). VWAP={vwap_val:.4f}"
                ),
                invalidation=f"close > upper_band({ub_val:.4f}) 지속 시 무효.",
                bull_case="추세 지속 시 추가 상승 가능.",
                bear_case="상단 밴드 이탈 후 VWAP 회귀 기대.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=c,
            reasoning=(
                f"VWAP Band HOLD: close={c:.4f}, VWAP={vwap_val:.4f}, "
                f"UB={ub_val:.4f}, LB={lb_val:.4f}"
            ),
            invalidation="",
        )
