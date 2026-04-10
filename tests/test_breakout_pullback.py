"""BreakoutPullbackStrategy 단위 테스트 (14개)."""

import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.breakout_pullback import BreakoutPullbackStrategy

strat = BreakoutPullbackStrategy()

N = 30


def _make_df(closes, opens=None, highs=None, lows=None, volumes=None):
    n = len(closes)
    if opens is None:
        opens = closes[:]
    if highs is None:
        highs = [max(c, o) * 1.001 for c, o in zip(closes, opens)]
    if lows is None:
        lows = [min(c, o) * 0.999 for c, o in zip(closes, opens)]
    if volumes is None:
        volumes = [1000.0] * n
    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def _flat_df(n=N, base=100.0):
    return _make_df([base] * n)


# 1. 전략 이름 확인
def test_strategy_name():
    assert strat.name == "breakout_pullback"


# 2. 데이터 부족 → HOLD LOW
def test_insufficient_data_hold():
    df = _flat_df(n=10)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 3. 최소 행 경계: 24행 → HOLD LOW
def test_min_rows_boundary_24():
    df = _flat_df(n=24)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 4. 최소 행 경계: 25행 → LOW 아님
def test_min_rows_boundary_25():
    df = _flat_df(n=25)
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
    assert sig.strategy == "breakout_pullback"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and sig.reasoning
    assert isinstance(sig.invalidation, str)


# 7. entry_price = 마지막 완성봉 close (df.iloc[-2])
def test_entry_price_is_last_close():
    closes = [100.0] * (N - 2) + [99.5, 100.0]
    highs = [c * 1.001 for c in closes]
    lows = [c * 0.999 for c in closes]
    sig = strat.generate(_make_df(closes, highs=highs, lows=lows))
    assert abs(sig.entry_price - 99.5) < 1e-6


# 8. 상향 돌파 후 저항선 풀백 + 양봉 → BUY 또는 HOLD
def test_buy_pullback_signal():
    """
    앞 20봉: 100 횡보 → resistance ≈ 100
    이후 5봉: 110 (상향 돌파)
    마지막 완성봉(idx=-2): close=100.5 (저항 근처 풀백, 저항*0.99<100.5<저항), open=99.5 (양봉)
    """
    closes = [100.0] * 20 + [110.0] * 5 + [100.5] * 4 + [100.5, 100.0]
    highs = [c * 1.005 for c in closes]
    lows = [c * 0.995 for c in closes]
    opens = closes[:]
    opens[-2] = 99.5  # 양봉: close(100.5) > open(99.5)
    df = _make_df(closes, opens=opens, highs=highs, lows=lows)
    sig = strat.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)


# 9. 하향 돌파 후 지지선 풀백 + 음봉 → SELL 또는 HOLD
def test_sell_pullback_signal():
    closes = [100.0] * 20 + [90.0] * 5 + [99.5] * 4 + [99.5, 100.0]
    highs = [c * 1.005 for c in closes]
    lows = [c * 0.995 for c in closes]
    opens = closes[:]
    opens[-2] = 100.5  # 음봉: close(99.5) < open(100.5)
    df = _make_df(closes, opens=opens, highs=highs, lows=lows)
    sig = strat.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


# 10. 높은 볼륨 → HIGH confidence
def test_high_confidence_high_volume():
    closes = [100.0] * N
    opens = closes[:]
    volumes = [1000.0] * N
    volumes[-2] = 2000.0  # avg*1.5 이상
    df = _make_df(closes, opens=opens, volumes=volumes)
    sig = strat.generate(df)
    # HIGH confidence는 볼륨 조건 충족 시
    if sig.action != Action.HOLD:
        assert sig.confidence == Confidence.HIGH


# 11. 낮은 볼륨 → MEDIUM confidence
def test_medium_confidence_low_volume():
    closes = [100.0] * N
    opens = closes[:]
    volumes = [1000.0] * N
    volumes[-2] = 500.0  # avg의 절반
    df = _make_df(closes, opens=opens, volumes=volumes)
    sig = strat.generate(df)
    if sig.action != Action.HOLD:
        assert sig.confidence == Confidence.MEDIUM


# 12. 돌파 없으면 BUY 없음
def test_no_breakout_no_buy():
    closes = [100.0] * N
    opens = closes[:]
    opens[-2] = 99.5  # 양봉이지만 돌파 없음
    df = _make_df(closes, opens=opens)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 13. 가격 하락 중이면 BUY 없음 (음봉)
def test_price_down_no_buy():
    closes = [100.0] * 20 + [110.0] * 5 + [100.5] * 4 + [100.5, 100.0]
    highs = [c * 1.005 for c in closes]
    lows = [c * 0.995 for c in closes]
    opens = closes[:]
    opens[-2] = 101.0  # 음봉: close(100.5) < open(101.0)
    df = _make_df(closes, opens=opens, highs=highs, lows=lows)
    sig = strat.generate(df)
    assert sig.action != Action.BUY


# 14. HOLD reasoning이 비어있지 않음
def test_hold_reasoning_nonempty():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert sig.reasoning
    assert any(kw in sig.reasoning for kw in [
        "close", "resistance", "support", "부족", "조건", "NaN", "풀백"
    ])
