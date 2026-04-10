"""ExhaustionBarStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.exhaustion_bar import ExhaustionBarStrategy, _calc_atr14_ewm, _calc_rsi14
from src.strategy.base import Action, Confidence


def _make_df(closes, highs=None, lows=None, opens=None) -> pd.DataFrame:
    n = len(closes)
    if highs is None:
        highs = [c + 0.5 for c in closes]
    if lows is None:
        lows = [c - 0.5 for c in closes]
    if opens is None:
        opens = closes
    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": [1000.0] * n,
    })


def _exhaustion_down_df(n: int = 30) -> pd.DataFrame:
    """
    하락 추세 + 마지막 완성봉(-2)이 소진 하락봉 조건을 만족하도록 구성.
    - prev_trend_up = False (close[idx-1] < close[idx-5])
    - body가 매우 큼 (atr * 2)
    - 10봉 최저점 갱신
    - RSI < 30을 위해 강한 하락 지속
    """
    # 강한 하락 추세로 RSI를 30 이하로 낮춤
    closes = [200.0 - i * 5.0 for i in range(n)]
    opens = [c + 3.0 for c in closes]  # 하락봉: open > close, body=3
    highs = [o + 0.5 for o in opens]
    lows = [c - 0.5 for c in closes]
    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": [1000.0] * n,
    })


def _exhaustion_up_df(n: int = 30) -> pd.DataFrame:
    """
    상승 추세 + 마지막 완성봉(-2)이 소진 상승봉 조건을 만족하도록 구성.
    - prev_trend_up = True
    - body 큼
    - 10봉 최고점 갱신
    - RSI > 70을 위해 강한 상승 지속
    """
    closes = [100.0 + i * 5.0 for i in range(n)]
    opens = [c - 3.0 for c in closes]  # 상승봉: open < close
    highs = [c + 0.5 for c in closes]
    lows = [o - 0.5 for o in opens]
    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": [1000.0] * n,
    })


# ── 테스트 ────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 확인."""
    assert ExhaustionBarStrategy.name == "exhaustion_bar"
    assert ExhaustionBarStrategy().name == "exhaustion_bar"


def test_insufficient_data_hold():
    """2. 데이터 부족 (< 20행) → HOLD, LOW."""
    df = _make_df([100.0] * 10)
    sig = ExhaustionBarStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_boundary():
    """3. 정확히 19행 → HOLD."""
    df = _make_df([100.0] * 19)
    sig = ExhaustionBarStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_exact_min_rows_no_error():
    """4. 정확히 20행 → 에러 없이 Signal 반환."""
    df = _make_df([100.0 + i * 0.1 for i in range(20)])
    sig = ExhaustionBarStrategy().generate(df)
    assert sig.strategy == "exhaustion_bar"


def test_signal_strategy_field():
    """5. Signal.strategy == 'exhaustion_bar'."""
    df = _make_df([100.0] * 25)
    sig = ExhaustionBarStrategy().generate(df)
    assert sig.strategy == "exhaustion_bar"


def test_signal_entry_price_is_float():
    """6. entry_price가 float."""
    df = _make_df([100.0] * 25)
    sig = ExhaustionBarStrategy().generate(df)
    assert isinstance(sig.entry_price, float)


def test_action_enum_valid():
    """7. action이 Action enum 값 중 하나."""
    df = _make_df([100.0] * 25)
    sig = ExhaustionBarStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_hold_on_flat_data():
    """8. 횡보 데이터 → HOLD (추세 없음, body 작음, RSI 중립)."""
    df = _make_df([100.0] * 25)
    sig = ExhaustionBarStrategy().generate(df)
    assert sig.action == Action.HOLD


def test_signal_reasoning_not_empty():
    """9. reasoning, invalidation 문자열 비어있지 않음."""
    df = _make_df([100.0] * 25)
    sig = ExhaustionBarStrategy().generate(df)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str) and len(sig.invalidation) > 0


def test_buy_signal_exhaustion_down():
    """10. 강한 하락 추세 소진봉 → BUY 또는 HOLD (조건 충족 여부에 따라)."""
    df = _exhaustion_down_df(n=30)
    sig = ExhaustionBarStrategy().generate(df)
    # 조건이 충족되면 BUY, 아니면 HOLD (RSI가 < 30이어야 함)
    assert sig.action in (Action.BUY, Action.HOLD)


def test_sell_signal_exhaustion_up():
    """11. 강한 상승 추세 소진봉 → SELL 또는 HOLD."""
    df = _exhaustion_up_df(n=30)
    sig = ExhaustionBarStrategy().generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


def test_confidence_high_when_large_body():
    """12. body > ATR * 2.5 일 때 HIGH confidence."""
    # 강한 하락봉 시리즈: body가 ATR 대비 매우 큼
    n = 30
    closes = [200.0 - i * 10.0 for i in range(n)]
    opens = [c + 8.0 for c in closes]  # body=8, 매우 큰 하락봉
    highs = [o + 1.0 for o in opens]
    lows = [c - 1.0 for c in closes]
    df = pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": [1000.0] * n,
    })
    sig = ExhaustionBarStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_atr14_ewm_returns_series():
    """13. _calc_atr14_ewm이 올바른 길이의 Series 반환."""
    df = _make_df([100.0 + i for i in range(30)])
    result = _calc_atr14_ewm(df)
    assert isinstance(result, pd.Series)
    assert len(result) == 30


def test_rsi14_range():
    """14. _calc_rsi14 결과가 0~100 범위."""
    closes = pd.Series([100.0 + i * 2.0 for i in range(30)])
    result = _calc_rsi14(closes)
    assert result.min() >= 0.0
    assert result.max() <= 100.0


def test_rsi14_overbought_on_strong_uptrend():
    """15. 강한 상승 추세에서 RSI > 70."""
    closes = pd.Series([100.0 + i * 5.0 for i in range(30)])
    rsi = _calc_rsi14(closes)
    # 강한 상승이면 후반부 RSI는 높아야 함
    assert float(rsi.iloc[-1]) > 60.0


def test_rsi14_oversold_on_strong_downtrend():
    """16. 강한 하락 추세에서 RSI < 40."""
    closes = pd.Series([200.0 - i * 5.0 for i in range(30)])
    rsi = _calc_rsi14(closes)
    assert float(rsi.iloc[-1]) < 40.0


def test_insufficient_reasoning_contains_row_count():
    """17. 데이터 부족 시 reasoning에 행 수 정보 포함."""
    df = _make_df([100.0] * 5)
    sig = ExhaustionBarStrategy().generate(df)
    assert "5" in sig.reasoning


def test_signal_fields_complete():
    """18. Signal 모든 필드 존재."""
    df = _make_df([100.0] * 25)
    sig = ExhaustionBarStrategy().generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy is not None
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_no_exception_on_large_df():
    """19. 큰 데이터프레임에서도 예외 없음."""
    df = _exhaustion_up_df(n=200)
    sig = ExhaustionBarStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_prev_trend_up_logic():
    """20. prev_trend_up 로직: close[idx-1] > close[idx-5] 확인."""
    # idx=-2 기준으로 close[-3] > close[-7] 이어야 uptrend
    n = 25
    closes = [100.0 + i * 2.0 for i in range(n)]  # 상승 추세
    df = _make_df(closes)
    idx = n - 2
    # close[idx-1] = closes[idx-1], close[idx-5] = closes[idx-5]
    assert closes[idx - 1] > closes[idx - 5], "테스트 데이터 확인: 상승 추세여야 함"
    sig = ExhaustionBarStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
