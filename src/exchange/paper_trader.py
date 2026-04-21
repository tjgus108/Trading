"""
Paper Trading (모의거래) 모드.
실제 API 호출 없이 신호를 기록하고 가상 P&L 추적.
슬리피지, 부분체결, 타임아웃 시뮬레이션 포함.
RegimeDetector 통합: 매 틱마다 레짐 감지 → 전략 라우팅 + CRISIS 포지션 스케일링.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
import time
import random
import logging

logger = logging.getLogger(__name__)


@dataclass
class PaperTrade:
    timestamp: float
    symbol: str
    action: str  # BUY/SELL
    entry_price: float
    quantity: float
    actual_quantity: float  # 부분체결 경우 다를 수 있음
    strategy: str
    confidence: str
    pnl: float = 0.0  # SELL 시 실현 P&L
    slippage_pct: float = 0.0  # 슬리피지 (%)
    is_partial: bool = False  # 부분체결 여부


@dataclass
class PaperAccount:
    initial_balance: float = 10000.0
    balance: float = 10000.0
    positions: Dict[str, float] = field(default_factory=dict)   # symbol → qty
    avg_entry: Dict[str, float] = field(default_factory=dict)   # symbol → avg price
    trades: List[PaperTrade] = field(default_factory=list)
    total_pnl: float = 0.0


class PaperTrader:
    """
    시뮬레이션 거래 엔진.
    - 슬리피지: BUY/SELL 신호 가격에서 slippage_pct 범위 내 변동
      + 주문 크기(notional value) 비례 시장 충격: √(notional / $10k)
      + 60% adverse 방향 편향 + 40% 랜덤 노이즈
    - 부분체결: 확률 partial_fill_prob로 50~80% 만 채워짐
    - 타임아웃: timeout_prob 확률로 타임아웃 (잔량은 취소됨)
    - RegimeDetector 통합: update_regime(df) 호출 → 레짐 전환 시 콜백 + CRISIS 포지션 스케일링
    """

    def __init__(
        self,
        initial_balance: float = 10000.0,
        fee_rate: float = 0.00055,    # Bybit taker 0.055%
        slippage_pct: float = 0.05,   # 양방향 최대 0.05% (±)
        partial_fill_prob: float = 0.05,  # 부분체결 확률 5%
        timeout_prob: float = 0.01,  # 타임아웃 확률 1%
        regime_detector=None,         # src.ml.regime_detector.RegimeDetector (선택)
        regime_router=None,           # src.strategy.regime_router.RegimeStrategyRouter (선택)
        performance_monitor=None,     # src.risk.performance_tracker.PerformanceMonitor (선택)
    ):
        self.account = PaperAccount(
            initial_balance=initial_balance,
            balance=initial_balance,
        )
        self.fee_rate = fee_rate
        self.slippage_pct = slippage_pct  # 최대 편차 (%)
        self.partial_fill_prob = partial_fill_prob
        self.timeout_prob = timeout_prob

        # ── Regime integration ──────────────────────────────────────────────
        self._regime_detector = regime_detector
        self._regime_router = regime_router
        self._performance_monitor = performance_monitor
        self._current_regime: str = "RANGE"  # 초기 기본값

    # ── Regime interface ────────────────────────────────────────────────────

    def update_regime(self, df) -> str:
        """매 틱/봉마다 호출. RegimeDetector로 레짐을 갱신하고 전환 시 콜백을 발행.

        Parameters
        ----------
        df : pd.DataFrame
            OHLCV DataFrame (high/low/close 필수)

        Returns
        -------
        str
            현재 레짐 ('TREND' | 'RANGE' | 'CRISIS')
        """
        if self._regime_detector is None:
            return self._current_regime

        prev = self._current_regime
        new_regime = self._regime_detector.detect(df)

        if new_regime != prev:
            logger.info("Regime change: %s → %s", prev, new_regime)
            self._current_regime = new_regime

            # PerformanceMonitor 레짐 전환 알림
            if self._performance_monitor is not None:
                try:
                    self._performance_monitor.regime_change_alert(prev, new_regime)
                except Exception as exc:
                    logger.warning("regime_change_alert failed: %s", exc)

        return self._current_regime

    @property
    def current_regime(self) -> str:
        """현재 레짐 문자열 반환."""
        return self._current_regime

    def get_position_scale(self) -> float:
        """현재 레짐에 따른 포지션 배율 반환 (CRISIS=0.5, 나머지=1.0)."""
        if self._regime_detector is not None:
            from src.ml.regime_detector import RegimeDetector
            return RegimeDetector.get_position_scale(self._current_regime)
        return 1.0

    def should_skip_strategy(self, strategy_name: str) -> bool:
        """RegimeStrategyRouter를 통해 현재 레짐에서 전략을 스킵해야 하면 True."""
        if self._regime_router is None:
            return False
        return self._regime_router.should_skip(strategy_name, self._current_regime)

    def get_active_strategies(self) -> List[str]:
        """현재 레짐에서 활성화된 전략 목록 반환."""
        if self._regime_router is None:
            return []
        return self._regime_router.get_active_strategies(self._current_regime)

    # ── Trade execution ──────────────────────────────────────────────────────

    def execute_signal(
        self,
        symbol: str,
        action: str,
        price: float,
        quantity: float,
        strategy: str,
        confidence: str,
    ) -> dict:
        """신호를 모의 실행. 실제 API 없음.

        RegimeDetector 연동 시:
          - CRISIS 레짐: quantity에 0.5 배율 자동 적용
          - RegimeRouter로 skip 판정된 전략은 "skipped" 상태 반환

        Returns:
            - status: "filled" | "partial" | "timeout" | "rejected" | "error" | "skipped"
            - slippage_pct: 실제 체결 가격 대비 슬리피지 (%)
            - actual_quantity: 실제 체결 수량
            - regime: 현재 레짐 (문자열)
        """
        action = action.upper()
        if action not in ("BUY", "SELL"):
            return {"status": "error", "reason": f"unknown action: {action}"}

        # Regime-based strategy skip (BUY만 체크; SELL은 항상 허용)
        if action == "BUY" and self.should_skip_strategy(strategy):
            return {
                "status": "skipped",
                "reason": f"strategy '{strategy}' skipped in regime '{self._current_regime}'",
                "regime": self._current_regime,
            }

        # Regime-based position scaling (BUY만 적용)
        if action == "BUY":
            scale = self.get_position_scale()
            if scale != 1.0:
                quantity = quantity * scale

        # Input validation
        if quantity <= 0:
            return {"status": "rejected", "reason": "quantity must be positive"}
        if price <= 0:
            return {"status": "rejected", "reason": "price must be positive"}

        # 타임아웃 체크
        if random.random() < self.timeout_prob:
            return {"status": "timeout", "reason": "simulated timeout", "symbol": symbol}

        # 부분체결 체크
        is_partial = random.random() < self.partial_fill_prob
        actual_qty = quantity * random.uniform(0.5, 0.8) if is_partial else quantity

        # 슬리피지 계산: 시장 충격 반영 (adverse direction)
        # BUY → 가격 상승 방향, SELL → 가격 하락 방향으로 편향
        # base_slip: 항상 불리한 방향의 기본 슬리피지 (시장 충격)
        # noise: ±random 노이즈 (호가 스프레드 변동)
        # volume_impact: 주문 크기에 비례한 시장 충격 (√ 모델)
        #   - 주문 금액 $10k 기준 impact=1.0, 금액이 커질수록 √비례 증가
        #   - ex) $40k → impact=2.0, $90k → impact=3.0
        order_notional = price * actual_qty
        volume_impact = max(1.0, (order_notional / 10_000) ** 0.5)
        effective_slip = self.slippage_pct * volume_impact
        base_slip = effective_slip * 0.6  # 60%는 adverse 방향 고정
        noise = random.uniform(-effective_slip * 0.4, effective_slip * 0.4)
        if action == "BUY":
            slippage_range = base_slip + noise   # 양수 → 가격 상승 (불리)
        else:
            slippage_range = -(base_slip + noise)  # 음수 → 가격 하락 (불리)
        actual_price = price * (1 + slippage_range / 100)
        # 슬리피지를 basis points (bps)로 계산: (actual - expected) / expected * 10000
        slippage_bps = (actual_price - price) / price * 10000 if price > 0 else 0.0

        fee = actual_price * actual_qty * self.fee_rate
        trade = PaperTrade(
            timestamp=time.time(),
            symbol=symbol,
            action=action,
            entry_price=price,
            quantity=quantity,
            actual_quantity=actual_qty,
            strategy=strategy,
            confidence=confidence,
            slippage_pct=slippage_bps,  # Now in basis points (bps)
            is_partial=is_partial,
        )

        if action == "BUY":
            cost = actual_price * actual_qty + fee
            if cost > self.account.balance:
                return {"status": "rejected", "reason": "insufficient balance"}
            self.account.balance -= cost
            prev_qty = self.account.positions.get(symbol, 0.0)
            prev_avg = self.account.avg_entry.get(symbol, 0.0)
            new_qty = prev_qty + actual_qty
            # 가중평균 진입가
            self.account.avg_entry[symbol] = (
                (prev_avg * prev_qty + actual_price * actual_qty) / new_qty
            )
            self.account.positions[symbol] = new_qty

        else:  # SELL
            held = self.account.positions.get(symbol, 0.0)
            sell_qty = min(actual_qty, held)
            if sell_qty <= 0:
                return {"status": "rejected", "reason": "no position to sell"}
            # 실제 판매량으로 actual_qty와 fee를 재계산
            actual_qty = sell_qty
            fee = actual_price * actual_qty * self.fee_rate
            proceeds = actual_price * sell_qty - fee
            avg = self.account.avg_entry.get(symbol, actual_price)
            pnl = (actual_price - avg) * sell_qty - fee
            trade.actual_quantity = sell_qty
            trade.pnl = pnl
            self.account.balance += proceeds
            self.account.total_pnl += pnl
            new_qty = held - sell_qty
            if new_qty < 1e-9:  # float precision guard
                self.account.positions.pop(symbol, None)
                self.account.avg_entry.pop(symbol, None)
            else:
                self.account.positions[symbol] = new_qty

        self.account.trades.append(trade)
        
        fill_status = "partial" if is_partial else "filled"
        return {
            "status": fill_status,
            "symbol": symbol,
            "action": action,
            "requested_price": price,
            "actual_price": round(actual_price, 8),
            "requested_quantity": quantity,
            "actual_quantity": round(actual_qty, 8),
            "fee": round(fee, 8),
            "pnl": round(trade.pnl, 8),
            "slippage_bps": round(slippage_bps, 2),  # Basis points for accuracy
            "slippage_pct": round(slippage_range, 4),  # % for backwards compatibility
            "balance": round(self.account.balance, 2),
            "regime": self._current_regime,
        }

    def get_summary(self) -> dict:
        """모의거래 요약: total_return%, trade_count, win_rate. slippage in basis points."""
        trades = self.account.trades
        sell_trades = [t for t in trades if t.action == "SELL"]
        win_count = sum(1 for t in sell_trades if t.pnl > 0)
        trade_count = len(trades)
        win_rate = win_count / len(sell_trades) if sell_trades else 0.0
        total_return = (
            (self.account.balance - self.account.initial_balance)
            / self.account.initial_balance
        )
        # 체결된 거래만 통계 (부분체결 포함). slippage는 basis points.
        total_slippage_bps = sum(t.slippage_pct for t in trades) if trades else 0.0
        
        return {
            "initial_balance": self.account.initial_balance,
            "current_balance": round(self.account.balance, 2),
            "total_pnl": round(self.account.total_pnl, 2),
            "total_return_pct": round(total_return * 100, 4),
            "trade_count": trade_count,
            "sell_count": len(sell_trades),
            "win_rate": round(win_rate, 4),
            "avg_slippage_bps": round(total_slippage_bps / len(trades), 2) if trades else 0.0,
            "open_positions": dict(self.account.positions),
            "open_position_value": round(
                sum(self.account.positions.get(sym, 0) * self.account.avg_entry.get(sym, 0) 
                    for sym in self.account.positions),
                2
            ),
        }

    def reset(self) -> None:
        """계좌 초기화 (테스트용)"""
        self.account = PaperAccount(
            initial_balance=self.account.initial_balance,
            balance=self.account.initial_balance,
        )
