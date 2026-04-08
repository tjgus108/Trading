"""
G1. SpecialistEnsemble 파이프라인 연결 테스트.
"""

from dataclasses import fields
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.alpha.specialist_agents import SpecialistVote
from src.pipeline.runner import PipelineResult, TradingPipeline
from src.strategy.base import Action, Confidence, Signal


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _make_df(n: int = 10) -> pd.DataFrame:
    """최소한의 지표 컬럼을 포함한 테스트용 DataFrame."""
    import time
    now = int(time.time() * 1000)
    interval = 3600 * 1000
    data = {
        "timestamp": [now - (n - i) * interval for i in range(n)],
        "open":  [50000.0 + i * 10 for i in range(n)],
        "high":  [50200.0 + i * 10 for i in range(n)],
        "low":   [49800.0 + i * 10 for i in range(n)],
        "close": [50100.0 + i * 10 for i in range(n)],
        "volume":[10.0] * n,
        "rsi14": [50.0] * n,
        "ema20": [49900.0 + i * 10 for i in range(n)],
        "ema50": [49500.0 + i * 10 for i in range(n)],
        "atr14": [300.0] * n,
        "volume_ratio_20": [1.0] * n,
    }
    return pd.DataFrame(data)


def _make_signal(action: Action = Action.BUY) -> Signal:
    return Signal(
        action=action,
        confidence=Confidence.HIGH,
        strategy="test",
        entry_price=50100.0,
        reasoning="test signal",
        invalidation="",
        bull_case="",
        bear_case="",
    )


def _make_pipeline(dry_run: bool = True) -> TradingPipeline:
    """컴포넌트를 모두 Mock으로 구성한 TradingPipeline."""
    connector = MagicMock()
    connector.fetch_balance.return_value = {"total": {"USDT": 10000.0}}

    data_feed = MagicMock()
    df = _make_df()
    data_summary = MagicMock()
    data_summary.df = df
    data_summary.missing = 0
    data_summary.anomalies = []
    data_summary.candles = len(df)
    data_feed.fetch.return_value = data_summary

    strategy = MagicMock()
    strategy.generate.return_value = _make_signal(Action.BUY)

    risk_manager = MagicMock()
    from src.risk.manager import RiskResult, RiskStatus
    risk_manager.evaluate.return_value = RiskResult(
        status=RiskStatus.APPROVED,
        position_size=0.01,
        stop_loss=49500.0,
        take_profit=51000.0,
        reason="",
        risk_amount=100.0,
        portfolio_exposure=0.01,
    )

    pipeline = TradingPipeline(
        connector=connector,
        data_feed=data_feed,
        strategy=strategy,
        risk_manager=risk_manager,
        symbol="BTC/USDT",
        timeframe="1h",
        dry_run=dry_run,
    )
    return pipeline


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

def test_pipeline_result_has_specialist_field():
    """PipelineResult 데이터클래스에 specialist_action 필드가 존재해야 한다."""
    field_names = {f.name for f in fields(PipelineResult)}
    assert "specialist_action" in field_names
    result = PipelineResult(timestamp="t", symbol="BTC/USDT", pipeline_step="start", status="OK")
    assert result.specialist_action == ""


def test_pipeline_without_specialist():
    """specialist_ensemble=None이어도 파이프라인이 정상 동작해야 한다."""
    pipeline = _make_pipeline()
    assert pipeline.specialist_ensemble is None
    result = pipeline.run()
    assert result.status in ("OK", "BLOCKED", "ERROR")
    # specialist_action은 기본값 ""
    assert result.specialist_action == ""


def test_specialist_ensemble_allows_agree():
    """SpecialistEnsemble이 같은 방향(BUY)이면 원래 BUY 신호 유지."""
    pipeline = _make_pipeline()

    mock_ensemble = MagicMock()
    mock_ensemble.analyze.return_value = SpecialistVote(
        agent_name="ensemble",
        action="BUY",      # strategy 신호와 동일
        confidence=0.8,
        reasoning="agree",
    )
    pipeline.specialist_ensemble = mock_ensemble

    result = pipeline.run()
    # 충돌 없으므로 HOLD로 전환되지 않아야 함
    assert result.signal is not None
    assert result.signal.action != Action.HOLD
    assert result.specialist_action == "BUY"


def test_specialist_ensemble_blocks_conflict():
    """SpecialistEnsemble이 반대 방향(SELL) + confidence>=0.7이면 HOLD로 전환."""
    pipeline = _make_pipeline()
    # strategy는 BUY 신호 반환 (기본 설정)

    mock_ensemble = MagicMock()
    mock_ensemble.analyze.return_value = SpecialistVote(
        agent_name="ensemble",
        action="SELL",     # BUY와 반대
        confidence=0.75,   # >= 0.7
        reasoning="conflict",
    )
    pipeline.specialist_ensemble = mock_ensemble

    result = pipeline.run()
    assert result.signal is not None
    assert result.signal.action == Action.HOLD
    assert "SpecialistEnsemble 충돌" in result.signal.reasoning
    # pipeline_step은 alpha에서 멈춰야 함
    assert result.pipeline_step == "alpha"
    # notes에 충돌 메시지 포함
    assert any("SPECIALIST conflict" in n for n in result.notes)


def test_specialist_ensemble_low_confidence_no_block():
    """SpecialistEnsemble이 반대 방향이라도 confidence < 0.7이면 HOLD 전환 안 함."""
    pipeline = _make_pipeline()

    mock_ensemble = MagicMock()
    mock_ensemble.analyze.return_value = SpecialistVote(
        agent_name="ensemble",
        action="SELL",     # 반대 방향
        confidence=0.5,    # < 0.7 → 차단 안 함
        reasoning="low conf",
    )
    pipeline.specialist_ensemble = mock_ensemble

    result = pipeline.run()
    assert result.signal is not None
    assert result.signal.action != Action.HOLD
