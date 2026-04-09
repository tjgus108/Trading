"""
Circuit Breaker: Drawdown 기반 자동 거래 중단.
일일 낙폭 -5%, 전체 낙폭 -15% 초과 시 트리거.
"""
import logging

logger = logging.getLogger(__name__)


class CircuitBreaker:
    def __init__(
        self,
        daily_drawdown_limit: float = 0.05,   # -5% 일일 낙폭
        total_drawdown_limit: float = 0.15,   # -15% 전체 낙폭
    ):
        self.daily_drawdown_limit = daily_drawdown_limit
        self.total_drawdown_limit = total_drawdown_limit
        self._triggered: bool = False
        self._reason: str = ""
        self._daily_start_balance: float = 0.0

    def check(
        self,
        current_balance: float,
        peak_balance: float,
        daily_start_balance: float,
    ) -> dict:
        """
        반환: {"triggered": bool, "reason": str, "drawdown_pct": float}
        daily_drawdown: (daily_start - current) / daily_start
        total_drawdown: (peak - current) / peak
        """
        if daily_start_balance <= 0 or peak_balance <= 0:
            return {"triggered": False, "reason": "", "drawdown_pct": 0.0}

        daily_dd = (daily_start_balance - current_balance) / daily_start_balance
        total_dd = (peak_balance - current_balance) / peak_balance

        # 이미 트리거된 상태는 유지
        if self._triggered:
            worst = max(daily_dd, total_dd)
            return {
                "triggered": True,
                "reason": self._reason,
                "drawdown_pct": round(worst, 6),
            }

        if daily_dd >= self.daily_drawdown_limit:
            self._triggered = True
            self._reason = (
                f"일일 낙폭 {daily_dd:.2%} ≥ 한계 {self.daily_drawdown_limit:.2%}"
            )
            logger.warning("CircuitBreaker TRIGGERED: %s", self._reason)
            return {
                "triggered": True,
                "reason": self._reason,
                "drawdown_pct": round(daily_dd, 6),
            }

        if total_dd >= self.total_drawdown_limit:
            self._triggered = True
            self._reason = (
                f"전체 낙폭 {total_dd:.2%} ≥ 한계 {self.total_drawdown_limit:.2%}"
            )
            logger.warning("CircuitBreaker TRIGGERED: %s", self._reason)
            return {
                "triggered": True,
                "reason": self._reason,
                "drawdown_pct": round(total_dd, 6),
            }

        worst = max(daily_dd, total_dd)
        return {"triggered": False, "reason": "", "drawdown_pct": round(worst, 6)}

    def reset_daily(self, daily_start_balance: float):
        """매일 자정 리셋 — 일일 트리거만 해제, 전체 낙폭 트리거는 수동 해제 필요."""
        self._daily_start_balance = daily_start_balance
        # 전체 낙폭으로 트리거된 경우 유지, 일일로만 트리거된 경우 해제
        if self._triggered and "일일" in self._reason:
            self._triggered = False
            self._reason = ""
            logger.info("CircuitBreaker: 일일 리셋 완료 (start_balance=%.2f)", daily_start_balance)

    def reset_all(self):
        """전체 상태 초기화."""
        self._triggered = False
        self._reason = ""
        logger.info("CircuitBreaker: 전체 리셋")

    @property
    def is_triggered(self) -> bool:
        return self._triggered
