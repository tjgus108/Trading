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
    connector.is_halted = False
    connector.sync_positions.return_value = []
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


def test_pipeline_risk_blocked():
    """Risk Manager가 신호를 BLOCKED하면 execution 단계까지 진행하지 않는다."""
    pipeline = _make_pipeline()
    
    from src.risk.manager import RiskResult, RiskStatus
    # risk_manager를 BLOCKED 반환하도록 설정
    pipeline.risk_manager.evaluate.return_value = RiskResult(
        status=RiskStatus.BLOCKED,
        position_size=0.0,
        stop_loss=0.0,
        take_profit=0.0,
        reason="Daily loss limit exceeded",
        risk_amount=0.0,
        portfolio_exposure=0.0,
    )
    
    result = pipeline.run()
    assert result.status == "BLOCKED"
    assert result.pipeline_step == "risk"
    assert any("Daily loss limit exceeded" in n for n in result.notes)
    # execution이 없어야 함
    assert result.execution is None


def test_pipeline_execution_fails():
    """Execution 단계에서 예외 발생 시 ERROR 상태로 반환."""
    pipeline = _make_pipeline(dry_run=False)
    
    # execution이 실패하도록 connector 설정
    pipeline.connector.create_order.side_effect = Exception("Connection timeout")
    
    result = pipeline.run()
    assert result.status == "ERROR"
    assert result.pipeline_step == "execution"
    assert "Connection timeout" in result.error


def test_pipeline_ensemble_conflict_llm():
    """MultiLLMEnsemble이 conflicts_with()를 반환하면 HOLD 전환."""
    pipeline = _make_pipeline()
    
    mock_ensemble = MagicMock()
    mock_ensemble.conflicts_with.return_value = True
    mock_ensemble.summary.return_value = "Strong SELL consensus"
    pipeline.ensemble = mock_ensemble
    
    result = pipeline.run()
    assert result.signal is not None
    assert result.signal.action == Action.HOLD
    assert "[ENSEMBLE_CONFLICT]" in result.signal.reasoning
    assert result.pipeline_step == "alpha"
    assert any("ENSEMBLE conflict → HOLD" in n for n in result.notes)


def test_pipeline_kelly_sizing():
    """Kelly Sizer가 충분한 거래 이력(>=10)이 있을 때 position_size 조정."""
    from src.risk.kelly_sizer import KellySizer
    
    pipeline = _make_pipeline()
    
    # trade_history 10개 이상으로 설정
    pipeline._trade_history = [
        {"pnl": 100, "entry": 50000, "exit": 50100},
    ] * 10
    
    mock_kelly = MagicMock(spec=KellySizer)
    # from_trade_history를 통해 Kelly size 계산
    pipeline.kelly_sizer = MagicMock()
    
    # Mock KellySizer.from_trade_history
    with patch('src.pipeline.runner.KellySizer.from_trade_history') as mock_from_history:
        mock_from_history.return_value = 0.02  # 새로운 kelly size
        result = pipeline.run()
        assert result.status == "OK"
        assert any("Kelly size" in n for n in result.notes)


def test_pipeline_vol_targeting():
    """VolTargeting이 position_size를 조정한다."""
    from src.risk.vol_targeting import VolTargeting
    
    pipeline = _make_pipeline()
    
    mock_vol_targeting = MagicMock(spec=VolTargeting)
    mock_vol_targeting.adjust.return_value = 0.015  # 조정된 size
    pipeline.vol_targeting = mock_vol_targeting
    
    result = pipeline.run()
    assert result.status == "OK"
    assert any("VolTarget size" in n for n in result.notes)
    mock_vol_targeting.adjust.assert_called_once()


# ------------------------------------------------------------------
# Full Pipeline Integration Tests (Specialist + Risk + Execution)
# ------------------------------------------------------------------

def test_full_pipeline_specialist_ensemble_with_risk_and_twap():
    """
    통합 테스트: SpecialistEnsemble + RiskManager + TWAP 실행기
    완전한 파이프라인 흐름을 검증하면서 specialist voting 결과를 반영.
    """
    from src.exchange.twap import TWAPExecutor, TWAPResult
    
    pipeline = _make_pipeline(dry_run=False)
    
    # 1. SpecialistEnsemble 설정 — technical agent가 SELL, sentiment가 HOLD → consensus BUY
    mock_ensemble = MagicMock()
    mock_ensemble.analyze.return_value = SpecialistVote(
        agent_name="ensemble_consensus",
        action="BUY",      # strategy와 일치
        confidence=0.85,
        reasoning="3/3 agents agree BUY; strong technical + positive sentiment",
    )
    pipeline.specialist_ensemble = mock_ensemble
    
    # 2. TWAP Executor 설정
    mock_twap = MagicMock(spec=TWAPExecutor)
    mock_twap.execute.return_value = TWAPResult(
        slices_executed=4,
        avg_price=50150.0,
        total_qty=0.01,
        filled_qty=0.01,
        estimated_slippage_pct=0.1,
        dry_run=False,
    )
    pipeline.twap_executor = mock_twap
    
    # 3. Pipeline 실행
    result = pipeline.run()
    
    # 4. Assertions: 전체 파이프라인이 execution까지 도달
    assert result.status == "OK"
    assert result.pipeline_step == "execution"
    assert result.signal is not None
    assert result.signal.action == Action.BUY
    assert result.specialist_action == "BUY"
    assert result.execution is not None
    assert result.execution["status"] == "TWAP_COMPLETE"
    assert result.execution["slices"] == 4
    assert result.execution["avg_price"] == 50150.0
    # impl_shortfall = (50150 - 50100) / 50100 * 10000 ≈ 9.98 bps
    assert result.impl_shortfall_bps is not None
    assert 9.0 < result.impl_shortfall_bps < 11.0
    
    # TWAP executor가 호출되었는지 확인
    mock_twap.execute.assert_called_once()
    mock_ensemble.analyze.assert_called_once()


def test_full_pipeline_specialist_conflict_blocks_at_alpha():
    """
    통합 테스트: SpecialistEnsemble 강한 반대가 신호를 HOLD로 블록
    파이프라인이 alpha 단계에서 멈추고 risk/execution은 건너뛰는지 확인.
    """
    pipeline = _make_pipeline(dry_run=False)
    
    # Strategy는 BUY 신호 반환
    # SpecialistEnsemble이 강한 SELL 합의로 반대
    mock_ensemble = MagicMock()
    mock_ensemble.analyze.return_value = SpecialistVote(
        agent_name="ensemble_consensus",
        action="SELL",     # strategy 신호와 반대
        confidence=0.92,   # >= 0.7 → 블록 조건 만족
        reasoning="Bearish consensus: all 3 agents see weakness; technical breakdown detected",
    )
    pipeline.specialist_ensemble = mock_ensemble
    
    # Risk manager를 어떻게 설정하든 호출되지 않아야 함
    risk_call_count = 0
    def track_risk_calls(*args, **kwargs):
        nonlocal risk_call_count
        risk_call_count += 1
        from src.risk.manager import RiskResult, RiskStatus
        return RiskResult(
            status=RiskStatus.APPROVED,
            position_size=0.01,
            stop_loss=49500.0,
            take_profit=51000.0,
            reason="",
            risk_amount=100.0,
            portfolio_exposure=0.01,
        )
    
    pipeline.risk_manager.evaluate.side_effect = track_risk_calls
    
    # Pipeline 실행
    result = pipeline.run()
    
    # Assertions: HOLD로 전환되고 alpha에서 멈춤
    assert result.status == "OK"
    assert result.pipeline_step == "alpha"
    assert result.signal is not None
    assert result.signal.action == Action.HOLD
    assert "SpecialistEnsemble 충돌" in result.signal.reasoning
    assert "SPECIALIST conflict" in str(result.notes)
    
    # Risk manager가 호출되지 않았음을 확인
    assert risk_call_count == 0
    pipeline.connector.create_order.assert_not_called()


def test_full_pipeline_kelly_sizer_and_vol_targeting_together():
    """
    통합 테스트: Kelly Sizer + VolTargeting 조합 동작
    risk manager의 position_size가 두 개의 사이저에 의해 순차적으로 조정되는지 확인.
    """
    from src.risk.kelly_sizer import KellySizer
    from src.risk.vol_targeting import VolTargeting
    
    pipeline = _make_pipeline()
    
    # Trade history 충분히 구성
    pipeline._trade_history = [
        {"pnl": 50 + (i * 10), "entry": 50000 + i * 10, "exit": 50050 + i * 10}
        for i in range(15)
    ]
    
    # Mock Kelly Sizer
    mock_kelly = MagicMock(spec=KellySizer)
    mock_kelly.from_trade_history = MagicMock(return_value=0.015)  # Kelly says 0.015
    pipeline.kelly_sizer = mock_kelly
    
    # Mock VolTargeting
    mock_vol = MagicMock(spec=VolTargeting)
    mock_vol.adjust.return_value = 0.012  # VolTarget further adjusts to 0.012
    pipeline.vol_targeting = mock_vol
    
    # Pipeline 실행 (dry_run=True)
    result = pipeline.run()
    
    # Assertions
    assert result.status == "OK"
    assert result.pipeline_step == "execution"
    assert result.signal is not None
    assert result.signal.action == Action.BUY
    
    # Kelly sizer가 호출되었는지 확인 (trade_history >= 10)
    assert any("Kelly size" in n for n in result.notes)
    
    # Vol targeting이 호출되었는지 확인
    assert any("VolTarget size" in n for n in result.notes)
    mock_vol.adjust.assert_called_once()



def test_pipeline_data_anomaly_detection():
    """
    Data anomaly 감지 시 notes에 기록되는지 검증.
    파이프라인은 계속 진행하지만 anomaly가 로깅됨.
    """
    pipeline = _make_pipeline()
    
    df = _make_df()
    data_summary = MagicMock()
    data_summary.df = df
    data_summary.missing = 2  # 5 이상이 아니므로 경고만
    data_summary.anomalies = ["price_gap > 5%", "volume_spike 10x"]
    data_summary.candles = len(df)
    pipeline.data_feed.fetch.return_value = data_summary
    
    result = pipeline.run()
    
    # 파이프라인은 OK이지만 notes에 anomalies가 기록됨
    assert result.status == "OK"
    assert result.pipeline_step in ("execution", "risk")
    assert any("ANOMALIES" in n for n in result.notes)


def test_pipeline_sequential_failures_ensemble_then_risk():
    """
    SpecialistEnsemble이 HOLD 전환 후 risk manager 호출 안 됨을 검증.
    dry_run=True에서도 정상 상태 반환.
    """
    pipeline = _make_pipeline(dry_run=True)
    
    # Ensemble이 강한 반대로 HOLD 전환
    mock_ensemble = MagicMock()
    mock_ensemble.analyze.return_value = SpecialistVote(
        agent_name="strong_opposing_vote",
        action="SELL",
        confidence=0.95,
        reasoning="System-wide bearish signals detected",
    )
    pipeline.specialist_ensemble = mock_ensemble
    
    # Risk manager 호출 카운트
    risk_call_count = 0
    original_evaluate = pipeline.risk_manager.evaluate
    
    def track_risk_calls(*args, **kwargs):
        nonlocal risk_call_count
        risk_call_count += 1
        from src.risk.manager import RiskResult, RiskStatus
        return RiskResult(
            status=RiskStatus.APPROVED,
            position_size=0.01,
            stop_loss=49500.0,
            take_profit=51000.0,
            reason="",
            risk_amount=100.0,
            portfolio_exposure=0.01,
        )
    
    pipeline.risk_manager.evaluate.side_effect = track_risk_calls
    
    result = pipeline.run()
    
    # HOLD로 전환되고 risk manager는 호출 안 됨
    assert result.signal.action == Action.HOLD
    assert result.pipeline_step == "alpha"
    assert result.status == "OK"
    assert risk_call_count == 0
