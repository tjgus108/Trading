"""
HeikinAshiStrategy: Heikin-Ashi 캔들 기반 추세 추종 전략.
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class HeikinAshiStrategy(BaseStrategy):
    name = "heikin_ashi"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = float(last["close"])

        if len(df) < 10:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="데이터 부족 (최소 10행 필요)",
                invalidation="N/A",
            )

        # ── Heikin-Ashi 계산 ────────────────────────────────────────────
        ha_close_arr = ((df["open"] + df["high"] + df["low"] + df["close"]) / 4).values

        ha_open = [0.0] * len(df)
        ha_open[0] = (df["open"].iloc[0] + df["close"].iloc[0]) / 2
        for i in range(1, len(df)):
            ha_open[i] = (ha_open[i - 1] + ha_close_arr[i - 1]) / 2

        ha_open_s = pd.Series(ha_open, index=df.index)
        ha_close_s = pd.Series(ha_close_arr, index=df.index)
        ha_high_s = pd.concat([df["high"], ha_open_s, ha_close_s], axis=1).max(axis=1)
        ha_low_s = pd.concat([df["low"], ha_open_s, ha_close_s], axis=1).min(axis=1)

        idx = len(df) - 2  # 마지막 완성 캔들

        # 3봉 연속 확인
        bull_3 = all(ha_close_s.iloc[i] > ha_open_s.iloc[i] for i in range(idx - 2, idx + 1))
        bear_3 = all(ha_close_s.iloc[i] < ha_open_s.iloc[i] for i in range(idx - 2, idx + 1))

        low_rising = ha_low_s.iloc[idx - 1] >= ha_low_s.iloc[idx - 2]
        high_falling = ha_high_s.iloc[idx - 1] <= ha_high_s.iloc[idx - 2]

        ha_c = ha_close_s.iloc[idx]
        ha_o = ha_open_s.iloc[idx]
        ha_h = ha_high_s.iloc[idx]
        ha_l = ha_low_s.iloc[idx]

        # ── 신호 판단 ────────────────────────────────────────────────────
        if bull_3 and low_rising:
            no_upper_wick = ha_h == ha_c
            confidence = Confidence.HIGH if no_upper_wick else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Heikin-Ashi 3봉 연속 상승 캔들 (HA_Close > HA_Open) "
                    f"및 저점 상승 확인. HA_Close={ha_c:.4f}, HA_Open={ha_o:.4f}"
                ),
                invalidation=f"HA_Low 하락 시 무효. 현재 HA_Low={ha_l:.4f}",
                bull_case="연속 상승 HA 캔들로 강한 상승 추세",
                bear_case="위꼬리 발생 시 추세 약화 가능",
            )

        if bear_3 and high_falling:
            # 하락 캔들에서 아래꼬리 없음: HA_Low == HA_Close (close가 최저점)
            no_lower_wick = ha_l == ha_c
            confidence = Confidence.HIGH if no_lower_wick else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Heikin-Ashi 3봉 연속 하락 캔들 (HA_Close < HA_Open) "
                    f"및 고점 하락 확인. HA_Close={ha_c:.4f}, HA_Open={ha_o:.4f}"
                ),
                invalidation=f"HA_High 상승 시 무효. 현재 HA_High={ha_h:.4f}",
                bull_case="아래꼬리 발생 시 반등 가능",
                bear_case="연속 하락 HA 캔들로 강한 하락 추세",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning="HA 추세 조건 미충족 (HOLD)",
            invalidation="N/A",
        )
