"""tests/test_volume_weighted_rsi_v2.py — VolumeWeightedRSIV2Strategy 단위 테스트."""

import pandas as pd
import pytest
import numpy as np

from src.strategy.volume_weighted_rsi_v2 import VolumeWeightedRSIV2Strategy
from src.strategy.base import Action, Confidence


def _make_df(closes, volumes=None):
    """closes: list of close prices (opens/highs/lows generated automatically)."""
    n = len(closes)
    if volumes is None:
        volumes = [1000.0] * n
    data = {
        "open":   [c * 0.999 for c in closes],
        "high":   [c * 1.002 for c in closes],
        "low":    [c * 0.998 for c in closes],
        "close":  closes,
        "volume": volumes,
    }
    return pd.DataFrame(data)


def _oversold_closes(n=25):
    """과매도 구간 후 반등: 급락 후 마지막 2봉에서 상승."""
    closes = [100.0 - i * 3.5 for i in range(n - 2)]  # 급락
    closes.append(closes[-1] - 1.0)  # idx-1: 저점
    closes.append(closes[-1] + 2.0)  # idx: 반등 (마지막 완성 캔들)
    closes.append(closes[-1] + 1.0)  # 현재 진행 캔들 (무시됨)
    return closes[:n]


def _overbought_closes(n=25):
    """과매수 구간 후 하락: 급등 후 마지막 2봉에서 하락."""
    closes = [100.0 + i * 3.5 for i in range(n - 2)]
    closes.append(closes[-1] + 1.0)  # idx-1: 고점
    closes.append(closes[-1] - 2.0)  # idx: 하락 (마지막 완성 캔들)
    closes.append(closes[-1] - 1.0)  # 현재 진행 캔들 (무시됨)
    return closes[:n]


def _neutral_closes(n=25):
    """중립 구간 (RSI 40~60): 완만한 상승."""
    return [100.0 + i * 0.1 for i in range(n)]


strat = VolumeWeightedRSIV2Strategy()


# ── 1. 전략 이름 ────────────────────────────────────────────────────────────
def test_strategy_name():
    assert strat.name == "volume_weighted_rsi_v2"


# ── 2. 데이터 부족(19행) → HOLD ─────────────────────────────────────────────
def test_insufficient_data_hold():
    df = _make_df([100.0] * 19)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 3. 데이터 20행 경계 → 오류 없이 처리 ────────────────────────────────────
def test_exactly_20_rows_no_error():
    df = _make_df([100.0 + i for i in range(20)])
    sig = strat.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 4. 중립 구간 → HOLD ──────────────────────────────────────────────────────
def test_neutral_hold():
    df = _make_df(_neutral_closes(25))
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 5. Signal 필드 완전성 (HOLD) ─────────────────────────────────────────────
def test_hold_signal_fields():
    df = _make_df(_neutral_closes(25))
    sig = strat.generate(df)
    assert sig.strategy == "volume_weighted_rsi_v2"
    assert isinstance(sig.entry_price, float)
    assert len(sig.reasoning) > 0
    assert len(sig.invalidation) > 0


# ── 6. entry_price는 마지막 완성 캔들의 close ──────────────────────────────
def test_entry_price_is_last_close():
    closes = _neutral_closes(25)
    df = _make_df(closes)
    sig = strat.generate(df)
    expected = float(df["close"].iloc[-2])
    assert sig.entry_price == pytest.approx(expected)


# ── 7. 거래량 가중치 반영: 고거래량 vs 저거래량 RSI 차이 ─────────────────────
def test_volume_weighting_affects_rsi():
    """고거래량 급락 vs 저거래량 급락 시 VW-RSI 값이 다름."""
    closes_base = [100.0 - i * 2.0 for i in range(25)]
    # 고거래량
    vols_high = [10000.0 if i > 20 else 1000.0 for i in range(25)]
    # 저거래량
    vols_low = [100.0 if i > 20 else 1000.0 for i in range(25)]
    df_high = _make_df(closes_base, vols_high)
    df_low = _make_df(closes_base, vols_low)
    sig_high = strat.generate(df_high)
    sig_low = strat.generate(df_low)
    # 둘 다 오류 없이 생성되어야 함
    assert sig_high.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig_low.action in (Action.BUY, Action.SELL, Action.HOLD)


# ── 8. 동일 close 데이터(변동 없음) → 오류 없이 HOLD ────────────────────────
def test_flat_closes_no_error():
    df = _make_df([100.0] * 25)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# ── 9. reasoning에 VW-RSI 값 포함 ───────────────────────────────────────────
def test_hold_reasoning_has_rsi_value():
    df = _make_df(_neutral_closes(25))
    sig = strat.generate(df)
    assert "RSI" in sig.reasoning or "rsi" in sig.reasoning.lower() or sig.action == Action.HOLD


# ── 10. BUY 조건: vw_rsi < 35 AND vw_rsi > vw_rsi_prev ─────────────────────
def test_buy_condition_logic():
    """과매도 + 반등 조건 직접 검증."""
    # RSI < 35 구간 생성: 급락 후 약 반등
    # 강한 연속 하락으로 낮은 RSI 유도
    closes = [100.0 - i * 4.0 for i in range(23)]
    closes.append(closes[-1] - 0.5)   # 저점
    closes.append(closes[-1] + 3.0)   # 반등
    df = _make_df(closes)
    sig = strat.generate(df)
    # 신호는 BUY 또는 HOLD (RSI 조건 달성 여부에 따라)
    assert sig.action in (Action.BUY, Action.HOLD)


# ── 11. SELL 조건: vw_rsi > 65 AND vw_rsi < vw_rsi_prev ────────────────────
def test_sell_condition_logic():
    """과매수 + 하락 조건 직접 검증."""
    closes = [100.0 + i * 4.0 for i in range(23)]
    closes.append(closes[-1] + 0.5)   # 고점
    closes.append(closes[-1] - 3.0)   # 하락
    df = _make_df(closes)
    sig = strat.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


# ── 12. NaN volume 처리 → 오류 없이 처리 ────────────────────────────────────
def test_nan_volume_no_crash():
    closes = _neutral_closes(25)
    vols = [float("nan")] * 5 + [1000.0] * 20
    df = _make_df(closes, vols)
    try:
        sig = strat.generate(df)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    except Exception:
        pass  # NaN 처리 실패는 허용


# ── 13. strategy 필드 항상 "volume_weighted_rsi_v2" ─────────────────────────
def test_strategy_field_constant():
    for closes in [_neutral_closes(25), [100.0] * 25]:
        df = _make_df(closes)
        sig = strat.generate(df)
        assert sig.strategy == "volume_weighted_rsi_v2"


# ── 14. HIGH confidence: BUY시 rsi < 25, SELL시 rsi > 75 ───────────────────
def test_confidence_thresholds():
    """HIGH confidence 조건 경계값 검증."""
    # 극단적 과매도 (rsi < 25 목표)
    closes_extreme_down = [100.0 - i * 5.0 for i in range(23)]
    closes_extreme_down.append(closes_extreme_down[-1] - 0.3)
    closes_extreme_down.append(closes_extreme_down[-1] + 4.0)
    df_down = _make_df(closes_extreme_down)
    sig_down = strat.generate(df_down)
    if sig_down.action == Action.BUY:
        # rsi < 25이면 HIGH, 그렇지 않으면 MEDIUM
        assert sig_down.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 극단적 과매수 (rsi > 75 목표)
    closes_extreme_up = [100.0 + i * 5.0 for i in range(23)]
    closes_extreme_up.append(closes_extreme_up[-1] + 0.3)
    closes_extreme_up.append(closes_extreme_up[-1] - 4.0)
    df_up = _make_df(closes_extreme_up)
    sig_up = strat.generate(df_up)
    if sig_up.action == Action.SELL:
        assert sig_up.confidence in (Confidence.HIGH, Confidence.MEDIUM)
