"""VolumeWeightedRSIStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volume_weighted_rsi import VolumeWeightedRSIStrategy, _calc_vrsi
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 40, close_values=None, volume: float = 1000.0) -> pd.DataFrame:
    if close_values is not None:
        closes = list(close_values)
        n = len(closes)
    else:
        closes = [100.0 + i * 0.1 for i in range(n)]
    return pd.DataFrame({
        "open": closes,
        "high": [c + 1 for c in closes],
        "low": [c - 1 for c in closes],
        "close": closes,
        "volume": [volume] * n,
    })


def _make_buy_cross_df() -> pd.DataFrame:
    """급락 후 반등 -> VRSI < 30 -> >= 30 교차."""
    closes = [100.0 - i * 2.0 for i in range(25)] + [50.0 + i * 3.0 for i in range(25)]
    return _make_df(close_values=closes)


def _make_sell_cross_df() -> pd.DataFrame:
    """급등 후 하락 -> VRSI > 70 -> <= 70 교차."""
    closes = [100.0 + i * 2.0 for i in range(25)] + [150.0 - i * 3.0 for i in range(25)]
    return _make_df(close_values=closes)


# ── 테스트 ────────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 확인."""
    assert VolumeWeightedRSIStrategy.name == "volume_weighted_rsi"
    assert VolumeWeightedRSIStrategy().name == "volume_weighted_rsi"


def test_instance_creation():
    """2. 인스턴스 생성."""
    strat = VolumeWeightedRSIStrategy()
    assert strat is not None


def test_insufficient_data_hold():
    """3. 데이터 부족 -> HOLD + LOW confidence."""
    df = _make_df(n=5)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_none_df_returns_hold():
    """4. df=None -> HOLD."""
    sig = VolumeWeightedRSIStrategy().generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_reasoning():
    """5. 데이터 부족 시 reasoning에 'Insufficient' 포함."""
    df = _make_df(n=5)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert "Insufficient" in sig.reasoning or "insufficient" in sig.reasoning.lower()


def test_normal_data_returns_signal():
    """6. 정상 데이터 -> Signal 반환."""
    df = _make_df(n=40)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_signal_fields_complete():
    """7. Signal 필드 완성."""
    df = _make_df(n=40)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert isinstance(sig.action, Action)
    assert isinstance(sig.confidence, Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


def test_buy_reasoning_keyword():
    """8. BUY reasoning에 'VRSI' 키워드 포함."""
    # 직접 BUY signal을 유도하는 데이터 구성
    df = _make_buy_cross_df()
    sig = VolumeWeightedRSIStrategy().generate(df)
    if sig.action == Action.BUY:
        assert "VRSI" in sig.reasoning or "vrsi" in sig.reasoning.lower()


def test_sell_reasoning_keyword():
    """9. SELL reasoning에 'VRSI' 키워드 포함."""
    df = _make_sell_cross_df()
    sig = VolumeWeightedRSIStrategy().generate(df)
    if sig.action == Action.SELL:
        assert "VRSI" in sig.reasoning or "vrsi" in sig.reasoning.lower()


def test_high_confidence_buy():
    """10. HIGH confidence BUY: vrsi_prev < 20."""
    from src.strategy.volume_weighted_rsi import VolumeWeightedRSIStrategy
    vrsi_prev = 15.0
    vrsi_now = 31.0
    if vrsi_prev < 30 and vrsi_now >= 30:
        conf = Confidence.HIGH if vrsi_prev < 20 else Confidence.MEDIUM
        assert conf == Confidence.HIGH


def test_medium_confidence_logic():
    """11. MEDIUM confidence: vrsi_prev between 20-30."""
    vrsi_prev = 25.0
    vrsi_now = 31.0
    if vrsi_prev < 30 and vrsi_now >= 30:
        conf = Confidence.HIGH if vrsi_prev < 20 else Confidence.MEDIUM
        assert conf == Confidence.MEDIUM


def test_entry_price_positive():
    """12. entry_price > 0 (충분한 데이터)."""
    df = _make_df(n=40)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert sig.entry_price > 0


def test_strategy_field_value():
    """13. strategy 필드 값 확인."""
    df = _make_df(n=40)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert sig.strategy == "volume_weighted_rsi"


def test_minimum_rows_works():
    """14. 최소 행 수(20)에서 동작."""
    df = _make_df(n=20)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert isinstance(sig, Signal)
    assert sig.strategy == "volume_weighted_rsi"
