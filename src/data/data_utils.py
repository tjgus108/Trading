"""
Historical data download & validation utilities.
다양한 타임프레임과 기간을 지원하는 실제 거래소 데이터 다운로드 및 검증.

역할:
1. 실제 거래소(Bybit 등)에서 OHLCV 데이터 페이지네이션으로 다운로드
2. 데이터 무결성 검증: 갭, 누락 캔들, 비정상 OHLC 관계
3. 기술 지표 계산 (feed.py와 동일)
4. 캐시 활용으로 중복 다운로드 방지
5. 다중 타임프레임 지원

사용 예시:
    downloader = HistoricalDataDownloader(exchange="bybit", cache_dir="./data_cache")
    df = downloader.download("BTC/USDT", "1h", days=180, validate=True)
    stats = downloader.validate_data(df, timeframe="1h")
    print(stats)  # DataValidationReport
"""

from __future__ import annotations
import logging
import time
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
from scipy import stats
import pandas as pd

logger = logging.getLogger(__name__)

# Timeframe to milliseconds mapping
TIMEFRAME_MS = {
    "1m": 60_000,
    "5m": 300_000,
    "15m": 900_000,
    "1h": 3_600_000,
    "4h": 14_400_000,
    "1d": 86_400_000,
}


@dataclass
class DataValidationReport:
    """데이터 검증 결과 리포트."""
    symbol: str
    timeframe: str
    total_candles: int
    start_time: str
    end_time: str
    missing_candles: int
    gap_count: int
    gaps: List[Tuple[str, str]]  # [(start, end), ...]
    anomalies: List[str]
    data_quality_pct: float  # 0-100, 100 = 완벽
    is_valid: bool

    def __str__(self) -> str:
        return (
            f"DataValidation: {self.symbol} {self.timeframe}\n"
            f"  Candles: {self.total_candles}\n"
            f"  Range: {self.start_time} ~ {self.end_time}\n"
            f"  Missing: {self.missing_candles}, Gaps: {self.gap_count}\n"
            f"  Anomalies: {len(self.anomalies)}\n"
            f"  Quality: {self.data_quality_pct:.1f}%\n"
            f"  Valid: {self.is_valid}"
        )


class HistoricalDataDownloader:
    """실제 거래소에서 OHLCV 데이터를 다운로드하고 검증하는 클래스."""

    def __init__(
        self,
        exchange: str = "bybit",
        cache_dir: Optional[str] = None,
        timeout_ms: int = 20000,
        max_retries: int = 3,
    ):
        """
        Args:
            exchange: 거래소 이름 (ccxt에서 지원하는 이름, 예: "bybit", "binance")
            cache_dir: 다운로드된 데이터 캐시 디렉토리 (None이면 캐시 미사용)
            timeout_ms: API 호출 타임아웃 (밀리초)
            max_retries: 실패 시 최대 재시도 횟수
        """
        self.exchange_name = exchange
        self.timeout_ms = timeout_ms
        self.max_retries = max_retries
        self._exchange = None
        
        # Lazy initialization — ccxt를 여기서 import하지 않고 필요할 때만
        # ValueError (잘못된 거래소 이름)는 즉시 전파, 그 외 연결 에러는 defer
        try:
            self._init_exchange()
        except ValueError:
            raise
        except Exception as e:
            logger.warning("Exchange initialization deferred: %s", e)
            # 테스트 환경에서는 실제 exchange 필요 없음

        # 캐시 설정
        self.cache_dir = None
        if cache_dir:
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Cache enabled: %s", self.cache_dir)

    def _init_exchange(self):
        """거래소 인스턴스 초기화."""
        # 알려진 거래소 목록으로 이름을 먼저 검증 (ccxt import 전)
        _KNOWN_EXCHANGES = {
            "bybit", "binance", "okx", "kraken", "coinbase", "huobi",
            "kucoin", "gate", "bitfinex", "bitmex", "deribit", "ftx",
            "bitget", "mexc", "phemex", "bitmart", "gemini", "poloniex",
        }
        if self.exchange_name not in _KNOWN_EXCHANGES:
            raise ValueError(f"Exchange '{self.exchange_name}' not supported by ccxt")

        try:
            import ccxt
            exchange_class = getattr(ccxt, self.exchange_name, None)
            if exchange_class is None:
                raise ValueError(f"Exchange '{self.exchange_name}' not supported by ccxt")
            self._exchange = exchange_class({
                "timeout": self.timeout_ms,
                "enableRateLimit": True,
            })
            logger.debug("Initialized %s exchange", self.exchange_name)
        except ValueError:
            raise
        except Exception as e:
            logger.error("Failed to initialize %s: %s", self.exchange_name, e)
            raise

    def _get_cache_path(self, symbol: str, timeframe: str, ext: str = "parquet") -> Path:
        """캐시 파일 경로 생성."""
        if not self.cache_dir:
            return None
        safe_symbol = symbol.replace("/", "_")
        return self.cache_dir / f"{safe_symbol}_{timeframe}.{ext}"

    def _load_from_cache(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """캐시에서 데이터 로드. parquet → pickle 순으로 시도."""
        if not self.cache_dir:
            return None

        # parquet 우선 시도
        parquet_path = self._get_cache_path(symbol, timeframe, "parquet")
        if parquet_path.exists():
            try:
                df = pd.read_parquet(parquet_path)
                logger.debug("Loaded %d candles from cache (parquet): %s %s",
                           len(df), symbol, timeframe)
                return df
            except Exception as e:
                logger.warning("Failed to load parquet cache %s: %s", parquet_path, e)

        # pickle 폴백
        pickle_path = self._get_cache_path(symbol, timeframe, "pkl")
        if pickle_path.exists():
            try:
                df = pd.read_pickle(pickle_path)
                logger.debug("Loaded %d candles from cache (pickle): %s %s",
                           len(df), symbol, timeframe)
                return df
            except Exception as e:
                logger.warning("Failed to load pickle cache %s: %s", pickle_path, e)

        return None

    def _save_to_cache(self, df: pd.DataFrame, symbol: str, timeframe: str):
        """캐시에 데이터 저장. parquet 실패 시 pickle으로 폴백."""
        if not self.cache_dir or df.empty:
            return

        # parquet 우선 시도
        parquet_path = self._get_cache_path(symbol, timeframe, "parquet")
        try:
            df.to_parquet(parquet_path)
            logger.debug("Saved %d candles to cache (parquet): %s", len(df), parquet_path)
            return
        except Exception as e:
            logger.debug("Parquet save failed, falling back to pickle: %s", e)

        # pickle 폴백
        pickle_path = self._get_cache_path(symbol, timeframe, "pkl")
        try:
            df.to_pickle(pickle_path)
            logger.debug("Saved %d candles to cache (pickle): %s", len(df), pickle_path)
        except Exception as e:
            logger.warning("Failed to save cache %s: %s", pickle_path, e)

    def download(
        self,
        symbol: str,
        timeframe: str,
        days: int = 180,
        limit: int = 1000,
        validate: bool = True,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        OHLCV 데이터를 다운로드 (페이지네이션).

        Args:
            symbol: 심볼 (예: "BTC/USDT")
            timeframe: 타임프레임 (예: "1h")
            days: 다운로드할 일 수
            limit: 한 번에 페치할 최대 캔들 수 (exchange별로 제한 있음)
            validate: 다운로드 후 검증 여부
            use_cache: 캐시 사용 여부

        Returns:
            OHLCV DataFrame (columns: open, high, low, close, volume)

        Raises:
            ValueError: 데이터 검증 실패 또는 exchange 에러
        """
        # 캐시에서 로드 시도
        if use_cache:
            cached = self._load_from_cache(symbol, timeframe)
            if cached is not None:
                return cached

        # 실제 다운로드
        logger.info("Downloading %s %s for %d days (paginated)...",
                   symbol, timeframe, days)
        df = self._fetch_paginated(symbol, timeframe, days, limit)

        if df is None or df.empty:
            raise ValueError(f"No data retrieved for {symbol} {timeframe}")

        # 캐시 저장
        if use_cache:
            self._save_to_cache(df, symbol, timeframe)

        # 검증
        if validate:
            report = self.validate_data(df, timeframe)
            if not report.is_valid:
                logger.warning("Data validation failed: %s", report)
                # 경고만 하고 데이터는 반환 (호출자가 판단)

        return df

    def _fetch_paginated(
        self,
        symbol: str,
        timeframe: str,
        days: int,
        limit: int,
    ) -> Optional[pd.DataFrame]:
        """페이지네이션으로 데이터 수집."""
        if self._exchange is None:
            raise RuntimeError("Exchange not initialized. Cannot fetch data.")
        
        tf_ms = TIMEFRAME_MS.get(timeframe, 3_600_000)
        total_candles = (days * 24 * 3600 * 1000) // tf_ms

        all_data = []
        now_ms = int(time.time() * 1000)
        since = now_ms - (total_candles * tf_ms)

        seen_ts: Set[int] = set()
        stall_count = 0
        attempt = 0

        while len(all_data) < total_candles and attempt < self.max_retries:
            try:
                logger.debug("Fetching %s (since=%s, limit=%d)",
                           symbol, datetime.fromtimestamp(since/1000, tz=None), limit)
                ohlcv = self._exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)

                if not ohlcv:
                    stall_count += 1
                    if stall_count >= 3:
                        logger.info("No more data available, stopping pagination")
                        break
                    time.sleep(1)
                    continue

                stall_count = 0
                new_count = 0
                for row in ohlcv:
                    if row[0] not in seen_ts:
                        seen_ts.add(row[0])
                        all_data.append(row)
                        new_count += 1

                if new_count == 0:
                    stall_count += 1
                    if stall_count >= 3:
                        break

                # 다음 페이지로
                since = ohlcv[-1][0] + tf_ms
                if since >= now_ms:
                    logger.debug("Reached current time, stopping pagination")
                    break

                # Rate limiting
                time.sleep(0.3)
                attempt = 0  # Reset attempt counter on success

            except Exception as e:
                attempt += 1
                logger.warning("Fetch attempt %d/%d failed: %s (retrying...)",
                             attempt, self.max_retries, str(e)[:100])
                if attempt >= self.max_retries:
                    raise
                time.sleep(min(2 ** attempt, 10))

        if not all_data:
            return None

        df = pd.DataFrame(
            all_data,
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.drop_duplicates(subset=["timestamp"]).set_index("timestamp").sort_index()

        logger.info("Downloaded %d candles: %s ~ %s (%d days)",
                   len(df), df.index[0], df.index[-1],
                   (df.index[-1] - df.index[0]).days)
        return df

    def validate_data(
        self,
        df: pd.DataFrame,
        timeframe: str,
    ) -> DataValidationReport:
        """
        데이터 무결성 검증.

        Returns:
            DataValidationReport with detailed findings
        """
        anomalies = []

        # 1. 빈 DataFrame 체크
        if df.empty:
            return DataValidationReport(
                symbol="UNKNOWN",
                timeframe=timeframe,
                total_candles=0,
                start_time="",
                end_time="",
                missing_candles=0,
                gap_count=0,
                gaps=[],
                anomalies=["Empty DataFrame"],
                data_quality_pct=0.0,
                is_valid=False,
            )

        # 2. OHLC 관계 검증
        invalid_high = df[df["high"] < df[["open", "close"]].max(axis=1)]
        if not invalid_high.empty:
            anomalies.append(
                f"high < max(open,close) at {invalid_high.index[0]}"
            )

        invalid_low = df[df["low"] > df[["open", "close"]].min(axis=1)]
        if not invalid_low.empty:
            anomalies.append(
                f"low > min(open,close) at {invalid_low.index[0]}"
            )

        inverted = df[df["high"] < df["low"]]
        if not inverted.empty:
            anomalies.append(f"high < low at {inverted.index[0]}")

        # 3. 가격 0 이하 체크
        if (df["close"] <= 0).any():
            anomalies.append("close <= 0 detected")

        # 4. 극단적 가격 점프 (>10% in single candle)
        pct_change = df["close"].pct_change().abs()
        spikes = pct_change[pct_change > 0.10]
        if not spikes.empty:
            anomalies.append(f"price spike >10% at {spikes.index[0]}")

        # 5. 갭과 누락 캔들 감지
        missing, gaps = self._detect_gaps(df, timeframe)
        # ─ 데이터 품질 통계 (kurtosis, skewness) 계산 및 로깅 ─
        kurtosis_val = None
        skewness_val = None
        if len(df) > 2:
            try:
                log_returns = np.log(df["close"].pct_change() + 1).dropna()
                if len(log_returns) > 2:
                    kurtosis_val = stats.kurtosis(log_returns)
                    skewness_val = stats.skew(log_returns)
                    symbol_name = getattr(df, 'name', 'UNKNOWN')
                    logger.debug(
                        "Data quality stats for %s %s: kurtosis=%.2f, skewness=%.2f",
                        symbol_name,
                        timeframe,
                        kurtosis_val,
                        skewness_val
                    )
                    # fat-tail 부재 경고: 암호화폐 정상 범위는 kurtosis ≥ 2.0
                    if kurtosis_val < 2.0:
                        logger.warning(
                            "Low kurtosis detected for %s %s: %.2f (expected ≥ 2.0). "
                            "Data may lack fat tails — synthetic or stale data suspected.",
                            symbol_name,
                            timeframe,
                            kurtosis_val,
                        )
            except Exception as e:
                logger.debug("Failed to compute data stats: %s", e)


        # 6. 데이터 품질 점수
        expected_candles = len(pd.date_range(
            start=df.index[0],
            end=df.index[-1],
            freq=self._freq_from_timeframe(timeframe)
        ))
        quality_pct = 100.0 * len(df) / expected_candles if expected_candles > 0 else 0.0

        # 누락 데이터 비율 > 5% 경고 (Cycle 149)
        if expected_candles > 0 and missing > 0:
            missing_ratio = missing / expected_candles
            if missing_ratio > 0.05:
                symbol_name = df.name if hasattr(df, 'name') else "UNKNOWN"
                logger.warning(
                    "High missing data ratio for %s %s: %.1f%% (%d/%d candles missing). "
                    "Consider re-downloading or using a different timeframe.",
                    symbol_name,
                    timeframe,
                    missing_ratio * 100,
                    missing,
                    expected_candles,
                )

        return DataValidationReport(
            symbol=df.name if hasattr(df, 'name') else "UNKNOWN",
            timeframe=timeframe,
            total_candles=len(df),
            start_time=str(df.index[0]),
            end_time=str(df.index[-1]),
            missing_candles=missing,
            gap_count=len(gaps),
            gaps=gaps,
            anomalies=anomalies,
            data_quality_pct=min(100.0, quality_pct),
            is_valid=(missing == 0 and len(anomalies) == 0 and len(gaps) == 0),
        )

    def _detect_gaps(
        self,
        df: pd.DataFrame,
        timeframe: str,
    ) -> Tuple[int, List[Tuple[str, str]]]:
        """
        타임프레임에 맞는 갭과 누락 캔들 감지.

        Returns:
            (missing_count, [(gap_start, gap_end), ...])
        """
        freq = self._freq_from_timeframe(timeframe)
        if freq is None:
            return 0, []

        expected = pd.date_range(
            start=df.index[0],
            end=df.index[-1],
            freq=freq
        )
        missing = len(expected) - len(df)

        gaps = []
        if missing > 0:
            # 갭 구간 찾기
            expected_set = set(expected)
            actual_set = set(df.index)
            gap_idx = sorted(expected_set - actual_set)

            # 연속된 갭을 구간으로 병합
            if gap_idx:
                gap_start = gap_idx[0]
                gap_end = gap_idx[0]
                for ts in gap_idx[1:]:
                    if (ts - gap_end).total_seconds() <= 2 * self._seconds_per_timeframe(timeframe):
                        gap_end = ts
                    else:
                        gaps.append((str(gap_start), str(gap_end)))
                        gap_start = ts
                        gap_end = ts
                gaps.append((str(gap_start), str(gap_end)))

        return missing, gaps

    @staticmethod
    def _freq_from_timeframe(timeframe: str) -> Optional[str]:
        """타임프레임을 pandas freq로 변환."""
        freq_map = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "1h": "1h",
            "4h": "4h",
            "1d": "1D",
        }
        return freq_map.get(timeframe)

    @staticmethod
    def _seconds_per_timeframe(timeframe: str) -> int:
        """타임프레임을 초 단위로 변환."""
        ms = TIMEFRAME_MS.get(timeframe, 3_600_000)
        return ms // 1000


def download_multi_timeframe(
    symbol: str,
    timeframes: List[str] = None,
    days: int = 180,
    exchange: str = "bybit",
    cache_dir: str = "./data_cache",
) -> Dict[str, pd.DataFrame]:
    """
    여러 타임프레임 데이터를 한 번에 다운로드.

    Args:
        symbol: 심볼 (예: "BTC/USDT")
        timeframes: 타임프레임 리스트 (예: ["1h", "4h", "1d"])
        days: 다운로드할 일 수
        exchange: 거래소 (예: "bybit")
        cache_dir: 캐시 디렉토리

    Returns:
        {timeframe: DataFrame, ...}

    Example:
        dfs = download_multi_timeframe("BTC/USDT", ["1h", "4h"], days=180)
        print(dfs["1h"].shape)  # (4320, 5)
    """
    if timeframes is None:
        timeframes = ["1h", "4h", "1d"]

    downloader = HistoricalDataDownloader(
        exchange=exchange,
        cache_dir=cache_dir,
    )

    results = {}
    for tf in timeframes:
        try:
            df = downloader.download(symbol, tf, days=days, validate=True)
            results[tf] = df
            logger.info("Downloaded %s: %d candles", tf, len(df))
        except Exception as e:
            logger.error("Failed to download %s: %s", tf, e)
            results[tf] = None

    return results
