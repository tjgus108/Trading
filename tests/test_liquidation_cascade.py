"""
LiquidationCascadeStrategy 단위 테스트.
모든 테스트는 mock 사용 — 실제 API 호출 없음.
"""

import time
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.data.liquidation_feed import LiquidationFetcher, LiquidationPressure
from src.strategy.base import Action, Confidence
from src.strategy.liquidation_cascade import LiquidationCascadeStrategy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df(rsi: float = 50.0, close: float = 50000.0, n: int = 5) -> pd.DataFrame:
    """최소 generate() 실행에 필요한 DataFrame 생성 (인덱스 -2 참조)."""
    data = {
        "close": [close] * n,
        "rsi14": [rsi] * n,
    }
    return pd.DataFrame(data)


def _pressure(long_liq: float = 1_000_000, short_liq: float = 200_000,
              cascade_risk: bool = False) -> LiquidationPressure:
    total = long_liq + short_liq
    ratio = long_liq / (total + 1e-9)
    score = max(-3.0, min(3.0, (0.5 - ratio) * 6.0))
    return LiquidationPressure(
        long_liq_usd=long_liq,
        short_liq_usd=short_liq,
        liq_ratio=ratio,
        total_liq_usd=total,
        cascade_risk=cascade_risk,
        score=score,
    )


# ---------------------------------------------------------------------------
# 1. name
# ---------------------------------------------------------------------------

def test_name():
    strategy = LiquidationCascadeStrategy()
    assert strategy.name == "liquidation_cascade"


# ---------------------------------------------------------------------------
# 2. LiquidationFetcher.compute_pressure — long liq dominant
# ---------------------------------------------------------------------------

def test_pressure_long_liq_dominant():
    fetcher = LiquidationFetcher.mock(long_liq=1_000_000, short_liq=50_000)
    p = fetcher.compute_pressure()
    assert p.liq_ratio > 0.75, f"Expected ratio > 0.75, got {p.liq_ratio}"
    assert p.long_liq_usd > p.short_liq_usd


# ---------------------------------------------------------------------------
# 3. LiquidationFetcher.compute_pressure — short liq dominant
# ---------------------------------------------------------------------------

def test_pressure_short_liq_dominant():
    fetcher = LiquidationFetcher.mock(long_liq=50_000, short_liq=1_000_000)
    p = fetcher.compute_pressure()
    assert p.liq_ratio < 0.25, f"Expected ratio < 0.25, got {p.liq_ratio}"
    assert p.short_liq_usd > p.long_liq_usd


# ---------------------------------------------------------------------------
# 4. score range -3 ~ +3
# ---------------------------------------------------------------------------

def test_pressure_score_range():
    for long_liq, short_liq in [
        (1_000_000, 0),
        (0, 1_000_000),
        (500_000, 500_000),
        (1_000_000, 1_000_000),
    ]:
        fetcher = LiquidationFetcher.mock(long_liq=long_liq, short_liq=short_liq)
        p = fetcher.compute_pressure()
        assert -3.0 <= p.score <= 3.0, f"score out of range: {p.score}"


# ---------------------------------------------------------------------------
# 5. BUY HIGH on long cascade + RSI < 35
# ---------------------------------------------------------------------------

def test_strategy_buy_on_long_cascade():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=30.0)

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=900_000, short_liq=100_000)):
        signal = strategy.generate(df)

    assert signal.action == Action.BUY
    assert signal.confidence == Confidence.HIGH


# ---------------------------------------------------------------------------
# 6. SELL HIGH on short cascade + RSI > 65
# ---------------------------------------------------------------------------

def test_strategy_sell_on_short_cascade():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=70.0)

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=100_000, short_liq=900_000)):
        signal = strategy.generate(df)

    assert signal.action == Action.SELL
    assert signal.confidence == Confidence.HIGH


# ---------------------------------------------------------------------------
# 7. HOLD on cascade_risk=True
# ---------------------------------------------------------------------------

def test_strategy_hold_on_cascade_risk():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=30.0)  # RSI would normally trigger BUY

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=900_000, short_liq=100_000,
                                             cascade_risk=True)):
        signal = strategy.generate(df)

    assert signal.action == Action.HOLD


# ---------------------------------------------------------------------------
# 8. HOLD on neutral liq_ratio ≈ 0.5
# ---------------------------------------------------------------------------

def test_strategy_hold_neutral():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=50.0)

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=500_000, short_liq=500_000)):
        signal = strategy.generate(df)

    assert signal.action == Action.HOLD


# ---------------------------------------------------------------------------
# 9. reasoning contains liq data
# ---------------------------------------------------------------------------

def test_reasoning_contains_liq_data():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=30.0)

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=900_000, short_liq=100_000)):
        signal = strategy.generate(df)

    assert "long_liq" in signal.reasoning


# ---------------------------------------------------------------------------
# 10. STRATEGY_REGISTRY contains liquidation_cascade
# ---------------------------------------------------------------------------

def test_registry_contains_liquidation_cascade():
    from src.orchestrator import STRATEGY_REGISTRY
    assert "liquidation_cascade" in STRATEGY_REGISTRY
    assert STRATEGY_REGISTRY["liquidation_cascade"] is LiquidationCascadeStrategy


# ---------------------------------------------------------------------------
# 11. BUY MEDIUM when only liq_ratio > 0.75 but RSI not oversold
# ---------------------------------------------------------------------------

def test_strategy_buy_medium_when_rsi_not_oversold():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=55.0)  # not < 35

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=900_000, short_liq=100_000)):
        signal = strategy.generate(df)

    assert signal.action == Action.BUY
    assert signal.confidence == Confidence.MEDIUM


# ---------------------------------------------------------------------------
# 12. SELL MEDIUM when only liq_ratio < 0.25 but RSI not overbought
# ---------------------------------------------------------------------------

def test_strategy_sell_medium_when_rsi_not_overbought():
    strategy = LiquidationCascadeStrategy()
    df = _make_df(rsi=50.0)  # not > 65

    with patch.object(strategy._fetcher, "compute_pressure",
                      return_value=_pressure(long_liq=100_000, short_liq=900_000)):
        signal = strategy.generate(df)

    assert signal.action == Action.SELL
    assert signal.confidence == Confidence.MEDIUM


# ---------------------------------------------------------------------------
# 13. get_recent returns [] on HTTP error (no exception propagation)
# ---------------------------------------------------------------------------

def test_get_recent_returns_empty_on_error():
    with patch("time.sleep"):
        fetcher = LiquidationFetcher(symbol="BTC/USDT")
        with patch("src.data.liquidation_feed._requests") as mock_req:
            mock_req.get.side_effect = Exception("network error")
            result = fetcher.get_recent()
        assert result == []


# ---------------------------------------------------------------------------
# 14. mock factory produces correct liq_ratio
# ---------------------------------------------------------------------------

def test_mock_factory_ratio():
    fetcher = LiquidationFetcher.mock(long_liq=750_000, short_liq=250_000)
    p = fetcher.compute_pressure()
    assert abs(p.liq_ratio - 0.75) < 0.01


# ---------------------------------------------------------------------------
# 15. get_recent with retry — fallback on persistent failure
# ---------------------------------------------------------------------------

def test_get_recent_retry_fallback():
    """API 재시도 실패 후 fallback 동작 확인."""
    with patch("time.sleep"):
        fetcher = LiquidationFetcher(symbol="BTC/USDT")

        # 첫 번째 fetch 성공 → fallback 데이터 저장 (Bybit v5 형식)
        with patch("src.data.liquidation_feed._requests") as mock_req:
            mock_req.get.return_value.json.return_value = {
                "retCode": 0,
                "result": {"list": [{"side": "Buy", "price": "50000", "size": "1", "symbol": "BTCUSDT", "time": "1700000000000"}]}
            }
            mock_req.get.return_value.raise_for_status.return_value = None
            result1 = fetcher.get_recent()

        assert len(result1) == 1
        assert result1[0]["side"] == "BUY"

        # 두 번째 fetch 실패 (모든 재시도 후) → fallback 반환
        with patch("src.data.liquidation_feed._requests") as mock_req:
            mock_req.get.side_effect = Exception("network error")
            result2 = fetcher.get_recent()

        # fallback 데이터 반환
        assert len(result2) == 1
        assert result2[0]["side"] == "BUY"


# ---------------------------------------------------------------------------
# 16. get_recent with retry — success on second attempt
# ---------------------------------------------------------------------------

def test_get_recent_retry_success_on_second_attempt():
    """첫 시도 실패, 두 번째 시도 성공."""
    with patch("time.sleep"):
        fetcher = LiquidationFetcher(symbol="BTC/USDT", max_retries=2)
        
        call_count = 0
        
        def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary network error")
            # 두 번째 호출 성공 (Bybit v5 형식)
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "retCode": 0,
                "result": {"list": [{"side": "Sell", "price": "50000", "size": "2", "symbol": "BTCUSDT", "time": "1700000000000"}]}
            }
            mock_resp.raise_for_status.return_value = None
            return mock_resp
        
        with patch("src.data.liquidation_feed._requests") as mock_req:
            mock_req.get.side_effect = mock_get
            result = fetcher.get_recent()
        
        assert len(result) == 1
        assert result[0]["side"] == "SELL"
        assert call_count == 2  # 첫 실패 + 두 번째 성공

# ---------------------------------------------------------------------------
# 17. get_recent returns list of dicts with required fields
# ---------------------------------------------------------------------------

def test_get_recent_format_validation():
    """get_recent() 반환 데이터 형식 검증: list[dict] with symbol, side, price, executedQty."""
    fetcher = LiquidationFetcher.mock(long_liq=1_000_000, short_liq=500_000)
    result = fetcher.get_recent()
    
    # 리스트 형식 확인
    assert isinstance(result, list)
    assert len(result) > 0
    
    # 각 원소가 dict 확인
    for item in result:
        assert isinstance(item, dict)
        # 필수 필드 확인
        assert "symbol" in item
        assert "side" in item
        assert "price" in item
        assert "executedQty" in item or "origQty" in item
        assert "time" in item
        
        # side는 SELL 또는 BUY
        assert item["side"] in ["SELL", "BUY"]


# ---------------------------------------------------------------------------
# 18. compute_pressure returns LiquidationPressure with valid ranges
# ---------------------------------------------------------------------------

def test_compute_pressure_format_validation():
    """compute_pressure() 반환 데이터 형식 검증: LiquidationPressure 필드 범위 확인."""
    fetcher = LiquidationFetcher.mock(long_liq=1_000_000, short_liq=500_000)
    pressure = fetcher.compute_pressure()
    
    # 타입 확인
    assert isinstance(pressure, LiquidationPressure)
    
    # 필드 존재 및 타입 확인
    assert isinstance(pressure.long_liq_usd, float) and pressure.long_liq_usd >= 0
    assert isinstance(pressure.short_liq_usd, float) and pressure.short_liq_usd >= 0
    assert isinstance(pressure.liq_ratio, float)
    assert isinstance(pressure.total_liq_usd, float) and pressure.total_liq_usd >= 0
    assert isinstance(pressure.cascade_risk, bool)
    assert isinstance(pressure.score, float)
    
    # 범위 검증
    assert 0 <= pressure.liq_ratio <= 1.0, f"liq_ratio out of range: {pressure.liq_ratio}"
    assert -3.0 <= pressure.score <= 3.0, f"score out of range: {pressure.score}"
    assert pressure.total_liq_usd == pressure.long_liq_usd + pressure.short_liq_usd
