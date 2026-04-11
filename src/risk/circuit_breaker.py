"""
Circuit Breaker: 다층 자동 거래 중단.
- 일일 낙폭 / 전체 낙폭
- 변동성 급등: 현재 ATR이 기준 ATR의 atr_surge_multiplier 배 이상이면 트리거
  (포지션 full-block이 아닌 50% 축소 신호를 반환)
- 상관관계 급증: 전략 간 상관계수 ≥ corr_threshold → size_multiplier=0.7 축소
- 플래시 크래시 감지: 단일 캔들 가격 변동 ≥ flash_crash_pct → 즉시 완전 차단
"""
import logging
from typing import Optional

from src.analysis.strategy_correlation import SignalCorrelationTracker

logger = logging.getLogger(__name__)


class CircuitBreaker:
    def __init__(
        self,
        daily_drawdown_limit: float = 0.05,   # -5% 일일 낙폭
        total_drawdown_limit: float = 0.15,   # -15% 전체 낙폭
        atr_surge_multiplier: float = 2.0,    # 현재 ATR ≥ baseline * 2.0 → 변동성 급등
        corr_threshold: float = 0.7,          # 전략 상관계수 ≥ 0.7 → 축소
        flash_crash_pct: float = 0.10,        # 단일 캔들 10% 이상 변동 → 즉시 차단
        correlation_tracker: Optional[SignalCorrelationTracker] = None,
    ):
        self.daily_drawdown_limit = daily_drawdown_limit
        self.total_drawdown_limit = total_drawdown_limit
        self.atr_surge_multiplier = atr_surge_multiplier
        self.corr_threshold = corr_threshold
        self.flash_crash_pct = flash_crash_pct
        self._correlation_tracker = correlation_tracker
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
        correlation_throttle: bool = False,
        size_multiplier: float = 1.0,
    ) -> dict:
        return {
            "triggered": triggered,
            "reason": reason,
            "drawdown_pct": round(drawdown_pct, 6),
            "volatility_surge": volatility_surge,
            "correlation_throttle": correlation_throttle,
            "size_multiplier": size_multiplier,   # 1.0=정상, 0.7=상관축소, 0.5=반축소, 0.0=완전차단
        }

    # ── 메인 체크 ──────────────────────────────────────────────────────────────
    def check(
        self,
        current_balance: float,
        peak_balance: float,
        daily_start_balance: float,
        current_atr: Optional[float] = None,
        baseline_atr: Optional[float] = None,
        candle_open: Optional[float] = None,
        candle_close: Optional[float] = None,
    ) -> dict:
        """
        반환:
          triggered            : bool   — True면 거래 완전 차단
          reason               : str
          drawdown_pct         : float
          volatility_surge     : bool   — True면 포지션 50% 축소 권고
          correlation_throttle : bool   — True면 포지션 70% 축소 권고
          size_multiplier      : float  — 1.0=정상, 0.7=상관축소, 0.5=ATR축소, 0.0=차단

        ATR surge와 correlation throttle이 동시 발생하면 더 보수적인 값(0.5) 사용.
        낙폭 조건은 항상 우선 — triggered=True, size_multiplier=0.0.
        플래시 크래시(candle_open/candle_close 제공 시)는 낙폭보다 먼저 체크.
        """
        if daily_start_balance <= 0 or peak_balance <= 0:
            return self._make_result(False, "", 0.0)

        # ── 플래시 크래시 체크 (최우선) ──────────────────────────────────────
        if candle_open is not None and candle_close is not None and candle_open > 0:
            candle_chg = abs(candle_close - candle_open) / candle_open
            if candle_chg >= self.flash_crash_pct:
                self._triggered = True
                self._reason = (
                    f"플래시 크래시 감지: 캔들 변동 {candle_chg:.2%} ≥ 한계 {self.flash_crash_pct:.2%} "
                    f"(open={candle_open}, close={candle_close})"
                )
                logger.warning("CircuitBreaker TRIGGERED: %s", self._reason)
                return self._make_result(True, self._reason, 0.0, size_multiplier=0.0)

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

        worst = max(daily_dd, total_dd)

        # ── ATR 변동성 급등 체크 ──────────────────────────────────────────────
        atr_surge = False
        atr_reason = ""
        if (
            current_atr is not None
            and baseline_atr is not None
            and baseline_atr > 0
            and current_atr >= baseline_atr * self.atr_surge_multiplier
        ):
            surge_ratio = current_atr / baseline_atr
            atr_reason = (
                f"ATR 급등 {surge_ratio:.2f}x "
                f"(현재 {current_atr:.4f} ≥ 기준 {baseline_atr:.4f} × {self.atr_surge_multiplier})"
            )
            atr_surge = True
            logger.warning("CircuitBreaker VOLATILITY SURGE: %s — 포지션 50%% 축소", atr_reason)

        # ── 상관관계 급증 체크 ────────────────────────────────────────────────
        corr_throttle = False
        corr_reason = ""
        if self._correlation_tracker is not None:
            # 양의 상관만 throttle (전략 중복 케이스); 음의 상관은 헤지 효과
            high_pairs = [
                (a, b, r)
                for a, b, r in self._correlation_tracker.high_correlation_pairs(
                    threshold=self.corr_threshold
                )
                if r >= self.corr_threshold
            ]
            if high_pairs:
                top_a, top_b, top_r = high_pairs[0]
                corr_reason = (
                    f"상관관계 급증 {top_a}↔{top_b} r={top_r:+.3f} ≥ {self.corr_threshold}"
                )
                corr_throttle = True
                logger.warning(
                    "CircuitBreaker CORRELATION THROTTLE: %s — 포지션 70%% 축소", corr_reason
                )

        # ── 복합 판정 ─────────────────────────────────────────────────────────
        if atr_surge and corr_throttle:
            # ATR surge가 더 보수적
            combined_reason = f"{atr_reason} | {corr_reason}"
            return self._make_result(
                False, combined_reason, worst,
                volatility_surge=True,
                correlation_throttle=True,
                size_multiplier=0.5,
            )
        if atr_surge:
            return self._make_result(
                False, atr_reason, worst,
                volatility_surge=True,
                size_multiplier=0.5,
            )
        if corr_throttle:
            return self._make_result(
                False, corr_reason, worst,
                correlation_throttle=True,
                size_multiplier=0.7,
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
