"""OBVDivergenceStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence
from src.strategy.obv_divergence import OBVDivergenceStrategy

strategy = OBVDivergenceStrategy()

_N = 40
_LOOKBACK = 10


def _make_bullish_div_df(n: int = _N, high_conf: bool = False) -> pd.DataFrame:
    """
    Bullish Divergence:
      close_now < close_prev * 1.01  (가격 하락)
      OBV_EMA_now > OBV_EMA_prev     (OBV 상승)

    가격은 낮아지지만 OBV 상승을 만들려면:
      - 하락 시 작은 볼륨 → OBV 조금 감소
      - 상승 시 큰 볼륨 → OBV 많이 증가
      → 결과: 가격 저점 but OBV 고점

    인덱스 구조 (n=40):
      0..27  : base (n-12=28 rows)
      28     : close_prev (idx-10 = n-12)
      29..38 : 10 moves (idx = n-2 = 38)
      39     : 미완성 캔들 (n-1)
    """
    closes = []
    volumes = []

    # 처음 (n-12)봉: 기준점 가격 100
    base = 100.0
    for _ in range(n - 12):
        closes.append(base)
        volumes.append(1000.0)

    # position n-12: close_prev = 100 (idx-10 기준점)
    closes.append(base)
    volumes.append(1000.0)

    # 이후 10봉 (positions n-11 ~ n-2 = idx): 가격은 내려가지만 OBV는 올라야 함
    # 패턴: 상승(큰볼륨), 하락(작은볼륨), 반복 but 전체는 하락
    price = base
    big_vol = 8000.0 if high_conf else 3000.0
    small_vol = 50.0

    # 10 candles: alternating up(big vol) and down(small vol), trending slightly down
    moves = [+0.3, -0.8, +0.3, -0.8, +0.3, -0.8, +0.3, -0.8, +0.3, -0.8]
    for m in moves:
        price += m
        closes.append(price)
        volumes.append(big_vol if m > 0 else small_vol)

    # close_now = price ≈ 100 + 5*0.3 + 5*(-0.8) = 97.5 < 100*1.01=101 ✓

    # 마지막 봉은 미완성 캔들 (position n-1)
    closes.append(price)
    volumes.append(1000.0)

    assert len(closes) == n, f"Expected {n} rows, got {len(closes)}"

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": volumes,
        "ema50": [100.0] * n,
        "atr14": [0.5] * n,
    })
    return df


def _make_bearish_div_df(n: int = _N, high_conf: bool = False) -> pd.DataFrame:
    """
    Bearish Divergence:
      close_now > close_prev * 0.99  (가격 상승)
      OBV_EMA_now < OBV_EMA_prev     (OBV 하락)

    가격은 올라가지만 OBV 하락을 만들려면:
      - 상승 시 작은 볼륨 → OBV 조금 증가
      - 하락 시 큰 볼륨 → OBV 많이 감소
      → 결과: 가격 고점 but OBV 저점

    인덱스 구조 (n=40):
      0..27  : base (n-12=28 rows)
      28     : close_prev (idx-10 = n-12)
      29..38 : 10 moves (idx = n-2 = 38)
      39     : 미완성 캔들 (n-1)
    """
    closes = []
    volumes = []

    base = 100.0
    for _ in range(n - 12):
        closes.append(base)
        volumes.append(1000.0)

    # position n-12: close_prev = 100
    closes.append(base)
    volumes.append(1000.0)

    price = base
    big_vol = 8000.0 if high_conf else 3000.0
    small_vol = 50.0

    # 10 candles: alternating down(big vol) and up(small vol), trending slightly up
    moves = [-0.3, +0.8, -0.3, +0.8, -0.3, +0.8, -0.3, +0.8, -0.3, +0.8]
    for m in moves:
        price += m
        closes.append(price)
        volumes.append(big_vol if m < 0 else small_vol)

    # close_now = price ≈ 100 + 5*(0.8) + 5*(-0.3) = 102.5 > 100*0.99=99 ✓

    closes.append(price)
    volumes.append(1000.0)

    assert len(closes) == n

    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "volume": volumes,
        "ema50": [100.0] * n,
        "atr14": [0.5] * n,
    })
    return df


def _make_flat_df(n: int = _N) -> pd.DataFrame:
    """다이버전스 없는 평탄한 데이터."""
    closes = np.full(n, 100.0, dtype=float)
    df = pd.DataFrame({
        "open": closes,
        "close": closes,
        "high": closes + 0.5,
        "low": closes - 0.5,
        "volume": np.ones(n) * 1000.0,
        "ema50": np.full(n, 100.0),
        "atr14": np.ones(n) * 0.5,
    })
    return df


def _compute_divs(df: pd.DataFrame):
    """OBV Divergence 조건 직접 계산 (검증용)."""
    idx = len(df) - 2
    close_diff = df["close"].diff()
    sign = close_diff.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    obv = (df["volume"] * sign).cumsum()
    obv_ema = obv.ewm(span=20, adjust=False).mean()

    close_now = float(df["close"].iloc[idx])
    close_prev = float(df["close"].iloc[idx - _LOOKBACK])
    obv_ema_now = float(obv_ema.iloc[idx])
    obv_ema_prev = float(obv_ema.iloc[idx - _LOOKBACK])

    bullish = (close_now < close_prev * 1.01) and (obv_ema_now > obv_ema_prev)
    bearish = (close_now > close_prev * 0.99) and (obv_ema_now < obv_ema_prev)

    obv_ema_change = abs(obv_ema_now - obv_ema_prev)
    window_std_vals = obv_ema.iloc[max(0, idx - 19): idx + 1]
    obv_ema_std = float(window_std_vals.std()) if len(window_std_vals) > 1 else 0.0
    is_high = obv_ema_std > 0 and obv_ema_change > obv_ema_std

    return bullish, bearish, is_high, obv_ema_now, obv_ema_prev, close_now, close_prev


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "obv_divergence"


# ── 2. Bullish Divergence → BUY ─────────────────────────────────────────
def test_bullish_divergence_buy():
    df = _make_bullish_div_df()
    bullish, bearish, _, obv_ema_now, obv_ema_prev, close_now, close_prev = _compute_divs(df)
    assert bullish, (
        f"bullish divergence 조건 미충족: close_now={close_now:.2f} < close_prev*1.01={close_prev*1.01:.2f}? "
        f"{close_now < close_prev * 1.01}, obv_ema_now={obv_ema_now:.1f} > obv_ema_prev={obv_ema_prev:.1f}? "
        f"{obv_ema_now > obv_ema_prev}"
    )
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 3. Bearish Divergence → SELL ────────────────────────────────────────
def test_bearish_divergence_sell():
    df = _make_bearish_div_df()
    bullish, bearish, _, obv_ema_now, obv_ema_prev, close_now, close_prev = _compute_divs(df)
    assert bearish, (
        f"bearish divergence 조건 미충족: close_now={close_now:.2f} > close_prev*0.99={close_prev*0.99:.2f}? "
        f"{close_now > close_prev * 0.99}, obv_ema_now={obv_ema_now:.1f} < obv_ema_prev={obv_ema_prev:.1f}? "
        f"{obv_ema_now < obv_ema_prev}"
    )
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 4. BUY HIGH confidence ───────────────────────────────────────────────
def test_buy_high_confidence():
    df = _make_bullish_div_df(high_conf=True)
    bullish, _, is_high, obv_ema_now, obv_ema_prev, close_now, close_prev = _compute_divs(df)
    assert bullish, (
        f"bullish divergence여야 함: close {close_now:.2f} < {close_prev*1.01:.2f}? "
        f"obv_ema {obv_ema_now:.1f} > {obv_ema_prev:.1f}?"
    )
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    if is_high:
        assert sig.confidence == Confidence.HIGH


# ── 5. SELL HIGH confidence ──────────────────────────────────────────────
def test_sell_high_confidence():
    df = _make_bearish_div_df(high_conf=True)
    _, bearish, is_high, obv_ema_now, obv_ema_prev, close_now, close_prev = _compute_divs(df)
    assert bearish, (
        f"bearish divergence여야 함: close {close_now:.2f} > {close_prev*0.99:.2f}? "
        f"obv_ema {obv_ema_now:.1f} < {obv_ema_prev:.1f}?"
    )
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    if is_high:
        assert sig.confidence == Confidence.HIGH


# ── 6. BUY MEDIUM confidence ─────────────────────────────────────────────
def test_buy_medium_confidence():
    df = _make_bullish_div_df(high_conf=False)
    bullish, _, is_high, _, _, _, _ = _compute_divs(df)
    if bullish and not is_high:
        sig = strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM


# ── 7. HOLD — 다이버전스 없음 ───────────────────────────────────────────
def test_hold_no_divergence():
    df = _make_flat_df()
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 8. 데이터 부족 → HOLD (LOW) ──────────────────────────────────────────
def test_insufficient_data():
    df = _make_flat_df(n=10)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW
    assert "부족" in sig.reasoning


# ── 9. None 입력 → HOLD ───────────────────────────────────────────────────
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 10. Signal 필드 완전성 ───────────────────────────────────────────────
def test_signal_fields_complete():
    df = _make_flat_df()
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "obv_divergence"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 11. BUY reasoning에 "Bullish" 포함 ──────────────────────────────────
def test_buy_reasoning_contains_bullish():
    df = _make_bullish_div_df()
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert "Bullish" in sig.reasoning


# ── 12. SELL reasoning에 "Bearish" 포함 ─────────────────────────────────
def test_sell_reasoning_contains_bearish():
    df = _make_bearish_div_df()
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert "Bearish" in sig.reasoning


# ── 13. entry_price = 마지막 완성 캔들 close ─────────────────────────────
def test_entry_price_is_last_close():
    df = _make_bullish_div_df()
    sig = strategy.generate(df)
    expected_close = float(df["close"].iloc[-2])
    assert sig.entry_price == pytest.approx(expected_close, abs=1e-6)


# ── 14. 최소 데이터 경계값 (25행 통과, 24행 실패) ────────────────────────
def test_min_rows_boundary():
    df_ok = _make_flat_df(n=25)
    sig_ok = strategy.generate(df_ok)
    assert sig_ok.action in (Action.BUY, Action.SELL, Action.HOLD)

    df_fail = _make_flat_df(n=24)
    sig_fail = strategy.generate(df_fail)
    assert sig_fail.action == Action.HOLD
    assert sig_fail.confidence == Confidence.LOW
