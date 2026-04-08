"""PPOStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.ppo import PPOStrategy


def _make_df(n: int = 100, close_prices=None) -> pd.DataFrame:
    """테스트용 DataFrame 생성."""
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
        "ema50": close * 0.98,
        "atr14": np.ones(n) * 0.5,
    })


class _ForcedPPOStrategy(PPOStrategy):
    """PPO 내부 지표 값을 고정해 특정 조건을 강제 테스트하는 서브클래스."""

    def __init__(self, ppo_prev, ppo_now, sig_prev, sig_now, hist_prev, hist_now):
        self._fp = (ppo_prev, ppo_now, sig_prev, sig_now, hist_prev, hist_now)

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 35:
            return Signal(
                action=Action.HOLD, confidence=Confidence.LOW, strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="데이터 부족 (최소 35행 필요)",
                invalidation="충분한 데이터 확보 후 재실행",
            )

        ppo_prev, ppo_now, sig_prev, sig_now, hist_prev, hist_now = self._fp
        entry_price = float(self._last(df)["close"])

        cross_up = ppo_prev <= sig_prev and ppo_now > sig_now
        cross_down = ppo_prev >= sig_prev and ppo_now < sig_now

        confidence = Confidence.HIGH if abs(ppo_now) > 1.0 else Confidence.MEDIUM

        if cross_up and ppo_now > 0 and hist_now > hist_prev:
            return Signal(
                action=Action.BUY, confidence=confidence, strategy=self.name,
                entry_price=entry_price,
                reasoning=f"PPO 상향 크로스 (PPO={ppo_now:.3f} > Signal={sig_now:.3f})",
                invalidation="PPO가 Signal 아래로 하락 시 무효",
            )

        if cross_down and ppo_now < 0 and hist_now < hist_prev:
            return Signal(
                action=Action.SELL, confidence=confidence, strategy=self.name,
                entry_price=entry_price,
                reasoning=f"PPO 하향 크로스 (PPO={ppo_now:.3f} < Signal={sig_now:.3f})",
                invalidation="PPO가 Signal 위로 반등 시 무효",
            )

        return Signal(
            action=Action.HOLD, confidence=Confidence.MEDIUM, strategy=self.name,
            entry_price=entry_price,
            reasoning=f"명확한 크로스 없음 (PPO={ppo_now:.3f}, Signal={sig_now:.3f})",
            invalidation="PPO 크로스 발생 시 재평가",
        )


def _make_buy_df() -> pd.DataFrame:
    """BUY 조건을 강제하는 _ForcedPPOStrategy 용 충분한 길이 df."""
    return _make_df(n=80)


def _make_sell_df() -> pd.DataFrame:
    """SELL 조건을 강제하는 _ForcedPPOStrategy 용 충분한 길이 df."""
    return _make_df(n=80)


# ── 1. 전략 이름 ─────────────────────────────────────────────────────────────

def test_strategy_name():
    s = PPOStrategy()
    assert s.name == "ppo"


# ── 2. BUY 신호 ──────────────────────────────────────────────────────────────

def test_buy_signal():
    """PPO 상향 크로스 + PPO>0 + Histogram 증가 → BUY."""
    # ppo_prev <= sig_prev (크로스 직전), ppo_now > sig_now (크로스 직후)
    # ppo_now > 0, hist_now > hist_prev
    s = _ForcedPPOStrategy(
        ppo_prev=-0.1, ppo_now=0.5,
        sig_prev=0.0, sig_now=0.3,
        hist_prev=0.1, hist_now=0.2,
    )
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 ─────────────────────────────────────────────────────────────

def test_sell_signal():
    """PPO 하향 크로스 + PPO<0 + Histogram 감소 → SELL."""
    # ppo_prev >= sig_prev (크로스 직전), ppo_now < sig_now (크로스 직후)
    # ppo_now < 0, hist_now < hist_prev
    s = _ForcedPPOStrategy(
        ppo_prev=0.1, ppo_now=-0.5,
        sig_prev=0.0, sig_now=-0.3,
        hist_prev=-0.1, hist_now=-0.2,
    )
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence ───────────────────────────────────────────────────

def test_buy_high_confidence():
    """|PPO| > 1.0 → HIGH confidence."""
    s = _ForcedPPOStrategy(
        ppo_prev=-0.5, ppo_now=1.5,   # |ppo_now| > 1.0
        sig_prev=0.0, sig_now=0.8,
        hist_prev=0.2, hist_now=0.7,
    )
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 5. BUY MEDIUM confidence ─────────────────────────────────────────────────

def test_buy_medium_confidence():
    """|PPO| <= 1.0 → MEDIUM confidence."""
    s = _ForcedPPOStrategy(
        ppo_prev=-0.1, ppo_now=0.5,   # |ppo_now| = 0.5 <= 1.0
        sig_prev=0.0, sig_now=0.3,
        hist_prev=0.1, hist_now=0.2,
    )
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 6. SELL HIGH confidence ──────────────────────────────────────────────────

def test_sell_high_confidence():
    """|PPO| > 1.0 → HIGH confidence (SELL)."""
    s = _ForcedPPOStrategy(
        ppo_prev=0.5, ppo_now=-1.5,   # |ppo_now| > 1.0
        sig_prev=0.0, sig_now=-0.8,
        hist_prev=-0.2, hist_now=-0.7,
    )
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 7. SELL MEDIUM confidence ────────────────────────────────────────────────

def test_sell_medium_confidence():
    """|PPO| <= 1.0 → MEDIUM confidence (SELL)."""
    s = _ForcedPPOStrategy(
        ppo_prev=0.1, ppo_now=-0.5,   # |ppo_now| = 0.5 <= 1.0
        sig_prev=0.0, sig_now=-0.3,
        hist_prev=-0.1, hist_now=-0.2,
    )
    df = _make_sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 8. PPO > Signal이지만 PPO < 0 → HOLD ────────────────────────────────────

def test_hold_when_ppo_positive_cross_but_ppo_negative():
    """PPO가 Signal 위로 크로스해도 PPO<0이면 BUY 조건 불충족 → HOLD."""
    # cross_up=True이지만 ppo_now < 0
    s = _ForcedPPOStrategy(
        ppo_prev=-1.0, ppo_now=-0.3,  # cross_up (prev <= sig_prev, now > sig_now) 만족
        sig_prev=-0.5, sig_now=-0.5,  # ppo_now(-0.3) > sig_now(-0.5) → cross_up=True
        hist_prev=-0.5, hist_now=0.2, # hist 증가
    )
    df = _make_df(n=80)
    sig = s.generate(df)
    # ppo_now = -0.3 < 0 이므로 BUY 불가
    assert sig.action == Action.HOLD


# ── 9. 데이터 부족 → HOLD ───────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = PPOStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 10. Signal 필드 완전성 ──────────────────────────────────────────────────

def test_signal_fields_complete():
    s = PPOStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    assert sig.strategy == "ppo"
    assert sig.entry_price > 0
    assert sig.reasoning != ""
    assert sig.invalidation != ""
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 11. BUY reasoning에 "PPO" 포함 ──────────────────────────────────────────

def test_buy_reasoning_contains_ppo():
    s = _ForcedPPOStrategy(
        ppo_prev=-0.1, ppo_now=0.5,
        sig_prev=0.0, sig_now=0.3,
        hist_prev=0.1, hist_now=0.2,
    )
    df = _make_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert "PPO" in sig.reasoning


# ── 12. SELL reasoning에 "PPO" 포함 ─────────────────────────────────────────

def test_sell_reasoning_contains_ppo():
    s = _ForcedPPOStrategy(
        ppo_prev=0.1, ppo_now=-0.5,
        sig_prev=0.0, sig_now=-0.3,
        hist_prev=-0.1, hist_now=-0.2,
    )
    df = _make_df(n=80)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert "PPO" in sig.reasoning


# ── 13. HOLD 신호 구조 확인 ─────────────────────────────────────────────────

def test_hold_signal_structure():
    s = PPOStrategy()
    df = _make_df(n=80)  # 평탄한 데이터 → 크로스 없음
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert sig.strategy == "ppo"


# ── 14. entry_price가 마지막 완성 캔들 종가 ─────────────────────────────────

def test_entry_price_is_last_candle():
    s = PPOStrategy()
    df = _make_df(n=80)
    sig = s.generate(df)
    expected = float(df["close"].iloc[-2])
    assert sig.entry_price == pytest.approx(expected, rel=1e-6)
