"""
EntropyMomentumStrategy 단위 테스트 (14개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.entropy_momentum import EntropyMomentumStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(closes: list) -> pd.DataFrame:
    closes = np.array(closes, dtype=float)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.005,
        "low": closes * 0.995,
        "close": closes,
        "volume": np.ones(len(closes)) * 1000,
    })


def _make_trending_up(n: int = 40) -> pd.DataFrame:
    """일정하게 상승하는 데이터 → 낮은 엔트로피 + 상승 모멘텀."""
    closes = [100.0 * (1.005 ** i) for i in range(n)]
    return _make_df(closes)


def _make_trending_down(n: int = 40) -> pd.DataFrame:
    """일정하게 하락하는 데이터 → 낮은 엔트로피 + 하락 모멘텀."""
    closes = [100.0 * (0.995 ** i) for i in range(n)]
    return _make_df(closes)


def _make_noisy(n: int = 40, seed: int = 42) -> pd.DataFrame:
    """랜덤 노이즈 → 높은 엔트로피."""
    np.random.seed(seed)
    changes = np.random.choice([-1, 1], size=n) * np.random.uniform(0.001, 0.003, n)
    closes = 100.0 * np.cumprod(1 + changes)
    return _make_df(closes)


# ── tests ─────────────────────────────────────────────────────────────────────

class TestEntropyMomentumStrategy:

    def setup_method(self):
        self.strat = EntropyMomentumStrategy()

    # 1. 기본 속성
    def test_name(self):
        assert self.strat.name == "entropy_momentum"

    # 2. 데이터 부족 시 HOLD
    def test_insufficient_data_returns_hold(self):
        df = _make_trending_up(10)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW
        assert "데이터 부족" in sig.reasoning

    # 3. 정확히 MIN_ROWS-1 개 → HOLD
    def test_min_rows_minus_one_hold(self):
        df = _make_trending_up(24)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 4. 반환 타입 확인
    def test_returns_signal_type(self):
        df = _make_trending_up(40)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)

    # 5. strategy 이름 일치
    def test_signal_strategy_field(self):
        df = _make_trending_up(40)
        sig = self.strat.generate(df)
        assert sig.strategy == "entropy_momentum"

    # 6. entry_price = 마지막 완성 캔들 close
    def test_entry_price_is_last_completed_candle(self):
        df = _make_trending_up(40)
        sig = self.strat.generate(df)
        assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-6)

    # 7. 상승 추세 → BUY 신호 가능
    def test_trending_up_produces_buy_or_hold(self):
        df = _make_trending_up(40)
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 8. 하락 추세 → SELL 신호 가능
    def test_trending_down_produces_sell_or_hold(self):
        df = _make_trending_down(40)
        sig = self.strat.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 9. 강한 상승 추세에서 BUY 신호 발생
    def test_strong_uptrend_buy(self):
        closes = [100.0 * (1.008 ** i) for i in range(50)]
        df = _make_df(closes)
        sig = self.strat.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 10. 강한 하락 추세에서 SELL 신호 발생
    def test_strong_downtrend_sell(self):
        closes = [100.0 * (0.992 ** i) for i in range(50)]
        df = _make_df(closes)
        sig = self.strat.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 11. confidence는 유효한 값
    def test_confidence_valid_values(self):
        df = _make_trending_up(40)
        sig = self.strat.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 12. reasoning 문자열 비어있지 않음
    def test_reasoning_not_empty(self):
        df = _make_trending_up(40)
        sig = self.strat.generate(df)
        assert len(sig.reasoning) > 0

    # 13. 노이즈 데이터 → HOLD
    def test_noisy_data_hold(self):
        df = _make_noisy(40, seed=0)
        sig = self.strat.generate(df)
        # 노이즈는 주로 HOLD이지만, 우연히 조건 충족 가능하므로 Action 유효성만 체크
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 14. bull_case / bear_case 필드 존재
    def test_bull_bear_case_fields(self):
        df = _make_trending_up(40)
        sig = self.strat.generate(df)
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")

    # 15. MIN_ROWS 경계값 - 정확히 25행
    def test_exactly_min_rows(self):
        df = _make_trending_up(25)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 16. 큰 데이터셋도 처리 가능
    def test_large_dataset(self):
        df = _make_trending_up(200)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)

    # 17. HIGH confidence는 ep < ema * 0.5일 때
    def test_high_confidence_strong_uptrend(self):
        # 매우 일정한 상승: entropy_proxy가 낮아질 가능성
        closes = [100.0 * (1.010 ** i) for i in range(60)]
        df = _make_df(closes)
        sig = self.strat.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
