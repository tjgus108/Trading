"""
Exchange connector: ccxt 기반 거래소 연결 및 주문 실행 레이어.
모든 거래소 접근은 이 모듈을 통한다.
"""

import os
import time
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Optional, List

import ccxt

logger = logging.getLogger(__name__)

# API 호출 강제 타임아웃 (초) — ccxt 자체 timeout과 별도로 스레드 레벨 보호
API_CALL_TIMEOUT = 30


class ExchangeConnector:
    def __init__(self, exchange_name: str, sandbox: bool = True, timeout_ms: int = 15000):
        self.exchange_name = exchange_name
        self.sandbox = sandbox
        self._timeout_ms = timeout_ms
        self._exchange: Optional[ccxt.Exchange] = None
        self._last_balance: Optional[dict] = None
        self._consecutive_failures: int = 0
        self._max_consecutive_failures: int = 5  # 연속 실패 시 halt

    def connect(self) -> None:
        exchange_class = getattr(ccxt, self.exchange_name)
        self._exchange = exchange_class(
            {
                "apiKey": os.environ["EXCHANGE_API_KEY"],
                "secret": os.environ["EXCHANGE_API_SECRET"],
                "enableRateLimit": True,
                "timeout": self._timeout_ms,
                "options": {"fetchCurrencies": False},
            }
        )
        if self.sandbox:
            self._exchange.set_sandbox_mode(True)
        # load_markets도 hang 가능 → 스레드 타임아웃으로 보호
        self._call_with_deadline(self._exchange.load_markets, timeout=API_CALL_TIMEOUT)
        self._consecutive_failures = 0
        logger.info("Connected to %s (sandbox=%s, timeout=%dms)", self.exchange_name, self.sandbox, self._timeout_ms)
        self.check_api_permissions()

    def reconnect(self, max_retries: int = 3) -> bool:
        """거래소 재연결. Exponential backoff 적용. 성공 시 True."""
        for attempt in range(1, max_retries + 1):
            try:
                logger.warning("Reconnecting to %s (attempt %d/%d)...",
                               self.exchange_name, attempt, max_retries)
                self.connect()
                logger.info("Reconnected to %s successfully", self.exchange_name)
                return True
            except Exception as e:
                wait = min(2 ** attempt, 60)
                logger.error("Reconnect attempt %d failed: %s. Waiting %ds...",
                             attempt, str(e)[:100], wait)
                time.sleep(wait)
        logger.critical("Failed to reconnect after %d attempts", max_retries)
        return False

    def sync_positions(self, symbol: str = "BTC/USDT") -> List[dict]:
        """거래소에서 실제 열린 포지션을 조회해 동기화."""
        try:
            positions = self.exchange.fetch_positions([symbol])
            open_pos = [p for p in positions if float(p.get("contracts", 0)) > 0]
            if open_pos:
                logger.warning("Found %d open positions on exchange: %s",
                               len(open_pos),
                               [(p["symbol"], p["side"], p["contracts"]) for p in open_pos])
            return open_pos
        except Exception as e:
            logger.error("sync_positions failed: %s", e)
            return []

    @property
    def is_halted(self) -> bool:
        """연속 API 실패가 임계값을 초과하면 True."""
        return self._consecutive_failures >= self._max_consecutive_failures

    def check_api_permissions(self) -> dict:
        """API Key 권한을 조회하고 출금(withdraw) 권한 유무를 확인한다.

        출금 권한이 감지되면 CRITICAL 경고를 남긴다.
        반환값: {"withdraw": bool, "trade": bool, "read": bool} — 거래소가 제공하는 키
        거래소가 권한 조회를 지원하지 않으면 빈 dict를 반환하고 WARNING을 남긴다.
        """
        try:
            info = self.exchange.fetch_api_key_permissions()
        except (ccxt.NotSupported, AttributeError):
            logger.warning(
                "check_api_permissions: %s does not support fetchApiKeyPermissions — skipping",
                self.exchange_name,
            )
            return {}

        withdraw_enabled = bool(info.get("withdraw", False))
        if withdraw_enabled:
            logger.critical(
                "SECURITY WARNING: API key has WITHDRAW permission enabled on %s. "
                "Revoke withdraw permission immediately to prevent fund loss.",
                self.exchange_name,
            )
        else:
            logger.info(
                "API key permission check passed: no withdraw permission detected on %s",
                self.exchange_name,
            )
        return info


    def health_check(self) -> dict:
        """연결 상태 및 거래소 상태 확인.
        
        반환값: {
            "connected": bool,
            "exchange": str,
            "sandbox": bool,
            "markets_loaded": bool,
            "last_tick": dict or None
        }
        """
        if self._exchange is None:
            return {
                "connected": False,
                "exchange": self.exchange_name,
                "sandbox": self.sandbox,
                "markets_loaded": False,
                "last_tick": None,
            }
        
        try:
            # 시장 정보 확인 (간단한 ping)
            markets_loaded = len(self._exchange.symbols) > 0 if hasattr(self._exchange, 'symbols') else False
            
            logger.debug("health_check: %s is healthy", self.exchange_name)
            return {
                "connected": True,
                "exchange": self.exchange_name,
                "sandbox": self.sandbox,
                "markets_loaded": markets_loaded,
                "last_tick": None,
            }
        except Exception as e:
            logger.warning("health_check failed: %s", str(e))
            return {
                "connected": False,
                "exchange": self.exchange_name,
                "sandbox": self.sandbox,
                "markets_loaded": False,
                "last_tick": None,
            }

    # API 응답 시간 추적
    _LATENCY_WARN_MS = 5000   # 5초 초과 시 경고
    _LATENCY_HALT_MS = 15000  # 15초 초과 시 halt 카운트

    @property
    def exchange(self) -> ccxt.Exchange:
        if self._exchange is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._exchange

    def _call_with_deadline(self, fn, *args, timeout: int = API_CALL_TIMEOUT, **kwargs):
        """fn을 별도 스레드에서 실행하고 timeout초 내 미완료 시 RequestTimeout 발생.

        중요: shutdown(wait=False)로 hang 스레드를 기다리지 않는다.
        with 문은 __exit__에서 wait=True를 하므로 사용하지 않는다.
        """
        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(fn, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            fn_name = getattr(fn, '__name__', str(fn))
            raise ccxt.RequestTimeout(
                f"{fn_name} did not respond within {timeout}s — possible hang"
            )
        finally:
            pool.shutdown(wait=False, cancel_futures=True)

    def _timed_call(self, fn, *args, **kwargs):
        """API 호출을 래핑해 응답 시간 추적 + 강제 타임아웃. 느린 응답 시 경고/halt."""
        start = time.time()
        try:
            result = self._call_with_deadline(fn, *args, timeout=API_CALL_TIMEOUT, **kwargs)
            elapsed_ms = (time.time() - start) * 1000
            if elapsed_ms > self._LATENCY_HALT_MS:
                self._consecutive_failures += 1
                logger.error(
                    "API call %.0fms (>%dms halt threshold): %s [consecutive=%d]",
                    elapsed_ms, self._LATENCY_HALT_MS, fn.__name__,
                    self._consecutive_failures,
                )
            elif elapsed_ms > self._LATENCY_WARN_MS:
                logger.warning(
                    "Slow API call %.0fms (>%dms): %s",
                    elapsed_ms, self._LATENCY_WARN_MS, fn.__name__,
                )
            return result
        except ccxt.RequestTimeout:
            # _call_with_deadline에서 hang 감지 또는 ccxt 자체 타임아웃
            self._consecutive_failures += 1
            elapsed_ms = (time.time() - start) * 1000
            logger.error(
                "API call TIMEOUT after %.0fms: %s [consecutive=%d]",
                elapsed_ms, fn.__name__, self._consecutive_failures,
            )
            raise
        except Exception:
            elapsed_ms = (time.time() - start) * 1000
            logger.debug("API call failed after %.0fms: %s", elapsed_ms, fn.__name__)
            raise

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> list:
        data = self._timed_call(self.exchange.fetch_ohlcv, symbol, timeframe, limit=limit)
        if not data:
            raise ValueError(f"No OHLCV data returned for {symbol} {timeframe}")
        logger.debug("Fetched %d candles for %s %s", len(data), symbol, timeframe)
        return data

    def fetch_balance(self) -> dict:
        """잔고 조회. 실패/타임아웃 시 캐시 반환, 캐시도 없으면 안전 기본값."""
        try:
            result = self._timed_call(self.exchange.fetch_balance)
        except Exception as exc:
            logger.warning("fetch_balance failed: %s", exc)
            if self._last_balance:
                logger.info("Returning cached balance (may be stale)")
                return self._last_balance
            return {"total": {}, "free": {}, "used": {}}
        if not result or not isinstance(result, dict):
            logger.warning("fetch_balance returned unexpected response: %r", result)
            if hasattr(self, "_last_balance") and self._last_balance:
                return self._last_balance
            return {"total": {}, "free": {}, "used": {}}
        self._last_balance = result
        return result

    def fetch_ticker(self, symbol: str) -> dict:
        return self._timed_call(self.exchange.fetch_ticker, symbol)

    _RETRYABLE = (ccxt.NetworkError, ccxt.RequestTimeout)

    def create_order(
        self,
        symbol: str,
        side: str,  # "buy" or "sell"
        amount: float,
        order_type: str = "market",
        price: Optional[float] = None,
        max_retries: int = 2,
        params: Optional[dict] = None,
    ) -> dict:
        # 멱등성 보장: 동일 clientOrderId로 재시도 시 중복 주문 방지
        client_order_id = f"bot_{uuid.uuid4().hex[:16]}"
        logger.info(
            "Submitting %s %s order: %s %.6f @ %s (cid=%s)",
            order_type,
            side,
            symbol,
            amount,
            price or "market",
            client_order_id,
        )
        merged_params = {"clientOrderId": client_order_id}
        if params:
            merged_params.update(params)
        # 연속 실패 시 halt 상태면 주문 거부
        if self.is_halted:
            raise RuntimeError(
                f"Connector halted: {self._consecutive_failures} consecutive failures. "
                f"Call reconnect() to resume."
            )

        last_exc: Exception = RuntimeError("max_retries must be >= 1")
        for attempt in range(1, max_retries + 1):
            try:
                if order_type == "market":
                    order = self.exchange.create_market_order(
                        symbol, side, amount, params=merged_params
                    )
                elif order_type == "limit":
                    if price is None:
                        raise ValueError("price required for limit order")
                    order = self.exchange.create_limit_order(
                        symbol, side, amount, price, params=merged_params
                    )
                else:
                    raise ValueError(f"Unsupported order_type: {order_type}")
                logger.info(
                    "Order submitted: id=%s status=%s filled=%s avg_price=%s cid=%s",
                    order.get("id"), order.get("status"), order.get("filled"),
                    order.get("average"), client_order_id,
                )
                self._consecutive_failures = 0  # 성공 시 리셋
                return order
            except self._RETRYABLE as exc:
                self._consecutive_failures += 1
                last_exc = exc
                logger.warning(
                    "create_order attempt %d/%d failed (%s): %s (cid=%s) [consecutive=%d]",
                    attempt, max_retries, type(exc).__name__, exc,
                    client_order_id, self._consecutive_failures,
                )
                if attempt < max_retries:
                    time.sleep(1)
        raise last_exc

    def fetch_order(self, order_id: str, symbol: str) -> dict:
        return self.exchange.fetch_order(order_id, symbol)

    def cancel_order(self, order_id: str, symbol: str) -> dict:
        logger.warning("Cancelling order %s", order_id)
        return self.exchange.cancel_order(order_id, symbol)

    def wait_for_fill(self, order_id: str, symbol: str, timeout: int = 60,
                      expected_price: Optional[float] = None) -> dict:
        """주문 체결 대기. timeout(초) 초과 시 취소 후 TIMEOUT 반환.

        반환 시 filled/amount를 포함해 partial fill 수량을 보존한다.
        cancel 실패 시에도 최종 주문 상태를 반환한다.

        슬리피지 추적: expected_price 제공 시 actual_price와 비교해 slippage_bps 계산.
        slippage_bps = (actual - expected) / expected * 10000
        """
        deadline = time.time() + timeout
        last_order: dict = {}
        while time.time() < deadline:
            try:
                # fetch_order도 _call_with_deadline로 보호 — hang 방지
                last_order = self._call_with_deadline(
                    self.exchange.fetch_order, order_id, symbol, timeout=10
                )
            except Exception as exc:
                logger.warning("fetch_order failed during wait: %s", exc)
                time.sleep(2)
                continue
            status = last_order.get("status")
            if status == "closed":
                # 체결 시 슬리피지 계산
                if expected_price and expected_price > 0:
                    actual_price = last_order.get("average", 0.0) or expected_price
                    slippage_bps = (actual_price - expected_price) / expected_price * 10000
                    last_order["slippage_bps"] = round(slippage_bps, 2)
                return last_order
            if status == "canceled":
                return last_order
            time.sleep(2)

        # 타임아웃: 취소 시도 후 최종 상태 재확인
        try:
            self.cancel_order(order_id, symbol)
        except Exception as exc:
            logger.warning("cancel_order failed after timeout: %s", exc)

        # 취소 후 최종 상태 확인 (partial fill 보존)
        try:
            last_order = self.fetch_order(order_id, symbol)
        except Exception:
            pass

        filled = last_order.get("filled", 0.0) or 0.0
        result = {
            "status": "timeout",
            "id": order_id,
            "symbol": symbol,
            "filled": filled,
            "amount": last_order.get("amount", 0.0),
            "partial": filled > 0,
        }
        # 부분 체결 시 슬리피지 계산
        if filled > 0 and expected_price and expected_price > 0:
            actual_price = last_order.get("average", 0.0) or expected_price
            slippage_bps = (actual_price - expected_price) / expected_price * 10000
            result["slippage_bps"] = round(slippage_bps, 2)
        return result
