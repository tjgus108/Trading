"""
Ichimoku Cloud Position 전략:
- 현재 구름 위/아래 위치 기반 신호
- BUY:  close > cloud_top AND tenkan > kijun
- SELL: close < cloud_bottom AND tenkan < kijun
- confidence: HIGH if close distance from cloud > 2%, MEDIUM 그 외
- 최소 데이터: 80행 (52+26+2)
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 80
_TENKAN_PERIOD = 9
_KIJUN_PERIOD = 26
_SENKOU_B_PERIOD = 52
_DISPLACEMENT = 26
_HIGH_CONF_DISTANCE = 0.02  # 2% 이격


class IchimokuCloudPosStrategy(BaseStrategy):
    name = "ichimoku_cloud_pos"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2  # _last() 기준 마지막 완성 캔들

        # Tenkan-sen: 최근 9봉
        tenkan = (
            float(df["high"].iloc[idx - _TENKAN_PERIOD + 1:idx + 1].max())
            + float(df["low"].iloc[idx - _TENKAN_PERIOD + 1:idx + 1].min())
        ) / 2

        # Kijun-sen: 최근 26봉
        kijun = (
            float(df["high"].iloc[idx - _KIJUN_PERIOD + 1:idx + 1].max())
            + float(df["low"].iloc[idx - _KIJUN_PERIOD + 1:idx + 1].min())
        ) / 2

        # 현재 구름: senkou_a.shift(26), senkou_b.shift(26) — idx-26 위치에서 계산
        senkou_idx = idx - _DISPLACEMENT

        # Senkou A at senkou_idx
        sa_tenkan = (
            float(df["high"].iloc[senkou_idx - _TENKAN_PERIOD + 1:senkou_idx + 1].max())
            + float(df["low"].iloc[senkou_idx - _TENKAN_PERIOD + 1:senkou_idx + 1].min())
        ) / 2
        sa_kijun = (
            float(df["high"].iloc[senkou_idx - _KIJUN_PERIOD + 1:senkou_idx + 1].max())
            + float(df["low"].iloc[senkou_idx - _KIJUN_PERIOD + 1:senkou_idx + 1].min())
        ) / 2
        senkou_a = (sa_tenkan + sa_kijun) / 2

        # Senkou B at senkou_idx: 52봉 high/low 중간값
        senkou_b = (
            float(df["high"].iloc[senkou_idx - _SENKOU_B_PERIOD + 1:senkou_idx + 1].max())
            + float(df["low"].iloc[senkou_idx - _SENKOU_B_PERIOD + 1:senkou_idx + 1].min())
        ) / 2

        cloud_top = max(senkou_a, senkou_b)
        cloud_bottom = min(senkou_a, senkou_b)

        close = float(df["close"].iloc[idx])

        # confidence: close와 구름 경계 거리 기준
        if close > cloud_top:
            dist_pct = (close - cloud_top) / cloud_top if cloud_top != 0 else 0.0
        elif close < cloud_bottom:
            dist_pct = (cloud_bottom - close) / cloud_bottom if cloud_bottom != 0 else 0.0
        else:
            dist_pct = 0.0

        confidence = Confidence.HIGH if dist_pct >= _HIGH_CONF_DISTANCE else Confidence.MEDIUM

        context = (
            f"close={close:.2f} tenkan={tenkan:.2f} kijun={kijun:.2f} "
            f"cloud_top={cloud_top:.2f} cloud_bottom={cloud_bottom:.2f} "
            f"dist_pct={dist_pct:.4f}"
        )

        # BUY: 구름 위 AND tenkan > kijun
        if close > cloud_top and tenkan > kijun:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Cloud Position BUY: close({close:.2f})>cloud_top({cloud_top:.2f}), "
                    f"tenkan({tenkan:.2f})>kijun({kijun:.2f})"
                ),
                invalidation=f"Close below cloud_top ({cloud_top:.2f}) or tenkan < kijun",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 구름 아래 AND tenkan < kijun
        if close < cloud_bottom and tenkan < kijun:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Cloud Position SELL: close({close:.2f})<cloud_bottom({cloud_bottom:.2f}), "
                    f"tenkan({tenkan:.2f})<kijun({kijun:.2f})"
                ),
                invalidation=f"Close above cloud_bottom ({cloud_bottom:.2f}) or tenkan > kijun",
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
