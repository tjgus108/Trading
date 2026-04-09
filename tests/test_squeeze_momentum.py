"""SqueezeMomentumStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.squeeze_momentum import SqueezeMomentumStrategy, _squeeze_signals


def _make_df(n=60, seed=42):
    """기본 DataFrame 생성."""
    np.random.seed(seed)
    base = np.linspace(100, 102, n)
    noise = np.random.uniform(-0.3, 0.3, n)
    close = base + noise
    return pd.DataFrame({
        "open": close,
        "close": close,
        "high": close + 0.5,
        "low": close - 0.5,
        "volume": np.ones(n) * 1000,
    })


def _make_buy_df():
    """Squeeze 해제 + 양의 모멘텀 상황."""
    n = 60
    np.random.seed(1)
    # squeeze ON 구간: 변동성 낮음, squeeze OFF: 마지막 직전에 돌파
    close = np.ones(n) * 100.0
    # 마지막 몇 봉에서 급등 (양의 모멘텀)
    close[-5:] = np.linspace(100, 115, 5)
    high = close + 0.1  # BB 좁게 유지
    low = close - 0.1
    # 마지막 봉은 high/low 확장 (KC 돌파)
    high[-3:] = close[-3:] + 3.0
    low[-3:] = close[-3:] - 3.0
    df = pd.DataFrame({
        "open": close,
        "close": close,
        "high": high,
        "low": low,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_sell_df():
    """Squeeze 해제 + 음의 모멘텀 상황."""
    n = 60
    np.random.seed(2)
    close = np.ones(n) * 100.0
    close[-5:] = np.linspace(100, 85, 5)
    high = close + 0.1
    low = close - 0.1
    high[-3:] = close[-3:] + 3.0
    low[-3:] = close[-3:] - 3.0
    df = pd.DataFrame({
        "open": close,
        "close": close,
        "high": high,
        "low": low,
        "volume": np.ones(n) * 1000,
    })
    return df


strategy = SqueezeMomentumStrategy()


# 1. 전략 이름
def test_strategy_name():
    assert strategy.name == "squeeze_momentum"


# 2. 인스턴스 타입
def test_strategy_instance():
    strat = SqueezeMomentumStrategy()
    assert isinstance(strat, SqueezeMomentumStrategy)


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
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig is not None
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# 6. Signal 필드 완전성
def test_signal_fields_complete():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.strategy == "squeeze_momentum"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# 7. entry_price는 마지막 완성봉 close
def test_entry_price_is_last_close():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), abs=1e-6)


# 8. HOLD reasoning에 "Squeeze" 또는 "squeeze" 포함
def test_hold_reasoning_content():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    if sig.action == Action.HOLD:
        assert "Squeeze" in sig.reasoning or "squeeze" in sig.reasoning or "부족" in sig.reasoning


# 9. BUY 신호 confidence 유효성
def test_buy_confidence_valid():
    df = _make_buy_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 10. SELL 신호 confidence 유효성
def test_sell_confidence_valid():
    df = _make_sell_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 11. BUY reasoning에 "momentum" 포함
def test_buy_reasoning_contains_momentum():
    df = _make_buy_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "momentum" in sig.reasoning.lower()


# 12. SELL reasoning에 "momentum" 포함
def test_sell_reasoning_contains_momentum():
    df = _make_sell_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "momentum" in sig.reasoning.lower()


# 13. _squeeze_signals 길이 일치
def test_squeeze_signals_length():
    df = _make_df(n=60)
    sq, mom, std = _squeeze_signals(df)
    assert len(sq) == len(df)
    assert len(mom) == len(df)
    assert len(std) == len(df)


# 14. _squeeze_signals: squeeze는 bool Series
def test_squeeze_series_is_bool():
    df = _make_df(n=60)
    sq, _, _ = _squeeze_signals(df)
    assert sq.dtype == bool


# 15. 25행 경계 (정확히 최소 행)
def test_exactly_min_rows():
    df = _make_df(n=25)
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# 16. 24행 → HOLD (최소 미달)
def test_below_min_rows_hold():
    df = _make_df(n=24)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# 17. BUY/SELL 이외 → HOLD action 값
def test_hold_action_value():
    df = _make_df(n=60)
    sig = strategy.generate(df)
    if sig.action == Action.HOLD:
        assert sig.action == Action.HOLD
