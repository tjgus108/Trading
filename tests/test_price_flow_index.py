"""PriceFlowIndexStrategy 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action, Confidence, Signal
from src.strategy.price_flow_index import PriceFlowIndexStrategy

strategy = PriceFlowIndexStrategy()


def _make_df(n=30, pfi_target=50.0, rising=True):
    """
    OHLCV DataFrame 생성.
    pfi_target: 마지막 완성 캔들에서의 목표 pfi 값을 유도하는 데이터 생성
    rising: True이면 마지막 완성봉 pfi가 이전보다 높게 설정
    """
    np.random.seed(7)
    base = 100.0

    # pfi 조작: typical_price 상승 비율 제어
    # pfi ≈ 100 * pos_flow / (pos_flow + neg_flow)
    # pos_flow가 크면 pfi 높음, neg_flow가 크면 pfi 낮음
    opens = np.full(n, base, dtype=float)
    closes = np.full(n, base, dtype=float)
    highs = np.full(n, base + 0.5, dtype=float)
    lows = np.full(n, base - 0.5, dtype=float)
    volumes = np.full(n, 1000.0, dtype=float)

    if pfi_target < 30:
        # 과매도: 대부분 하락 (neg_flow 지배), 마지막 완성봉은 반등
        for i in range(n - 3):
            closes[i] = base - i * 0.1
            opens[i] = closes[i] + 0.05
            highs[i] = closes[i] + 0.1
            lows[i] = closes[i] - 0.5

        idx = n - 2
        # 직전봉: 하락
        closes[idx - 1] = closes[idx - 2] - 0.3
        opens[idx - 1] = closes[idx - 1] + 0.05
        highs[idx - 1] = closes[idx - 1] + 0.1
        lows[idx - 1] = closes[idx - 1] - 0.5

        if rising:
            # 마지막 완성봉: 살짝 반등 (전봉보다 typical_price 높게)
            closes[idx] = closes[idx - 1] + 0.1
            opens[idx] = closes[idx] - 0.05
            highs[idx] = closes[idx] + 0.1
            lows[idx] = closes[idx] - 0.1
        else:
            # 계속 하락
            closes[idx] = closes[idx - 1] - 0.1
            opens[idx] = closes[idx] + 0.05
            highs[idx] = closes[idx] + 0.1
            lows[idx] = closes[idx] - 0.5

    elif pfi_target > 70:
        # 과매수: 대부분 상승 (pos_flow 지배), 마지막 완성봉은 하락 전환
        for i in range(n - 3):
            closes[i] = base + i * 0.1
            opens[i] = closes[i] - 0.05
            highs[i] = closes[i] + 0.5
            lows[i] = closes[i] - 0.1

        idx = n - 2
        closes[idx - 1] = closes[idx - 2] + 0.3
        opens[idx - 1] = closes[idx - 1] - 0.05
        highs[idx - 1] = closes[idx - 1] + 0.5
        lows[idx - 1] = closes[idx - 1] - 0.1

        if not rising:
            # 마지막 완성봉: 하락 전환
            closes[idx] = closes[idx - 1] - 0.1
            opens[idx] = closes[idx] + 0.05
            highs[idx] = closes[idx] + 0.1
            lows[idx] = closes[idx] - 0.5
        else:
            # 계속 상승
            closes[idx] = closes[idx - 1] + 0.1
            opens[idx] = closes[idx] - 0.05
            highs[idx] = closes[idx] + 0.5
            lows[idx] = closes[idx] - 0.1

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })
    return df


def _make_oversold_extreme_df(n=30):
    """pfi < 20 조건 유도 (극단적 과매도)."""
    np.random.seed(13)
    base = 100.0
    opens = np.full(n, base, dtype=float)
    closes = np.full(n, base, dtype=float)
    highs = np.full(n, base + 0.5, dtype=float)
    lows = np.full(n, base - 0.5, dtype=float)
    volumes = np.full(n, 1000.0, dtype=float)

    # 거의 전부 하락 (neg_flow 절대 지배)
    for i in range(n - 3):
        closes[i] = base - i * 0.2
        opens[i] = closes[i] + 0.1
        highs[i] = opens[i] + 0.05
        lows[i] = closes[i] - 1.0
        volumes[i] = 5000.0  # 하락 시 볼륨 대

    idx = n - 2
    # 직전봉: 대폭 하락, 볼륨 대
    closes[idx - 1] = closes[idx - 2] - 0.5
    opens[idx - 1] = closes[idx - 1] + 0.1
    highs[idx - 1] = opens[idx - 1] + 0.05
    lows[idx - 1] = closes[idx - 1] - 1.0
    volumes[idx - 1] = 5000.0

    # 마지막 완성봉: 반등 (typical_price 이전보다 높게)
    closes[idx] = closes[idx - 1] + 0.3
    opens[idx] = closes[idx] - 0.1
    highs[idx] = closes[idx] + 0.2
    lows[idx] = opens[idx] - 0.05
    volumes[idx] = 200.0  # 상승 시 볼륨 소

    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    })


def _make_overbought_extreme_df(n=30):
    """pfi > 80 조건 유도 (극단적 과매수)."""
    np.random.seed(17)
    base = 100.0
    opens = np.full(n, base, dtype=float)
    closes = np.full(n, base, dtype=float)
    highs = np.full(n, base + 0.5, dtype=float)
    lows = np.full(n, base - 0.5, dtype=float)
    volumes = np.full(n, 1000.0, dtype=float)

    for i in range(n - 3):
        closes[i] = base + i * 0.2
        opens[i] = closes[i] - 0.1
        highs[i] = closes[i] + 1.0
        lows[i] = opens[i] - 0.05
        volumes[i] = 5000.0

    idx = n - 2
    closes[idx - 1] = closes[idx - 2] + 0.5
    opens[idx - 1] = closes[idx - 1] - 0.1
    highs[idx - 1] = closes[idx - 1] + 1.0
    lows[idx - 1] = opens[idx - 1] - 0.05
    volumes[idx - 1] = 5000.0

    # 마지막 완성봉: 하락 전환
    closes[idx] = closes[idx - 1] - 0.3
    opens[idx] = closes[idx] + 0.1
    highs[idx] = opens[idx] + 0.05
    lows[idx] = closes[idx] - 0.2
    volumes[idx] = 200.0

    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    })


# ── 1. 전략 이름 ──────────────────────────────────────────────────────────
def test_strategy_name():
    assert strategy.name == "price_flow_index"


# ── 2. None 입력 → HOLD ──────────────────────────────────────────────────
def test_none_input():
    sig = strategy.generate(None)
    assert sig.action == Action.HOLD


# ── 3. 데이터 부족 → HOLD ────────────────────────────────────────────────
def test_insufficient_data():
    df = _make_df(n=5)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "부족" in sig.reasoning


# ── 4. MIN_ROWS 경계 확인 ────────────────────────────────────────────────
def test_min_rows_boundary():
    df = _make_df(n=strategy.MIN_ROWS)
    sig = strategy.generate(df)
    assert isinstance(sig, Signal)


# ── 5. 과매도 반등 → BUY ─────────────────────────────────────────────────
def test_oversold_rising_buy():
    df = _make_df(n=30, pfi_target=20.0, rising=True)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY


# ── 6. 과매도 하락 지속 → HOLD (반등 없음) ───────────────────────────────
def test_oversold_falling_hold():
    df = _make_df(n=30, pfi_target=20.0, rising=False)
    sig = strategy.generate(df)
    # pfi < 30 but not rising → HOLD
    assert sig.action == Action.HOLD


# ── 7. 과매수 하락 → SELL ────────────────────────────────────────────────
def test_overbought_falling_sell():
    df = _make_df(n=30, pfi_target=80.0, rising=False)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL


# ── 8. 중립 구간 (pfi ≈ 50) → HOLD ──────────────────────────────────────
def test_neutral_pfi_hold():
    df = _make_df(n=30, pfi_target=50.0, rising=True)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD


# ── 9. 극단 과매도 (pfi < 20) → HIGH confidence BUY ──────────────────────
def test_extreme_oversold_high_confidence():
    df = _make_oversold_extreme_df(n=30)
    sig = strategy.generate(df)
    if sig.action == Action.BUY:
        assert sig.confidence == Confidence.HIGH


# ── 10. 극단 과매수 (pfi > 80) → HIGH confidence SELL ────────────────────
def test_extreme_overbought_high_confidence():
    df = _make_overbought_extreme_df(n=30)
    sig = strategy.generate(df)
    if sig.action == Action.SELL:
        assert sig.confidence == Confidence.HIGH


# ── 11. Signal 필드 완전성 ────────────────────────────────────────────────
def test_signal_fields():
    df = _make_df(n=30, pfi_target=20.0, rising=True)
    sig = strategy.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "price_flow_index"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 12. entry_price = last(-2) close ─────────────────────────────────────
def test_entry_price_is_last_close():
    df = _make_df(n=30, pfi_target=20.0, rising=True)
    sig = strategy.generate(df)
    expected = float(df.iloc[-2]["close"])
    assert sig.entry_price == expected


# ── 13. BUY reasoning에 "과매도" 포함 ────────────────────────────────────
def test_buy_reasoning_content():
    df = _make_df(n=30, pfi_target=20.0, rising=True)
    sig = strategy.generate(df)
    assert sig.action == Action.BUY
    assert "과매도" in sig.reasoning


# ── 14. SELL reasoning에 "과매수" 포함 ───────────────────────────────────
def test_sell_reasoning_content():
    df = _make_df(n=30, pfi_target=80.0, rising=False)
    sig = strategy.generate(df)
    assert sig.action == Action.SELL
    assert "과매수" in sig.reasoning


# ── 15. HOLD reasoning에 "신호 없음" 포함 ────────────────────────────────
def test_hold_reasoning_content():
    df = _make_df(n=30, pfi_target=50.0, rising=True)
    sig = strategy.generate(df)
    assert sig.action == Action.HOLD
    assert "신호 없음" in sig.reasoning


# ── 16. bull_case/bear_case에 pfi 값 포함 ────────────────────────────────
def test_bull_bear_case_contains_pfi():
    df = _make_df(n=30, pfi_target=20.0, rising=True)
    sig = strategy.generate(df)
    assert "pfi=" in sig.bull_case
    assert "pfi=" in sig.bear_case
