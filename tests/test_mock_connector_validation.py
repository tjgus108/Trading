"""
MockExchangeConnector fetch_ohlcv 검증 테스트.
반환값 일관성, 경계값 테스트.
"""

import pytest
from src.exchange.mock_connector import MockExchangeConnector


class TestMockConnectorFetchOhlcv:
    """MockExchangeConnector.fetch_ohlcv() 검증"""

    @pytest.fixture
    def connector(self):
        return MockExchangeConnector(symbol="BTC/USDT", base_price=65000.0)

    def test_fetch_ohlcv_return_structure(self, connector):
        """반환값이 [ts, open, high, low, close, volume] 구조임을 검증."""
        candles = connector.fetch_ohlcv("BTC/USDT", "1h", limit=10)
        
        assert isinstance(candles, list), "fetch_ohlcv should return list"
        assert len(candles) == 10, f"Expected 10 candles, got {len(candles)}"
        
        for i, candle in enumerate(candles):
            assert len(candle) == 6, f"Candle {i}: expected 6 elements, got {len(candle)}"
            ts, open_, high, low, close, volume = candle
            
            # 타입 검증
            assert isinstance(ts, int), f"Candle {i}: timestamp should be int"
            assert isinstance(open_, (int, float)), f"Candle {i}: open should be numeric"
            assert isinstance(high, (int, float)), f"Candle {i}: high should be numeric"
            assert isinstance(low, (int, float)), f"Candle {i}: low should be numeric"
            assert isinstance(close, (int, float)), f"Candle {i}: close should be numeric"
            assert isinstance(volume, (int, float)), f"Candle {i}: volume should be numeric"

    def test_fetch_ohlcv_ohlc_consistency(self, connector):
        """OHLC 관계 일관성: high >= {open,close} >= low."""
        candles = connector.fetch_ohlcv("BTC/USDT", "1h", limit=50)
        
        for i, candle in enumerate(candles):
            ts, open_, high, low, close, volume = candle
            
            assert high >= open_, f"Candle {i}: high({high}) < open({open_})"
            assert high >= close, f"Candle {i}: high({high}) < close({close})"
            assert high >= low, f"Candle {i}: high({high}) < low({low})"
            assert close >= low, f"Candle {i}: close({close}) < low({low})"
            assert open_ >= low, f"Candle {i}: open({open_}) < low({low})"

    def test_fetch_ohlcv_timestamp_ordering(self, connector):
        """타임스탬프가 과거에서 미래 순으로 정렬됨."""
        candles = connector.fetch_ohlcv("BTC/USDT", "1h", limit=20)
        
        timestamps = [candle[0] for candle in candles]
        assert timestamps == sorted(timestamps), "Timestamps must be in ascending order"

    def test_fetch_ohlcv_volume_positive(self, connector):
        """모든 캔들의 volume >= 0."""
        candles = connector.fetch_ohlcv("BTC/USDT", "1h", limit=30)
        
        for i, candle in enumerate(candles):
            volume = candle[5]
            assert volume >= 0, f"Candle {i}: volume must be >= 0, got {volume}"

    def test_fetch_ohlcv_boundary_limit_1(self, connector):
        """limit=1 경계값 테스트."""
        candles = connector.fetch_ohlcv("BTC/USDT", "1h", limit=1)
        
        assert len(candles) == 1
        assert len(candles[0]) == 6

    def test_fetch_ohlcv_boundary_large_limit(self, connector):
        """limit=1000 경계값 테스트."""
        candles = connector.fetch_ohlcv("BTC/USDT", "1h", limit=1000)
        
        assert len(candles) == 1000
        # 첫번째 캔들과 마지막 캔들 검증
        assert len(candles[0]) == 6
        assert len(candles[-1]) == 6

    def test_fetch_ohlcv_timeframe_intervals(self, connector):
        """다양한 timeframe 지원 검증."""
        timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]
        
        for tf in timeframes:
            candles = connector.fetch_ohlcv("BTC/USDT", tf, limit=5)
            assert len(candles) == 5, f"Timeframe {tf}: expected 5 candles, got {len(candles)}"
            
            # 타임스탬프 간격 검증 (다음 캔들 - 현재 캔들 = 해당 timeframe interval)
            interval_map = {
                "1m": 60_000, "5m": 300_000, "15m": 900_000,
                "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000,
            }
            expected_interval = interval_map[tf]
            
            for i in range(len(candles) - 1):
                actual_interval = candles[i+1][0] - candles[i][0]
                assert actual_interval == expected_interval, \
                    f"Timeframe {tf}, candle {i}: expected interval {expected_interval}ms, got {actual_interval}ms"

    def test_fetch_ohlcv_unknown_timeframe_fallback(self, connector):
        """미지원 timeframe에서 기본값(1h) 적용."""
        candles = connector.fetch_ohlcv("BTC/USDT", "unknown_tf", limit=3)
        
        # 기본값 3600_000 (1h)로 처리되므로 간격이 1h
        assert len(candles) == 3
        for i in range(len(candles) - 1):
            interval = candles[i+1][0] - candles[i][0]
            assert interval == 3_600_000, "Unknown timeframe should fallback to 1h"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
