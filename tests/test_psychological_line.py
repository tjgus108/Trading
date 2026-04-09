"""
PsychologicalLineStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.psychological_line import PsychologicalLineStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_pl_closes(n: int, window_pattern: list, final_two: tuple) -> np.ndarray:
    """
    window_pattern: 마지막 12봉(idx-12 ~ idx-1)의 up/down 패턴 (길이 12)
                    True=상승, False=하락. 단 마지막 원소가 idx-1(close_prev)
    final_two: (close_prev, close_now) — idx-1, idx 값 (절대값)
    전체 n개 배열 반환. 앞부분은 100으로 채움.
    """
    closes = np.full(n, 100.0)
    # idx = n - 2, idx-1 = n-3
    base = 100.0
    # window 12봉을 idx-12 ~ idx-1에 배치 (idx-1 = n-3)
    # window_pattern[0] = n-3-11 위치부터
    start = n - 3 - 11  # = n - 14
    closes[start] = base
    for i, up in enumerate(window_pattern[1:], 1):
        closes[start + i] = closes[start + i - 1] * (1.005 if up else 0.996)
    # idx-1 = n-3, idx = n-2
    closes[n - 3] = final_two[0]
    closes[n - 2] = final_two[1]
    closes[n - 1] = final_two[1] * 1.001  # 미래봉 (사용 안 함)
    return closes


def _make_df(n: int = 40, pl_type: str = "neutral") -> pd.DataFrame:
    """
    pl_type:
      "bearish_rising"     - PL < 25 & 현재 봉 상승 (BUY)
      "bullish_falling"    - PL > 75 & 현재 봉 하락 (SELL)
      "bearish_falling"    - PL < 25 & 현재 봉 하락 (HOLD)
      "bullish_rising"     - PL > 75 & 현재 봉 상승 (HOLD)
      "neutral"            - 25 <= PL <= 75 (HOLD)
      "extreme_bearish"    - PL < 17 & 상승 (HIGH confidence BUY)
      "extreme_bullish"    - PL > 83 & 하락 (HIGH confidence SELL)

    전략은 idx = len(df)-2 사용.
    rolling(12).sum()이 정확히 계산되려면 idx 기준 12봉 이상 필요.
    n >= 30 권장.
    """
    np.random.seed(0)
    n_base = max(n, 30)
    base = 100.0

    if pl_type == "bearish_rising":
        # 12봉 중 2봉 상승 (PL = 2/12*100 ≈ 16.7%) + idx 봉 상승
        # pattern: 11 down, 1 up (마지막이 close_prev 직전)
        # close_prev < close_now (상승)
        closes = np.full(n_base, base)
        # idx-12 ~ idx-1: 10 down, 1 up, 1 down
        for i in range(n_base - 14, n_base - 3):
            closes[i] = closes[i - 1] * 0.996 if i > 0 else base
        closes[n_base - 14] = base
        for i in range(n_base - 13, n_base - 5):
            closes[i] = closes[i - 1] * 0.996
        closes[n_base - 5] = closes[n_base - 6] * 1.005  # 1 up
        closes[n_base - 4] = closes[n_base - 5] * 0.996  # 1 down
        closes[n_base - 3] = closes[n_base - 4] * 0.996  # close_prev (하락)
        closes[n_base - 2] = closes[n_base - 3] * 1.005  # close_now (상승) → BUY
        closes[n_base - 1] = closes[n_base - 2] * 1.001

    elif pl_type == "bullish_falling":
        # 12봉 중 10봉 상승 (PL ≈ 83.3%) + idx 봉 하락
        closes = np.full(n_base, base)
        closes[n_base - 14] = base
        for i in range(n_base - 13, n_base - 5):
            closes[i] = closes[i - 1] * 1.005
        closes[n_base - 5] = closes[n_base - 6] * 0.996  # 1 down
        closes[n_base - 4] = closes[n_base - 5] * 1.005  # 1 up
        closes[n_base - 3] = closes[n_base - 4] * 1.005  # close_prev (상승)
        closes[n_base - 2] = closes[n_base - 3] * 0.996  # close_now (하락) → SELL
        closes[n_base - 1] = closes[n_base - 2] * 0.999

    elif pl_type == "bearish_falling":
        # 12봉 중 2봉 상승 + idx 봉 하락 → HOLD
        closes = np.full(n_base, base)
        closes[n_base - 14] = base
        for i in range(n_base - 13, n_base - 5):
            closes[i] = closes[i - 1] * 0.996
        closes[n_base - 5] = closes[n_base - 6] * 1.005
        closes[n_base - 4] = closes[n_base - 5] * 0.996
        closes[n_base - 3] = closes[n_base - 4] * 1.005  # close_prev (상승)
        closes[n_base - 2] = closes[n_base - 3] * 0.996  # close_now (하락) → HOLD
        closes[n_base - 1] = closes[n_base - 2] * 0.999

    elif pl_type == "bullish_rising":
        # 12봉 중 10봉 상승 + idx 봉 상승 → HOLD
        closes = np.full(n_base, base)
        closes[n_base - 14] = base
        for i in range(n_base - 13, n_base - 5):
            closes[i] = closes[i - 1] * 1.005
        closes[n_base - 5] = closes[n_base - 6] * 0.996
        closes[n_base - 4] = closes[n_base - 5] * 1.005
        closes[n_base - 3] = closes[n_base - 4] * 0.996  # close_prev (하락)
        closes[n_base - 2] = closes[n_base - 3] * 1.005  # close_now (상승) → HOLD
        closes[n_base - 1] = closes[n_base - 2] * 1.001

    elif pl_type == "extreme_bearish":
        # 12봉 중 1봉 상승 (PL ≈ 8.3%) + idx 봉 상승 → HIGH confidence BUY
        closes = np.full(n_base, base)
        closes[n_base - 14] = base
        for i in range(n_base - 13, n_base - 3):
            closes[i] = closes[i - 1] * 0.996
        closes[n_base - 3] = closes[n_base - 4] * 0.996  # close_prev (하락)
        closes[n_base - 2] = closes[n_base - 3] * 1.005  # close_now (상승)
        closes[n_base - 1] = closes[n_base - 2] * 1.001

    elif pl_type == "extreme_bullish":
        # 12봉 중 11봉 상승 (PL ≈ 91.7%) + idx 봉 하락 → HIGH confidence SELL
        closes = np.full(n_base, base)
        closes[n_base - 14] = base
        for i in range(n_base - 13, n_base - 3):
            closes[i] = closes[i - 1] * 1.005
        closes[n_base - 3] = closes[n_base - 4] * 1.005  # close_prev (상승)
        closes[n_base - 2] = closes[n_base - 3] * 0.996  # close_now (하락)
        closes[n_base - 1] = closes[n_base - 2] * 0.999

    else:  # neutral: 6 up / 6 down 반복 → PL ≈ 50%
        closes = np.array([base * (1.003 if i % 2 == 0 else 0.997) ** (i // 2 + 1)
                           for i in range(n_base)], dtype=float)
        closes = np.full(n_base, base)
        for i in range(1, n_base):
            closes[i] = closes[i - 1] * (1.003 if i % 2 == 0 else 0.997)

    df = pd.DataFrame({
        "open": closes * 0.999,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.random.uniform(1000, 5000, len(closes)),
        "ema50": closes * 0.98,
        "atr14": closes * 0.005,
    })
    return df


def _make_insufficient_df(n: int = 10) -> pd.DataFrame:
    closes = np.linspace(100, 105, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.01,
        "low": closes * 0.99,
        "close": closes,
        "volume": np.ones(n) * 1000,
        "ema50": closes * 0.98,
        "atr14": closes * 0.005,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestPsychologicalLineStrategy:

    def setup_method(self):
        self.strategy = PsychologicalLineStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "psychological_line"

    # 2. Signal 인스턴스 반환
    def test_returns_signal(self):
        df = _make_df(n=40, pl_type="neutral")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 4. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. PL < 25 & 상승봉 → BUY
    def test_bearish_rising_buy(self):
        df = _make_df(n=40, pl_type="bearish_rising")
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 6. PL > 75 & 하락봉 → SELL
    def test_bullish_falling_sell(self):
        df = _make_df(n=40, pl_type="bullish_falling")
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 7. PL < 25 & 하락봉 → HOLD (방향 불충족)
    def test_bearish_falling_hold(self):
        df = _make_df(n=40, pl_type="bearish_falling")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 8. PL > 75 & 상승봉 → HOLD (방향 불충족)
    def test_bullish_rising_hold(self):
        df = _make_df(n=40, pl_type="bullish_rising")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 9. 중립 → HOLD
    def test_neutral_hold(self):
        df = _make_df(n=40, pl_type="neutral")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 10. 극단 과매도 BUY → HIGH confidence
    def test_extreme_bearish_high_confidence(self):
        df = _make_df(n=40, pl_type="extreme_bearish")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 11. 극단 과매수 SELL → HIGH confidence
    def test_extreme_bullish_high_confidence(self):
        df = _make_df(n=40, pl_type="extreme_bullish")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.HIGH

    # 12. strategy 필드 일치
    def test_signal_strategy_field(self):
        df = _make_df(n=40, pl_type="neutral")
        signal = self.strategy.generate(df)
        assert signal.strategy == "psychological_line"

    # 13. entry_price는 float
    def test_entry_price_is_float(self):
        df = _make_df(n=40, pl_type="neutral")
        signal = self.strategy.generate(df)
        assert isinstance(signal.entry_price, float)

    # 14. reasoning에 "PL" 포함
    def test_reasoning_contains_pl(self):
        df = _make_df(n=40, pl_type="neutral")
        signal = self.strategy.generate(df)
        assert "PL" in signal.reasoning

    # 15. BUY 신호에 bull_case/bear_case 포함
    def test_buy_signal_has_bull_bear_case(self):
        df = _make_df(n=40, pl_type="bearish_rising")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 16. SELL 신호에 bull_case/bear_case 포함
    def test_sell_signal_has_bull_bear_case(self):
        df = _make_df(n=40, pl_type="bullish_falling")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 17. confidence 유효값
    def test_confidence_valid_values(self):
        df = _make_df(n=40, pl_type="neutral")
        signal = self.strategy.generate(df)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 18. action 유효값
    def test_action_valid_values(self):
        df = _make_df(n=40, pl_type="neutral")
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 19. invalidation 문자열
    def test_invalidation_is_string(self):
        df = _make_df(n=40, pl_type="neutral")
        signal = self.strategy.generate(df)
        assert isinstance(signal.invalidation, str)

    # 20. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df(n=40, pl_type="bearish_rising")
        signal = self.strategy.generate(df)
        assert len(signal.reasoning) > 0
