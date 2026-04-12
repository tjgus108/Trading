"""
PriceActionMomentumStrategy: Cycle 117 최종 (body 0.40 + 강한 roc5).

개선 사항:
- body_strength: 0.40 (균형)
- roc5 절대값: > 0.005 (0.5% 최소)
- roc5 상대값: roc5_std*0.6 (강함)
- SMA50 (원래대로)
- 목표: PF >= 1.5, Sharpe >= 1.0
"""

import pandas as pd
import math
from src.strategy.base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35


class PriceActionMomentumStrategy(BaseStrategy):
    name = "price_action_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        open_ = df["open"]
        high = df["high"]
        low = df["low"]

        body = close - open_
        body_abs = body.abs()
        total_range = high - low + 1e-10
        body_strength = body_abs / total_range

        roc5 = close.pct_change(5)
        roc5_ma = roc5.rolling(10, min_periods=1).mean()
        roc5_std = roc5.rolling(20, min_periods=1).std()
        
        sma50 = close.rolling(50, min_periods=1).mean()

        idx = len(df) - 2

        v_body = float(body.iloc[idx])
        v_body_strength = float(body_strength.iloc[idx])
        v_roc5 = float(roc5.iloc[idx])
        v_roc5_ma = float(roc5_ma.iloc[idx])
        v_roc5_std = float(roc5_std.iloc[idx])
        v_close = float(close.iloc[idx])
        v_sma50 = float(sma50.iloc[idx])

        if any(math.isnan(x) for x in [v_body, v_body_strength, v_roc5, v_roc5_ma]):
            return self._hold(df, "NaN in indicators")

        context = (
            f"close={v_close:.4f} body={v_body:.4f} "
            f"body_strength={v_body_strength:.3f} roc5={v_roc5:.4f} roc5_ma={v_roc5_ma:.4f}"
        )

        is_high_conf = (
            v_body_strength > 0.6
            and not math.isnan(v_roc5_std)
            and abs(v_roc5) > v_roc5_std * 1.5
        )

        # BUY: body 0.40 + 강한 roc5
        if (
            v_body > 0
            and v_body_strength >= 0.40
            and v_roc5 > 0.005
            and v_roc5 > v_roc5_ma - (v_roc5_std * 0.6 if not math.isnan(v_roc5_std) else 0)
            and v_close > v_sma50
        ):
            confidence = Confidence.HIGH if is_high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=v_close,
                reasoning=(
                    f"PA Momentum BUY: body_strength={v_body_strength:.3f} "
                    f"roc5={v_roc5:.4f}, sma50 uptrend"
                ),
                invalidation="body<=0 or body_strength<0.40 or close<=sma50",
                bull_case=context,
                bear_case=context,
            )

        # SELL: body 0.40 + 강한 roc5
        if (
            v_body < 0
            and v_body_strength >= 0.40
            and v_roc5 < -0.005
            and v_roc5 < v_roc5_ma + (v_roc5_std * 0.6 if not math.isnan(v_roc5_std) else 0)
            and v_close < v_sma50
        ):
            confidence = Confidence.HIGH if is_high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=v_close,
                reasoning=(
                    f"PA Momentum SELL: body_strength={v_body_strength:.3f} "
                    f"roc5={v_roc5:.4f}, sma50 downtrend"
                ),
                invalidation="body>=0 or body_strength<0.40 or close>=sma50",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        idx = len(df) - 2
        close = float(df["close"].iloc[idx]) if len(df) >= 2 else 0.0
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
