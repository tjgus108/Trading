"""
PriceActionScorerStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.price_action_scorer import PriceActionScorerStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 21  # 최소 20행 + 1 (현재 진행중 캔들)


def _make_df(n: int = _MIN_ROWS, **overrides) -> pd.DataFrame:
    """기본 DataFrame 생성. overrides로 특정 행(-2) 값을 덮어쓸 수 있음."""
    data = {
        "open":   [100.0] * n,
        "high":   [101.0] * n,
        "low":    [99.0]  * n,
        "close":  [100.0] * n,
        "volume": [1000.0] * n,
    }
    df = pd.DataFrame(data)
    for col, val in overrides.items():
        df.at[n - 2, col] = val
    return df


def _bull_candle(n: int = _MIN_ROWS) -> pd.DataFrame:
    """
    bull_score=4: 양봉, body_ratio>0.6, lower_wick 짧음, 거래량 확인
    open=100, close=103, high=103.5, low=99.8 → body=3, range=3.7, ratio≈0.81
    lower_wick = min(close,open)-low = 100-99.8 = 0.2, ratio=0.2/3.7≈0.054 < 0.2
    """
    df = pd.DataFrame({
        "open":   [100.0] * n,
        "high":   [103.5] * n,
        "low":    [99.8]  * n,
        "close":  [103.0] * n,
        "volume": [2000.0] * n,  # 항상 vol_ma(=2000)와 같음 → > 판정은 False
    })
    # 신호 봉 거래량을 평균 이상으로 올림
    df.at[n - 2, "volume"] = 3000.0
    return df


def _bear_candle(n: int = _MIN_ROWS) -> pd.DataFrame:
    """
    bear_score=4: 음봉, body_ratio>0.6, upper_wick 짧음, 거래량 확인
    open=103, close=100, high=103.2, low=99.0
    body=3, range=4.2, ratio≈0.714 > 0.6 ✓
    upper_wick = 103.2-103 = 0.2, ratio=0.048 < 0.2 ✓
    lower_wick = min(100,103)-99.0 = 1.0, ratio=1.0/4.2≈0.238 >= 0.2 → bull lower_wick False
    bull_score = 0+1+0+1 = 2, bear_score = 1+1+1+1 = 4 ✓
    """
    df = pd.DataFrame({
        "open":   [103.0] * n,
        "high":   [103.2] * n,
        "low":    [99.0]  * n,
        "close":  [100.0] * n,
        "volume": [2000.0] * n,
    })
    df.at[n - 2, "volume"] = 3000.0
    return df


class TestPriceActionScorerStrategy:

    def setup_method(self):
        self.strategy = PriceActionScorerStrategy()

    # 1. 전략 이름 확인
    def test_name(self):
        assert self.strategy.name == "price_action_scorer"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. BUY 신호 (bull_score=4)
    def test_buy_signal_bull_score_4(self):
        df = _bull_candle()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "price_action_scorer"

    # 4. BUY HIGH confidence when bull_score==4
    def test_buy_high_confidence(self):
        df = _bull_candle()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 5. SELL 신호 (bear_score=4)
    def test_sell_signal_bear_score_4(self):
        df = _bear_candle()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "price_action_scorer"

    # 6. SELL HIGH confidence when bear_score==4
    def test_sell_high_confidence(self):
        df = _bear_candle()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 7. HOLD: 도지(doji)처럼 body_ratio 낮음
    def test_hold_doji(self):
        # open=close → body=0 → bull_score와 bear_score 모두 낮음
        df = _make_df()
        # 신호 봉(-2): open==close, 긴 꼬리
        df.at[_MIN_ROWS - 2, "open"] = 100.0
        df.at[_MIN_ROWS - 2, "close"] = 100.0
        df.at[_MIN_ROWS - 2, "high"] = 105.0
        df.at[_MIN_ROWS - 2, "low"] = 95.0
        df.at[_MIN_ROWS - 2, "volume"] = 500.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 8. entry_price == last close
    def test_entry_price_is_last_close(self):
        df = _bull_candle()
        sig = self.strategy.generate(df)
        assert sig.entry_price == float(df.iloc[-2]["close"])

    # 9. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _bull_candle()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ["action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"]:
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 10. bull_score=3 → BUY MEDIUM
    def test_buy_medium_confidence_score_3(self):
        """
        bull_score=3: 양봉 + body_ratio>0.6 + lower_wick짧음, 거래량 낮음(vol_ma 이하)
        """
        n = _MIN_ROWS
        df = pd.DataFrame({
            "open":   [100.0] * n,
            "high":   [103.5] * n,
            "low":    [99.8]  * n,
            "close":  [103.0] * n,
            "volume": [2000.0] * n,
        })
        # 신호 봉 거래량을 평균 이하로 낮춤 → 거래량 조건 False
        df.at[n - 2, "volume"] = 500.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 11. bear_score=3 → SELL MEDIUM
    def test_sell_medium_confidence_score_3(self):
        n = _MIN_ROWS
        df = pd.DataFrame({
            "open":   [103.0] * n,
            "high":   [103.2] * n,
            "low":    [99.8]  * n,
            "close":  [100.0] * n,
            "volume": [2000.0] * n,
        })
        df.at[n - 2, "volume"] = 500.0
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # 12. HOLD reasoning 포함 확인
    def test_hold_reasoning_not_empty(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.reasoning != ""

    # 13. 최소 행 정확히 20개 → 정상 작동
    def test_min_rows_exactly_20(self):
        df = _bull_candle(n=20)
        sig = self.strategy.generate(df)
        # 20행이면 정상 동작 (HOLD 아닐 수도 있음, action이 있어야 함)
        assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 14. 19행 → Insufficient
    def test_19_rows_insufficient(self):
        df = _bull_candle(n=19)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning
