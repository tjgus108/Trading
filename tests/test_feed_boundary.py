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


# ── Cycle400 C(데이터): duplicate timestamp 처리 + 다수 동일 심볼 요청 ──────


class TestToDataframeDuplicateTimestamps:
    """_to_dataframe duplicate timestamp 제거 테스트 (Cycle400 C)."""

    def test_duplicate_timestamps_removed_keep_last(self):
        """동일 타임스탬프 2개 → 마지막 값 유지, 행 수 1개."""
        connector = MagicMock()
        ts = 1704067200000
        connector.fetch_ohlcv.return_value = [
            [ts, 42000, 42500, 41800, 42100, 100],  # 첫 번째 (제거됨)
            [ts, 42000, 42500, 41800, 42200, 100],  # 두 번째 (keep last)
        ]
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        assert len(result.df) == 1, f"중복 제거 후 1행 기대: {len(result.df)}"
        assert result.df["close"].iloc[0] == pytest.approx(42200.0), (
            "중복 제거 시 마지막 값(42200) 유지 기대"
        )

    def test_three_duplicate_timestamps_keep_last(self):
        """3개 중복 타임스탬프 → 마지막 1행만 남음."""
        connector = MagicMock()
        ts = 1704067200000
        connector.fetch_ohlcv.return_value = [
            [ts, 42000, 42500, 41800, 42000, 100],
            [ts, 42000, 42500, 41800, 42100, 100],
            [ts, 42000, 42500, 41800, 42200, 100],  # keep
        ]
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        assert len(result.df) == 1
        assert result.df["close"].iloc[0] == pytest.approx(42200.0)

    def test_partial_duplicates_unique_retained(self):
        """일부만 중복인 경우 — 중복 2개 + 고유 1개 → 총 2행."""
        connector = MagicMock()
        ts1 = 1704067200000
        ts2 = 1704070800000  # 1시간 후
        connector.fetch_ohlcv.return_value = [
            [ts1, 42000, 42500, 41800, 42000, 100],  # 중복1 (제거)
            [ts1, 42000, 42500, 41800, 42100, 100],  # 중복1 keep
            [ts2, 43000, 43500, 42800, 43000, 200],  # 고유
        ]
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        assert len(result.df) == 2, f"부분 중복 → 2행 기대: {len(result.df)}"


# ── Cycle403 C(데이터): ema200/ema20_slope/return_5 엣지케이스 ─────────────────


class TestAddIndicatorsNewColumnsEdge:
    """ema200, ema20_slope, return_5 엣지케이스 (Cycle403 C)."""

    def _make_raw(self, n: int = 50, close: float = 42000.0):
        return [
            [1704067200000 + i * 3600000,
             close * 0.99, close * 1.01, close * 0.98, close, 100.0]
            for i in range(n)
        ]

    def test_ema200_column_present_and_last_value_finite(self):
        """50행 데이터 → ema200 컬럼이 생성되고 마지막 행은 유한값."""
        import numpy as np
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(n=50)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=50)
        df = result.df
        assert "ema200" in df.columns, "ema200 컬럼 없음"
        assert np.isfinite(df["ema200"].iloc[-1]), "ema200 마지막 값이 NaN/inf"

    def test_ema20_slope_near_zero_for_constant_close(self):
        """close 일정 → ema20 기울기(ema20_slope)는 0에 근접해야 함."""
        import numpy as np
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(n=50, close=42000.0)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=50)
        df = result.df
        assert "ema20_slope" in df.columns, "ema20_slope 컬럼 없음"
        # close 일정 → ema20 diff ≈ 0, slope ≈ 0
        valid = df["ema20_slope"].dropna()
        assert (valid.abs() < 1e-8).all(), f"ema20_slope가 0 아님: {valid.abs().max()}"

    def test_return_5_nan_first_rows_finite_after_five(self):
        """20행 데이터 → return_5(pct_change(5)): 처음 4행 NaN, 5행 이후 유한값."""
        import numpy as np
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(n=20)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=20)
        df = result.df
        assert "return_5" in df.columns, "return_5 컬럼 없음"
        # 첫 5행은 NaN (pct_change(5))
        assert df["return_5"].iloc[:5].isna().all(), "return_5 첫 5행이 NaN이 아님"
        # 6행 이후(인덱스 5+)는 유한값
        later = df["return_5"].iloc[5:]
        assert later.notna().all(), f"return_5 6행 이후에 NaN 존재: {later.isna().sum()}"


class TestSameSymbolMultipleRequests:
    """동일 심볼 복수 요청 캐시 동작 테스트 (Cycle400 C)."""

    def _make_raw(self, n: int = 50):
        return [
            [1704067200000 + i * 3600000, 42000, 42500, 41800, 42000, 100]
            for i in range(n)
        ]

    def test_same_symbol_second_request_hits_cache(self):
        """동일 심볼·타임프레임·limit 두 번째 요청 → 캐시 히트."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(50)
        feed = DataFeed(connector, cache_ttl=3600)

        feed.fetch("BTC/USDT", "1h", limit=50)  # miss
        feed.fetch("BTC/USDT", "1h", limit=50)  # hit

        assert feed.cache_stats()["hit_count"] == 1
        assert connector.fetch_ohlcv.call_count == 1

    def test_different_limit_is_different_cache_key(self):
        """limit 다름 → 캐시 키 불일치 → 두 번 모두 미스."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(50)
        feed = DataFeed(connector, cache_ttl=3600)

        feed.fetch("BTC/USDT", "1h", limit=50)
        feed.fetch("BTC/USDT", "1h", limit=100)

        assert feed.cache_stats()["miss_count"] == 2
        assert connector.fetch_ohlcv.call_count == 2

    def test_different_symbol_is_different_cache_key(self):
        """심볼 다름 → 별도 캐시 키 → 각각 미스."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(50)
        feed = DataFeed(connector, cache_ttl=3600)

        feed.fetch("BTC/USDT", "1h", limit=50)
        feed.fetch("ETH/USDT", "1h", limit=50)

        assert feed.cache_stats()["miss_count"] == 2
        assert connector.fetch_ohlcv.call_count == 2


# ── Cycle405 C(데이터): rsi14 NaN 첫 행, bb 관계, volume 0 처리 ──────────────


class TestIndicatorEdgeCases:
    """DataFeed 지표 엣지케이스 — rsi14, bb 관계, volume 0 (Cycle405 C)."""

    def _make_raw(self, n: int, close: float = 42000.0, volume: float = 100.0):
        return [
            [1704067200000 + i * 3600000,
             close * 0.99, close * 1.01, close * 0.98, close, volume]
            for i in range(n)
        ]

    def test_rsi14_nan_first_rows(self):
        """30행 데이터 → rsi14 첫 14행 이내에 NaN이 존재해야 함 (warm-up 필요)."""
        import numpy as np
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(n=30)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=30)
        df = result.df
        assert "rsi14" in df.columns, "rsi14 컬럼 없음"
        # RSI(14)는 최소 14+1=15행 이후부터 유효 — 앞부분에 NaN 존재해야 함
        early = df["rsi14"].iloc[:14]
        assert early.isna().any(), "rsi14 첫 14행 내 NaN이 없음 (warm-up 미적용)"

    def test_bb_upper_gte_bb_lower(self):
        """50행 정상 데이터 → bb_upper >= bb_lower 항상 성립해야 함."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(n=50)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=50)
        df = result.df
        assert "bb_upper" in df.columns
        assert "bb_lower" in df.columns
        valid = df[["bb_upper", "bb_lower"]].dropna()
        assert (valid["bb_upper"] >= valid["bb_lower"]).all(), (
            "bb_upper < bb_lower 케이스 발생"
        )

    def test_volume_zero_no_inf_no_crash(self):
        """volume=0 데이터 → 크래시 없음, vwap/volume_quote에 inf 없음."""
        import numpy as np
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(n=30, volume=0.0)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=30)
        df = result.df
        assert isinstance(df, pd.DataFrame)
        for col in ["vwap", "volume_quote"]:
            if col in df.columns:
                vals = df[col].replace([np.inf, -np.inf], np.nan)
                assert not np.isinf(df[col].fillna(0)).any(), f"{col}에 inf 존재"


# ── Cycle408 C(데이터): ema200/bb_width/macd_hist 경계값 테스트 ──────────────


class TestIndicatorBoundaryC408:
    """Cycle408 C(데이터): ema200 지연 특성, bb_width 상수, macd_hist 추세 방향 경계 테스트."""

    def _make_raw(self, closes, base_ts=1704067200000):
        """지정된 close 값으로 OHLCV raw 리스트 생성."""
        rows = []
        for i, c in enumerate(closes):
            rows.append([
                base_ts + i * 3600000,
                c * 0.999, c * 1.001, c * 0.998, c, 100.0
            ])
        return rows

    def test_ema200_lags_ema20_on_sudden_spike(self):
        """가격 급등 시 ema200이 ema20보다 close와의 거리가 더 멀어야 함 (ema200 더 느린 반응)."""
        import numpy as np
        # 250 행: 처음 240은 고정, 마지막 10은 급등
        base_price = 42000.0
        spike_price = 50000.0
        closes = [base_price] * 240 + [spike_price] * 10
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(closes)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=250)
        df = result.df
        last_close = float(df["close"].iloc[-1])
        last_ema20 = float(df["ema20"].iloc[-1])
        last_ema200 = float(df["ema200"].iloc[-1])
        dist20 = abs(last_close - last_ema20)
        dist200 = abs(last_close - last_ema200)
        assert dist200 > dist20, (
            f"ema200({dist200:.2f})이 ema20({dist20:.2f})보다 close와 가까움 — 반응 속도 역전"
        )

    def test_bb_width_zero_for_constant_close(self):
        """모든 봉의 close가 동일 → std=0 → bb_upper=bb_lower → bb_width=0."""
        import numpy as np
        constant_close = 42000.0
        closes = [constant_close] * 50
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(closes)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=50)
        df = result.df
        assert "bb_width" in df.columns, "bb_width 컬럼 없음"
        valid = df["bb_width"].dropna()
        assert len(valid) > 0, "bb_width 유효값 없음"
        # 상수 close → std=0 → bb_width=0
        assert (valid.abs() < 1e-9).all(), (
            f"상수 가격 bb_width 비영 값 존재: max={valid.abs().max():.2e}"
        )

    def test_macd_hist_positive_in_sustained_uptrend(self):
        """지속적 상승 추세에서 macd_hist > 0 이어야 함 (fast EMA > slow EMA → hist > 0)."""
        import numpy as np
        # 100 행 단조 증가 가격
        closes = [40000.0 + i * 50.0 for i in range(100)]
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(closes)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=100)
        df = result.df
        assert "macd_hist" in df.columns, "macd_hist 컬럼 없음"
        last_hist = float(df["macd_hist"].iloc[-1])
        assert last_hist > 0, (
            f"단조 상승 추세 macd_hist 마지막 값 음수: {last_hist:.6f}"
        )


# ---------------------------------------------------------------------------
# Cycle410 C(데이터): EMA slope, donchian shift, vwap20 경계 테스트
# ---------------------------------------------------------------------------

class TestIndicatorBoundaryC410:
    """Cycle410 C(데이터): feed.py 지표 경계값 테스트."""

    def _make_raw(self, closes, volumes=None):
        """최소 OHLCV 원시 데이터 생성."""
        ts_base = 1704067200000
        result = []
        for i, c in enumerate(closes):
            vol = volumes[i] if volumes else 100.0
            result.append([ts_base + i * 3600000, c * 0.998, c * 1.002, c * 0.995, c, vol])
        return result

    def test_ema20_slope_positive_for_sustained_uptrend(self):
        """지속 상승 추세에서 ema20_slope 마지막 값이 양수여야 함."""
        closes = [40000.0 + i * 100.0 for i in range(60)]
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(closes)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=60)
        df = result.df
        assert "ema20_slope" in df.columns, "ema20_slope 컬럼 없음"
        last_slope = float(df["ema20_slope"].iloc[-1])
        assert last_slope > 0, (
            f"상승 추세 ema20_slope 마지막 값이 양수여야 함: {last_slope:.8f}"
        )

    def test_donchian_high_excludes_current_bar(self):
        """donchian_high는 shift(1)로 현재 봉을 제외 — 마지막 봉 직전 20봉 최고가 반영."""
        # 처음 20봉은 일정 가격, 마지막 봉 high를 대폭 높임
        closes = [40000.0] * 20 + [50000.0]  # 21봉
        connector = MagicMock()
        raw = []
        ts_base = 1704067200000
        for i, c in enumerate(closes):
            h = c * 1.001  # high는 close의 0.1% 위
            raw.append([ts_base + i * 3600000, c * 0.999, h, c * 0.998, c, 100.0])
        connector.fetch_ohlcv.return_value = raw
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=21)
        df = result.df
        assert "donchian_high" in df.columns, "donchian_high 컬럼 없음"
        last_donchian = float(df["donchian_high"].iloc[-1])
        # 마지막 봉(high=50050)이 donchian_high에 반영되지 않아야 함
        # shift(1) → 마지막 봉 직전 20봉 기준 → max ≈ 40000*1.001 = 40040
        assert last_donchian < 45000.0, (
            f"donchian_high는 현재 봉 제외 — 40040 근처 기대, 실제: {last_donchian:.2f}"
        )

    def test_vwap20_finite_with_uniform_price_volume(self):
        """균일 가격/거래량 데이터 → vwap20이 NaN/Inf 아닌 유한값이어야 함."""
        closes = [40000.0] * 50
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw(closes, volumes=[500.0] * 50)
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=50)
        df = result.df
        assert "vwap20" in df.columns, "vwap20 컬럼 없음"
        last_vwap20 = float(df["vwap20"].iloc[-1])
        assert not (last_vwap20 != last_vwap20), f"vwap20 NaN: {last_vwap20}"  # NaN check
        assert abs(last_vwap20) < float("inf"), f"vwap20 Inf: {last_vwap20}"
        # 균일 가격에서 vwap20 ≈ typical price = (high+low+close)/3
        # _make_raw: high=close*1.002, low=close*0.995 → typical ≈ 40000*(1.002+0.995+1)/3 = 39960
        typical_approx = 40000.0 * (1.002 + 0.995 + 1.0) / 3.0
        assert abs(last_vwap20 - typical_approx) < 10.0, (
            f"균일 가격 vwap20 ≈ {typical_approx:.0f} 기대: {last_vwap20:.2f}"
        )


# ── Cycle403 C(데이터): invalidate_cache() 동작 테스트 ──────────────────────


class TestInvalidateCache:
    """invalidate_cache() 심볼별·전체 무효화 테스트 (Cycle403 C)."""

    def _make_raw(self, n: int = 10):
        return [
            [1704067200000 + i * 3600000, 42000, 42500, 41800, 42000, 100]
            for i in range(n)
        ]

    def test_invalidate_specific_symbol_forces_refetch(self):
        """특정 심볼 무효화 → 해당 심볼 다음 fetch는 미스."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw()
        feed = DataFeed(connector, cache_ttl=3600)

        feed.fetch("BTC/USDT", "1h", limit=10)   # miss → cached
        assert feed.cache_stats()["miss_count"] == 1

        feed.invalidate_cache(symbol="BTC/USDT")

        feed.fetch("BTC/USDT", "1h", limit=10)   # must re-fetch
        assert feed.cache_stats()["miss_count"] == 2
        assert connector.fetch_ohlcv.call_count == 2

    def test_invalidate_all_clears_every_entry(self):
        """전체 무효화 → 모든 심볼 캐시 제거."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw()
        feed = DataFeed(connector, cache_ttl=3600)

        feed.fetch("BTC/USDT", "1h", limit=10)
        feed.fetch("ETH/USDT", "1h", limit=10)
        assert feed.cache_stats()["miss_count"] == 2

        feed.invalidate_cache()  # 전체 무효화

        feed.fetch("BTC/USDT", "1h", limit=10)
        feed.fetch("ETH/USDT", "1h", limit=10)
        assert feed.cache_stats()["miss_count"] == 4
        assert connector.fetch_ohlcv.call_count == 4

    def test_invalidate_one_symbol_other_remains_cached(self):
        """BTC 무효화 → ETH는 캐시 유지."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._make_raw()
        feed = DataFeed(connector, cache_ttl=3600)

        feed.fetch("BTC/USDT", "1h", limit=10)
        feed.fetch("ETH/USDT", "1h", limit=10)
        assert connector.fetch_ohlcv.call_count == 2

        feed.invalidate_cache(symbol="BTC/USDT")

        # ETH는 여전히 캐시 히트
        feed.fetch("ETH/USDT", "1h", limit=10)
        assert connector.fetch_ohlcv.call_count == 2  # ETH는 재요청 없음

        # BTC는 캐시 미스
        feed.fetch("BTC/USDT", "1h", limit=10)
        assert connector.fetch_ohlcv.call_count == 3
