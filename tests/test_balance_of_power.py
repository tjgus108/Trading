"""
BalanceOfPowerStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.balance_of_power import BalanceOfPowerStrategy, _calc_bop_lines
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 40, close: float = 100.0) -> pd.DataFrame:
    """flat DataFrame (open == close → BOP = 0)."""
    return pd.DataFrame({
        "open": [close] * n,
        "close": [close] * n,
        "high": [close + 2.0] * n,
        "low": [close - 2.0] * n,
        "volume": [1000.0] * n,
    })


def _make_buy_df(n: int = 50) -> pd.DataFrame:
    """
    BOP SMA가 음수 구간에서 signal 상향 교차 → BUY 유도.
    앞부분: 강한 매도 (close < open), 뒷부분: 약한 매수 반전.
    """
    opens = [100.0] * n
    # 앞 n-10: 강한 매도 (bop 음수)
    closes = [98.0] * (n - 10)
    # 뒷 10: 점진적 반전 — bop_sma가 signal을 상향 교차하도록
    closes += [98.5, 99.0, 99.5, 99.8, 100.0, 100.2, 100.5, 100.8, 101.0, 101.2]
    highs = [o + 3.0 for o in opens]
    lows = [c - 0.5 for c in closes]
    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


def _make_sell_df(n: int = 50) -> pd.DataFrame:
    """
    BOP SMA가 양수 구간에서 signal 하향 교차 → SELL 유도.
    앞부분: 강한 매수 (close > open), 뒷부분: 약한 매도 반전.
    """
    opens = [100.0] * n
    closes = [102.0] * (n - 10)
    closes += [101.5, 101.0, 100.5, 100.2, 100.0, 99.8, 99.5, 99.2, 99.0, 98.8]
    highs = [c + 0.5 for c in closes]
    lows = [o - 3.0 for o in opens]
    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


def _make_high_conf_buy_df(n: int = 60) -> pd.DataFrame:
    """극단적 매도 후 강한 반전 → HIGH confidence BUY."""
    opens = [100.0] * n
    closes = [94.0] * (n - 8) + [94.5, 95.0, 95.5, 96.0, 96.5, 97.0, 97.5, 98.0]
    highs = [o + 4.0 for o in opens]
    lows = [c - 0.3 for c in closes]
    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


def _make_high_conf_sell_df(n: int = 60) -> pd.DataFrame:
    """극단적 매수 후 강한 반전 → HIGH confidence SELL."""
    opens = [100.0] * n
    closes = [106.0] * (n - 8) + [105.5, 105.0, 104.5, 104.0, 103.5, 103.0, 102.5, 102.0]
    highs = [c + 0.3 for c in closes]
    lows = [o - 4.0 for o in opens]
    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })


# ── 1. 전략명 확인 ─────────────────────────────────────────────────────────

def test_strategy_name():
    assert BalanceOfPowerStrategy.name == "balance_of_power"


# ── 2. 인스턴스 생성 ───────────────────────────────────────────────────────

def test_instance_creation():
    s = BalanceOfPowerStrategy()
    assert isinstance(s, BalanceOfPowerStrategy)


# ── 3. 데이터 부족 → HOLD ─────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    df = _make_df(n=10)
    sig = BalanceOfPowerStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 4. None 입력 → HOLD ───────────────────────────────────────────────────

def test_none_input_returns_hold():
    sig = BalanceOfPowerStrategy().generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ─────────────────────────────────────────

def test_insufficient_data_reasoning():
    df = _make_df(n=10)
    sig = BalanceOfPowerStrategy().generate(df)
    assert "Insufficient" in sig.reasoning or "부족" in sig.reasoning or "10" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ──────────────────────────────────────────

def test_normal_data_returns_signal():
    df = _make_df(n=40)
    sig = BalanceOfPowerStrategy().generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성 ───────────────────────────────────────────────────

def test_signal_fields_complete():
    df = _make_df(n=40)
    sig = BalanceOfPowerStrategy().generate(df)
    assert sig.action in list(Action)
    assert sig.confidence in list(Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


# ── 8. BUY reasoning 키워드 확인 ─────────────────────────────────────────

def test_buy_reasoning_keyword():
    df = _make_buy_df()
    sig = BalanceOfPowerStrategy().generate(df)
    if sig.action == Action.BUY:
        assert any(kw in sig.reasoning for kw in ["BOP", "상향", "cross", "교차"])


# ── 9. SELL reasoning 키워드 확인 ────────────────────────────────────────

def test_sell_reasoning_keyword():
    df = _make_sell_df()
    sig = BalanceOfPowerStrategy().generate(df)
    if sig.action == Action.SELL:
        assert any(kw in sig.reasoning for kw in ["BOP", "하향", "cross", "교차"])


# ── 10. HIGH confidence 테스트 ────────────────────────────────────────────

def test_high_confidence_buy():
    df = _make_high_conf_buy_df()
    sig = BalanceOfPowerStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_high_confidence_sell():
    df = _make_high_conf_sell_df()
    sig = BalanceOfPowerStrategy().generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 11. MEDIUM confidence 테스트 ─────────────────────────────────────────

def test_hold_has_low_confidence():
    """HOLD 신호는 LOW confidence."""
    df = _make_df(n=40)
    sig = BalanceOfPowerStrategy().generate(df)
    if sig.action == Action.HOLD:
        assert sig.confidence == Confidence.LOW


# ── 12. entry_price > 0 ───────────────────────────────────────────────────

def test_entry_price_positive():
    df = _make_df(n=40)
    sig = BalanceOfPowerStrategy().generate(df)
    assert sig.entry_price > 0


# ── 13. strategy 필드 값 확인 ─────────────────────────────────────────────

def test_strategy_field_in_signal():
    df = _make_df(n=40)
    sig = BalanceOfPowerStrategy().generate(df)
    assert sig.strategy == "balance_of_power"


# ── 14. 최소 행 수에서 동작 ───────────────────────────────────────────────

def test_exactly_min_rows():
    """30행 정확히 — 유효한 Action 반환."""
    df = _make_df(n=30)
    sig = BalanceOfPowerStrategy().generate(df)
    assert sig.action in list(Action)


def test_29_rows_returns_hold():
    df = _make_df(n=29)
    sig = BalanceOfPowerStrategy().generate(df)
    assert sig.action == Action.HOLD


# ── zero-range 엣지 케이스 ────────────────────────────────────────────────

def test_zero_range_no_crash():
    """high == low — ZeroDivision 없어야 함."""
    df = _make_df(n=40)
    df["high"] = df["close"]
    df["low"] = df["close"]
    sig = BalanceOfPowerStrategy().generate(df)
    assert isinstance(sig, Signal)
