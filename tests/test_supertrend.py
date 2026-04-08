"""SuperTrendStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.supertrend import SuperTrendStrategy
from src.strategy.base import Action, Confidence


def _make_df(n: int = 30, atr: float = 1.0) -> pd.DataFrame:
    """기본 테스트용 DataFrame 생성."""
    close = np.linspace(100.0, 110.0, n)
    return pd.DataFrame(
        {
            "open": close - 0.5,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": np.ones(n) * 1000,
            "atr14": np.ones(n) * atr,
        }
    )


def _make_buy_signal_df() -> pd.DataFrame:
    """sell 추세 → buy 추세 전환 유도: 하락 후 마지막 두 캔들에서 급등."""
    n = 40
    close_base = np.linspace(110.0, 90.0, n - 2)
    # 급등으로 upper band 돌파 → buy 추세로 전환
    close = np.concatenate([close_base, [130.0, 128.0]])
    atr = np.ones(n) * 1.5
    return pd.DataFrame(
        {
            "open": close - 0.5,
            "high": close + 2.0,
            "low": close - 2.0,
            "close": close,
            "volume": np.ones(n) * 1000,
            "atr14": atr,
        }
    )


def _make_sell_signal_df() -> pd.DataFrame:
    """buy 추세 → sell 추세 전환 유도: 상승 후 마지막 두 캔들에서 급락."""
    n = 40
    close_base = np.linspace(90.0, 110.0, n - 2)
    # 급락으로 lower band 이탈 → sell 추세로 전환
    close = np.concatenate([close_base, [70.0, 72.0]])
    atr = np.ones(n) * 1.5
    return pd.DataFrame(
        {
            "open": close - 0.5,
            "high": close + 2.0,
            "low": close - 2.0,
            "close": close,
            "volume": np.ones(n) * 1000,
            "atr14": atr,
        }
    )


# --- 테스트 ---

def test_strategy_name():
    """전략 이름이 'supertrend'인지 확인."""
    st = SuperTrendStrategy()
    assert st.name == "supertrend"


def test_buy_signal_on_trend_reversal_up():
    """sell→buy 추세 전환 시 BUY HIGH 신호 생성."""
    st = SuperTrendStrategy(period=10, multiplier=3.0)
    df = _make_buy_signal_df()
    signal = st.generate(df)
    assert signal.action == Action.BUY
    assert signal.confidence == Confidence.HIGH


def test_sell_signal_on_trend_reversal_down():
    """buy→sell 추세 전환 시 SELL HIGH 신호 생성."""
    st = SuperTrendStrategy(period=10, multiplier=3.0)
    df = _make_sell_signal_df()
    signal = st.generate(df)
    assert signal.action == Action.SELL
    assert signal.confidence == Confidence.HIGH


def test_hold_on_insufficient_data():
    """데이터 부족 시 HOLD 반환."""
    st = SuperTrendStrategy(period=10, multiplier=3.0)
    df = _make_df(n=5)
    signal = st.generate(df)
    assert signal.action == Action.HOLD


def test_hold_on_trend_continuation():
    """추세 지속(전환 없음) 시 HOLD 반환."""
    st = SuperTrendStrategy(period=10, multiplier=3.0)
    # 지속 상승 → buy 추세 유지
    df = _make_df(n=30, atr=0.5)
    signal = st.generate(df)
    assert signal.action == Action.HOLD


def test_signal_fields_present():
    """Signal 객체에 필수 필드가 모두 있는지 검증."""
    st = SuperTrendStrategy()
    df = _make_df(n=30)
    signal = st.generate(df)
    assert signal.strategy == "supertrend"
    assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(signal.entry_price, float)
    assert isinstance(signal.reasoning, str)
    assert isinstance(signal.invalidation, str)
