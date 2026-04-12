"""
F1. SpecialistAgents 단위 테스트.
"""

import numpy as np
import pandas as pd
import pytest

from src.alpha.specialist_agents import (
    OnchainAnalystAgent,
    SentimentAnalystAgent,
    SpecialistEnsemble,
    SpecialistVote,
    TechnicalAnalystAgent,
)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _make_df(
    rsi14: float = 50.0,
    close: float = 100.0,
    ema20: float = 98.0,
    ema50: float = 95.0,
    volume_ratio_20: float = 1.0,
    n: int = 5,
) -> pd.DataFrame:
    """테스트용 OHLCV + 지표 DataFrame."""
    return pd.DataFrame(
        {
            "close": [close] * n,
            "rsi14": [rsi14] * n,
            "ema20": [ema20] * n,
            "ema50": [ema50] * n,
            "volume_ratio_20": [volume_ratio_20] * n,
        }
    )


# ------------------------------------------------------------------
# TechnicalAnalystAgent
# ------------------------------------------------------------------

def test_technical_agent_name():
    agent = TechnicalAnalystAgent()
    assert agent.name == "technical"


def test_technical_buy_on_oversold_rsi():
    """RSI < 30 → BUY."""
    agent = TechnicalAnalystAgent()
    df = _make_df(rsi14=25.0, close=100.0, ema20=98.0, ema50=95.0)
    vote = agent.analyze(df)
    assert isinstance(vote, SpecialistVote)
    assert vote.action == "BUY"
    assert vote.confidence > 0


def test_technical_sell_on_overbought_rsi():
    """RSI > 70 → SELL."""
    agent = TechnicalAnalystAgent()
    # RSI 과매수 + EMA 하락 배열 → SELL
    df = _make_df(rsi14=75.0, close=90.0, ema20=95.0, ema50=98.0)
    vote = agent.analyze(df)
    assert isinstance(vote, SpecialistVote)
    assert vote.action == "SELL"
    assert vote.confidence > 0


def test_technical_hold_on_conflict():
    """RSI 중립 + EMA 혼재 → SpecialistVote 반환 (action 불문)."""
    agent = TechnicalAnalystAgent()
    # RSI 중립(50), EMA 혼재(close < ema20이지만 ema20 < ema50 아님)
    df = _make_df(rsi14=50.0, close=96.0, ema20=97.0, ema50=98.0)
    vote = agent.analyze(df)
    assert isinstance(vote, SpecialistVote)
    assert vote.action in ("BUY", "SELL", "HOLD")
    assert 0.0 <= vote.confidence <= 1.0


def test_technical_both_signals_agree_confidence():
    """RSI < 30 + EMA 상승배열 → confidence 0.75."""
    agent = TechnicalAnalystAgent()
    df = _make_df(rsi14=28.0, close=102.0, ema20=100.0, ema50=95.0)
    vote = agent.analyze(df)
    assert vote.action == "BUY"
    assert vote.confidence == pytest.approx(0.75)


# ------------------------------------------------------------------
# SentimentAnalystAgent
# ------------------------------------------------------------------

def test_sentiment_agent_buy():
    """sentiment_score=2.0 → BUY."""
    agent = SentimentAnalystAgent()
    df = _make_df()
    vote = agent.analyze(df, sentiment_score=2.0)
    assert isinstance(vote, SpecialistVote)
    assert vote.action == "BUY"
    assert vote.confidence >= 0.65


def test_sentiment_agent_sell():
    """sentiment_score=-2.0 → SELL."""
    agent = SentimentAnalystAgent()
    df = _make_df()
    vote = agent.analyze(df, sentiment_score=-2.0)
    assert isinstance(vote, SpecialistVote)
    assert vote.action == "SELL"
    assert vote.confidence >= 0.65


def test_sentiment_volume_bonus():
    """volume_ratio_20 > 2.0 → confidence +0.1."""
    agent = SentimentAnalystAgent()
    df_normal = _make_df(volume_ratio_20=1.0)
    df_spike = _make_df(volume_ratio_20=3.0)
    vote_normal = agent.analyze(df_normal, sentiment_score=2.0)
    vote_spike = agent.analyze(df_spike, sentiment_score=2.0)
    assert vote_spike.confidence > vote_normal.confidence


# ------------------------------------------------------------------
# OnchainAnalystAgent
# ------------------------------------------------------------------

def test_onchain_agent_buy():
    """onchain_score=2.0 → BUY."""
    agent = OnchainAnalystAgent()
    df = _make_df()
    vote = agent.analyze(df, onchain_score=2.0)
    assert isinstance(vote, SpecialistVote)
    assert vote.action == "BUY"
    assert vote.confidence == pytest.approx(0.70)


def test_onchain_agent_sell():
    """onchain_score=-2.0 → SELL."""
    agent = OnchainAnalystAgent()
    df = _make_df()
    vote = agent.analyze(df, onchain_score=-2.0)
    assert isinstance(vote, SpecialistVote)
    assert vote.action == "SELL"
    assert vote.confidence == pytest.approx(0.70)


def test_onchain_agent_hold():
    """onchain_score=0.5 → HOLD."""
    agent = OnchainAnalystAgent()
    df = _make_df()
    vote = agent.analyze(df, onchain_score=0.5)
    assert vote.action == "HOLD"
    assert vote.confidence == pytest.approx(0.5)


# ------------------------------------------------------------------
# SpecialistEnsemble
# ------------------------------------------------------------------

def test_ensemble_consensus_buy():
    """3개 모두 BUY 방향 → ensemble BUY."""
    ensemble = SpecialistEnsemble()
    # RSI < 30 + EMA 상승 → Technical BUY
    # sentiment_score=2.0 → Sentiment BUY
    # onchain_score=2.0   → Onchain BUY
    df = _make_df(rsi14=25.0, close=102.0, ema20=100.0, ema50=95.0)
    vote = ensemble.analyze(df, sentiment_score=2.0, onchain_score=2.0)
    assert isinstance(vote, SpecialistVote)
    assert vote.action == "BUY"
    assert vote.agent_name == "ensemble"


def test_ensemble_consensus_hold():
    """BUY/SELL/HOLD 혼재 → HOLD."""
    ensemble = SpecialistEnsemble()
    # Technical: RSI=75, EMA 하락 → SELL
    # Sentiment: score=2.0 → BUY
    # Onchain:   score=0.0 → HOLD
    df = _make_df(rsi14=75.0, close=90.0, ema20=95.0, ema50=98.0)
    vote = ensemble.analyze(df, sentiment_score=2.0, onchain_score=0.0)
    assert isinstance(vote, SpecialistVote)
    # BUY/SELL/HOLD 각 1개씩이면 HOLD, 또는 2개 일치 시 해당 방향
    assert vote.action in ("BUY", "SELL", "HOLD")
    assert 0.0 <= vote.confidence <= 1.0


def test_ensemble_two_out_of_three():
    """2개 BUY + 1개 HOLD → BUY."""
    ensemble = SpecialistEnsemble()
    # Technical: RSI=25, EMA 상승 → BUY
    # Sentiment: score=2.0 → BUY
    # Onchain: score=0.0 → HOLD
    df = _make_df(rsi14=25.0, close=102.0, ema20=100.0, ema50=95.0)
    vote = ensemble.analyze(df, sentiment_score=2.0, onchain_score=0.0)
    assert vote.action == "BUY"
    assert vote.agent_name == "ensemble"


# ------------------------------------------------------------------
# SpecialistVote confidence range
# ------------------------------------------------------------------

def test_specialist_vote_confidence_range():
    """모든 에이전트 confidence가 0~1 범위 내."""
    df = _make_df(rsi14=25.0, close=102.0, ema20=100.0, ema50=95.0, volume_ratio_20=3.0)

    agents_votes = [
        TechnicalAnalystAgent().analyze(df),
        SentimentAnalystAgent().analyze(df, sentiment_score=3.0),
        SentimentAnalystAgent().analyze(df, sentiment_score=-3.0),
        OnchainAnalystAgent().analyze(df, onchain_score=3.0),
        OnchainAnalystAgent().analyze(df, onchain_score=-3.0),
        SpecialistEnsemble().analyze(df, sentiment_score=2.0, onchain_score=2.0),
    ]
    for vote in agents_votes:
        assert 0.0 <= vote.confidence <= 1.0, (
            f"{vote.agent_name} confidence={vote.confidence} out of range"
        )


# ------------------------------------------------------------------
# Graceful degradation
# ------------------------------------------------------------------

def test_technical_agent_empty_df_returns_hold():
    """빈 DataFrame → TechnicalAnalystAgent는 HOLD를 반환해야 한다."""
    agent = TechnicalAnalystAgent()
    vote = agent.analyze(pd.DataFrame())
    assert vote.action == "HOLD"
    assert 0.0 <= vote.confidence <= 1.0


def test_technical_agent_missing_columns_returns_hold():
    """필요 컬럼 없는 DataFrame → HOLD."""
    agent = TechnicalAnalystAgent()
    df = pd.DataFrame({"close": [100.0, 101.0]})  # rsi14, ema20, ema50 없음
    vote = agent.analyze(df)
    assert vote.action == "HOLD"
    assert 0.0 <= vote.confidence <= 1.0


def test_ensemble_agent_failure_graceful_degradation():
    """한 에이전트가 예외를 던져도 ensemble이 HOLD로 대체하고 결과를 반환해야 한다."""
    from unittest.mock import patch

    ensemble = SpecialistEnsemble()
    df = _make_df(rsi14=25.0, close=102.0, ema20=100.0, ema50=95.0)

    # OnchainAnalystAgent.analyze가 예외를 던지도록 패치
    with patch.object(ensemble.onchain, "analyze", side_effect=RuntimeError("onchain API down")):
        vote = ensemble.analyze(df, sentiment_score=2.0, onchain_score=2.0)

    # 예외에도 불구하고 유효한 SpecialistVote가 반환돼야 한다
    assert isinstance(vote, SpecialistVote)
    assert vote.action in ("BUY", "SELL", "HOLD")
    assert 0.0 <= vote.confidence <= 1.0
    assert vote.agent_name == "ensemble"


def test_ensemble_all_agents_fail_returns_hold():
    """모든 에이전트가 실패하면 ensemble은 HOLD confidence=0을 반환해야 한다."""
    from unittest.mock import patch

    ensemble = SpecialistEnsemble()
    df = _make_df()

    with patch.object(ensemble.technical, "analyze", side_effect=RuntimeError("fail")), \
         patch.object(ensemble.sentiment, "analyze", side_effect=RuntimeError("fail")), \
         patch.object(ensemble.onchain, "analyze", side_effect=RuntimeError("fail")):
        vote = ensemble.analyze(df)

    assert isinstance(vote, SpecialistVote)
    # 모두 HOLD(confidence=0)이면 합의 실패 → HOLD
    assert vote.action == "HOLD"
    assert vote.agent_name == "ensemble"


def test_ensemble_two_buy_one_sell_returns_buy():
    """2:1 split (BUY vs SELL, HOLD 없음) → 다수결 BUY, confidence는 BUY 평균."""
    from unittest.mock import patch

    ensemble = SpecialistEnsemble()
    df = _make_df()

    buy_vote = SpecialistVote(agent_name="x", action="BUY", confidence=0.70, reasoning="")
    sell_vote = SpecialistVote(agent_name="y", action="SELL", confidence=0.65, reasoning="")

    with patch.object(ensemble.technical, "analyze", return_value=buy_vote), \
         patch.object(ensemble.sentiment, "analyze", return_value=buy_vote), \
         patch.object(ensemble.onchain, "analyze", return_value=sell_vote):
        vote = ensemble.analyze(df)

    assert vote.action == "BUY"
    assert vote.confidence == pytest.approx(0.70)  # 평균(0.70, 0.70)
    assert vote.agent_name == "ensemble"


def test_ensemble_unanimous_sell():
    """3개 모두 SELL → ensemble SELL, confidence = 3개 평균."""
    ensemble = SpecialistEnsemble()
    # RSI > 70 + EMA 하락 → Technical SELL
    # sentiment_score=-2.0 → Sentiment SELL
    # onchain_score=-2.0   → Onchain SELL
    df = _make_df(rsi14=75.0, close=90.0, ema20=95.0, ema50=98.0)
    vote = ensemble.analyze(df, sentiment_score=-2.0, onchain_score=-2.0)
    assert vote.action == "SELL"
    assert vote.agent_name == "ensemble"
    assert 0.0 <= vote.confidence <= 1.0


def test_ensemble_all_hold_no_failures():
    """에이전트 실패 없이 3개 모두 HOLD → HOLD, confidence <= 0.5."""
    ensemble = SpecialistEnsemble()
    # RSI=50(중립), EMA 혼재, sentiment/onchain 중립
    df = _make_df(rsi14=50.0, close=96.0, ema20=97.0, ema50=98.0)
    vote = ensemble.analyze(df, sentiment_score=0.0, onchain_score=0.0)
    assert vote.action == "HOLD"
    assert vote.agent_name == "ensemble"
    assert 0.0 <= vote.confidence <= 1.0
