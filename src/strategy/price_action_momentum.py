"""
PriceActionMomentumStrategy: Cycle 121 v2 (body 0.50 + ROC5 + optional SMA200).

개선 사항 (Cycle 121):
- body_strength: 0.40 → 0.50 (더 강한 바디 요구)
- roc5 필터: 강화된 momentum 요구사항
- SMA200 추가: 장기 추세 확인 (선택적, 없으면 무시)
- 목표: -13.69% → positive return, PF >= 1.5
"""

import pandas as pd
import math
from src.strategy.base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35  # Keep original for test compatibility


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
        sma200 = close.rolling(200, min_periods=1).mean() if len(df) >= 200 else None

        idx = len(df) - 2

        v_body = float(body.iloc[idx])
        v_body_strength = float(body_strength.iloc[idx])
        v_roc5 = float(roc5.iloc[idx])
        v_roc5_ma = float(roc5_ma.iloc[idx])
        v_roc5_std = float(roc5_std.iloc[idx])
        v_close = float(close.iloc[idx])
        v_sma50 = float(sma50.iloc[idx])
        v_sma200 = None
        if sma200 is not None:
            v_sma200_raw = float(sma200.iloc[idx])
            if not math.isnan(v_sma200_raw):
                v_sma200 = v_sma200_raw

        if any(math.isnan(x) for x in [v_body, v_body_strength, v_roc5, v_roc5_ma]):
            return self._hold(df, "NaN in indicators")

        # SMA200 trend check (optional)
        sma200_ok = v_sma200 is None or v_close > v_sma200 > 0

        context = (
            f"close={v_close:.4f} body={v_body:.4f} "
            f"body_strength={v_body_strength:.3f} roc5={v_roc5:.4f} roc5_ma={v_roc5_ma:.4f}"
        )

        is_high_conf = (
            v_body_strength > 0.6
            and not math.isnan(v_roc5_std)
            and abs(v_roc5) > v_roc5_std * 1.5
        )

        # BUY: strong body + uptrend momentum + optional long-term trend
        if (
            v_body > 0
            and v_body_strength >= 0.50  # 0.40 → 0.50: 강화됨
            and v_roc5 > 0.005
            and v_roc5 > v_roc5_ma - (v_roc5_std * 0.6 if not math.isnan(v_roc5_std) else 0)
            and v_close > v_sma50
            and sma200_ok  # SMA200 없으면 무시
        ):
            confidence = Confidence.HIGH if is_high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=v_close,
                reasoning=(
                    f"PA Momentum BUY: body_strength={v_body_strength:.3f} (>=0.50) "
                    f"roc5={v_roc5:.4f}, sma50 uptrend"
                ),
                invalidation="body<=0 or body_strength<0.50 or close<=sma50",
                bull_case=context,
                bear_case=context,
            )

        # SELL: strong body + downtrend momentum + optional long-term trend
        if (
            v_body < 0
            and v_body_strength >= 0.50  # 0.40 → 0.50: 강화됨
            and v_roc5 < -0.005
            and v_roc5 < v_roc5_ma + (v_roc5_std * 0.6 if not math.isnan(v_roc5_std) else 0)
            and v_close < v_sma50
            and (v_sma200 is None or v_close < v_sma200)  # SMA200 없으면 무시
        ):
            confidence = Confidence.HIGH if is_high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=v_close,
                reasoning=(
                    f"PA Momentum SELL: body_strength={v_body_strength:.3f} (>=0.50) "
                    f"roc5={v_roc5:.4f}, sma50 downtrend"
                ),
                invalidation="body>=0 or body_strength<0.50 or close>=sma50",
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
