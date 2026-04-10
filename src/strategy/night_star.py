"""
NightStarStrategy: Morning Star (BUY) / Evening Star (SELL) 3봉 반전 패턴.
- Morning Star BUY: 강한 음봉 → 도지/소형봉 → 강한 양봉
- Evening Star SELL: 강한 양봉 → 도지/소형봉 → 강한 음봉
- volume 확인으로 HIGH confidence 결정
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 15


class NightStarStrategy(BaseStrategy):
    name = "night_star"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "데이터 부족 (최소 15행 필요)")

        idx = len(df) - 2  # 마지막 완성 캔들

        close = df["close"]
        open_ = df["open"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        # 3봉 인덱스
        i0 = idx - 2  # base candle
        i1 = idx - 1  # star candle
        i2 = idx      # confirm candle

        c0 = float(close.iloc[i0])
        o0 = float(open_.iloc[i0])
        h0 = float(high.iloc[i0])
        l0 = float(low.iloc[i0])

        c1 = float(close.iloc[i1])
        o1 = float(open_.iloc[i1])
        h1 = float(high.iloc[i1])
        l1 = float(low.iloc[i1])

        c2 = float(close.iloc[i2])
        o2 = float(open_.iloc[i2])
        h2 = float(high.iloc[i2])
        l2 = float(low.iloc[i2])

        # NaN 체크
        vals = [c0, o0, h0, l0, c1, o1, h1, l1, c2, o2, h2, l2]
        if any(v != v for v in vals):
            return self._hold(df, "NaN 값 감지")

        base_body = abs(c0 - o0)
        star_body = abs(c1 - o1)
        confirm_body = abs(c2 - o2)

        base_range = h0 - l0
        star_range = h1 - l1
        confirm_range = h2 - l2

        base_body_ratio = base_body / (base_range + 1e-10)
        star_body_ratio = star_body / (star_range + 1e-10)
        confirm_body_ratio = confirm_body / (confirm_range + 1e-10)

        # volume 평균 (rolling 10)
        vol_mean = float(volume.rolling(10, min_periods=1).mean().iloc[i2])
        vol_confirm = float(volume.iloc[i2])
        high_vol = vol_confirm > vol_mean

        # doji 체크 (star candle)
        is_doji = (o1 == c1) or star_body == 0

        entry_price = c2

        # ── Morning Star (BUY) ────────────────────────────────────────────────
        base_bearish = c0 < o0
        base_strong = base_body_ratio > 0.5
        star_small = star_body_ratio < 0.35
        confirm_bullish = c2 > o2
        confirm_strong = confirm_body_ratio > 0.4

        if base_bearish and base_strong and star_small and confirm_bullish and confirm_strong:
            conf = Confidence.HIGH if (is_doji or high_vol) else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"Morning Star 패턴. "
                    f"base 음봉(body_ratio={base_body_ratio:.2f}), "
                    f"star 소형(body_ratio={star_body_ratio:.2f}), "
                    f"confirm 양봉(body_ratio={confirm_body_ratio:.2f}), "
                    f"vol_confirm={vol_confirm:.0f} vol_mean={vol_mean:.0f}"
                ),
                invalidation=f"star candle low {l1:.4f} 하회 시",
                bull_case="3봉 반전 Morning Star, 하락 추세 종료 기대",
                bear_case="확인 양봉 후 재하락 가능",
            )

        # ── Evening Star (SELL) ───────────────────────────────────────────────
        base_bullish = c0 > o0
        confirm_bearish = c2 < o2

        if base_bullish and base_strong and star_small and confirm_bearish and confirm_strong:
            conf = Confidence.HIGH if (is_doji or high_vol) else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"Evening Star 패턴. "
                    f"base 양봉(body_ratio={base_body_ratio:.2f}), "
                    f"star 소형(body_ratio={star_body_ratio:.2f}), "
                    f"confirm 음봉(body_ratio={confirm_body_ratio:.2f}), "
                    f"vol_confirm={vol_confirm:.0f} vol_mean={vol_mean:.0f}"
                ),
                invalidation=f"star candle high {h1:.4f} 상회 시",
                bull_case="하위 지지 반등 가능",
                bear_case="3봉 반전 Evening Star, 상승 추세 종료 기대",
            )

        return self._hold(df, "Morning/Evening Star 패턴 미감지")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
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
