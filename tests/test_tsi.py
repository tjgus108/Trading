"""
TSIStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.tsi import TSIStrategy, _calc_tsi
from src.strategy.base import Action, Confidence, Signal

_COLS = ["open", "close", "high", "low", "volume", "ema50", "atr14"]


def _make_df(n: int = 60, close: float = 100.0) -> pd.DataFrame:
    """기본 flat DataFrame."""
    data = {
        "open": [close] * n,
        "close": [close] * n,
        "high": [close + 2.0] * n,
        "low": [close - 2.0] * n,
        "volume": [1000.0] * n,
        "ema50": [close] * n,
        "atr14": [2.0] * n,
    }
    return pd.DataFrame(data)


def _make_uptrend_df(n: int = 80) -> pd.DataFrame:
    """꾸준히 상승하는 가격 — TSI > 0, 상향 크로스 유도."""
    closes = [100.0 + i * 0.5 for i in range(n)]
    data = {
        "open": closes[:],
        "close": closes[:],
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": [1000.0] * n,
        "ema50": [closes[i] - 5 for i in range(n)],
        "atr14": [1.5] * n,
    }
    return pd.DataFrame(data)


def _make_downtrend_df(n: int = 80) -> pd.DataFrame:
    """꾸준히 하락하는 가격 — TSI < 0, 하향 크로스 유도."""
    closes = [200.0 - i * 0.5 for i in range(n)]
    data = {
        "open": closes[:],
        "close": closes[:],
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": [1000.0] * n,
        "ema50": [closes[i] + 5 for i in range(n)],
        "atr14": [1.5] * n,
    }
    return pd.DataFrame(data)


def _make_cross_up_df(n: int = 80) -> pd.DataFrame:
    """하락 후 급상승 — TSI 상향 크로스 유도."""
    closes = [100.0 - i * 0.3 for i in range(n // 2)]
    closes += [closes[-1] + i * 1.2 for i in range(1, n - n // 2 + 1)]
    closes = closes[:n]
    data = {
        "open": closes[:],
        "close": closes[:],
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": [1000.0] * n,
        "ema50": [closes[i] - 3 for i in range(n)],
        "atr14": [1.5] * n,
    }
    return pd.DataFrame(data)


def _make_cross_down_df(n: int = 80) -> pd.DataFrame:
    """상승 후 급하락 — TSI 하향 크로스 유도."""
    closes = [100.0 + i * 0.3 for i in range(n // 2)]
    closes += [closes[-1] - i * 1.2 for i in range(1, n - n // 2 + 1)]
    closes = closes[:n]
    data = {
        "open": closes[:],
        "close": closes[:],
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": [1000.0] * n,
        "ema50": [closes[i] + 3 for i in range(n)],
        "atr14": [1.5] * n,
    }
    return pd.DataFrame(data)


# ── 기본 인터페이스 테스트 ──────────────────────────────────────────────────


def test_returns_signal_instance():
    df = _make_df()
    sig = TSIStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_strategy_name():
    assert TSIStrategy.name == "tsi"


def test_signal_has_required_fields():
    df = _make_df()
    sig = TSIStrategy().generate(df)
    assert sig.action in list(Action)
    assert sig.confidence in list(Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_strategy_name_in_signal():
    df = _make_df()
    sig = TSIStrategy().generate(df)
    assert sig.strategy == "tsi"


# ── 데이터 부족 테스트 ─────────────────────────────────────────────────────


def test_insufficient_data_returns_hold():
    df = _make_df(n=30)
    sig = TSIStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_exactly_min_rows():
    """50행 정확히 — 유효한 Action 반환."""
    df = _make_df(n=50)
    sig = TSIStrategy().generate(df)
    assert sig.action in list(Action)


def test_49_rows_returns_hold():
    df = _make_df(n=49)
    sig = TSIStrategy().generate(df)
    assert sig.action == Action.HOLD


# ── _calc_tsi 내부 함수 테스트 ────────────────────────────────────────────


def test_calc_tsi_returns_four_floats():
    df = _make_df(n=60)
    result = _calc_tsi(df)
    assert len(result) == 4
    for val in result:
        assert isinstance(val, float)


def test_calc_tsi_uptrend_positive():
    """상승 추세에서 TSI > 0."""
    df = _make_uptrend_df()
    tsi_now, _, _, _ = _calc_tsi(df)
    assert tsi_now > 0


def test_calc_tsi_downtrend_negative():
    """하락 추세에서 TSI < 0."""
    df = _make_downtrend_df()
    tsi_now, _, _, _ = _calc_tsi(df)
    assert tsi_now < 0


# ── HOLD 조건 테스트 ───────────────────────────────────────────────────────


def test_flat_market_holds():
    """평탄한 시장 → PC≈0 → HOLD."""
    df = _make_df(n=60)
    sig = TSIStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_hold_action_has_low_confidence():
    df = _make_df(n=60)
    sig = TSIStrategy().generate(df)
    if sig.action == Action.HOLD:
        assert sig.confidence == Confidence.LOW


# ── BUY/SELL 신호 공통 테스트 ─────────────────────────────────────────────


def test_buy_signal_entry_price_is_close():
    """BUY 신호 진입가 = 신호 봉 close."""
    df = _make_uptrend_df()
    sig = TSIStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)


def test_sell_signal_entry_price_is_close():
    df = _make_downtrend_df()
    sig = TSIStrategy().generate(df)
    if sig.action == Action.SELL:
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)


def test_buy_signal_has_bull_case():
    df = _make_uptrend_df()
    sig = TSIStrategy().generate(df)
    if sig.action == Action.BUY:
        assert len(sig.bull_case) > 0


def test_sell_signal_has_bear_case():
    df = _make_downtrend_df()
    sig = TSIStrategy().generate(df)
    if sig.action == Action.SELL:
        assert len(sig.bear_case) > 0


# ── Confidence 레벨 테스트 ────────────────────────────────────────────────


def test_non_hold_signal_confidence():
    """BUY/SELL 신호는 MEDIUM 또는 HIGH."""
    for df in [_make_uptrend_df(), _make_downtrend_df(),
               _make_cross_up_df(), _make_cross_down_df()]:
        sig = TSIStrategy().generate(df)
        if sig.action != Action.HOLD:
            assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


# ── 엣지 케이스 ────────────────────────────────────────────────────────────


def test_zero_price_change_no_crash():
    """모든 PC=0일 때 ZeroDivision 없어야 함."""
    df = _make_df(n=60)
    sig = TSIStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_large_dataframe():
    df = _make_df(n=500)
    sig = TSIStrategy().generate(df)
    assert isinstance(sig, Signal)
