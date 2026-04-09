"""
Momentum Reversal 전략:
- mom14 = close - close.shift(14)
- mom_ema = EWM(mom14, span=9)
- BUY:  mom14 < 0 AND mom_ema > mom_ema.shift(1) AND close > close.shift(1)
- SELL: mom14 > 0 AND mom_ema < mom_ema.shift(1) AND close < close.shift(1)
- confidence: HIGH if |mom14| > std(mom14, 20), MEDIUM 그 외
- 최소 데이터: 25행
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_MOM_PERIOD = 14
_EMA_SPAN = 9
_STD_PERIOD = 20


class MomentumReversalStrategy(BaseStrategy):
    """모멘텀 반전 전략."""

    name = "momentum_reversal"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-2]),
                reasoning=f"데이터 부족: {len(df)}행 < {_MIN_ROWS}행 필요",
                invalidation="충분한 히스토리 데이터 확보 후 재시도",
            )

        close = df["close"]

        # 지표 계산
        mom14 = close - close.shift(_MOM_PERIOD)
        mom_ema = mom14.ewm(span=_EMA_SPAN, adjust=False).mean()
        mom14_std = mom14.rolling(_STD_PERIOD).std()

        idx = len(df) - 2

        m14 = float(mom14.iloc[idx])
        m_ema_cur = float(mom_ema.iloc[idx])
        m_ema_prev = float(mom_ema.iloc[idx - 1])
        close_cur = float(close.iloc[idx])
        close_prev = float(close.iloc[idx - 1])
        std_val = float(mom14_std.iloc[idx]) if not pd.isna(mom14_std.iloc[idx]) else 0.0

        # confidence
        if std_val > 0 and abs(m14) > std_val:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM

        context = (
            f"close={close_cur:.2f} mom14={m14:.4f} "
            f"mom_ema={m_ema_cur:.4f} mom_ema_prev={m_ema_prev:.4f} "
            f"std={std_val:.4f}"
        )

        # BUY: 음수 모멘텀에서 회복
        if m14 < 0 and m_ema_cur > m_ema_prev and close_cur > close_prev:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_cur,
                reasoning=(
                    f"모멘텀 반전 상승: mom14={m14:.4f} < 0, "
                    f"mom_ema 회복({m_ema_prev:.4f}→{m_ema_cur:.4f}), "
                    f"close 상승({close_prev:.2f}→{close_cur:.2f})"
                ),
                invalidation="mom14 양전환 또는 mom_ema 재하락 시 무효",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 양수 모멘텀에서 약화
        if m14 > 0 and m_ema_cur < m_ema_prev and close_cur < close_prev:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_cur,
                reasoning=(
                    f"모멘텀 반전 하락: mom14={m14:.4f} > 0, "
                    f"mom_ema 약화({m_ema_prev:.4f}→{m_ema_cur:.4f}), "
                    f"close 하락({close_prev:.2f}→{close_cur:.2f})"
                ),
                invalidation="mom14 음전환 또는 mom_ema 재상승 시 무효",
                bull_case=context,
                bear_case=context,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_cur,
            reasoning=f"조건 미충족: {context}",
            invalidation="반전 조건 충족 시 재평가",
            bull_case=context,
            bear_case=context,
        )
