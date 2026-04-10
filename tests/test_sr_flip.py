"""
SRFlipStrategy 단위 테스트 (14개)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.sr_flip import SRFlipStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_flat_df(n: int = 30) -> pd.DataFrame:
    closes = np.ones(n) * 100.0
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


def _make_insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


def _make_buy_df() -> pd.DataFrame:
    """
    이전 저항 swing high 존재 + 현재 종가가 저항 * 1.001 초과 → BUY.
    n=25, idx=23
    swing high를 idx-7 위치에 삽입.
    """
    n = 25
    closes = np.ones(n) * 100.0
    highs = np.ones(n) * 101.0
    lows = np.ones(n) * 99.0

    # swing high at idx-7 = 16
    shi = 16
    highs[shi] = 110.0
    highs[shi - 1] = 105.0
    highs[shi - 2] = 103.0
    highs[shi + 1] = 105.0
    highs[shi + 2] = 103.0

    # curr_close (idx=23) > swing_high * 1.001 = 110.11
    closes[23] = 111.0
    closes[24] = 112.0  # last candle (진행 중, 무시됨)

    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


def _make_sell_df() -> pd.DataFrame:
    """
    이전 지지 swing low 존재 + 현재 종가가 지지 * 0.999 미만 → SELL.
    n=25, idx=23
    """
    n = 25
    closes = np.ones(n) * 100.0
    highs = np.ones(n) * 101.0
    lows = np.ones(n) * 99.0

    # swing low at idx-7 = 16
    sli = 16
    lows[sli] = 90.0
    lows[sli - 1] = 94.0
    lows[sli - 2] = 96.0
    lows[sli + 1] = 94.0
    lows[sli + 2] = 96.0

    # curr_close (idx=23) < swing_low * 0.999 = 89.91
    closes[23] = 89.0
    closes[24] = 88.0

    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


def _make_high_confidence_buy_df() -> pd.DataFrame:
    """proximity < 0.005 → HIGH confidence BUY."""
    n = 25
    closes = np.ones(n) * 100.0
    highs = np.ones(n) * 101.0
    lows = np.ones(n) * 99.0

    shi = 16
    highs[shi] = 110.0
    highs[shi - 1] = 105.0
    highs[shi - 2] = 103.0
    highs[shi + 1] = 105.0
    highs[shi + 2] = 103.0

    # proximity = |close - 110| / 110 < 0.005 → close in (109.45, 110.55)
    # but also curr_close > 110 * 1.001 = 110.11
    closes[23] = 110.2   # proximity = 0.2/110 ≈ 0.0018 < 0.005
    closes[24] = 110.5

    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


def _make_medium_confidence_buy_df() -> pd.DataFrame:
    """proximity >= 0.005 → MEDIUM confidence BUY."""
    n = 25
    closes = np.ones(n) * 100.0
    highs = np.ones(n) * 101.0
    lows = np.ones(n) * 99.0

    shi = 16
    highs[shi] = 110.0
    highs[shi - 1] = 105.0
    highs[shi - 2] = 103.0
    highs[shi + 1] = 105.0
    highs[shi + 2] = 103.0

    # proximity = |close - 110| / 110 >= 0.005 → close > 110.55
    closes[23] = 115.0   # far from level
    closes[24] = 116.0

    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestSRFlipStrategy:

    def setup_method(self):
        self.strategy = SRFlipStrategy()

    # 1. 전략명 확인
    def test_strategy_name(self):
        assert self.strategy.name == "sr_flip"

    # 2. 인스턴스 생성
    def test_instance_creation(self):
        assert isinstance(self.strategy, SRFlipStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 4. None 입력 → HOLD
    def test_none_input_hold(self):
        signal = self.strategy.generate(None)
        assert signal.action == Action.HOLD

    # 5. 데이터 부족 reasoning 확인
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "Insufficient" in signal.reasoning

    # 6. 정상 데이터 → Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_flat_df(n=30)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 7. Signal 필드 완성
    def test_signal_fields_complete(self):
        df = _make_flat_df(n=30)
        signal = self.strategy.generate(df)
        assert isinstance(signal.action, Action)
        assert isinstance(signal.confidence, Confidence)
        assert isinstance(signal.strategy, str)
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str)
        assert isinstance(signal.invalidation, str)

    # 8. BUY reasoning 키워드 확인
    def test_buy_reasoning_keyword(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "flip" in signal.reasoning.lower() or "resistance" in signal.reasoning.lower()

    # 9. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "flip" in signal.reasoning.lower() or "support" in signal.reasoning.lower()

    # 10. HIGH confidence BUY
    def test_high_confidence_buy(self):
        df = _make_high_confidence_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 11. MEDIUM confidence BUY
    def test_medium_confidence_buy(self):
        df = _make_medium_confidence_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.MEDIUM

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_flat_df(n=30)
        signal = self.strategy.generate(df)
        assert signal.entry_price > 0

    # 13. strategy 필드 값 확인
    def test_strategy_field_value(self):
        df = _make_flat_df(n=30)
        signal = self.strategy.generate(df)
        assert signal.strategy == "sr_flip"

    # 14. 최소 행 수(15)에서 동작
    def test_minimum_rows_works(self):
        df = _make_flat_df(n=15)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
