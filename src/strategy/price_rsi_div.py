"""
PriceRSIDivergence 전략:
- 고전적 RSI 다이버전스 감지 (피크 찾기 방식, pivot 기반).
- 최근 30봉에서 price pivot high/low 탐색 (좌우 3봉).
- RSI14 직접 계산 (EWM Wilder 방식).
- Bullish divergence: price low2 < low1, RSI low2 > RSI low1
- Bearish divergence: price high2 > high1, RSI high2 < RSI high1
- BUY: bullish divergence + RSI < 50
- SELL: bearish divergence + RSI > 50
- confidence: RSI 차이 > 10 → HIGH
- 최소 행: 35
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Tuple

from .base import Action, BaseStrategy, Confidence, Signal

_LOOKBACK = 30
_PIVOT_WING = 3      # 피벗 좌우 확인 봉 수
_RSI_PERIOD = 14
_HIGH_CONF_RSI_DIFF = 10.0
_MIN_ROWS = 35


def _calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Wilder EWM RSI 계산."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    alpha = 1.0 / period
    avg_gain = gain.ewm(alpha=alpha, adjust=False).mean()
    avg_loss = loss.ewm(alpha=alpha, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


def _find_pivot_highs(highs: pd.Series, wing: int) -> List[int]:
    """로컬 피벗 고점 인덱스 목록 반환."""
    pivots = []
    n = len(highs)
    for i in range(wing, n - wing):
        lo = i - wing
        hi = i + wing + 1
        if highs.iloc[i] == highs.iloc[lo:hi].max():
            pivots.append(i)
    return pivots


def _find_pivot_lows(lows: pd.Series, wing: int) -> List[int]:
    """로컬 피벗 저점 인덱스 목록 반환."""
    pivots = []
    n = len(lows)
    for i in range(wing, n - wing):
        lo = i - wing
        hi = i + wing + 1
        if lows.iloc[i] == lows.iloc[lo:hi].min():
            pivots.append(i)
    return pivots


class PriceRSIDivergenceStrategy(BaseStrategy):
    name = "price_rsi_div"

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

        # RSI 계산 (전체 df 기준)
        rsi_series = _calc_rsi(df["close"], _RSI_PERIOD)

        # 분석 window: 마지막 완성봉 포함 최근 30봉
        # df.iloc[-2] = last completed candle
        # window = df.iloc[-(1 + _LOOKBACK):-1] → 30봉, 마지막이 last completed
        window_df = df.iloc[-(1 + _LOOKBACK):-1].copy()
        window_rsi = rsi_series.iloc[-(1 + _LOOKBACK):-1].copy()
        window_rsi = window_rsi.reset_index(drop=True)
        window_df = window_df.reset_index(drop=True)

        last_rsi = float(window_rsi.iloc[-1])
        last_close = float(window_df["close"].iloc[-1])

        bullish, bull_rsi_diff = self._check_bullish(window_df, window_rsi)
        bearish, bear_rsi_diff = self._check_bearish(window_df, window_rsi)

        bull_case = (
            f"Bullish div RSI diff={bull_rsi_diff:.1f}" if bullish else "No bullish divergence"
        )
        bear_case = (
            f"Bearish div RSI diff={bear_rsi_diff:.1f}" if bearish else "No bearish divergence"
        )

        if bullish and not bearish and last_rsi < 50:
            conf = Confidence.HIGH if bull_rsi_diff > _HIGH_CONF_RSI_DIFF else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=last_close,
                reasoning=(
                    f"Bullish price-RSI divergence: price lower low + RSI higher low, "
                    f"RSI diff={bull_rsi_diff:.1f}, RSI={last_rsi:.1f}"
                ),
                invalidation="Close below recent swing low",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if bearish and not bullish and last_rsi > 50:
            conf = Confidence.HIGH if bear_rsi_diff > _HIGH_CONF_RSI_DIFF else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=last_close,
                reasoning=(
                    f"Bearish price-RSI divergence: price higher high + RSI lower high, "
                    f"RSI diff={bear_rsi_diff:.1f}, RSI={last_rsi:.1f}"
                ),
                invalidation="Close above recent swing high",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=last_close,
            reasoning=(
                f"No divergence signal. bullish={bullish}, bearish={bearish}, RSI={last_rsi:.1f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )

    def _check_bullish(
        self, window_df: pd.DataFrame, window_rsi: pd.Series
    ) -> Tuple[bool, float]:
        """
        Bullish: 두 번째 price low < 첫 번째 price low,
                 두 번째 RSI low > 첫 번째 RSI low.
        마지막 봉 자체가 두 번째 pivot low 역할.
        """
        lows_s = window_df["low"]
        pivot_idxs = _find_pivot_lows(lows_s, _PIVOT_WING)

        # 마지막 봉 제외한 피벗 저점들과 비교
        last_idx = len(window_df) - 1
        last_price_low = float(lows_s.iloc[last_idx])
        last_rsi = float(window_rsi.iloc[last_idx])

        # pivot 중 last_idx 제외하고 last_idx - PIVOT_WING 이전의 것
        earlier_pivots = [i for i in pivot_idxs if i <= last_idx - _PIVOT_WING]
        if not earlier_pivots:
            return False, 0.0

        best_rsi_diff = 0.0
        found = False
        for i in earlier_pivots:
            ref_price_low = float(lows_s.iloc[i])
            ref_rsi = float(window_rsi.iloc[i])
            # price lower low: last < ref
            # RSI higher low: last_rsi > ref_rsi
            if last_price_low < ref_price_low and last_rsi > ref_rsi:
                diff = last_rsi - ref_rsi
                if diff > best_rsi_diff:
                    best_rsi_diff = diff
                    found = True

        return found, best_rsi_diff

    def _check_bearish(
        self, window_df: pd.DataFrame, window_rsi: pd.Series
    ) -> Tuple[bool, float]:
        """
        Bearish: 두 번째 price high > 첫 번째 price high,
                 두 번째 RSI high < 첫 번째 RSI high.
        마지막 봉 자체가 두 번째 pivot high 역할.
        """
        highs_s = window_df["high"]
        pivot_idxs = _find_pivot_highs(highs_s, _PIVOT_WING)

        last_idx = len(window_df) - 1
        last_price_high = float(highs_s.iloc[last_idx])
        last_rsi = float(window_rsi.iloc[last_idx])

        earlier_pivots = [i for i in pivot_idxs if i <= last_idx - _PIVOT_WING]
        if not earlier_pivots:
            return False, 0.0

        best_rsi_diff = 0.0
        found = False
        for i in earlier_pivots:
            ref_price_high = float(highs_s.iloc[i])
            ref_rsi = float(window_rsi.iloc[i])
            # price higher high: last > ref
            # RSI lower high: last_rsi < ref_rsi
            if last_price_high > ref_price_high and last_rsi < ref_rsi:
                diff = ref_rsi - last_rsi
                if diff > best_rsi_diff:
                    best_rsi_diff = diff
                    found = True

        return found, best_rsi_diff
