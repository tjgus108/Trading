"""
F3. DEX 가격 피드.

실제 연동:
  - Uniswap V3: https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3
    → GraphQL 쿼리로 BTC/USDC 또는 WETH/USDC 최근 swap 가격 조회
  - 실패 시: CoinGecko 무료 API (https://api.coingecko.com/api/v3/simple/price)

캐시: 60초

인터페이스:
  DEXPriceFeed:
    get_price(symbol: str = "BTC") -> float  # USD 기준
    get_spread(cex_price: float, symbol: str = "BTC") -> dict
      → {"dex_price": float, "cex_price": float, "spread_pct": float, "arb_direction": "BUY_DEX"/"SELL_DEX"/"NONE"}
    mock(symbol, price) -> DEXPriceFeed  # 테스트용 classmethod
"""

import logging
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
CACHE_TTL = 60

SYMBOL_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BTC/USDT": "bitcoin",
    "ETH/USDT": "ethereum",
}

ARB_THRESHOLD_PCT = 0.3


class DEXPriceFeed:
    def __init__(self):
        self._cache: dict[str, tuple[float, float]] = {}  # symbol → (price, timestamp)

    def get_price(self, symbol: str = "BTC") -> float:
        """DEX/CoinGecko 가격. 실패 시 0.0"""
        now = time.time()
        if symbol in self._cache:
            price, ts = self._cache[symbol]
            if now - ts < CACHE_TTL:
                return price

        price = self._fetch_coingecko(symbol)
        if price > 0.0:
            self._cache[symbol] = (price, now)
        return price

    def get_spread(self, cex_price: float, symbol: str = "BTC") -> dict:
        """
        스프레드 계산.
        spread_pct = (dex_price - cex_price) / cex_price * 100
        arb_direction:
          spread_pct > 0.3% → SELL_DEX (CEX에서 사서 DEX에 팔기)
          spread_pct < -0.3% → BUY_DEX (DEX에서 사서 CEX에 팔기)
          기타 → NONE
        """
        dex_price = self.get_price(symbol)

        if dex_price == 0.0 or cex_price == 0.0:
            return {
                "dex_price": dex_price,
                "cex_price": cex_price,
                "spread_pct": 0.0,
                "arb_direction": "NONE",
            }

        spread_pct = (dex_price - cex_price) / cex_price * 100

        if spread_pct > ARB_THRESHOLD_PCT:
            direction = "SELL_DEX"
        elif spread_pct < -ARB_THRESHOLD_PCT:
            direction = "BUY_DEX"
        else:
            direction = "NONE"

        return {
            "dex_price": dex_price,
            "cex_price": cex_price,
            "spread_pct": spread_pct,
            "arb_direction": direction,
        }

    @classmethod
    def mock(cls, symbol: str = "BTC", price: float = 50000.0) -> "DEXPriceFeed":
        """테스트/데모용 mock"""
        feed = cls()
        feed._cache[symbol] = (price, time.time())
        return feed

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _fetch_coingecko(self, symbol: str) -> float:
        """CoinGecko API로 가격 조회. 실패 시 0.0"""
        coin_id = SYMBOL_MAP.get(symbol)
        if coin_id is None:
            logger.warning("DEXPriceFeed: unknown symbol '%s'", symbol)
            return 0.0

        try:
            resp = requests.get(
                COINGECKO_URL,
                params={"ids": coin_id, "vs_currencies": "usd"},
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            price = float(data[coin_id]["usd"])
            logger.debug("DEXPriceFeed: %s=%s (CoinGecko)", symbol, price)
            return price
        except Exception as e:
            logger.warning("DEXPriceFeed: CoinGecko fetch failed for '%s': %s", symbol, e)
            return 0.0
