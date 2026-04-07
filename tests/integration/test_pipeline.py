"""
TradingPipeline 통합 테스트.
dry_run=True 모드로 전체 파이프라인을 실행하여 각 단계를 검증한다.
실제 주문은 제출하지 않는다.
EXCHANGE_API_KEY 환경변수가 없으면 전체 테스트를 건너뛴다.
"""

import os

import pytest

from src.data.feed import DataFeed
from src.exchange.connector import ExchangeConnector
from src.pipeline.runner import PipelineResult, TradingPipeline
from src.risk.manager import CircuitBreaker, RiskManager
from src.strategy.donchian_breakout import DonchianBreakoutStrategy


def _require_credentials():
    if not os.environ.get("EXCHANGE_API_KEY"):
        pytest.skip("No API credentials: set EXCHANGE_API_KEY and EXCHANGE_API_SECRET")


@pytest.fixture(scope="module")
def connector():
    _require_credentials()
    conn = ExchangeConnector(exchange_name="binance", sandbox=True)
    conn.connect()
    return conn


@pytest.fixture(scope="module")
def data_feed(connector):
    return DataFeed(connector=connector)


@pytest.fixture(scope="module")
def risk_manager():
    cb = CircuitBreaker(
        max_daily_loss=0.05,
        max_drawdown=0.20,
        max_consecutive_losses=5,
        flash_crash_pct=0.10,
    )
    return RiskManager(
        risk_per_trade=0.01,
        atr_multiplier_sl=1.5,
        atr_multiplier_tp=3.0,
        max_position_size=0.10,
        circuit_breaker=cb,
    )


@pytest.fixture(scope="module")
def pipeline(connector, data_feed, risk_manager):
    return TradingPipeline(
        connector=connector,
        data_feed=data_feed,
        strategy=DonchianBreakoutStrategy(),
        risk_manager=risk_manager,
        symbol="BTC/USDT",
        timeframe="1h",
        dry_run=True,
    )


@pytest.mark.integration
def test_pipeline_dry_run(pipeline):
    """전체 파이프라인을 dry_run 모드로 실행하고 결과를 검증한다."""
    result = pipeline.run()

    # PipelineResult 타입 확인
    assert isinstance(result, PipelineResult), "run() should return a PipelineResult"

    # status는 "OK" 또는 "BLOCKED"여야 한다 (ERROR는 허용하지 않음)
    assert result.status in ("OK", "BLOCKED"), (
        f"Expected status 'OK' or 'BLOCKED', got '{result.status}'. "
        f"error={result.error}"
    )

    # 데이터 단계는 반드시 통과해야 한다
    assert result.pipeline_step in ("data", "alpha", "risk", "execution"), (
        f"Unexpected pipeline_step: {result.pipeline_step}"
    )

    # HOLD 신호이거나 dry_run 실행까지 도달했다면 execution 상태를 검증한다
    if result.execution is not None:
        exec_status = result.execution.get("status")
        assert exec_status == "DRY_RUN", (
            f"Expected execution.status == 'DRY_RUN', got '{exec_status}'"
        )

    # HOLD 신호인 경우: execution이 없고 signal.action == HOLD
    if result.signal is not None and result.execution is None:
        from src.strategy.base import Action
        # HOLD이면 pipeline_step이 alpha에서 멈춰야 한다
        if result.signal.action == Action.HOLD:
            assert result.pipeline_step == "alpha", (
                f"HOLD signal should stop at 'alpha', got '{result.pipeline_step}'"
            )


@pytest.mark.integration
def test_data_feed_indicators(data_feed):
    """DataFeed.fetch() 후 모든 기술 지표 컬럼이 존재하는지 확인한다."""
    summary = data_feed.fetch("BTC/USDT", "1h", limit=200)

    required_indicators = [
        "ema20",
        "ema50",
        "atr14",
        "rsi14",
        "donchian_high",
        "donchian_low",
        "vwap",
    ]

    df_columns = set(summary.df.columns)
    for indicator in required_indicators:
        assert indicator in df_columns, (
            f"Expected indicator column '{indicator}' not found in DataFrame. "
            f"Available columns: {sorted(df_columns)}"
        )

    # 지표값이 NaN이 아닌 유효한 행이 존재해야 한다 (충분한 캔들 이후)
    valid_rows = summary.df[required_indicators].dropna()
    assert len(valid_rows) > 0, "All indicator rows are NaN — not enough candles?"

    # summary.indicators 목록에도 포함되어야 한다
    for indicator in required_indicators:
        assert indicator in summary.indicators, (
            f"Indicator '{indicator}' missing from DataSummary.indicators list"
        )
