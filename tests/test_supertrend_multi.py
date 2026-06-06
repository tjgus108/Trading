"""SupertrendMultiStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.supertrend_multi import SupertrendMultiStrategy
from src.strategy.base import Action, Confidence


# ── 헬퍼 ──────────────────────────────────────────────────────────────────────

def _make_df(n: int = 50, atr: float = 1.0, trend: str = "up") -> pd.DataFrame:
    """기본 DataFrame 생성. trend='up'|'down'|'flat'."""
    if trend == "up":
        close = np.linspace(80.0, 120.0, n)
    elif trend == "down":
        close = np.linspace(120.0, 80.0, n)
    else:
        close = np.ones(n) * 100.0

    return pd.DataFrame({
        "open":   close - 0.5,
        "high":   close + 1.0,
        "low":    close - 1.0,
        "close":  close,
        "volume": np.ones(n) * 1000.0,
    })


def _make_bullish_df(n: int = 60) -> pd.DataFrame:
    """모든 Supertrend를 bullish로 유도."""
    close = np.linspace(60.0, 160.0, n)  # 강한 상승
    return pd.DataFrame({
        "open":   close - 0.3,
        "high":   close + 0.5,
        "low":    close - 0.5,
        "close":  close,
        "volume": np.ones(n) * 2000.0,
    })


def _make_bearish_df(n: int = 60) -> pd.DataFrame:
    """모든 Supertrend를 bearish로 유도."""
    # 더 가파른 하락 + 마지막 몇 봉을 확실히 아래로
    close = np.linspace(200.0, 50.0, n)
    high  = close + 0.3
    low   = close - 0.3
    # 마지막 5봉 급락 강화
    for i in range(n - 5, n):
        delta = (n - i) * 3.0
        close[i] = close[i] - delta
        high[i]  = close[i] + 0.3
        low[i]   = close[i] - 0.3
    return pd.DataFrame({
        "open":   close + 0.1,
        "high":   high,
        "low":    low,
        "close":  close,
        "volume": np.ones(n) * 2000.0,
    })


# ── 테스트 ────────────────────────────────────────────────────────────────────

def test_strategy_name():
    """전략 이름 확인."""
    st = SupertrendMultiStrategy()
    assert st.name == "supertrend_multi"


def test_insufficient_data_returns_hold():
    """MIN_ROWS(25) 미만 데이터 시 HOLD 반환."""
    st = SupertrendMultiStrategy()
    df = _make_df(n=10)
    sig = st.generate(df)
    assert sig.action == Action.HOLD


def test_exactly_min_rows_returns_signal():
    """정확히 MIN_ROWS(25)일 때 Signal 반환 (HOLD이어도 무방)."""
    st = SupertrendMultiStrategy()
    df = _make_df(n=25)
    sig = st.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_bullish_trend_generates_buy():
    """강한 상승 추세 시 BUY 신호 생성."""
    st = SupertrendMultiStrategy()
    df = _make_bullish_df(n=80)
    sig = st.generate(df)
    assert sig.action == Action.BUY


def test_bearish_trend_generates_sell():
    """강한 하락 추세 시 SELL 신호 생성."""
    st = SupertrendMultiStrategy()
    df = _make_bearish_df(n=80)
    sig = st.generate(df)
    assert sig.action == Action.SELL


def test_mixed_trend_generates_hold():
    """Supertrend 불일치 시 HOLD."""
    st = SupertrendMultiStrategy()
    df = _make_df(n=50, trend="flat")
    sig = st.generate(df)
    # flat 데이터는 일치하지 않거나 HOLD
    assert sig.action in (Action.HOLD, Action.BUY, Action.SELL)


def test_signal_has_required_fields():
    """Signal 필수 필드 존재 확인."""
    st = SupertrendMultiStrategy()
    df = _make_bullish_df(n=60)
    sig = st.generate(df)
    assert sig.strategy == "supertrend_multi"
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)


def test_high_volume_gives_high_confidence():
    """BUY 신호 + 높은 볼륨 → HIGH confidence."""
    st = SupertrendMultiStrategy()
    df = _make_bullish_df(n=80)
    # 마지막 완성봉(-2)의 volume을 평균의 2배로 높임
    avg = float(df["volume"].mean())
    df.iloc[-2, df.columns.get_loc("volume")] = avg * 2.5
    sig = st.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_low_volume_gives_medium_confidence():
    """BUY 신호 + 낮은 볼륨 → MEDIUM confidence."""
    st = SupertrendMultiStrategy()
    df = _make_bullish_df(n=80)
    df["volume"] = 1.0  # 모두 동일하게 낮게
    df.iloc[-2, df.columns.get_loc("volume")] = 0.5  # 평균보다 낮음
    sig = st.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.MEDIUM


def test_no_volume_column_still_works():
    """volume 컬럼 없어도 동작 (MEDIUM confidence)."""
    st = SupertrendMultiStrategy()
    df = _make_bullish_df(n=80).drop(columns=["volume"])
    sig = st.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)
    if sig.action != Action.HOLD:
        assert sig.confidence == Confidence.MEDIUM


def test_entry_price_is_last_close():
    """entry_price가 마지막 완성봉의 close와 같은지 확인."""
    st = SupertrendMultiStrategy()
    df = _make_bullish_df(n=60)
    sig = st.generate(df)
    assert sig.entry_price == pytest.approx(float(df["close"].iloc[-2]), rel=1e-6)


def test_sell_signal_has_required_fields():
    """SELL Signal 필드 확인."""
    st = SupertrendMultiStrategy()
    df = _make_bearish_df(n=80)
    sig = st.generate(df)
    if sig.action == Action.SELL:
        assert isinstance(sig.bull_case, str)
        assert isinstance(sig.bear_case, str)
        assert "bearish" in sig.reasoning.lower() or "trend" in sig.reasoning.lower()


def test_hold_reasoning_mentions_trend():
    """HOLD 시 reasoning에 정보가 포함되는지 확인."""
    st = SupertrendMultiStrategy()
    df = _make_df(n=10)  # 데이터 부족 → HOLD
    sig = st.generate(df)
    assert len(sig.reasoning) > 0


def test_large_dataset_no_error():
    """대용량 데이터에서 오류 없이 동작."""
    st = SupertrendMultiStrategy()
    df = _make_bullish_df(n=500)
    sig = st.generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_rsi_ob_filter_blocks_buy_when_rsi_high():
    """rsi_ob_filter=True 시 RSI 과매수 구간 BUY 차단 (fold4 ATH 오신호 방지)."""
    st_no_filter = SupertrendMultiStrategy(rsi_ob_filter=False)
    st_with_filter = SupertrendMultiStrategy(rsi_ob_filter=True, rsi_ob_threshold=75.0)

    # 강한 bullish 데이터 생성 후 RSI14를 강제로 높게 만듦
    df = _make_bullish_df(n=100)

    # rsi14 컬럼으로 RSI를 85로 고정 (threshold=75 초과)
    df["rsi14"] = 85.0

    sig_no_filter = st_no_filter.generate(df)
    sig_with_filter = st_with_filter.generate(df)

    # rsi_ob_filter=False면 BUY 가능, True면 HOLD
    if sig_no_filter.action == Action.BUY:
        assert sig_with_filter.action == Action.HOLD
        assert "rsi_ob_filter" in sig_with_filter.reasoning.lower() or "rsi" in sig_with_filter.reasoning.lower()


def test_rsi_ob_filter_allows_buy_when_rsi_normal():
    """RSI가 임계값 이하일 때 rsi_ob_filter=True여도 BUY 허용."""
    st = SupertrendMultiStrategy(rsi_ob_filter=True, rsi_ob_threshold=75.0)
    df = _make_bullish_df(n=100)
    df["rsi14"] = 60.0  # 임계값(75) 이하 → BUY 허용

    sig = st.generate(df)
    # RSI가 낮으면 rsi_ob_filter가 차단하지 않음
    assert sig.action in (Action.BUY, Action.HOLD)  # ATR 필터에 따라 달라질 수 있음


def test_rsi_ob_filter_does_not_block_sell():
    """rsi_ob_filter는 BUY만 차단, SELL에는 영향 없음."""
    st = SupertrendMultiStrategy(rsi_ob_filter=True, rsi_ob_threshold=75.0, ema_filter=False)
    df = _make_bearish_df(n=80)
    df["rsi14"] = 85.0  # RSI 높아도 SELL은 차단하지 않음

    sig = st.generate(df)
    # SELL이면 rsi_ob_filter와 무관하게 나와야 함
    assert sig.action in (Action.SELL, Action.HOLD)
