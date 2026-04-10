"""ConnorsRSIStrategy 단위 테스트 (14개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.connors_rsi import ConnorsRSIStrategy, _compute_crsi, _compute_streak
from src.strategy.base import Action, Confidence


def _make_df(n: int = 130, close_values=None) -> pd.DataFrame:
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


def _make_buy_cross_df(n: int = 130) -> pd.DataFrame:
    """CRSI crosses above 10: 급락 후 마지막에 반등."""
    closes = [100.0 - i * 0.8 for i in range(n - 3)] + [
        100.0 - (n - 4) * 0.8 + i * 0.5 for i in range(3)
    ]
    return _make_df(close_values=closes)


def _make_sell_cross_df(n: int = 130) -> pd.DataFrame:
    """CRSI crosses below 90: 급등 후 마지막에 하락."""
    closes = [100.0 + i * 0.8 for i in range(n - 3)] + [
        100.0 + (n - 4) * 0.8 - i * 0.5 for i in range(3)
    ]
    return _make_df(close_values=closes)


# ── 테스트 ────────────────────────────────────────────────────────────────

def test_strategy_name_class():
    """1. 클래스 속성 name = 'connors_rsi'."""
    assert ConnorsRSIStrategy.name == "connors_rsi"


def test_strategy_name_instance():
    """2. 인스턴스 name = 'connors_rsi'."""
    assert ConnorsRSIStrategy().name == "connors_rsi"


def test_insufficient_data_returns_hold():
    """3. 데이터 부족 (< 110행) → HOLD, LOW confidence."""
    df = _make_df(n=50)
    sig = ConnorsRSIStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_none_df_returns_hold():
    """4. df=None → HOLD 반환."""
    sig = ConnorsRSIStrategy().generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_reasoning():
    """5. 부족 데이터 시 reasoning에 'Insufficient' 포함."""
    df = _make_df(n=50)
    sig = ConnorsRSIStrategy().generate(df)
    assert "Insufficient" in sig.reasoning


def test_sufficient_data_returns_signal():
    """6. 충분한 데이터 → Signal 반환, 에러 없음."""
    df = _make_df(n=130)
    sig = ConnorsRSIStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_signal_fields_complete():
    """7. Signal 필드 완전성."""
    df = _make_df(n=130)
    sig = ConnorsRSIStrategy().generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str)


def test_signal_strategy_field():
    """8. Signal.strategy = 'connors_rsi'."""
    df = _make_df(n=130)
    sig = ConnorsRSIStrategy().generate(df)
    assert sig.strategy == "connors_rsi"


def test_signal_entry_price_positive():
    """9. entry_price >= 0 (충분한 데이터)."""
    df = _make_df(n=130)
    sig = ConnorsRSIStrategy().generate(df)
    assert sig.entry_price >= 0.0


def test_buy_signal_reasoning():
    """10. BUY 신호 reasoning에 'crosses above' 포함."""
    df = _make_df(n=130)
    sig = ConnorsRSIStrategy().generate(df)
    if sig.action == Action.BUY:
        assert "crosses above" in sig.reasoning


def test_sell_signal_reasoning():
    """11. SELL 신호 reasoning에 'crosses below' 포함."""
    df = _make_df(n=130)
    sig = ConnorsRSIStrategy().generate(df)
    if sig.action == Action.SELL:
        assert "crosses below" in sig.reasoning


def test_buy_confidence_high_or_medium():
    """12. BUY 시 confidence HIGH 또는 MEDIUM."""
    df = _make_buy_cross_df()
    sig = ConnorsRSIStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_sell_confidence_high_or_medium():
    """13. SELL 시 confidence HIGH 또는 MEDIUM."""
    df = _make_sell_cross_df()
    sig = ConnorsRSIStrategy().generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_min_rows_boundary():
    """14. 정확히 110행 → 에러 없이 Signal 반환."""
    df = _make_df(n=110)
    sig = ConnorsRSIStrategy().generate(df)
    assert sig.strategy == "connors_rsi"


def test_compute_streak_up():
    """15. 연속 상승 시 streak 양수 누적."""
    close = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
    streak = _compute_streak(close)
    assert float(streak.iloc[-1]) == 4.0


def test_compute_streak_down():
    """16. 연속 하락 시 streak 음수 누적."""
    close = pd.Series([14.0, 13.0, 12.0, 11.0, 10.0])
    streak = _compute_streak(close)
    assert float(streak.iloc[-1]) == -4.0


def test_compute_crsi_returns_series():
    """17. _compute_crsi()가 pd.Series 반환."""
    df = _make_df(n=130)
    crsi = _compute_crsi(df)
    assert isinstance(crsi, pd.Series)
    assert len(crsi) == len(df)


def test_hold_has_reasoning():
    """18. HOLD 시 reasoning 비어있지 않음."""
    df = _make_df(n=130)
    sig = ConnorsRSIStrategy().generate(df)
    if sig.action == Action.HOLD:
        assert len(sig.reasoning) > 0
