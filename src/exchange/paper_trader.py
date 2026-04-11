"""
Paper Trading (모의거래) 모드.
실제 API 호출 없이 신호를 기록하고 가상 P&L 추적.
슬리피지, 부분체결, 타임아웃 시뮬레이션 포함.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time
import random


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
    - 슬리피지: BUY/SELL 신호 가격에서 percent_range 내 변동
    - 부분체결: 확률 partial_fill_prob로 최대 80% 만 채워짐
    - 타임아웃: timeout_prob 확률로 타임아웃 (잔량은 취소됨)
    """
    
    def __init__(
        self,
        initial_balance: float = 10000.0,
        fee_rate: float = 0.001,
        slippage_pct: float = 0.05,  # 양방향 최대 0.05% (±)
        partial_fill_prob: float = 0.05,  # 부분체결 확률 5%
        timeout_prob: float = 0.01,  # 타임아웃 확률 1%
    ):
        self.account = PaperAccount(
            initial_balance=initial_balance,
            balance=initial_balance,
        )
        self.fee_rate = fee_rate
        self.slippage_pct = slippage_pct  # 최대 편차 (%)
        self.partial_fill_prob = partial_fill_prob
        self.timeout_prob = timeout_prob

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
        
        Returns:
            - status: "filled" | "partial" | "timeout" | "rejected" | "error"
            - slippage_pct: 실제 체결 가격 대비 슬리피지 (%)
            - actual_quantity: 실제 체결 수량
        """
        action = action.upper()
        if action not in ("BUY", "SELL"):
            return {"status": "error", "reason": f"unknown action: {action}"}

        # 타임아웃 체크
        if random.random() < self.timeout_prob:
            return {"status": "timeout", "reason": "simulated timeout", "symbol": symbol}

        # 부분체결 체크
        is_partial = random.random() < self.partial_fill_prob
        actual_qty = quantity * random.uniform(0.5, 0.8) if is_partial else quantity

        # 슬리피지 계산: 음수면 BUY에 유리, 양수면 SELL에 유리
        slippage_range = random.uniform(-self.slippage_pct, self.slippage_pct)
        actual_price = price * (1 + slippage_range / 100)

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
            slippage_pct=slippage_range,
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
            if new_qty <= 0:
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
            "slippage_pct": round(slippage_range, 4),
            "balance": round(self.account.balance, 2),
        }

    def get_summary(self) -> dict:
        """모의거래 요약: total_return%, trade_count, win_rate"""
        trades = self.account.trades
        sell_trades = [t for t in trades if t.action == "SELL"]
        win_count = sum(1 for t in sell_trades if t.pnl > 0)
        trade_count = len(trades)
        win_rate = win_count / len(sell_trades) if sell_trades else 0.0
        total_return = (
            (self.account.balance - self.account.initial_balance)
            / self.account.initial_balance
        )
        # 체결된 거래만 통계 (부분체결 포함)
        filled_trades = [t for t in trades if not t.is_partial or t.is_partial]
        total_slippage = sum(t.slippage_pct for t in filled_trades) if filled_trades else 0.0
        
        return {
            "initial_balance": self.account.initial_balance,
            "current_balance": round(self.account.balance, 2),
            "total_pnl": round(self.account.total_pnl, 2),
            "total_return_pct": round(total_return * 100, 4),
            "trade_count": trade_count,
            "sell_count": len(sell_trades),
            "win_rate": round(win_rate, 4),
            "avg_slippage_pct": round(total_slippage / len(filled_trades), 4) if filled_trades else 0.0,
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
