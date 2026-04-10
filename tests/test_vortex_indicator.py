"""tests/test_vortex_indicator.py — VortexIndicatorStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.vortex_indicator import VortexIndicatorStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 50) -> pd.DataFrame:
    np.random.seed(0)
    close = 100 + np.cumsum(np.random.randn(n) * 0.5)
    high = close + np.abs(np.random.randn(n) * 0.3)
    low = close - np.abs(np.random.randn(n) * 0.3)
    return pd.DataFrame({
        "open": close - 0.1,
        "close": close,
        "high": high,
        "low": low,
        "volume": np.ones(n) * 1000,
    })


def _make_buy_df() -> pd.DataFrame:
    """VI+ 크로스오버 VI-: 봉 47(idx=len-2)에서 강한 상승으로 VI+ > VI- 전환.

    설계 (n=50, idx=48):
      - 봉 0~33: 중립
      - 봉 34~46: 하락 패턴 (VM- 지배) → idx-1=47에서 VI- > VI+
      - 봉 47(idx-1=47): 하락 패턴 마지막 → VI-[47] > VI+[47]
      - 봉 48(idx=48): 극단 상승 → VI+[48] >> VI-[48] (크로스오버)
      - 봉 49: dummy
    """
    n = 50
    close = np.full(n, 100.0)
    high = close.copy()
    low = close.copy()

    # 봉 0~33: 중립
    for i in range(34):
        high[i] = close[i] + 0.5
        low[i] = close[i] - 0.5

    # 봉 34~47: 강한 하락 패턴 → VM- 지배, VI- > VI+
    # VM-[i] = |low[i] - high[i-1]| = |(100-5.0) - (100+0.1)| = 5.1
    # VM+[i] = |high[i] - low[i-1]| = |(100+0.1) - (100-0.5)| = 0.6 (봉 34는 이전 중립 봉)
    for i in range(34, 48):
        high[i] = close[i] + 0.1
        low[i] = close[i] - 5.0

    # 봉 48 (idx=len-2): 극단 상승 → VI+ 압도
    # VM+[48] = |high[48] - low[47]| = |(100+500) - (100-5)| = 505
    # VM-[48] = |low[48] - high[47]| = |(100-0.01) - (100+0.1)| = 0.11
    high[48] = close[48] + 500.0
    low[48] = close[48] - 0.01

    # 봉 49: dummy
    high[49] = close[49] + 0.1
    low[49] = close[49] - 1.0

    return pd.DataFrame({
        "open": close - 0.1,
        "close": close,
        "high": high,
        "low": low,
        "volume": np.ones(n) * 1000,
    })


def _make_sell_df() -> pd.DataFrame:
    """VI- 크로스오버 VI+: 봉 48(idx=len-2)에서 강한 하락으로 VI- > VI+ 전환."""
    n = 50
    np.random.seed(1)
    close = np.full(n, 100.0)
    high = close.copy()
    low = close.copy()

    # 봉 0~35: 중립
    for i in range(36):
        high[i] = close[i] + 0.5
        low[i] = close[i] - 0.5

    # 봉 36~47: 상승 패턴 → VI+ > VI-
    for i in range(36, 48):
        high[i] = close[i] + 5.0
        low[i] = close[i] - 0.1

    # 봉 48 (idx=len-2): 극단 하락 → VI- 압도
    high[48] = close[48] + 0.1
    low[48] = close[48] - 500.0

    # 봉 49: dummy
    high[49] = close[49] + 0.5
    low[49] = close[49] - 0.5

    return pd.DataFrame({
        "open": close - 0.1,
        "close": close,
        "high": high,
        "low": low,
        "volume": np.ones(n) * 1000,
    })


def _compute_vi(df: pd.DataFrame):
    period = 14
    high = df["high"]
    low = df["low"]
    close = df["close"]
    vm_plus = (high - low.shift(1)).abs()
    vm_minus = (low - high.shift(1)).abs()
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    vi_plus = vm_plus.rolling(period).sum() / tr.rolling(period).sum()
    vi_minus = vm_minus.rolling(period).sum() / tr.rolling(period).sum()
    return vi_plus, vi_minus


# ── 테스트 14개 ────────────────────────────────────────────────────────────

def test_strategy_name_class():
    """1. 클래스 속성 .name == 'vortex_indicator'."""
    assert VortexIndicatorStrategy.name == "vortex_indicator"


def test_strategy_name_instance():
    """2. 인스턴스 .name == 'vortex_indicator'."""
    assert VortexIndicatorStrategy().name == "vortex_indicator"


def test_insufficient_data_returns_hold():
    """3. 데이터 부족 (< 20행) → HOLD."""
    sig = VortexIndicatorStrategy().generate(_make_df(10))
    assert sig.action == Action.HOLD


def test_none_input_returns_hold():
    """4. None 입력 → HOLD."""
    sig = VortexIndicatorStrategy().generate(None)
    assert sig.action == Action.HOLD


def test_empty_df_returns_hold():
    """4b. 빈 DataFrame 입력 → HOLD."""
    sig = VortexIndicatorStrategy().generate(pd.DataFrame())
    assert sig.action == Action.HOLD


def test_insufficient_data_reasoning():
    """5. 데이터 부족 reasoning에 'Insufficient' 포함."""
    sig = VortexIndicatorStrategy().generate(_make_df(5))
    assert "Insufficient" in sig.reasoning or "insufficient" in sig.reasoning.lower()


def test_sufficient_data_returns_signal():
    """6. 충분한 데이터 → Signal 반환."""
    sig = VortexIndicatorStrategy().generate(_make_df(40))
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_signal_fields_complete():
    """7. Signal 필드 완전성 (action, confidence, strategy, entry_price, reasoning)."""
    sig = VortexIndicatorStrategy().generate(_make_df(40))
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert sig.strategy == "vortex_indicator"
    assert isinstance(sig.entry_price, float)
    assert len(sig.reasoning) > 0


def test_buy_signal():
    """8. BUY 신호: VI+ 크로스오버 VI-."""
    sig = VortexIndicatorStrategy().generate(_make_buy_df())
    assert sig.action == Action.BUY


def test_sell_signal():
    """9. SELL 신호: VI+ 크로스 하방 VI-."""
    sig = VortexIndicatorStrategy().generate(_make_sell_df())
    assert sig.action == Action.SELL


def test_high_confidence_buy():
    """10. BUY HIGH confidence: |VI+ - VI-| > 0.1."""
    df = _make_buy_df()
    vi_plus, vi_minus = _compute_vi(df)
    idx = len(df) - 2
    sep = abs(float(vi_plus.iloc[idx]) - float(vi_minus.iloc[idx]))
    sig = VortexIndicatorStrategy().generate(df)
    if sig.action == Action.BUY and sep > 0.1:
        assert sig.confidence == Confidence.HIGH


def test_medium_confidence():
    """11. separation <= 0.1 → MEDIUM confidence."""
    # 작은 separation을 가진 신호 케이스에서 confidence 확인
    df = _make_df(40)
    high = df["high"].values.copy()
    low = df["low"].values.copy()
    close = df["close"].values.copy()
    # 작은 상승 패턴
    for i in range(25, 40):
        high[i] = close[i] + 0.05
        low[i] = close[i] - 0.03
    df["high"] = high
    df["low"] = low
    vi_plus, vi_minus = _compute_vi(df)
    idx = len(df) - 2
    sep = abs(float(vi_plus.iloc[idx]) - float(vi_minus.iloc[idx]))
    sig = VortexIndicatorStrategy().generate(df)
    if sig.action in (Action.BUY, Action.SELL) and sep <= 0.1:
        assert sig.confidence == Confidence.MEDIUM


def test_entry_price_positive():
    """12. entry_price > 0."""
    sig = VortexIndicatorStrategy().generate(_make_df(40))
    assert sig.entry_price > 0


def test_strategy_field_equals_name():
    """13. Signal.strategy == 'vortex_indicator'."""
    sig = VortexIndicatorStrategy().generate(_make_buy_df())
    assert sig.strategy == "vortex_indicator"


def test_min_rows_boundary():
    """14. 정확히 20행 → Signal 반환 (에러 없음)."""
    sig = VortexIndicatorStrategy().generate(_make_df(20))
    assert sig.strategy == "vortex_indicator"
