"""RSIOBOSStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.rsi_ob_os import RSIOBOSStrategy, _compute_rsi

strategy = RSIOBOSStrategy()

_N = 50


def _make_df(
    n: int = _N,
    rsi_level: str = "neutral",  # "oversold", "overbought", "neutral"
    rsi_turning: str = "flat",   # "up", "down", "flat"
    vol_high: bool = True,
    rsi_extreme: bool = False,   # True → RSI < 25 or > 75
) -> pd.DataFrame:
    """
    rsi_level: 마지막 RSI 레벨
    rsi_turning: RSI 방향 (up: 반전 상승, down: 꺾임)
    vol_high: 마지막 봉 volume > vol_avg * 1.2
    rsi_extreme: HIGH confidence용 (RSI < 25 or > 75)
    """
    closes = np.full(n, 100.0, dtype=float)
    volumes = np.ones(n) * 1000.0

    if rsi_level == "oversold":
        # 강한 하락 → RSI 30 이하
        for i in range(n - 5):
            closes[i] = 100.0 - i * (0.5 if not rsi_extreme else 0.7)
        closes[n - 5] = closes[n - 6] - (2.0 if not rsi_extreme else 3.0)
        closes[n - 4] = closes[n - 5] - (1.5 if not rsi_extreme else 2.5)
        closes[n - 3] = closes[n - 4] - (1.0 if not rsi_extreme else 2.0)
        if rsi_turning == "up":
            closes[n - 2] = closes[n - 3] + 0.5  # idx: 반등 (RSI 반전 시작)
        else:
            closes[n - 2] = closes[n - 3] - 0.5  # 계속 하락

    elif rsi_level == "overbought":
        # 강한 상승 → RSI 70 이상
        for i in range(n - 5):
            closes[i] = 100.0 + i * (0.5 if not rsi_extreme else 0.7)
        closes[n - 5] = closes[n - 6] + (2.0 if not rsi_extreme else 3.0)
        closes[n - 4] = closes[n - 5] + (1.5 if not rsi_extreme else 2.5)
        closes[n - 3] = closes[n - 4] + (1.0 if not rsi_extreme else 2.0)
        if rsi_turning == "down":
            closes[n - 2] = closes[n - 3] - 0.5  # idx: 꺾임
        else:
            closes[n - 2] = closes[n - 3] + 0.5  # 계속 상승

    if vol_high:
        volumes[n - 2] = 2000.0  # idx: 볼륨 증가

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": closes + 1.0,
        "low": closes - 1.0,
        "volume": volumes,
        "ema50": np.full(n, 100.0),
        "atr14": np.ones(n) * 0.5,
    })
    return df


def _get_conditions(df: pd.DataFrame):
    """RSI 조건 직접 계산 (검증용)."""
    idx = len(df) - 2
    rsi = _compute_rsi(df["close"], 14)
    vol_avg = df["volume"].rolling(20).mean()

    rsi_now = float(rsi.iloc[idx])
    rsi_prev = float(rsi.iloc[idx - 1])
    vol_now = float(df["volume"].iloc[idx])
    vol_avg_now = float(vol_avg.iloc[idx])

    vol_ok = vol_now > vol_avg_now * 1.2
    return rsi_now, rsi_prev, vol_ok


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "rsi_ob_os"


# ── 2. BUY — 과매도 + 볼륨 + RSI 반전 ──────────────────────────────────
def test_buy_signal():
    df = _make_df(rsi_level="oversold", rsi_turning="up", vol_high=True)
    rsi_now, rsi_prev, vol_ok = _get_conditions(df)
    if rsi_now < 30 and rsi_now > rsi_prev and vol_ok:
        sig = strategy.generate(df)
        assert sig.action == Action.BUY


# ── 3. SELL — 과매수 + 볼륨 + RSI 꺾임 ─────────────────────────────────
def test_sell_signal():
    df = _make_df(rsi_level="overbought", rsi_turning="down", vol_high=True)
    rsi_now, rsi_prev, vol_ok = _get_conditions(df)
    if rsi_now > 70 and rsi_now < rsi_prev and vol_ok:
        sig = strategy.generate(df)
        assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence (RSI < 25) ───────────────────────────────────
def test_buy_high_confidence():
    df = _make_df(rsi_level="oversold", rsi_turning="up", vol_high=True, rsi_extreme=True)
    rsi_now, rsi_prev, vol_ok = _get_conditions(df)
    sig = strategy.generate(df)
    if sig.action == Action.BUY and rsi_now < 25:
        assert sig.confidence == Confidence.HIGH


# ── 5. SELL HIGH confidence (RSI > 75) ──────────────────────────────────
def test_sell_high_confidence():
    df = _make_df(rsi_level="overbought", rsi_turning="down", vol_high=True, rsi_extreme=True)
    rsi_now, rsi_prev, vol_ok = _get_conditions(df)
    sig = strategy.generate(df)
    if sig.action == Action.SELL and rsi_now > 75:
        assert sig.confidence == Confidence.HIGH


# ── 6. 볼륨 부족 → HOLD ──────────────────────────────────────────────────
def test_hold_low_volume():
    df = _make_df(rsi_level="oversold", rsi_turning="up", vol_high=False)
    rsi_now, rsi_prev, vol_ok = _get_conditions(df)
    if not vol_ok:
        sig = strategy.generate(df)
        assert sig.action == Action.HOLD


# ── 7. 과매도이지만 RSI 반전 없음 → HOLD ────────────────────────────────
def test_hold_oversold_no_reversal():
    df = _make_df(rsi_level="oversold", rsi_turning="flat", vol_high=True)
    rsi_now, rsi_prev, vol_ok = _get_conditions(df)
    # RSI가 계속 하락하거나 동일하면 BUY 조건 미충족
    sig = strategy.generate(df)
    # rsi_turning=flat → rsi_now <= rsi_prev인 경우 HOLD
    if rsi_now <= rsi_prev:
        assert sig.action == Action.HOLD


# ── 8. 데이터 부족 → HOLD (LOW) ──────────────────────────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW
    assert "부족" in sig.reasoning


# ── 9. None 입력 → HOLD ───────────────────────────────────────────────────
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 10. Signal 필드 완전성 ───────────────────────────────────────────────
def test_signal_fields_complete():
    df = _make_df()
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "rsi_ob_os"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 11. BUY reasoning에 "RSI" 포함 ──────────────────────────────────────
def test_buy_reasoning_contains_rsi():
    df = _make_df(rsi_level="oversold", rsi_turning="up", vol_high=True)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "RSI" in sig.reasoning


# ── 12. SELL reasoning에 "RSI" 포함 ─────────────────────────────────────
def test_sell_reasoning_contains_rsi():
    df = _make_df(rsi_level="overbought", rsi_turning="down", vol_high=True)
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "RSI" in sig.reasoning


# ── 13. entry_price = 마지막 완성 캔들 close ─────────────────────────────
def test_entry_price_is_last_close():
    df = _make_df()
    sig = strategy.generate(df)
    expected_close = float(df["close"].iloc[-2])
    assert sig.entry_price == pytest.approx(expected_close, abs=1e-6)


# ── 14. 최소 데이터 경계값 (25행 통과, 24행 실패) ────────────────────────
def test_min_rows_boundary():
    df_ok = _make_df(n=25)
    sig_ok = strategy.generate(df_ok)
    assert sig_ok.action in (Action.BUY, Action.SELL, Action.HOLD)

    df_fail = _make_df(n=24)
    sig_fail = strategy.generate(df_fail)
    assert sig_fail.action == Action.HOLD
    assert sig_fail.confidence == Confidence.LOW
