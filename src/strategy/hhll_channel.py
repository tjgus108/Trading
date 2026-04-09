"""
HHLL Channel (Highest High / Lowest Low Channel) 전략:
- HH20 = 20봉 최고가 (현재봉 제외)
- LL20 = 20봉 최저가 (현재봉 제외)
- Position = (close - LL20) / Channel Width * 100  (0~100%)
- BUY: Position > 80 AND Volume > 20봉 평균
- SELL: Position < 20 AND Volume > 20봉 평균
- HOLD: 20 <= Position <= 80 또는 Volume 조건 미충족
- confidence: HIGH if Position > 90 (BUY) or Position < 10 (SELL), MEDIUM otherwise
- 최소 25행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_PERIOD = 20


class HHLLChannelStrategy(BaseStrategy):
    name = "hhll_channel"

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

        idx = len(df) - 2
        period = _PERIOD

        high_slice = df["high"].iloc[idx - period: idx]  # 현재봉 제외
        low_slice = df["low"].iloc[idx - period: idx]
        hh = float(high_slice.max())
        ll = float(low_slice.min())
        close = float(df["close"].iloc[idx])
        width = hh - ll
        pos = (close - ll) / max(width, 1e-10) * 100

        avg_vol = float(df["volume"].iloc[idx - 20: idx].mean())
        vol_ok = float(df["volume"].iloc[idx]) > avg_vol

        bull_case = (
            f"Position={pos:.1f}% (>80), 채널 상단 돌파 모멘텀. "
            f"HH={hh:.2f}, LL={ll:.2f}, close={close:.2f}, vol_ok={vol_ok}"
        )
        bear_case = (
            f"Position={pos:.1f}% (<20), 채널 하단 돌파 모멘텀. "
            f"HH={hh:.2f}, LL={ll:.2f}, close={close:.2f}, vol_ok={vol_ok}"
        )

        if pos > 80 and vol_ok:
            conf = Confidence.HIGH if pos > 90 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"HHLL Position={pos:.1f}% > 80 (상단 돌파). "
                    f"HH={hh:.2f}, LL={ll:.2f}, Width={width:.2f}, vol_ok={vol_ok}"
                ),
                invalidation=f"Position < 80 또는 Volume < 평균",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if pos < 20 and vol_ok:
            conf = Confidence.HIGH if pos < 10 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"HHLL Position={pos:.1f}% < 20 (하단 돌파). "
                    f"HH={hh:.2f}, LL={ll:.2f}, Width={width:.2f}, vol_ok={vol_ok}"
                ),
                invalidation=f"Position > 20 또는 Volume < 평균",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"HHLL Position={pos:.1f}% (20~80 또는 Volume 조건 미충족). "
                f"HH={hh:.2f}, LL={ll:.2f}, vol_ok={vol_ok}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
