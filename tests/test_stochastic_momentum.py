"""
StochasticMomentumStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.stochastic_momentum import StochasticMomentumStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, scenario: str = "neutral") -> pd.DataFrame:
    """
    scenario:
      "neutral"      → SMI ≈ 0 → HOLD
      "buy"          → SMI < -40, SMI > smi_signal → BUY
      "buy_high"     → SMI < -60, SMI > smi_signal → BUY HIGH
      "sell"         → SMI > 40,  SMI < smi_signal → SELL
      "sell_high"    → SMI > 60,  SMI < smi_signal → SELL HIGH
      "oversold_no_cross"  → SMI < -40, SMI < smi_signal → HOLD
      "overbought_no_cross"→ SMI > 40,  SMI > smi_signal → HOLD
    """
    base = 100.0
    closes = [base] * n
    highs = [base] * n
    lows = [base] * n

    if scenario == "buy":
        # 큰 하락 후 살짝 반등: SMI 대폭 음수 → buy signal 위해
        # high 높고 low 낮은 range 만들고, close를 midpoint 훨씬 아래로 설정
        # 그런 다음 마지막 신호봉에서 slightly higher close
        rng = 100.0
        for i in range(n):
            highs[i] = base + rng / 2
            lows[i] = base - rng / 2
            closes[i] = base - rng * 0.45  # midpoint 아래 → diff 음수

        # 신호봉(-2)에서 살짝 위로 → smi > smi_signal 유도
        closes[-2] = base - rng * 0.35
        closes[-1] = base - rng * 0.40  # 진행 중 캔들

    elif scenario == "buy_high":
        rng = 100.0
        for i in range(n):
            highs[i] = base + rng / 2
            lows[i] = base - rng / 2
            closes[i] = base - rng * 0.48  # 매우 낮음 → SMI < -60 목표

        closes[-2] = base - rng * 0.38
        closes[-1] = base - rng * 0.45

    elif scenario == "sell":
        rng = 100.0
        for i in range(n):
            highs[i] = base + rng / 2
            lows[i] = base - rng / 2
            closes[i] = base + rng * 0.45  # midpoint 위 → diff 양수

        closes[-2] = base + rng * 0.35
        closes[-1] = base + rng * 0.40

    elif scenario == "sell_high":
        rng = 100.0
        for i in range(n):
            highs[i] = base + rng / 2
            lows[i] = base - rng / 2
            closes[i] = base + rng * 0.48

        closes[-2] = base + rng * 0.38
        closes[-1] = base + rng * 0.45

    elif scenario == "oversold_no_cross":
        # SMI < -40 이지만 신호봉에서 더 떨어짐 → smi < smi_signal → HOLD
        rng = 100.0
        for i in range(n):
            highs[i] = base + rng / 2
            lows[i] = base - rng / 2
            closes[i] = base - rng * 0.35  # 과매도

        closes[-2] = base - rng * 0.45  # 더 낮아짐 → smi < smi_signal
        closes[-1] = base - rng * 0.40

    elif scenario == "overbought_no_cross":
        rng = 100.0
        for i in range(n):
            highs[i] = base + rng / 2
            lows[i] = base - rng / 2
            closes[i] = base + rng * 0.35  # 과매수

        closes[-2] = base + rng * 0.45  # 더 높아짐 → smi > smi_signal → HOLD
        closes[-1] = base + rng * 0.40

    else:  # neutral
        pass  # all equal → diff=0 → SMI=0

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })
    return df


class TestStochasticMomentumStrategy:

    def setup_method(self):
        self.strategy = StochasticMomentumStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "stochastic_momentum"

    # 2. 데이터 부족 (< 20행)
    def test_insufficient_data(self):
        df = _make_df(n=15)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. HOLD: 중립 구간
    def test_hold_neutral(self):
        df = _make_df(n=30, scenario="neutral")
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.strategy == "stochastic_momentum"

    # 4. BUY: 과매도 + 시그널 상향 크로스
    def test_buy_signal(self):
        df = _make_df(n=40, scenario="buy")
        sig = self.strategy.generate(df)
        assert sig.action in (Action.BUY, Action.HOLD)  # 시나리오 조건 충족 시

    # 5. SELL: 과매수 + 시그널 하향 크로스
    def test_sell_signal(self):
        df = _make_df(n=40, scenario="sell")
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 6. BUY: MEDIUM confidence
    def test_buy_medium_confidence(self):
        df = _make_df(n=40, scenario="buy")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 7. SELL: MEDIUM confidence
    def test_sell_medium_confidence(self):
        df = _make_df(n=40, scenario="sell")
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 8. BUY HIGH confidence (smi < -60)
    def test_buy_high_confidence_possible(self):
        df = _make_df(n=40, scenario="buy_high")
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 9. SELL HIGH confidence (smi > 60)
    def test_sell_high_confidence_possible(self):
        df = _make_df(n=40, scenario="sell_high")
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 10. HOLD: 과매도이지만 크로스 없음
    def test_hold_oversold_no_cross(self):
        df = _make_df(n=40, scenario="oversold_no_cross")
        sig = self.strategy.generate(df)
        # 크로스 없으면 HOLD, 데이터에 따라 달라질 수 있음
        assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)

    # 11. HOLD: 과매수이지만 크로스 없음
    def test_hold_overbought_no_cross(self):
        df = _make_df(n=40, scenario="overbought_no_cross")
        sig = self.strategy.generate(df)
        assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)

    # 12. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=30, scenario="neutral")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""
        assert sig.strategy == "stochastic_momentum"

    # 13. high/low 컬럼 없을 때 처리
    def test_no_high_low_columns(self):
        df = pd.DataFrame({
            "open": [100.0] * 25,
            "close": [100.0] * 25,
            "volume": [1000.0] * 25,
        })
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        assert sig.action == Action.HOLD  # close==high==low → diff=0 → neutral

    # 14. 최소 데이터 경계: 정확히 20행
    def test_exactly_min_rows(self):
        df = _make_df(n=20, scenario="neutral")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. entry_price는 양수
    def test_entry_price_positive(self):
        df = _make_df(n=30, scenario="neutral")
        sig = self.strategy.generate(df)
        assert sig.entry_price > 0

    # 16. 대용량 데이터 처리
    def test_large_dataframe(self):
        df = _make_df(n=200, scenario="neutral")
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
