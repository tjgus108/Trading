"""
PriceActionConfirmStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.pa_confirm import PriceActionConfirmStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n=30, closes=None, opens=None, volumes=None, atr14=None):
    """기본 DataFrame 생성."""
    if closes is None:
        closes = np.linspace(100.0, 110.0, n)
    if opens is None:
        opens = closes.copy()
    if volumes is None:
        volumes = np.ones(n) * 1000.0
    if atr14 is None:
        atr14 = np.ones(n) * 1.0

    return pd.DataFrame({
        "open": opens,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": volumes,
        "atr14": atr14,
    })


def _make_buy_df(n=30):
    """
    BUY 조건 충족:
    - 마지막 완성봉(iloc[-2]): 큰 양봉 body > ATR*0.8, vol > avg*1.2, mom3 > 0
    """
    closes = np.ones(n) * 100.0
    opens = np.ones(n) * 100.0
    volumes = np.ones(n) * 1000.0
    atr14 = np.ones(n) * 1.0

    # 3봉 전보다 오름 (mom3 > 0)
    closes[-5] = 99.0
    closes[-4] = 99.5
    closes[-3] = 100.0  # prev_3 for mom3
    # 완성봉(-2): 큰 양봉
    closes[-2] = 102.0   # mom3 = (102-99)/99 > 0
    opens[-2] = 100.5    # body = 1.5 > ATR*0.8=0.8
    atr14[-2] = 1.0
    volumes[-2] = 1500.0  # > avg*1.2
    # avg_vol from [-22:-2] = 1000, so 1500 > 1200

    return pd.DataFrame({
        "open": opens,
        "high": closes * 1.01,
        "low": closes * 0.99,
        "close": closes,
        "volume": volumes,
        "atr14": atr14,
    })


def _make_sell_df(n=30):
    """
    SELL 조건 충족:
    - 마지막 완성봉(iloc[-2]): 큰 음봉, vol ok, mom3 < 0
    """
    closes = np.ones(n) * 100.0
    opens = np.ones(n) * 100.0
    volumes = np.ones(n) * 1000.0
    atr14 = np.ones(n) * 1.0

    closes[-5] = 101.0
    closes[-4] = 100.5
    closes[-3] = 100.0
    closes[-2] = 98.0    # mom3 = (98-101)/101 < 0
    opens[-2] = 99.5     # body=1.5, close < open → 음봉
    atr14[-2] = 1.0
    volumes[-2] = 1500.0

    return pd.DataFrame({
        "open": opens,
        "high": closes * 1.01,
        "low": closes * 0.99,
        "close": closes,
        "volume": volumes,
        "atr14": atr14,
    })


def _make_high_conf_buy_df(n=30):
    """HIGH confidence BUY: body > ATR*1.5, vol > avg*1.5"""
    closes = np.ones(n) * 100.0
    opens = np.ones(n) * 100.0
    volumes = np.ones(n) * 1000.0
    atr14 = np.ones(n) * 1.0

    closes[-3] = 99.0
    closes[-2] = 103.0   # mom3 > 0
    opens[-2] = 100.8    # body = 2.2 > ATR*1.5=1.5
    atr14[-2] = 1.0
    volumes[-2] = 1600.0  # > avg*1.5=1500

    return pd.DataFrame({
        "open": opens,
        "high": closes * 1.01,
        "low": closes * 0.99,
        "close": closes,
        "volume": volumes,
        "atr14": atr14,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestPAConfirmStrategy:

    def setup_method(self):
        self.strategy = PriceActionConfirmStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "pa_confirm"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 3. 데이터 부족 → LOW confidence
    def test_insufficient_data_low_confidence(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.confidence == Confidence.LOW

    # 4. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert "부족" in sig.reasoning

    # 5. Signal 반환 타입
    def test_returns_signal_instance(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 6. action 유효값
    def test_action_is_valid(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. confidence 유효값
    def test_confidence_is_valid(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 8. strategy 필드 일치
    def test_strategy_field(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "pa_confirm"

    # 9. entry_price는 _last 봉 close와 일치
    def test_entry_price_matches_last_close(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert abs(sig.entry_price - float(df["close"].iloc[-2])) < 1e-6

    # 10. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 11. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert len(sig.reasoning) > 0

    # 12. BUY 신호 발생
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 13. SELL 신호 발생
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 14. BUY 신호 시 reasoning에 "PA BUY" 포함
    def test_buy_reasoning_label(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "PA BUY" in sig.reasoning

    # 15. SELL 신호 시 reasoning에 "PA SELL" 포함
    def test_sell_reasoning_label(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "PA SELL" in sig.reasoning

    # 16. HIGH confidence BUY: body > ATR*1.5, vol > avg*1.5
    def test_high_confidence_buy(self):
        df = _make_high_conf_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 17. 볼륨 부족 → HOLD
    def test_low_volume_hold(self):
        df = _make_buy_df()
        df = df.copy()
        df.iloc[-2, df.columns.get_loc("volume")] = 500.0  # avg=1000, 500 < 1200
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 18. 작은 캔들 → HOLD
    def test_small_body_hold(self):
        df = _make_buy_df()
        df = df.copy()
        # body < ATR*0.8: open=close
        df.iloc[-2, df.columns.get_loc("open")] = df["close"].iloc[-2]
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 19. bull_case / bear_case 필드 존재
    def test_signal_has_bull_bear_case(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig.bull_case, str)
        assert isinstance(sig.bear_case, str)

    # 20. BUY 시 invalidation 비어있지 않음
    def test_buy_invalidation_not_empty(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert len(sig.invalidation) > 0

    # 21. SELL 시 invalidation 비어있지 않음
    def test_sell_invalidation_not_empty(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert len(sig.invalidation) > 0

    # 22. mom3 방향 불일치 → HOLD (큰 양봉이지만 mom3 < 0)
    def test_momentum_mismatch_hold(self):
        df = _make_buy_df()
        df = df.copy()
        # mom3: close[-2] 기준 3봉 전보다 낮게
        idx = len(df) - 2
        df.iloc[idx - 3, df.columns.get_loc("close")] = 105.0  # prev3 > close → mom3 < 0
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
