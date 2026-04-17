"""
TradeLogger: 세무 신고 및 감사 대비 거래 체결 내역 CSV 로거.

모든 실 체결 거래를 append-only CSV에 기록한다.
포맷: timestamp_utc, symbol, side, order_id, client_order_id,
      price, amount, cost, fee, fee_currency, status, strategy, note
"""

from __future__ import annotations

import csv
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_FIELDS = [
    "timestamp_utc",
    "symbol",
    "side",
    "order_id",
    "client_order_id",
    "price",
    "amount",
    "cost",
    "fee",
    "fee_currency",
    "status",
    "strategy",
    "note",
]


class TradeLogger:
    """append-only CSV 기반 체결 로거. 파일 생성 시 헤더 자동 기록."""

    def __init__(self, csv_path: str | os.PathLike = "logs/trades.csv"):
        self.csv_path = Path(csv_path)
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        if not self.csv_path.exists() or self.csv_path.stat().st_size == 0:
            with self.csv_path.open("w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=_FIELDS).writeheader()

    def log_fill(
        self,
        order: dict,
        symbol: str,
        side: str,
        strategy: str = "",
        note: str = "",
    ) -> None:
        """거래소가 반환한 주문(fill) dict를 CSV에 기록. 예외 내부 흡수."""
        try:
            fee_info = order.get("fee") or {}
            if isinstance(fee_info, list) and fee_info:
                fee_info = fee_info[0]
            row = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "symbol": symbol,
                "side": side,
                "order_id": order.get("id", ""),
                "client_order_id": (order.get("clientOrderId", "")
                                    or (order.get("info", {}).get("clientOrderId", "")
                                        if isinstance(order.get("info"), dict) else "")),
                "price": order.get("average") or order.get("price") or "",
                "amount": order.get("filled") or order.get("amount") or "",
                "cost": order.get("cost") or "",
                "fee": (fee_info or {}).get("cost", "") if isinstance(fee_info, dict) else "",
                "fee_currency": (fee_info or {}).get("currency", "") if isinstance(fee_info, dict) else "",
                "status": order.get("status", ""),
                "strategy": strategy,
                "note": note,
            }
            with self._lock, self.csv_path.open("a", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=_FIELDS).writerow(row)
        except Exception as e:
            logger.warning("TradeLogger.log_fill failed: %s", e)
