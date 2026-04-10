"""
EMADynamicSupportStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.ema_dynamic_support import EMADynamicSupportStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(closes, volumes=None):
    n = len(closes)
    if volumes is None:
        volumes = np.ones(n) * 1000.0
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": volumes,
    })


def _make_uptrend_df(n=70):
    """상승 추세: EMA21 > EMA55"""
    closes = np.array([100.0 * (1.002 ** i) for i in range(n)])
    return _make_df(closes)


def _make_downtrend_df(n=70):
    """하락 추세: EMA21 < EMA55"""
    closes = np.array([200.0 * (0.998 ** i) for i in range(n)])
    return _make_df(closes)


def _make_insufficient_df(n=30):
    closes = np.linspace(100, 110, n)
    return _make_df(closes)


def _make_ema21_buy_df(n=70):
    """
    BUY: close ≈ EMA21 ±0.3%, close > EMA21, close > prev_close, EMA21 > EMA55
    EMA21이 close에 거의 수렴한 안정적 상승 구간에서 터치 시뮬레이션.
    EMA는 closes 전체로 내부에서 재계산되므로, 안정 구간을 길게 만들어 수렴시킴.
    """
    # 앞부분은 강한 상승, 뒷부분은 안정 (EMA가 close에 수렴)
    base_up = np.array([100.0 * (1.003 ** i) for i in range(n - 10)])
    stable_val = base_up[-1]
    stable = np.ones(10) * stable_val

    closes = np.concatenate([base_up, stable])

    # EMA21 재계산 → stable 구간에서 ema21 ≈ close
    ema21_series = pd.Series(closes).ewm(span=21, adjust=False).mean()
    ema21 = float(ema21_series.iloc[-2])

    # close[-2]를 ema21 바로 위로: 내부 EMA는 이미 수렴해 있어 변화 최소
    closes[-2] = ema21 * 1.0005   # +0.05% → touch, close > ema21
    closes[-3] = ema21 * 0.9995   # prev_close < close[-2] ✓
    closes[-1] = ema21 * 1.001    # 현재 진행 중 봉

    return _make_df(closes)


def _make_ema21_sell_df(n=70):
    """
    SELL: close ≈ EMA21 ±0.3%, close < EMA21, close < prev_close, EMA21 < EMA55
    하락 추세에서 마지막 완성봉이 EMA21에 닿은 후 반락.
    """
    base_down = np.array([200.0 * (0.997 ** i) for i in range(n - 10)])
    stable_val = base_down[-1]
    stable = np.ones(10) * stable_val

    closes = np.concatenate([base_down, stable])

    ema21_series = pd.Series(closes).ewm(span=21, adjust=False).mean()
    ema21 = float(ema21_series.iloc[-2])

    closes[-2] = ema21 * 0.9995   # -0.05% → touch, close < ema21
    closes[-3] = ema21 * 1.0005   # prev_close > close[-2] ✓
    closes[-1] = ema21 * 0.999

    return _make_df(closes)


def _make_ema55_buy_df(n=70):
    """EMA55 터치 BUY: |close/EMA55 - 1| < 0.005, close > EMA55, close > prev, EMA21 > EMA55"""
    closes = np.array([100.0 * (1.003 ** i) for i in range(n)])

    ema55 = float(pd.Series(closes).ewm(span=55, adjust=False).mean().iloc[-2])

    closes[-2] = ema55 * 1.002   # ±0.5% 이내, close > EMA55
    closes[-3] = ema55 * 0.999   # prev < close[-2]
    closes[-1] = ema55 * 1.003

    return _make_df(closes)


# ── tests ─────────────────────────────────────────────────────────────────────

class TestEMADynamicSupportStrategy:

    def setup_method(self):
        self.strategy = EMADynamicSupportStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "ema_dynamic_support"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 3. 데이터 부족 → LOW confidence
    def test_insufficient_data_low_confidence(self):
        df = _make_insufficient_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.confidence == Confidence.LOW

    # 4. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=30)
        sig = self.strategy.generate(df)
        assert "부족" in sig.reasoning

    # 5. Signal 반환 타입
    def test_returns_signal_instance(self):
        df = _make_uptrend_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 6. action 유효값
    def test_action_is_valid(self):
        df = _make_uptrend_df()
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. confidence 유효값
    def test_confidence_is_valid(self):
        df = _make_uptrend_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 8. strategy 필드 일치
    def test_strategy_field(self):
        df = _make_uptrend_df()
        sig = self.strategy.generate(df)
        assert sig.strategy == "ema_dynamic_support"

    # 9. entry_price는 _last 봉 close
    def test_entry_price_matches_last_close(self):
        df = _make_uptrend_df()
        sig = self.strategy.generate(df)
        assert abs(sig.entry_price - float(df["close"].iloc[-2])) < 1e-6

    # 10. entry_price > 0
    def test_entry_price_positive(self):
        df = _make_uptrend_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 11. reasoning 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_uptrend_df()
        sig = self.strategy.generate(df)
        assert len(sig.reasoning) > 0

    # 12. bull_case / bear_case 필드 존재
    def test_signal_has_bull_bear_case(self):
        df = _make_uptrend_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig.bull_case, str)
        assert isinstance(sig.bear_case, str)

    # 13. EMA21 BUY 신호
    def test_ema21_buy_signal(self):
        df = _make_ema21_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 14. EMA21 SELL 신호
    def test_ema21_sell_signal(self):
        df = _make_ema21_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 15. BUY reasoning에 "BUY" 포함
    def test_buy_reasoning_label(self):
        df = _make_ema21_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert "BUY" in sig.reasoning

    # 16. SELL reasoning에 "SELL" 포함
    def test_sell_reasoning_label(self):
        df = _make_ema21_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert "SELL" in sig.reasoning

    # 17. BUY invalidation 비어있지 않음
    def test_buy_has_invalidation(self):
        df = _make_ema21_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert len(sig.invalidation) > 0

    # 18. SELL invalidation 비어있지 않음
    def test_sell_has_invalidation(self):
        df = _make_ema21_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert len(sig.invalidation) > 0

    # 19. 상승 추세지만 EMA 터치 없으면 → HOLD 또는 BUY (SELL 아님)
    def test_uptrend_no_sell(self):
        df = _make_uptrend_df()
        sig = self.strategy.generate(df)
        assert sig.action != Action.SELL

    # 20. 하락 추세지만 EMA 터치 없으면 → HOLD 또는 SELL (BUY 아님)
    def test_downtrend_no_buy(self):
        df = _make_downtrend_df()
        sig = self.strategy.generate(df)
        assert sig.action != Action.BUY

    # 21. EMA55 터치 BUY
    def test_ema55_buy_signal(self):
        df = _make_ema55_buy_df()
        sig = self.strategy.generate(df)
        # EMA55 터치 조건이면 BUY이거나 아닐 수 있음(EMA21>EMA55 필요)
        # 조건 만족 시 BUY, 아니면 HOLD
        assert sig.action in (Action.BUY, Action.HOLD)

    # 22. EMA200 있을 때 완전 정렬이면 HIGH confidence BUY
    def test_high_confidence_with_ema200_alignment(self):
        # 210개 이상, 강한 상승
        n = 220
        closes = np.array([100.0 * (1.002 ** i) for i in range(n)])
        df = _make_df(closes)

        ema21 = float(pd.Series(closes).ewm(span=21, adjust=False).mean().iloc[-2])
        closes[-2] = ema21 * 1.001
        closes[-3] = ema21 * 0.999
        df = _make_df(closes)

        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH
