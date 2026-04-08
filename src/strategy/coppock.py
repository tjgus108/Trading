"""
Coppock Curve 전략 - 장기 바닥 포착.
- ROC14 = (close - close.shift(14)) / close.shift(14) * 100
- ROC11 = (close - close.shift(11)) / close.shift(11) * 100
- Coppock = WMA(ROC14 + ROC11, 10)
- BUY: Coppock < 0 AND 상승 중 (바닥 반등)
- SELL: Coppock > 0 AND 하락 중 (고점 반락)
- 최소 40행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 40
_WMA_PERIOD = 10
_HIGH_CONF_THRESHOLD = 5.0


def _wma(series: pd.Series, period: int) -> pd.Series:
    """Weighted Moving Average (최신 데이터에 높은 가중치)."""
    weights = list(range(1, period + 1))

    def wma_calc(x):
        return sum(x[i] * weights[i] for i in range(period)) / sum(weights)

    return series.rolling(period).apply(wma_calc, raw=True)


class CoppockStrategy(BaseStrategy):
    name = "coppock"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족 (최소 40행 필요)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2
        roc14 = (df["close"] - df["close"].shift(14)) / df["close"].shift(14) * 100
        roc11 = (df["close"] - df["close"].shift(11)) / df["close"].shift(11) * 100
        coppock = _wma(roc14 + roc11, _WMA_PERIOD)

        cop_now = float(coppock.iloc[idx])
        cop_prev = float(coppock.iloc[idx - 1])
        entry = float(df["close"].iloc[idx])

        # BUY: Coppock < 0 AND 상승 중
        if cop_now < 0 and cop_now > cop_prev:
            conf = Confidence.HIGH if abs(cop_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Coppock 바닥 반등: {cop_prev:.4f} → {cop_now:.4f} (음수 구간 상승)"
                ),
                invalidation="Coppock이 다시 하락 전환 시",
                bull_case=f"Coppock={cop_now:.4f} < 0, 장기 바닥 반등 신호",
                bear_case="아직 음수 구간, 추가 하락 가능",
            )

        # SELL: Coppock > 0 AND 하락 중
        if cop_now > 0 and cop_now < cop_prev:
            conf = Confidence.HIGH if abs(cop_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Coppock 고점 반락: {cop_prev:.4f} → {cop_now:.4f} (양수 구간 하락)"
                ),
                invalidation="Coppock이 다시 상승 전환 시",
                bull_case="단기 반등 가능",
                bear_case=f"Coppock={cop_now:.4f} > 0, 하락 전환 신호",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"Coppock 중립: {cop_now:.4f} (이전: {cop_prev:.4f})",
            invalidation="",
            bull_case="",
            bear_case="",
        )
