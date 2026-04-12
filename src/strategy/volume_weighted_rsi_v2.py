"""
VolumeWeightedRSIV2Strategy: 거래량 가중 RSI v2 전략.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class VolumeWeightedRSIV2Strategy(BaseStrategy):
    name = "volume_weighted_rsi_v2"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = float(last["close"])

        if len(df) < 20:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="데이터 부족 (최소 20행 필요)",
                invalidation="N/A",
            )

        close = df["close"]
        volume = df["volume"]

        # ── VW-RSI 계산 ─────────────────────────────────────────────────
        delta = close.diff()
        vol_weight = volume / (volume.rolling(14, min_periods=1).mean() + 1e-10)
        weighted_gain = (delta.clip(lower=0) * vol_weight).rolling(14, min_periods=1).mean()
        weighted_loss = ((-delta.clip(upper=0)) * vol_weight).rolling(14, min_periods=1).mean()
        vw_rsi = 100 - 100 / (1 + weighted_gain / (weighted_loss + 1e-10))
        vw_rsi_ma = vw_rsi.rolling(5, min_periods=1).mean()  # noqa: F841

        idx = len(df) - 2  # 마지막 완성 캔들

        rsi_val = float(vw_rsi.iloc[idx])
        rsi_prev = float(vw_rsi.iloc[idx - 1])

        # NaN 체크
        if pd.isna(rsi_val) or pd.isna(rsi_prev):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN 감지 (HOLD)",
                invalidation="N/A",
            )

        # ── 신호 판단 ────────────────────────────────────────────────────
        if rsi_val < 35 and rsi_val > rsi_prev:
            confidence = Confidence.HIGH if rsi_val < 25 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"VW-RSI 과매도 반등: {rsi_prev:.2f} → {rsi_val:.2f} (임계값 35 미만)"
                ),
                invalidation=f"VW-RSI 재하락 시 무효. 현재={rsi_val:.2f}",
                bull_case="과매도 구간에서 거래량 가중 RSI 상승 반등",
                bear_case="추세 지속 시 추가 하락 가능",
            )

        if rsi_val > 65 and rsi_val < rsi_prev:
            confidence = Confidence.HIGH if rsi_val > 75 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"VW-RSI 과매수 하락: {rsi_prev:.2f} → {rsi_val:.2f} (임계값 65 초과)"
                ),
                invalidation=f"VW-RSI 재상승 시 무효. 현재={rsi_val:.2f}",
                bull_case="일시적 조정 후 재상승 가능",
                bear_case="과매수 구간에서 거래량 가중 RSI 하락",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"VW-RSI 조건 미충족 (현재={rsi_val:.2f}, HOLD)",
            invalidation="N/A",
        )
