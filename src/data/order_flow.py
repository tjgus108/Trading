"""
OrderFlowFetcher: Binance REST orderbook 기반 매수/매도 압력 계산.
인증 불필요, 공개 API 사용.

VPINCalculator: 벌크 분류 기반 VPIN 계산기.
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional

import urllib.request
import urllib.error
import json

import pandas as pd

logger = logging.getLogger(__name__)

BINANCE_DEPTH_URL = "https://api.binance.com/api/v3/depth"


@dataclass
class OrderFlowData:
    bid_vol: float
    ask_vol: float
    ofi: float          # [-1, +1]
    pressure: str       # "BUY_PRESSURE" | "SELL_PRESSURE" | "NEUTRAL"
    score: float        # [-3, +3]
    source: str         # "binance" | "mock" | "unavailable"


def _ofi_to_score(ofi: float) -> float:
    """OFI [-1,+1] → score [-3,+3] linear mapping. Clamp to bounds."""
    score = ofi * 3.0
    return max(-3.0, min(3.0, score))


def _pressure_from_ofi(ofi: float) -> str:
    if ofi > 0.3:
        return "BUY_PRESSURE"
    if ofi < -0.3:
        return "SELL_PRESSURE"
    return "NEUTRAL"


class OrderFlowFetcher:
    def __init__(self, symbol: str = "BTCUSDT", use_cache_seconds: int = 60):
        self.symbol = symbol
        self.use_cache_seconds = use_cache_seconds
        self._cache: Optional[OrderFlowData] = None
        self._cache_ts: float = 0.0

    def fetch(self) -> OrderFlowData:
        """Fetch orderbook from Binance REST. On any failure returns score=0, source='unavailable'."""
        now = time.monotonic()
        if self._cache is not None and (now - self._cache_ts) < self.use_cache_seconds:
            return self._cache

        try:
            url = f"{BINANCE_DEPTH_URL}?symbol={self.symbol}&limit=20"
            req = urllib.request.Request(url, headers={"User-Agent": "trading-bot/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())

            bid_vol = sum(float(qty) for _, qty in data["bids"])
            ask_vol = sum(float(qty) for _, qty in data["asks"])
            total = bid_vol + ask_vol

            if total == 0:
                raise ValueError("Zero total volume in orderbook")

            ofi = (bid_vol - ask_vol) / total
            pressure = _pressure_from_ofi(ofi)
            score = _ofi_to_score(ofi)

            result = OrderFlowData(
                bid_vol=bid_vol,
                ask_vol=ask_vol,
                ofi=round(ofi, 6),
                pressure=pressure,
                score=round(score, 4),
                source="binance",
            )
            self._cache = result
            self._cache_ts = now
            logger.info("OrderFlow: ofi=%.4f pressure=%s score=%.2f", ofi, pressure, score)
            return result

        except Exception as exc:
            logger.warning("OrderFlow fetch failed: %s — returning score=0", exc)
            return OrderFlowData(
                bid_vol=0.0,
                ask_vol=0.0,
                ofi=0.0,
                pressure="NEUTRAL",
                score=0.0,
                source="unavailable",
            )

    def mock(self, ofi: float = 0.0) -> OrderFlowData:
        """Return synthetic OrderFlowData for testing."""
        ofi = max(-1.0, min(1.0, ofi))
        bid_vol = (1 + ofi) * 100.0
        ask_vol = (1 - ofi) * 100.0
        pressure = _pressure_from_ofi(ofi)
        score = _ofi_to_score(ofi)
        return OrderFlowData(
            bid_vol=bid_vol,
            ask_vol=ask_vol,
            ofi=round(ofi, 6),
            pressure=pressure,
            score=round(score, 4),
            source="mock",
        )


class VPINCalculator:
    """
    VPIN (Volume-Synchronized Probability of Informed Trading) 계산기.

    방법: 벌크 분류 (bulk classification)
    - 각 캔들을 buy_vol / sell_vol로 분류 (close > open → buy, else → sell)
    - VPIN = sum|buy_vol - sell_vol| / total_vol (n_buckets 이동평균)

    해석: VPIN > 0.5 → 고독성 (informed trader 활동), 방향성 강함
    """

    def __init__(self, n_buckets: int = 50):
        self.n_buckets = n_buckets

    def compute(self, df: pd.DataFrame) -> pd.Series:
        """
        df: OHLCV DataFrame (close, open, volume 컬럼 필요)
        returns: VPIN 시리즈 (0~1), 길이 = len(df)
        """
        # close > open: BUY (1.0), close == open: NEUTRAL (0.5), close < open: SELL (0.0)
        buy_frac = pd.Series(0.0, index=df.index)
        buy_frac[df["close"] > df["open"]] = 1.0
        buy_frac[df["close"] == df["open"]] = 0.5
        
        buy_vol = df["volume"] * buy_frac
        sell_vol = df["volume"] * (1 - buy_frac)
        imbalance = (buy_vol - sell_vol).abs()
        total_vol = df["volume"]
        vpin = (imbalance.rolling(self.n_buckets).sum() /
                total_vol.rolling(self.n_buckets).sum().replace(0, 1))
        return vpin.clip(0, 1)


    def get_latest(self, df: pd.DataFrame) -> float:
        """마지막 VPIN 값 반환. 데이터 부족 시 0.5"""
        result = self.compute(df)
        if result.empty or result.iloc[-1] != result.iloc[-1]:  # NaN check
            return 0.5
        return float(result.iloc[-1])
