"""
TRIX (Triple Exponential Average) 전략:
- BUY: TRIX > 0 AND TRIX가 Signal 상향 크로스
- SELL: TRIX < 0 AND TRIX가 Signal 하향 크로스
- Confidence: HIGH if |TRIX| > 0.1, MEDIUM otherwise
- 최소 60행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_PERIOD = 15
_SIGNAL_PERIOD = 9
_MIN_ROWS = 60
_HIGH_CONF_THRESHOLD = 0.1


def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


class TRIXStrategy(BaseStrategy):
    name = "trix"

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

        ema1 = _ema(df["close"], _PERIOD)
        ema2 = _ema(ema1, _PERIOD)
        ema3 = _ema(ema2, _PERIOD)
        trix = (ema3 - ema3.shift(1)) / ema3.shift(1) * 100
        signal_line = trix.rolling(_SIGNAL_PERIOD).mean()

        idx = len(df) - 2
        trix_now = float(trix.iloc[idx])
        trix_prev = float(trix.iloc[idx - 1])
        sig_now = float(signal_line.iloc[idx])
        sig_prev = float(signal_line.iloc[idx - 1])

        entry = float(df["close"].iloc[idx])

        # BUY: TRIX > 0 AND 상향 크로스
        if trix_now > 0 and trix_prev <= sig_prev and trix_now > sig_now:
            conf = Confidence.HIGH if abs(trix_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"TRIX 상향 크로스: TRIX {trix_prev:.4f} → {trix_now:.4f}, "
                    f"Signal {sig_prev:.4f} → {sig_now:.4f}"
                ),
                invalidation="TRIX가 다시 Signal 하향 크로스 시",
                bull_case=f"TRIX {trix_now:.4f} > 0, 모멘텀 상승",
                bear_case="단기 반등일 수 있음",
            )

        # SELL: TRIX < 0 AND 하향 크로스
        if trix_now < 0 and trix_prev >= sig_prev and trix_now < sig_now:
            conf = Confidence.HIGH if abs(trix_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"TRIX 하향 크로스: TRIX {trix_prev:.4f} → {trix_now:.4f}, "
                    f"Signal {sig_prev:.4f} → {sig_now:.4f}"
                ),
                invalidation="TRIX가 다시 Signal 상향 크로스 시",
                bull_case="단기 반등일 수 있음",
                bear_case=f"TRIX {trix_now:.4f} < 0, 모멘텀 하락",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"TRIX 중립: TRIX={trix_now:.4f}, Signal={sig_now:.4f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
