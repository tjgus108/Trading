"""
HeikenAshiTrendStrategy: Heiken Ashi 캔들로 순수 추세 파악.

로직:
  - HA 계산:
      ha_close = (open + high + low + close) / 4
      ha_open[0] = (open[0] + close[0]) / 2
      ha_open[i] = (ha_open[i-1] + ha_close[i-1]) / 2
      ha_high = max(high, ha_open, ha_close)
      ha_low  = min(low, ha_open, ha_close)
  - bullish_ha = ha_close > ha_open
  - BUY:  최근 3봉(idx-2, idx-1, idx) 모두 HA 양봉 AND ha_close[idx] > ha_close[idx-1]
  - SELL: 최근 3봉 모두 HA 음봉 AND ha_close[idx] < ha_close[idx-1]
  - confidence: HIGH if 5연속 같은 방향 HA 봉 else MEDIUM
  - 최소 데이터: 10행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 10


class HeikenAshiTrendStrategy(BaseStrategy):
    name = "heiken_ashi_trend"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for HeikenAshiTrend (min 10 rows)")

        n = len(df)
        ha_open = [0.0] * n
        ha_close = [0.0] * n

        ha_open[0] = (float(df["open"].iloc[0]) + float(df["close"].iloc[0])) / 2
        ha_close[0] = (
            float(df["open"].iloc[0])
            + float(df["high"].iloc[0])
            + float(df["low"].iloc[0])
            + float(df["close"].iloc[0])
        ) / 4

        for i in range(1, n):
            ha_close[i] = (
                float(df["open"].iloc[i])
                + float(df["high"].iloc[i])
                + float(df["low"].iloc[i])
                + float(df["close"].iloc[i])
            ) / 4
            ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2

        idx = len(df) - 2  # 마지막 완성 캔들

        # 최근 3봉 인덱스
        i0, i1, i2 = idx - 2, idx - 1, idx

        if i0 < 0:
            return self._hold(df, "Insufficient data for 3-candle check")

        bull_3 = (
            ha_close[i0] > ha_open[i0]
            and ha_close[i1] > ha_open[i1]
            and ha_close[i2] > ha_open[i2]
        )
        bear_3 = (
            ha_close[i0] < ha_open[i0]
            and ha_close[i1] < ha_open[i1]
            and ha_close[i2] < ha_open[i2]
        )

        # 5연속 확인 (HIGH confidence)
        streak = 1
        if ha_close[idx] > ha_open[idx]:
            # bullish streak
            for i in range(idx - 1, -1, -1):
                if ha_close[i] > ha_open[i]:
                    streak += 1
                else:
                    break
        elif ha_close[idx] < ha_open[idx]:
            # bearish streak
            for i in range(idx - 1, -1, -1):
                if ha_close[i] < ha_open[i]:
                    streak += 1
                else:
                    break

        conf = Confidence.HIGH if streak >= 5 else Confidence.MEDIUM

        ha_c_curr = ha_close[idx]
        ha_c_prev = ha_close[idx - 1]
        ha_o_curr = ha_open[idx]

        context = (
            f"ha_close={ha_c_curr:.4f} ha_open={ha_o_curr:.4f} "
            f"streak={streak}"
        )

        # BUY: 3봉 모두 양봉 + 상승 추세
        if bull_3 and ha_c_curr > ha_c_prev:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=float(df.iloc[idx]["close"]),
                reasoning=f"HeikenAshiTrend: HA 3봉 연속 양봉 + 상승 추세. {context}",
                invalidation="HA 음봉 전환 시",
                bull_case=f"연속 {streak}봉 HA 상승 추세 지속",
                bear_case="HA 음봉 발생 시 추세 전환",
            )

        # SELL: 3봉 모두 음봉 + 하락 추세
        if bear_3 and ha_c_curr < ha_c_prev:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=float(df.iloc[idx]["close"]),
                reasoning=f"HeikenAshiTrend: HA 3봉 연속 음봉 + 하락 추세. {context}",
                invalidation="HA 양봉 전환 시",
                bull_case="HA 양봉 발생 시 반등 가능",
                bear_case=f"연속 {streak}봉 HA 하락 추세 지속",
            )

        return self._hold(df, f"HeikenAshiTrend: 조건 미충족. {context}")

    def _hold(self, df: Optional[pd.DataFrame], reason: str) -> Signal:
        price = 0.0
        if df is not None and len(df) >= 2:
            try:
                price = float(self._last(df)["close"])
            except Exception:
                price = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
        )
