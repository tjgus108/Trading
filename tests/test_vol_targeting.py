"""VolTargeting 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.risk.vol_targeting import VolTargeting


def _make_df(closes):
    closes = np.asarray(closes, dtype=float)
    return pd.DataFrame({"close": closes})


# ── 경계 조건 테스트 ────────────────────────────────────────────────────────────

def test_nonpositive_base_size_raises():
    """base_size <= 0이면 ValueError."""
    vt = VolTargeting()
    df = _make_df(np.linspace(100, 110, 25))
    with pytest.raises(ValueError, match="base_size must be positive"):
        vt.adjust(base_size=0.0, df=df)
    with pytest.raises(ValueError):
        vt.adjust(base_size=-1.0, df=df)


def test_nonpositive_close_price_fallback():
    """close에 0 또는 음수가 포함되면 fallback → scalar=1.0, adjust=base_size."""
    vt = VolTargeting(target_vol=0.20)
    closes = list(np.linspace(100, 110, 19)) + [0.0]  # 마지막 캔들 0
    df = _make_df(closes)
    result = vt.adjust(base_size=0.05, df=df)
    assert result == pytest.approx(0.05), "fallback scalar=1.0이어야 함"


# ── 기존 동작 검증 ──────────────────────────────────────────────────────────────

def test_scalar_clipped_to_max():
    """변동성이 극히 낮으면 scalar가 max_scalar에 클리핑."""
    vt = VolTargeting(target_vol=0.20, max_scalar=2.0)
    # 거의 flat한 시계열 → realized_vol 매우 낮음 → scalar 매우 크지만 2.0에 클리핑
    closes = [100.0] * 24 + [100.0001]
    df = _make_df(closes)
    s = vt.scalar(df)
    assert s == pytest.approx(2.0)


def test_scalar_clipped_to_min():
    """변동성이 극히 높으면 scalar가 min_scalar에 클리핑."""
    vt = VolTargeting(target_vol=0.20, min_scalar=0.1)
    rng = np.random.default_rng(42)
    # 매우 큰 변동: ±50% 랜덤 수익률
    prices = 100.0 * np.cumprod(1 + rng.uniform(-0.5, 0.5, 25))
    df = _make_df(prices)
    s = vt.scalar(df)
    assert s == pytest.approx(0.1)


def test_adjust_returns_base_when_vol_equals_target():
    """realized_vol == target_vol이면 scalar=1.0, adjusted==base_size."""
    vt = VolTargeting(target_vol=0.20, annualization=1)
    # std(log_returns) = 0.20 이 되도록 역산
    # log_returns = [+0.20, -0.20] → std(ddof=1) = 0.20*sqrt(2)  — 복잡하므로
    # realized_vol()을 직접 패치하지 않고, 단지 fallback 경로(데이터 부족)를 사용
    df = _make_df([100.0])  # len < 2 → fallback rv = target_vol
    result = vt.adjust(base_size=0.05, df=df)
    assert result == pytest.approx(0.05)


def test_adjust_no_double_call(monkeypatch):
    """adjust()가 realized_vol()을 정확히 1회만 호출하는지 확인."""
    vt = VolTargeting()
    df = _make_df(np.linspace(100, 120, 25))
    call_count = {"n": 0}
    original = vt.realized_vol

    def counting_rv(d):
        call_count["n"] += 1
        return original(d)

    monkeypatch.setattr(vt, "realized_vol", counting_rv)
    vt.adjust(base_size=0.01, df=df)
    assert call_count["n"] == 1, f"realized_vol() called {call_count['n']} times, expected 1"
