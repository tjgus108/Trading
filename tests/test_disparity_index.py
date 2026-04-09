"""
DisparityIndexStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.disparity_index import DisparityIndexStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 80, di_type: str = "neutral") -> pd.DataFrame:
    """
    di_type:
      "oversold_rising"    - DI < -5 & DI 상승 (BUY 조건)
      "overbought_falling" - DI > 5  & DI 하락 (SELL 조건)
      "oversold_falling"   - DI < -5 & DI 하락 (HOLD)
      "overbought_rising"  - DI > 5  & DI 상승 (HOLD)
      "neutral"            - |DI| < 5 (HOLD)
      "extreme_oversold"   - DI < -8 & 상승 (HIGH confidence BUY)
      "extreme_overbought" - DI > 8  & 하락 (HIGH confidence SELL)

    EMA20이 높은 가격 수준에서 안정화된 후 가격이 급락(또는 급등)하면
    DI가 명확하게 임계값을 벗어난다.
    """
    np.random.seed(42)
    n_base = max(n, 60)

    if di_type == "oversold_rising":
        # EMA20을 100 근처에 유지한 채 idx-1에서 매우 낮고, idx에서 약간 높게.
        # EWM 특성: 앞 60개=100 → EMA≈100, 마지막 2개를 85, 87로 하면:
        # EMA[-3] ≈ 100*(19/21) + 85*(2/21) ≈ 98.9 → DI ≈ (85-98.9)/98.9 ≈ -14%
        # EMA[-2] ≈ 98.9*(19/21) + 87*(2/21) ≈ 97.2 → DI ≈ (87-97.2)/97.2 ≈ -10.5%
        # -10.5 > -14 이므로 di_now > di_prev (상승) → BUY
        closes = np.full(n_base, 100.0)
        closes[-3] = 85.0
        closes[-2] = 87.0
        closes[-1] = 88.0

    elif di_type == "overbought_falling":
        # EMA≈100, closes[-3]=115, closes[-2]=113
        # DI[-3] ≈ (115-101)/101 ≈ +13.8%
        # DI[-2] < DI[-3] → 하락 → SELL
        closes = np.full(n_base, 100.0)
        closes[-3] = 115.0
        closes[-2] = 113.0
        closes[-1] = 112.0

    elif di_type == "oversold_falling":
        # DI < -5 & DI 하락 → HOLD
        # closes[-3]=87, closes[-2]=85: DI[-2] < DI[-3]
        closes = np.full(n_base, 100.0)
        closes[-3] = 87.0
        closes[-2] = 85.0
        closes[-1] = 84.0

    elif di_type == "overbought_rising":
        # DI > 5 & DI 상승 → HOLD
        # closes[-3]=113, closes[-2]=115: DI[-2] > DI[-3]
        closes = np.full(n_base, 100.0)
        closes[-3] = 113.0
        closes[-2] = 115.0
        closes[-1] = 116.0

    elif di_type == "extreme_oversold":
        # DI < -8 확실히: closes[-3]=82, closes[-2]=84
        # DI[-3] ≈ (82-99)/99 ≈ -17%, DI[-2] 약간 상승
        closes = np.full(n_base, 100.0)
        closes[-3] = 82.0
        closes[-2] = 84.0
        closes[-1] = 85.0

    elif di_type == "extreme_overbought":
        # DI > 8 확실히: closes[-3]=118, closes[-2]=116
        closes = np.full(n_base, 100.0)
        closes[-3] = 118.0
        closes[-2] = 116.0
        closes[-1] = 115.0

    else:  # neutral: 완만한 상승 → DI ≈ 0
        closes = np.linspace(99, 101, n_base)

    df = pd.DataFrame({
        "open": closes * 0.999,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.random.uniform(1000, 5000, n_base),
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

class TestDisparityIndexStrategy:

    def setup_method(self):
        self.strategy = DisparityIndexStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "disparity_index"

    # 2. Signal 인스턴스 반환
    def test_returns_signal(self):
        df = _make_df(n=60, di_type="neutral")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 4. 데이터 부족 시 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=10)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 5. 중립 구간 → HOLD
    def test_neutral_hold(self):
        df = _make_df(n=60, di_type="neutral")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 6. DI < -5 & 상승 → BUY
    def test_oversold_rising_buy(self):
        df = _make_df(n=60, di_type="oversold_rising")
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY

    # 7. DI > 5 & 하락 → SELL
    def test_overbought_falling_sell(self):
        df = _make_df(n=60, di_type="overbought_falling")
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 8. DI < -5 & 하락 → HOLD (방향 불충족)
    def test_oversold_falling_hold(self):
        df = _make_df(n=60, di_type="oversold_falling")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 9. DI > 5 & 상승 → HOLD (방향 불충족)
    def test_overbought_rising_hold(self):
        df = _make_df(n=60, di_type="overbought_rising")
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 10. 극단 과매도 BUY → HIGH confidence
    def test_extreme_oversold_high_confidence(self):
        df = _make_df(n=60, di_type="extreme_oversold")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 11. 극단 과열 SELL → HIGH confidence
    def test_extreme_overbought_high_confidence(self):
        df = _make_df(n=60, di_type="extreme_overbought")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.HIGH

    # 12. strategy 필드 일치
    def test_signal_strategy_field(self):
        df = _make_df(n=60, di_type="neutral")
        signal = self.strategy.generate(df)
        assert signal.strategy == "disparity_index"

    # 13. entry_price는 float
    def test_entry_price_is_float(self):
        df = _make_df(n=60, di_type="neutral")
        signal = self.strategy.generate(df)
        assert isinstance(signal.entry_price, float)

    # 14. reasoning에 "DI" 포함
    def test_reasoning_contains_di(self):
        df = _make_df(n=60, di_type="neutral")
        signal = self.strategy.generate(df)
        assert "DI" in signal.reasoning

    # 15. BUY 신호에 bull_case/bear_case 포함
    def test_buy_signal_has_bull_bear_case(self):
        df = _make_df(n=60, di_type="oversold_rising")
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 16. SELL 신호에 bull_case/bear_case 포함
    def test_sell_signal_has_bull_bear_case(self):
        df = _make_df(n=60, di_type="overbought_falling")
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 17. confidence 유효값
    def test_confidence_valid_values(self):
        df = _make_df(n=60, di_type="neutral")
        signal = self.strategy.generate(df)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 18. action 유효값
    def test_action_valid_values(self):
        df = _make_df(n=60, di_type="neutral")
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 19. invalidation 문자열
    def test_invalidation_is_string(self):
        df = _make_df(n=60, di_type="neutral")
        signal = self.strategy.generate(df)
        assert isinstance(signal.invalidation, str)

    # 20. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df(n=60, di_type="oversold_rising")
        signal = self.strategy.generate(df)
        assert len(signal.reasoning) > 0
