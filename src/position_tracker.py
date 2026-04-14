"""
PositionTracker: 열린 포지션과 일일 P&L 추적.

- 체결 시 포지션 기록
- 청산 시 P&L 계산 및 WORKLOG 기록
- 일일 P&L 요약 → Telegram
- .claude-state/POSITIONS.md 실시간 업데이트
- CircuitBreaker.record_trade_result() 연동
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

POSITIONS_FILE = ".claude-state/POSITIONS.md"


@dataclass
class Position:
    symbol: str
    side: str           # "BUY" | "SELL"
    entry_price: float
    size: float
    stop_loss: float
    take_profit: float
    opened_at: str      # UTC ISO string
    order_id: Optional[str] = None

    def unrealized_pnl(self, current_price: float) -> float:
        if self.side == "BUY":
            return (current_price - self.entry_price) * self.size
        return (self.entry_price - current_price) * self.size

    def to_md_row(self, current_price: Optional[float] = None) -> str:
        upnl = ""
        if current_price is not None:
            upnl = f"  uPnL={self.unrealized_pnl(current_price):+.2f}"
        return (
            f"| {self.symbol} | {self.side} | {self.entry_price:.2f} | "
            f"{self.size:.6f} | {self.stop_loss:.2f} | {self.take_profit:.2f} | "
            f"{self.opened_at}{upnl} |"
        )


@dataclass
class ClosedTrade:
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    opened_at: str
    closed_at: str
    reason: str    # "SL" | "TP" | "MANUAL" | "TIMEOUT"


class DailyPnL:
    def __init__(self):
        self.realized: float = 0.0
        self.trade_count: int = 0
        self.wins: int = 0
        self.losses: int = 0
        self.date: str = self._today()

    def _today(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def record(self, pnl: float) -> None:
        today = self._today()
        if today != self.date:          # 날짜 바뀌면 리셋
            self._reset(today)
        self.realized += pnl
        self.trade_count += 1
        if pnl > 0:
            self.wins += 1
        else:
            self.losses += 1

    def _reset(self, date: str) -> None:
        logger.info("Daily P&L reset for %s (prev: %.2f)", date, self.realized)
        self.realized = 0.0
        self.trade_count = 0
        self.wins = 0
        self.losses = 0
        self.date = date

    def summary(self) -> str:
        win_rate = self.wins / self.trade_count if self.trade_count else 0
        return (
            f"Daily P&L [{self.date}]: {self.realized:+.2f} USDT  "
            f"trades={self.trade_count}  win_rate={win_rate:.0%}"
        )


class PositionTracker:
    def __init__(self):
        self._open: Dict[str, Position] = {}   # symbol → Position
        self._daily = DailyPnL()
        self._history: List[ClosedTrade] = []

    # ── Public API ────────────────────────────────────────────────────────

    def open_position(self, position: Position) -> None:
        self._open[position.symbol] = position
        logger.info("Position opened: %s %s %.6f @ %.2f",
                    position.side, position.symbol, position.size, position.entry_price)
        self._write_positions_file()

    def close_position(
        self,
        symbol: str,
        exit_price: float,
        reason: str = "MANUAL",
        circuit_breaker=None,
        account_balance: float = 0.0,
    ) -> Optional[ClosedTrade]:
        pos = self._open.pop(symbol, None)
        if pos is None:
            logger.warning("close_position: no open position for %s", symbol)
            return None

        if pos.side == "BUY":
            pnl = (exit_price - pos.entry_price) * pos.size
        else:
            pnl = (pos.entry_price - exit_price) * pos.size

        trade = ClosedTrade(
            symbol=symbol,
            side=pos.side,
            entry_price=pos.entry_price,
            exit_price=exit_price,
            size=pos.size,
            pnl=pnl,
            opened_at=pos.opened_at,
            closed_at=datetime.now(timezone.utc).isoformat(),
            reason=reason,
        )
        self._history.append(trade)
        self._daily.record(pnl)

        if circuit_breaker and account_balance > 0:
            circuit_breaker.record_trade_result(pnl, account_balance)

        logger.info("Position closed: %s pnl=%+.2f reason=%s", symbol, pnl, reason)
        self._write_positions_file()
        return trade

    def has_position(self, symbol: str) -> bool:
        return symbol in self._open

    def get_position(self, symbol: str) -> Optional[Position]:
        return self._open.get(symbol)

    def daily_summary(self) -> str:
        return self._daily.summary()

    def open_count(self) -> int:
        return len(self._open)

    def today_pnl(self) -> float:
        return self._daily.realized

    # ── File persistence ──────────────────────────────────────────────────

    def _write_positions_file(self) -> None:
        try:
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            lines = [
                "# Open Positions",
                f"\n_Last updated: {ts}_",
                "\n## Active Positions",
            ]
            if self._open:
                lines.append("| Symbol | Side | Entry | Size | SL | TP | Opened |")
                lines.append("|---|---|---|---|---|---|---|")
                for pos in self._open.values():
                    lines.append(pos.to_md_row())
            else:
                lines.append("(none)")

            lines.append("\n## Today's P&L")
            lines.append(self._daily.summary())

            lines.append("\n## Closed Today")
            today = self._daily.date
            today_trades = [t for t in self._history if t.closed_at.startswith(today)]
            if today_trades:
                for t in today_trades[-10:]:  # 최근 10개만
                    lines.append(
                        f"- {t.side} {t.symbol}  entry={t.entry_price:.2f}"
                        f"  exit={t.exit_price:.2f}  pnl={t.pnl:+.2f}  [{t.reason}]"
                    )
            else:
                lines.append("(none)")

            with open(POSITIONS_FILE, "w") as f:
                f.write("\n".join(lines) + "\n")
        except OSError as e:
            logger.warning("Could not write positions file: %s", e)
