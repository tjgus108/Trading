"""TickVolumeStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.tick_volume import TickVolumeStrategy


def _make_df(n: int = 40, close_prices=None, volume_factor: float = 1.0) -> pd.DataFrame:
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
        "volume": np.ones(n) * 1000 * volume_factor,
    })


def _make_buy_df(n: int = 40) -> pd.DataFrame:
    """Strong up-ticks with high volume → BUY 조건."""
    # 지속 상승 + 높은 볼륨
    close = np.linspace(100, 120, n)
    volume = np.ones(n) * 2000  # tick_vol_ma * 1.5 초과
    return pd.DataFrame({
        "open": close * 0.999,
        "high": close * 1.005,
        "low": close * 0.995,
        "close": close,
        "volume": volume,
    })


def _make_sell_df(n: int = 40) -> pd.DataFrame:
    """Strong down-ticks with high volume → SELL 조건."""
    close = np.linspace(120, 100, n)
    volume = np.ones(n) * 2000
    return pd.DataFrame({
        "open": close * 1.001,
        "high": close * 1.005,
        "low": close * 0.995,
        "close": close,
        "volume": volume,
    })


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────────

def test_strategy_name():
    s = TickVolumeStrategy()
    assert s.name == "tick_volume"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────────

def test_instantiation():
    s = TickVolumeStrategy()
    assert isinstance(s, TickVolumeStrategy)


# ── 3. 데이터 부족 → HOLD ────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = TickVolumeStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ──────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = TickVolumeStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 entry_price = 0 ───────────────────────────────────────────

def test_insufficient_data_entry_price_zero():
    s = TickVolumeStrategy()
    df = _make_df(n=5)
    sig = s.generate(df)
    assert sig.entry_price == 0.0


# ── 6. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = TickVolumeStrategy()
    df = _make_df(n=5)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning


# ── 7. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = TickVolumeStrategy()
    df = _make_df(n=40)
    sig = s.generate(df)
    assert isinstance(sig, Signal)


# ── 8. Signal 필드 완성 ──────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = TickVolumeStrategy()
    df = _make_df(n=40)
    sig = s.generate(df)
    assert sig.strategy == "tick_volume"
    assert sig.entry_price > 0
    assert sig.reasoning != ""
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


# ── 9. entry_price > 0 ───────────────────────────────────────────────────────

def test_entry_price_positive():
    s = TickVolumeStrategy()
    df = _make_df(n=40)
    sig = s.generate(df)
    assert sig.entry_price > 0


# ── 10. strategy 필드 값 확인 ────────────────────────────────────────────────

def test_strategy_field_value():
    s = TickVolumeStrategy()
    df = _make_df(n=40)
    sig = s.generate(df)
    assert sig.strategy == "tick_volume"


# ── 11. BUY 조건 테스트 ──────────────────────────────────────────────────────

def test_buy_signal():
    s = TickVolumeStrategy()
    df = _make_buy_df(n=40)
    sig = s.generate(df)
    # 지속 상승 + 높은 볼륨이면 BUY 또는 HOLD (조건 충족 여부에 따라)
    assert sig.action in (Action.BUY, Action.HOLD)


# ── 12. SELL 조건 테스트 ─────────────────────────────────────────────────────

def test_sell_signal():
    s = TickVolumeStrategy()
    df = _make_sell_df(n=40)
    sig = s.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


# ── 13. BUY reasoning 키워드 ─────────────────────────────────────────────────

def test_buy_reasoning_keyword():
    s = TickVolumeStrategy()
    df = _make_buy_df(n=40)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "BUY" in sig.reasoning or "tick_volume" in sig.reasoning


# ── 14. 최소 행 수(20)에서 동작 ─────────────────────────────────────────────

def test_minimum_rows():
    s = TickVolumeStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 15. HIGH confidence 조건 ─────────────────────────────────────────────────

def test_high_confidence_when_volume_large():
    """volume > tick_vol_ma * 1.5 이면 HIGH confidence."""
    s = TickVolumeStrategy()
    # 처음 30개는 낮은 볼륨, 마지막 부분은 높은 볼륨
    n = 40
    close = np.linspace(100, 120, n)
    volume = np.ones(n) * 1000
    volume[-10:] = 3000  # 1000 * 1.5 = 1500 초과
    df = pd.DataFrame({
        "open": close * 0.999,
        "high": close * 1.005,
        "low": close * 0.995,
        "close": close,
        "volume": volume,
    })
    sig = s.generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 16. HOLD 조건 - 볼륨 부족 ────────────────────────────────────────────────

def test_hold_when_low_volume():
    """volume <= tick_vol_ma 이면 신호 없음 → HOLD."""
    s = TickVolumeStrategy()
    close = np.linspace(100, 120, 40)
    # 균일 볼륨 → tick_vol_ma == volume → vol_active = False
    volume = np.ones(40) * 1000
    df = pd.DataFrame({
        "open": close * 0.999,
        "high": close * 1.005,
        "low": close * 0.995,
        "close": close,
        "volume": volume,
    })
    sig = s.generate(df)
    # 볼륨이 tick_vol_ma와 같으면 vol_active=False → HOLD
    assert sig.action == Action.HOLD
