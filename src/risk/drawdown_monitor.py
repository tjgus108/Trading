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
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Deque, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    NONE = "NONE"
    WARNING = "WARNING"       # 일일 DD 초과 — 경고
    HALT = "HALT"             # 주간 DD 초과 — 거래 중단
    FORCE_LIQUIDATE = "FORCE_LIQUIDATE"  # 월간 DD 초과 — 강제 청산


class MddLevel(str, Enum):
    """단계적 MDD 서킷브레이커 레벨.

    MDD (peak 대비 전체 낙폭) 기준 4단계:
      NORMAL       : MDD < mdd_warn_pct       → 정상 (size_multiplier=1.0)
      WARN         : mdd_warn_pct ≤ MDD < mdd_block_pct → 경고 + 포지션 50% 축소
      BLOCK_ENTRY  : mdd_block_pct ≤ MDD < mdd_liquidate_pct → 신규 진입 차단
      LIQUIDATE    : mdd_liquidate_pct ≤ MDD < mdd_halt_pct → 모든 포지션 청산 권고
      FULL_HALT    : MDD ≥ mdd_halt_pct       → 전체 거래 중단
    """
    NORMAL = "NORMAL"
    WARN = "WARN"
    BLOCK_ENTRY = "BLOCK_ENTRY"
    LIQUIDATE = "LIQUIDATE"
    FULL_HALT = "FULL_HALT"


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
    mdd_level: MddLevel = MddLevel.NORMAL          # 단계적 MDD 레벨
    mdd_size_multiplier: float = 1.0  # MDD 단계별 사이즈 배수 (1.0/0.5/0.0)


class DrawdownMonitor:
    """실시간 MDD 추적 및 긴급 정지 모듈.

    3층 서킷브레이커:
      daily_limit  (기본 0.03): 일일 DD 초과 → WARNING + 거래 중단
      weekly_limit (기본 0.07): 주간 DD 초과 → HALT + 거래 중단
      monthly_limit(기본 0.15): 월간 DD 초과 → FORCE_LIQUIDATE

    단계적 MDD 서킷브레이커 (peak 대비 전체 낙폭 기준):
      mdd_warn_pct      (기본 0.05): MDD ≥ 5%  → 경고 + 포지션 사이즈 50% 축소
      mdd_block_pct     (기본 0.10): MDD ≥ 10% → 신규 진입 차단
      mdd_liquidate_pct (기본 0.15): MDD ≥ 15% → 모든 포지션 청산 권고
      mdd_halt_pct      (기본 0.20): MDD ≥ 20% → 전체 거래 중단

    연속 손실 관리:
      loss_streak_threshold    (기본 3): N회 연속 손실 시 size_multiplier=0.5 적용 + streak 쿨다운 시작
      single_loss_halt_pct     (기본 0.02): 단일 거래 손실이 계좌의 N% 초과 시 쿨다운 시작
      cooldown_seconds         (기본 3600): 단일 큰 손실 쿨다운 지속 시간 (초)
      streak_cooldown_seconds  (기본 14400): 연속 손실 N회 도달 시 쿨다운 지속 시간 (4시간)
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
        streak_cooldown_seconds: float = 14400.0,
        mdd_warn_pct: float = 0.05,
        mdd_block_pct: float = 0.10,
        mdd_liquidate_pct: float = 0.15,
        mdd_halt_pct: float = 0.20,
    ) -> None:
        """
        Args:
            max_drawdown_pct: 전체 MDD 한계 (legacy). 초과 시 거래 차단.
            recovery_pct: 차단 해제 기준 (낙폭이 max - recovery 이하로 회복 시 재개).
            daily_limit:   일일 낙폭 한계 (기본 3%).
            weekly_limit:  주간 낙폭 한계 (기본 7%).
            monthly_limit: 월간 낙폭 한계 (기본 15%).
            loss_streak_threshold: 연속 손실 N회 시 size_multiplier 0.5로 축소.
                                   이 횟수에 도달하면 streak_cooldown_seconds 쿨다운도 시작.
            single_loss_halt_pct:  단일 손실이 계좌 대비 이 비율 초과 시 쿨다운 시작.
            cooldown_seconds:      단일 큰 손실 후 쿨다운 지속 시간 (초). 기본 1시간.
            streak_cooldown_seconds: 연속 손실(loss_streak_threshold 도달) 후 쿨다운 지속 시간 (초).
                                     기본 4시간. 0으로 설정 시 연속 손실 쿨다운 비활성화.
            mdd_warn_pct:      MDD 경고 기준 (기본 5%). 포지션 50% 축소.
            mdd_block_pct:     MDD 진입 차단 기준 (기본 10%). 신규 진입 차단.
            mdd_liquidate_pct: MDD 청산 권고 기준 (기본 15%). 모든 포지션 청산 권고.
            mdd_halt_pct:      MDD 완전 중단 기준 (기본 20%). 전체 거래 중단.
        """
        self.max_drawdown_pct = max_drawdown_pct
        self.recovery_pct = recovery_pct
        self.daily_limit = daily_limit
        self.weekly_limit = weekly_limit
        self.monthly_limit = monthly_limit
        self.loss_streak_threshold = loss_streak_threshold
        self.single_loss_halt_pct = single_loss_halt_pct
        self.cooldown_seconds = cooldown_seconds
        self.streak_cooldown_seconds = streak_cooldown_seconds
        self.mdd_warn_pct = mdd_warn_pct
        self.mdd_block_pct = mdd_block_pct
        self.mdd_liquidate_pct = mdd_liquidate_pct
        self.mdd_halt_pct = mdd_halt_pct
        self._high_vol_daily_limit: float = 0.02   # HIGH_VOL 레짐 일일 DD 한도 (2%)
        self._current_regime: str = ''             # 현재 레짐 (빈 문자열 = 기본)

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
        self._single_loss_cooldown_until: float = 0.0  # 단일 손실로 인한 쿨다운

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

    def set_regime(self, regime: str) -> None:
        """현재 시장 레짐 설정. HIGH_VOL 시 일일 DD 한도를 강화한다.

        Args:
            regime: 레짐 문자열 — 'TREND_UP', 'TREND_DOWN', 'RANGING', 'HIGH_VOL'
        """
        self._current_regime = regime.upper() if regime else ''
        if self._current_regime == 'HIGH_VOL':
            logger.info(
                'DrawdownMonitor: HIGH_VOL 레짐 — 일일 DD 한도 %.1f%% → %.1f%% 강화',
                self.daily_limit * 100, self._high_vol_daily_limit * 100,
            )
        else:
            logger.debug('DrawdownMonitor: regime=%s (일일 한도=%.1f%%)', self._current_regime, self.daily_limit * 100)

    def _effective_daily_limit(self) -> float:
        """현재 레짐에 따른 실효 일일 DD 한도 반환."""
        if self._current_regime == 'HIGH_VOL':
            return self._high_vol_daily_limit
        return self.daily_limit

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
                self._single_loss_cooldown_until = time.monotonic() + self.cooldown_seconds
                logger.warning(
                    "DrawdownMonitor: 쿨다운 시작 — 단일 손실 %.2f%% ≥ %.2f%% "
                    "(%.0f초 동안 거래 정지)",
                    loss_pct * 100, self.single_loss_halt_pct * 100, self.cooldown_seconds,
                )

        # 연속 손실이 threshold에 정확히 도달 → streak 쿨다운 시작 (size reduction만, 완전 블록 아님)
        # (streak_cooldown_seconds=0 이면 스킵)
        if (
            self._consecutive_losses == self.loss_streak_threshold
            and self.streak_cooldown_seconds > 0
        ):
            self._cooldown_until = time.monotonic() + self.streak_cooldown_seconds
            logger.warning(
                "DrawdownMonitor: 연속 손실 쿨다운 시작 — %d회 연속 손실 "
                "(%.0f초 = %.1f시간 동안 거래 정지)",
                self._consecutive_losses,
                self.streak_cooldown_seconds,
                self.streak_cooldown_seconds / 3600,
            )

    def is_in_cooldown(self) -> bool:
        """현재 시간 기반 쿨다운 중인지 여부 (단일 손실로 인한 완전 블록만)."""
        return time.monotonic() < self._single_loss_cooldown_until
    
    def is_in_streak_cooldown(self) -> bool:
        """연속 손실로 인한 쿨다운 (size reduction 적용됨)."""
        return time.monotonic() < self._cooldown_until

    def get_size_multiplier(self) -> float:
        """포지션 사이즈 배수 반환.

        여러 조건의 최소값을 적용:
        - 단일 손실 쿨다운 중: 0.0 (완전 차단)
        - 연속 손실 >= threshold: 0.5 (50% 축소, streak_cooldown 중에도 유지)
        - MDD 단계별: get_mdd_size_multiplier() 결과
        - 정상: 1.0
        """
        if self.is_in_cooldown():
            return 0.0
        streak_mult = 0.5 if self._consecutive_losses >= self.loss_streak_threshold else 1.0
        mdd_mult = self.get_mdd_size_multiplier()
        return min(streak_mult, mdd_mult)

    # ── 단계적 MDD 서킷브레이커 ─────────────────────────────────

    def get_mdd_level(self) -> MddLevel:
        """현재 peak 대비 전체 낙폭 기준 MDD 단계 반환.

        MDD 단계:
          NORMAL      : MDD < mdd_warn_pct
          WARN        : mdd_warn_pct ≤ MDD < mdd_block_pct
          BLOCK_ENTRY : mdd_block_pct ≤ MDD < mdd_liquidate_pct
          LIQUIDATE   : mdd_liquidate_pct ≤ MDD < mdd_halt_pct
          FULL_HALT   : MDD ≥ mdd_halt_pct
        """
        dd = self.current_drawdown()
        if dd >= self.mdd_halt_pct:
            return MddLevel.FULL_HALT
        if dd >= self.mdd_liquidate_pct:
            return MddLevel.LIQUIDATE
        if dd >= self.mdd_block_pct:
            return MddLevel.BLOCK_ENTRY
        if dd >= self.mdd_warn_pct:
            return MddLevel.WARN
        return MddLevel.NORMAL

    def get_mdd_size_multiplier(self) -> float:
        """MDD 단계에 따른 포지션 사이즈 배수 반환.

        NORMAL      → 1.0  (정상)
        WARN        → 0.5  (50% 축소)
        BLOCK_ENTRY → 0.0  (신규 진입 차단)
        LIQUIDATE   → 0.0  (청산 권고, 진입 불가)
        FULL_HALT   → 0.0  (전체 중단)
        """
        level = self.get_mdd_level()
        if level == MddLevel.NORMAL:
            return 1.0
        if level == MddLevel.WARN:
            return 0.5
        # BLOCK_ENTRY, LIQUIDATE, FULL_HALT → 0.0
        return 0.0

    def should_liquidate_all(self) -> bool:
        """MDD LIQUIDATE 이상 단계 시 True — 모든 포지션 청산 권고."""
        level = self.get_mdd_level()
        return level in (MddLevel.LIQUIDATE, MddLevel.FULL_HALT)

    @property
    def mdd_level(self) -> MddLevel:
        """현재 MDD 단계 (프로퍼티)."""
        return self.get_mdd_level()

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

        # 단계적 MDD 레벨 계산
        cur_mdd_level = self.get_mdd_level()
        cur_mdd_size_mult = self.get_mdd_size_multiplier()

        # MDD 단계 로깅 (NORMAL 제외)
        if cur_mdd_level != MddLevel.NORMAL:
            logger.info(
                "DrawdownMonitor: MDD 단계 [%s] — drawdown=%.2f%% (size_mult=%.1f)",
                cur_mdd_level.value, drawdown * 100, cur_mdd_size_mult,
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
            mdd_level=cur_mdd_level,
            mdd_size_multiplier=cur_mdd_size_mult,
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
        if daily_dd >= self._effective_daily_limit():
            return (
                AlertLevel.WARNING,
                f"일일 낙폭 {daily_dd:.1%} ≥ 한계 {self._effective_daily_limit():.1%} — 경고",
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
        self._single_loss_cooldown_until = 0.0
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
            "streak_cooldown_seconds": self.streak_cooldown_seconds,
            "mdd_warn_pct": self.mdd_warn_pct,
            "mdd_block_pct": self.mdd_block_pct,
            "mdd_liquidate_pct": self.mdd_liquidate_pct,
            "mdd_halt_pct": self.mdd_halt_pct,
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
            "_single_loss_cooldown_until": self._single_loss_cooldown_until,
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
            streak_cooldown_seconds=data.get("streak_cooldown_seconds", 14400.0),
            mdd_warn_pct=data.get("mdd_warn_pct", 0.05),
            mdd_block_pct=data.get("mdd_block_pct", 0.10),
            mdd_liquidate_pct=data.get("mdd_liquidate_pct", 0.15),
            mdd_halt_pct=data.get("mdd_halt_pct", 0.20),
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
        obj._single_loss_cooldown_until = data.get("_single_loss_cooldown_until", 0.0)
        return obj


# ────────────────────────────────────────────────────────────────────────────────
# DriftMonitor: Page-Hinkley 기반 수익률 분포 변화(concept drift) 감지
# ────────────────────────────────────────────────────────────────────────────────

class DriftState(str, Enum):
    NORMAL = "NORMAL"      # 드리프트 없음
    WARNING = "WARNING"    # 경고 (드리프트 후보)
    DRIFT = "DRIFT"        # 드리프트 확정 → CB 연동 트리거


class DriftMonitor:
    """Page-Hinkley 테스트 기반 수익률 분포 변화 감지기.

    거래 수익률(pnl_pct)을 스트리밍으로 입력받아 분포의 평균 또는 분산이
    통계적으로 유의미하게 변화했는지 감지한다.

    Page-Hinkley Test (양방향):
        m_t = x_t - mu_ref + delta        (delta: 감도 조절)
        M_t = sum(m_0..m_t)               (누적합)
        ph_t = max(M_0..M_t) - M_t        (Page-Hinkley 통계량, 하락 감지)
        drift if ph_t > lambda_            (lambda_: 감지 한계)

    상승 감지: m_t = mu_ref - x_t + delta 로 동일 구조 적용.

    분산 감지:
        rolling 분산이 warm-up 기간 분산의 var_ratio_threshold 배 초과 시 WARNING.

    Args:
        window:              분산 감지용 롤링 윈도우 크기 (기본 30).
        warm_up:             기준 통계 수집 기간 (기본 50). warm-up 전에는 감지 안 함.
        delta:               PH 최소 감지 임계값 (기본 0.001). 작을수록 민감.
        lambda_:             PH 감지 한계 (기본 50). 클수록 false positive 감소.
        var_ratio_threshold: 분산 배율 임계값 (기본 2.0). warm-up 분산 대비 N배 초과 시 WARNING.
        on_drift:            드리프트 감지 시 호출할 콜백 함수 (optional).
                             signature: (state: DriftState, reason: str) -> None
    """

    def __init__(
        self,
        window: int = 30,
        warm_up: int = 50,
        delta: float = 0.001,
        lambda_: float = 50.0,
        var_ratio_threshold: float = 2.0,
        on_drift: Optional[Callable[["DriftState", str], None]] = None,
    ) -> None:
        self.window = window
        self.warm_up = warm_up
        self.delta = delta
        self.lambda_ = lambda_
        self.var_ratio_threshold = var_ratio_threshold
        self.on_drift = on_drift

        self._returns: Deque[float] = deque(maxlen=max(window, warm_up) * 2)
        self._n: int = 0
        self._state: DriftState = DriftState.NORMAL

        # PH 통계량 (하락 감지)
        self._ph_sum_down: float = 0.0
        self._ph_max_down: float = 0.0  # max(M_t) for downward shift detection
        # PH 통계량 (상승 감지)
        self._ph_sum_up: float = 0.0
        self._ph_max_up: float = 0.0

        # warm-up 기간 참조 통계
        self._mu_ref: float = 0.0
        self._var_ref: float = 0.0
        self._warm_up_done: bool = False

    # ── 내부 헬퍼 ─────────────────────────────────────────────────

    def _update_ph(self, x: float) -> Tuple[float, float]:
        """Page-Hinkley 통계량 업데이트. (ph_down, ph_up) 반환.

        표준 PH 공식 (하락 감지):
            m_t = (x_t - mu_ref + delta)   — 평균 하락 시 m_t < 0
            M_t = sum(m)                    — 누적합, 하락 시 감소
            ph_t = max(M) - M_t             — M이 하락할수록 증가
        """
        # 하락 감지: x가 mu_ref 아래로 이동 → ph_down 증가
        m_down = x - self._mu_ref + self.delta
        self._ph_sum_down += m_down
        self._ph_max_down = max(self._ph_max_down, self._ph_sum_down)
        ph_down = self._ph_max_down - self._ph_sum_down

        # 상승 감지: x가 mu_ref 위로 이동 → ph_up 증가
        m_up = self._mu_ref - x + self.delta
        self._ph_sum_up += m_up
        self._ph_max_up = max(self._ph_max_up, self._ph_sum_up)
        ph_up = self._ph_max_up - self._ph_sum_up

        return ph_down, ph_up

    def _rolling_variance(self) -> float:
        """최근 window 기간 수익률 분산."""
        recent = list(self._returns)[-self.window:]
        if len(recent) < 2:
            return 0.0
        return float(np.var(recent, ddof=1))

    # ── 메인 업데이트 ──────────────────────────────────────────────

    def update(self, pnl_pct: float) -> "DriftState":
        """수익률(pnl_pct) 한 건 입력. 현재 DriftState 반환.

        Args:
            pnl_pct: 거래 손익 비율. 예) -0.02 = -2% 손실, 0.015 = +1.5% 수익.

        Returns:
            DriftState: NORMAL / WARNING / DRIFT
        """
        self._returns.append(pnl_pct)
        self._n += 1

        # warm-up 완료 판정
        if not self._warm_up_done and self._n >= self.warm_up:
            warm_data = list(self._returns)[:self.warm_up]
            self._mu_ref = float(np.mean(warm_data))
            self._var_ref = float(np.var(warm_data, ddof=1))
            # PH 통계량 초기화
            self._ph_sum_down = 0.0
            self._ph_max_down = 0.0
            self._ph_sum_up = 0.0
            self._ph_max_up = 0.0
            self._warm_up_done = True
            logger.debug(
                "DriftMonitor: warm-up 완료 — mu_ref=%.5f, var_ref=%.8f",
                self._mu_ref, self._var_ref,
            )

        if not self._warm_up_done:
            return self._state

        # Page-Hinkley 업데이트
        ph_down, ph_up = self._update_ph(pnl_pct)

        # 분산 감지
        rolling_var = self._rolling_variance()
        var_ratio = (rolling_var / self._var_ref) if self._var_ref > 0 else 1.0

        # 감지 판정
        new_state = DriftState.NORMAL
        reason = ""

        if ph_down > self.lambda_:
            new_state = DriftState.DRIFT
            reason = (
                f"PH(하락) {ph_down:.1f} > lambda {self.lambda_:.1f} "
                f"(mu_ref={self._mu_ref:.5f})"
            )
        elif ph_up > self.lambda_:
            new_state = DriftState.DRIFT
            reason = (
                f"PH(상승) {ph_up:.1f} > lambda {self.lambda_:.1f} "
                f"(mu_ref={self._mu_ref:.5f})"
            )
        elif var_ratio >= self.var_ratio_threshold:
            new_state = DriftState.WARNING
            reason = (
                f"분산 {var_ratio:.2f}x 급등 "
                f"(rolling={rolling_var:.8f}, ref={self._var_ref:.8f})"
            )

        # 상태 전이 + 콜백
        if new_state != DriftState.NORMAL:
            if new_state == DriftState.DRIFT:
                logger.warning(
                    "DriftMonitor: DRIFT 감지 — %s [n=%d]", reason, self._n
                )
            else:
                logger.warning(
                    "DriftMonitor: WARNING — %s [n=%d]", reason, self._n
                )
            self._state = new_state
            if self.on_drift is not None:
                try:
                    self.on_drift(new_state, reason)
                except Exception as exc:  # noqa: BLE001
                    logger.error("DriftMonitor: on_drift 콜백 오류 — %s", exc)
        elif self._state != DriftState.NORMAL:
            # 드리프트 감지 후 정상화 — PH 리셋 (새 기준점)
            logger.info(
                "DriftMonitor: 정상화 감지 — 참조 통계 갱신 [n=%d]", self._n
            )
            self._reset_ph_and_ref()
            self._state = DriftState.NORMAL

        return self._state

    def _reset_ph_and_ref(self) -> None:
        """PH 통계량과 참조 평균을 최근 window 데이터 기준으로 갱신."""
        recent = list(self._returns)[-self.window:]
        if len(recent) >= 2:
            self._mu_ref = float(np.mean(recent))
            self._var_ref = float(np.var(recent, ddof=1))
        self._ph_sum_down = 0.0
        self._ph_max_down = 0.0
        self._ph_sum_up = 0.0
        self._ph_max_up = 0.0

    # ── 상태 조회 ──────────────────────────────────────────────────

    @property
    def state(self) -> "DriftState":
        return self._state

    @property
    def n_samples(self) -> int:
        return self._n

    @property
    def is_drift(self) -> bool:
        return self._state == DriftState.DRIFT

    @property
    def is_warning(self) -> bool:
        return self._state in (DriftState.WARNING, DriftState.DRIFT)

    def reset(self) -> None:
        """전체 상태 초기화 (새 세션 시작 시)."""
        self._returns.clear()
        self._n = 0
        self._state = DriftState.NORMAL
        self._ph_sum_down = 0.0
        self._ph_max_down = 0.0
        self._ph_sum_up = 0.0
        self._ph_max_up = 0.0
        self._mu_ref = 0.0
        self._var_ref = 0.0
        self._warm_up_done = False
        logger.info("DriftMonitor: reset")
