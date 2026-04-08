"""
G2. CME Basis Spread Strategy.

basis_annual > 15%: 현물-선물 캐리 매력 높음 → BUY (현물 매수, 선물 숏 포지션 대비)
basis_annual < 3%: 디스카운트 → SELL (contango 붕괴 신호)
3% ~ 15%: HOLD

confidence:
  |basis_annual| > 20% → HIGH
  |basis_annual| > 10% → MEDIUM
  else → LOW
"""

import logging
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal
from src.data.options_feed import CMEBasisFeed

logger = logging.getLogger(__name__)


class CMEBasisStrategy(BaseStrategy):
    """CME Basis Spread 기반 캐리 전략."""

    name = "cme_basis"

    BUY_THRESHOLD = 15.0   # annual %
    SELL_THRESHOLD = 3.0   # annual %

    def __init__(
        self,
        feed: Optional[CMEBasisFeed] = None,
        symbol: str = "BTCUSDT",
    ):
        self._feed = feed or CMEBasisFeed()
        self._symbol = symbol

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = float(last["close"])

        basis = self._feed.get_basis(self._symbol)
        basis_annual = basis["basis_annual"]
        basis_pct = basis["basis_pct"]

        conf = self._confidence(basis_annual)
        reasoning_base = f"basis_annual={basis_annual:.1f}%, basis_pct={basis_pct:.2f}%"

        if basis_annual > self.BUY_THRESHOLD:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"캐리 매력 높음: {reasoning_base} > {self.BUY_THRESHOLD}%",
                invalidation=f"basis_annual < {self.SELL_THRESHOLD}% 붕괴",
                bull_case=f"연 {basis_annual:.1f}% 캐리 수익, 현물-선물 스프레드 수취",
                bear_case="basis 급락 시 포지션 청산 필요",
            )

        if basis_annual < self.SELL_THRESHOLD:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Contango 붕괴: {reasoning_base} < {self.SELL_THRESHOLD}%",
                invalidation=f"basis_annual > {self.BUY_THRESHOLD}% 회복",
                bull_case="",
                bear_case=f"캐리 수익 소멸, 디스카운트 진입",
            )

        return Signal(
            action=Action.HOLD,
            confidence=conf,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"중립 구간: {reasoning_base} ({self.SELL_THRESHOLD}%~{self.BUY_THRESHOLD}%)",
            invalidation="",
            bull_case=f"basis_annual > {self.BUY_THRESHOLD}% 달성 시 캐리 진입",
            bear_case=f"basis_annual < {self.SELL_THRESHOLD}% 하락 시 청산",
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _confidence(basis_annual: float) -> Confidence:
        abs_basis = abs(basis_annual)
        if abs_basis > 20.0:
            return Confidence.HIGH
        if abs_basis > 10.0:
            return Confidence.MEDIUM
        return Confidence.LOW
