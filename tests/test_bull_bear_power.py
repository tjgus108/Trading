"""tests/test_bull_bear_power.py — BullBearPowerStrategy 단위 테스트 (12개)"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.bull_bear_power import BullBearPowerStrategy
from src.strategy.base import Action, Confidence


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_df(n: int = 30, close=None, high=None, low=None) -> pd.DataFrame:
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
    })


def _buy_df(n: int = 80) -> pd.DataFrame:
    """
    BUY 신호 유발 DataFrame.
    조건:
      1. EMA13 상승: close가 완만하게 상승
      2. Bear Power < 0: low가 EMA13보다 충분히 낮도록 큰 gap 사용
      3. Bear Power rising: iloc[-2] bear > iloc[-3] bear
    EMA lag 효과로 bear가 양수가 되지 않도록 low를 충분히 낮게 설정.
    """
    close = np.linspace(100, 105, n)  # 완만한 상승 (EMA lag 최소화)
    high = close + 5
    low = close.copy()
    # low를 충분히 낮게: EMA lag이 최대 ~5 정도이므로 30 이상 차이면 bear < 0 보장
    low[:] = close - 30
    # bear_now > bear_prev 조건: low[n-2] > low[n-3] (close 상승과 함께)
    # 기본적으로 close 상승이면 low도 상승하므로 자연스럽게 bear 개선
    # 추가로 명시적 조정
    low[n - 2] = close[n - 2] - 20  # bear_now ≈ -20 (EMA lag 고려해도 < 0)
    low[n - 3] = close[n - 3] - 35  # bear_prev ≈ -35 → bear_now > bear_prev
    return _make_df(n=n, close=close, high=high, low=low)


def _sell_df(n: int = 80) -> pd.DataFrame:
    """
    SELL 신호 유발 DataFrame.
    조건:
      1. EMA13 하락: close가 완만하게 하락
      2. Bull Power > 0: high가 EMA13보다 충분히 높도록 큰 gap 사용
      3. Bull Power falling: bull_now < bull_prev
    """
    close = np.linspace(105, 100, n)  # 완만한 하락
    high = close.copy()
    low = close - 5
    high[:] = close + 30  # bull ≈ +30 (EMA lag 고려해도 > 0)
    high[n - 2] = close[n - 2] + 20  # bull_now ≈ +20
    high[n - 3] = close[n - 3] + 35  # bull_prev ≈ +35 → bull_now < bull_prev
    return _make_df(n=n, close=close, high=high, low=low)


# ── 테스트 ───────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 = 'bull_bear_power'"""
    assert BullBearPowerStrategy.name == "bull_bear_power"


def test_buy_signal():
    """2. BUY 신호 발생 (EMA 상승, Bear<0, Bear rising)"""
    strat = BullBearPowerStrategy()
    sig = strat.generate(_buy_df())
    assert sig.action == Action.BUY


def test_sell_signal():
    """3. SELL 신호 발생 (EMA 하락, Bull>0, Bull falling)"""
    strat = BullBearPowerStrategy()
    sig = strat.generate(_sell_df())
    assert sig.action == Action.SELL


def test_insufficient_data_returns_hold():
    """4. 데이터 부족 (19행) → HOLD"""
    strat = BullBearPowerStrategy()
    df = _make_df(n=19)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_buy_high_confidence():
    """5. BUY HIGH confidence: |bear| > EMA13 * 0.01 — EMA13 small relative to gap"""
    strat = BullBearPowerStrategy()
    # close가 매우 작으면 EMA13도 작고 threshold도 작아짐 → |bear| > threshold 쉽게 충족
    n = 50
    close = np.linspace(1.0, 1.3, n)
    high = close + 0.5
    low = close.copy()
    low[:] = close - 0.1  # |bear| ≈ 0.1 >> EMA13*0.01 ≈ 0.012
    low[n - 2] = close[n - 2] - 0.05
    low[n - 3] = close[n - 3] - 0.15
    df = _make_df(n=n, close=close, high=high, low=low)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_buy_medium_confidence():
    """6. BUY MEDIUM confidence: |bear| <= EMA13 * 0.01"""
    strat = BullBearPowerStrategy()
    # flat close → EMA13 ≈ close → EMA lag ≈ 0
    # 마지막 두 봉만 close 조금 올려 EMA_rising 조건 충족
    # bear = low - EMA13: low = close - 0.001, threshold = EMA13*0.01 ≈ 1.0*0.01 = 0.01
    # |bear| ≈ 0.001 < 0.01 → MEDIUM
    n = 80
    close = np.ones(n) * 100.0
    close[n - 2] = 100.01  # EMA 미세 상승
    close[n - 3] = 100.005
    high = close + 5
    low = close.copy()
    low[:] = close - 0.05  # bear ≈ -0.05, threshold = 100*0.01 = 1.0 → MEDIUM
    low[n - 2] = close[n - 2] - 0.03  # bear_now ≈ -0.03 (개선)
    low[n - 3] = close[n - 3] - 0.06  # bear_prev ≈ -0.06
    df = _make_df(n=n, close=close, high=high, low=low)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


def test_sell_high_confidence():
    """7. SELL HIGH confidence: |bull| > EMA13 * 0.01"""
    strat = BullBearPowerStrategy()
    n = 50
    close = np.linspace(1.3, 1.0, n)
    high = close.copy()
    low = close - 0.5
    high[:] = close + 0.1  # |bull| ≈ 0.1 >> threshold ≈ 0.012
    high[n - 2] = close[n - 2] + 0.05
    high[n - 3] = close[n - 3] + 0.15
    df = _make_df(n=n, close=close, high=high, low=low)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


def test_sell_medium_confidence():
    """8. SELL MEDIUM confidence: |bull| <= EMA13 * 0.01"""
    strat = BullBearPowerStrategy()
    # flat close → EMA13 ≈ close → EMA lag ≈ 0
    # 마지막 두 봉만 close 조금 내려 EMA_falling 조건 충족
    # bull = high - EMA13: high = close + 0.05, threshold = 100*0.01 = 1.0 → MEDIUM
    n = 80
    close = np.ones(n) * 100.0
    close[n - 2] = 99.99   # EMA 미세 하락
    close[n - 3] = 99.995
    low = close - 5
    high = close.copy()
    high[:] = close + 0.05  # bull ≈ +0.05, threshold = 1.0 → MEDIUM
    high[n - 2] = close[n - 2] + 0.03  # bull_now ≈ +0.03 (감소)
    high[n - 3] = close[n - 3] + 0.06  # bull_prev ≈ +0.06
    df = _make_df(n=n, close=close, high=high, low=low)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


def test_bear_worsening_is_hold():
    """9. EMA 상승이지만 Bear Power 악화 → HOLD"""
    strat = BullBearPowerStrategy()
    n = 30
    close = np.linspace(100, 120, n)
    high = close + 5
    low = close.copy()
    low[:] = close - 3
    # bear 악화: iloc[-2] bear < iloc[-3] bear
    low[-2] = close[-2] - 20  # bear_now 더 낮음 (악화)
    low[-3] = close[-3] - 1
    df = _make_df(n=n, close=close, high=high, low=low)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_bull_rising_is_hold():
    """10. EMA 하락이지만 Bull Power 상승 → HOLD"""
    strat = BullBearPowerStrategy()
    n = 30
    close = np.linspace(120, 100, n)
    high = close.copy()
    low = close - 5
    high[:] = close + 3
    # bull 상승: iloc[-2] bull > iloc[-3] bull → 조건 불충족
    high[-2] = close[-2] + 20  # bull_now 더 높음 (상승)
    high[-3] = close[-3] + 1
    df = _make_df(n=n, close=close, high=high, low=low)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_signal_strategy_name():
    """11. Signal.strategy 필드 = 'bull_bear_power'"""
    strat = BullBearPowerStrategy()
    sig = strat.generate(_buy_df())
    assert sig.strategy == "bull_bear_power"


def test_signal_fields_complete():
    """12. Signal 필드 완전성 확인"""
    strat = BullBearPowerStrategy()
    sig = strat.generate(_buy_df())
    assert sig.action == Action.BUY
    assert isinstance(sig.entry_price, float)
    assert sig.reasoning != ""
    assert "BullBearPower" in sig.reasoning
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
