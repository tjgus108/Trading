"""
Spinning Top / Neutral Doji Breakout 전략:
- Spinning Top: 몸통 작고 위아래 꼬리 비슷한 불확실성 캔들
  - body < total_range * 0.25
  - upper_wick > body * 0.5 AND lower_wick > body * 0.5
- Spinning Top 이후 다음 봉으로 방향 확인 (idx = len(df) - 2):
  - BUY: 현재 봉(curr)이 이전 봉(spinning top)의 high 돌파 + RSI < 55
  - SELL: 현재 봉(curr)이 이전 봉(spinning top)의 low 돌파 + RSI > 45
- confidence: HIGH if 돌파폭 > ATR * 0.3, MEDIUM otherwise
- 최소 10행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 10


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


class SpinningTopStrategy(BaseStrategy):
    name = "spinning_top"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        curr = df.iloc[idx]
        prev = df.iloc[idx - 1]  # spinning top 후보
        atr = float(df["atr14"].iloc[idx])

        p_o = float(prev["open"])
        p_c = float(prev["close"])
        p_h = float(prev["high"])
        p_l = float(prev["low"])
        p_body = abs(p_c - p_o)
        p_range = p_h - p_l
        p_upper = p_h - max(p_o, p_c)
        p_lower = min(p_o, p_c) - p_l

        is_spinning = (
            p_range > 0
            and p_body < p_range * 0.25
            and p_upper > p_body * 0.5
            and p_lower > p_body * 0.5
        )

        if not is_spinning:
            return self._hold(df, f"No Spinning Top: body={p_body:.4f} range={p_range:.4f}")

        c_close = float(curr["close"])
        rsi_val = float(_rsi(df["close"]).iloc[idx])

        breakout_up = c_close - p_h
        breakout_down = p_l - c_close

        buy_signal = c_close > p_h and rsi_val < 55
        sell_signal = c_close < p_l and rsi_val > 45

        if not buy_signal and not sell_signal:
            return self._hold(
                df,
                f"Spinning Top but no breakout: close={c_close:.4f} prev_h={p_h:.4f} prev_l={p_l:.4f} rsi={rsi_val:.1f}",
            )

        if buy_signal:
            confidence = Confidence.HIGH if breakout_up > atr * 0.3 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=c_close,
                reasoning=f"Spinning Top breakout up: close={c_close:.4f} > prev_high={p_h:.4f}, RSI={rsi_val:.1f}",
                invalidation=f"Close below spinning top low ({p_l:.2f})",
                bull_case="Breakout above spinning top signals bullish resolution",
                bear_case="",
            )

        confidence = Confidence.HIGH if breakout_down > atr * 0.3 else Confidence.MEDIUM
        return Signal(
            action=Action.SELL,
            confidence=confidence,
            strategy=self.name,
            entry_price=c_close,
            reasoning=f"Spinning Top breakout down: close={c_close:.4f} < prev_low={p_l:.4f}, RSI={rsi_val:.1f}",
            invalidation=f"Close above spinning top high ({p_h:.2f})",
            bull_case="",
            bear_case="Breakout below spinning top signals bearish resolution",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = df.iloc[len(df) - 2] if len(df) >= 2 else df.iloc[-1]
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
