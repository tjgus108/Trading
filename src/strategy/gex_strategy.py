"""
G2. GEX Signal Strategy.

Positive GEX (딜러 헤지) → 변동성 억제 → mean-revert 전략:
  RSI > 65 → SELL (과매수 후 반전)
  RSI < 35 → BUY (과매도 후 반전)

Negative GEX (추세 가속) → 추세 추종:
  close > EMA20 → BUY
  close < EMA20 → SELL

GEX 데이터 없으면 HOLD.
"""

import logging
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal
from src.data.options_feed import GEXFeed

logger = logging.getLogger(__name__)


class GEXStrategy(BaseStrategy):
    """GEX 기반 복합 전략 (mean-revert / 추세추종 전환)."""

    name = "gex_signal"

    def __init__(
        self,
        feed: Optional[GEXFeed] = None,
        symbol: str = "BTC",
        rsi_overbought: float = 65.0,
        rsi_oversold: float = 35.0,
    ):
        self._feed = feed or GEXFeed()
        self._symbol = symbol
        self._rsi_overbought = rsi_overbought
        self._rsi_oversold = rsi_oversold

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = float(last["close"])

        gex_data = self._feed.get_gex(self._symbol)

        # GEX score=0 이면 데이터 없음 처리 (mock 기본값과 구분하기 위해
        # net_gex=0 일 때도 score=0 → HOLD)
        if gex_data["net_gex"] == 0.0 and gex_data["score"] == 0.0:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="GEX 데이터 없음 — 대기",
                invalidation="GEX 데이터 수신 시 재평가",
            )

        positive_gex: bool = gex_data["positive"]
        score = gex_data["score"]
        conf = Confidence.HIGH if abs(score) >= 2 else Confidence.MEDIUM

        if positive_gex:
            # Mean-revert 구간
            rsi = float(last.get("rsi14", 50.0))
            if rsi > self._rsi_overbought:
                return Signal(
                    action=Action.SELL,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=f"Positive GEX({score:.2f}) + RSI과매수({rsi:.1f}>{self._rsi_overbought}) → mean-revert SELL",
                    invalidation="RSI 중립 복귀 또는 GEX 음전환",
                    bull_case="",
                    bear_case="딜러 헤지로 변동성 억제, 과매수 반전 예상",
                )
            if rsi < self._rsi_oversold:
                return Signal(
                    action=Action.BUY,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=f"Positive GEX({score:.2f}) + RSI과매도({rsi:.1f}<{self._rsi_oversold}) → mean-revert BUY",
                    invalidation="RSI 중립 복귀 또는 GEX 음전환",
                    bull_case="딜러 헤지로 변동성 억제, 과매도 반전 예상",
                    bear_case="",
                )
        else:
            # 추세 추종 구간
            close = float(last["close"])
            ema20 = float(last.get("ema20", close))
            if close > ema20:
                return Signal(
                    action=Action.BUY,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=f"Negative GEX({score:.2f}) + close({close:.2f})>EMA20({ema20:.2f}) → 추세추종 BUY",
                    invalidation="close < EMA20 이탈",
                    bull_case="GEX 음전환 추세 가속 구간",
                    bear_case="",
                )
            if close < ema20:
                return Signal(
                    action=Action.SELL,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=f"Negative GEX({score:.2f}) + close({close:.2f})<EMA20({ema20:.2f}) → 추세추종 SELL",
                    invalidation="close > EMA20 돌파",
                    bull_case="",
                    bear_case="GEX 음전환 하방 추세 가속",
                )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"GEX({score:.2f}) 신호 없음 — 대기",
            invalidation="RSI 또는 EMA20 조건 충족 시 재평가",
        )
