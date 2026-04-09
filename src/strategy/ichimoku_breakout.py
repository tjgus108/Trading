"""
IchimokuBreakoutStrategy:
- 기존 ichimoku.py(Tenkan>Kijun 단순), ichimoku_advanced.py(Chikou 포함),
  ichimoku_cloud_pos.py(구름 내 위치)와 차별화:
  TK Cross (크로스 순간) + 구름 위/아래 위치 기반 진입
- Tenkan-sen: (high.rolling(9).max() + low.rolling(9).min()) / 2
- Kijun-sen: (high.rolling(26).max() + low.rolling(26).min()) / 2
- Senkou A = ((tenkan + kijun) / 2).shift(26)
- Senkou B = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
- kumo_top = max(senkou_a, senkou_b), kumo_bottom = min(senkou_a, senkou_b)
- BUY: Tenkan crosses above Kijun (prev tenkan<=kijun, curr tenkan>kijun)
        AND close > kumo_top
- SELL: Tenkan crosses below Kijun (prev tenkan>=kijun, curr tenkan<kijun)
        AND close < kumo_bottom
- confidence: distance_to_kumo / close > 2% → HIGH, otherwise MEDIUM
- 최소 행: 80
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 80


def _tenkan(high: pd.Series, low: pd.Series) -> pd.Series:
    return (high.rolling(9).max() + low.rolling(9).min()) / 2


def _kijun(high: pd.Series, low: pd.Series) -> pd.Series:
    return (high.rolling(26).max() + low.rolling(26).min()) / 2


def _senkou_a(tenkan: pd.Series, kijun: pd.Series) -> pd.Series:
    return ((tenkan + kijun) / 2).shift(26)


def _senkou_b(high: pd.Series, low: pd.Series) -> pd.Series:
    return ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)


class IchimokuBreakoutStrategy(BaseStrategy):
    name = "ichimoku_breakout"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "데이터 부족")

        high = df["high"]
        low = df["low"]
        close = df["close"]

        tenkan = _tenkan(high, low)
        kijun = _kijun(high, low)
        senkou_a = _senkou_a(tenkan, kijun)
        senkou_b = _senkou_b(high, low)

        # 마지막 완성봉 인덱스 (-2)
        idx = len(df) - 2

        tk_curr = float(tenkan.iloc[idx])
        tk_prev = float(tenkan.iloc[idx - 1])
        kj_curr = float(kijun.iloc[idx])
        kj_prev = float(kijun.iloc[idx - 1])

        sa_curr = float(senkou_a.iloc[idx])
        sb_curr = float(senkou_b.iloc[idx])
        close_curr = float(close.iloc[idx])

        # NaN 체크
        if any(v != v for v in (tk_curr, tk_prev, kj_curr, kj_prev, sa_curr, sb_curr)):
            return self._hold(df, "데이터 부족 (NaN)")

        kumo_top = max(sa_curr, sb_curr)
        kumo_bottom = min(sa_curr, sb_curr)

        # TK Cross 감지
        bullish_cross = (tk_prev <= kj_prev) and (tk_curr > kj_curr)
        bearish_cross = (tk_prev >= kj_prev) and (tk_curr < kj_curr)

        # Confidence: 구름까지 거리
        if close_curr > kumo_top:
            distance = (close_curr - kumo_top) / close_curr
        elif close_curr < kumo_bottom:
            distance = (kumo_bottom - close_curr) / close_curr
        else:
            distance = 0.0

        confidence = Confidence.HIGH if distance > 0.02 else Confidence.MEDIUM

        context = (
            f"close={close_curr:.2f} tenkan={tk_curr:.2f} kijun={kj_curr:.2f} "
            f"kumo_top={kumo_top:.2f} kumo_bottom={kumo_bottom:.2f} "
            f"dist={distance:.4f}"
        )

        if bullish_cross and close_curr > kumo_top:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_curr,
                reasoning=(
                    f"Ichimoku Breakout BUY: TK cross(tenkan {tk_prev:.2f}→{tk_curr:.2f} "
                    f"> kijun {kj_curr:.2f}), close({close_curr:.2f})>kumo_top({kumo_top:.2f})"
                ),
                invalidation=f"Close below kumo_top ({kumo_top:.2f}) or TK cross 실패",
                bull_case=context,
                bear_case=context,
            )

        if bearish_cross and close_curr < kumo_bottom:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_curr,
                reasoning=(
                    f"Ichimoku Breakout SELL: TK cross(tenkan {tk_prev:.2f}→{tk_curr:.2f} "
                    f"< kijun {kj_curr:.2f}), close({close_curr:.2f})<kumo_bottom({kumo_bottom:.2f})"
                ),
                invalidation=f"Close above kumo_bottom ({kumo_bottom:.2f}) or TK cross 실패",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        close_now = float(df["close"].iloc[-2]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_now,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
