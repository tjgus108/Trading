"""
Exchange 모듈 단위 테스트.

connector.py (ExchangeConnector) + paper_connector.py (PaperConnector) 커버.
실제 거래소 API 호출 없이 mock 사용.

ccxt 라이브러리 import 실패 시에도 mock으로 대체하여 테스트 실행 가능.
"""

import logging
import sys
import time
import types
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# ─────────────────────────────────────────────────────────────
# ccxt mock: ccxt import가 실패하는 환경에서도 테스트 가능하도록
# ─────────────────────────────────────────────────────────────

try:
    import ccxt as _real_ccxt
    HAS_CCXT = True
except (ImportError, OSError):
    HAS_CCXT = False
    # ccxt mock 모듈 생성
    _mock_ccxt = types.ModuleType("ccxt")
    _mock_ccxt.Exchange = type("Exchange", (), {})
    _mock_ccxt.NetworkError = type("NetworkError", (Exception,), {})
    _mock_ccxt.RequestTimeout = type("RequestTimeout", (_mock_ccxt.NetworkError,), {})
    _mock_ccxt.NotSupported = type("NotSupported", (Exception,), {})
    sys.modules["ccxt"] = _mock_ccxt

import ccxt  # noqa: E402 — 이제 실제든 mock이든 import 가능

# connector 모듈 import 전에 ccxt가 sys.modules에 있어야 함
from src.exchange.connector import ExchangeConnector, API_CALL_TIMEOUT  # noqa: E402
from src.exchange.paper_connector import PaperConnector  # noqa: E402


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _make_connector(**overrides) -> ExchangeConnector:
    """mock _exchange가 세팅된 ExchangeConnector 반환."""
    conn = ExchangeConnector.__new__(ExchangeConnector)
    conn.exchange_name = overrides.get("exchange_name", "bybit")
    conn.sandbox = overrides.get("sandbox", True)
    conn._timeout_ms = overrides.get("timeout_ms", 15000)
    conn._exchange = MagicMock()
    conn._last_balance = None
    conn._consecutive_failures = overrides.get("consecutive_failures", 0)
    conn._max_consecutive_failures = overrides.get("max_consecutive_failures", 5)
    return conn


# =============================================================
# ExchangeConnector 초기화
# =============================================================

class TestExchangeConnectorInit:
    """ExchangeConnector 초기화 테스트."""

    def test_init_defaults(self):
        conn = ExchangeConnector("bybit")
        assert conn.exchange_name == "bybit"
        assert conn.sandbox is True
        assert conn._timeout_ms == 15000
        assert conn._exchange is None
        assert conn._consecutive_failures == 0

    def test_init_custom_params(self):
        conn = ExchangeConnector("binance", sandbox=False, timeout_ms=30000)
        assert conn.exchange_name == "binance"
        assert conn.sandbox is False
        assert conn._timeout_ms == 30000


# =============================================================
# exchange 프로퍼티
# =============================================================

class TestExchangeProperty:
    """exchange 프로퍼티 테스트."""

    def test_exchange_property_raises_when_not_connected(self):
        conn = ExchangeConnector("bybit")
        with pytest.raises(RuntimeError, match="Not connected"):
            _ = conn.exchange

    def test_exchange_property_returns_exchange_when_connected(self):
        conn = _make_connector()
        assert conn.exchange is conn._exchange


# =============================================================
# is_halted / consecutive failures
# =============================================================

class TestIsHalted:
    """연속 실패 기반 halt 상태 테스트."""

    def test_not_halted_by_default(self):
        conn = _make_connector()
        assert conn.is_halted is False

    def test_halted_when_failures_reach_threshold(self):
        conn = _make_connector(consecutive_failures=5)
        assert conn.is_halted is True

    def test_not_halted_when_below_threshold(self):
        conn = _make_connector(consecutive_failures=4)
        assert conn.is_halted is False

    def test_halted_boundary_exact_threshold(self):
        conn = _make_connector(consecutive_failures=5, max_consecutive_failures=5)
        assert conn.is_halted is True

    def test_custom_max_failures(self):
        conn = _make_connector(consecutive_failures=3, max_consecutive_failures=3)
        assert conn.is_halted is True

    def test_zero_failures_not_halted(self):
        conn = _make_connector(consecutive_failures=0)
        assert conn.is_halted is False


# =============================================================
# health_check
# =============================================================

class TestHealthCheck:
    """health_check() 테스트."""

    def test_health_check_not_connected(self):
        conn = ExchangeConnector("bybit")
        result = conn.health_check()
        assert result["connected"] is False
        assert result["exchange"] == "bybit"
        assert result["sandbox"] is True
        assert result["markets_loaded"] is False
        assert result["last_tick"] is None

    def test_health_check_connected_with_symbols(self):
        conn = _make_connector()
        conn._exchange.symbols = ["BTC/USDT", "ETH/USDT"]
        result = conn.health_check()
        assert result["connected"] is True
        assert result["markets_loaded"] is True

    def test_health_check_connected_no_symbols(self):
        conn = _make_connector()
        conn._exchange.symbols = []
        result = conn.health_check()
        assert result["connected"] is True
        assert result["markets_loaded"] is False

    def test_health_check_exception_returns_disconnected(self):
        conn = _make_connector()
        type(conn._exchange).symbols = PropertyMock(side_effect=Exception("network err"))
        result = conn.health_check()
        assert result["connected"] is False

    def test_health_check_sandbox_flag_reflected(self):
        conn = _make_connector(sandbox=False)
        conn._exchange = None
        result = conn.health_check()
        assert result["sandbox"] is False


# =============================================================
# _call_with_deadline
# =============================================================

class TestCallWithDeadline:
    """_call_with_deadline() 타임아웃 보호 테스트.

    Note: Python 3.7에서는 ThreadPoolExecutor.shutdown(cancel_futures=True)가
    지원되지 않아 TypeError가 발생할 수 있음. 이 경우 _call_with_deadline을
    mock으로 대체하여 로직만 검증.
    """

    @pytest.fixture(autouse=True)
    def _check_python_version(self):
        """Python 3.9 미만이면 _call_with_deadline 직접 호출 테스트 스킵."""
        import sys
        if sys.version_info < (3, 9):
            pytest.skip("_call_with_deadline uses cancel_futures (Python 3.9+)")

    def test_normal_call_returns_result(self):
        conn = _make_connector()
        result = conn._call_with_deadline(lambda: 42, timeout=5)
        assert result == 42

    def test_timeout_raises_request_timeout(self):
        def slow_fn():
            time.sleep(10)
        conn = _make_connector()
        with pytest.raises(ccxt.RequestTimeout):
            conn._call_with_deadline(slow_fn, timeout=1)

    def test_call_with_positional_args(self):
        def add(a, b):
            return a + b
        conn = _make_connector()
        result = conn._call_with_deadline(add, 3, 4, timeout=5)
        assert result == 7

    def test_exception_propagated(self):
        def failing_fn():
            raise ValueError("bad input")
        conn = _make_connector()
        with pytest.raises(ValueError, match="bad input"):
            conn._call_with_deadline(failing_fn, timeout=5)


# =============================================================
# _timed_call
# =============================================================

class TestTimedCall:
    """_timed_call() 응답 시간 추적 테스트."""

    def test_fast_call_no_failure_increment(self):
        conn = _make_connector()
        conn._call_with_deadline = MagicMock(return_value="ok")
        result = conn._timed_call(MagicMock(__name__="fast_fn"))
        assert result == "ok"
        assert conn._consecutive_failures == 0

    def test_timeout_increments_failures(self):
        conn = _make_connector()
        conn._call_with_deadline = MagicMock(side_effect=ccxt.RequestTimeout("timeout"))
        with pytest.raises(ccxt.RequestTimeout):
            conn._timed_call(MagicMock(__name__="slow_fn"))
        assert conn._consecutive_failures == 1

    def test_other_exception_does_not_increment_failures(self):
        conn = _make_connector()
        conn._call_with_deadline = MagicMock(side_effect=ValueError("bad"))
        with pytest.raises(ValueError):
            conn._timed_call(MagicMock(__name__="bad_fn"))
        assert conn._consecutive_failures == 0


# =============================================================
# _retry
# =============================================================

class TestRetry:
    """_retry() 재시도 로직 테스트."""

    def test_success_on_first_try(self):
        conn = _make_connector()
        conn._timed_call = MagicMock(return_value="data")
        result = conn._retry(MagicMock(), max_retries=3)
        assert result == "data"

    @patch("src.exchange.connector.time.sleep")
    def test_retry_on_network_error(self, mock_sleep):
        conn = _make_connector()
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ccxt.NetworkError("net err")
            return "recovered"

        conn._timed_call = MagicMock(side_effect=side_effect)
        result = conn._retry(MagicMock(), max_retries=3)
        assert result == "recovered"

    @patch("src.exchange.connector.time.sleep")
    def test_retry_exhausted_raises(self, mock_sleep):
        conn = _make_connector()
        conn._timed_call = MagicMock(side_effect=ccxt.NetworkError("persistent"))
        with pytest.raises(ccxt.NetworkError):
            conn._retry(MagicMock(), max_retries=2)
        # 2 retries = 2 failures incremented in _retry
        assert conn._consecutive_failures == 2

    @patch("src.exchange.connector.time.sleep")
    def test_retry_backoff_called(self, mock_sleep):
        """재시도 사이에 backoff sleep이 호출됨."""
        conn = _make_connector()
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ccxt.NetworkError("err")
            return "ok"

        conn._timed_call = MagicMock(side_effect=side_effect)
        conn._retry(MagicMock(), max_retries=3)
        # 2번 실패 후 성공: sleep 2번 호출
        assert mock_sleep.call_count == 2


# =============================================================
# fetch_ohlcv
# =============================================================

class TestFetchOhlcv:
    """fetch_ohlcv() 테스트."""

    def test_returns_data(self):
        conn = _make_connector()
        fake_data = [[1, 100, 110, 90, 105, 500]]
        conn._retry = MagicMock(return_value=fake_data)
        result = conn.fetch_ohlcv("BTC/USDT", "1h", limit=1)
        assert result == fake_data

    def test_empty_data_raises_value_error(self):
        conn = _make_connector()
        conn._retry = MagicMock(return_value=[])
        with pytest.raises(ValueError, match="No OHLCV data"):
            conn.fetch_ohlcv("BTC/USDT", "1h")

    def test_none_data_raises_value_error(self):
        conn = _make_connector()
        conn._retry = MagicMock(return_value=None)
        with pytest.raises((ValueError, TypeError)):
            conn.fetch_ohlcv("BTC/USDT", "1h")


# =============================================================
# fetch_balance
# =============================================================

class TestFetchBalance:
    """fetch_balance() 캐시 및 폴백 테스트."""

    def test_returns_fresh_balance(self):
        conn = _make_connector()
        fake_balance = {"total": {"USDT": 10000}, "free": {"USDT": 10000}, "used": {}}
        conn._timed_call = MagicMock(return_value=fake_balance)
        result = conn.fetch_balance()
        assert result == fake_balance
        assert conn._last_balance == fake_balance

    def test_failure_returns_cached(self):
        conn = _make_connector()
        cached = {"total": {"USDT": 5000}, "free": {"USDT": 5000}, "used": {}}
        conn._last_balance = cached
        conn._timed_call = MagicMock(side_effect=Exception("fail"))
        result = conn.fetch_balance()
        assert result == cached

    def test_failure_no_cache_returns_safe_default(self):
        conn = _make_connector()
        conn._timed_call = MagicMock(side_effect=Exception("fail"))
        result = conn.fetch_balance()
        assert result == {"total": {}, "free": {}, "used": {}}

    def test_none_response_returns_cached(self):
        conn = _make_connector()
        cached = {"total": {"USDT": 3000}, "free": {"USDT": 3000}, "used": {}}
        conn._last_balance = cached
        conn._timed_call = MagicMock(return_value=None)
        result = conn.fetch_balance()
        assert result == cached

    def test_non_dict_response_returns_default(self):
        conn = _make_connector()
        conn._timed_call = MagicMock(return_value="invalid")
        result = conn.fetch_balance()
        assert result == {"total": {}, "free": {}, "used": {}}

    def test_non_dict_response_with_cache_returns_cache(self):
        conn = _make_connector()
        cached = {"total": {"USDT": 1000}, "free": {"USDT": 1000}, "used": {}}
        conn._last_balance = cached
        conn._timed_call = MagicMock(return_value="bad")
        result = conn.fetch_balance()
        assert result == cached


# =============================================================
# fetch_ticker
# =============================================================

class TestFetchTicker:
    """fetch_ticker() 테스트."""

    def test_returns_ticker(self):
        conn = _make_connector()
        fake_ticker = {"last": 65000.0, "symbol": "BTC/USDT"}
        conn._retry = MagicMock(return_value=fake_ticker)
        result = conn.fetch_ticker("BTC/USDT")
        assert result == fake_ticker


# =============================================================
# create_order
# =============================================================

class TestCreateOrder:
    """create_order() 주문 생성 테스트."""

    def test_market_buy_order(self):
        conn = _make_connector()
        fake_order = {"id": "ord1", "status": "closed", "filled": 0.5, "average": 65000.0}
        conn._exchange.create_market_order.return_value = fake_order
        result = conn.create_order("BTC/USDT", "buy", 0.5, order_type="market")
        assert result["id"] == "ord1"
        assert result["status"] == "closed"
        assert conn._consecutive_failures == 0

    def test_market_sell_order(self):
        conn = _make_connector()
        fake_order = {"id": "ord_sell", "status": "closed", "filled": 1.0, "average": 66000.0}
        conn._exchange.create_market_order.return_value = fake_order
        result = conn.create_order("BTC/USDT", "sell", 1.0, order_type="market")
        assert result["id"] == "ord_sell"
        assert result["filled"] == 1.0

    def test_limit_order_requires_price(self):
        conn = _make_connector()
        with pytest.raises(ValueError, match="price required"):
            conn.create_order("BTC/USDT", "buy", 0.5, order_type="limit", price=None)

    def test_limit_order_with_price(self):
        conn = _make_connector()
        fake_order = {"id": "ord2", "status": "open", "filled": 0.0, "average": None}
        conn._exchange.create_limit_order.return_value = fake_order
        result = conn.create_order("BTC/USDT", "buy", 0.5, order_type="limit", price=64000.0)
        assert result["id"] == "ord2"
        conn._exchange.create_limit_order.assert_called_once()

    def test_unsupported_order_type(self):
        conn = _make_connector()
        with pytest.raises(ValueError, match="Unsupported order_type"):
            conn.create_order("BTC/USDT", "buy", 0.5, order_type="stop_limit")

    def test_halted_connector_rejects_order(self):
        conn = _make_connector(consecutive_failures=5)
        with pytest.raises(RuntimeError, match="Connector halted"):
            conn.create_order("BTC/USDT", "buy", 0.5)

    @patch("src.exchange.connector.time.sleep")
    def test_retry_on_network_error_then_success(self, mock_sleep):
        conn = _make_connector()
        conn._exchange.create_market_order.side_effect = [
            ccxt.NetworkError("net"),
            {"id": "ord3", "status": "closed", "filled": 0.5, "average": 65000.0},
        ]
        result = conn.create_order("BTC/USDT", "buy", 0.5, max_retries=2)
        assert result["id"] == "ord3"
        assert conn._consecutive_failures == 0  # 성공 시 리셋

    @patch("src.exchange.connector.time.sleep")
    def test_all_retries_fail_raises(self, mock_sleep):
        conn = _make_connector()
        conn._exchange.create_market_order.side_effect = ccxt.NetworkError("persist")
        with pytest.raises(ccxt.NetworkError):
            conn.create_order("BTC/USDT", "buy", 0.5, max_retries=2)
        assert conn._consecutive_failures == 2

    def test_client_order_id_generated(self):
        conn = _make_connector()
        fake_order = {"id": "ord4", "status": "closed", "filled": 1.0, "average": 65000.0}
        conn._exchange.create_market_order.return_value = fake_order
        conn.create_order("BTC/USDT", "buy", 1.0)
        call_args = conn._exchange.create_market_order.call_args
        params = call_args[1].get("params", {})
        assert "clientOrderId" in params
        assert params["clientOrderId"].startswith("bot_")

    def test_custom_params_merged_with_client_id(self):
        conn = _make_connector()
        fake_order = {"id": "ord5", "status": "closed", "filled": 1.0, "average": 65000.0}
        conn._exchange.create_market_order.return_value = fake_order
        conn.create_order("BTC/USDT", "buy", 1.0, params={"reduceOnly": True})
        call_args = conn._exchange.create_market_order.call_args
        params = call_args[1].get("params", {})
        assert params.get("reduceOnly") is True
        assert "clientOrderId" in params  # client ID도 여전히 포함

    def test_success_resets_consecutive_failures(self):
        conn = _make_connector(consecutive_failures=3)
        fake_order = {"id": "ord6", "status": "closed", "filled": 1.0, "average": 65000.0}
        conn._exchange.create_market_order.return_value = fake_order
        conn.create_order("BTC/USDT", "buy", 1.0)
        assert conn._consecutive_failures == 0


# =============================================================
# fetch_order / cancel_order
# =============================================================

class TestFetchCancelOrder:
    """fetch_order / cancel_order 테스트."""

    def test_fetch_order(self):
        conn = _make_connector()
        fake = {"id": "ord1", "status": "closed"}
        conn._exchange.fetch_order.return_value = fake
        result = conn.fetch_order("ord1", "BTC/USDT")
        assert result == fake

    def test_cancel_order(self):
        conn = _make_connector()
        fake = {"id": "ord1", "status": "canceled"}
        conn._exchange.cancel_order.return_value = fake
        result = conn.cancel_order("ord1", "BTC/USDT")
        assert result == fake


# =============================================================
# wait_for_fill
# =============================================================

class TestWaitForFill:
    """wait_for_fill() 체결 대기 테스트."""

    def test_immediate_fill(self):
        conn = _make_connector()
        conn._call_with_deadline = MagicMock(
            return_value={"id": "ord1", "status": "closed", "average": 65000.0, "filled": 1.0}
        )
        result = conn.wait_for_fill("ord1", "BTC/USDT", timeout=5)
        assert result["status"] == "closed"

    def test_fill_with_slippage_tracking(self):
        conn = _make_connector()
        conn._call_with_deadline = MagicMock(
            return_value={"id": "ord1", "status": "closed", "average": 65100.0, "filled": 1.0}
        )
        result = conn.wait_for_fill("ord1", "BTC/USDT", timeout=5, expected_price=65000.0)
        assert result["status"] == "closed"
        assert "slippage_bps" in result
        expected_bps = round((65100 - 65000) / 65000 * 10000, 2)
        assert abs(result["slippage_bps"] - expected_bps) < 0.1

    def test_fill_without_expected_price_no_slippage(self):
        conn = _make_connector()
        conn._call_with_deadline = MagicMock(
            return_value={"id": "ord1", "status": "closed", "average": 65100.0, "filled": 1.0}
        )
        result = conn.wait_for_fill("ord1", "BTC/USDT", timeout=5)
        assert "slippage_bps" not in result

    def test_canceled_order_returned_immediately(self):
        conn = _make_connector()
        conn._call_with_deadline = MagicMock(
            return_value={"id": "ord1", "status": "canceled", "filled": 0}
        )
        result = conn.wait_for_fill("ord1", "BTC/USDT", timeout=5)
        assert result["status"] == "canceled"

    @patch("src.exchange.connector.time.sleep")
    @patch("src.exchange.connector.time.time")
    def test_timeout_returns_timeout_status(self, mock_time, mock_sleep):
        """타임아웃 시 cancel 시도 후 timeout 상태 반환."""
        conn = _make_connector()
        mock_time.side_effect = [0, 100, 100, 100]
        conn._call_with_deadline = MagicMock(
            return_value={"id": "ord1", "status": "open", "filled": 0, "amount": 1.0}
        )
        conn._exchange.cancel_order.return_value = {}
        conn._exchange.fetch_order.return_value = {
            "id": "ord1", "status": "canceled", "filled": 0, "amount": 1.0
        }
        result = conn.wait_for_fill("ord1", "BTC/USDT", timeout=5)
        assert result["status"] == "timeout"
        assert result["partial"] is False
        assert result["id"] == "ord1"
        assert result["symbol"] == "BTC/USDT"

    @patch("src.exchange.connector.time.sleep")
    @patch("src.exchange.connector.time.time")
    def test_timeout_with_partial_fill_and_slippage(self, mock_time, mock_sleep):
        """타임아웃이지만 부분 체결 + 슬리피지 추적."""
        conn = _make_connector()
        mock_time.side_effect = [0, 100, 100, 100]
        conn._call_with_deadline = MagicMock(
            return_value={"id": "ord1", "status": "open", "filled": 0.3, "amount": 1.0}
        )
        conn._exchange.cancel_order.return_value = {}
        conn._exchange.fetch_order.return_value = {
            "id": "ord1", "status": "canceled", "filled": 0.3, "amount": 1.0, "average": 65050.0
        }
        result = conn.wait_for_fill("ord1", "BTC/USDT", timeout=5, expected_price=65000.0)
        assert result["status"] == "timeout"
        assert result["partial"] is True
        assert result["filled"] == 0.3
        assert "slippage_bps" in result


# =============================================================
# connect + reconnect
# =============================================================

class TestConnectReconnect:
    """connect() / reconnect() 테스트."""

    @patch.dict("os.environ", {"EXCHANGE_API_KEY": "test_key", "EXCHANGE_API_SECRET": "test_secret"})
    @patch("src.exchange.connector.ccxt")
    def test_connect_success(self, mock_ccxt_module):
        mock_exchange = MagicMock()
        mock_ccxt_module.bybit.return_value = mock_exchange
        conn = ExchangeConnector("bybit", sandbox=True)
        conn._call_with_deadline = MagicMock()
        conn.check_api_permissions = MagicMock(return_value={})
        conn.connect()
        assert conn._exchange is mock_exchange
        mock_exchange.set_sandbox_mode.assert_called_once_with(True)
        assert conn._consecutive_failures == 0

    @patch.dict("os.environ", {"EXCHANGE_API_KEY": "k", "EXCHANGE_API_SECRET": "s"})
    @patch("src.exchange.connector.ccxt")
    def test_connect_no_sandbox(self, mock_ccxt_module):
        mock_exchange = MagicMock()
        mock_ccxt_module.binance.return_value = mock_exchange
        conn = ExchangeConnector("binance", sandbox=False)
        conn._call_with_deadline = MagicMock()
        conn.check_api_permissions = MagicMock(return_value={})
        conn.connect()
        mock_exchange.set_sandbox_mode.assert_not_called()

    @patch("src.exchange.connector.time.sleep")
    def test_reconnect_success_first_attempt(self, mock_sleep):
        conn = _make_connector()
        conn.connect = MagicMock()
        result = conn.reconnect(max_retries=3)
        assert result is True
        conn.connect.assert_called_once()

    @patch("src.exchange.connector.time.sleep")
    def test_reconnect_success_second_attempt(self, mock_sleep):
        conn = _make_connector()
        conn.connect = MagicMock(side_effect=[Exception("fail"), None])
        result = conn.reconnect(max_retries=3)
        assert result is True
        assert conn.connect.call_count == 2

    @patch("src.exchange.connector.time.sleep")
    def test_reconnect_fails_all_attempts(self, mock_sleep):
        conn = _make_connector()
        conn.connect = MagicMock(side_effect=Exception("fail"))
        result = conn.reconnect(max_retries=2)
        assert result is False
        assert conn.connect.call_count == 2


# =============================================================
# sync_positions
# =============================================================

class TestSyncPositions:
    """sync_positions() 테스트."""

    def test_returns_open_positions(self):
        conn = _make_connector()
        conn._exchange.fetch_positions.return_value = [
            {"symbol": "BTC/USDT", "side": "long", "contracts": "0.5"},
            {"symbol": "BTC/USDT", "side": "short", "contracts": "0"},
        ]
        result = conn.sync_positions("BTC/USDT")
        assert len(result) == 1
        assert result[0]["contracts"] == "0.5"

    def test_no_open_positions(self):
        conn = _make_connector()
        conn._exchange.fetch_positions.return_value = [
            {"symbol": "BTC/USDT", "side": "long", "contracts": "0"},
        ]
        result = conn.sync_positions("BTC/USDT")
        assert len(result) == 0

    def test_exception_returns_empty_list(self):
        conn = _make_connector()
        conn._exchange.fetch_positions.side_effect = Exception("API error")
        result = conn.sync_positions("BTC/USDT")
        assert result == []

    def test_multiple_open_positions(self):
        conn = _make_connector()
        conn._exchange.fetch_positions.return_value = [
            {"symbol": "BTC/USDT", "side": "long", "contracts": "1.0"},
            {"symbol": "BTC/USDT", "side": "short", "contracts": "0.5"},
        ]
        result = conn.sync_positions("BTC/USDT")
        assert len(result) == 2


# =============================================================
# check_api_permissions
# =============================================================

class TestCheckApiPermissions:
    """check_api_permissions() 테스트."""

    def test_no_withdraw_logs_info(self, caplog):
        conn = _make_connector()
        conn._exchange.fetch_api_key_permissions.return_value = {
            "read": True, "trade": True, "withdraw": False,
        }
        with caplog.at_level(logging.INFO, logger="src.exchange.connector"):
            result = conn.check_api_permissions()
        assert result["withdraw"] is False
        assert any("permission check passed" in m for m in caplog.messages)

    def test_withdraw_enabled_logs_critical(self, caplog):
        conn = _make_connector()
        conn._exchange.fetch_api_key_permissions.return_value = {
            "read": True, "trade": True, "withdraw": True,
        }
        with caplog.at_level(logging.CRITICAL, logger="src.exchange.connector"):
            result = conn.check_api_permissions()
        assert result["withdraw"] is True
        critical_msgs = [m for m in caplog.messages if "WITHDRAW" in m or "SECURITY" in m]
        assert critical_msgs

    def test_not_supported_returns_empty(self, caplog):
        conn = _make_connector()
        conn._exchange.fetch_api_key_permissions.side_effect = ccxt.NotSupported("n/a")
        with caplog.at_level(logging.WARNING, logger="src.exchange.connector"):
            result = conn.check_api_permissions()
        assert result == {}

    def test_attribute_error_returns_empty(self):
        conn = _make_connector()
        conn._exchange.fetch_api_key_permissions.side_effect = AttributeError("no attr")
        result = conn.check_api_permissions()
        assert result == {}


# =============================================================
# _RETRYABLE 프로퍼티
# =============================================================

class TestRetryableProperty:
    """_RETRYABLE 프로퍼티 테스트."""

    def test_retryable_contains_network_error(self):
        conn = _make_connector()
        assert ccxt.NetworkError in conn._RETRYABLE

    def test_retryable_contains_request_timeout(self):
        conn = _make_connector()
        assert ccxt.RequestTimeout in conn._RETRYABLE


# =============================================================
# PaperConnector 테스트
# =============================================================

class TestPaperConnectorInit:
    """PaperConnector 초기화 테스트."""

    def test_default_init(self):
        pc = PaperConnector(symbol="BTC/USDT")
        assert pc.symbol == "BTC/USDT"
        assert pc.paper_trader is not None
        assert pc.paper_trader.account.initial_balance == 10000.0

    def test_custom_init(self):
        pc = PaperConnector(
            symbol="ETH/USDT",
            initial_balance=50000.0,
            fee_rate=0.002,
            slippage_pct=0.1,
        )
        assert pc.symbol == "ETH/USDT"
        assert pc.paper_trader.account.initial_balance == 50000.0
        assert pc.paper_trader.fee_rate == 0.002
        assert pc.paper_trader.slippage_pct == 0.1

    def test_custom_probabilities(self):
        pc = PaperConnector(
            symbol="BTC/USDT",
            partial_fill_prob=0.1,
            timeout_prob=0.05,
        )
        assert pc.paper_trader.partial_fill_prob == 0.1
        assert pc.paper_trader.timeout_prob == 0.05


class TestPaperConnectorConnect:
    """PaperConnector.connect() 테스트."""

    def test_connect_is_noop(self):
        pc = PaperConnector(symbol="BTC/USDT")
        pc.connect()  # 예외 없이 실행


class TestPaperConnectorFetchBalance:
    """PaperConnector.fetch_balance() 테스트."""

    def test_initial_balance(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=10000.0,
            slippage_pct=0.0, partial_fill_prob=0.0, timeout_prob=0.0,
        )
        balance = pc.fetch_balance()
        assert balance["free"] == 10000.0
        assert balance["used"] == 0.0
        assert balance["total"] == 10000.0

    def test_balance_after_buy(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=10000.0,
            fee_rate=0.0, slippage_pct=0.0,
            partial_fill_prob=0.0, timeout_prob=0.0,
        )
        pc.create_order("BTC/USDT", "buy", 1.0, price=1000.0)
        balance = pc.fetch_balance()
        assert balance["free"] == 9000.0
        assert balance["used"] > 0
        assert balance["total"] == balance["free"] + balance["used"]

    def test_balance_after_full_sell(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=10000.0,
            fee_rate=0.0, slippage_pct=0.0,
            partial_fill_prob=0.0, timeout_prob=0.0,
        )
        pc.create_order("BTC/USDT", "buy", 1.0, price=1000.0)
        pc.create_order("BTC/USDT", "sell", 1.0, price=1000.0)
        balance = pc.fetch_balance()
        assert balance["used"] == 0.0
        assert balance["free"] == balance["total"]


class TestPaperConnectorCreateOrder:
    """PaperConnector.create_order() 테스트."""

    def test_buy_order_success(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=50000.0,
            fee_rate=0.0, slippage_pct=0.0,
            partial_fill_prob=0.0, timeout_prob=0.0,
        )
        result = pc.create_order("BTC/USDT", "buy", 1.0, price=10000.0)
        assert result["status"] == "closed"
        assert result["filled"] == 1.0
        assert result["symbol"] == "BTC/USDT"
        assert result["side"] == "buy"

    def test_sell_order_success(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=50000.0,
            fee_rate=0.0, slippage_pct=0.0,
            partial_fill_prob=0.0, timeout_prob=0.0,
        )
        pc.create_order("BTC/USDT", "buy", 1.0, price=10000.0)
        result = pc.create_order("BTC/USDT", "sell", 1.0, price=11000.0)
        assert result["status"] == "closed"
        assert result["filled"] == 1.0

    def test_price_none_raises(self):
        pc = PaperConnector(symbol="BTC/USDT")
        with pytest.raises(ValueError, match="requires an explicit price"):
            pc.create_order("BTC/USDT", "buy", 1.0)

    def test_insufficient_balance_raises(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=100.0,
            slippage_pct=0.0, partial_fill_prob=0.0, timeout_prob=0.0,
        )
        with pytest.raises(ValueError, match="Order rejected"):
            pc.create_order("BTC/USDT", "buy", 1.0, price=50000.0)

    def test_sell_no_position_raises(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=50000.0,
            slippage_pct=0.0, partial_fill_prob=0.0, timeout_prob=0.0,
        )
        with pytest.raises(ValueError, match="Order rejected"):
            pc.create_order("BTC/USDT", "sell", 1.0, price=10000.0)

    def test_ccxt_compatible_fields(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=50000.0,
            fee_rate=0.0, slippage_pct=0.0,
            partial_fill_prob=0.0, timeout_prob=0.0,
        )
        result = pc.create_order("BTC/USDT", "buy", 2.0, price=5000.0)
        for field in ["id", "symbol", "type", "side", "price", "amount",
                       "status", "filled", "remaining"]:
            assert field in result, f"Missing CCXT field: {field}"

    def test_timeout_returns_canceled(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=50000.0,
            timeout_prob=1.0,
        )
        result = pc.create_order("BTC/USDT", "buy", 1.0, price=10000.0)
        assert result["status"] == "canceled"
        assert result["filled"] == 0.0
        assert result["remaining"] == 1.0

    def test_limit_order_type_preserved(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=50000.0,
            fee_rate=0.0, slippage_pct=0.0,
            partial_fill_prob=0.0, timeout_prob=0.0,
        )
        result = pc.create_order("BTC/USDT", "buy", 1.0, order_type="limit", price=10000.0)
        assert result["type"] == "limit"

    def test_order_remaining_calculated(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=50000.0,
            fee_rate=0.0, slippage_pct=0.0,
            partial_fill_prob=0.0, timeout_prob=0.0,
        )
        result = pc.create_order("BTC/USDT", "buy", 3.0, price=5000.0)
        assert result["remaining"] == result["amount"] - result["filled"]

    def test_slippage_info_in_order(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=50000.0,
            fee_rate=0.0, slippage_pct=0.0,
            partial_fill_prob=0.0, timeout_prob=0.0,
        )
        result = pc.create_order("BTC/USDT", "buy", 1.0, price=10000.0)
        assert "info" in result
        assert "slippage_pct" in result["info"]


class TestPaperConnectorWaitForFill:
    """PaperConnector.wait_for_fill() 테스트."""

    def test_immediate_return(self):
        pc = PaperConnector(symbol="BTC/USDT")
        result = pc.wait_for_fill("paper_ord_1", "BTC/USDT")
        assert result["status"] == "closed"
        assert result["id"] == "paper_ord_1"

    def test_custom_timeout_ignored(self):
        pc = PaperConnector(symbol="BTC/USDT")
        result = pc.wait_for_fill("ord1", "BTC/USDT", timeout=120)
        assert result["status"] == "closed"


class TestPaperConnectorUnsupported:
    """PaperConnector 미지원 메서드 테스트."""

    def test_fetch_ticker_not_implemented(self):
        pc = PaperConnector(symbol="BTC/USDT")
        with pytest.raises(NotImplementedError):
            pc.fetch_ticker("BTC/USDT")

    def test_fetch_order_not_implemented(self):
        pc = PaperConnector(symbol="BTC/USDT")
        with pytest.raises(NotImplementedError):
            pc.fetch_order("ord1", "BTC/USDT")

    def test_cancel_order_not_implemented(self):
        pc = PaperConnector(symbol="BTC/USDT")
        with pytest.raises(NotImplementedError):
            pc.cancel_order("ord1", "BTC/USDT")


class TestPaperConnectorSummaryAndReset:
    """PaperConnector.get_paper_summary() / reset 테스트."""

    def test_summary_after_trade(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=10000.0,
            fee_rate=0.0, slippage_pct=0.0,
            partial_fill_prob=0.0, timeout_prob=0.0,
        )
        pc.create_order("BTC/USDT", "buy", 1.0, price=1000.0)
        summary = pc.get_paper_summary()
        assert summary["trade_count"] == 1
        assert summary["initial_balance"] == 10000.0

    def test_summary_includes_required_keys(self):
        pc = PaperConnector(symbol="BTC/USDT")
        summary = pc.get_paper_summary()
        for key in ["initial_balance", "current_balance", "total_pnl",
                     "total_return_pct", "trade_count", "win_rate", "open_positions"]:
            assert key in summary

    def test_reset_paper_account(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=10000.0,
            fee_rate=0.0, slippage_pct=0.0,
            partial_fill_prob=0.0, timeout_prob=0.0,
        )
        pc.create_order("BTC/USDT", "buy", 1.0, price=1000.0)
        assert pc.paper_trader.account.balance < 10000.0
        pc.reset_paper_account()
        assert pc.paper_trader.account.balance == 10000.0
        assert pc.paper_trader.account.positions == {}
        assert pc.paper_trader.account.trades == []


class TestPaperConnectorRoundTrip:
    """PaperConnector 왕복 거래 정합성."""

    def test_buy_sell_round_trip_balance(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=50000.0,
            fee_rate=0.0, slippage_pct=0.0,
            partial_fill_prob=0.0, timeout_prob=0.0,
        )
        pc.create_order("BTC/USDT", "buy", 2.0, price=10000.0)
        pc.create_order("BTC/USDT", "sell", 2.0, price=11000.0)
        balance = pc.fetch_balance()
        assert abs(balance["total"] - 52000.0) < 1.0

    def test_loss_round_trip(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=50000.0,
            fee_rate=0.0, slippage_pct=0.0,
            partial_fill_prob=0.0, timeout_prob=0.0,
        )
        pc.create_order("BTC/USDT", "buy", 1.0, price=10000.0)
        pc.create_order("BTC/USDT", "sell", 1.0, price=9000.0)
        balance = pc.fetch_balance()
        assert abs(balance["total"] - 49000.0) < 1.0

    def test_multiple_round_trips_summary(self):
        pc = PaperConnector(
            symbol="BTC/USDT", initial_balance=100000.0,
            fee_rate=0.0, slippage_pct=0.0,
            partial_fill_prob=0.0, timeout_prob=0.0,
        )
        for buy_p, sell_p in [(1000, 1200), (1200, 1100), (1100, 1500)]:
            pc.create_order("BTC/USDT", "buy", 1.0, price=float(buy_p))
            pc.create_order("BTC/USDT", "sell", 1.0, price=float(sell_p))

        summary = pc.get_paper_summary()
        assert summary["trade_count"] == 6
        assert summary["sell_count"] == 3
        # Total PnL = 200 - 100 + 400 = 500
        assert abs(summary["total_pnl"] - 500.0) < 1.0
