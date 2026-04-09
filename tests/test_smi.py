"""
SMIStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.smi import SMIStrategy, _calc_smi
from src.strategy.base import Action, Confidence, Signal

_COLS = ["open", "close", "high", "low", "volume", "ema50", "atr14"]


def _make_df(n: int = 50, close: float = 100.0, high_offset: float = 2.0, low_offset: float = 2.0) -> pd.DataFrame:
    """기본 DataFrame 생성. 마지막 봉(-1)은 진행 중 캔들."""
    closes = [close] * n
    highs = [close + high_offset] * n
    lows = [close - low_offset] * n
    data = {
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
        "ema50": [close] * n,
        "atr14": [high_offset] * n,
    }
    return pd.DataFrame(data)


def _make_oversold_df(n: int = 50, smi_target: float = -50.0) -> pd.DataFrame:
    """SMI < -40 (과매도) 조건을 유도하는 DataFrame."""
    # close를 high-low 범위 최저점 근처에 위치시킴
    # HH 크고 LL 작고 close가 LL에 가까울수록 SMI 음수
    closes = [100.0] * n
    highs = [120.0] * n   # HH = 120
    lows = [80.0] * n     # LL = 80, mid = 100
    # close < mid 이면 D < 0 → SMI < 0
    for i in range(n):
        closes[i] = 82.0   # close ≈ LL+2, D = 82-100 = -18
    # 신호 봉(-2)도 같은 수준
    data = {
        "open": closes[:],
        "close": closes[:],
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
        "ema50": [100.0] * n,
        "atr14": [5.0] * n,
    }
    return pd.DataFrame(data)


def _make_overbought_df(n: int = 50) -> pd.DataFrame:
    """SMI > 40 (과매수) 조건을 유도하는 DataFrame."""
    closes = [100.0] * n
    highs = [120.0] * n
    lows = [80.0] * n
    for i in range(n):
        closes[i] = 118.0   # close ≈ HH-2, D = 118-100 = +18
    data = {
        "open": closes[:],
        "close": closes[:],
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
        "ema50": [100.0] * n,
        "atr14": [5.0] * n,
    }
    return pd.DataFrame(data)


# ── 기본 인터페이스 테스트 ──────────────────────────────────────────────────


def test_returns_signal_instance():
    df = _make_df()
    sig = SMIStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_strategy_name():
    assert SMIStrategy.name == "smi"


def test_signal_has_required_fields():
    df = _make_df()
    sig = SMIStrategy().generate(df)
    assert sig.action in list(Action)
    assert sig.confidence in list(Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


# ── 데이터 부족 테스트 ─────────────────────────────────────────────────────


def test_insufficient_data_returns_hold():
    df = _make_df(n=10)
    sig = SMIStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_exactly_min_rows():
    """25행 정확히 — HOLD 또는 유효 신호."""
    df = _make_df(n=25)
    sig = SMIStrategy().generate(df)
    assert sig.action in list(Action)


def test_24_rows_hold():
    df = _make_df(n=24)
    sig = SMIStrategy().generate(df)
    assert sig.action == Action.HOLD


# ── HOLD 조건 테스트 ───────────────────────────────────────────────────────


def test_neutral_market_holds():
    """중립 시장(close ≈ midpoint) → SMI ≈ 0 → HOLD."""
    df = _make_df(n=50, close=100.0, high_offset=5.0, low_offset=5.0)
    sig = SMIStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_hold_action_has_low_confidence():
    df = _make_df(n=50)
    sig = SMIStrategy().generate(df)
    if sig.action == Action.HOLD:
        assert sig.confidence == Confidence.LOW


# ── _calc_smi 내부 함수 테스트 ────────────────────────────────────────────


def test_calc_smi_returns_two_floats():
    df = _make_df(n=50)
    smi, sig = _calc_smi(df)
    assert isinstance(smi, float)
    assert isinstance(sig, float)


def test_calc_smi_oversold_negative():
    """과매도 데이터에서 SMI < 0."""
    df = _make_oversold_df()
    smi, _ = _calc_smi(df)
    assert smi < 0


def test_calc_smi_overbought_positive():
    """과매수 데이터에서 SMI > 0."""
    df = _make_overbought_df()
    smi, _ = _calc_smi(df)
    assert smi > 0


# ── BUY 신호 테스트 ────────────────────────────────────────────────────────


def test_buy_signal_entry_price_is_close():
    """BUY 신호 진입가 = 신호 봉 close."""
    df = _make_oversold_df()
    sig = SMIStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)


def test_buy_signal_has_bull_case():
    df = _make_oversold_df()
    sig = SMIStrategy().generate(df)
    if sig.action == Action.BUY:
        assert len(sig.bull_case) > 0


# ── SELL 신호 테스트 ───────────────────────────────────────────────────────


def test_sell_signal_entry_price_is_close():
    df = _make_overbought_df()
    sig = SMIStrategy().generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)


def test_sell_signal_has_bear_case():
    df = _make_overbought_df()
    sig = SMIStrategy().generate(df)
    if sig.action == Action.SELL:
        assert len(sig.bear_case) > 0


# ── Confidence 레벨 테스트 ────────────────────────────────────────────────


def test_confidence_medium_or_high_on_non_hold():
    """BUY/SELL 신호는 MEDIUM 또는 HIGH."""
    for df in [_make_oversold_df(), _make_overbought_df()]:
        sig = SMIStrategy().generate(df)
        if sig.action != Action.HOLD:
            assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_strategy_name_in_signal():
    df = _make_df()
    sig = SMIStrategy().generate(df)
    assert sig.strategy == "smi"


# ── 엣지 케이스 ────────────────────────────────────────────────────────────


def test_zero_range_no_crash():
    """high == low (range=0) — ZeroDivision 없어야 함."""
    df = _make_df(n=50, high_offset=0.0, low_offset=0.0)
    sig = SMIStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_large_dataframe():
    df = _make_df(n=500)
    sig = SMIStrategy().generate(df)
    assert isinstance(sig, Signal)
