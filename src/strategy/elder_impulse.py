"""
Elder Impulse System 전략.

- EMA13   = close의 13기간 EWM
- MACD_line = EWM(close,12) - EWM(close,26)
- Signal_line = EWM(MACD_line, 9)
- MACD_hist = MACD_line - Signal_line

Impulse 색상:
  GREEN = EMA13 상승 AND MACD_hist 상승 → 강한 매수
  RED   = EMA13 하락 AND MACD_hist 하락 → 강한 매도
  BLUE  = 그 외

BUY:  이전봉 RED → 현재봉 GREEN (색상 전환)
SELL: 이전봉 GREEN → 현재봉 RED

confidence:
  HIGH   if 방향 전환 AND |MACD_hist| > std(MACD_hist, 20)
  MEDIUM 그 외

최소 데이터: 35행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35


def _impulse_color(ema_up: bool, hist_up: bool) -> str:
    if ema_up and hist_up:
        return "GREEN"
    if not ema_up and not hist_up:
        return "RED"
    return "BLUE"


class ElderImpulseStrategy(BaseStrategy):
    name = "elder_impulse"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for Elder Impulse (need 35 rows)")

        idx = len(df) - 2  # _last() = iloc[-2]

        ema13 = df["close"].ewm(span=13, adjust=False).mean()
        macd_line = (
            df["close"].ewm(span=12, adjust=False).mean()
            - df["close"].ewm(span=26, adjust=False).mean()
        )
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_hist = macd_line - signal_line

        ema_now = float(ema13.iloc[idx])
        ema_prev = float(ema13.iloc[idx - 1])
        hist_now = float(macd_hist.iloc[idx])
        hist_prev = float(macd_hist.iloc[idx - 1])
        close = float(df["close"].iloc[idx])

        color_now = _impulse_color(ema_now > ema_prev, hist_now > hist_prev)

        # 이전봉 색상: idx-1 vs idx-2
        ema_prev2 = float(ema13.iloc[idx - 2])
        hist_prev2 = float(macd_hist.iloc[idx - 2])
        color_prev = _impulse_color(ema_prev > ema_prev2, hist_prev > hist_prev2)

        # MACD hist 표준편차 (최대 20봉)
        window = macd_hist.iloc[max(0, idx - 19): idx + 1]
        hist_std = float(window.std()) if len(window) > 1 else 0.0

        context = (
            f"close={close:.4f} ema13={ema_now:.4f} "
            f"macd_hist={hist_now:.6f} color={color_now} prev_color={color_prev}"
        )

        # BUY: RED → GREEN
        if color_prev == "RED" and color_now == "GREEN":
            confidence = (
                Confidence.HIGH
                if hist_std > 0 and abs(hist_now) > hist_std
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Elder Impulse BUY: RED→GREEN 전환 "
                    f"(ema13={ema_now:.4f}, macd_hist={hist_now:.6f})"
                ),
                invalidation="GREEN 유지 실패 또는 BLUE로 전환",
                bull_case=context,
                bear_case=context,
            )

        # SELL: GREEN → RED
        if color_prev == "GREEN" and color_now == "RED":
            confidence = (
                Confidence.HIGH
                if hist_std > 0 and abs(hist_now) > hist_std
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Elder Impulse SELL: GREEN→RED 전환 "
                    f"(ema13={ema_now:.4f}, macd_hist={hist_now:.6f})"
                ),
                invalidation="RED 유지 실패 또는 BLUE로 전환",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(
            df,
            f"No signal: color_prev={color_prev} color_now={color_now}",
            context,
            context,
        )

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
        try:
            close = float(self._last(df)["close"])
        except Exception:
            close = 0.0
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
