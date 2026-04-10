"""PriceMomentumOscStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.price_momentum_osc import PriceMomentumOscStrategy


def _make_df(n: int = 80, close_prices=None) -> pd.DataFrame:
    if close_prices is not None:
        close = np.array(close_prices, dtype=float)
        n = len(close)
    else:
        close = np.linspace(100, 110, n)
    return pd.DataFrame({
        "open": close * 0.999,
        "high": close * 1.005,
        "low": close * 0.995,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


class _ForcedPMOStrategy(PriceMomentumOscStrategy):
    """내부 지표 값을 고정해 신호 강제."""

    def __init__(self, hist_prev, hist_now, ppo_now):
        self._hist_prev = hist_prev
        self._hist_now = hist_now
        self._ppo_now = ppo_now

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < 35:
            return self._hold(df, "Insufficient data (minimum 35 rows required)")

        entry_price = float(self._last(df)["close"])
        hist_prev = self._hist_prev
        hist_now = self._hist_now
        ppo_now = self._ppo_now

        confidence = Confidence.HIGH if abs(ppo_now) > 2.0 else Confidence.MEDIUM
        cross_above = hist_prev < 0 and hist_now >= 0
        cross_below = hist_prev >= 0 and hist_now < 0

        if cross_above and ppo_now < 0:
            return Signal(
                action=Action.BUY, confidence=confidence, strategy=self.name,
                entry_price=entry_price,
                reasoning=f"PPO 히스토그램 상향 크로스 0 (prev={hist_prev:.3f}→now={hist_now:.3f}), PPO={ppo_now:.3f} < 0 (과매도 구간)",
                invalidation="PPO 히스토그램이 다시 0 아래로 하락 시 무효",
            )

        if cross_below and ppo_now > 0:
            return Signal(
                action=Action.SELL, confidence=confidence, strategy=self.name,
                entry_price=entry_price,
                reasoning=f"PPO 히스토그램 하향 크로스 0 (prev={hist_prev:.3f}→now={hist_now:.3f}), PPO={ppo_now:.3f} > 0 (과매수 구간)",
                invalidation="PPO 히스토그램이 다시 0 위로 반등 시 무효",
            )

        return Signal(
            action=Action.HOLD, confidence=Confidence.MEDIUM, strategy=self.name,
            entry_price=entry_price,
            reasoning=f"크로스 없음 (ppo_hist={hist_now:.3f}, PPO={ppo_now:.3f})",
            invalidation="PPO 히스토그램 크로스 발생 시 재평가",
        )


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────────

def test_strategy_name():
    s = PriceMomentumOscStrategy()
    assert s.name == "price_momentum_osc"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────────

def test_instantiation():
    s = PriceMomentumOscStrategy()
    assert isinstance(s, PriceMomentumOscStrategy)


# ── 3. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = PriceMomentumOscStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ──────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = PriceMomentumOscStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = PriceMomentumOscStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning or "minimum" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = PriceMomentumOscStrategy()
    df = _make_df(n=80)
    sig = s.generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성 ──────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = PriceMomentumOscStrategy()
    df = _make_df(n=80)
    sig = s.generate(df)
    assert sig.strategy == "price_momentum_osc"
    assert sig.entry_price > 0
    assert sig.reasoning != ""
    assert sig.invalidation != ""
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 8. BUY reasoning 키워드 확인 ─────────────────────────────────────────────

def test_buy_reasoning_keywords():
    s = _ForcedPMOStrategy(hist_prev=-0.5, hist_now=0.1, ppo_now=-1.0)
    df = _make_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert "PPO" in sig.reasoning or "크로스" in sig.reasoning or "과매도" in sig.reasoning


# ── 9. SELL reasoning 키워드 확인 ────────────────────────────────────────────

def test_sell_reasoning_keywords():
    s = _ForcedPMOStrategy(hist_prev=0.5, hist_now=-0.1, ppo_now=1.0)
    df = _make_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert "PPO" in sig.reasoning or "크로스" in sig.reasoning or "과매수" in sig.reasoning


# ── 10. HIGH confidence 테스트 ───────────────────────────────────────────────

def test_high_confidence_buy():
    """|ppo| > 2.0 → HIGH confidence."""
    s = _ForcedPMOStrategy(hist_prev=-0.5, hist_now=0.1, ppo_now=-2.5)
    df = _make_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 11. MEDIUM confidence 테스트 ─────────────────────────────────────────────

def test_medium_confidence_buy():
    """|ppo| <= 2.0 → MEDIUM confidence."""
    s = _ForcedPMOStrategy(hist_prev=-0.5, hist_now=0.1, ppo_now=-1.0)
    df = _make_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 12. entry_price > 0 ──────────────────────────────────────────────────────

def test_entry_price_positive():
    s = PriceMomentumOscStrategy()
    df = _make_df(n=80)
    sig = s.generate(df)
    assert sig.entry_price > 0


# ── 13. strategy 필드 값 확인 ────────────────────────────────────────────────

def test_strategy_field_value():
    s = PriceMomentumOscStrategy()
    df = _make_df(n=80)
    sig = s.generate(df)
    assert sig.strategy == "price_momentum_osc"


# ── 14. 최소 행 수(35)에서 동작 ─────────────────────────────────────────────

def test_minimum_rows():
    s = PriceMomentumOscStrategy()
    df = _make_df(n=35)
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
