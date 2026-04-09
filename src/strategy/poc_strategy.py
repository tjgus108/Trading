"""
POCStrategy: Volume Profile Point of Control (POC) 기반 전략.

- 최근 20봉의 가격 범위를 10개 bin으로 나눠 볼륨 가중 분포 계산
- POC = 볼륨이 가장 많은 bin 중앙값
- VAH = POC 기준 위 70% 거래량 경계
- VAL = POC 기준 아래 70% 거래량 경계
- BUY: close < VAL (가치 영역 아래)
- SELL: close > VAH (가치 영역 위)
- confidence: |close - POC| / POC > 2% → HIGH
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

NUM_BINS = 10
LOOKBACK = 20
VALUE_AREA_PCT = 0.70
HIGH_CONF_THRESHOLD = 0.02


def _compute_volume_profile(
    df: pd.DataFrame, idx: int
) -> Optional[Tuple[float, float, float]]:
    """
    idx 기준 최근 LOOKBACK봉 볼륨 프로파일 계산.
    Returns (poc, vah, val) or None if range is zero.
    """
    start = max(0, idx - LOOKBACK + 1)
    highs = df["high"].iloc[start : idx + 1]
    lows = df["low"].iloc[start : idx + 1]
    closes = df["close"].iloc[start : idx + 1]
    volumes = df["volume"].iloc[start : idx + 1]

    low_val = lows.min()
    high_val = highs.max()
    price_range = high_val - low_val

    if price_range == 0:
        return None

    bin_size = price_range / NUM_BINS
    bins = [low_val + i * bin_size for i in range(NUM_BINS + 1)]

    # 각 봉의 close가 속하는 bin에 volume 누적
    bin_volumes = np.zeros(NUM_BINS)
    for close, vol in zip(closes, volumes):
        bin_idx = int((close - low_val) / bin_size)
        bin_idx = min(bin_idx, NUM_BINS - 1)
        bin_volumes[bin_idx] += vol

    total_vol = bin_volumes.sum()
    if total_vol == 0:
        return None

    # POC: 가장 많은 볼륨의 bin 중앙값
    poc_bin = int(np.argmax(bin_volumes))
    poc = (bins[poc_bin] + bins[poc_bin + 1]) / 2.0

    # Value Area: POC 부터 위아래로 70% 볼륨 채우기
    va_target = total_vol * VALUE_AREA_PCT
    va_vol = bin_volumes[poc_bin]
    upper = poc_bin
    lower = poc_bin

    while va_vol < va_target:
        above_vol = bin_volumes[upper + 1] if upper + 1 < NUM_BINS else 0.0
        below_vol = bin_volumes[lower - 1] if lower - 1 >= 0 else 0.0

        if above_vol == 0 and below_vol == 0:
            break

        if above_vol >= below_vol and upper + 1 < NUM_BINS:
            upper += 1
            va_vol += bin_volumes[upper]
        elif lower - 1 >= 0:
            lower -= 1
            va_vol += bin_volumes[lower]
        else:
            upper += 1
            va_vol += bin_volumes[upper]

    vah = (bins[upper] + bins[upper + 1]) / 2.0
    val = (bins[lower] + bins[lower + 1]) / 2.0

    return poc, vah, val


class POCStrategy(BaseStrategy):
    name = "poc_strategy"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 25:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="데이터 부족 (최소 25봉 필요)",
                invalidation="",
            )

        last = self._last(df)
        idx = len(df) - 2  # _last와 동일한 인덱스
        close = float(last["close"])

        result = _compute_volume_profile(df, idx)
        if result is None:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning="가격 범위 0 — 볼륨 프로파일 계산 불가",
                invalidation="",
            )

        poc, vah, val = result
        dist_pct = abs(close - poc) / poc if poc != 0 else 0.0
        confidence = Confidence.HIGH if dist_pct > HIGH_CONF_THRESHOLD else Confidence.MEDIUM

        if close < val:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"close={close:.4f} < VAL={val:.4f}. "
                    f"POC={poc:.4f}, VAH={vah:.4f}. dist={dist_pct*100:.2f}%"
                ),
                invalidation=f"Close below VAL ({val:.4f}) 지속 or 추세 전환",
                bull_case=f"가치 영역 아래 → POC({poc:.4f})까지 회귀 기대",
                bear_case=f"추세 하락 지속 시 VAL 이탈 확대",
            )

        if close > vah:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"close={close:.4f} > VAH={vah:.4f}. "
                    f"POC={poc:.4f}, VAL={val:.4f}. dist={dist_pct*100:.2f}%"
                ),
                invalidation=f"Close above VAH ({vah:.4f}) 지속 or 브레이크아웃",
                bull_case=f"강한 상승 돌파 시 VAH 지지로 전환 가능",
                bear_case=f"가치 영역 위 → POC({poc:.4f})까지 회귀 기대",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"close={close:.4f} 가치 영역 내 (VAL={val:.4f} ~ VAH={vah:.4f}). "
                f"POC={poc:.4f}"
            ),
            invalidation="",
            bull_case=f"VAH({vah:.4f}) 상향 돌파 시 SELL 전환",
            bear_case=f"VAL({val:.4f}) 하향 이탈 시 BUY 전환",
        )
