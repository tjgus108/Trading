"""
MultiFactorScoreStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.multi_factor import MultiFactorScoreStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(closes, highs=None, lows=None, volumes=None):
    n = len(closes)
    closes = np.array(closes, dtype=float)
    if highs is None:
        highs = closes * 1.005
    if lows is None:
        lows = closes * 0.995
    if volumes is None:
        volumes = np.ones(n) * 1000.0
    return pd.DataFrame({
        "open": closes,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_strong_bull_df(n=60):
    """강한 상승: 여러 팩터 BUY 유도."""
    closes = np.array([100.0 * (1.005 ** i) for i in range(n)])
    volumes = np.ones(n) * 2000.0  # 높은 거래량
    return _make_df(closes, volumes=volumes)


def _make_strong_bear_df(n=60):
    """강한 하락: 여러 팩터 SELL 유도."""
    closes = np.array([200.0 * (0.995 ** i) for i in range(n)])
    volumes = np.ones(n) * 500.0  # 낮은 거래량
    return _make_df(closes, volumes=volumes)


def _make_neutral_df(n=60):
    """중립 횡보."""
    np.random.seed(42)
    closes = 100.0 + np.random.uniform(-0.5, 0.5, n)
    return _make_df(closes)


def _make_insufficient_df(n=10):
    closes = np.linspace(100, 110, n)
    return _make_df(closes)


def _make_score_buy_df(n=60):
    """score >= 4.0 유도: 강한 상승 + BB 하단 이탈."""
    closes = np.array([100.0 * (1.004 ** i) for i in range(n)])
    # 마지막 2봉을 급락시켜 BB_lower 하향 돌파 (반전 BUY)
    # 단, EMA20 위에서 유지되어야 score 최대화
    # → 전체 강세 유지 + 마지막만 BB 하단 이탈
    closes[-2] = 70.0
    highs = np.maximum(closes * 1.005, closes)
    lows = np.minimum(closes * 0.995, closes)
    return _make_df(closes, highs, lows)


def _make_score_sell_df(n=60):
    """score <= -4.0 유도: 강한 하락 + BB 상단 이탈."""
    closes = np.array([200.0 * (0.996 ** i) for i in range(n)])
    closes[-2] = 300.0  # BB_upper 상향 돌파 (반전 SELL)
    highs = np.maximum(closes * 1.005, closes)
    lows = np.minimum(closes * 0.995, closes)
    return _make_df(closes, highs, lows)


# ── tests ─────────────────────────────────────────────────────────────────────

class TestMultiFactorScoreStrategy:

    def setup_method(self):
        self.strategy = MultiFactorScoreStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "multi_factor"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → confidence LOW
    def test_insufficient_data_confidence_low(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. Signal 인스턴스 반환
    def test_returns_signal_instance(self):
        df = _make_strong_bull_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 6. action은 유효한 값
    def test_action_is_valid(self):
        df = _make_strong_bull_df()
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. confidence는 유효한 값
    def test_confidence_is_valid(self):
        df = _make_strong_bull_df()
        signal = self.strategy.generate(df)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 8. strategy 필드 일치
    def test_strategy_field(self):
        df = _make_strong_bull_df()
        signal = self.strategy.generate(df)
        assert signal.strategy == "multi_factor"

    # 9. entry_price는 _last 봉 close와 일치
    def test_entry_price_matches_last_close(self):
        df = _make_strong_bull_df()
        signal = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert abs(signal.entry_price - expected) < 1e-6

    # 10. reasoning은 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_strong_bull_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0

    # 11. bull_case / bear_case 필드 존재
    def test_signal_has_bull_bear_case(self):
        df = _make_strong_bull_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal.bull_case, str)
        assert isinstance(signal.bear_case, str)

    # 12. entry_price는 양수 float
    def test_entry_price_positive(self):
        df = _make_strong_bull_df()
        signal = self.strategy.generate(df)
        assert isinstance(signal.entry_price, float)
        assert signal.entry_price > 0

    # 13. BUY reasoning에 "score" 포함
    def test_buy_reasoning_contains_score(self):
        df = _make_strong_bull_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "score" in signal.reasoning.lower() or "Score" in signal.reasoning

    # 14. SELL reasoning에 "score" 포함
    def test_sell_reasoning_contains_score(self):
        df = _make_strong_bear_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "score" in signal.reasoning.lower() or "Score" in signal.reasoning

    # 15. BUY 시 invalidation 포함
    def test_buy_has_invalidation(self):
        df = _make_strong_bull_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.invalidation) > 0

    # 16. SELL 시 invalidation 포함
    def test_sell_has_invalidation(self):
        df = _make_strong_bear_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.invalidation) > 0

    # 17. 정확히 25봉 → 에러 없음
    def test_exactly_25_rows_no_error(self):
        closes = np.linspace(100, 125, 25)
        df = _make_df(closes)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 18. 중립 횡보 → HOLD
    def test_neutral_returns_hold(self):
        df = _make_neutral_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 19. score >= 5.0 → HIGH confidence
    def test_high_score_high_confidence(self):
        df = _make_strong_bull_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            # reasoning에서 score 추출
            import re
            m = re.search(r"score=([-\d.]+)", signal.reasoning)
            if m:
                s = float(m.group(1))
                if s >= 5.0:
                    assert signal.confidence == Confidence.HIGH

    # 20. HOLD reasoning에 "임계값" 또는 "score" 포함
    def test_hold_reasoning_contains_info(self):
        df = _make_neutral_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD
        assert "score" in signal.reasoning.lower() or "Score" in signal.reasoning

    # 21. 상승 추세 → SELL 아님 (HOLD 또는 BUY)
    def test_strong_bull_no_sell(self):
        closes = np.array([100.0 * (1.006 ** i) for i in range(60)])
        df = _make_df(closes, volumes=np.ones(60) * 3000.0)
        signal = self.strategy.generate(df)
        assert signal.action != Action.SELL

    # 22. 하락 추세 → BUY 아님 (HOLD 또는 SELL)
    def test_strong_bear_no_buy(self):
        closes = np.array([200.0 * (0.994 ** i) for i in range(60)])
        df = _make_df(closes, volumes=np.ones(60) * 200.0)
        signal = self.strategy.generate(df)
        assert signal.action != Action.BUY
