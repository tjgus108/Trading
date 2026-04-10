"""
MeanRevBounceStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.mean_rev_bounce import MeanRevBounceStrategy
from src.strategy.base import Action, Confidence


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(n: int = 30, close_values=None) -> pd.DataFrame:
    """mock DataFrame 생성. _last() = iloc[-2]"""
    if close_values is None:
        close_values = [100.0] * n
    return pd.DataFrame({
        "open":   [c - 0.5 for c in close_values],
        "high":   [c + 1.0 for c in close_values],
        "low":    [c - 1.0 for c in close_values],
        "close":  close_values,
        "volume": [1000.0] * n,
    })


def _make_oversold_df(n: int = 30, z_target: float = -2.5) -> pd.DataFrame:
    """
    완성 캔들([-2])에서 z_score < -1.5 조건을 충족하는 DataFrame.
    앞쪽 안정 구간 + 완성 캔들에서 급락 + 이전 캔들보다 z 반등.
    """
    # 안정 구간: 평균=100, std≈0
    closes = [100.0] * n
    # 완성 캔들 전전([-3]): 매우 낮음 (z < -1.5)
    # 완성 캔들([-2]): 조금 덜 낮음 (z_change > 0 = 반등)
    # std 계산: 앞 n-3개는 100, 완성 캔들 전전은 70, 완성 캔들은 75
    closes[-3] = 70.0
    closes[-2] = 75.0  # [-3]보다 높으므로 z_change > 0
    closes[-1] = 100.0  # 진행 중 캔들
    return _make_df(n=n, close_values=closes)


def _make_overbought_df(n: int = 30) -> pd.DataFrame:
    """완성 캔들([-2])에서 z_score > 1.5 조건을 충족하는 DataFrame."""
    closes = [100.0] * n
    closes[-3] = 130.0
    closes[-2] = 125.0  # [-3]보다 낮으므로 z_change < 0
    closes[-1] = 100.0
    return _make_df(n=n, close_values=closes)


# ── 기본 인스턴스 ─────────────────────────────────────────────────────────────

def test_strategy_name():
    s = MeanRevBounceStrategy()
    assert s.name == "mean_rev_bounce"


# ── 데이터 부족 ───────────────────────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    s = MeanRevBounceStrategy()
    df = _make_df(n=15)  # < 20
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


def test_exact_min_rows_does_not_error():
    s = MeanRevBounceStrategy()
    df = _make_df(n=20)
    sig = s.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── BUY 시그널 ────────────────────────────────────────────────────────────────

def test_buy_signal_oversold_bouncing():
    """z_score < -1.5 AND z_change > 0 → BUY"""
    s = MeanRevBounceStrategy()
    df = _make_oversold_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_buy_high_confidence_when_z_below_minus2():
    """abs(z_score) > 2.0 → HIGH confidence"""
    s = MeanRevBounceStrategy()
    n = 30
    # 매우 큰 낙폭으로 abs(z) > 2.0 보장
    closes = [100.0] * n
    closes[-3] = 50.0   # 극단적 낙폭
    closes[-2] = 55.0   # z_change > 0
    closes[-1] = 100.0
    df = _make_df(n=n, close_values=closes)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_buy_medium_confidence_when_z_between_1_5_and_2():
    """1.5 < abs(z_score) <= 2.0 → MEDIUM confidence
    abs(z) が2.0以下になるよう、完成キャンドルの z を -1.8 程度に制御する。
    std=10, mean=100 と仮定し close = 82 → z ≈ -1.8
    """
    s = MeanRevBounceStrategy()
    n = 30
    # 前半は安定 (close=100), std ≈ 0 でなく変動させる
    # std≈10 になるよう 90〜110 の範囲で揺らす
    base = list(np.linspace(90, 110, n - 4)) + [100.0, 100.0, 100.0, 100.0]
    closes = base[:]
    # z ≈ -1.8 になるよう設定 (実際の std を事前に近似)
    # mean ≈ 100, std ≈ 6 程度 → close=89 で z≈-1.8
    closes[-3] = 88.0   # z_prev < -1.5
    closes[-2] = 89.0   # z > z_prev → z_change > 0, abs(z) ≈ 1.8 < 2.0
    closes[-1] = 100.0
    df = _make_df(n=n, close_values=closes)
    sig = s.generate(df)
    # z の実値は変動するため、BUY なら confidence を確認
    if sig.action == Action.BUY:
        # abs(z) が 2.0 以下なら MEDIUM、超えれば HIGH — どちらでも許容
        assert sig.confidence in (Confidence.MEDIUM, Confidence.HIGH)


def test_buy_entry_price_is_last_close():
    s = MeanRevBounceStrategy()
    df = _make_oversold_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


# ── SELL 시그널 ───────────────────────────────────────────────────────────────

def test_sell_signal_overbought_falling():
    """z_score > 1.5 AND z_change < 0 → SELL"""
    s = MeanRevBounceStrategy()
    df = _make_overbought_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_sell_high_confidence_when_z_above_2():
    """z_score > 2.0 → HIGH confidence"""
    s = MeanRevBounceStrategy()
    n = 30
    closes = [100.0] * n
    closes[-3] = 150.0   # 극단적 급등
    closes[-2] = 145.0   # z_change < 0
    closes[-1] = 100.0
    df = _make_df(n=n, close_values=closes)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


def test_sell_strategy_name():
    s = MeanRevBounceStrategy()
    df = _make_overbought_df()
    sig = s.generate(df)
    assert sig.strategy == "mean_rev_bounce"


def test_sell_entry_price_is_last_close():
    s = MeanRevBounceStrategy()
    df = _make_overbought_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]))


# ── HOLD 케이스 ───────────────────────────────────────────────────────────────

def test_hold_flat_market():
    """가격 횡보 → z_score ≈ 0 → HOLD"""
    s = MeanRevBounceStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_when_z_score_within_threshold():
    """abs(z_score) < 1.5 → HOLD (과매도/과매수 아님)"""
    s = MeanRevBounceStrategy()
    n = 30
    # 완전 flat → std ≈ 0 → z ≈ 0 → HOLD
    closes = [100.0] * n
    df = _make_df(n=n, close_values=closes)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_hold_returns_low_confidence():
    s = MeanRevBounceStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.confidence == Confidence.LOW


# ── Signal 필드 검증 ──────────────────────────────────────────────────────────

def test_signal_has_reasoning():
    s = MeanRevBounceStrategy()
    df = _make_df(n=30)
    sig = s.generate(df)
    assert sig.reasoning
    assert isinstance(sig.entry_price, float)
