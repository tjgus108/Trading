"""
F3. CrossExchangeArbStrategy: CEX vs DEX 가격 차익.

로직:
  1. CEX 가격 = df["close"].iloc[-1]
  2. DEX 가격 = DEXPriceFeed.get_price(symbol)
  3. 스프레드 계산
  4. |spread| > min_spread_pct (기본 0.3%) → 방향에 따라 BUY/SELL
  5. DEX 가격 조회 실패 → HOLD

파라미터:
  min_spread_pct: float = 0.3   # 최소 차익 임계값 (%)
  symbol: str = "BTC"

신호 reasoning에: "CEX={:.2f} DEX={:.2f} spread={:.3f}%" 포함
"""

import logging

import pandas as pd

from src.data.dex_feed import DEXPriceFeed
from .base import Action, BaseStrategy, Confidence, Signal

logger = logging.getLogger(__name__)


class CrossExchangeArbStrategy(BaseStrategy):
    """CEX vs DEX 스프레드 기반 차익 전략."""

    name = "cross_exchange_arb"

    def __init__(self, min_spread_pct: float = 0.3, symbol: str = "BTC"):
        self._feed = DEXPriceFeed()
        self.min_spread_pct = min_spread_pct
        self.symbol = symbol

    def generate(self, df: pd.DataFrame) -> Signal:
        cex_price = float(df["close"].iloc[-1])
        idx = len(df) - 1

        # 변동성 레짐 필터
        vol = df["close"].pct_change().rolling(20, min_periods=1).std().iloc[idx]
        if vol > 0.03:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=cex_price,
                reasoning=f"고변동성 레짐 HOLD: realized_vol={vol:.4f} > 0.03 (스프레드 신뢰 불가)",
                invalidation="vol < 0.03 시 재검토",
            )

        # ATR 정규화 필터
        high = df["high"] if "high" in df.columns else df["close"]
        low = df["low"] if "low" in df.columns else df["close"]
        tr = (high - low).abs()
        atr14 = tr.rolling(14, min_periods=1).mean().iloc[idx]
        if cex_price > 0 and atr14 / cex_price > 0.02:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=cex_price,
                reasoning=f"ATR 과대 HOLD: atr14/close={atr14/cex_price:.4f} > 0.02",
                invalidation="atr14/close < 0.02 시 재검토",
            )

        spread_info = self._feed.get_spread(cex_price, self.symbol)

        dex_price = spread_info["dex_price"]
        spread_pct = spread_info["spread_pct"]
        direction = spread_info["arb_direction"]

        reasoning = (
            f"CEX={cex_price:.2f} DEX={dex_price:.2f} spread={spread_pct:.3f}%"
        )

        # DEX 가격 조회 실패
        if dex_price == 0.0:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=cex_price,
                reasoning=f"DEX 가격 조회 실패 — HOLD. {reasoning}",
                invalidation="DEX 가격 복구 시 재평가",
            )

        # 스프레드 임계값 미달
        if direction == "NONE" or abs(spread_pct) < self.min_spread_pct:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=cex_price,
                reasoning=f"차익 없음 — HOLD. {reasoning}",
                invalidation=f"|spread| > {self.min_spread_pct:.1f}% 시 진입",
            )

        # BUY_DEX: DEX 싸다 → DEX에서 사서 CEX에 팔기 → BUY 신호
        if direction == "BUY_DEX":
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=cex_price,
                reasoning=f"BUY_DEX 차익 진입. {reasoning}",
                invalidation=f"|spread| < {self.min_spread_pct:.1f}% 시 청산",
                bull_case=f"DEX 저렴, spread={spread_pct:.3f}% 차익 기회",
                bear_case="슬리피지/수수료로 차익 잠식 위험",
            )

        # SELL_DEX: DEX 비싸다 → CEX에서 사서 DEX에 팔기 → SELL 신호
        return Signal(
            action=Action.SELL,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=cex_price,
            reasoning=f"SELL_DEX 차익 진입. {reasoning}",
            invalidation=f"|spread| < {self.min_spread_pct:.1f}% 시 청산",
            bull_case="",
            bear_case=f"DEX 고가, spread={spread_pct:.3f}% 역방향 차익",
        )
