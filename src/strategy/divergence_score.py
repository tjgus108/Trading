"""
DivergenceScore 전략:
- 여러 오실레이터(RSI, CCI, Momentum)의 방향을 점수화하여 신호 생성
- score = rsi_dir + cci_dir + mom_dir  (-3 ~ +3)
- BUY:  score >= 2 AND score > prev_score
- SELL: score <= -2 AND score < prev_score
- HOLD: 그 외
- confidence: HIGH if |score| == 3 else MEDIUM
- 최소 데이터: 35행
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35
_RSI_PERIOD = 14
_CCI_PERIOD = 20
_MOM_PERIOD = 10
_BUY_SCORE = 2
_SELL_SCORE = -2


def _calc_rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def _calc_cci(close: pd.Series, period: int) -> pd.Series:
    rolling_mean = close.rolling(period).mean()
    rolling_mad = close.rolling(period).apply(
        lambda x: float(np.abs(x - x.mean()).mean()), raw=True
    )
    return (close - rolling_mean) / (0.015 * rolling_mad.replace(0, 1e-10))


class DivergenceScoreStrategy(BaseStrategy):
    name = "divergence_score"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold_safe(df, "Insufficient data for DivergenceScore (need 35 rows)")

        close = df["close"]

        rsi = _calc_rsi(close, _RSI_PERIOD)
        cci = _calc_cci(close, _CCI_PERIOD)
        mom = close.pct_change(_MOM_PERIOD)

        idx = len(df) - 2

        if idx < 1:
            return self._hold_safe(df, "Insufficient data for DivergenceScore (idx < 1)")

        for val, label in [
            (rsi.iloc[idx], "rsi"),
            (rsi.iloc[idx - 1], "prev_rsi"),
            (cci.iloc[idx], "cci"),
            (cci.iloc[idx - 1], "prev_cci"),
            (mom.iloc[idx], "mom"),
            (mom.iloc[idx - 1], "prev_mom"),
        ]:
            if pd.isna(val):
                return self._hold_safe(df, f"Insufficient data for DivergenceScore ({label} is NaN)")

        rsi_now = float(rsi.iloc[idx])
        rsi_prev = float(rsi.iloc[idx - 1])
        cci_now = float(cci.iloc[idx])
        cci_prev = float(cci.iloc[idx - 1])
        mom_now = float(mom.iloc[idx])
        mom_prev = float(mom.iloc[idx - 1])
        close_now = float(close.iloc[idx])

        # Score calculation
        rsi_dir = 1 if rsi_now > rsi_prev else -1
        cci_dir = 1 if cci_now > cci_prev else -1
        mom_dir = 1 if mom_now > 0 else -1

        prev_rsi_dir = 1 if rsi_prev > float(rsi.iloc[idx - 2] if idx >= 2 else rsi_prev) else -1
        prev_cci_dir = 1 if cci_prev > float(cci.iloc[idx - 2] if idx >= 2 else cci_prev) else -1
        prev_mom_val = float(mom.iloc[idx - 1])
        prev_mom_dir = 1 if prev_mom_val > 0 else -1

        score = rsi_dir + cci_dir + mom_dir
        prev_score = prev_rsi_dir + prev_cci_dir + prev_mom_dir

        ctx = (
            f"rsi={rsi_now:.1f} cci={cci_now:.1f} mom={mom_now:.4f} score={score}"
        )

        if score >= _BUY_SCORE and score > prev_score:
            conf = Confidence.HIGH if abs(score) == 3 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"Divergence BUY: score={score} > prev_score={prev_score}, "
                    f"rsi={rsi_now:.1f} cci={cci_now:.1f} mom={mom_now:.4f}"
                ),
                invalidation=f"Score drops below {_BUY_SCORE} or momentum reverses",
                bull_case=ctx,
                bear_case=ctx,
            )

        if score <= _SELL_SCORE and score < prev_score:
            conf = Confidence.HIGH if abs(score) == 3 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"Divergence SELL: score={score} < prev_score={prev_score}, "
                    f"rsi={rsi_now:.1f} cci={cci_now:.1f} mom={mom_now:.4f}"
                ),
                invalidation=f"Score rises above {_SELL_SCORE} or momentum reverses",
                bull_case=ctx,
                bear_case=ctx,
            )

        return self._hold_safe(
            df,
            f"No signal: score={score} prev_score={prev_score} rsi={rsi_now:.1f}",
        )

    def _hold_safe(self, df: Optional[pd.DataFrame], reason: str) -> Signal:
        if df is None or len(df) < 2:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=reason,
                invalidation="",
            )
        idx = len(df) - 2
        close = float(df["close"].iloc[idx])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
        )
