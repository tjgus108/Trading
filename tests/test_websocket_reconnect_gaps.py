"""WebSocket reconnect 갭 감지/보고 테스트 (Cycle 239)."""

import time
import pytest

from src.data.websocket_feed import BinanceWebSocketFeed, CandleBar


class TestReconnectGaps:
    """get_reconnect_gaps() 및 갭 기록 로직 검증."""

    def _make_feed(self) -> BinanceWebSocketFeed:
        return BinanceWebSocketFeed("btcusdt", "1h")

    def test_get_reconnect_gaps_initial_empty(self):
        """초기 상태에서 갭 목록은 빈 리스트."""
        feed = self._make_feed()
        gaps = feed.get_reconnect_gaps()
        assert gaps == []

    def test_record_reconnect_gap_single(self):
        """단일 reconnect 갭 기록 및 조회."""
        feed = self._make_feed()
        start = time.time() - 30.0
        end = time.time()
        feed._record_reconnect_gap(start, end)

        gaps = feed.get_reconnect_gaps()
        assert len(gaps) == 1
        assert gaps[0]["start"] == start
        assert gaps[0]["end"] == end
        assert abs(gaps[0]["gap_seconds"] - (end - start)) < 0.01

    def test_record_reconnect_gap_multiple(self):
        """여러 reconnect 갭이 순서대로 기록."""
        feed = self._make_feed()
        now = time.time()
        for i in range(5):
            feed._record_reconnect_gap(now + i * 10, now + i * 10 + 5)

        gaps = feed.get_reconnect_gaps()
        assert len(gaps) == 5
        # 모든 갭이 5초
        for g in gaps:
            assert abs(g["gap_seconds"] - 5.0) < 0.01

    def test_reconnect_gaps_fifo_max_100(self):
        """최대 100개까지만 FIFO로 보관."""
        feed = self._make_feed()
        now = time.time()
        for i in range(120):
            feed._record_reconnect_gap(now + i, now + i + 1)

        gaps = feed.get_reconnect_gaps()
        assert len(gaps) == 100
        # 가장 오래된 것은 i=20 (처음 20개는 제거)
        expected_start = now + 20
        assert abs(gaps[0]["start"] - expected_start) < 0.01

    def test_gap_recorded_on_reconnect_then_candle(self):
        """reconnect 후 첫 캔들 수신 시 갭이 자동 기록되는 시나리오."""
        feed = self._make_feed()
        # 이전에 데이터를 수신한 시점 시뮬레이션
        recv_time = time.time() - 60.0
        feed._last_recv_ts = recv_time

        # _pending_gap_start 설정 (reconnect 발생 시)
        feed._pending_gap_start = recv_time

        # 캔들 수신 시뮬레이션 (_process_message 호출)
        msg = {
            "k": {
                "t": 1704067200000,
                "o": "42000",
                "h": "42500",
                "l": "41800",
                "c": "42100",
                "v": "100",
                "x": True,
            }
        }
        feed._process_message(msg)

        gaps = feed.get_reconnect_gaps()
        assert len(gaps) == 1
        assert gaps[0]["start"] == recv_time
        assert gaps[0]["gap_seconds"] > 0

    def test_no_gap_without_prior_data(self):
        """이전 데이터 수신 이력 없이 reconnect 시 갭 기록 안 됨."""
        feed = self._make_feed()
        # _last_recv_ts가 None인 상태에서 캔들 수신
        assert feed._last_recv_ts is None
        assert feed._pending_gap_start is None  # type: ignore[attr-defined]

        msg = {
            "k": {
                "t": 1704067200000,
                "o": "42000",
                "h": "42500",
                "l": "41800",
                "c": "42100",
                "v": "100",
                "x": True,
            }
        }
        feed._process_message(msg)

        gaps = feed.get_reconnect_gaps()
        assert len(gaps) == 0

    def test_gap_dict_structure(self):
        """반환 딕셔너리에 start, end, gap_seconds 키가 존재."""
        feed = self._make_feed()
        feed._record_reconnect_gap(100.0, 130.0)
        gaps = feed.get_reconnect_gaps()
        assert len(gaps) == 1
        g = gaps[0]
        assert "start" in g
        assert "end" in g
        assert "gap_seconds" in g
        assert g["gap_seconds"] == 30.0

    def test_get_reconnect_gaps_returns_copy(self):
        """get_reconnect_gaps()는 복사본 반환 (원본 불변)."""
        feed = self._make_feed()
        feed._record_reconnect_gap(1.0, 2.0)
        gaps1 = feed.get_reconnect_gaps()
        gaps1.clear()  # 외부에서 삭제
        # 원본은 영향 없음
        gaps2 = feed.get_reconnect_gaps()
        assert len(gaps2) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
