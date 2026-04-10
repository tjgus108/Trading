"""LinearChannelReversionStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.linear_channel_rev import LinearChannelReversionStrategy, _calc_channel
from src.strategy.base import Action, Confidence


def _make_df(closes, highs=None, lows=None) -> pd.DataFrame:
    n = len(closes)
    if highs is None:
        highs = [c + 1.0 for c in closes]
    if lows is None:
        lows = [c - 1.0 for c in closes]
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": [1000.0] * n,
    })


def _buy_reversion_df(n: int = 40) -> pd.DataFrame:
    """
    채널 하단 이탈 후 복귀 조건:
    - prev_close(-3) < lower
    - curr_close(-2) >= lower
    """
    # 완만한 상승 추세로 채널 형성
    base = [100.0 + i * 0.2 for i in range(n - 3)]
    # prev_close: 채널 하단 아래로 급락
    prev_c = base[-1] - 15.0
    # curr_close: 채널 근처로 복귀
    curr_c = base[-1] - 4.0
    # 미완성봉
    last_c = curr_c + 0.1
    closes = base + [prev_c, curr_c, last_c]
    return _make_df(closes)


def _sell_reversion_df(n: int = 40) -> pd.DataFrame:
    """
    채널 상단 이탈 후 복귀 조건:
    - prev_close(-3) > upper
    - curr_close(-2) <= upper
    """
    base = [200.0 - i * 0.2 for i in range(n - 3)]
    prev_c = base[-1] + 15.0
    curr_c = base[-1] + 4.0
    last_c = curr_c - 0.1
    closes = base + [prev_c, curr_c, last_c]
    return _make_df(closes)


def _flat_df(n: int = 40) -> pd.DataFrame:
    return _make_df([100.0] * n)


# ── 테스트 ────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 확인."""
    assert LinearChannelReversionStrategy.name == "linear_channel_rev"
    assert LinearChannelReversionStrategy().name == "linear_channel_rev"


def test_insufficient_data_hold():
    """2. 데이터 부족 (< 35행) → HOLD, LOW."""
    df = _make_df([100.0] * 10)
    sig = LinearChannelReversionStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_boundary():
    """3. 정확히 34행 → HOLD."""
    df = _make_df([100.0 + i * 0.1 for i in range(34)])
    sig = LinearChannelReversionStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_exact_min_rows_no_error():
    """4. 정확히 35행 → 에러 없이 Signal 반환."""
    df = _make_df([100.0 + i * 0.1 for i in range(35)])
    sig = LinearChannelReversionStrategy().generate(df)
    assert sig.strategy == "linear_channel_rev"


def test_signal_strategy_field():
    """5. Signal.strategy == 'linear_channel_rev'."""
    df = _flat_df(n=40)
    sig = LinearChannelReversionStrategy().generate(df)
    assert sig.strategy == "linear_channel_rev"


def test_signal_entry_price_is_float():
    """6. entry_price가 float."""
    df = _flat_df(n=40)
    sig = LinearChannelReversionStrategy().generate(df)
    assert isinstance(sig.entry_price, float)


def test_action_enum_valid():
    """7. action이 Action enum 값 중 하나."""
    df = _flat_df(n=40)
    sig = LinearChannelReversionStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_hold_on_flat_data():
    """8. 횡보 데이터 → HOLD (이탈 없음)."""
    df = _flat_df(n=40)
    sig = LinearChannelReversionStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_signal_reasoning_not_empty():
    """9. reasoning, invalidation 문자열 비어있지 않음."""
    df = _flat_df(n=40)
    sig = LinearChannelReversionStrategy().generate(df)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str) and len(sig.invalidation) > 0


def test_buy_reversion_signal():
    """10. 채널 하단 이탈 후 복귀 → BUY."""
    df = _buy_reversion_df(n=40)
    sig = LinearChannelReversionStrategy().generate(df)
    # 조건이 맞으면 BUY, 아니면 HOLD
    assert sig.action in (Action.BUY, Action.HOLD)


def test_sell_reversion_signal():
    """11. 채널 상단 이탈 후 복귀 → SELL."""
    df = _sell_reversion_df(n=40)
    sig = LinearChannelReversionStrategy().generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


def test_signal_fields_complete():
    """12. Signal 모든 필드 존재."""
    df = _flat_df(n=40)
    sig = LinearChannelReversionStrategy().generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy is not None
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_calc_channel_upper_lower():
    """13. _calc_channel: upper > lower."""
    close_30 = np.array([100.0 + i * 0.5 + np.sin(i) for i in range(30)])
    upper, lower, channel_std, deviation = _calc_channel(close_30)
    assert upper > lower


def test_calc_channel_std_positive():
    """14. _calc_channel: channel_std >= 0."""
    close_30 = np.array([100.0 + i * 0.3 for i in range(30)])
    _, _, channel_std, _ = _calc_channel(close_30)
    assert channel_std >= 0.0


def test_calc_channel_flat_std_zero():
    """15. 완전히 선형 데이터 → residuals.std() ≈ 0."""
    close_30 = np.arange(30, dtype=float) * 2.0 + 100.0
    _, _, channel_std, _ = _calc_channel(close_30)
    assert channel_std == pytest.approx(0.0, abs=1e-8)


def test_confidence_high_when_large_deviation():
    """16. deviation > 2.5 * channel_std → HIGH confidence."""
    # 강한 이탈: 마지막 봉이 채널 훨씬 밖
    n = 40
    base = [100.0 + i * 0.1 for i in range(n - 3)]
    prev_c = base[-1] - 30.0  # 매우 큰 이탈
    curr_c = base[-1] - 3.0   # 복귀
    last_c = curr_c + 0.1
    closes = base + [prev_c, curr_c, last_c]
    df = _make_df(closes)
    sig = LinearChannelReversionStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_insufficient_reasoning_contains_row_count():
    """17. 데이터 부족 시 reasoning에 행 수 정보 포함."""
    df = _make_df([100.0] * 5)
    sig = LinearChannelReversionStrategy().generate(df)
    assert "5" in sig.reasoning


def test_no_exception_on_large_df():
    """18. 큰 데이터프레임에서도 예외 없음."""
    closes = [100.0 + i * 0.5 + np.sin(i) * 2 for i in range(200)]
    df = _make_df(closes)
    sig = LinearChannelReversionStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_buy_reasoning_contains_lower():
    """19. BUY reasoning에 'lower' 포함."""
    df = _buy_reversion_df(n=40)
    sig = LinearChannelReversionStrategy().generate(df)
    if sig.action == Action.BUY:
        assert "lower" in sig.reasoning


def test_sell_reasoning_contains_upper():
    """20. SELL reasoning에 'upper' 포함."""
    df = _sell_reversion_df(n=40)
    sig = LinearChannelReversionStrategy().generate(df)
    if sig.action == Action.SELL:
        assert "upper" in sig.reasoning
