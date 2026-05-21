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


# ── 추가 시나리오: target_vol vs realized_vol 비교 ─────────────────────────────

def test_target_vol_greater_than_realized_clips_to_max():
    """realized_vol < target_vol → scalar > 1, max_scalar(2.0)에 클리핑."""
    vt = VolTargeting(target_vol=0.20, annualization=1, max_scalar=2.0, min_scalar=0.1)
    rng = np.random.default_rng(7)
    log_rets = rng.normal(0, 0.10, 24)  # rv ≈ 0.10 < target 0.20
    closes = 100 * np.exp(np.concatenate([[0], np.cumsum(log_rets)]))
    df = pd.DataFrame({"close": closes})
    rv = vt.realized_vol(df)
    s = vt.scalar(df)
    assert rv < vt.target_vol, f"rv({rv:.4f}) should be < target(0.20)"
    assert s == pytest.approx(2.0), "scalar must be clipped to max_scalar when rv << target"


def test_target_vol_less_than_realized_no_clip():
    """realized_vol > target_vol → scalar < 1, min_scalar 클리핑 없는 범위."""
    vt = VolTargeting(target_vol=0.20, annualization=1, max_scalar=2.0, min_scalar=0.1)
    rng = np.random.default_rng(7)
    log_rets = rng.normal(0, 0.40, 24)  # rv ≈ 0.40 > target 0.20
    closes = 100 * np.exp(np.concatenate([[0], np.cumsum(log_rets)]))
    df = pd.DataFrame({"close": closes})
    rv = vt.realized_vol(df)
    s = vt.scalar(df)
    assert rv > vt.target_vol, f"rv({rv:.4f}) should be > target(0.20)"
    expected = vt.target_vol / rv
    assert s == pytest.approx(expected, rel=1e-6), "scalar = target/rv without clipping"
    assert 0.1 < s < 1.0


def test_numerical_stability_identical_prices():
    """모든 가격이 동일(변동 없음) → log_return=0, std=0 → rv=0 → scalar=1.0(fallback)."""
    vt = VolTargeting(target_vol=0.20, annualization=252 * 24)
    df = pd.DataFrame({"close": [100.0] * 25})
    rv = vt.realized_vol(df)
    s = vt.scalar(df)
    # std=0 → rv=0 → _scalar_from_rv returns 1.0
    assert rv == pytest.approx(0.0)
    assert s == pytest.approx(1.0), "zero rv must return scalar=1.0 (no divide-by-zero)"


# ── 추가 경계 조건: 극단적 target_vol ─────────────────────────────────────────

def test_very_small_target_vol_clamps_to_min_scalar():
    """target_vol이 매우 작으면 scalar가 min_scalar에 클리핑."""
    vt = VolTargeting(target_vol=0.0001, annualization=1, max_scalar=2.0, min_scalar=0.1)
    rng = np.random.default_rng(0)
    # rv ≈ 0.20 (정상 변동성) >> target_vol 0.0001 → scalar 극소 → min_scalar
    log_rets = rng.normal(0, 0.20, 24)
    closes = 100 * np.exp(np.concatenate([[0], np.cumsum(log_rets)]))
    df = pd.DataFrame({"close": closes})
    s = vt.scalar(df)
    assert s == pytest.approx(0.1), "very small target_vol must clamp to min_scalar"


def test_very_large_target_vol_clamps_to_max_scalar():
    """target_vol이 매우 크면 scalar가 max_scalar에 클리핑."""
    vt = VolTargeting(target_vol=100.0, annualization=1, max_scalar=2.0, min_scalar=0.1)
    rng = np.random.default_rng(0)
    # rv ≈ 0.20 (정상 변동성) << target_vol 100.0 → scalar 극대 → max_scalar
    log_rets = rng.normal(0, 0.20, 24)
    closes = 100 * np.exp(np.concatenate([[0], np.cumsum(log_rets)]))
    df = pd.DataFrame({"close": closes})
    s = vt.scalar(df)
    assert s == pytest.approx(2.0), "very large target_vol must clamp to max_scalar"


def test_nonpositive_target_vol_raises():
    """target_vol <= 0이면 ValueError."""
    with pytest.raises(ValueError, match="target_vol must be positive"):
        VolTargeting(target_vol=0.0)
    with pytest.raises(ValueError, match="target_vol must be positive"):
        VolTargeting(target_vol=-0.5)


# ── EWMA vol_method 테스트 ────────────────────────────────────────────────────

def test_invalid_vol_method_raises():
    """잘못된 vol_method이면 ValueError."""
    with pytest.raises(ValueError, match="vol_method must be"):
        VolTargeting(vol_method="invalid")


def test_ewma_returns_positive_scalar():
    """ewma 모드에서 realized_vol()이 양수 스칼라를 반환."""
    vt = VolTargeting(vol_method="ewma", ewma_span=10)
    rng = np.random.default_rng(0)
    closes = 100 * np.cumprod(1 + rng.normal(0, 0.01, 25))
    df = _make_df(closes)
    rv = vt.realized_vol(df)
    assert rv > 0.0, "EWMA realized_vol should be positive"
    assert isinstance(rv, float)


def test_simple_returns_positive_scalar():
    """simple 모드(기본값)에서 realized_vol()이 양수 스칼라를 반환."""
    vt = VolTargeting(vol_method="simple")
    rng = np.random.default_rng(1)
    closes = 100 * np.cumprod(1 + rng.normal(0, 0.01, 25))
    df = _make_df(closes)
    rv = vt.realized_vol(df)
    assert rv > 0.0
    assert isinstance(rv, float)


def test_ewma_more_sensitive_to_recent_vol():
    """EWMA가 최근 급등 변동성에 simple보다 더 민감하게 반응."""
    rng = np.random.default_rng(42)
    # 앞부분: 저변동성, 뒷부분: 고변동성
    low_vol_rets = rng.normal(0, 0.002, 15)
    high_vol_rets = rng.normal(0, 0.05, 10)
    all_rets = np.concatenate([low_vol_rets, high_vol_rets])
    closes = 100 * np.exp(np.cumsum(np.concatenate([[0], all_rets])))
    df = _make_df(closes)

    vt_simple = VolTargeting(vol_method="simple", annualization=1)
    vt_ewma = VolTargeting(vol_method="ewma", ewma_span=5, annualization=1)

    rv_simple = vt_simple.realized_vol(df)
    rv_ewma = vt_ewma.realized_vol(df)

    # EWMA는 최근 고변동성에 더 빠르게 반응 → simple보다 큰 값
    assert rv_ewma > rv_simple, (
        f"EWMA rv({rv_ewma:.4f}) should exceed simple rv({rv_simple:.4f}) "
        "when recent volatility spikes"
    )


def test_ewma_adjust_returns_positive():
    """EWMA 모드에서 adjust()가 양수를 반환."""
    vt = VolTargeting(vol_method="ewma", ewma_span=10)
    rng = np.random.default_rng(5)
    closes = 100 * np.cumprod(1 + rng.normal(0, 0.01, 25))
    df = _make_df(closes)
    result = vt.adjust(base_size=0.01, df=df)
    assert result > 0.0
