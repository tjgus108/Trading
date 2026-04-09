"""
FailedBreakoutStrategy: False breakout 감지 후 역방향 거래.

- resistance = close.rolling(20).max().shift(1)  (직전 20봉 고점)
- support    = close.rolling(20).min().shift(1)  (직전 20봉 저점)
- ATR14 사용
- Fake BUY breakout  (→ SELL): prev high > resistance AND prev close < resistance
- Fake SELL breakout (→ BUY):  prev low  < support    AND prev close > support
- confidence: HIGH if (돌파범위 / ATR14 > 0.5), else MEDIUM
- 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_ROLL = 20
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


class FailedBreakoutStrategy(BaseStrategy):
    name = "failed_breakout"

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

        close = df["close"]
        high = df["high"]
        low = df["low"]

        resistance = close.rolling(_ROLL).max().shift(1)
        support = close.rolling(_ROLL).min().shift(1)
        atr = _atr(df, _ATR_PERIOD)

        idx = len(df) - 2
        prev_high = float(high.iloc[idx])
        prev_low = float(low.iloc[idx])
        prev_close = float(close.iloc[idx])
        res = float(resistance.iloc[idx])
        sup = float(support.iloc[idx])
        atr_val = float(atr.iloc[idx])
        entry = prev_close

        def _conf(breakout_size: float) -> Confidence:
            if atr_val > 0 and (breakout_size / atr_val) > _HIGH_CONF_RATIO:
                return Confidence.HIGH
            return Confidence.MEDIUM

        # Fake BUY breakout → SELL
        if prev_high > res and prev_close < res:
            breakout_size = prev_high - res
            conf = _conf(breakout_size)
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Fake 상향돌파 실패: 봉고점 {prev_high:.4f} > 저항 {res:.4f}, "
                    f"종가 {prev_close:.4f} < 저항 (복귀), 돌파범위/ATR={breakout_size/atr_val:.2f}"
                    if atr_val > 0
                    else f"Fake 상향돌파 실패: 봉고점 {prev_high:.4f} > 저항 {res:.4f}"
                ),
                invalidation="가격이 저항선 위로 재돌파하며 마감 시",
                bull_case="저항선 위 안착 성공 시 상승 지속",
                bear_case=f"저항 돌파 실패, 매도 압력 증가 예상",
            )

        # Fake SELL breakout → BUY
        if prev_low < sup and prev_close > sup:
            breakout_size = sup - prev_low
            conf = _conf(breakout_size)
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Fake 하향돌파 실패: 봉저점 {prev_low:.4f} < 지지 {sup:.4f}, "
                    f"종가 {prev_close:.4f} > 지지 (복귀), 돌파범위/ATR={breakout_size/atr_val:.2f}"
                    if atr_val > 0
                    else f"Fake 하향돌파 실패: 봉저점 {prev_low:.4f} < 지지 {sup:.4f}"
                ),
                invalidation="가격이 지지선 아래로 재이탈하며 마감 시",
                bull_case=f"지지선 이탈 실패, 매수 세력 강세 확인",
                bear_case="지지선 붕괴 지속 시 추가 하락 가능",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"Fake breakout 없음: 저항={res:.4f}, 지지={sup:.4f}, "
                f"봉고={prev_high:.4f}, 봉저={prev_low:.4f}, 종가={prev_close:.4f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
