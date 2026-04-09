"""
SessionHighLowStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.session_high_low import SessionHighLowStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(
    n: int = 30,
    session_window: int = 20,
    session_high: float = 110.0,
    session_low: float = 90.0,
    last_close: float = 100.0,
) -> pd.DataFrame:
    """
    최근 session_window봉에 session_high/low를 포함,
    신호 봉(-2)의 close를 last_close로 설정.
    """
    closes = [100.0] * n
    highs = [100.0] * n
    lows = [100.0] * n
    opens = [100.0] * n
    volumes = [1000.0] * n

    # 세션 레인지 설정: -session_window-1 ~ -1 구간에 high/low 포함
    # _last()는 df.iloc[-2]이므로, 세션은 df.iloc[-21:-1]
    start = n - session_window - 1
    end = n - 1
    for i in range(start, end):
        highs[i] = session_high
        lows[i] = session_low

    # 신호 봉 = -2
    closes[-2] = last_close

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })
    return df


class TestSessionHighLowStrategy:

    def setup_method(self):
        self.strategy = SessionHighLowStrategy(session_window=20)

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "session_high_low"

    # 2. BUY 신호: close >= session_high * 0.995
    def test_buy_signal(self):
        # session_high=110, threshold=110*0.995=109.45, close=109.5
        df = _make_df(last_close=109.5, session_high=110.0, session_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "session_high_low"
        assert sig.entry_price == 109.5

    # 3. SELL 신호: close <= session_low * 1.005
    def test_sell_signal(self):
        # session_low=90, threshold=90*1.005=90.45, close=90.4
        df = _make_df(last_close=90.4, session_high=110.0, session_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.entry_price == 90.4

    # 4. HOLD: close 중간
    def test_hold_in_middle(self):
        df = _make_df(last_close=100.0, session_high=110.0, session_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 5. BUY HIGH confidence: close >= session_high * 0.999
    def test_buy_high_confidence(self):
        # session_high=110, 0.999*110=109.89, close=109.9
        df = _make_df(last_close=109.9, session_high=110.0, session_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 6. BUY MEDIUM confidence: session_high*0.995 <= close < session_high*0.999
    def test_buy_medium_confidence(self):
        # session_high=110, 0.995*110=109.45, 0.999*110=109.89, close=109.5
        df = _make_df(last_close=109.5, session_high=110.0, session_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 7. SELL HIGH confidence: close <= session_low * 1.001
    def test_sell_high_confidence(self):
        # session_low=90, 1.001*90=90.09, close=90.05
        df = _make_df(last_close=90.05, session_high=110.0, session_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 8. SELL MEDIUM confidence: session_low*1.001 < close <= session_low*1.005
    def test_sell_medium_confidence(self):
        # session_low=90, 1.001*90=90.09, 1.005*90=90.45, close=90.3
        df = _make_df(last_close=90.3, session_high=110.0, session_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 9. 데이터 부족 (< 25행)
    def test_insufficient_data(self):
        df = _make_df(n=20, last_close=109.5)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.confidence == Confidence.LOW

    # 10. 커스텀 session_window 파라미터
    def test_custom_session_window(self):
        strategy = SessionHighLowStrategy(session_window=10)
        # session_high=110 → threshold=109.45
        df = _make_df(n=30, session_window=10, session_high=110.0, session_low=90.0, last_close=109.5)
        sig = strategy.generate(df)
        assert sig.action == Action.BUY

    # 11. Signal 필드 완전성
    def test_signal_fields(self):
        df = _make_df(last_close=109.5)
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

    # 12. HOLD reasoning 포함
    def test_hold_reasoning(self):
        df = _make_df(last_close=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.reasoning != ""

    # 13. close가 정확히 session_high (BUY HIGH)
    def test_close_equals_session_high(self):
        df = _make_df(last_close=110.0, session_high=110.0, session_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 14. close가 정확히 session_low (SELL HIGH)
    def test_close_equals_session_low(self):
        df = _make_df(last_close=90.0, session_high=110.0, session_low=90.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH
