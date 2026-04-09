"""ADLStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.adl import ADLStrategy

strategy = ADLStrategy()

_EMA_SPAN = 14


def _clv_sign_df(n=60, close_above_ema=True, cross="none", sustained=False):
    """
    CLV 기반으로 ADL 크로스를 직접 설계.
    - CLV ≈ +1: close == high (extreme bullish candle)
    - CLV ≈ -1: close == low  (extreme bearish candle)
    강한 CLV를 여러 봉 주면 ADL이 EMA를 충분히 앞지를 수 있다.
    """
    ema50_val = 100.0
    base_close = 110.0 if close_above_ema else 90.0
    vol = 1000.0
    spread = 2.0  # high - low

    # 기본 candle: neutral (close at midpoint → CLV = 0)
    closes = np.full(n, base_close, dtype=float)
    highs  = closes + spread
    lows   = closes - spread
    volumes = np.full(n, vol)

    def bullish(i):
        """close == high → CLV = +1"""
        highs[i]  = closes[i]
        lows[i]   = closes[i] - spread * 2

    def bearish(i):
        """close == low → CLV = -1"""
        lows[i]   = closes[i]
        highs[i]  = closes[i] + spread * 2

    def neutral(i):
        highs[i] = closes[i] + spread
        lows[i]  = closes[i] - spread

    if cross == "up":
        # 앞 절반: bearish candles → ADL 내려가고 EMA도 낮아짐
        half = n // 2
        for i in range(half):
            bearish(i)

        if sustained:
            # idx-2에서도 ADL > EMA (HIGH conf):
            # half ~ n-4: 강한 bullish 연속 → ADL 높이고 EMA 위로
            for i in range(half, n - 4):
                bullish(i)
            # idx-2 (n-4): bullish 유지 → ADL > EMA
            bullish(n - 4)
            # idx-1 (n-3): 극강 bearish × 대량 볼륨 → ADL이 EMA 밑으로 급락
            bearish(n - 3)
            volumes[n - 3] = vol * 50
            # idx   (n-2): 극강 bullish × 대량 볼륨 → ADL이 EMA 위로 (cross_up)
            bullish(n - 2)
            volumes[n - 2] = vol * 80
        else:
            # 앞 n-3봉 모두 bearish → EMA도 낮음, idx-1도 bearish
            for i in range(half, n - 3):
                bearish(i)
            bearish(n - 3)
            # idx(n-2): 극강 bullish 대량 볼륨 → ADL이 EMA 위로 순간 뛰어오름
            bullish(n - 2)
            volumes[n - 2] = vol * 50

    elif cross == "down":
        half = n // 2
        for i in range(half):
            bullish(i)

        if sustained:
            for i in range(half, n - 4):
                bearish(i)
            bearish(n - 4)
            # idx-1 (n-3): 극강 bullish × 대량 볼륨 → ADL이 EMA 위로 잠깐 올라감
            bullish(n - 3)
            volumes[n - 3] = vol * 50
            # idx   (n-2): 극강 bearish × 대량 볼륨 → ADL이 EMA 아래로 (cross_down)
            bearish(n - 2)
            volumes[n - 2] = vol * 80
        else:
            for i in range(half, n - 3):
                bullish(i)
            bullish(n - 3)
            bearish(n - 2)
            volumes[n - 2] = vol * 50

    else:
        # neutral — 모두 mid-point
        for i in range(n):
            neutral(i)

    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   highs,
        "low":    lows,
        "volume": volumes,
        "ema50":  np.full(n, ema50_val),
        "atr14":  np.ones(n) * 0.5,
    })
    return df


def _compute_adl_cross(df):
    """ADL 및 크로스 상태 반환 (검증용)."""
    idx = len(df) - 2
    clv = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"] + 1e-10)
    mfv = clv * df["volume"]
    adl = mfv.cumsum()
    adl_ema = adl.ewm(span=_EMA_SPAN, adjust=False).mean()

    adl_now   = float(adl.iloc[idx])
    adl_prev  = float(adl.iloc[idx - 1])
    ema_now   = float(adl_ema.iloc[idx])
    ema_prev  = float(adl_ema.iloc[idx - 1])
    adl_prev2 = float(adl.iloc[idx - 2])
    ema_prev2 = float(adl_ema.iloc[idx - 2])

    cross_up   = adl_prev <= ema_prev and adl_now > ema_now
    cross_down = adl_prev >= ema_prev and adl_now < ema_now
    return cross_up, cross_down, adl_prev2, ema_prev2


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "adl"


# ── 2. BUY 신호 (ADL 상향 크로스, close>ema50) ───────────────────────────
def test_buy_signal():
    df = _clv_sign_df(cross="up", close_above_ema=True, sustained=False)
    cross_up, _, _, _ = _compute_adl_cross(df)
    assert cross_up, "cross_up이 True여야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 (ADL 하향 크로스, close<ema50) ──────────────────────────
def test_sell_signal():
    df = _clv_sign_df(cross="down", close_above_ema=False, sustained=False)
    _, cross_down, _, _ = _compute_adl_cross(df)
    assert cross_down, "cross_down이 True여야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence (adl_prev2 > ema_prev2) ──────────────────────
def test_buy_high_confidence():
    df = _clv_sign_df(cross="up", close_above_ema=True, sustained=True)
    cross_up, _, adl_prev2, ema_prev2 = _compute_adl_cross(df)
    assert cross_up, "cross_up이 True여야 함"
    assert adl_prev2 > ema_prev2, f"adl_prev2({adl_prev2:.2f}) > ema_prev2({ema_prev2:.2f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 5. BUY MEDIUM confidence (adl_prev2 <= ema_prev2) ───────────────────
def test_buy_medium_confidence():
    df = _clv_sign_df(cross="up", close_above_ema=True, sustained=False)
    cross_up, _, adl_prev2, ema_prev2 = _compute_adl_cross(df)
    assert cross_up, "cross_up이 True여야 함"
    assert adl_prev2 <= ema_prev2, f"adl_prev2({adl_prev2:.2f}) <= ema_prev2({ema_prev2:.2f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 6. SELL HIGH confidence (adl_prev2 < ema_prev2) ─────────────────────
def test_sell_high_confidence():
    df = _clv_sign_df(cross="down", close_above_ema=False, sustained=True)
    _, cross_down, adl_prev2, ema_prev2 = _compute_adl_cross(df)
    assert cross_down, "cross_down이 True여야 함"
    assert adl_prev2 < ema_prev2, f"adl_prev2({adl_prev2:.2f}) < ema_prev2({ema_prev2:.2f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 7. SELL MEDIUM confidence (adl_prev2 >= ema_prev2) ──────────────────
def test_sell_medium_confidence():
    df = _clv_sign_df(cross="down", close_above_ema=False, sustained=False)
    _, cross_down, adl_prev2, ema_prev2 = _compute_adl_cross(df)
    assert cross_down, "cross_down이 True여야 함"
    assert adl_prev2 >= ema_prev2, f"adl_prev2({adl_prev2:.2f}) >= ema_prev2({ema_prev2:.2f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 8. ADL 상향 크로스이지만 close < ema50 → HOLD ───────────────────────
def test_buy_cross_but_below_ema50_hold():
    df = _clv_sign_df(cross="up", close_above_ema=False, sustained=False)
    cross_up, _, _, _ = _compute_adl_cross(df)
    assert cross_up, "cross_up이 True여야 함"
    close_val = float(df["close"].iloc[-2])
    ema50_val = float(df["ema50"].iloc[-2])
    assert close_val < ema50_val
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 9. ADL 하향 크로스이지만 close > ema50 → HOLD ───────────────────────
def test_sell_cross_but_above_ema50_hold():
    df = _clv_sign_df(cross="down", close_above_ema=True, sustained=False)
    _, cross_down, _, _ = _compute_adl_cross(df)
    assert cross_down, "cross_down이 True여야 함"
    close_val = float(df["close"].iloc[-2])
    ema50_val = float(df["ema50"].iloc[-2])
    assert close_val > ema50_val
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 10. 데이터 부족 → HOLD ──────────────────────────────────────────────
def test_insufficient_data():
    df = _clv_sign_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 11. None 입력 → HOLD ────────────────────────────────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 12. Signal 필드 완전성 ──────────────────────────────────────────────
def test_signal_fields():
    df = _clv_sign_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "adl"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 13. BUY reasoning에 "ADL" 포함 ─────────────────────────────────────
def test_buy_reasoning_contains_adl():
    df = _clv_sign_df(cross="up", close_above_ema=True, sustained=False)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "ADL" in sig.reasoning


# ── 14. SELL reasoning에 "ADL" 포함 ────────────────────────────────────
def test_sell_reasoning_contains_adl():
    df = _clv_sign_df(cross="down", close_above_ema=False, sustained=False)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "ADL" in sig.reasoning


# ── 15. HOLD 신호 (크로스 없음) ─────────────────────────────────────────
def test_hold_no_cross():
    df = _clv_sign_df(cross="none", close_above_ema=True)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
