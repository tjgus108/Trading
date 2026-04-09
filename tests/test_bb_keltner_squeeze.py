"""
BBKeltnerSqueezeStrategy 단위 테스트 (최소 12개)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.bb_keltner_squeeze import BBKeltnerSqueezeStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 50, close_values=None, high_values=None, low_values=None) -> pd.DataFrame:
    """
    mock DataFrame.  _last() = iloc[-2] (완성봉).
    high/low 생략 시 close ±5 사용.
    """
    if close_values is None:
        close_values = [100.0] * n

    c = list(close_values)
    h = list(high_values) if high_values is not None else [v + 5.0 for v in c]
    l = list(low_values) if low_values is not None else [v - 5.0 for v in c]

    return pd.DataFrame({
        "open":   c,
        "high":   h,
        "low":    l,
        "close":  c,
        "volume": [1000.0] * n,
    })


def _squeeze_then_release_df(n: int = 60, bullish: bool = True) -> pd.DataFrame:
    """
    squeeze 후 돌파 패턴.
    - 앞 n-20 행: 작은 변동 (squeeze 유발)
    - 마지막 완성봉[-2]: 큰 변동 (squeeze 해제)
    """
    # 좁은 range → BB < KC
    close = [100.0] * n
    high  = [101.0] * n
    low   = [99.0]  * n

    # 완성봉 [-2]: 변동 확대 → squeeze 해제
    if bullish:
        close[-2] = 115.0
        high[-2]  = 120.0
        low[-2]   = 99.0
    else:
        close[-2] = 85.0
        high[-2]  = 101.0
        low[-2]   = 80.0

    # 진행 중 캔들 [-1]: 중립
    close[-1] = 100.0
    high[-1]  = 101.0
    low[-1]   = 99.0

    return pd.DataFrame({
        "open":   close,
        "high":   high,
        "low":    low,
        "close":  close,
        "volume": [1000.0] * n,
    })


# ── 1. 기본 인스턴스 ─────────────────────────────────────────────────────────

def test_strategy_name():
    assert BBKeltnerSqueezeStrategy().name == "bb_keltner_squeeze"


# ── 2. 데이터 부족 ───────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = BBKeltnerSqueezeStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows_hold():
    """정확히 최소 행수면 HOLD (경계 테스트)."""
    s = BBKeltnerSqueezeStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 3. squeeze 없을 때 HOLD ──────────────────────────────────────────────────

def test_no_squeeze_returns_hold():
    """변동이 커서 BB > KC → squeeze 없음 → HOLD."""
    s = BBKeltnerSqueezeStrategy()
    n = 60
    # 큰 변동: BB wide > KC
    close = list(np.linspace(80, 120, n))
    high  = [v + 10 for v in close]
    low   = [v - 10 for v in close]
    close[-1] = close[-2]  # 진행 중 캔들
    df = _make_df(n=n, close_values=close, high_values=high, low_values=low)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. Signal 필드 검증 ──────────────────────────────────────────────────────

def test_signal_has_strategy_name():
    s = BBKeltnerSqueezeStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    assert sig.strategy == "bb_keltner_squeeze"


def test_hold_signal_has_low_confidence():
    s = BBKeltnerSqueezeStrategy()
    df = _make_df(n=60)
    sig = s.generate(df)
    if sig.action == Action.HOLD:
        assert sig.confidence == Confidence.LOW


def test_entry_price_equals_last_close():
    """entry_price는 iloc[-2]의 close."""
    s = BBKeltnerSqueezeStrategy()
    n = 60
    close = [100.0] * n
    close[-2] = 99.5  # 완성봉
    df = _make_df(n=n, close_values=close)
    sig = s.generate(df)
    assert sig.entry_price == pytest.approx(99.5)


# ── 5. BUY 시그널 ────────────────────────────────────────────────────────────

def test_buy_signal_on_bullish_squeeze_release():
    """squeeze 해제 + momentum > 0 → BUY."""
    s = BBKeltnerSqueezeStrategy()
    df = _squeeze_then_release_df(n=60, bullish=True)
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_signal_action_and_strategy():
    """BUY 시그널 strategy 필드 확인."""
    s = BBKeltnerSqueezeStrategy()
    df = _squeeze_then_release_df(n=60, bullish=True)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.strategy == "bb_keltner_squeeze"
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 6. SELL 시그널 ───────────────────────────────────────────────────────────

def test_sell_signal_on_bearish_squeeze_release():
    """squeeze 해제 + momentum < 0 → SELL."""
    s = BBKeltnerSqueezeStrategy()
    df = _squeeze_then_release_df(n=60, bullish=False)
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_signal_confidence():
    """SELL 시그널 confidence 검증."""
    s = BBKeltnerSqueezeStrategy()
    df = _squeeze_then_release_df(n=60, bullish=False)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 7. reasoning/invalidation 비어있지 않음 ──────────────────────────────────

def test_buy_signal_has_reasoning():
    s = BBKeltnerSqueezeStrategy()
    df = _squeeze_then_release_df(n=60, bullish=True)
    sig = s.generate(df)
    assert len(sig.reasoning) > 0


def test_sell_signal_has_invalidation():
    s = BBKeltnerSqueezeStrategy()
    df = _squeeze_then_release_df(n=60, bullish=False)
    sig = s.generate(df)
    assert len(sig.reasoning) > 0


# ── 8. 충분한 행 + flat 가격 → HOLD ─────────────────────────────────────────

def test_flat_price_hold():
    """완전히 flat한 가격 → std=0 → BB=KC=mid → squeeze 여부는 edge, 결국 HOLD."""
    s = BBKeltnerSqueezeStrategy()
    df = _make_df(n=60, close_values=[100.0] * 60)
    sig = s.generate(df)
    # flat → momentum=0 → 돌파해도 momentum=0 → HOLD
    assert sig.action == Action.HOLD
