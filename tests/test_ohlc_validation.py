"""
OHLC 관계 검증 테스트
"""

from unittest.mock import MagicMock
import pandas as pd
import pytest

from src.data.feed import DataFeed


class TestOHLCValidation:
    """OHLC 관계 검증 테스트."""

    def test_valid_ohlc_relationships(self):
        """정상 OHLC 데이터: 이상 감지 없음."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42200, 100],  # high=42500 >= max(42000,42200), low=41800 <= min(42000,42200)
            [1704070800000, 42200, 42800, 42000, 42500, 150],  # 정상
        ]
        
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        # anomalies에 OHLC 관련 이상이 없어야 함
        ohlc_issues = [a for a in result.anomalies if 'high' in a or 'low' in a]
        assert len(ohlc_issues) == 0, f"정상 데이터인데 이상 감지: {ohlc_issues}"

    def test_high_less_than_max_open_close(self):
        """high < max(open, close) 감지."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 41500, 41800, 42200, 100],  # high=41500 < max(42000,42200)=42200 (오류!)
        ]
        
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        # anomalies에 high 이상 감지
        assert any('high < max(open,close)' in a for a in result.anomalies), \
            f"high 이상 미감지: {result.anomalies}"

    def test_low_greater_than_min_open_close(self):
        """low > min(open, close) 감지."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 42100, 42200, 100],  # low=42100 > min(42000,42200)=42000 (오류!)
        ]
        
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        # anomalies에 low 이상 감지
        assert any('low > min(open,close)' in a for a in result.anomalies), \
            f"low 이상 미감지: {result.anomalies}"

    def test_high_less_than_low(self):
        """high < low 감지 (기존 로직)."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 41500, 42200, 42100, 100],  # high=41500 < low=42200 (역전!)
        ]
        
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        # anomalies에 역전 감지
        assert any('high < low' in a for a in result.anomalies), \
            f"역전 미감지: {result.anomalies}"


class TestAnomalyDetectionExtended:
    """추가 이상 감지 테스트 (volume 0, stale feed)."""

    def _make_candles(self, n=20, base=42000, step=1):
        """n개의 정상 캔들 생성. 1시간 간격, OHLC 관계 정상."""
        candles = []
        ts = 1704067200000
        price = base
        for i in range(n):
            candles.append([ts + i * 3600000, price, price + 50, price - 50, price + step * i, 100 + i])
        return candles

    def test_zero_volume_below_threshold_no_anomaly(self):
        """볼륨 0 캔들이 1% 미만이면 anomaly 기록 안함."""
        connector = MagicMock()
        candles = self._make_candles(100)
        # 1개만 zero vol → 1% 이하, anomaly 없음
        candles[5][5] = 0
        connector.fetch_ohlcv.return_value = candles

        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        assert not any("zero volume" in a for a in result.anomalies), \
            f"Unexpected zero-vol anomaly: {result.anomalies}"

    def test_zero_volume_above_threshold_anomaly(self):
        """볼륨 0 캔들이 1% 초과 시 anomaly 기록."""
        connector = MagicMock()
        candles = self._make_candles(20)
        # 20개 중 2개 zero vol → 10%, anomaly 발생
        candles[3][5] = 0
        candles[10][5] = 0
        connector.fetch_ohlcv.return_value = candles

        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        assert any("zero volume" in a for a in result.anomalies), \
            f"Expected zero-vol anomaly, got: {result.anomalies}"

    def test_stale_feed_consecutive_identical_closes(self):
        """연속 5개 이상 동일 종가 → stale feed 이상 감지."""
        connector = MagicMock()
        candles = self._make_candles(20, step=0)
        # close 모두 동일 (step=0) → 연속 중복
        for c in candles:
            c[4] = 42000  # close 고정
        connector.fetch_ohlcv.return_value = candles

        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        assert any("stale feed" in a for a in result.anomalies), \
            f"Expected stale feed anomaly, got: {result.anomalies}"

    def test_no_stale_feed_with_varying_closes(self):
        """종가가 변하는 정상 데이터는 stale 미감지."""
        connector = MagicMock()
        candles = self._make_candles(20, step=10)  # 10씩 증가
        connector.fetch_ohlcv.return_value = candles

        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        assert not any("stale feed" in a for a in result.anomalies), \
            f"Unexpected stale feed: {result.anomalies}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
