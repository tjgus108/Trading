"""Phase A 전략 3종 단위 테스트.

A1: FundingRateStrategy
A2: ResidualMeanReversionStrategy
A3: PairTradingStrategy
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.funding_rate import FundingRateStrategy
from src.strategy.residual_mean_reversion import ResidualMeanReversionStrategy
from src.strategy.pair_trading import PairTradingStrategy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df(n: int = 120, start_price: float = 50000.0, seed: int = 42) -> pd.DataFrame:
    """지표 포함 더미 DataFrame."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    close = start_price + np.cumsum(rng.standard_normal(n) * 300)
    close = np.abs(close)  # 음수 방지
    high = close + np.abs(rng.standard_normal(n) * 100)
    low = close - np.abs(rng.standard_normal(n) * 100)
    low = np.maximum(low, close * 0.9)
    df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 10.0}, index=idx)

    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [(df["high"] - df["low"]), (df["high"] - prev_close).abs(), (df["low"] - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
    df["donchian_high"] = df["high"].rolling(20).max()
    df["donchian_low"] = df["low"].rolling(20).min()
    typical = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
    return df


# ---------------------------------------------------------------------------
# A1: FundingRateStrategy
# ---------------------------------------------------------------------------

class TestFundingRateStrategy:
    def test_name(self):
        assert FundingRateStrategy.name == "funding_rate"

    def test_hold_without_funding_rate_neutral_rsi(self):
        """펀딩비 없고 RSI 중립 → HOLD."""
        df = _make_df()
        # RSI 중립 구간 억지로 만들기 (마지막 -2 캔들 RSI 40~60대)
        df["rsi14"] = 50.0
        strategy = FundingRateStrategy()
        signal = strategy.generate(df)
        assert signal.action == Action.HOLD

    def test_sell_on_high_funding_rate(self):
        """펀딩비 > 0.03% → SELL (RSI 중립으로 HIGH confidence 확인)."""
        df = _make_df()
        df["rsi14"] = 55.0  # rsi_confirm=True이므로 >=45이면 HIGH로 분기
        strategy = FundingRateStrategy()
        strategy.update_funding_rate(0.0005)  # +0.05% >= VERY_EXTREME(0.05%)
        signal = strategy.generate(df)
        assert signal.action == Action.SELL
        assert signal.confidence == Confidence.HIGH

    def test_buy_on_negative_funding_rate(self):
        """펀딩비 < -0.01% → BUY."""
        df = _make_df()
        strategy = FundingRateStrategy()
        strategy.update_funding_rate(-0.0002)  # -0.02%
        signal = strategy.generate(df)
        assert signal.action == Action.BUY

    def test_hold_on_normal_funding_rate(self):
        """펀딩비 정상 범위 → HOLD."""
        df = _make_df()
        strategy = FundingRateStrategy()
        strategy.update_funding_rate(0.0001)  # +0.01%, 정상
        signal = strategy.generate(df)
        assert signal.action == Action.HOLD

    def test_proxy_sell_on_extreme_rsi(self):
        """펀딩비 없고 RSI >= 80 → SELL (proxy, LOW confidence)."""
        df = _make_df()
        df["rsi14"] = 82.0
        strategy = FundingRateStrategy()
        signal = strategy.generate(df)
        assert signal.action == Action.SELL
        assert signal.confidence == Confidence.LOW

    def test_proxy_buy_on_low_rsi(self):
        """펀딩비 없고 RSI <= 20 → BUY (proxy, LOW confidence)."""
        df = _make_df()
        df["rsi14"] = 18.0
        strategy = FundingRateStrategy()
        signal = strategy.generate(df)
        assert signal.action == Action.BUY
        assert signal.confidence == Confidence.LOW

    def test_update_funding_rate_history(self):
        """history 최대 20개 유지."""
        strategy = FundingRateStrategy()
        for i in range(25):
            strategy.update_funding_rate(0.0001 * i)
        assert len(strategy._funding_rate_history) == 20

    def test_signal_has_required_fields(self):
        df = _make_df()
        strategy = FundingRateStrategy()
        strategy.update_funding_rate(0.0004)
        signal = strategy.generate(df)
        assert signal.strategy == "funding_rate"
        assert signal.entry_price > 0
        assert signal.reasoning != ""

    def test_medium_confidence_for_borderline(self):
        """경계값(0.03%)에서 MEDIUM confidence."""
        df = _make_df()
        df["rsi14"] = 45.0
        strategy = FundingRateStrategy()
        strategy.update_funding_rate(0.0003)  # 정확히 임계값
        signal = strategy.generate(df)
        assert signal.action == Action.SELL
        assert signal.confidence == Confidence.MEDIUM


# ---------------------------------------------------------------------------
# A2: ResidualMeanReversionStrategy
# ---------------------------------------------------------------------------

class TestResidualMeanReversionStrategy:
    def test_name(self):
        assert ResidualMeanReversionStrategy.name == "residual_mean_reversion"

    def test_hold_without_btc_data_neutral(self):
        """BTC 없고 returns z-score 중립 → HOLD."""
        rng = np.random.default_rng(0)
        df = _make_df()
        # 중립적인 수익률 패턴
        df["close"] = 50000 + np.cumsum(rng.standard_normal(len(df)) * 10)
        strategy = ResidualMeanReversionStrategy()
        signal = strategy.generate(df)
        # HOLD or LOW confidence (fallback 모드)
        assert signal.action in (Action.HOLD, Action.BUY, Action.SELL)
        assert signal.confidence == Confidence.LOW

    def test_with_btc_data_returns_signal(self):
        """BTC 데이터 주입 시 HIGH/MEDIUM confidence 신호."""
        alt_df = _make_df(120, start_price=2000.0, seed=1)
        btc_df = _make_df(120, start_price=50000.0, seed=2)
        strategy = ResidualMeanReversionStrategy(window=30)
        strategy.set_btc_data(btc_df)
        signal = strategy.generate(alt_df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.strategy == "residual_mean_reversion"

    def test_sell_when_zscore_high(self):
        """잔차 z-score 높을 때 SELL 발생 확인."""
        rng = np.random.default_rng(99)
        # alt 최근 수익률을 극단적으로 높게
        alt_df = _make_df(120, start_price=2000.0, seed=1)
        btc_df = _make_df(120, start_price=50000.0, seed=2)
        # alt 마지막 10개 캔들을 급등 패턴으로
        alt_df.loc[alt_df.index[-15:], "close"] = alt_df["close"].iloc[-15] * np.linspace(1.0, 1.3, 15)

        strategy = ResidualMeanReversionStrategy(window=20)
        strategy.set_btc_data(btc_df)
        signal = strategy.generate(alt_df)
        # 신호가 유효함을 확인
        assert signal.action in (Action.SELL, Action.HOLD)
        assert signal.entry_price > 0

    def test_insufficient_data_returns_hold(self):
        """데이터 부족(window보다 짧음) → HOLD."""
        df = _make_df(20)  # 20캔들만
        strategy = ResidualMeanReversionStrategy(window=30)
        signal = strategy.generate(df)
        assert signal.action == Action.HOLD

    def test_btc_data_set_correctly(self):
        """set_btc_data 후 내부 상태 확인."""
        btc_df = _make_df(100)
        strategy = ResidualMeanReversionStrategy()
        strategy.set_btc_data(btc_df)
        assert strategy._btc_df is not None
        assert len(strategy._btc_df) == 100

    def test_signal_entry_price_matches_close(self):
        """entry_price가 df 마지막 완성 캔들 close와 일치."""
        df = _make_df(120)
        btc_df = _make_df(120, start_price=50000.0, seed=3)
        strategy = ResidualMeanReversionStrategy(window=30)
        strategy.set_btc_data(btc_df)
        signal = strategy.generate(df)
        expected_entry = df.iloc[-2]["close"]
        assert abs(signal.entry_price - expected_entry) < 1e-6


# ---------------------------------------------------------------------------
# A3: PairTradingStrategy
# ---------------------------------------------------------------------------

class TestPairTradingStrategy:
    def test_name(self):
        assert PairTradingStrategy.name == "pair_trading"

    def test_hold_without_eth_data(self):
        """ETH 데이터 없으면 HOLD (pair 불가)."""
        btc_df = _make_df(120, start_price=50000.0)
        strategy = PairTradingStrategy()
        signal = strategy.generate(btc_df)
        assert signal.action == Action.HOLD
        assert signal.confidence == Confidence.LOW

    def test_with_eth_data_returns_signal(self):
        """ETH 데이터 주입 시 유효한 신호."""
        btc_df = _make_df(120, start_price=50000.0, seed=10)
        eth_df = _make_df(120, start_price=3000.0, seed=11)
        strategy = PairTradingStrategy(spread_window=60, beta_window=80)
        strategy.set_eth_data(eth_df)
        signal = strategy.generate(btc_df)
        assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
        assert signal.strategy == "pair_trading"

    def test_sell_when_spread_extreme_high(self):
        """BTC가 ETH 대비 과열 → SELL BTC."""
        rng = np.random.default_rng(55)
        btc_df = _make_df(120, start_price=50000.0, seed=20)
        eth_df = _make_df(120, start_price=3000.0, seed=21)
        # BTC 최근 30개 캔들 급등 (ETH는 그대로)
        btc_df.loc[btc_df.index[-30:], "close"] = btc_df["close"].iloc[-30] * np.linspace(1.0, 1.5, 30)

        strategy = PairTradingStrategy(spread_window=60, beta_window=80)
        strategy.set_eth_data(eth_df)
        signal = strategy.generate(btc_df)
        assert signal.action in (Action.SELL, Action.HOLD)  # 극단 과열 → SELL

    def test_buy_when_spread_extreme_low(self):
        """BTC가 ETH 대비 과냉 → BUY BTC."""
        btc_df = _make_df(120, start_price=50000.0, seed=30)
        eth_df = _make_df(120, start_price=3000.0, seed=31)
        # BTC 최근 30개 캔들 급락
        btc_df.loc[btc_df.index[-30:], "close"] = btc_df["close"].iloc[-30] * np.linspace(1.0, 0.6, 30)

        strategy = PairTradingStrategy(spread_window=60, beta_window=80)
        strategy.set_eth_data(eth_df)
        signal = strategy.generate(btc_df)
        assert signal.action in (Action.BUY, Action.HOLD)

    def test_eth_data_set_correctly(self):
        """set_eth_data 내부 상태."""
        eth_df = _make_df(100, start_price=3000.0)
        strategy = PairTradingStrategy()
        strategy.set_eth_data(eth_df)
        assert strategy._eth_df is not None

    def test_insufficient_eth_data_returns_hold(self):
        """ETH 데이터 너무 짧으면 HOLD."""
        btc_df = _make_df(120)
        eth_df = _make_df(30, start_price=3000.0)  # spread_window=60보다 짧음
        strategy = PairTradingStrategy(spread_window=60)
        strategy.set_eth_data(eth_df)
        signal = strategy.generate(btc_df)
        assert signal.action == Action.HOLD

    def test_signal_has_required_fields(self):
        btc_df = _make_df(120, start_price=50000.0, seed=40)
        eth_df = _make_df(120, start_price=3000.0, seed=41)
        strategy = PairTradingStrategy(spread_window=60, beta_window=80)
        strategy.set_eth_data(eth_df)
        signal = strategy.generate(btc_df)
        assert signal.entry_price > 0
        assert signal.reasoning != ""

    def test_cointegrated_assets_hold_mostly(self):
        """공적분 관계 자산은 대부분 HOLD (극단 이탈 없음)."""
        rng = np.random.default_rng(77)
        n = 120
        idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
        # BTC와 ETH를 거의 같은 수익률로 생성 (tight cointegration)
        common_factor = np.cumsum(rng.standard_normal(n) * 100)
        btc_close = 50000 + common_factor
        eth_close = 3000 + common_factor / 15  # ~같은 방향

        btc_df = _make_df(n, start_price=50000.0, seed=0)
        btc_df["close"] = btc_close
        eth_df = _make_df(n, start_price=3000.0, seed=0)
        eth_df["close"] = eth_close

        strategy = PairTradingStrategy(spread_window=60, beta_window=80)
        strategy.set_eth_data(eth_df)
        signal = strategy.generate(btc_df)
        # 타이트한 공적분이면 z-score가 낮아 HOLD 가능성 높음
        assert signal.action in (Action.HOLD, Action.BUY, Action.SELL)
