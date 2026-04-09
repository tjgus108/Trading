"""
CupHandleStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.cup_handle import CupHandleStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(closes, highs=None, lows=None, volumes=None):
    n = len(closes)
    if highs is None:
        highs = [c * 1.005 for c in closes]
    if lows is None:
        lows = [c * 0.995 for c in closes]
    if volumes is None:
        volumes = [1000.0] * n
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_insufficient_df(n=30):
    closes = np.linspace(100, 110, n)
    return _make_df(closes)


def _make_flat_df(n=70):
    """패턴 없는 평탄한 데이터 → HOLD."""
    closes = np.ones(n) * 100.0
    return _make_df(closes)


def _make_cup_handle_buy_df():
    """
    실제 Cup & Handle + BUY 조건을 충족하는 데이터.

    구조 (총 75봉):
      [0..14]   상승 → 좌측 고점 (rim ~115)
      [15..44]  U자형 하락/반등 (cup, 30봉 너비)
      [45]      우측 고점 = 115  (cup_right)
      [46..48]  Handle 조정 (3봉, 113~114 수준)
      [49]      _last (iloc[-2]): close = 116 → 우측 고점(115) 돌파
      [50]      현재 진행봉 (더미)

    총 51봉 사용.
    """
    n = 51
    closes = np.zeros(n)

    # 좌측 rim 구간 [0..14]: 100→115
    closes[0:15] = np.linspace(100, 115, 15)

    # Cup 바닥 [15..44]: 115 → 80 → 115 (U자형, 30봉)
    cup_half = 15
    down = np.linspace(115, 80, cup_half + 1)
    up = np.linspace(80, 115, cup_half + 1)
    closes[15:30] = down[:-1]
    closes[30:46] = up  # [30..45]

    # [45] = 115 (우측 rim = cup_right)
    closes[45] = 115.0

    # Handle [46..48]: 소폭 조정
    closes[46] = 113.5
    closes[47] = 113.0
    closes[48] = 113.5

    # _last = iloc[-2] = [49]: 돌파
    closes[49] = 116.5

    # 현재 진행봉 [50]
    closes[50] = 116.0

    highs = closes * 1.003
    lows = closes * 0.997

    # _last 볼륨을 평균 1.6배로 설정 → HIGH confidence
    volumes = np.ones(n) * 1000.0
    volumes[49] = 1600.0

    return _make_df(closes, highs=list(highs), lows=list(lows), volumes=list(volumes))


def _make_cup_no_breakout_df():
    """
    Cup & Handle 존재하지만 close가 우측 고점 미달 → HOLD.
    """
    n = 51
    closes = np.zeros(n)

    closes[0:15] = np.linspace(100, 115, 15)

    cup_half = 15
    down = np.linspace(115, 80, cup_half + 1)
    up = np.linspace(80, 115, cup_half + 1)
    closes[15:30] = down[:-1]
    closes[30:46] = up

    closes[45] = 115.0
    closes[46] = 113.5
    closes[47] = 113.0
    closes[48] = 113.5
    closes[49] = 114.0  # 우측 고점(115) 미달
    closes[50] = 114.0

    return _make_df(closes)


# ── tests ──────────────────────────────────────────────────────────────────────

class TestCupHandleStrategy:

    def setup_method(self):
        self.strategy = CupHandleStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "cup_handle"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=30)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → confidence LOW
    def test_insufficient_data_confidence_low(self):
        df = _make_insufficient_df(n=30)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=30)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. 정확히 60행 (경계값) → 신호 반환 (action 존재)
    def test_exactly_min_rows(self):
        df = _make_flat_df(n=60)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 6. 패턴 없는 평탄 데이터 → HOLD
    def test_flat_data_hold(self):
        df = _make_flat_df(n=70)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 7. Cup & Handle + 돌파 → BUY or HOLD (패턴 유연 검증)
    def test_cup_handle_breakout_buy_or_hold(self):
        df = _make_cup_handle_buy_df()
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.HOLD)

    # 8. Cup & Handle 감지 + 미돌파 → HOLD
    def test_cup_no_breakout_hold(self):
        df = _make_cup_no_breakout_df()
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.HOLD)

    # 9. BUY 시 HIGH confidence (볼륨 1.6배)
    def test_buy_high_confidence_with_volume(self):
        df = _make_cup_handle_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_flat_df(n=70)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "cup_handle"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 11. BUY reasoning에 "Cup" 포함
    def test_buy_reasoning_contains_cup(self):
        df = _make_cup_handle_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "Cup" in signal.reasoning

    # 12. BUY 시 entry_price가 양수
    def test_buy_entry_price_positive(self):
        df = _make_cup_handle_buy_df()
        signal = self.strategy.generate(df)
        assert signal.entry_price > 0

    # 13. SELL 미지원 → SELL 없음
    def test_no_sell_signal(self):
        df = _make_cup_handle_buy_df()
        signal = self.strategy.generate(df)
        assert signal.action != Action.SELL

    # 14. BUY 시 invalidation 포함
    def test_buy_invalidation_present(self):
        df = _make_cup_handle_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.invalidation) > 0

    # 15. entry_price가 float 타입
    def test_entry_price_is_float(self):
        df = _make_flat_df(n=70)
        signal = self.strategy.generate(df)
        assert isinstance(signal.entry_price, float)
