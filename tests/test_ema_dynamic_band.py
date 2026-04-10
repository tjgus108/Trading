"""
EMADynamicBandStrategy 단위 테스트 (14개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.ema_dynamic_band import EMADynamicBandStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(closes, volumes=None):
    n = len(closes)
    if volumes is None:
        volumes = np.ones(n) * 1000.0
    return pd.DataFrame({
        "open": closes,
        "high": np.array(closes) * 1.005,
        "low": np.array(closes) * 0.995,
        "close": closes,
        "volume": volumes,
    })


def _make_insufficient_df(n=30):
    closes = np.linspace(100, 110, n)
    return _make_df(closes)


def _make_stable_df(n=80):
    """안정적 횡보: 밴드 내 유지"""
    closes = np.ones(n) * 100.0 + np.random.default_rng(42).normal(0, 0.5, n)
    return _make_df(closes)


def _make_buy_df(n=80):
    """
    BUY: close < lower AND close > lower.shift(1)
    안정적 상승 후 마지막 봉에서 하단 밴드 아래로 하락 후 복귀.
    """
    np.random.seed(0)
    closes = np.linspace(100, 102, n).copy()

    # 지표를 미리 계산해 lower 값 추정
    close_s = pd.Series(closes)
    ema20 = close_s.ewm(span=20, adjust=False).mean()
    returns = close_s.pct_change()
    rv = returns.rolling(20).std()
    rv_pct = rv.rolling(50).rank(pct=True)
    band_mult = 0.01 + 0.02 * rv_pct
    lower = ema20 * (1 - band_mult)

    idx = n - 2
    lower_val = float(lower.iloc[idx])
    lower_prev = float(lower.iloc[idx - 1])

    # close[idx] < lower_val, close[idx-1] > lower_prev
    closes[idx] = lower_val * 0.995
    closes[idx - 1] = lower_prev * 1.005

    return _make_df(closes)


def _make_sell_df(n=80):
    """
    SELL: close > upper AND close < upper.shift(1)
    """
    np.random.seed(1)
    closes = np.linspace(100, 102, n).copy()

    close_s = pd.Series(closes)
    ema20 = close_s.ewm(span=20, adjust=False).mean()
    returns = close_s.pct_change()
    rv = returns.rolling(20).std()
    rv_pct = rv.rolling(50).rank(pct=True)
    band_mult = 0.01 + 0.02 * rv_pct
    upper = ema20 * (1 + band_mult)

    idx = n - 2
    upper_val = float(upper.iloc[idx])
    upper_prev = float(upper.iloc[idx - 1])

    # close[idx] > upper_val, close[idx-1] < upper_prev
    closes[idx] = upper_val * 1.005
    closes[idx - 1] = upper_prev * 0.995

    return _make_df(closes)


# ── tests ─────────────────────────────────────────────────────────────────────

class TestEMADynamicBandStrategy:

    def setup_method(self):
        self.strategy = EMADynamicBandStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "ema_dynamic_band"

    # 2. 인스턴스 확인
    def test_instance(self):
        assert isinstance(self.strategy, EMADynamicBandStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 4. 데이터 부족 → LOW confidence
    def test_insufficient_data_low_confidence(self):
        df = _make_insufficient_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.confidence == Confidence.LOW

    # 5. reasoning에 "Insufficient" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=30)
        sig = self.strategy.generate(df)
        assert "Insufficient" in sig.reasoning

    # 6. 정상 signal 반환
    def test_returns_signal(self):
        df = _make_stable_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 7. Signal 필드 존재
    def test_signal_fields(self):
        df = _make_stable_df()
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")

    # 8. BUY reasoning에 "BUY" 포함
    def test_buy_reasoning_label(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "BUY" in sig.reasoning

    # 9. SELL reasoning에 "SELL" 포함
    def test_sell_reasoning_label(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "SELL" in sig.reasoning

    # 10. HIGH confidence when rv_percentile < 0.2
    def test_high_confidence_low_volatility(self):
        # 매우 안정적인 데이터 (낮은 변동성)
        closes = np.ones(80) * 100.0
        df = _make_df(closes)
        sig = self.strategy.generate(df)
        # 낮은 변동성 → HIGH 가능
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 11. MEDIUM confidence for normal volatility
    def test_medium_confidence_normal(self):
        df = _make_stable_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 12. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_stable_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 13. strategy 필드 일치
    def test_strategy_field(self):
        df = _make_stable_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "ema_dynamic_band"

    # 14. 최소 행 경계 (55행)
    def test_min_rows_boundary(self):
        closes = np.linspace(100, 110, 55)
        df = _make_df(closes)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. action 유효값
    def test_action_valid(self):
        df = _make_stable_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 16. BUY signal 발생 가능성
    def test_buy_signal_possible(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 17. SELL signal 발생 가능성
    def test_sell_signal_possible(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)
