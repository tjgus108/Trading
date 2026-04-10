"""Tests for OrderBlockStrategy."""

import pandas as pd
import pytest

from src.strategy.order_block import OrderBlockStrategy
from src.strategy.base import Action, Confidence


def _base_rows(n: int = 20) -> list:
    """기본 중립 캔들 n개 (음봉/양봉 교차 없음, 큰 이동 없음)."""
    return [
        {
            "open": 100.0, "high": 101.0, "low": 99.0,
            "close": 100.5, "volume": 1000.0, "atr14": 2.0,
        }
        for _ in range(n)
    ]


def _make_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows)


# ── 1. 이름 확인 ──────────────────────────────────────────────────────────

def test_name():
    assert OrderBlockStrategy.name == "order_block"


# ── 2. 데이터 부족 → HOLD ────────────────────────────────────────────────

def test_insufficient_data():
    s = OrderBlockStrategy()
    df = _make_df(_base_rows(10))
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows_no_ob():
    """15행, OB 없는 데이터 → HOLD."""
    s = OrderBlockStrategy()
    df = _make_df(_base_rows(15))
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 3. Bullish OB BUY 신호 ───────────────────────────────────────────────

def _make_bullish_ob_df(close_in_ob: float = 98.5) -> pd.DataFrame:
    """
    idx = len-2 = 18 (총 20행)
    i=16: 음봉 OB (open=102, high=102, low=97, close=97.5) → size=5
    i=17: 5% 이상 상승봉 (prev close=97.5 → curr close=103.2, ~5.8% up)
    idx=18: close가 OB 존 [97.0, 102.0] 내 → BUY
    ATR=2.0, OB size=5.0 > ATR*1.0=2.0 → HIGH
    """
    rows = _base_rows(20)
    # i=16: 음봉 OB (high=102, low=97 → size=5)
    rows[16] = {"open": 102.0, "high": 102.0, "low": 97.0, "close": 97.5,
                "volume": 1000.0, "atr14": 2.0}
    # i=17: 5% 이상 상승봉
    rows[17] = {"open": 97.5, "high": 104.0, "low": 97.0, "close": 103.2,
                "volume": 2000.0, "atr14": 2.0}
    # idx=18: close는 OB 존 [97.0, 102.0] 내, 이 봉은 양봉이 아니어야 함
    # (bearish OB 탐지 방지: idx=18이 강한 하락봉이 되면 안 됨)
    rows[18] = {"open": 99.0, "high": 100.0, "low": 97.5, "close": close_in_ob,
                "volume": 1500.0, "atr14": 2.0}
    return _make_df(rows)


def test_bullish_ob_buy_signal():
    """Bullish OB 존 진입 → BUY."""
    s = OrderBlockStrategy()
    df = _make_bullish_ob_df(close_in_ob=98.0)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert "Bullish OB" in sig.reasoning


def test_bullish_ob_high_confidence():
    """OB 크기 > ATR14 → HIGH confidence."""
    s = OrderBlockStrategy()
    # OB: low=97, high=102 → size=5.0, ATR=2.0 → HIGH (5.0 > 2.0)
    df = _make_bullish_ob_df(close_in_ob=98.0)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_bullish_ob_medium_confidence():
    """OB 크기 <= ATR14 → MEDIUM confidence."""
    s = OrderBlockStrategy()
    rows = _base_rows(20)
    # OB 크기 = 0.5 (< ATR=2.0) → MEDIUM
    rows[16] = {"open": 100.3, "high": 100.5, "low": 100.0, "close": 100.1,
                "volume": 1000.0, "atr14": 2.0}
    rows[17] = {"open": 100.1, "high": 106.0, "low": 100.0, "close": 105.4,
                "volume": 2000.0, "atr14": 2.0}
    rows[18] = {"open": 100.2, "high": 100.4, "low": 100.0, "close": 100.2,
                "volume": 1500.0, "atr14": 2.0}
    df = _make_df(rows)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


def test_bullish_ob_close_outside_ob_hold():
    """close가 OB 존 밖 → HOLD."""
    s = OrderBlockStrategy()
    df = _make_bullish_ob_df(close_in_ob=96.0)  # OB low=97, 이하
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. Bearish OB SELL 신호 ──────────────────────────────────────────────

def _make_bearish_ob_df(close_in_ob: float = 101.0) -> pd.DataFrame:
    """
    i=16: 양봉 OB (low=100, high=105) → size=5, ATR=2 → HIGH
    i=17: 5% 이상 하락봉 (close=96, prev close=101.5 → -5.4%)
    idx=18: close가 OB 존 [100.0, 105.0] 내에 있으면 SELL
    주의: idx=18은 강한 상승봉이 되면 안 됨 (bullish OB 오탐 방지).
    idx=18의 close < prev row(17) close여야 bullish_ob가 찾아지지 않음.
    row18 close=101.0 vs row17 close=96.0 → 5.2% up → bullish OB 탐지됨!
    따라서 row18 close를 row17 close 이하로 설정.
    """
    rows = _base_rows(20)
    rows[16] = {"open": 100.5, "high": 105.0, "low": 100.0, "close": 101.5,
                "volume": 1000.0, "atr14": 2.0}
    rows[17] = {"open": 101.5, "high": 102.0, "low": 95.0, "close": 96.0,
                "volume": 2000.0, "atr14": 2.0}
    # close_in_ob은 OB 존 [100.0, 105.0] 내 값이어야 하지만
    # row17 close=96.0 대비 상승폭이 5% 미만이어야 bullish OB 미탐지
    # 100.0이면 (100-96)/96*100 = 4.17% < 5% → OK
    rows[18] = {"open": 101.0, "high": 102.0, "low": 99.5, "close": close_in_ob,
                "volume": 1500.0, "atr14": 2.0}
    return _make_df(rows)


def test_bearish_ob_sell_signal():
    """Bearish OB 존 진입 → SELL."""
    s = OrderBlockStrategy()
    # close=100.5: row17 close=96 → (100.5-96)/96*100 = 4.7% < 5% → no bullish OB
    df = _make_bearish_ob_df(close_in_ob=100.5)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert "Bearish OB" in sig.reasoning


def test_bearish_ob_high_confidence():
    """Bearish OB 크기 > ATR14 → HIGH confidence."""
    s = OrderBlockStrategy()
    # OB size = 105.0 - 100.0 = 5.0, ATR=2.0 → HIGH
    df = _make_bearish_ob_df(close_in_ob=100.5)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


def test_bearish_ob_close_outside_ob_hold():
    """close가 Bearish OB 존 밖 → HOLD."""
    s = OrderBlockStrategy()
    # OB: [100.0, 105.0], close=95.5 → 밖 (low 미만)
    # 단, 95.5는 row17 close=96 대비 하락이므로 bullish OB 미탐지
    rows = _base_rows(20)
    rows[16] = {"open": 100.5, "high": 105.0, "low": 100.0, "close": 101.5,
                "volume": 1000.0, "atr14": 2.0}
    rows[17] = {"open": 101.5, "high": 102.0, "low": 95.0, "close": 96.0,
                "volume": 2000.0, "atr14": 2.0}
    rows[18] = {"open": 95.0, "high": 96.0, "low": 94.0, "close": 95.5,
                "volume": 1500.0, "atr14": 2.0}
    df = _make_df(rows)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 5. Signal 필드 검증 ───────────────────────────────────────────────────

def test_buy_signal_fields():
    """BUY 신호 필드 전체 확인."""
    s = OrderBlockStrategy()
    df = _make_bullish_ob_df(close_in_ob=98.0)
    sig = s.generate(df)
    assert sig.strategy == "order_block"
    assert sig.action == Action.BUY
    assert isinstance(sig.entry_price, float)
    assert sig.invalidation != ""
    assert sig.bull_case != ""
    assert sig.bear_case != ""


def test_sell_signal_fields():
    """SELL 신호 필드 전체 확인."""
    s = OrderBlockStrategy()
    df = _make_bearish_ob_df(close_in_ob=100.5)
    sig = s.generate(df)
    assert sig.strategy == "order_block"
    assert sig.action == Action.SELL
    assert isinstance(sig.entry_price, float)
    assert sig.invalidation != ""


def test_hold_signal_fields():
    """HOLD 신호 필드 확인."""
    s = OrderBlockStrategy()
    df = _make_df(_base_rows(20))
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.strategy == "order_block"
    assert sig.confidence == Confidence.LOW


# ── 6. ATR 컬럼 없을 때 fallback ─────────────────────────────────────────

def test_no_atr_column_fallback():
    """atr14 컬럼 없어도 동작."""
    rows = _base_rows(20)
    rows[16] = {"open": 99.5, "high": 99.0, "low": 97.0, "close": 97.5, "volume": 1000.0}
    rows[17] = {"open": 97.5, "high": 103.0, "low": 97.0, "close": 102.7, "volume": 2000.0}
    rows[18] = {"open": 99.0, "high": 100.0, "low": 97.5, "close": 98.0, "volume": 1500.0}
    # atr14 제거
    clean = [{k: v for k, v in r.items() if k != "atr14"} for r in rows]
    df = _make_df(clean)
    sig = OrderBlockStrategy().generate(df)
    # 결과는 BUY or HOLD, 에러 없어야 함
    assert sig.action in (Action.BUY, Action.HOLD, Action.SELL)


# ── 7. entry_price 정확성 ─────────────────────────────────────────────────

def test_entry_price_equals_close():
    """entry_price == last close."""
    s = OrderBlockStrategy()
    df = _make_bullish_ob_df(close_in_ob=98.0)
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(98.0)
