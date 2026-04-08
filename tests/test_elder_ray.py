"""tests/test_elder_ray.py — ElderRayStrategy 단위 테스트 (12개)"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.elder_ray import ElderRayStrategy
from src.strategy.base import Action, Confidence


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_df(n: int = 30, close=None, high=None, low=None, atr14: float = 100.0) -> pd.DataFrame:
    """기본 DataFrame 생성. close/high/low를 지정하거나 기본값 사용."""
    if close is None:
        close = np.linspace(100, 110, n)
    if high is None:
        high = np.array(close) + 5
    if low is None:
        low = np.array(close) - 5
    return pd.DataFrame({
        "open": np.array(close) - 1,
        "close": np.array(close, dtype=float),
        "high": np.array(high, dtype=float),
        "low": np.array(low, dtype=float),
        "volume": np.ones(n) * 1000,
        "ema50": np.array(close, dtype=float),
        "atr14": np.full(n, atr14),
    })


def _buy_df(n: int = 50, atr14: float = 100.0) -> pd.DataFrame:
    """
    BUY 신호 유발 DataFrame.
    조건:
      1. EMA13 상승: close가 계속 상승 → ema_now > ema_prev
      2. Bear Power < 0: low < EMA13. 상승 추세에서 EMA13 ≈ close이므로
         low를 close - large_gap으로 설정하면 bear < 0 보장
      3. Bear Power 개선(bear_now > bear_prev): 마지막 직전 봉은 low를 더 낮게,
         마지막 완성 봉(iloc[-2])은 low를 덜 낮게 → bear 개선
    """
    close = np.linspace(100, 130, n)
    high = close + 5
    low = close.copy()
    # 기본 low: close - 10 → EMA13 ≈ close이므로 bear = low - ema ≈ -10 < 0
    low[:] = close - 10
    # idx = n-2 (마지막 완성 봉), idx-1 = n-3
    # bear_now > bear_prev 되려면: low[n-2] - ema[n-2] > low[n-3] - ema[n-3]
    # ema 차이는 작으므로 low[n-2] > low[n-3]이면 됨
    # 기본적으로 close가 상승하면 low도 상승하므로 자연스럽게 bear 개선 가능
    # 하지만 EMA 추격 효과 때문에 확실히 하려면 low[n-2]를 상대적으로 높게
    low[n - 2] = close[n - 2] - 5   # bear_now ≈ -5
    low[n - 3] = close[n - 3] - 15  # bear_prev ≈ -15 → bear_now > bear_prev
    return _make_df(n=n, close=close, high=high, low=low, atr14=atr14)


def _sell_df(n: int = 50, atr14: float = 100.0) -> pd.DataFrame:
    """
    SELL 신호 유발 DataFrame.
    조건:
      1. EMA13 하락: close가 계속 하락 → ema_now < ema_prev
      2. Bull Power > 0: high > EMA13. 하락 추세에서 EMA13 ≈ close이므로
         high = close + large_gap
      3. Bull Power 감소(bull_now < bull_prev): 마지막 직전 봉 high를 더 높게,
         마지막 완성 봉(iloc[-2])은 high를 덜 높게 → bull 감소
    """
    close = np.linspace(130, 100, n)
    high = close.copy()
    low = close - 5
    # 기본 high: close + 10
    high[:] = close + 10
    # idx = n-2, idx-1 = n-3
    # bull_now < bull_prev 되려면: high[n-2] - ema[n-2] < high[n-3] - ema[n-3]
    high[n - 2] = close[n - 2] + 5   # bull_now ≈ +5
    high[n - 3] = close[n - 3] + 15  # bull_prev ≈ +15 → bull_now < bull_prev
    return _make_df(n=n, close=close, high=high, low=low, atr14=atr14)


# ── 테스트 ───────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 = 'elder_ray'"""
    assert ElderRayStrategy.name == "elder_ray"


def test_buy_signal():
    """2. BUY 신호 발생 (EMA 상승, Bear<0, Bear 개선)"""
    strat = ElderRayStrategy()
    df = _buy_df()
    sig = strat.generate(df)
    assert sig.action == Action.BUY


def test_sell_signal():
    """3. SELL 신호 발생 (EMA 하락, Bull>0, Bull 감소)"""
    strat = ElderRayStrategy()
    df = _sell_df()
    sig = strat.generate(df)
    assert sig.action == Action.SELL


def test_buy_high_confidence():
    """4. BUY HIGH confidence: |Bear Power| > 0.5 * ATR"""
    strat = ElderRayStrategy()
    # ATR이 작으면 |bear| > 0.5*ATR 조건 충족 쉬움
    df = _buy_df(atr14=1.0)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_buy_medium_confidence():
    """5. BUY MEDIUM confidence: |Bear Power| <= 0.5 * ATR"""
    strat = ElderRayStrategy()
    # ATR이 매우 크면 |bear| <= 0.5*ATR → MEDIUM
    df = _buy_df(atr14=10000.0)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


def test_sell_high_confidence():
    """6. SELL HIGH confidence: |Bull Power| > 0.5 * ATR"""
    strat = ElderRayStrategy()
    df = _sell_df(atr14=1.0)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


def test_sell_medium_confidence():
    """7. SELL MEDIUM confidence: |Bull Power| <= 0.5 * ATR"""
    strat = ElderRayStrategy()
    df = _sell_df(atr14=10000.0)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


def test_buy_conditions_bear_worsening_is_hold():
    """8. EMA 상승이지만 Bear Power 악화(악화=감소) → HOLD"""
    strat = ElderRayStrategy()
    n = 30
    # EMA 상승 조건은 만족하지만, bear_now < bear_prev (악화) → HOLD
    close = np.linspace(100, 120, n)
    high = close + 5
    # low를 뒤에서 더 낮게 설정해 Bear Power가 악화되도록 조작
    low = close - 3
    # 마지막 두 봉의 low를 조작: iloc[-2] = idx, iloc[-3] = idx-1
    # bear_now = low[idx] - ema[idx], bear_prev = low[idx-1] - ema[idx-1]
    # bear_now < bear_prev 가 되도록 low[idx]를 더 낮게
    low[-2] = close[-2] - 20  # bear_now 매우 낮음 (악화)
    low[-3] = close[-3] - 1   # bear_prev 상대적으로 높음
    df = _make_df(n=n, close=close, high=high, low=low, atr14=100.0)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_insufficient_data_returns_hold():
    """9. 데이터 부족 (19행) → HOLD"""
    strat = ElderRayStrategy()
    df = _make_df(n=19)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_signal_fields_complete():
    """10. Signal 필드 완전성 확인"""
    strat = ElderRayStrategy()
    df = _buy_df()
    sig = strat.generate(df)
    assert sig.strategy == "elder_ray"
    assert isinstance(sig.entry_price, float)
    assert sig.reasoning != ""
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


def test_buy_reasoning_contains_elder_or_bear_power():
    """11. BUY reasoning에 'Elder' 또는 'Bear Power' 포함"""
    strat = ElderRayStrategy()
    df = _buy_df()
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert "Elder" in sig.reasoning or "Bear Power" in sig.reasoning


def test_sell_reasoning_contains_elder_or_bull_power():
    """12. SELL reasoning에 'Elder' 또는 'Bull Power' 포함"""
    strat = ElderRayStrategy()
    df = _sell_df()
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert "Elder" in sig.reasoning or "Bull Power" in sig.reasoning
