"""
Price Channel Break Strategy: 20봉 채널 신규 돌파.

Turtle/Donchian과의 차별점:
- 볼륨 필터 없음, ATR 필터 없음, 55봉 없음
- "신규 돌파" 확인: 직전 3봉 중 최고가가 이미 entry_high 초과면 HOLD (이미 돌파된 상태)
- Exit channel: 10봉 최고/최저 (참고용)

BUY:  close > entry_high (20봉 고점 돌파) AND 직전 3봉 모두 close <= entry_high
SELL: close < entry_low (20봉 저점 이탈) AND 직전 3봉 모두 close >= entry_low

confidence HIGH: BUY 시 close > entry_high * 1.005 (0.5% 이상 돌파)
                 SELL 시 close < entry_low * 0.995 (0.5% 이상 이탈)
최소 행: 25
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 25


class PriceChannelBreakStrategy(BaseStrategy):
    name = "price_channel_break"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: Price Channel Break 계산에 최소 25행 필요",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        # _last() = df.iloc[-2]
        idx = len(df) - 2

        # Entry channel: 20봉 최고/최저 (현재봉 제외)
        entry_high = float(df["high"].iloc[idx - 20:idx].max())
        entry_low = float(df["low"].iloc[idx - 20:idx].min())

        # Exit channel: 10봉 최고/최저 (참고용)
        exit_high10 = float(df["high"].iloc[idx - 10:idx].max())
        exit_low10 = float(df["low"].iloc[idx - 10:idx].min())

        close = float(df["close"].iloc[idx])

        # 신규 돌파 확인: 직전 3봉(idx-3, idx-2, idx-1 → 하지만 idx는 이미 _last 기준)
        # 직전 3봉 = idx-3, idx-2, idx-1 중에서 idx-1은 현재봉, idx-2가 _last
        # 즉 idx-1(현재), idx(=_last), 그리고 "직전 3봉 내 BUY신호 없었는지"는
        # 완성된 봉 기준: idx-1, idx-2, idx-3 close 확인
        # 여기서 idx = len(df)-2 이므로:
        #   idx   = _last (현재 완성봉)
        #   idx-1 = 1봉 전
        #   idx-2 = 2봉 전
        #   idx-3 = 3봉 전
        prev_closes = [
            float(df["close"].iloc[idx - 1]),
            float(df["close"].iloc[idx - 2]),
            float(df["close"].iloc[idx - 3]),
        ]

        # 직전 3봉이 이미 entry_high 초과 → 이미 돌파된 상태 (신규 아님)
        already_broken_up = any(c > entry_high for c in prev_closes)
        # 직전 3봉이 이미 entry_low 하향 → 이미 이탈된 상태
        already_broken_down = any(c < entry_low for c in prev_closes)

        broke_up = close > entry_high and not already_broken_up
        broke_down = close < entry_low and not already_broken_down

        # confidence: 0.5% 이상 돌파
        high_conf_buy = close > entry_high * 1.005
        high_conf_sell = close < entry_low * 0.995

        bull_case = (
            f"close={close:.4f} > entry_high={entry_high:.4f} "
            f"(신규돌파={broke_up}, already_broken={already_broken_up})"
        )
        bear_case = (
            f"close={close:.4f} < entry_low={entry_low:.4f} "
            f"(신규이탈={broke_down}, already_broken={already_broken_down})"
        )

        if broke_up:
            conf = Confidence.HIGH if high_conf_buy else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Price Channel Break BUY: close({close:.4f}) > 20봉 고점({entry_high:.4f}) 신규 돌파. "
                    f"돌파폭={((close/entry_high)-1)*100:.2f}%. "
                    f"Exit channel (10봉 저점): {exit_low10:.4f}"
                ),
                invalidation=f"20봉 고점({entry_high:.4f}) 아래로 재진입",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if broke_down:
            conf = Confidence.HIGH if high_conf_sell else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Price Channel Break SELL: close({close:.4f}) < 20봉 저점({entry_low:.4f}) 신규 이탈. "
                    f"이탈폭={((entry_low/close)-1)*100:.2f}%. "
                    f"Exit channel (10봉 고점): {exit_high10:.4f}"
                ),
                invalidation=f"20봉 저점({entry_low:.4f}) 위로 회복",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"Price Channel Break HOLD: close={close:.4f}, "
                f"20봉 range=[{entry_low:.4f}, {entry_high:.4f}]. "
                f"broke_up={broke_up}, broke_down={broke_down}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
