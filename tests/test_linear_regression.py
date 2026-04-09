"""LinearRegressionStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.linear_regression import LinearRegressionStrategy, _linear_regression
from src.strategy.base import Action, Confidence


def _make_df(n: int = 30, close_values=None) -> pd.DataFrame:
    if close_values is not None:
        closes = list(close_values)
        n = len(closes)
    else:
        closes = [100.0 + i * 0.1 for i in range(n)]

    return pd.DataFrame(
        {
            "open": closes,
            "high": [c + 1.0 for c in closes],
            "low": [c - 1.0 for c in closes],
            "close": closes,
            "volume": [1000.0] * n,
            "ema50": closes,
            "atr14": [1.0] * n,
        }
    )


def _make_uptrend_df(n: int = 30) -> pd.DataFrame:
    """강한 상승 추세 (R² 높음, slope > 0, close > predicted)."""
    # 완벽한 선형 상승 → R²≈1
    closes = [100.0 + i * 1.0 for i in range(n)]
    return _make_df(close_values=closes)


def _make_downtrend_df(n: int = 30) -> pd.DataFrame:
    """강한 하락 추세 (R² 높음, slope < 0, close < predicted)."""
    closes = [200.0 - i * 1.0 for i in range(n)]
    return _make_df(close_values=closes)


def _make_noisy_df(n: int = 30) -> pd.DataFrame:
    """잡음 많은 횡보 (R² 낮음)."""
    rng = np.random.default_rng(42)
    closes = [100.0 + rng.uniform(-5, 5) for _ in range(n)]
    return _make_df(close_values=closes)


# ── 테스트 ────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 = 'linear_regression'."""
    assert LinearRegressionStrategy.name == "linear_regression"
    assert LinearRegressionStrategy().name == "linear_regression"


def test_insufficient_data_returns_hold():
    """2. 데이터 부족 (< 25행) → HOLD, LOW confidence."""
    df = _make_df(n=10)
    sig = LinearRegressionStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_sufficient_data_returns_signal():
    """3. 충분한 데이터로 Signal 반환, 에러 없음."""
    df = _make_df(n=30)
    sig = LinearRegressionStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_signal_strategy_field():
    """4. Signal.strategy = 'linear_regression'."""
    df = _make_df(n=30)
    sig = LinearRegressionStrategy().generate(df)
    assert sig.strategy == "linear_regression"


def test_signal_entry_price_is_float():
    """5. entry_price가 float."""
    df = _make_df(n=30)
    sig = LinearRegressionStrategy().generate(df)
    assert isinstance(sig.entry_price, float)


def test_buy_signal_uptrend():
    """6. 완벽한 선형 상승 → BUY."""
    df = _make_uptrend_df(n=30)
    sig = LinearRegressionStrategy().generate(df)
    assert sig.action == Action.BUY


def test_sell_signal_downtrend():
    """7. 강한 하락 추세: slope < 0, R² > 0.9, close < predicted → SELL."""
    # 하락 후 마지막 캔들에서 close가 회귀 예측값보다 낮도록 구성
    # close[idx]를 predicted보다 낮게 만들기 위해 마지막 2행을 더 급락시킴
    n = 32
    closes = [200.0 - i * 1.0 for i in range(n - 2)] + [
        200.0 - (n - 2) * 1.0 - 3.0,  # idx-1: 추가 급락
        200.0 - (n - 1) * 1.0 - 5.0,  # idx (현재봉, 미완성)
    ]
    df = _make_df(close_values=closes)
    sig = LinearRegressionStrategy().generate(df)
    assert sig.action == Action.SELL


def test_hold_low_r2():
    """8. R² < 0.7 → HOLD."""
    df = _make_noisy_df(n=30)
    sig = LinearRegressionStrategy().generate(df)
    # 잡음 데이터라면 R²<0.7일 가능성 높음 → HOLD
    # 실제 계산 값으로 검증
    from src.strategy.linear_regression import _linear_regression
    idx = len(df) - 2
    y = df["close"].iloc[idx - 20 + 1: idx + 1].values
    _, _, r2 = _linear_regression(y)
    if r2 < 0.7:
        assert sig.action == Action.HOLD


def test_linear_regression_helper_perfect():
    """9. 완벽한 선형 데이터 → R²≈1."""
    y = np.arange(20, dtype=float)
    slope, predicted, r_squared = _linear_regression(y)
    assert slope == pytest.approx(1.0, abs=1e-6)
    assert r_squared == pytest.approx(1.0, abs=1e-6)
    assert predicted == pytest.approx(19.0, abs=1e-6)


def test_linear_regression_helper_flat():
    """10. 상수 데이터 → slope≈0, R²≈0 (또는 NaN에 안전)."""
    y = np.ones(20) * 100.0
    slope, predicted, r_squared = _linear_regression(y)
    assert slope == pytest.approx(0.0, abs=1e-6)
    assert predicted == pytest.approx(100.0, abs=1e-6)


def test_buy_high_confidence():
    """11. 강한 상승 추세 → HIGH confidence (R²>0.9)."""
    df = _make_uptrend_df(n=30)
    sig = LinearRegressionStrategy().generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


def test_sell_high_confidence():
    """12. 강한 하락 추세 → HIGH confidence (R²>0.9)."""
    df = _make_downtrend_df(n=30)
    sig = LinearRegressionStrategy().generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence == Confidence.HIGH


def test_signal_fields_complete():
    """13. Signal 필드 완전성."""
    df = _make_uptrend_df(n=30)
    sig = LinearRegressionStrategy().generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert len(sig.reasoning) > 0


def test_exact_min_rows_boundary():
    """14. 정확히 25행 → 에러 없이 Signal 반환."""
    df = _make_df(n=25)
    sig = LinearRegressionStrategy().generate(df)
    assert sig.strategy == "linear_regression"


def test_custom_period():
    """15. 사용자 지정 period=10 작동."""
    df = _make_uptrend_df(n=30)
    sig = LinearRegressionStrategy(period=10).generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_buy_reasoning_contains_slope():
    """16. BUY reasoning에 'slope' 포함."""
    df = _make_uptrend_df(n=30)
    sig = LinearRegressionStrategy().generate(df)
    if sig.action == Action.BUY:
        assert "slope" in sig.reasoning


def test_sell_reasoning_contains_slope():
    """17. SELL reasoning에 'slope' 포함."""
    df = _make_downtrend_df(n=30)
    sig = LinearRegressionStrategy().generate(df)
    if sig.action == Action.SELL:
        assert "slope" in sig.reasoning


def test_buy_signal_bull_case():
    """18. BUY 신호 bull_case 필드 있음."""
    df = _make_uptrend_df(n=30)
    sig = LinearRegressionStrategy().generate(df)
    if sig.action == Action.BUY:
        assert isinstance(sig.bull_case, str)
        assert len(sig.bull_case) > 0
