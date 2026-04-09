"""
CoppockEnhancedStrategy - Coppock 커브 + RSI 필터.

- Coppock = WMA(11) of (ROC(14) + ROC(11))
- WMA(11): weights = [1,2,...,11] / sum(1..11)
- BUY:  Coppock crosses above 0 AND Coppock rising AND RSI > 50
- SELL: Coppock crosses below 0 AND Coppock falling AND RSI < 50
- confidence: |Coppock| > rolling(20).std() → HIGH, else MEDIUM
- 최소 행: 30
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_WMA_PERIOD = 11
_RSI_PERIOD = 14


def _wma(series: pd.Series, period: int) -> pd.Series:
    weights = list(range(1, period + 1))
    total = sum(weights)

    def _calc(x):
        return sum(x[i] * weights[i] for i in range(period)) / total

    return series.rolling(period).apply(_calc, raw=True)


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    return 100 - 100 / (1 + rs)


class CoppockEnhancedStrategy(BaseStrategy):
    name = "coppock_enhanced"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족 (최소 30행 필요)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2
        close = df["close"]

        roc14 = (close - close.shift(14)) / (close.shift(14) + 1e-10) * 100
        roc11 = (close - close.shift(11)) / (close.shift(11) + 1e-10) * 100
        coppock = _wma(roc14 + roc11, _WMA_PERIOD)
        rsi = _rsi(close, _RSI_PERIOD)

        cop_now = float(coppock.iloc[idx])
        cop_prev = float(coppock.iloc[idx - 1])
        rsi_now = float(rsi.iloc[idx])
        entry = float(close.iloc[idx])

        # confidence: |Coppock| > rolling(20).std() → HIGH
        std20 = float(coppock.rolling(20).std().iloc[idx])
        if abs(cop_now) > std20:
            conf = Confidence.HIGH
        else:
            conf = Confidence.MEDIUM

        # BUY: crosses above 0 AND rising AND RSI > 50
        if cop_prev <= 0 and cop_now > 0 and cop_now > cop_prev and rsi_now > 50:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Coppock 0 상향돌파: {cop_prev:.4f}→{cop_now:.4f}, RSI={rsi_now:.1f}>50"
                ),
                invalidation="Coppock이 다시 0 하향 시",
                bull_case=f"Coppock={cop_now:.4f} 상승, RSI={rsi_now:.1f}",
                bear_case="RSI 과열 주의",
            )

        # SELL: crosses below 0 AND falling AND RSI < 50
        if cop_prev >= 0 and cop_now < 0 and cop_now < cop_prev and rsi_now < 50:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Coppock 0 하향돌파: {cop_prev:.4f}→{cop_now:.4f}, RSI={rsi_now:.1f}<50"
                ),
                invalidation="Coppock이 다시 0 상향 시",
                bull_case="단기 반등 가능",
                bear_case=f"Coppock={cop_now:.4f} 하락, RSI={rsi_now:.1f}",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"Coppock 중립: {cop_now:.4f}, RSI={rsi_now:.1f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
