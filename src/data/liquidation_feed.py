"""
청산 데이터 피드.

Bybit 최근 거래 REST API (public, 인증 불필요):
  GET https://api.bybit.com/v5/market/recent-trade?category=linear&symbol=BTCUSDT&limit=50

응답: {result: {list: [{symbol, side, price, size, time}, ...]}}

재시도: exponential backoff (Cycle 6 패턴) + fallback
  - 최대 2회 재시도
  - 실패 시 마지막 성공 데이터 반환
  - fallback도 없으면 빈 리스트 반환
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Optional

try:
    import requests as _requests
except ImportError:
    _requests = None  # type: ignore

logger = logging.getLogger(__name__)

_MAX_RETRIES = 2
_RETRY_BACKOFF_SECONDS = [1, 2]  # exponential backoff


@dataclass
class LiquidationPressure:
    long_liq_usd: float
    short_liq_usd: float
    liq_ratio: float      # 0~1
    total_liq_usd: float
    cascade_risk: bool
    score: float          # -3~+3 (short liq 우세 → +3 BUY, long liq 우세 → -3 SELL)


class LiquidationFetcher:
    _BASE_URL = "https://api.bybit.com/v5/market/recent-trade"

    def __init__(self, symbol: str = "BTC/USDT", max_retries: int = _MAX_RETRIES):
        self.symbol = symbol
        self._ccxt_symbol = symbol.replace("/", "")  # BTC/USDT → BTCUSDT
        self._mock_data: Optional[list[dict]] = None
        self.max_retries = max_retries
        self._last_successful: Optional[list[dict]] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_recent(self, limit: int = 50) -> list[dict]:
        """Bybit v5 recent-trade 엔드포인트 호출. 재시도 + fallback 포함."""
        if self._mock_data is not None:
            return self._mock_data

        if _requests is None:
            return []

        for attempt in range(self.max_retries + 1):
            try:
                resp = _requests.get(
                    self._BASE_URL,
                    params={
                        "category": "linear",
                        "symbol": self._ccxt_symbol,
                        "limit": min(limit, 1000),
                    },
                    timeout=5,
                )
                resp.raise_for_status()
                data = resp.json()

                # Bybit v5 응답: {retCode: 0, result: {list: [...]}}
                if data.get("retCode") != 0:
                    raise ValueError(f"Bybit API error: {data.get('retMsg', 'unknown')}")

                trades = data.get("result", {}).get("list", [])
                # Bybit 필드 → 표준화 (Binance 호환)
                result = []
                for t in trades:
                    result.append({
                        "symbol": t.get("symbol", self._ccxt_symbol),
                        "side": t.get("side", "").upper(),
                        "price": t.get("price", "0"),
                        "executedQty": t.get("size", "0"),
                        "origQty": t.get("size", "0"),
                        "time": int(t.get("time", 0)),
                    })

                self._last_successful = result
                logger.debug("LiquidationFetcher: Bybit API success (attempt %d/%d)",
                             attempt + 1, self.max_retries + 1)
                return result
            except Exception as e:
                if attempt < self.max_retries:
                    wait = _RETRY_BACKOFF_SECONDS[attempt]
                    logger.warning(
                        "LiquidationFetcher: attempt %d/%d failed for '%s': %s. Retry in %ds...",
                        attempt + 1, self.max_retries + 1,
                        self._ccxt_symbol, str(e), wait,
                    )
                    time.sleep(wait)
                else:
                    logger.warning(
                        "LiquidationFetcher: failed after %d retries for '%s': %s",
                        self.max_retries + 1, self._ccxt_symbol, str(e),
                    )

        # fallback
        if self._last_successful is not None:
            logger.warning("LiquidationFetcher: using fallback for '%s'", self._ccxt_symbol)
            return self._last_successful

        return []

    def compute_pressure(self, limit: int = 50) -> LiquidationPressure:
        """최근 거래 데이터로 매수/매도 압력 계산."""
        orders = self.get_recent(limit=limit)

        now_ms = int(time.time() * 1000)
        ten_min_ms = 10 * 60 * 1000

        long_liq_usd = 0.0
        short_liq_usd = 0.0
        recent_usd_values: list[float] = []
        older_usd_values: list[float] = []

        for o in orders:
            try:
                price = float(o.get("price", 0) or 0)
                qty = float(o.get("executedQty", 0) or o.get("origQty", 0) or 0)
                usd_val = price * qty
                side = str(o.get("side", "")).upper()
                ts = int(o.get("time", 0) or 0)

                if side == "SELL":
                    long_liq_usd += usd_val
                elif side == "BUY":
                    short_liq_usd += usd_val

                if now_ms - ts <= ten_min_ms:
                    recent_usd_values.append(usd_val)
                else:
                    older_usd_values.append(usd_val)
            except (TypeError, ValueError):
                continue

        total_liq_usd = long_liq_usd + short_liq_usd
        liq_ratio = long_liq_usd / (total_liq_usd + 1e-9)

        cascade_risk = False
        if recent_usd_values and older_usd_values:
            recent_avg = sum(recent_usd_values) / len(recent_usd_values)
            older_avg = sum(older_usd_values) / len(older_usd_values)
            if older_avg > 0 and recent_avg >= 3 * older_avg:
                cascade_risk = True

        score = round((0.5 - liq_ratio) * 6.0, 4)
        score = max(-3.0, min(3.0, score))

        return LiquidationPressure(
            long_liq_usd=long_liq_usd,
            short_liq_usd=short_liq_usd,
            liq_ratio=liq_ratio,
            total_liq_usd=total_liq_usd,
            cascade_risk=cascade_risk,
            score=score,
        )

    # ------------------------------------------------------------------
    # Mock factory
    # ------------------------------------------------------------------

    @classmethod
    def mock(cls, long_liq: float = 1_000_000, short_liq: float = 200_000) -> "LiquidationFetcher":
        """테스트/데모용: 고정값 반환."""
        fetcher = cls()
        now_ms = int(time.time() * 1000)
        orders: list[dict] = []

        if long_liq > 0:
            orders.append({
                "symbol": "BTCUSDT",
                "side": "SELL",
                "type": "LIQUIDATION",
                "price": "50000",
                "origQty": str(long_liq / 50000),
                "executedQty": str(long_liq / 50000),
                "time": now_ms - 60_000,
            })

        if short_liq > 0:
            orders.append({
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "LIQUIDATION",
                "price": "50000",
                "origQty": str(short_liq / 50000),
                "executedQty": str(short_liq / 50000),
                "time": now_ms - 60_000,
            })

        fetcher._mock_data = orders
        return fetcher
