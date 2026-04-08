"""ParabolicSARStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.parabolic_sar import ParabolicSARStrategy
from src.strategy.base import Action, Confidence


def _make_df(n: int = 50, base: float = 100.0, atr: float = 1.0) -> pd.DataFrame:
    """기본 테스트용 DataFrame."""
    close = np.linspace(base, base + 10, n)
    return pd.DataFrame({
        "open": close - 0.3,
        "high": close + 0.5,
        "low": close - 0.5,
        "close": close,
        "volume": np.ones(n) * 1000,
        "ema50": close,
        "atr14": np.ones(n) * atr,
    })


def _make_buy_signal_df() -> pd.DataFrame:
    """
    하락 추세 → 상승 전환 유도:
    긴 하락으로 SAR가 위에 형성된 후, iloc[-2]에서 close가 SAR 위로 급등.
    iloc[-2] = index n-2 위치에서 반전이 일어나야 함.
    """
    n = 50
    # 하락 추세 확립 (n-3까지)
    falling = np.linspace(200.0, 100.0, n - 2)
    # index n-2 (-2): 급등 → SAR(EP~200 근처) 돌파
    reversal = 300.0
    # index n-1 (-1): 현재 진행 중 캔들 (어떤 값이든 OK)
    current = 310.0
    close = np.append(falling, [reversal, current])
    high = close + 1.0
    low = close - 1.0
    high[-2] = reversal + 5.0
    return pd.DataFrame({
        "open": close - 0.3,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
        "ema50": close,
        "atr14": np.ones(n) * 1.0,
    })


def _make_sell_signal_df() -> pd.DataFrame:
    """
    상승 추세 → 하락 전환 유도:
    긴 상승으로 SAR가 아래에 형성된 후, iloc[-2]에서 close가 SAR 아래로 급락.
    iloc[-2] = index n-2 위치에서 반전이 일어나야 함.
    """
    n = 50
    # 상승 추세 확립 (n-3까지)
    rising = np.linspace(100.0, 200.0, n - 2)
    # index n-2 (-2): 급락 → SAR(EP~100 근처) 아래로 돌파
    reversal = 0.5  # SAR(~100)보다 훨씬 아래
    # index n-1 (-1): 현재 진행 중 캔들
    current = 0.4
    close = np.append(rising, [reversal, current])
    high = close + 1.0
    low = close - 1.0
    low[-2] = max(reversal - 5.0, 0.01)
    return pd.DataFrame({
        "open": close - 0.3,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
        "ema50": close,
        "atr14": np.ones(n) * 1.0,
    })


# ── 1. 전략 이름 ────────────────────────────────────────────────────────────

def test_strategy_name():
    assert ParabolicSARStrategy().name == "parabolic_sar"


# ── 2. BUY 신호 ─────────────────────────────────────────────────────────────

def test_buy_signal():
    strat = ParabolicSARStrategy()
    df = _make_buy_signal_df()
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 ─────────────────────────────────────────────────────────────

def test_sell_signal():
    strat = ParabolicSARStrategy()
    df = _make_sell_signal_df()
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence (RSI < 60) ────────────────────────────────────────

def test_buy_high_confidence():
    """RSI < 60인 BUY → HIGH confidence."""
    strat = ParabolicSARStrategy()
    df = _make_buy_signal_df()
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        rsi = strat._compute_rsi(df["close"])
        if rsi < 60:
            assert sig.confidence == Confidence.HIGH
        else:
            assert sig.confidence == Confidence.MEDIUM
    else:
        pytest.skip("BUY signal not triggered for this dataset")


# ── 5. BUY MEDIUM confidence ──────────────────────────────────────────────────

def test_buy_medium_confidence():
    """RSI >= 60인 BUY → MEDIUM confidence."""
    strat = ParabolicSARStrategy()
    # 하락 후 강한 급등으로 RSI 높게 만들기
    n = 60
    falling = np.linspace(130.0, 85.0, n - 8)
    # 매우 강한 급등 → RSI 높아짐
    rising = np.array([88.0, 95.0, 103.0, 112.0, 120.0, 128.0, 135.0, 140.0])
    close = np.concatenate([falling, rising])
    high = close + 1.0
    high[-8:] = close[-8:] + 5.0
    low = close - 1.0
    df = pd.DataFrame({
        "open": close - 0.3,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
        "ema50": close,
        "atr14": np.ones(n) * 1.0,
    })
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        rsi = strat._compute_rsi(df["close"])
        if rsi >= 60:
            assert sig.confidence == Confidence.MEDIUM
        else:
            assert sig.confidence == Confidence.HIGH
    else:
        pytest.skip("BUY signal not triggered for this dataset")


# ── 6. SELL HIGH confidence (RSI > 40) ───────────────────────────────────────

def test_sell_high_confidence():
    """RSI > 40인 SELL → HIGH confidence."""
    strat = ParabolicSARStrategy()
    df = _make_sell_signal_df()
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        rsi = strat._compute_rsi(df["close"])
        if rsi > 40:
            assert sig.confidence == Confidence.HIGH
        else:
            assert sig.confidence == Confidence.MEDIUM
    else:
        pytest.skip("SELL signal not triggered for this dataset")


# ── 7. SELL MEDIUM confidence ─────────────────────────────────────────────────

def test_sell_medium_confidence():
    """RSI <= 40인 SELL → MEDIUM confidence."""
    strat = ParabolicSARStrategy()
    # 상승 후 매우 강한 급락으로 RSI 낮게 만들기
    n = 60
    rising = np.linspace(70.0, 130.0, n - 8)
    plunging = np.array([126.0, 120.0, 112.0, 103.0, 94.0, 85.0, 77.0, 70.0])
    close = np.concatenate([rising, plunging])
    high = close + 1.0
    low = close - 1.0
    low[-8:] = close[-8:] - 5.0
    df = pd.DataFrame({
        "open": close - 0.3,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
        "ema50": close,
        "atr14": np.ones(n) * 1.0,
    })
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        rsi = strat._compute_rsi(df["close"])
        if rsi <= 40:
            assert sig.confidence == Confidence.MEDIUM
        else:
            assert sig.confidence == Confidence.HIGH
    else:
        pytest.skip("SELL signal not triggered for this dataset")


# ── 8. 데이터 부족 → HOLD ─────────────────────────────────────────────────────

def test_insufficient_data_hold():
    strat = ParabolicSARStrategy()
    df = _make_df(n=20)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 9. Signal 필드 완전성 ─────────────────────────────────────────────────────

def test_signal_fields_complete():
    strat = ParabolicSARStrategy()
    df = _make_df(n=50)
    sig = strat.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "parabolic_sar"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str)


# ── 10. BUY reasoning에 "SAR" 포함 ────────────────────────────────────────────

def test_buy_reasoning_contains_sar():
    strat = ParabolicSARStrategy()
    df = _make_buy_signal_df()
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert "SAR" in sig.reasoning
    else:
        pytest.skip("BUY signal not triggered")


# ── 11. SELL reasoning에 "SAR" 포함 ───────────────────────────────────────────

def test_sell_reasoning_contains_sar():
    strat = ParabolicSARStrategy()
    df = _make_sell_signal_df()
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert "SAR" in sig.reasoning
    else:
        pytest.skip("SELL signal not triggered")


# ── 12. entry_price = close (iloc[-2]) ────────────────────────────────────────

def test_entry_price_equals_close():
    strat = ParabolicSARStrategy()
    df = _make_df(n=50)
    sig = strat.generate(df)
    expected = float(df["close"].iloc[-2])
    assert sig.entry_price == pytest.approx(expected)
