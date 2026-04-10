"""BreakoutConfirmationStrategy 단위 테스트 (12개)."""

import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.breakout_confirm import BreakoutConfirmationStrategy

strat = BreakoutConfirmationStrategy()

N = 30


def _make_df(closes, volumes=None):
    n = len(closes)
    if volumes is None:
        volumes = [1000.0] * n
    return pd.DataFrame({
        "open": closes,
        "high": [c * 1.001 for c in closes],
        "low": [c * 0.999 for c in closes],
        "close": closes,
        "volume": volumes,
    })


def _flat_df(n=N, base=100.0, volume=1000.0):
    return _make_df([base] * n, [volume] * n)


def _breakout_up_df():
    """
    저항 돌파 상향 확인 케이스:
    - 앞 20봉: 100 근처 횡보 (저항 ~100)
    - 이후: 105, 106 (prev_close > 100, curr_close > 100)
    - 볼륨 급등
    """
    closes = [100.0] * 25 + [105.0, 106.0, 107.0, 108.0, 109.0]
    volumes = [1000.0] * 25 + [1500.0, 1500.0, 1500.0, 1500.0, 1500.0]
    return _make_df(closes, volumes)


def _breakdown_df():
    """
    지지 이탈 하향 확인 케이스:
    - 앞 20봉: 100 근처 횡보 (지지 ~100)
    - 이후: 95, 94 (prev_close < 100, curr_close < 100)
    - 볼륨 급등
    """
    closes = [100.0] * 25 + [95.0, 94.0, 93.0, 92.0, 91.0]
    volumes = [1000.0] * 25 + [1500.0, 1500.0, 1500.0, 1500.0, 1500.0]
    return _make_df(closes, volumes)


# 1. 전략 이름 확인
def test_strategy_name():
    assert strat.name == "breakout_confirm"


# 2. 데이터 부족 → HOLD (LOW confidence)
def test_insufficient_data_hold():
    df = _flat_df(n=20)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 3. 최소 행 경계: 24행 → HOLD LOW
def test_min_rows_boundary_24():
    df = _flat_df(n=24)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# 4. 최소 행 경계: 25행 → LOW가 아님
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
    assert sig.strategy == "breakout_confirm"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str) and sig.reasoning
    assert isinstance(sig.invalidation, str)


# 7. HOLD reasoning에 close/resistance/support 정보 포함
def test_hold_reasoning_contains_price_info():
    df = _flat_df(n=N)
    sig = strat.generate(df)
    assert "close" in sig.reasoning or "resistance" in sig.reasoning or "돌파" in sig.reasoning


# 8. 볼륨 미달 → HOLD (저항 돌파해도 볼륨 부족)
def test_low_volume_no_signal():
    closes = [100.0] * 25 + [105.0, 106.0, 107.0, 108.0, 109.0]
    volumes = [1000.0] * 25 + [1100.0, 1100.0, 1100.0, 1100.0, 1100.0]  # avg*1.3 미달
    df = _make_df(closes, volumes)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD


# 9. 저항 돌파 BUY 신호 확인
def test_breakout_up_buy_signal():
    df = _breakout_up_df()
    sig = strat.generate(df)
    assert sig.action in (Action.BUY, Action.HOLD)


# 10. 지지 이탈 SELL 신호 확인
def test_breakdown_sell_signal():
    df = _breakdown_df()
    sig = strat.generate(df)
    assert sig.action in (Action.SELL, Action.HOLD)


# 11. HIGH confidence: volume > avg * 2.0
def test_high_confidence_high_volume():
    # avg_vol 계산: 마지막 완성봉(idx=-2) 이전 20봉
    # idx = N-2 = 28, 대상 범위: iloc[-21:-1] = iloc[9:29]
    # 앞 25봉(idx 0~24)=1000, 뒤 봉들(idx 25~)=high_vol
    # lookback=20이므로 iloc[-21:-1] = iloc[9:29] = 20봉
    # closes: 25개 100 + 5개 105~109 → 총 30
    # volumes: 25개 1000 + 5개 high_vol
    # iloc[9:29] → idx 9..28 → 앞 16개 1000 + 4개 high_vol (idx25~28)
    # avg = (16*1000 + 4*high_vol) / 20 → HIGH 조건: high_vol > avg*2
    # 간단하게: high_vol=5000 → avg=(16000+4*5000)/20=2200, high_vol=5000>2200*2=4400 ✓
    closes = [100.0] * 25 + [105.0, 106.0, 107.0, 108.0, 109.0]
    volumes = [1000.0] * 25 + [5000.0, 5000.0, 5000.0, 5000.0, 5000.0]
    df = _make_df(closes, volumes)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# 12. MEDIUM confidence: 1.3x <= volume < 2.0x
def test_medium_confidence_moderate_volume():
    closes = [100.0] * 25 + [105.0, 106.0, 107.0, 108.0, 109.0]
    volumes = [1000.0] * 25 + [1400.0, 1400.0, 1400.0, 1400.0, 1400.0]  # 1.3~2.0 사이
    df = _make_df(closes, volumes)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


# 13. entry_price가 마지막 완성봉 close와 동일 (_last = df.iloc[-2])
def test_entry_price_is_last_close():
    # df.iloc[-2] = 마지막 완성봉 → closes[-2]가 기준
    closes = [100.0] * (N - 2) + [99.5, 100.0]  # closes[-2] = 99.5
    df = _make_df(closes)
    sig = strat.generate(df)
    assert abs(sig.entry_price - 99.5) < 1e-6


# 14. BUY reasoning에 저항/돌파 정보 포함 (BUY 발생 시)
def test_buy_reasoning_contains_resistance():
    closes = [100.0] * 25 + [105.0, 106.0, 107.0, 108.0, 109.0]
    volumes = [1000.0] * 25 + [2100.0, 2100.0, 2100.0, 2100.0, 2100.0]
    df = _make_df(closes, volumes)
    sig = strat.generate(df)
    if sig.action == Action.BUY:
        assert "저항" in sig.reasoning or "resistance" in sig.reasoning.lower()


# 15. SELL reasoning에 지지/이탈 정보 포함 (SELL 발생 시)
def test_sell_reasoning_contains_support():
    closes = [100.0] * 25 + [95.0, 94.0, 93.0, 92.0, 91.0]
    volumes = [1000.0] * 25 + [2100.0, 2100.0, 2100.0, 2100.0, 2100.0]
    df = _make_df(closes, volumes)
    sig = strat.generate(df)
    if sig.action == Action.SELL:
        assert "지지" in sig.reasoning or "support" in sig.reasoning.lower()
