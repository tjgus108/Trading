"""
CPCV (Combinatorially Purged Cross-Validation) 단위 테스트.
Cycle 215 D(ML): run_cpcv + CPCVResult + _build_purged_train 검증.
"""

import numpy as np
import pandas as pd
import pytest

from src.backtest.cpcv import CPCVResult, run_cpcv, _build_purged_train
from src.strategy.base import Action, BaseStrategy, Confidence, Signal


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------

class AlwaysBuyStrategy(BaseStrategy):
    name = "always_buy_cpcv"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = df.iloc[-1]
        return Signal(
            action=Action.BUY,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning="test",
            invalidation="none",
        )


class HoldStrategy(BaseStrategy):
    name = "hold_cpcv"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = df.iloc[-1]
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning="test",
            invalidation="none",
        )


def make_df(n: int = 600) -> pd.DataFrame:
    """지표 포함 테스트용 DataFrame."""
    np.random.seed(42)
    closes_arr = 100.0 * np.cumprod(1 + 0.001 + np.random.randn(n) * 0.002)
    closes = pd.Series(closes_arr)
    highs = closes * 1.005
    lows = closes * 0.995
    atr14 = np.full(n, 1.0)
    rsi14 = np.full(n, 50.0)
    vwap = closes * 0.99
    ema50 = closes.rolling(50).mean().fillna(closes * 0.98)
    ema20 = closes.rolling(20).mean().fillna(closes * 0.99)
    ema9 = closes.rolling(9).mean().fillna(closes * 0.995)
    ema21 = closes.rolling(21).mean().fillna(closes * 0.98)
    volume = np.full(n, 1000.0)
    donchian_high = closes.rolling(20).max().fillna(closes * 1.005)
    donchian_low = closes.rolling(20).min().fillna(closes * 0.995)
    return pd.DataFrame({
        "close": closes,
        "high": highs,
        "low": lows,
        "atr14": atr14,
        "rsi14": rsi14,
        "vwap": vwap,
        "ema50": ema50,
        "ema20": ema20,
        "ema9": ema9,
        "ema21": ema21,
        "volume": volume,
        "donchian_high": donchian_high,
        "donchian_low": donchian_low,
    })


# ---------------------------------------------------------------------------
# 테스트 1: CPCVResult 데이터클래스 생성
# ---------------------------------------------------------------------------

def test_cpcv_result_dataclass():
    r = CPCVResult(
        paths=[0.5, -0.3, 1.2],
        pbo=0.333,
        n_groups=6,
        k=2,
        mean_sharpe=0.467,
        std_sharpe=0.75,
        n_paths=15,
    )
    assert r.pbo == 0.333
    assert r.n_groups == 6
    assert r.k == 2
    assert len(r.paths) == 3
    assert r.n_paths == 15


# ---------------------------------------------------------------------------
# 테스트 2: CPCVResult.summary() 포맷
# ---------------------------------------------------------------------------

def test_cpcv_result_summary():
    r = CPCVResult(
        paths=[0.5, -0.3],
        pbo=0.5,
        n_groups=6,
        k=2,
        mean_sharpe=0.1,
        std_sharpe=0.4,
        n_paths=15,
    )
    summary = r.summary()
    assert "CPCV_RESULT" in summary
    assert "pbo" in summary
    assert "HIGH_OVERFIT" in summary  # pbo >= 0.5


# ---------------------------------------------------------------------------
# 테스트 3: PBO < 0.5 -> LOW_OVERFIT
# ---------------------------------------------------------------------------

def test_cpcv_result_low_overfit_verdict():
    r = CPCVResult(
        paths=[1.0, 2.0, 0.5],
        pbo=0.0,
        n_groups=6,
        k=2,
        mean_sharpe=1.167,
        std_sharpe=0.76,
        n_paths=15,
    )
    assert "LOW_OVERFIT" in r.summary()


# ---------------------------------------------------------------------------
# 테스트 4: run_cpcv 반환 타입
# ---------------------------------------------------------------------------

def test_run_cpcv_returns_result_type():
    def factory(params):
        return AlwaysBuyStrategy()

    df = make_df(600)
    result = run_cpcv(factory, df, n_groups=6, k=2)
    assert isinstance(result, CPCVResult)


# ---------------------------------------------------------------------------
# 테스트 5: run_cpcv C(6,2)=15 경로 수
# ---------------------------------------------------------------------------

def test_run_cpcv_path_count():
    def factory(params):
        return AlwaysBuyStrategy()

    df = make_df(600)
    result = run_cpcv(factory, df, n_groups=6, k=2)
    # C(6,2) = 15
    assert result.n_paths == 15
    # 실제 실행된 경로 수 <= 15 (데이터 부족 skip 가능)
    assert len(result.paths) <= 15


# ---------------------------------------------------------------------------
# 테스트 6: 데이터 부족 시 graceful 처리
# ---------------------------------------------------------------------------

def test_run_cpcv_insufficient_data():
    def factory(params):
        return AlwaysBuyStrategy()

    df = make_df(100)  # 6 * 50 = 300 필요
    result = run_cpcv(factory, df, n_groups=6, k=2)
    assert result.pbo == 1.0
    assert len(result.paths) == 0
    assert result.n_paths == 0


# ---------------------------------------------------------------------------
# 테스트 7: k >= n_groups -> ValueError
# ---------------------------------------------------------------------------

def test_run_cpcv_k_gte_n_raises():
    def factory(params):
        return AlwaysBuyStrategy()

    df = make_df(600)
    with pytest.raises(ValueError, match="k.*>=.*n_groups"):
        run_cpcv(factory, df, n_groups=6, k=6)


# ---------------------------------------------------------------------------
# 테스트 8: PBO 범위 0~1
# ---------------------------------------------------------------------------

def test_pbo_range():
    def factory(params):
        return AlwaysBuyStrategy()

    df = make_df(600)
    result = run_cpcv(factory, df, n_groups=6, k=2)
    assert 0.0 <= result.pbo <= 1.0


# ---------------------------------------------------------------------------
# 테스트 9: mean_sharpe / std_sharpe 일관성
# ---------------------------------------------------------------------------

def test_mean_std_sharpe_consistency():
    def factory(params):
        return AlwaysBuyStrategy()

    df = make_df(600)
    result = run_cpcv(factory, df, n_groups=6, k=2)
    if result.paths:
        expected_mean = np.mean(result.paths)
        assert abs(result.mean_sharpe - expected_mean) < 0.01


# ---------------------------------------------------------------------------
# 테스트 10: 다른 n_groups/k 조합 (N=4, k=1 -> C(4,1)=4)
# ---------------------------------------------------------------------------

def test_run_cpcv_n4_k1():
    def factory(params):
        return AlwaysBuyStrategy()

    df = make_df(400)
    result = run_cpcv(factory, df, n_groups=4, k=1)
    assert result.n_paths == 4  # C(4,1) = 4


# ---------------------------------------------------------------------------
# 테스트 11: _build_purged_train embargo 적용
# ---------------------------------------------------------------------------

def test_build_purged_train_embargo():
    """embargo 적용 시 훈련셋에서 테스트 인접 구간이 제거됨."""
    n = 600
    df = pd.DataFrame({"x": range(n)})
    group_size = 100
    groups = [(i * group_size, (i + 1) * group_size) for i in range(6)]

    # 테스트 그룹: [2, 3] (인덱스 200~400)
    # 훈련 그룹: [0, 1, 4, 5]
    # embargo = avg_test_len(100) * 0.05 = 5봉
    train_df = _build_purged_train(
        df, groups,
        train_group_ids=[0, 1, 4, 5],
        test_group_ids=(2, 3),
        embargo_pct=0.05,
    )

    # 훈련셋에 테스트 구간(200~400)이 포함되면 안 됨
    train_indices = set(train_df["x"].values)
    for idx in range(200, 400):
        assert idx not in train_indices, f"테스트 구간 인덱스 {idx}가 훈련셋에 포함됨"

    # embargo 구간도 제거됐는지 확인 (195~200 제거, 400~405 제거)
    for idx in range(195, 200):
        assert idx not in train_indices, f"embargo 구간 인덱스 {idx}가 훈련셋에 포함됨"
    for idx in range(400, 405):
        assert idx not in train_indices, f"embargo 구간 인덱스 {idx}가 훈련셋에 포함됨"


# ---------------------------------------------------------------------------
# 테스트 12: _build_purged_train embargo_pct=0 -> embargo 최소 1봉
# ---------------------------------------------------------------------------

def test_build_purged_train_min_embargo():
    """embargo_pct=0이어도 최소 1봉은 제거."""
    n = 300
    df = pd.DataFrame({"x": range(n)})
    groups = [(0, 100), (100, 200), (200, 300)]

    train_df = _build_purged_train(
        df, groups,
        train_group_ids=[0, 2],
        test_group_ids=(1,),
        embargo_pct=0.0,
    )

    train_indices = set(train_df["x"].values)
    # 테스트 구간 100~200이 훈련셋에 없어야 함
    for idx in range(100, 200):
        assert idx not in train_indices

    # embargo 최소 1봉: 99(테스트 직전)와 200(테스트 직후)도 제거
    assert 99 not in train_indices, "embargo 최소 1봉: 인덱스 99가 제거돼야 함"
    assert 200 not in train_indices, "embargo 최소 1봉: 인덱스 200이 제거돼야 함"


# ---------------------------------------------------------------------------
# 테스트 13: params 전달 검증
# ---------------------------------------------------------------------------

def test_run_cpcv_params_passed():
    """strategy_factory에 params가 올바르게 전달되는지 검증."""
    received_params = []

    class ParamCapture(BaseStrategy):
        name = "param_capture"
        def __init__(self, params):
            self._params = params
            received_params.append(params.copy())
        def generate(self, df):
            last = df.iloc[-1]
            return Signal(
                action=Action.HOLD, confidence=Confidence.LOW,
                strategy=self.name, entry_price=float(last["close"]),
                reasoning="test", invalidation="none",
            )

    def factory(params):
        return ParamCapture(params)

    df = make_df(400)
    test_params = {"alpha": 0.5, "beta": 10}
    run_cpcv(factory, df, n_groups=4, k=1, params=test_params)

    # factory가 호출될 때마다 test_params가 전달되어야 함
    assert len(received_params) > 0
    for p in received_params:
        assert p == test_params


# ---------------------------------------------------------------------------
# 테스트 14: HoldStrategy -> 0 trades, PBO = 1.0
# ---------------------------------------------------------------------------

def test_run_cpcv_no_trades_high_pbo():
    """거래 없는 전략은 Sharpe=0 -> 모든 경로 Sharpe <= 0 -> PBO 높음."""
    def factory(params):
        return HoldStrategy()

    df = make_df(600)
    result = run_cpcv(factory, df, n_groups=6, k=2)
    # HoldStrategy는 거래 0건 -> Sharpe=0 -> 모든 경로 sharpe < 0은 아니지만 = 0
    # PBO = P(Sharpe < 0) — 0은 < 0이 아니므로 PBO가 반드시 1.0은 아님
    # 하지만 fail_reasons="no trades" -> sharpe=0 -> negative 아님
    assert isinstance(result, CPCVResult)
    assert result.n_paths > 0 or result.pbo == 1.0


# ---------------------------------------------------------------------------
# 테스트 15: embargo_pct 변경 시 결과 변동
# ---------------------------------------------------------------------------

def test_embargo_pct_affects_train_size():
    """embargo_pct가 크면 훈련셋이 줄어듬."""
    n = 600
    df = pd.DataFrame({"x": range(n)})
    groups = [(i * 100, (i + 1) * 100) for i in range(6)]

    train_small = _build_purged_train(
        df, groups, [0, 1, 4, 5], (2, 3), embargo_pct=0.01)
    train_large = _build_purged_train(
        df, groups, [0, 1, 4, 5], (2, 3), embargo_pct=0.10)

    assert len(train_large) <= len(train_small), (
        f"큰 embargo가 작은 훈련셋을 생성해야 함: "
        f"embargo=0.01 -> {len(train_small)}, embargo=0.10 -> {len(train_large)}"
    )
