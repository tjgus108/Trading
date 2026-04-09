"""
Hurst Exponent 전략: RS Analysis로 추세 지속성/평균 회귀를 감지.

H > 0.55 → 추세 지속 → 추세 추종 진입
H < 0.45 → 평균 회귀 → 역추세 진입
0.45 <= H <= 0.55 → 랜덤워크 → HOLD
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 40
RS_WINDOW = 32


def _calc_hurst(close: pd.Series) -> Optional[float]:
    """RS Analysis로 Hurst Exponent 추정. numpy만 사용."""
    if len(close) < RS_WINDOW + 1:
        return None

    prices = close.iloc[-(RS_WINDOW + 1):].values
    log_returns = np.log(prices[1:] / prices[:-1])  # length = RS_WINDOW

    n = len(log_returns)
    if n < 4:
        return None

    mean_r = np.mean(log_returns)
    deviations = log_returns - mean_r
    cumdev = np.cumsum(deviations)

    r = cumdev.max() - cumdev.min()
    s = np.std(log_returns, ddof=1)

    if s < 1e-12:
        return None

    rs = r / s
    if rs <= 0:
        return None

    h = np.log(rs) / np.log(n)
    return float(h)


class HurstExponentStrategy(BaseStrategy):
    name = "hurst_strategy"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last = df.iloc[-1]
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last["close"]),
                reasoning=f"데이터 부족: 최소 {MIN_ROWS}행 필요 (현재 {len(df)}행)",
                invalidation="",
            )

        last = self._last(df)
        entry = float(last["close"])

        h = _calc_hurst(df["close"].iloc[:-1])  # 완성봉만 사용
        if h is None:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="Hurst Exponent 계산 실패 (변동성 없음)",
                invalidation="",
            )

        # EMA9, EMA21 계산
        ema9 = float(df["close"].iloc[:-1].ewm(span=9, adjust=False).mean().iloc[-1])
        ema21 = float(df["close"].iloc[:-1].ewm(span=21, adjust=False).mean().iloc[-1])
        sma20 = float(df["close"].iloc[-22:-2].mean())  # 완성봉 기준 20봉 평균

        # Confidence
        if h > 0.65 or h < 0.35:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM

        bull_case = (
            f"H={h:.4f}, EMA9={ema9:.4f}, EMA21={ema21:.4f}, "
            f"SMA20={sma20:.4f}, close={entry:.4f}"
        )
        bear_case = bull_case

        # 추세 지속 영역 (H > 0.55)
        if h > 0.55:
            if ema9 > ema21:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"추세 지속성 감지: H={h:.4f} > 0.55. "
                        f"상승 추세: EMA9({ema9:.4f}) > EMA21({ema21:.4f})"
                    ),
                    invalidation=f"EMA9 < EMA21 또는 H < 0.55",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            else:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"추세 지속성 감지: H={h:.4f} > 0.55. "
                        f"하락 추세: EMA9({ema9:.4f}) < EMA21({ema21:.4f})"
                    ),
                    invalidation=f"EMA9 > EMA21 또는 H < 0.55",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )

        # 평균 회귀 영역 (H < 0.45)
        if h < 0.45:
            if entry < sma20 * 0.97:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"평균 회귀 신호: H={h:.4f} < 0.45. "
                        f"과매도: close({entry:.4f}) < SMA20*0.97({sma20 * 0.97:.4f})"
                    ),
                    invalidation=f"close > SMA20({sma20:.4f}) 또는 H > 0.45",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            if entry > sma20 * 1.03:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"평균 회귀 신호: H={h:.4f} < 0.45. "
                        f"과매수: close({entry:.4f}) > SMA20*1.03({sma20 * 1.03:.4f})"
                    ),
                    invalidation=f"close < SMA20({sma20:.4f}) 또는 H > 0.45",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )

        # 랜덤워크 (0.45 <= H <= 0.55) 또는 회귀 조건 미충족
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"H={h:.4f}: "
                + ("랜덤워크 구간 (0.45~0.55)" if 0.45 <= h <= 0.55
                   else f"평균 회귀지만 진입 조건 미충족 (SMA20={sma20:.4f})")
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
