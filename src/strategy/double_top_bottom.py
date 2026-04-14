"""
Double Top / Bottom 전략:
- Double Bottom (BUY): 최근 20봉에서 2개의 pivot low 탐지, 넥라인 돌파
- Double Top  (SELL): 최근 20봉에서 2개의 pivot high 탐지, 넥라인 하향 돌파
- confidence: HIGH if 넥라인 돌파폭 > 1%, MEDIUM 그 외
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_LOOKBACK = 20          # 최근 몇 봉 탐색
_PIVOT_WINDOW = 3       # pivot 확인용 앞뒤 봉 수
_PRICE_TOLERANCE = 0.02 # 두 저/고점 사이 허용 오차 (2%)
_NECKLINE_TOLERANCE = 0.005  # 넥라인 돌파 판정 여유 (0.5%)
_HIGH_CONF_THRESHOLD = 0.01  # 넥라인 돌파폭 > 1% → HIGH
_MIN_ROWS = 25


def _find_pivot_lows(series: pd.Series, window: int) -> list:
    """pivot low 인덱스 목록 반환 (앞뒤 window봉보다 낮은 지점)."""
    pivots = []
    n = len(series)
    for i in range(window, n - window):
        if series.iloc[i] == series.iloc[i - window: i + window + 1].min():
            pivots.append(i)
    return pivots


def _find_pivot_highs(series: pd.Series, window: int) -> list:
    """pivot high 인덱스 목록 반환 (앞뒤 window봉보다 높은 지점)."""
    pivots = []
    n = len(series)
    for i in range(window, n - window):
        if series.iloc[i] == series.iloc[i - window: i + window + 1].max():
            pivots.append(i)
    return pivots


class DoubleTopBottomStrategy(BaseStrategy):
    name = "double_top_bottom"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold_signal(0.0, "데이터 부족")

        last = self._last(df)   # df.iloc[-2]
        entry = float(last["close"])

        # 최근 _LOOKBACK+1봉 (진행 중인 봉 제외)
        window = df.iloc[-(_LOOKBACK + 2): -1]

        buy_signal, buy_breakout = self._check_double_bottom(window)
        sell_signal, sell_breakout = self._check_double_top(window)

        if buy_signal and not sell_signal:
            conf = Confidence.HIGH if buy_breakout > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Double Bottom 넥라인 돌파 ({buy_breakout:.1%})",
                invalidation="최근 저점 하향 돌파 시",
                bull_case=f"두 저점 수렴 후 넥라인 돌파 {buy_breakout:.1%}",
                bear_case="패턴 실패 가능",
            )

        if sell_signal and not buy_signal:
            conf = Confidence.HIGH if sell_breakout > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Double Top 넥라인 하향 돌파 ({sell_breakout:.1%})",
                invalidation="최근 고점 상향 돌파 시",
                bull_case="패턴 실패 가능",
                bear_case=f"두 고점 수렴 후 넥라인 하향 돌파 {sell_breakout:.1%}",
            )

        return self._hold_signal(entry, "Double Top/Bottom 패턴 없음")

    # ── Double Bottom ────────────────────────────────────────────────────────

    def _check_double_bottom(self, window: pd.DataFrame) -> "Tuple[bool, float]":
        lows = window["low"].reset_index(drop=True)
        closes = window["close"].reset_index(drop=True)
        n = len(lows)
        pivots = _find_pivot_lows(lows, _PIVOT_WINDOW)

        # low1은 현재로부터 최소 5봉 이전, low2는 가장 최근 pivot
        # low2: pivots 중 마지막 (가장 최근), low1: low2 이전 pivot
        valid_pivots = [p for p in pivots if p <= n - 1]
        if len(valid_pivots) < 2:
            return False, 0.0

        idx2 = valid_pivots[-1]
        # low2는 최소 5봉 이전이어야 함 (n-1 기준)
        if (n - 1 - idx2) < 5:
            # 뒤에서 두 번째 사용
            if len(valid_pivots) < 3:
                return False, 0.0
            idx2 = valid_pivots[-2]
            idx1 = valid_pivots[-3]
        else:
            idx1 = valid_pivots[-2]

        if idx1 >= idx2:
            return False, 0.0

        low1 = float(lows.iloc[idx1])
        low2 = float(lows.iloc[idx2])

        # 두 저점이 2% 이내
        if abs(low1 - low2) / low1 >= _PRICE_TOLERANCE:
            return False, 0.0

        # 넥라인 = low1~low2 구간 close 최대값
        neckline = float(closes.iloc[idx1: idx2 + 1].max())
        current_close = float(closes.iloc[-1])

        # 현재 close > neckline * (1 - tolerance)
        if current_close <= neckline * (1 - _NECKLINE_TOLERANCE):
            return False, 0.0

        breakout_pct = (current_close - neckline) / neckline
        return True, max(breakout_pct, 0.0)

    # ── Double Top ───────────────────────────────────────────────────────────

    def _check_double_top(self, window: pd.DataFrame) -> "Tuple[bool, float]":
        highs = window["high"].reset_index(drop=True)
        closes = window["close"].reset_index(drop=True)
        n = len(highs)
        pivots = _find_pivot_highs(highs, _PIVOT_WINDOW)

        valid_pivots = [p for p in pivots if p <= n - 1]
        if len(valid_pivots) < 2:
            return False, 0.0

        idx2 = valid_pivots[-1]
        if (n - 1 - idx2) < 5:
            if len(valid_pivots) < 3:
                return False, 0.0
            idx2 = valid_pivots[-2]
            idx1 = valid_pivots[-3]
        else:
            idx1 = valid_pivots[-2]

        if idx1 >= idx2:
            return False, 0.0

        high1 = float(highs.iloc[idx1])
        high2 = float(highs.iloc[idx2])

        # 두 고점이 2% 이내
        if abs(high1 - high2) / high1 >= _PRICE_TOLERANCE:
            return False, 0.0

        # 넥라인 = high1~high2 구간 close 최소값
        neckline = float(closes.iloc[idx1: idx2 + 1].min())
        current_close = float(closes.iloc[-1])

        # 현재 close < neckline * (1 + tolerance)
        if current_close >= neckline * (1 + _NECKLINE_TOLERANCE):
            return False, 0.0

        breakout_pct = (neckline - current_close) / neckline
        return True, max(breakout_pct, 0.0)

    # ── Helper ───────────────────────────────────────────────────────────────

    def _hold_signal(self, price: float, reason: str) -> Signal:
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
