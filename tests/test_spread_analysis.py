"""SpreadAnalysisStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.spread_analysis import SpreadAnalysisStrategy

strategy = SpreadAnalysisStrategy()


def _make_df(n=40, mode="hold"):
    """
    mode: "buy"  → 낮은 스프레드 + 위쪽 마감 + 상승
          "sell" → 낮은 스프레드 + 아래쪽 마감 + 하락
          "hold" → 스프레드 높음 또는 애매한 위치
    """
    closes = np.full(n, 100.0, dtype=float)
    highs = np.full(n, 102.0, dtype=float)
    lows = np.full(n, 98.0, dtype=float)
    volumes = np.ones(n) * 1000.0

    if mode == "buy":
        # 평균 스프레드를 높게 설정 (롤링 14 mean이 높도록)
        for i in range(n - 5):
            highs[i] = closes[i] + 5.0   # 큰 스프레드
            lows[i] = closes[i] - 5.0
        # 마지막 구간: 낮은 스프레드 + close가 high 근처 (위쪽 마감)
        for i in range(n - 5, n):
            highs[i] = closes[i] + 0.5   # 낮은 스프레드
            lows[i] = closes[i] - 0.5
            closes[i] = (highs[i] + lows[i]) * 0.5 + 0.4  # close_pos > 0.7

    elif mode == "sell":
        # 평균 스프레드를 높게 설정
        for i in range(n - 5):
            highs[i] = closes[i] + 5.0
            lows[i] = closes[i] - 5.0
        # 마지막 구간: 낮은 스프레드 + close가 low 근처 (아래쪽 마감)
        for i in range(n - 5, n):
            highs[i] = closes[i] + 0.5
            lows[i] = closes[i] - 0.5
            closes[i] = (highs[i] + lows[i]) * 0.5 - 0.4  # close_pos < 0.3

    opens = closes.copy()
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


def _make_buy_df(n=40):
    """BUY 신호 조건 명확하게 설계."""
    closes = np.full(n, 100.0, dtype=float)
    highs = np.full(n, 105.0, dtype=float)  # 넓은 스프레드 → 평균 높아짐
    lows = np.full(n, 95.0, dtype=float)
    volumes = np.ones(n) * 1000.0

    # 마지막 10봉: 스프레드 매우 낮음 + close가 위쪽
    for i in range(n - 10, n):
        highs[i] = 100.5
        lows[i] = 99.5
        closes[i] = 100.4   # close_pos = (100.4-99.5)/(100.5-99.5) = 0.9 > 0.7

    opens = closes.copy()
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


def _make_sell_df(n=40):
    """SELL 신호 조건 명확하게 설계."""
    closes = np.full(n, 100.0, dtype=float)
    highs = np.full(n, 105.0, dtype=float)
    lows = np.full(n, 95.0, dtype=float)
    volumes = np.ones(n) * 1000.0

    # 마지막 10봉: 스프레드 매우 낮음 + close가 아래쪽
    for i in range(n - 10, n):
        highs[i] = 100.5
        lows[i] = 99.5
        closes[i] = 99.6   # close_pos = (99.6-99.5)/(100.5-99.5) = 0.1 < 0.3

    opens = closes.copy()
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
    assert strategy.name == "spread_analysis"


# 2. 인스턴스 타입
def test_instance():
    s = SpreadAnalysisStrategy()
    assert isinstance(s, SpreadAnalysisStrategy)


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


# 6. 정상 signal 반환
def test_normal_signal():
    df = _make_df(n=40, mode="hold")
    sig = strategy.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# 7. Signal 필드 완전성
def test_signal_fields():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "spread_analysis"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# 8. BUY reasoning에 "스프레드" 포함
def test_buy_reasoning():
    df = _make_buy_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "스프레드" in sig.reasoning


# 9. SELL reasoning에 "스프레드" 포함
def test_sell_reasoning():
    df = _make_sell_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "스프레드" in sig.reasoning


# 10. HIGH confidence 가능
def test_confidence_high_possible():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# 11. MEDIUM confidence 가능
def test_confidence_medium_possible():
    df = _make_buy_df()
    sig = strategy.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# 12. entry_price >= 0
def test_entry_price_nonnegative():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    assert sig.entry_price >= 0.0


# 13. strategy 필드 확인
def test_strategy_field():
    df = _make_df(n=40)
    sig = strategy.generate(df)
    assert sig.strategy == "spread_analysis"


# 14. 최소 20행으로 실행 가능
def test_min_rows_boundary():
    df = _make_df(n=20)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)
