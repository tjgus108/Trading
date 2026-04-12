"""
TrendContinuationStrategy:
- 상승/하락 추세 중 조정 후 재개 감지
- Long-term trend: EMA50 기울기 (ema50[-1] > ema50[-6] → 상승)
- Pullback: close가 EMA21 근처까지 되돌림 (close/ema21 - 1 in [-0.02, 0.02])
- Continuation:
    BUY:  uptrend AND pullback_complete AND close > ema21 * 1.001
    SELL: downtrend AND rally_complete   AND close < ema21 * 0.999
- confidence: pullback 후 volume spike (vol > avg_vol * 1.3) → HIGH
- 최소 데이터: 55행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 55
_EMA_FAST = 21
_EMA_SLOW = 50
_PULLBACK_PCT = 0.02       # ±2% EMA21 근처
_BUY_ENTRY_MULT = 1.001    # close > ema21 * 1.001
_SELL_ENTRY_MULT = 0.999   # close < ema21 * 0.999
_TREND_LOOKBACK = 5        # ema50[-1] vs ema50[-6]
_VOL_SPIKE_MULT = 1.3


def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


class TrendContinuationStrategy(BaseStrategy):
    name = "trend_continuation"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        volume = df["volume"]

        ema21 = _ema(close, _EMA_FAST)
        ema50 = _ema(close, _EMA_SLOW)

        idx = len(df) - 2  # 마지막 완성 캔들

        close_now = float(close.iloc[idx])
        open_now = float(df["open"].iloc[idx])
        ema21_now = float(ema21.iloc[idx])
        ema50_now = float(ema50.iloc[idx])
        ema50_prev = float(ema50.iloc[idx - _TREND_LOOKBACK])

        # Volume spike: 최근 20봉 평균 대비
        vol_now = float(volume.iloc[idx])
        vol_avg = float(volume.iloc[max(0, idx - 20):idx].mean())
        vol_spike = vol_avg > 0 and vol_now > vol_avg * _VOL_SPIKE_MULT

        # Trend direction
        uptrend = ema50_now > ema50_prev
        downtrend = ema50_now < ema50_prev

        # Pullback to EMA21
        ratio = close_now / ema21_now - 1.0 if ema21_now != 0 else 0.0
        near_ema21 = -_PULLBACK_PCT <= ratio <= _PULLBACK_PCT

        context = (
            f"close={close_now:.2f} ema21={ema21_now:.2f} ema50={ema50_now:.2f} "
            f"ratio={ratio:.4f} vol_spike={vol_spike} uptrend={uptrend}"
        )

        # BUY: 상승추세 + EMA21 근처 풀백 + 양봉으로 재개
        if uptrend and near_ema21 and close_now > ema21_now * _BUY_ENTRY_MULT and close_now > open_now:
            confidence = Confidence.HIGH if vol_spike else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"상승추세 조정 후 재개: ema50↑, close near ema21({ema21_now:.2f}), "
                    f"양봉 확인, ratio={ratio:.4f}"
                ),
                invalidation=f"close < ema21 ({ema21_now:.2f})",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 하락추세 + EMA21 근처 반등 + 음봉으로 재개
        if downtrend and near_ema21 and close_now < ema21_now * _SELL_ENTRY_MULT and close_now < open_now:
            confidence = Confidence.HIGH if vol_spike else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"하락추세 반등 후 재개: ema50↓, close near ema21({ema21_now:.2f}), "
                    f"음봉 확인, ratio={ratio:.4f}"
                ),
                invalidation=f"close > ema21 ({ema21_now:.2f})",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
        idx = len(df) - 2 if len(df) >= 2 else 0
        close = float(df["close"].iloc[idx])
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
