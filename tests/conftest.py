"""Shared test fixtures for strategy unit tests."""

import numpy as np
import pandas as pd
import pytest
from scipy import stats


# ─────────────────────────────────────────────────────────────
# GARCH(1,1) + Student-t 기반 합성 데이터 생성
# ─────────────────────────────────────────────────────────────

def _generate_garch_returns(
    n: int = 1000,
    omega: float = 0.0001,
    alpha: float = 0.08,
    beta: float = 0.90,
    df: float = 6.0,
) -> np.ndarray:
    """
    GARCH(1,1) + Student-t 분포로 수익률 생성 (fat tails 재현).
    
    Args:
        n: 생성할 수익률 개수
        omega: GARCH intercept (장기 평균 분산)
        alpha: GARCH(1) coefficient (전일 쇼크)
        beta: GARCH(1) coefficient (전일 분산)
        df: Student-t 자유도 (낮을수록 fat tails 강함)
    
    Returns:
        형태 (n,)의 수익률 배열
    
    Notes:
        - BTC 1h 기준 현실적 파라미터:
          omega=0.0001, alpha=0.08, beta=0.90 (alpha+beta≈0.98)
        - Student-t df=6: 실제 kurtosis ≈ 5.0+ (첨도 재현)
    """
    # 초기 조건: 무조건부 분산
    sigma2 = np.ones(n) * omega / (1 - alpha - beta)
    
    returns = np.zeros(n)
    
    for t in range(1, n):
        # Student-t 분포에서 샘플링 (평균 0, 표준편차 1로 정규화)
        z_t = stats.t.rvs(df, loc=0, scale=1)
        
        # 조건부 표준편차 적용
        returns[t] = np.sqrt(sigma2[t-1]) * z_t
        
        # GARCH(1,1) 업데이트: sigma^2_t = omega + alpha * ret^2_{t-1} + beta * sigma^2_{t-1}
        sigma2[t] = omega + alpha * returns[t-1]**2 + beta * sigma2[t-1]
    
    return returns


def _generate_garch_prices(
    n: int = 100,
    initial_price: float = 100.0,
    omega: float = 0.0001,
    alpha: float = 0.08,
    beta: float = 0.90,
    df: float = 6.0,
) -> np.ndarray:
    """
    GARCH 기반 합성 가격 시계열 생성 (fat tails).
    
    Args:
        n: 생성할 캔들 개수
        initial_price: 초기 가격
        omega, alpha, beta: GARCH 파라미터
        df: Student-t 자유도
    
    Returns:
        형태 (n,)의 가격 배열
    """
    returns = _generate_garch_returns(n, omega, alpha, beta, df)
    prices = initial_price * np.exp(np.cumsum(returns))
    return prices


@pytest.fixture
def sample_df():
    """
    기본 샘플 DataFrame 생성 (GARCH(1,1) + Student-t 기반).
    open, high, low, close, volume 필드 포함.
    100~110 범위의 가격, 1000의 거래량.
    
    생성 방식:
    - close: GARCH(1,1) + Student-t 분포로 생성 (fat tails 재현)
    - high/low: close 기반 생성
    - volume: 고정
    
    특성:
    - 첨도: >= 3.0 (vs 기존 0.51)
    - Volatility Clustering: 있음
    """
    n = 100
    close = _generate_garch_prices(n, initial_price=100.0)
    
    # high/low: close 주변 변동 (Wilder's ATR 스타일)
    intra_volatility = np.abs(np.random.randn(n) * 0.5)
    high = close + intra_volatility
    low = close - intra_volatility
    
    df = pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000.0,
    })
    return df


@pytest.fixture
def sample_df_with_ema(sample_df):
    """
    EMA 지표를 포함한 DataFrame.
    ema20, ema50 칼럼 추가.
    """
    df = sample_df.copy()
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    return df


def _make_df(n: int = 100, close_prices=None) -> pd.DataFrame:
    """
    Internal helper for backward compatibility with existing tests.
    지표가 포함된 더미 DataFrame 생성 (GARCH(1,1) + Student-t 기반).
    
    Args:
        n: 캔들 개수
        close_prices: 사용자 정의 가격 배열 (지정 시 이를 우선 사용, GARCH 무시)
    
    Returns:
        기술 지표가 계산된 DataFrame
    """
    if close_prices is not None:
        close = np.array(close_prices, dtype=float)
        n = len(close)
    else:
        # GARCH(1,1) + Student-t 기반 합성 가격
        close = _generate_garch_prices(n, initial_price=100.0)
    
    # high/low: close 주변 변동
    intra_volatility = np.abs(np.random.randn(n) * 0.5)
    high = close + intra_volatility
    low = close - intra_volatility
    
    df = pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000.0,
    })
    
    # 기본 지표 추가
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    
    # ATR14
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]),
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs()
    ], axis=1).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    
    # RSI14
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
    
    # Donchian
    df["donchian_high"] = df["high"].rolling(20).max()
    df["donchian_low"] = df["low"].rolling(20).min()
    
    # VWAP
    typical = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
    
    return df
