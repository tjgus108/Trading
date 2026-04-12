"""Data feeds health check 테스트."""

import pytest
from unittest.mock import MagicMock, PropertyMock

from src.data.health_check import (
    DataFeedsHealthCheck,
    FeedStatus,
    FeedHealthReport,
    DataHealthCheck,
)


class TestFeedHealthReport:
    """FeedHealthReport 단위 테스트."""

    def test_feed_health_report_creation(self):
        """기본 레포트 생성."""
        report = FeedHealthReport(
            name="test_feed",
            status=FeedStatus.LIVE,
            is_available=True,
            latency_ms=5.2,
            last_update="2024-01-01T10:00:00Z",
        )
        assert report.name == "test_feed"
        assert report.status == FeedStatus.LIVE
        assert report.is_available is True
        assert report.latency_ms == 5.2

    def test_feed_health_report_repr(self):
        """레포트 문자열 표현."""
        report = FeedHealthReport(
            name="binance_rest",
            status=FeedStatus.LIVE,
            is_available=True,
        )
        repr_str = repr(report)
        assert "binance_rest" in repr_str
        assert "LIVE" in repr_str

    def test_feed_health_report_unavailable(self):
        """unavailable 피드."""
        report = FeedHealthReport(
            name="broken_feed",
            status=FeedStatus.DISCONNECTED,
            is_available=False,
            error_msg="connection timeout",
        )
        repr_str = repr(report)
        assert "unavailable" in repr_str


class TestDataHealthCheck:
    """DataHealthCheck 전체 상태 레포트."""

    def test_data_health_check_healthy(self):
        """live 피드 있으면 healthy."""
        reports = {
            "feed1": FeedHealthReport("feed1", FeedStatus.LIVE, True),
        }
        health = DataHealthCheck(feeds=reports, live_count=1, total_feeds=1)
        assert health.is_healthy() is True

    def test_data_health_check_unhealthy(self):
        """live 피드 없으면 unhealthy."""
        reports = {
            "feed1": FeedHealthReport("feed1", FeedStatus.DISCONNECTED, False),
        }
        health = DataHealthCheck(feeds=reports, live_count=0, total_feeds=1)
        assert health.is_healthy() is False

    def test_data_health_check_repr(self):
        """상태 문자열 표현."""
        reports = {
            "feed1": FeedHealthReport("feed1", FeedStatus.LIVE, True),
            "feed2": FeedHealthReport("feed2", FeedStatus.FALLBACK, True),
        }
        health = DataHealthCheck(
            feeds=reports,
            live_count=1,
            fallback_count=1,
            disconnected_count=0,
            total_feeds=2,
            primary_feed="feed1",
        )
        repr_str = repr(health)
        assert "1 live" in repr_str
        assert "1 fallback" in repr_str
        assert "primary=feed1" in repr_str


class TestDataFeedsHealthCheck:
    """DataFeedsHealthCheck 메인 클래스."""

    def test_register_feed(self):
        """피드 등록."""
        checker = DataFeedsHealthCheck()
        mock_feed = MagicMock()
        checker.register_feed("test_feed", mock_feed, feed_type="rest")

        assert "test_feed" in checker._feeds
        assert checker._feed_types["test_feed"] == "rest"

    def test_check_rest_feed_live(self):
        """REST 피드 live 상태."""
        checker = DataFeedsHealthCheck()
        mock_feed = MagicMock()
        mock_feed.fetch = MagicMock(return_value={})
        mock_feed._cache = {}

        checker.register_feed("rest_feed", mock_feed, feed_type="rest")
        report = checker._check_rest_feed("rest_feed", mock_feed)

        assert report.status == FeedStatus.LIVE
        assert report.is_available is True
        assert "cache_size" in report.metadata

    def test_check_websocket_feed_connected(self):
        """WebSocket 피드 connected 상태."""
        checker = DataFeedsHealthCheck()
        mock_feed = MagicMock()
        mock_feed.is_connected = True
        mock_feed.candle_count = MagicMock(return_value=100)
        mock_feed._retry_count = 0

        report = checker._check_websocket_feed("ws_feed", mock_feed)

        assert report.status == FeedStatus.LIVE
        assert report.is_available is True
        assert report.metadata["candle_count"] == 100

    def test_check_websocket_feed_fallback(self):
        """WebSocket 피드 fallback 상태 (연결 끊겼지만 캔들 있음)."""
        checker = DataFeedsHealthCheck()
        mock_feed = MagicMock()
        mock_feed.is_connected = False
        mock_feed.candle_count = MagicMock(return_value=50)
        mock_feed._retry_count = 2
        mock_feed.MAX_RETRY = 5

        report = checker._check_websocket_feed("ws_feed", mock_feed)

        assert report.status == FeedStatus.FALLBACK
        assert report.is_available is True

    def test_check_websocket_feed_disconnected(self):
        """WebSocket 피드 완전히 disconnected (max retry 초과)."""
        checker = DataFeedsHealthCheck()
        mock_feed = MagicMock()
        mock_feed.is_connected = False
        mock_feed.candle_count = MagicMock(return_value=0)
        mock_feed._retry_count = 5
        mock_feed.MAX_RETRY = 5

        report = checker._check_websocket_feed("ws_feed", mock_feed)

        assert report.status == FeedStatus.DISCONNECTED
        assert report.is_available is False

    def test_check_ws_adapter_websocket_active(self):
        """WebSocketDataAdapter: websocket active."""
        checker = DataFeedsHealthCheck()
        mock_ws = MagicMock()
        mock_ws.is_connected = True
        mock_adapter = MagicMock()
        mock_adapter._ws = mock_ws
        mock_adapter._rest = None

        report = checker._check_ws_adapter("adapter", mock_adapter)

        assert report.status == FeedStatus.LIVE
        assert report.metadata["source"] == "websocket"

    def test_check_ws_adapter_rest_fallback(self):
        """WebSocketDataAdapter: REST fallback 사용 중."""
        checker = DataFeedsHealthCheck()
        mock_ws = MagicMock()
        mock_ws.is_connected = False
        mock_rest = MagicMock()
        mock_adapter = MagicMock()
        mock_adapter._ws = mock_ws
        mock_adapter._rest = mock_rest

        report = checker._check_ws_adapter("adapter", mock_adapter)

        assert report.status == FeedStatus.FALLBACK
        assert report.metadata["source"] == "rest_fallback"

    def test_check_dex_feed(self):
        """DEX 피드 상태."""
        checker = DataFeedsHealthCheck()
        mock_feed = MagicMock()
        mock_feed.get_price = MagicMock(return_value=50000.0)
        mock_feed._is_mock = False

        report = checker._check_dex_feed("dex_feed", mock_feed)

        assert report.status == FeedStatus.LIVE
        assert report.is_available is True

    def test_check_all_multiple_feeds(self):
        """여러 피드 종합 체크."""
        checker = DataFeedsHealthCheck()

        # REST feed (live)
        rest_feed = MagicMock()
        rest_feed.fetch = MagicMock()
        rest_feed._cache = {}
        checker.register_feed("rest", rest_feed, feed_type="rest")

        # WebSocket feed (live)
        ws_feed = MagicMock()
        ws_feed.is_connected = True
        ws_feed.candle_count = MagicMock(return_value=100)
        ws_feed._retry_count = 0
        checker.register_feed("websocket", ws_feed, feed_type="websocket")

        # DEX feed (live)
        dex_feed = MagicMock()
        dex_feed.get_price = MagicMock(return_value=50000.0)
        dex_feed._is_mock = False
        checker.register_feed("dex", dex_feed, feed_type="dex")

        result = checker.check_all()

        assert result.is_healthy() is True
        assert result.live_count == 3
        assert result.fallback_count == 0
        assert result.disconnected_count == 0
        assert result.total_feeds == 3
        assert result.primary_feed is not None

    def test_check_all_degraded_mode(self):
        """degraded mode: websocket fallback, REST live."""
        checker = DataFeedsHealthCheck()

        # REST feed (live)
        rest_feed = MagicMock()
        rest_feed.fetch = MagicMock()
        rest_feed._cache = {}
        checker.register_feed("rest", rest_feed, feed_type="rest")

        # WebSocket adapter (fallback to REST)
        mock_ws = MagicMock()
        mock_ws.is_connected = False
        mock_rest = MagicMock()
        mock_adapter = MagicMock()
        mock_adapter._ws = mock_ws
        mock_adapter._rest = mock_rest
        checker.register_feed("ws_adapter", mock_adapter, feed_type="adapter")

        result = checker.check_all()

        assert result.is_healthy() is True
        assert result.live_count == 1
        assert result.fallback_count == 1
        assert "operating_in_degraded_mode" in result.anomalies

    def test_check_all_all_disconnected(self):
        """anomaly: 모든 피드 disconnected (max retry 초과)."""
        checker = DataFeedsHealthCheck()

        # Disconnected WebSocket (max retry 초과)
        ws_feed = MagicMock()
        ws_feed.is_connected = False
        ws_feed.candle_count = MagicMock(return_value=0)
        ws_feed._retry_count = 5  # >= MAX_RETRY
        ws_feed.MAX_RETRY = 5
        checker.register_feed("websocket", ws_feed, feed_type="websocket")

        result = checker.check_all()

        assert result.is_healthy() is False
        assert result.disconnected_count == 1
        assert "all_feeds_disconnected" in result.anomalies


class TestDataHealthCheckExport:
    """DataHealthCheck JSON export 기능."""

    def test_to_dict_basic(self):
        """to_dict() 기본 변환."""
        reports = {
            "feed1": FeedHealthReport("feed1", FeedStatus.LIVE, True, latency_ms=5.0),
        }
        health = DataHealthCheck(
            feeds=reports,
            live_count=1,
            fallback_count=0,
            disconnected_count=0,
            total_feeds=1,
            primary_feed="feed1",
        )
        
        data = health.to_dict()
        
        assert data["live_count"] == 1
        assert data["fallback_count"] == 0
        assert data["disconnected_count"] == 0
        assert data["total_feeds"] == 1
        assert data["primary_feed"] == "feed1"
        assert data["is_healthy"] is True
        assert "feed1" in data["feeds"]

    def test_to_dict_with_anomalies(self):
        """to_dict() with anomalies."""
        reports = {
            "feed1": FeedHealthReport("feed1", FeedStatus.DISCONNECTED, False),
        }
        health = DataHealthCheck(
            feeds=reports,
            live_count=0,
            fallback_count=0,
            disconnected_count=1,
            total_feeds=1,
            anomalies=["all_feeds_disconnected"],
        )
        
        data = health.to_dict()
        
        assert data["is_healthy"] is False
        assert data["anomalies"] == ["all_feeds_disconnected"]

    def test_to_dict_feed_details(self):
        """to_dict() includes feed details."""
        report = FeedHealthReport(
            "test_feed",
            FeedStatus.LIVE,
            True,
            latency_ms=10.5,
            last_update="2024-01-01T10:00:00Z",
            error_msg=None,
            metadata={"cache_size": 100},
        )
        health = DataHealthCheck(feeds={"test_feed": report}, live_count=1, total_feeds=1)
        
        data = health.to_dict()
        feed_data = data["feeds"]["test_feed"]
        
        assert feed_data["status"] == "LIVE"
        assert feed_data["is_available"] is True
        assert feed_data["latency_ms"] == 10.5
        assert feed_data["last_update"] == "2024-01-01T10:00:00Z"
        assert feed_data["metadata"]["cache_size"] == 100

    def test_to_json_valid_json(self):
        """to_json() produces valid JSON."""
        import json
        
        reports = {
            "feed1": FeedHealthReport("feed1", FeedStatus.LIVE, True),
            "feed2": FeedHealthReport("feed2", FeedStatus.FALLBACK, True),
        }
        health = DataHealthCheck(
            feeds=reports,
            live_count=1,
            fallback_count=1,
            total_feeds=2,
            primary_feed="feed1",
        )
        
        json_str = health.to_json()
        
        # Should parse without error
        parsed = json.loads(json_str)
        assert parsed["live_count"] == 1
        assert parsed["fallback_count"] == 1
        assert parsed["total_feeds"] == 2

    def test_to_json_formatting(self):
        """to_json() is properly formatted (indented)."""
        reports = {
            "feed1": FeedHealthReport("feed1", FeedStatus.LIVE, True),
        }
        health = DataHealthCheck(feeds=reports, live_count=1, total_feeds=1)
        
        json_str = health.to_json()
        
        # Indented JSON should have newlines and spaces
        assert "\n" in json_str
        assert "  " in json_str  # 2-space indent

    def test_to_json_round_trip(self):
        """to_json() → json.loads() → to_dict() round-trip validation."""
        import json
        
        # Create original health check with multiple feeds
        reports = {
            "rest": FeedHealthReport(
                "rest",
                FeedStatus.LIVE,
                True,
                latency_ms=5.2,
                last_update="2024-01-01T10:00:00Z",
                metadata={"cache_size": 100}
            ),
            "websocket": FeedHealthReport(
                "websocket",
                FeedStatus.FALLBACK,
                True,
                latency_ms=2.1,
                error_msg=None,
                metadata={"candle_count": 50, "retry_count": 2}
            ),
        }
        original_health = DataHealthCheck(
            feeds=reports,
            live_count=1,
            fallback_count=1,
            disconnected_count=0,
            total_feeds=2,
            primary_feed="rest",
            anomalies=["operating_in_degraded_mode"]
        )
        
        # Step 1: to_json()
        json_str = original_health.to_json()
        
        # Step 2: parse JSON back
        parsed_dict = json.loads(json_str)
        
        # Step 3: compare key fields
        assert parsed_dict["live_count"] == 1
        assert parsed_dict["fallback_count"] == 1
        assert parsed_dict["disconnected_count"] == 0
        assert parsed_dict["total_feeds"] == 2
        assert parsed_dict["primary_feed"] == "rest"
        assert parsed_dict["is_healthy"] is True
        assert parsed_dict["anomalies"] == ["operating_in_degraded_mode"]
        
        # Step 4: verify feed details preserved
        rest_feed = parsed_dict["feeds"]["rest"]
        assert rest_feed["status"] == "LIVE"
        assert rest_feed["is_available"] is True
        assert rest_feed["latency_ms"] == 5.2
        assert rest_feed["last_update"] == "2024-01-01T10:00:00Z"
        assert rest_feed["metadata"]["cache_size"] == 100
        
        ws_feed = parsed_dict["feeds"]["websocket"]
        assert ws_feed["status"] == "FALLBACK"
        assert ws_feed["latency_ms"] == 2.1
        assert ws_feed["metadata"]["candle_count"] == 50
