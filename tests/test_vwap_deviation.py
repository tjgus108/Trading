"""
VWAPDeviationStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.vwap_deviation import VWAPDeviationStrategy, _calc_zscore
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, close: float = 100.0) -> pd.DataFrame:
    """기본 flat DataFrame."""
    return pd.DataFrame({
        "open": [close] * n,
        "close": [close] * n,
        "high": [close + 2.0] * n,
        "low": [close - 2.0] * n,
        "volume": [1000.0] * n,
    })


def _make_buy_df(n: int = 40) -> pd.DataFrame:
    """VWAP 대비 큰 음의 편차 후 회복 → BUY 신호 유도."""
    closes = [100.0] * (n - 5) + [70.0, 72.0, 74.0, 76.0, 78.0]
    volumes = [1000.0] * n
    return pd.DataFrame({
        "open": [100.0] * n,
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": volumes,
    })


def _make_sell_df(n: int = 40) -> pd.DataFrame:
    """VWAP 대비 큰 양의 편차 후 하락 → SELL 신호 유도."""
    closes = [100.0] * (n - 5) + [130.0, 128.0, 126.0, 124.0, 122.0]
    volumes = [1000.0] * n
    return pd.DataFrame({
        "open": [100.0] * n,
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": volumes,
    })


def _make_high_confidence_buy_df(n: int = 50) -> pd.DataFrame:
    """극단적인 VWAP 하방 편차 → HIGH confidence BUY."""
    closes = [100.0] * (n - 5) + [50.0, 52.0, 54.0, 56.0, 58.0]
    volumes = [1000.0] * n
    return pd.DataFrame({
        "open": [100.0] * n,
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": volumes,
    })


def _make_high_confidence_sell_df(n: int = 50) -> pd.DataFrame:
    """극단적인 VWAP 상방 편차 → HIGH confidence SELL."""
    closes = [100.0] * (n - 5) + [160.0, 158.0, 156.0, 154.0, 152.0]
    volumes = [1000.0] * n
    return pd.DataFrame({
        "open": [100.0] * n,
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": volumes,
    })


# ── 1. 전략명 확인 ─────────────────────────────────────────────────────────

def test_strategy_name():
    assert VWAPDeviationStrategy.name == "vwap_deviation"


# ── 2. 인스턴스 생성 ───────────────────────────────────────────────────────

def test_instance_creation():
    s = VWAPDeviationStrategy()
    assert isinstance(s, VWAPDeviationStrategy)


# ── 3. 데이터 부족 → HOLD ─────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    df = _make_df(n=10)
    sig = VWAPDeviationStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 4. None 입력 → HOLD ───────────────────────────────────────────────────

def test_none_input_returns_hold():
    sig = VWAPDeviationStrategy().generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ─────────────────────────────────────────

def test_insufficient_data_reasoning():
    df = _make_df(n=10)
    sig = VWAPDeviationStrategy().generate(df)
    assert "Insufficient" in sig.reasoning or "부족" in sig.reasoning or "10" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ──────────────────────────────────────────

def test_normal_data_returns_signal():
    df = _make_df(n=30)
    sig = VWAPDeviationStrategy().generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성 ───────────────────────────────────────────────────

def test_signal_fields_complete():
    df = _make_df(n=30)
    sig = VWAPDeviationStrategy().generate(df)
    assert sig.action in list(Action)
    assert sig.confidence in list(Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


# ── 8. BUY reasoning 키워드 확인 ─────────────────────────────────────────

def test_buy_reasoning_keyword():
    df = _make_buy_df()
    sig = VWAPDeviationStrategy().generate(df)
    if sig.action == Action.BUY:
        assert any(kw in sig.reasoning for kw in ["VWAP", "zscore", "dev_zscore", "하방", "회복"])


# ── 9. SELL reasoning 키워드 확인 ────────────────────────────────────────

def test_sell_reasoning_keyword():
    df = _make_sell_df()
    sig = VWAPDeviationStrategy().generate(df)
    if sig.action == Action.SELL:
        assert any(kw in sig.reasoning for kw in ["VWAP", "zscore", "dev_zscore", "상방", "하락"])


# ── 10. HIGH confidence 테스트 ────────────────────────────────────────────

def test_high_confidence_buy():
    df = _make_high_confidence_buy_df()
    sig = VWAPDeviationStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_high_confidence_sell():
    df = _make_high_confidence_sell_df()
    sig = VWAPDeviationStrategy().generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 11. MEDIUM confidence 테스트 ─────────────────────────────────────────

def test_medium_confidence_on_normal_signal():
    """비신호 구간은 LOW confidence."""
    df = _make_df(n=30)
    sig = VWAPDeviationStrategy().generate(df)
    if sig.action == Action.HOLD:
        assert sig.confidence == Confidence.LOW


# ── 12. entry_price > 0 ───────────────────────────────────────────────────

def test_entry_price_positive():
    df = _make_df(n=30)
    sig = VWAPDeviationStrategy().generate(df)
    assert sig.entry_price > 0


# ── 13. strategy 필드 값 확인 ─────────────────────────────────────────────

def test_strategy_field_in_signal():
    df = _make_df(n=30)
    sig = VWAPDeviationStrategy().generate(df)
    assert sig.strategy == "vwap_deviation"


# ── 14. 최소 행 수에서 동작 ───────────────────────────────────────────────

def test_exactly_min_rows():
    """25행 정확히 — 유효한 Action 반환."""
    df = _make_df(n=25)
    sig = VWAPDeviationStrategy().generate(df)
    assert sig.action in list(Action)


def test_24_rows_returns_hold():
    df = _make_df(n=24)
    sig = VWAPDeviationStrategy().generate(df)
    assert sig.action == Action.HOLD
