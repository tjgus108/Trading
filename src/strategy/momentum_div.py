"""
MomentumDivergenceStrategy: 가격 모멘텀과 볼륨 모멘텀의 다이버전스 전략.

- price_mom = (close - close.shift(10)) / close.shift(10)
- vol_mom   = (volume - volume.rolling(10).mean()) / volume.rolling(10).mean()
- Bullish divergence: price_mom < 0 AND vol_mom > 0.5  (가격 하락 중 볼륨 증가)
- Bearish divergence: price_mom > 0 AND vol_mom < -0.3 (가격 상승 중 볼륨 감소)
- BUY:  bullish divergence AND RSI14 < 50
- SELL: bearish divergence AND RSI14 > 50
- confidence: HIGH if |vol_mom| > 1.0
- 최소 행: 20
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_RSI_PERIOD = 14
_MOM_PERIOD = 10


def _calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))


class MomentumDivergenceStrategy(BaseStrategy):
    name = "momentum_div"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="데이터 부족: 모멘텀 다이버전스 계산 불가",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        close = df["close"]
        volume = df["volume"]

        price_mom = (close - close.shift(_MOM_PERIOD)) / close.shift(_MOM_PERIOD)
        vol_rolling_mean = volume.rolling(_MOM_PERIOD).mean()
        vol_mom = (volume - vol_rolling_mean) / vol_rolling_mean.replace(0, float("nan"))
        rsi = _calc_rsi(close, _RSI_PERIOD)

        idx = len(df) - 2  # 마지막 완성 캔들

        pm = float(price_mom.iloc[idx])
        vm = float(vol_mom.iloc[idx])
        rsi_val = float(rsi.iloc[idx])
        close_val = float(close.iloc[idx])

        info = (
            f"price_mom={pm:.4f}, vol_mom={vm:.4f}, RSI14={rsi_val:.1f}"
        )
        bull_case = f"가격 하락 중 볼륨 급증. {info}"
        bear_case = f"가격 상승 중 볼륨 감소. {info}"

        bullish_div = pm < 0 and vm > 0.5
        bearish_div = pm > 0 and vm < -0.3

        if bullish_div and rsi_val < 50:
            conf = Confidence.HIGH if abs(vm) > 1.0 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Bullish divergence: 가격 하락 중 볼륨 증가, RSI<50. {info}",
                invalidation="price_mom > 0 또는 RSI >= 50",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if bearish_div and rsi_val > 50:
            conf = Confidence.HIGH if abs(vm) > 1.0 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Bearish divergence: 가격 상승 중 볼륨 감소, RSI>50. {info}",
                invalidation="price_mom < 0 또는 RSI <= 50",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_val,
            reasoning=f"다이버전스 조건 미충족. {info}",
            invalidation="bullish/bearish divergence 조건 충족 시 재평가",
            bull_case=bull_case,
            bear_case=bear_case,
        )
