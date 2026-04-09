"""TurtleTradingStrategy 단위 테스트 (12개+)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.turtle_trading import TurtleTradingStrategy

strategy = TurtleTradingStrategy()


def _make_df(n=70, scenario="hold"):
    """
    scenario:
      "buy20"   → 20봉 최고가 돌파 (MEDIUM)
      "buy55"   → 20봉 + 55봉 최고가 모두 돌파 (HIGH)
      "sell20"  → 20봉 최저가 하향 돌파 (MEDIUM)
      "sell55"  → 20봉 + 55봉 최저가 모두 하향 돌파 (HIGH)
      "no_vol"  → 채널 돌파하지만 볼륨 부족 → HOLD
      "hold"    → 신호 없음
    """
    base = 100.0
    closes = np.full(n, base, dtype=float)
    highs = closes + 1.0
    lows = closes - 1.0
    volumes = np.ones(n) * 1000.0

    idx = n - 2  # 신호 생성 인덱스

    if scenario == "buy20":
        # 20봉 최고가를 살짝 낮게 유지하고 idx 봉에서 돌파
        highs[idx - 20:idx] = base + 0.5   # 20봉 high = 101.5
        closes[idx] = base + 1.0           # close = 101.0 > 101.5? → 아니므로 조정
        highs[idx - 20:idx] = base + 0.3   # 20봉 high max = 101.3
        closes[idx] = base + 0.5           # close = 100.5 > 100.3 → 돌파
        # 볼륨 충분
        volumes[idx] = 2000.0
        # 55봉 채널: idx 봉 close < h55이어야 MEDIUM
        highs[idx - 55:idx - 20] = base + 2.0  # h55 > close

    elif scenario == "buy55":
        # 20봉 + 55봉 모두 돌파
        highs[idx - 55:idx] = base + 0.3
        closes[idx] = base + 0.5          # > h55 = h20 = 100.3
        volumes[idx] = 2000.0

    elif scenario == "sell20":
        lows[idx - 20:idx] = base - 0.3   # 20봉 low min = 99.7
        closes[idx] = base - 0.5          # close = 99.5 < 99.7
        volumes[idx] = 2000.0
        lows[idx - 55:idx - 20] = base - 2.0  # l55 < close (MEDIUM)

    elif scenario == "sell55":
        lows[idx - 55:idx] = base - 0.3
        closes[idx] = base - 0.5          # < l55 = l20 = 99.7
        volumes[idx] = 2000.0

    elif scenario == "no_vol":
        highs[idx - 20:idx] = base + 0.3
        closes[idx] = base + 0.5
        volumes[idx] = 500.0  # 볼륨 부족 (평균 1000 > 500)

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": volumes,
        "ema50": np.full(n, base),
        "atr14": np.full(n, 1.0),
    })
    return df


# ── 기본 케이스 ────────────────────────────────────────────────

def test_buy20_action():
    sig = strategy.generate(_make_df(scenario="buy20"))
    assert sig.action == Action.BUY


def test_buy20_medium_confidence():
    sig = strategy.generate(_make_df(scenario="buy20"))
    assert sig.confidence == Confidence.MEDIUM


def test_buy55_action():
    sig = strategy.generate(_make_df(scenario="buy55"))
    assert sig.action == Action.BUY


def test_buy55_high_confidence():
    sig = strategy.generate(_make_df(scenario="buy55"))
    assert sig.confidence == Confidence.HIGH


def test_sell20_action():
    sig = strategy.generate(_make_df(scenario="sell20"))
    assert sig.action == Action.SELL


def test_sell20_medium_confidence():
    sig = strategy.generate(_make_df(scenario="sell20"))
    assert sig.confidence == Confidence.MEDIUM


def test_sell55_action():
    sig = strategy.generate(_make_df(scenario="sell55"))
    assert sig.action == Action.SELL


def test_sell55_high_confidence():
    sig = strategy.generate(_make_df(scenario="sell55"))
    assert sig.confidence == Confidence.HIGH


def test_no_vol_hold():
    """볼륨 부족 시 HOLD."""
    sig = strategy.generate(_make_df(scenario="no_vol"))
    assert sig.action == Action.HOLD


def test_hold_scenario():
    sig = strategy.generate(_make_df(scenario="hold"))
    assert sig.action == Action.HOLD


# ── 데이터 부족 ────────────────────────────────────────────────

def test_insufficient_data_hold():
    """60행 미만 → HOLD."""
    df = _make_df(n=50, scenario="hold")
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


def test_insufficient_data_low_confidence():
    df = _make_df(n=30, scenario="hold")
    sig = strategy.generate(df)
    assert sig.confidence == Confidence.LOW


# ── Signal 필드 검증 ────────────────────────────────────────────

def test_signal_has_strategy_name():
    sig = strategy.generate(_make_df(scenario="hold"))
    assert sig.strategy == "turtle_trading"


def test_buy_entry_price_is_close():
    df = _make_df(scenario="buy55")
    sig = strategy.generate(df)
    idx = len(df) - 2
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[idx]))


def test_sell_entry_price_is_close():
    df = _make_df(scenario="sell55")
    sig = strategy.generate(df)
    idx = len(df) - 2
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[idx]))


def test_buy_reasoning_mentions_atr():
    sig = strategy.generate(_make_df(scenario="buy20"))
    assert "ATR14" in sig.reasoning


def test_sell_reasoning_mentions_exit_channel():
    sig = strategy.generate(_make_df(scenario="sell20"))
    assert "10-bar high" in sig.reasoning


def test_buy_invalidation_mentions_10bar_low():
    sig = strategy.generate(_make_df(scenario="buy20"))
    assert "10-bar low" in sig.invalidation
