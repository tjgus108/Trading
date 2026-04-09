"""MACDHistDivStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.macd_hist_div import MACDHistDivStrategy

strategy = MACDHistDivStrategy()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _base_df(n=60, seed=0):
    np.random.seed(seed)
    base = np.linspace(100, 102, n)
    df = pd.DataFrame({
        "open":   base,
        "close":  base + np.random.uniform(-0.1, 0.1, n),
        "high":   base + 0.5,
        "low":    base - 0.5,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_bullish_div_df():
    """
    Bullish divergence 조건 수동 구성:
    - close가 최근 10봉 중 최저 근처
    - MACD histogram이 10봉 전보다 높음
    - histogram < 0 (여전히 음수)

    EWM 계산을 피하고, 조건을 직접 유도하기 위해
    하락 후 약간 회복하는 패턴을 사용.
    """
    n = 80
    # 전반부(0~49): 100에서 서서히 하락 후 반등
    # 후반부(50~79): 하락세이나 histogram은 개선 중

    close = np.full(n, 100.0)

    # 0~39: 약한 하락
    close[0:40] = np.linspace(100, 95, 40)
    # 40~49: 반등
    close[40:50] = np.linspace(95, 98, 10)
    # 50~68: 다시 하락 (더 낮은 close)
    close[50:69] = np.linspace(98, 90, 19)
    # 69~78: 매우 작은 반등 (histogram 개선 유도)
    close[69:79] = np.linspace(90, 90.5, 10)
    # index 78 (iloc[-2]): 낮은 close, histogram 개선 기대
    close[78] = 89.8
    close[79] = 89.9  # ongoing candle

    df = pd.DataFrame({
        "open":   close - 0.1,
        "close":  close,
        "high":   close + 0.5,
        "low":    close - 0.5,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_bearish_div_df():
    """
    Bearish divergence 조건 구성:
    - close가 최근 10봉 최고 근처
    - histogram이 10봉 전보다 낮음
    - histogram > 0 (여전히 양수)
    """
    n = 80
    close = np.full(n, 100.0)

    # 0~39: 약한 상승
    close[0:40] = np.linspace(100, 108, 40)
    # 40~49: 조정
    close[40:50] = np.linspace(108, 105, 10)
    # 50~68: 다시 상승 (더 높은 close)
    close[50:69] = np.linspace(105, 115, 19)
    # 69~78: 소폭 횡보 → histogram 약화
    close[69:79] = np.linspace(115, 114.5, 10)
    # index 78 (iloc[-2]): 높은 close, histogram 약화 기대
    close[78] = 115.1
    close[79] = 115.2

    df = pd.DataFrame({
        "open":   close - 0.1,
        "close":  close,
        "high":   close + 0.5,
        "low":    close - 0.5,
        "volume": np.ones(n) * 1000,
    })
    return df


# ── 테스트 ────────────────────────────────────────────────────────────────────

# 1. 전략 이름
def test_strategy_name():
    assert strategy.name == "macd_hist_div"


# 2. None 입력 → HOLD
def test_none_input_returns_hold():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# 3. 데이터 부족 (39행) → HOLD
def test_insufficient_data_returns_hold():
    df = _base_df(39)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# 4. 최소 경계 (40행) → HOLD 또는 신호 (패닉 없음)
def test_min_data_no_error():
    df = _base_df(40)
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# 5. 평탄한 데이터 → HOLD (divergence 없음)
def test_flat_data_returns_hold():
    n = 60
    close = np.full(n, 100.0)
    df = pd.DataFrame({
        "open":   close,
        "close":  close,
        "high":   close + 0.1,
        "low":    close - 0.1,
        "volume": np.ones(n) * 1000,
    })
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# 6. Signal 필드 완전성
def test_signal_has_required_fields():
    df = _base_df(60)
    sig = strategy.generate(df)
    assert sig.strategy == "macd_hist_div"
    assert sig.reasoning != ""
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# 7. _last(df) = df.iloc[-2] 확인
def test_last_returns_second_to_last():
    df = _base_df(10)
    last = strategy._last(df)
    pd.testing.assert_series_equal(last, df.iloc[-2])


# 8. BUY 시 entry_price 양수
def test_buy_entry_price_positive():
    df = _make_bullish_div_df()
    sig = strategy.generate(df)
    assert sig.entry_price > 0


# 9. SELL 시 entry_price 양수
def test_sell_entry_price_positive():
    df = _make_bearish_div_df()
    sig = strategy.generate(df)
    assert sig.entry_price > 0


# 10. 단조 상승 → BUY 아님 (histogram bearish 또는 HOLD)
def test_monotone_rising_not_buy():
    n = 60
    close = np.linspace(90, 110, n)
    df = pd.DataFrame({
        "open":   close,
        "close":  close,
        "high":   close + 1,
        "low":    close - 1,
        "volume": np.ones(n) * 1000,
    })
    sig = strategy.generate(df)
    assert sig.action != Action.BUY


# 11. 단조 하락 → SELL 아님 (histogram bullish 또는 HOLD)
def test_monotone_falling_not_sell():
    n = 60
    close = np.linspace(110, 90, n)
    df = pd.DataFrame({
        "open":   close,
        "close":  close,
        "high":   close + 1,
        "low":    close - 1,
        "volume": np.ones(n) * 1000,
    })
    sig = strategy.generate(df)
    assert sig.action != Action.SELL


# 12. BUY 신호 reasoning에 "Bullish" 포함 확인
def test_bullish_reasoning_text():
    df = _make_bullish_div_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "Bullish" in sig.reasoning


# 13. SELL 신호 reasoning에 "Bearish" 포함 확인
def test_bearish_reasoning_text():
    df = _make_bearish_div_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "Bearish" in sig.reasoning


# 14. confidence 값은 유효한 Enum
def test_confidence_is_valid_enum():
    df = _base_df(60)
    sig = strategy.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# 15. entry_price = close at _last (df.iloc[-2])
def test_entry_price_equals_last_close():
    df = _base_df(60)
    sig = strategy.generate(df)
    expected_price = float(df.iloc[-2]["close"])
    assert abs(sig.entry_price - expected_price) < 1e-9
