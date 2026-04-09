"""
VolumeClimaxStrategy: 극단적 거래량과 함께 추세 소진 감지.
- Buying climax: climax_vol AND 음봉 (close < open) → SELL
- Selling climax: climax_vol AND 양봉 (close > open) → BUY
- 추가 조건: RSI14 < 30 (BUY) or RSI14 > 70 (SELL)
- confidence: volume > avg * 5.0 → HIGH, else MEDIUM
- 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_VOL_LOOKBACK = 20
_CLIMAX_MULT = 3.0
_HIGH_CONF_MULT = 5.0
_RSI_PERIOD = 14
_RSI_OS = 30.0
_RSI_OB = 70.0


def _calc_rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    # avg_loss=0 → no losses → RSI=100; use fillna to avoid divide-by-zero NaN
    rs = avg_gain / avg_loss.where(avg_loss != 0, other=float("nan"))
    rsi = 100 - (100 / (1 + rs))
    # avg_loss == 0 means pure uptrend → RSI=100
    rsi = rsi.where(avg_loss != 0, other=100.0)
    return rsi


class VolumeClimaxStrategy(BaseStrategy):
    name = "volume_climax"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        signal_idx = len(df) - 2
        last = self._last(df)

        close = float(last["close"])
        open_ = float(last["open"])
        volume = float(last["volume"])

        # 볼륨 평균: 신호 봉 이전 20개 봉
        vol_window = df["volume"].iloc[max(0, signal_idx - _VOL_LOOKBACK):signal_idx]
        vol_avg = float(vol_window.mean()) if len(vol_window) > 0 else 1.0
        vol_ratio = volume / vol_avg if vol_avg > 0 else 0.0

        # RSI14
        rsi_series = _calc_rsi(df["close"], _RSI_PERIOD)
        rsi = float(rsi_series.iloc[signal_idx])

        climax_vol = vol_ratio > _CLIMAX_MULT
        bull_candle = close > open_   # 양봉
        bear_candle = close < open_   # 음봉

        # Selling climax: 극단적 거래량 + 양봉 = 하락 추세 소진 → BUY
        selling_climax = climax_vol and bull_candle
        # Buying climax: 극단적 거래량 + 음봉 = 상승 추세 소진 → SELL
        buying_climax = climax_vol and bear_candle

        info = (
            f"vol_ratio={vol_ratio:.2f} rsi={rsi:.1f} close={close:.4f} open={open_:.4f}"
        )

        if selling_climax and rsi < _RSI_OS:
            confidence = Confidence.HIGH if vol_ratio > _HIGH_CONF_MULT else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Selling climax (하락 소진): {info}",
                invalidation=f"RSI 30 초과 또는 음봉 전환",
                bull_case=f"극단적 거래량({vol_ratio:.1f}x) + RSI과매도({rsi:.1f})",
                bear_case="추세 소진 실패 가능성",
            )

        if buying_climax and rsi > _RSI_OB:
            confidence = Confidence.HIGH if vol_ratio > _HIGH_CONF_MULT else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Buying climax (상승 소진): {info}",
                invalidation=f"RSI 70 미만 또는 양봉 전환",
                bull_case="추세 소진 실패 가능성",
                bear_case=f"극단적 거래량({vol_ratio:.1f}x) + RSI과매수({rsi:.1f})",
            )

        return self._hold(df, f"No climax signal: {info}", info, info)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        close = float(df.iloc[-2]["close"]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
