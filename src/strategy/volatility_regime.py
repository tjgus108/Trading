"""
VolatilityRegimeStrategy:
- ATR14 (EWM) 기반 변동성 레짐 감지
- High vol: ATR_ratio > rolling_mean * 1.5  → Mean reversion
  - BUY:  close < BB lower (oversold)
  - SELL: close > BB upper (overbought)
- Low vol + BB squeeze → Breakout
  - BUY:  close > BB upper
  - SELL: close < BB lower
- confidence: ATR_ratio 극단값(> 2x mean or < 0.5x mean) → HIGH
- 최소 행: 35
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35
_BB_PERIOD = 20
_BB_STD = 2.0
_ATR_PERIOD = 14
_ATR_ROLL = 20
_HIGH_VOL_MULT = 1.5
_LOW_VOL_MULT = 0.7
_SQUEEZE_MULT = 0.7
_HIGH_CONF_HIGH_MULT = 2.0
_HIGH_CONF_LOW_MULT = 0.5


class VolatilityRegimeStrategy(BaseStrategy):
    name = "volatility_regime"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2  # 마지막 완성봉
        last = df.iloc[idx]
        close = float(last["close"])

        # ── ATR14 (EWM) ──────────────────────────────────────────────────────
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
        atr14 = tr.ewm(span=_ATR_PERIOD, adjust=False).mean()

        # ATR_ratio = ATR14 / close
        atr_ratio = atr14 / df["close"].replace(0, float("nan"))
        atr_ratio_roll_mean = atr_ratio.rolling(_ATR_ROLL).mean()

        curr_atr_ratio = float(atr_ratio.iloc[idx])
        curr_roll_mean = float(atr_ratio_roll_mean.iloc[idx])

        if curr_roll_mean == 0 or pd.isna(curr_roll_mean):
            return self._hold(df, "ATR roll mean not available")

        # ── Bollinger Bands ───────────────────────────────────────────────────
        bb_mid = df["close"].rolling(_BB_PERIOD).mean()
        bb_std = df["close"].rolling(_BB_PERIOD).std()
        bb_upper = bb_mid + _BB_STD * bb_std
        bb_lower = bb_mid - _BB_STD * bb_std
        bandwidth = (bb_upper - bb_lower) / bb_mid.replace(0, float("nan"))
        bw_roll_mean = bandwidth.rolling(_BB_PERIOD).mean()

        curr_upper = float(bb_upper.iloc[idx])
        curr_lower = float(bb_lower.iloc[idx])
        curr_bw = float(bandwidth.iloc[idx])
        curr_bw_mean = float(bw_roll_mean.iloc[idx])

        # ── 레짐 판단 ─────────────────────────────────────────────────────────
        high_vol = curr_atr_ratio > curr_roll_mean * _HIGH_VOL_MULT
        low_vol = curr_atr_ratio < curr_roll_mean * _LOW_VOL_MULT

        # BB squeeze
        squeeze = (
            not pd.isna(curr_bw_mean)
            and curr_bw_mean > 0
            and curr_bw < curr_bw_mean * _SQUEEZE_MULT
        )

        # ── confidence ───────────────────────────────────────────────────────
        extreme = (
            curr_atr_ratio > curr_roll_mean * _HIGH_CONF_HIGH_MULT
            or curr_atr_ratio < curr_roll_mean * _HIGH_CONF_LOW_MULT
        )
        confidence = Confidence.HIGH if extreme else Confidence.MEDIUM

        regime_str = "high_vol" if high_vol else ("low_vol" if low_vol else "normal")
        bull = (
            f"regime={regime_str}, close={close:.4f}, "
            f"BB_lower={curr_lower:.4f}, BB_upper={curr_upper:.4f}, squeeze={squeeze}"
        )
        bear = bull

        # ── Low vol + squeeze → Breakout ─────────────────────────────────────
        if low_vol and squeeze:
            if close > curr_upper:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"Low vol squeeze breakout UP: "
                        f"close({close:.4f}) > BB_upper({curr_upper:.4f}), "
                        f"atr_ratio={curr_atr_ratio:.4f} < mean*{_LOW_VOL_MULT}({curr_roll_mean*_LOW_VOL_MULT:.4f})"
                    ),
                    invalidation=f"close < BB_upper({curr_upper:.4f})",
                    bull_case=bull,
                    bear_case=bear,
                )
            if close < curr_lower:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"Low vol squeeze breakout DOWN: "
                        f"close({close:.4f}) < BB_lower({curr_lower:.4f}), "
                        f"atr_ratio={curr_atr_ratio:.4f} < mean*{_LOW_VOL_MULT}({curr_roll_mean*_LOW_VOL_MULT:.4f})"
                    ),
                    invalidation=f"close > BB_lower({curr_lower:.4f})",
                    bull_case=bull,
                    bear_case=bear,
                )

        # ── High vol → Mean reversion ─────────────────────────────────────────
        if high_vol:
            if close < curr_lower:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"High vol mean reversion BUY: "
                        f"close({close:.4f}) < BB_lower({curr_lower:.4f}), "
                        f"atr_ratio={curr_atr_ratio:.4f} > mean*{_HIGH_VOL_MULT}({curr_roll_mean*_HIGH_VOL_MULT:.4f})"
                    ),
                    invalidation=f"close > BB_mid({float(bb_mid.iloc[idx]):.4f})",
                    bull_case=bull,
                    bear_case=bear,
                )
            if close > curr_upper:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"High vol mean reversion SELL: "
                        f"close({close:.4f}) > BB_upper({curr_upper:.4f}), "
                        f"atr_ratio={curr_atr_ratio:.4f} > mean*{_HIGH_VOL_MULT}({curr_roll_mean*_HIGH_VOL_MULT:.4f})"
                    ),
                    invalidation=f"close < BB_mid({float(bb_mid.iloc[idx]):.4f})",
                    bull_case=bull,
                    bear_case=bear,
                )

        return self._hold(
            df,
            f"No signal: regime={regime_str}, squeeze={squeeze}, "
            f"close={close:.4f} [BB {curr_lower:.4f}~{curr_upper:.4f}]",
            bull,
            bear,
        )

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
