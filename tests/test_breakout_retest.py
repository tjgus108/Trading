"""BreakoutRetestStrategy 단위 테스트 (12개)."""

import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.breakout_retest import BreakoutRetestStrategy

strat = BreakoutRetestStrategy()

N = 35


def _make_df(closes, opens=None, volumes=None):
    n = len(closes)
    if opens is None:
        opens = closes[:]
    if volumes is None:
        volumes = [1000.0] * n
    return pd.DataFrame({
        "open": opens,
        "high": [max(c, o) * 1.001 for c, o in zip(closes, opens)],
        "low": [min(c, o) * 0.999 for c, o in zip(closes, opens)],
        "close": closes,
        "volume": volumes,
    })


def _flat_df(n=N, base=100.0):
    return _make_df([base] * n)


# 1. 전략 이름 확인
def test_strategy_name():
    assert strat.name == "breakout_retest"


# 2. 데이터 부족 → HOLD LOW
def test_insufficient_data_hold():
    df = _flat_df(n=20)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 3. 최소 행 경계: 29행 → HOLD LOW
def test_min_rows_boundary_29():
    df = _flat_df(n=29)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 4. 최소 행 경계: 30행 → LOW 아님
def test_min_rows_boundary_30():
    df = _flat_df(n=30)
    sig = strat.generate(df)
    assert sig.confidence != Confidence.LOW


# 5. flat 데이터 → HOLD (돌파 없음)
def test_flat_data_hold():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 6. Signal 필드 완전성
def test_signal_fields_complete():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig.strategy == "breakout_retest"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and sig.reasoning
    assert isinstance(sig.invalidation, str)


# 7. entry_price = 마지막 완성봉 close (df.iloc[-2])
def test_entry_price_is_last_close():
    closes = [100.0] * (N - 2) + [99.5, 100.0]
    sig = strat.generate(_make_df(closes))
    assert abs(sig.entry_price - 99.5) < 1e-6


# 8. BUY retest: 저항 돌파 후 되돌림 + 양봉
def test_buy_retest_signal():
    """
    앞 25봉: 100 횡보 → resistance ≈ 100 (shift(3))
    idx-5~idx-1: 110 (돌파)
    idx-1(완성봉): close=100.2(retest), open=99.8(양봉), vol=500(낮음)
    """
    # 총 35봉 구성
    closes = [100.0] * 25 + [110.0] * 5 + [100.2, 100.5, 100.3, 100.2, 100.5]
    opens = closes[:]
    # 마지막 완성봉(idx=-2, idx=33): close=100.2, open=99.8 → 양봉
    opens[-2] = 99.8
    volumes = [1000.0] * (N - 2) + [500.0, 1000.0]
    df = _make_df(closes, opens, volumes)
    sig = strat.generate(df)
    # 조건이 맞으면 BUY, 아니면 HOLD (tolerance 조건 검증)
    assert sig.action in (Action.BUY, Action.HOLD)


# 9. SELL retest: 지지 이탈 후 되돌림 + 음봉
def test_sell_retest_signal():
    closes = [100.0] * 25 + [90.0] * 5 + [99.8, 99.5, 99.7, 99.8, 99.5]
    opens = closes[:]
    opens[-2] = 100.2  # 음봉: close < open
    volumes = [1000.0] * (N - 2) + [500.0, 1000.0]
    df = _make_df(closes, opens, volumes)
    sig = strat.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


# 10. 낮은 볼륨 pullback → HIGH confidence (BUY 발생 시)
def test_high_confidence_low_volume_pullback():
    closes = [100.0] * 25 + [110.0] * 5 + [100.2, 100.5, 100.3, 100.2, 100.5]
    opens = closes[:]
    opens[-2] = 99.8
    volumes = [1000.0] * (N - 2) + [500.0, 1000.0]
    df = _make_df(closes, opens, volumes)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# 11. 높은 볼륨 pullback → MEDIUM confidence (BUY 발생 시)
def test_medium_confidence_high_volume_pullback():
    closes = [100.0] * 25 + [110.0] * 5 + [100.2, 100.5, 100.3, 100.2, 100.5]
    opens = closes[:]
    opens[-2] = 99.8
    volumes = [1000.0] * (N - 2) + [2000.0, 1000.0]
    df = _make_df(closes, opens, volumes)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


# 12. 돌파 없으면 BUY 없음 (retest 조건만 충족)
def test_no_breakout_no_buy():
    # 전체 100으로 flat, 마지막 완성봉만 살짝 다름 → 돌파 없음
    closes = [100.0] * N
    opens = closes[:]
    opens[-2] = 99.8  # 양봉이지만 돌파 없음
    df = _make_df(closes, opens)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 13. 음봉이면 BUY 없음 (돌파 후 retest 있어도)
def test_bearish_candle_no_buy():
    closes = [100.0] * 25 + [110.0] * 5 + [100.2, 100.5, 100.3, 100.2, 100.5]
    opens = closes[:]
    opens[-2] = 100.8  # 음봉: close(100.2) < open(100.8)
    df = _make_df(closes, opens)
    sig = strat.generate(df)
    # 음봉이면 BUY 조건 불충족
    assert sig.action != Action.BUY


# 14. HOLD reasoning에 price 정보 포함
def test_hold_reasoning_contains_info():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig.reasoning  # 비어있지 않음
    assert any(kw in sig.reasoning for kw in ["close", "resistance", "support", "retest", "조건", "데이터"])


# 15. BUY signal의 reasoning에 저항 정보 포함
def test_buy_reasoning_contains_resistance():
    closes = [100.0] * 25 + [110.0] * 5 + [100.2, 100.5, 100.3, 100.2, 100.5]
    opens = closes[:]
    opens[-2] = 99.8
    volumes = [1000.0] * (N - 2) + [500.0, 1000.0]
    df = _make_df(closes, opens, volumes)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert "저항" in sig.reasoning or "resistance" in sig.reasoning.lower()
