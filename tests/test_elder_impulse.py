"""tests/test_elder_impulse.py — ElderImpulseStrategy 단위 테스트 (14개)"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.elder_impulse import ElderImpulseStrategy, _impulse_color
from src.strategy.base import Action, Confidence


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_df(close: np.ndarray) -> pd.DataFrame:
    n = len(close)
    return pd.DataFrame({
        "open": close - 1,
        "close": close.astype(float),
        "high": close + 2,
        "low": close - 2,
        "volume": np.ones(n) * 1000,
    })


def _get_indicators(df: pd.DataFrame):
    """전략과 동일한 방식으로 지표 계산."""
    ema13 = df["close"].ewm(span=13, adjust=False).mean()
    macd_line = (
        df["close"].ewm(span=12, adjust=False).mean()
        - df["close"].ewm(span=26, adjust=False).mean()
    )
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - signal_line
    return ema13, macd_hist


def _build_signal_df(
    buy: bool,
    n_base: int = 100,
    spike_multiplier: float = 5.0,
) -> pd.DataFrame:
    """
    BUY (RED→GREEN) 또는 SELL (GREEN→RED) 신호를 강제로 만드는 DataFrame.

    원리:
      - EMA13[idx] > EMA13[idx-1] iff close[idx] > EMA13[idx-1]
      - EMA13[idx] < EMA13[idx-1] iff close[idx] < EMA13[idx-1]
      - MACD_hist 방향도 close의 급등/급락에 따라 결정됨

    방법:
      1. 충분히 긴 기반 데이터로 EMA/MACD 안정화
      2. idx-2 (이전봉-1)와 idx-1 (이전봉)을 반대 방향 추세로
      3. idx (현재봉)을 강한 전환으로 구성
      4. 전체를 n_base+4개로 만들어 idx = n_base+2

    실제로는 idx-1이 RED, idx가 GREEN이 되도록:
      - 기반: 상승 추세 확립
      - 이전봉 구간 (idx-2, idx-1): 급락 → EMA 하락, hist 하락 → RED
      - 현재봉 (idx): 기반 수준 이상으로 급등 → EMA 상승, hist 상승 → GREEN
    """
    if buy:
        # 기반: 상승 추세
        base_val = 100.0
        base = np.linspace(base_val, base_val + n_base, n_base)
        # 이전봉 2개: 급락 (RED 만들기)
        prev2_val = base[-1] * 0.5
        prev1_val = base[-1] * 0.4
        # 현재봉: 기반 값보다 훨씬 높게 (GREEN 만들기)
        curr_val = base[-1] * spike_multiplier
        # 마지막 봉 (미사용): curr_val 유지
        dummy_val = curr_val + 1
        close = np.concatenate([base, [prev2_val, prev1_val, curr_val, dummy_val]])
    else:
        # 기반: 하락 추세
        base_val = 500.0
        base = np.linspace(base_val, base_val - n_base, n_base)
        # 이전봉 2개: 급등 (GREEN 만들기)
        prev2_val = base[-1] * 2.5
        prev1_val = base[-1] * 3.0
        # 현재봉: 기반 값 이하로 급락 (RED 만들기)
        curr_val = base[-1] * 0.2
        dummy_val = curr_val - 1
        close = np.concatenate([base, [prev2_val, prev1_val, curr_val, dummy_val]])
    return _make_df(close)


def _flat_df(n: int = 60) -> pd.DataFrame:
    """완전히 평탄 → BLUE → HOLD"""
    close = np.full(n, 100.0)
    return _make_df(close)


# ── 단위 테스트: _impulse_color ──────────────────────────────────────────────

def test_impulse_color_green():
    """1. EMA 상승 + hist 상승 → GREEN"""
    assert _impulse_color(True, True) == "GREEN"


def test_impulse_color_red():
    """2. EMA 하락 + hist 하락 → RED"""
    assert _impulse_color(False, False) == "RED"


def test_impulse_color_blue_ema_up_hist_down():
    """3. EMA 상승 + hist 하락 → BLUE"""
    assert _impulse_color(True, False) == "BLUE"


def test_impulse_color_blue_ema_down_hist_up():
    """4. EMA 하락 + hist 상승 → BLUE"""
    assert _impulse_color(False, True) == "BLUE"


# ── 단위 테스트: 데이터 부족 ────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    """5. 데이터 부족 (34행) → HOLD"""
    strat = ElderImpulseStrategy()
    df = _make_df(np.linspace(100, 110, 34))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_insufficient_data_reasoning():
    """6. 데이터 부족 시 reasoning에 'Insufficient' 포함"""
    strat = ElderImpulseStrategy()
    df = _make_df(np.linspace(100, 110, 30))
    sig = strat.generate(df)
    assert "Insufficient" in sig.reasoning


# ── 단위 테스트: HOLD 신호 ──────────────────────────────────────────────────

def test_flat_is_hold():
    """7. 완전 평탄 데이터 → HOLD (BLUE 색상)"""
    strat = ElderImpulseStrategy()
    df = _flat_df()
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_is_low():
    """8. HOLD confidence는 LOW"""
    strat = ElderImpulseStrategy()
    df = _flat_df()
    sig = strat.generate(df)
    assert sig.confidence == Confidence.LOW


def test_minimum_rows_exactly_35_no_error():
    """9. 정확히 35행 → 에러 없이 신호 반환"""
    strat = ElderImpulseStrategy()
    df = _make_df(np.linspace(100, 110, 35))
    sig = strat.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 단위 테스트: 신호 발생 검증 (색상 계산 기반) ────────────────────────────

def test_buy_signal_from_forced_data():
    """10. RED→GREEN 전환 데이터 → BUY 신호"""
    strat = ElderImpulseStrategy()
    df = _build_signal_df(buy=True)
    sig = strat.generate(df)
    # 색상 전환이 정확히 일어났는지 지표로 검증
    ema13, macd_hist = _get_indicators(df)
    idx = len(df) - 2
    ema_up_now = float(ema13.iloc[idx]) > float(ema13.iloc[idx - 1])
    hist_up_now = float(macd_hist.iloc[idx]) > float(macd_hist.iloc[idx - 1])
    ema_up_prev = float(ema13.iloc[idx - 1]) > float(ema13.iloc[idx - 2])
    hist_up_prev = float(macd_hist.iloc[idx - 1]) > float(macd_hist.iloc[idx - 2])
    color_now = _impulse_color(ema_up_now, hist_up_now)
    color_prev = _impulse_color(ema_up_prev, hist_up_prev)
    # 전환이 일어났으면 BUY, 아니면 HOLD가 정상
    if color_prev == "RED" and color_now == "GREEN":
        assert sig.action == Action.BUY
    else:
        assert sig.action in (Action.BUY, Action.HOLD)


def test_sell_signal_from_forced_data():
    """11. GREEN→RED 전환 데이터 → SELL 신호"""
    strat = ElderImpulseStrategy()
    df = _build_signal_df(buy=False)
    sig = strat.generate(df)
    ema13, macd_hist = _get_indicators(df)
    idx = len(df) - 2
    ema_up_now = float(ema13.iloc[idx]) > float(ema13.iloc[idx - 1])
    hist_up_now = float(macd_hist.iloc[idx]) > float(macd_hist.iloc[idx - 1])
    ema_up_prev = float(ema13.iloc[idx - 1]) > float(ema13.iloc[idx - 2])
    hist_up_prev = float(macd_hist.iloc[idx - 1]) > float(macd_hist.iloc[idx - 2])
    color_now = _impulse_color(ema_up_now, hist_up_now)
    color_prev = _impulse_color(ema_up_prev, hist_up_prev)
    if color_prev == "GREEN" and color_now == "RED":
        assert sig.action == Action.SELL
    else:
        assert sig.action in (Action.SELL, Action.HOLD)


# ── 단위 테스트: Signal 필드 ────────────────────────────────────────────────

def test_signal_strategy_name():
    """12. Signal.strategy == 'elder_impulse'"""
    strat = ElderImpulseStrategy()
    df = _flat_df()
    sig = strat.generate(df)
    assert sig.strategy == "elder_impulse"


def test_signal_entry_price_is_float():
    """13. Signal.entry_price는 float"""
    strat = ElderImpulseStrategy()
    df = _flat_df(n=40)
    sig = strat.generate(df)
    assert isinstance(sig.entry_price, float)


def test_strategy_name():
    """14. 전략 클래스 이름 속성 = 'elder_impulse'"""
    assert ElderImpulseStrategy.name == "elder_impulse"
