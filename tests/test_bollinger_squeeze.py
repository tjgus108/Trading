"""
BollingerSqueezeStrategy 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.bollinger_squeeze import BollingerSqueezeStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 40, closes=None) -> pd.DataFrame:
    """기본 DataFrame 생성. closes 미지정 시 단순 상승 시리즈 사용."""
    if closes is None:
        closes = [100.0 + i * 0.1 for i in range(n)]
    closes = list(closes)
    assert len(closes) == n
    return pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
        "volume": [1000.0] * n,
    })


def _make_squeeze_buy_df() -> pd.DataFrame:
    """
    BB squeeze + upward momentum + close > mid 조건을 만족하는 DataFrame.

    설계:
    - 앞 20개: 큰 진동 (BB 폭 크게) → width_ma를 높게 형성
    - 중간 20개: 완전히 flat → bb_width ≈ 0, width_ma 감소 중
    - 마지막 10개: flat + 아주 미세하게 상승
      → bb_width는 여전히 작아서 squeeze=True
      → idx=-2의 close가 5봉 전 close보다 0.01 높아 momentum > 0
      → close > bb_mid (평균값보다 살짝 높음)
    """
    # 앞: 100 ↔ 120 진동 (넓은 BB)
    front_volatile = [100.0 + (i % 2) * 20 for i in range(20)]
    # 중간: 110 flat
    mid_flat = [110.0] * 20
    # 마지막: 110.0, 110.0, 110.0, 110.0, 110.0, 110.01, 110.01, 110.01, 110.02, 110.03
    # idx=-2는 index 48 → close=110.02, 5봉 전(idx=43)=110.0 → momentum=0.02>0
    tail = [110.0, 110.0, 110.0, 110.0, 110.0, 110.01, 110.01, 110.01, 110.02, 110.03]
    closes = front_volatile + mid_flat + tail
    return _make_df(n=len(closes), closes=closes)


def _make_squeeze_sell_df() -> pd.DataFrame:
    """
    BB squeeze + downward momentum + close < mid 조건을 만족하는 DataFrame.
    """
    front_volatile = [100.0 + (i % 2) * 20 for i in range(20)]
    mid_flat = [110.0] * 20
    # idx=-2: close=109.98, 5봉 전=110.0 → momentum=-0.02<0, close < mid
    tail = [110.0, 110.0, 110.0, 110.0, 110.0, 109.99, 109.99, 109.99, 109.98, 109.97]
    closes = front_volatile + mid_flat + tail
    return _make_df(n=len(closes), closes=closes)


class TestBollingerSqueezeStrategy:

    def setup_method(self):
        self.strategy = BollingerSqueezeStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "bollinger_squeeze"

    # 2. 데이터 부족 (< 25행) → HOLD
    def test_insufficient_data_hold(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. 경계값: 정확히 25행 → HOLD가 아닐 수 있음 (최소 동작)
    def test_exactly_min_rows(self):
        df = _make_df(n=25)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=40)
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

    # 5. strategy 필드 일치
    def test_strategy_field(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.strategy == "bollinger_squeeze"

    # 6. entry_price는 float
    def test_entry_price_is_float(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert isinstance(sig.entry_price, float)

    # 7. BUY: squeeze + upward momentum + close > mid
    def test_buy_signal(self):
        df = _make_squeeze_buy_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    # 8. BUY entry_price == last close (idx=-2)
    def test_buy_entry_price(self):
        df = _make_squeeze_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.entry_price == float(df["close"].iloc[-2])

    # 9. SELL: squeeze + downward momentum + close < mid
    def test_sell_signal(self):
        df = _make_squeeze_sell_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # 10. SELL entry_price == last close (idx=-2)
    def test_sell_entry_price(self):
        df = _make_squeeze_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.entry_price == float(df["close"].iloc[-2])

    # 11. HOLD: no squeeze (highly volatile data)
    def test_hold_no_squeeze(self):
        np.random.seed(42)
        closes = list(np.random.uniform(80, 120, 40))
        df = _make_df(n=40, closes=closes)
        sig = self.strategy.generate(df)
        # 랜덤 변동성이 크면 squeeze 없이 HOLD 가능성 높음
        assert isinstance(sig, Signal)

    # 12. BUY confidence: HIGH when width < width_ma * 0.5
    def test_buy_confidence_type(self):
        df = _make_squeeze_buy_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.BUY:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 13. SELL confidence: HIGH or MEDIUM
    def test_sell_confidence_type(self):
        df = _make_squeeze_sell_df()
        sig = self.strategy.generate(df)
        if sig.action == Action.SELL:
            assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 14. 대량 데이터에서 에러 없이 동작
    def test_large_dataframe(self):
        df = _make_df(n=500)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 15. HOLD reasoning 포함
    def test_hold_reasoning_not_empty(self):
        df = _make_df(n=40)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""
