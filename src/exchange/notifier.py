"""
알림 모듈 스켈레톤: 3계층 알림 구조.

계층:
  CRITICAL — 즉시 전송 (손실 한계, 보호 모드, 시스템 장애)
  SILENT   — 요약 배치로 전송 (일일 리포트, 성과 변동)
  SUPPRESS — 기록만 하고 전송 안 함 (디버그, 데이터 갱신)

현재: 인터페이스만 정의. 실제 Telegram API 연동은 미구현.
"""
from __future__ import annotations

import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    CRITICAL = "CRITICAL"  # 즉시 전송
    SILENT = "SILENT"      # 배치 요약
    SUPPRESS = "SUPPRESS"  # 전송 안 함 (로그만)


class Notifier:
    """
    알림 인터페이스.

    사용법:
        notifier = Notifier()
        notifier.send("MAX LOSS REACHED", AlertLevel.CRITICAL)
        notifier.send("Daily report generated", AlertLevel.SILENT)
        notifier.send("Data refreshed", AlertLevel.SUPPRESS)
    """

    def __init__(self, enabled: bool = False):
        self._enabled = enabled
        self._pending_silent: list[str] = []

    def send(self, message: str, level: AlertLevel = AlertLevel.SILENT) -> bool:
        """
        알림 전송.

        Args:
            message: 알림 메시지
            level: 알림 계층

        Returns:
            True if delivered (or queued), False if suppressed/disabled.
        """
        if level == AlertLevel.SUPPRESS:
            logger.debug("[NOTIFIER:SUPPRESS] %s", message)
            return False

        if level == AlertLevel.CRITICAL:
            logger.warning("[NOTIFIER:CRITICAL] %s", message)
            if self._enabled:
                return self._deliver(message)
            return False

        # SILENT — 배치 큐에 추가
        self._pending_silent.append(message)
        logger.debug("[NOTIFIER:SILENT] queued (%d pending)", len(self._pending_silent))
        return True

    def flush_silent(self) -> bool:
        """SILENT 큐 배치 전송 (일일 리포트 시점에 호출)."""
        if not self._pending_silent:
            return False
        summary = "\n".join(f"- {m}" for m in self._pending_silent)
        logger.info("[NOTIFIER:FLUSH] %d silent messages", len(self._pending_silent))
        self._pending_silent.clear()
        if self._enabled:
            return self._deliver(f"[Daily Summary]\n{summary}")
        return False

    def _deliver(self, text: str) -> bool:
        """
        실제 전송 (Telegram API).
        현재는 스텁 — 실제 구현 시 여기에 연동.
        """
        # TODO: Telegram Bot API 연동
        # import requests
        # url = f"https://api.telegram.org/bot{token}/sendMessage"
        # resp = requests.post(url, json={"chat_id": chat_id, "text": text})
        # return resp.ok
        logger.info("[NOTIFIER:DELIVER] (stub) %s", text[:100])
        return False

    @property
    def pending_count(self) -> int:
        return len(self._pending_silent)
