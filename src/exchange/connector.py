"""
Exchange connector: ccxt 기반 거래소 연결 및 주문 실행 레이어.
모든 거래소 접근은 이 모듈을 통한다.
"""

import os
import time
import logging
from typing import Optional

import ccxt

logger = logging.getLogger(__name__)


class ExchangeConnector:
    def __init__(self, exchange_name: str, sandbox: bool = True):
        self.exchange_name = exchange_name
        self.sandbox = sandbox
        self._exchange: Optional[ccxt.Exchange] = None

    def connect(self) -> None:
        exchange_class = getattr(ccxt, self.exchange_name)
        self._exchange = exchange_class(
            {
                "apiKey": os.environ["EXCHANGE_API_KEY"],
                "secret": os.environ["EXCHANGE_API_SECRET"],
                "enableRateLimit": True,
            }
        )
        if self.sandbox:
            self._exchange.set_sandbox_mode(True)
        self._exchange.load_markets()
        logger.info("Connected to %s (sandbox=%s)", self.exchange_name, self.sandbox)

    @property
    def exchange(self) -> ccxt.Exchange:
        if self._exchange is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._exchange

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> list:
        data = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        if not data:
            raise ValueError(f"No OHLCV data returned for {symbol} {timeframe}")
        logger.debug("Fetched %d candles for %s %s", len(data), symbol, timeframe)
        return data

    def fetch_balance(self) -> dict:
        return self.exchange.fetch_balance()

    def fetch_ticker(self, symbol: str) -> dict:
        return self.exchange.fetch_ticker(symbol)

    def create_order(
        self,
        symbol: str,
        side: str,  # "buy" or "sell"
        amount: float,
        order_type: str = "market",
        price: Optional[float] = None,
    ) -> dict:
        logger.info(
            "Submitting %s %s order: %s %.6f @ %s",
            order_type,
            side,
            symbol,
            amount,
            price or "market",
        )
        if order_type == "market":
            order = self.exchange.create_market_order(symbol, side, amount)
        elif order_type == "limit":
            if price is None:
                raise ValueError("price required for limit order")
            order = self.exchange.create_limit_order(symbol, side, amount, price)
        else:
            raise ValueError(f"Unsupported order_type: {order_type}")
        logger.info("Order submitted: %s", order.get("id"))
        return order

    def fetch_order(self, order_id: str, symbol: str) -> dict:
        return self.exchange.fetch_order(order_id, symbol)

    def cancel_order(self, order_id: str, symbol: str) -> dict:
        logger.warning("Cancelling order %s", order_id)
        return self.exchange.cancel_order(order_id, symbol)

    def wait_for_fill(self, order_id: str, symbol: str, timeout: int = 60) -> dict:
        """주문 체결 대기. timeout(초) 초과 시 취소 후 TIMEOUT 반환."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            order = self.fetch_order(order_id, symbol)
            status = order.get("status")
            if status == "closed":
                return order
            if status == "canceled":
                return order
            time.sleep(2)
        self.cancel_order(order_id, symbol)
        return {"status": "timeout", "id": order_id, "symbol": symbol}
