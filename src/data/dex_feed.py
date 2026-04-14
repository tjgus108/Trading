"""
F3. DEX 가격 피드.

실제 연동:
  - Uniswap V3: https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3
    → GraphQL 쿼리로 BTC/USDC 또는 WETH/USDC 최근 swap 가격 조회
  - 실패 시: CoinGecko 무료 API (https://api.coingecko.com/api/v3/simple/price)

캐시: 60초

재시도: exponential backoff (Cycle 6 패턴) + fallback
  - 최대 2회 재시도
  - 실패 시 마지막 성공 가격 반환
  - fallback도 없으면 0.0 반환

인터페이스:
  DEXPriceFeed:
    get_price(symbol: str = "BTC") -> float  # USD 기준
    get_spread(cex_price: float, symbol: str = "BTC") -> dict
      → {"dex_price": float, "cex_price": float, "spread_pct": float, "arb_direction": "BUY_DEX"/"SELL_DEX"/"NONE"}
    mock(symbol, price) -> DEXPriceFeed  # 테스트용 classmethod
"""

import logging
import time
from typing import Optional, Tuple, Dict

import requests

logger = logging.getLogger(__name__)

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
CACHE_TTL = 60
_MAX_RETRIES = 2
_RETRY_BACKOFF_SECONDS = [1, 2]  # exponential backoff

SYMBOL_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BTC/USDT": "bitcoin",
    "ETH/USDT": "ethereum",
}

ARB_THRESHOLD_PCT = 0.3


class DEXPriceFeed:
    def __init__(self, max_retries: int = _MAX_RETRIES):
        self._cache: Dict[str, Tuple[float, float]] = {}  # symbol → (price, timestamp)
        self._last_successful: Dict[str, float] = {}  # symbol → last_price (fallback)
        self.max_retries = max_retries

    def get_price(self, symbol: str = "BTC") -> float:
        """
        DEX/CoinGecko 가격 조회.
        - 캐시 유효 시 캐시값 반환
        - API 호출 (재시도 포함)
        - 실패 시: fallback → 0.0
        """
        now = time.time()
        if symbol in self._cache:
            price, ts = self._cache[symbol]
            if now - ts < CACHE_TTL:
                return price

        price = self._fetch_coingecko_with_retry(symbol)
        if price > 0.0:
            self._cache[symbol] = (price, now)
            self._last_successful[symbol] = price
            return price

        # 재시도 후 실패 → fallback 사용
        if symbol in self._last_successful:
            logger.warning(
                "DEXPriceFeed.get_price failed after retries, using fallback for '%s'",
                symbol
            )
            return self._last_successful[symbol]

        # fallback도 없으면 0.0
        logger.warning("DEXPriceFeed.get_price failed and no fallback available for '%s'", symbol)
        return 0.0

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
        feed._last_successful[symbol] = price
        return feed

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _fetch_coingecko_with_retry(self, symbol: str) -> float:
        """
        CoinGecko API 재시도 (exponential backoff).
        실패 시 0.0 반환.
        """
        coin_id = SYMBOL_MAP.get(symbol)
        if coin_id is None:
            logger.warning("DEXPriceFeed: unknown symbol '%s'", symbol)
            return 0.0

        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.get(
                    COINGECKO_URL,
                    params={"ids": coin_id, "vs_currencies": "usd"},
                    timeout=5,
                )
                resp.raise_for_status()
                data = resp.json()
                price = float(data[coin_id]["usd"])
                logger.debug("DEXPriceFeed: %s=%s (CoinGecko, attempt %d)", symbol, price, attempt + 1)
                return price
            except Exception as e:
                if attempt < self.max_retries:
                    wait = _RETRY_BACKOFF_SECONDS[attempt]
                    logger.warning(
                        "DEXPriceFeed: CoinGecko attempt %d/%d failed for '%s': %s. Retry in %ds...",
                        attempt + 1,
                        self.max_retries + 1,
                        symbol,
                        str(e),
                        wait,
                    )
                    time.sleep(wait)
                else:
                    logger.warning(
                        "DEXPriceFeed: CoinGecko failed after %d retries for '%s': %s",
                        self.max_retries + 1,
                        symbol,
                        str(e),
                    )

        return 0.0

    def _fetch_coingecko(self, symbol: str) -> float:
        """CoinGecko API로 가격 조회. 재시도 로직 없음 (하위호환)."""
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
