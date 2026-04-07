"""
ExchangeConnector 통합 테스트.
실제 Binance testnet에 연결하여 API 동작을 검증한다.
EXCHANGE_API_KEY 환경변수가 없으면 전체 테스트를 건너뛴다.
"""

import os

import pytest

from src.exchange.connector import ExchangeConnector


def _require_credentials():
    if not os.environ.get("EXCHANGE_API_KEY"):
        pytest.skip("No API credentials: set EXCHANGE_API_KEY and EXCHANGE_API_SECRET")


@pytest.fixture(scope="module")
def connector():
    _require_credentials()
    conn = ExchangeConnector(exchange_name="binance", sandbox=True)
    conn.connect()
    return conn


@pytest.mark.integration
def test_connect_sandbox():
    """Binance testnet에 정상적으로 연결되는지 확인한다."""
    _require_credentials()
    conn = ExchangeConnector(exchange_name="binance", sandbox=True)
    conn.connect()
    # connect() 이후 exchange 속성이 존재해야 한다
    assert conn.exchange is not None
    # 마켓이 로드되어 있어야 한다
    assert len(conn.exchange.markets) > 0


@pytest.mark.integration
def test_fetch_ohlcv(connector):
    """BTC/USDT 1h 캔들 100개를 가져오고 구조를 검증한다."""
    data = connector.fetch_ohlcv("BTC/USDT", "1h", limit=100)

    # 길이 검증
    assert len(data) == 100, f"Expected 100 candles, got {len(data)}"

    # 각 캔들은 [timestamp, open, high, low, close, volume] 6개 요소여야 한다
    for candle in data:
        assert len(candle) == 6, f"Expected 6 elements per candle, got {len(candle)}"

    # 타입 검증: timestamp는 정수, 나머지는 숫자
    first = data[0]
    assert isinstance(first[0], int), "timestamp should be int (ms)"
    for i in range(1, 6):
        assert isinstance(first[i], (int, float)), f"OHLCV[{i}] should be numeric"

    # OHLCV 기본 유효성: high >= low, close > 0, volume >= 0
    for candle in data:
        _, open_, high, low, close, volume = candle
        assert high >= low, "high must be >= low"
        assert close > 0, "close must be > 0"
        assert volume >= 0, "volume must be >= 0"


@pytest.mark.integration
def test_fetch_balance(connector):
    """잔고 조회 결과가 딕셔너리 형태임을 검증한다."""
    balance = connector.fetch_balance()

    assert isinstance(balance, dict), "fetch_balance() should return a dict"
    # ccxt 표준: 'total', 'free', 'used' 키가 존재한다
    assert "total" in balance, "balance should have 'total' key"
    assert "free" in balance, "balance should have 'free' key"
    assert "used" in balance, "balance should have 'used' key"
    # 각 항목도 딕셔너리여야 한다
    assert isinstance(balance["total"], dict)
    assert isinstance(balance["free"], dict)
    assert isinstance(balance["used"], dict)


@pytest.mark.integration
def test_fetch_ticker(connector):
    """BTC/USDT 현재가 조회 후 price > 0을 검증한다."""
    ticker = connector.fetch_ticker("BTC/USDT")

    assert isinstance(ticker, dict), "fetch_ticker() should return a dict"
    # ccxt 표준 ticker 필드 확인
    assert "last" in ticker, "ticker should have 'last' (last price) key"
    assert ticker["last"] is not None, "last price should not be None"
    assert ticker["last"] > 0, f"last price must be > 0, got {ticker['last']}"
