"""EaseOfMovementStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.ease_of_movement import EaseOfMovementStrategy
from src.strategy.base import Action, Confidence


def _make_df(n: int = 30, close_val: float = 100.0, ema50_val: float = 100.0,
             high_val: float = 101.0, low_val: float = 99.0,
             volume: float = 1e6) -> pd.DataFrame:
    """기본 DataFrame (EOM ≈ 0, no signal)."""
    return pd.DataFrame({
        "open": np.full(n, close_val - 0.5),
        "high": np.full(n, high_val),
        "low": np.full(n, low_val),
        "close": np.full(n, close_val),
        "volume": np.full(n, volume),
        "ema50": np.full(n, ema50_val),
        "atr14": np.full(n, 1.0),
    })


def _make_buy_df(n: int = 80) -> pd.DataFrame:
    """
    BUY 조건: EOM > 0, 상승 중, close > ema50.
    - 가격이 일정하게 상승 → midpoint_move > 0
    - 볼륨 매우 낮게, 고저차 작게 → box_ratio 작게 → EMV 크게
    - EMA(14)가 수렴할 수 있도록 n=80 사용
    """
    base = 100.0
    close = np.linspace(base, base + n * 2.0, n)  # 강한 상승
    high = close + 0.1
    low = close - 0.1
    volume = np.full(n, 1.0)  # 매우 낮은 볼륨 → EOM 크게
    ema50 = np.full(n, base - 20.0)  # close >> ema50 보장

    return pd.DataFrame({
        "open": close - 0.05,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
        "ema50": ema50,
        "atr14": np.full(n, 0.2),
    })


def _make_sell_df(n: int = 80) -> pd.DataFrame:
    """
    SELL 조건: EOM < 0, 하락 중, close < ema50.
    """
    base = 200.0
    close = np.linspace(base, base - n * 2.0, n)  # 강한 하락
    high = close + 0.1
    low = close - 0.1
    volume = np.full(n, 1.0)
    ema50 = np.full(n, base + 20.0)  # close << ema50 보장

    return pd.DataFrame({
        "open": close - 0.05,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
        "ema50": ema50,
        "atr14": np.full(n, 0.2),
    })


# 1. 전략 이름 확인
def test_strategy_name():
    s = EaseOfMovementStrategy()
    assert s.name == "ease_of_movement"


# 2. 데이터 부족 → HOLD
def test_hold_insufficient_data():
    s = EaseOfMovementStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# 3. 최소 행수 경계: 19행 → HOLD
def test_hold_below_min_rows():
    s = EaseOfMovementStrategy()
    df = _make_df(n=19)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# 4. 최소 행수 충족: 20행 → 오류 없음
def test_no_error_at_min_rows():
    s = EaseOfMovementStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# 5. 정적 데이터 (가격 변동 없음) → HOLD (EOM ≈ 0)
def test_hold_no_price_movement():
    s = EaseOfMovementStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# 6. 상승 추세 → BUY
def test_buy_on_uptrend():
    s = EaseOfMovementStrategy()
    df = _make_buy_df(n=40)
    sig = s.generate(df)
    assert sig.action == Action.BUY


# 7. 하락 추세 → SELL
def test_sell_on_downtrend():
    s = EaseOfMovementStrategy()
    df = _make_sell_df(n=40)
    sig = s.generate(df)
    assert sig.action == Action.SELL


# 8. BUY 시 confidence 확인
def test_buy_confidence_type():
    s = EaseOfMovementStrategy()
    df = _make_buy_df(n=40)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 9. SELL 시 confidence 확인
def test_sell_confidence_type():
    s = EaseOfMovementStrategy()
    df = _make_sell_df(n=40)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 10. Signal 필드 검증
def test_signal_fields_present():
    s = EaseOfMovementStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.strategy == "ease_of_movement"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


# 11. entry_price는 float
def test_entry_price_is_float():
    s = EaseOfMovementStrategy()
    df = _make_df(n=30, close_val=55.5)
    sig = s.generate(df)
    assert isinstance(sig.entry_price, float)


# 12. HOLD 시 confidence는 LOW
def test_hold_confidence_is_low():
    s = EaseOfMovementStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 13. close < ema50이면 BUY 안 함
def test_no_buy_when_close_below_ema50():
    s = EaseOfMovementStrategy()
    df = _make_buy_df(n=40)
    # ema50을 close보다 훨씬 높게 설정
    df["ema50"] = df["close"] + 50.0
    sig = s.generate(df)
    assert sig.action != Action.BUY


# 14. close > ema50이면 SELL 안 함
def test_no_sell_when_close_above_ema50():
    s = EaseOfMovementStrategy()
    df = _make_sell_df(n=40)
    # ema50을 close보다 훨씬 낮게 설정
    df["ema50"] = df["close"] - 50.0
    sig = s.generate(df)
    assert sig.action != Action.SELL
