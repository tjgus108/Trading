"""
Data feeds health check aggregator.

각 데이터 소스(REST DataFeed, WebSocket, DEX, liquidation 등)의 상태를 수집하고
어느 피드가 live인지, 어느 피드가 fallback 중인지 종합 보고.

data-agent가 사용.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class FeedStatus(str, Enum):
    """피드 상태."""
    LIVE = "LIVE"           # 정상 작동
    FALLBACK = "FALLBACK"   # fallback 모드 (성능 저하)
    DISCONNECTED = "DISCONNECTED"  # 연결 끊김
    ERROR = "ERROR"         # 오류 발생
    UNKNOWN = "UNKNOWN"     # 상태 미확인


@dataclass
class FeedHealthReport:
    """단일 피드 상태 레포트."""
    name: str              # e.g., "binance_rest", "binance_websocket"
    status: FeedStatus
    is_available: bool     # 사용 가능 여부
    latency_ms: float = 0.0
    last_update: Optional[str] = None
    error_msg: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        status_str = f"{self.status.value}"
        if not self.is_available:
            status_str += " (unavailable)"
        return (
            f"<{self.name}: {status_str}, "
            f"latency={self.latency_ms:.1f}ms, "
            f"last_update={self.last_update}>"
        )


@dataclass
class DataHealthCheck:
    """전체 데이터 피드 상태 종합 보고."""
    feeds: Dict[str, FeedHealthReport]
    live_count: int = 0
    fallback_count: int = 0
    disconnected_count: int = 0
    total_feeds: int = 0
    primary_feed: Optional[str] = None  # 현재 활성화된 주 피드
    anomalies: list = field(default_factory=list)

    def is_healthy(self) -> bool:
        """최소 1개 이상의 live 피드 있으면 healthy."""
        return self.live_count > 0

    def __repr__(self) -> str:
        summary = (
            f"DataHealthCheck: {self.live_count} live, "
            f"{self.fallback_count} fallback, "
            f"{self.disconnected_count} disconnected "
            f"(total={self.total_feeds})"
        )
        if self.primary_feed:
            summary += f", primary={self.primary_feed}"
        if self.anomalies:
            summary += f", {len(self.anomalies)} anomalies"
        return summary


    def to_dict(self) -> Dict[str, Any]:
        """상태 정보를 딕셔너리로 변환."""
        return {
            "live_count": self.live_count,
            "fallback_count": self.fallback_count,
            "disconnected_count": self.disconnected_count,
            "total_feeds": self.total_feeds,
            "primary_feed": self.primary_feed,
            "is_healthy": self.is_healthy(),
            "anomalies": self.anomalies,
            "feeds": {
                name: {
                    "status": report.status.value,
                    "is_available": report.is_available,
                    "latency_ms": report.latency_ms,
                    "last_update": report.last_update,
                    "error_msg": report.error_msg,
                    "metadata": report.metadata,
                }
                for name, report in self.feeds.items()
            },
        }

    def to_json(self) -> str:
        """상태 정보를 JSON 문자열로 변환."""
        import json
        return json.dumps(self.to_dict(), indent=2)

class DataFeedsHealthCheck:
    """
    Data feeds 상태 수집 및 종합.

    사용:
      health_checker = DataFeedsHealthCheck()
      health_checker.register_feed("binance_rest", feed_obj)
      health_checker.register_feed("binance_ws", ws_feed_obj)
      report = health_checker.check_all()
      print(report)
    """

    def __init__(self):
        self._feeds: Dict[str, Any] = {}
        self._feed_types: Dict[str, str] = {}  # name → feed type

    def register_feed(self, name: str, feed_obj: Any, feed_type: str = "unknown") -> None:
        """피드 등록."""
        self._feeds[name] = feed_obj
        self._feed_types[name] = feed_type
        logger.info("Registered feed: %s (type=%s)", name, feed_type)

    def check_all(self) -> DataHealthCheck:
        """모든 등록된 피드 상태 확인."""
        reports = {}
        live_count = 0
        fallback_count = 0
        disconnected_count = 0

        for name, feed_obj in self._feeds.items():
            feed_type = self._feed_types.get(name, "unknown")
            report = self._check_single(name, feed_obj, feed_type)
            reports[name] = report

            if report.status == FeedStatus.LIVE:
                live_count += 1
            elif report.status == FeedStatus.FALLBACK:
                fallback_count += 1
            elif report.status == FeedStatus.DISCONNECTED:
                disconnected_count += 1

        # 주 피드 결정: 첫 번째 LIVE 피드
        primary_feed = None
        for name, report in reports.items():
            if report.status == FeedStatus.LIVE:
                primary_feed = name
                break

        result = DataHealthCheck(
            feeds=reports,
            live_count=live_count,
            fallback_count=fallback_count,
            disconnected_count=disconnected_count,
            total_feeds=len(self._feeds),
            primary_feed=primary_feed,
        )

        # 이상 감지
        anomalies = []
        if live_count == 0 and disconnected_count > 0:
            anomalies.append("all_feeds_disconnected")
        if fallback_count > 0:
            anomalies.append("operating_in_degraded_mode")

        result.anomalies = anomalies
        logger.info(result)
        return result

    def _check_single(self, name: str, feed_obj: Any, feed_type: str) -> FeedHealthReport:
        """단일 피드 상태 확인."""
        try:
            # feed_type이 명시적으로 지정되면 우선 사용 (테스트 및 타입 안정성)
            if feed_type == "adapter":
                return self._check_ws_adapter(name, feed_obj)
            elif feed_type == "websocket":
                return self._check_websocket_feed(name, feed_obj)
            elif feed_type == "rest":
                return self._check_rest_feed(name, feed_obj)
            elif feed_type == "dex":
                return self._check_dex_feed(name, feed_obj)
            
            # feed_type이 "unknown"이면 hasattr 기반 자동 감지
            if hasattr(feed_obj, "_ws"):
                return self._check_ws_adapter(name, feed_obj)
            if hasattr(feed_obj, "is_connected"):
                return self._check_websocket_feed(name, feed_obj)
            if hasattr(feed_obj, "fetch"):
                return self._check_rest_feed(name, feed_obj)
            if hasattr(feed_obj, "get_price"):
                return self._check_dex_feed(name, feed_obj)

            # 알려지지 않은 유형
            return FeedHealthReport(
                name=name,
                status=FeedStatus.UNKNOWN,
                is_available=False,
                error_msg="unknown feed type",
            )

        except Exception as e:
            logger.error("Error checking feed %s: %s", name, e)
            return FeedHealthReport(
                name=name,
                status=FeedStatus.ERROR,
                is_available=False,
                error_msg=str(e),
            )

    def _check_rest_feed(self, name: str, feed_obj: Any) -> FeedHealthReport:
        """DataFeed (REST) 상태 확인."""
        try:
            # fetch 메서드 존재 확인
            if not hasattr(feed_obj, "fetch"):
                return FeedHealthReport(
                    name=name,
                    status=FeedStatus.UNKNOWN,
                    is_available=False,
                    error_msg="no fetch method",
                )

            # 캐시 상태 확인 (선택)
            cache_size = len(getattr(feed_obj, "_cache", {}))
            metadata = {"cache_size": cache_size}

            return FeedHealthReport(
                name=name,
                status=FeedStatus.LIVE,
                is_available=True,
                latency_ms=0.0,
                last_update="ready",
                metadata=metadata,
            )
        except Exception as e:
            return FeedHealthReport(
                name=name,
                status=FeedStatus.ERROR,
                is_available=False,
                error_msg=str(e),
            )

    def _check_websocket_feed(self, name: str, feed_obj: Any) -> FeedHealthReport:
        """BinanceWebSocketFeed 상태 확인."""
        try:
            is_connected = getattr(feed_obj, "is_connected", False)
            candle_count = getattr(feed_obj, "candle_count", lambda: 0)()
            retry_count = getattr(feed_obj, "_retry_count", 0)
            max_retry = getattr(feed_obj, "MAX_RETRY", 5)

            if is_connected:
                status = FeedStatus.LIVE
                is_avail = True
            elif retry_count >= max_retry:
                # 최대 재시도 초과 → DISCONNECTED
                status = FeedStatus.DISCONNECTED
                is_avail = False
            elif candle_count > 0 and retry_count < max_retry:
                # 연결 끊겼지만 캔들 있고 재시도 중
                status = FeedStatus.FALLBACK
                is_avail = True
            else:
                # 연결 시도 중
                status = FeedStatus.FALLBACK
                is_avail = True

            metadata = {
                "candle_count": candle_count,
                "retry_count": retry_count,
                "max_retry": max_retry,
            }

            return FeedHealthReport(
                name=name,
                status=status,
                is_available=is_avail,
                latency_ms=0.0,
                last_update=f"{candle_count} candles buffered",
                metadata=metadata,
            )
        except Exception as e:
            return FeedHealthReport(
                name=name,
                status=FeedStatus.ERROR,
                is_available=False,
                error_msg=str(e),
            )

    def _check_ws_adapter(self, name: str, feed_obj: Any) -> FeedHealthReport:
        """WebSocketDataAdapter 상태 확인."""
        try:
            ws = getattr(feed_obj, "_ws", None)
            rest = getattr(feed_obj, "_rest", None)

            if ws and getattr(ws, "is_connected", False):
                return FeedHealthReport(
                    name=name,
                    status=FeedStatus.LIVE,
                    is_available=True,
                    last_update="websocket active",
                    metadata={"source": "websocket"},
                )
            elif rest:
                # REST fallback 있음
                return FeedHealthReport(
                    name=name,
                    status=FeedStatus.FALLBACK,
                    is_available=True,
                    last_update="fallback to REST",
                    metadata={"source": "rest_fallback"},
                )
            else:
                return FeedHealthReport(
                    name=name,
                    status=FeedStatus.DISCONNECTED,
                    is_available=False,
                    error_msg="no websocket or rest fallback",
                )
        except Exception as e:
            return FeedHealthReport(
                name=name,
                status=FeedStatus.ERROR,
                is_available=False,
                error_msg=str(e),
            )

    def _check_dex_feed(self, name: str, feed_obj: Any) -> FeedHealthReport:
        """DEXPriceFeed 상태 확인."""
        try:
            # get_price 메서드 존재 확인
            if not hasattr(feed_obj, "get_price"):
                return FeedHealthReport(
                    name=name,
                    status=FeedStatus.UNKNOWN,
                    is_available=False,
                    error_msg="no get_price method",
                )

            # mock 피드는 항상 live
            is_mock = getattr(feed_obj, "_is_mock", False)
            status = FeedStatus.LIVE if is_mock else FeedStatus.LIVE

            return FeedHealthReport(
                name=name,
                status=status,
                is_available=True,
                last_update="price feed ready",
                metadata={"is_mock": is_mock},
            )
        except Exception as e:
            return FeedHealthReport(
                name=name,
                status=FeedStatus.ERROR,
                is_available=False,
                error_msg=str(e),
            )
