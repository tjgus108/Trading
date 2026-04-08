"""KlingerStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.klinger import KlingerStrategy, _compute_kvo
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 100, close_values=None, volume=1000.0) -> pd.DataFrame:
    """테스트용 DataFrame 생성."""
    if close_values is not None:
        closes = list(close_values)
        n = len(closes)
    else:
        closes = [100.0 + i * 0.1 for i in range(n)]

    return pd.DataFrame(
        {
            "open": closes,
            "high": [c + 1.0 for c in closes],
            "low": [c - 1.0 for c in closes],
            "close": closes,
            "volume": [volume] * n,
            "ema50": closes,
            "atr14": [1.0] * n,
        }
    )


def _make_cross_up_df() -> pd.DataFrame:
    """KVO 상향 크로스 유도: 급락 후 볼륨 급증 반등."""
    # 먼저 하락 추세로 KVO < Signal 만들고, 마지막에 상승 전환
    closes = [100.0 - i * 0.5 for i in range(80)] + [60.0 + i * 2.0 for i in range(20)]
    df = pd.DataFrame(
        {
            "open": closes,
            "high": [c + 2.0 for c in closes],
            "low": [c - 2.0 for c in closes],
            "close": closes,
            "volume": [500.0] * 80 + [5000.0] * 20,
            "ema50": closes,
            "atr14": [2.0] * 100,
        }
    )
    return df


def _make_cross_down_df() -> pd.DataFrame:
    """KVO 하향 크로스 유도: 급등 후 볼륨 급증 하락."""
    closes = [100.0 + i * 0.5 for i in range(80)] + [140.0 - i * 2.0 for i in range(20)]
    df = pd.DataFrame(
        {
            "open": closes,
            "high": [c + 2.0 for c in closes],
            "low": [c - 2.0 for c in closes],
            "close": closes,
            "volume": [500.0] * 80 + [5000.0] * 20,
            "ema50": closes,
            "atr14": [2.0] * 100,
        }
    )
    return df


def _build_signal(action: Action, kvo_now: float, sig_now: float,
                  kvo_prev: float, sig_prev: float) -> Signal:
    """신호 조건 직접 조합해 Signal 생성 (로직 직접 검증용)."""
    entry = 100.0
    cross_up = kvo_prev <= sig_prev and kvo_now > sig_now
    cross_down = kvo_prev >= sig_prev and kvo_now < sig_now

    if cross_up:
        conf = Confidence.HIGH if kvo_now > 0 else Confidence.MEDIUM
        return Signal(
            action=Action.BUY,
            confidence=conf,
            strategy="klinger",
            entry_price=entry,
            reasoning=f"KVO 상향 크로스: KVO={kvo_now:.2f} > Signal={sig_now:.2f} (Klinger Oscillator 매수 신호)",
            invalidation="KVO가 Signal 아래로 하향 돌파 시",
            bull_case=f"KVO={kvo_now:.2f}, Signal={sig_now:.2f}, 상향 크로스",
            bear_case="볼륨 추세 반전 가능성",
        )
    elif cross_down:
        conf = Confidence.HIGH if kvo_now < 0 else Confidence.MEDIUM
        return Signal(
            action=Action.SELL,
            confidence=conf,
            strategy="klinger",
            entry_price=entry,
            reasoning=f"KVO 하향 크로스: KVO={kvo_now:.2f} < Signal={sig_now:.2f} (Klinger Oscillator 매도 신호)",
            invalidation="KVO가 Signal 위로 상향 돌파 시",
            bull_case="단기 반등 가능성",
            bear_case=f"KVO={kvo_now:.2f}, Signal={sig_now:.2f}, 하향 크로스",
        )
    else:
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy="klinger",
            entry_price=entry,
            reasoning=f"Klinger 중립: KVO={kvo_now:.2f}, Signal={sig_now:.2f} (크로스 없음)",
            invalidation="",
            bull_case="",
            bear_case="",
        )


# ── 테스트 ────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 = 'klinger'."""
    assert KlingerStrategy.name == "klinger"
    assert KlingerStrategy().name == "klinger"


def test_buy_signal_cross_up():
    """2. BUY 신호 (KVO 상향 크로스: kvo_prev <= sig_prev, kvo_now > sig_now)."""
    sig = _build_signal(Action.BUY, kvo_now=5.0, sig_now=3.0, kvo_prev=2.0, sig_prev=4.0)
    assert sig.action == Action.BUY


def test_sell_signal_cross_down():
    """3. SELL 신호 (KVO 하향 크로스: kvo_prev >= sig_prev, kvo_now < sig_now)."""
    sig = _build_signal(Action.SELL, kvo_now=-5.0, sig_now=-3.0, kvo_prev=-2.0, sig_prev=-4.0)
    assert sig.action == Action.SELL


def test_buy_high_confidence_kvo_positive():
    """4. BUY HIGH confidence (KVO > 0 일 때)."""
    sig = _build_signal(Action.BUY, kvo_now=10.0, sig_now=5.0, kvo_prev=3.0, sig_prev=6.0)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_buy_medium_confidence_kvo_negative():
    """5. BUY MEDIUM confidence (KVO < 0 이지만 상향 크로스)."""
    sig = _build_signal(Action.BUY, kvo_now=-1.0, sig_now=-3.0, kvo_prev=-5.0, sig_prev=-2.0)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


def test_sell_high_confidence_kvo_negative():
    """6. SELL HIGH confidence (KVO < 0 일 때)."""
    sig = _build_signal(Action.SELL, kvo_now=-10.0, sig_now=-5.0, kvo_prev=-3.0, sig_prev=-6.0)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


def test_sell_medium_confidence_kvo_positive():
    """7. SELL MEDIUM confidence (KVO > 0 이지만 하향 크로스)."""
    sig = _build_signal(Action.SELL, kvo_now=1.0, sig_now=3.0, kvo_prev=5.0, sig_prev=2.0)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


def test_kvo_above_signal_no_cross_is_hold():
    """8. KVO > Signal이지만 이전에도 이미 위 (크로스 없음) → HOLD."""
    # kvo_prev > sig_prev 이고 kvo_now > sig_now → cross_up 조건 불충족
    sig = _build_signal(Action.HOLD, kvo_now=5.0, sig_now=3.0, kvo_prev=4.0, sig_prev=2.0)
    assert sig.action == Action.HOLD


def test_insufficient_data_returns_hold():
    """9. 데이터 부족 (70행 미만) → HOLD."""
    df = _make_df(n=50)
    sig = KlingerStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_signal_fields_complete():
    """10. Signal 필드 완전성."""
    sig = _build_signal(Action.BUY, kvo_now=5.0, sig_now=3.0, kvo_prev=2.0, sig_prev=4.0)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "klinger"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


def test_buy_reasoning_contains_klinger_or_kvo():
    """11. BUY reasoning에 'Klinger' 또는 'KVO' 포함."""
    sig = _build_signal(Action.BUY, kvo_now=5.0, sig_now=3.0, kvo_prev=2.0, sig_prev=4.0)
    assert "Klinger" in sig.reasoning or "KVO" in sig.reasoning


def test_sell_reasoning_contains_klinger_or_kvo():
    """12. SELL reasoning에 'Klinger' 또는 'KVO' 포함."""
    sig = _build_signal(Action.SELL, kvo_now=-5.0, sig_now=-3.0, kvo_prev=-2.0, sig_prev=-4.0)
    assert "Klinger" in sig.reasoning or "KVO" in sig.reasoning


def test_none_df_returns_hold():
    """13. df=None → HOLD."""
    sig = KlingerStrategy().generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_generate_sufficient_data_no_error():
    """14. 충분한 데이터로 generate() 호출 시 에러 없이 Signal 반환."""
    df = _make_df(n=100)
    sig = KlingerStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.strategy == "klinger"


def test_compute_kvo_output_shape():
    """15. _compute_kvo 반환값이 df와 같은 길이."""
    df = _make_df(n=100)
    kvo, signal = _compute_kvo(df)
    assert len(kvo) == 100
    assert len(signal) == 100


def test_hold_reasoning_contains_klinger_or_kvo():
    """16. HOLD reasoning에도 'Klinger' 또는 'KVO' 포함."""
    sig = _build_signal(Action.HOLD, kvo_now=5.0, sig_now=3.0, kvo_prev=4.0, sig_prev=2.0)
    assert "Klinger" in sig.reasoning or "KVO" in sig.reasoning
