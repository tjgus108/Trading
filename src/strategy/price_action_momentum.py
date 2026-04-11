"""
PriceActionMomentumStrategy: 개선된 버전.

개선 사항:
- body_strength 기준 완화: 0.5 → 0.35 (신호 증가)
- roc5 기준 완화: roc5 > roc5_ma → roc5 > roc5_ma - roc5_std*0.3 (민감도 ↑)
- momentum 추가 필터: close > sma(50)일 때만 BUY (트렌드 확인)
- 최소 35행 (더 안정적인 지표)
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
        
        # 추가 필터: SMA(50) 트렌드 확인
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

        # BUY: 개선된 조건
        # - body_strength >= 0.35 (from 0.5, 더 많은 신호)
        # - roc5 > roc5_ma - roc5_std*0.3 (완화된 모멘텀 기준)
        # - close > sma50 (상승 트렌드 확인)
        if (
            v_body > 0
            and v_body_strength >= 0.35
            and v_roc5 > v_roc5_ma - (v_roc5_std * 0.3 if not math.isnan(v_roc5_std) else 0)
            and v_roc5 > 0
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
                    f"roc5={v_roc5:.4f}>threshold, sma50 uptrend"
                ),
                invalidation="body<=0 or body_strength<0.35 or close<=sma50",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 개선된 조건
        # - body_strength >= 0.35 (from 0.5, 더 많은 신호)
        # - roc5 < roc5_ma + roc5_std*0.3 (완화된 모멘텀 기준)
        # - close < sma50 (하락 트렌드 확인)
        if (
            v_body < 0
            and v_body_strength >= 0.35
            and v_roc5 < v_roc5_ma + (v_roc5_std * 0.3 if not math.isnan(v_roc5_std) else 0)
            and v_roc5 < 0
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
                    f"roc5={v_roc5:.4f}<threshold, sma50 downtrend"
                ),
                invalidation="body>=0 or body_strength<0.35 or close>=sma50",
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
