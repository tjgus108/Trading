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
    validate_ohlcv,
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


class TestValidateOhlcv:
    """validate_ohlcv() 함수 테스트."""
    
    def test_validate_normal_data(self):
        """정상 데이터 검증 → is_valid=True."""
        dates = pd.date_range('2024-01-01', periods=100, freq='4h', tz='UTC')
        df = pd.DataFrame({
            'open': [50000.0] * 100,
            'high': [50100.0] * 100,
            'low': [49900.0] * 100,
            'close': [50050.0] * 100,
            'volume': [1000.0] * 100,
        }, index=dates)
        
        result = validate_ohlcv(df, expected_interval_seconds=14400)
        
        assert result['is_valid'] == True
        assert result['duplicates'] == 0
        assert result['gaps'] == 0
        assert result['ohlc_violations'] == 0
        assert result['gap_ratio'] == 0.0
    
    def test_validate_with_duplicates(self):
        """중복 포함 → duplicates > 0."""
        dates = pd.date_range('2024-01-01', periods=100, freq='4h', tz='UTC')
        df = pd.DataFrame({
            'open': [50000.0] * 100,
            'high': [50100.0] * 100,
            'low': [49900.0] * 100,
            'close': [50050.0] * 100,
            'volume': [1000.0] * 100,
        }, index=dates)
        
        # 중복 행 추가
        df = pd.concat([df, df.iloc[[10]]])
        df = df.sort_index()
        
        result = validate_ohlcv(df, expected_interval_seconds=14400)
        
        assert result['is_valid'] == False
        assert result['duplicates'] > 0
    
    def test_validate_with_gaps(self):
        """갭 포함 → gaps > 0, gap_ratio > 0."""
        dates = pd.date_range('2024-01-01', periods=100, freq='4h', tz='UTC')
        df = pd.DataFrame({
            'open': [50000.0] * 100,
            'high': [50100.0] * 100,
            'low': [49900.0] * 100,
            'close': [50050.0] * 100,
            'volume': [1000.0] * 100,
        }, index=dates)
        
        # 갭 추가 (50번째와 51번째 사이에 2개 행 제거)
        df = df.drop(df.index[50:52])
        
        result = validate_ohlcv(df, expected_interval_seconds=14400)
        
        assert result['is_valid'] == False
        assert result['gaps'] > 0
        assert result['gap_ratio'] > 0
    
    def test_validate_with_ohlc_violations(self):
        """OHLC 위반 → ohlc_violations > 0."""
        dates = pd.date_range('2024-01-01', periods=100, freq='4h', tz='UTC')
        df = pd.DataFrame({
            'open': [50000.0] * 100,
            'high': [50100.0] * 100,
            'low': [49900.0] * 100,
            'close': [50050.0] * 100,
            'volume': [1000.0] * 100,
        }, index=dates)
        
        # OHLC 위반: high < open
        df.loc[df.index[10], 'high'] = 49500.0
        
        result = validate_ohlcv(df, expected_interval_seconds=14400)
        
        assert result['is_valid'] == False
        assert result['ohlc_violations'] > 0
    
    def test_validate_with_negative_volume(self):
        """음수 볼륨 포함."""
        dates = pd.date_range('2024-01-01', periods=100, freq='4h', tz='UTC')
        df = pd.DataFrame({
            'open': [50000.0] * 100,
            'high': [50100.0] * 100,
            'low': [49900.0] * 100,
            'close': [50050.0] * 100,
            'volume': [1000.0] * 100,
        }, index=dates)
        
        # 음수 볼륨 추가
        df.loc[df.index[10], 'volume'] = -100.0
        
        result = validate_ohlcv(df, expected_interval_seconds=14400)
        
        assert result['negative_volume'] > 0
        assert result['is_valid'] == True


class TestCsvLoader:
    """load_csv_ohlcv() 함수 테스트."""
    
    def test_load_csv_basic(self):
        """정상 CSV 파일 로드, 컬럼/인덱스 검증."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("timestamp,open,high,low,close,volume\n")
            f.write("2024-01-01 00:00:00,50000,50100,49900,50050,1000\n")
            f.write("2024-01-01 01:00:00,50050,50150,49950,50100,1100\n")
            f.write("2024-01-01 02:00:00,50100,50200,50000,50150,1200\n")
            csv_path = f.name
        
        try:
            from src.data.data_utils import load_csv_ohlcv
            
            df = load_csv_ohlcv(csv_path, validate=False)
            
            # 컬럼 확인
            assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']
            
            # 인덱스 확인 (DatetimeIndex, UTC)
            assert isinstance(df.index, pd.DatetimeIndex)
            assert df.index.tz is not None
            assert str(df.index.tz) == 'UTC'
            
            # 행 수 확인
            assert len(df) == 3
            
            # 값 확인
            assert df.iloc[0]['open'] == 50000
            assert df.iloc[0]['volume'] == 1000
        finally:
            import os
            os.unlink(csv_path)
    
    def test_load_csv_auto_validates(self):
        """validate=True일 때 validate_ohlcv 자동 호출."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("timestamp,open,high,low,close,volume\n")
            f.write("2024-01-01 00:00:00,50000,50100,49900,50050,1000\n")
            f.write("2024-01-01 01:00:00,50050,50150,49950,50100,1100\n")
            csv_path = f.name
        
        try:
            from src.data.data_utils import load_csv_ohlcv
            
            # validate=True로 로드
            df = load_csv_ohlcv(csv_path, validate=True, expected_interval_seconds=3600)
            
            # 데이터 로드 확인
            assert len(df) == 2
            assert df.iloc[0]['open'] == 50000
        finally:
            import os
            os.unlink(csv_path)
    
    def test_resample_1h_to_4h(self):
        """1h 데이터를 4h로 리샘플링."""
        from src.data.data_utils import resample_ohlcv
        
        # 1시간 간격 데이터 생성 (16개 = 4일)
        dates = pd.date_range('2024-01-01', periods=16, freq='1h', tz='UTC')
        df = pd.DataFrame({
            'open': [50000 + i*10 for i in range(16)],
            'high': [50100 + i*10 for i in range(16)],
            'low': [49900 + i*10 for i in range(16)],
            'close': [50050 + i*10 for i in range(16)],
            'volume': [1000 + i*100 for i in range(16)],
        }, index=dates)
        
        # 4h로 리샘플링
        df_4h = resample_ohlcv(df, '4h')
        
        # 캔들 수 확인 (약 16 / 4 = 4개)
        assert len(df_4h) == 4
        
        # 컬럼 확인
        assert list(df_4h.columns) == ['open', 'high', 'low', 'close', 'volume']
        
        # 첫 번째 4h 캔들: open은 첫 행, close는 4번째 행
        assert df_4h.iloc[0]['open'] == df.iloc[0]['open']  # 50000
        assert df_4h.iloc[0]['close'] == df.iloc[3]['close']  # 50080
        
        # 볼륨은 합산
        assert df_4h.iloc[0]['volume'] == df.iloc[0:4]['volume'].sum()
    
    def test_resample_invalid_timeframe(self):
        """잘못된 timeframe → ValueError."""
        from src.data.data_utils import resample_ohlcv

        dates = pd.date_range('2024-01-01', periods=10, freq='1h', tz='UTC')
        df = pd.DataFrame({
            'open': [50000] * 10,
            'high': [50100] * 10,
            'low': [49900] * 10,
            'close': [50050] * 10,
            'volume': [1000] * 10,
        }, index=dates)

        with pytest.raises(ValueError):
            resample_ohlcv(df, 'invalid_timeframe')

    def test_resample_drop_incomplete_partial_buckets(self):
        """misaligned 시작(01:00)이면 partial 버킷 제거 후 완전 4h 버킷만 남음."""
        from src.data.data_utils import resample_ohlcv

        # 01:00 시작 — 첫 4h 버킷(00:00-04:00)은 3개 candle, 마지막 버킷은 1개
        dates = pd.date_range('2024-01-01 01:00', periods=16, freq='1h', tz='UTC')
        df = pd.DataFrame({
            'open': [50000 + i * 10 for i in range(16)],
            'high': [50100 + i * 10 for i in range(16)],
            'low':  [49900 + i * 10 for i in range(16)],
            'close': [50050 + i * 10 for i in range(16)],
            'volume': [1000] * 16,
        }, index=dates)

        df_4h = resample_ohlcv(df, '4h', drop_incomplete=True)
        # 완전한 버킷만 남아야 함 (04:00, 08:00, 12:00 = 3개)
        assert len(df_4h) == 3, f"Expected 3 complete buckets, got {len(df_4h)}"
        # 첫 버킷이 04:00이어야 함 (00:00 partial 버킷 제거됨)
        assert df_4h.index[0] == pd.Timestamp('2024-01-01 04:00:00', tz='UTC')

    def test_resample_drop_incomplete_false_keeps_all(self):
        """drop_incomplete=False이면 partial 버킷도 유지."""
        from src.data.data_utils import resample_ohlcv

        dates = pd.date_range('2024-01-01 01:00', periods=16, freq='1h', tz='UTC')
        df = pd.DataFrame({
            'open': [50000] * 16,
            'high': [50100] * 16,
            'low':  [49900] * 16,
            'close': [50050] * 16,
            'volume': [1000] * 16,
        }, index=dates)

        df_4h = resample_ohlcv(df, '4h', drop_incomplete=False)
        # partial 버킷 포함: 5개 (00:00, 04:00, 08:00, 12:00, 16:00)
        assert len(df_4h) == 5, f"Expected 5 buckets with partial, got {len(df_4h)}"

    def test_resample_aligned_unaffected_by_drop_incomplete(self):
        """정렬된 데이터(00:00 시작)는 drop_incomplete=True여도 손실 없음."""
        from src.data.data_utils import resample_ohlcv

        dates = pd.date_range('2024-01-01 00:00', periods=16, freq='1h', tz='UTC')
        df = pd.DataFrame({
            'open': [50000] * 16,
            'high': [50100] * 16,
            'low':  [49900] * 16,
            'close': [50050] * 16,
            'volume': [1000] * 16,
        }, index=dates)

        df_4h = resample_ohlcv(df, '4h', drop_incomplete=True)
        assert len(df_4h) == 4  # 16 / 4 = 4 완전한 버킷
