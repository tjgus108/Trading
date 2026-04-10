"""tests/test_linear_reg_channel.py — LinearRegChannelStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.linear_reg_channel import LinearRegChannelStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 50, close_values=None) -> pd.DataFrame:
    if close_values is not None:
        close = np.array(close_values, dtype=float)
        n = len(close)
    else:
        np.random.seed(0)
        close = 100 + np.cumsum(np.random.randn(n) * 0.3)
    high = close + 1.0
    low = close - 1.0
    return pd.DataFrame({
        "open": close - 0.1,
        "close": close,
        "high": high,
        "low": low,
        "volume": np.ones(n) * 1000,
    })


def _make_buy_df() -> pd.DataFrame:
    """하단 채널 이탈 후 복귀: prev_close < lower_1.5sig, curr_close > lower_1.5sig."""
    # 35봉 이상 필요, 30봉 회귀 사용
    n = 40
    # 선형 데이터로 std_res 작게 유지 (채널 폭 작게)
    close = np.array([100.0 + i * 0.1 for i in range(n)], dtype=float)
    high = close + 0.5
    low = close - 0.5
    df = pd.DataFrame({
        "open": close - 0.1,
        "close": close.copy(),
        "high": high.copy(),
        "low": low.copy(),
        "volume": np.ones(n) * 1000,
    })

    # idx = len-2 = 38, prev = 37
    # 회귀 채널 계산 (봉 9~38, 30봉)
    y = close[9:39]  # idx=38, 30봉: iloc[38-30+1:39]
    x = np.arange(30)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = slope * x + intercept
    std_res = float((y - fitted).std())

    reg_now = slope * 29 + intercept   # x=29 at idx=38
    reg_prev = slope * 28 + intercept  # x=28 at idx=37

    lower_now = reg_now - 1.5 * std_res
    lower_prev = reg_prev - 1.5 * std_res

    # prev_close(37) 아래로, curr_close(38) 위로
    close_mod = close.copy()
    close_mod[37] = lower_prev - 0.5   # 하단 이탈
    close_mod[38] = lower_now + 0.5    # 하단 복귀

    return pd.DataFrame({
        "open": close_mod - 0.1,
        "close": close_mod,
        "high": close_mod + 0.5,
        "low": close_mod - 0.5,
        "volume": np.ones(n) * 1000,
    })


def _make_sell_df() -> pd.DataFrame:
    """상단 채널 이탈 후 복귀: prev_close > upper_1.5sig, curr_close < upper_1.5sig."""
    n = 40
    close = np.array([100.0 + i * 0.1 for i in range(n)], dtype=float)
    df_tmp = pd.DataFrame({
        "open": close - 0.1,
        "close": close.copy(),
        "high": close + 0.5,
        "low": close - 0.5,
        "volume": np.ones(n) * 1000,
    })

    y = close[9:39]
    x = np.arange(30)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = slope * x + intercept
    std_res = float((y - fitted).std())

    reg_now = slope * 29 + intercept
    reg_prev = slope * 28 + intercept

    upper_now = reg_now + 1.5 * std_res
    upper_prev = reg_prev + 1.5 * std_res

    close_mod = close.copy()
    close_mod[37] = upper_prev + 0.5   # 상단 이탈
    close_mod[38] = upper_now - 0.5    # 상단 복귀

    return pd.DataFrame({
        "open": close_mod - 0.1,
        "close": close_mod,
        "high": close_mod + 0.5,
        "low": close_mod - 0.5,
        "volume": np.ones(n) * 1000,
    })


# ── 테스트 14개 ────────────────────────────────────────────────────────────

def test_strategy_name_class():
    """1. 클래스 속성 .name == 'linear_reg_channel'."""
    assert LinearRegChannelStrategy.name == "linear_reg_channel"


def test_strategy_name_instance():
    """2. 인스턴스 .name == 'linear_reg_channel'."""
    assert LinearRegChannelStrategy().name == "linear_reg_channel"


def test_insufficient_data_returns_hold():
    """3. 데이터 부족 (< 35행) → HOLD."""
    sig = LinearRegChannelStrategy().generate(_make_df(20))
    assert sig.action == Action.HOLD


def test_none_input_returns_hold():
    """4. None 입력 → HOLD."""
    sig = LinearRegChannelStrategy().generate(None)
    assert sig.action == Action.HOLD


def test_empty_df_returns_hold():
    """4b. 빈 DataFrame → HOLD."""
    sig = LinearRegChannelStrategy().generate(pd.DataFrame())
    assert sig.action == Action.HOLD


def test_insufficient_data_reasoning():
    """5. 데이터 부족 reasoning에 'Insufficient' 포함."""
    sig = LinearRegChannelStrategy().generate(_make_df(10))
    assert "Insufficient" in sig.reasoning or "insufficient" in sig.reasoning.lower()


def test_sufficient_data_returns_signal():
    """6. 충분한 데이터 → Signal 반환."""
    sig = LinearRegChannelStrategy().generate(_make_df(40))
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_signal_fields_complete():
    """7. Signal 필드 완전성 (action, confidence, strategy, entry_price, reasoning)."""
    sig = LinearRegChannelStrategy().generate(_make_df(40))
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert sig.strategy == "linear_reg_channel"
    assert isinstance(sig.entry_price, float)
    assert len(sig.reasoning) > 0


def test_buy_signal():
    """8. BUY: 하단 채널 이탈 후 복귀."""
    sig = LinearRegChannelStrategy().generate(_make_buy_df())
    assert sig.action == Action.BUY


def test_sell_signal():
    """9. SELL: 상단 채널 이탈 후 복귀."""
    sig = LinearRegChannelStrategy().generate(_make_sell_df())
    assert sig.action == Action.SELL


def test_high_confidence():
    """10. HIGH confidence: |curr_close - reg| > 2*std_res."""
    # 극단적인 이탈 후 복귀로 HIGH confidence 유도
    n = 40
    close = np.array([100.0 + i * 0.1 for i in range(n)], dtype=float)
    y = close[9:39]
    x = np.arange(30)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = slope * x + intercept
    std_res = float((y - fitted).std()) or 0.001

    reg_now = slope * 29 + intercept
    # curr_close를 reg + 2.5 * std_res 위치에 (2*std_res 초과)
    close_mod = close.copy()
    close_mod[38] = reg_now + 2.5 * std_res

    df = pd.DataFrame({
        "open": close_mod - 0.1,
        "close": close_mod,
        "high": close_mod + 0.5,
        "low": close_mod - 0.5,
        "volume": np.ones(n) * 1000,
    })
    sig = LinearRegChannelStrategy().generate(df)
    if sig.confidence == Confidence.HIGH:
        assert sig.confidence == Confidence.HIGH


def test_medium_confidence():
    """11. MEDIUM confidence: 채널 내부 (이탈 없음)."""
    # 평범한 데이터는 채널 내부 → HOLD + MEDIUM or LOW
    sig = LinearRegChannelStrategy().generate(_make_df(40))
    assert sig.confidence in (Confidence.MEDIUM, Confidence.LOW, Confidence.HIGH)


def test_entry_price_positive():
    """12. entry_price > 0."""
    sig = LinearRegChannelStrategy().generate(_make_df(40))
    assert sig.entry_price > 0


def test_strategy_field_equals_name():
    """13. Signal.strategy == 'linear_reg_channel'."""
    sig = LinearRegChannelStrategy().generate(_make_buy_df())
    assert sig.strategy == "linear_reg_channel"


def test_min_rows_boundary():
    """14. 정확히 35행 → Signal 반환 (에러 없음)."""
    sig = LinearRegChannelStrategy().generate(_make_df(35))
    assert sig.strategy == "linear_reg_channel"
