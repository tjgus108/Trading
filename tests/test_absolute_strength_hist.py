"""tests/test_absolute_strength_hist.py — AbsoluteStrengthHistStrategy 단위 테스트 (14개)"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.absolute_strength_hist import AbsoluteStrengthHistStrategy
from src.strategy.base import Action, Confidence


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_df(close: np.ndarray) -> pd.DataFrame:
    n = len(close)
    return pd.DataFrame({
        "open": close - 1,
        "close": close.astype(float),
        "high": close + 2,
        "low": close - 2,
        "volume": np.ones(n) * 1000,
    })


def _compute_diff_val(close: np.ndarray) -> np.ndarray:
    """전략과 동일한 로직으로 diff_val 계산."""
    s = pd.Series(close.astype(float))
    diff = s.diff()
    bulls = diff.clip(lower=0)
    bears = (-diff).clip(lower=0)
    s1b = bulls.ewm(span=9, adjust=False).mean()
    s1br = bears.ewm(span=9, adjust=False).mean()
    s2b = s1b.ewm(span=3, adjust=False).mean()
    s2br = s1br.ewm(span=3, adjust=False).mean()
    return (s2b - s2br).values


def _buy_df() -> pd.DataFrame:
    """
    BUY crossover: diff_val crosses above 0 at iloc[-2] of the full df.
    전략은 idx=len(df)-2 를 사용하므로 full df 기준으로 dv[-3]<0, dv[-2]>=0 확인.
    """
    base_falling = np.linspace(100, 50, 60)
    base_rising = np.linspace(50, 130, 40)
    full = np.concatenate([base_falling, base_rising])
    # full 자체에서 crossover 위치 탐색 (마지막에 더미 추가 없이)
    for end in range(len(full), 20, -1):
        close = full[:end]
        dv = _compute_diff_val(close)
        if len(dv) >= 4 and dv[-3] < 0 and dv[-2] >= 0:
            return _make_df(close)
    raise RuntimeError("BUY crossover 위치를 찾지 못함.")


def _sell_df() -> pd.DataFrame:
    """
    SELL crossover: diff_val crosses below 0 at iloc[-2] of the full df.
    """
    base_rising = np.linspace(50, 100, 60)
    base_falling = np.linspace(100, 20, 40)
    full = np.concatenate([base_rising, base_falling])
    for end in range(len(full), 20, -1):
        close = full[:end]
        dv = _compute_diff_val(close)
        if len(dv) >= 4 and dv[-3] > 0 and dv[-2] <= 0:
            return _make_df(close)
    raise RuntimeError("SELL crossover 위치를 찾지 못함.")


def _hold_df_positive(n: int = 60) -> pd.DataFrame:
    """diff_val이 계속 양수 → 크로스오버 없음 → HOLD"""
    close = np.linspace(100, 120, n)
    return _make_df(close)


def _hold_df_negative(n: int = 60) -> pd.DataFrame:
    """diff_val이 계속 음수 → 크로스오버 없음 → HOLD"""
    close = np.linspace(120, 100, n)
    return _make_df(close)


# ── 테스트 ───────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 = 'absolute_strength_hist'"""
    assert AbsoluteStrengthHistStrategy.name == "absolute_strength_hist"


def test_insufficient_data_returns_hold():
    """2. 데이터 부족 (19행) → HOLD"""
    strat = AbsoluteStrengthHistStrategy()
    close = np.linspace(100, 110, 19)
    sig = strat.generate(_make_df(close))
    assert sig.action == Action.HOLD


def test_insufficient_data_reasoning():
    """3. 데이터 부족 시 reasoning에 'Insufficient' 포함"""
    strat = AbsoluteStrengthHistStrategy()
    close = np.linspace(100, 110, 10)
    sig = strat.generate(_make_df(close))
    assert "Insufficient" in sig.reasoning


def test_buy_signal():
    """4. BUY 크로스오버 신호 발생"""
    strat = AbsoluteStrengthHistStrategy()
    sig = strat.generate(_buy_df())
    assert sig.action == Action.BUY


def test_sell_signal():
    """5. SELL 크로스오버 신호 발생"""
    strat = AbsoluteStrengthHistStrategy()
    sig = strat.generate(_sell_df())
    assert sig.action == Action.SELL


def test_hold_when_no_crossover_positive():
    """6. diff_val 계속 양수 → HOLD"""
    strat = AbsoluteStrengthHistStrategy()
    sig = strat.generate(_hold_df_positive())
    assert sig.action == Action.HOLD


def test_hold_when_no_crossover_negative():
    """7. diff_val 계속 음수 → HOLD"""
    strat = AbsoluteStrengthHistStrategy()
    sig = strat.generate(_hold_df_negative())
    assert sig.action == Action.HOLD


def test_buy_signal_strategy_field():
    """8. BUY Signal.strategy = 'absolute_strength_hist'"""
    strat = AbsoluteStrengthHistStrategy()
    sig = strat.generate(_buy_df())
    assert sig.strategy == "absolute_strength_hist"


def test_sell_signal_strategy_field():
    """9. SELL Signal.strategy = 'absolute_strength_hist'"""
    strat = AbsoluteStrengthHistStrategy()
    sig = strat.generate(_sell_df())
    assert sig.strategy == "absolute_strength_hist"


def test_buy_entry_price_is_float():
    """10. BUY entry_price가 float"""
    strat = AbsoluteStrengthHistStrategy()
    sig = strat.generate(_buy_df())
    assert isinstance(sig.entry_price, float)


def test_sell_entry_price_is_float():
    """11. SELL entry_price가 float"""
    strat = AbsoluteStrengthHistStrategy()
    sig = strat.generate(_sell_df())
    assert isinstance(sig.entry_price, float)


def test_buy_reasoning_contains_ash():
    """12. BUY reasoning에 'ASH' 포함"""
    strat = AbsoluteStrengthHistStrategy()
    sig = strat.generate(_buy_df())
    assert "ASH" in sig.reasoning


def test_sell_reasoning_contains_ash():
    """13. SELL reasoning에 'ASH' 포함"""
    strat = AbsoluteStrengthHistStrategy()
    sig = strat.generate(_sell_df())
    assert "ASH" in sig.reasoning


def test_confidence_is_valid_enum():
    """14. confidence가 HIGH/MEDIUM/LOW 중 하나"""
    strat = AbsoluteStrengthHistStrategy()
    for df in [_buy_df(), _sell_df(), _hold_df_positive()]:
        sig = strat.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
