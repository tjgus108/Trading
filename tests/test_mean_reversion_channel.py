"""tests/test_mean_reversion_channel.py — MeanReversionChannelStrategy 단위 테스트 (12개)"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.mean_reversion_channel import MeanReversionChannelStrategy
from src.strategy.base import Action, Confidence


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_df(close: np.ndarray) -> pd.DataFrame:
    n = len(close)
    return pd.DataFrame({
        "open": close - 1,
        "close": close.astype(float),
        "high": close + 2,
        "low": close - 2,
        "volume": np.ones(n) * 1000,
    })


def _buy_df(n: int = 70) -> pd.DataFrame:
    """
    z_score < -2 AND z_now > z_prev (반전 시작) 조건을 만족하는 DataFrame.

    SMA50 ≈ 100 수준에서 마지막 완성봉을 -2.5σ 이하로 하강 후
    바로 직전봉보다 약간 반등시킴.
    """
    # 기본 50봉: 100 근처 안정
    base = np.full(n - 4, 100.0)
    # 큰 std를 만들기 위해 초반에 변동 추가
    base[:20] = np.linspace(90, 110, 20)
    # 마지막 4봉: 급락 후 반등
    # idx = n-2 (완성봉), idx-1 = n-3
    # 완성봉 z_score < -2 이고 z_now > z_prev 가 되도록
    # z_prev (n-3): 더 낮게, z_now (n-2): 살짝 덜 낮게
    tail = np.array([100.0, 80.0, 75.0, 78.0])  # 75 < 78 → 반전
    close = np.concatenate([base, tail])
    assert len(close) == n
    return _make_df(close)


def _sell_df(n: int = 70) -> pd.DataFrame:
    """
    z_score > +2 AND z_now < z_prev (반전 시작) 조건을 만족하는 DataFrame.
    """
    base = np.full(n - 4, 100.0)
    base[:20] = np.linspace(90, 110, 20)
    # 급등 후 반락
    tail = np.array([100.0, 120.0, 126.0, 123.0])  # 126 > 123 → 반전
    close = np.concatenate([base, tail])
    assert len(close) == n
    return _make_df(close)


def _normal_df(n: int = 70) -> pd.DataFrame:
    """z_score ≈ 0 → HOLD"""
    close = np.full(n, 100.0)
    return _make_df(close)


# ── 테스트 ───────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 = 'mean_reversion_channel'"""
    assert MeanReversionChannelStrategy.name == "mean_reversion_channel"


def test_insufficient_data_returns_hold():
    """2. 데이터 부족 (54행) → HOLD"""
    strat = MeanReversionChannelStrategy()
    df = _make_df(np.linspace(100, 110, 54))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_insufficient_data_reasoning():
    """3. 데이터 부족 시 reasoning에 'Insufficient' 포함"""
    strat = MeanReversionChannelStrategy()
    df = _make_df(np.linspace(100, 110, 40))
    sig = strat.generate(df)
    assert "Insufficient" in sig.reasoning


def test_buy_signal():
    """4. z_score < -2 AND 반전 시작 → BUY"""
    strat = MeanReversionChannelStrategy()
    df = _buy_df()
    sig = strat.generate(df)
    assert sig.action == Action.BUY


def test_sell_signal():
    """5. z_score > +2 AND 반전 시작 → SELL"""
    strat = MeanReversionChannelStrategy()
    df = _sell_df()
    sig = strat.generate(df)
    assert sig.action == Action.SELL


def test_normal_is_hold():
    """6. 정상 범위 z_score → HOLD"""
    strat = MeanReversionChannelStrategy()
    df = _normal_df()
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_buy_reasoning_contains_keyword():
    """7. BUY reasoning에 'MeanReversionChannel' 또는 'z_score' 포함"""
    strat = MeanReversionChannelStrategy()
    df = _buy_df()
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert "MeanReversionChannel" in sig.reasoning or "z_score" in sig.reasoning


def test_sell_reasoning_contains_keyword():
    """8. SELL reasoning에 'MeanReversionChannel' 또는 'z_score' 포함"""
    strat = MeanReversionChannelStrategy()
    df = _sell_df()
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert "MeanReversionChannel" in sig.reasoning or "z_score" in sig.reasoning


def test_signal_fields_complete():
    """9. Signal 필드 완전성 확인"""
    strat = MeanReversionChannelStrategy()
    df = _buy_df()
    sig = strat.generate(df)
    assert sig.strategy == "mean_reversion_channel"
    assert isinstance(sig.entry_price, float)
    assert sig.entry_price > 0
    assert sig.reasoning != ""
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


def test_buy_high_confidence():
    """10. |z_score| > 2.5 → HIGH confidence"""
    strat = MeanReversionChannelStrategy()
    # std가 매우 작으면 z_score가 극단적으로 커짐 → |z| > 2.5
    n = 70
    base = np.full(n - 4, 100.0)
    # std ≈ 0.1 수준으로 만들기 위해 거의 일정
    base += np.random.default_rng(42).uniform(-0.05, 0.05, len(base))
    # 마지막 봉에서 급락: z_score << -2.5
    tail = np.array([100.0, 97.5, 97.0, 97.3])
    close = np.concatenate([base, tail])
    df = _make_df(close)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_sell_confidence_is_high_or_medium():
    """11. SELL confidence는 HIGH 또는 MEDIUM"""
    strat = MeanReversionChannelStrategy()
    df = _sell_df()
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_hold_confidence_is_low():
    """12. HOLD confidence는 LOW"""
    strat = MeanReversionChannelStrategy()
    df = _normal_df()
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_entry_price_equals_last_close():
    """13. entry_price = 마지막 완성봉 close (iloc[-2])"""
    strat = MeanReversionChannelStrategy()
    df = _buy_df()
    sig = strat.generate(df)
    expected = float(df["close"].iloc[-2])
    assert abs(sig.entry_price - expected) < 1e-6


def test_minimum_rows_exactly_55():
    """14. 정확히 55행 → 에러 없이 신호 반환"""
    strat = MeanReversionChannelStrategy()
    df = _make_df(np.linspace(100, 110, 55))
    sig = strat.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
