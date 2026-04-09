"""
EMA Stack (Multi-EMA 정렬):
  ema8  = EWM(close, span=8)
  ema21 = EWM(close, span=21)
  ema50 = df["ema50"] (기존 컬럼 사용)

  Perfect Bull Stack:  ema8 > ema21 > ema50 AND close > ema8
  Perfect Bear Stack:  ema8 < ema21 < ema50 AND close < ema8

  BUY:  perfect_bull AND close > ema8 (stack 진입/유지)
  SELL: perfect_bear AND close < ema8

  confidence: HIGH if ema8/ema21/ema50 간격이 확대 중, MEDIUM 그 외
  최소 데이터: 55행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 55


class EMAStackStrategy(BaseStrategy):
    name = "ema_stack"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: EMA Stack 계산에 최소 55행 필요",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        ema8_series = df["close"].ewm(span=8, adjust=False).mean()
        ema21_series = df["close"].ewm(span=21, adjust=False).mean()

        last = self._last(df)  # df.iloc[-2]
        idx = -2  # _last 기준 인덱스

        close = float(last["close"])
        ema8 = float(ema8_series.iloc[idx])
        ema21 = float(ema21_series.iloc[idx])
        ema50 = float(last["ema50"])

        # 이전봉 값 (간격 확대 확인용)
        prev_ema8 = float(ema8_series.iloc[idx - 1])
        prev_ema21 = float(ema21_series.iloc[idx - 1])
        prev_ema50 = float(df["ema50"].iloc[idx - 1])

        perfect_bull = ema8 > ema21 > ema50
        perfect_bear = ema8 < ema21 < ema50

        # 간격 확대 여부
        bull_gap_now = (ema8 - ema21) + (ema21 - ema50)
        bull_gap_prev = (prev_ema8 - prev_ema21) + (prev_ema21 - prev_ema50)
        bear_gap_now = (ema21 - ema8) + (ema50 - ema21)
        bear_gap_prev = (prev_ema21 - prev_ema8) + (prev_ema50 - prev_ema21)

        bull_expanding = bull_gap_now > bull_gap_prev
        bear_expanding = bear_gap_now > bear_gap_prev

        bull_case = (
            f"EMA8={ema8:.4f} EMA21={ema21:.4f} EMA50={ema50:.4f} close={close:.4f} | "
            f"perfect_bull={perfect_bull}"
        )
        bear_case = (
            f"EMA8={ema8:.4f} EMA21={ema21:.4f} EMA50={ema50:.4f} close={close:.4f} | "
            f"perfect_bear={perfect_bear}"
        )

        if perfect_bull and close > ema8:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if bull_expanding else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"EMA Stack BUY: ema8({ema8:.4f}) > ema21({ema21:.4f}) > ema50({ema50:.4f}), "
                    f"close({close:.4f}) > ema8. 간격={'확대' if bull_expanding else '유지'}"
                ),
                invalidation=f"Close below ema8 ({ema8:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if perfect_bear and close < ema8:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH if bear_expanding else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"EMA Stack SELL: ema8({ema8:.4f}) < ema21({ema21:.4f}) < ema50({ema50:.4f}), "
                    f"close({close:.4f}) < ema8. 간격={'확대' if bear_expanding else '유지'}"
                ),
                invalidation=f"Close above ema8 ({ema8:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"EMA Stack HOLD: perfect_bull={perfect_bull}, perfect_bear={perfect_bear}, "
                f"ema8={ema8:.4f}, ema21={ema21:.4f}, ema50={ema50:.4f}, close={close:.4f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
