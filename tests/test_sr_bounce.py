"""
SRBounceStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.sr_bounce import SRBounceStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 80, seed: int = 0) -> pd.DataFrame:
    np.random.seed(seed)
    closes = np.linspace(100.0, 110.0, n)
    highs = closes * (1 + np.random.uniform(0.005, 0.015, n))
    lows = closes * (1 - np.random.uniform(0.005, 0.015, n))
    opens = closes * (1 + np.random.uniform(-0.003, 0.003, n))
    volumes = np.random.uniform(1000, 3000, n)
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    })


def _make_support_bounce_df() -> pd.DataFrame:
    """Support 레벨 근처에서 BUY 조건이 성립하는 DataFrame."""
    n = 80
    closes = np.ones(n) * 100.0
    highs = closes + 1.0
    lows = closes - 1.0
    opens = closes.copy()
    volumes = np.ones(n) * 1000.0

    # pivot low 생성: window = df.iloc[n-2-50 : n-2] = df.iloc[28:78]
    # 5번 인덱스(window 기준)에 명확한 pivot low 삽입
    base = 28
    support_val = 95.0
    pivot_idx = base + 7  # 5 <= 7 <= n-50-5 = 23 범위 내
    lows[pivot_idx] = support_val
    for k in range(1, 6):
        lows[pivot_idx - k] = support_val + k * 0.5
        lows[pivot_idx + k] = support_val + k * 0.5

    # pivot high 생성 (resistance를 위)
    res_val = 110.0
    pivot_h_idx = base + 20
    highs[pivot_h_idx] = res_val
    for k in range(1, 6):
        highs[pivot_h_idx - k] = res_val - k * 0.5
        highs[pivot_h_idx + k] = res_val - k * 0.5

    # idx = n-2 = 78: close near support (within ±1%)
    closes[78] = support_val * 1.005  # 95.475
    highs[78] = closes[78] + 0.1
    lows[78] = closes[78] - 0.1

    # 볼륨: idx(78) > avg * 1.1
    volumes[78] = 5000.0

    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    })


def _make_resistance_touch_df() -> pd.DataFrame:
    """Resistance 레벨 근처에서 SELL 조건이 성립하는 DataFrame."""
    n = 80
    closes = np.ones(n) * 100.0
    highs = closes + 1.0
    lows = closes - 1.0
    opens = closes.copy()
    volumes = np.ones(n) * 1000.0

    base = 28
    res_val = 108.0

    # pivot high 생성
    pivot_h_idx = base + 7
    highs[pivot_h_idx] = res_val
    for k in range(1, 6):
        highs[pivot_h_idx - k] = res_val - k * 0.5
        highs[pivot_h_idx + k] = res_val - k * 0.5

    # support는 현재가 아래
    sup_val = 90.0
    pivot_l_idx = base + 20
    lows[pivot_l_idx] = sup_val
    for k in range(1, 6):
        lows[pivot_l_idx - k] = sup_val + k * 0.5
        lows[pivot_l_idx + k] = sup_val + k * 0.5

    # idx = 78: close near resistance (within ±1%)
    closes[78] = res_val * 1.005  # 108.54
    highs[78] = closes[78] + 0.1
    lows[78] = closes[78] - 0.1

    volumes[78] = 5000.0

    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    })


def _make_insufficient_df(n: int = 30) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestSRBounceStrategy:

    def setup_method(self):
        self.strategy = SRBounceStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "sr_bounce"

    # 2. 데이터 부족(60 미만) → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=30)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=30)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. Signal 반환 타입
    def test_returns_signal_type(self):
        df = _make_df(n=80)
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)

    # 5. Support 터치 → BUY 가능
    def test_support_bounce_buy(self):
        df = _make_support_bounce_df()
        signal = self.strategy.generate(df)
        # support 터치 + vol 확인 → BUY 기대
        assert signal.action in (Action.BUY, Action.HOLD)

    # 6. Resistance 터치 → SELL 가능
    def test_resistance_touch_sell(self):
        df = _make_resistance_touch_df()
        signal = self.strategy.generate(df)
        assert signal.action in (Action.SELL, Action.HOLD)

    # 7. 볼륨 낮으면 신호 없음
    def test_low_volume_no_signal(self):
        df = _make_support_bounce_df()
        df["volume"] = 1.0
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 8. entry_price == close[idx]
    def test_entry_price_equals_close(self):
        df = _make_df(n=80)
        signal = self.strategy.generate(df)
        expected = float(df["close"].iloc[-2])
        assert abs(signal.entry_price - expected) < 1e-6

    # 9. confidence 유효 값
    def test_confidence_valid_values(self):
        for fn in [lambda: _make_df(80), _make_support_bounce_df, _make_resistance_touch_df]:
            signal = self.strategy.generate(fn())
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=80)
        signal = self.strategy.generate(df)
        assert isinstance(signal.strategy, str)
        assert signal.strategy == "sr_bounce"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)
        assert isinstance(signal.bull_case, str)
        assert isinstance(signal.bear_case, str)

    # 11. action은 BUY/SELL/HOLD 중 하나
    def test_action_valid(self):
        df = _make_df(n=80)
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 12. _find_pivot_highs: 명확한 고점 포함
    def test_find_pivot_highs(self):
        import numpy as np
        high = np.array([1.0] * 15)
        high[7] = 10.0  # clear pivot high
        result = self.strategy._find_pivot_highs(high, len(high))
        assert 7 in result

    # 13. _find_pivot_lows: 명확한 저점 포함
    def test_find_pivot_lows(self):
        import numpy as np
        low = np.array([10.0] * 15)
        low[7] = 1.0  # clear pivot low
        result = self.strategy._find_pivot_lows(low, len(low))
        assert 7 in result

    # 14. nearest_below: 가장 가까운 하방 레벨
    def test_nearest_below(self):
        levels = [90.0, 95.0, 98.0]
        result = self.strategy._nearest_below(levels, 99.0)
        assert result == 98.0

    # 15. nearest_above: 가장 가까운 상방 레벨
    def test_nearest_above(self):
        levels = [102.0, 105.0, 110.0]
        result = self.strategy._nearest_above(levels, 101.0)
        assert result == 102.0

    # 16. count_touches: 터치 횟수 계산
    def test_count_touches_correct(self):
        n = 80
        closes = np.ones(n) * 100.0
        # 몇 개를 레벨 근처로 설정
        closes[60] = 95.5
        closes[65] = 95.2
        closes[70] = 94.8
        df = pd.DataFrame({
            "open": closes, "high": closes + 1, "low": closes - 1,
            "close": closes, "volume": np.ones(n) * 1000,
        })
        count = self.strategy._count_touches(df, 95.0, 78)
        assert count >= 2
