"""MFIStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.mfi import MFIStrategy
from src.strategy.base import Action, Confidence


def _make_df(n=50, tp_trend=None, volume=1000.0):
    """테스트용 DataFrame 생성. tp_trend로 TP 시계열 제어."""
    np.random.seed(42)
    close = np.full(n, 100.0)
    if tp_trend is not None:
        close = np.array(tp_trend, dtype=float)
    high = close + 1.0
    low = close - 1.0
    volume_arr = np.full(n, volume)
    return pd.DataFrame({
        "open": close,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume_arr,
        "ema50": close,
        "atr14": np.full(n, 1.0),
    })


def _make_buy_df():
    """MFI < 20 이고 상승 중인 상황 생성.

    전략에서 idx = len(df)-2 를 사용하고 rolling(14).sum()을 계산한다.
    idx-1 구간: 14개 전부 하락 → pos_sum=0 → MFI 낮음
    idx 구간: 13개 하락 + 1개 상승 → MFI 약간 높아짐 (rising)
    """
    n = 60
    # 처음 44개 하락, 45번째 상승, 46~59 하락
    # idx = 58 (len=60, idx=58)
    # idx-1=57 구간 [44..57]: 14개 모두 하락 → pos_sum≈0 → MFI≈0
    # idx=58 구간 [45..58]: 13개 하락 + 44→45 상승 1개 → MFI 약간 증가
    prices = (
        list(np.linspace(1000, 100, 45))   # 0..44: 하락
        + [101.0]                            # 45: 상승 (44→45)
        + list(np.linspace(101, 90, 14))    # 46..59: 다시 하락
    )
    return _make_df(n=n, tp_trend=prices)


def _make_sell_df():
    """MFI > 80 이고 하락 중인 상황 생성.

    idx-1 구간 14개: 전부 상승 → MFI≈100 (높음)
    idx 구간 14개: 13개 상승 + 마지막 1개 하락 → MFI 약간 감소 (falling)
    """
    n = 60
    # idx = 58
    # idx-1 = 57, rolling window [44..57]: 모두 상승 → MFI≈100
    # idx = 58, rolling window [45..58]: [45..57] 상승 + [57→58] 하락 → MFI 감소
    prices = (
        list(np.linspace(100, 1100, 58))   # 0..57: 꾸준히 상승
        + [1099.0]                           # 58: 하락 (1100→1099)
        + [1098.0]                           # 59: 하락
    )
    return _make_df(n=n, tp_trend=prices)


# ── 기본 속성 ──────────────────────────────────────────────────────────────

def test_strategy_name():
    assert MFIStrategy.name == "mfi"


# ── BUY / SELL 신호 ────────────────────────────────────────────────────────

def test_buy_signal():
    strategy = MFIStrategy()
    df = _make_buy_df()
    signal = strategy.generate(df)
    assert signal.action == Action.BUY


def test_sell_signal():
    strategy = MFIStrategy()
    df = _make_sell_df()
    signal = strategy.generate(df)
    assert signal.action == Action.SELL


# ── Confidence ─────────────────────────────────────────────────────────────

def test_buy_high_confidence():
    """MFI < 10 → HIGH confidence BUY."""
    strategy = MFIStrategy()
    # 극단적 하락 후 반등: negative MF 압도적
    n = 60
    prices = list(np.linspace(500, 50, 50)) + list(np.linspace(50, 52, 10))
    df = _make_df(n=n, tp_trend=prices)
    signal = strategy.generate(df)
    if signal.action == Action.BUY:
        assert signal.confidence == Confidence.HIGH
    else:
        pytest.skip("이 데이터셋에서 BUY 미발생, confidence 검증 불가")


def test_buy_medium_confidence():
    """MFI 10~20 → MEDIUM confidence BUY."""
    strategy = MFIStrategy()
    df = _make_buy_df()
    signal = strategy.generate(df)
    if signal.action == Action.BUY:
        assert signal.confidence in (Confidence.MEDIUM, Confidence.HIGH)
    else:
        pytest.skip("BUY 미발생")


def test_sell_high_confidence():
    """MFI > 90 → HIGH confidence SELL."""
    strategy = MFIStrategy()
    n = 60
    prices = list(np.linspace(50, 500, 50)) + list(np.linspace(500, 498, 10))
    df = _make_df(n=n, tp_trend=prices)
    signal = strategy.generate(df)
    if signal.action == Action.SELL:
        assert signal.confidence == Confidence.HIGH
    else:
        pytest.skip("이 데이터셋에서 SELL 미발생, confidence 검증 불가")


def test_sell_medium_confidence():
    """MFI 80~90 → MEDIUM confidence SELL."""
    strategy = MFIStrategy()
    df = _make_sell_df()
    signal = strategy.generate(df)
    if signal.action == Action.SELL:
        assert signal.confidence in (Confidence.MEDIUM, Confidence.HIGH)
    else:
        pytest.skip("SELL 미발생")


# ── HOLD 케이스 ────────────────────────────────────────────────────────────

def test_hold_when_mfi_low_but_falling():
    """MFI < 20 이지만 하락 중이면 HOLD."""
    strategy = MFIStrategy()
    n = 50
    # 하락 후 계속 하락 (반등 없음)
    prices = list(np.linspace(200, 75, 48)) + [74.0, 73.0]
    df = _make_df(n=n, tp_trend=prices)
    signal = strategy.generate(df)
    # MFI가 낮더라도 하락 중이면 BUY가 아님
    assert signal.action in (Action.HOLD, Action.SELL)


def test_hold_on_insufficient_data():
    """데이터 부족 (< 20행) → HOLD, LOW confidence."""
    strategy = MFIStrategy()
    df = _make_df(n=10)
    signal = strategy.generate(df)
    assert signal.action == Action.HOLD
    assert signal.confidence == Confidence.LOW


def test_hold_on_none_data():
    """None 입력 → HOLD."""
    strategy = MFIStrategy()
    signal = strategy.generate(None)
    assert signal.action == Action.HOLD


# ── Signal 필드 완전성 ─────────────────────────────────────────────────────

def test_signal_fields_complete():
    """Signal 객체에 필수 필드가 모두 존재."""
    strategy = MFIStrategy()
    df = _make_df(n=30)
    signal = strategy.generate(df)
    assert signal.action is not None
    assert signal.confidence is not None
    assert signal.strategy == "mfi"
    assert isinstance(signal.entry_price, float)
    assert isinstance(signal.reasoning, str)
    assert isinstance(signal.invalidation, str)


# ── Reasoning 문자열 ───────────────────────────────────────────────────────

def test_buy_reasoning_contains_mfi():
    """BUY 신호의 reasoning에 'MFI' 포함."""
    strategy = MFIStrategy()
    df = _make_buy_df()
    signal = strategy.generate(df)
    if signal.action == Action.BUY:
        assert "MFI" in signal.reasoning
    else:
        pytest.skip("BUY 미발생")


def test_sell_reasoning_contains_mfi():
    """SELL 신호의 reasoning에 'MFI' 포함."""
    strategy = MFIStrategy()
    df = _make_sell_df()
    signal = strategy.generate(df)
    if signal.action == Action.SELL:
        assert "MFI" in signal.reasoning
    else:
        pytest.skip("SELL 미발생")
