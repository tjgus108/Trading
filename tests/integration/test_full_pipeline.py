"""통합 테스트: MockExchangeConnector 기반 전체 파이프라인."""
import pytest
from src.exchange.mock_connector import MockExchangeConnector
from src.data.feed import DataFeed
from src.backtest.engine import BacktestEngine
from src.strategy.ema_cross import EmaCrossStrategy
from src.strategy.funding_carry import FundingCarryStrategy


@pytest.mark.integration
def test_backtest_ema_cross_full():
    """EMA Cross 전략 전체 백테스트 파이프라인."""
    conn = MockExchangeConnector()
    conn.connect()
    feed = DataFeed(conn)
    summary = feed.fetch("BTC/USDT", "1h", limit=200)
    engine = BacktestEngine(slippage=0.001, timeframe="1h")
    result = engine.run(EmaCrossStrategy(), summary.df)
    assert result is not None
    assert hasattr(result, "sharpe_ratio")
    assert hasattr(result, "max_drawdown")


@pytest.mark.integration
def test_data_feed_cache():
    """DataFeed 캐싱 동작 확인."""
    conn = MockExchangeConnector()
    conn.connect()
    feed = DataFeed(conn, cache_ttl=60)
    s1 = feed.fetch("BTC/USDT", "1h", limit=100)
    s2 = feed.fetch("BTC/USDT", "1h", limit=100)
    # 두 번째는 캐시 히트 → 동일 객체
    assert s1 is s2


@pytest.mark.integration
def test_tournament_runs():
    """전략 토너먼트 병렬 실행 확인."""
    from src.backtest.engine import BacktestEngine
    from src.strategy.donchian_breakout import DonchianBreakoutStrategy
    import pandas as pd, numpy as np
    conn = MockExchangeConnector()
    conn.connect()
    feed = DataFeed(conn)
    summary = feed.fetch("BTC/USDT", "1h", limit=300)
    df = summary.df
    strategies = [EmaCrossStrategy(), DonchianBreakoutStrategy(), FundingCarryStrategy()]
    engine = BacktestEngine(slippage=0.0005, timeframe="1h")
    results = [engine.run(s, df) for s in strategies]
    assert len(results) == 3
    assert all(r is not None for r in results)


@pytest.mark.integration
def test_walk_forward_ema():
    """Walk-Forward 최적화 실행 확인."""
    from src.backtest.walk_forward import optimize_ema_cross
    conn = MockExchangeConnector()
    conn.connect()
    feed = DataFeed(conn)
    summary = feed.fetch("BTC/USDT", "1h", limit=500)
    result = optimize_ema_cross(summary.df, n_windows=2)
    assert result is not None
    assert hasattr(result, "is_stable")
    assert hasattr(result, "best_params")
