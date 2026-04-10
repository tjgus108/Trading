"""
VolumeMomentumBreakStrategy 단위 테스트 (14개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.volume_momentum_break import VolumeMomentumBreakStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 50, vol_ratio: float = 1.0, roc3_direction: str = "up") -> pd.DataFrame:
    """테스트용 OHLCV DataFrame 생성."""
    np.random.seed(42)
    closes = np.linspace(100, 110, n) if roc3_direction == "up" else np.linspace(110, 100, n)
    closes = closes + np.random.normal(0, 0.01, n)

    base_vol = 1000.0
    volumes = np.full(n, base_vol)
    # 마지막 완성 캔들(idx=-2)에 vol_ratio 적용
    volumes[-2] = base_vol * vol_ratio

    highs = closes * 1.005
    lows = closes * 0.995
    opens = closes * (1 + np.random.uniform(-0.001, 0.001, n))

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_buy_df() -> pd.DataFrame:
    """vol_surge + 상승 모멘텀 가속 조건을 정확히 만족하는 DataFrame.

    전략: idx = len(df) - 2 (마지막 완성 캔들)
    BUY: vol_ratio[idx]>2 AND roc3[idx]>roc3_ma[idx] AND roc3[idx]>0

    n=55이면 idx=53.
    - closes[53]: 급등 (roc3[53] > 0 보장)
    - closes[50..52]: 완만 상승 (roc3_ma가 작도록)
    - closes[0..49]: flat 100
    - volumes[53]: 100 (나머지 1) → vol_ma ≈ 6.95 → vol_ratio ≈ 14
    """
    n = 55
    closes = np.ones(n) * 100.0
    # idx 40~52: 완만 상승 (roc3_ma 형성용, roc3 ≈ 0.001~0.002)
    for i in range(40, 53):
        closes[i] = 100 + (i - 39) * 0.05
    # idx=53 (len-2): 급격 상승 → roc3[53] = (closes[53]-closes[50])/closes[50] >> roc3_ma
    closes[53] = closes[52] * 1.05   # +5% from prev candle
    closes[54] = closes[53] * 1.01   # idx=-1 (current, ignored)

    volumes = np.ones(n) * 1.0
    volumes[53] = 100.0  # idx=-2에 거래량 폭등

    highs = closes * 1.005
    lows = closes * 0.995
    opens = closes.copy()

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_sell_df() -> pd.DataFrame:
    """vol_surge + 하락 모멘텀 가속 조건을 정확히 만족하는 DataFrame.

    n=55이면 idx=53.
    SELL: vol_ratio[53]>2 AND roc3[53]<roc3_ma[53] AND roc3[53]<0
    """
    n = 55
    closes = np.ones(n) * 100.0
    # idx 40~52: 완만 하락 (roc3_ma ≈ 0)
    for i in range(40, 53):
        closes[i] = 100 - (i - 39) * 0.05
    # idx=53 (len-2): 급격 하락 → roc3[53] << roc3_ma
    closes[53] = closes[52] * 0.95   # -5% from prev
    closes[54] = closes[53] * 0.99   # idx=-1 (current, ignored)

    volumes = np.ones(n) * 1.0
    volumes[53] = 100.0  # idx=-2에 거래량 폭등

    highs = closes * 1.005
    lows = closes * 0.995
    opens = closes.copy()

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestVolumeMomentumBreakStrategy:

    def setup_method(self):
        self.strategy = VolumeMomentumBreakStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "volume_momentum_break"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=10)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 시 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_df(n=5)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. 정상 데이터 Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_df(n=50)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 5. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=50)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "volume_momentum_break"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 6. 거래량 급증 + 상승 모멘텀 → BUY
    def test_vol_surge_up_momentum_buy(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.BUY, f"reasoning: {signal.reasoning}"

    # 7. BUY 시 vol_ratio > 3.0 → HIGH confidence
    def test_buy_high_confidence_when_vol_ratio_gt3(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 8. 거래량 급증 + 하락 모멘텀 → SELL
    def test_vol_surge_down_momentum_sell(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        assert signal.action == Action.SELL

    # 9. SELL 시 vol_ratio > 3.0 → HIGH confidence
    def test_sell_high_confidence_when_vol_ratio_gt3(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.HIGH

    # 10. 거래량 미급증 → HOLD
    def test_no_vol_surge_hold(self):
        df = _make_df(n=50, vol_ratio=1.2, roc3_direction="up")
        signal = self.strategy.generate(df)
        # vol_ratio < 2.0 이므로 BUY 불가
        assert signal.action == Action.HOLD

    # 11. HOLD 시 confidence LOW
    def test_hold_confidence_low(self):
        df = _make_df(n=50, vol_ratio=1.0)
        signal = self.strategy.generate(df)
        if signal.action == Action.HOLD:
            assert signal.confidence == Confidence.LOW

    # 12. BUY reasoning에 "거래량 급증" 포함
    def test_buy_reasoning_contains_keyword(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "거래량" in signal.reasoning

    # 13. SELL reasoning에 "하락" 포함
    def test_sell_reasoning_contains_keyword(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "하락" in signal.reasoning

    # 14. BUY 신호에 bull_case/bear_case 존재
    def test_buy_signal_has_bull_bear_case(self):
        df = _make_buy_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 15. SELL 신호에 bull_case/bear_case 존재
    def test_sell_signal_has_bull_bear_case(self):
        df = _make_sell_df()
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.bull_case) > 0
            assert len(signal.bear_case) > 0

    # 16. entry_price는 마지막 완성 캔들 close
    def test_entry_price_is_last_close(self):
        df = _make_df(n=50)
        signal = self.strategy.generate(df)
        assert signal.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-6)
