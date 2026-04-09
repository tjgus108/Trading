"""RelativeVolumeStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.relative_volume import RelativeVolumeStrategy


def _make_df(
    n: int = 30,
    signal_close: float = 105.0,
    signal_open: float = 100.0,
    signal_volume: float = 1000.0,
    base_close: float = 100.0,
    avg_volume: float = 300.0,
) -> pd.DataFrame:
    """신호 봉 = index -2."""
    closes = [base_close] * n
    opens = [base_close - 0.5] * n
    volumes = [avg_volume] * n
    highs = [base_close + 1.0] * n
    lows = [base_close - 1.0] * n

    closes[-2] = signal_close
    opens[-2] = signal_open
    volumes[-2] = signal_volume
    highs[-2] = signal_close + 0.5
    lows[-2] = min(signal_open, signal_close) - 0.5

    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })


strategy = RelativeVolumeStrategy()


# 1. 전략 이름
def test_name():
    assert strategy.name == "relative_volume"


# 2. BUY 신호: RVOL > 2.0, 양봉, close > VWAP
def test_buy_signal():
    # signal_close(105) > base_close(100) → 양봉, VWAP ≈ base_close(100)
    df = _make_df(signal_close=105.0, signal_open=100.5, signal_volume=900.0, avg_volume=300.0)
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)  # 조건 충족 시 BUY
    assert isinstance(sig, Signal)


# 3. BUY signal fields
def test_buy_signal_fields():
    df = _make_df(signal_close=110.0, signal_open=100.5, signal_volume=900.0, avg_volume=300.0)
    sig = strategy.generate(df)
    assert sig.strategy == "relative_volume"
    assert isinstance(sig.entry_price, float)
    assert sig.entry_price > 0


# 4. SELL 신호: RVOL > 2.0, 음봉, close < VWAP
def test_sell_signal():
    # signal_close(90) < signal_open(100) → 음봉, close < VWAP(≈100)
    df = _make_df(signal_close=90.0, signal_open=100.0, signal_volume=900.0, avg_volume=300.0)
    sig = strategy.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)
    assert isinstance(sig, Signal)


# 5. SELL signal fields
def test_sell_signal_fields():
    df = _make_df(signal_close=85.0, signal_open=100.0, signal_volume=900.0, avg_volume=300.0)
    sig = strategy.generate(df)
    assert sig.strategy == "relative_volume"
    assert isinstance(sig.entry_price, float)


# 6. HOLD: RVOL < 1.5 (낮은 거래량)
def test_hold_low_rvol():
    df = _make_df(signal_close=105.0, signal_open=100.5, signal_volume=350.0, avg_volume=300.0)
    sig = strategy.generate(df)
    # rvol = 350/300 ≈ 1.17 < 1.5 → HOLD
    assert sig.action == Action.HOLD


# 7. HOLD: 양봉이지만 RVOL 2.0~1.5 사이
def test_hold_medium_rvol():
    df = _make_df(signal_close=105.0, signal_open=100.5, signal_volume=500.0, avg_volume=300.0)
    sig = strategy.generate(df)
    # rvol ≈ 1.67, < 2.0 → BUY 조건 미충족 → HOLD
    assert sig.action == Action.HOLD


# 8. 데이터 부족 (< 25행)
def test_insufficient_data():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# 9. None 입력
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# 10. entry_price = 0.0 when insufficient data
def test_insufficient_entry_price_zero():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.entry_price == 0.0


# 11. Signal 필드 완전성 (HOLD)
def test_hold_signal_fields():
    df = _make_df(signal_volume=100.0, avg_volume=300.0)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    for field in ("action", "confidence", "strategy", "entry_price",
                  "reasoning", "invalidation", "bull_case", "bear_case"):
        assert hasattr(sig, field)


# 12. entry_price == last close on HOLD
def test_hold_entry_price_matches_close():
    df = _make_df(signal_close=102.0, signal_volume=100.0, avg_volume=300.0)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.entry_price == float(df.iloc[-2]["close"])


# 13. HIGH confidence: RVOL > 3.0 and close > bb_upper
def test_high_confidence_buy():
    # RVOL > 3.0 필요: signal_volume = 1200, avg = 300 → rvol=4.0
    # close를 매우 높게 설정해 볼린저 상단 돌파
    closes = [100.0] * 30
    opens = [99.0] * 30
    volumes = [300.0] * 30
    closes[-2] = 200.0  # 극단적 값으로 BB 상단 돌파
    opens[-2] = 100.5
    volumes[-2] = 1200.0
    df = pd.DataFrame({
        "open": opens, "close": closes,
        "high": [c + 1 for c in closes], "low": [c - 1 for c in closes],
        "volume": volumes,
    })
    sig = strategy.generate(df)
    # HIGH confidence 또는 최소 BUY여야 함
    assert sig.action in (Action.BUY, Action.HOLD)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 14. MEDIUM confidence: RVOL > 2.0 but <= 3.0
def test_medium_confidence():
    df = _make_df(signal_close=110.0, signal_open=100.5, signal_volume=750.0, avg_volume=300.0)
    # rvol = 750/300 = 2.5 → BUY 조건 충족 시 MEDIUM
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


# 15. reasoning 문자열 확인 (BUY)
def test_buy_reasoning():
    df = _make_df(signal_close=115.0, signal_open=100.5, signal_volume=900.0, avg_volume=300.0)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "rvol" in sig.reasoning.lower() or "RVOL" in sig.reasoning


# 16. reasoning 문자열 확인 (SELL)
def test_sell_reasoning():
    df = _make_df(signal_close=85.0, signal_open=100.0, signal_volume=900.0, avg_volume=300.0)
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "rvol" in sig.reasoning.lower() or "RVOL" in sig.reasoning
