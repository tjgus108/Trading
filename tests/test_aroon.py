"""
AroonStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.aroon import AroonStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 30
_PERIOD = 25


def _make_df(n: int = _MIN_ROWS + 5, close: float = 100.0,
             high: float = 110.0, low: float = 90.0) -> pd.DataFrame:
    """균일한 OHLCV DataFrame 생성."""
    return pd.DataFrame({
        "open":   [close] * n,
        "close":  [close] * n,
        "high":   [high]  * n,
        "low":    [low]   * n,
        "volume": [1000.0] * n,
        "atr14":  [1.0]   * n,
    })


def _make_buy_df(aroon_up: float = 80.0, aroon_down: float = 20.0,
                 n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    Aroon Up >= 70 AND Aroon Down <= 30 조건을 만드는 DataFrame.
    - aroon_up=100  → idx 위치가 최근 25봉 중 최고점
    - aroon_down=0  → idx 위치가 최근 25봉 중 최저점
    aroon_up을 낮추려면 신고점을 더 오래 전에 만든다.
    """
    rows = n
    base_close = 100.0
    highs  = [base_close] * rows
    lows   = [base_close] * rows
    closes = [base_close] * rows

    idx = rows - 2  # _last() 기준

    # periods_since_high = (period-1) * (1 - aroon_up/100)
    psh = round((_PERIOD - 1) * (1 - aroon_up / 100))
    # periods_since_low  = (period-1) * (1 - aroon_down/100)
    psl = round((_PERIOD - 1) * (1 - aroon_down / 100))

    high_pos = idx - psh
    low_pos  = idx - psl

    # 해당 위치에 신고점/신저점 배치
    for i in range(rows):
        highs[i] = base_close
        lows[i]  = base_close

    if 0 <= high_pos < rows:
        highs[high_pos] = base_close + 20  # 신고점
    if 0 <= low_pos < rows:
        lows[low_pos] = base_close - 20   # 신저점

    return pd.DataFrame({
        "open":   closes[:],
        "close":  closes,
        "high":   highs,
        "low":    lows,
        "volume": [1000.0] * rows,
        "atr14":  [1.0]   * rows,
    })


def _make_sell_df(aroon_up: float = 20.0, aroon_down: float = 80.0,
                  n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """Aroon Down >= 70 AND Aroon Up <= 30 조건."""
    rows = n
    base_close = 100.0
    highs  = [base_close] * rows
    lows   = [base_close] * rows
    closes = [base_close] * rows

    idx = rows - 2

    psh = round((_PERIOD - 1) * (1 - aroon_up / 100))
    psl = round((_PERIOD - 1) * (1 - aroon_down / 100))

    high_pos = idx - psh
    low_pos  = idx - psl

    if 0 <= high_pos < rows:
        highs[high_pos] = base_close + 20
    if 0 <= low_pos < rows:
        lows[low_pos] = base_close - 20

    return pd.DataFrame({
        "open":   closes[:],
        "close":  closes,
        "high":   highs,
        "low":    lows,
        "volume": [1000.0] * rows,
        "atr14":  [1.0]   * rows,
    })


class TestAroonStrategy:

    def setup_method(self):
        self.strategy = AroonStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "aroon"

    # 2. BUY 신호 (Aroon Up>=70, Down<=30)
    def test_buy_signal(self):
        df = _make_buy_df(aroon_up=100.0, aroon_down=0.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "aroon"

    # 3. SELL 신호 (Aroon Down>=70, Up<=30)
    def test_sell_signal(self):
        df = _make_sell_df(aroon_up=0.0, aroon_down=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "aroon"

    # 4. BUY HIGH confidence (AroonUp==100)
    def test_buy_high_confidence_up100(self):
        df = _make_buy_df(aroon_up=100.0, aroon_down=0.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 5. BUY MEDIUM confidence (Up<100, Down<100)
    def test_buy_medium_confidence(self):
        df = _make_buy_df(aroon_up=80.0, aroon_down=20.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 6. SELL HIGH confidence (AroonDown==100)
    def test_sell_high_confidence_down100(self):
        df = _make_sell_df(aroon_up=0.0, aroon_down=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 7. SELL MEDIUM confidence
    def test_sell_medium_confidence(self):
        df = _make_sell_df(aroon_up=20.0, aroon_down=80.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 8. 횡보 HOLD (중립 구간)
    def test_hold_sideways(self):
        # 고점/저점이 25봉 중간쯤에 위치 → Up~50, Down~50
        df = _make_buy_df(aroon_up=50.0, aroon_down=50.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=15)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 10. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_buy_df(aroon_up=100.0, aroon_down=0.0)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 11. BUY reasoning에 "Aroon" 포함
    def test_buy_reasoning_contains_aroon(self):
        df = _make_buy_df(aroon_up=100.0, aroon_down=0.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert "Aroon" in sig.reasoning

    # 12. SELL reasoning에 "Aroon" 포함
    def test_sell_reasoning_contains_aroon(self):
        df = _make_sell_df(aroon_up=0.0, aroon_down=100.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert "Aroon" in sig.reasoning

    # 13. entry_price는 현재 close
    def test_entry_price_is_close(self):
        df = _make_buy_df(aroon_up=100.0, aroon_down=0.0)
        sig = self.strategy.generate(df)
        expected_close = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected_close, rel=1e-3)
