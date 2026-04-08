"""
KeltnerChannelStrategy 단위 테스트
"""

import math
import pandas as pd
import pytest

from src.strategy.keltner_channel import KeltnerChannelStrategy
from src.strategy.base import Action, Confidence


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_df(closes, atr14=2.0) -> pd.DataFrame:
    """close 리스트로 DataFrame 생성. atr14는 스칼라 또는 리스트."""
    n = len(closes)
    if isinstance(atr14, (int, float)):
        atr14_col = [float(atr14)] * n
    else:
        atr14_col = list(atr14)
    return pd.DataFrame({
        "open":   [100.0] * n,
        "high":   [105.0] * n,
        "low":    [95.0]  * n,
        "close":  closes,
        "volume": [1000.0] * n,
        "ema50":  [100.0]  * n,
        "atr14":  atr14_col,
    })


def _descending(n: int, start: float = 200.0, step: float = 2.0) -> list:
    """
    n개의 연속 하락 시리즈.
    RSI: 순수 하락이면 gain=0, loss>0 → RSI → 0.
    atr14를 1로 설정하면 EMA-2 < 현재 close가 되려면 close가 매우 낮아야 함.
    → atr14를 크게 설정해서 lower band를 높게 유지.
    """
    return [start - i * step for i in range(n)]


def _ascending(n: int, start: float = 0.0, step: float = 2.0) -> list:
    """n개의 연속 상승 시리즈. RSI → 100."""
    return [start + i * step for i in range(n)]


def _buy_df(n: int = 40, step: float = 2.0):
    """
    BUY 신호용 DataFrame.
    - 앞 n-2개: 고가 유지 → EMA 높게 → RSI: 나중에 하락으로 낮아짐
    - close[-2]: 매우 낮게 → close << lower band
    - atr14=1 → lower = EMA - 2, EMA가 높으면 lower도 높음
    전략: 앞쪽 하락 시리즈(EMA 높게 유지)에서 끝을 극단 하락으로 만듦.
    n-2개를 하락 시리즈로 만들되 EMA가 close[-2]보다 훨씬 높도록 step을 작게,
    마지막은 그보다 훨씬 낮게 설정.
    """
    # 앞 n-2개: 1000에서 1까지 하락
    base_closes = [1000.0 - i * (999.0 / (n - 2)) for i in range(n - 2)]
    # EMA(20) of base_closes의 마지막 값 ≈ 앞쪽 가중치 → 500 이상
    # close[-2] = 1.0 (매우 낮음), atr=1 → lower = EMA - 2 ≈ 498 >> close[-2]=1
    closes = base_closes + [1.0, 1.0]   # [-2]=1.0, [-1]=1.0
    return _make_df(closes, atr14=1.0)


def _sell_df(n: int = 40, step: float = 2.0):
    """
    SELL 신호용 DataFrame.
    - 앞 n-2개: 상승 시리즈
    - close[-2]: 매우 높게 → close >> upper band
    """
    base_closes = [1.0 + i * (999.0 / (n - 2)) for i in range(n - 2)]
    # EMA(20) ≈ 앞쪽 가중치 → 500 이하
    # close[-2] = 1000.0, atr=1 → upper = EMA + 2 ≈ 502 << close[-2]=1000
    closes = base_closes + [1000.0, 1000.0]
    return _make_df(closes, atr14=1.0)


# ── 테스트 1: 전략 이름 ────────────────────────────────────────────────────────

def test_strategy_name():
    s = KeltnerChannelStrategy()
    assert s.name == "keltner_channel"


# ── 테스트 2: BUY 신호 ────────────────────────────────────────────────────────

def test_buy_signal():
    """close < Lower, RSI < 40 → BUY"""
    s = KeltnerChannelStrategy()
    df = _buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


# ── 테스트 3: SELL 신호 ───────────────────────────────────────────────────────

def test_sell_signal():
    """close > Upper, RSI > 60 → SELL"""
    s = KeltnerChannelStrategy()
    df = _sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


# ── 테스트 4: BUY HIGH confidence (RSI < 30) ────────────────────────────────

def test_buy_high_confidence():
    """순수 하락 → RSI → 0 → BUY HIGH"""
    s = KeltnerChannelStrategy()
    df = _buy_df(n=40, step=3.0)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 테스트 5: BUY MEDIUM or HIGH confidence ──────────────────────────────────

def test_buy_medium_or_high_confidence():
    """BUY 시 confidence는 HIGH 또는 MEDIUM"""
    s = KeltnerChannelStrategy()
    df = _buy_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 테스트 6: SELL HIGH confidence (RSI > 70) ───────────────────────────────

def test_sell_high_confidence():
    """순수 상승 → RSI → 100 → SELL HIGH"""
    s = KeltnerChannelStrategy()
    df = _sell_df(n=40, step=3.0)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


# ── 테스트 7: SELL MEDIUM or HIGH confidence ─────────────────────────────────

def test_sell_medium_or_high_confidence():
    """SELL 시 confidence는 HIGH 또는 MEDIUM"""
    s = KeltnerChannelStrategy()
    df = _sell_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# ── 테스트 8: close < Lower이지만 RSI >= 40 → HOLD ─────────────────────────

def test_hold_when_close_below_lower_but_rsi_neutral():
    """
    RSI가 중립 (≈50) 이면서 close가 band 내부 → HOLD.
    sin 패턴(상승/하락 교대)으로 RSI ≈ 50, ATR 충분히 커서 band 내부 유지.
    """
    s = KeltnerChannelStrategy()
    n = 40
    # 진동 패턴 → RSI ≈ 50, close도 EMA 근처
    closes = [100.0 + 5.0 * math.sin(i * 0.8) for i in range(n)]
    # atr=100 → lower=EMA-200, upper=EMA+200 → close≈100은 band 내부 → HOLD
    df = _make_df(closes, atr14=100.0)
    sig = s.generate(df)
    assert sig.action == Action.HOLD


# ── 테스트 9: 데이터 부족 → HOLD ────────────────────────────────────────────

def test_insufficient_data_returns_hold():
    """25행 미만 → HOLD"""
    s = KeltnerChannelStrategy()
    closes = [100.0] * 20
    df = _make_df(closes)
    sig = s.generate(df)
    assert sig.action == Action.HOLD
    assert "Insufficient" in sig.reasoning


# ── 테스트 10: Signal 필드 완전성 ───────────────────────────────────────────

def test_signal_fields_complete():
    """Signal 객체의 필수 필드가 모두 존재하는지 확인"""
    s = KeltnerChannelStrategy()
    closes = [100.0] * 30
    df = _make_df(closes)
    sig = s.generate(df)
    assert hasattr(sig, "action")
    assert hasattr(sig, "confidence")
    assert hasattr(sig, "strategy")
    assert hasattr(sig, "entry_price")
    assert hasattr(sig, "reasoning")
    assert hasattr(sig, "invalidation")
    assert hasattr(sig, "bull_case")
    assert hasattr(sig, "bear_case")
    assert isinstance(sig.entry_price, float)


# ── 테스트 11: BUY reasoning에 "Keltner" 포함 ───────────────────────────────

def test_buy_reasoning_contains_keltner():
    """BUY 신호 reasoning에 'Keltner' 포함"""
    s = KeltnerChannelStrategy()
    df = _buy_df(n=40, step=3.0)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert "Keltner" in sig.reasoning


# ── 테스트 12: SELL reasoning에 "Keltner" 포함 ──────────────────────────────

def test_sell_reasoning_contains_keltner():
    """SELL 신호 reasoning에 'Keltner' 포함"""
    s = KeltnerChannelStrategy()
    df = _sell_df(n=40, step=3.0)
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert "Keltner" in sig.reasoning


# ── 테스트 13: strategy 필드 = "keltner_channel" ────────────────────────────

def test_signal_strategy_field():
    """Signal.strategy == 'keltner_channel'"""
    s = KeltnerChannelStrategy()
    closes = [100.0] * 30
    df = _make_df(closes)
    sig = s.generate(df)
    assert sig.strategy == "keltner_channel"


# ── 테스트 14: entry_price = iloc[-2].close ──────────────────────────────────

def test_entry_price_equals_last_close():
    """entry_price는 항상 iloc[-2].close"""
    s = KeltnerChannelStrategy()
    df = _buy_df(n=40, step=3.0)
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert sig.entry_price == pytest.approx(df.iloc[-2]["close"])
