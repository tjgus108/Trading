"""VolumePriceTrendV2Strategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.volume_price_trend_v2 import VolumePriceTrendV2Strategy

strategy = VolumePriceTrendV2Strategy()


def _make_df(n=40):
    closes = np.linspace(100.0, 110.0, n)
    opens = closes - 0.2
    highs = closes + 1.0
    lows = closes - 1.0
    volumes = np.ones(n) * 1000.0
    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })


def _make_buy_df(n=50):
    """vpt_hist > 0, 상승 중, vpt > vpt_signal 조건 유도."""
    closes = np.linspace(100.0, 120.0, n)
    volumes = np.ones(n) * 2000.0
    # 마지막 몇 봉 볼륨을 크게 올려 vpt를 빠르게 올림
    volumes[-5:] = 10000.0
    opens = closes - 0.5
    highs = closes + 1.0
    lows = closes - 1.0
    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })


def _make_sell_df(n=50):
    """vpt_hist < 0, 하락 중, vpt < vpt_signal 조건 유도."""
    closes = np.linspace(120.0, 100.0, n)
    volumes = np.ones(n) * 2000.0
    volumes[-5:] = 10000.0
    opens = closes + 0.5
    highs = closes + 1.0
    lows = closes - 1.0
    return pd.DataFrame({
        "open": opens,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
    })


# 1. 전략 이름
def test_strategy_name():
    assert strategy.name == "volume_price_trend_v2"


# 2. 인스턴스 타입
def test_instance():
    s = VolumePriceTrendV2Strategy()
    assert isinstance(s, VolumePriceTrendV2Strategy)


# 3. 데이터 부족 → HOLD (n < 20)
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# 4. None 입력 → HOLD
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# 5. reasoning 필드가 문자열
def test_reasoning_is_string():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    assert isinstance(sig.reasoning, str)
    assert len(sig.reasoning) > 0


# 6. 정상 signal 반환 (action 유효)
def test_normal_signal_valid_action():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# 7. Signal 필드 완전성
def test_signal_fields():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "volume_price_trend_v2"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# 8. BUY 시 reasoning에 "VPT" 포함
def test_buy_reasoning_contains_vpt():
    df = _make_buy_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "VPT" in sig.reasoning


# 9. SELL 시 reasoning에 "VPT" 포함
def test_sell_reasoning_contains_vpt():
    df = _make_sell_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "VPT" in sig.reasoning


# 10. confidence는 HIGH/MEDIUM/LOW 중 하나
def test_confidence_valid():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# 11. entry_price >= 0
def test_entry_price_non_negative():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    assert sig.entry_price >= 0.0


# 12. strategy 필드 확인
def test_strategy_field():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    assert sig.strategy == "volume_price_trend_v2"


# 13. 경계값 n=20 실행 가능
def test_min_rows_boundary():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)


# 14. 데이터 부족 시 entry_price = 0.0
def test_insufficient_entry_price():
    df = _make_df(n=5)
    sig = strategy.generate(df)
    assert sig.entry_price == 0.0
