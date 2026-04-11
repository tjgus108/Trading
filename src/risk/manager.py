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
from typing import Optional

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
    """하드코딩된 서킷 브레이커. LLM 판단 없이 규칙으로만 동작."""

    def __init__(
        self,
        max_daily_loss: float,
        max_drawdown: float,
        max_consecutive_losses: int = 5,
        flash_crash_pct: float = 0.10,
    ):
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.max_consecutive_losses = max_consecutive_losses
        self.flash_crash_pct = flash_crash_pct
        self._daily_loss: float = 0.0
        self._peak_balance: float = 0.0
        self._consecutive_losses: int = 0

    def check(
        self,
        current_balance: float,
        last_candle_pct_change: float,
    ) -> Optional[str]:
        """위반 시 사유 문자열 반환, 정상이면 None."""
        if self._peak_balance == 0:
            self._peak_balance = current_balance

        self._peak_balance = max(self._peak_balance, current_balance)
        drawdown = (self._peak_balance - current_balance) / self._peak_balance

        if self._daily_loss >= self.max_daily_loss:
            return f"daily_loss {self._daily_loss:.2%} >= limit {self.max_daily_loss:.2%}"
        if drawdown >= self.max_drawdown:
            return f"drawdown {drawdown:.2%} >= limit {self.max_drawdown:.2%}"
        if self._consecutive_losses >= self.max_consecutive_losses:
            return f"consecutive_losses {self._consecutive_losses} >= {self.max_consecutive_losses}"
        if abs(last_candle_pct_change) >= self.flash_crash_pct:
            return f"flash crash detected: {last_candle_pct_change:.2%} move"
        return None

    def record_trade_result(self, pnl: float, account_balance: float) -> None:
        if pnl < 0:
            self._daily_loss += abs(pnl) / account_balance
            self._consecutive_losses += 1
        else:
            self._consecutive_losses = 0

    def reset_daily(self) -> None:
        self._daily_loss = 0.0
        self._consecutive_losses = 0


class RiskManager:
    def __init__(
        self,
        risk_per_trade: float = 0.01,      # 계좌 대비 1%
        atr_multiplier_sl: float = 1.5,    # 손절: ATR * 1.5
        atr_multiplier_tp: float = 3.0,    # 익절: ATR * 3.0
        max_position_size: float = 0.10,   # 계좌 대비 최대 10%
        circuit_breaker: Optional[CircuitBreaker] = None,
        jitter_pct: float = 0.0,  # ±jitter_pct 랜덤 노이즈 (0~0.05)
    ):
        self.risk_per_trade = risk_per_trade
        self.atr_multiplier_sl = atr_multiplier_sl
        self.atr_multiplier_tp = atr_multiplier_tp
        self.max_position_size = max_position_size
        self.circuit_breaker = circuit_breaker
        self.jitter_pct = max(0.0, min(jitter_pct, 0.05))  # 상한 5%

    # ── 변동성 체제(regime)별 ATR multiplier ─────────────────────────────────

    @staticmethod
    def adaptive_stop_multiplier(
        df: Optional[pd.DataFrame],
        window: int = 20,
        annualization: int = 252 * 24,  # 1h 기준
        low_vol_threshold: float = 0.3,
        high_vol_threshold: float = 0.6,
    ) -> float:
        """최근 realized_vol 기반으로 ATR SL multiplier를 자동 조정.

        realized_vol = std(log_returns, window) * sqrt(annualization)

        - vol < low_vol_threshold  → 1.2  (저변동: 타이트)
        - low <= vol < high        → 1.5  (중변동: 기본)
        - vol >= high_vol_threshold → 2.5  (고변동: 넓게)

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

        logger.debug(
            "adaptive_stop_multiplier: realized_vol=%.4f → multiplier=%.1f",
            realized_vol, mult,
        )
        return mult

    def reset_daily(self) -> None:
        """자정 리셋: 일일 손실 초기화."""
        if self.circuit_breaker:
            self.circuit_breaker.reset_daily()

    def evaluate(
        self,
        action: str,           # "BUY" | "SELL" | "HOLD"
        entry_price: float,
        atr: float,
        account_balance: float,
        last_candle_pct_change: float = 0.0,
        candle_df: Optional[pd.DataFrame] = None,  # adaptive multiplier용
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

        # 포지션 사이징 (candle_df 있으면 adaptive multiplier, 없으면 config 값 사용)
        if candle_df is not None:
            sl_mult = self.adaptive_stop_multiplier(candle_df)
        else:
            sl_mult = self.atr_multiplier_sl
        sl_distance = atr * sl_mult
        risk_amount = account_balance * self.risk_per_trade
        position_size = risk_amount / sl_distance

        # 최대 포지션 한도 클램프
        max_size = (account_balance * self.max_position_size) / entry_price
        position_size = min(position_size, max_size)

        # 주문 지터: 봇의 예측 가능한 패턴 노출 방지 (AMM 착취 대응)
        if self.jitter_pct > 0.0:
            noise = random.uniform(-self.jitter_pct, self.jitter_pct)
            position_size = position_size * (1.0 + noise)
            position_size = min(position_size, max_size)  # 클램프 재적용
            logger.debug("Order jitter applied: noise=%.4f%%", noise * 100)

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
