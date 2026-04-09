"""
AnchoredVWAPStrategy:
- 최근 50봉에서 가장 큰 갭(gap_pct > 3%) 위치를 anchor로 설정
- 없으면 최근 20봉 lowest low / highest high 포인트를 anchor로
- Anchored VWAP = sum(close*volume, anchor:) / sum(volume, anchor:)
- BUY: close > avwap AND close > EMA20 AND volume > avg_vol_20
- SELL: close < avwap AND close < EMA20 AND volume > avg_vol_20
- confidence: gap anchor 존재 AND |close/avwap - 1| > 1% → HIGH
- 최소 행: 25
"""

from typing import Optional, Tuple

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_GAP_THRESH = 0.03   # 3%
_HIGH_CONF_DEV = 0.01  # 1%


class AnchoredVWAPStrategy(BaseStrategy):
    name = "anchored_vwap"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2  # 마지막 완성봉 인덱스
        last = df.iloc[idx]
        close = float(last["close"])
        volume = float(last["volume"])

        # ── EMA20 ────────────────────────────────────────────────────────────
        ema20_series = df["close"].ewm(span=20, adjust=False).mean()
        ema20 = float(ema20_series.iloc[idx])

        # ── avg_vol_20 ───────────────────────────────────────────────────────
        avg_vol_20 = float(df["volume"].iloc[max(0, idx - 19):idx + 1].mean())

        # ── anchor 포인트 결정 ────────────────────────────────────────────────
        anchor_idx, gap_anchor = self._find_anchor(df, idx)

        # ── Anchored VWAP 계산 ───────────────────────────────────────────────
        avwap = self._calc_avwap(df, anchor_idx, idx)
        if avwap is None or avwap <= 0:
            return self._hold(df, "AVWAP calculation failed")

        # ── 신호 조건 ─────────────────────────────────────────────────────────
        vol_ok = volume > avg_vol_20
        dev = abs(close / avwap - 1.0)

        if gap_anchor and dev > _HIGH_CONF_DEV:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM

        bull = (
            f"close({close:.4f}) > AVWAP({avwap:.4f}), "
            f"EMA20={ema20:.4f}, vol={volume:.0f}>avg={avg_vol_20:.0f}"
        )
        bear = (
            f"close({close:.4f}) < AVWAP({avwap:.4f}), "
            f"EMA20={ema20:.4f}, vol={volume:.0f}>avg={avg_vol_20:.0f}"
        )

        if close > avwap and close > ema20 and vol_ok:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"close > AVWAP({avwap:.4f}) AND EMA20({ema20:.4f}) AND vol OK, "
                    f"gap_anchor={gap_anchor}, dev={dev*100:.2f}%"
                ),
                invalidation=f"close < AVWAP({avwap:.4f})",
                bull_case=bull,
                bear_case=bear,
            )

        if close < avwap and close < ema20 and vol_ok:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"close < AVWAP({avwap:.4f}) AND EMA20({ema20:.4f}) AND vol OK, "
                    f"gap_anchor={gap_anchor}, dev={dev*100:.2f}%"
                ),
                invalidation=f"close > AVWAP({avwap:.4f})",
                bull_case=bull,
                bear_case=bear,
            )

        return self._hold(
            df,
            f"No signal: close={close:.4f} AVWAP={avwap:.4f} EMA20={ema20:.4f} vol_ok={vol_ok}",
            bull,
            bear,
        )

    # ── 내부 헬퍼 ─────────────────────────────────────────────────────────────

    def _find_anchor(self, df: pd.DataFrame, idx: int) -> Tuple[int, bool]:
        """anchor 인덱스와 gap anchor 여부를 반환."""
        # 최근 50봉 (idx 포함, 이전 50봉)
        start50 = max(1, idx - 49)
        closes = df["close"].values

        best_gap_idx: Optional[int] = None
        best_gap_pct = 0.0

        for i in range(start50, idx + 1):
            prev_close = closes[i - 1]
            if prev_close == 0:
                continue
            gap_pct = abs(closes[i] - prev_close) / prev_close
            if gap_pct > _GAP_THRESH and gap_pct > best_gap_pct:
                best_gap_pct = gap_pct
                best_gap_idx = i

        if best_gap_idx is not None:
            return best_gap_idx, True

        # gap 없으면 최근 20봉 lowest low / highest high
        start20 = max(0, idx - 19)
        lows = df["low"].values
        highs = df["high"].values

        low_window = lows[start20: idx + 1]
        high_window = highs[start20: idx + 1]

        low_min = float(low_window.min())
        high_max = float(high_window.max())

        close_now = float(closes[idx])
        if abs(close_now - low_min) <= abs(close_now - high_max):
            # 현재 가격이 low에 가까우면 lowest low anchor
            local_idx = int(low_window.argmin()) + start20
        else:
            local_idx = int(high_window.argmax()) + start20

        return local_idx, False

    def _calc_avwap(
        self, df: pd.DataFrame, anchor_idx: int, idx: int
    ) -> Optional[float]:
        """anchor_idx부터 idx까지의 VWAP."""
        if anchor_idx > idx:
            return None
        sub = df.iloc[anchor_idx: idx + 1]
        vol_sum = float(sub["volume"].sum())
        if vol_sum == 0:
            return None
        cv_sum = float((sub["close"] * sub["volume"]).sum())
        return cv_sum / vol_sum

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
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
