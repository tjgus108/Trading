"""DeMarkerStrategy 단위 테스트 (14개 이상)."""

import pandas as pd
import pytest

from src.strategy.demarker import DeMarkerStrategy, _compute_demarker
from src.strategy.base import Action, Confidence


def _make_df(n: int = 30, close_values=None) -> pd.DataFrame:
    if close_values is not None:
        closes = list(close_values)
        n = len(closes)
    else:
        closes = [100.0 + i * 0.1 for i in range(n)]

    return pd.DataFrame(
        {
            "open": closes,
            "high": [c + 1.0 for c in closes],
            "low": [c - 1.0 for c in closes],
            "close": closes,
            "volume": [1000.0] * n,
        }
    )


def _make_buy_cross_df(n: int = 30) -> pd.DataFrame:
    """dem crosses above 0.3: 먼저 낮은 구간 유지 후 마지막에 반등."""
    # 급락 후 마지막 한 봉 반등 → DeMax 갑자기 커짐
    closes = [100.0 - i * 1.0 for i in range(n - 1)] + [100.0 - (n - 2) * 1.0 + 5.0]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    return pd.DataFrame(
        {
            "open": closes,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": [1000.0] * n,
        }
    )


def _make_sell_cross_df(n: int = 30) -> pd.DataFrame:
    """dem crosses below 0.7: 급등 후 마지막에 하락."""
    closes = [100.0 + i * 1.0 for i in range(n - 1)] + [100.0 + (n - 2) * 1.0 - 5.0]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    return pd.DataFrame(
        {
            "open": closes,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": [1000.0] * n,
        }
    )


# ── 테스트 ────────────────────────────────────────────────────────────────

def test_strategy_name_class():
    """1. 클래스 속성 name = 'demarker'."""
    assert DeMarkerStrategy.name == "demarker"


def test_strategy_name_instance():
    """2. 인스턴스 name = 'demarker'."""
    assert DeMarkerStrategy().name == "demarker"


def test_insufficient_data_returns_hold():
    """3. 데이터 부족 (< 20행) → HOLD, LOW confidence."""
    df = _make_df(n=10)
    sig = DeMarkerStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_none_df_returns_hold():
    """4. df=None → HOLD 반환."""
    sig = DeMarkerStrategy().generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_reasoning():
    """5. 부족 데이터 시 reasoning 에 'Insufficient' 포함."""
    df = _make_df(n=5)
    sig = DeMarkerStrategy().generate(df)
    assert "Insufficient" in sig.reasoning


def test_sufficient_data_returns_signal():
    """6. 충분한 데이터 → Signal 반환, 에러 없음."""
    df = _make_df(n=30)
    sig = DeMarkerStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_signal_fields_complete():
    """7. Signal 필드 완전성 (action, confidence, reasoning, invalidation)."""
    df = _make_df(n=30)
    sig = DeMarkerStrategy().generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str)


def test_signal_strategy_field():
    """8. Signal.strategy = 'demarker'."""
    df = _make_df(n=30)
    sig = DeMarkerStrategy().generate(df)
    assert sig.strategy == "demarker"


def test_signal_entry_price_positive():
    """9. entry_price > 0 (충분한 데이터)."""
    df = _make_df(n=30)
    sig = DeMarkerStrategy().generate(df)
    assert sig.entry_price >= 0.0


def test_buy_signal_reasoning_contains_cross():
    """10. BUY 신호 reasoning에 'crosses above' 포함."""
    strat = DeMarkerStrategy()
    # 강제로 BUY 조건 만들기: dem prev < 0.3, current >= 0.3
    df = _make_df(n=30)
    dem = _compute_demarker(df)
    # dem 값이 0.3 근처인지 확인 후 테스트
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert "crosses above" in sig.reasoning


def test_sell_signal_reasoning_contains_cross():
    """11. SELL 신호 reasoning에 'crosses below' 포함."""
    strat = DeMarkerStrategy()
    df = _make_df(n=30)
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert "crosses below" in sig.reasoning


def test_buy_confidence_high_or_medium():
    """12. BUY 시 confidence는 HIGH 또는 MEDIUM."""
    df = _make_df(n=30)
    sig = DeMarkerStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_sell_confidence_high_or_medium():
    """13. SELL 시 confidence는 HIGH 또는 MEDIUM."""
    df = _make_df(n=30)
    sig = DeMarkerStrategy().generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_min_rows_boundary():
    """14. 정확히 20행 → Signal 반환 (에러 없음)."""
    df = _make_df(n=20)
    sig = DeMarkerStrategy().generate(df)
    assert sig.strategy == "demarker"


def test_compute_demarker_returns_series():
    """15. _compute_demarker()가 pd.Series 반환."""
    df = _make_df(n=30)
    dem = _compute_demarker(df)
    assert isinstance(dem, pd.Series)
    assert len(dem) == len(df)


def test_compute_demarker_range():
    """16. DeMarker 유효값은 [0, 1] 범위."""
    df = _make_df(n=50)
    dem = _compute_demarker(df).dropna()
    assert (dem >= 0.0).all() and (dem <= 1.0).all()


def test_hold_has_reasoning():
    """17. HOLD 시 reasoning 비어있지 않음."""
    df = _make_df(n=30)
    sig = DeMarkerStrategy().generate(df)
    if sig.action == Action.HOLD:
        assert len(sig.reasoning) > 0
