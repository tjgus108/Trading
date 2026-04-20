"""
Health Check 모듈: 거래소 연결 상태 모니터링 + 자동 복구.

기능:
- 주기적 liveness check (기본 5분 간격)
- 데이터 지연 감지 (마지막 데이터 수신 시각 기반)
- 연결 끊김 시 자동 재연결 (최대 3회)
- 실패 시 포지션 보호 모드 (신규 주문 차단, 기존 포지션 유지)
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """시스템 건강 상태."""
    HEALTHY = "HEALTHY"           # 정상
    DEGRADED = "DEGRADED"         # 지연 감지 (데이터 stale)
    DISCONNECTED = "DISCONNECTED" # 연결 끊김
    PROTECTED = "PROTECTED"       # 보호 모드 (재연결 실패)


@dataclass
class HealthState:
    """현재 건강 상태 스냅샷."""
    status: HealthStatus = HealthStatus.HEALTHY
    last_check_time: float = 0.0
    last_healthy_time: float = 0.0
    last_data_time: float = 0.0        # 마지막 데이터 수신 시각
    consecutive_failures: int = 0
    reconnect_attempts: int = 0
    total_checks: int = 0
    total_failures: int = 0
    protection_activated_at: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "last_check_time": self.last_check_time,
            "last_healthy_time": self.last_healthy_time,
            "last_data_time": self.last_data_time,
            "consecutive_failures": self.consecutive_failures,
            "reconnect_attempts": self.reconnect_attempts,
            "total_checks": self.total_checks,
            "total_failures": self.total_failures,
            "protection_activated_at": self.protection_activated_at,
        }


class HealthChecker:
    """
    거래소 연결 health check + 자동 복구 엔진.

    사용법:
        checker = HealthChecker(
            check_fn=lambda: exchange.health_check(),
            reconnect_fn=lambda: exchange.reconnect(),
        )

        # 매 tick에서 호출
        if checker.should_check():
            checker.run_check()

        # 신규 주문 전 차단 여부 확인
        if checker.is_order_blocked():
            logger.warning("Orders blocked — protection mode active")
    """

    def __init__(
        self,
        check_fn: Callable[[], dict],
        reconnect_fn: Optional[Callable[[], bool]] = None,
        check_interval: float = 300.0,      # 5분 (초)
        data_stale_threshold: float = 600.0, # 10분 이상 데이터 없으면 stale
        max_reconnect_attempts: int = 3,
    ):
        self._check_fn = check_fn
        self._reconnect_fn = reconnect_fn
        self.check_interval = check_interval
        self.data_stale_threshold = data_stale_threshold
        self.max_reconnect_attempts = max_reconnect_attempts
        self.state = HealthState()
        self.state.last_healthy_time = time.time()
        self.state.last_data_time = time.time()

    def should_check(self) -> bool:
        """check_interval 경과 시 True."""
        return (time.time() - self.state.last_check_time) >= self.check_interval

    def record_data_received(self) -> None:
        """데이터 수신 시 호출 — 데이터 지연 타이머 리셋."""
        self.state.last_data_time = time.time()

    def is_order_blocked(self) -> bool:
        """보호 모드일 때 True — 신규 주문 차단."""
        return self.state.status == HealthStatus.PROTECTED

    def is_healthy(self) -> bool:
        """HEALTHY 상태인지 확인."""
        return self.state.status == HealthStatus.HEALTHY

    def run_check(self) -> HealthState:
        """
        1회 health check 실행.
        - check_fn 호출 → connected 확인
        - 데이터 지연 감지
        - 실패 시 재연결 시도 (최대 max_reconnect_attempts)
        - 재연결 실패 시 보호 모드 진입
        """
        now = time.time()
        self.state.last_check_time = now
        self.state.total_checks += 1

        # 1. check_fn 호출
        try:
            result = self._check_fn()
            connected = result.get("connected", False)
        except Exception as exc:
            logger.warning("Health check function raised: %s", str(exc)[:100])
            connected = False

        # 2. 데이터 지연 체크
        data_age = now - self.state.last_data_time
        data_stale = data_age > self.data_stale_threshold

        # 3. 상태 결정
        if connected and not data_stale:
            # 정상
            self.state.status = HealthStatus.HEALTHY
            self.state.last_healthy_time = now
            self.state.consecutive_failures = 0
            self.state.reconnect_attempts = 0
            self.state.protection_activated_at = None
            logger.debug("Health check OK (data_age=%.0fs)", data_age)
            return self.state

        if connected and data_stale:
            # 연결은 OK이지만 데이터가 stale
            self.state.status = HealthStatus.DEGRADED
            self.state.consecutive_failures += 1
            self.state.total_failures += 1
            logger.warning(
                "Health check DEGRADED: data stale for %.0fs (threshold=%.0fs)",
                data_age, self.data_stale_threshold,
            )
            return self.state

        # 4. 연결 끊김 → 재연결 시도
        self.state.consecutive_failures += 1
        self.state.total_failures += 1
        self.state.status = HealthStatus.DISCONNECTED
        logger.warning(
            "Health check DISCONNECTED (consecutive=%d)",
            self.state.consecutive_failures,
        )

        if self._reconnect_fn is not None and \
           self.state.reconnect_attempts < self.max_reconnect_attempts:
            self.state.reconnect_attempts += 1
            logger.info(
                "Attempting reconnect (%d/%d)...",
                self.state.reconnect_attempts, self.max_reconnect_attempts,
            )
            try:
                success = self._reconnect_fn()
                if success:
                    self.state.status = HealthStatus.HEALTHY
                    self.state.last_healthy_time = time.time()
                    self.state.consecutive_failures = 0
                    self.state.reconnect_attempts = 0
                    logger.info("Reconnect succeeded")
                    return self.state
                else:
                    logger.warning("Reconnect returned False")
            except Exception as exc:
                logger.error("Reconnect failed: %s", str(exc)[:100])

        # 5. 재연결 실패 → 보호 모드
        if self.state.reconnect_attempts >= self.max_reconnect_attempts:
            self.state.status = HealthStatus.PROTECTED
            if self.state.protection_activated_at is None:
                self.state.protection_activated_at = now
            logger.critical(
                "PROTECTION MODE: %d reconnect attempts exhausted. "
                "New orders BLOCKED. Existing positions PRESERVED.",
                self.max_reconnect_attempts,
            )

        return self.state

    def reset(self) -> None:
        """수동으로 보호 모드 해제 (재시작 시)."""
        self.state = HealthState()
        self.state.last_healthy_time = time.time()
        self.state.last_data_time = time.time()
        logger.info("HealthChecker reset — all states cleared")

    def summary(self) -> dict:
        """현재 상태 요약."""
        return self.state.to_dict()
