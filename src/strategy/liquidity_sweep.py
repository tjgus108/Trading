"""
LiquiditySweepStrategy: 단기 고/저점 청산 후 반전 (Stop Hunt).

- recent_high = high.rolling(10).max().shift(1)
- recent_low  = low.rolling(10).min().shift(1)
- Bullish sweep: low < recent_low AND close > recent_low  → BUY
- Bearish sweep: high > recent_high AND close < recent_high → SELL
- confidence: 스윕 크기 > ATR14 * 0.5 → HIGH, else MEDIUM
- 최소 행: 15
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 15
_ROLL = 10
_ATR_PERIOD = 14
_HIGH_CONF_RATIO = 0.5


def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(com=period - 1, adjust=False).mean()


class LiquiditySweepStrategy(BaseStrategy):
    name = "liquidity_sweep"

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

        high = df["high"]
        low = df["low"]
        close = df["close"]

        recent_high = high.rolling(_ROLL).max().shift(1)
        recent_low = low.rolling(_ROLL).min().shift(1)
        atr = _atr(df, _ATR_PERIOD)

        idx = len(df) - 2
        cur_high = float(high.iloc[idx])
        cur_low = float(low.iloc[idx])
        cur_close = float(close.iloc[idx])
        r_high = float(recent_high.iloc[idx])
        r_low = float(recent_low.iloc[idx])
        atr_val = float(atr.iloc[idx])
        entry = cur_close

        def _conf(sweep_size: float) -> Confidence:
            if atr_val > 0 and (sweep_size / atr_val) > _HIGH_CONF_RATIO:
                return Confidence.HIGH
            return Confidence.MEDIUM

        # Bullish sweep: low swept below recent_low, close recovered above
        if cur_low < r_low and cur_close > r_low:
            sweep_size = r_low - cur_low
            conf = _conf(sweep_size)
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bullish sweep: 저점 {cur_low:.4f} < recent_low {r_low:.4f}, "
                    f"종가 {cur_close:.4f} > recent_low (복귀), 스윕크기/ATR="
                    f"{sweep_size/atr_val:.2f}" if atr_val > 0
                    else f"Bullish sweep: 저점 {cur_low:.4f} < recent_low {r_low:.4f}, 복귀"
                ),
                invalidation="종가가 recent_low 아래로 재이탈 시",
                bull_case="저점 청산 후 매수세 유입, 상승 반전 기대",
                bear_case="청산 후 추가 하락 시 추세 지속 가능",
            )

        # Bearish sweep: high swept above recent_high, close rejected below
        if cur_high > r_high and cur_close < r_high:
            sweep_size = cur_high - r_high
            conf = _conf(sweep_size)
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bearish sweep: 고점 {cur_high:.4f} > recent_high {r_high:.4f}, "
                    f"종가 {cur_close:.4f} < recent_high (복귀), 스윕크기/ATR="
                    f"{sweep_size/atr_val:.2f}" if atr_val > 0
                    else f"Bearish sweep: 고점 {cur_high:.4f} > recent_high {r_high:.4f}, 복귀"
                ),
                invalidation="종가가 recent_high 위로 재돌파 시",
                bull_case="고점 돌파 성공 시 상승 지속 가능",
                bear_case="고점 청산 후 매도세 유입, 하락 반전 기대",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"Sweep 없음: recent_high={r_high:.4f}, recent_low={r_low:.4f}, "
                f"고={cur_high:.4f}, 저={cur_low:.4f}, 종={cur_close:.4f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
