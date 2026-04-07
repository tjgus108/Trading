"""
MockExchangeConnector: API 키 없이 가짜 데이터로 전체 파이프라인을 실행한다.
--demo 모드에서 사용.
"""

import time
import random
import logging

logger = logging.getLogger(__name__)


class MockExchangeConnector:
    """ccxt ExchangeConnector와 동일한 인터페이스, 가짜 데이터 반환."""

    def __init__(self, symbol: str = "BTC/USDT", base_price: float = 65000.0):
        self.symbol = symbol
        self.base_price = base_price
        self._balance = {"total": {"USDT": 10000.0, "BTC": 0.0}}

    def connect(self) -> None:
        logger.info("MockConnector: connected (no real exchange)")

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> list:
        now = int(time.time() * 1000)
        interval_map = {
            "1m": 60_000, "5m": 300_000, "15m": 900_000,
            "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000,
        }
        interval = interval_map.get(timeframe, 3_600_000)

        price = self.base_price
        candles = []
        for i in range(limit):
            ts = now - (limit - i) * interval
            # 약한 상승 트렌드 + 랜덤 노이즈
            price = price * (1 + random.gauss(0.0002, 0.008))
            high = price * (1 + abs(random.gauss(0, 0.003)))
            low  = price * (1 - abs(random.gauss(0, 0.003)))
            vol  = random.uniform(5, 30)
            candles.append([ts, price, high, low, price, vol])

        logger.debug("MockConnector: generated %d candles for %s %s", limit, symbol, timeframe)
        return candles

    def fetch_balance(self) -> dict:
        return self._balance

    def fetch_ticker(self, symbol: str) -> dict:
        return {"last": self.base_price, "symbol": symbol}

    def create_order(self, symbol, side, amount, order_type="market", price=None) -> dict:
        fill_price = self.base_price * (1 + random.gauss(0, 0.0005))
        order_id = f"mock-{int(time.time()*1000)}"
        logger.info("MockConnector: %s %s %.6f @ %.2f (mock)", side, symbol, amount, fill_price)
        if side == "buy":
            cost = amount * fill_price
            self._balance["total"]["USDT"] = max(0, self._balance["total"]["USDT"] - cost)
            self._balance["total"]["BTC"] = self._balance["total"].get("BTC", 0) + amount
        else:
            revenue = amount * fill_price
            self._balance["total"]["USDT"] = self._balance["total"]["USDT"] + revenue
            self._balance["total"]["BTC"] = max(0, self._balance["total"].get("BTC", 0) - amount)
        return {
            "id": order_id, "status": "closed", "symbol": symbol,
            "side": side, "amount": amount, "filled": amount,
            "average": fill_price, "price": fill_price,
        }

    def fetch_order(self, order_id: str, symbol: str) -> dict:
        return {"id": order_id, "status": "closed", "filled": 0.001, "average": self.base_price}

    def cancel_order(self, order_id: str, symbol: str) -> dict:
        return {"id": order_id, "status": "canceled"}

    def wait_for_fill(self, order_id: str, symbol: str, timeout: int = 60) -> dict:
        return {"id": order_id, "status": "closed", "filled": 0.001, "average": self.base_price}

    def load_markets(self):
        pass
