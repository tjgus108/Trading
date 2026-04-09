"""
Paper Trading (모의거래) 모드.
실제 API 호출 없이 신호를 기록하고 가상 P&L 추적.
"""
from dataclasses import dataclass, field
from typing import List, Dict
import time


@dataclass
class PaperTrade:
    timestamp: float
    symbol: str
    action: str  # BUY/SELL
    entry_price: float
    quantity: float
    strategy: str
    confidence: str
    pnl: float = 0.0  # SELL 시 실현 P&L


@dataclass
class PaperAccount:
    initial_balance: float = 10000.0
    balance: float = 10000.0
    positions: Dict[str, float] = field(default_factory=dict)   # symbol → qty
    avg_entry: Dict[str, float] = field(default_factory=dict)   # symbol → avg price
    trades: List[PaperTrade] = field(default_factory=list)
    total_pnl: float = 0.0


class PaperTrader:
    def __init__(self, initial_balance: float = 10000.0, fee_rate: float = 0.001):
        self.account = PaperAccount(
            initial_balance=initial_balance,
            balance=initial_balance,
        )
        self.fee_rate = fee_rate

    def execute_signal(
        self,
        symbol: str,
        action: str,
        price: float,
        quantity: float,
        strategy: str,
        confidence: str,
    ) -> dict:
        """신호를 모의 실행. 실제 API 없음."""
        action = action.upper()
        if action not in ("BUY", "SELL"):
            return {"status": "error", "reason": f"unknown action: {action}"}

        fee = price * quantity * self.fee_rate
        trade = PaperTrade(
            timestamp=time.time(),
            symbol=symbol,
            action=action,
            entry_price=price,
            quantity=quantity,
            strategy=strategy,
            confidence=confidence,
        )

        if action == "BUY":
            cost = price * quantity + fee
            if cost > self.account.balance:
                return {"status": "rejected", "reason": "insufficient balance"}
            self.account.balance -= cost
            prev_qty = self.account.positions.get(symbol, 0.0)
            prev_avg = self.account.avg_entry.get(symbol, 0.0)
            new_qty = prev_qty + quantity
            # 가중평균 진입가
            self.account.avg_entry[symbol] = (
                (prev_avg * prev_qty + price * quantity) / new_qty
            )
            self.account.positions[symbol] = new_qty

        else:  # SELL
            held = self.account.positions.get(symbol, 0.0)
            sell_qty = min(quantity, held)
            if sell_qty <= 0:
                return {"status": "rejected", "reason": "no position to sell"}
            proceeds = price * sell_qty - fee
            avg = self.account.avg_entry.get(symbol, price)
            pnl = (price - avg) * sell_qty - fee
            trade.quantity = sell_qty
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
        return {
            "status": "filled",
            "symbol": symbol,
            "action": action,
            "price": price,
            "quantity": trade.quantity,
            "fee": fee,
            "pnl": trade.pnl,
            "balance": self.account.balance,
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
        return {
            "initial_balance": self.account.initial_balance,
            "current_balance": self.account.balance,
            "total_pnl": self.account.total_pnl,
            "total_return_pct": round(total_return * 100, 4),
            "trade_count": trade_count,
            "sell_count": len(sell_trades),
            "win_rate": round(win_rate, 4),
            "open_positions": dict(self.account.positions),
        }
