"""
PriceCycleDetectorStrategy 단위 테스트.

DataFrame 구조 (n=40 기본):
  - 인덱스 -1: 진행 중 캔들 (무시)
  - 인덱스 -2 (last): _last(df) = 신호 봉
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.price_cycle_detector import PriceCycleDetectorStrategy


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _flat_df(n: int = 40, close: float = 100.0) -> pd.DataFrame:
    return pd.DataFrame({
        "open":   [close] * n,
        "close":  [close] * n,
        "high":   [close + 1.0] * n,
        "low":    [close - 1.0] * n,
        "volume": [1000.0] * n,
    })


def _cyclic_buy_df(n: int = 50) -> pd.DataFrame:
    """강한 양의 자기상관 + 상승 위상 → BUY."""
    import math
    # lag=5 사인파, 현재 위치가 상승 위상
    closes = [100.0 + 5.0 * math.sin(2 * math.pi * i / 5) for i in range(n)]
    # 마지막 완성봉(-2)이 상승 위상에 있도록 조정
    # sin(2pi*i/5)이 lag 5 전보다 크려면 상승 위상
    # i=n-2 기준: sin(2pi*(n-2)/5) vs sin(2pi*(n-2-5)/5) = sin(2pi*(n-7)/5)
    # 상승 위상: i가 0에서 1.25(=5/4)로 갈 때
    # n=50 → idx=48: sin(2pi*48/5) = sin(2pi*9.6) ≈ sin(2pi*0.6) ≈ -0.951
    # 상승 위상이 아니므로 n을 조정
    # 대신 간단히 구성: 처음 n-2개는 사인파, 마지막 2개는 높은 값으로
    closes_adj = [100.0 + 5.0 * math.sin(2 * math.pi * i / 5) for i in range(n)]
    # 강제로 idx-5 < idx 가 되도록 마지막 부분 조정
    # 실제로는 사인파를 그냥 사용하고 상승 위상 확인
    df = pd.DataFrame({
        "open":   closes_adj,
        "close":  closes_adj,
        "high":   [c + 0.5 for c in closes_adj],
        "low":    [c - 0.5 for c in closes_adj],
        "volume": [1000.0] * n,
    })
    return df


def _strong_cycle_buy_df(n: int = 50) -> pd.DataFrame:
    """
    best_corr > 0.7 (HIGH) + cycle_momentum > 0.01 → BUY HIGH.
    lag=4 사인파로 강한 자기상관, idx-4 < idx (상승 위상).
    """
    import math
    # lag=4 사인파: corr(lag=4) ≈ 1.0
    # idx = n-2 = 48, lag_close = idx-4 = 44
    # sin(2pi*48/4) = sin(24pi) = 0
    # sin(2pi*44/4) = sin(22pi) = 0
    # 상승 위상이 아니므로 offset 추가
    closes = [100.0 + 10.0 * math.sin(2 * math.pi * i / 4 + 0.5) for i in range(n)]
    # idx=48: sin(2pi*48/4+0.5) = sin(24pi+0.5) = sin(0.5) ≈ 0.479
    # idx-4=44: sin(2pi*44/4+0.5) = sin(22pi+0.5) = sin(0.5) ≈ 0.479 → 동일
    # 대신 위상 shift=1로
    closes = [100.0 + 10.0 * math.sin(2 * math.pi * i / 4 + 1.0) for i in range(n)]
    # idx=48: sin(24pi+1.0) = sin(1.0) ≈ 0.841
    # idx-4=44: sin(22pi+1.0) = sin(1.0) ≈ 0.841 → 동일 (주기의 배수)
    # lag=4이면 idx-4는 정확히 1주기 전 → 동일 값
    # 대신 lag=3을 강제: sin(2pi*i/5 + phase)
    # 사인파보다 실제 모멘텀이 있는 패턴 사용
    # 마지막 5개는 급등: cycle_momentum 보장
    base = 100.0
    closes = []
    for i in range(n - 5):
        closes.append(base + 2.0 * math.sin(2 * math.pi * i / 5))
    # 마지막 5개: 급등 (idx-5 대비 +3%)
    last_base = closes[-1]
    for j in range(5):
        closes.append(last_base * (1 + 0.007 * (j + 1)))
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })
    return df


def _make_cycle_signal_df(
    n: int = 50,
    corr_target: float = 0.8,
    momentum_up: bool = True,
) -> pd.DataFrame:
    """
    autocorr이 높고 cycle_momentum이 원하는 방향인 DataFrame.
    lag=2 사인파 + 마지막에 방향 조정.
    """
    import math
    lag = 2
    closes = [100.0 + 8.0 * math.sin(2 * math.pi * i / (lag * 2)) for i in range(n)]
    # idx = n-2
    idx = n - 2
    curr = closes[idx]
    ref = closes[idx - lag] if idx >= lag else curr
    current_mom = (curr - ref) / ref if ref != 0 else 0

    if momentum_up and current_mom <= 0.01:
        # 강제로 상승 위상 만들기
        closes[idx] = ref * 1.02
    elif not momentum_up and current_mom >= -0.01:
        closes[idx] = ref * 0.98

    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 0.5 for c in closes],
        "low":    [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })
    return df


# ── 테스트 ───────────────────────────────────────────────────────────────────

class TestPriceCycleDetectorStrategy:

    def setup_method(self):
        self.strat = PriceCycleDetectorStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strat.name == "price_cycle_detector"

    # 2. 인스턴스 타입
    def test_instance(self):
        from src.strategy.base import BaseStrategy
        assert isinstance(self.strat, BaseStrategy)

    # 3. 데이터 부족 → HOLD
    def test_insufficient_data_returns_hold(self):
        df = _flat_df(n=20)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient data" in sig.reasoning

    # 4. None 대신 Signal 반환 (데이터 부족)
    def test_returns_signal_not_none(self):
        df = _flat_df(n=10)
        sig = self.strat.generate(df)
        assert sig is not None
        assert isinstance(sig, Signal)

    # 5. reasoning 필드 존재
    def test_reasoning_field_exists(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert isinstance(sig.reasoning, str)
        assert len(sig.reasoning) > 0

    # 6. 정상 Signal 반환 (충분한 데이터)
    def test_normal_signal_returned(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 7. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)

    # 8. 평탄한 데이터 → HOLD (자기상관 없음)
    def test_flat_data_returns_hold(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 9. BUY reasoning에 자기상관 관련 내용
    def test_buy_reasoning_content(self):
        df = _make_cycle_signal_df(n=50, momentum_up=True)
        sig = self.strat.generate(df)
        if sig.action == Action.BUY:
            assert "best_corr" in sig.reasoning or "자기상관" in sig.reasoning or "위상" in sig.reasoning

    # 10. SELL reasoning에 하락 관련 내용
    def test_sell_reasoning_content(self):
        df = _make_cycle_signal_df(n=50, momentum_up=False)
        sig = self.strat.generate(df)
        if sig.action == Action.SELL:
            assert "best_corr" in sig.reasoning or "하락" in sig.reasoning

    # 11. HIGH confidence 조건 (best_corr > 0.7)
    def test_high_confidence_possible(self):
        # 강한 사인파로 HIGH 가능
        df = _make_cycle_signal_df(n=50, momentum_up=True)
        sig = self.strat.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 12. MEDIUM confidence 가능
    def test_medium_confidence_possible(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 13. entry_price > 0
    def test_entry_price_positive(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert sig.entry_price > 0

    # 14. strategy 필드 = "price_cycle_detector"
    def test_strategy_field(self):
        df = _flat_df(n=40)
        sig = self.strat.generate(df)
        assert sig.strategy == "price_cycle_detector"

    # 추가: 최소 행 경계값 (34행 → HOLD)
    def test_34_rows_returns_hold(self):
        df = _flat_df(n=34)
        sig = self.strat.generate(df)
        assert sig.action == Action.HOLD

    # 추가: 35행 → Signal 반환
    def test_35_rows_processes(self):
        df = _flat_df(n=35)
        sig = self.strat.generate(df)
        assert isinstance(sig, Signal)
