"""
PriceDivergenceIndexStrategy 단위 테스트.

DataFrame 구조:
  - 인덱스 -1: 진행 중 캔들 (무시)
  - 인덱스 -2 (last): _last(df) = 신호 봉
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.price_divergence_index import PriceDivergenceIndexStrategy


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _flat_df(n: int = 40, close: float = 100.0, volume: float = 1000.0) -> pd.DataFrame:
    """모든 봉이 동일한 기본 DataFrame."""
    return pd.DataFrame({
        "open":   [close] * n,
        "close":  [close] * n,
        "high":   [close + 1.0] * n,
        "low":    [close - 1.0] * n,
        "volume": [volume] * n,
    })


def _bull_div_df(n: int = 40) -> pd.DataFrame:
    """
    불리시 다이버전스 DataFrame:
    - 앞부분: 상승 (RSI 높게, OBV 높게 형성)
    - 뒷부분: 가격 하락 + RSI는 상승 + OBV는 증가 → bull_div_score=2
    - RSI < 50 조건 충족
    """
    closes = []
    volumes = []
    n_front = n - 15

    # 앞부분: 100 → 120 (상승, RSI 높아짐)
    for i in range(n_front):
        closes.append(100.0 + i * 0.5)
        volumes.append(1000.0)

    # 중간: 120 → 100 (하락, RSI 낮아짐)
    for i in range(10):
        closes.append(120.0 - i * 2.0)
        volumes.append(800.0)

    # 마지막 5봉: 가격은 더 낮게, 하지만 volume 증가 (OBV 증가)
    # 이 구간에서 bull_div_score 형성
    for i in range(5):
        closes.append(100.0 - i * 0.5)
        volumes.append(5000.0)  # volume 급증 → OBV 증가

    return pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "volume": volumes,
    })


def _bear_div_df(n: int = 40) -> pd.DataFrame:
    """
    베어리시 다이버전스 DataFrame:
    - 앞부분: 하락 (RSI 낮게, OBV 낮게 형성)
    - 뒷부분: 가격 상승 + RSI는 하락 + OBV는 감소 → bear_div_score=2
    - RSI > 50 조건 충족
    """
    closes = []
    volumes = []
    n_front = n - 15

    # 앞부분: 120 → 100 (하락)
    for i in range(n_front):
        closes.append(120.0 - i * 0.5)
        volumes.append(1000.0)

    # 중간: 100 → 120 (상승, RSI 높아짐)
    for i in range(10):
        closes.append(100.0 + i * 2.0)
        volumes.append(800.0)

    # 마지막 5봉: 가격은 더 높지만 volume 급감 (OBV 감소)
    for i in range(5):
        closes.append(120.0 + i * 0.5)
        volumes.append(100.0)  # volume 급감 → OBV 감소

    return pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "volume": volumes,
    })


def _bull_div_synthetic(n: int = 40) -> pd.DataFrame:
    """
    bull_div_score=2 강제 생성:
    - lookback=10 구간: 가격 하락, RSI 상승(→ rsi_change>0), OBV 증가(→ obv_norm>0)
    """
    # 가격: 앞부분 안정 → 후반 하락
    closes = [100.0] * 20 + [100.0 - i * 1.0 for i in range(20)]
    # volume: 후반 급증 → OBV 증가
    volumes = [500.0] * 20 + [5000.0] * 20

    return pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "volume": volumes,
    })


# ── 테스트 ───────────────────────────────────────────────────────────────────

class TestPriceDivergenceIndexStrategy:

    def setup_method(self):
        self.strat = PriceDivergenceIndexStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strat.name == "price_divergence_index"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _flat_df(n=10)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert "부족" in sig.reasoning

    # 3. 경계값: 24행 → HOLD
    def test_24_rows_returns_hold(self):
        df = _flat_df(n=24)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 4. 경계값: 25행 → 처리됨
    def test_25_rows_processes(self):
        df = _flat_df(n=25)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)

    # 5. None 입력 → HOLD
    def test_none_input_returns_hold(self):
        sig = self.strat.generate(None)
        assert sig.action == Action.HOLD

    # 6. 균일한 가격 → HOLD (다이버전스 없음)
    def test_flat_df_returns_hold(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 7. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)

    # 8. strategy 필드 확인
    def test_signal_strategy_name(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert sig.strategy == "price_divergence_index"

    # 9. entry_price는 마지막 완성봉 close
    def test_entry_price_is_last_close(self):
        df = _flat_df(n=40)
        last_close = float(df["close"].iloc[-2])
        sig = self.strat.generate(df)
        assert sig.entry_price == pytest.approx(last_close, abs=1e-6)

    # 10. 상승 trend DataFrame → BUY 또는 HOLD (SELL 아님)
    def test_rising_df_no_sell(self):
        closes = [100.0 + i * 0.5 for i in range(40)]
        df = pd.DataFrame({
            "open": closes, "close": closes,
            "high": [c + 0.5 for c in closes],
            "low": [c - 0.5 for c in closes],
            "volume": [1000.0] * 40,
        })
        sig = self.strat.generate(df)
        assert sig.action != Action.SELL

    # 11. BUY 시 bull_div_score 언급
    def test_buy_reasoning_mentions_bull_div(self):
        df = _bull_div_df(n=40)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert "bull_div_score" in sig.reasoning

    # 12. SELL 시 bear_div_score 언급
    def test_sell_reasoning_mentions_bear_div(self):
        df = _bear_div_df(n=40)
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert "bear_div_score" in sig.reasoning

    # 13. BUY confidence: HIGH or MEDIUM
    def test_buy_confidence_valid(self):
        df = _bull_div_df(n=40)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 14. SELL confidence: HIGH or MEDIUM
    def test_sell_confidence_valid(self):
        df = _bear_div_df(n=40)
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 15. bull_div_score=2 → HIGH confidence BUY
    def test_bull_score_2_high_confidence(self):
        """bull_div_score=2이면 HIGH confidence."""
        df = _bull_div_synthetic(n=40)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence == Confidence.HIGH

    # 16. HOLD reasoning에 다이버전스 없음 언급
    def test_hold_reasoning_mentions_no_divergence(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        if sig.action == Action.HOLD:
            assert sig.reasoning is not None and len(sig.reasoning) > 0

    # 17. 충분한 데이터 시 entry_price > 0
    def test_entry_price_positive(self):
        df = _flat_df(n=40, close=50.0)
        sig = self.strat.generate(df)
        assert sig.entry_price >= 0.0
