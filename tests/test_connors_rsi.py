"""ConnorsRSIStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.connors_rsi import ConnorsRSIStrategy, _rsi, _compute_streak, _compute_crsi
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
            "ema50": closes,
            "atr14": [1.0] * n,
        }
    )


def _make_oversold_df(n: int = 130) -> pd.DataFrame:
    """CRSI < 20 구간 유도: 급락 후 완만 반등."""
    # 처음 n-5행은 급락, 마지막 5행은 약반등
    closes = [100.0 - i * 0.8 for i in range(n - 5)] + [
        100.0 - (n - 5) * 0.8 + i * 0.2 for i in range(5)
    ]
    return _make_df(close_values=closes)


def _make_overbought_df(n: int = 130) -> pd.DataFrame:
    """CRSI > 80 구간 유도: 급등 후 완만 하락."""
    closes = [100.0 + i * 0.8 for i in range(n - 5)] + [
        100.0 + (n - 5) * 0.8 - i * 0.2 for i in range(5)
    ]
    return _make_df(close_values=closes)


# ── 테스트 ────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 = 'connors_rsi'."""
    assert ConnorsRSIStrategy.name == "connors_rsi"
    assert ConnorsRSIStrategy().name == "connors_rsi"


def test_insufficient_data_returns_hold():
    """2. 데이터 부족 (< 110행) → HOLD, LOW confidence."""
    df = _make_df(n=50)
    sig = ConnorsRSIStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_sufficient_data_returns_signal():
    """3. 충분한 데이터로 Signal 반환, 에러 없음."""
    df = _make_df(n=130)
    sig = ConnorsRSIStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_signal_strategy_field():
    """4. Signal.strategy = 'connors_rsi'."""
    df = _make_df(n=130)
    sig = ConnorsRSIStrategy().generate(df)
    assert sig.strategy == "connors_rsi"


def test_signal_entry_price_is_float():
    """5. entry_price가 float."""
    df = _make_df(n=130)
    sig = ConnorsRSIStrategy().generate(df)
    assert isinstance(sig.entry_price, float)


def test_signal_fields_complete():
    """6. Signal 필드 완전성."""
    df = _make_df(n=130)
    sig = ConnorsRSIStrategy().generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert len(sig.reasoning) > 0


def test_rsi_helper_range():
    """7. _rsi() 결과가 [0, 100] 범위."""
    series = pd.Series([100.0 + np.sin(i) * 5 for i in range(50)])
    result = _rsi(series, 3).dropna()
    assert (result >= 0).all() and (result <= 100).all()


def test_compute_streak_up():
    """8. 연속 상승 시 streak 양수 누적."""
    close = np.array([10.0, 11.0, 12.0, 13.0, 14.0])
    streak = _compute_streak(close)
    assert streak[-1] == 4.0


def test_compute_streak_down():
    """9. 연속 하락 시 streak 음수 누적."""
    close = np.array([14.0, 13.0, 12.0, 11.0, 10.0])
    streak = _compute_streak(close)
    assert streak[-1] == -4.0


def test_compute_streak_reset():
    """10. 방향 전환 시 streak 리셋."""
    close = np.array([10.0, 11.0, 12.0, 11.0, 12.0])
    streak = _compute_streak(close)
    # 11 < 12 이후 12 > 11 → 새로운 streak = 1
    assert streak[-1] == 1.0


def test_compute_crsi_returns_series():
    """11. _compute_crsi()가 pd.Series 반환."""
    df = _make_df(n=130)
    crsi = _compute_crsi(df)
    assert isinstance(crsi, pd.Series)
    assert len(crsi) == len(df)


def test_crsi_range_valid():
    """12. CRSI 유효값은 [0, 100] 범위."""
    df = _make_df(n=130)
    crsi = _compute_crsi(df).dropna()
    assert (crsi >= 0).all() and (crsi <= 100).all()


def test_hold_action_has_reasoning():
    """13. HOLD 시 reasoning 비어있지 않음."""
    df = _make_df(n=130)  # 단조 상승 → 중간 CRSI 구간 → HOLD 가능
    sig = ConnorsRSIStrategy().generate(df)
    if sig.action == Action.HOLD:
        assert len(sig.reasoning) > 0


def test_buy_signal_confidence_levels():
    """14. BUY 신호 confidence는 HIGH 또는 MEDIUM."""
    df = _make_oversold_df()
    sig = ConnorsRSIStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_sell_signal_confidence_levels():
    """15. SELL 신호 confidence는 HIGH 또는 MEDIUM."""
    df = _make_overbought_df()
    sig = ConnorsRSIStrategy().generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_exact_min_rows_boundary():
    """16. 정확히 110행 → 에러 없이 Signal 반환."""
    df = _make_df(n=110)
    sig = ConnorsRSIStrategy().generate(df)
    assert sig.strategy == "connors_rsi"


def test_buy_signal_has_bull_case():
    """17. BUY 신호는 bull_case 필드 있음."""
    df = _make_oversold_df()
    sig = ConnorsRSIStrategy().generate(df)
    if sig.action == Action.BUY:
        assert isinstance(sig.bull_case, str)


def test_sell_signal_has_bear_case():
    """18. SELL 신호는 bear_case 필드 있음."""
    df = _make_overbought_df()
    sig = ConnorsRSIStrategy().generate(df)
    if sig.action == Action.SELL:
        assert isinstance(sig.bear_case, str)
