"""
HeikinAshiSmoothedStrategy: 5기간 EMA 스무딩 적용 Heikin-Ashi 추세 전략.

로직:
  - Heikin Ashi 캔들: ha_close = (o+h+l+c)/4, ha_open = (prev_ha_open + prev_ha_close)/2
  - 5기간 EMA 스무딩: ha_close_smooth = ha_close.ewm(span=5).mean()
  - Consecutive HA 양봉 >= 3 AND lower wick 없음(ha_low == ha_open) → BUY
  - Consecutive HA 음봉 >= 3 AND upper wick 없음(ha_high == ha_open) → SELL
  - confidence: >= 5연속 + wick 없음 → HIGH, 그 외 MEDIUM
  - 최소 행: 20
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_SMOOTH_SPAN = 5
_CONSEC_HIGH = 5


class HeikinAshiSmoothedStrategy(BaseStrategy):
    name = "ha_smoothed"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = float(last["close"])

        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="데이터 부족 (최소 20행 필요)",
                invalidation="N/A",
            )

        # ── Heikin-Ashi 계산 ────────────────────────────────────────────────
        ha_close_raw = (df["open"] + df["high"] + df["low"] + df["close"]) / 4

        ha_open_vals = [0.0] * len(df)
        ha_open_vals[0] = (df["open"].iloc[0] + df["close"].iloc[0]) / 2
        for i in range(1, len(df)):
            ha_open_vals[i] = (ha_open_vals[i - 1] + ha_close_raw.iloc[i - 1]) / 2

        ha_open_s = pd.Series(ha_open_vals, index=df.index)
        ha_close_s = pd.Series(ha_close_raw.values, index=df.index)

        # 5기간 EMA 스무딩
        ha_close_smooth = ha_close_s.ewm(span=_SMOOTH_SPAN, adjust=False).mean()

        ha_high_s = pd.concat([df["high"], ha_open_s, ha_close_smooth], axis=1).max(axis=1)
        ha_low_s = pd.concat([df["low"], ha_open_s, ha_close_smooth], axis=1).min(axis=1)

        idx = len(df) - 2  # 마지막 완성 캔들

        # ── 연속 봉 수 계산 ─────────────────────────────────────────────────
        bull_count = 0
        for i in range(idx, -1, -1):
            if ha_close_smooth.iloc[i] > ha_open_s.iloc[i]:
                bull_count += 1
            else:
                break

        bear_count = 0
        for i in range(idx, -1, -1):
            if ha_close_smooth.iloc[i] < ha_open_s.iloc[i]:
                bear_count += 1
            else:
                break

        ha_c = float(ha_close_smooth.iloc[idx])
        ha_o = float(ha_open_s.iloc[idx])
        ha_h = float(ha_high_s.iloc[idx])
        ha_l = float(ha_low_s.iloc[idx])

        # ── BUY 조건: >=3 연속 양봉 + lower wick 없음 (ha_low == ha_open) ──
        if bull_count >= 3:
            no_lower_wick = abs(ha_l - ha_o) < 1e-8
            if no_lower_wick:
                confidence = Confidence.HIGH if bull_count >= _CONSEC_HIGH else Confidence.MEDIUM
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"HA Smoothed {bull_count}봉 연속 상승 + lower wick 없음. "
                        f"HA_Close_Smooth={ha_c:.4f}, HA_Open={ha_o:.4f}"
                    ),
                    invalidation=f"HA_Low < HA_Open 발생 시 무효. 현재 HA_Low={ha_l:.4f}",
                    bull_case=f"연속 {bull_count}봉 상승 추세 지속",
                    bear_case="lower wick 발생 시 추세 약화",
                )

        # ── SELL 조건: >=3 연속 음봉 + upper wick 없음 (ha_high == ha_open) ─
        if bear_count >= 3:
            no_upper_wick = abs(ha_h - ha_o) < 1e-8
            if no_upper_wick:
                confidence = Confidence.HIGH if bear_count >= _CONSEC_HIGH else Confidence.MEDIUM
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"HA Smoothed {bear_count}봉 연속 하락 + upper wick 없음. "
                        f"HA_Close_Smooth={ha_c:.4f}, HA_Open={ha_o:.4f}"
                    ),
                    invalidation=f"HA_High > HA_Open 발생 시 무효. 현재 HA_High={ha_h:.4f}",
                    bull_case="upper wick 발생 시 반등 가능",
                    bear_case=f"연속 {bear_count}봉 하락 추세 지속",
                )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"HA Smoothed 조건 미충족 (HOLD). "
                f"bull_count={bull_count}, bear_count={bear_count}"
            ),
            invalidation="N/A",
        )
