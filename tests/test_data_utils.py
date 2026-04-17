"""
Tests for src/data/data_utils.py — data download and validation.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

from src.data.data_utils import (
    HistoricalDataDownloader,
    DataValidationReport,
    TIMEFRAME_MS,
)


class TestDataValidationReport:
    """DataValidationReport 클래스 테스트."""
    
    def test_report_creation(self):
        """레포트 생성 및 필드 확인."""
        report = DataValidationReport(
            symbol="BTC/USDT",
            timeframe="1h",
            total_candles=1000,
            start_time="2024-01-01",
            end_time="2024-02-11",
            missing_candles=5,
            gap_count=1,
            gaps=[("2024-01-15", "2024-01-16")],
            anomalies=["price spike >10%"],
            data_quality_pct=99.5,
            is_valid=False,
        )
        
        assert report.symbol == "BTC/USDT"
        assert report.timeframe == "1h"
        assert report.total_candles == 1000
        assert report.is_valid is False
        assert len(report.anomalies) == 1
    
    def test_report_string_representation(self):
        """레포트 문자열 출력 확인."""
        report = DataValidationReport(
            symbol="ETH/USDT",
            timeframe="4h",
            total_candles=500,
            start_time="2024-01-01",
            end_time="2024-01-30",
            missing_candles=0,
            gap_count=0,
            gaps=[],
            anomalies=[],
            data_quality_pct=100.0,
            is_valid=True,
        )
        
        report_str = str(report)
        assert "ETH/USDT" in report_str
        assert "4h" in report_str
        assert "500" in report_str


class TestHistoricalDataDownloaderInit:
    """HistoricalDataDownloader 초기화 테스트."""
    
    def test_init_default(self):
        """기본값으로 초기화."""
        downloader = HistoricalDataDownloader()
        
        assert downloader.exchange_name == "bybit"
        assert downloader.timeout_ms == 20000
        assert downloader.max_retries == 3
        assert downloader.cache_dir is None
    
    def test_init_with_cache(self):
        """캐시 디렉토리 지정."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = HistoricalDataDownloader(cache_dir=tmpdir)
            assert downloader.cache_dir == Path(tmpdir)
            assert downloader.cache_dir.exists()
    
    def test_init_invalid_exchange(self):
        """지원하지 않는 거래소."""
        with pytest.raises(ValueError):
            HistoricalDataDownloader(exchange="nonexistent_exchange")


class TestDataValidation:
    """데이터 검증 로직 테스트."""
    
    def create_valid_df(self, num_candles=1000) -> pd.DataFrame:
        """유효한 OHLCV DataFrame 생성."""
        dates = pd.date_range('2024-01-01', periods=num_candles, freq='1h', tz='UTC')
        base_price = 50000
        df = pd.DataFrame({
            'open': base_price + np.random.randn(num_candles) * 100,
            'high': base_price + abs(np.random.randn(num_candles)) * 150,
            'low': base_price - abs(np.random.randn(num_candles)) * 150,
            'close': base_price + np.random.randn(num_candles) * 100,
            'volume': np.random.rand(num_candles) * 1000,
        }, index=dates)
        
        # OHLC 관계 정정
        df['high'] = df[['open', 'high', 'close']].max(axis=1) + 1
        df['low'] = df[['open', 'low', 'close']].min(axis=1) - 1
        return df
    
    def test_validate_perfect_data(self):
        """완벽한 데이터 검증."""
        downloader = HistoricalDataDownloader()
        df = self.create_valid_df(1000)
        
        report = downloader.validate_data(df, "1h")
        
        assert report.is_valid is True
        assert report.anomalies == []
        assert report.missing_candles == 0
        assert report.gap_count == 0
        assert report.data_quality_pct == 100.0
    
    def test_validate_empty_dataframe(self):
        """빈 DataFrame 검증."""
        downloader = HistoricalDataDownloader()
        df = pd.DataFrame()
        
        report = downloader.validate_data(df, "1h")
        
        assert report.is_valid is False
        assert "Empty DataFrame" in report.anomalies
        assert report.total_candles == 0
    
    def test_validate_negative_price(self):
        """음수 가격 감지."""
        downloader = HistoricalDataDownloader()
        df = self.create_valid_df(100)
        df.loc[df.index[10], 'close'] = -100  # 음수 가격
        
        report = downloader.validate_data(df, "1h")
        
        assert report.is_valid is False
        assert any("close <= 0" in a for a in report.anomalies)
    
    def test_validate_inverted_ohlc(self):
        """high < low 감지."""
        downloader = HistoricalDataDownloader()
        df = self.create_valid_df(100)
        df.loc[df.index[10], 'high'] = 100
        df.loc[df.index[10], 'low'] = 1000
        
        report = downloader.validate_data(df, "1h")
        
        assert report.is_valid is False
        assert any("high < low" in a for a in report.anomalies)
    
    def test_validate_price_spike(self):
        """극단적 가격 점프 감지 (>10%)."""
        downloader = HistoricalDataDownloader()
        df = self.create_valid_df(100)
        df.loc[df.index[10], 'close'] = df.loc[df.index[9], 'close'] * 1.15  # 15% 점프
        
        report = downloader.validate_data(df, "1h")
        
        assert report.is_valid is False
        assert any("spike" in a.lower() for a in report.anomalies)
    
    def test_detect_gaps(self):
        """시계열 갭 감지."""
        downloader = HistoricalDataDownloader()
        
        # 정상 시리즈 생성 후 중간에 2시간 갭 추가
        dates = pd.date_range('2024-01-01', periods=100, freq='1h', tz='UTC')
        df = self.create_valid_df(100)
        df.index = dates
        
        # 50번째와 51번째 사이에 갭 추가
        df = df.drop(df.index[50:52])
        
        report = downloader.validate_data(df, "1h")
        
        assert report.missing_candles == 2
        assert report.gap_count > 0
        assert len(report.gaps) > 0


class TestCacheOperations:
    """캐시 저장/로드 테스트."""
    
    def test_cache_save_and_load(self):
        """캐시 저장 및 로드."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = HistoricalDataDownloader(cache_dir=tmpdir)
            
            # 테스트 데이터프레임
            dates = pd.date_range('2024-01-01', periods=100, freq='1h', tz='UTC')
            df = pd.DataFrame({
                'open': [50000] * 100,
                'high': [50100] * 100,
                'low': [49900] * 100,
                'close': [50050] * 100,
                'volume': [1000] * 100,
            }, index=dates)
            
            # 캐시 저장
            downloader._save_to_cache(df, "BTC/USDT", "1h")
            
            # 캐시 로드
            loaded = downloader._load_from_cache("BTC/USDT", "1h")
            
            assert loaded is not None
            assert len(loaded) == len(df)
            pd.testing.assert_frame_equal(df, loaded)
    
    def test_cache_miss_when_disabled(self):
        """캐시 비활성화 시 로드 실패."""
        downloader = HistoricalDataDownloader(cache_dir=None)
        
        result = downloader._load_from_cache("BTC/USDT", "1h")
        
        assert result is None


class TestUtilityFunctions:
    """유틸리티 함수 테스트."""
    
    def test_freq_from_timeframe(self):
        """타임프레임 to pandas freq 변환."""
        downloader = HistoricalDataDownloader()
        
        assert downloader._freq_from_timeframe("1m") == "1min"
        assert downloader._freq_from_timeframe("5m") == "5min"
        assert downloader._freq_from_timeframe("1h") == "1h"
        assert downloader._freq_from_timeframe("4h") == "4h"
        assert downloader._freq_from_timeframe("1d") == "1D"
        assert downloader._freq_from_timeframe("unknown") is None
    
    def test_seconds_per_timeframe(self):
        """타임프레임 to 초 변환."""
        downloader = HistoricalDataDownloader()
        
        assert downloader._seconds_per_timeframe("1m") == 60
        assert downloader._seconds_per_timeframe("1h") == 3600
        assert downloader._seconds_per_timeframe("1d") == 86400


class TestTimefameConstants:
    """TIMEFRAME_MS 상수 테스트."""
    
    def test_timeframe_ms_values(self):
        """타임프레임 밀리초 값."""
        assert TIMEFRAME_MS["1m"] == 60_000
        assert TIMEFRAME_MS["5m"] == 300_000
        assert TIMEFRAME_MS["15m"] == 900_000
        assert TIMEFRAME_MS["1h"] == 3_600_000
        assert TIMEFRAME_MS["4h"] == 14_400_000
        assert TIMEFRAME_MS["1d"] == 86_400_000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
