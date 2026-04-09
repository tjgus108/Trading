"""
HATrendStrategy: Heikin-Ashi 추세 추종 전략 (꼬리 없음 조건 포함).
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class HATrendStrategy(BaseStrategy):
    name = "ha_trend"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = float(last["close"])

        if len(df) < 15:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="데이터 부족 (최소 15행 필요)",
                invalidation="N/A",
            )

        # ── Heikin-Ashi 계산 ────────────────────────────────────────────
        ha_close_arr = ((df["open"] + df["high"] + df["low"] + df["close"]) / 4).values

        ha_open_arr = [0.0] * len(df)
        ha_open_arr[0] = (df["open"].iloc[0] + df["close"].iloc[0]) / 2
        for i in range(1, len(df)):
            ha_open_arr[i] = (ha_open_arr[i - 1] + ha_close_arr[i - 1]) / 2

        ha_open_s = pd.Series(ha_open_arr, index=df.index)
        ha_close_s = pd.Series(ha_close_arr, index=df.index)
        ha_high_s = pd.concat([df["high"], ha_open_s, ha_close_s], axis=1).max(axis=1)
        ha_low_s = pd.concat([df["low"], ha_open_s, ha_close_s], axis=1).min(axis=1)

        idx = len(df) - 2  # 마지막 완성 캔들

        # ── 연속 양봉/음봉 카운트 ────────────────────────────────────────
        def _count_consecutive_bull(end_idx):
            count = 0
            for i in range(end_idx, -1, -1):
                if ha_close_s.iloc[i] > ha_open_s.iloc[i]:
                    count += 1
                else:
                    break
            return count

        def _count_consecutive_bear(end_idx):
            count = 0
            for i in range(end_idx, -1, -1):
                if ha_close_s.iloc[i] < ha_open_s.iloc[i]:
                    count += 1
                else:
                    break
            return count

        bull_count = _count_consecutive_bull(idx)
        bear_count = _count_consecutive_bear(idx)

        # 3봉 연속 확인
        bull_3 = bull_count >= 3
        bear_3 = bear_count >= 3

        # 꼬리 없음 조건: 최근 3봉 모두 확인
        def _no_lower_wick_3(end_idx):
            """BUY: ha_low >= ha_open * 0.999 (아래꼬리 없음)"""
            for i in range(end_idx - 2, end_idx + 1):
                if ha_low_s.iloc[i] < ha_open_s.iloc[i] * 0.999:
                    return False
            return True

        def _no_upper_wick_3(end_idx):
            """SELL: ha_high <= ha_open * 1.001 (위꼬리 없음)"""
            for i in range(end_idx - 2, end_idx + 1):
                if ha_high_s.iloc[i] > ha_open_s.iloc[i] * 1.001:
                    return False
            return True

        ha_c = float(ha_close_s.iloc[idx])
        ha_o = float(ha_open_s.iloc[idx])
        ha_h = float(ha_high_s.iloc[idx])
        ha_l = float(ha_low_s.iloc[idx])

        # ── BUY 판단 ─────────────────────────────────────────────────────
        if bull_3 and _no_lower_wick_3(idx):
            confidence = Confidence.HIGH if bull_count >= 5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"HA 연속 양봉 {bull_count}봉 (아래꼬리 없음). "
                    f"HA_Close={ha_c:.4f}, HA_Open={ha_o:.4f}"
                ),
                invalidation=f"HA 음봉 출현 시 무효. 현재 HA_Low={ha_l:.4f}",
                bull_case=f"연속 {bull_count}봉 HA 양봉으로 강한 상승 추세",
                bear_case="아래꼬리 출현 시 추세 약화 가능",
            )

        # ── SELL 판단 ────────────────────────────────────────────────────
        if bear_3 and _no_upper_wick_3(idx):
            confidence = Confidence.HIGH if bear_count >= 5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"HA 연속 음봉 {bear_count}봉 (위꼬리 없음). "
                    f"HA_Close={ha_c:.4f}, HA_Open={ha_o:.4f}"
                ),
                invalidation=f"HA 양봉 출현 시 무효. 현재 HA_High={ha_h:.4f}",
                bull_case="위꼬리 출현 시 반등 가능",
                bear_case=f"연속 {bear_count}봉 HA 음봉으로 강한 하락 추세",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning="HA 추세 조건 미충족 (3봉 연속 또는 꼬리 없음 조건 불충족)",
            invalidation="N/A",
        )
