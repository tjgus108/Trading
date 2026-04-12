"""
E2. FundingCarryStrategy 단위 테스트.
"""

import pandas as pd
import pytest

from src.strategy.funding_carry import FundingCarryStrategy
from src.strategy.base import Action


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n=20, rsi=50.0, funding_rate=None) -> pd.DataFrame:
    """최소 DataFrame 생성. funding_rate 인수 있으면 컬럼 추가."""
    close = [100.0 + i for i in range(n)]
    df = pd.DataFrame(
        {
            "close": close,
            "rsi14": [rsi] * n,
            "atr14": [1.0] * n,
        }
    )
    if funding_rate is not None:
        df["funding_rate"] = funding_rate
    return df


# ── 기본 속성 ─────────────────────────────────────────────────────────────────

def test_name():
    assert FundingCarryStrategy.name == "funding_carry"


# ── funding_rate 컬럼 사용 경로 ───────────────────────────────────────────────

def test_buy_on_high_funding():
    """funding_rate > entry_threshold → BUY"""
    strat = FundingCarryStrategy(entry_threshold=0.0003)
    df = _make_df(funding_rate=0.0005)
    sig = strat.generate(df)
    assert sig.action == Action.BUY


def test_sell_on_low_funding():
    """funding_rate < exit_threshold → SELL"""
    strat = FundingCarryStrategy(exit_threshold=0.0001)
    df = _make_df(funding_rate=0.00005)
    sig = strat.generate(df)
    assert sig.action == Action.SELL


def test_hold_on_neutral_funding():
    """exit_threshold <= funding_rate <= entry_threshold → HOLD"""
    strat = FundingCarryStrategy(entry_threshold=0.0003, exit_threshold=0.0001)
    df = _make_df(funding_rate=0.0002)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── RSI proxy 경로 ─────────────────────────────────────────────────────────────

def test_rsi_proxy_high():
    """funding_rate 컬럼 없고 RSI > 70 → BUY (proxy=0.0004 > 0.0003)"""
    strat = FundingCarryStrategy(entry_threshold=0.0003)
    df = _make_df(rsi=75.0)  # funding_rate 컬럼 없음
    sig = strat.generate(df)
    assert sig.action == Action.BUY


def test_rsi_proxy_low():
    """funding_rate 컬럼 없고 RSI < 30 → SELL (proxy=-0.0002 < 0.0001)"""
    strat = FundingCarryStrategy(exit_threshold=0.0001)
    df = _make_df(rsi=25.0)  # funding_rate 컬럼 없음
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── reasoning 검증 ─────────────────────────────────────────────────────────────

def test_reasoning_contains_funding_rate():
    """Signal.reasoning에 'funding_rate' 문자열 포함"""
    strat = FundingCarryStrategy()
    df = _make_df(funding_rate=0.0005)
    sig = strat.generate(df)
    assert "funding_rate" in sig.reasoning


# ── 레지스트리 등록 확인 ──────────────────────────────────────────────────────────

def test_registry_contains_funding_carry():
    """STRATEGY_REGISTRY에 'funding_carry' 키 존재"""
    from src.orchestrator import STRATEGY_REGISTRY
    assert "funding_carry" in STRATEGY_REGISTRY
    assert STRATEGY_REGISTRY["funding_carry"] is FundingCarryStrategy


# ── entry_price ──────────────────────────────────────────────────────────────

def test_entry_price_is_last_close():
    """entry_price == df['close'].iloc[-2] (BaseStrategy._last 기준)"""
    strat = FundingCarryStrategy()
    df = _make_df(n=20, funding_rate=0.0005)
    sig = strat.generate(df)
    assert sig.entry_price == df["close"].iloc[-2]


# ── 레짐 필터 테스트 ──────────────────────────────────────────────────────────

def _make_df_high_vol(n=30, funding_rate=0.0005) -> pd.DataFrame:
    """변동성 높은 DataFrame: close가 큰 폭으로 진동."""
    import numpy as np
    rng = list(range(n))
    # 매 캔들 ±5% 진동 → realized vol >> 0.03
    close = [100.0 * (1 + 0.06 * ((-1) ** i)) for i in rng]
    df = pd.DataFrame({
        "close": close,
        "rsi14": [50.0] * n,
        "atr14": [1.0] * n,
        "funding_rate": [funding_rate] * n,
    })
    return df


def _make_df_downtrend(n=40, funding_rate=0.0005) -> pd.DataFrame:
    """급락 추세 DataFrame: EMA20 기울기 << -0.02, vol은 낮게 유지."""
    # 균일하게 하락 → vol 낮음, EMA 기울기 충분히 음수
    close = [100.0 - i * 0.8 for i in range(n)]
    df = pd.DataFrame({
        "close": close,
        "rsi14": [50.0] * n,
        "atr14": [1.0] * n,
        "funding_rate": [funding_rate] * n,
    })
    return df


def test_hold_on_high_volatility():
    """realized_vol > 0.03 → HOLD (변동성 레짐 필터)"""
    strat = FundingCarryStrategy(entry_threshold=0.0003)
    df = _make_df_high_vol(funding_rate=0.0005)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert "변동성" in sig.reasoning or "vol" in sig.reasoning


def test_hold_on_downtrend():
    """EMA20 기울기 < -0.02 → HOLD (추세 강도 필터)"""
    strat = FundingCarryStrategy(entry_threshold=0.0003)
    df = _make_df_downtrend(funding_rate=0.0005)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert "기울기" in sig.reasoning or "slope" in sig.reasoning
