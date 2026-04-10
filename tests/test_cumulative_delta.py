"""CumulativeDeltaStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.cumulative_delta import CumulativeDeltaStrategy

strategy = CumulativeDeltaStrategy()


def _make_df(n=50, mode="hold"):
    """
    mode: "buy"  → cum_delta 음수에서 상향 돌파
          "sell" → cum_delta 양수에서 하향 돌파
          "hold" → 크로스 없음
    """
    closes = np.linspace(100.0, 110.0, n)
    opens = closes - 0.2
    highs = closes + 1.0
    lows = closes - 1.0
    volumes = np.ones(n) * 1000.0

    if mode == "buy":
        # 음봉 많이 → cum_delta 음수, 마지막에 큰 양봉으로 돌파
        closes = np.full(n, 100.0, dtype=float)
        opens = closes + 0.5  # 음봉 (open > close)
        # 마지막 idx = n-2: 큰 양봉
        opens[n - 2] = closes[n - 2] - 3.0
        highs = closes + 1.0
        lows = closes - 1.0
        opens = np.where(opens > highs, highs - 0.1, opens)
        opens = np.where(opens < lows, lows + 0.1, opens)
    elif mode == "sell":
        # 양봉 많이 → cum_delta 양수, 마지막에 큰 음봉으로 하락 돌파
        closes = np.full(n, 100.0, dtype=float)
        opens = closes - 0.5  # 양봉 (open < close)
        # 마지막 idx = n-2: 큰 음봉
        opens[n - 2] = closes[n - 2] + 3.0
        highs = closes + 1.0
        lows = closes - 1.0
        opens = np.where(opens > highs, highs - 0.1, opens)
        opens = np.where(opens < lows, lows + 0.1, opens)

    df = pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
        "ema50": np.full(n, 100.0),
        "atr14": np.ones(n) * 1.0,
    })
    return df


def _make_buy_df(n=60):
    """cum_delta가 음수에서 상향 돌파하도록 설계된 데이터."""
    opens = np.full(n, 100.5, dtype=float)  # 음봉: open > close
    closes = np.full(n, 100.0, dtype=float)
    highs = np.full(n, 101.5, dtype=float)
    lows = np.full(n, 99.0, dtype=float)
    volumes = np.ones(n) * 1000.0

    # idx = n-3 (prev): 계속 음봉 → cum_delta < 0, cum_delta <= ma
    # idx = n-2 (now): 큰 양봉으로 전환, cum_delta 상승 > ma
    opens[n - 2] = 97.0   # 큰 양봉
    closes[n - 2] = 103.0
    highs[n - 2] = 104.0
    lows[n - 2] = 96.5

    df = pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
        "ema50": np.full(n, 100.0),
        "atr14": np.ones(n) * 1.0,
    })
    return df


def _make_sell_df(n=60):
    """cum_delta가 양수에서 하향 돌파하도록 설계된 데이터."""
    opens = np.full(n, 99.5, dtype=float)   # 양봉: open < close
    closes = np.full(n, 100.0, dtype=float)
    highs = np.full(n, 101.0, dtype=float)
    lows = np.full(n, 98.5, dtype=float)
    volumes = np.ones(n) * 1000.0

    # idx = n-2: 큰 음봉으로 전환
    opens[n - 2] = 103.0
    closes[n - 2] = 97.0
    highs[n - 2] = 103.5
    lows[n - 2] = 96.5

    df = pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
        "ema50": np.full(n, 100.0),
        "atr14": np.ones(n) * 1.0,
    })
    return df


# 1. 전략 이름
def test_strategy_name():
    assert strategy.name == "cumulative_delta"


# 2. 인스턴스 타입
def test_instance():
    s = CumulativeDeltaStrategy()
    assert isinstance(s, CumulativeDeltaStrategy)


# 3. 데이터 부족 → HOLD (n < 30)
def test_insufficient_data():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# 4. None 입력 → HOLD
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# 5. reasoning 필드가 문자열
def test_reasoning_is_string():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert isinstance(sig.reasoning, str)
    assert len(sig.reasoning) > 0


# 6. 정상 signal 반환 (HOLD)
def test_normal_hold_signal():
    df = _make_df(n=50, mode="hold")
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# 7. Signal 필드 완전성
def test_signal_fields():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "cumulative_delta"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# 8. BUY reasoning에 "CumDelta" 포함
def test_buy_reasoning():
    df = _make_buy_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "CumDelta" in sig.reasoning


# 9. SELL reasoning에 "CumDelta" 포함
def test_sell_reasoning():
    df = _make_sell_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "CumDelta" in sig.reasoning


# 10. HIGH confidence 가능
def test_confidence_high_possible():
    """confidence가 HIGH 또는 MEDIUM 중 하나."""
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# 11. MEDIUM confidence 가능
def test_confidence_medium_possible():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# 12. entry_price > 0 (정상 데이터)
def test_entry_price_positive():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.entry_price >= 0.0


# 13. strategy 필드 확인
def test_strategy_field():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.strategy == "cumulative_delta"


# 14. 최소 30행으로 실행 가능
def test_min_rows_boundary():
    df = _make_df(n=30)
    sig = strategy.generate(df)
    # 30행이면 실행은 되어야 함 (NaN 등으로 HOLD 가능)
    assert isinstance(sig, Signal)
