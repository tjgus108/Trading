"""
Ichimoku Advanced 전략 (Chikou Span 추가):
- Tenkan-sen (9봉), Kijun-sen (26봉) — 기존과 동일
- Senkou A = (Tenkan + Kijun) / 2 (26봉 앞으로 기준 → 현재 idx에서 idx-26 위치값)
- Senkou B = (52봉 high + 52봉 low) / 2 (26봉 앞으로 기준)
- Chikou Span = 현재 close (26봉 뒤로 기준 → idx 위치 close vs idx-26 위치 close)
- 구름(Kumo): Senkou A vs Senkou B at 현재 시점
- BUY 조건 (3가지 모두):
  1. Tenkan > Kijun
  2. close > max(Senkou A, Senkou B) — 구름 위
  3. Chikou Span(curr close) > close 26봉 전
- SELL 조건: 반대
- confidence: HIGH if 구름 두께 > ATR, MEDIUM otherwise
- 최소 데이터: 60행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 80  # senkou_b(52) + displacement(26) + idx(2) = 80
_TENKAN_PERIOD = 9
_KIJUN_PERIOD = 26
_SENKOU_B_PERIOD = 52
_DISPLACEMENT = 26


class IchimokuAdvancedStrategy(BaseStrategy):
    name = "ichimoku_advanced"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2  # 마지막 완성 캔들

        # Tenkan-sen: 최근 9봉
        t_slice_h = df["high"].iloc[idx - _TENKAN_PERIOD + 1:idx + 1]
        t_slice_l = df["low"].iloc[idx - _TENKAN_PERIOD + 1:idx + 1]
        tenkan = (float(t_slice_h.max()) + float(t_slice_l.min())) / 2

        # Kijun-sen: 최근 26봉
        k_slice_h = df["high"].iloc[idx - _KIJUN_PERIOD + 1:idx + 1]
        k_slice_l = df["low"].iloc[idx - _KIJUN_PERIOD + 1:idx + 1]
        kijun = (float(k_slice_h.max()) + float(k_slice_l.min())) / 2

        # Senkou A, B — 26봉 앞으로 기준이므로 현재 시점(idx)의 구름 = idx-26 위치에서 계산
        senkou_idx = idx - _DISPLACEMENT  # 현재 구름값이 그려지는 기준 과거 인덱스

        if senkou_idx < _SENKOU_B_PERIOD - 1:
            return self._hold(df, "Insufficient data for Senkou")

        # Senkou A at senkou_idx: Tenkan(senkou_idx) + Kijun(senkou_idx)
        sa_t_h = df["high"].iloc[senkou_idx - _TENKAN_PERIOD + 1:senkou_idx + 1]
        sa_t_l = df["low"].iloc[senkou_idx - _TENKAN_PERIOD + 1:senkou_idx + 1]
        sa_tenkan = (float(sa_t_h.max()) + float(sa_t_l.min())) / 2

        sa_k_h = df["high"].iloc[senkou_idx - _KIJUN_PERIOD + 1:senkou_idx + 1]
        sa_k_l = df["low"].iloc[senkou_idx - _KIJUN_PERIOD + 1:senkou_idx + 1]
        sa_kijun = (float(sa_k_h.max()) + float(sa_k_l.min())) / 2

        senkou_a = (sa_tenkan + sa_kijun) / 2

        # Senkou B at senkou_idx: 52봉 high/low 중간값
        sb_h = df["high"].iloc[senkou_idx - _SENKOU_B_PERIOD + 1:senkou_idx + 1]
        sb_l = df["low"].iloc[senkou_idx - _SENKOU_B_PERIOD + 1:senkou_idx + 1]
        senkou_b = (float(sb_h.max()) + float(sb_l.min())) / 2

        kumo_top = max(senkou_a, senkou_b)
        kumo_bottom = min(senkou_a, senkou_b)
        kumo_thickness = kumo_top - kumo_bottom

        # Chikou Span: 현재 close를 26봉 뒤로 비교 → curr close vs close at (idx - 26)
        chikou_ref_idx = idx - _DISPLACEMENT
        chikou_ref_close = float(df["close"].iloc[chikou_ref_idx])
        curr_close = float(df["close"].iloc[idx])

        atr = float(df["atr14"].iloc[idx])
        confidence = (
            Confidence.HIGH if kumo_thickness > atr else Confidence.MEDIUM
        )

        context = (
            f"close={curr_close:.2f} tenkan={tenkan:.2f} kijun={kijun:.2f} "
            f"senkou_a={senkou_a:.2f} senkou_b={senkou_b:.2f} "
            f"kumo_thickness={kumo_thickness:.2f} atr={atr:.2f} "
            f"chikou_ref={chikou_ref_close:.2f}"
        )

        # BUY: 모두 충족
        buy_cross = tenkan > kijun
        buy_above_cloud = curr_close > kumo_top
        buy_chikou = curr_close > chikou_ref_close

        if buy_cross and buy_above_cloud and buy_chikou:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"Ichimoku Advanced BUY: tenkan({tenkan:.2f})>kijun({kijun:.2f}), "
                    f"close({curr_close:.2f})>kumo_top({kumo_top:.2f}), "
                    f"chikou({curr_close:.2f})>ref({chikou_ref_close:.2f})"
                ),
                invalidation=f"Close below kumo_top ({kumo_top:.2f}) or tenkan < kijun",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 모두 충족
        sell_cross = tenkan < kijun
        sell_below_cloud = curr_close < kumo_bottom
        sell_chikou = curr_close < chikou_ref_close

        if sell_cross and sell_below_cloud and sell_chikou:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"Ichimoku Advanced SELL: tenkan({tenkan:.2f})<kijun({kijun:.2f}), "
                    f"close({curr_close:.2f})<kumo_bottom({kumo_bottom:.2f}), "
                    f"chikou({curr_close:.2f})<ref({chikou_ref_close:.2f})"
                ),
                invalidation=f"Close above kumo_bottom ({kumo_bottom:.2f}) or tenkan > kijun",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
