"""
STC (Schaff Trend Cycle) 전략:
- MACD = EMA(close, 23) - EMA(close, 50)
- %K_macd = Stochastic of MACD over 10 periods
- %D_macd = EMA(%K_macd, 3)  → 첫번째 Stochastic
- %K_stc = Stochastic of %D_macd over 10 periods
- STC = EMA(%K_stc, 3)  → 최종 STC (0~100 범위)
- BUY: STC < 25 AND 상승 중 (현재 > 이전)
- SELL: STC > 75 AND 하락 중 (현재 < 이전)
- 최소 80행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 80
_BUY_LEVEL = 25
_SELL_LEVEL = 75
_HIGH_BUY = 10
_HIGH_SELL = 90


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _stoch(series: pd.Series, period: int) -> pd.Series:
    """Stochastic %K of a series"""
    roll_min = series.rolling(period).min()
    roll_max = series.rolling(period).max()
    denom = (roll_max - roll_min).replace(0, 1e-10)
    return 100 * (series - roll_min) / denom


def _calc_stc(df: pd.DataFrame) -> pd.Series:
    macd = _ema(df["close"], 23) - _ema(df["close"], 50)
    k1 = _stoch(macd, 10)
    d1 = _ema(k1, 3)
    k2 = _stoch(d1, 10)
    stc = _ema(k2, 3)
    return stc


class STCStrategy(BaseStrategy):
    name = "stc"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족 (최소 80행 필요)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        stc = _calc_stc(df)

        idx = len(df) - 2
        stc_now = float(stc.iloc[idx])
        stc_prev = float(stc.iloc[idx - 1])
        entry = float(df["close"].iloc[idx])

        # BUY: STC < 25 AND 상승 중
        if stc_now < _BUY_LEVEL and stc_now > stc_prev:
            conf = Confidence.HIGH if stc_now < _HIGH_BUY else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"STC 과매도 구간 상승: STC {stc_prev:.2f} → {stc_now:.2f} "
                    f"(< {_BUY_LEVEL})"
                ),
                invalidation=f"STC가 {_BUY_LEVEL} 이상으로 상승 후 재하락 시",
                bull_case=f"STC={stc_now:.2f} 과매도 반등 신호",
                bear_case="추세 지속 가능성 있음",
            )

        # SELL: STC > 75 AND 하락 중
        if stc_now > _SELL_LEVEL and stc_now < stc_prev:
            conf = Confidence.HIGH if stc_now > _HIGH_SELL else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"STC 과매수 구간 하락: STC {stc_prev:.2f} → {stc_now:.2f} "
                    f"(> {_SELL_LEVEL})"
                ),
                invalidation=f"STC가 {_SELL_LEVEL} 이하로 하락 후 재상승 시",
                bull_case="단기 반등 가능성 있음",
                bear_case=f"STC={stc_now:.2f} 과매수 하락 신호",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"STC 중립: STC={stc_now:.2f} (이전={stc_prev:.2f})",
            invalidation="",
            bull_case="",
            bear_case="",
        )
