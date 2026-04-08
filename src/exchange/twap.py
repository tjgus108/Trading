"""
TWAP (Time-Weighted Average Price) 실행 알고리즘.

대형 주문을 n_slices개로 균등 분할 → interval_seconds 간격으로 체결.
슬리피지 최소화 목적.

실제 거래소 연결 없이도 동작 (시뮬레이션 모드).
"""

from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TWAPResult:
    """TWAP 실행 결과."""

    slices_executed: int
    avg_price: float
    total_qty: float
    estimated_slippage_pct: float
    dry_run: bool


class TWAPExecutor:
    """TWAP 실행기."""

    def __init__(
        self,
        n_slices: int = 5,
        interval_seconds: float = 60.0,
        dry_run: bool = True,
    ) -> None:
        """
        Args:
            n_slices: 분할 횟수
            interval_seconds: 슬라이스 간격 (초)
            dry_run: True이면 실제 주문 없이 시뮬레이션
        """
        self.n_slices = n_slices
        self.interval_seconds = interval_seconds
        self.dry_run = dry_run

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute(
        self,
        connector,
        symbol: str,
        side: str,
        total_qty: float,
        price_limit: Optional[float] = None,
    ) -> TWAPResult:
        """TWAP 주문 실행.

        Args:
            connector: 거래소 커넥터 (place_order 메서드 보유). dry_run=True면 미사용.
            symbol: 심볼 (e.g. "BTC/USDT")
            side: "buy" | "sell"
            total_qty: 총 주문 수량
            price_limit: 제한 가격 (None이면 시장가)

        Returns:
            TWAPResult
        """
        slice_qty = total_qty / self.n_slices
        filled_prices: list[float] = []

        for i in range(self.n_slices):
            if self.dry_run:
                # 시뮬레이션: price_limit 기준으로 소폭 랜덤 변동
                ref_price = price_limit if price_limit is not None else 0.0
                # 슬리피지 시뮬레이션: ±0.05% 랜덤
                simulated_price = ref_price * (1.0 + np.random.uniform(-0.0005, 0.0005))
                filled_prices.append(simulated_price)
                logger.debug(
                    "[dry_run] slice %d/%d: %s %s %.6f @ %.4f",
                    i + 1,
                    self.n_slices,
                    side,
                    symbol,
                    slice_qty,
                    simulated_price,
                )
            else:
                result = connector.place_order(
                    symbol=symbol,
                    side=side,
                    qty=slice_qty,
                    price=price_limit,
                )
                filled_price = result.get("price", price_limit or 0.0)
                filled_prices.append(filled_price)
                logger.info(
                    "slice %d/%d filled: %s @ %.4f",
                    i + 1,
                    self.n_slices,
                    symbol,
                    filled_price,
                )

            # 마지막 슬라이스 후에는 대기 없음
            if i < self.n_slices - 1 and not self.dry_run:
                time.sleep(self.interval_seconds)

        avg_price = float(np.mean(filled_prices)) if filled_prices else 0.0
        slippage = self.estimate_slippage(total_qty, price_limit or avg_price)

        return TWAPResult(
            slices_executed=len(filled_prices),
            avg_price=avg_price,
            total_qty=total_qty,
            estimated_slippage_pct=slippage,
            dry_run=self.dry_run,
        )

    def estimate_slippage(
        self,
        qty: float,
        price: float,
        daily_volume: Optional[float] = None,
    ) -> float:
        """Almgren-Chriss 간소화 슬리피지 추정.

        slippage = 0.1 * (qty / daily_volume) ** 0.5

        daily_volume 없으면 0.0005 (0.05%) 반환.

        Args:
            qty: 주문 수량
            price: 현재 가격 (미사용, 확장 고려)
            daily_volume: 일 거래량 (수량 단위). None이면 기본값 사용.

        Returns:
            슬리피지 비율 (소수, e.g. 0.001 = 0.1%)
        """
        if daily_volume is None or daily_volume <= 0:
            return 0.0005

        ratio = qty / daily_volume
        return 0.1 * float(np.sqrt(ratio))
