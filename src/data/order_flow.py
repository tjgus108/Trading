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
        

    def validate_extreme_imbalance(self, df: pd.DataFrame, ofi_threshold: float = 0.9) -> dict:
        """
        Detect and validate extreme order flow imbalances (potential anomalies).
        
        Args:
            df: OHLCV DataFrame
            ofi_threshold: OFI threshold for extreme imbalance (default 0.9 = 90%)
        
        Returns:
            {
                'has_extreme': bool,
                'extreme_count': int,
                'max_imbalance': float,
                'issue': str or None
            }
        
        Notes (Cycle 219):
        - Extreme imbalances (OFI > 0.9 or < -0.9) may indicate:
          * Data feed anomalies or errors
          * One-sided orderbook capture (snapshot timing issue)
          * Highly illiquid pairs
        - Returns warning but does not reject data
        """
        if df.empty:
            return {'has_extreme': False, 'extreme_count': 0, 'max_imbalance': 0.0, 'issue': None}
        
        # Compute OFI for each candle
        volume = df["volume"].fillna(0.0).clip(lower=0.0)
        if volume.sum() == 0:
            return {'has_extreme': False, 'extreme_count': 0, 'max_imbalance': 0.0, 'issue': 'zero_total_vol'}
        
        # Buy vs Sell classification
        buy_frac = pd.Series(0.5, index=df.index, dtype=float)
        buy_frac[df["close"] > df["open"]] = 1.0
        buy_frac[df["close"] < df["open"]] = 0.0
        buy_frac[volume == 0] = 0.5
        
        bid_vol = volume * buy_frac
        ask_vol = volume * (1 - buy_frac)
        total = bid_vol + ask_vol
        
        # OFI with safety check for division
        ofi_series = (bid_vol - ask_vol) / total.replace(0, float('nan'))
        ofi_series = ofi_series.fillna(0.5)
        ofi_abs = ofi_series.abs()
        
        # Count extreme imbalances
        extreme_mask = ofi_abs > ofi_threshold
        extreme_count = extreme_mask.sum()
        
        # Issue categorization
        issue = None
        if extreme_count > 0:
            extreme_ratio = extreme_count / len(df)
            if extreme_ratio > 0.5:
                issue = f"excessive_extreme_imbalances ({extreme_ratio*100:.1f}% of candles)"
            else:
                issue = f"extreme_imbalances_detected ({extreme_count} candles)"
        
        return {
            'has_extreme': extreme_count > 0,
            'extreme_count': int(extreme_count),
            'max_imbalance': float(ofi_abs.max()),
            'issue': issue
        }



class OFICalculator:
    """
    OFI (Order Flow Imbalance) 계산기.
    
    데이터 스트림에서 호가창 기반 주문 흐름 불균형을 계산.
    - 입력: 시간별 bid/ask 물량 변화
    - 출력: [-1, +1] 범위의 OFI 지수
    
    사용 사례:
    - VPIN과 통합하여 매수/매도 압력 감지
    - 극단적 불균형(OFI < -0.9 또는 > +0.9) 감지 시 실행 지연
    """
    
    def __init__(self):
        pass
    
    def compute_from_orderbook(self, 
                              bid_depth: float, 
                              ask_depth: float) -> float:
        """
        호가창 물량으로부터 OFI 계산.
        
        Args:
            bid_depth: 누적 매수 호가 물량 (bid side)
            ask_depth: 누적 매도 호가 물량 (ask side)
        
        Returns:
            ofi: [-1, +1] OFI 값
            - ofi > +0.5: 강한 매수 압력
            - ofi < -0.5: 강한 매도 압력
            - ofi ≈ 0: 중립
            
        Notes:
            - bid_depth + ask_depth = 0 시 0.0 반환 (호가창 미수집)
        """
        total = bid_depth + ask_depth
        if total == 0:
            return 0.0
        
        ofi = (bid_depth - ask_depth) / total
        return max(-1.0, min(1.0, ofi))
    
    def compute_from_time_series(self, 
                                 bid_volumes: pd.Series, 
                                 ask_volumes: pd.Series) -> pd.Series:
        """
        시계열 호가 물량으로부터 OFI 시리즈 계산.
        
        Args:
            bid_volumes: 시간별 bid 물량 Series
            ask_volumes: 시간별 ask 물량 Series
        
        Returns:
            ofi_series: 시간별 OFI [-1, +1]
            
        Edge cases:
            - bid + ask = 0: OFI = 0.0 (호가창 데이터 부족)
            - 길이 불일치: min(len(bid), len(ask))로 정렬
        """
        if bid_volumes.empty or ask_volumes.empty:
            return pd.Series([], dtype=float)
        
        # 길이 맞추기
        min_len = min(len(bid_volumes), len(ask_volumes))
        bid = bid_volumes.iloc[:min_len].fillna(0.0)
        ask = ask_volumes.iloc[:min_len].fillna(0.0)
        
        total = bid + ask
        # 안전한 나눗셈: total == 0 → 0.0
        ofi = (bid - ask) / total.replace(0, float('nan'))
        ofi = ofi.fillna(0.0)
        
        # [-1, +1] 범위로 클리핑
        ofi = ofi.clip(-1.0, 1.0)
        
        return ofi
    
    def detect_extreme_ofi(self, 
                          ofi_series: pd.Series, 
                          threshold: float = 0.8) -> dict:
        """
        극단적 OFI 불균형 감지.
        
        Args:
            ofi_series: OFI 시리즈
            threshold: 극단 판정 임계값 (기본 0.8 = 80%)
        
        Returns:
            {
                'has_extreme': bool,
                'extreme_count': int,
                'extreme_indices': list,
                'max_ofi': float,
                'min_ofi': float,
            }
            
        Notes:
            - 매도 폭주 (OFI < -threshold): 실행 회피 또는 지연 신호
            - 매수 폭주 (OFI > +threshold): 슬리피지 주의
        """
        if ofi_series.empty:
            return {
                'has_extreme': False,
                'extreme_count': 0,
                'extreme_indices': [],
                'max_ofi': 0.0,
                'min_ofi': 0.0,
            }
        
        # 극단값 찾기
        ofi_abs = ofi_series.abs()
        extreme_mask = ofi_abs > threshold
        extreme_indices = ofi_series[extreme_mask].index.tolist()
        
        return {
            'has_extreme': extreme_mask.any(),
            'extreme_count': int(extreme_mask.sum()),
            'extreme_indices': extreme_indices,
            'max_ofi': float(ofi_series.max()),
            'min_ofi': float(ofi_series.min()),
        }


def compute_ofi_vpin_correlation(df: pd.DataFrame, vpin_window: int = 50) -> dict:
    """OFI, bid_ask_depth_imbalance, VPIN 3개 피처 상관성 분석.

    피처 중복 여부 판단 목적. 세 피처 모두 매수/매도 압력을 측정하지만
    계산 방식이 달라 상관성이 높으면 하나를 제거해 차원을 줄일 수 있다.

    Args:
        df: OHLCV DataFrame (open, high, low, close, volume 컬럼 필요)
        vpin_window: VPIN 롤링 윈도우 (기본 50봉)

    Returns:
        {
            'pearson': {'ofi_vpin': float, 'ofi_depth': float, 'vpin_depth': float},
            'spearman': {'ofi_vpin': float, 'ofi_depth': float, 'vpin_depth': float},
            'n_samples': int,
            'redundant': list[str],  # 상관계수 >= 0.85인 쌍 목록
        }
    """
    if df.empty or len(df) < max(vpin_window, 10):
        return {'pearson': {}, 'spearman': {}, 'n_samples': 0, 'redundant': []}

    volume = df["volume"].fillna(0.0).clip(lower=0.0)
    buy_frac = pd.Series(0.5, index=df.index, dtype=float)
    buy_frac[df["close"] > df["open"]] = 1.0
    buy_frac[df["close"] < df["open"]] = 0.0
    buy_frac[volume == 0] = 0.5

    buy_vol = volume * buy_frac
    sell_vol = volume * (1.0 - buy_frac)

    # OFI (캔들 단위, 가격 기반)
    total_vol = buy_vol + sell_vol
    ofi = (buy_vol - sell_vol) / total_vol.replace(0, float('nan'))
    ofi = ofi.fillna(0.0).clip(-1.0, 1.0)

    # bid_ask_depth_imbalance (OFI와 동일 공식, VPIN 버전)
    depth_imbalance = ofi.copy()

    # VPIN (롤링 window 기반)
    imbalance_abs = (buy_vol - sell_vol).abs()
    rolling_vol = volume.rolling(vpin_window).sum()
    rolling_imb = imbalance_abs.rolling(vpin_window).sum()
    vpin = (rolling_imb / rolling_vol.replace(0, float('nan'))).fillna(0.5).clip(0.0, 1.0)

    # 공통 유효 인덱스 (vpin_window 이후 + NaN 제거)
    combined = pd.DataFrame({'ofi': ofi, 'depth': depth_imbalance, 'vpin': vpin}).dropna()
    combined = combined.iloc[vpin_window:]
    n = len(combined)

    if n < 10:
        return {'pearson': {}, 'spearman': {}, 'n_samples': n, 'redundant': []}

    def _pearson(a: pd.Series, b: pd.Series) -> float:
        std_a, std_b = a.std(), b.std()
        if std_a < 1e-12 or std_b < 1e-12:
            return float('nan')
        return float(a.corr(b, method='pearson'))

    def _spearman(a: pd.Series, b: pd.Series) -> float:
        return float(a.corr(b, method='spearman'))

    pearson = {
        'ofi_vpin':  _pearson(combined['ofi'], combined['vpin']),
        'ofi_depth': _pearson(combined['ofi'], combined['depth']),
        'vpin_depth': _pearson(combined['vpin'], combined['depth']),
    }
    spearman = {
        'ofi_vpin':  _spearman(combined['ofi'], combined['vpin']),
        'ofi_depth': _spearman(combined['ofi'], combined['depth']),
        'vpin_depth': _spearman(combined['vpin'], combined['depth']),
    }

    # 중복 판정: |Pearson| >= 0.85
    redundant = [
        pair for pair, val in pearson.items()
        if val == val and abs(val) >= 0.85  # NaN 제외
    ]

    logger.info(
        "OFI/VPIN correlation (n=%d): ofi_vpin=%.3f ofi_depth=%.3f vpin_depth=%.3f | redundant=%s",
        n, pearson.get('ofi_vpin', float('nan')),
        pearson.get('ofi_depth', float('nan')),
        pearson.get('vpin_depth', float('nan')),
        redundant or "none",
    )
    return {'pearson': pearson, 'spearman': spearman, 'n_samples': n, 'redundant': redundant}

