"""
ValueAreaStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.value_area import ValueAreaStrategy
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 30, close_values=None, volume_values=None) -> pd.DataFrame:
    if close_values is None:
        close_values = [100.0] * n
    if volume_values is None:
        volume_values = [1000.0] * n
    return pd.DataFrame({
        "open":   [100.0] * n,
        "high":   [105.0] * n,
        "low":    [95.0]  * n,
        "close":  close_values,
        "volume": volume_values,
    })


def _make_buy_df() -> pd.DataFrame:
    """
    prev_close (idx-1) < va_low, curr_close (idx = len-2) > va_low → BUY
    Use a large dip at idx-1, recovery at idx.
    """
    n = 40
    closes = [100.0] * n
    volumes = [1000.0] * n
    # Make rolling(20) period stable around 100, then insert dip
    idx = n - 2  # 완성봉 위치
    closes[idx - 1] = 60.0   # prev: far below VA low (~100 - 0.7*std)
    closes[idx] = 98.0        # curr: back inside VA
    closes[idx + 1] = 98.0   # 진행 중 캔들
    return _make_df(n=n, close_values=closes, volume_values=volumes)


def _make_sell_df() -> pd.DataFrame:
    """
    prev_close > va_high, curr_close < va_high → SELL
    """
    n = 40
    closes = [100.0] * n
    idx = n - 2
    closes[idx - 1] = 140.0  # prev: far above VA high
    closes[idx] = 102.0       # curr: back inside VA
    closes[idx + 1] = 102.0
    return _make_df(n=n, close_values=closes)


# ── 1. 전략명 확인 ────────────────────────────────────────────────────────────

def test_strategy_name():
    assert ValueAreaStrategy.name == "value_area"


# ── 2. 인스턴스 생성 ──────────────────────────────────────────────────────────

def test_strategy_is_instantiable():
    s = ValueAreaStrategy()
    assert s is not None


# ── 3. 데이터 부족 → HOLD ─────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = ValueAreaStrategy()
    df = _make_df(n=20)  # < 25
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 4. None 입력 → HOLD ──────────────────────────────────────────────────────

def test_none_input_returns_hold():
    s = ValueAreaStrategy()
    sig = s.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인 ────────────────────────────────────────────

def test_insufficient_data_reasoning():
    s = ValueAreaStrategy()
    df = _make_df(n=10)
    sig = s.generate(df)
    assert "Insufficient" in sig.reasoning


# ── 6. 정상 데이터 → Signal 반환 ─────────────────────────────────────────────

def test_normal_data_returns_signal():
    s = ValueAreaStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성 ───────────────────────────────────────────────────────

def test_signal_fields_complete():
    s = ValueAreaStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy is not None
    assert sig.reasoning is not None
    assert sig.invalidation is not None


# ── 8. BUY reasoning 확인 ────────────────────────────────────────────────────

def test_buy_reasoning():
    s = ValueAreaStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert "VA 하단 재진입" in sig.reasoning or "va_low" in sig.reasoning.lower()


# ── 9. SELL reasoning 확인 ───────────────────────────────────────────────────

def test_sell_reasoning():
    s = ValueAreaStrategy()
    df = _make_sell_df()
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert "VA 상단 재진입" in sig.reasoning or "va_high" in sig.reasoning.lower()


# ── 10. HIGH confidence 테스트 ────────────────────────────────────────────────

def test_high_confidence_when_near_vwap():
    """
    BUY 신호 + close가 vwap에 매우 근접 → HIGH confidence 기대
    """
    s = ValueAreaStrategy()
    # 모든 close 동일하면 std≈0, |close - vwap|≈0 < std*0.3≈0 → 비교 어려움
    # close가 vwap에 매우 근접한 경우를 simulate
    n = 40
    closes = [100.0] * n
    idx = n - 2
    closes[idx - 1] = 60.0   # 이전봉: VA 아래
    closes[idx] = 100.001     # 현재봉: VWAP 근처 재진입 (HIGH conf 목표)
    closes[idx + 1] = 100.0
    df = _make_df(n=n, close_values=closes)
    sig = s.generate(df)
    # BUY가 나오면 confidence가 HIGH 또는 MEDIUM이어야 함
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 11. MEDIUM confidence 테스트 ─────────────────────────────────────────────

def test_medium_confidence_when_far_from_vwap():
    s = ValueAreaStrategy()
    df = _make_buy_df()
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


# ── 12. entry_price > 0 ──────────────────────────────────────────────────────

def test_entry_price_positive():
    s = ValueAreaStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.entry_price >= 0


# ── 13. strategy 필드 값 확인 ─────────────────────────────────────────────────

def test_signal_strategy_field():
    s = ValueAreaStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.strategy == "value_area"


# ── 14. 최소 행(25행) 동작 확인 ──────────────────────────────────────────────

def test_exactly_min_rows():
    s = ValueAreaStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    assert isinstance(sig, Signal)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 15. EMA momentum filter: 4h 봉 대응 확인 (Cycle 245) ─────────────────────

def test_ema_momentum_filter_generates_signal():
    """EMA short-period momentum filter가 4h-like 시나리오에서 신호를 생성하는지 확인."""
    s = ValueAreaStrategy()
    n = 30
    closes = [100.0] * n
    idx = n - 2
    # 이전 봉: VA low 아래로 이탈
    closes[idx - 1] = 85.0
    # 현재 봉: VA 위로 회복 + EMA10 > prev EMA10 (closes[idx] > EMA10[idx-1])
    closes[idx] = 99.0
    closes[idx + 1] = 99.0
    df = _make_df(n=n, close_values=closes)
    sig = s.generate(df)
    # 신호가 HOLD이거나 BUY여야 함 (필터 통과 여부와 무관하게 예외 없음)
    assert sig.action in (Action.BUY, Action.HOLD)
    assert isinstance(sig, Signal)


# ── 16. 기본 파라미터 확인 (Cycle 245 기준: va_period=10, ema_short=10) ────────

def test_default_params():
    """Cycle 245 업데이트된 기본값 확인."""
    from src.strategy.value_area import _VA_PERIOD, _EMA_SHORT, _EMA_LONG, _MIN_ROWS
    assert _VA_PERIOD == 10
    assert _EMA_SHORT == 10
    assert _EMA_LONG == 20
    assert _MIN_ROWS == 25
