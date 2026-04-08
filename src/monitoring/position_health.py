"""
K2. Position Health Monitor — 보유 포지션 리스크 상태 추적.

현재 포지션의 미실현 손익, 손절 거리, 리스크/리워드 비율을 계산하고
상태(HEALTHY / WARNING / CRITICAL)를 반환한다.

사용:
  monitor = PositionHealthMonitor()
  health = monitor.evaluate(
      entry_price=50000, current_price=49000,
      stop_loss=48000, take_profit=53000,
      side="long"
  )
  print(health.status)  # "WARNING"
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PositionHealth:
    status: str            # "HEALTHY" | "WARNING" | "CRITICAL"
    unrealized_pnl_pct: float  # 미실현 손익 비율 (양수=이익)
    stop_distance_pct: float   # 현재가 ~ 손절가 거리 (양수)
    risk_reward_ratio: float   # (TP 거리) / (SL 거리)
    side: str
    reason: str

    def is_critical(self) -> bool:
        return self.status == "CRITICAL"


class PositionHealthMonitor:
    """포지션 건강 상태 평가기."""

    WARNING_LOSS_PCT = 0.03    # 3% 손실 → WARNING
    CRITICAL_LOSS_PCT = 0.06   # 6% 손실 → CRITICAL
    MIN_STOP_DISTANCE = 0.005  # 손절까지 0.5% 미만 → CRITICAL
    MIN_RR_RATIO = 0.5         # R/R < 0.5 → WARNING

    def evaluate(
        self,
        entry_price: float,
        current_price: float,
        stop_loss: float,
        take_profit: float,
        side: str = "long",     # "long" | "short"
    ) -> PositionHealth:
        """포지션 건강 상태 평가."""
        if entry_price <= 0:
            return PositionHealth(
                status="CRITICAL", unrealized_pnl_pct=0.0,
                stop_distance_pct=0.0, risk_reward_ratio=0.0,
                side=side, reason="Invalid entry_price",
            )

        # 미실현 손익
        if side == "long":
            unrealized_pct = (current_price - entry_price) / entry_price
            stop_distance = (current_price - stop_loss) / current_price if current_price > 0 else 0.0
            tp_distance = (take_profit - current_price) / current_price if current_price > 0 else 0.0
        else:  # short
            unrealized_pct = (entry_price - current_price) / entry_price
            stop_distance = (stop_loss - current_price) / current_price if current_price > 0 else 0.0
            tp_distance = (current_price - take_profit) / current_price if current_price > 0 else 0.0

        stop_distance = max(0.0, stop_distance)
        tp_distance = max(0.0, tp_distance)
        rr = tp_distance / stop_distance if stop_distance > 1e-9 else 0.0

        # 상태 결정
        reasons = []
        status = "HEALTHY"

        if unrealized_pct <= -self.CRITICAL_LOSS_PCT:
            status = "CRITICAL"
            reasons.append(f"손실 {unrealized_pct:.1%} ≥ {-self.CRITICAL_LOSS_PCT:.1%}")
        elif unrealized_pct <= -self.WARNING_LOSS_PCT:
            status = "WARNING"
            reasons.append(f"손실 {unrealized_pct:.1%}")

        if stop_distance < self.MIN_STOP_DISTANCE:
            status = "CRITICAL"
            reasons.append(f"손절 근접 {stop_distance:.2%}")

        if rr < self.MIN_RR_RATIO and status == "HEALTHY":
            status = "WARNING"
            reasons.append(f"R/R={rr:.2f} < {self.MIN_RR_RATIO}")

        reason = "; ".join(reasons) if reasons else "정상 범위"

        logger.debug(
            "PositionHealth: %s side=%s pnl=%.2%% stop_dist=%.2%% rr=%.2f",
            status, side, unrealized_pct, stop_distance, rr,
        )

        return PositionHealth(
            status=status,
            unrealized_pnl_pct=unrealized_pct,
            stop_distance_pct=stop_distance,
            risk_reward_ratio=rr,
            side=side,
            reason=reason,
        )
