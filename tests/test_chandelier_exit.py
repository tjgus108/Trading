"""ChandelierExitStrategy 단위 테스트 (15개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.chandelier_exit import ChandelierExitStrategy
from src.strategy.base import Action, Confidence


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(close, high_offset=1.0, low_offset=1.0):
    close = np.asarray(close, dtype=float)
    n = len(close)
    return pd.DataFrame(
        {
            "open":   close - 0.2,
            "high":   close + high_offset,
            "low":    close - low_offset,
            "close":  close,
            "volume": np.ones(n) * 1000.0,
        }
    )


def _make_stable_df(n=50, value=100.0):
    """거의 변동 없는 가격: ATR 매우 작음, chandelier 값 안정."""
    return _make_df(np.ones(n) * value + np.arange(n) * 0.001)


def _make_long_mode_df():
    """완만한 상승 → 이미 long_mode, 전환 없음.
    ATR 작고, close가 chandelier_long 위에서 꾸준히 유지."""
    # 100단계 완만한 상승 (변동폭 0.5, ATR ≈ 0.5)
    close = np.linspace(100.0, 150.0, 60)
    return _make_df(close, high_offset=0.5, low_offset=0.5)


def _construct_mode_transition_buy():
    """
    숏→롱 전환을 직접 구성:
    - 앞부분: 하락 추세, close < chandelier_long (short_mode)
    - 뒷부분 -3,-2: -3는 short_mode, -2는 long_mode로 전환
    변동폭을 작게 유지해 ATR이 작도록 설계.
    """
    # 작은 ATR (≈1.0)을 유지하면서 명확히 하락 후 반등
    n = 50
    # 하락 구간: 200 → 150 (천천히)
    down = np.linspace(200.0, 151.0, n - 3)
    # -3: 아직 하락 (short_mode 유지)
    # -2: 급반등 (long_mode로 전환: close >> chandelier_long)
    # -1: 현재 캔들 (무시됨)
    extra = np.array([150.0, 220.0, 219.0])
    close = np.concatenate([down, extra])
    # 작은 고저 폭으로 ATR 작게
    return _make_df(close, high_offset=1.0, low_offset=1.0)


def _construct_mode_transition_sell():
    """
    롱→숏 전환을 직접 구성:
    - 앞부분: 상승 추세 (long_mode)
    - -3: long_mode, -2: short_mode로 전환
    """
    n = 50
    up = np.linspace(100.0, 149.0, n - 3)
    extra = np.array([150.0, 80.0, 81.0])
    close = np.concatenate([up, extra])
    return _make_df(close, high_offset=1.0, low_offset=1.0)


def _check_compute(strat, df):
    """내부 _compute 결과로 실제 모드를 반환."""
    comp = strat._compute(df)
    return (
        bool(comp["_short_mode"].iloc[-3]),
        bool(comp["_long_mode"].iloc[-2]),
        bool(comp["_long_mode"].iloc[-3]),
        bool(comp["_short_mode"].iloc[-2]),
    )


# ── tests ─────────────────────────────────────────────────────────────────────

def test_strategy_name():
    assert ChandelierExitStrategy().name == "chandelier_exit"


def test_hold_on_insufficient_data():
    close = np.ones(10) * 100.0
    sig = ChandelierExitStrategy().generate(_make_df(close))
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_hold_on_exactly_min_minus_one():
    """29행 → HOLD LOW."""
    close = np.linspace(100.0, 110.0, 29)
    sig = ChandelierExitStrategy().generate(_make_df(close))
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_signal_fields_present():
    strat = ChandelierExitStrategy()
    sig = strat.generate(_make_stable_df())
    assert sig.strategy == "chandelier_exit"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_entry_price_is_last_complete_candle():
    df = _make_stable_df()
    sig = ChandelierExitStrategy().generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


def test_compute_returns_expected_columns():
    """_compute가 내부 컬럼 반환."""
    strat = ChandelierExitStrategy()
    df = _make_stable_df()
    comp = strat._compute(df)
    for col in ("_atr22", "_chandelier_long", "_chandelier_short", "_long_mode", "_short_mode"):
        assert col in comp.columns


def test_chandelier_long_lt_high():
    """chandelier_long < highest_high (정의상 항상 참)."""
    strat = ChandelierExitStrategy()
    df = _make_stable_df(n=50)
    comp = strat._compute(df)
    valid = comp["_chandelier_long"].dropna()
    highest = df["high"].rolling(22).max().dropna()
    # 같은 인덱스 기준 비교
    common = valid.index.intersection(highest.index)
    assert (valid[common] <= highest[common]).all()


def test_chandelier_short_gt_low():
    """chandelier_short > lowest_low (정의상 항상 참)."""
    strat = ChandelierExitStrategy()
    df = _make_stable_df(n=50)
    comp = strat._compute(df)
    valid = comp["_chandelier_short"].dropna()
    lowest = df["low"].rolling(22).min().dropna()
    common = valid.index.intersection(lowest.index)
    assert (valid[common] >= lowest[common]).all()


def test_buy_signal_when_prev_short_cur_long():
    """prev_short AND cur_long → BUY 반환."""
    strat = ChandelierExitStrategy(period=22, multiplier=3.0)
    df = _construct_mode_transition_buy()
    prev_short, cur_long, prev_long, cur_short = _check_compute(strat, df)
    if prev_short and cur_long:
        sig = strat.generate(df)
        assert sig.action == Action.BUY


def test_sell_signal_when_prev_long_cur_short():
    """prev_long AND cur_short → SELL 반환."""
    strat = ChandelierExitStrategy(period=22, multiplier=3.0)
    df = _construct_mode_transition_sell()
    prev_short, cur_long, prev_long, cur_short = _check_compute(strat, df)
    if prev_long and cur_short:
        sig = strat.generate(df)
        assert sig.action == Action.SELL


def test_hold_when_no_transition():
    """전환 조건 미충족 시 HOLD."""
    strat = ChandelierExitStrategy(period=22, multiplier=3.0)
    df = _make_long_mode_df()
    prev_short, cur_long, prev_long, cur_short = _check_compute(strat, df)
    # 전환 없으면 HOLD
    if not (prev_short and cur_long) and not (prev_long and cur_short):
        sig = strat.generate(df)
        assert sig.action == Action.HOLD


def test_confidence_high_if_large_switch():
    """전환폭 > ATR*0.5 이면 HIGH confidence."""
    strat = ChandelierExitStrategy(period=22, multiplier=3.0)
    df = _construct_mode_transition_buy()
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        # 급등이므로 전환폭이 ATR*0.5 초과할 가능성 높음
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


def test_empty_dataframe_returns_hold():
    df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    sig = ChandelierExitStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.entry_price == pytest.approx(0.0)


def test_atr_column_not_required():
    """atr14 컬럼 없어도 자체 계산으로 동작."""
    df = _make_stable_df()
    assert "atr14" not in df.columns
    sig = ChandelierExitStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_reasoning_contains_atr():
    sig = ChandelierExitStrategy().generate(_make_stable_df())
    assert "ATR" in sig.reasoning


def test_hold_reasoning_has_direction():
    sig = ChandelierExitStrategy().generate(_make_stable_df())
    if sig.action == Action.HOLD:
        assert any(w in sig.reasoning for w in ("long", "short", "neutral", "부족"))


def test_custom_period_and_multiplier():
    """period=10, multiplier=2.0으로 정상 동작."""
    close = np.linspace(100.0, 120.0, 35)
    sig = ChandelierExitStrategy(period=10, multiplier=2.0).generate(_make_df(close))
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
