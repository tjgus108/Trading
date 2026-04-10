"""
CrossoverConfluenceStrategy: 여러 MA 크로스오버 동시 발생.

- EMA9, EMA21, EMA50, RSI14 사용
- BUY: EMA9 crosses above EMA21 AND EMA9 > EMA50 AND RSI14 > 45
- SELL: EMA9 crosses below EMA21 AND EMA9 < EMA50 AND RSI14 < 55
- confidence HIGH: EMA21 also recently crossed EMA50 (within 5봉)
- 최소 행: 55
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 55
EMA9_P = 9
EMA21_P = 21
EMA50_P = 50
RSI_P = 14
CONF_LOOKBACK = 5


def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))


class CrossoverConfluenceStrategy(BaseStrategy):
    name = "crossover_confluence"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: 최소 55행 필요",
                invalidation="",
            )

        close = df["close"]

        # 컬럼 우선 사용, 없으면 직접 계산
        if "ema9" in df.columns:
            ema9 = df["ema9"]
        else:
            ema9 = _ema(close, EMA9_P)

        if "ema21" in df.columns:
            ema21 = df["ema21"]
        else:
            ema21 = _ema(close, EMA21_P)

        if "ema50" in df.columns:
            ema50 = df["ema50"]
        else:
            ema50 = _ema(close, EMA50_P)

        if "rsi14" in df.columns:
            rsi_series = df["rsi14"]
        else:
            rsi_series = _rsi(close, RSI_P)

        # 마지막 완성봉 (iloc[-2])
        last = self._last(df)
        prev = df.iloc[-3]

        last_idx = len(df) - 2
        prev_idx = len(df) - 3

        now9 = float(ema9.iloc[-2])
        now21 = float(ema21.iloc[-2])
        now50 = float(ema50.iloc[-2])
        prev9 = float(ema9.iloc[-3])
        prev21 = float(ema21.iloc[-3])

        rsi_val = float(rsi_series.iloc[-2])
        entry_price = float(last["close"])

        # EMA9 crosses above EMA21
        cross_up = prev9 <= prev21 and now9 > now21
        # EMA9 crosses below EMA21
        cross_down = prev9 >= prev21 and now9 < now21

        # EMA21 recently crossed EMA50 within 5봉 → HIGH confidence
        high_conf = False
        check_start = max(0, len(df) - CONF_LOOKBACK - 2)
        for i in range(check_start, len(df) - 2):
            if i == 0:
                continue
            e21_now = float(ema21.iloc[i])
            e21_prev = float(ema21.iloc[i - 1])
            e50_now = float(ema50.iloc[i])
            e50_prev = float(ema50.iloc[i - 1])
            if (e21_prev <= e50_prev and e21_now > e50_now) or (
                e21_prev >= e50_prev and e21_now < e50_now
            ):
                high_conf = True
                break

        confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM

        bull_case = (
            f"EMA9={now9:.4f} > EMA21={now21:.4f} > EMA50={now50:.4f} cross up, RSI={rsi_val:.1f}"
        )
        bear_case = (
            f"EMA9={now9:.4f} < EMA21={now21:.4f}, EMA50={now50:.4f} cross down, RSI={rsi_val:.1f}"
        )

        if cross_up and now9 > now50 and rsi_val > 45:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"EMA9 crossed above EMA21 (prev={prev9:.4f}<={prev21:.4f}, "
                    f"now={now9:.4f}>{now21:.4f}), EMA9>{now50:.4f}(EMA50), RSI={rsi_val:.1f}>45"
                    + (" | EMA21/EMA50 최근 크로스 확인" if high_conf else "")
                ),
                invalidation=f"Close below EMA21 ({now21:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if cross_down and now9 < now50 and rsi_val < 55:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"EMA9 crossed below EMA21 (prev={prev9:.4f}>={prev21:.4f}, "
                    f"now={now9:.4f}<{now21:.4f}), EMA9<{now50:.4f}(EMA50), RSI={rsi_val:.1f}<55"
                    + (" | EMA21/EMA50 최근 크로스 확인" if high_conf else "")
                ),
                invalidation=f"Close above EMA21 ({now21:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"크로스오버 조건 미충족: EMA9={now9:.4f}, EMA21={now21:.4f}, "
                f"EMA50={now50:.4f}, RSI={rsi_val:.1f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
