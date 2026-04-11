"""
Circuit Breaker: 다층 자동 거래 중단.
- 일일 낙폭 / 전체 낙폭
- 변동성 급등: 현재 ATR이 기준 ATR의 atr_surge_multiplier 배 이상이면 트리거
  (포지션 full-block이 아닌 50% 축소 신호를 반환)
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CircuitBreaker:
    def __init__(
        self,
        daily_drawdown_limit: float = 0.05,   # -5% 일일 낙폭
        total_drawdown_limit: float = 0.15,   # -15% 전체 낙폭
        atr_surge_multiplier: float = 2.0,    # 현재 ATR ≥ baseline * 2.0 → 변동성 급등
    ):
        self.daily_drawdown_limit = daily_drawdown_limit
        self.total_drawdown_limit = total_drawdown_limit
        self.atr_surge_multiplier = atr_surge_multiplier
        self._triggered: bool = False
        self._reason: str = ""
        self._daily_start_balance: float = 0.0

    # ── 내부 헬퍼 ──────────────────────────────────────────────────────────────
    def _make_result(
        self,
        triggered: bool,
        reason: str,
        drawdown_pct: float,
        volatility_surge: bool = False,
        size_multiplier: float = 1.0,
    ) -> dict:
        return {
            "triggered": triggered,
            "reason": reason,
            "drawdown_pct": round(drawdown_pct, 6),
            "volatility_surge": volatility_surge,
            "size_multiplier": size_multiplier,   # 1.0=정상, 0.5=반축소, 0.0=완전차단
        }

    # ── 메인 체크 ──────────────────────────────────────────────────────────────
    def check(
        self,
        current_balance: float,
        peak_balance: float,
        daily_start_balance: float,
        current_atr: Optional[float] = None,
        baseline_atr: Optional[float] = None,
    ) -> dict:
        """
        반환:
          triggered       : bool   — True면 거래 완전 차단
          reason          : str
          drawdown_pct    : float
          volatility_surge: bool   — True면 포지션 50% 축소 권고 (triggered=False일 때만 유효)
          size_multiplier : float  — 1.0=정상, 0.5=축소, 0.0=차단

        변동성 급등(ATR surge)은 단독으로 triggered=True를 유발하지 않고
        size_multiplier=0.5 + volatility_surge=True 를 반환한다.
        낙폭 조건과 함께 발생하면 triggered=True.
        """
        if daily_start_balance <= 0 or peak_balance <= 0:
            return self._make_result(False, "", 0.0)

        daily_dd = (daily_start_balance - current_balance) / daily_start_balance
        total_dd = (peak_balance - current_balance) / peak_balance

        # 이미 트리거된 상태 유지
        if self._triggered:
            worst = max(daily_dd, total_dd)
            return self._make_result(True, self._reason, worst, size_multiplier=0.0)

        # ── 낙폭 체크 ─────────────────────────────────────────────────────────
        if daily_dd >= self.daily_drawdown_limit:
            self._triggered = True
            self._reason = (
                f"일일 낙폭 {daily_dd:.2%} ≥ 한계 {self.daily_drawdown_limit:.2%}"
            )
            logger.warning("CircuitBreaker TRIGGERED: %s", self._reason)
            return self._make_result(True, self._reason, daily_dd, size_multiplier=0.0)

        if total_dd >= self.total_drawdown_limit:
            self._triggered = True
            self._reason = (
                f"전체 낙폭 {total_dd:.2%} ≥ 한계 {self.total_drawdown_limit:.2%}"
            )
            logger.warning("CircuitBreaker TRIGGERED: %s", self._reason)
            return self._make_result(True, self._reason, total_dd, size_multiplier=0.0)

        # ── ATR 변동성 급등 체크 ──────────────────────────────────────────────
        worst = max(daily_dd, total_dd)
        if (
            current_atr is not None
            and baseline_atr is not None
            and baseline_atr > 0
            and current_atr >= baseline_atr * self.atr_surge_multiplier
        ):
            surge_ratio = current_atr / baseline_atr
            reason = (
                f"ATR 급등 {surge_ratio:.2f}x "
                f"(현재 {current_atr:.4f} ≥ 기준 {baseline_atr:.4f} × {self.atr_surge_multiplier})"
            )
            logger.warning("CircuitBreaker VOLATILITY SURGE: %s — 포지션 50%% 축소", reason)
            return self._make_result(
                False, reason, worst,
                volatility_surge=True,
                size_multiplier=0.5,
            )

        return self._make_result(False, "", worst)

    # ── 리셋 ──────────────────────────────────────────────────────────────────
    def reset_daily(self, daily_start_balance: float):
        """매일 자정 리셋 — 일일 트리거만 해제, 전체 낙폭 트리거는 수동 해제 필요."""
        self._daily_start_balance = daily_start_balance
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
