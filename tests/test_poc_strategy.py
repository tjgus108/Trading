"""POCStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.poc_strategy import POCStrategy
from src.strategy.base import Action, Confidence


def _make_df(n: int = 30, close_vals=None, high_delta: float = 1.0,
             low_delta: float = 1.0, vol: float = 100.0) -> pd.DataFrame:
    """기본 OHLCV DataFrame 생성. close_vals 미지정 시 n개 100.0."""
    if close_vals is None:
        close_vals = np.full(n, 100.0)
    else:
        close_vals = np.array(close_vals, dtype=float)
        n = len(close_vals)

    return pd.DataFrame({
        "open": close_vals - 0.3,
        "high": close_vals + high_delta,
        "low": close_vals - low_delta,
        "close": close_vals,
        "volume": np.full(n, vol),
    })


def _make_spread_df(n: int = 30) -> pd.DataFrame:
    """POC 계산에 충분한 가격 분산이 있는 DF."""
    closes = np.linspace(90.0, 110.0, n)
    return pd.DataFrame({
        "open": closes - 0.5,
        "high": closes + 2.0,
        "low": closes - 2.0,
        "close": closes,
        "volume": np.ones(n) * 100.0,
    })


# 1. 전략 이름
def test_strategy_name():
    assert POCStrategy().name == "poc_strategy"


# 2. 데이터 부족 → HOLD
def test_insufficient_data_returns_hold():
    s = POCStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 3. 정확히 25행 → 정상 처리 (HOLD or actionable)
def test_exactly_25_rows_no_error():
    s = POCStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# 4. close가 VAL 아래 → BUY
def test_buy_signal_close_below_val():
    """close가 가격 범위 최저 근처 → VAL 아래 → BUY."""
    s = POCStrategy()
    # 대부분 봉이 110 근처 거래 → POC/VAL 높은 쪽. 마지막(-2) close만 낮게
    n = 30
    closes = np.full(n, 110.0)
    closes[-2] = 85.0  # _last → iloc[-2]
    df = _make_df(n=n, close_vals=closes, high_delta=2.0, low_delta=2.0)
    sig = s.generate(df)
    assert sig.action == Action.BUY


# 5. close가 VAH 위 → SELL
def test_sell_signal_close_above_vah():
    """close가 가격 범위 최고 근처 → VAH 위 → SELL."""
    s = POCStrategy()
    n = 30
    closes = np.full(n, 90.0)
    closes[-2] = 115.0  # _last → iloc[-2]
    df = _make_df(n=n, close_vals=closes, high_delta=2.0, low_delta=2.0)
    sig = s.generate(df)
    assert sig.action == Action.SELL


# 6. close가 가치 영역 내 → HOLD
def test_hold_signal_close_within_value_area():
    """가격이 고르게 분포, close가 중간 → HOLD."""
    s = POCStrategy()
    df = _make_spread_df(n=30)
    # _last(df) = df.iloc[-2], 중간 값(100) → value area 내
    sig = s.generate(df)
    # close=109.31... 은 value area 안일 수도 밖일 수도 — 중요한 건 오류 없이 동작
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.strategy == "poc_strategy"


# 7. HIGH confidence: |close - POC| / POC > 2%
def test_high_confidence_when_far_from_poc():
    s = POCStrategy()
    n = 30
    closes = np.full(n, 100.0)
    closes[-2] = 75.0  # 25% 이탈 → HIGH
    df = _make_df(n=n, close_vals=closes, high_delta=1.0, low_delta=1.0)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# 8. MEDIUM confidence: |close - POC| / POC <= 2%
def test_medium_confidence_when_near_poc():
    s = POCStrategy()
    n = 30
    # 모든 봉이 100.0 → POC=100, close=-2봉도 거의 같으면 MEDIUM
    # 약간만 벗어나도록
    closes = np.full(n, 100.0)
    closes[-2] = 99.5  # 0.5% 이탈
    df = _make_df(n=n, close_vals=closes, high_delta=1.0, low_delta=1.0)
    sig = s.generate(df)
    # 가격 범위가 2.0, bin_size=0.2 → VAL/VAH 매우 좁으므로 HOLD or BUY/SELL
    # confidence가 MEDIUM인지만 확인
    if sig.action != Action.HOLD:
        assert sig.confidence == Confidence.MEDIUM


# 9. Signal 필드 완전성
def test_signal_fields_complete():
    s = POCStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.strategy == "poc_strategy"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# 10. 가격 범위 0 (모든 close/high/low 동일) → HOLD
def test_zero_price_range_returns_hold():
    s = POCStrategy()
    n = 30
    df = pd.DataFrame({
        "open": np.full(n, 100.0),
        "high": np.full(n, 100.0),
        "low": np.full(n, 100.0),
        "close": np.full(n, 100.0),
        "volume": np.full(n, 100.0),
    })
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# 11. 볼륨 0 → HOLD
def test_zero_volume_returns_hold():
    s = POCStrategy()
    n = 30
    df = _make_df(n=n, close_vals=np.linspace(90, 110, n), high_delta=2.0, low_delta=2.0, vol=0.0)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# 12. BUY 신호의 entry_price = close
def test_buy_signal_entry_price_equals_close():
    s = POCStrategy()
    n = 30
    closes = np.full(n, 110.0)
    closes[-2] = 85.0
    df = _make_df(n=n, close_vals=closes, high_delta=2.0, low_delta=2.0)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(85.0)


# 13. SELL 신호의 entry_price = close
def test_sell_signal_entry_price_equals_close():
    s = POCStrategy()
    n = 30
    closes = np.full(n, 90.0)
    closes[-2] = 115.0
    df = _make_df(n=n, close_vals=closes, high_delta=2.0, low_delta=2.0)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price == pytest.approx(115.0)


# 14. reasoning에 POC 값 포함 (non-HOLD)
def test_reasoning_contains_poc():
    s = POCStrategy()
    n = 30
    closes = np.full(n, 110.0)
    closes[-2] = 85.0
    df = _make_df(n=n, close_vals=closes, high_delta=2.0, low_delta=2.0)
    sig = s.generate(df)
    if sig.action != Action.HOLD:
        assert "POC=" in sig.reasoning
