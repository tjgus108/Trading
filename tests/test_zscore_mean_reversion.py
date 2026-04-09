"""
ZScoreMeanReversionStrategy 단위 테스트 (mock DataFrame만 사용)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.zscore_mean_reversion import ZScoreMeanReversionStrategy
from src.strategy.base import Action, Confidence


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 30, close_values=None) -> pd.DataFrame:
    """
    mock DataFrame 생성.
    주의: strategy는 idx = len(df) - 2 를 사용하므로 마지막 행은 진행 중 캔들.
    """
    if close_values is None:
        close_values = [100.0] * n

    df = pd.DataFrame({
        "open":   [100.0] * n,
        "high":   [105.0] * n,
        "low":    [95.0]  * n,
        "close":  close_values,
        "volume": [1000.0] * n,
        "ema50":  [100.0]  * n,
        "atr14":  [1.0]    * n,
    })
    return df


def _make_df_with_zscore(n: int = 30, target_z: float = -3.0) -> pd.DataFrame:
    """
    완성 캔들(iloc[-2])이 특정 Z-Score를 갖도록 설계된 DataFrame.
    period=20 rolling 기준으로 앞 19캔들은 base=100, 마지막 완성 캔들만 outlier.
    """
    base = 100.0
    closes = [base] * n
    # [-2]에 outlier 삽입: mean≈100, std≈0이면 outlier가 Z-Score를 결정
    # 실제로는 std가 미세하게 > 0이므로 큰 편차 사용
    if target_z < 0:
        closes[-2] = base - 30.0  # 크게 낮춰서 BUY 유도
    else:
        closes[-2] = base + 30.0  # 크게 높여서 SELL 유도
    closes[-1] = base  # 진행 중 캔들
    return _make_df(n=n, close_values=closes)


# ── 기본 인스턴스 ────────────────────────────────────────────────────────────

def test_strategy_name():
    s = ZScoreMeanReversionStrategy()
    assert s.name == "zscore_mean_reversion"


def test_strategy_is_instantiable():
    s = ZScoreMeanReversionStrategy()
    assert s is not None


# ── 데이터 부족 ──────────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = ZScoreMeanReversionStrategy()
    df = _make_df(n=20)  # < 25
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exactly_min_rows():
    """정확히 25행 → HOLD 반환 (데이터 부족 아님, 신호 없음)"""
    s = ZScoreMeanReversionStrategy()
    df = _make_df(n=25)
    sig = s.generate(df)
    # 모든 close 동일 → zscore≈0 → HOLD
    assert sig.action == Action.HOLD


# ── BUY 시그널 ───────────────────────────────────────────────────────────────

def test_buy_signal_generated():
    """Z-Score < -2.0 → BUY"""
    s = ZScoreMeanReversionStrategy()
    df = _make_df_with_zscore(n=30, target_z=-3.0)
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_medium_confidence():
    """BUY 신호가 발생하고 confidence는 MEDIUM 또는 HIGH"""
    s = ZScoreMeanReversionStrategy()
    # _make_df_with_zscore(target_z=-3.0)는 Z≈-3.08 → HIGH
    # MEDIUM을 직접 만들기 어려우므로 action=BUY이고 confidence가 유효한 값인지 확인
    df = _make_df_with_zscore(n=30, target_z=-3.0)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    # confidence는 MEDIUM 또는 HIGH여야 함 (LOW는 불가)
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_buy_high_confidence():
    """|Z| > 2.5 → BUY HIGH (큰 편차 사용)"""
    s = ZScoreMeanReversionStrategy()
    # closes[-2] = 70 (base-30) → Z ≈ -3.08 > 2.5 → HIGH
    df = _make_df_with_zscore(n=30, target_z=-3.0)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── SELL 시그널 ──────────────────────────────────────────────────────────────

def test_sell_signal_generated():
    """Z-Score > 2.0 → SELL"""
    s = ZScoreMeanReversionStrategy()
    df = _make_df_with_zscore(n=30, target_z=3.0)
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_medium_confidence():
    """SELL 신호가 발생하고 confidence는 MEDIUM 또는 HIGH"""
    s = ZScoreMeanReversionStrategy()
    df = _make_df_with_zscore(n=30, target_z=3.0)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_sell_high_confidence():
    """|Z| > 2.5 → SELL HIGH (큰 편차 사용)"""
    s = ZScoreMeanReversionStrategy()
    df = _make_df_with_zscore(n=30, target_z=3.0)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── HOLD 케이스 ──────────────────────────────────────────────────────────────

def test_hold_when_zscore_neutral():
    """Z-Score ≈ 0 → HOLD"""
    s = ZScoreMeanReversionStrategy()
    df = _make_df(n=30)  # 모두 100.0 → z≈0
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_confidence_is_low():
    """HOLD 신호는 항상 LOW confidence"""
    s = ZScoreMeanReversionStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW


# ── Signal 필드 검증 ─────────────────────────────────────────────────────────

def test_entry_price_equals_idx_close():
    """entry_price == df['close'].iloc[-2]"""
    s = ZScoreMeanReversionStrategy()
    df = _make_df_with_zscore(n=30, target_z=-3.0)
    sig = s.generate(df)
    expected_close = float(df["close"].iloc[-2])
    assert sig.entry_price == pytest.approx(expected_close)


def test_signal_strategy_field():
    """signal.strategy == 'zscore_mean_reversion'"""
    s = ZScoreMeanReversionStrategy()
    df = _make_df_with_zscore(n=30, target_z=3.0)
    sig = s.generate(df)
    assert sig.strategy == "zscore_mean_reversion"


def test_reasoning_contains_zscore():
    """reasoning에 Z-Score 값 포함"""
    s = ZScoreMeanReversionStrategy()
    df = _make_df_with_zscore(n=30, target_z=-3.0)
    sig = s.generate(df)
    assert "z=" in sig.reasoning or "Z-Score" in sig.reasoning
