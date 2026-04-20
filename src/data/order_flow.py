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
import numpy as np

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
    
    Edge case 처리:
    - 거래량 0인 캔들: 무시 (중립으로 처리)
    - 윈도우 내 전체 거래량 0: NaN → 0.5로 보정
    - 극단적 스프레드 (high == low): 무시
    """

    def __init__(self, n_buckets: int = 50, min_bucket_vol: float = 0.0):
        if n_buckets <= 0:
            raise ValueError(f"n_buckets must be > 0, got {n_buckets}")
        self.n_buckets = n_buckets
        self.min_bucket_vol = min_bucket_vol  # 최소 거래량 필터 (기본 비활성)

    def compute(self, df: pd.DataFrame) -> pd.Series:
        """
        df: OHLCV DataFrame (close, open, volume 컬럼 필요)
        returns: VPIN 시리즈 (0~1), 길이 = len(df)
        
        Edge cases:
        - 0 거래량 봉: buy_frac=0.5 (중립)
        - High==Low (극단 스프레드): close와 open 비교로 방향 결정
        - 윈도우 거래량 0: NaN → 0.5로 보정
        """
        if df.empty:
            return pd.Series([], dtype=float)
        
        # 거래량 검증: 음수 or NaN 제거
        volume = df["volume"].fillna(0.0).clip(lower=0.0)
        
        # close > open: BUY (1.0), close == open: NEUTRAL (0.5), close < open: SELL (0.0)
        buy_frac = pd.Series(0.5, index=df.index, dtype=float)
        buy_frac[df["close"] > df["open"]] = 1.0
        buy_frac[df["close"] < df["open"]] = 0.0
        
        # 0 거래량 봉은 명시적으로 0.5 (중립)
        buy_frac[volume == 0] = 0.5
        
        buy_vol = volume * buy_frac
        sell_vol = volume * (1 - buy_frac)
        imbalance = (buy_vol - sell_vol).abs()
        
        rolling_vol = volume.rolling(self.n_buckets).sum()
        rolling_imbalance = imbalance.rolling(self.n_buckets).sum()
        
        # 윈도우 거래량 > 0 인 경우만 계산, 아니면 NaN
        vpin = rolling_imbalance / rolling_vol.replace(0, float('nan'))
        
        # NaN → 0.5로 보정 (데이터 부족 상태)
        vpin = vpin.fillna(0.5)
        
        # 0~1 범위로 클리핑
        vpin = vpin.clip(0, 1)
        
        return vpin

    def get_latest(self, df: pd.DataFrame) -> float:
        """
        마지막 VPIN 값 반환. 데이터 부족 시 0.5
        
        안전 처리:
        - 빈 DataFrame: 0.5
        - NaN 마지막 값: 0.5
        """
        if df.empty:
            return 0.5
        
        result = self.compute(df)
        if result.empty:
            return 0.5
        
        latest = result.iloc[-1]
        # NaN 체크 (latest != latest는 NaN 검증)
        if latest != latest or np.isnan(latest):
            return 0.5
        
        return float(latest)

    def validate_inputs(self, df: pd.DataFrame) -> tuple:
        """
        데이터 검증 및 통계 반환.
        
        Returns:
            (is_valid, stats_dict)
            - is_valid: 계산 가능 여부
            - stats_dict: {"zero_vol_count", "nan_count", "total_vol", "min_vol", "max_vol"}
        """
        if df.empty:
            return False, {"error": "empty_dataframe"}
        
        if "volume" not in df.columns or "close" not in df.columns or "open" not in df.columns:
            return False, {"error": "missing_columns"}
        
        volume = df["volume"].fillna(0.0)
        zero_vol_count = (volume == 0).sum()
        nan_count = df["volume"].isna().sum()
        total_vol = volume.sum()
        
        stats = {
            "zero_vol_count": int(zero_vol_count),
            "nan_count": int(nan_count),
            "total_vol": float(total_vol),
            "min_vol": float(volume.min()),
            "max_vol": float(volume.max()),
            "rows": len(df),
        }
        
        # 유효: 최소 n_buckets개 행 + 0이 아닌 거래량 존재
        is_valid = len(df) >= self.n_buckets and total_vol > 0
        
        return is_valid, stats
