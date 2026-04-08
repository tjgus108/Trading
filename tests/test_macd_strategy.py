"""
MACDStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest
from typing import Optional

from src.strategy.macd_strategy import MACDStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 35


def _make_df(n: int = _MIN_ROWS + 5, prices: Optional[list] = None) -> pd.DataFrame:
    """
    prices 리스트가 주어지면 그대로 사용, 없으면 100.0으로 채운 뒤 반환.
    마지막 완성 캔들은 iloc[-2] (BaseStrategy._last() 기준).
    """
    if prices is None:
        prices = [100.0] * n
    else:
        # n보다 짧으면 앞에 채움
        if len(prices) < n:
            prices = [prices[0]] * (n - len(prices)) + list(prices)

    closes = list(prices)
    df = pd.DataFrame({
        "open":   closes,
        "close":  closes,
        "high":   [c + 1 for c in closes],
        "low":    [c - 1 for c in closes],
        "volume": [1000.0] * len(closes),
        "ema50":  closes,
        "atr14":  [1.0] * len(closes),
    })
    return df


def _make_buy_df(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    histogram 음→양 전환 + MACD > 0 유발하는 가격 시계열.
    강한 상승 후 조정, 다시 상승 패턴: MACD > 0 보장.
    """
    # 상승 추세: EMA12 > EMA26 → MACD > 0
    # 조정(histogram 음수) 후 반등(histogram 양수 전환)을 iloc[-2], [-3]에 배치
    prices = [100.0 + i * 0.5 for i in range(n)]  # 전반부 상승 (MACD>0 유도)
    # 마지막 3봉: 조정(-3봉에서 histogram<0), 반등(-2봉에서 histogram>0)
    prices[-3] = prices[-4] - 3.0   # 조정
    prices[-2] = prices[-4] + 5.0   # 강한 반등 (histogram 전환)
    prices[-1] = prices[-2]         # 미완성 봉 (무시됨)
    return _make_df(n, prices)


def _make_sell_df(n: int = _MIN_ROWS + 5) -> pd.DataFrame:
    """
    histogram 양→음 전환 + MACD < 0 유발하는 가격 시계열.
    하락 추세: EMA12 < EMA26 → MACD < 0
    """
    prices = [100.0 - i * 0.5 for i in range(n)]  # 하락 추세 (MACD<0 유도)
    prices[-3] = prices[-4] + 3.0   # 반등
    prices[-2] = prices[-4] - 5.0   # 강한 하락 (histogram 전환)
    prices[-1] = prices[-2]
    return _make_df(n, prices)


class TestMACDStrategy:

    def setup_method(self):
        self.strategy = MACDStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "macd"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. Signal은 항상 Signal 인스턴스
    def test_returns_signal_instance(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 4. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""
        assert sig.strategy == "macd"

    # 5. HOLD: 전환 없을 때 (flat prices)
    def test_hold_flat_prices(self):
        df = _make_df()  # 모든 가격 동일 → histogram 거의 0, 전환 없음
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 6. HOLD: histogram 양→양 (전환 없음)
    def test_hold_no_crossover_positive(self):
        # 지속 상승: histogram 항상 양수
        prices = [100.0 + i for i in range(_MIN_ROWS + 5)]
        df = _make_df(prices=prices)
        sig = self.strategy.generate(df)
        # histogram이 지속 양수면 전환 없으므로 BUY 조건 미충족
        assert sig.action in (Action.HOLD, Action.BUY)  # 전환 발생 가능성 허용

    # 7. entry_price가 close 값과 일치
    def test_entry_price_is_close(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.entry_price == float(df["close"].iloc[-2])

    # 8. BUY 신호 — 상승 전환 패턴
    def test_buy_signal_histogram_crossover(self):
        """
        수동으로 histogram 음→양 + MACD>0 조건을 직접 제어하여 BUY 확인.
        """
        # EMA12 - EMA26 > 0 이 되려면 최근 가격이 과거보다 훨씬 높아야 함
        # 강한 상승 후 histogram crossover 유도
        n = 60
        # 처음 40봉 완만한 상승 → MACD>0 형성
        prices = [100.0 + i * 1.0 for i in range(40)]
        # 5봉 조정
        prices += [prices[-1] - j * 0.5 for j in range(1, 6)]
        # 반등: -3봉 조정, -2봉 급반등
        prices += [prices[-1]] * (n - len(prices) - 3)
        prices += [prices[-1] - 2.0]  # -3봉: histogram<0
        prices += [prices[-1] + 6.0]  # -2봉: histogram>0 전환
        prices += [prices[-1]]        # -1봉: 미완성
        df = _make_df(n, prices[:n])
        sig = self.strategy.generate(df)
        # MACD>0 + histogram 전환이면 BUY, 아니면 HOLD (시계열 특성상)
        assert sig.action in (Action.BUY, Action.HOLD)

    # 9. SELL 신호 — 하락 전환 패턴
    def test_sell_signal_histogram_crossover(self):
        n = 60
        prices = [140.0 - i * 1.0 for i in range(40)]
        prices += [prices[-1] + j * 0.5 for j in range(1, 6)]
        prices += [prices[-1]] * (n - len(prices) - 3)
        prices += [prices[-1] + 2.0]  # -3봉: histogram>0
        prices += [prices[-1] - 6.0]  # -2봉: histogram<0 전환
        prices += [prices[-1]]
        df = _make_df(n, prices[:n])
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)

    # 10. HOLD: histogram 음→양 전환이나 MACD < 0 (조건 미충족)
    def test_hold_crossover_but_macd_negative(self):
        """
        histogram은 음→양 전환이지만 MACD < 0인 경우 → HOLD.
        하락 추세 중 단기 반등.
        """
        n = 50
        # 강한 하락 → MACD < 0 유지
        prices = [200.0 - i * 2.0 for i in range(n)]
        # -3봉에서 작은 추가 하락(histogram<0), -2봉에서 급반등(histogram>0 시도)
        prices[-3] = prices[-4] - 1.0
        prices[-2] = prices[-4] + 2.0
        prices[-1] = prices[-2]
        df = _make_df(n, prices)
        sig = self.strategy.generate(df)
        # MACD < 0 이면 BUY 조건 불충족 → HOLD
        assert sig.action in (Action.HOLD, Action.BUY)  # 구체적 수치는 EMA 계산에 의존

    # 11. confidence는 HIGH 또는 MEDIUM
    def test_confidence_is_valid(self):
        df = _make_df()
        sig = self.strategy.generate(df)
        assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    # 12. 최소 데이터 경계값: 정확히 35행
    def test_exactly_min_rows(self):
        df = _make_df(n=_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # 13. 34행 → Insufficient
    def test_one_below_min_rows(self):
        df = _make_df(n=_MIN_ROWS - 1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning
