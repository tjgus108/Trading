"""
Williams Fractal 전략:
- 5봉 패턴으로 Bullish/Bearish Fractal 탐지
- BUY: 최근 5봉 내 bullish fractal + close > ema50
- SELL: 최근 5봉 내 bearish fractal + close < ema50
- Confidence: HIGH if RSI 확인 (BUY: rsi<50, SELL: rsi>50), MEDIUM otherwise
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 15
_FRACTAL_LOOKBACK = 5  # 최근 5봉 내 fractal 탐색


def _has_bullish_fractal(df: pd.DataFrame, idx: int) -> "tuple[bool, object]":
    """idx-2 위치가 5봉 중 중심인 bullish fractal 탐지."""
    if idx < 4:
        return False, None
    center = idx - 2
    low_c = df["low"].iloc[center]
    for j in [center - 2, center - 1, center + 1, center + 2]:
        if df["low"].iloc[j] <= low_c:
            return False, None
    return True, low_c


def _has_bearish_fractal(df: pd.DataFrame, idx: int) -> "tuple[bool, object]":
    """idx-2 위치가 5봉 중 중심인 bearish fractal 탐지."""
    if idx < 4:
        return False, None
    center = idx - 2
    high_c = df["high"].iloc[center]
    for j in [center - 2, center - 1, center + 1, center + 2]:
        if df["high"].iloc[j] >= high_c:
            return False, None
    return True, high_c


class WilliamsFractalStrategy(BaseStrategy):
    name = "williams_fractal"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2  # 마지막 완성 캔들 인덱스
        last = df.iloc[idx]
        close = float(last["close"])
        ema50 = float(last["ema50"])
        rsi = float(last.get("rsi14", 50.0))

        # 최근 _FRACTAL_LOOKBACK 봉 내 fractal 탐색
        bullish_found = False
        bearish_found = False
        bull_level = None
        bear_level = None

        for i in range(idx, max(idx - _FRACTAL_LOOKBACK, 3), -1):
            if not bullish_found:
                found, level = _has_bullish_fractal(df, i)
                if found:
                    bullish_found = True
                    bull_level = level
            if not bearish_found:
                found, level = _has_bearish_fractal(df, i)
                if found:
                    bearish_found = True
                    bear_level = level
            if bullish_found and bearish_found:
                break

        bull_case = (
            f"Bullish fractal @ {bull_level:.4f}, close={close:.4f}, ema50={ema50:.4f}"
            if bullish_found and bull_level is not None
            else "No bullish fractal"
        )
        bear_case = (
            f"Bearish fractal @ {bear_level:.4f}, close={close:.4f}, ema50={ema50:.4f}"
            if bearish_found and bear_level is not None
            else "No bearish fractal"
        )

        # BUY: bullish fractal + close > ema50
        if bullish_found and close > ema50:
            conf = Confidence.HIGH if rsi < 50 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Bullish fractal 반등: close({close:.4f}) > ema50({ema50:.4f}), RSI={rsi:.1f}",
                invalidation=f"Close below fractal low {bull_level:.4f}",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: bearish fractal + close < ema50
        if bearish_found and close < ema50:
            conf = Confidence.HIGH if rsi > 50 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Bearish fractal 반락: close({close:.4f}) < ema50({ema50:.4f}), RSI={rsi:.1f}",
                invalidation=f"Close above fractal high {bear_level:.4f}",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning="Fractal 조건 미충족",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
