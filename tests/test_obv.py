"""OBVStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.obv import OBVStrategy

strategy = OBVStrategy()


def _make_df(n=50, close_above_ema=True, cross="none", sustained=False):
    """
    cross: "up" → OBV가 OBV_EMA를 상향 돌파 (idx-1 → idx 기준)
           "down" → OBV가 OBV_EMA를 하향 돌파
           "none" → 크로스 없음
    sustained: True  → obv_prev2 > ema_prev2 (HIGH conf, idx-2에도 이미 같은 방향)
               False → obv_prev2 <= ema_prev2 (MEDIUM conf, 방금 크로스)
    close_above_ema: close vs ema50 위치
    """
    base_close = 110.0 if close_above_ema else 90.0
    ema50_val = 100.0

    closes = np.full(n, base_close, dtype=float)
    volumes = np.ones(n) * 1000.0

    # cross=up: idx-1에서 크로스 발생 (obv_prev <= ema_prev, obv_now > ema_now)
    # HIGH(sustained): obv_prev2 > ema_prev2 — idx-2에서 이미 OBV > EMA
    # MEDIUM: obv_prev2 <= ema_prev2 — idx-2까지는 OBV <= EMA
    #
    # 구현 전략:
    #   앞 n-5 봉: 하락(OBV 낮춤) → EMA도 낮아짐
    #   sustained=True: n-5 ~ n-4 봉 강한 상승 → OBV를 EMA 위로 올림 (obv_prev2 > ema_prev2)
    #                   n-3(idx-1) 봉 약한 하락 → OBV가 EMA 아래로 (obv_prev <= ema_prev)
    #                   n-2(idx) 봉 강한 상승 → OBV > EMA 다시 (cross_up)
    #   sustained=False: n-3(idx-1) 봉 하락 → obv_prev <= ema_prev
    #                    n-2(idx) 봉 강한 상승 → cross_up

    if cross == "up":
        if sustained:
            # HIGH conf: obv_prev2 > ema_prev2
            # 앞 절반 하락 → OBV 낮음, 중간부터 지속 상승 → OBV가 EMA 위로
            # 그 후 idx-1(n-3)에서 하락으로 OBV가 EMA 아래로 (obv_prev <= ema_prev)
            # idx(n-2)에서 강한 상승 → cross_up
            half = n // 2
            for i in range(half):
                closes[i] = base_close - 1.0   # 전반부 하락
            for i in range(half, n - 4):
                closes[i] = base_close + 1.0   # 후반부 상승 → OBV 역전
            closes[n - 4] = base_close + 1.0   # idx-2: OBV > EMA (sustained)
            closes[n - 3] = base_close - 2.0   # idx-1: 하락 → OBV가 EMA 아래
            closes[n - 2] = base_close + 4.0   # idx: 강한 상승 → cross_up
        else:
            # MEDIUM conf: obv_prev2 <= ema_prev2
            for i in range(n - 3):
                closes[i] = base_close - 1.0   # 전부 하락
            closes[n - 3] = base_close - 1.0   # idx-1: 하락 (obv_prev <= ema_prev)
            closes[n - 2] = base_close + 8.0   # idx: 강한 상승 → cross_up

    elif cross == "down":
        if sustained:
            # HIGH conf: obv_prev2 < ema_prev2
            half = n // 2
            for i in range(half):
                closes[i] = base_close + 1.0   # 전반부 상승
            for i in range(half, n - 4):
                closes[i] = base_close - 1.0   # 후반부 하락 → OBV 역전
            closes[n - 4] = base_close - 1.0   # idx-2: OBV < EMA (sustained)
            closes[n - 3] = base_close + 2.0   # idx-1: 상승 → OBV가 EMA 위
            closes[n - 2] = base_close - 4.0   # idx: 강한 하락 → cross_down
        else:
            # MEDIUM conf: obv_prev2 >= ema_prev2
            for i in range(n - 3):
                closes[i] = base_close + 1.0   # 전부 상승
            closes[n - 3] = base_close + 1.0   # idx-1: 상승 (obv_prev >= ema_prev)
            closes[n - 2] = base_close - 8.0   # idx: 강한 하락 → cross_down

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": closes + 0.5,
        "low": closes - 0.5,
        "volume": volumes,
        "ema50": np.full(n, ema50_val),
        "atr14": np.ones(n) * 0.5,
    })
    return df


def _compute_obv_cross(df):
    """OBV 및 크로스 상태 반환 (검증용)."""
    idx = len(df) - 2
    close_diff = df["close"].diff()
    obv = (df["volume"] * close_diff.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))).cumsum()
    obv_ema = obv.ewm(span=20, adjust=False).mean()

    obv_now = float(obv.iloc[idx])
    obv_prev = float(obv.iloc[idx - 1])
    ema_now = float(obv_ema.iloc[idx])
    ema_prev = float(obv_ema.iloc[idx - 1])
    obv_prev2 = float(obv.iloc[idx - 2])
    ema_prev2 = float(obv_ema.iloc[idx - 2])

    cross_up = obv_prev <= ema_prev and obv_now > ema_now
    cross_down = obv_prev >= ema_prev and obv_now < ema_now
    return cross_up, cross_down, obv_prev2, ema_prev2


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "obv"


# ── 2. BUY 신호 (OBV 상향 크로스, close>ema50) ───────────────────────────
def test_buy_signal():
    df = _make_df(cross="up", close_above_ema=True, sustained=False)
    cross_up, cross_down, _, _ = _compute_obv_cross(df)
    assert cross_up, "cross_up이 True여야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 (OBV 하향 크로스, close<ema50) ──────────────────────────
def test_sell_signal():
    df = _make_df(cross="down", close_above_ema=False, sustained=False)
    cross_up, cross_down, _, _ = _compute_obv_cross(df)
    assert cross_down, "cross_down이 True여야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence (2봉 전에도 OBV > EMA) ────────────────────────
def test_buy_high_confidence():
    df = _make_df(cross="up", close_above_ema=True, sustained=True)
    cross_up, _, obv_prev2, ema_prev2 = _compute_obv_cross(df)
    assert cross_up, "cross_up이 True여야 함"
    assert obv_prev2 > ema_prev2, f"obv_prev2({obv_prev2:.0f}) > ema_prev2({ema_prev2:.0f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 5. BUY MEDIUM confidence (방금 크로스) ───────────────────────────────
def test_buy_medium_confidence():
    df = _make_df(cross="up", close_above_ema=True, sustained=False)
    cross_up, _, obv_prev2, ema_prev2 = _compute_obv_cross(df)
    assert cross_up, "cross_up이 True여야 함"
    assert obv_prev2 <= ema_prev2, f"obv_prev2({obv_prev2:.0f}) <= ema_prev2({ema_prev2:.0f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 6. SELL HIGH confidence (2봉 전에도 OBV < EMA) ───────────────────────
def test_sell_high_confidence():
    df = _make_df(cross="down", close_above_ema=False, sustained=True)
    _, cross_down, obv_prev2, ema_prev2 = _compute_obv_cross(df)
    assert cross_down, "cross_down이 True여야 함"
    assert obv_prev2 < ema_prev2, f"obv_prev2({obv_prev2:.0f}) < ema_prev2({ema_prev2:.0f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 7. SELL MEDIUM confidence (방금 크로스) ──────────────────────────────
def test_sell_medium_confidence():
    df = _make_df(cross="down", close_above_ema=False, sustained=False)
    _, cross_down, obv_prev2, ema_prev2 = _compute_obv_cross(df)
    assert cross_down, "cross_down이 True여야 함"
    assert obv_prev2 >= ema_prev2, f"obv_prev2({obv_prev2:.0f}) >= ema_prev2({ema_prev2:.0f}) 이어야 함"
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 8. OBV>EMA이지만 close<ema50 → HOLD ─────────────────────────────────
def test_buy_obv_cross_but_below_ema_hold():
    df = _make_df(cross="up", close_above_ema=False, sustained=False)
    cross_up, _, _, _ = _compute_obv_cross(df)
    assert cross_up, "cross_up이 True여야 함"
    close_val = float(df["close"].iloc[-2])
    ema50_val = float(df["ema50"].iloc[-2])
    assert close_val < ema50_val
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 9. 데이터 부족 → HOLD ────────────────────────────────────────────────
def test_insufficient_data():
    df = _make_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 10. Signal 필드 완전성 ───────────────────────────────────────────────
def test_signal_fields():
    df = _make_df(n=50)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "obv"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 11. BUY reasoning에 "OBV" 포함 ──────────────────────────────────────
def test_buy_reasoning_contains_obv():
    df = _make_df(cross="up", close_above_ema=True, sustained=False)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "OBV" in sig.reasoning


# ── 12. SELL reasoning에 "OBV" 포함 ─────────────────────────────────────
def test_sell_reasoning_contains_obv():
    df = _make_df(cross="down", close_above_ema=False, sustained=False)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "OBV" in sig.reasoning


# ── 13. None 입력 → HOLD ─────────────────────────────────────────────────
def test_none_data():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 14. HOLD 신호 (크로스 없음) ──────────────────────────────────────────
def test_hold_no_cross():
    df = _make_df(cross="none", close_above_ema=True)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
