"""
NarrowRangeStrategy (개선): NR7 + ATR 축소 + 거래량 확인

- NR7: 최근 7봉 중 최소 range 감지
- ATR 필터: NR 기간 ATR이 평균보다 수축 (20봉 평균 기준)
- 돌파 거래량: 진정 거래량이 20봉 평균의 1.2x 이상
- Breakout: prev가 NR7 AND ATR 축소 AND close 돌파 AND volume spike
- confidence: NR4+NR7 AND volume>1.5x → HIGH, 아니면 MEDIUM
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class NarrowRangeStrategy(BaseStrategy):
    name = "narrow_range"
    MIN_ROWS = 25
    ATR_LOOKBACK = 20
    VOL_LOOKBACK = 20
    VOL_SPIKE_MULT = 1.0   # 완화: 1.2→1.0 (4h봉 거래 수 증가 목적, Cycle 206)
    ATR_THRESHOLD = 0.90   # 완화: 0.85→0.90 (더 여유로운 ATR 수축 조건, Cycle 206)

    def __init__(self, nr_lookback: int = 5, **kwargs):
        """
        Args:
            nr_lookback: NR lookback 기간 (NR5=5, NR7=7). 4h봉 신호 부족 완화를 위해 기본 5.
        """
        self.nr_lookback = max(4, int(nr_lookback))  # 최소 4봉 (NR4 확인용)

    def _is_nr(self, ranges: pd.Series, idx: int, n: int) -> bool:
        """idx번 봉이 최근 n봉 중 최소 range인지 확인."""
        if idx < n - 1:
            return False
        window = ranges.iloc[idx - n + 1: idx + 1]
        return float(ranges.iloc[idx]) <= float(window.min())

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return self._hold(df, f"데이터 부족: {len(df)} < {self.MIN_ROWS}")

        # current = 마지막 완성봉 (iloc[-2])
        # prev    = 그 이전 봉 (iloc[-3]) → NR 후보
        curr_idx = len(df) - 2  # 완성봉
        prev_idx = curr_idx - 1  # NR 후보봉

        if prev_idx < self.nr_lookback - 1:
            return self._hold(df, f"NR{self.nr_lookback} 판단에 필요한 이전 봉 부족")

        ranges = df["high"] - df["low"]

        # prev봉이 NR(lookback), NR4 확인
        is_nr7 = self._is_nr(ranges, prev_idx, self.nr_lookback)
        is_nr4 = self._is_nr(ranges, prev_idx, 4)

        if not is_nr7:
            return self._hold(
                df,
                f"NR{self.nr_lookback} 조건 미충족: prev_range={float(ranges.iloc[prev_idx]):.4f}",
            )

        # ATR 축소 확인 (NR 기간 ATR이 평균보다 작은지)
        atr_series = df["atr14"]
        nr_atr = float(atr_series.iloc[prev_idx])
        avg_atr = float(atr_series.iloc[prev_idx - self.ATR_LOOKBACK : prev_idx].mean())
        
        # ATR이 평균의 85% 이하 → 축소 상태
        atr_shrunk = nr_atr <= avg_atr * self.ATR_THRESHOLD
        
        if not atr_shrunk:
            return self._hold(
                df,
                f"ATR 축소 미충족: nr_atr={nr_atr:.4f} > avg*{self.ATR_THRESHOLD}={avg_atr*self.ATR_THRESHOLD:.4f}",
            )

        # 거래량 확인 (현재 봉)
        vol_current = float(df["volume"].iloc[curr_idx])
        avg_vol = float(df["volume"].iloc[curr_idx - self.VOL_LOOKBACK : curr_idx].mean())
        
        vol_spike = vol_current >= avg_vol * self.VOL_SPIKE_MULT
        
        close_curr = float(df["close"].iloc[curr_idx])
        high_prev = float(df["high"].iloc[prev_idx])
        low_prev = float(df["low"].iloc[prev_idx])
        prev_range = float(ranges.iloc[prev_idx])

        # confidence: NR4+NR7 AND volume spike → HIGH
        conf = Confidence.HIGH if (is_nr4 and is_nr7 and vol_spike) else Confidence.MEDIUM

        bull_case = (
            f"NR7={'Y'} NR4={'Y' if is_nr4 else 'N'} ATR_shrink={'Y'} "
            f"vol_spike={'Y' if vol_spike else 'N'}, "
            f"close={close_curr:.4f} > prev_high={high_prev:.4f}"
        )
        bear_case = (
            f"NR7={'Y'} NR4={'Y' if is_nr4 else 'N'} ATR_shrink={'Y'} "
            f"vol_spike={'Y' if vol_spike else 'N'}, "
            f"close={close_curr:.4f} < prev_low={low_prev:.4f}"
        )

        # 상향 돌파
        if close_curr > high_prev:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_curr,
                reasoning=(
                    f"NR7 상향 돌파: close({close_curr:.4f})>high({high_prev:.4f}), "
                    f"ATR={nr_atr:.4f} < avg*{self.ATR_THRESHOLD}({avg_atr*self.ATR_THRESHOLD:.4f}), vol_spike={vol_spike}"
                ),
                invalidation=f"close < prev_high({high_prev:.4f}) 복귀 시 무효",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # 하향 돌파
        if close_curr < low_prev:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_curr,
                reasoning=(
                    f"NR7 하향 돌파: close({close_curr:.4f})<low({low_prev:.4f}), "
                    f"ATR={nr_atr:.4f} < avg*{self.ATR_THRESHOLD}({avg_atr*self.ATR_THRESHOLD:.4f}), vol_spike={vol_spike}"
                ),
                invalidation=f"close > prev_low({low_prev:.4f}) 복귀 시 무효",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(
            df,
            f"NR7+ATR 축소 감지됐으나 돌파 없음: close={close_curr:.4f} in [{low_prev:.4f}, {high_prev:.4f}]",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = self._last(df)
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
