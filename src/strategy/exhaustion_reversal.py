"""
ExhaustionReversalStrategy: 추세 소진 후 반전 감지.

로직:
  - atr = (high - low).rolling(14, min_periods=1).mean()
  - body = (close - open).abs()
  - body_ratio = body / (high - low + 1e-10)
  - volume_spike = volume > volume.rolling(20, min_periods=1).mean() * 2.0
  - BUY (소진 저점):
      close < close.rolling(20, min_periods=1).min().shift(1)
      body_ratio < 0.3
      volume_spike
  - SELL (소진 고점):
      close > close.rolling(20, min_periods=1).max().shift(1)
      body_ratio < 0.3
      volume_spike
  - confidence HIGH: volume > volume.rolling(20).mean() * 3.0 else MEDIUM
  - 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


class ExhaustionReversalStrategy(BaseStrategy):
    name = "exhaustion_reversal"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="데이터 부족: 최소 25행 필요",
                invalidation="",
            )

        idx = len(df) - 2  # 마지막 완성봉

        close = df["close"]
        high = df["high"]
        low = df["low"]
        open_ = df["open"]
        volume = df["volume"]

        body = (close - open_).abs()
        hl_range = high - low
        body_ratio = body / (hl_range + 1e-10)

        vol_ma20 = volume.rolling(20, min_periods=1).mean()
        volume_spike = volume > vol_ma20 * 2.0

        close_min20 = close.rolling(20, min_periods=1).min().shift(1).ffill()
        close_max20 = close.rolling(20, min_periods=1).max().shift(1).ffill()

        close_val = float(close.iloc[idx])
        body_ratio_val = float(body_ratio.iloc[idx])
        volume_val = float(volume.iloc[idx])
        vol_ma_val = float(vol_ma20.iloc[idx])
        close_min_val = float(close_min20.iloc[idx])
        close_max_val = float(close_max20.iloc[idx])
        volume_spike_val = bool(volume_spike.iloc[idx])

        entry = close_val

        context = (
            f"close={entry:.4f} body_ratio={body_ratio_val:.3f} "
            f"volume={volume_val:.0f} vol_ma={vol_ma_val:.0f} "
            f"close_min20={close_min_val:.4f} close_max20={close_max_val:.4f}"
        )

        # BUY: 소진 저점
        if (
            close_val < close_min_val
            and body_ratio_val < 0.3
            and volume_spike_val
        ):
            confidence = (
                Confidence.HIGH
                if volume_val > vol_ma_val * 3.0
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Exhaustion Reversal BUY: 새 저점 close({entry:.4f})<min20({close_min_val:.4f}), "
                    f"body_ratio={body_ratio_val:.3f}<0.3, volume spike ({volume_val:.0f}>{vol_ma_val * 2:.0f})"
                ),
                invalidation=f"close > {close_min_val:.4f} 또는 volume_spike 소멸",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 소진 고점
        if (
            close_val > close_max_val
            and body_ratio_val < 0.3
            and volume_spike_val
        ):
            confidence = (
                Confidence.HIGH
                if volume_val > vol_ma_val * 3.0
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Exhaustion Reversal SELL: 새 고점 close({entry:.4f})>max20({close_max_val:.4f}), "
                    f"body_ratio={body_ratio_val:.3f}<0.3, volume spike ({volume_val:.0f}>{vol_ma_val * 2:.0f})"
                ),
                invalidation=f"close < {close_max_val:.4f} 또는 volume_spike 소멸",
                bull_case=context,
                bear_case=context,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"Exhaustion Reversal HOLD: 소진 조건 미충족 "
                f"body_ratio={body_ratio_val:.3f} volume_spike={volume_spike_val}"
            ),
            invalidation="",
            bull_case=context,
            bear_case=context,
        )
