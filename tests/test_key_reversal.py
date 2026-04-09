"""
KeyReversalStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import pandas as pd
import pytest

from src.strategy.key_reversal import KeyReversalStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_base_df(n: int = 40, base_price: float = 100.0, base_vol: float = 100.0) -> pd.DataFrame:
    """기본 평탄한 DataFrame."""
    return pd.DataFrame({
        "open":   [base_price] * n,
        "close":  [base_price] * n,
        "high":   [base_price + 1.0] * n,
        "low":    [base_price - 1.0] * n,
        "volume": [base_vol] * n,
    })


def _make_bullish_df(
    n: int = 40,
    base_price: float = 100.0,
    avg_vol: float = 100.0,
    vol_mult: float = 2.0,
    yearly_low_break: bool = False,
) -> pd.DataFrame:
    """Bullish Key Reversal 유도: new 20봉 저점 + close > prev_close + 거래량 확인."""
    prices = [base_price] * n
    volumes = [avg_vol] * n
    highs = [p + 1.0 for p in prices]
    lows = [p - 1.0 for p in prices]
    opens = list(prices)

    sig_idx = n - 2
    prev_idx = n - 3

    # prev_close
    prices[prev_idx] = base_price
    # 신호봉: low < 20봉 저점, close > prev_close
    new_low = base_price - 3.0  # 이전 20봉 저점(base-1)보다 낮음
    lows[sig_idx] = new_low
    opens[sig_idx] = new_low + 0.5
    prices[sig_idx] = base_price + 1.0  # close > prev_close
    highs[sig_idx] = prices[sig_idx] + 0.5
    volumes[sig_idx] = avg_vol * vol_mult

    if yearly_low_break:
        # 52주 최저보다도 낮게
        lows[sig_idx] = base_price - 50.0
        opens[sig_idx] = lows[sig_idx] + 0.5
        prices[sig_idx] = base_price + 1.0

    df = pd.DataFrame({
        "open": opens, "close": prices,
        "high": highs, "low": lows, "volume": volumes,
    })
    return df


def _make_bearish_df(
    n: int = 40,
    base_price: float = 100.0,
    avg_vol: float = 100.0,
    vol_mult: float = 2.0,
    yearly_high_break: bool = False,
) -> pd.DataFrame:
    """Bearish Key Reversal 유도: new 20봉 고점 + close < prev_close + 거래량 확인."""
    prices = [base_price] * n
    volumes = [avg_vol] * n
    highs = [p + 1.0 for p in prices]
    lows = [p - 1.0 for p in prices]
    opens = list(prices)

    sig_idx = n - 2
    prev_idx = n - 3

    prices[prev_idx] = base_price
    new_high = base_price + 3.0  # 이전 20봉 고점(base+1)보다 높음
    highs[sig_idx] = new_high
    opens[sig_idx] = new_high - 0.5
    prices[sig_idx] = base_price - 1.0  # close < prev_close
    lows[sig_idx] = prices[sig_idx] - 0.5
    volumes[sig_idx] = avg_vol * vol_mult

    if yearly_high_break:
        highs[sig_idx] = base_price + 50.0
        opens[sig_idx] = highs[sig_idx] - 0.5
        prices[sig_idx] = base_price - 1.0

    df = pd.DataFrame({
        "open": opens, "close": prices,
        "high": highs, "low": lows, "volume": volumes,
    })
    return df


class TestKeyReversalStrategy:

    def setup_method(self):
        self.strategy = KeyReversalStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "key_reversal"

    # 2. 데이터 부족 → HOLD
    def test_insufficient_data(self):
        df = _make_base_df(n=20)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 3. Bullish Key Reversal → BUY
    def test_bullish_key_reversal_buy(self):
        df = _make_bullish_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "key_reversal"

    # 4. BUY entry_price = signal close
    def test_buy_entry_price(self):
        df = _make_bullish_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.entry_price == float(df.iloc[-2]["close"])

    # 5. Bearish Key Reversal → SELL
    def test_bearish_key_reversal_sell(self):
        df = _make_bearish_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "key_reversal"

    # 6. SELL entry_price = signal close
    def test_sell_entry_price(self):
        df = _make_bearish_df()
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.entry_price == float(df.iloc[-2]["close"])

    # 7. BUY HIGH confidence: 52주 저점 돌파
    def test_buy_high_confidence_yearly_low(self):
        df = _make_bullish_df(yearly_low_break=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 8. SELL HIGH confidence: 52주 고점 돌파
    def test_sell_high_confidence_yearly_high(self):
        df = _make_bearish_df(yearly_high_break=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 9. BUY MEDIUM confidence: 52주 저점 아님 (이전 봉에 더 낮은 저점 존재)
    def test_buy_medium_confidence(self):
        df = _make_bullish_df(yearly_low_break=False)
        sig_idx = len(df) - 2
        # 이전 봉 중 하나에 신호봉 low보다 낮은 값 삽입 → 52주 저점 아님
        signal_low = float(df.iloc[sig_idx]["low"])
        df.at[0, "low"] = signal_low - 10.0  # 더 낮은 역사적 저점
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 10. HOLD: 거래량 부족 (vol_mult < 1.5)
    def test_hold_insufficient_volume(self):
        df = _make_bullish_df(vol_mult=1.2)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. HOLD: new 20봉 저점 없음 (양봉이지만 저점 신기록 아님)
    def test_hold_no_new_low(self):
        df = _make_base_df(n=40)
        # 신호봉 close > prev_close, vol OK 이지만 low는 평범
        df.at[38, "close"] = 101.0  # close > prev(100)
        df.at[38, "volume"] = 200.0  # > avg*1.5
        # low[-2] = 99.0 이지만 이전 봉들도 모두 99.0 → 신 저점 아님
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 12. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_bullish_df()
        sig = self.strategy.generate(df)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)

    # 13. HOLD entry_price = _last close
    def test_hold_entry_price(self):
        df = _make_base_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.entry_price == float(df.iloc[-2]["close"])

    # 14. HOLD reasoning 비어있지 않음
    def test_hold_reasoning_nonempty(self):
        df = _make_base_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 15. Bearish: close >= prev_close이면 HOLD (반전 없음)
    def test_bearish_hold_no_reversal(self):
        """고점은 신기록이지만 close >= prev_close → Bearish Key Reversal 아님."""
        n = 40
        base_price = 100.0
        avg_vol = 100.0
        prices = [base_price] * n
        volumes = [avg_vol] * n
        highs = [p + 1.0 for p in prices]
        lows = [p - 1.0 for p in prices]
        opens = list(prices)

        sig_idx = n - 2
        # 신호봉: 20봉 고점 신기록
        highs[sig_idx] = base_price + 5.0
        opens[sig_idx] = base_price + 4.0
        # close > prev_close → Bearish 조건 미충족
        prices[sig_idx] = base_price + 2.0
        lows[sig_idx] = base_price - 0.5
        volumes[sig_idx] = avg_vol * 2.0

        # 신호봉 low가 이전 20봉 최저보다 낮지 않도록 유지 → Bullish 조건도 미충족
        # (lows are all base_price - 1.0, signal low = base_price - 0.5 > min)

        df = pd.DataFrame({
            "open": opens, "close": prices,
            "high": highs, "low": lows, "volume": volumes,
        })
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
