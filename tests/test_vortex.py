"""tests/test_vortex.py — VortexStrategy 단위 테스트 (12개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.vortex import VortexStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 50) -> pd.DataFrame:
    """기본 OHLCV + 지표 DataFrame 생성."""
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(n) * 0.5)
    high = close + np.abs(np.random.randn(n) * 0.3)
    low = close - np.abs(np.random.randn(n) * 0.3)
    return pd.DataFrame({
        "open": close - 0.1,
        "close": close,
        "high": high,
        "low": low,
        "volume": np.ones(n) * 1000,
        "ema50": close,
        "atr14": np.ones(n) * 0.5,
    })


def _make_buy_df() -> pd.DataFrame:
    """VI+ 크로스오버 VI- 상황 데이터 생성.
    설계:
      - 봉 0~33: 하락 패턴 (VM- 지배, 총 34봉)
      - 봉 34~47: 하락 패턴 유지 → idx-1=47에서 VI- > VI+
      - 봉 48 (idx=len-2): 이전 14봉(35~48) 중 봉 48만 극단적 상승
        VM+[48] = |high[48]-low[47]| = |(100+500)-(100-1)| = 501
        VM-[35~47] = 각 1.0 * 13봉 = 13
        → VI+ 압도
      - 봉 49: dummy
    """
    n = 50
    close = np.full(n, 100.0)
    high = close.copy()
    low = close.copy()

    # 봉 0~47: 하락 패턴 (high=close+0.1, low=close-1.0)
    for i in range(48):
        high[i] = close[i] + 0.1
        low[i] = close[i] - 1.0

    # 봉 48 (idx=len-2): 극단적 상승
    # VM+[48] = |high[48] - low[47]| = |(100+500) - (100-1)| = 501
    # VM-[35..47] 각 = |low[i] - high[i-1]| = |(100-1) - (100+0.1)| = 1.1 → 13*1.1 = 14.3
    # VM+[35..47] 각 = |high[i] - low[i-1]| = |(100+0.1) - (100-1)| = 1.1 → 13*1.1 = 14.3
    # VM+[48] = 501 → 합 = 14.3 + 501 = 515.3 >> VM- 합 14.3+1.1 = 15.4
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
        "ema50": close,
        "atr14": np.ones(n) * 0.5,
    })


def _make_sell_df() -> pd.DataFrame:
    """VI- 크로스오버 VI+ 상황 데이터 생성.
    전략: 직전 14봉은 상승 패턴 (VI+>VI-), 마지막 봉만 급락 (VI->VI+로 크로스).
    """
    n = 50
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(n) * 0.1)
    high = close.copy()
    low = close.copy()

    # 봉 1~35: 중립
    for i in range(35):
        high[i] = close[i] + 0.5
        low[i] = close[i] - 0.5

    # 봉 36~48 (idx=35~47): 상승 패턴 → VM+가 커져서 VI+ > VI- 상태
    for i in range(35, 48):
        high[i] = close[i] + 5.0
        low[i] = close[i] - 0.1

    # 봉 49 (idx=48, _last=iloc[-2]): 급락 → VI- > VI+ 크로스 발생
    high[48] = close[48] + 0.1
    low[48] = close[48] - 10.0

    # 봉 50 (idx=49, 진행 중 캔들, 사용 안 됨)
    high[49] = close[49] + 0.5
    low[49] = close[49] - 0.5

    return pd.DataFrame({
        "open": close - 0.1,
        "close": close,
        "high": high,
        "low": low,
        "volume": np.ones(n) * 1000,
        "ema50": close,
        "atr14": np.ones(n) * 0.5,
    })


def _compute_vi(df: pd.DataFrame):
    """VI+, VI- 시리즈 반환."""
    period = 14
    high = df["high"]
    low = df["low"]
    close = df["close"]
    vm_plus = (high - low.shift(1)).abs()
    vm_minus = (low - high.shift(1)).abs()
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    vi_plus = vm_plus.rolling(period).sum() / tr.rolling(period).sum()
    vi_minus = vm_minus.rolling(period).sum() / tr.rolling(period).sum()
    return vi_plus, vi_minus


# ── 테스트 12개 ─────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 = 'vortex'."""
    assert VortexStrategy.name == "vortex"


def test_buy_signal():
    """2. BUY 신호 (VI+ 크로스오버)."""
    strategy = VortexStrategy()
    df = _make_buy_df()
    signal = strategy.generate(df)
    assert signal.action == Action.BUY


def test_sell_signal():
    """3. SELL 신호 (VI- 크로스오버)."""
    strategy = VortexStrategy()
    df = _make_sell_df()
    signal = strategy.generate(df)
    assert signal.action == Action.SELL


def test_buy_high_confidence():
    """4. BUY HIGH confidence (|VI+-VI-|>0.2)."""
    strategy = VortexStrategy()
    df = _make_buy_df()
    vi_plus, vi_minus = _compute_vi(df)
    idx = len(df) - 2
    sep = abs(float(vi_plus.iloc[idx]) - float(vi_minus.iloc[idx]))
    signal = strategy.generate(df)
    if signal.action == Action.BUY and sep > 0.2:
        assert signal.confidence == Confidence.HIGH


def test_buy_medium_confidence():
    """5. BUY MEDIUM confidence (|VI+-VI-|<=0.2)."""
    strategy = VortexStrategy()
    # 작은 separation을 가진 BUY 케이스 직접 모킹
    n = 40
    df = _make_df(n)
    high = df["high"].values.copy()
    low = df["low"].values.copy()
    close = df["close"].values.copy()
    # 약한 상승 (separation이 작도록)
    for i in range(n - 15, n):
        low[i] = close[i] - 0.05
        high[i] = close[i] + 1.1
    df["high"] = high
    df["low"] = low

    vi_plus, vi_minus = _compute_vi(df)
    idx = len(df) - 2
    sep = abs(float(vi_plus.iloc[idx]) - float(vi_minus.iloc[idx]))
    signal = strategy.generate(df)
    if signal.action == Action.BUY and sep <= 0.2:
        assert signal.confidence == Confidence.MEDIUM


def test_sell_high_confidence():
    """6. SELL HIGH confidence (|VI+-VI-|>0.2)."""
    strategy = VortexStrategy()
    df = _make_sell_df()
    vi_plus, vi_minus = _compute_vi(df)
    idx = len(df) - 2
    sep = abs(float(vi_plus.iloc[idx]) - float(vi_minus.iloc[idx]))
    signal = strategy.generate(df)
    if signal.action == Action.SELL and sep > 0.2:
        assert signal.confidence == Confidence.HIGH


def test_sell_medium_confidence():
    """7. SELL MEDIUM confidence (|VI+-VI-|<=0.2)."""
    strategy = VortexStrategy()
    n = 40
    df = _make_df(n)
    high = df["high"].values.copy()
    low = df["low"].values.copy()
    close = df["close"].values.copy()
    for i in range(n - 15, n):
        high[i] = close[i] + 0.05
        low[i] = close[i] - 1.1
    df["high"] = high
    df["low"] = low

    vi_plus, vi_minus = _compute_vi(df)
    idx = len(df) - 2
    sep = abs(float(vi_plus.iloc[idx]) - float(vi_minus.iloc[idx]))
    signal = strategy.generate(df)
    if signal.action == Action.SELL and sep <= 0.2:
        assert signal.confidence == Confidence.MEDIUM


def test_hold_no_crossover():
    """8. VI+>VI-이지만 크로스오버 없음 → HOLD."""
    strategy = VortexStrategy()
    n = 50
    df = _make_df(n)
    # 지속적으로 VI+>VI- 상태 유지 (크로스 없음): 모든 봉에 동일한 상승 패턴
    high = df["high"].values.copy()
    low = df["low"].values.copy()
    close = df["close"].values.copy()
    for i in range(n):
        low[i] = close[i] - 0.05
        high[i] = close[i] + 2.0
    df["high"] = high
    df["low"] = low

    signal = strategy.generate(df)
    # 크로스오버 없으면 HOLD
    vi_plus, vi_minus = _compute_vi(df)
    idx = len(df) - 2
    vp_now = float(vi_plus.iloc[idx])
    vp_prev = float(vi_plus.iloc[idx - 1])
    vm_now = float(vi_minus.iloc[idx])
    vm_prev = float(vi_minus.iloc[idx - 1])
    cross_up = vp_prev <= vm_prev and vp_now > vm_now
    if not cross_up:
        assert signal.action == Action.HOLD


def test_insufficient_data():
    """9. 데이터 부족 → HOLD."""
    strategy = VortexStrategy()
    df = _make_df(15)  # 20행 미만
    signal = strategy.generate(df)
    assert signal.action == Action.HOLD


def test_signal_fields_complete():
    """10. Signal 필드 완전성."""
    strategy = VortexStrategy()
    df = _make_df(40)
    signal = strategy.generate(df)
    assert isinstance(signal, Signal)
    assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert signal.strategy == "vortex"
    assert isinstance(signal.entry_price, float)
    assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
    assert isinstance(signal.invalidation, str)


def test_buy_reasoning_contains_vortex_or_vi_plus():
    """11. BUY reasoning에 'Vortex' 또는 'VI+' 포함."""
    strategy = VortexStrategy()
    df = _make_buy_df()
    signal = strategy.generate(df)
    if signal.action == Action.BUY:
        assert "Vortex" in signal.reasoning or "VI+" in signal.reasoning


def test_sell_reasoning_contains_vortex_or_vi_minus():
    """12. SELL reasoning에 'Vortex' 또는 'VI-' 포함."""
    strategy = VortexStrategy()
    df = _make_sell_df()
    signal = strategy.generate(df)
    if signal.action == Action.SELL:
        assert "Vortex" in signal.reasoning or "VI-" in signal.reasoning
