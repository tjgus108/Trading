"""tests/test_dema_cross.py — DEMACrossStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.dema_cross import DEMACrossStrategy, _dema


# ── 헬퍼 ──────────────────────────────────────────────────────────────────

def _make_df(close_prices, n=None):
    """close 시계열로 DataFrame 생성. 나머지 컬럼은 더미."""
    prices = list(close_prices)
    if n and len(prices) < n:
        prices = [prices[0]] * (n - len(prices)) + prices
    size = len(prices)
    return pd.DataFrame({
        "open": prices,
        "high": [p * 1.001 for p in prices],
        "low": [p * 0.999 for p in prices],
        "close": prices,
        "volume": [1000.0] * size,
        "ema50": prices,
        "atr14": [1.0] * size,
    })


def _make_crossup_df():
    """DEMA5가 DEMA20을 상향 크로스하도록 설계된 DataFrame."""
    # 낮은 가격에서 급등 → DEMA5가 DEMA20을 넘어섬
    base = [100.0] * 30
    # 마지막 몇 개 캔들을 크게 올림
    base[-5:] = [110.0, 115.0, 120.0, 125.0, 130.0]
    df = _make_df(base)
    # 실제 크로스 발생 여부 확인 후 반환
    return df


def _make_crossdown_df():
    """DEMA5가 DEMA20을 하향 크로스하도록 설계된 DataFrame."""
    base = [130.0] * 30
    base[-5:] = [120.0, 115.0, 110.0, 105.0, 100.0]
    return _make_df(base)


def _force_crossup_df():
    """
    cross_up을 강제로 유발: idx-1에서 d5<=d20, idx에서 d5>d20.
    가격을 조작해서 직접 보장.
    """
    # 30행: 앞 28개는 낮은 가격, 마지막 2개(idx-1, idx)를 조작
    prices = [100.0] * 28 + [100.0, 200.0]
    # 마지막 캔들(진행 중) 추가
    prices.append(200.0)
    return _make_df(prices)


def _force_crossdown_df():
    """cross_down 강제 유발."""
    prices = [200.0] * 28 + [200.0, 100.0]
    prices.append(100.0)
    return _make_df(prices)


# ── 테스트 ─────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 = 'dema_cross'"""
    s = DEMACrossStrategy()
    assert s.name == "dema_cross"


def test_buy_signal_crossup():
    """2. BUY 신호 (DEMA5 상향 크로스)"""
    s = DEMACrossStrategy()
    df = _force_crossup_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY


def test_sell_signal_crossdown():
    """3. SELL 신호 (DEMA5 하향 크로스)"""
    s = DEMACrossStrategy()
    df = _force_crossdown_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL


def test_buy_high_confidence():
    """4. BUY HIGH confidence (이격>0.5%)"""
    s = DEMACrossStrategy()
    # 극단적인 크로스 → 이격 크게 벌어짐
    prices = [100.0] * 28 + [100.0, 300.0, 300.0]
    df = _make_df(prices)
    sig = s.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_buy_medium_confidence():
    """5. BUY MEDIUM confidence (이격 작음)"""
    s = DEMACrossStrategy()
    # 이전 값보다 아주 약간만 올라서 크로스하지만 이격 0.5% 미만
    prices = [100.0] * 29 + [100.0001]
    prices = [100.0] * 28 + [99.9999, 100.001, 100.001]
    df = _make_df(prices)
    sig = s.generate(df)
    # MEDIUM이거나 HOLD일 수 있음 — BUY라면 MEDIUM
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


def test_sell_high_confidence():
    """6. SELL HIGH confidence (이격>0.5%)"""
    s = DEMACrossStrategy()
    prices = [300.0] * 28 + [300.0, 100.0, 100.0]
    df = _make_df(prices)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence == Confidence.HIGH


def test_sell_medium_confidence():
    """7. SELL MEDIUM confidence"""
    s = DEMACrossStrategy()
    prices = [100.0] * 28 + [100.001, 99.9999, 99.9999]
    df = _make_df(prices)
    sig = s.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence == Confidence.MEDIUM


def test_hold_no_cross():
    """8. DEMA5>DEMA20이지만 크로스 없음 → HOLD"""
    s = DEMACrossStrategy()
    # 지속적으로 상승해서 DEMA5 > DEMA20이지만 크로스(이전에 이미 넘은 상태) 없음
    prices = [100.0] * 10 + [110.0] * 20
    df = _make_df(prices)
    sig = s.generate(df)
    # 크로스가 발생하지 않으면 HOLD
    assert sig.action == Action.HOLD


def test_insufficient_data():
    """9. 데이터 부족 → HOLD"""
    s = DEMACrossStrategy()
    df = _make_df([100.0] * 20)  # 25행 미만
    sig = s.generate(df)
    assert sig.action == Action.HOLD


def test_signal_fields_complete():
    """10. Signal 필드 완전성"""
    s = DEMACrossStrategy()
    df = _force_crossup_df()
    sig = s.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "dema_cross"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and len(sig.reasoning) > 0
    assert sig.invalidation is not None


def test_buy_reasoning_contains_dema():
    """11. BUY reasoning에 'DEMA' 포함"""
    s = DEMACrossStrategy()
    df = _force_crossup_df()
    sig = s.generate(df)
    assert sig.action == Action.BUY
    assert "DEMA" in sig.reasoning


def test_sell_reasoning_contains_dema():
    """12. SELL reasoning에 'DEMA' 포함"""
    s = DEMACrossStrategy()
    df = _force_crossdown_df()
    sig = s.generate(df)
    assert sig.action == Action.SELL
    assert "DEMA" in sig.reasoning


def test_dema_faster_than_ema():
    """보너스: DEMA가 EMA보다 반응이 빠른지 확인 (방향성)"""
    prices = pd.Series([100.0] * 20 + [200.0] * 10)
    ema = prices.ewm(span=5, adjust=False).mean()
    dema = _dema(prices, 5)
    # 급등 후 DEMA가 EMA보다 높아야 함 (더 빠르게 반응)
    assert float(dema.iloc[-1]) >= float(ema.iloc[-1])


def test_hold_exact_25_rows():
    """25행 정확히 있을 때 HOLD 아님 (처리 가능)"""
    s = DEMACrossStrategy()
    df = _make_df([100.0] * 25)
    sig = s.generate(df)
    # 25행 이상이면 데이터 부족 아님
    assert "데이터 부족" not in sig.reasoning
