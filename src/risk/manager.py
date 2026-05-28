"""
RiskManager: 포지션 사이징, 서킷 브레이커, 한도 체크.
risk-agent가 이 모듈을 사용한다.
LLM이 직접 수치를 계산하지 않고 이 코드가 처리한다.
"""

import logging
import math
import random
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional, Union

from src.strategy.base import SessionType, is_active_session

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class RiskStatus(Enum):
    APPROVED = "APPROVED"
    BLOCKED = "BLOCKED"


@dataclass
class RiskResult:
    status: RiskStatus
    reason: Optional[str]
    position_size: Optional[float]    # units
    stop_loss: Optional[float]        # price
    take_profit: Optional[float]      # price
    risk_amount: Optional[float]      # USD
    portfolio_exposure: Optional[float]  # 0~1

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "reason": self.reason,
            "position_size": self.position_size,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "risk_amount": self.risk_amount,
            "portfolio_exposure": self.portfolio_exposure,
        }


class CircuitBreaker:
    """하드코딩된 서킷 브레이커. LLM 판단 없이 규칙으로만 동작.

    Note: circuit_breaker.py의 CircuitBreaker는 더 복잡한 기능(rapid_decline,
    ATR surge, correlation throttle, tick_cooldown 등)을 갖추고 있지만 현재
    미사용 상태. orchestrator.py는 이 클래스를 사용. 통합 검토 시 이 클래스를
    circuit_breaker.py로 교체하거나 인터페이스를 맞춰야 함.
    """

    def __init__(
        self,
        max_daily_loss: float,
        max_drawdown: float,
        max_consecutive_losses: int = 5,
        flash_crash_pct: float = 0.10,
        flash_crash_window: int = 15,  # 15 minutes window for flash crash detection
    ):
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.max_consecutive_losses = max_consecutive_losses
        self.flash_crash_pct = flash_crash_pct
        self.flash_crash_window = flash_crash_window  # minutes
        self._daily_loss: float = 0.0
        self._peak_balance: float = 0.0
        self._consecutive_losses: int = 0
        
        # Flash crash protection: track price history over 15min window
        self._price_history: list = []  # [(timestamp, price), ...]
        self._flash_crash_triggered: bool = False
        self._flash_crash_cooldown: int = 0  # Blocks new entries for N candles after crash

    def check(
        self,
        current_balance: float,
        last_candle_pct_change: float,
        current_price: Optional[float] = None,
        timestamp: Optional[float] = None,
    ) -> Optional[str]:
        """위반 시 사유 문자열 반환, 정상이면 None."""
        if self._peak_balance <= 0:
            self._peak_balance = current_balance if current_balance > 0 else 1.0

        self._peak_balance = max(self._peak_balance, current_balance)
        drawdown = (self._peak_balance - current_balance) / self._peak_balance if self._peak_balance > 0 else 0.0

        if self._daily_loss >= self.max_daily_loss:
            return f"daily_loss {self._daily_loss:.2%} >= limit {self.max_daily_loss:.2%}"
        if drawdown >= self.max_drawdown:
            return f"drawdown {drawdown:.2%} >= limit {self.max_drawdown:.2%}"
        if self._consecutive_losses >= self.max_consecutive_losses:
            return f"consecutive_losses {self._consecutive_losses} >= {self.max_consecutive_losses}"
        # Single-candle flash crash (immediate detection)
        if last_candle_pct_change <= -self.flash_crash_pct:
            self._flash_crash_triggered = True
            self._flash_crash_cooldown = 60  # Block new entries for 60 candles
            return f"flash crash detected: {last_candle_pct_change:.2%} move"
        
        # 15-minute window flash crash detection
        if current_price is not None and timestamp is not None:
            self._update_price_history(timestamp, current_price)
            window_pct = self._calculate_window_decline()
            if window_pct <= -self.flash_crash_pct:
                self._flash_crash_triggered = True
                self._flash_crash_cooldown = 60
                return f"flash crash in {self.flash_crash_window}min window: {window_pct:.2%} decline"
        
        # Cooldown countdown
        if self._flash_crash_cooldown > 0:
            self._flash_crash_cooldown -= 1
            if self._flash_crash_cooldown == 0:
                self._flash_crash_triggered = False
        
        return None
    
    def _update_price_history(self, timestamp: float, price: float) -> None:
        """Track price history for 15-minute window."""
        import time
        current_time = time.time() if timestamp == 0 else timestamp
        window_seconds = self.flash_crash_window * 60
        
        # Add new price
        self._price_history.append((current_time, price))
        
        # Remove old prices outside window
        self._price_history = [
            (t, p) for t, p in self._price_history
            if current_time - t <= window_seconds
        ]
    
    def _calculate_window_decline(self) -> float:
        """Calculate max % decline over flash crash window."""
        if len(self._price_history) < 2:
            return 0.0
        
        highest = max(p for _, p in self._price_history)
        lowest = min(p for _, p in self._price_history)
        
        if highest <= 0:
            return 0.0
        
        return (lowest - highest) / highest

    def record_trade_result(self, pnl: float, account_balance: float) -> None:
        if pnl < 0:
            self._daily_loss += abs(pnl) / account_balance
            self._consecutive_losses += 1
        else:
            self._consecutive_losses = 0

    def reset_daily(self) -> None:
        self._daily_loss = 0.0
        self._consecutive_losses = 0


class FullCircuitBreakerAdapter:
    """circuit_breaker.CircuitBreaker(풀버전)을 RiskManager의 레거시 CB 인터페이스로 어댑트.

    사용법:
        from src.risk.circuit_breaker import CircuitBreaker as FullCB
        full_cb = FullCB(daily_drawdown_limit=0.03, total_drawdown_limit=0.15)
        adapter = FullCircuitBreakerAdapter(full_cb, initial_balance=10_000)
        risk_mgr = RiskManager(circuit_breaker=adapter)
    """

    def __init__(self, full_cb, initial_balance: float):
        self._cb = full_cb
        self._peak_balance: float = initial_balance
        self._daily_start_balance: float = initial_balance

    def check(
        self,
        current_balance: float,
        last_candle_pct_change: float,
        current_price: Optional[float] = None,
        timestamp: Optional[float] = None,
    ) -> Optional[str]:
        self._peak_balance = max(self._peak_balance, current_balance)

        candle_open = candle_close = None
        if last_candle_pct_change != 0.0 and current_price is not None and current_price > 0:
            candle_close = current_price
            denom = 1.0 + last_candle_pct_change
            candle_open = current_price / denom if denom != 0 else None

        result = self._cb.check(
            current_balance=current_balance,
            peak_balance=self._peak_balance,
            daily_start_balance=self._daily_start_balance,
            candle_open=candle_open,
            candle_close=candle_close,
        )
        return result["reason"] if result["triggered"] else None

    def record_trade_result(self, pnl: float, account_balance: float) -> None:
        self._cb.record_trade_result(is_loss=(pnl < 0))

    def reset_daily(self, new_daily_start: Optional[float] = None) -> None:
        if new_daily_start is not None:
            self._daily_start_balance = new_daily_start
        self._cb.reset_daily(self._daily_start_balance)


class RiskManager:
    def __init__(
        self,
        risk_per_trade: float = 0.01,      # 계좌 대비 1%
        atr_multiplier_sl: float = 1.5,    # 손절: ATR * 1.5
        atr_multiplier_tp: float = 3.0,    # 익절: ATR * 3.0
        max_position_size: float = 0.10,   # 계좌 대비 최대 10%
        circuit_breaker: Optional[CircuitBreaker] = None,
        jitter_pct: float = 0.0,  # ±jitter_pct 랜덤 노이즈 (0~0.05)
        session_filter: bool = False,  # True 시 세션별 포지션 축소 활성화
        max_total_exposure: float = 0.30,  # 다중 포지션 총 노출 한도 (계좌 대비 30%)
        kelly_sizer: Optional[object] = None,   # KellySizer — CF-VaR 포지션 한도용
        drawdown_monitor: Optional[object] = None,  # DrawdownMonitor — trailing stop 신호용
        portfolio_optimizer: Optional[object] = None,  # PortfolioOptimizer — CF-VaR 한도 계산용
    ):
        if not (0 < risk_per_trade <= 1.0):
            raise ValueError(f"risk_per_trade must be in (0, 1.0], got {risk_per_trade}")
        if atr_multiplier_sl <= 0:
            raise ValueError(f"atr_multiplier_sl must be > 0, got {atr_multiplier_sl}")
        if atr_multiplier_tp <= 0:
            raise ValueError(f"atr_multiplier_tp must be > 0, got {atr_multiplier_tp}")
        if not (0 < max_position_size <= 1.0):
            raise ValueError(f"max_position_size must be in (0, 1.0], got {max_position_size}")
        if not (0 < max_total_exposure <= 1.0):
            raise ValueError(f"max_total_exposure must be in (0, 1.0], got {max_total_exposure}")
        self.risk_per_trade = risk_per_trade
        self.atr_multiplier_sl = atr_multiplier_sl
        self.atr_multiplier_tp = atr_multiplier_tp
        self.max_position_size = max_position_size
        self.circuit_breaker = circuit_breaker
        self.jitter_pct = max(0.0, min(jitter_pct, 0.05))  # 상한 5%
        self.session_filter = session_filter
        self.max_total_exposure = max_total_exposure
        self.kelly_sizer = kelly_sizer
        self.drawdown_monitor = drawdown_monitor
        self.portfolio_optimizer = portfolio_optimizer

    # ── 변동성 체제(regime)별 ATR multiplier ─────────────────────────────────

    # 레짐별 stop multiplier 하한/상한 테이블
    _REGIME_STOP_BOUNDS: dict = {
        # (floor, ceiling)  — None = no bound
        "TREND_UP":   (None, 1.5),   # 상승 추세: 최대 1.5 (타이트)
        "BULL":       (None, 1.5),
        "TREND_DOWN": (2.0,  None),  # 하락 추세: 최소 2.0 (잡음 흡수)
        "BEAR":       (2.0,  None),
        "CRISIS":     (2.5,  None),  # 위기: 최소 2.5 (큰 움직임 허용)
        "HIGH_VOL":   (2.0,  None),
    }

    @staticmethod
    def adaptive_stop_multiplier(
        df: Optional[pd.DataFrame],
        window: int = 20,
        annualization: int = 252 * 24,  # 1h 기준
        low_vol_threshold: float = 0.3,
        high_vol_threshold: float = 0.6,
        regime: Optional[str] = None,
    ) -> float:
        """최근 realized_vol 기반으로 ATR SL multiplier를 자동 조정.

        realized_vol = std(log_returns, window) * sqrt(annualization)

        - vol < low_vol_threshold  → 1.2  (저변동: 타이트)
        - low <= vol < high        → 1.5  (중변동: 기본)
        - vol >= high_vol_threshold → 2.5  (고변동: 넓게)

        regime이 주어지면 레짐별 floor/ceiling 적용:
        - CRISIS/HIGH_VOL → 최소 2.5/2.0 (하한)
        - TREND_UP/BULL   → 최대 1.5 (상한)
        - TREND_DOWN/BEAR → 최소 2.0 (하한)

        df가 None이거나 캔들 수 부족 시 기본값 1.5 반환.
        """
        if df is None or len(df) < 2:
            return 1.5

        closes = df["close"].values[-window:]
        if len(closes) < 2:
            return 1.5

        log_returns = np.diff(np.log(closes.astype(float)))
        std = float(np.std(log_returns, ddof=1))
        realized_vol = std * math.sqrt(annualization)

        if realized_vol < low_vol_threshold:
            mult = 1.2
        elif realized_vol < high_vol_threshold:
            mult = 1.5
        else:
            mult = 2.5

        # 레짐 기반 floor/ceiling 적용
        if regime is not None:
            bounds = RiskManager._REGIME_STOP_BOUNDS.get(regime.upper())
            if bounds is not None:
                floor_val, ceil_val = bounds
                if floor_val is not None:
                    mult = max(mult, floor_val)
                if ceil_val is not None:
                    mult = min(mult, ceil_val)

        logger.debug(
            "adaptive_stop_multiplier: realized_vol=%.4f regime=%s → multiplier=%.1f",
            realized_vol, regime, mult,
        )
        return mult

    def check_total_exposure(
        self,
        open_positions: list,  # list of {"size": float, "price": float}
        account_balance: float,
    ) -> Optional[str]:
        """기존 포지션들의 총 노출이 max_total_exposure 초과 시 사유 반환, 정상이면 None."""
        total = sum(p["size"] * p["price"] for p in open_positions)
        ratio = total / account_balance if account_balance > 0 else 0.0
        if ratio >= self.max_total_exposure:
            return (
                f"total_exposure {ratio:.2%} >= limit {self.max_total_exposure:.2%}"
            )
        return None

    def reset_daily(self) -> None:
        """자정 리셋: 일일 손실 초기화."""
        if self.circuit_breaker:
            self.circuit_breaker.reset_daily()

    # ── Kill Switch 연동 ─────────────────────────────────────────────────────

    def check_strategy_health(
        self,
        strategy_name: str,
        current_mdd: float,
        backtest_mdd: float,
    ) -> dict:
        """전략의 MDD 건강 상태를 확인하고 KILL/CONTINUE 판정을 반환.

        DrawdownMonitor.should_kill_strategy()를 내부에서 호출하여
        현재 MDD가 백테스트 MDD의 1.5배를 초과하면 KILL 권장.

        Args:
            strategy_name: 전략 이름 (로깅용).
            current_mdd: 현재 실시간 MDD (0~1 비율).
            backtest_mdd: 백테스트에서 관측된 MDD (0~1 비율).

        Returns:
            {"action": "KILL", "reason": ..., "strategy": ..., "current_mdd": ..., "threshold": ...}
            또는
            {"action": "CONTINUE", "strategy": ..., "current_mdd": ..., "threshold": ...}
        """
        if self.drawdown_monitor is None:
            logger.warning(
                "check_strategy_health: drawdown_monitor not set — defaulting to CONTINUE"
            )
            return {
                "action": "CONTINUE",
                "strategy": strategy_name,
                "current_mdd": abs(current_mdd),
                "threshold": abs(backtest_mdd) * 1.5,
                "reason": "drawdown_monitor not configured",
            }

        status = self.drawdown_monitor.get_kill_switch_status(
            current_mdd=current_mdd,
            backtest_mdd=backtest_mdd,
        )

        if status["should_kill"]:
            logger.warning(
                "check_strategy_health: KILL %s — MDD %.2f%% > threshold %.2f%%",
                strategy_name, status["current_mdd"] * 100, status["threshold"] * 100,
            )
            return {
                "action": "KILL",
                "reason": "MDD exceeded threshold",
                "strategy": strategy_name,
                "current_mdd": status["current_mdd"],
                "threshold": status["threshold"],
            }

        logger.debug(
            "check_strategy_health: CONTINUE %s — MDD %.2f%% < threshold %.2f%%",
            strategy_name, status["current_mdd"] * 100, status["threshold"] * 100,
        )
        return {
            "action": "CONTINUE",
            "strategy": strategy_name,
            "current_mdd": status["current_mdd"],
            "threshold": status["threshold"],
        }

    # Confidence → 포지션 사이징 배율 (HIGH=1.5x, MEDIUM=1.0x, LOW=0.5x)
    CONFIDENCE_MULTIPLIER = {"HIGH": 1.5, "MEDIUM": 1.0, "LOW": 0.5}

    def evaluate(
        self,
        action: str,           # "BUY" | "SELL" | "HOLD"
        entry_price: float,
        atr: float,
        account_balance: float,
        last_candle_pct_change: float = 0.0,
        candle_df: Optional[pd.DataFrame] = None,  # adaptive multiplier용
        timestamp: Union[datetime, None] = None,  # 세션 필터용 UTC 시각
        open_positions: Optional[list] = None,  # 다중 포지션 total exposure 체크용
        confidence: str = "MEDIUM",  # 전략 신뢰도 → 포지션 사이징 반영
        regime: Optional[str] = None,  # 레짐 → adaptive_stop_multiplier 조정
    ) -> RiskResult:
        if action == "HOLD":
            return RiskResult(
                status=RiskStatus.APPROVED,
                reason="HOLD signal — no order needed",
                position_size=0,
                stop_loss=None,
                take_profit=None,
                risk_amount=0,
                portfolio_exposure=0,
            )

        # 서킷 브레이커 우선 체크
        if self.circuit_breaker:
            block_reason = self.circuit_breaker.check(account_balance, last_candle_pct_change)
            if block_reason:
                logger.warning("Circuit breaker triggered: %s", block_reason)
                return RiskResult(
                    status=RiskStatus.BLOCKED,
                    reason=f"Circuit breaker: {block_reason}",
                    position_size=None,
                    stop_loss=None,
                    take_profit=None,
                    risk_amount=None,
                    portfolio_exposure=None,
                )

        # 다중 포지션 total exposure 체크
        if open_positions:
            exposure_reason = self.check_total_exposure(open_positions, account_balance)
            if exposure_reason:
                logger.warning("Total exposure limit breached: %s", exposure_reason)
                return RiskResult(
                    status=RiskStatus.BLOCKED,
                    reason=f"Total exposure limit: {exposure_reason}",
                    position_size=None,
                    stop_loss=None,
                    take_profit=None,
                    risk_amount=None,
                    portfolio_exposure=None,
                )

        # entry_price 검증: 0 이하면 포지션 사이즈 계산 불가
        if entry_price <= 0 or not math.isfinite(entry_price):
            logger.warning("Invalid entry_price: %.6f — BLOCKED", entry_price)
            return RiskResult(
                status=RiskStatus.BLOCKED,
                reason=f"Invalid entry_price: {entry_price} (must be > 0)",
                position_size=None,
                stop_loss=None,
                take_profit=None,
                risk_amount=None,
                portfolio_exposure=None,
            )

        # account_balance 검증: 0 이하면 노출도 계산 불가
        if account_balance <= 0:
            logger.warning("Invalid account_balance: %.2f — BLOCKED", account_balance)
            return RiskResult(
                status=RiskStatus.BLOCKED,
                reason=f"Invalid account_balance: {account_balance} (must be > 0)",
                position_size=None,
                stop_loss=None,
                take_profit=None,
                risk_amount=None,
                portfolio_exposure=None,
            )

        # ATR 경증증: 0 이하거나 NaN이면 SL 계산 불가
        if not (atr > 0) or not math.isfinite(atr):
            logger.warning("Invalid ATR value: %s — BLOCKED", atr)
            return RiskResult(
                status=RiskStatus.BLOCKED,
                reason=f"Invalid ATR: {atr} (must be finite and > 0)",
                position_size=None,
                stop_loss=None,
                take_profit=None,
                risk_amount=None,
                portfolio_exposure=None,
            )

        # 포지션 사이징 (candle_df 있으면 adaptive multiplier, 없으면 config 값 사용)
        if candle_df is not None:
            sl_mult = self.adaptive_stop_multiplier(candle_df, regime=regime)
        else:
            sl_mult = self.atr_multiplier_sl
        sl_distance = atr * sl_mult
        conf_mult = self.CONFIDENCE_MULTIPLIER.get((confidence or "MEDIUM").upper(), 1.0)
        risk_amount = account_balance * self.risk_per_trade * conf_mult
        position_size = risk_amount / sl_distance

        # 최대 포지션 한도 클램프
        max_size = (account_balance * self.max_position_size) / entry_price
        position_size = min(position_size, max_size)

        # CF-VaR 포지션 한도 적용 (KellySizer + PortfolioOptimizer 모두 있을 때)
        if self.kelly_sizer is not None and self.portfolio_optimizer is not None:
            cf_result = self.kelly_sizer.estimate_cornish_fisher_var()
            if cf_result is not None:
                cf_var = cf_result["cf_var"]
                hist_var = cf_result["hist_var"]
                cf_mult = self.portfolio_optimizer.cf_var_position_limit(
                    cf_var=cf_var,
                    normal_var=hist_var,
                )
                if cf_mult < 1.0:
                    logger.info(
                        "CF-VaR position limit: cf_var=%.4f hist_var=%.4f multiplier=%.2f",
                        cf_var, hist_var, cf_mult,
                    )
                    position_size *= cf_mult
                    max_size *= cf_mult  # 후속 클램프 기준도 동기화

        # 레짐별 Kelly fraction 적용: Quarter-Kelly(0.25) 기준 정규화
        # HIGH_VOL=0.10→0.4x, TREND_DOWN=0.15→0.6x, TREND_UP/BULL=0.25→1.0x
        _kelly_scale = 1.0
        if self.kelly_sizer is not None and regime is not None:
            _kelly_frac = self.kelly_sizer.update_fraction_for_regime(regime)
            _kelly_scale = _kelly_frac / 0.25
            position_size *= _kelly_scale
            max_size *= _kelly_scale
            logger.debug(
                "Kelly regime scale: regime=%s fraction=%.2f scale=%.2f",
                regime, _kelly_frac, _kelly_scale,
            )

        # DrawdownMonitor 통합: MDD 단계별 사이즈 + 연속 손실 쿨다운 + 낙폭 가속 동시 반영
        if self.drawdown_monitor is not None:
            _size_mult = self.drawdown_monitor.get_size_multiplier()
            if _size_mult < 1.0:
                position_size *= _size_mult
                max_size *= _size_mult
                logger.warning(
                    "DrawdownMonitor size_mult=%.2f applied (streak/MDD)", _size_mult
                )
                if regime and regime.upper() in ("HIGH_VOL", "CRISIS") and _kelly_scale < 1.0:
                    logger.warning(
                        "HIGH_VOL compound: kelly_scale=%.2f MDD_mult=%.2f net=%.2f",
                        _kelly_scale, _size_mult, _kelly_scale * _size_mult,
                    )
            if self.drawdown_monitor.trailing_stop_signal():
                position_size *= 0.5
                max_size *= 0.5
                logger.warning("DrawdownMonitor trailing_stop_signal — position_size halved")

        # ATR이 매우 커서 포지션 사이즈가 사실상 0인 경우 BLOCK (< 1e-8 단위)
        if position_size < 1e-8:
            logger.warning("position_size <= 0 after sizing (ATR too large?): atr=%.6f — BLOCKED", atr)
            return RiskResult(
                status=RiskStatus.BLOCKED,
                reason=f"position_size is zero after sizing (ATR={atr} may be abnormally large)",
                position_size=None,
                stop_loss=None,
                take_profit=None,
                risk_amount=None,
                portfolio_exposure=None,
            )

        # 주문 지터: 봇의 예측 가능한 패턴 노출 방지 (AMM 착취 대응)
        if self.jitter_pct > 0.0:
            noise = random.uniform(-self.jitter_pct, self.jitter_pct)
            position_size = position_size * (1.0 + noise)
            position_size = min(position_size, max_size)  # 클램프 재적용
            logger.debug("Order jitter applied: noise=%.4f%%", noise * 100)

        # 세션 필터: REDUCED 세션 → 50% 축소, 주말 → 30% 축소
        if self.session_filter:
            session = is_active_session(timestamp)
            if session == SessionType.REDUCED:
                ts = timestamp
                if ts is None:
                    from datetime import timezone
                    ts = datetime.now(timezone.utc)
                is_weekend = ts.weekday() >= 5
                scale = 0.30 if is_weekend else 0.50
                position_size *= scale
                logger.debug(
                    "Session filter (%s): position_size scaled by %.0f%%",
                    "weekend" if is_weekend else "asia/off-hours", scale * 100,
                )

        if action == "BUY":
            stop_loss = entry_price - sl_distance
            take_profit = entry_price + atr * self.atr_multiplier_tp
        else:  # SELL
            stop_loss = entry_price + sl_distance
            take_profit = entry_price - atr * self.atr_multiplier_tp

        exposure = (position_size * entry_price) / account_balance

        logger.info(
            "Risk approved: size=%.4f SL=%.2f TP=%.2f exposure=%.1f%%",
            position_size,
            stop_loss,
            take_profit,
            exposure * 100,
        )
        return RiskResult(
            status=RiskStatus.APPROVED,
            reason=None,
            position_size=round(position_size, 6),
            stop_loss=round(stop_loss, 2),
            take_profit=round(take_profit, 2),
            risk_amount=round(risk_amount, 2),
            portfolio_exposure=round(exposure, 4),
        )


class SignalCorrelationTracker:
    """전략 시그널 상관관계 모니터링.

    활성 전략 다수가 동시에 같은 방향(BUY/SELL)을 낼 때 경고 로깅.
    live_paper_trader에서 집중 포지션 리스크를 감지하는 데 사용.

    사용법:
        tracker = SignalCorrelationTracker(warn_threshold=0.8)
        tracker.record("BTC/USDT", "StratA", "BUY")
        tracker.record("BTC/USDT", "StratB", "BUY")
        tracker.record("BTC/USDT", "StratC", "SELL")
        tracker.check_and_warn("BTC/USDT")  # 2/3 = 0.67 → 경고 없음 (< 0.8)
    """

    def __init__(self, warn_threshold: float = 0.75, window: int = 1):
        """
        Args:
            warn_threshold: 동일 방향 비율 임계값 (기본 0.75 = 75%).
                            이 비율 이상이면 WARNING 로깅.
            window: 몇 tick 분의 시그널을 집계할지 (기본 1 = 최신 tick만).
        """
        self.warn_threshold = warn_threshold
        self.window = window
        # symbol → {strategy_name: "BUY" | "SELL" | "HOLD"}
        self._signals: dict[str, dict[str, str]] = {}

    def record(self, symbol: str, strategy_name: str, action: str) -> None:
        """시그널 기록. action: "BUY", "SELL", "HOLD"."""
        if symbol not in self._signals:
            self._signals[symbol] = {}
        self._signals[symbol][strategy_name] = action.upper()

    def reset(self, symbol: str) -> None:
        """심볼의 시그널 초기화 (tick 시작 시 호출)."""
        self._signals[symbol] = {}

    def check_and_warn(self, symbol: str) -> Optional[str]:
        """
        동일 방향 비율이 warn_threshold를 초과하면 WARNING 로그 + 방향 반환.

        Returns:
            "BUY" | "SELL" if concentrated, else None.
        """
        sigs = self._signals.get(symbol, {})
        active = {k: v for k, v in sigs.items() if v in ("BUY", "SELL")}
        if len(active) < 2:
            return None

        buy_count = sum(1 for v in active.values() if v == "BUY")
        sell_count = sum(1 for v in active.values() if v == "SELL")
        total = len(active)

        dominant, dominant_count = ("BUY", buy_count) if buy_count >= sell_count else ("SELL", sell_count)
        ratio = dominant_count / total

        if ratio >= self.warn_threshold:
            logger.warning(
                "[SignalCorrelation] %s: %d/%d strategies -> %s (%.0f%% concentration). "
                "Concentrated risk detected.",
                symbol, dominant_count, total, dominant, ratio * 100,
            )
            return dominant
        return None

    def summary(self, symbol: str) -> dict:
        """현재 시그널 분포 요약."""
        sigs = self._signals.get(symbol, {})
        active = {k: v for k, v in sigs.items() if v in ("BUY", "SELL")}
        buy_count = sum(1 for v in active.values() if v == "BUY")
        sell_count = sum(1 for v in active.values() if v == "SELL")
        return {
            "symbol": symbol,
            "total_strategies": len(sigs),
            "active_signals": len(active),
            "buy": buy_count,
            "sell": sell_count,
            "hold": len(sigs) - len(active),
        }


# ── 유틸 함수 (클래스 밖) ──────────────────────────────────────────────────────

def check_parameter_ratio(n_params: int, n_data_points: int, threshold: float = 10.0) -> dict:
    """
    파라미터 수 대비 데이터 포인트 비율 체크.
    n_data_points / n_params < threshold면 과적합 위험.
    """
    ratio = n_data_points / max(n_params, 1)
    return {
        "ratio": ratio,
        "overfitting_risk": ratio < threshold,
        "message": f"데이터/파라미터 비율: {ratio:.1f} (기준: {threshold})"
    }
