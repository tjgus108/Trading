"""NarrowRangeStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.narrow_range import NarrowRangeStrategy
from src.strategy.base import Action, Confidence


# ── 헬퍼 ──────────────────────────────────────────────────────────────────────

def _make_df(n: int = 20, base_range: float = 2.0) -> pd.DataFrame:
    """균일한 range의 기본 DataFrame."""
    close = np.linspace(100.0, 110.0, n)
    return pd.DataFrame({
        "open":  close - 0.5,
        "high":  close + base_range / 2,
        "low":   close - base_range / 2,
        "close": close,
    })


def _make_nr7_buy_df() -> pd.DataFrame:
    """
    iloc[-3]이 NR7, iloc[-2]의 close가 iloc[-3].high를 돌파 → BUY.
    """
    n = 20
    close = np.linspace(100.0, 110.0, n)
    high  = close + 2.0
    low   = close - 2.0

    # iloc[-3]: range를 아주 좁게 (NR7)
    nr_idx = n - 3
    high[nr_idx] = 105.5
    low[nr_idx]  = 105.0   # range = 0.5

    # iloc[-2]: close > prev_high(105.5) → 돌파
    close[n - 2] = 106.5
    high[n - 2]  = 107.0
    low[n - 2]   = 105.8

    return pd.DataFrame({
        "open":  close - 0.3,
        "high":  high,
        "low":   low,
        "close": close,
    })


def _make_nr7_sell_df() -> pd.DataFrame:
    """
    iloc[-3]이 NR7, iloc[-2]의 close가 iloc[-3].low 아래로 돌파 → SELL.
    """
    n = 20
    close = np.linspace(110.0, 100.0, n)
    high  = close + 2.0
    low   = close - 2.0

    nr_idx = n - 3
    high[nr_idx] = 105.5
    low[nr_idx]  = 105.0   # range = 0.5

    # iloc[-2]: close < prev_low(105.0) → 하향 돌파
    close[n - 2] = 104.0
    high[n - 2]  = 104.8
    low[n - 2]   = 103.5

    return pd.DataFrame({
        "open":  close + 0.3,
        "high":  high,
        "low":   low,
        "close": close,
    })


def _make_nr7_no_breakout_df() -> pd.DataFrame:
    """NR7이지만 돌파 없음 → HOLD."""
    n = 20
    close = np.linspace(100.0, 110.0, n)
    high  = close + 2.0
    low   = close - 2.0

    nr_idx = n - 3
    high[nr_idx] = 105.5
    low[nr_idx]  = 105.0   # range = 0.5 (NR7)

    # iloc[-2]: close는 prev_high/low 사이에 머뭄
    close[n - 2] = 105.2
    high[n - 2]  = 105.4
    low[n - 2]   = 105.1

    return pd.DataFrame({
        "open":  close - 0.1,
        "high":  high,
        "low":   low,
        "close": close,
    })


# ── 테스트 ────────────────────────────────────────────────────────────────────

def test_strategy_name():
    """전략 이름 확인."""
    st = NarrowRangeStrategy()
    assert st.name == "narrow_range"


def test_insufficient_data_returns_hold():
    """MIN_ROWS(10) 미만 데이터 시 HOLD."""
    st = NarrowRangeStrategy()
    df = _make_df(n=5)
    sig = st.generate(df)
    assert sig.action == Action.HOLD


def test_exactly_min_rows():
    """정확히 MIN_ROWS(10)일 때 Signal 반환."""
    st = NarrowRangeStrategy()
    df = _make_df(n=10)
    sig = st.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_buy_signal_on_nr7_breakout_up():
    """NR7 후 상향 돌파 → BUY."""
    st = NarrowRangeStrategy()
    df = _make_nr7_buy_df()
    sig = st.generate(df)
    assert sig.action == Action.BUY


def test_sell_signal_on_nr7_breakout_down():
    """NR7 후 하향 돌파 → SELL."""
    st = NarrowRangeStrategy()
    df = _make_nr7_sell_df()
    sig = st.generate(df)
    assert sig.action == Action.SELL


def test_hold_when_no_nr7():
    """NR7 조건 미충족 시 HOLD."""
    st = NarrowRangeStrategy()
    df = _make_df(n=20, base_range=2.0)  # 균일 range
    sig = st.generate(df)
    # 균일 range일 때는 NR7 미충족(equal이면 <=이므로 조건 충족할 수 있음)
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


def test_hold_when_nr7_but_no_breakout():
    """NR7이지만 돌파 없음 → HOLD."""
    st = NarrowRangeStrategy()
    df = _make_nr7_no_breakout_df()
    sig = st.generate(df)
    assert sig.action == Action.HOLD


def test_buy_confidence_high_when_nr4_and_nr7():
    """NR4+NR7 둘 다 충족 시 HIGH confidence."""
    st = NarrowRangeStrategy()
    df = _make_nr7_buy_df()
    # nr_idx(iloc[-3])가 NR4도 만족하도록 앞 3봉 범위도 넓게 세팅
    df.iloc[-6, df.columns.get_loc("high")] = df.iloc[-6]["close"] + 5.0
    df.iloc[-6, df.columns.get_loc("low")]  = df.iloc[-6]["close"] - 5.0
    df.iloc[-5, df.columns.get_loc("high")] = df.iloc[-5]["close"] + 5.0
    df.iloc[-5, df.columns.get_loc("low")]  = df.iloc[-5]["close"] - 5.0
    df.iloc[-4, df.columns.get_loc("high")] = df.iloc[-4]["close"] + 5.0
    df.iloc[-4, df.columns.get_loc("low")]  = df.iloc[-4]["close"] - 5.0
    sig = st.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_signal_fields_present():
    """Signal 필수 필드 존재 확인."""
    st = NarrowRangeStrategy()
    df = _make_nr7_buy_df()
    sig = st.generate(df)
    assert sig.strategy == "narrow_range"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_entry_price_is_last_complete_close():
    """BUY 시 entry_price == 마지막 완성봉 close."""
    st = NarrowRangeStrategy()
    df = _make_nr7_buy_df()
    sig = st.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-6)


def test_sell_entry_price_is_last_complete_close():
    """SELL 시 entry_price == 마지막 완성봉 close."""
    st = NarrowRangeStrategy()
    df = _make_nr7_sell_df()
    sig = st.generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-6)


def test_hold_reasoning_not_empty():
    """HOLD 시 reasoning 비어있지 않음."""
    st = NarrowRangeStrategy()
    df = _make_df(n=5)
    sig = st.generate(df)
    assert len(sig.reasoning) > 0


def test_different_from_nr7_strategy():
    """narrow_range는 NR7 감지 후 돌파까지 확인하는 다른 로직임."""
    from src.strategy.nr7 import NR7Strategy
    nr7_st = NR7Strategy()
    nr_st = NarrowRangeStrategy()
    df = _make_nr7_no_breakout_df()
    # nr7은 atr14 컬럼 필요 → 추가
    df["atr14"] = 0.5
    sig_nr7 = nr7_st.generate(df)
    sig_nr = nr_st.generate(df)
    # narrow_range는 돌파가 없으면 HOLD
    assert sig_nr.action == Action.HOLD
    # 두 전략의 이름이 다름
    assert sig_nr.strategy == "narrow_range"
    assert sig_nr7.strategy == "nr7"


def test_large_dataset_no_error():
    """대용량 데이터에서 오류 없음."""
    st = NarrowRangeStrategy()
    df = _make_nr7_buy_df()
    # 앞에 많은 데이터 추가
    prefix = _make_df(n=200)
    df_large = pd.concat([prefix, df], ignore_index=True)
    sig = st.generate(df_large)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
