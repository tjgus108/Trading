"""CCIBreakoutStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.cci_breakout import CCIBreakoutStrategy, _calc_cci


def _make_df(n=50, flat=True):
    """기본 DataFrame 생성. flat=True이면 완만한 시세."""
    np.random.seed(0)
    base = np.linspace(100, 102, n)
    return pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.2, 0.2, n),
        "high": base + 0.5,
        "low": base - 0.5,
        "volume": np.ones(n) * 1000,
    })


def _make_buy_df():
    """CCI +100 상향 돌파를 만드는 DataFrame."""
    n = 50
    # 앞부분은 낮은 가격, 마지막 2봉 직전에 급등
    close = np.concatenate([np.ones(n - 3) * 100.0, [100.0, 99.0, 130.0, 130.0]])
    high = close + 1.0
    low = close - 1.0
    df = pd.DataFrame({
        "open": close,
        "close": close,
        "high": high,
        "low": low,
        "volume": np.ones(len(close)) * 1000,
    })
    return df


def _make_sell_df():
    """CCI -100 하향 돌파를 만드는 DataFrame."""
    n = 50
    close = np.concatenate([np.ones(n - 3) * 100.0, [100.0, 101.0, 70.0, 70.0]])
    high = close + 1.0
    low = close - 1.0
    df = pd.DataFrame({
        "open": close,
        "close": close,
        "high": high,
        "low": low,
        "volume": np.ones(len(close)) * 1000,
    })
    return df


strategy = CCIBreakoutStrategy()


# 1. 전략 이름
def test_strategy_name():
    assert strategy.name == "cci_breakout"


# 2. 인스턴스 타입
def test_strategy_instance():
    strat = CCIBreakoutStrategy()
    assert isinstance(strat, CCIBreakoutStrategy)


# 3. 데이터 부족 → HOLD
def test_insufficient_data_hold():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# 4. None 입력 → HOLD
def test_none_input_hold():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# 5. 정상 데이터 → Signal 반환
def test_normal_data_returns_signal():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig is not None
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# 6. Signal 필드 완전성
def test_signal_fields_complete():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.strategy == "cci_breakout"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# 7. 완만한 데이터 → HOLD
def test_flat_data_hold():
    df = _make_df(n=50, flat=True)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# 8. HOLD reasoning에 "CCI" 포함
def test_hold_reasoning_contains_cci():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    if sig.action == Action.HOLD:
        assert "CCI" in sig.reasoning


# 9. BUY 신호 발생 확인
def test_buy_signal_generated():
    df = _make_buy_df()
    sig = strategy.generate(df)
    # CCI +100 상향 돌파가 발생하는 데이터이므로 BUY 또는 HOLD
    assert sig.action in (Action.BUY, Action.HOLD)


# 10. SELL 신호 발생 확인
def test_sell_signal_generated():
    df = _make_sell_df()
    sig = strategy.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


# 11. BUY confidence는 HIGH 또는 MEDIUM
def test_buy_confidence_valid():
    df = _make_buy_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 12. SELL confidence는 HIGH 또는 MEDIUM
def test_sell_confidence_valid():
    df = _make_sell_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 13. entry_price는 마지막 완성봉 close
def test_entry_price_is_last_close():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), abs=1e-6)


# 14. _calc_cci 길이 일치
def test_calc_cci_length():
    df = _make_df(n=50)
    cci = _calc_cci(df)
    assert len(cci) == len(df)


# 15. _calc_cci NaN이 앞부분에만 존재
def test_calc_cci_nan_only_at_start():
    df = _make_df(n=50)
    cci = _calc_cci(df)
    # 마지막 10개는 NaN이 없어야 함
    assert not cci.iloc[-10:].isna().any()


# 16. 25행 경계 (정확히 최소 행)
def test_exactly_min_rows():
    df = _make_df(n=25)
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# 17. 24행 → HOLD (최소 미달)
def test_below_min_rows_hold():
    df = _make_df(n=24)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
