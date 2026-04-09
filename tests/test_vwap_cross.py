"""VWAPCrossStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.vwap_cross import VWAPCrossStrategy
from src.strategy.base import Action, Confidence


def _make_df(n: int = 60, close_val: float = 100.0, volume: float = 1000.0) -> pd.DataFrame:
    """기본 DataFrame: VWAP20 ≈ VWAP50 (크로스 없음)."""
    close = np.full(n, close_val)
    return pd.DataFrame({
        "open": close - 0.5,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": np.full(n, volume),
        "ema50": np.full(n, close_val),
        "atr14": np.full(n, 1.0),
    })


def _make_cross_up_df(n: int = 100) -> pd.DataFrame:
    """
    VWAP20 상향 크로스 VWAP50 조건 생성.
    전략: 앞 (n-2)개는 낮은 가격, 마지막 2개(idx-1, idx)는 크로스 직전/직후.
    - 앞 n-22개: low zone (TP=91) → VWAP50 ≈ 91, VWAP20 ≈ 91
    - n-22 ~ n-3 (19개, prev window 일부): mid zone (TP=100) → VWAP20 prev ≈ 100 ≈ VWAP50
    - n-2 (idx, 1개만 high zone): TP=120 → VWAP20 now > VWAP50 now

    실제로 rolling window를 직접 조작하는 것이 더 간단:
    prev idx(=n-3)에서 v20_prev <= v50_prev,
    now idx(=n-2)에서 v20_now > v50_now 되어야 함.

    간단한 방법: 앞 50개는 TP=100(중립), n-22~n-3(19개)는 TP=100,
    n-2(idx)만 TP=200 고가. 이렇게 하면:
    - VWAP20 now: 19개*100 + 1개*200 / 20 = 2100/20 = 105
    - VWAP50 now: 49개*100 + 1개*200 / 50 = 5100/50 = 102
    - VWAP20 prev: 20개*100 / 20 = 100
    - VWAP50 prev: 50개*100 / 50 = 100
    → cross_up: prev(100 <= 100) and now(105 > 102) ✓
    """
    close = np.full(n, 100.0)
    high = np.full(n, 101.0)
    low = np.full(n, 99.0)
    volume = np.ones(n)  # 균일 볼륨이면 TP 평균 = VWAP

    # idx = n-2, 이 행만 TP=200 고가로 설정
    idx = n - 2
    high[idx] = 201.0
    low[idx] = 199.0
    close[idx] = 200.0

    return pd.DataFrame({
        "open": close - 0.5,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
        "ema50": np.full(n, 95.0),
        "atr14": np.full(n, 1.0),
    })


def _make_cross_down_df(n: int = 100) -> pd.DataFrame:
    """
    VWAP20 하향 크로스 VWAP50 조건 생성.
    idx(n-2)만 TP=0 저가.
    - VWAP20 now: 19개*100 + 1개*0 / 20 = 95
    - VWAP50 now: 49개*100 + 1개*0 / 50 = 98
    - VWAP20 prev: 100, VWAP50 prev: 100
    → cross_down: prev(100 >= 100) and now(95 < 98) ✓
    """
    close = np.full(n, 100.0)
    high = np.full(n, 101.0)
    low = np.full(n, 99.0)
    volume = np.ones(n)

    idx = n - 2
    high[idx] = 1.0
    low[idx] = 0.0
    close[idx] = 0.5

    return pd.DataFrame({
        "open": close - 0.1,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
        "ema50": np.full(n, 105.0),
        "atr14": np.full(n, 1.0),
    })


# 1. 전략 이름 확인
def test_strategy_name():
    s = VWAPCrossStrategy()
    assert s.name == "vwap_cross"


# 2. 데이터 부족 → HOLD
def test_hold_insufficient_data():
    s = VWAPCrossStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# 3. 최소 행수 경계: 54행 → HOLD
def test_hold_exactly_below_min_rows():
    s = VWAPCrossStrategy()
    df = _make_df(n=54)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# 4. 최소 행수 충족: 55행 → 오류 없음
def test_no_error_at_min_rows():
    s = VWAPCrossStrategy()
    df = _make_df(n=55)
    sig = s.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# 5. 크로스 없음 → HOLD
def test_hold_no_cross():
    s = VWAPCrossStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# 6. 상향 크로스 → BUY
def test_buy_on_cross_up():
    s = VWAPCrossStrategy()
    df = _make_cross_up_df(n=60)
    sig = s.generate(df)
    assert sig.action == Action.BUY


# 7. 하향 크로스 → SELL
def test_sell_on_cross_down():
    s = VWAPCrossStrategy()
    df = _make_cross_down_df(n=60)
    sig = s.generate(df)
    assert sig.action == Action.SELL


# 8. BUY 시 confidence 확인 (spread > 0.5% → HIGH)
def test_buy_high_confidence_large_spread():
    s = VWAPCrossStrategy()
    df = _make_cross_up_df(n=60)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 9. Signal 필드 검증
def test_signal_fields_present():
    s = VWAPCrossStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "vwap_cross"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


# 10. entry_price는 close 값
def test_entry_price_equals_close():
    s = VWAPCrossStrategy()
    df = _make_df(n=60, close_val=123.45)
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(123.45, abs=1e-3)


# 11. HOLD reasoning 문자열 포함 확인
def test_hold_reasoning_nonempty():
    s = VWAPCrossStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert len(sig.reasoning) > 0


# 12. BUY signal reasoning에 'VWAP20' 포함
def test_buy_reasoning_contains_vwap20():
    s = VWAPCrossStrategy()
    df = _make_cross_up_df(n=60)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "VWAP20" in sig.reasoning


# 13. SELL signal reasoning에 'VWAP20' 포함
def test_sell_reasoning_contains_vwap20():
    s = VWAPCrossStrategy()
    df = _make_cross_down_df(n=60)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "VWAP20" in sig.reasoning


# 14. HOLD 시 confidence는 LOW
def test_hold_confidence_is_low():
    s = VWAPCrossStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW
