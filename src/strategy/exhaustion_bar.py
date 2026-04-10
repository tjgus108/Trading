"""
ExhaustionBarStrategy: 소진봉(Exhaustion Bar) 기반 반전 전략.

- ATR14 = TR.ewm(span=14, adjust=False).mean()
- body = abs(close - open)
- prev_trend_up = close[idx-1] > close[idx-5]  (5봉 상승)
- Exhaustion up:  prev_trend_up AND body > atr14*1.5 AND rsi14 > 70 AND high == recent 10봉 최고
- Exhaustion down: not prev_trend_up AND body > atr14*1.5 AND rsi14 < 30 AND low == recent 10봉 최저
- BUY:  exhaustion_down (하락 소진 → 반전)
- SELL: exhaustion_up  (상승 소진 → 반전)
- confidence: body > atr14*2.5 → HIGH, 나머지 → MEDIUM
- 최소 데이터: 20행
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_ATR_MULT_MEDIUM = 1.5
_ATR_MULT_HIGH = 2.5
_RSI_OB = 70
_RSI_OS = 30
_TREND_LOOKBACK = 5   # prev_trend_up: close[idx-1] > close[idx-5]
_HIGH_LOOKBACK = 10   # recent 10봉 최고/최저


def _calc_atr14_ewm(df: pd.DataFrame) -> pd.Series:
    """TR.ewm(span=14, adjust=False).mean() 으로 ATR14 계산."""
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    close = df["close"].astype(float)
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(span=14, adjust=False).mean()


def _calc_rsi14(close: pd.Series) -> pd.Series:
    """단순 Wilder RSI 근사 (ewm). avg_loss=0 → RSI=100, avg_gain=0 → RSI=0."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(span=14, adjust=False).mean()
    avg_loss = loss.ewm(span=14, adjust=False).mean()
    # avg_loss=0 이면 RSI=100, avg_gain=0이면 RSI=0
    rsi = pd.Series(50.0, index=close.index, dtype=float)
    both_zero = (avg_loss == 0) & (avg_gain == 0)
    only_gain = (avg_loss == 0) & (avg_gain > 0)
    normal = avg_loss > 0
    rsi[only_gain] = 100.0
    rs_normal = avg_gain[normal] / avg_loss[normal]
    rsi[normal] = 100.0 - (100.0 / (1.0 + rs_normal))
    return rsi


class ExhaustionBarStrategy(BaseStrategy):
    """소진봉 반전 전략."""

    name = "exhaustion_bar"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            close_val = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"데이터 부족: {len(df)}행 < {_MIN_ROWS}행 필요",
                invalidation="충분한 히스토리 데이터 확보 후 재시도",
            )

        # 신호 기준 인덱스: iloc[-2]
        idx = len(df) - 2

        atr14_series = _calc_atr14_ewm(df)
        rsi14_series = _calc_rsi14(df["close"].astype(float))

        last = df.iloc[idx]
        close = float(last["close"])
        open_ = float(last["open"])
        high = float(last["high"])
        low = float(last["low"])

        body = abs(close - open_)
        atr = float(atr14_series.iloc[idx])
        rsi = float(rsi14_series.iloc[idx])

        # prev_trend_up: close[idx-1] > close[idx-5]
        trend_ref_idx = idx - _TREND_LOOKBACK
        if trend_ref_idx < 0:
            trend_ref_idx = 0
        prev_trend_up = float(df["close"].iloc[idx - 1]) > float(df["close"].iloc[trend_ref_idx])

        # recent 10봉 최고/최저: df.iloc[idx-9 : idx+1] (현재봉 포함 10봉)
        window_start = max(0, idx - _HIGH_LOOKBACK + 1)
        recent_window = df.iloc[window_start: idx + 1]
        recent_high = float(recent_window["high"].max())
        recent_low = float(recent_window["low"].min())

        exhaustion_up = (
            prev_trend_up
            and body > atr * _ATR_MULT_MEDIUM
            and rsi > _RSI_OB
            and high == recent_high
        )
        exhaustion_down = (
            not prev_trend_up
            and body > atr * _ATR_MULT_MEDIUM
            and rsi < _RSI_OS
            and low == recent_low
        )

        confidence = Confidence.HIGH if body > atr * _ATR_MULT_HIGH else Confidence.MEDIUM

        context = (
            f"close={close:.4f} body={body:.4f} atr={atr:.4f} rsi={rsi:.1f} "
            f"prev_trend_up={prev_trend_up} high={high:.4f} low={low:.4f} "
            f"recent_high={recent_high:.4f} recent_low={recent_low:.4f}"
        )

        if exhaustion_down:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"하락 소진봉 감지 → 반전 기대: body={body:.4f} > ATR*{_ATR_MULT_MEDIUM}={atr * _ATR_MULT_MEDIUM:.4f}, "
                    f"RSI={rsi:.1f} < {_RSI_OS}, 10봉 최저점 갱신"
                ),
                invalidation=f"close < low({low:.4f}) 갱신 시 무효",
                bull_case=context,
                bear_case=context,
            )

        if exhaustion_up:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"상승 소진봉 감지 → 반전 기대: body={body:.4f} > ATR*{_ATR_MULT_MEDIUM}={atr * _ATR_MULT_MEDIUM:.4f}, "
                    f"RSI={rsi:.1f} > {_RSI_OB}, 10봉 최고점 갱신"
                ),
                invalidation=f"close > high({high:.4f}) 갱신 시 무효",
                bull_case=context,
                bear_case=context,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=f"소진봉 조건 미충족: {context}",
            invalidation="소진봉 조건 충족 시 재평가",
            bull_case=context,
            bear_case=context,
        )
