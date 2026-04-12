"""
I2. DrawdownMonitor — 실시간 MDD 추적 + 긴급 정지.

Peak equity를 추적하며, 현재 손실이 max_drawdown_pct 초과 시
circuit_breaker 패턴으로 거래 차단.

3층 서킷브레이커:
  - 일일 DD > daily_limit  → WARNING (거래 중단)
  - 주간 DD > weekly_limit → HALT (거래 중단)
  - 월간 DD > monthly_limit → FORCE_LIQUIDATE (강제 청산)

사용:
    monitor = DrawdownMonitor(max_drawdown_pct=0.15)  # 15% MDD
    monitor.update(current_equity=9500)
    if monitor.is_halted():
        # 거래 중단
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    NONE = "NONE"
    WARNING = "WARNING"       # 일일 DD 초과 — 경고
    HALT = "HALT"             # 주간 DD 초과 — 거래 중단
    FORCE_LIQUIDATE = "FORCE_LIQUIDATE"  # 월간 DD 초과 — 강제 청산


@dataclass
class DrawdownStatus:
    current_equity: float
    peak_equity: float
    drawdown_pct: float       # 현재 낙폭 (양수, 0~1)
    max_drawdown_pct: float   # 최대 허용 낙폭
    halted: bool
    reason: str
    alert_level: AlertLevel = AlertLevel.NONE
    daily_drawdown_pct: float = 0.0
    weekly_drawdown_pct: float = 0.0
    monthly_drawdown_pct: float = 0.0


class DrawdownMonitor:
    """실시간 MDD 추적 및 긴급 정지 모듈.

    3층 서킷브레이커:
      daily_limit  (기본 0.03): 일일 DD 초과 → WARNING + 거래 중단
      weekly_limit (기본 0.07): 주간 DD 초과 → HALT + 거래 중단
      monthly_limit(기본 0.15): 월간 DD 초과 → FORCE_LIQUIDATE
    """

    def __init__(
        self,
        max_drawdown_pct: float = 0.15,
        recovery_pct: float = 0.05,
        daily_limit: float = 0.03,
        weekly_limit: float = 0.07,
        monthly_limit: float = 0.15,
    ) -> None:
        """
        Args:
            max_drawdown_pct: 전체 MDD 한계 (legacy). 초과 시 거래 차단.
            recovery_pct: 차단 해제 기준 (낙폭이 max - recovery 이하로 회복 시 재개).
            daily_limit:   일일 낙폭 한계 (기본 3%).
            weekly_limit:  주간 낙폭 한계 (기본 7%).
            monthly_limit: 월간 낙폭 한계 (기본 15%).
        """
        self.max_drawdown_pct = max_drawdown_pct
        self.recovery_pct = recovery_pct
        self.daily_limit = daily_limit
        self.weekly_limit = weekly_limit
        self.monthly_limit = monthly_limit

        self._peak: Optional[float] = None
        self._current: float = 0.0
        self._halted: bool = False
        self._halt_reason: str = ""
        self._alert_level: AlertLevel = AlertLevel.NONE

        # 3층 서킷브레이커용 기준 잔고
        self._daily_start: Optional[float] = None
        self._weekly_start: Optional[float] = None
        self._monthly_start: Optional[float] = None

    # ── 기준 잔고 설정 ─────────────────────────────────────────

    def set_daily_start(self, equity: float) -> None:
        """일일 기준 잔고 설정 (매일 자정 호출)."""
        self._daily_start = equity
        logger.info("DrawdownMonitor: daily_start=%.2f", equity)

    def set_weekly_start(self, equity: float) -> None:
        """주간 기준 잔고 설정 (매주 월요일 호출)."""
        self._weekly_start = equity
        logger.info("DrawdownMonitor: weekly_start=%.2f", equity)

    def set_monthly_start(self, equity: float) -> None:
        """월간 기준 잔고 설정 (매월 1일 호출)."""
        self._monthly_start = equity
        logger.info("DrawdownMonitor: monthly_start=%.2f", equity)

    # ── 낙폭 계산 헬퍼 ────────────────────────────────────────

    def _dd(self, start: Optional[float], current: float) -> float:
        if start is None or start <= 0:
            return 0.0
        return max(0.0, (start - current) / start)

    # ── 메인 업데이트 ──────────────────────────────────────────

    def update(self, current_equity: float) -> DrawdownStatus:
        """현재 자본금으로 상태 업데이트. DrawdownStatus 반환."""
        self._current = current_equity

        if self._peak is None or current_equity > self._peak:
            self._peak = current_equity

        drawdown = (self._peak - current_equity) / self._peak if self._peak > 0 else 0.0

        # 3층 낙폭 계산
        daily_dd = self._dd(self._daily_start, current_equity)
        weekly_dd = self._dd(self._weekly_start, current_equity)
        monthly_dd = self._dd(self._monthly_start, current_equity)

        # 3층 서킷브레이커 체크 (우선순위: 월간 > 주간 > 일일)
        new_level, new_reason = self._check_tiered(
            daily_dd, weekly_dd, monthly_dd, drawdown
        )

        if new_level != AlertLevel.NONE and not self._halted:
            self._halted = True
            self._alert_level = new_level
            self._halt_reason = new_reason
            logger.warning("DrawdownMonitor: HALTED [%s] — %s", new_level.value, new_reason)

        # legacy MDD 체크 (기준 잔고 미설정 시 폴백)
        elif not self._halted and drawdown >= self.max_drawdown_pct:
            self._halted = True
            self._alert_level = AlertLevel.HALT
            self._halt_reason = (
                f"MDD {drawdown:.1%} ≥ 한계 {self.max_drawdown_pct:.1%} "
                f"(peak={self._peak:.2f}, current={current_equity:.2f})"
            )
            logger.warning("DrawdownMonitor: HALTED — %s", self._halt_reason)

        # 차단 해제 체크 (FORCE_LIQUIDATE는 수동 해제만)
        elif self._halted and self._alert_level != AlertLevel.FORCE_LIQUIDATE:
            if drawdown < (self.max_drawdown_pct - self.recovery_pct):
                self._halted = False
                self._alert_level = AlertLevel.NONE
                self._halt_reason = ""
                logger.info(
                    "DrawdownMonitor: RESUMED — drawdown=%.2f%% peak=%.2f",
                    drawdown * 100, self._peak,
                )

        return DrawdownStatus(
            current_equity=current_equity,
            peak_equity=self._peak,
            drawdown_pct=drawdown,
            max_drawdown_pct=self.max_drawdown_pct,
            halted=self._halted,
            reason=self._halt_reason,
            alert_level=self._alert_level,
            daily_drawdown_pct=daily_dd,
            weekly_drawdown_pct=weekly_dd,
            monthly_drawdown_pct=monthly_dd,
        )

    def _check_tiered(
        self,
        daily_dd: float,
        weekly_dd: float,
        monthly_dd: float,
        total_dd: float,
    ) -> tuple[AlertLevel, str]:
        """3층 서킷브레이커 체크. 가장 심각한 레벨 반환."""
        if monthly_dd >= self.monthly_limit:
            return (
                AlertLevel.FORCE_LIQUIDATE,
                f"월간 낙폭 {monthly_dd:.1%} ≥ 한계 {self.monthly_limit:.1%} — 강제 청산",
            )
        if weekly_dd >= self.weekly_limit:
            return (
                AlertLevel.HALT,
                f"주간 낙폭 {weekly_dd:.1%} ≥ 한계 {self.weekly_limit:.1%} — 거래 중단",
            )
        if daily_dd >= self.daily_limit:
            return (
                AlertLevel.WARNING,
                f"일일 낙폭 {daily_dd:.1%} ≥ 한계 {self.daily_limit:.1%} — 경고",
            )
        return AlertLevel.NONE, ""

    # ── 상태 조회 ──────────────────────────────────────────────

    def is_halted(self) -> bool:
        return self._halted

    def alert_level(self) -> AlertLevel:
        return self._alert_level

    def current_drawdown(self) -> float:
        """현재 낙폭 비율 (0~1)."""
        if self._peak is None or self._peak <= 0:
            return 0.0
        return max(0.0, (self._peak - self._current) / self._peak)

    # ── 리셋 ──────────────────────────────────────────────────

    def reset(self) -> None:
        """상태 초기화 (새 거래 세션 시작 시)."""
        self._peak = None
        self._current = 0.0
        self._halted = False
        self._halt_reason = ""
        self._alert_level = AlertLevel.NONE
        self._daily_start = None
        self._weekly_start = None
        self._monthly_start = None
        logger.info("DrawdownMonitor: reset")

    def reset_daily(self, equity: float) -> None:
        """일일 기준 잔고 리셋. WARNING 레벨 해제."""
        self._daily_start = equity
        if self._halted and self._alert_level == AlertLevel.WARNING:
            self._halted = False
            self._alert_level = AlertLevel.NONE
            self._halt_reason = ""
            logger.info("DrawdownMonitor: daily reset — WARNING cleared")

    # ── 수동 제어 ──────────────────────────────────────────────

    def force_halt(self, reason: str = "Manual halt") -> None:
        """수동으로 거래 차단."""
        self._halted = True
        self._halt_reason = reason
        logger.warning("DrawdownMonitor: force halt — %s", reason)

    def force_resume(self) -> None:
        """수동으로 거래 재개 (FORCE_LIQUIDATE 포함 해제)."""
        self._halted = False
        self._alert_level = AlertLevel.NONE
        self._halt_reason = ""
        logger.info("DrawdownMonitor: force resume")

    # ── 직렬화 ────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """런타임 상태를 dict로 직렬화 (재시작 복원용)."""
        return {
            "max_drawdown_pct": self.max_drawdown_pct,
            "recovery_pct": self.recovery_pct,
            "daily_limit": self.daily_limit,
            "weekly_limit": self.weekly_limit,
            "monthly_limit": self.monthly_limit,
            "_peak": self._peak,
            "_current": self._current,
            "_halted": self._halted,
            "_halt_reason": self._halt_reason,
            "_alert_level": self._alert_level.value,
            "_daily_start": self._daily_start,
            "_weekly_start": self._weekly_start,
            "_monthly_start": self._monthly_start,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DrawdownMonitor":
        """to_dict() 결과로 인스턴스 복원."""
        obj = cls(
            max_drawdown_pct=data["max_drawdown_pct"],
            recovery_pct=data["recovery_pct"],
            daily_limit=data["daily_limit"],
            weekly_limit=data["weekly_limit"],
            monthly_limit=data["monthly_limit"],
        )
        obj._peak = data["_peak"]
        obj._current = data["_current"]
        obj._halted = data["_halted"]
        obj._halt_reason = data["_halt_reason"]
        obj._alert_level = AlertLevel(data["_alert_level"])
        obj._daily_start = data["_daily_start"]
        obj._weekly_start = data["_weekly_start"]
        obj._monthly_start = data["_monthly_start"]
        return obj
