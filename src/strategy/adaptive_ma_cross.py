"""
AdaptiveMACrossStrategy: 변동성에 따라 MA 기간을 조절하는 크로스 전략.

ATR_ratio = ATR14 / close
ATR_ratio > 최근 20봉 평균 → 고변동성: fast=5, slow=15
else → 저변동성: fast=15, slow=40

BUY: fast_ma crosses above slow_ma
SELL: fast_ma crosses below slow_ma
HIGH confidence: |fast_ma - slow_ma| > ATR14 * 0.3
최소 45행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 45


class AdaptiveMACrossStrategy(BaseStrategy):
    name = "adaptive_ma_cross"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: 최소 45행 필요",
                invalidation="",
            )

        last = self._last(df)
        prev = df.iloc[-3]

        close = float(last["close"])
        atr14 = float(last["atr14"]) if "atr14" in df.columns else _calc_atr(df)

        # ── ATR ratio & 변동성 판단 ───────────────────────────────────────────
        atr_ratio_series = df["atr14"] / df["close"] if "atr14" in df.columns else (
            df["close"].rolling(14).std() / df["close"]
        )
        current_ratio = float(atr_ratio_series.iloc[-2])
        lookback = min(20, len(df) - 2)
        avg_ratio = float(atr_ratio_series.iloc[-lookback - 1: -1].mean())
        high_vol = current_ratio > avg_ratio

        fast_period = 5 if high_vol else 15
        slow_period = 15 if high_vol else 40

        # ── MA 계산 (iloc[-1] 제외, 완성봉 기준) ─────────────────────────────
        closes = df["close"].iloc[:-1]  # 현재 진행봉 제외
        fast_ma_series = closes.ewm(span=fast_period, adjust=False).mean()
        slow_ma_series = closes.ewm(span=slow_period, adjust=False).mean()

        now_fast = float(fast_ma_series.iloc[-1])   # _last 봉 (_last = iloc[-2])
        now_slow = float(slow_ma_series.iloc[-1])
        prev_fast = float(fast_ma_series.iloc[-2])  # 그 직전 봉
        prev_slow = float(slow_ma_series.iloc[-2])

        cross_up = prev_fast <= prev_slow and now_fast > now_slow
        cross_down = prev_fast >= prev_slow and now_fast < now_slow

        gap = abs(now_fast - now_slow)
        conf = Confidence.HIGH if gap > atr14 * 0.3 else Confidence.MEDIUM

        vol_label = "high_vol" if high_vol else "low_vol"
        bull_case = (
            f"fast({fast_period})={now_fast:.2f} slow({slow_period})={now_slow:.2f} "
            f"ATR={atr14:.2f} gap={gap:.2f} {vol_label}"
        )
        bear_case = bull_case

        if cross_up:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Adaptive MA cross UP ({vol_label}): "
                    f"fast({fast_period})={now_fast:.2f} crossed above "
                    f"slow({slow_period})={now_slow:.2f}. gap={gap:.2f} ATR={atr14:.2f}."
                ),
                invalidation=f"fast_ma crosses below slow_ma ({now_slow:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if cross_down:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Adaptive MA cross DOWN ({vol_label}): "
                    f"fast({fast_period})={now_fast:.2f} crossed below "
                    f"slow({slow_period})={now_slow:.2f}. gap={gap:.2f} ATR={atr14:.2f}."
                ),
                invalidation=f"fast_ma crosses above slow_ma ({now_slow:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"No MA cross. fast({fast_period})={now_fast:.2f} "
                f"slow({slow_period})={now_slow:.2f} ({vol_label})."
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )


def _calc_atr(df: pd.DataFrame, period: int = 14) -> float:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    return float(tr.rolling(period).mean().iloc[-2])
