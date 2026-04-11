"""
Data feeds integration smoke test: sentiment, onchain, news, feed 모두 동시 작동.
"""

import pytest
from unittest.mock import MagicMock, patch
import json
from datetime import datetime

from src.data.health_check import (
    DataFeedsHealthCheck,
    FeedStatus,
)


class TestDataFeedsIntegration:
    """모든 데이터 피드 통합 smoke test."""

    def test_all_feeds_concurrent_initialization(self):
        """모든 피드를 동시에 초기화하고 상태 확인."""
        checker = DataFeedsHealthCheck()
        
        # 1. REST DataFeed (OHLCV)
        rest_feed = MagicMock()
        rest_feed.fetch = MagicMock(return_value={"BTC/USDT": MagicMock()})
        rest_feed._cache = {"BTC/USDT": []}
        checker.register_feed("binance_rest_ohlcv", rest_feed, feed_type="rest")
        
        # 2. SentimentFetcher 시뮬레이션
        sentiment_feed = MagicMock()
        sentiment_feed.fetch = MagicMock(return_value={
            "fear_greed_index": 65,
            "funding_rate": 0.0003,
            "sentiment_score": 1.5,
        })
        checker.register_feed("sentiment_fg", sentiment_feed, feed_type="rest")
        
        # 3. OnchainFetcher 시뮬레이션
        onchain_feed = MagicMock()
        onchain_feed.fetch = MagicMock(return_value={
            "exchange_flow": "NEUTRAL",
            "whale_activity": "NEUTRAL",
            "nvt_signal": "FAIR",
            "onchain_score": 0.5,
        })
        checker.register_feed("onchain_metrics", onchain_feed, feed_type="rest")
        
        # 4. NewsMonitor 시뮬레이션
        news_feed = MagicMock()
        news_feed.fetch = MagicMock(return_value={
            "risk_level": "NONE",
            "recent_events": [],
        })
        checker.register_feed("news_monitor", news_feed, feed_type="rest")
        
        # 모든 피드 상태 확인
        result = checker.check_all()
        
        # Assertions
        assert result.is_healthy() is True
        assert result.live_count == 4, f"Expected 4 live feeds, got {result.live_count}"
        assert result.total_feeds == 4
        assert result.disconnected_count == 0
        assert "binance_rest_ohlcv" in result.feeds
        assert "sentiment_fg" in result.feeds
        assert "onchain_metrics" in result.feeds
        assert "news_monitor" in result.feeds
        
        # 모든 피드가 LIVE 상태
        for name, report in result.feeds.items():
            assert report.status == FeedStatus.LIVE, f"{name} status: {report.status}"
            assert report.is_available is True

    def test_mixed_feed_states(self):
        """일부 피드는 LIVE, 일부는 FALLBACK 상태."""
        checker = DataFeedsHealthCheck()
        
        # LIVE: REST DataFeed
        rest_feed = MagicMock()
        rest_feed.fetch = MagicMock()
        rest_feed._cache = {}
        checker.register_feed("rest_primary", rest_feed, feed_type="rest")
        
        # FALLBACK: WebSocket adapter (REST fallback 사용)
        mock_ws = MagicMock()
        mock_ws.is_connected = False
        mock_rest = MagicMock()
        mock_adapter = MagicMock()
        mock_adapter._ws = mock_ws
        mock_adapter._rest = mock_rest
        checker.register_feed("ws_adapter_fallback", mock_adapter, feed_type="adapter")
        
        # LIVE: Sentiment (REST)
        sentiment_feed = MagicMock()
        sentiment_feed.fetch = MagicMock()
        sentiment_feed._cache = {}
        checker.register_feed("sentiment", sentiment_feed, feed_type="rest")
        
        # LIVE: Onchain (REST)
        onchain_feed = MagicMock()
        onchain_feed.fetch = MagicMock()
        onchain_feed._cache = {}
        checker.register_feed("onchain", onchain_feed, feed_type="rest")
        
        result = checker.check_all()
        
        # Overall healthy (최소 1개 LIVE)
        assert result.is_healthy() is True
        assert result.live_count == 3
        assert result.fallback_count == 1
        assert result.total_feeds == 4
        assert "operating_in_degraded_mode" in result.anomalies

    def test_feed_data_consistency(self):
        """각 피드에서 반환된 데이터 구조 일관성."""
        checker = DataFeedsHealthCheck()
        
        # 각 피드 등록
        feeds = {
            "rest_ohlcv": MagicMock(fetch=MagicMock()),
            "sentiment": MagicMock(fetch=MagicMock()),
            "onchain": MagicMock(fetch=MagicMock()),
            "news": MagicMock(fetch=MagicMock()),
        }
        
        for feed_name, feed_obj in feeds.items():
            feed_obj._cache = {}
            checker.register_feed(feed_name, feed_obj, feed_type="rest")
        
        result = checker.check_all()
        
        # 모든 피드 리포트의 필드 검증
        for name, report in result.feeds.items():
            assert hasattr(report, "name")
            assert hasattr(report, "status")
            assert hasattr(report, "is_available")
            assert hasattr(report, "latency_ms")
            assert hasattr(report, "last_update")
            assert hasattr(report, "metadata")
            assert isinstance(report.metadata, dict)

    def test_feed_error_handling(self):
        """피드 오류 발생 시 처리."""
        checker = DataFeedsHealthCheck()
        
        # Error: 속성 누락 피드
        broken_feed = MagicMock(spec=[])  # fetch 메서드 없음
        checker.register_feed("broken", broken_feed, feed_type="rest")
        
        # LIVE: 정상 피드
        good_feed = MagicMock()
        good_feed.fetch = MagicMock()
        good_feed._cache = {}
        checker.register_feed("good", good_feed, feed_type="rest")
        
        result = checker.check_all()
        
        # broken 피드는 UNKNOWN 또는 ERROR
        broken_report = result.feeds["broken"]
        assert broken_report.status in [FeedStatus.UNKNOWN, FeedStatus.ERROR]
        assert broken_report.is_available is False
        
        # good 피드는 LIVE
        good_report = result.feeds["good"]
        assert good_report.status == FeedStatus.LIVE
        
        # 하나라도 LIVE 있으면 healthy
        assert result.is_healthy() is True

    def test_feed_primary_selection(self):
        """첫 번째 LIVE 피드를 primary로 선정."""
        checker = DataFeedsHealthCheck()
        
        # 피드 순서: sentiment -> onchain -> rest
        # 첫 번째 LIVE를 primary로 선택
        
        sentiment = MagicMock()
        sentiment.fetch = MagicMock()
        sentiment._cache = {}
        checker.register_feed("sentiment", sentiment, feed_type="rest")
        
        onchain = MagicMock()
        onchain.fetch = MagicMock()
        onchain._cache = {}
        checker.register_feed("onchain", onchain, feed_type="rest")
        
        rest = MagicMock()
        rest.fetch = MagicMock()
        rest._cache = {}
        checker.register_feed("rest", rest, feed_type="rest")
        
        result = checker.check_all()
        
        # primary는 첫 번째 LIVE (sentiment)
        assert result.primary_feed == "sentiment"
        assert result.live_count == 3

    def test_concurrent_feed_anomaly_detection(self):
        """여러 피드의 이상 상태 감지."""
        checker = DataFeedsHealthCheck()
        
        # 모든 피드가 DISCONNECTED
        ws_feed = MagicMock()
        ws_feed.is_connected = False
        ws_feed.candle_count = MagicMock(return_value=0)
        ws_feed._retry_count = 5
        ws_feed.MAX_RETRY = 5
        checker.register_feed("websocket", ws_feed, feed_type="websocket")
        
        result = checker.check_all()
        
        # 이상 감지
        assert result.is_healthy() is False
        assert result.live_count == 0
        assert result.disconnected_count == 1
        assert "all_feeds_disconnected" in result.anomalies

    def test_feed_summary_report(self):
        """모든 피드 상태의 요약 리포트."""
        checker = DataFeedsHealthCheck()
        
        # 4개의 데이터 소스
        feeds_data = [
            ("rest_ohlcv", "rest", True),
            ("ws_adapter", "adapter", True),
            ("sentiment", "rest", True),
            ("onchain", "rest", True),
        ]
        
        for feed_name, feed_type, make_mock in feeds_data:
            mock_feed = MagicMock()
            if feed_type == "rest":
                mock_feed.fetch = MagicMock()
                mock_feed._cache = {}
            elif feed_type == "adapter":
                mock_ws = MagicMock()
                mock_ws.is_connected = True
                mock_feed._ws = mock_ws
                mock_feed._rest = None
            
            checker.register_feed(feed_name, mock_feed, feed_type=feed_type)
        
        result = checker.check_all()
        
        # 요약 리포트 생성
        summary = repr(result)
        
        assert "4 live" in summary or "live" in summary
        assert "DISCONNECTED" not in summary or "0 disconnected" in summary
        
        # 각 피드 리포트 접근 가능
        assert len(result.feeds) == 4
        for name in ["rest_ohlcv", "ws_adapter", "sentiment", "onchain"]:
            assert name in result.feeds
            assert result.feeds[name].status == FeedStatus.LIVE


# 병렬 호출 시뮬레이션
class TestParallelFetchSimulation:
    """여러 피드를 병렬로 fetch하는 시뮬레이션."""

    def test_parallel_sentiment_and_onchain(self):
        """sentiment + onchain 병렬 fetch."""
        # 실제 호출은 안 하고, 병렬 구조만 테스트
        sentiment_result = {"fear_greed": 65, "score": 1.5}
        onchain_result = {"flow": "NEUTRAL", "score": 0.5}
        
        # 두 결과를 동시에 처리
        checker = DataFeedsHealthCheck()
        
        sentiment = MagicMock()
        sentiment.data = sentiment_result
        sentiment.fetch = MagicMock(return_value=sentiment_result)
        
        onchain = MagicMock()
        onchain.data = onchain_result
        onchain.fetch = MagicMock(return_value=onchain_result)
        
        checker.register_feed("sentiment", sentiment, feed_type="rest")
        checker.register_feed("onchain", onchain, feed_type="rest")
        
        result = checker.check_all()
        
        assert result.is_healthy() is True
        assert result.live_count == 2

    def test_four_feeds_integration(self):
        """4개 피드 모두 한 번에 초기화."""
        checker = DataFeedsHealthCheck()
        
        feeds = {
            "rest_ohlcv": ("rest", True),
            "sentiment_fg": ("rest", True),
            "onchain_metrics": ("rest", True),
            "news_monitor": ("rest", True),
        }
        
        for feed_name, (feed_type, _) in feeds.items():
            feed = MagicMock()
            feed.fetch = MagicMock()
            feed._cache = {}
            checker.register_feed(feed_name, feed, feed_type=feed_type)
        
        result = checker.check_all()
        
        assert result.total_feeds == 4
        assert result.live_count == 4
        assert result.is_healthy() is True
        assert len(result.feeds) == 4
