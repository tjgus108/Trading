"""Tests for FairValueGapStrategy."""

import pandas as pd
import pytest

from src.strategy.fvg_strategy import FairValueGapStrategy
from src.strategy.base import Action, Confidence


def _base_rows(n: int = 20) -> list:
    """기본 중립 캔들 n개 (FVG 없음: high=low=100 이므로 갭 불가)."""
    return [
        {
            "open": 100.0, "high": 100.5, "low": 99.5,
            "close": 100.0, "volume": 1000.0, "atr14": 2.0,
        }
        for _ in range(n)
    ]


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


# ── 1. 이름 확인 ──────────────────────────────────────────────────────────

def test_name():
    assert FairValueGapStrategy.name == "fvg_strategy"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────

def test_insufficient_data():
    s = FairValueGapStrategy()
    df = _make_df(_base_rows(10))
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows_no_fvg():
    """15행, FVG 없는 데이터 → HOLD."""
    s = FairValueGapStrategy()
    df = _make_df(_base_rows(15))
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 3. Bearish FVG → BUY (갭 채움) ──────────────────────────────────────

def _make_bearish_fvg_df(close_in_gap: float = 103.0) -> pd.DataFrame:
    """
    idx = len-2 = 18 (총 20행)
    bearish FVG at i=18: df[16].low=105.0 > df[18].high=102.0
      → fvg_low=102.0, fvg_high=105.0, gap=3.0
    row[17]: low >= row[15].high 이고 high <= row[19].low 이어야 추가 FVG 없음.
    모든 base rows는 high=100.5, low=99.5 이므로 row[15].high=100.5.
    row[17].low=103.0이면 _find_bullish_fvg에서 row[15].high(100.5) < row[17].low(103.0) → bullish FVG 생성!
    따라서 row[17].low를 낮게 설정 (100.0 이하).
    """
    rows = _base_rows(20)
    rows[16] = {"open": 106.0, "high": 107.0, "low": 105.0, "close": 105.5,
                "volume": 1000.0, "atr14": 2.0}
    # row[17]: low=99.5 이하로 설정해 row[15]와 bullish FVG 방지
    rows[17] = {"open": 104.0, "high": 105.0, "low": 99.0, "close": 104.0,
                "volume": 1000.0, "atr14": 2.0}
    # i=18 (idx): high=102.0 → fvg_low=102.0, fvg_high=105.0
    rows[18] = {"open": 102.5, "high": 102.0, "low": 101.0, "close": close_in_gap,
                "volume": 1000.0, "atr14": 2.0}
    return _make_df(rows)


def test_bearish_fvg_buy_signal():
    """Bearish FVG 존 진입 → BUY."""
    s = FairValueGapStrategy()
    df = _make_bearish_fvg_df(close_in_gap=103.0)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert "Bearish FVG" in sig.reasoning


def test_bearish_fvg_high_confidence():
    """gap > ATR14 * 1.5 → HIGH confidence."""
    s = FairValueGapStrategy()
    # 별도 데이터: gap=4.5, ATR=2.0 → 4.5 > 3.0 → HIGH
    rows = _base_rows(20)
    rows[16] = {"open": 106.0, "high": 107.0, "low": 106.5, "close": 106.8,
                "volume": 1000.0, "atr14": 2.0}
    rows[17] = {"open": 103.0, "high": 105.0, "low": 99.0, "close": 103.0,
                "volume": 1000.0, "atr14": 2.0}
    # fvg_low=102.0 (row18.high), fvg_high=106.5 (row16.low) → gap=4.5 > 3.0
    rows[18] = {"open": 102.5, "high": 102.0, "low": 101.0, "close": 104.0,
                "volume": 1000.0, "atr14": 2.0}
    df = _make_df(rows)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_bearish_fvg_medium_confidence():
    """gap <= ATR14 * 1.5 → MEDIUM confidence."""
    s = FairValueGapStrategy()
    rows = _base_rows(20)
    # gap = 0.8 (< ATR=2.0 * 1.5=3.0) → MEDIUM
    rows[16] = {"open": 102.0, "high": 103.0, "low": 102.5, "close": 102.2,
                "volume": 1000.0, "atr14": 2.0}
    rows[17] = {"open": 101.0, "high": 102.0, "low": 100.5, "close": 101.0,
                "volume": 1000.0, "atr14": 2.0}
    rows[18] = {"open": 101.8, "high": 101.7, "low": 101.5, "close": 101.8,
                "volume": 1000.0, "atr14": 2.0}
    df = _make_df(rows)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


def test_bearish_fvg_close_outside_gap_hold():
    """close가 Bearish FVG 존 밖 → HOLD."""
    s = FairValueGapStrategy()
    # 완전히 독립적인 데이터: FVG가 없는 단순 시세
    df = _make_df(_base_rows(20))
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. Bullish FVG → SELL (갭 채움) ─────────────────────────────────────

def _make_bullish_fvg_df(close_in_gap: float = 97.0) -> pd.DataFrame:
    """
    bullish FVG: candle[i-2].high < candle[i].low
    i=16: high=95.0
    i=18 (idx): low=97.0 → fvg_low=95.0, fvg_high=97.0
    """
    rows = _base_rows(20)
    rows[16] = {"open": 94.0, "high": 95.0, "low": 93.0, "close": 94.5,
                "volume": 1000.0, "atr14": 2.0}
    rows[17] = {"open": 95.5, "high": 96.0, "low": 95.0, "close": 95.5,
                "volume": 1000.0, "atr14": 2.0}
    rows[18] = {"open": 97.5, "high": 98.0, "low": 97.0, "close": close_in_gap,
                "volume": 1000.0, "atr14": 2.0}
    return _make_df(rows)


def test_bullish_fvg_sell_signal():
    """Bullish FVG 존 진입 → SELL."""
    s = FairValueGapStrategy()
    df = _make_bullish_fvg_df(close_in_gap=95.5)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert "Bullish FVG" in sig.reasoning


def test_bullish_fvg_high_confidence():
    """gap > ATR14 * 1.5 → HIGH confidence."""
    s = FairValueGapStrategy()
    rows = _base_rows(20)
    # gap = 97.0 - 93.0 = 4.0, ATR=2.0, threshold=3.0 → HIGH
    rows[16] = {"open": 92.0, "high": 93.0, "low": 91.0, "close": 92.5,
                "volume": 1000.0, "atr14": 2.0}
    rows[17] = {"open": 94.0, "high": 95.0, "low": 93.5, "close": 94.0,
                "volume": 1000.0, "atr14": 2.0}
    rows[18] = {"open": 97.5, "high": 98.0, "low": 97.0, "close": 93.5,
                "volume": 1000.0, "atr14": 2.0}
    df = _make_df(rows)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


def test_bullish_fvg_close_outside_gap_hold():
    """close가 Bullish FVG 존 밖 → HOLD."""
    s = FairValueGapStrategy()
    # FVG 없는 단순 데이터
    rows = _base_rows(20)
    # 모든 봉 동일 → 갭 없음
    df = _make_df(rows)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 5. Signal 필드 검증 ───────────────────────────────────────────────────

def test_buy_signal_fields():
    """BUY 신호 필드 전체 확인."""
    s = FairValueGapStrategy()
    df = _make_bearish_fvg_df(close_in_gap=103.0)
    sig = s.generate(df)
    assert sig.strategy == "fvg_strategy"
    assert sig.action == Action.BUY
    assert isinstance(sig.entry_price, float)
    assert sig.invalidation != ""
    assert sig.bull_case != ""
    assert sig.bear_case != ""


def test_sell_signal_fields():
    """SELL 신호 필드 전체 확인."""
    s = FairValueGapStrategy()
    df = _make_bullish_fvg_df(close_in_gap=95.5)
    sig = s.generate(df)
    assert sig.strategy == "fvg_strategy"
    assert sig.action == Action.SELL
    assert sig.invalidation != ""


def test_hold_signal_fields():
    """HOLD 신호 필드 확인."""
    s = FairValueGapStrategy()
    df = _make_df(_base_rows(20))
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.strategy == "fvg_strategy"
    assert sig.confidence == Confidence.LOW


# ── 6. ATR 컬럼 없을 때 fallback ─────────────────────────────────────────

def test_no_atr_column_fallback():
    """atr14 컬럼 없어도 동작."""
    rows = _base_rows(20)
    rows[16] = {"open": 106.0, "high": 107.0, "low": 105.0, "close": 105.5, "volume": 1000.0}
    rows[17] = {"open": 104.0, "high": 105.0, "low": 103.0, "close": 104.0, "volume": 1000.0}
    rows[18] = {"open": 102.5, "high": 102.0, "low": 101.0, "close": 103.0, "volume": 1000.0}
    clean = [{k: v for k, v in r.items() if k != "atr14"} for r in rows]
    df = _make_df(clean)
    sig = FairValueGapStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 7. entry_price 정확성 ─────────────────────────────────────────────────

def test_entry_price_equals_close():
    """entry_price == last close."""
    s = FairValueGapStrategy()
    df = _make_bearish_fvg_df(close_in_gap=103.0)
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(103.0)
