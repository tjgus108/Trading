"""
_fetch_fresh 경계 테스트: NaN/공 DataFrame 처리
"""

from unittest.mock import MagicMock
import pandas as pd
import pytest

from src.data.feed import DataFeed


class TestFetchFreshBoundaries:
    """_fetch_fresh 경계 조건 테스트."""

    def test_fetch_fresh_empty_dataframe(self):
        """빈 raw 데이터 → ValueError 발생."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = []  # 빈 리스트
        
        feed = DataFeed(connector)
        
        # 수정된 동작: ValueError 발생 (명확한 에러)
        with pytest.raises(ValueError, match="Empty OHLCV data"):
            feed.fetch("BTC/USDT", "1h", limit=500)

    def test_fetch_fresh_single_candle_with_nan(self):
        """단일 캔들 NaN 데이터 → 지표 계산 및 summary 반환."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, float('nan'), 100],  # NaN close
        ]
        
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        # DataSummary 정상 생성 (NaN값이 있어도 반환)
        assert result.symbol == "BTC/USDT"
        assert result.candles == 1
        assert pd.isna(result.df['close'].iloc[0])
        # 지표는 모두 계산됨
        assert 'ema20' in result.df.columns
        assert 'rsi14' in result.df.columns
        assert 'atr14' in result.df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestCacheTTLBoundaries:
    """캐시 TTL 경계 조건 테스트."""

    def test_cache_ttl_zero_disables_cache(self):
        """ttl=0 → 캐시 비활성화 (모든 요청이 미스)."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 41900, 100],
        ]
        
        feed = DataFeed(connector, cache_ttl=0)
        
        # 첫 fetch
        result1 = feed.fetch("BTC/USDT", "1h", limit=500)
        assert result1.symbol == "BTC/USDT"
        assert feed.cache_stats()['hit_count'] == 0
        assert feed.cache_stats()['miss_count'] == 1
        
        # 동일 key로 두 번째 fetch → ttl=0이므로 캐시 무효
        result2 = feed.fetch("BTC/USDT", "1h", limit=500)
        assert feed.cache_stats()['hit_count'] == 0
        assert feed.cache_stats()['miss_count'] == 2
        
        # fetch_ohlcv 호출이 2번
        assert connector.fetch_ohlcv.call_count == 2

    def test_cache_ttl_very_large_value(self):
        """ttl=999999999 → 캐시 거의 항상 유효 (테스트 범위 내)."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 41900, 100],
        ]
        
        feed = DataFeed(connector, cache_ttl=999999999)
        
        # 첫 fetch
        result1 = feed.fetch("BTC/USDT", "1h", limit=500)
        assert feed.cache_stats()['miss_count'] == 1
        
        # 동일 key로 10번 fetch → 모두 캐시 히트
        for _ in range(10):
            result = feed.fetch("BTC/USDT", "1h", limit=500)
            assert result.symbol == "BTC/USDT"
        
        assert feed.cache_stats()['hit_count'] == 10
        assert feed.cache_stats()['miss_count'] == 1
        
        # fetch_ohlcv 호출은 1번만
        assert connector.fetch_ohlcv.call_count == 1


class TestRegimeAwareCacheTTL:
    """레짐 기반 캐시 TTL 차별화 테스트."""

    def _make_feed(self, cache_ttl=60):
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 41900, 100],
        ]
        return DataFeed(connector, cache_ttl=cache_ttl)

    def test_high_volatility_shorter_ttl(self):
        """고변동성 레짐 → TTL이 base의 0.33배."""
        feed = self._make_feed(cache_ttl=60)
        feed.cache_regime("BTC/USDT", "high_volatility")
        assert feed._effective_ttl("BTC/USDT") == pytest.approx(60 * 0.33, abs=0.1)

    def test_low_volatility_longer_ttl(self):
        """저변동성 레짐 → TTL이 base의 1.5배."""
        feed = self._make_feed(cache_ttl=60)
        feed.cache_regime("BTC/USDT", "low_volatility")
        assert feed._effective_ttl("BTC/USDT") == pytest.approx(90.0, abs=0.1)

    def test_crisis_very_short_ttl(self):
        """위기 레짐 → TTL이 base의 0.2배."""
        feed = self._make_feed(cache_ttl=100)
        feed.cache_regime("BTC/USDT", "crisis")
        assert feed._effective_ttl("BTC/USDT") == pytest.approx(100 * 0.2, abs=0.1)

    def test_no_regime_uses_base_ttl(self):
        """레짐 미설정 → 기본 TTL 사용."""
        feed = self._make_feed(cache_ttl=60)
        assert feed._effective_ttl("BTC/USDT") == 60

    def test_unknown_regime_uses_base_ttl(self):
        """알 수 없는 레짐 → 기본 TTL 사용 (multiplier 1.0)."""
        feed = self._make_feed(cache_ttl=60)
        feed.cache_regime("BTC/USDT", "some_unknown_regime")
        assert feed._effective_ttl("BTC/USDT") == 60

    def test_regime_ttl_forces_cache_miss(self):
        """고변동성 레짐 설정 시 짧은 TTL로 캐시 미스 유도."""
        import time as _time
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 41900, 100],
        ]
        feed = DataFeed(connector, cache_ttl=60)

        # 첫 fetch → miss
        feed.fetch("BTC/USDT", "1h", limit=500)
        assert feed.cache_stats()['miss_count'] == 1

        # 고변동성 레짐 설정 (effective TTL = 20초)
        feed.cache_regime("BTC/USDT", "high_volatility")

        # 캐시 타임스탬프를 30초 전으로 조작 → base TTL(60s)로는 히트, regime TTL(20s)로는 미스
        key = ("BTC/USDT", "1h", 500)
        cached_summary, _ = feed._cache[key]
        feed._cache[key] = (cached_summary, _time.time() - 30)

        feed.fetch("BTC/USDT", "1h", limit=500)
        assert feed.cache_stats()['miss_count'] == 2  # regime TTL 때문에 미스

    def test_cache_stats_includes_regime_cache_size(self):
        """cache_stats에 regime_cache_size 포함."""
        feed = self._make_feed(cache_ttl=60)
        feed.cache_regime("BTC/USDT", "high_volatility")
        feed.cache_regime("ETH/USDT", "low_volatility")
        stats = feed.cache_stats()
        assert stats['regime_cache_size'] == 2


class TestTimestampGapDetection:
    """타임스탬프 갭 감지 테스트."""

    def test_no_gaps_clean_data(self):
        """갭 없는 정상 데이터 → 갭 이상 없음."""
        connector = MagicMock()
        dates = pd.date_range('2024-01-01', periods=100, freq='1h', tz='UTC')
        raw = [[int(d.timestamp() * 1000), 100, 101, 99, 100, 50] for d in dates]
        connector.fetch_ohlcv.return_value = raw

        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h")
        assert not any("timestamp gaps" in a for a in result.anomalies)

    def test_large_gap_detected(self):
        """큰 갭 (>3x median) 있으면 감지."""
        connector = MagicMock()
        dates = list(pd.date_range('2024-01-01', periods=50, freq='1h', tz='UTC'))
        # 50번째 캔들 이후 10시간 갭
        gap_dates = list(pd.date_range(dates[-1] + pd.Timedelta(hours=10), periods=50, freq='1h', tz='UTC'))
        all_dates = dates + gap_dates
        raw = [[int(d.timestamp() * 1000), 100, 101, 99, 100, 50] for d in all_dates]
        connector.fetch_ohlcv.return_value = raw

        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h")
        assert any("timestamp gaps" in a for a in result.anomalies)

    def test_single_candle_no_crash(self):
        """단일 캔들 → 갭 감지 없이 정상 처리."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 41900, 100],
        ]
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h")
        assert not any("timestamp gaps" in a for a in result.anomalies)


# ── 볼륨 단위 정규화 테스트 ──────────────────────────────────────

class TestVolumeNormalization:
    """볼륨 단위 정규화 테스트."""

    def _make_raw(self, n=50, close=50000.0, base_vol=2.0):
        """base volume 기준 raw OHLCV 생성."""
        import time
        ts = int(time.time() * 1000) - n * 3600000
        return [
            [ts + i * 3600000, close * 0.99, close * 1.01, close * 0.98, close, base_vol]
            for i in range(n)
        ]

    def test_volume_unit_base_default(self):
        """기본 volume_unit='base'이면 volume 변환 없음."""
        connector = MagicMock()
        raw = self._make_raw(close=50000.0, base_vol=2.0)
        connector.fetch_ohlcv.return_value = raw
        feed = DataFeed(connector, volume_unit="base")
        result = feed.fetch("BTC/USDT", "1h", limit=50)
        # base volume 유지 (2.0)
        assert abs(result.df["volume"].iloc[-1] - 2.0) < 0.01

    def test_volume_unit_quote_converts_to_base(self):
        """volume_unit='quote'이면 volume/close → base volume으로 변환."""
        connector = MagicMock()
        close = 50000.0
        quote_vol = 100000.0  # 100000 USDT = 2 BTC at 50000
        raw = self._make_raw(close=close, base_vol=quote_vol)
        connector.fetch_ohlcv.return_value = raw
        feed = DataFeed(connector, volume_unit="quote")
        result = feed.fetch("BTC/USDT", "1h", limit=50)
        # quote 변환: 100000 / 50000 = 2.0 BTC
        assert abs(result.df["volume"].iloc[-1] - 2.0) < 0.01

    def test_volume_quote_column_always_present(self):
        """volume_quote 컬럼은 항상 추가되어야 함."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw()
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=50)
        assert "volume_quote" in result.df.columns

    def test_volume_quote_equals_volume_times_close(self):
        """volume_quote = volume * close 검증."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(close=50000.0, base_vol=2.0)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=50)
        df = result.df
        expected = df["volume"] * df["close"]
        pd.testing.assert_series_equal(
            df["volume_quote"].iloc[-10:],
            expected.iloc[-10:],
            check_names=False,
        )

    def test_volume_quote_sma20_present(self):
        """volume_quote_sma20 컬럼이 추가되어야 함."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(n=50)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=50)
        assert "volume_quote_sma20" in result.df.columns


# ── _add_indicators NaN 경계값 테스트 (Cycle 393 C) ───────────────────────────


class TestAddIndicatorsNanBoundary:
    """_add_indicators() NaN/영값 경계 조건 테스트."""

    def _make_raw_candles(self, n=50, close=42000.0, volume=100.0):
        """단순 OHLCV raw 리스트 생성."""
        return [
            [1704067200000 + i * 3600000,
             close * 0.99, close * 1.01, close * 0.98, close, volume]
            for i in range(n)
        ]

    def test_zero_volume_no_inf_in_vwap(self):
        """volume=0 캔들에서 VWAP 계산 시 inf 발생 없음 (NaN이어야 함)."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw_candles(n=30, volume=0.0)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=30)
        df = result.df
        # VWAP 컬럼 존재 확인
        assert "vwap" in df.columns
        assert "vwap20" in df.columns
        # inf가 없어야 함 (NaN 또는 정상값만 허용)
        import numpy as np
        assert not np.isinf(df["vwap"].dropna()).any(), "vwap에 inf 발생"
        assert not np.isinf(df["vwap20"].dropna()).any(), "vwap20에 inf 발생"

    def test_constant_close_rsi_no_crash(self):
        """close 값이 모두 동일하면 avg_loss=0 → RSI가 NaN (크래시 아님)."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw_candles(n=30, close=42000.0)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=30)
        df = result.df
        # rsi14 컬럼 존재 (크래시 없이 완료)
        assert "rsi14" in df.columns
        # close 불변 → delta=0 → gain=loss=0 → rs=NaN → rsi14=NaN (첫 봉 이후)
        import numpy as np
        rsi_values = df["rsi14"].iloc[1:]  # 첫 봉 제외
        assert not np.isinf(rsi_values.dropna()).any(), "rsi14에 inf 발생"

    def test_bb_width_non_negative_for_normal_prices(self):
        """정상 가격 데이터에서 bb_width >= 0 이어야 함 (bb_upper >= bb_lower)."""
        import numpy as np
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw_candles(n=50, close=42000.0)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=50)
        df = result.df
        assert "bb_width" in df.columns
        valid = df["bb_width"].dropna()
        assert (valid >= 0).all(), f"bb_width 음수 발생: {valid[valid < 0]}"

    def test_macd_hist_equals_macd_minus_signal(self):
        """macd_hist = macd - macd_signal 일관성 검증."""
        import numpy as np
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw_candles(n=50, close=42000.0)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=50)
        df = result.df
        assert "macd" in df.columns
        assert "macd_signal" in df.columns
        assert "macd_hist" in df.columns
        expected = df["macd"] - df["macd_signal"]
        np.testing.assert_allclose(
            df["macd_hist"].values, expected.values, atol=1e-10,
            err_msg="macd_hist ≠ macd - macd_signal"
        )


# ── _add_indicators 매우 짧은 df 엣지케이스 테스트 (Cycle 398 C) ──────────────


class TestAddIndicatorsShortDf:
    """_add_indicators() 매우 짧은 df (< 10 rows) 경계 조건 테스트."""

    def _make_raw_candles(self, n: int, close: float = 42000.0, volume: float = 100.0):
        return [
            [1704067200000 + i * 3600000,
             close * 0.99, close * 1.01, close * 0.98, close, volume]
            for i in range(n)
        ]

    def test_very_short_df_3rows_no_crash(self):
        """3행 df → _add_indicators 크래시 없음, 모든 컬럼 생성."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw_candles(n=3)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=3)
        df = result.df
        for col in ["ema20", "ema50", "atr14", "rsi14", "sma20", "bb_upper", "bb_lower",
                    "macd", "macd_signal", "macd_hist", "bb_width", "vwap"]:
            assert col in df.columns, f"{col} 컬럼 없음"

    def test_very_short_df_1row_no_crash(self):
        """1행 df → 크래시 없음, 컬럼 추가됨."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw_candles(n=1)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=1)
        df = result.df
        assert len(df) == 1
        assert "ema20" in df.columns
        assert "atr14" in df.columns

    def test_short_df_5rows_atr_all_nan_except_last(self):
        """5행 df → ATR은 EWM이므로 값이 있어야 함 (rolling이 아닌 ewm 방식)."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw_candles(n=5)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=5)
        df = result.df
        # EWM(alpha=1/14) 방식: 첫 봉부터 값 계산됨 (NaN은 첫 봉만)
        assert "atr14" in df.columns
        non_nan = df["atr14"].dropna()
        assert len(non_nan) >= 1, "atr14가 전부 NaN"

    def test_short_df_volume_quote_auto_created(self):
        """단 행 df에서도 volume_quote 컬럼이 자동 생성됨."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw_candles(n=2)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=2)
        df = result.df
        assert "volume_quote" in df.columns
        assert "volume_quote_sma20" in df.columns

    def test_short_df_donchian_all_nan_when_insufficient_data(self):
        """5행 df → donchian은 rolling(20)이므로 전부 NaN."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw_candles(n=5)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=5)
        df = result.df
        assert "donchian_high" in df.columns
        # donchian_high: shift(1).rolling(20) → n=5에서는 전부 NaN
        assert df["donchian_high"].isna().all(), "donchian_high가 5행에서 NaN이 아님"
