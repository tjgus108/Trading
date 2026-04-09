"""
CupHandleStrategy:
  최근 60봉에서 Cup & Handle 패턴 탐지.

  Cup: 좌측 고점 → 하락 → 우측 고점 (U자형)
    - 너비: 20~50봉
    - 깊이: 10~40%

  Handle: Cup 우측 후 3~10봉 소폭 조정
    - 깊이 < Cup 깊이의 1/3

  BUY: Handle 후 close > 우측 고점 돌파
  SELL: 미지원 (HOLD)
  confidence: 돌파 볼륨 > 평균 볼륨 1.5배 → HIGH, 그 외 MEDIUM
  최소 행: 60
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 60
CUP_WIDTH_MIN = 20
CUP_WIDTH_MAX = 50
CUP_DEPTH_MIN = 0.10
CUP_DEPTH_MAX = 0.40
HANDLE_BARS_MIN = 3
HANDLE_BARS_MAX = 10


class CupHandleStrategy(BaseStrategy):
    name = "cup_handle"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: Cup & Handle 계산에 최소 60행 필요",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        last = self._last(df)  # df.iloc[-2]
        close = float(last["close"])
        last_idx = len(df) - 2  # _last 기준 인덱스

        cup_result = self._find_cup_and_handle(df, last_idx)

        if cup_result is None:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning="Cup & Handle 패턴 미감지",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        cup_left, cup_bottom_idx, cup_right, cup_depth, handle_low, right_high = cup_result

        # BUY 조건: close > 우측 고점 (돌파)
        if close > right_high:
            avg_vol = float(df["volume"].iloc[max(0, last_idx - 20):last_idx].mean())
            last_vol = float(last["volume"])
            high_conf = avg_vol > 0 and last_vol > avg_vol * 1.5

            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if high_conf else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Cup & Handle BUY: 우측 고점({right_high:.4f}) 돌파, "
                    f"cup_depth={cup_depth:.1%}, close={close:.4f}"
                ),
                invalidation=f"Close below handle_low {handle_low:.4f}",
                bull_case=(
                    f"Cup 너비={cup_right - cup_left}봉, 깊이={cup_depth:.1%}, "
                    f"우측 고점={right_high:.4f} 돌파"
                ),
                bear_case=f"Handle low {handle_low:.4f} 이탈 시 패턴 무효화",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"Cup & Handle 감지됐으나 돌파 미완: "
                f"close={close:.4f}, 우측 고점={right_high:.4f}"
            ),
            invalidation=f"Close below handle_low {handle_low:.4f}",
            bull_case=f"우측 고점 {right_high:.4f} 돌파 시 BUY",
            bear_case="",
        )

    def _find_cup_and_handle(
        self, df: pd.DataFrame, last_idx: int
    ) -> Optional[Tuple[int, int, int, float, float, float]]:
        """
        Cup & Handle 패턴 탐지.
        Returns (cup_left, cup_bottom_idx, cup_right, cup_depth, handle_low, right_high)
        또는 None.
        """
        closes = df["close"].values

        # cup_right는 handle을 포함해야 하므로 last_idx - HANDLE_BARS_MIN 이전
        # cup_right 범위: last_idx - HANDLE_BARS_MAX ~ last_idx - HANDLE_BARS_MIN
        for handle_len in range(HANDLE_BARS_MIN, HANDLE_BARS_MAX + 1):
            cup_right = last_idx - handle_len
            if cup_right < 1:
                continue

            right_high = float(closes[cup_right])

            # cup 너비 범위로 cup_left 탐색
            for cup_width in range(CUP_WIDTH_MIN, CUP_WIDTH_MAX + 1):
                cup_left = cup_right - cup_width
                if cup_left < 0:
                    break

                left_high = float(closes[cup_left])

                # 좌우 고점이 비슷해야 함 (10% 이내 차이)
                if abs(left_high - right_high) / max(left_high, right_high) > 0.10:
                    continue

                # Cup 내부 최저점 찾기
                cup_slice = closes[cup_left: cup_right + 1]
                bottom_offset = int(np.argmin(cup_slice))
                cup_bottom_idx = cup_left + bottom_offset
                cup_bottom = float(cup_slice[bottom_offset])

                # Cup rim (좌우 평균)
                cup_rim = (left_high + right_high) / 2.0
                if cup_rim <= 0:
                    continue

                cup_depth = (cup_rim - cup_bottom) / cup_rim

                # 깊이 조건: 10~40%
                if not (CUP_DEPTH_MIN <= cup_depth <= CUP_DEPTH_MAX):
                    continue

                # U자형: 바닥이 cup 중간 40% 구간에 있어야 함
                mid_start = cup_left + int(cup_width * 0.30)
                mid_end = cup_left + int(cup_width * 0.70)
                if not (mid_start <= cup_bottom_idx <= mid_end):
                    continue

                # Handle: cup_right 이후 last_idx까지
                handle_slice = closes[cup_right: last_idx + 1]
                if len(handle_slice) < 2:
                    continue

                handle_low = float(np.min(handle_slice))

                # Handle 깊이 < Cup 깊이의 1/3
                handle_depth = (right_high - handle_low) / right_high if right_high > 0 else 0
                if handle_depth >= cup_depth / 3.0:
                    continue

                # Handle은 right_high 아래에 있어야 함 (조정)
                if handle_low >= right_high:
                    continue

                return (cup_left, cup_bottom_idx, cup_right, cup_depth, handle_low, right_high)

        return None
