"""
I2. DrawdownMonitor — 실시간 MDD 추적 + 긴급 정지.

Peak equity를 추적하며, 현재 손실이 max_drawdown_pct 초과 시
circuit_breaker 패턴으로 거래 차단.

3층 서킷브레이커:
  - 일일 DD > daily_limit  → WARNING (거래 중단)
  - 주간 DD > weekly_limit → HALT (거래 중단)
  - 월간 DD > monthly_limit → FORCE_LIQUIDATE (강제 청산)

연속 손실 + 시간 기반 쿨다운:
  - 연속 손실 >= loss_streak_threshold → 포지션 사이즈 50% 축소
  - 큰 손실(single_loss_halt_pct 초과) → cooldown_seconds 동안 거래 일시 정지

사용:
    monitor = DrawdownMonitor(max_drawdown_pct=0.15)  # 15% MDD
    monitor.update(current_equity=9500)
    if monitor.is_halted():
        # 거래 중단
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple

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
    consecutive_losses: int = 0
    size_multiplier: float = 1.0   # 포지션 사이즈 배수 (1.0=정상, 0.5=연속손실 축소)
    cooldown_active: bool = False  # 시간 기반 쿨다운 중 여부


class DrawdownMonitor:
    """실시간 MDD 추적 및 긴급 정지 모듈.

    3층 서킷브레이커:
      daily_limit  (기본 0.03): 일일 DD 초과 → WARNING + 거래 중단
      weekly_limit (기본 0.07): 주간 DD 초과 → HALT + 거래 중단
      monthly_limit(기본 0.15): 월간 DD 초과 → FORCE_LIQUIDATE

    연속 손실 관리:
      loss_streak_threshold (기본 3): N회 연속 손실 시 size_multiplier=0.5 적용
      single_loss_halt_pct  (기본 0.02): 단일 거래 손실이 계좌의 N% 초과 시 쿨다운 시작
      cooldown_seconds      (기본 3600): 쿨다운 지속 시간 (초)
    """

    def __init__(
        self,
        max_drawdown_pct: float = 0.15,
        recovery_pct: float = 0.05,
        daily_limit: float = 0.03,
        weekly_limit: float = 0.07,
        monthly_limit: float = 0.15,
        loss_streak_threshold: int = 3,
        single_loss_halt_pct: float = 0.02,
        cooldown_seconds: float = 3600.0,
    ) -> None:
        """
        Args:
            max_drawdown_pct: 전체 MDD 한계 (legacy). 초과 시 거래 차단.
            recovery_pct: 차단 해제 기준 (낙폭이 max - recovery 이하로 회복 시 재개).
            daily_limit:   일일 낙폭 한계 (기본 3%).
            weekly_limit:  주간 낙폭 한계 (기본 7%).
            monthly_limit: 월간 낙폭 한계 (기본 15%).
            loss_streak_threshold: 연속 손실 N회 시 size_multiplier 0.5로 축소.
            single_loss_halt_pct:  단일 손실이 계좌 대비 이 비율 초과 시 쿨다운 시작.
            cooldown_seconds:      쿨다운 지속 시간 (초). 기본 1시간.
        """
        self.max_drawdown_pct = max_drawdown_pct
        self.recovery_pct = recovery_pct
        self.daily_limit = daily_limit
        self.weekly_limit = weekly_limit
        self.monthly_limit = monthly_limit
        self.loss_streak_threshold = loss_streak_threshold
        self.single_loss_halt_pct = single_loss_halt_pct
        self.cooldown_seconds = cooldown_seconds

        self._peak: Optional[float] = None
        self._current: float = 0.0
        self._halted: bool = False
        self._halt_reason: str = ""
        self._alert_level: AlertLevel = AlertLevel.NONE

        # 3층 서킷브레이커용 기준 잔고
        self._daily_start: Optional[float] = None
        self._weekly_start: Optional[float] = None
        self._monthly_start: Optional[float] = None

        # 연속 손실 + 쿨다운 상태
        self._consecutive_losses: int = 0
        self._cooldown_until: float = 0.0   # epoch seconds; 0=쿨다운 없음

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

    # ── 연속 손실 + 쿨다운 관리 ───────────────────────────────

    def record_trade_result(self, pnl: float, equity: float) -> None:
        """거래 결과 기록.

        Args:
            pnl:    거래 손익 (음수=손실, 양수=수익).
            equity: 거래 후 계좌 잔고.
        """
        if pnl >= 0:
            if self._consecutive_losses > 0:
                logger.info(
                    "DrawdownMonitor: 연속 손실 초기화 (이전 %d회)", self._consecutive_losses
                )
            self._consecutive_losses = 0
            return

        # 손실 처리
        self._consecutive_losses += 1
        logger.info(
            "DrawdownMonitor: 연속 손실 %d회 (threshold=%d)",
            self._consecutive_losses, self.loss_streak_threshold,
        )

        # 단일 손실 비율이 single_loss_halt_pct 초과 → 쿨다운 시작
        if equity > 0:
            loss_pct = abs(pnl) / equity
            if loss_pct >= self.single_loss_halt_pct:
                self._cooldown_until = time.monotonic() + self.cooldown_seconds
                logger.warning(
                    "DrawdownMonitor: 쿨다운 시작 — 단일 손실 %.2f%% ≥ %.2f%% "
                    "(%.0f초 동안 거래 정지)",
                    loss_pct * 100, self.single_loss_halt_pct * 100, self.cooldown_seconds,
                )

    def is_in_cooldown(self) -> bool:
        """현재 시간 기반 쿨다운 중인지 여부."""
        return time.monotonic() < self._cooldown_until

    def get_size_multiplier(self) -> float:
        """포지션 사이즈 배수 반환.

        - 쿨다운 중: 0.0 (완전 차단)
        - 연속 손실 >= threshold: 0.5 (50% 축소)
        - 정상: 1.0
        """
        if self.is_in_cooldown():
            return 0.0
        if self._consecutive_losses >= self.loss_streak_threshold:
            return 0.5
        return 1.0

    @property
    def consecutive_losses(self) -> int:
        return self._consecutive_losses

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

        # ── 티어드 서킷브레이커: 항상 적용 (이미 halted여도 심각도 상향 가능) ──
        _severity = {AlertLevel.NONE: 0, AlertLevel.WARNING: 1,
                     AlertLevel.HALT: 2, AlertLevel.FORCE_LIQUIDATE: 3}
        if new_level != AlertLevel.NONE:
            if _severity[new_level] > _severity[self._alert_level]:
                # 새 레벨이 더 심각 → 즉시 적용 (신규 halt 또는 에스컬레이션)
                self._halted = True
                self._alert_level = new_level
                self._halt_reason = new_reason
                logger.warning(
                    "DrawdownMonitor: HALTED [%s] — %s", new_level.value, new_reason
                )
            elif not self._halted:
                # 동일 심각도, 아직 미halt → halt 시작
                self._halted = True
                self._alert_level = new_level
                self._halt_reason = new_reason
                logger.warning(
                    "DrawdownMonitor: HALTED [%s] — %s", new_level.value, new_reason
                )
            # 이미 halt + 동일/더 낮은 레벨 → 유지 (no change)

        # legacy MDD 체크 (기준 잔고 미설정 시 폴백)
        elif not self._halted and drawdown >= self.max_drawdown_pct:
            self._halted = True
            self._alert_level = AlertLevel.HALT
            self._halt_reason = (
                f"MDD {drawdown:.1%} ≥ 한계 {self.max_drawdown_pct:.1%} "
                f"(peak={self._peak:.2f}, current={current_equity:.2f})"
            )
            logger.warning("DrawdownMonitor: HALTED — %s", self._halt_reason)

        # 차단 해제 체크: tiered 조건 해소 + MDD 회복 기준 충족 시만 재개
        # FORCE_LIQUIDATE는 수동 해제(force_resume)만 허용
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
            consecutive_losses=self._consecutive_losses,
            size_multiplier=self.get_size_multiplier(),
            cooldown_active=self.is_in_cooldown(),
        )

    def _check_tiered(
        self,
        daily_dd: float,
        weekly_dd: float,
        monthly_dd: float,
        total_dd: float,
    ) -> Tuple[AlertLevel, str]:
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
        self._consecutive_losses = 0
        self._cooldown_until = 0.0
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
            "loss_streak_threshold": self.loss_streak_threshold,
            "single_loss_halt_pct": self.single_loss_halt_pct,
            "cooldown_seconds": self.cooldown_seconds,
            "_peak": self._peak,
            "_current": self._current,
            "_halted": self._halted,
            "_halt_reason": self._halt_reason,
            "_alert_level": self._alert_level.value,
            "_daily_start": self._daily_start,
            "_weekly_start": self._weekly_start,
            "_monthly_start": self._monthly_start,
            "_consecutive_losses": self._consecutive_losses,
            "_cooldown_until": self._cooldown_until,
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
            loss_streak_threshold=data.get("loss_streak_threshold", 3),
            single_loss_halt_pct=data.get("single_loss_halt_pct", 0.02),
            cooldown_seconds=data.get("cooldown_seconds", 3600.0),
        )
        obj._peak = data["_peak"]
        obj._current = data["_current"]
        obj._halted = data["_halted"]
        obj._halt_reason = data["_halt_reason"]
        obj._alert_level = AlertLevel(data["_alert_level"])
        obj._daily_start = data["_daily_start"]
        obj._weekly_start = data["_weekly_start"]
        obj._monthly_start = data["_monthly_start"]
        obj._consecutive_losses = data.get("_consecutive_losses", 0)
        obj._cooldown_until = data.get("_cooldown_until", 0.0)
        return obj
