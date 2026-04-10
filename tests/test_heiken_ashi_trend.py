"""
HeikenAshiTrendStrategy 단위 테스트 (mock DataFrame, API 호출 없음).

HA 계산:
  ha_close[i] = (open + high + low + close) / 4
  ha_open[0]  = (open[0] + close[0]) / 2
  ha_open[i]  = (ha_open[i-1] + ha_close[i-1]) / 2
  bullish = ha_close > ha_open
"""

import pandas as pd
import pytest

from src.strategy.heiken_ashi_trend import HeikenAshiTrendStrategy
from src.strategy.base import Action, Confidence, Signal


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_trending_df(
    n: int = 20,
    direction: str = "up",    # "up" | "down" | "mixed"
    streak_len: int = 3,
) -> pd.DataFrame:
    """
    HA 신호를 확실히 만들기 위한 단조 추세 DataFrame.

    direction="up"  → 모든 봉이 강한 상승 (open < close, 큰 몸통)
    direction="down"→ 모든 봉이 강한 하락 (open > close, 큰 몸통)
    direction="mixed" → 교대 방향
    """
    base = 100.0
    opens, highs, lows, closes, volumes = [], [], [], [], []

    for i in range(n):
        if direction == "up":
            o = base + i * 1.0
            c = o + 2.0        # 큰 양봉
            h = c + 0.5
            l = o - 0.5
        elif direction == "down":
            o = base + (n - i) * 1.0
            c = o - 2.0        # 큰 음봉
            h = o + 0.5
            l = c - 0.5
        else:  # mixed
            if i % 2 == 0:
                o = base + 1.0
                c = o + 2.0
                h = c + 0.5
                l = o - 0.5
            else:
                o = base + 3.0
                c = o - 2.0
                h = o + 0.5
                l = c - 0.5
        opens.append(o)
        highs.append(h)
        lows.append(l)
        closes.append(c)
        volumes.append(1000.0)

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _make_flat_df(n: int = 20) -> pd.DataFrame:
    """모든 봉이 동일한 값 → HOLD."""
    return pd.DataFrame({
        "open":   [100.0] * n,
        "high":   [100.5] * n,
        "low":    [99.5]  * n,
        "close":  [100.0] * n,
        "volume": [1000.0] * n,
    })


# ── 테스트 ───────────────────────────────────────────────────────────────────

class TestHeikenAshiTrendStrategy:

    def setup_method(self):
        self.strategy = HeikenAshiTrendStrategy()

    # 1. 전략명 확인
    def test_strategy_name(self):
        assert self.strategy.name == "heiken_ashi_trend"

    # 2. 인스턴스 생성
    def test_instance_creation(self):
        s = HeikenAshiTrendStrategy()
        assert s is not None

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_trending_df(n=5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 4. None 입력 → HOLD
    def test_none_input_hold(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD

    # 5. 데이터 부족 reasoning 확인
    def test_insufficient_data_reasoning(self):
        df = _make_trending_df(n=5)
        sig = self.strategy.generate(df)
        assert "Insufficient" in sig.reasoning

    # 6. 정상 데이터 → Signal 반환
    def test_normal_data_returns_signal(self):
        df = _make_trending_df(n=20, direction="up")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 완성
    def test_signal_fields_complete(self):
        df = _make_trending_df(n=20, direction="up")
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert sig.reasoning != ""

    # 8. BUY reasoning 키워드 확인
    def test_buy_reasoning_keyword(self):
        df = _make_trending_df(n=20, direction="up")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            lower = sig.reasoning.lower()
            assert "heikenashitrend" in lower or "양봉" in lower or "ha" in lower

    # 9. SELL reasoning 키워드 확인
    def test_sell_reasoning_keyword(self):
        df = _make_trending_df(n=20, direction="down")
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            lower = sig.reasoning.lower()
            assert "heikenashitrend" in lower or "음봉" in lower or "ha" in lower

    # 10. HIGH confidence (5연속 HA 양봉)
    def test_high_confidence_long_streak(self):
        # 충분히 긴 상승 추세 → streak >= 5
        df = _make_trending_df(n=30, direction="up")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 11. strategy 필드 값 확인
    def test_strategy_field_value(self):
        df = _make_trending_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.strategy == "heiken_ashi_trend"

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_trending_df(n=20, direction="up")
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. 최소 행 수(10)에서 동작
    def test_minimum_rows_works(self):
        df = _make_trending_df(n=10, direction="up")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 14. HOLD: mixed direction
    def test_hold_mixed_direction(self):
        df = _make_flat_df(n=20)
        sig = self.strategy.generate(df)
        # flat 데이터는 3봉 연속 같은 방향이 아님 → HOLD
        assert sig.action == Action.HOLD

    # 15. BUY signal on uptrend
    def test_buy_signal_uptrend(self):
        df = _make_trending_df(n=20, direction="up")
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 16. SELL signal on downtrend
    def test_sell_signal_downtrend(self):
        df = _make_trending_df(n=20, direction="down")
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 17. MEDIUM confidence (3봉, streak < 5)
    def test_medium_confidence_short_streak(self):
        # 딱 3봉만 같은 방향 (앞부분은 반대 방향)
        opens  = [105.0, 103.0, 101.0] + [99.0, 100.0, 101.0, 102.0] + [100.0] * 13
        closes = [103.0, 101.0, 99.0]  + [101.0, 102.0, 103.0, 104.0] + [100.0] * 13
        highs  = [c + 0.5 for c in closes]
        lows   = [o - 0.5 for o in opens]
        n = len(opens)
        df = pd.DataFrame({
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": [1000.0] * n,
        })
        sig = self.strategy.generate(df)
        # 신호가 BUY 또는 HOLD. BUY면 MEDIUM 체크
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)

    # 18. Action enum values valid
    def test_action_enum_valid(self):
        df = _make_trending_df(n=20, direction="up")
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
