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
from typing import Optional, List

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
    avg_execution_time: float = 0.0  # 슬라이스당 평균 실행 시간 (초)
    errors: int = 0  # 슬라이스 실행 중 발생한 에러 수


class TWAPExecutor:
    """TWAP 실행기."""

    _VALID_SIDES = {"buy", "sell"}

    def __init__(
        self,
        n_slices: int = 5,
        interval_seconds: float = 60.0,
        dry_run: bool = True,
        timeout_per_slice: Optional[float] = None,
        max_retries_per_slice: int = 2,
    ) -> None:
        """
        Args:
            n_slices: 분할 횟수
            interval_seconds: 슬라이스 간격 (초)
            dry_run: True이면 실제 주문 없이 시뮬레이션
            timeout_per_slice: 슬라이스당 타임아웃 (초). None이면 무제한.
            max_retries_per_slice: 라이브 모드에서 슬라이스 실패 시 재시도 횟수.
        """
        if n_slices < 1:
            raise ValueError(f"n_slices must be >= 1, got {n_slices}")
        self.n_slices = n_slices
        self.interval_seconds = interval_seconds
        self.dry_run = dry_run
        self.timeout_per_slice = timeout_per_slice
        self.max_retries_per_slice = max_retries_per_slice

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

        Raises:
            ValueError: total_qty <= 0 또는 dry_run에서 price_limit이 None/0
        """
        if total_qty <= 0:
            raise ValueError(f"total_qty must be > 0, got {total_qty}")
        side_lower = side.lower()
        if side_lower not in self._VALID_SIDES:
            raise ValueError(
                f"side must be 'buy' or 'sell', got {side!r}"
            )
        if self.dry_run and (price_limit is None or price_limit <= 0):
            raise ValueError(
                f"price_limit must be > 0 in dry_run mode, got {price_limit}"
            )
        slice_qty = total_qty / self.n_slices
        filled_prices: List[float] = []
        filled_quantities: List[float] = []
        partial_fills = 0
        timeout_occurred = False
        errors = 0
        slice_times: List[float] = []
        start_time = time.time()

        for i in range(self.n_slices):
            _slice_t0 = time.time()
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
                slice_start = time.time()
                slice_success = False
                for attempt in range(1, self.max_retries_per_slice + 1):
                    try:
                        result = connector.place_order(
                            symbol=symbol,
                            side=side,
                            qty=slice_qty,
                            price=price_limit,
                        )
                        if result is None:
                            raise ValueError("connector.place_order returned None (empty orderbook?)")
                        filled_price = result.get("price", price_limit or 0.0)
                        if filled_price is None or filled_price <= 0:
                            logger.warning(
                                "slice %d/%d: invalid price %s in result, using price_limit",
                                i + 1, self.n_slices, filled_price,
                            )
                            filled_price = price_limit or 0.0
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

                        # 슬라이스별 타임아웃 체크
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
                        slice_success = True
                        break  # 성공 시 retry 루프 탈출
                    except Exception as e:
                        logger.error(
                            "slice %d/%d attempt %d/%d failed: %s",
                            i + 1, self.n_slices, attempt,
                            self.max_retries_per_slice, str(e),
                        )
                        if attempt < self.max_retries_per_slice:
                            time.sleep(1)  # 재시도 전 짧은 대기
                if not slice_success:
                    errors += 1
                    logger.error(
                        "slice %d/%d FAILED after %d retries — skipping",
                        i + 1, self.n_slices, self.max_retries_per_slice,
                    )
                if timeout_occurred:
                    break

            slice_times.append(time.time() - _slice_t0)
            # 마지막 슬라이스 후에는 대기 없음
            if i < self.n_slices - 1 and not self.dry_run:
                time.sleep(self.interval_seconds)

        # 결과 계산: 수량 가중 평균 가격 (부분 체결 반영)
        if filled_prices and filled_quantities:
            total_cost = sum(p * q for p, q in zip(filled_prices, filled_quantities))
            total_filled_for_avg = sum(filled_quantities)
            avg_price = total_cost / total_filled_for_avg if total_filled_for_avg > 0 else 0.0
        else:
            avg_price = 0.0
        total_filled = sum(filled_quantities) if filled_quantities else 0.0
        slippage = self.estimate_slippage(total_filled, price_limit or avg_price, side=side)

        avg_exec_time = float(np.mean(slice_times)) if slice_times else 0.0

        return TWAPResult(
            slices_executed=len(filled_prices),
            avg_price=avg_price,
            total_qty=total_qty,
            filled_qty=total_filled,
            estimated_slippage_pct=slippage,
            dry_run=self.dry_run,
            partial_fills=partial_fills,
            timeout_occurred=timeout_occurred,
            avg_execution_time=avg_exec_time,
            errors=errors,
        )

    def estimate_slippage(
        self,
        qty: float,
        price: float,
        daily_volume: Optional[float] = None,
        side: Optional[str] = None,
        spread_bps: float = 0.0,
    ) -> float:
        """Almgren-Chriss 간소화 슬리피지 추정 (비대칭 지원).

        base_slippage = 0.1 * (qty / daily_volume) ** 0.5

        비대칭 보정: buy 주문은 ask쪽 스프레드(+), sell 주문은 bid쪽 스프레드(+)를
        반영해 각각 half-spread를 추가. 이는 시장 충격이 항상 불리한 방향으로
        작용하는 현실을 반영한다.

        daily_volume 없으면 0.0005 (0.05%) 반환.

        Args:
            qty: 주문 수량
            price: 현재 가격
            daily_volume: 일 거래량 (수량 단위). None이면 기본값 사용.
            side: "buy" | "sell" | None. None이면 방향 보정 없이 대칭 추정.
            spread_bps: 현재 bid-ask 스프레드 (basis points). 0이면 무시.

        Returns:
            슬리피지 비율 (소수, e.g. 0.001 = 0.1%). 항상 양수 (불리한 방향).
        """
        if daily_volume is None or daily_volume <= 0:
            base = 0.0005
        else:
            ratio = qty / daily_volume
            base = 0.1 * float(np.sqrt(ratio))

        # half-spread 보정: 스프레드의 절반만큼 추가 (주문이 호가를 건너뛸 때)
        half_spread = (spread_bps / 10000.0) / 2.0 if spread_bps > 0 else 0.0

        # buy/sell 비대칭: buy는 시장 충격이 크고(얇은 ask), sell은 약간 작은 경향
        # 경험적 계수: buy +10%, sell -5% (Almgren 2005 실증)
        if side is not None:
            side_lower = side.lower()
            if side_lower == "buy":
                base *= 1.10  # 매수 시 시장 충격 가중
            elif side_lower == "sell":
                base *= 0.95  # 매도 시 약간 완화

        return base + half_spread

    def execute_with_drawdown_protection(
        self,
        connector,
        symbol: str,
        side: str,
        total_qty: float,
        price_limit: Optional[float] = None,
        drawdown_monitor=None,
    ) -> TWAPResult:
        """DrawdownMonitor 연동 TWAP 실행.

        DrawdownMonitor의 상태에 따라 주문을 거부하거나 사이즈를 축소한다:
          - is_in_cooldown(): 주문 완전 거부 (total_qty=0 → 빈 결과)
          - get_size_multiplier() < 1.0: 사이즈 축소 적용

        Args:
            connector: 거래소 커넥터
            symbol: 심볼
            side: "buy" | "sell"
            total_qty: 원청 총 주문 수량
            price_limit: 제한 가격
            drawdown_monitor: DrawdownMonitor 인스턴스. None이면 제약 없음.

        Returns:
            TWAPResult. 쿨다운 중이면 slices_executed=0, filled_qty=0.

        Raises:
            ValueError: 입력 검증 실패 시
        """
        # DrawdownMonitor 체크
        if drawdown_monitor is not None:
            # 1. 쿨다운 중이면 완전 차단
            if drawdown_monitor.is_in_cooldown():
                logger.warning(
                    "TWAP execute_with_drawdown_protection: cooldown_active, rejecting order"
                )
                return TWAPResult(
                    slices_executed=0,
                    avg_price=0.0,
                    total_qty=total_qty,
                    filled_qty=0.0,
                    estimated_slippage_pct=0.0,
                    dry_run=self.dry_run,
                    partial_fills=0,
                    timeout_occurred=False,
                    avg_execution_time=0.0,
                    errors=1,
                )

            # 2. size_multiplier 적용 (연속 손실 축소 등)
            size_mult = drawdown_monitor.get_size_multiplier()
            adjusted_qty = total_qty * size_mult
            if adjusted_qty < total_qty:
                logger.info(
                    "TWAP execute_with_drawdown_protection: size_multiplier=%.2f, "
                    "qty adjusted %.6f → %.6f",
                    size_mult, total_qty, adjusted_qty,
                )
                total_qty = adjusted_qty

        # 표준 TWAP 실행
        if total_qty <= 0:
            logger.warning(
                "TWAP execute_with_drawdown_protection: total_qty <= 0 after adjustment"
            )
            return TWAPResult(
                slices_executed=0,
                avg_price=0.0,
                total_qty=0.0,
                filled_qty=0.0,
                estimated_slippage_pct=0.0,
                dry_run=self.dry_run,
                partial_fills=0,
                timeout_occurred=False,
                avg_execution_time=0.0,
                errors=1,
            )

        return self.execute(
            connector=connector,
            symbol=symbol,
            side=side,
            total_qty=total_qty,
            price_limit=price_limit,
        )
