"""
PriceEnvelopeStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_envelope import PriceEnvelopeStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 30, close_seq=None, ema50: float = 100.0) -> pd.DataFrame:
    """
    close_seq: 전체 close 시퀀스 (None이면 균등 100.0).
    신호 봉 = index -2.
    EMA20은 close_seq 기반으로 자동 계산됨.
    """
    if close_seq is None:
        closes = [100.0] * n
    else:
        closes = list(close_seq)
        assert len(closes) == n

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c * 1.01 for c in closes],
        "low": [c * 0.99 for c in closes],
        "volume": [1000.0] * n,
        "ema50": [ema50] * n,
        "atr14": [1.0] * n,
    })
    return df


def _make_buy_df(n: int = 30, base: float = 100.0, drop: float = 0.94) -> pd.DataFrame:
    """close가 EMA20보다 충분히 낮아 BUY 신호 발생. drop=0.94 → 6% 낮아 band + dist 조건 모두 충족."""
    closes = [base] * n
    for i in range(n - 5, n):
        closes[i] = base * drop
    return _make_df(n=n, close_seq=closes)


def _make_sell_df(n: int = 30, base: float = 100.0, rise: float = 1.06) -> pd.DataFrame:
    """close가 EMA20보다 충분히 높아 SELL 신호 발생. rise=1.06 → 6% 높아 band + dist 조건 모두 충족."""
    closes = [base] * n
    for i in range(n - 5, n):
        closes[i] = base * rise
    return _make_df(n=n, close_seq=closes)


class TestPriceEnvelopeStrategy:

    def setup_method(self):
        self.strategy = PriceEnvelopeStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "price_envelope"

    # 2. 데이터 부족 (< 25행) → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. BUY 신호: close < lower envelope
    def test_buy_signal(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "price_envelope"

    # 4. SELL 신호: close > upper envelope
    def test_sell_signal(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "price_envelope"

    # 5. HOLD: close inside envelope
    def test_hold_inside_band(self):
        df = _make_df()  # close = EMA20 = 100, 이격 0%
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 6. BUY HIGH confidence: dist > 3%
    def test_buy_high_confidence(self):
        df = _make_buy_df()  # 3.5% 이격
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 7. SELL HIGH confidence: dist > 3%
    def test_sell_high_confidence(self):
        df = _make_sell_df()  # 3.5% 이격
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 8. BUY confidence is HIGH or MEDIUM (dist > 2%)
    def test_buy_confidence_set(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 9. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert hasattr(sig, "action")
        assert hasattr(sig, "confidence")
        assert hasattr(sig, "strategy")
        assert hasattr(sig, "entry_price")
        assert hasattr(sig, "reasoning")
        assert hasattr(sig, "invalidation")
        assert hasattr(sig, "bull_case")
        assert hasattr(sig, "bear_case")
        assert sig.reasoning != ""

    # 10. 반환 타입 Signal
    def test_returns_signal_type(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 11. reasoning에 dist 값 포함
    def test_reasoning_contains_dist(self):
        df = _make_buy_df()
        sig = self.strategy.generate(df)
        assert "dist=" in sig.reasoning

    # 12. entry_price = 신호봉 close
    def test_entry_price_is_signal_close(self):
        closes = [100.0] * 30
        for i in range(25, 30):
            closes[i] = 96.4
        df = _make_df(close_seq=closes)
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.entry_price == pytest.approx(96.4)

    # 13. n=25 최소 행 정상 작동
    def test_minimum_rows(self):
        df = _make_df(n=25)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 14. SELL reasoning에 upper 값 포함
    def test_sell_reasoning_contains_upper(self):
        df = _make_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert "upper" in sig.reasoning or "과매수" in sig.reasoning
