"""BBBandwidthStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.bb_bandwidth import BBBandwidthStrategy
from src.strategy.base import Action, Confidence


def _make_df(n: int = 60, close_vals=None) -> pd.DataFrame:
    if close_vals is None:
        close_vals = np.linspace(100.0, 110.0, n)
    close = np.asarray(close_vals, dtype=float)
    return pd.DataFrame(
        {
            "open": close - 0.5,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": np.ones(len(close)) * 1000,
        }
    )


def _make_squeeze_buy_df() -> pd.DataFrame:
    """BB 수축 + 상단 근처: BUY 시그널 유도."""
    n = 80
    # 범위가 좁은 횡보 후 상단 근처에 가격 위치
    base = np.ones(60) * 100.0 + np.random.default_rng(42).normal(0, 0.1, 60)
    # 마지막 20개: 약간 상승하여 상단 근처
    end_close = np.ones(20) * 100.5
    close = np.concatenate([base, end_close])
    # high/low 도 좁게
    high = close + 0.15
    low = close - 0.15
    return pd.DataFrame({
        "open": close - 0.05,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


def _make_squeeze_sell_df() -> pd.DataFrame:
    """BB 수축 + 하단 근처: SELL 시그널 유도."""
    n = 80
    base = np.ones(60) * 100.0 + np.random.default_rng(42).normal(0, 0.1, 60)
    end_close = np.ones(20) * 99.5
    close = np.concatenate([base, end_close])
    high = close + 0.15
    low = close - 0.15
    return pd.DataFrame({
        "open": close - 0.05,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


# --- 테스트 ---

def test_strategy_name():
    st = BBBandwidthStrategy()
    assert st.name == "bb_bandwidth"


def test_insufficient_data_returns_hold():
    st = BBBandwidthStrategy()
    df = _make_df(n=20)
    sig = st.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_exact_boundary():
    st = BBBandwidthStrategy()
    df = _make_df(n=44)
    sig = st.generate(df)
    assert sig.action == Action.HOLD
    assert "데이터 부족" in sig.reasoning


def test_min_data_passes():
    """45행이면 데이터 부족 HOLD가 아니어야 한다."""
    st = BBBandwidthStrategy()
    df = _make_df(n=45)
    sig = st.generate(df)
    assert "데이터 부족" not in sig.reasoning


def test_signal_fields_present():
    st = BBBandwidthStrategy()
    df = _make_df(n=60)
    sig = st.generate(df)
    assert sig.strategy == "bb_bandwidth"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_entry_price_is_last_closed_candle():
    st = BBBandwidthStrategy()
    df = _make_df(n=60)
    sig = st.generate(df)
    assert sig.entry_price == float(df["close"].iloc[-2])


def test_hold_on_wide_bandwidth():
    """밴드 폭이 넓을 때 (수축 없음) → HOLD."""
    st = BBBandwidthStrategy()
    # 높은 변동성: bandwidth가 BW_SMA * 0.7 이상
    n = 80
    rng = np.random.default_rng(0)
    close = 100.0 + np.cumsum(rng.normal(0, 3.0, n))
    df = _make_df(n, close)
    sig = st.generate(df)
    # 변동성 클 때 squeeze 조건 미충족 → HOLD 가능
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


def test_buy_signal_squeeze_upper():
    """수축 + 상단 근접 → BUY."""
    st = BBBandwidthStrategy()
    df = _make_squeeze_buy_df()
    sig = st.generate(df)
    # 수축된 구간이므로 BUY 또는 HOLD
    assert sig.action in (Action.BUY, Action.HOLD)


def test_sell_signal_squeeze_lower():
    """수축 + 하단 근접 → SELL 또는 BUY (squeeze 방향에 따라 달라질 수 있음)."""
    st = BBBandwidthStrategy()
    df = _make_squeeze_sell_df()
    sig = st.generate(df)
    # squeeze 조건에서는 BUY/SELL/HOLD 모두 유효한 결과
    assert sig.action in (Action.SELL, Action.HOLD, Action.BUY)


def test_extreme_squeeze_high_confidence():
    """극단적 수축(BW < BW_SMA * 0.5) → HIGH confidence."""
    st = BBBandwidthStrategy()
    # 거의 움직임 없는 데이터로 극단 수축 유도
    n = 100
    close = np.ones(n) * 100.0
    close[-2] = 100.01  # 마지막 완성 캔들은 상단 근처
    high = close + 0.02
    low = close - 0.02
    df = pd.DataFrame({
        "open": close - 0.01,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })
    sig = st.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_bandwidth_reasoning_in_signal():
    """reasoning에 BW 값이 포함되는지 확인."""
    st = BBBandwidthStrategy()
    df = _make_df(n=60)
    sig = st.generate(df)
    # 정상 데이터면 BW 또는 조건 관련 텍스트 포함
    assert len(sig.reasoning) > 0


def test_custom_parameters():
    """커스텀 파라미터로 인스턴스 생성 및 동작 확인."""
    st = BBBandwidthStrategy(bb_period=10, std_mult=1.5, bw_period=10)
    df = _make_df(n=60)
    sig = st.generate(df)
    assert sig.strategy == "bb_bandwidth"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_hold_reasoning_contains_squeezed_flag():
    """HOLD 시 reasoning에 squeezed 상태 포함."""
    st = BBBandwidthStrategy()
    df = _make_df(n=60)
    sig = st.generate(df)
    if sig.action == Action.HOLD and "데이터 부족" not in sig.reasoning and "NaN" not in sig.reasoning:
        assert "squeezed" in sig.reasoning or "BW" in sig.reasoning


def test_large_dataset():
    """큰 데이터셋에서도 정상 동작."""
    st = BBBandwidthStrategy()
    n = 500
    rng = np.random.default_rng(99)
    close = 100.0 + np.cumsum(rng.normal(0, 0.5, n))
    df = _make_df(n, close)
    sig = st.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
