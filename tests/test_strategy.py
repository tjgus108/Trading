"""전략 신호 생성 단위 테스트. 거래소 연결 없이 동작한다."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal, REASONING_MAX_LEN
from src.strategy.donchian_breakout import DonchianBreakoutStrategy
from src.strategy.ema_cross import EmaCrossStrategy


def _make_sideways_df(n: int = 200) -> pd.DataFrame:
    """횡보(ADX 낮음) 구간 DataFrame: 거의 일정한 가격 (방향성 없음)."""
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    # 완전히 평탄한 가격 → DM = 0 → ADX ≈ 0
    rng = np.random.default_rng(0)
    close = np.full(n, 50000.0) + rng.uniform(-1, 1, n)  # 극소 노이즈
    high = close + 1.0
    low = close - 1.0
    df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 10.0}, index=idx)
    _add_indicators(df)
    return df


def _make_trending_df(n: int = 200, direction: str = "up") -> pd.DataFrame:
    """강한 추세(ADX 높음) 구간 DataFrame: 일방향으로 꾸준히 상승/하락."""
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    step = 300 if direction == "up" else -300
    close = 50000.0 + np.arange(n) * (step / n) * n
    rng = np.random.default_rng(42)
    close = close + rng.normal(0, 10, n)
    high = close + 50
    low = close - 50
    df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 10.0}, index=idx)
    _add_indicators(df)
    return df


def _add_indicators(df: pd.DataFrame) -> None:
    """공통 지표 계산 (inplace)."""
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
    df["donchian_high"] = df["high"].rolling(20, min_periods=1).max()
    df["donchian_low"] = df["low"].rolling(20, min_periods=1).min()
    typical = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()


def _make_df(n: int = 100) -> pd.DataFrame:
    """지표가 포함된 더미 DataFrame 생성."""
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    close = 50000 + np.cumsum(np.random.randn(n) * 200)
    high = close + np.abs(np.random.randn(n) * 100)
    low = close - np.abs(np.random.randn(n) * 100)
    df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 10.0}, index=idx)
    _add_indicators(df)
    return df


def test_ema_cross_returns_signal():
    df = _make_df(100)
    strategy = EmaCrossStrategy()
    signal = strategy.generate(df)
    assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert signal.strategy == "ema_cross"
    assert signal.entry_price > 0


def test_donchian_returns_signal():
    df = _make_df(100)
    strategy = DonchianBreakoutStrategy()
    signal = strategy.generate(df)
    assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert signal.strategy == "donchian_breakout"


def test_signal_has_bull_bear_case():
    df = _make_df(100)
    signal = EmaCrossStrategy().generate(df)
    assert signal.bull_case != "" or signal.action == Action.HOLD
    assert isinstance(signal.reasoning, str)
    assert isinstance(signal.invalidation, str)


def test_signal_metadata_optional():
    """Signal.metadata는 기본 None이며, dict 할당 시 저장된다."""
    from src.strategy.base import Signal, Action, Confidence

    sig_no_meta = Signal(
        action=Action.HOLD,
        confidence=Confidence.LOW,
        strategy="test",
        entry_price=100.0,
        reasoning="r",
        invalidation="i",
    )
    assert sig_no_meta.metadata is None

    sig_with_meta = Signal(
        action=Action.BUY,
        confidence=Confidence.HIGH,
        strategy="test",
        entry_price=100.0,
        reasoning="r",
        invalidation="i",
        metadata={"rsi": 55.0, "atr_ratio": 1.2},
    )
    assert sig_with_meta.metadata["rsi"] == 55.0


def test_ema_cross_buy_on_crossover():
    """EMA20이 EMA50을 상향 돌파하는 시나리오를 직접 주입 (ATR/VWAP/ADX 필터 포함)."""
    # 추세 구간 기반 df → ADX가 충분히 높음
    df = _make_trending_df(200, direction="up")
    # 마지막 두 캔들에 크로스오버 주입
    df.iloc[-3, df.columns.get_loc("ema20")] = 49000
    df.iloc[-3, df.columns.get_loc("ema50")] = 49100  # ema20 < ema50
    df.iloc[-2, df.columns.get_loc("ema20")] = 49200
    df.iloc[-2, df.columns.get_loc("ema50")] = 49100  # ema20 > ema50
    df.iloc[-2, df.columns.get_loc("rsi14")] = 55     # 과매수 아님
    # ATR 필터: 충분한 변동성 주입
    avg_atr = df["atr14"].iloc[-21:-1].mean()
    df.iloc[-2, df.columns.get_loc("atr14")] = avg_atr * 1.0  # >= 0.8 * avg_atr
    # VWAP 필터: close > vwap (BUY 조건)
    close_val = df.iloc[-2]["close"]
    df.iloc[-2, df.columns.get_loc("vwap")] = close_val * 0.99  # close > vwap
    signal = EmaCrossStrategy().generate(df)
    assert signal.action == Action.BUY


def test_signal_reasoning_max_length():
    """reasoning이 REASONING_MAX_LEN 초과 시 ValueError를 발생시킨다."""
    with pytest.raises(ValueError, match="reasoning exceeds"):
        Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy="test",
            entry_price=100.0,
            reasoning="x" * (REASONING_MAX_LEN + 1),
            invalidation="i",
        )
    # 경계값: 정확히 REASONING_MAX_LEN 길이는 통과해야 한다
    sig = Signal(
        action=Action.HOLD,
        confidence=Confidence.LOW,
        strategy="test",
        entry_price=100.0,
        reasoning="x" * REASONING_MAX_LEN,
        invalidation="i",
    )
    assert len(sig.reasoning) == REASONING_MAX_LEN


# ── ADX 필터 테스트 ────────────────────────────────────────────────────────────

def test_ema_cross_adx_low_returns_hold():
    """ADX < 20인 횡보 구간에서 EmaCross는 항상 HOLD를 반환해야 한다."""
    df = _make_sideways_df(200)
    signal = EmaCrossStrategy().generate(df)
    assert signal.action == Action.HOLD
    assert "ADX" in signal.reasoning


def test_ema_cross_adx_high_trend_generates_signal():
    """강한 추세 구간(ADX 높음)에서 EmaCross는 BUY/SELL/HOLD 중 하나를 반환하며, ADX 필터로 막히지 않아야 한다."""
    df = _make_trending_df(200, direction="up")
    signal = EmaCrossStrategy().generate(df)
    # ADX가 높은 추세 구간이므로 ADX 횡보 필터로 막히면 안 됨
    if signal.action == Action.HOLD:
        assert "ADX 낮음" not in signal.reasoning
    assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_donchian_adx_low_returns_hold():
    """ADX < 15인 횡보 구간에서 DonchianBreakout은 항상 HOLD를 반환해야 한다."""
    df = _make_sideways_df(200)
    signal = DonchianBreakoutStrategy().generate(df)
    assert signal.action == Action.HOLD
    assert "ADX" in signal.reasoning


def test_donchian_adx_high_trend_generates_signal():
    """강한 추세 구간(ADX 높음)에서 DonchianBreakout은 ADX 필터로 막히지 않아야 한다."""
    df = _make_trending_df(200, direction="up")
    signal = DonchianBreakoutStrategy().generate(df)
    if signal.action == Action.HOLD:
        assert "ADX 낮음" not in signal.reasoning
    assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
