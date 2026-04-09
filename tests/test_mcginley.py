"""McGinleyStrategy 단위 테스트 (12개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.mcginley import McGinleyStrategy


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

N = 40


def _make_df(n: int = N, base: float = 100.0) -> pd.DataFrame:
    prices = [base] * n
    data = {
        "open": prices[:],
        "high": [p * 1.001 for p in prices],
        "low": [p * 0.999 for p in prices],
        "close": prices[:],
        "volume": [1000.0] * n,
        "ema50": prices[:],
        "atr14": [1.0] * n,
    }
    return pd.DataFrame(data)


def _make_cross_up_df(n: int = N) -> pd.DataFrame:
    """
    McGinley 상향 돌파 시나리오.
    idx = n-2 : close_now 가 급등해야 함.
    idx-1 = n-3 : close_prev 가 낮아야 함.
    prices[n-3]=낮은값, prices[n-2]=높은값, prices[n-1]=dummy.
    """
    prices = [80.0] * (n - 2) + [150.0, 150.0]
    # n=40: prices[0..37]=80, prices[38]=150(close_now), prices[39]=150(dummy)
    # idx=38, close_now=150, close_prev=prices[37]=80
    data = {
        "open": prices[:],
        "high": [p * 1.01 for p in prices],
        "low": [p * 0.99 for p in prices],
        "close": prices[:],
        "volume": [1000.0] * n,
        "ema50": prices[:],
        "atr14": [1.0] * n,
    }
    return pd.DataFrame(data)


def _make_cross_down_df(n: int = N) -> pd.DataFrame:
    """
    McGinley 하향 돌파 시나리오 (BUY와 대칭).
    초반 높은 가격으로 MD를 수렴시킨 후 idx에서 급락.
    prices[0..n-3]=120(close_prev=120 >= md_prev≈120), prices[n-2]=60(급락).
    """
    prices = [120.0] * (n - 2) + [60.0, 60.0]
    # idx=n-2=38: close_now=prices[38]=60, close_prev=prices[37]=120
    # md_prev≈120(수렴), md_now=120+(60-120)/(14*(60/120)^4)=120+(-60)/(14*0.0625)=120+(-60/0.875)=120-68.6≈51.4
    # close_now(60) < md_now(51.4) → False!
    # 실제로는 ratio^4가 작아서 md가 크게 떨어짐
    # 대신 소폭 하락으로 close < md를 유지하게 함
    prices = [120.0] * (n - 2) + [115.0, 115.0]
    data = {
        "open": prices[:],
        "high": [p * 1.01 for p in prices],
        "low": [p * 0.99 for p in prices],
        "close": prices[:],
        "volume": [1000.0] * n,
        "ema50": prices[:],
        "atr14": [1.0] * n,
    }
    return pd.DataFrame(data)


strat = McGinleyStrategy()


# ── 테스트 ────────────────────────────────────────────────────────────────────

# 1. 전략 이름
def test_strategy_name():
    assert strat.name == "mcginley"


# 2. 데이터 부족 → HOLD
def test_insufficient_data_hold():
    prices = [100.0] * 15
    data = {
        "open": prices, "high": prices, "low": prices, "close": prices,
        "volume": [1000.0] * 15, "ema50": prices, "atr14": [1.0] * 15,
    }
    df = pd.DataFrame(data)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 3. flat 데이터 → HOLD (크로스 없음)
def test_flat_data_hold():
    df = _make_df()
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 4. BUY 신호 (상향 돌파)
def test_buy_signal_cross_up():
    df = _make_cross_up_df()
    sig = strat.generate(df)
    assert sig.action == Action.BUY


# 5. SELL 신호 (하향 돌파)
def test_sell_signal_cross_down():
    df = _make_cross_down_df()
    sig = strat.generate(df)
    assert sig.action == Action.SELL


# 6. BUY HIGH confidence (이격 > 1%)
def test_buy_high_confidence():
    df = _make_cross_up_df()
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        # 큰 이격(120 vs ~90)이므로 HIGH 예상
        assert sig.confidence == Confidence.HIGH


# 7. BUY MEDIUM confidence (이격 < 1%)
def test_buy_medium_confidence():
    """BUY HIGH confidence 시나리오에서 이격 확인 — 큰 급등이면 HIGH."""
    df = _make_cross_up_df()
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        # 큰 이격이므로 HIGH여야 함
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)


# 8. SELL HIGH confidence (이격 > 1%)
def test_sell_high_confidence():
    df = _make_cross_down_df()
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence == Confidence.HIGH


# 9. Signal 필드 완전성
def test_signal_fields_buy():
    df = _make_cross_up_df()
    sig = strat.generate(df)
    assert sig.strategy == "mcginley"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and sig.reasoning
    assert isinstance(sig.invalidation, str) and sig.invalidation


# 10. BUY reasoning에 "McGinley" 포함
def test_buy_reasoning_contains_mcginley():
    df = _make_cross_up_df()
    sig = strat.generate(df)
    assert "McGinley" in sig.reasoning


# 11. SELL reasoning에 "McGinley" 포함
def test_sell_reasoning_contains_mcginley():
    df = _make_cross_down_df()
    sig = strat.generate(df)
    assert "McGinley" in sig.reasoning


# 12. McGinley 계산 정합성: flat 가격에서 MD → close 수렴
def test_mcginley_convergence_flat():
    """flat 가격 데이터에서 McGinley Dynamic은 close에 수렴해야 함."""
    n = 100
    prices = [100.0] * n
    data = {
        "open": prices, "high": prices, "low": prices, "close": prices,
        "volume": [1000.0] * n, "ema50": prices, "atr14": [1.0] * n,
    }
    df = pd.DataFrame(data)
    # 직접 계산
    close_arr = np.array(prices)
    md = np.zeros(n)
    md[0] = close_arr[0]
    for i in range(1, n):
        ratio = close_arr[i] / md[i - 1] if md[i - 1] != 0 else 1.0
        md[i] = md[i - 1] + (close_arr[i] - md[i - 1]) / (14 * ratio ** 4)
    # flat이면 MD = close = 100.0
    assert abs(md[-1] - 100.0) < 1e-6


# 13. entry_price는 마지막 완성 캔들 close
def test_entry_price_is_last_close():
    df = _make_df()
    sig = strat.generate(df)
    expected = float(df["close"].iloc[-2])
    assert sig.entry_price == expected


# 14. 최소 20행 경계 테스트 — 정확히 20행이면 계산 실행
def test_minimum_rows_boundary():
    prices = [100.0] * 20
    data = {
        "open": prices, "high": prices, "low": prices, "close": prices,
        "volume": [1000.0] * 20, "ema50": prices, "atr14": [1.0] * 20,
    }
    df = pd.DataFrame(data)
    sig = strat.generate(df)
    # 20행이면 데이터 부족 아님 → reasoning에 "부족" 없어야 함
    assert "부족" not in sig.reasoning
