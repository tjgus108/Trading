"""
TrendMomentumScoreStrategy 단위 테스트.

DataFrame 구조:
  - 인덱스 -1: 진행 중 캔들 (무시)
  - 인덱스 -2 (last): _last(df) = 신호 봉
"""

import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.trend_momentum_score import TrendMomentumScoreStrategy


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _flat_df(n: int = 40, close: float = 100.0) -> pd.DataFrame:
    return pd.DataFrame({
        "open":   [close] * n,
        "close":  [close] * n,
        "high":   [close + 1.0] * n,
        "low":    [close - 1.0] * n,
        "volume": [1000.0] * n,
    })


def _bull_df(n: int = 50) -> pd.DataFrame:
    """
    강한 상승 추세: total_bull=5 → HIGH BUY
    - close > ema10 > ema20 > ema50 (trend_score=3)
    - roc5 > 0, roc10 > 0 (mom_score=2)
    """
    # 충분히 긴 상승 추세로 EMA 정렬 확실히 형성
    closes = [100.0 + i * 1.0 for i in range(n)]
    return pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })


def _bear_df(n: int = 50) -> pd.DataFrame:
    """
    강한 하락 추세: total_bull=0 → HIGH SELL
    - close < ema10 < ema20 < ema50 (trend_score=0)
    - roc5 < 0, roc10 < 0 (mom_score=0)
    """
    closes = [150.0 - i * 1.0 for i in range(n)]
    return pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })


def _medium_bull_df(n: int = 50) -> pd.DataFrame:
    """
    중간 상승: total_bull=4 → MEDIUM BUY
    - 상승하다가 마지막 몇 봉 약간 조정
    """
    closes = [100.0 + i * 0.8 for i in range(n - 5)] + [130.0 + i * 0.3 for i in range(5)]
    return pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })


# ── 테스트 ───────────────────────────────────────────────────────────────────

class TestTrendMomentumScoreStrategy:

    def setup_method(self):
        self.strat = TrendMomentumScoreStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strat.name == "trend_momentum_score"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _flat_df(n=10)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert "부족" in sig.reasoning

    # 3. 경계값: 29행 → HOLD
    def test_29_rows_returns_hold(self):
        df = _flat_df(n=29)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 4. 경계값: 30행 → 처리됨
    def test_30_rows_processes(self):
        df = _flat_df(n=30)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)

    # 5. None 입력 → HOLD
    def test_none_input_returns_hold(self):
        sig = self.strat.generate(None)
        assert sig.action == Action.HOLD

    # 6. 강한 상승 → BUY
    def test_bull_df_returns_buy(self):
        df = _bull_df(n=60)
        sig = self.strat.generate(df)
        assert sig.action == Action.BUY

    # 7. 강한 상승 → HIGH confidence (total_bull=5)
    def test_bull_df_high_confidence(self):
        df = _bull_df(n=60)
        sig = self.strat.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 8. 강한 하락 → SELL
    def test_bear_df_returns_sell(self):
        df = _bear_df(n=60)
        sig = self.strat.generate(df)
        assert sig.action == Action.SELL

    # 9. 강한 하락 → HIGH confidence (total_bull=0)
    def test_bear_df_high_confidence(self):
        df = _bear_df(n=60)
        sig = self.strat.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 10. 균일한 가격 → total_bull=0 (close==ema, roc==0) → SELL or HOLD
    def test_flat_df_not_buy(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert sig.action != Action.BUY

    # 11. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)

    # 12. strategy 필드 확인
    def test_signal_strategy_name(self):
        df = _bull_df(n=60)
        sig = self.strat.generate(df)
        assert sig.strategy == "trend_momentum_score"

    # 13. entry_price는 마지막 완성봉 close
    def test_entry_price_is_last_close(self):
        df = _bull_df(n=60)
        last_close = float(df["close"].iloc[-2])
        sig = self.strat.generate(df)
        assert sig.entry_price == pytest.approx(last_close, abs=1e-6)

    # 14. BUY reasoning에 total_bull 언급
    def test_buy_reasoning_mentions_total_bull(self):
        df = _bull_df(n=60)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert "total_bull" in sig.reasoning

    # 15. SELL reasoning에 total_bull 언급
    def test_sell_reasoning_mentions_total_bull(self):
        df = _bear_df(n=60)
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert "total_bull" in sig.reasoning

    # 16. BUY confidence: HIGH or MEDIUM
    def test_buy_confidence_valid(self):
        df = _bull_df(n=60)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 17. SELL confidence: HIGH or MEDIUM
    def test_sell_confidence_valid(self):
        df = _bear_df(n=60)
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 18. entry_price > 0
    def test_entry_price_positive(self):
        df = _flat_df(n=40, close=50.0)
        sig = self.strat.generate(df)
        assert sig.entry_price >= 0.0
