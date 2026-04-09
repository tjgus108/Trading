"""
Larry Williams Volatility Breakout 전략:
- 전일 변동폭 = 전일 high - 전일 low
- 돌파 기준: 전일 종가 + k * 전일 변동폭 (k=0.5)
- BUY:  현재 close > 전일 close + 0.5 * 전일 변동폭
        AND 볼륨 >= 10봉 평균
        AND RSI14 < 65
- SELL: 현재 close < 전일 close - 0.5 * 전일 변동폭
        AND 볼륨 >= 10봉 평균
        AND RSI14 > 35
- confidence: HIGH if 돌파폭 > 전일 변동폭 * 0.75, MEDIUM otherwise
- 최소 데이터: 15행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 15
_K = 0.5
_VOL_LOOKBACK = 10
_RSI_PERIOD = 14
_RSI_BUY_MAX = 65.0
_RSI_SELL_MIN = 35.0
_HIGH_CONF_RATIO = 0.75


def _compute_rsi(series: pd.Series, period: int = 14) -> float:
    """마지막 완성 캔들 기준 RSI 계산 (idx=-2 이전 데이터 사용)."""
    # series는 이미 idx+1까지 슬라이싱된 값
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    last_gain = float(avg_gain.iloc[-1])
    last_loss = float(avg_loss.iloc[-1])
    if last_loss == 0:
        return 100.0
    rs = last_gain / last_loss
    return 100.0 - (100.0 / (1.0 + rs))


class VolatilityBreakoutLWStrategy(BaseStrategy):
    name = "volatility_breakout_lw"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        prev = df.iloc[idx - 1]
        curr = df.iloc[idx]

        prev_range = float(prev["high"]) - float(prev["low"])
        prev_close = float(prev["close"])
        k = _K
        buy_level = prev_close + k * prev_range
        sell_level = prev_close - k * prev_range

        close = float(curr["close"])
        avg_vol = float(df["volume"].iloc[idx - _VOL_LOOKBACK:idx].mean())
        vol_ok = float(curr["volume"]) >= avg_vol

        # RSI14: idx+1까지 슬라이싱 (현재 완성 캔들 포함)
        rsi_start = max(0, idx - _RSI_PERIOD * 3)
        rsi_series = df["close"].iloc[rsi_start:idx + 1]
        rsi = _compute_rsi(rsi_series, _RSI_PERIOD)

        context = (
            f"close={close:.2f} buy_level={buy_level:.2f} sell_level={sell_level:.2f} "
            f"prev_range={prev_range:.2f} vol_ok={vol_ok} rsi={rsi:.1f}"
        )

        if close > buy_level and vol_ok and rsi < _RSI_BUY_MAX:
            breakout_mag = close - buy_level
            confidence = (
                Confidence.HIGH
                if breakout_mag > prev_range * _HIGH_CONF_RATIO
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"LW 변동성 돌파 BUY: close({close:.2f})>buy_level({buy_level:.2f}), "
                    f"vol_ok={vol_ok}, rsi={rsi:.1f}<{_RSI_BUY_MAX}"
                ),
                invalidation=f"Close below buy_level ({buy_level:.2f})",
                bull_case=context,
                bear_case=context,
            )

        if close < sell_level and vol_ok and rsi > _RSI_SELL_MIN:
            breakout_mag = sell_level - close
            confidence = (
                Confidence.HIGH
                if breakout_mag > prev_range * _HIGH_CONF_RATIO
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"LW 변동성 돌파 SELL: close({close:.2f})<sell_level({sell_level:.2f}), "
                    f"vol_ok={vol_ok}, rsi={rsi:.1f}>{_RSI_SELL_MIN}"
                ),
                invalidation=f"Close above sell_level ({sell_level:.2f})",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
