"""tests/test_colored_candles.py — ColoredCandlesStrategy 단위 테스트 (14개)"""

import numpy as np
import pandas as pd
import pytest
from typing import Optional

from src.strategy.colored_candles import ColoredCandlesStrategy
from src.strategy.base import Action, Confidence


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _make_df(
    close: np.ndarray,
    open_: Optional[np.ndarray] = None,
    volume: Optional[np.ndarray] = None,
) -> pd.DataFrame:
    n = len(close)
    if open_ is None:
        open_ = close - 1  # 기본: 모두 양봉
    if volume is None:
        volume = np.ones(n) * 1000
    return pd.DataFrame({
        "open": open_.astype(float),
        "close": close.astype(float),
        "high": close + 2,
        "low": open_ - 2,
        "volume": volume.astype(float),
    })


def _flat_df(n: int = 40) -> pd.DataFrame:
    """완전 평탄: close == open → 양봉/음봉 없음 → HOLD"""
    close = np.full(n, 100.0)
    open_ = np.full(n, 100.0)
    return _make_df(close, open_)


def _bull_run_df(n_base: int = 20, bull_count: int = 4, vol_inc: bool = True) -> pd.DataFrame:
    """연속 양봉 + 거래량 증가 데이터"""
    # base: 혼합 캔들
    base_close = np.linspace(100, 105, n_base)
    base_open = base_close - 0.5
    # 연속 양봉 구간: close > open
    bull_close = np.array([106.0 + i for i in range(bull_count)])
    bull_open = bull_close - 1.0
    # 마지막 봉 (미완성)
    dummy_close = np.array([bull_close[-1] + 1])
    dummy_open = dummy_close - 1.0
    close = np.concatenate([base_close, bull_close, dummy_close])
    open_arr = np.concatenate([base_open, bull_open, dummy_open])
    n = len(close)
    if vol_inc:
        # 거래량 증가: 마지막 완성 캔들(idx=-2)의 거래량 > 이전
        volume = np.ones(n) * 1000
        volume[-2] = 2000  # vol_increasing = True
        volume[-3] = 1500  # vol_ma < vol[-2]
    else:
        volume = np.ones(n) * 1000
        volume[-2] = 500  # 거래량 감소
    return _make_df(close, open_arr, volume)


def _bear_run_df(n_base: int = 20, bear_count: int = 4, vol_inc: bool = True) -> pd.DataFrame:
    """연속 음봉 + 거래량 증가 데이터"""
    base_close = np.linspace(110, 105, n_base)
    base_open = base_close + 0.5
    # 연속 음봉: close < open
    bear_close = np.array([104.0 - i for i in range(bear_count)])
    bear_open = bear_close + 1.0
    dummy_close = np.array([bear_close[-1] - 1])
    dummy_open = dummy_close + 1.0
    close = np.concatenate([base_close, bear_close, dummy_close])
    open_arr = np.concatenate([base_open, bear_open, dummy_open])
    n = len(close)
    if vol_inc:
        volume = np.ones(n) * 1000
        volume[-2] = 2000
        volume[-3] = 1500
    else:
        volume = np.ones(n) * 1000
        volume[-2] = 500
    return _make_df(close, open_arr, volume)


# ── 테스트: 데이터 부족 ──────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    """1. 데이터 부족 (19행) → HOLD"""
    strat = ColoredCandlesStrategy()
    df = _make_df(np.linspace(100, 110, 19))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_insufficient_data_reasoning():
    """2. 데이터 부족 시 reasoning에 'Insufficient' 포함"""
    strat = ColoredCandlesStrategy()
    df = _make_df(np.linspace(100, 110, 10))
    sig = strat.generate(df)
    assert "Insufficient" in sig.reasoning


def test_minimum_rows_exactly_20_no_error():
    """3. 정확히 20행 → 에러 없이 신호 반환"""
    strat = ColoredCandlesStrategy()
    df = _make_df(np.linspace(100, 110, 20))
    sig = strat.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 테스트: HOLD 신호 ────────────────────────────────────────────────────────

def test_flat_candles_hold():
    """4. 동가 캔들 (양봉/음봉 없음) → HOLD"""
    strat = ColoredCandlesStrategy()
    df = _flat_df()
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_is_low():
    """5. HOLD confidence는 LOW"""
    strat = ColoredCandlesStrategy()
    df = _flat_df()
    sig = strat.generate(df)
    assert sig.confidence == Confidence.LOW


# ── 테스트: BUY 신호 ─────────────────────────────────────────────────────────

def test_4_bull_run_buy_signal():
    """6. 연속 4 양봉 + 거래량 증가 → BUY"""
    strat = ColoredCandlesStrategy()
    df = _bull_run_df(bull_count=4, vol_inc=True)
    sig = strat.generate(df)
    assert sig.action == Action.BUY


def test_4_bull_run_high_confidence():
    """7. 연속 4 양봉 → HIGH confidence"""
    strat = ColoredCandlesStrategy()
    df = _bull_run_df(bull_count=4, vol_inc=True)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_bull_run_no_vol_increase_no_buy():
    """8. 연속 양봉이지만 거래량 감소 → BUY 아님"""
    strat = ColoredCandlesStrategy()
    df = _bull_run_df(bull_count=4, vol_inc=False)
    sig = strat.generate(df)
    assert sig.action != Action.BUY


# ── 테스트: SELL 신호 ────────────────────────────────────────────────────────

def test_4_bear_run_sell_signal():
    """9. 연속 4 음봉 + 거래량 증가 → SELL"""
    strat = ColoredCandlesStrategy()
    df = _bear_run_df(bear_count=4, vol_inc=True)
    sig = strat.generate(df)
    assert sig.action == Action.SELL


def test_4_bear_run_high_confidence():
    """10. 연속 4 음봉 → HIGH confidence"""
    strat = ColoredCandlesStrategy()
    df = _bear_run_df(bear_count=4, vol_inc=True)
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence == Confidence.HIGH


def test_bear_run_no_vol_increase_no_sell():
    """11. 연속 음봉이지만 거래량 감소 → SELL 아님"""
    strat = ColoredCandlesStrategy()
    df = _bear_run_df(bear_count=4, vol_inc=False)
    sig = strat.generate(df)
    assert sig.action != Action.SELL


# ── 테스트: Signal 필드 ──────────────────────────────────────────────────────

def test_signal_strategy_name():
    """12. Signal.strategy == 'colored_candles'"""
    strat = ColoredCandlesStrategy()
    df = _flat_df()
    sig = strat.generate(df)
    assert sig.strategy == "colored_candles"


def test_signal_entry_price_is_float():
    """13. Signal.entry_price는 float"""
    strat = ColoredCandlesStrategy()
    df = _flat_df(n=30)
    sig = strat.generate(df)
    assert isinstance(sig.entry_price, float)


def test_strategy_class_name():
    """14. 전략 클래스 이름 속성 = 'colored_candles'"""
    assert ColoredCandlesStrategy.name == "colored_candles"
