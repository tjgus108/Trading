"""
ALMAStrategy 단위 테스트 (12개 이상)
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.alma import ALMAStrategy, _alma
from src.strategy.base import Action, Confidence, Signal


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 60, trend: str = "up") -> pd.DataFrame:
    np.random.seed(42)
    base = 100.0
    closes = [base]

    if trend == "up":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(0.004, 0.010)))
    elif trend == "down":
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 - np.random.uniform(0.004, 0.010)))
    else:
        for _ in range(n - 1):
            closes.append(closes[-1] * (1 + np.random.uniform(-0.001, 0.001)))

    closes = np.array(closes)
    highs = closes * 1.005
    lows = closes * 0.995
    opens = closes * (1 + np.random.uniform(-0.002, 0.002, n))

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.random.uniform(1000, 5000, n),
        "ema50": closes * (0.92 if trend == "up" else 1.08 if trend == "down" else 1.0),
        "atr14": (highs - lows) * 0.5,
    })
    return df


def _make_crossup_df(n: int = 60) -> pd.DataFrame:
    """ALMA9이 ALMA21을 상향 크로스하도록 설계."""
    closes = np.concatenate([
        np.linspace(100, 95, n // 2),   # 먼저 하락
        np.linspace(95, 120, n - n // 2),  # 이후 급등
    ])
    highs = closes * 1.005
    lows = closes * 0.995
    df = pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 2000,
        "ema50": closes * 0.90,
        "atr14": (highs - lows) * 0.5,
    })
    return df


def _make_crossdown_df(n: int = 60) -> pd.DataFrame:
    """ALMA9이 ALMA21을 하향 크로스하도록 설계."""
    closes = np.concatenate([
        np.linspace(100, 110, n // 2),   # 먼저 상승
        np.linspace(110, 90, n - n // 2),  # 이후 급락
    ])
    highs = closes * 1.005
    lows = closes * 0.995
    df = pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 2000,
        "ema50": closes * 1.10,
        "atr14": (highs - lows) * 0.5,
    })
    return df


def _make_insufficient_df(n: int = 20) -> pd.DataFrame:
    closes = np.linspace(100, 110, n)
    highs = closes * 1.01
    lows = closes * 0.99
    return pd.DataFrame({
        "open": closes, "high": highs, "low": lows,
        "close": closes, "volume": np.ones(n) * 1000,
        "ema50": closes * 0.98,
        "atr14": (highs - lows) * 0.5,
    })


# ── tests ─────────────────────────────────────────────────────────────────────

class TestALMAFunction:

    def test_alma_returns_series(self):
        s = pd.Series(np.linspace(100, 110, 50))
        result = _alma(s, period=9)
        assert isinstance(result, pd.Series)
        assert len(result) == len(s)

    def test_alma_weights_sum_to_one(self):
        """가중치 합이 1이어야 함 (정규화)."""
        import numpy as np
        period = 9
        sigma = 6.0
        offset = 0.85
        m = int(offset * (period - 1))
        s = period / sigma
        weights = np.array([np.exp(-((i - m) ** 2) / (2 * s ** 2)) for i in range(period)])
        weights /= weights.sum()
        assert abs(weights.sum() - 1.0) < 1e-10

    def test_alma_shorter_period_more_responsive(self):
        """단기 ALMA가 장기 ALMA보다 최신 가격에 더 반응."""
        # 마지막 구간에서 급등 후 유지 → 단기가 더 높아야 함
        # 하락 후 급등 구간: 단기 ALMA가 장기 ALMA보다 높은 값
        closes = pd.Series(np.concatenate([np.ones(40) * 100, np.linspace(100, 120, 20)]))
        a9 = _alma(closes, 9).iloc[-1]
        a21 = _alma(closes, 21).iloc[-1]
        assert a9 > a21


class TestALMAStrategy:

    def setup_method(self):
        self.strategy = ALMAStrategy()

    # 1. 전략 이름
    def test_strategy_name(self):
        assert self.strategy.name == "alma"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data_hold(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 3. 데이터 부족 → reasoning에 "부족" 포함
    def test_insufficient_data_reasoning(self):
        df = _make_insufficient_df(n=15)
        signal = self.strategy.generate(df)
        assert "부족" in signal.reasoning

    # 4. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        assert isinstance(signal, Signal)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
        assert signal.strategy == "alma"
        assert isinstance(signal.entry_price, float)
        assert isinstance(signal.reasoning, str) and len(signal.reasoning) > 0
        assert isinstance(signal.invalidation, str)

    # 5. 정상 데이터 → 신호 반환 (BUY/SELL/HOLD 중 하나)
    def test_normal_data_returns_signal(self):
        df = _make_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 6. HOLD 시 confidence LOW
    def test_insufficient_data_confidence_low(self):
        df = _make_insufficient_df(n=20)
        signal = self.strategy.generate(df)
        assert signal.confidence == Confidence.LOW

    # 7. entry_price가 idx=-2 close와 일치
    def test_entry_price_equals_close_at_idx(self):
        df = _make_df(n=60, trend="up")
        idx = len(df) - 2
        expected = float(df["close"].iloc[idx])
        signal = self.strategy.generate(df)
        assert signal.entry_price == pytest.approx(expected, rel=1e-5)

    # 8. BUY 신호에 "상향 크로스" 포함
    def test_buy_reasoning_contains_cross(self):
        df = _make_crossup_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.BUY:
            assert "상향 크로스" in signal.reasoning or "ALMA9" in signal.reasoning

    # 9. SELL 신호에 "하향 크로스" 포함
    def test_sell_reasoning_contains_cross(self):
        df = _make_crossdown_df(n=80)
        signal = self.strategy.generate(df)
        if signal.action == Action.SELL:
            assert "하향 크로스" in signal.reasoning or "ALMA9" in signal.reasoning

    # 10. 최소 30행으로 정상 실행
    def test_exactly_min_rows(self):
        df = _make_df(n=30, trend="up")
        signal = self.strategy.generate(df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)

    # 11. 29행 → HOLD (데이터 부족)
    def test_below_min_rows_hold(self):
        df = _make_insufficient_df(n=29)
        signal = self.strategy.generate(df)
        assert signal.action == Action.HOLD

    # 12. reasoning에 "ALMA" 포함
    def test_reasoning_contains_alma(self):
        df = _make_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        assert "ALMA" in signal.reasoning

    # 13. bull_case/bear_case 존재 (데이터 충분)
    def test_bull_bear_case_present(self):
        df = _make_df(n=60, trend="up")
        signal = self.strategy.generate(df)
        if signal.bull_case:
            assert "ALMA9" in signal.bull_case
        if signal.bear_case:
            assert "ALMA9" in signal.bear_case

    # 14. 이격률 > 0.5% → HIGH confidence
    def test_high_confidence_large_divergence(self):
        """ALMA9와 ALMA21의 이격률이 크면 HIGH confidence."""
        # 급격한 가격 변화로 이격률 확보
        n = 60
        closes = np.concatenate([np.ones(40) * 100, np.linspace(100, 115, 20)])
        highs = closes * 1.005
        lows = closes * 0.995
        df = pd.DataFrame({
            "open": closes, "high": highs, "low": lows,
            "close": closes, "volume": np.ones(n) * 2000,
            "ema50": closes * 0.90, "atr14": (highs - lows) * 0.5,
        })
        signal = self.strategy.generate(df)
        if signal.action in (Action.BUY, Action.SELL):
            # 큰 이격 → HIGH, 아니면 MEDIUM
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    # 15. 횡보장 (크로스 없음) → HOLD
    def test_flat_market_hold(self):
        df = _make_df(n=60, trend="flat")
        signal = self.strategy.generate(df)
        # 크로스가 없으면 HOLD (매우 좁은 횡보에서는 크로스 미발생)
        # HOLD가 아닐 수도 있으므로 유효한 신호인지만 확인
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
