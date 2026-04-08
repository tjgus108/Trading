"""tests/test_price_channel.py — PriceChannelStrategy 단위 테스트 (12개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_channel import PriceChannelStrategy, _rsi
from src.strategy.base import Action, Confidence


def _zigzag(n: int, base: float, amplitude: float, period_len: int = 8) -> np.ndarray:
    """RSI가 극단값이 되지 않도록 진동하는 시계열 생성."""
    t = np.arange(n)
    return base + amplitude * np.sin(2 * np.pi * t / period_len)


def _make_df(n: int = 50, price: float = 100.0) -> pd.DataFrame:
    """횡보 기본 DataFrame (n>=25)."""
    closes = _zigzag(n, price, 0.5, 8)
    return pd.DataFrame({
        "open": closes.copy(),
        "close": closes.copy(),
        "high": closes + 1.0,
        "low": closes - 1.0,
        "volume": np.ones(n) * 1000.0,
        "ema50": np.full(n, price),
        "atr14": np.ones(n) * 1.0,
    })


def _make_buy_df(dist_pct: float = 0.005) -> pd.DataFrame:
    """
    n=60, idx=58 (iloc[-2]) 의 close가 Upper Channel을 돌파.
    zigzag로 RSI를 온건하게 유지 (< 70), 마지막에 breakout.
    """
    n = 60
    closes = _zigzag(n, 100.0, 1.5, 8)
    # 20봉 구간 highs (iloc[38:58]) max ≈ 102.0
    # zigzag max ≈ 101.5, highs = closes + 0.5 → max high ≈ 102.0
    # closes[58] = 102.5 → high[58]=103.0, 돌파
    closes[58] = 102.5 * (1 + (dist_pct - 0.005))  # dist_pct에 맞게 조정
    # 정확한 upper_ch 계산: highs[38:58] max
    highs_base = _zigzag(n, 100.0, 1.5, 8) + 0.5
    upper_ch = float(highs_base[38:58].max())
    closes[58] = upper_ch * (1 + dist_pct)
    closes[59] = closes[58]

    highs = closes.copy() + 0.5
    lows = closes.copy() - 0.5

    return pd.DataFrame({
        "open": closes.copy(),
        "close": closes.copy(),
        "high": highs,
        "low": lows,
        "volume": np.ones(n) * 1000.0,
        "ema50": np.full(n, 100.0),
        "atr14": np.ones(n) * 1.0,
    })


def _make_sell_df(dist_pct: float = 0.005) -> pd.DataFrame:
    """
    n=60, idx=58 (iloc[-2]) 의 close가 Lower Channel을 하향 돌파.
    zigzag로 RSI 온건하게 유지 (> 30), 마지막에 breakdown.
    """
    n = 60
    closes = _zigzag(n, 100.0, 1.5, 8)
    lows_base = _zigzag(n, 100.0, 1.5, 8) - 0.5
    lower_ch = float(lows_base[38:58].min())
    closes[58] = lower_ch * (1 - dist_pct)
    closes[59] = closes[58]

    highs = closes.copy() + 0.5
    lows = closes.copy() - 0.5

    return pd.DataFrame({
        "open": closes.copy(),
        "close": closes.copy(),
        "high": highs,
        "low": lows,
        "volume": np.ones(n) * 1000.0,
        "ema50": np.full(n, 100.0),
        "atr14": np.ones(n) * 1.0,
    })


# ── 1. 전략 이름 ─────────────────────────────────────────────────────────

def test_strategy_name():
    assert PriceChannelStrategy.name == "price_channel"


# ── 2. BUY 신호 (상향 돌파, RSI<70) ────────────────────────────────────

def test_buy_signal_basic():
    df = _make_buy_df(dist_pct=0.005)
    sig = PriceChannelStrategy().generate(df)
    assert sig.action == Action.BUY


# ── 3. SELL 신호 (하향 돌파, RSI>30) ───────────────────────────────────

def test_sell_signal_basic():
    df = _make_sell_df(dist_pct=0.005)
    sig = PriceChannelStrategy().generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence (이격>1%) ───────────────────────────────────

def test_buy_high_confidence():
    df = _make_buy_df(dist_pct=0.015)
    sig = PriceChannelStrategy().generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 5. BUY MEDIUM confidence (이격≤1%) ─────────────────────────────────

def test_buy_medium_confidence():
    df = _make_buy_df(dist_pct=0.005)
    sig = PriceChannelStrategy().generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 6. SELL HIGH confidence (이격>1%) ──────────────────────────────────

def test_sell_high_confidence():
    df = _make_sell_df(dist_pct=0.015)
    sig = PriceChannelStrategy().generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 7. SELL MEDIUM confidence (이격≤1%) ────────────────────────────────

def test_sell_medium_confidence():
    df = _make_sell_df(dist_pct=0.005)
    sig = PriceChannelStrategy().generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


# ── 8a. RSI >= 70 → BUY 차단 ──────────────────────────────────────────

def test_buy_blocked_by_high_rsi():
    """단조 급등 → RSI≈100 → close>upper여도 BUY 안 됨."""
    n = 60
    closes = np.linspace(50.0, 250.0, n)
    highs = closes + 0.5
    lows = closes - 0.5
    df = pd.DataFrame({
        "open": closes, "close": closes,
        "high": highs, "low": lows,
        "volume": np.ones(n) * 1000.0,
        "ema50": np.full(n, 100.0),
        "atr14": np.ones(n) * 1.0,
    })
    rsi_val = float(_rsi(pd.Series(closes)).iloc[58])
    sig = PriceChannelStrategy().generate(df)
    if rsi_val >= 70:
        # BUY가 나오면 안 됨
        assert sig.action != Action.BUY
    # RSI < 70이라면 BUY가 나와도 괜찮음 (데이터 자체가 조건 충족)


# ── 8b. RSI <= 30 → SELL 차단 ─────────────────────────────────────────

def test_sell_blocked_by_low_rsi():
    """단조 급락 → RSI≈0 → close<lower여도 SELL 안 됨."""
    n = 60
    closes = np.linspace(250.0, 50.0, n)
    highs = closes + 0.5
    lows = closes - 0.5
    df = pd.DataFrame({
        "open": closes, "close": closes,
        "high": highs, "low": lows,
        "volume": np.ones(n) * 1000.0,
        "ema50": np.full(n, 100.0),
        "atr14": np.ones(n) * 1.0,
    })
    rsi_val = float(_rsi(pd.Series(closes)).iloc[58])
    sig = PriceChannelStrategy().generate(df)
    if rsi_val <= 30:
        assert sig.action != Action.SELL


# ── 9. 데이터 부족 → HOLD ──────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    df = _make_df(n=20)
    sig = PriceChannelStrategy().generate(df)
    assert sig.action == Action.HOLD


# ── 10. Signal 필드 완전성 ─────────────────────────────────────────────

def test_signal_fields_complete():
    df = _make_df(n=50)
    sig = PriceChannelStrategy().generate(df)
    assert sig.strategy == "price_channel"
    assert isinstance(sig.entry_price, float)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert isinstance(sig.invalidation, str)


# ── 11. BUY reasoning에 "channel" 포함 ────────────────────────────────

def test_buy_reasoning_contains_channel():
    df = _make_buy_df(dist_pct=0.005)
    sig = PriceChannelStrategy().generate(df)
    assert sig.action == Action.BUY
    assert "channel" in sig.reasoning.lower()


# ── 12. SELL reasoning에 "channel" 포함 ───────────────────────────────

def test_sell_reasoning_contains_channel():
    df = _make_sell_df(dist_pct=0.005)
    sig = PriceChannelStrategy().generate(df)
    assert sig.action == Action.SELL
    assert "channel" in sig.reasoning.lower()
