"""
청산 데이터 피드.

Binance 청산 주문 REST API:
  GET https://fapi.binance.com/fapi/v1/forceOrders?symbol=BTCUSDT&limit=100

응답: [{symbol, side, type, price, origQty, executedQty, time}, ...]
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

try:
    import requests as _requests
except ImportError:
    _requests = None  # type: ignore


@dataclass
class LiquidationPressure:
    long_liq_usd: float
    short_liq_usd: float
    liq_ratio: float      # 0~1
    total_liq_usd: float
    cascade_risk: bool
    score: float          # -3~+3 (short liq 우세 → +3 BUY, long liq 우세 → -3 SELL)


class LiquidationFetcher:
    _BASE_URL = "https://fapi.binance.com/fapi/v1/forceOrders"

    def __init__(self, symbol: str = "BTC/USDT"):
        self.symbol = symbol
        self._ccxt_symbol = symbol.replace("/", "")  # BTC/USDT → BTCUSDT
        self._mock_data: Optional[list[dict]] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_recent(self, limit: int = 100) -> list[dict]:
        """Binance fapi /forceOrders 엔드포인트 호출. 실패 시 [] 반환."""
        if self._mock_data is not None:
            return self._mock_data

        if _requests is None:
            return []

        try:
            resp = _requests.get(
                self._BASE_URL,
                params={"symbol": self._ccxt_symbol, "limit": limit},
                timeout=5,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return []

    def compute_pressure(self, limit: int = 100) -> LiquidationPressure:
        """최근 청산 데이터로 매수/매도 압력 계산."""
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

                # side == "BUY" means the liquidation order was a forced buy
                # → the trader was SHORT and got liquidated (short liquidation)
                # side == "SELL" → trader was LONG → long liquidation
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

        # cascade_risk: 최근 10분 청산 평균이 이전 평균의 3배 이상
        cascade_risk = False
        if recent_usd_values and older_usd_values:
            recent_avg = sum(recent_usd_values) / len(recent_usd_values)
            older_avg = sum(older_usd_values) / len(older_usd_values)
            if older_avg > 0 and recent_avg >= 3 * older_avg:
                cascade_risk = True
        elif recent_usd_values and not older_usd_values:
            # 모든 데이터가 최근 10분: 데이터 부족으로 판단 불가 → False
            cascade_risk = False

        # score: liq_ratio 0→+3, 1→-3 선형 변환
        # short liq 우세(ratio≈0) → +3 BUY, long liq 우세(ratio≈1) → -3 SELL
        score = round((0.5 - liq_ratio) * 6.0, 4)  # [-3, +3]
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

        # long liquidation: side=SELL (forced sell of long position)
        if long_liq > 0:
            orders.append({
                "symbol": "BTCUSDT",
                "side": "SELL",
                "type": "LIQUIDATION",
                "price": "50000",
                "origQty": str(long_liq / 50000),
                "executedQty": str(long_liq / 50000),
                "time": now_ms - 60_000,  # 1분 전 (10분 이내)
            })

        # short liquidation: side=BUY
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
