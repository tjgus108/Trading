"""
StochDivergenceStrategy:
- Stochastic: K = 14기간, D = K의 3기간 SMA
- K = (close - low_14) / (high_14 - low_14) * 100
- Bullish divergence: price lower low + Stoch K higher low, K < 30
- Bearish divergence: price higher high + Stoch K lower high, K > 70
- BUY: bullish divergence + K crossing above D
- SELL: bearish divergence + K crossing below D
- confidence: divergence gap > 10 → HIGH, 그 외 → MEDIUM
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_K_PERIOD = 14
_D_PERIOD = 3
_OVERSOLD = 30.0
_OVERBOUGHT = 70.0
_HIGH_CONF_GAP = 10.0


def _calc_k_series(df: pd.DataFrame) -> "list[float]":
    """완성봉(-1 제외) 기준으로 K 시리즈 계산."""
    window = df.iloc[:-1]  # 진행 중 봉 제외
    closes = window["close"]
    highs = window["high"] if "high" in window.columns else window["close"]
    lows = window["low"] if "low" in window.columns else window["close"]

    k_series = []
    for i in range(_K_PERIOD - 1, len(window)):
        h = float(highs.iloc[i - _K_PERIOD + 1: i + 1].max())
        l = float(lows.iloc[i - _K_PERIOD + 1: i + 1].min())
        c = float(closes.iloc[i])
        denom = h - l
        if denom == 0:
            k_series.append(50.0)
        else:
            k_series.append((c - l) / denom * 100.0)
    return k_series


class StochDivergenceStrategy(BaseStrategy):
    name = "stoch_divergence"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        if "high" not in df.columns:
            df = df.copy()
            df["high"] = df["close"]
        if "low" not in df.columns:
            df = df.copy()
            df["low"] = df["close"]

        k_series = _calc_k_series(df)
        if len(k_series) < _D_PERIOD + 2:
            return self._hold(df, "Insufficient K series")

        # 최신 K 값들: [-1] = 신호봉, [-2] = 이전봉, [-3] = 그 이전봉
        k_now = k_series[-1]      # 신호봉 K (df.iloc[-2] 기준)
        k_prev = k_series[-2]     # K_prev
        k_prev2 = k_series[-3] if len(k_series) >= 3 else k_series[-2]

        # D 값들
        d_now = sum(k_series[-_D_PERIOD:]) / _D_PERIOD
        d_prev = sum(k_series[-_D_PERIOD - 1:-1]) / _D_PERIOD if len(k_series) >= _D_PERIOD + 1 else d_now

        # 가격 (완성봉 기준)
        completed = df.iloc[:-1]
        price_now = float(completed["close"].iloc[-1])    # 신호봉
        price_prev = float(completed["close"].iloc[-2])   # 이전봉
        price_prev2 = float(completed["close"].iloc[-3]) if len(completed) >= 3 else price_prev

        last = self._last(df)
        close = float(last["close"])

        context = (
            f"K={k_now:.1f} D={d_now:.1f} "
            f"K_prev={k_prev:.1f} K_prev2={k_prev2:.1f} "
            f"price={price_now:.4f}"
        )

        # Bullish divergence: price lower low + K higher low, K < 30
        bullish_div = (
            price_prev2 > price_prev > price_now  # price lower low
            and k_prev2 < k_prev              # K higher low (improving)
            and k_now < _OVERSOLD
        )
        # K crossing above D
        k_cross_up = k_now > d_now and k_prev <= d_prev

        # Bearish divergence: price higher high + K lower high, K > 70
        bearish_div = (
            price_prev2 < price_prev < price_now  # price higher high
            and k_prev2 > k_prev              # K lower high (weakening)
            and k_now > _OVERBOUGHT
        )
        # K crossing below D
        k_cross_down = k_now < d_now and k_prev >= d_prev

        if bullish_div and k_cross_up:
            gap = abs(k_now - k_prev2)
            confidence = Confidence.HIGH if gap > _HIGH_CONF_GAP else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Stoch bullish divergence + K cross above D: {context}",
                invalidation=f"K 다시 D 하향 이탈 시",
                bull_case=f"Bullish div gap={gap:.1f}, {context}",
                bear_case="divergence 무효화 시",
            )

        if bearish_div and k_cross_down:
            gap = abs(k_now - k_prev2)
            confidence = Confidence.HIGH if gap > _HIGH_CONF_GAP else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Stoch bearish divergence + K cross below D: {context}",
                invalidation=f"K 다시 D 상향 이탈 시",
                bull_case="divergence 무효화 시",
                bear_case=f"Bearish div gap={gap:.1f}, {context}",
            )

        return self._hold(df, f"No Stoch divergence: {context}")

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        if len(df) < 2:
            entry = 0.0
        else:
            last = self._last(df) if len(df) >= 2 else df.iloc[-1]
            entry = float(last["close"])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
