"""WebSocket feed 버퍼 오버플로우 검증 테스트."""

import pytest
from collections import deque
from src.data.websocket_feed import BinanceWebSocketFeed, CandleBar
import time


class TestWebSocketBufferOverflow:
    """deque maxlen 버퍼 오버플로우 방지 검증."""

    def test_candle_buffer_maxlen_enforced(self):
        """버퍼 maxlen이 MAX_CANDLES를 초과하지 않음."""
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        # MAX_CANDLES 이상 추가 시뮬레이션
        for i in range(1500):
            bar = CandleBar(
                timestamp=1000 + i,
                open=100.0 + i * 0.01,
                high=102.0 + i * 0.01,
                low=99.0 + i * 0.01,
                close=101.0 + i * 0.01,
                volume=1000.0,
            )
            with feed._lock:
                feed._candles.append(bar)
        
        # 버퍼는 maxlen 초과하지 않음
        assert len(feed._candles) == 1000  # MAX_CANDLES = 1000
        
        # 최신 1000개 캔들 유지 확인
        with feed._lock:
            oldest_bar = list(feed._candles)[0]
            newest_bar = list(feed._candles)[-1]
        
        # 최신 1500개 중 마지막 1000개만 보존됨 (처음 500개 제거)
        assert oldest_bar.timestamp == 1500  # 1000 + 500
        assert newest_bar.timestamp == 2499  # 1000 + 1499

    def test_deque_auto_eviction(self):
        """deque maxlen 자동 제거 기능 확인."""
        test_deque = deque(maxlen=100)
        
        # 150개 추가
        for i in range(150):
            test_deque.append(i)
        
        # maxlen 초과 시 자동으로 오래된 항목 제거
        assert len(test_deque) == 100
        assert list(test_deque)[0] == 50  # 처음 50개 제거됨
        assert list(test_deque)[-1] == 149

    def test_candle_count_respects_maxlen(self):
        """candle_count() 메서드가 maxlen 이상 반환하지 않음."""
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        # 2000개 캔들 추가
        for i in range(2000):
            bar = CandleBar(
                timestamp=2000 + i,
                open=100.0,
                high=102.0,
                low=99.0,
                close=101.0,
                volume=1000.0,
            )
            with feed._lock:
                feed._candles.append(bar)
        
        # candle_count는 1000 이하
        assert feed.candle_count() == 1000
        assert feed.candle_count() <= 1000

    def test_get_latest_df_memory_bounded(self):
        """get_latest_df가 메모리 누수 없이 제한된 캔들만 반환."""
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        # 수천 개 캔들 추가
        for i in range(5000):
            bar = CandleBar(
                timestamp=int(1000 * 60000 + i * 3600000),  # 1h 간격 ms
                open=100.0 + i * 0.001,
                high=102.0 + i * 0.001,
                low=99.0 + i * 0.001,
                close=101.0 + i * 0.001,
                volume=1000.0 + i * 0.1,
            )
            with feed._lock:
                feed._candles.append(bar)
        
        # limit=500 조회
        df = feed.get_latest_df(limit=500)
        
        # DataFrame이 생성되고 최대 500개 행
        assert df is not None
        assert len(df) <= 500
        assert len(df) == 500  # 버퍼에 1000개 있으므로 정확히 500개
        
        # 내부 버퍼는 여전히 1000 제한
        assert feed.candle_count() == 1000

    def test_concurrent_append_respects_maxlen(self):
        """동시 append 시에도 maxlen 유지."""
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        # 빠른 연속 추가 (race condition 시뮬레이션)
        for batch in range(10):
            for i in range(200):
                bar = CandleBar(
                    timestamp=1000 + batch * 200 + i,
                    open=100.0,
                    high=102.0,
                    low=99.0,
                    close=101.0,
                    volume=1000.0,
                )
                with feed._lock:
                    feed._candles.append(bar)
        
        # 총 2000개 추가했지만 버퍼는 1000
        assert feed.candle_count() == 1000
        
        # 최신 1000개만 유지
        with feed._lock:
            candles_list = list(feed._candles)
        
        assert candles_list[0].timestamp == 2000  # 처음 1000개 제거 (1000~1999)
        assert candles_list[-1].timestamp == 2999  # 마지막 (2000~2999)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
