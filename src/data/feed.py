"""
DataFeed: OHLCV 수집 + 기술 지표 계산.
data-agent가 이 모듈을 사용한다.
"""
from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

try:
    import ccxt
except ImportError:
    ccxt = None  # type: ignore[assignment]
import numpy as np
import pandas as pd
try:
    from scipy import stats as _scipy_stats
except ImportError:
    _scipy_stats = None  # type: ignore[assignment]

from src.exchange.connector import ExchangeConnector
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Circuit Breaker (cascading failure prevention)
# ─────────────────────────────────────────────────────────────────────────────

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Too many failures, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Simple circuit breaker to prevent cascading failures."""
    
    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 300,
                 success_threshold: int = 2):
        """
        Args:
            failure_threshold: Consecutive failures before OPEN state
            recovery_timeout: Seconds before attempting recovery (300s = 5min, API 재시도 폭주 방지)
            success_threshold: Consecutive successes to fully close
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._open_timestamp = None
    
    @property
    def state(self) -> CircuitState:
        """Current state with auto-recovery check."""
        if self._state == CircuitState.OPEN:
            if self._open_timestamp and \
               (time.time() - self._open_timestamp) >= self.recovery_timeout:
                logger.info("Circuit breaker: attempting recovery (OPEN -> HALF_OPEN)")
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
                self._failure_count = 0
        return self._state
    
    def record_success(self) -> None:
        """Record successful fetch."""
        self._failure_count = 0
        self._success_count += 1
        
        if self._state == CircuitState.HALF_OPEN and \
           self._success_count >= self.success_threshold:
            logger.info("Circuit breaker: fully recovered (HALF_OPEN -> CLOSED)")
            self._state = CircuitState.CLOSED
            self._success_count = 0
    
    def record_failure(self) -> None:
        """Record failed fetch."""
        self._success_count = 0
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._failure_count >= self.failure_threshold:
            if self._state != CircuitState.OPEN:
                logger.warning(
                    "Circuit breaker: too many failures (%d), opening circuit",
                    self._failure_count
                )
            self._state = CircuitState.OPEN
            self._open_timestamp = time.time()
    
    def can_attempt(self) -> bool:
        """Check if a fetch attempt should be allowed."""
        return self.state != CircuitState.OPEN



# Error classification
def _is_transient_error(error: Exception) -> bool:
    """네트워크/속도 제한 에러는 재시도 가능. SSL/cert 에러도 포함 (환경 인터셉션 대응)."""
    if ccxt is None:
        if isinstance(error, (TimeoutError, ConnectionError)):
            return True
        err_str = str(error).lower()
        return "ssl" in err_str or "certificate" in err_str

    transient_types = (
        ccxt.NetworkError,
        ccxt.RequestTimeout,
        ccxt.RateLimitExceeded,
        TimeoutError,
        ConnectionError,
    )
    if isinstance(error, transient_types):
        return True
    # SSL/certificate errors (e.g. ssl.SSLError) not wrapped by ccxt
    err_str = str(error).lower()
    return "ssl" in err_str or "certificate" in err_str


def _is_fatal_error(error: Exception) -> bool:
    """인증, 심볼, 권한 에러는 즉시 중단."""
    fatal_types = [ValueError, KeyError]
    
    if ccxt is not None:
        fatal_types.extend([
            ccxt.BadSymbol,
            ccxt.InvalidAddress,
            ccxt.AuthenticationError,
            ccxt.PermissionDenied,
        ])
    
    return isinstance(error, tuple(fatal_types))


def _is_rate_limit_error(error: Exception) -> bool:
    """Rate limit 에러 여부 감지."""
    if ccxt is None:
        return False
    return isinstance(error, ccxt.RateLimitExceeded)


def _backoff_with_rate_limit(error: Exception, attempt: int) -> None:
    """
    Rate limit 에러는 긴 backoff, 다른 transient 에러는 짧은 backoff.
    
    Args:
        error: 발생한 예외
        attempt: 시도 번호 (1부터)
    """
    if _is_rate_limit_error(error):
        # Rate limit: 2초 + attempt * 2초 (2s, 4s, 6s, ...)
        wait_time = 2 + attempt * 2
        logger.info(
            "RateLimitExceeded detected: backing off %d seconds (attempt %d)",
            wait_time, attempt
        )
    else:
        # 다른 transient 에러: 0.5초 * attempt (0.5s, 1s, 1.5s, ...)
        wait_time = 0.5 * attempt
    
    time.sleep(wait_time)



@dataclass
class DataSummary:
    symbol: str
    timeframe: str
    candles: int
    start: str
    end: str
    missing: int
    indicators: List[str]
    anomalies: List[str]
    df: pd.DataFrame = field(repr=False)


class DataFeed:
    # Regime-aware TTL multipliers: high volatility → shorter cache
    REGIME_TTL_MULTIPLIER = {
        "high_volatility": 0.33,   # 1/3 of base TTL
        "crisis": 0.2,             # 1/5 of base TTL
        "low_volatility": 1.5,     # 1.5x longer cache in calm markets
        "trending": 0.5,           # half TTL in trending regimes
    }

    # 공개 API fallback 거래소 목록 (인증 불필요, OHLCV 공개 지원)
    DEFAULT_FALLBACK_EXCHANGES: List[str] = ["binance", "okx", "bitget"]

    def __init__(
        self,
        connector: ExchangeConnector,
        cache_ttl: int = 60,
        max_retries: int = 3,
        max_cache_size: int = 128,
        fallback_exchange_ids: Optional[List[str]] = None,
        volume_unit: str = "base",  # "base" (BTC) or "quote" (USDT)
    ):
        self.connector = connector
        self._cache: dict = {}       # (symbol, timeframe, limit) → (DataSummary, timestamp)
        self._cache_ttl = cache_ttl  # 초 (base TTL)
        self._max_cache_size = max_cache_size  # 최대 캐시 엔트리 수
        self._max_retries = max_retries
        self._hit_count = 0          # 캐시 히트 수
        self._miss_count = 0         # 캐시 미스 수
        self._cache_hits: int = 0    # 캐시 히트 카운터 (get_cache_stats용, Cycle 239)
        self._cache_misses: int = 0  # 캐시 미스 카운터 (get_cache_stats용, Cycle 239)
        self._regime_cache: dict = {}  # symbol -> (regime_value, timestamp)
        self._circuit_breaker = CircuitBreaker()  # Cascading failure prevention
        # ─ Stale cache fallback (Cycle 176 개선)
        self._stale_cache: dict = {}  # (symbol, timeframe, limit) → (DataSummary, timestamp)
        self._fallback_count = 0       # 캐시 폴백 사용 횟수
        self._last_error_time: Optional[float] = None  # 마지막 에러 발생 시간
        # ─ 공개 API 거래소 fallback (Bybit SSL 차단 대응, 명시적 설정 필요)
        self._fallback_exchange_ids: List[str] = fallback_exchange_ids or []
        self._exchange_fallback_count = 0  # 공개 API fallback 사용 횟수

        # ─ 볼륨 단위 정규화
        self._volume_unit = volume_unit  # "base" (BTC) 또는 "quote" (USDT)
        
        # ─ Order book depth 캐시 (Cycle 229 개선)
        self._order_book_cache: dict = {}  # (symbol, levels) → (depth_dict, timestamp)

    def _effective_ttl(self, symbol: str) -> float:
        """레짐 기반 캐시 TTL 계산. 고변동성이면 짧게, 저변동성이면 길게."""
        regime = self.get_cached_regime(symbol)
        if regime is None:
            return self._cache_ttl
        multiplier = self.REGIME_TTL_MULTIPLIER.get(regime, 1.0)
        effective = self._cache_ttl * multiplier
        return effective

    def _get_stale_cache(self, key: tuple) -> Optional[tuple]:
        """만료된 캐시 데이터 반환 (폴백용). (DataSummary, age_seconds) 또는 None."""
        if key not in self._stale_cache:
            return None
        summary, ts = self._stale_cache[key]
        age = time.time() - ts
        return (summary, age)

    def _store_stale_cache(self, key: tuple, summary: DataSummary) -> None:
        """현재 캐시 데이터를 stale_cache에 저장 (폴백용)."""
        self._stale_cache[key] = (summary, time.time())

    def _use_cache_fallback(self, key: tuple) -> Optional[DataSummary]:
        """캐시 폴백 시도: 만료된 캐시 → 스테일 캐시 순서로 시도."""
        # 1. 만료된 hot cache 사용
        if key in self._cache:
            summary, ts = self._cache[key]
            age = time.time() - ts
            logger.info(
                "Cache fallback: using expired hot cache (age=%.1fs) for %s",
                age, key
            )
            return summary
        
        # 2. stale cache 사용
        stale_result = self._get_stale_cache(key)
        if stale_result:
            summary, age = stale_result
            logger.info(
                "Cache fallback: using stale cache (age=%.1fs) for %s",
                age, key
            )
            return summary
        
        return None

    def _detect_and_invalidate_stale_cache(self, max_age_seconds: int = 3600) -> int:
        """
        Detect stale cache entries (older than max_age_seconds) and remove them.
        
        Args:
            max_age_seconds: Maximum age (default 3600s = 1 hour) before cache is stale
        
        Returns:
            Number of invalidated cache entries
        
        Notes:
            - Stale cache older than 1 hour is typically expired and should not be served
            - Called periodically to prevent serving very old cached data
            - Keeps memory footprint under control by removing unused entries
        """
        now = time.time()
        invalidated = 0
        
        # Check stale cache for old entries
        keys_to_remove = []
        for key, (summary, ts) in list(self._stale_cache.items()):
            age = now - ts
            if age > max_age_seconds:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._stale_cache[key]
            invalidated += 1
        
        if invalidated > 0:
            logger.info(
                "Stale cache cleanup: removed %d entries older than %.0f seconds",
                invalidated, max_age_seconds
            )
        
        return invalidated
    
    def _is_cache_stale_for_regime(self, key: tuple, symbol: str) -> bool:
        """
        Check if a cached entry is considered stale for the current market regime.
        
        Args:
            key: Cache key (symbol, timeframe, limit)
            symbol: Trading symbol
        
        Returns:
            True if cache should be refreshed due to regime change
        
        Notes:
            - Crisis regime: stale if age > 0.2 * effective_ttl
            - High volatility: stale if age > 0.5 * effective_ttl
            - Normal regimes: stale if age > 0.9 * effective_ttl
            - Prevents serving outdated data during regime changes
        """
        if key not in self._cache:
            return False
        
        summary, ts = self._cache[key]
        age = time.time() - ts
        effective_ttl = self._effective_ttl(symbol)
        regime = self.get_cached_regime(symbol)
        
        # Crisis regime: stricter staleness check (20% of TTL)
        if regime == "crisis":
            is_stale = age > effective_ttl * 0.2
            if is_stale:
                logger.debug(
                    "Cache stale for crisis regime: %s (age=%.1fs, ttl=%.1fs)",
                    key, age, effective_ttl
                )
            return is_stale
        
        # High volatility: medium strictness (50% of TTL)
        if regime == "high_volatility":
            is_stale = age > effective_ttl * 0.5
            if is_stale:
                logger.debug(
                    "Cache stale for high_volatility regime: %s (age=%.1fs, ttl=%.1fs)",
                    key, age, effective_ttl
                )
            return is_stale
        
        # Normal: standard check (90% of TTL)
        is_stale = age > effective_ttl * 0.9
        if is_stale and regime:
            logger.debug(
                "Cache stale for %s regime: %s (age=%.1fs, ttl=%.1fs)",
                regime, key, age, effective_ttl
            )
        return is_stale


    def fetch(self, symbol: str, timeframe: str, limit: int = 500) -> DataSummary:
        # Circuit breaker check: reject if too many cascading failures
        if not self._circuit_breaker.can_attempt():
            raise RuntimeError(
                f"DataFeed circuit breaker OPEN: too many failures. "
                f"Will retry after {self._circuit_breaker.recovery_timeout}s"
            )

        # 캐시 키 정규화: 심볼을 대문자로 통일해 hit율 향상
        symbol_normalized = symbol.upper()
        key = (symbol_normalized, timeframe, limit)
        now = time.time()
        effective_ttl = self._effective_ttl(symbol)
        if key in self._cache:
            cached_summary, ts = self._cache[key]
            if now - ts < effective_ttl:
                self._hit_count += 1
                self._cache_hits += 1
                logger.debug(
                    "Cache HIT: %s %s (ttl=%.1fs, regime=%s)",
                    symbol, timeframe, effective_ttl,
                    self.get_cached_regime(symbol) or "default",
                )
                return cached_summary  # 캐시 히트
        # 캐시 미스: 실제 fetch (retry 포함)
        self._miss_count += 1
        self._cache_misses += 1
        logger.debug(
            "Cache MISS: %s %s (ttl=%.1fs, regime=%s)",
            symbol, timeframe, effective_ttl,
            self.get_cached_regime(symbol) or "default",
        )
        try:
            summary = self._fetch_with_retry(symbol, timeframe, limit)
            self._circuit_breaker.record_success()  # Success: reset failure count
            self._cache[key] = (summary, now)
            self._store_stale_cache(key, summary)  # 성공 데이터를 stale 캐시에 저장
            self._evict_if_needed()
            return summary
        except Exception as e:
            self._circuit_breaker.record_failure()  # Track failure
            self._last_error_time = time.time()

            # Stale cache 시도 조건:
            # - transient 에러: 네트워크 일시 장애 → stale 데이터로 대체
            # - exchange fallback 구성됨: primary + 모든 fallback 거래소 실패 → 오류 종류 무관하게 stale 시도
            should_try_cache = _is_transient_error(e) or bool(self._fallback_exchange_ids)
            if should_try_cache:
                logger.warning(
                    "Fetch failed (%s, error=%s): attempting cache fallback for %s %s",
                    "transient" if _is_transient_error(e) else "fallback-exhausted",
                    type(e).__name__, symbol, timeframe
                )
                fallback = self._use_cache_fallback(key)
                if fallback:
                    self._fallback_count += 1
                    # 재저장: 짧은 TTL(30s)로 캐시 갱신 → 반복 재시도 방지
                    # 거래소가 계속 다운돼도 30초마다 1회만 retry, 나머지는 캐시 히트
                    _STALE_REUSE_TTL = 30
                    self._cache[key] = (fallback, time.time() - self._cache_ttl + _STALE_REUSE_TTL)
                    return fallback

            raise

    def _fetch_with_retry(self, symbol: str, timeframe: str, limit: int) -> DataSummary:
        """Retry 로직과 함께 fetch. 에러 분류로 재시도 판단."""
        last_error = None
        for attempt in range(1, self._max_retries + 1):
            try:
                logger.debug(
                    "Fetching %s %s (limit=%d), attempt %d/%d",
                    symbol, timeframe, limit, attempt, self._max_retries
                )
                return self._fetch_fresh(symbol, timeframe, limit)
            except Exception as e:
                # Fatal 에러는 재시도하지 않음
                if _is_fatal_error(e):
                    error_type = type(e).__name__
                    logger.error(
                        "Fatal error (no retry): symbol=%s, timeframe=%s, "
                        "error_type=%s, message=%s",
                        symbol, timeframe, error_type, str(e)
                    )
                    raise
                
                # Transient 에러만 재시도
                last_error = e
                if attempt < self._max_retries:
                    logger.warning(
                        "Transient error: symbol=%s, timeframe=%s, "
                        "error=%s (attempt %d/%d, retrying...)",
                        symbol, timeframe, str(e), attempt, self._max_retries
                    )
                    _backoff_with_rate_limit(e, attempt)
                else:
                    # 마지막 재시도도 transient이면 로그
                    logger.warning(
                        "Final transient error: symbol=%s, timeframe=%s, "
                        "error=%s (attempt %d/%d)",
                        symbol, timeframe, str(e), attempt, self._max_retries
                    )
        
        # 모든 재시도 실패
        error_type = type(last_error).__name__
        logger.error(
            "Fetch exhausted: symbol=%s, timeframe=%s, limit=%d, "
            "max_retries=%d, error_type=%s, message=%s",
            symbol, timeframe, limit, self._max_retries, error_type, str(last_error)
        )
        raise last_error

    def fetch_multiple(
        self,
        symbols: List[str],
        timeframe: str,
        limit: int = 500,
        max_workers: int = None,
    ) -> Dict[str, DataSummary]:
        """
        여러 심볼을 병렬로 fetch.
        
        Args:
            symbols: 심볼 리스트 (예: ["BTC/USDT", "ETH/USDT"])
            timeframe: 타임프레임 (예: "1h")
            limit: 캔들 개수
            max_workers: 스레드 풀 크기 (기본: min(32, 심볼 수 + 4))
        
        Returns:
            {symbol: DataSummary} 딕셔너리
        
        Notes:
            - 기본 fetch()와 동일한 캐싱 로직 적용
            - 오류 발생 시 해당 심볼은 건너뛰고 나머지 진행
        """
        if max_workers is None:
            max_workers = min(len(symbols) + 4, 32)
        
        results = {}
        failed = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 작업 제출
            futures = {
                executor.submit(self.fetch, symbol, timeframe, limit): symbol
                for symbol in symbols
            }
            
            # 완료된 작업 수집
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    results[symbol] = future.result()
                except Exception as e:
                    failed[symbol] = str(e)
                    logger.warning("fetch_multiple: %s 실패 — %s", symbol, e)
        
        if failed:
            logger.info("fetch_multiple 완료: %d 성공, %d 실패", len(results), len(failed))
        
        return results

    def invalidate_cache(self, symbol=None, timeframe=None, regime_cache_too=True):
        """특정 심볼/타임프레임 또는 전체 캐시 무효화. regime_cache_too=True로 레짐 캐시도 함께 무효화."""
        if symbol is None and timeframe is None:
            self._cache.clear()
            if regime_cache_too:
                self._regime_cache.clear()
        else:
            # 심볼 정규화: 캐시 키와 일치시키기 위해 대문자로 변환
            symbol_normalized = symbol.upper() if symbol else None
            keys_to_del = [k for k in self._cache if (symbol_normalized and k[0] == symbol_normalized) or (timeframe and k[1] == timeframe)]
            for k in keys_to_del:
                del self._cache[k]
            if regime_cache_too and symbol:
                self._regime_cache.pop(symbol, None)

    def _evict_if_needed(self):
        """캐시가 max_cache_size를 초과하면 가장 오래된 엔트리 제거 (LRU)."""
        if len(self._cache) <= self._max_cache_size:
            return
        # 타임스탬프 기준 가장 오래된 엔트리 제거
        oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
        del self._cache[oldest_key]

    def cache_stats(self) -> dict:
        """
        캐시 히트율/미스율 통계 조회.
        
        Returns:
            {
                'hit_count': int,     # 캐시 히트 수
                'miss_count': int,    # 캐시 미스 수
                'total': int,         # 총 fetch 시도 수
                'hit_rate': float,    # 히트율 (0.0 ~ 1.0)
                'cached_keys': int,   # 현재 캐시된 키 개수
            }
        """
        total = self._hit_count + self._miss_count
        hit_rate = self._hit_count / total if total > 0 else 0.0
        return {
            'hit_count': self._hit_count,
            'miss_count': self._miss_count,
            'total': total,
            'hit_rate': hit_rate,
            'cached_keys': len(self._cache),
            'max_cache_size': self._max_cache_size,
            'regime_cache_size': len(self._regime_cache),
            'fallback_count': self._fallback_count,
            'stale_cache_size': len(self._stale_cache),
            'exchange_fallback_count': self._exchange_fallback_count,
            'volume_unit': self._volume_unit,
        }


    def get_cache_stats(self) -> dict:
        """
        캐시 hit/miss 통계 조회 (Cycle 239).

        Returns:
            {"hits": int, "misses": int, "hit_rate": float}
            hit_rate: 0.0 ~ 1.0 (총 요청이 0이면 0.0)
        """
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0.0
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": hit_rate,
        }

    def circuit_breaker_status(self) -> dict:
        """
        Get circuit breaker status (cascading failure detection).
        
        Returns:
            {
                'state': 'CLOSED' | 'OPEN' | 'HALF_OPEN',
                'failure_count': int,
                'recovery_timeout_remaining': float (seconds, 0 if not applicable),
            }
        """
        state_name = self._circuit_breaker.state.value
        remaining = 0.0
        if self._circuit_breaker._state == CircuitState.OPEN and \
           self._circuit_breaker._open_timestamp:
            remaining = max(
                0.0,
                self._circuit_breaker.recovery_timeout - 
                (time.time() - self._circuit_breaker._open_timestamp)
            )
        
        return {
            'state': state_name,
            'failure_count': self._circuit_breaker._failure_count,
            'recovery_timeout_remaining': remaining,
        }

    # 타임프레임 → 밀리초 매핑
    _TF_MS = {
        "1m": 60_000, "5m": 300_000, "15m": 900_000,
        "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000,
    }

    def fetch_paginated(self, symbol: str, timeframe: str, total_candles: int) -> DataSummary:
        """Paginated OHLCV fetch: 거래소 limit 제한을 우회하여 대량 데이터 수집."""
        tf_ms = self._TF_MS.get(timeframe)
        if tf_ms is None:
            raise ValueError(f"Unsupported timeframe for pagination: {timeframe}")

        batch_limit = self.connector.get_ohlcv_limit()
        now_ms = int(time.time() * 1000)
        since = now_ms - (total_candles * tf_ms)

        all_data: list = []
        seen_ts: set = set()
        stall_count = 0
        max_stalls = 5

        logger.info(
            "fetch_paginated: %s %s, target=%d candles, batch=%d, exchange=%s",
            symbol, timeframe, total_candles, batch_limit,
            self.connector.exchange_name,
        )

        while len(all_data) < total_candles and since < now_ms:
            try:
                batch = self.connector.fetch_ohlcv(
                    symbol, timeframe, limit=batch_limit, since=since,
                )
            except Exception as e:
                logger.warning("fetch_paginated batch error: %s", e)
                stall_count += 1
                if stall_count >= max_stalls:
                    logger.error("fetch_paginated: too many stalls, stopping")
                    break
                since += batch_limit * tf_ms
                time.sleep(1)
                continue

            if not batch:
                stall_count += 1
                if stall_count >= max_stalls:
                    break
                since += batch_limit * tf_ms
                time.sleep(0.5)
                continue

            stall_count = 0
            new_count = 0
            for row in batch:
                ts = row[0]
                if ts not in seen_ts:
                    seen_ts.add(ts)
                    all_data.append(row)
                    new_count += 1

            if new_count == 0:
                stall_count += 1
                if stall_count >= max_stalls:
                    break

            since = batch[-1][0] + tf_ms
            time.sleep(0.3)

        all_data.sort(key=lambda x: x[0])
        all_data = all_data[:total_candles]

        if not all_data:
            raise ValueError(
                f"fetch_paginated: no data collected for {symbol} {timeframe}"
            )

        used_exchange = getattr(self.connector, '_active_data_exchange', None) or self.connector.exchange_name
        logger.info(
            "fetch_paginated complete: %s %s, %d/%d candles via %s",
            symbol, timeframe, len(all_data), total_candles, used_exchange,
        )

        df = self._to_dataframe(all_data)
        if df.empty:
            raise ValueError(f"Empty DataFrame after pagination for {symbol} {timeframe}")

        missing = self._count_missing(df, timeframe)
        anomalies = self._detect_anomalies(df)
        df = self._normalize_volume(df)
        df = self._add_indicators(df)
        indicators = [c for c in df.columns if c not in {"open", "high", "low", "close", "volume"}]

        return DataSummary(
            symbol=symbol,
            timeframe=timeframe,
            candles=len(df),
            start=str(df.index[0]),
            end=str(df.index[-1]),
            missing=missing,
            indicators=indicators,
            anomalies=anomalies,
            df=df,
        )

    def _fetch_public_ohlcv(
        self, exchange_id: str, symbol: str, timeframe: str, limit: int
    ) -> list:
        """공개 API로 OHLCV 조회 (인증 불필요). SSL 오류 시 verify=False로 재시도."""
        if ccxt is None:
            raise RuntimeError("ccxt not available for public fallback")
        exchange_class = getattr(ccxt, exchange_id, None)
        if exchange_class is None:
            raise ValueError(f"Unknown exchange: {exchange_id}")
        ex = exchange_class({"enableRateLimit": True, "timeout": 15000})
        try:
            raw = ex.fetch_ohlcv(symbol, timeframe, limit=limit)
        except Exception as first_exc:
            # SSL 인터셉션 환경에서 인증서 검증 실패 시 verify=False로 재시도
            if isinstance(first_exc, (ccxt.NetworkError,)) or "ssl" in str(first_exc).lower() or "certificate" in str(first_exc).lower():
                logger.info(
                    "DataFeed: SSL error on %s fallback, retrying with verify=False",
                    exchange_id,
                )
                ex_no_ssl = exchange_class({"enableRateLimit": True, "timeout": 15000, "verify": False})
                raw = ex_no_ssl.fetch_ohlcv(symbol, timeframe, limit=limit)
            else:
                raise
        if not raw:
            raise ValueError(f"No OHLCV data from {exchange_id} for {symbol}")
        return raw

    def _fetch_fresh_with_exchange_fallback(
        self, symbol: str, timeframe: str, limit: int
    ) -> DataSummary:
        """primary connector 실패 시 공개 API fallback 거래소 순서대로 시도."""
        last_exc: Exception = RuntimeError("no fallback exchanges configured")
        for exchange_id in self._fallback_exchange_ids:
            try:
                logger.info(
                    "DataFeed: trying public fallback exchange=%s for %s %s",
                    exchange_id, symbol, timeframe,
                )
                raw = self._fetch_public_ohlcv(exchange_id, symbol, timeframe, limit)
                df = self._to_dataframe(raw)
                if df.empty:
                    raise ValueError(f"Empty OHLCV from {exchange_id}")
                missing = self._count_missing(df, timeframe)
                anomalies = self._detect_anomalies(df)
                df = self._normalize_volume(df)
                df = self._add_indicators(df)
                indicators = [c for c in df.columns if c not in {"open", "high", "low", "close", "volume"}]
                self._exchange_fallback_count += 1
                logger.info(
                    "DataFeed: public fallback SUCCESS via %s — %d candles for %s %s",
                    exchange_id, len(df), symbol, timeframe,
                )
                return DataSummary(
                    symbol=symbol,
                    timeframe=timeframe,
                    candles=len(df),
                    start=str(df.index[0]),
                    end=str(df.index[-1]),
                    missing=missing,
                    indicators=indicators,
                    anomalies=anomalies,
                    df=df,
                )
            except Exception as e:
                logger.warning(
                    "DataFeed: fallback exchange=%s failed for %s: %s",
                    exchange_id, symbol, e,
                )
                last_exc = e
        raise last_exc

    def _fetch_fresh(self, symbol: str, timeframe: str, limit: int) -> DataSummary:
        try:
            raw = self.connector.fetch_ohlcv(symbol, timeframe, limit=limit)
        except Exception as primary_exc:
            if _is_transient_error(primary_exc) and self._fallback_exchange_ids:
                logger.warning(
                    "DataFeed: primary connector failed (%s), trying exchange fallback",
                    type(primary_exc).__name__,
                )
                return self._fetch_fresh_with_exchange_fallback(symbol, timeframe, limit)
            raise
        df = self._to_dataframe(raw)
        
        # 경계: 빈 DataFrame 처리
        if df.empty:
            raise ValueError(f"Empty OHLCV data for {symbol} {timeframe}")
        
        missing = self._count_missing(df, timeframe)
        anomalies = self._detect_anomalies(df)
        df = self._normalize_volume(df)
        df = self._add_indicators(df)
        indicators = [c for c in df.columns if c not in {"open", "high", "low", "close", "volume"}]

        summary = DataSummary(
            symbol=symbol,
            timeframe=timeframe,
            candles=len(df),
            start=str(df.index[0]),
            end=str(df.index[-1]),
            missing=missing,
            indicators=indicators,
            anomalies=anomalies,
            df=df,
        )
        # ─ 데이터 품질 통계 계산 ─
        kurtosis_val = None
        skewness_val = None
        if len(df) > 2:
            try:
                log_returns = np.log(df["close"].pct_change() + 1).dropna()
                if len(log_returns) > 2:
                    if _scipy_stats is not None:
                        kurtosis_val = _scipy_stats.kurtosis(log_returns)
                        skewness_val = _scipy_stats.skew(log_returns)
                    else:
                        arr = log_returns.values
                        mu, std = arr.mean(), arr.std()
                        kurtosis_val = float(np.mean(((arr - mu) / std) ** 4) - 3) if std > 0 else 0.0
                        skewness_val = float(np.mean(((arr - mu) / std) ** 3)) if std > 0 else 0.0
            except:
                pass

        logger.info(
            "DataFeed: %s %s — %d candles, %d missing, %d anomalies, "
            "kurtosis=%.2f, skewness=%.2f",
        symbol,
        timeframe,
        len(df),
            missing,
            len(anomalies),
            kurtosis_val if kurtosis_val is not None else 0.0,
            skewness_val if skewness_val is not None else 0.0,
        )
        return summary

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _to_dataframe(self, raw: list) -> pd.DataFrame:
        """Convert raw OHLCV data to DataFrame with duplicate timestamp validation.
        
        Enhancements (Cycle 219):
        - Explicit duplicate timestamp detection and removal
        - Validation that final DataFrame has no duplicate indices
        - Logging of removed duplicates for debugging
        """
        df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        
        # Detect duplicates before indexing (for logging)
        dup_mask = df.duplicated(subset=["timestamp"], keep=False)
        if dup_mask.any():
            dup_count = dup_mask.sum()
            logger.warning(
                "_to_dataframe: %d duplicate timestamp entries detected, removing (keep last)",
                dup_count // 2  # each pair counted twice in keep=False mode
            )
        
        # Remove duplicates: keep last occurrence (most recent/complete data)
        df = df.drop_duplicates(subset=["timestamp"], keep="last")
        
        df.set_index("timestamp", inplace=True)
        df = df.astype(float)
        
        # Final validation: ensure no duplicate indices
        if df.index.duplicated().any():
            logger.error("_to_dataframe: CRITICAL — DataFrame still has duplicate timestamps after cleaning")
            raise ValueError("Duplicate timestamps remain after cleaning")
        
        return df


    def _normalize_volume(self, df: pd.DataFrame) -> pd.DataFrame:
        """볼륨 단위 정규화.
        
        ccxt는 거래소마다 base(BTC) 또는 quote(USDT) 단위로 volume을 반환.
        volume_unit="quote"이면 close로 나눠 base 단위로 변환.
        항상 volume_quote (USDT 단위) 컬럼도 추가.
        """
        if self._volume_unit == "quote":
            # quote volume → base volume 변환 (예: USDT → BTC)
            close_safe = df["close"].replace(0, np.nan)
            df["volume"] = df["volume"] / close_safe
            df["volume"] = df["volume"].fillna(0.0)
        # volume_quote: 항상 USDT 단위 (base volume * close)
        df["volume_quote"] = df["volume"] * df["close"]
        return df

    def _count_missing(self, df: pd.DataFrame, timeframe: str) -> int:
        freq_map = {"1m": "1min", "5m": "5min", "15m": "15min", "1h": "1h", "4h": "4h", "1d": "1D"}
        freq = freq_map.get(timeframe)
        if freq is None:
            return 0
        expected = pd.date_range(start=df.index[0], end=df.index[-1], freq=freq)
        return len(expected) - len(df)

    def _detect_anomalies(self, df: pd.DataFrame) -> List[str]:
        """
        Detect data anomalies including NaN/null, negative values, and OHLC inconsistencies.
        
        Checks:
        1. NaN/null values in OHLCV columns
        2. Negative prices (OHLC must be >= 0)
        3. Negative volume (impossible in real data)
        4. OHLC relationship validation
        5. Price gaps and spikes
        6. Zero volume candles (stale feed indicator)
        7. Duplicate close prices (feed frozen)
        8. Timestamp gaps (missing candles)
        
        Returns:
            List of anomaly strings (empty if no issues found)
        """
        anomalies = []
        ohlcv_cols = ["open", "high", "low", "close", "volume"]
        
        # 1. NaN/Null detection in OHLCV columns (data feed corruption)
        nan_mask = df[ohlcv_cols].isna()
        nan_count = nan_mask.sum()
        if nan_count.any():
            nan_cols = nan_count[nan_count > 0]
            for col in nan_cols.index:
                anomalies.append(
                    f"NaN values in {col}: {nan_count[col]} ({nan_count[col]/len(df)*100:.1f}%)"
                )
        
        # 2. Negative price values (OHLC must be non-negative)
        for col in ["open", "high", "low", "close"]:
            neg_count = (df[col] < 0).sum()
            if neg_count > 0:
                neg_idx = df[df[col] < 0].index[0]
                anomalies.append(f"negative {col}: {neg_count} candles, first at {neg_idx}")
        
        # 3. Negative volume (physically impossible)
        if (df["volume"] < 0).any():
            neg_vol_idx = df[df["volume"] < 0].index[0]
            anomalies.append(f"negative volume at {neg_vol_idx}")
        
        # 4. OHLC 관계 검증
        anomalies.extend(self._validate_ohlc_relationships(df))
        
        # 5. 종가 0 이하 (명시적 체크)
        if (df["close"] <= 0).any():
            anomalies.append("close <= 0 detected")
        
        # 6. 극단적 가격 점프 (단일 캔들 10% 이상)
        pct_change = df["close"].pct_change().abs()
        spikes = pct_change[pct_change > 0.10]
        if not spikes.empty:
            anomalies.append(f"price spike >10% at {spikes.index[0]}")
        
        # 7. 볼륨 0 캔들 (피드 동결/합성 데이터 의심)
        zero_vol = (df["volume"] == 0).sum()
        if zero_vol > 0:
            zero_vol_pct = zero_vol / len(df) * 100
            if zero_vol_pct > 1.0:  # 1% 초과 시만 기록
                anomalies.append(f"zero volume candles: {zero_vol} ({zero_vol_pct:.1f}%)")
            else:
                logger.debug("Minor zero-volume candles: %d (%.1f%%)", zero_vol, zero_vol_pct)
        
        # 8. 연속 중복 종가 감지 (스테일 피드 / 거래소 장애 의심)
        if len(df) >= 5:
            dup_mask = df["close"].diff().abs() < 1e-10
            consecutive_dups = 0
            max_consecutive = 0
            for v in dup_mask:
                consecutive_dups = consecutive_dups + 1 if v else 0
                max_consecutive = max(max_consecutive, consecutive_dups)
            if max_consecutive >= 5:
                anomalies.append(f"stale feed: {max_consecutive} consecutive identical closes")
        
        # 9. 타임스탬프 갭 감지 (연속된 캔들 사이 예상 간격의 3배 초과)
        if len(df) >= 2:
            time_diffs = df.index.to_series().diff().dropna()
            if not time_diffs.empty:
                median_diff = time_diffs.median()
                if median_diff.total_seconds() > 0:
                    large_gaps = time_diffs[time_diffs > median_diff * 3]
                    if not large_gaps.empty:
                        gap_count = len(large_gaps)
                        max_gap = large_gaps.max()
                        max_gap_at = large_gaps.idxmax()
                        anomalies.append(
                            f"timestamp gaps: {gap_count} gaps detected, "
                            f"largest={max_gap} at {max_gap_at}"
                        )
        
        return anomalies
    def _validate_ohlc_relationships(self, df: pd.DataFrame) -> List[str]:
        """
        OHLC 관계 검증: high >= max(open,close), low <= min(open,close)
        
        Returns:
            이상 감지 목록 (문제 없으면 빈 리스트)
        """
        issues = []
        
        # high >= max(open, close) 확인
        invalid_high = df[df["high"] < df[["open", "close"]].max(axis=1)]
        if not invalid_high.empty:
            issues.append(f"high < max(open,close) at {invalid_high.index[0]}")
        
        # low <= min(open, close) 확인
        invalid_low = df[df["low"] > df[["open", "close"]].min(axis=1)]
        if not invalid_low.empty:
            issues.append(f"low > min(open,close) at {invalid_low.index[0]}")
        
        # high >= low 확인 (기존 로직)
        inverted = df[df["high"] < df["low"]]
        if not inverted.empty:
            issues.append(f"high < low at {inverted.index[0]}")
        
        return issues

    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]
        high = df["high"]
        low = df["low"]

        # EMA
        df["ema20"] = close.ewm(span=20, adjust=False).mean()
        df["ema50"] = close.ewm(span=50, adjust=False).mean()
        df["ema200"] = close.ewm(span=200, adjust=False).mean()
        # EMA slope: 단위 시간당 상대 변화율 (NarrowRange ema_slope 필터용)
        df["ema20_slope"] = df["ema20"].diff() / df["ema20"]

        # ATR (Wilder)
        prev_close = close.shift(1)
        tr = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
        ).max(axis=1)
        df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["rsi14"] = 100 - (100 / (1 + rs))

        # Donchian Channel (20) — 이전 20봉 기준 (현재 봉 미포함)
        df["donchian_high"] = high.shift(1).rolling(20).max()
        df["donchian_low"] = low.shift(1).rolling(20).min()

        # SMA
        df["sma20"] = close.rolling(20, min_periods=1).mean()
        df["sma50"] = close.rolling(50, min_periods=1).mean()

        # Bollinger Bands
        df["bb_upper"] = df["sma20"] + 2 * close.rolling(20, min_periods=1).std()
        df["bb_lower"] = df["sma20"] - 2 * close.rolling(20, min_periods=1).std()

        # MACD
        df["macd"] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        # MACD Histogram: 모멘텀 강도 및 방향 확인 (dema_cross 신호 확인용)
        df["macd_hist"] = df["macd"] - df["macd_signal"]

        # BB Width: (bb_upper - bb_lower) / sma20 — 변동성 수축/확장 탐지 (BB squeeze)
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["sma20"].replace(0, np.nan)

        # VWAP (rolling session)
        typical = (high + low + close) / 3
        df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
        df["vwap20"] = (typical * df["volume"]).rolling(20, min_periods=1).sum() / df["volume"].rolling(20, min_periods=1).sum()

        # Volume SMA
        df["volume_sma20"] = df["volume"].rolling(20, min_periods=1).mean()
        # Volume Quote (USDT 단위, volume_quote가 없을 경우 대비)
        if "volume_quote" not in df.columns:
            df["volume_quote"] = df["volume"] * df["close"]
        df["volume_quote_sma20"] = df["volume_quote"].rolling(20, min_periods=1).mean()


        # Momentum
        df["return_5"] = close.pct_change(5)

        return df


    # ------------------------------------------------------------------
    # Funding Rate + Open Interest fetchers (for ML features)
    # ------------------------------------------------------------------

    def fetch_funding_rate(self, symbol: str) -> Optional[float]:
        """현재 funding rate 반환. 실패 시 None (파이프라인 블록 금지).

        Returns:
            funding rate as float (e.g., 0.0001 = 0.01%), or None on failure.
        """
        try:
            data = self.connector.fetch_funding_rate(symbol)
            rate = data.get("fundingRate")
            if rate is not None:
                return float(rate)
            return None
        except Exception as e:
            logger.warning("fetch_funding_rate failed for %s: %s", symbol, e)
            return None

    def fetch_funding_rate_history(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        """funding rate 이력을 DataFrame으로 반환.

        Returns:
            DataFrame with columns: ['funding_rate'], index=timestamp.
            실패 시 빈 DataFrame.
        """
        try:
            records = self.connector.fetch_funding_rate_history(symbol, limit=limit)
            if not records:
                return pd.DataFrame(columns=["funding_rate"])
            rows = []
            for r in records:
                ts = r.get("timestamp")
                fr = r.get("fundingRate")
                if ts is not None and fr is not None:
                    rows.append({"timestamp": ts, "funding_rate": float(fr)})
            if not rows:
                return pd.DataFrame(columns=["funding_rate"])
            df = pd.DataFrame(rows)
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
            df.set_index("timestamp", inplace=True)
            df.sort_index(inplace=True)
            return df
        except Exception as e:
            logger.warning("fetch_funding_rate_history failed for %s: %s", symbol, e)
            return pd.DataFrame(columns=["funding_rate"])

    def fetch_open_interest(self, symbol: str) -> Optional[float]:
        """현재 open interest 반환. 실패 시 None.

        Returns:
            open interest amount as float, or None on failure.
        """
        try:
            data = self.connector.fetch_open_interest(symbol)
            oi = data.get("openInterestAmount")
            if oi is not None:
                return float(oi)
            return None
        except Exception as e:
            logger.warning("fetch_open_interest failed for %s: %s", symbol, e)
            return None



    def get_order_book_depth(self, symbol: str, levels: int = 5, cache_ttl: int = 5) -> Optional[Dict]:
        """
        Order book depth 정보 조회 (호가창 깊이).
        
        TWAP 슬라이스 크기를 호가창 깊이에 동적 연동하기 위한 메서드.
        
        Args:
            symbol: 거래 심볼 (예: "BTC/USDT")
            levels: 호가 깊이 (기본 5 = 상위 5 호가, 최대 20)
            cache_ttl: 캐시 유지 시간 (초, 기본 5초 - 호가창은 실시간 변동이 많으므로 짧은 TTL)
        
        Returns:
            dict with structure:
            {
                'symbol': str,
                'bids': [(price, volume), ...],    # 매수 호가 (가격 내림차순)
                'asks': [(price, volume), ...],    # 매도 호가 (가격 오름차순)
                'bid_depth': float,                 # 최상위 호가 5개 누적 물량
                'ask_depth': float,                 # 최상위 호가 5개 누적 물량
                'spread': float,                    # 호가 스프레드 = (ask[0] - bid[0]) / mid_price
                'timestamp': float,                 # 조회 시간 (unix timestamp)
            }
            
            실패 시 None 반환 (파이프라인 블록 금지, 호가창 미사용 시 안전)
        
        Notes:
            - 캐시: (symbol, levels) 키로 관리하여 반복 조회 시 지연 방지
            - 호가창은 실시간 변동이 크므로 짧은 TTL 필요 (VWAP/TWAP 신뢰도 보장)
            - 레벨 개수 제한: 대부분 거래소는 20단계까지 지원
            - SSL 인터셉션 환경 대응: transient 에러 시 None 반환 (fallback 자동 트리거)
        """
        # 호가 깊이 제한 검증
        levels = min(max(levels, 1), 20)
        cache_key = (symbol.upper(), levels)
        now = time.time()
        
        # 호가창 캐시 확인 (짧은 TTL: 5초)
        if cache_key in self._order_book_cache:
            cached_data, ts = self._order_book_cache[cache_key]
            if now - ts < cache_ttl:
                logger.debug(
                    "Order book depth cache HIT: %s levels=%d (age=%.1fs)",
                    symbol, levels, now - ts
                )
                return cached_data
        
        # 캐시 미스: 거래소에서 호가 데이터 fetch
        try:
            logger.debug("Fetching order book depth: %s levels=%d", symbol, levels)
            order_book = self.connector.fetch_order_book(symbol, limit=levels)
            
            if not order_book or 'bids' not in order_book or 'asks' not in order_book:
                logger.warning("Invalid order book structure for %s", symbol)
                return None
            
            bids = order_book['bids'][:levels]
            asks = order_book['asks'][:levels]
            
            # 누적 물량 계산
            bid_depth = sum(vol for _, vol in bids)
            ask_depth = sum(vol for _, vol in asks)
            
            # 스프레드 계산 (mid_price 기반 퍼센티지)
            best_bid = bids[0][0] if bids else None
            best_ask = asks[0][0] if asks else None
            
            if best_bid and best_ask:
                mid_price = (best_bid + best_ask) / 2
                spread = (best_ask - best_bid) / mid_price if mid_price > 0 else 0
            else:
                spread = 0
            
            result = {
                'symbol': symbol.upper(),
                'bids': bids,
                'asks': asks,
                'bid_depth': bid_depth,
                'ask_depth': ask_depth,
                'spread': spread,
                'timestamp': now,
            }
            
            # 캐시 저장
            self._order_book_cache[cache_key] = (result, now)
            
            logger.debug(
                "Order book depth fetched: %s levels=%d, bid_depth=%.2f, ask_depth=%.2f, spread=%.4f%%",
                symbol, levels, bid_depth, ask_depth, spread * 100
            )
            return result
        
        except Exception as e:
            # Transient 에러는 로깅만 (파이프라인 블록 금지)
            if _is_transient_error(e):
                logger.warning(
                    "Order book fetch transient error (%s): %s — returning None",
                    type(e).__name__, symbol
                )
            else:
                logger.error(
                    "Order book fetch fatal error: %s — %s",
                    symbol, type(e).__name__
                )
            return None


    @staticmethod
    def compute_fr_oi_features(fr_series: pd.Series, oi_series: pd.Series) -> pd.DataFrame:
        """Funding rate + OI 파생 피처 계산.

        SSRN 연구 기반: delta_fr + fr*OI 곱이 단일 지표보다 정확도 향상.

        Args:
            fr_series: funding rate 시계열 (pd.Series, float)
            oi_series: open interest 시계열 (pd.Series, float, 같은 인덱스)

        Returns:
            DataFrame with columns:
              - funding_rate: 원본 FR
              - delta_fr: fr[t] - fr[t-1] (전기 대비 변화량)
              - fr_oi_interaction: fr * oi (곱 상호작용)
        """
        feat = pd.DataFrame(index=fr_series.index)
        feat["funding_rate"] = fr_series
        feat["delta_fr"] = fr_series.diff()
        # OI 정규화 후 곱 (스케일 차이 방지)
        oi_norm = oi_series / (oi_series.rolling(20, min_periods=1).mean() + 1e-9)
        feat["fr_oi_interaction"] = fr_series * oi_norm
        return feat

    # ------------------------------------------------------------------
    # Regime cache (lightweight regime tracking)
    # ------------------------------------------------------------------

    def cache_regime(self, symbol: str, regime_value: str, ttl: int = 300) -> None:
        """regime 감지 결과를 캐시에 저장 (TTL 기본 5분)."""
        self._regime_cache[symbol] = (regime_value, time.time() + ttl)

    def get_cached_regime(self, symbol: str) -> Optional[str]:
        """캐시된 regime 반환. 만료되었으면 None."""
        if symbol not in self._regime_cache:
            return None
        regime, expiry = self._regime_cache[symbol]
        if time.time() > expiry:
            del self._regime_cache[symbol]
            return None
        return regime

    def clear_regime_cache(self, symbol: Optional[str] = None) -> None:
        """regime 캐시 삭제."""
        if symbol:
            self._regime_cache.pop(symbol, None)
        else:
            self._regime_cache.clear()

    # ------------------------------------------------------------------
    # Auto-reconnection and enhanced validation
    # ------------------------------------------------------------------

    def ensure_connected(self, max_retries: int = 3) -> bool:
        """
        거래소 연결 상태 확인 및 재연결 시도.
        
        Args:
            max_retries: 재연결 최대 시도 횟수
        
        Returns:
            True if connected, False otherwise
        """
        try:
            # 헬스 체크로 연결 상태 확인
            health = self.connector.health_check()
            if health.get("connected"):
                return True
            
            # 연결 끊김 감지 → 재연결 시도
            logger.warning("DataFeed: connection lost, attempting reconnect...")
            if self.connector.reconnect(max_retries=max_retries):
                logger.info("DataFeed: reconnection successful")
                self.invalidate_cache()  # 캐시 무효화 (재연결 후)
                return True
            else:
                logger.error("DataFeed: reconnection failed after %d attempts", max_retries)
                return False
        except Exception as e:
            logger.error("DataFeed: ensure_connected failed: %s", e)
            return False

    def validate_fetch_result(self, summary: DataSummary) -> bool:
        """
        fetch 결과의 품질 검증. 임계값 이상의 이상이 있으면 False.
        
        Returns:
            True if data quality is acceptable
        """
        # 임계값: 누락 캔들이 전체의 5% 초과하면 경고
        missing_ratio = summary.missing / summary.candles if summary.candles > 0 else 0
        if missing_ratio > 0.05:
            logger.warning(
                "High missing ratio (%.1f%%): %s %s has %d missing candles",
                missing_ratio * 100, summary.symbol, summary.timeframe, summary.missing
            )
        
        # 이상 감지 시 경고
        if summary.anomalies:
            logger.warning(
                "Data anomalies detected: %s %s — %s",
                summary.symbol, summary.timeframe, "; ".join(summary.anomalies)
            )
        
        # 최소 캔들 수 확인 (최소 50개 필요)
        if summary.candles < 50:
            logger.error(
                "Insufficient data: %s %s only has %d candles (need >=50)",
                summary.symbol, summary.timeframe, summary.candles
            )
            return False
        
        return True

    # ------------------------------------------------------------------
    # Regime detection + caching pipeline (Cycle 174+)
    # ------------------------------------------------------------------

    def detect_and_cache_regime(
        self, symbol: str, df: pd.DataFrame, ttl: int = 300
    ) -> str:
        """
        DataFrame 기반 레짐 감지 및 캐싱 (DataFeed 내부 파이프라인).
        
        Args:
            symbol: 심볼
            df: OHLCV DataFrame (detect_regime 입력)
            ttl: 레짐 캐시 TTL (초, 기본 5분)
        
        Returns:
            감지된 레짐 문자열 ("bull" | "bear" | "ranging" | "crisis")
        
        Notes:
            - 이 메서드는 fetch 시 자동으로 호출됨
            - 결과는 regime_cache에 저장되어 RegimeAwareFeatureBuilder에서 활용 가능
        """
        # 지연 임포트: 순환 의존성 방지
        from src.ml.features import detect_regime
        
        try:
            regime = detect_regime(df, lookback=20)
            self.cache_regime(symbol, regime, ttl=ttl)
            logger.debug(
                "Regime detected and cached: %s → %s (ttl=%d)",
                symbol, regime, ttl
            )
            return regime
        except Exception as e:
            logger.warning(
                "Failed to detect regime for %s: %s (falling back to cached/default)",
                symbol, e
            )
            # 캐시된 레짐 반환 또는 None (fallback)
            return self.get_cached_regime(symbol) or "ranging"

    # Minimum bars needed for RegimeDetector (ADX14 + ATR20/MA20 warmup)
    REGIME_WARMUP_BARS = 40

    def fetch_with_regime(
        self, symbol: str, timeframe: str, limit: int = 500
    ) -> tuple:
        """
        OHLCV 데이터 fetch + 레짐 감지 (end-to-end 파이프라인).

        DataFeed → detect_regime() → RegimeAwareFeatureBuilder 연결점.

        Args:
            symbol: 거래 심볼
            timeframe: 타임프레임
            limit: 캔들 개수

        Returns:
            (DataSummary, regime_str): 데이터 + 감지된 레짐

        Example:
            >>> feed = DataFeed(connector)
            >>> summary, regime = feed.fetch_with_regime("BTC/USDT", "1h")
            >>> builder = RegimeAwareFeatureBuilder()
            >>> X, y, detected_regime = builder.build_with_regime(summary.df)
            >>> # detected_regime == regime (동일한 레짐 사용)
        """
        # 일반 fetch 수행
        summary = self.fetch(symbol, timeframe, limit)

        # 워밍업 검증: 캔들 수 부족하면 레짐 감지 스킵
        if summary.candles < self.REGIME_WARMUP_BARS:
            logger.warning(
                "DataFeed: %s %s — only %d candles (need >=%d for regime), skipping detection",
                symbol, timeframe, summary.candles, self.REGIME_WARMUP_BARS,
            )
            regime = self.get_cached_regime(symbol) or "ranging"
            return summary, regime

        # 데이터 갭 검증: 누락률이 높으면 레짐 감지 신뢰도 경고
        if summary.candles > 0 and summary.missing > 0:
            missing_ratio = summary.missing / summary.candles
            if missing_ratio > 0.1:
                logger.warning(
                    "DataFeed: %s %s — %.1f%% missing candles, regime detection may be unreliable",
                    symbol, timeframe, missing_ratio * 100,
                )

        # 레짐 감지 + 캐싱 (TTL은 effective_ttl 기반)
        effective_ttl = int(self._effective_ttl(symbol))
        regime = self.detect_and_cache_regime(symbol, summary.df, ttl=effective_ttl)

        logger.info(
            "DataFeed: %s %s — regime=%s, candles=%d",
            symbol, timeframe, regime, summary.candles
        )
        return summary, regime

    # ─────────────────────────────────────────────────────────────────
    # Cache TTL Documentation & Validation (Cycle 231)
    # ─────────────────────────────────────────────────────────────────
    
    def get_ttl_config(self) -> dict:
        """
        현재 DataFeed의 모든 캐시 TTL 설정을 조회.
        
        Returns:
            {
                'ohlcv_base_ttl': int,           # OHLCV 기본 TTL (초)
                'order_book_ttl': int,           # Order book 기본 TTL (초)
                'regime_cache_ttl': int,         # Regime 캐시 기본 TTL (초)
                'stale_reuse_ttl': int,          # Stale cache 재사용 TTL (초)
                'regime_ttl_multipliers': dict,  # 레짐별 TTL 배수
                'effective_ttl_formula': str,    # effective_ttl 계산식
                'order_book_cache_size': int,    # Order book 캐시 최대 항목 수
                'ohlcv_cache_size': int,         # OHLCV 캐시 최대 항목 수
            }
        
        Notes:
            - OHLCV cache: (symbol, timeframe, limit) 키로 관리
            - Order book cache: (symbol, levels) 키로 관리
            - Regime cache: symbol 키로 관리
            - Effective TTL = base_ttl * regime_multiplier
        """
        return {
            'ohlcv_base_ttl': self._cache_ttl,
            'order_book_ttl': 5,  # 호가창은 실시간이므로 짧은 TTL
            'regime_cache_ttl': 300,  # 기본값 5분
            'stale_reuse_ttl': 30,  # Stale cache 재사용 후 30초 내에 재시도
            'regime_ttl_multipliers': self.REGIME_TTL_MULTIPLIER.copy(),
            'effective_ttl_formula': 'effective_ttl = base_ttl * regime_multiplier',
            'order_book_cache_size': len(self._order_book_cache),
            'ohlcv_cache_size': len(self._cache),
        }
    
    def validate_ttl_consistency(self) -> dict:
        """
        캐시 TTL 설정의 일관성을 검증.
        
        Returns:
            {
                'is_consistent': bool,
                'issues': list[str],
                'warnings': list[str],
                'cache_sizes': {
                    'ohlcv': int,
                    'order_book': int,
                    'regime': int,
                },
                'ttl_ranges': {
                    'min_ttl': int,
                    'max_ttl': int,
                    'mean_ttl': float,
                }
            }
        
        Notes (Cycle 231):
            - OHLCV 기본 TTL (60초)은 모든 레짐에서 일관됨
            - Order book TTL (5초)는 호가창 실시간성 보장
            - Regime cache TTL (300초)는 OHLCV 캐시보다 길어야 함
            - effective_ttl은 regime 기반으로 동적 조정
        """
        issues = []
        warnings = []
        
        # 1. Base TTL 검증
        if self._cache_ttl < 30:
            warnings.append(f"OHLCV base_ttl={self._cache_ttl}s is very short (recommend >=30s)")
        if self._cache_ttl > 3600:
            warnings.append(f"OHLCV base_ttl={self._cache_ttl}s is very long (recommend <=3600s)")
        
        # 2. Regime TTL multiplier 검증
        multipliers = self.REGIME_TTL_MULTIPLIER
        for regime, mult in multipliers.items():
            if mult <= 0:
                issues.append(f"Invalid regime multiplier: {regime}={mult} (must be > 0)")
            if mult > 2.0:
                warnings.append(f"High regime multiplier: {regime}={mult} (data may become too stale)")
        
        # 3. Order book TTL vs OHLCV TTL
        order_book_ttl = 5
        if order_book_ttl > self._cache_ttl:
            issues.append(
                f"Order book TTL ({order_book_ttl}s) should be shorter than OHLCV base TTL ({self._cache_ttl}s)"
            )
        
        # 4. Stale cache TTL vs base TTL
        stale_reuse_ttl = 30
        if stale_reuse_ttl > self._cache_ttl:
            warnings.append(
                f"Stale reuse TTL ({stale_reuse_ttl}s) is approaching base TTL ({self._cache_ttl}s)"
            )
        
        # 5. Cache size 검증
        cache_sizes = {
            'ohlcv': len(self._cache),
            'order_book': len(self._order_book_cache),
            'regime': len(self._regime_cache),
        }
        if cache_sizes['ohlcv'] > self._max_cache_size:
            warnings.append(
                f"OHLCV cache size ({cache_sizes['ohlcv']}) exceeds max ({self._max_cache_size})"
            )
        
        # 6. TTL 범위 계산
        ttl_values = [self._cache_ttl]
        for mult in multipliers.values():
            ttl_values.append(int(self._cache_ttl * mult))
        ttl_values.append(300)  # regime cache
        
        ttl_ranges = {
            'min_ttl': min(ttl_values),
            'max_ttl': max(ttl_values),
            'mean_ttl': sum(ttl_values) / len(ttl_values) if ttl_values else 0,
        }
        
        is_consistent = len(issues) == 0
        
        return {
            'is_consistent': is_consistent,
            'issues': issues,
            'warnings': warnings,
            'cache_sizes': cache_sizes,
            'ttl_ranges': ttl_ranges,
        }

