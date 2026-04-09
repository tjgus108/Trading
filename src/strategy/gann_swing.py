"""
GannSwingStrategy: Gann Swing Chart 기반 매매 전략.

로직:
  - swing_high = high.rolling(5).max()
  - swing_low  = low.rolling(5).min()
  - Higher High (HH): swing_high > swing_high.shift(5)
  - Higher Low  (HL): swing_low  > swing_low.shift(5)
  - Lower  High (LH): swing_high < swing_high.shift(5)
  - Lower  Low  (LL): swing_low  < swing_low.shift(5)
  - BUY:  HH AND HL AND close > EMA20
  - SELL: LH AND LL AND close < EMA20
  - confidence HIGH: 위 두 조건 모두 + volume > avg_vol * 1.2
  - 최소 행: 20
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class GannSwingStrategy(BaseStrategy):
    name = "gann_swing"

    MIN_ROWS = 20

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: 최소 20행 필요",
                invalidation="",
            )

        last = self._last(df)

        high = df["high"]
        low = df["low"]
        close = df["close"]
        volume = df["volume"]

        swing_high = high.rolling(5).max()
        swing_low = low.rolling(5).min()

        # 마지막 완성봉 인덱스 = -2
        idx = len(df) - 2

        sh_now = swing_high.iloc[idx]
        sh_prev = swing_high.iloc[idx - 5] if idx >= 5 else None
        sl_now = swing_low.iloc[idx]
        sl_prev = swing_low.iloc[idx - 5] if idx >= 5 else None

        if sh_prev is None or sl_prev is None:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last["close"]),
                reasoning="데이터 부족: swing shift(5) 계산 불가",
                invalidation="",
            )

        hh = sh_now > sh_prev
        hl = sl_now > sl_prev
        lh = sh_now < sh_prev
        ll = sl_now < sl_prev

        # EMA20 계산 (컬럼이 없으면 직접 계산)
        if "ema20" in df.columns:
            ema20 = float(df["ema20"].iloc[idx])
        else:
            ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[idx])

        entry = float(last["close"])
        close_above_ema20 = entry > ema20
        close_below_ema20 = entry < ema20

        # 볼륨 필터
        vol_lookback = min(20, idx)
        avg_vol = volume.iloc[idx - vol_lookback: idx].mean()
        vol_ok = float(last["volume"]) > avg_vol * 1.2

        bull_case = (
            f"swing_high={sh_now:.4f} > prev={sh_prev:.4f} (HH={hh}), "
            f"swing_low={sl_now:.4f} > prev={sl_prev:.4f} (HL={hl}), "
            f"close={entry:.4f} EMA20={ema20:.4f}"
        )
        bear_case = (
            f"swing_high={sh_now:.4f} < prev={sh_prev:.4f} (LH={lh}), "
            f"swing_low={sl_now:.4f} < prev={sl_prev:.4f} (LL={ll}), "
            f"close={entry:.4f} EMA20={ema20:.4f}"
        )

        if hh and hl and close_above_ema20:
            confidence = Confidence.HIGH if vol_ok else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Gann Swing BUY: HH+HL (상승 스윙) AND close({entry:.4f}) > EMA20({ema20:.4f}). "
                    f"Vol filter: {vol_ok}"
                ),
                invalidation=f"Close below swing_low({sl_now:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if lh and ll and close_below_ema20:
            confidence = Confidence.HIGH if vol_ok else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Gann Swing SELL: LH+LL (하락 스윙) AND close({entry:.4f}) < EMA20({ema20:.4f}). "
                    f"Vol filter: {vol_ok}"
                ),
                invalidation=f"Close above swing_high({sh_now:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"Gann Swing HOLD: HH={hh} HL={hl} LH={lh} LL={ll} "
                f"close_above_ema20={close_above_ema20}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
