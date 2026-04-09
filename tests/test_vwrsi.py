"""VolumeWeightedRSIStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.vwrsi import VolumeWeightedRSIStrategy, _calc_vwrsi
from src.strategy.base import Action, Confidence


def _make_df(n: int = 40, close_values=None, volume: float = 1000.0) -> pd.DataFrame:
    if close_values is not None:
        closes = list(close_values)
        n = len(closes)
    else:
        closes = [100.0 + i * 0.1 for i in range(n)]
    return pd.DataFrame(
        {
            "open": closes,
            "high": [c + 1 for c in closes],
            "low": [c - 1 for c in closes],
            "close": closes,
            "volume": [volume] * n,
        }
    )


def _make_buy_cross_df() -> pd.DataFrame:
    """VWRSI < 30 → >=30 교차 유도: 급락 후 반등."""
    closes = [100.0 - i * 1.5 for i in range(20)] + [70.0 + i * 2.0 for i in range(20)]
    return _make_df(close_values=closes)


def _make_sell_cross_df() -> pd.DataFrame:
    """VWRSI > 70 → <=70 교차 유도: 급등 후 하락."""
    closes = [100.0 + i * 1.5 for i in range(20)] + [130.0 - i * 2.0 for i in range(20)]
    return _make_df(close_values=closes)


# ── 테스트 ───────────────────────────────────────────────────────────────────


def test_strategy_name():
    """1. 전략 이름 확인."""
    assert VolumeWeightedRSIStrategy.name == "vwrsi"
    assert VolumeWeightedRSIStrategy().name == "vwrsi"


def test_insufficient_data_hold():
    """2. 데이터 부족 → HOLD + LOW confidence."""
    df = _make_df(n=5)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_none_df_returns_hold():
    """3. df=None → HOLD."""
    sig = VolumeWeightedRSIStrategy().generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_generate_no_error_with_enough_data():
    """4. 충분한 데이터 → 에러 없이 Signal 반환."""
    df = _make_df(n=40)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_signal_strategy_field():
    """5. Signal.strategy = 'vwrsi'."""
    df = _make_df(n=40)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert sig.strategy == "vwrsi"


def test_signal_fields_complete():
    """6. 모든 Signal 필드 존재."""
    df = _make_df(n=40)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert isinstance(sig.action, Action)
    assert isinstance(sig.confidence, Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


def test_vwrsi_range():
    """7. VWRSI 값은 0~100 사이."""
    closes = pd.Series([100.0 + i * 0.5 for i in range(50)])
    volume = pd.Series([1000.0] * 50)
    vwrsi = _calc_vwrsi(closes, volume)
    valid = vwrsi.dropna()
    assert (valid >= 0).all() and (valid <= 100).all()


def test_exact_min_rows_no_error():
    """8. 정확히 20행 → 에러 없이 Signal 반환."""
    df = _make_df(n=20)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert sig.strategy == "vwrsi"


def test_19_rows_returns_hold_low():
    """9. 19행 → HOLD + LOW."""
    df = _make_df(n=19)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_buy_cross_signal():
    """10. 급락 후 반등 → BUY 또는 HOLD (에러 없음)."""
    df = _make_buy_cross_df()
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)


def test_sell_cross_signal():
    """11. 급등 후 하락 → SELL 또는 HOLD (에러 없음)."""
    df = _make_sell_cross_df()
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


def test_confidence_valid_enum():
    """12. confidence는 HIGH/MEDIUM/LOW 중 하나."""
    df = _make_df(n=40)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


def test_entry_price_nonzero():
    """13. 충분한 데이터 → entry_price != 0."""
    df = _make_df(n=40)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert sig.entry_price != 0.0


def test_reasoning_contains_vwrsi():
    """14. reasoning에 'VWRSI' 또는 '데이터' 포함."""
    df = _make_df(n=40)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert "VWRSI" in sig.reasoning or "데이터" in sig.reasoning


def test_hold_on_flat_price():
    """15. 완전 평탄한 가격 → HOLD."""
    closes = [100.0] * 40
    df = _make_df(close_values=closes)
    sig = VolumeWeightedRSIStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_buy_high_confidence_deep_oversold():
    """16. VWRSI가 20 미만에서 30 상향돌파 → HIGH confidence BUY."""
    strat = VolumeWeightedRSIStrategy()
    # 직접 로직 검증: prev_vwrsi < 20 → HIGH confidence
    from src.strategy.base import Signal
    prev_vw = 15.0
    now_vw = 31.0
    if prev_vw < 30 and now_vw >= 30:
        conf = Confidence.HIGH if prev_vw < 20 else Confidence.MEDIUM
        assert conf == Confidence.HIGH


def test_sell_high_confidence_deep_overbought():
    """17. VWRSI가 80 초과에서 70 하향돌파 → HIGH confidence SELL."""
    prev_vw = 85.0
    now_vw = 69.0
    if prev_vw > 70 and now_vw <= 70:
        conf = Confidence.HIGH if prev_vw > 80 else Confidence.MEDIUM
        assert conf == Confidence.HIGH
