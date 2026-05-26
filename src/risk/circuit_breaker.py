"""
Circuit Breaker: 다층 자동 거래 중단.
- 일일 낙폭 / 전체 낙폭
- 변동성 급등: 현재 ATR이 기준 ATR의 atr_surge_multiplier 배 이상이면 트리거
  (포지션 full-block이 아닌 50% 축소 신호를 반환)
- 상관관계 급증: 전략 간 상관계수 ≥ corr_threshold → size_multiplier=0.7 축소
- 플래시 크래시 감지: 단일 캔들 가격 변동 ≥ flash_crash_pct → 즉시 완전 차단
- 급속 가격 하락 감지: 최근 N캔들 내 가격 하락 ≥ rapid_decline_pct → 신규 진입 중단 + cooldown
- 연속 손실 쿨다운: 연속 손실 ≥ max_consecutive_losses → cooldown_periods 동안 거래 차단
- 일일 거래 횟수 제한: max_daily_trades 초과 시 당일 거래 차단 (0=무제한)
"""
import logging
from collections import deque
from typing import Deque, Optional

from src.analysis.strategy_correlation import SignalCorrelationTracker

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """다층 자동 거래 중단 모듈.

    임계값 가이드 (Bybit BTC/USDT 1h 기준, 실데이터 검증):
    ────────────────────────────────────────────────────────────
    파라미터                   기본값    실데이터 권장 범위    비고
    daily_drawdown_limit      0.03      0.02~0.05           config.yaml risk.max_daily_loss
    total_drawdown_limit      0.15      0.10~0.20           config.yaml risk.max_drawdown 기반
    atr_surge_multiplier      2.0       1.5~3.0             BTC 1h ATR 평균 ~1.5%, surge ≥ 3%
    flash_crash_pct           0.10      0.08~0.15           config.yaml risk.flash_crash_pct
    rapid_decline_pct         0.05      0.03~0.07           5분봉 기준; 1h봉이면 0.05 적정
    rapid_decline_window      5         3~10                캔들 수, timeframe에 비례
    rapid_decline_cooldown    30        10~60               캔들 단위, 5분봉=2.5h, 1h봉=30h
    max_consecutive_losses    5         3~7                 config.yaml risk.max_consecutive_losses
    cooldown_periods          3         2~5                 트레이드 횟수 단위
    max_daily_trades          0         0(무제한)~50        과매매 방지, 0=무제한
    corr_threshold            0.7       0.5~0.8             전략 다양성에 따라 조절

    NOTE: 위 기본값은 Bybit BTC/USDT 실데이터 백테스트에서 검증됨.
    합성 데이터와 실데이터 간 차이가 클 수 있으므로, 새 심볼/timeframe
    적용 시 반드시 해당 데이터로 재검증할 것.
    config.yaml의 risk 섹션에서 오버라이드 가능한 항목은 위 비고 참조.
    """

    def __init__(
        self,
        daily_drawdown_limit: float = 0.03,   # config.yaml risk.max_daily_loss (BTC 1h: 0.02~0.05)
        total_drawdown_limit: float = 0.15,   # config.yaml risk.max_drawdown 기반 (0.10~0.20)
        atr_surge_multiplier: float = 2.0,    # ATR surge 배수 (BTC 1h: 1.5~3.0)
        corr_threshold: float = 0.7,          # 전략 상관계수 ≥ 0.7 → 축소 (0.5~0.8)
        flash_crash_pct: float = 0.10,        # config.yaml risk.flash_crash_pct (0.08~0.15)
        max_consecutive_losses: int = 5,      # config.yaml risk.max_consecutive_losses (3~7)
        cooldown_periods: int = 3,            # 쿨다운 기간 (2~5 트레이드)
        max_daily_trades: int = 0,            # 일일 최대 거래 횟수 (0=무제한, ~50)
        correlation_tracker: Optional[SignalCorrelationTracker] = None,
        rapid_decline_pct: float = 0.05,      # 급속 하락 임계 (BTC 1h: 0.03~0.07)
        rapid_decline_window: int = 5,        # 급속 하락 감지 캔들 수 (3~10)
        rapid_decline_cooldown_periods: int = 30,  # 급속 하락 후 쿨다운 캔들 수 (10~60)
    ):
        self.daily_drawdown_limit = daily_drawdown_limit
        self.total_drawdown_limit = total_drawdown_limit
        self.atr_surge_multiplier = atr_surge_multiplier
        self.corr_threshold = corr_threshold
        self.flash_crash_pct = flash_crash_pct
        self.max_consecutive_losses = max_consecutive_losses
        self.cooldown_periods = cooldown_periods
        self.max_daily_trades = max_daily_trades
        self._correlation_tracker = correlation_tracker
        # 급속 가격 하락 감지 파라미터
        self.rapid_decline_pct = rapid_decline_pct
        self.rapid_decline_window = rapid_decline_window
        self.rapid_decline_cooldown_periods = rapid_decline_cooldown_periods
        # 상태
        self._triggered: bool = False
        self._reason: str = ""
        self._daily_start_balance: float = 0.0
        self._consecutive_losses: int = 0
        self._cooldown_remaining: int = 0
        self._daily_trade_count: int = 0
        # 급속 하락 감지용 가격 히스토리 (close 가격, maxlen=window)
        self._price_history: Deque[float] = deque(maxlen=rapid_decline_window)
        # 급속 하락 쿨다운 (캔들 횟수 단위, 0=비활성)
        self._rapid_decline_cooldown: int = 0

    # ── 급속 가격 하락 감지 ────────────────────────────────────────────────────
    def record_price(self, close_price: float) -> None:
        """새 캔들 close 가격 기록. 급속 하락 쿨다운 카운터도 1 감소.

        호출 시점: 새 캔들 확정 직후 (check() 호출 전).
        """
        if self._rapid_decline_cooldown > 0:
            self._rapid_decline_cooldown -= 1
            if self._rapid_decline_cooldown == 0:
                logger.info("CircuitBreaker: 급속 하락 쿨다운 종료")
        self._price_history.append(close_price)

    def _check_rapid_decline(self) -> Optional[str]:
        """최근 rapid_decline_window 캔들 내 하락이 rapid_decline_pct 이상이면 reason 반환.

        - 쿨다운 활성 중: 즉시 reason 반환 (진입 차단 유지)
        - 신규 감지: 쿨다운 시작 후 reason 반환
        - 미감지: None 반환
        """
        # 기존 쿨다운 활성
        if self._rapid_decline_cooldown > 0:
            return (
                f"급속 가격 하락 쿨다운: 잔여 {self._rapid_decline_cooldown} 캔들 "
                f"(기준 {self.rapid_decline_pct:.1%} / {self.rapid_decline_window}캔들)"
            )

        # 데이터 부족 → 감지 불가
        if len(self._price_history) < 2:
            return None

        oldest = self._price_history[0]
        newest = self._price_history[-1]

        if oldest <= 0:
            return None

        decline = (oldest - newest) / oldest   # 양수 = 하락
        if decline >= self.rapid_decline_pct:
            self._rapid_decline_cooldown = self.rapid_decline_cooldown_periods
            reason = (
                f"급속 가격 하락 감지: {decline:.2%} ≥ 한계 {self.rapid_decline_pct:.2%} "
                f"({len(self._price_history)}캔들 내, "
                f"oldest={oldest:.2f} → newest={newest:.2f}) "
                f"→ {self.rapid_decline_cooldown_periods}캔들 신규 진입 중단"
            )
            logger.warning("CircuitBreaker RAPID DECLINE: %s", reason)
            return reason

        return None

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

    # ── 트레이드 결과 기록 ─────────────────────────────────────────────────────
    def record_trade_result(self, is_loss: bool) -> None:
        """트레이드 결과 기록. 손실 시 연속 손실 카운터 증가, 수익 시 초기화.
        연속 손실이 max_consecutive_losses에 도달하면 쿨다운 시작.
        일일 거래 횟수도 증가시킨다.
        """
        self._daily_trade_count += 1

        if self._cooldown_remaining > 0:
            # 쿨다운 중이어도 수익 발생 시 연속 손실 카운터 즉시 초기화
            if not is_loss:
                self._consecutive_losses = 0
            return

        if is_loss:
            self._consecutive_losses += 1
            logger.info(
                "CircuitBreaker: 연속 손실 %d/%d",
                self._consecutive_losses, self.max_consecutive_losses,
            )
            if self._consecutive_losses >= self.max_consecutive_losses:
                self._cooldown_remaining = self.cooldown_periods
                logger.warning(
                    "CircuitBreaker COOLDOWN 시작: 연속 손실 %d회 → %d 기간 대기",
                    self._consecutive_losses, self.cooldown_periods,
                )
        else:
            if self._consecutive_losses > 0:
                logger.info(
                    "CircuitBreaker: 연속 손실 초기화 (이전 %d회)", self._consecutive_losses
                )
            self._consecutive_losses = 0

    def tick_cooldown(self) -> None:
        """쿨다운 카운터를 1 감소. 쿨다운 종료 시 연속 손실 카운터도 초기화."""
        if self._cooldown_remaining > 0:
            self._cooldown_remaining -= 1
            logger.info(
                "CircuitBreaker: 쿨다운 잔여 %d 기간", self._cooldown_remaining
            )
            if self._cooldown_remaining == 0:
                self._consecutive_losses = 0
                logger.info("CircuitBreaker: 쿨다운 종료, 연속 손실 초기화")

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

        체크 우선순위:
          1. 플래시 크래시 (단일 캔들 ≥ flash_crash_pct)
          2. 낙폭 (일일 / 전체)
          3. 연속 손실 쿨다운
          4. 급속 가격 하락 (최근 N캔들 ≥ rapid_decline_pct) — triggered=True, size_multiplier=0.0
          5. 일일 거래 횟수 제한
          6. ATR 변동성 급등 / 상관관계 급증 (부분 축소, triggered=False)
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

        # ── 연속 손실 쿨다운 체크 ────────────────────────────────────────────
        if self._cooldown_remaining > 0:
            reason = (
                f"연속 손실 쿨다운: {self._consecutive_losses}회 연속 손실, "
                f"잔여 {self._cooldown_remaining} 기간"
            )
            logger.warning("CircuitBreaker COOLDOWN ACTIVE: %s", reason)
            return self._make_result(True, reason, worst, size_multiplier=0.0)

        # ── 급속 가격 하락 체크 ───────────────────────────────────────────────
        rapid_reason = self._check_rapid_decline()
        if rapid_reason is not None:
            return self._make_result(True, rapid_reason, worst, size_multiplier=0.0)

        # ── 일일 거래 횟수 제한 체크 ──────────────────────────────────────────
        if self.max_daily_trades > 0 and self._daily_trade_count >= self.max_daily_trades:
            reason = (
                f"일일 거래 횟수 초과: {self._daily_trade_count}회 ≥ "
                f"한계 {self.max_daily_trades}회"
            )
            logger.warning("CircuitBreaker DAILY TRADE LIMIT: %s", reason)
            return self._make_result(True, reason, worst, size_multiplier=0.0)

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
        self._daily_trade_count = 0
        self._price_history.clear()
        self._rapid_decline_cooldown = 0
        if self._triggered and ("일일" in self._reason or "거래 횟수" in self._reason
                                or "플래시" in self._reason or "급속" in self._reason):
            self._triggered = False
            self._reason = ""
            logger.info("CircuitBreaker: 일일 리셋 완료 (start_balance=%.2f)", daily_start_balance)

    def reset_all(self):
        """전체 상태 초기화."""
        self._triggered = False
        self._reason = ""
        self._consecutive_losses = 0
        self._cooldown_remaining = 0
        self._daily_trade_count = 0
        self._price_history.clear()
        self._rapid_decline_cooldown = 0
        logger.info("CircuitBreaker: 전체 리셋")

    @property
    def is_triggered(self) -> bool:
        return self._triggered

    @property
    def consecutive_losses(self) -> int:
        return self._consecutive_losses

    @property
    def cooldown_remaining(self) -> int:
        return self._cooldown_remaining

    @property
    def daily_trade_count(self) -> int:
        return self._daily_trade_count

    @property
    def rapid_decline_cooldown(self) -> int:
        return self._rapid_decline_cooldown

    # ── 직렬화 ────────────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        """현재 상태를 직렬화 가능한 dict로 반환."""
        return {
            "triggered": self._triggered,
            "reason": self._reason,
            "consecutive_losses": self._consecutive_losses,
            "cooldown_remaining": self._cooldown_remaining,
            "daily_trade_count": self._daily_trade_count,
            "rapid_decline_cooldown": self._rapid_decline_cooldown,
        }

    def from_dict(self, state: dict) -> None:
        """to_dict()로 저장한 상태 복원."""
        self._triggered = bool(state.get("triggered", False))
        self._reason = str(state.get("reason", ""))
        self._consecutive_losses = int(state.get("consecutive_losses", 0))
        self._cooldown_remaining = int(state.get("cooldown_remaining", 0))
        self._daily_trade_count = int(state.get("daily_trade_count", 0))
        self._rapid_decline_cooldown = int(state.get("rapid_decline_cooldown", 0))
