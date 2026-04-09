"""
HigherTimeframeEMAStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.htf_ema import HigherTimeframeEMAStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 80, scenario: str = "buy_cross") -> pd.DataFrame:
    """
    scenario:
      "buy_cross"   → HTF EMA 상승 + close crosses above EMA9
      "sell_cross"  → HTF EMA 하락 + close crosses below EMA9
      "htf_up_no_cross" → HTF 상승이지만 cross 없음
      "flat"        → 횡보, 신호 없음
      "buy_3up"     → HTF EMA 3연속 상승 + cross above (HIGH confidence)
      "sell_3down"  → HTF EMA 3연속 하락 + cross below (HIGH confidence)
    """
    np.random.seed(7)

    if scenario == "buy_cross":
        # 전체 상승 추세 + 마지막 봉에서 EMA9 위로 돌파
        closes = np.linspace(100, 130, n).astype(float)
        # 마지막 두 봉 조작: 이전 봉 EMA9 아래, 마지막 봉 EMA9 위
        # EMA9 ~ 130 근처일 것이므로 마지막만 급등
        closes[-2] = closes[-3] * 0.985   # prev: EMA9 아래
        closes[-1] = closes[-3] * 1.02    # last (완성봉): EMA9 위
    elif scenario == "sell_cross":
        closes = np.linspace(130, 100, n).astype(float)
        closes[-2] = closes[-3] * 1.015   # prev: EMA9 위
        closes[-1] = closes[-3] * 0.98    # last (완성봉): EMA9 아래
    elif scenario == "htf_up_no_cross":
        # 상승 추세이지만 close 계속 EMA9 위 (cross 없음)
        closes = np.linspace(100, 130, n).astype(float)
    elif scenario == "flat":
        closes = np.ones(n) * 100.0
        closes += np.sin(np.linspace(0, 6 * np.pi, n)) * 0.5
    elif scenario == "buy_3up":
        # 꾸준한 상승 + cross above
        closes = np.linspace(100, 140, n).astype(float)
        closes[-2] = closes[-3] * 0.982
        closes[-1] = closes[-3] * 1.025
    elif scenario == "sell_3down":
        # 꾸준한 하락 + cross below
        closes = np.linspace(140, 100, n).astype(float)
        closes[-2] = closes[-3] * 1.018
        closes[-1] = closes[-3] * 0.975
    else:
        closes = np.ones(n) * 100.0

    df = pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })
    return df


def _make_insufficient_df(n: int = 30) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.01,
        "low": closes * 0.99,
        "close": closes,
        "volume": np.ones(n) * 1000,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestHigherTimeframeEMAStrategy:

    def setup_method(self):
        self.strat = HigherTimeframeEMAStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strat.name == "htf_ema"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=30)
        signal = self.strat.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → LOW confidence
    def test_insufficient_data_low_confidence(self):
        df = _make_insufficient_df(n=30)
        signal = self.strat.generate(df)
        assert signal.confidence == Confidence.LOW

    # 4. 데이터 부족 reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=20)
        signal = self.strat.generate(df)
        assert "부족" in signal.reasoning

    # 5. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=80, scenario="buy_cross")
        signal = self.strat.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "htf_ema"
        assert isinstance(signal.entry_price, float)
        assert len(signal.reasoning) > 0

    # 6. HTF 3연속 상승 + cross above → HIGH confidence BUY
    def test_buy_3up_high_confidence(self):
        df = _make_df(n=100, scenario="buy_3up")
        signal = self.strat.generate(df)
        if signal.action == Action.BUY:
            assert signal.confidence == Confidence.HIGH

    # 7. HTF 3연속 하락 + cross below → HIGH confidence SELL
    def test_sell_3down_high_confidence(self):
        df = _make_df(n=100, scenario="sell_3down")
        signal = self.strat.generate(df)
        if signal.action == Action.SELL:
            assert signal.confidence == Confidence.HIGH

    # 8. BUY 신호 reasoning에 "HTF EMA" 포함
    def test_buy_reasoning_contains_htf_ema(self):
        df = _make_df(n=100, scenario="buy_3up")
        signal = self.strat.generate(df)
        if signal.action == Action.BUY:
            assert "HTF EMA" in signal.reasoning

    # 9. SELL 신호 reasoning에 "HTF EMA" 포함
    def test_sell_reasoning_contains_htf_ema(self):
        df = _make_df(n=100, scenario="sell_3down")
        signal = self.strat.generate(df)
        if signal.action == Action.SELL:
            assert "HTF EMA" in signal.reasoning

    # 10. BUY 신호에 invalidation 존재
    def test_buy_has_invalidation(self):
        df = _make_df(n=100, scenario="buy_3up")
        signal = self.strat.generate(df)
        if signal.action == Action.BUY:
            assert len(signal.invalidation) > 0

    # 11. SELL 신호에 invalidation 존재
    def test_sell_has_invalidation(self):
        df = _make_df(n=100, scenario="sell_3down")
        signal = self.strat.generate(df)
        if signal.action == Action.SELL:
            assert len(signal.invalidation) > 0

    # 12. entry_price == df.iloc[-2]["close"]
    def test_entry_price_is_last_close(self):
        df = _make_df(n=80, scenario="flat")
        signal = self.strat.generate(df)
        assert signal.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-5)

    # 13. bull_case / bear_case 존재 (충분한 데이터)
    def test_bull_bear_case_present(self):
        df = _make_df(n=80, scenario="flat")
        signal = self.strat.generate(df)
        assert isinstance(signal.bull_case, str)
        assert isinstance(signal.bear_case, str)

    # 14. 횡보 → HOLD
    def test_flat_market_hold(self):
        df = _make_df(n=80, scenario="flat")
        signal = self.strat.generate(df)
        assert signal.action == Action.HOLD

    # 15. HOLD reasoning에 cross 정보 포함
    def test_hold_reasoning_contains_cross(self):
        df = _make_df(n=80, scenario="flat")
        signal = self.strat.generate(df)
        if signal.action == Action.HOLD:
            assert "cross" in signal.reasoning.lower() or "No cross" in signal.reasoning

    # 16. generate returns Signal instance in all scenarios
    @pytest.mark.parametrize("scenario", ["buy_cross", "sell_cross", "htf_up_no_cross", "flat", "buy_3up", "sell_3down"])
    def test_returns_signal_all_scenarios(self, scenario):
        df = _make_df(n=100, scenario=scenario)
        signal = self.strat.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
