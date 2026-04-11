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
    filled_qty: float  # 실제 체결 수량 (부분 체결 반영)
    estimated_slippage_pct: float
    dry_run: bool
    partial_fills: int = 0  # 부분 체결된 슬라이스 개수
    timeout_occurred: bool = False  # 타임아웃 여부


class TWAPExecutor:
    """TWAP 실행기."""

    def __init__(
        self,
        n_slices: int = 5,
        interval_seconds: float = 60.0,
        dry_run: bool = True,
        timeout_per_slice: Optional[float] = None,
    ) -> None:
        """
        Args:
            n_slices: 분할 횟수
            interval_seconds: 슬라이스 간격 (초)
            dry_run: True이면 실제 주문 없이 시뮬레이션
            timeout_per_slice: 슬라이스당 타임아웃 (초). None이면 무제한.
        """
        self.n_slices = n_slices
        self.interval_seconds = interval_seconds
        self.dry_run = dry_run
        self.timeout_per_slice = timeout_per_slice

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
            TWAPResult (부분 체결/타임아웃 정보 포함)
        """
        slice_qty = total_qty / self.n_slices
        filled_prices: list[float] = []
        filled_quantities: list[float] = []
        partial_fills = 0
        timeout_occurred = False
        start_time = time.time()

        for i in range(self.n_slices):
            # 타임아웃 체크
            if self.timeout_per_slice is not None:
                elapsed = time.time() - start_time
                if elapsed > self.timeout_per_slice * self.n_slices:
                    logger.warning(
                        "TWAP timeout: %.2f sec exceeds limit %.2f sec",
                        elapsed,
                        self.timeout_per_slice * self.n_slices,
                    )
                    timeout_occurred = True
                    break

            if self.dry_run:
                # 시뮬레이션: price_limit 기준으로 소폭 랜덤 변동
                ref_price = price_limit if price_limit is not None else 0.0
                # 슬리피지 시뮬레이션: ±0.05% 랜덤
                simulated_price = ref_price * (1.0 + np.random.uniform(-0.0005, 0.0005))
                filled_prices.append(simulated_price)
                # 부분 체결 시뮬레이션 (20% 확률)
                fill_ratio = 1.0 if np.random.random() > 0.2 else np.random.uniform(0.5, 0.99)
                filled_qty = slice_qty * fill_ratio
                filled_quantities.append(filled_qty)
                if fill_ratio < 1.0:
                    partial_fills += 1
                    logger.debug(
                        "[dry_run] slice %d/%d: PARTIAL %s %s %.6f @ %.4f (%.1f%% filled)",
                        i + 1,
                        self.n_slices,
                        side,
                        symbol,
                        filled_qty,
                        simulated_price,
                        fill_ratio * 100,
                    )
                else:
                    logger.debug(
                        "[dry_run] slice %d/%d: %s %s %.6f @ %.4f",
                        i + 1,
                        self.n_slices,
                        side,
                        symbol,
                        filled_qty,
                        simulated_price,
                    )
            else:
                try:
                    slice_start = time.time()
                    result = connector.place_order(
                        symbol=symbol,
                        side=side,
                        qty=slice_qty,
                        price=price_limit,
                    )
                    filled_price = result.get("price", price_limit or 0.0)
                    filled_qty = result.get("filled", slice_qty)  # 부분 체결 반영
                    filled_prices.append(filled_price)
                    filled_quantities.append(filled_qty)

                    if filled_qty < slice_qty - 1e-8:
                        partial_fills += 1
                        logger.warning(
                            "slice %d/%d PARTIAL: %s @ %.4f (%.1f%% filled)",
                            i + 1,
                            self.n_slices,
                            symbol,
                            filled_price,
                            (filled_qty / slice_qty) * 100,
                        )
                    else:
                        logger.info(
                            "slice %d/%d filled: %s @ %.4f",
                            i + 1,
                            self.n_slices,
                            symbol,
                            filled_price,
                        )

                    # 타임아웃 체크
                    if self.timeout_per_slice is not None:
                        slice_elapsed = time.time() - slice_start
                        if slice_elapsed > self.timeout_per_slice:
                            logger.warning(
                                "slice %d timeout: %.2f sec > %.2f sec limit",
                                i + 1,
                                slice_elapsed,
                                self.timeout_per_slice,
                            )
                            timeout_occurred = True
                            break
                except Exception as e:
                    logger.error("slice %d execution failed: %s", i + 1, str(e))
                    timeout_occurred = True
                    break

            # 마지막 슬라이스 후에는 대기 없음
            if i < self.n_slices - 1 and not self.dry_run:
                time.sleep(self.interval_seconds)

        # 결과 계산
        avg_price = (
            float(np.mean(filled_prices)) if filled_prices else 0.0
        )
        total_filled = sum(filled_quantities) if filled_quantities else 0.0
        slippage = self.estimate_slippage(total_filled, price_limit or avg_price)

        return TWAPResult(
            slices_executed=len(filled_prices),
            avg_price=avg_price,
            total_qty=total_qty,
            filled_qty=total_filled,
            estimated_slippage_pct=slippage,
            dry_run=self.dry_run,
            partial_fills=partial_fills,
            timeout_occurred=timeout_occurred,
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
