"""
MarketMakerStrategy: 축적 → 조작 → 분배 패턴.

- Accumulation: 최근 10봉 ATR < avg_ATR * 0.7 (좁은 범위)
- range_high = close.rolling(10).max() over accumulation window
- range_low  = close.rolling(10).min() over accumulation window
- Manipulation (하방): low < range_low AND close > range_low (spike down + recover)
- BUY: accumulation + 하방 조작 + close > range_high
- Manipulation (상방): high > range_high AND close < range_high (spike up + reject)
- SELL: accumulation + 상방 조작 + close < range_low
- confidence: manipulation spike > ATR * 2 → HIGH, else MEDIUM
- 최소 행: 20
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_ACC_WINDOW = 10
_ATR_PERIOD = 14
_ACC_ATR_RATIO = 0.7
_HIGH_CONF_SPIKE = 2.0
_BASELINE_WINDOW = 20  # longer baseline for ATR comparison


def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
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
    return tr.ewm(com=period - 1, adjust=False).mean()


class MarketMakerStrategy(BaseStrategy):
    name = "market_maker_sig"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        high = df["high"]
        low = df["low"]
        close = df["close"]
        atr_series = _atr(df, _ATR_PERIOD)

        # candle range (high-low) for accumulation detection (more responsive than ewm ATR)
        candle_range = high - low
        # avg candle range over accumulation window (shifted to avoid lookahead)
        acc_range_avg = candle_range.rolling(_ACC_WINDOW).mean().shift(1)
        # long-term baseline: wider window (shifted)
        baseline_range_avg = candle_range.rolling(_BASELINE_WINDOW).mean().shift(1)

        # accumulation range for entry/exit detection (shifted)
        range_high = close.rolling(_ACC_WINDOW).max().shift(1)
        range_low = close.rolling(_ACC_WINDOW).min().shift(1)

        idx = len(df) - 2
        cur_high = float(high.iloc[idx])
        cur_low = float(low.iloc[idx])
        cur_close = float(close.iloc[idx])
        cur_atr = float(atr_series.iloc[idx])
        r_high = float(range_high.iloc[idx])
        r_low = float(range_low.iloc[idx])
        entry = cur_close

        # Accumulation: recent avg candle range < long-term baseline * ratio
        cur_acc_range = float(acc_range_avg.iloc[idx])
        cur_baseline = float(baseline_range_avg.iloc[idx])
        is_accumulation = (cur_baseline > 0) and (cur_acc_range < cur_baseline * _ACC_ATR_RATIO)
        acc_avg_atr = cur_acc_range  # for reasoning display

        def _conf(spike_size: float) -> Confidence:
            if cur_atr > 0 and (spike_size / cur_atr) > _HIGH_CONF_SPIKE:
                return Confidence.HIGH
            return Confidence.MEDIUM

        if is_accumulation:
            # BUY: downward manipulation + close > range_high
            if cur_low < r_low and cur_close > r_low and cur_close > r_high:
                spike_size = r_low - cur_low
                conf = _conf(spike_size)
                return Signal(
                    action=Action.BUY,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"MM BUY: 축적({_ACC_WINDOW}봉, range={acc_avg_atr:.4f}<baseline*0.7={cur_baseline*_ACC_ATR_RATIO:.4f}) "
                        f"+ 하방조작(저={cur_low:.4f}<range_low={r_low:.4f}) "
                        f"+ 분배(종={cur_close:.4f}>range_high={r_high:.4f}), "
                        f"spike/ATR={spike_size/cur_atr:.2f}" if cur_atr > 0
                        else f"MM BUY: 축적 + 하방조작 + 분배"
                    ),
                    invalidation="종가가 range_low 아래로 재이탈 시",
                    bull_case="MM 하방 조작 후 분배 상승 시작",
                    bear_case="조작 후 추가 하락 시 추세 전환 실패",
                )

            # SELL: upward manipulation + close < range_low
            if cur_high > r_high and cur_close < r_high and cur_close < r_low:
                spike_size = cur_high - r_high
                conf = _conf(spike_size)
                return Signal(
                    action=Action.SELL,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"MM SELL: 축적({_ACC_WINDOW}봉, range={acc_avg_atr:.4f}<baseline*0.7={cur_baseline*_ACC_ATR_RATIO:.4f}) "
                        f"+ 상방조작(고={cur_high:.4f}>range_high={r_high:.4f}) "
                        f"+ 분배(종={cur_close:.4f}<range_low={r_low:.4f}), "
                        f"spike/ATR={spike_size/cur_atr:.2f}" if cur_atr > 0
                        else f"MM SELL: 축적 + 상방조작 + 분배"
                    ),
                    invalidation="종가가 range_high 위로 재돌파 시",
                    bull_case="조작 후 추가 상승 시 추세 전환 실패",
                    bear_case="MM 상방 조작 후 분배 하락 시작",
                )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"MM 패턴 없음: 축적={'O' if is_accumulation else 'X'}"
                f"(range={acc_avg_atr:.4f},baseline={cur_baseline:.4f}), "
                f"range_high={r_high:.4f}, range_low={r_low:.4f}, "
                f"고={cur_high:.4f}, 저={cur_low:.4f}, 종={cur_close:.4f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
