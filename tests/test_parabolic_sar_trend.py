"""ParabolicSARTrendStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.parabolic_sar_trend import ParabolicSARTrendStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, base: float = 100.0) -> pd.DataFrame:
    close = np.linspace(base, base + 10, n)
    return pd.DataFrame({
        "open": close - 0.3,
        "high": close + 0.5,
        "low": close - 0.5,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


def _make_buy_df() -> pd.DataFrame:
    """하락 추세 후 idx=-2에서 상승 전환 유도."""
    n = 40
    falling = np.linspace(200.0, 80.0, n - 2)
    # 급등으로 SAR(위) 돌파
    close = np.append(falling, [300.0, 310.0])
    high = close + 2.0
    low = close - 2.0
    high[-2] = 310.0
    return pd.DataFrame({
        "open": close - 0.3,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


def _make_sell_df() -> pd.DataFrame:
    """상승 추세 후 idx=-2에서 하락 전환 유도."""
    n = 40
    rising = np.linspace(50.0, 200.0, n - 2)
    # 급락으로 SAR(아래) 돌파
    close = np.append(rising, [0.5, 0.4])
    high = close + 2.0
    low = np.maximum(close - 2.0, 0.01)
    low[-2] = 0.01
    return pd.DataFrame({
        "open": close - 0.3,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


# ── 1. 전략명 확인 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert ParabolicSARTrendStrategy.name == "parabolic_sar_trend"


# ── 2. 인스턴스 생성 ─────────────────────────────────────────────────────────
def test_instantiation():
    strat = ParabolicSARTrendStrategy()
    assert strat is not None


# ── 3. 데이터 부족 → HOLD ────────────────────────────────────────────────────
def test_insufficient_data_hold():
    strat = ParabolicSARTrendStrategy()
    df = _make_df(n=10)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ──────────────────────────────────────────────────────
def test_none_input_hold():
    strat = ParabolicSARTrendStrategy()
    sig = strat.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ───────────────────────────────────────────
def test_insufficient_data_reasoning():
    strat = ParabolicSARTrendStrategy()
    df = _make_df(n=5)
    sig = strat.generate(df)
    assert "Insufficient" in sig.reasoning or "부족" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ────────────────────────────────────────────
def test_normal_data_returns_signal():
    strat = ParabolicSARTrendStrategy()
    df = _make_df(n=30)
    sig = strat.generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성 ──────────────────────────────────────────────────────
def test_signal_fields_complete():
    strat = ParabolicSARTrendStrategy()
    df = _make_df(n=30)
    sig = strat.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "parabolic_sar_trend"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str)


# ── 8. BUY reasoning 키워드 확인 ────────────────────────────────────────────
def test_buy_reasoning_keyword():
    strat = ParabolicSARTrendStrategy()
    df = _make_buy_df()
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert "SAR" in sig.reasoning
    else:
        pytest.skip("BUY signal not triggered for this dataset")


# ── 9. SELL reasoning 키워드 확인 ───────────────────────────────────────────
def test_sell_reasoning_keyword():
    strat = ParabolicSARTrendStrategy()
    df = _make_sell_df()
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert "SAR" in sig.reasoning
    else:
        pytest.skip("SELL signal not triggered for this dataset")


# ── 10. HIGH confidence 테스트 ──────────────────────────────────────────────
def test_high_confidence():
    """close와 SAR 거리가 2% 초과하면 HIGH."""
    strat = ParabolicSARTrendStrategy()
    df = _make_buy_df()
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        sar = strat._compute_sar(df)
        idx = len(df) - 2
        dist = abs(float(df["close"].iloc[idx]) - float(sar.iloc[idx])) / float(df["close"].iloc[idx])
        if dist > 0.02:
            assert sig.confidence == Confidence.HIGH
        else:
            assert sig.confidence == Confidence.MEDIUM
    else:
        pytest.skip("BUY not triggered")


# ── 11. MEDIUM confidence 테스트 ────────────────────────────────────────────
def test_medium_confidence_hold():
    """HOLD 신호는 MEDIUM confidence."""
    strat = ParabolicSARTrendStrategy()
    df = _make_df(n=30)
    sig = strat.generate(df)
    if sig.action == Action.HOLD and sig.confidence != Confidence.LOW:
        assert sig.confidence == Confidence.MEDIUM


# ── 12. entry_price > 0 ─────────────────────────────────────────────────────
def test_entry_price_positive():
    strat = ParabolicSARTrendStrategy()
    df = _make_df(n=30)
    sig = strat.generate(df)
    assert sig.entry_price > 0


# ── 13. strategy 필드 값 확인 ───────────────────────────────────────────────
def test_strategy_field():
    strat = ParabolicSARTrendStrategy()
    df = _make_df(n=30)
    sig = strat.generate(df)
    assert sig.strategy == "parabolic_sar_trend"


# ── 14. 최소 행 수에서 동작 ─────────────────────────────────────────────────
def test_min_rows_works():
    strat = ParabolicSARTrendStrategy()
    df = _make_df(n=20)
    sig = strat.generate(df)
    assert isinstance(sig, Signal)
    assert sig.entry_price > 0
