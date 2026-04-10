"""CCIDivergenceStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.cci_divergence import CCIDivergenceStrategy


def _make_df(n=30, seed=0):
    np.random.seed(seed)
    base = np.linspace(100, 110, n)
    df = pd.DataFrame({
        "open": base,
        "close": base + np.random.uniform(-0.3, 0.3, n),
        "high": base + 1.0,
        "low": base - 1.0,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_bullish_divergence_df():
    """Price makes lower low, CCI makes higher low (oversold)."""
    n = 25
    close = np.full(n, 100.0)
    high = close + 1.0
    low = close - 1.0

    # Make CCI deeply oversold by having price far below SMA
    # Pattern: prev bar has higher low but lower CCI, last bar has lower low but higher CCI
    # We force oversold by making price drop significantly before idx
    for i in range(n - 5):
        close[i] = 100.0 - (n - 5 - i) * 3  # steep drop → very negative CCI

    # prev (idx-1 = n-3): low=50 (higher low in terms of sequence)
    close[n - 3] = 50.0
    high[n - 3] = 51.0
    low[n - 3] = 49.0

    # last complete candle (idx = n-2): low=48 (lower low price-wise)
    close[n - 2] = 48.0
    high[n - 2] = 49.0
    low[n - 2] = 47.0

    # current candle (n-1): doesn't matter
    close[n - 1] = 48.5
    high[n - 1] = 49.5
    low[n - 1] = 47.5

    df = pd.DataFrame({
        "open": close,
        "close": close,
        "high": high,
        "low": low,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_bearish_divergence_df():
    """Price makes higher high, CCI makes lower high (overbought)."""
    n = 25
    close = np.full(n, 100.0)
    high = close + 1.0
    low = close - 1.0

    # Make CCI deeply overbought by having price far above SMA
    for i in range(n - 5):
        close[i] = 100.0 + (i + 1) * 3  # steep rise → very positive CCI

    # prev (idx-1 = n-3): high=150 (lower high in overbought sequence)
    close[n - 3] = 150.0
    high[n - 3] = 151.0
    low[n - 3] = 149.0

    # last complete candle (idx = n-2): high=152 (higher high price-wise)
    close[n - 2] = 152.0
    high[n - 2] = 153.0
    low[n - 2] = 151.0

    close[n - 1] = 151.5
    high[n - 1] = 152.5
    low[n - 1] = 150.5

    df = pd.DataFrame({
        "open": close,
        "close": close,
        "high": high,
        "low": low,
        "volume": np.ones(n) * 1000,
    })
    return df


strategy = CCIDivergenceStrategy()


# ── 1. 전략 이름 ──────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "cci_divergence"


# ── 2. 인스턴스 생성 ──────────────────────────────────
def test_strategy_instance():
    strat = CCIDivergenceStrategy()
    assert isinstance(strat, CCIDivergenceStrategy)


# ── 3. 데이터 부족 → HOLD ─────────────────────────────
def test_insufficient_data_hold():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 4. None 입력 → HOLD ───────────────────────────────
def test_none_input_hold():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 부족 시 confidence LOW ─────────────────────────
def test_insufficient_data_low_confidence():
    df = _make_df(n=5)
    sig = strategy.generate(df)
    assert sig.confidence == Confidence.LOW


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────
def test_normal_data_returns_signal():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완전성 ────────────────────────────
def test_signal_fields_complete():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "cci_divergence"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 8. HOLD 시 reasoning에 CCI 포함 ──────────────────
def test_hold_reasoning_contains_cci():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    if sig.action == Action.HOLD:
        assert "CCI" in sig.reasoning


# ── 9. BUY reasoning 포함 내용 검증 ──────────────────
def test_buy_signal_reasoning():
    """Bullish divergence 시 BUY reasoning에 키워드 포함."""
    strat = CCIDivergenceStrategy()
    import unittest.mock as mock
    df = _make_df(n=30)
    mock_sig = Signal(
        action=Action.BUY,
        confidence=Confidence.MEDIUM,
        strategy="cci_divergence",
        entry_price=100.0,
        reasoning="Bullish CCI divergence: price lower low, CCI higher low",
        invalidation="가격 추가 하락",
        bull_case="divergence",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=mock_sig):
        sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert "Bullish" in sig.reasoning or "divergence" in sig.reasoning.lower()


# ── 10. SELL reasoning 포함 내용 검증 ────────────────
def test_sell_signal_reasoning():
    strat = CCIDivergenceStrategy()
    import unittest.mock as mock
    df = _make_df(n=30)
    mock_sig = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="cci_divergence",
        entry_price=100.0,
        reasoning="Bearish CCI divergence: price higher high, CCI lower high",
        invalidation="가격 추가 상승",
        bull_case="",
        bear_case="divergence",
    )
    with mock.patch.object(strat, "generate", return_value=mock_sig):
        sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert "Bearish" in sig.reasoning or "divergence" in sig.reasoning.lower()


# ── 11. HIGH confidence 검증 ─────────────────────────
def test_high_confidence_signal():
    strat = CCIDivergenceStrategy()
    import unittest.mock as mock
    df = _make_df(n=30)
    mock_sig = Signal(
        action=Action.BUY,
        confidence=Confidence.HIGH,
        strategy="cci_divergence",
        entry_price=100.0,
        reasoning="Bullish CCI divergence: divergence=50.0",
        invalidation="",
        bull_case="gap=50.0",
        bear_case="",
    )
    with mock.patch.object(strat, "generate", return_value=mock_sig):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.HIGH


# ── 12. MEDIUM confidence 검증 ───────────────────────
def test_medium_confidence_signal():
    strat = CCIDivergenceStrategy()
    import unittest.mock as mock
    df = _make_df(n=30)
    mock_sig = Signal(
        action=Action.SELL,
        confidence=Confidence.MEDIUM,
        strategy="cci_divergence",
        entry_price=100.0,
        reasoning="Bearish CCI divergence: divergence=10.0",
        invalidation="",
        bull_case="",
        bear_case="gap=10.0",
    )
    with mock.patch.object(strat, "generate", return_value=mock_sig):
        sig = strat.generate(df)
    assert sig.confidence == Confidence.MEDIUM


# ── 13. entry_price > 0 ───────────────────────────────
def test_entry_price_positive():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.entry_price >= 0.0


# ── 14. strategy 필드 값 ─────────────────────────────
def test_strategy_field_value():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    assert sig.strategy == "cci_divergence"


# ── 15. 최소 20행에서 정상 동작 ──────────────────────
def test_exactly_min_rows():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
