"""
I2. DrawdownMonitor — 실시간 MDD 추적 + 긴급 정지.

Peak equity를 추적하며, 현재 손실이 max_drawdown_pct 초과 시
circuit_breaker 패턴으로 거래 차단.

사용:
    monitor = DrawdownMonitor(max_drawdown_pct=0.15)  # 15% MDD
    monitor.update(current_equity=9500)
    if monitor.is_halted():
        # 거래 중단
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class DrawdownStatus:
    current_equity: float
    peak_equity: float
    drawdown_pct: float     # 현재 낙폭 (양수, 0~1)
    max_drawdown_pct: float # 최대 허용 낙폭
    halted: bool
    reason: str


class DrawdownMonitor:
    """실시간 MDD 추적 및 긴급 정지 모듈."""

    def __init__(
        self,
        max_drawdown_pct: float = 0.15,
        recovery_pct: float = 0.05,
    ) -> None:
        """
        Args:
            max_drawdown_pct: MDD 한계 (e.g. 0.15 = 15%). 초과 시 거래 차단.
            recovery_pct: 차단 해제 기준 (낙폭이 max - recovery 이하로 회복 시 재개).
        """
        self.max_drawdown_pct = max_drawdown_pct
        self.recovery_pct = recovery_pct

        self._peak: Optional[float] = None
        self._current: float = 0.0
        self._halted: bool = False
        self._halt_reason: str = ""

    def update(self, current_equity: float) -> DrawdownStatus:
        """현재 자본금으로 상태 업데이트. DrawdownStatus 반환."""
        self._current = current_equity

        if self._peak is None or current_equity > self._peak:
            self._peak = current_equity

        drawdown = (self._peak - current_equity) / self._peak if self._peak > 0 else 0.0

        # 거래 차단 체크
        if not self._halted and drawdown >= self.max_drawdown_pct:
            self._halted = True
            self._halt_reason = (
                f"MDD {drawdown:.1%} ≥ 한계 {self.max_drawdown_pct:.1%} "
                f"(peak={self._peak:.2f}, current={current_equity:.2f})"
            )
            logger.warning("DrawdownMonitor: HALTED — %s", self._halt_reason)

        # 차단 해제 체크 (peak 기준 recovery_pct 내로 회복)
        elif self._halted and drawdown < (self.max_drawdown_pct - self.recovery_pct):
            self._halted = False
            self._halt_reason = ""
            logger.info(
                "DrawdownMonitor: RESUMED — drawdown=%.1%% peak=%.2f",
                drawdown, self._peak,
            )

        return DrawdownStatus(
            current_equity=current_equity,
            peak_equity=self._peak,
            drawdown_pct=drawdown,
            max_drawdown_pct=self.max_drawdown_pct,
            halted=self._halted,
            reason=self._halt_reason,
        )

    def is_halted(self) -> bool:
        return self._halted

    def current_drawdown(self) -> float:
        """현재 낙폭 비율 (0~1)."""
        if self._peak is None or self._peak <= 0:
            return 0.0
        return max(0.0, (self._peak - self._current) / self._peak)

    def reset(self) -> None:
        """상태 초기화 (새 거래 세션 시작 시)."""
        self._peak = None
        self._current = 0.0
        self._halted = False
        self._halt_reason = ""
        logger.info("DrawdownMonitor: reset")

    def force_halt(self, reason: str = "Manual halt") -> None:
        """수동으로 거래 차단."""
        self._halted = True
        self._halt_reason = reason
        logger.warning("DrawdownMonitor: force halt — %s", reason)

    def force_resume(self) -> None:
        """수동으로 거래 재개."""
        self._halted = False
        self._halt_reason = ""
        logger.info("DrawdownMonitor: force resume")
