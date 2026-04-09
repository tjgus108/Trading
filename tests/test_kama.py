"""KAMAStrategy 단위 테스트."""

from typing import Optional

import numpy as np
import pandas as pd
import pytest

from src.strategy.kama import KAMAStrategy, _compute_kama
from src.strategy.base import Action, Confidence


def _make_df(n: int = 40, close: Optional[np.ndarray] = None) -> pd.DataFrame:
    if close is None:
        close = np.linspace(100.0, 110.0, n)
    n = len(close)
    return pd.DataFrame(
        {
            "open": close - 0.5,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": np.ones(n) * 1000,
            "atr14": np.ones(n) * 1.0,
        }
    )


def _make_crossup_df() -> pd.DataFrame:
    """KAMA보다 낮게 유지하다 마지막 두 봉에서 강하게 상향 돌파."""
    n = 40
    # 초반 횡보 → KAMA ≈ 100 근방
    close = np.full(n, 100.0, dtype=float)
    # iloc[-3] = 99 (KAMA 아래), iloc[-2] = 115 (KAMA 위)
    close[-3] = 99.0
    close[-2] = 115.0
    close[-1] = 115.5  # 현재 진행 중 캔들 (무시됨)
    return _make_df(close=close)


def _make_crossdown_df() -> pd.DataFrame:
    """KAMA보다 높게 유지하다 마지막 두 봉에서 강하게 하향 돌파."""
    n = 40
    close = np.full(n, 110.0, dtype=float)
    # iloc[-3] = 111 (KAMA 위), iloc[-2] = 95 (KAMA 아래)
    close[-3] = 111.0
    close[-2] = 95.0
    close[-1] = 94.5
    return _make_df(close=close)


# --- 기본 ---

def test_strategy_name():
    assert KAMAStrategy().name == "kama"


def test_hold_on_insufficient_data():
    """20행 미만 데이터 → HOLD LOW."""
    st = KAMAStrategy()
    df = _make_df(n=10)
    sig = st.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_hold_on_exactly_minimum_rows():
    """정확히 20행 → 최소 요건 충족, HOLD 이상."""
    st = KAMAStrategy()
    df = _make_df(n=20)
    sig = st.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# --- BUY 신호 ---

def test_buy_signal_on_crossup():
    """KAMA 상향 돌파 시 BUY 신호."""
    st = KAMAStrategy()
    df = _make_crossup_df()
    sig = st.generate(df)
    assert sig.action == Action.BUY


def test_buy_signal_high_confidence_large_gap():
    """이격 > 1% 시 HIGH confidence."""
    st = KAMAStrategy()
    df = _make_crossup_df()
    sig = st.generate(df)
    # 15% 이격이므로 HIGH 예상
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_buy_entry_price_equals_last_close():
    """entry_price가 iloc[-2] close와 같아야 함."""
    st = KAMAStrategy()
    df = _make_crossup_df()
    sig = st.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(df["close"].iloc[-2], rel=1e-6)


# --- SELL 신호 ---

def test_sell_signal_on_crossdown():
    """KAMA 하향 돌파 시 SELL 신호."""
    st = KAMAStrategy()
    df = _make_crossdown_df()
    sig = st.generate(df)
    assert sig.action == Action.SELL


def test_sell_signal_high_confidence_large_gap():
    """이격 > 1% 시 SELL HIGH confidence."""
    st = KAMAStrategy()
    df = _make_crossdown_df()
    sig = st.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence == Confidence.HIGH


# --- HOLD ---

def test_hold_on_flat_trend():
    """횡보(돌파 없음) → HOLD."""
    st = KAMAStrategy()
    close = np.full(40, 100.0)
    df = _make_df(close=close)
    sig = st.generate(df)
    assert sig.action == Action.HOLD


# --- Signal 필드 유효성 ---

def test_signal_fields_valid():
    """Signal 필수 필드 타입 검증."""
    st = KAMAStrategy()
    df = _make_df(n=40)
    sig = st.generate(df)
    assert sig.strategy == "kama"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


# --- _compute_kama 유틸 ---

def test_compute_kama_length():
    """KAMA 시리즈 길이가 입력과 동일해야 함."""
    close = pd.Series(np.linspace(100.0, 120.0, 50))
    kama = _compute_kama(close)
    assert len(kama) == 50


def test_compute_kama_nan_prefix():
    """첫 10행은 NaN이어야 함 (ER period=10)."""
    close = pd.Series(np.linspace(100.0, 120.0, 50))
    kama = _compute_kama(close)
    assert kama.iloc[:10].isna().all()


def test_compute_kama_follows_trend():
    """강한 상승 추세 시 KAMA가 증가해야 함."""
    close = pd.Series(np.linspace(100.0, 200.0, 60))
    kama = _compute_kama(close)
    valid = kama.dropna()
    assert valid.iloc[-1] > valid.iloc[0]
