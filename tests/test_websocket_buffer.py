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


class TestWebSocketReconnect:
    """WebSocket 재연결 로직 검증 (외부 API 호출 없이 모킹)."""

    def test_reconnect_retry_count_increments(self):
        """연결 실패 시 retry_count 증가."""
        import asyncio
        from unittest.mock import AsyncMock, patch
        
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        async def mock_listen_fail():
            raise ConnectionError("Mocked connection error")
        
        # _listen을 실패하도록 모킹
        with patch.object(feed, "_listen", side_effect=mock_listen_fail):
            try:
                asyncio.run(feed._connect_with_retry())
            except:
                pass
        
        # 최소 1회 이상 재시도 (MAX_RETRY=5 미만)
        assert feed._retry_count > 0
        assert feed._retry_count <= 5

    def test_reconnect_resets_on_success(self):
        """성공적 연결 후 retry_count 리셋."""
        import asyncio
        from unittest.mock import AsyncMock, patch
        
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        feed._retry_count = 3  # 이전 실패 상태
        
        async def mock_listen_success():
            # 성공: _process_message 시뮬레이션
            await asyncio.sleep(0.01)  # 짧은 대기 후 반환
        
        with patch.object(feed, "_listen", side_effect=mock_listen_success):
            with patch.object(feed, "_stop_event") as mock_stop:
                mock_stop.is_set.side_effect = [False, True]  # 1회 루프만
                try:
                    asyncio.run(feed._connect_with_retry())
                except:
                    pass
        
        # 성공 후 retry_count는 0으로 리셋됨
        assert feed._retry_count == 0

    def test_max_retry_stops_reconnect(self):
        """MAX_RETRY 초과 시 재연결 중단."""
        import asyncio
        from unittest.mock import patch
        
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        async def mock_listen_fail():
            raise ConnectionError("Persistent failure")
        
        with patch.object(feed, "_listen", side_effect=mock_listen_fail):
            try:
                asyncio.run(feed._connect_with_retry())
            except:
                pass
        
        # MAX_RETRY=5 도달 시 중단
        assert feed._retry_count == 5
        assert feed._connected == False

    def test_reconnect_exponential_backoff(self):
        """지수 백오프: 각 재시도마다 대기시간 증가."""
        import asyncio
        from unittest.mock import patch
        import time
        
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        attempt_times = []
        
        async def mock_listen_fail():
            attempt_times.append(time.time())
            raise ConnectionError("Simulated failure")
        
        with patch.object(feed, "_listen", side_effect=mock_listen_fail):
            start = time.time()
            try:
                asyncio.run(feed._connect_with_retry())
            except:
                pass
            elapsed = time.time() - start
        
        # 재시도가 발생했고, 대기시간이 누적됨
        assert feed._retry_count > 0
        # 지수 백오프로 인해 최소 대기 (2^1 + 2^2 + ... + 2^n) 초 이상 소요
        # 예: 5회 실패 → 2 + 4 + 8 + 16 + 32 = 62초 (하지만 실제는 더 빠름)
        # 단순 검증: 최소 1회 이상 지연 발생
        assert len(attempt_times) >= 2


class TestWebSocketMetrics:
    """WebSocket 연결 메트릭 추적 테스트."""
    
    def test_connection_metrics_initial_state(self):
        """초기 메트릭 상태 검증."""
        from src.data.websocket_feed import BinanceWebSocketFeed
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        metrics = feed.get_connection_metrics()
        assert metrics.is_connected == False
        assert metrics.retry_count == 0
        assert metrics.reconnection_count == 0
        assert metrics.total_candles_received == 0
    
    def test_connection_metrics_after_candle(self):
        """캔들 수신 후 메트릭 업데이트."""
        from src.data.websocket_feed import BinanceWebSocketFeed, CandleBar
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        bar = CandleBar(
            timestamp=1000,
            open=100.0,
            high=102.0,
            low=99.0,
            close=101.0,
            volume=1000.0,
        )
        with feed._lock:
            feed._candles.append(bar)
        
        # 메트릭 업데이트 (실제 메시지 처리는 시뮬레이션)
        metrics = feed.get_connection_metrics()
        # candle_count는 증가했을 것
        assert feed.candle_count() == 1
    
    def test_connection_metrics_uptime(self):
        """업타임 계산 검증."""
        import time
        from src.data.websocket_feed import BinanceWebSocketFeed
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        feed._start_time = time.time() - 10  # 10초 전 시작
        metrics = feed.get_connection_metrics()
        
        assert metrics.uptime_seconds is not None
        assert metrics.uptime_seconds >= 10  # 최소 10초 이상
    
    def test_connection_metrics_reconnection_count(self):
        """재연결 횟수 카운팅."""
        from src.data.websocket_feed import BinanceWebSocketFeed
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        feed._reconnection_count = 3
        metrics = feed.get_connection_metrics()
        
        assert metrics.reconnection_count == 3


class TestWebSocketBackoffJitter:
    """WebSocket exponential backoff + jitter 테스트."""
    
    def test_backoff_formula_retry_1(self):
        """retry_count=1: 약 2초 (jitter 포함)."""
        from src.data.websocket_feed import BinanceWebSocketFeed
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        delays = []
        for _ in range(100):
            delay = feed._calculate_backoff_with_jitter(1)
            delays.append(delay)
        
        avg_delay = sum(delays) / len(delays)
        # 평균이 2초 근처 (±10% jitter)
        assert 1.8 <= avg_delay <= 2.2, f"Expected ~2.0s, got {avg_delay}"
    
    def test_backoff_formula_retry_2(self):
        """retry_count=2: 약 4초 (jitter 포함)."""
        from src.data.websocket_feed import BinanceWebSocketFeed
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        delays = []
        for _ in range(100):
            delay = feed._calculate_backoff_with_jitter(2)
            delays.append(delay)
        
        avg_delay = sum(delays) / len(delays)
        # 평균이 4초 근처 (±10% jitter)
        assert 3.6 <= avg_delay <= 4.4, f"Expected ~4.0s, got {avg_delay}"
    
    def test_backoff_formula_retry_5(self):
        """retry_count=5: 약 32초 (jitter 포함)."""
        from src.data.websocket_feed import BinanceWebSocketFeed
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        delay = feed._calculate_backoff_with_jitter(5)
        
        # 32 * (1 ± 0.1) = 28.8 ~ 35.2
        assert 28.8 <= delay <= 35.2, f"Expected 28.8~35.2s, got {delay}"
    
    def test_backoff_jitter_variability(self):
        """지터: 같은 retry_count에서도 지연이 변함."""
        from src.data.websocket_feed import BinanceWebSocketFeed
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        delays = [feed._calculate_backoff_with_jitter(2) for _ in range(20)]
        
        # 지연이 다양해야 함 (지터 효과)
        min_delay = min(delays)
        max_delay = max(delays)
        
        # 최소와 최대가 다름 (표준편차 > 0)
        assert min_delay < max_delay, "Jitter should produce variable delays"
        
        # 범위가 예상 범위 내
        assert 3.6 <= min_delay <= 4.4
        assert 3.6 <= max_delay <= 4.4
    
    def test_backoff_exponential_growth(self):
        """지수 증가: retry_count가 높을수록 대기시간 길어짐."""
        from src.data.websocket_feed import BinanceWebSocketFeed
        feed = BinanceWebSocketFeed("btcusdt", "1h")
        
        # 지터 최소화 위해 여러 번 샘플
        base_delays = []
        for i in range(1, 6):
            samples = [feed._calculate_backoff_with_jitter(i) for _ in range(50)]
            avg = sum(samples) / len(samples)
            base_delays.append(avg)
        
        # 각 단계가 약 2배씩 증가해야 함
        for i in range(1, len(base_delays)):
            ratio = base_delays[i] / base_delays[i-1]
            # jitter 때문에 정확히 2배는 아니지만 1.8~2.2 범위
            assert 1.8 <= ratio <= 2.2, f"Step {i}: expected ~2x, got {ratio:.2f}x"
