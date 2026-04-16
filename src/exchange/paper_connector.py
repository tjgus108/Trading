"""
PaperConnector: PaperTrader를 ExchangeConnector 인터페이스에 맞춰 래핑.
실제 거래소 API 대신 모의거래를 실행하며, sandbox/demo 모드로 사용 가능.
"""

import logging
from typing import Optional
from src.exchange.paper_trader import PaperTrader

logger = logging.getLogger(__name__)


class PaperConnector:
    """
    PaperTrader를 ExchangeConnector 호환 인터페이스로 제공.
    - create_order() → PaperTrader.execute_signal()
    - wait_for_fill() → 즉시 반환 (모의거래이므로)
    - fetch_balance() → PaperTrader 잔액 반환
    """
    
    def __init__(
        self,
        symbol: str,
        initial_balance: float = 10000.0,
        fee_rate: float = 0.001,
        slippage_pct: float = 0.05,
        partial_fill_prob: float = 0.05,
        timeout_prob: float = 0.01,
    ):
        self.symbol = symbol
        self.paper_trader = PaperTrader(
            initial_balance=initial_balance,
            fee_rate=fee_rate,
            slippage_pct=slippage_pct,
            partial_fill_prob=partial_fill_prob,
            timeout_prob=timeout_prob,
        )
        logger.info(
            "PaperConnector initialized: symbol=%s, balance=%.2f, slippage=%.2f%%",
            symbol, initial_balance, slippage_pct
        )

    def connect(self) -> None:
        """모의거래는 연결 필요 없음 (no-op)"""
        logger.info("PaperConnector.connect() - no-op for paper trading")

    def fetch_balance(self) -> dict:
        """현재 계좌 잔액 반환 (open position value 포함)"""
        summary = self.paper_trader.get_summary()
        open_value = summary.get("open_position_value", 0.0)
        return {
            "free": summary["current_balance"],
            "used": open_value,
            "total": summary["current_balance"] + open_value,
        }

    def fetch_ticker(self, symbol: str) -> dict:
        """호출 불가 (모의거래에서는 사용 안 함)"""
        raise NotImplementedError("PaperConnector does not support fetch_ticker")

    def create_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        order_type: str = "market",
        price: Optional[float] = None,
    ) -> dict:
        """
        모의 주문 생성.
        
        Args:
            symbol: 거래 쌍 (e.g. "BTC/USDT")
            side: "buy" or "sell"
            amount: 수량
            order_type: "market" or "limit" (현재 둘 다 동일하게 처리)
            price: 가격 (side="sell"일 때 필수)
        
        Returns:
            {"id": order_id, "status": "closed", "filled": amount, ...}
        """
        if price is None:
            raise ValueError(
                "PaperConnector.create_order() requires an explicit price. "
                "Market orders must pass the current market price."
            )
        
        result = self.paper_trader.execute_signal(
            symbol=symbol,
            action=side.upper(),
            price=price,
            quantity=amount,
            strategy="execution",
            confidence="HIGH",
        )
        
        # PaperTrader 반환값을 CCXT 포맷으로 변환
        status = result.get("status")
        if status == "timeout":
            return {
                "id": "paper_order_timeout",
                "symbol": symbol,
                "type": order_type,
                "side": side,
                "price": price,
                "amount": amount,
                "status": "canceled",  # CCXT 호환: timeout은 canceled로 표현
                "filled": 0.0,
                "remaining": amount,
            }
        elif status == "rejected":
            raise ValueError(f"Order rejected: {result.get('reason')}")
        elif status == "error":
            raise ValueError(f"Order error: {result.get('reason')}")
        else:
            # filled or partial
            filled_amt = result.get("actual_quantity", amount)
            return {
                "id": f"paper_order_{int(result.get('timestamp', 0))}",
                "symbol": symbol,
                "type": order_type,
                "side": side,
                "price": result.get("actual_price", price),
                "amount": amount,
                "status": "closed",
                "filled": filled_amt,
                "remaining": amount - filled_amt,
                "info": {
                    "slippage_pct": result.get("slippage_pct", 0.0),
                    "is_partial": result.get("status") == "partial",
                },
            }

    def wait_for_fill(self, order_id: str, symbol: str, timeout: int = 60) -> dict:
        """모의거래는 즉시 체결 (wait 불필요)"""
        logger.debug("PaperConnector.wait_for_fill() - immediate for paper trading")
        return {"status": "closed", "id": order_id, "symbol": symbol, "filled": 0}

    def fetch_order(self, order_id: str, symbol: str) -> dict:
        """호출 불가"""
        raise NotImplementedError("PaperConnector does not support fetch_order")

    def cancel_order(self, order_id: str, symbol: str) -> dict:
        """호출 불가"""
        raise NotImplementedError("PaperConnector does not support cancel_order")

    def get_paper_summary(self) -> dict:
        """모의거래 성과 요약 (보고용)"""
        return self.paper_trader.get_summary()

    def reset_paper_account(self) -> None:
        """모의 계좌 초기화 (테스트용)"""
        self.paper_trader.reset()
