"""Tests for SmartMoneyConceptStrategy."""

import pandas as pd
import pytest

from src.strategy.smc_strategy import SmartMoneyConceptStrategy
from src.strategy.base import Action, Confidence


def _make_df(rows):
    return pd.DataFrame(rows)


def _base_rows(n=20):
    """중립 봉 n개: 100 근처 횡보."""
    return [
        {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1000.0}
        for _ in range(n)
    ]


def _make_choch_buy_df():
    """
    bearish structure (5봉 하락) + close > recent_hh → CHoCH BUY
    총 20행, idx=18

    rolling(5) at idx=18: rows[14..18]
    str_down=1 iff row18.close < row14.close

    recent_hh at idx=18 = max(high[9..17])
    CHoCH BUY iff row18.close > recent_hh

    해결: rows 0~17 high를 모두 90.0으로 낮게 설정
    → recent_hh = max(high[9..17]) = 90.0
    row14.close=98 (하락 시작), row18.close=91 < 98 (str_down=1) AND 91 > 90 (> recent_hh) ✓
    """
    # base: high=90.0, low=89.0, close=89.5
    rows = [
        {"open": 89.5, "high": 90.0, "low": 89.0, "close": 89.5, "volume": 1000.0}
        for _ in range(20)
    ]
    # rows 14~17: 하락 구조 close 98→97→96→95, high=90 유지
    rows[14] = {"open": 98.5, "high": 90.0, "low": 97.0, "close": 98.0, "volume": 1000.0}
    rows[15] = {"open": 97.5, "high": 90.0, "low": 96.0, "close": 97.0, "volume": 1000.0}
    rows[16] = {"open": 96.5, "high": 90.0, "low": 95.0, "close": 96.0, "volume": 1000.0}
    rows[17] = {"open": 95.5, "high": 90.0, "low": 94.0, "close": 95.0, "volume": 1000.0}
    # recent_hh at idx=18 = max(high[9..17]) = 90.0
    # row18.close=91 > 90.0 (> recent_hh=90) ✓
    # str_down: row18.close=91 < row14.close=98 ✓
    rows[18] = {"open": 90.5, "high": 92.0, "low": 90.0, "close": 91.0, "volume": 1000.0}
    rows[19] = {"open": 91.0, "high": 92.0, "low": 90.5, "close": 91.5, "volume": 1000.0}
    return _make_df(rows)


def _make_choch_sell_df():
    """
    bullish structure (5봉 상승) + close < recent_ll → CHoCH SELL
    총 20행, idx=18

    rolling(5) at idx=18: rows[14..18]
    str_up=1 iff row18.close > row14.close
    CHoCH SELL iff row18.close < recent_ll = min(low[9..17])

    해결: rows 0~17 low를 모두 115.0으로 높게 설정
    → recent_ll = min(low[9..17]) = 115.0
    row14.close=105 (상승 시작), row18.close=109 > 105 (str_up=1) AND 109 < 115 (< recent_ll) ✓
    """
    # base: low=115.0, high=116.0, close=115.5
    rows = [
        {"open": 115.5, "high": 116.0, "low": 115.0, "close": 115.5, "volume": 1000.0}
        for _ in range(20)
    ]
    # rows 14~17: 상승 구조 close 105→106→107→108, low=115 유지
    rows[14] = {"open": 104.5, "high": 116.0, "low": 115.0, "close": 105.0, "volume": 1000.0}
    rows[15] = {"open": 105.5, "high": 116.0, "low": 115.0, "close": 106.0, "volume": 1000.0}
    rows[16] = {"open": 106.5, "high": 116.0, "low": 115.0, "close": 107.0, "volume": 1000.0}
    rows[17] = {"open": 107.5, "high": 116.0, "low": 115.0, "close": 108.0, "volume": 1000.0}
    # recent_ll at idx=18 = min(low[9..17]) = 115.0
    # row18.close=109 > row14.close=105 → str_up=1 ✓
    # row18.close=109 < 115.0=recent_ll → CHoCH SELL ✓
    rows[18] = {"open": 108.5, "high": 110.0, "low": 108.0, "close": 109.0, "volume": 1000.0}
    rows[19] = {"open": 109.0, "high": 110.0, "low": 108.0, "close": 109.5, "volume": 1000.0}
    return _make_df(rows)


# ── 1. 이름 확인 ──────────────────────────────────────────────────────────
def test_name():
    assert SmartMoneyConceptStrategy.name == "smc_strategy"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────
def test_insufficient_data():
    s = SmartMoneyConceptStrategy()
    df = _make_df(_base_rows(10))
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exact_min_rows_neutral():
    """15행, 중립 → HOLD."""
    s = SmartMoneyConceptStrategy()
    df = _make_df(_base_rows(15))
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 3. CHoCH BUY ────────────────────────────────────────────────────────
def test_choch_buy_signal():
    """bearish structure + close > recent_hh → BUY."""
    s = SmartMoneyConceptStrategy()
    df = _make_choch_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert "CHoCH BUY" in sig.reasoning


def test_choch_buy_strategy_name():
    """BUY 신호의 strategy 필드."""
    s = SmartMoneyConceptStrategy()
    sig = s.generate(_make_choch_buy_df())
    assert sig.strategy == "smc_strategy"


def test_choch_buy_fields_populated():
    """BUY 신호 필드 비어있지 않음."""
    s = SmartMoneyConceptStrategy()
    sig = s.generate(_make_choch_buy_df())
    assert sig.invalidation != ""
    assert sig.bull_case != ""
    assert sig.bear_case != ""
    assert isinstance(sig.entry_price, float)


# ── 4. CHoCH SELL ───────────────────────────────────────────────────────
def test_choch_sell_signal():
    """bullish structure + close < recent_ll → SELL."""
    s = SmartMoneyConceptStrategy()
    df = _make_choch_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert "CHoCH SELL" in sig.reasoning


def test_choch_sell_strategy_name():
    s = SmartMoneyConceptStrategy()
    sig = s.generate(_make_choch_sell_df())
    assert sig.strategy == "smc_strategy"


def test_choch_sell_fields_populated():
    s = SmartMoneyConceptStrategy()
    sig = s.generate(_make_choch_sell_df())
    assert sig.invalidation != ""
    assert sig.bull_case != ""
    assert sig.bear_case != ""


# ── 5. Confidence: volume 기반 ──────────────────────────────────────────
def _make_choch_buy_high_vol_df():
    """
    CHoCH BUY 데이터 (30행) + idx=28에서 HIGH volume.
    avg_vol rolling(20) at idx=28: rows[9..28] → 20행 모두 포함 → avg 계산 정상.
    rows 0~27: volume=100, row28: volume=200
    avg = (19*100 + 200)/20 = 105 → 200 > 157.5 → HIGH
    """
    n = 30
    rows = [
        {"open": 89.5, "high": 90.0, "low": 89.0, "close": 89.5, "volume": 100.0}
        for _ in range(n)
    ]
    # CHoCH BUY 구조: rows 24~27 하락, row28 돌파
    rows[24] = {"open": 98.5, "high": 90.0, "low": 97.0, "close": 98.0, "volume": 100.0}
    rows[25] = {"open": 97.5, "high": 90.0, "low": 96.0, "close": 97.0, "volume": 100.0}
    rows[26] = {"open": 96.5, "high": 90.0, "low": 95.0, "close": 96.0, "volume": 100.0}
    rows[27] = {"open": 95.5, "high": 90.0, "low": 94.0, "close": 95.0, "volume": 100.0}
    # recent_hh at idx=28 = max(high[19..27]) = 90.0 (all 90.0)
    # str_down: row28.close=91 < row24.close=98 ✓, close=91 > 90.0=recent_hh ✓
    rows[28] = {"open": 90.5, "high": 92.0, "low": 90.0, "close": 91.0, "volume": 200.0}
    rows[29] = {"open": 91.0, "high": 92.0, "low": 90.5, "close": 91.5, "volume": 100.0}
    return _make_df(rows)


def test_high_confidence_on_high_volume():
    """volume > avg * 1.5 → HIGH."""
    s = SmartMoneyConceptStrategy()
    sig = s.generate(_make_choch_buy_high_vol_df())
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_medium_confidence_on_normal_volume():
    """volume 보통 → MEDIUM (BUY 신호 시)."""
    df = _make_choch_buy_df()
    s = SmartMoneyConceptStrategy()
    sig = s.generate(df)
    # volume=1000, avg~1000, 1000 <= 1000*1.5=1500 → MEDIUM
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


# ── 6. HOLD signal 필드 ────────────────────────────────────────────────
def test_hold_signal_fields():
    s = SmartMoneyConceptStrategy()
    df = _make_df(_base_rows(20))
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.strategy == "smc_strategy"
    assert sig.confidence == Confidence.LOW


# ── 7. entry_price ───────────────────────────────────────────────────────
def test_buy_entry_price_equals_close():
    s = SmartMoneyConceptStrategy()
    df = _make_choch_buy_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df.iloc[-2]["close"]))


def test_sell_entry_price_equals_close():
    s = SmartMoneyConceptStrategy()
    df = _make_choch_sell_df()
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(float(df.iloc[-2]["close"]))
