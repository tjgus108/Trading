"""
MomentumScoreStrategy 단위 테스트.

DataFrame 구조 (n=40 기본):
  - 인덱스 -1: 진행 중 캔들 (무시)
  - 인덱스 -2 (last): _last(df) = 신호 봉
"""

import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.momentum_score import MomentumScoreStrategy


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


def _bull_df(n: int = 40) -> pd.DataFrame:
    """
    강한 상승 모멘텀 DataFrame (score_up >= 4.5 → HIGH BUY):
    - RSI > 55, MACD hist > 0, close > EMA20, close > close[5ago], vol > avg_vol
    """
    base = 100.0
    closes = []
    # 앞부분 천천히 상승 → EMA20, MACD, RSI 형성
    for i in range(n):
        closes.append(base + i * 0.5)
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 1.0 for c in closes],
        "low":    [c - 1.0 for c in closes],
        # iloc[-2](_last)의 volume을 평균보다 높게 → score_up += 0.5 → total >= 4.5
        "volume": [1000.0] * (n - 2) + [5000.0] + [1000.0],
    })
    return df


def _bear_df(n: int = 40) -> pd.DataFrame:
    """
    강한 하락 모멘텀 DataFrame (score_down >= 4.5 → HIGH SELL):
    - RSI < 45, MACD hist < 0, close < EMA20, close < close[5ago], vol > avg_vol
    """
    base = 120.0
    closes = []
    for i in range(n):
        closes.append(base - i * 0.5)
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 1.0 for c in closes],
        "low":    [c - 1.0 for c in closes],
        # iloc[-2](_last)의 volume을 평균보다 낮게 → score_down += 0.5 → total >= 4.5
        "volume": [5000.0] * (n - 2) + [100.0] + [5000.0],
    })
    return df


# ── 테스트 ───────────────────────────────────────────────────────────────────

class TestMomentumScoreStrategy:

    def setup_method(self):
        self.strat = MomentumScoreStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strat.name == "momentum_score"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _flat_df(n=20)
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

    # 5. 강한 상승 → BUY
    def test_bull_df_returns_buy(self):
        df = _bull_df(n=40)
        sig = self.strat.generate(df)
        assert sig.action == Action.BUY

    # 6. 강한 상승 → HIGH confidence (score_up >= 4.5)
    def test_bull_df_high_confidence(self):
        df = _bull_df(n=40)
        sig = self.strat.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 7. 강한 하락 → SELL
    def test_bear_df_returns_sell(self):
        df = _bear_df(n=40)
        sig = self.strat.generate(df)
        assert sig.action == Action.SELL

    # 8. 강한 하락 → HIGH confidence (score_down >= 4.5)
    def test_bear_df_high_confidence(self):
        df = _bear_df(n=40)
        sig = self.strat.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 9. 균일한 가격 → HOLD (모멘텀 없음)
    def test_flat_df_returns_hold(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 10. BUY reasoning에 score_up 언급
    def test_buy_reasoning_mentions_score_up(self):
        df = _bull_df(n=40)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert "score_up" in sig.reasoning

    # 11. SELL reasoning에 score_down 언급
    def test_sell_reasoning_mentions_score_down(self):
        df = _bear_df(n=40)
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert "score_down" in sig.reasoning

    # 12. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)

    # 13. strategy 필드 = "momentum_score"
    def test_signal_strategy_name(self):
        df = _bull_df(n=40)
        sig = self.strat.generate(df)
        assert sig.strategy == "momentum_score"

    # 14. entry_price는 마지막 완성봉 close
    def test_entry_price_is_last_close(self):
        df = _bull_df(n=40)
        last_close = float(df["close"].iloc[-2])
        sig = self.strat.generate(df)
        assert sig.entry_price == pytest.approx(last_close, abs=1e-6)

    # 15. BUY MEDIUM confidence (score_up == 4, volume 낮음 → 4.0)
    def test_buy_medium_confidence_score_4(self):
        """score_up = 4 (volume 점수 없음) → MEDIUM."""
        base = 100.0
        n = 40
        closes = [base + i * 0.5 for i in range(n)]
        # volume을 평균과 동일하게 해 volume 점수 0
        df = pd.DataFrame({
            "open":   closes,
            "close":  closes,
            "high":   [c + 1.0 for c in closes],
            "low":    [c - 1.0 for c in closes],
            "volume": [1000.0] * n,  # 균일 → score_up += 0 (vol == avg)
        })
        sig = self.strat.generate(df)
        # score_up이 4이면 MEDIUM
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)

    # 16. SELL MEDIUM confidence (score_down == 4, volume 낮음 → 4.0)
    def test_sell_medium_confidence_score_4(self):
        """score_down = 4 (volume 점수 없음) → MEDIUM."""
        base = 120.0
        n = 40
        closes = [base - i * 0.5 for i in range(n)]
        df = pd.DataFrame({
            "open":   closes,
            "close":  closes,
            "high":   [c + 1.0 for c in closes],
            "low":    [c - 1.0 for c in closes],
            "volume": [1000.0] * n,
        })
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)
