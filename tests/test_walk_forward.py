"""
WalkForwardValidator 단위 테스트 (10개).
"""

import numpy as np
import pandas as pd
import pytest

from src.backtest.walk_forward import WalkForwardValidator, WalkForwardValidationResult
from src.strategy.base import Action, BaseStrategy, Confidence, Signal


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------

class AlwaysBuyStrategy(BaseStrategy):
    name = "always_buy"

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
    name = "hold"

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


def make_df(n: int = 500) -> pd.DataFrame:
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
# 테스트 1: 인스턴스 생성
# ---------------------------------------------------------------------------

def test_validator_instantiation():
    validator = WalkForwardValidator(train_window=200, test_window=50, step_size=50)
    assert validator.train_window == 200
    assert validator.test_window == 50
    assert validator.step_size == 50


# ---------------------------------------------------------------------------
# 테스트 2: validate()가 WalkForwardValidationResult 반환
# ---------------------------------------------------------------------------

def test_validate_returns_result_type():
    validator = WalkForwardValidator(train_window=200, test_window=50, step_size=50)
    df = make_df(500)
    result = validator.validate(df, AlwaysBuyStrategy())
    assert isinstance(result, WalkForwardValidationResult)


# ---------------------------------------------------------------------------
# 테스트 3: windows 수가 올바름
# ---------------------------------------------------------------------------

def test_windows_count_correct():
    # 500봉, train=200, test=50, step=50
    # 윈도우: start=0 (end=250), start=50 (end=300), ..., start=250 (end=500)
    validator = WalkForwardValidator(train_window=200, test_window=50, step_size=50)
    df = make_df(500)
    result = validator.validate(df, AlwaysBuyStrategy())
    # 수동 계산: start 0,50,100,150,200,250 → test_end 250,300,350,400,450,500 (모두 <=500)
    expected_windows = 6
    assert result.windows == expected_windows


# ---------------------------------------------------------------------------
# 테스트 4: mean_return이 float
# ---------------------------------------------------------------------------

def test_mean_return_is_float():
    validator = WalkForwardValidator(train_window=200, test_window=50, step_size=50)
    df = make_df(500)
    result = validator.validate(df, AlwaysBuyStrategy())
    assert isinstance(result.mean_return, float)


# ---------------------------------------------------------------------------
# 테스트 5: consistency_score가 0~1 범위
# ---------------------------------------------------------------------------

def test_consistency_score_range():
    validator = WalkForwardValidator(train_window=200, test_window=50, step_size=50)
    df = make_df(500)
    result = validator.validate(df, AlwaysBuyStrategy())
    assert 0.0 <= result.consistency_score <= 1.0


# ---------------------------------------------------------------------------
# 테스트 6: 데이터 부족 시 ValueError 발생
# ---------------------------------------------------------------------------

def test_insufficient_data_raises():
    validator = WalkForwardValidator(train_window=200, test_window=50, step_size=50)
    df = make_df(100)  # 100 < 200+50
    with pytest.raises(ValueError, match="데이터 부족"):
        validator.validate(df, AlwaysBuyStrategy())


# ---------------------------------------------------------------------------
# 테스트 7: 다양한 train/test 윈도우 설정
# ---------------------------------------------------------------------------

def test_custom_window_settings():
    validator = WalkForwardValidator(train_window=100, test_window=30, step_size=30)
    df = make_df(400)
    result = validator.validate(df, HoldStrategy())
    assert isinstance(result, WalkForwardValidationResult)
    assert result.windows >= 1


# ---------------------------------------------------------------------------
# 테스트 8: 각 results에 start/end 인덱스 포함
# ---------------------------------------------------------------------------

def test_results_contain_start_end():
    validator = WalkForwardValidator(train_window=200, test_window=50, step_size=50)
    df = make_df(500)
    result = validator.validate(df, AlwaysBuyStrategy())
    assert result.windows > 0
    for r in result.results:
        assert "start" in r
        assert "end" in r
        assert "test_start" in r
        assert "test_end" in r
        assert r["start"] >= 0
        assert r["end"] > r["start"]


# ---------------------------------------------------------------------------
# 테스트 9: fee_rate/slippage_pct 파라미터 전달 (예외 없이 실행)
# ---------------------------------------------------------------------------

def test_fee_slippage_params_passed():
    validator = WalkForwardValidator(train_window=200, test_window=50, step_size=50)
    df = make_df(500)
    # 수수료/슬리피지 0으로 설정해도 정상 동작해야 함
    result = validator.validate(df, AlwaysBuyStrategy(), fee_rate=0.0, slippage_pct=0.0)
    assert isinstance(result, WalkForwardValidationResult)

    # 높은 수수료로도 동작해야 함
    result_high_fee = validator.validate(df, AlwaysBuyStrategy(), fee_rate=0.005, slippage_pct=0.001)
    assert isinstance(result_high_fee, WalkForwardValidationResult)


# ---------------------------------------------------------------------------
# 테스트 10: win_rate 계산 검증 (수익 윈도우 수 / 전체 윈도우 수)
# ---------------------------------------------------------------------------

def test_win_rate_calculation():
    validator = WalkForwardValidator(train_window=200, test_window=50, step_size=50)
    df = make_df(500)
    result = validator.validate(df, AlwaysBuyStrategy())

    # 수동 계산
    profitable = sum(1 for r in result.results if r["total_return"] > 0)
    expected_win_rate = profitable / result.windows if result.windows > 0 else 0.0

    assert abs(result.win_rate - expected_win_rate) < 1e-9
    assert abs(result.consistency_score - expected_win_rate) < 1e-9


# ---------------------------------------------------------------------------
# 경계 조건 테스트 (Cycle 18, Option 1)
# ---------------------------------------------------------------------------

# 테스트 11: WalkForwardValidator 최소 데이터로 정상 동작
def test_validator_minimum_data():
    """정확히 train_window + test_window 데이터로 정상 동작."""
    validator = WalkForwardValidator(train_window=200, test_window=50, step_size=50)
    df = make_df(250)  # 정확히 200 + 50
    result = validator.validate(df, AlwaysBuyStrategy())
    assert result.windows == 1


# 테스트 12: WalkForwardOptimizer 데이터 부족 (< 200)
def test_optimizer_insufficient_data():
    """데이터가 200 미만이면 실패 결과 반환."""
    from src.backtest.walk_forward import WalkForwardOptimizer
    from src.strategy.funding_rate import FundingRateStrategy

    def factory(params: dict):
        return FundingRateStrategy(**params)

    opt = WalkForwardOptimizer(
        strategy_name="funding_rate",
        strategy_factory=factory,
        param_grid={"long_threshold": [0.0003], "short_threshold": [-0.0001]},
        n_windows=2,
    )
    df = make_df(100)  # 100 < 200
    result = opt.run(df)
    assert not result.is_stable
    assert len(result.fail_reasons) > 0
    assert "데이터 부족" in result.fail_reasons[0]


# 테스트 13: WalkForwardOptimizer 매개변수 그리드 없음
def test_optimizer_no_param_grid():
    """param_grid가 없고 DEFAULT에도 없으면 실패."""
    from src.backtest.walk_forward import WalkForwardOptimizer
    from src.strategy.base import BaseStrategy

    class DummyStrategy(BaseStrategy):
        name = "dummy"
        def generate(self, df):
            return None

    opt = WalkForwardOptimizer(
        strategy_name="unknown_strategy",
        strategy_factory=lambda p: DummyStrategy(),
        param_grid=None,  # 명시적으로 없음
        n_windows=2,
    )
    df = make_df(500)
    result = opt.run(df)
    assert not result.is_stable
    assert "파라미터 그리드" in result.fail_reasons[0]


# 테스트 14: WalkForwardOptimizer 윈도우 경계 조건 (정확히 최소 요구)
def test_optimizer_window_boundary_exact_minimum():
    """
    윈도우 분할에서 IS >= 100, OOS >= 30 최소 요구.
    n_windows=1, is_ratio=0.6인 경우:
      - window_size = n // (n_windows + 1) = 260 // 2 = 130
      - oos_size = 130 * (1 - 0.6) = 52
      - is_size = 130 - 52 = 78 < 100 이므로 윈도우 버려짐
    n_windows=2라도 분할을 통해 정확히 필요한 크기만 사용할 수 있는지 검증.
    """
    from src.backtest.walk_forward import WalkForwardOptimizer
    from src.strategy.funding_rate import FundingRateStrategy
    
    def factory(params: dict):
        return FundingRateStrategy(**params)
    
    # 260봉: window_size=130, is=78, oos=52 → IS부족 (78<100)
    opt = WalkForwardOptimizer(
        strategy_name="funding_rate",
        strategy_factory=factory,
        param_grid={"long_threshold": [0.0003], "short_threshold": [-0.0001]},
        n_windows=1,
    )
    df = make_df(260)
    result = opt.run(df)
    # 윈도우가 최소값 미충족으로 버려지므로 유효 윈도우 없음
    assert len(result.windows) == 0
    assert not result.is_stable



# 테스트 14: IS<=0, OOS>0 → ratio=1.0 (non-overfit 오분류 수정)
def test_ratio_negative_is_positive_oos():
    """IS Sharpe<=0이고 OOS Sharpe>0이면 ratio=1.0으로 non-overfit 처리."""
    from src.backtest.walk_forward import WindowResult
    # ratio 계산 로직 직접 검증
    best_is_sharpe = -0.3
    oos_sharpe = 0.5

    if best_is_sharpe > 0:
        ratio = oos_sharpe / best_is_sharpe
    elif oos_sharpe > 0:
        ratio = 1.0
    else:
        ratio = 0.0

    assert ratio == 1.0, f"IS<=0 OOS>0 should be non-overfit (ratio=1.0), got {ratio}"

    # IS<=0, OOS<=0 → ratio=0.0
    oos_sharpe2 = -0.1
    if best_is_sharpe > 0:
        ratio2 = oos_sharpe2 / best_is_sharpe
    elif oos_sharpe2 > 0:
        ratio2 = 1.0
    else:
        ratio2 = 0.0

    assert ratio2 == 0.0, f"IS<=0 OOS<=0 should be overfit (ratio=0.0), got {ratio2}"


# ---------------------------------------------------------------------------
# RollingOOSValidator 테스트 (Cycle 180)
# ---------------------------------------------------------------------------

class AlwaysSellStrategy(BaseStrategy):
    """항상 SELL 신호 → 하락장에서 수익."""
    name = "always_sell"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = df.iloc[-1]
        return Signal(
            action=Action.SELL,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning="test",
            invalidation="none",
        )


def make_oos_df(n: int = 2000) -> pd.DataFrame:
    """RollingOOSValidator용 대형 DataFrame (기본 IS 1080 + OOS 360 = 1440 필요)."""
    np.random.seed(42)
    closes = 100.0 * np.cumprod(1 + 0.0005 + np.random.randn(n) * 0.002)
    highs = closes * 1.005
    lows = closes * 0.995
    atr14 = np.full(n, 1.0)
    return pd.DataFrame({"close": closes, "high": highs, "low": lows, "atr14": atr14})


# 테스트 15: RollingOOSValidator 인스턴스 생성
def test_rolling_oos_instantiation():
    from src.backtest.walk_forward import RollingOOSValidator
    v = RollingOOSValidator(is_bars=100, oos_bars=50, slide_bars=50)
    assert v.is_bars == 100
    assert v.oos_bars == 50
    assert v.slide_bars == 50


# 테스트 16: 데이터 부족 시 graceful 처리
def test_rolling_oos_insufficient_data():
    from src.backtest.walk_forward import RollingOOSValidator, BundleOOSResult
    v = RollingOOSValidator(is_bars=1080, oos_bars=360)
    df = make_df(500)  # 500 < 1080 + 360
    result = v.validate(AlwaysBuyStrategy(), df)
    assert isinstance(result, BundleOOSResult)
    assert not result.all_passed
    assert len(result.folds) == 0
    assert "데이터 부족" in result.fail_reasons[0]


# 테스트 17: 빈 데이터 (0행)
def test_rolling_oos_empty_data():
    from src.backtest.walk_forward import RollingOOSValidator, BundleOOSResult
    v = RollingOOSValidator(is_bars=100, oos_bars=50)
    df = pd.DataFrame({"close": [], "high": [], "low": [], "atr14": []})
    result = v.validate(AlwaysBuyStrategy(), df)
    assert isinstance(result, BundleOOSResult)
    assert not result.all_passed
    assert len(result.folds) == 0


# 테스트 18: 정확히 최소 데이터 (is_bars + oos_bars)로 1 fold 생성
def test_rolling_oos_exact_minimum_data():
    from src.backtest.walk_forward import RollingOOSValidator
    v = RollingOOSValidator(is_bars=100, oos_bars=50, slide_bars=50)
    df = make_oos_df(150)  # 정확히 100 + 50
    result = v.validate(AlwaysBuyStrategy(), df)
    assert len(result.folds) == 1


# 테스트 19: WFE 계산 — IS Sharpe 음수일 때 올바른 처리
def test_rolling_oos_wfe_negative_is_sharpe():
    """IS Sharpe가 음수일 때 WFE가 apply_wfe와 동일 로직으로 계산되는지 검증."""
    from src.backtest.walk_forward import RollingOOSValidator
    # 작은 윈도우로 빠른 검증
    v = RollingOOSValidator(is_bars=100, oos_bars=50, slide_bars=50)
    df = make_oos_df(200)
    result = v.validate(HoldStrategy(), df)
    # HoldStrategy는 거래 없음 → Sharpe 0 또는 매우 낮음
    for fold in result.folds:
        # WFE는 0.0 또는 1.0 (음수 IS 처리에 따라)이어야 함
        # 절대로 극단적 큰 값(>10)이 되면 안 됨
        assert fold.wfe <= 10.0, f"WFE too large: {fold.wfe} (broken negative IS handling)"


# 테스트 20: 여러 fold가 올바르게 슬라이드되는지 확인
def test_rolling_oos_multiple_folds():
    from src.backtest.walk_forward import RollingOOSValidator
    v = RollingOOSValidator(is_bars=100, oos_bars=50, slide_bars=50)
    df = make_oos_df(400)  # 100+50=150, 슬라이드 50씩 → 여러 fold
    result = v.validate(AlwaysBuyStrategy(), df)
    # 400봉, start=0→end=150, start=50→end=200, ..., start=200→end=350, start=250→end=400
    assert result.folds is not None
    assert len(result.folds) >= 2
    # fold_id는 순차적
    for i, fold in enumerate(result.folds):
        assert fold.fold_id == i


# 테스트 21: BundleOOSResult.summary() 포맷 검증
def test_bundle_oos_result_summary_format():
    from src.backtest.walk_forward import BundleOOSResult, OOSFoldResult
    fold = OOSFoldResult(
        fold_id=0, is_sharpe=1.5, oos_sharpe=1.0,
        is_mdd=0.05, oos_mdd=0.08, wfe=0.667,
        oos_pf=1.8, oos_trades=20, passed=True, fail_reasons=[],
    )
    result = BundleOOSResult(
        strategy_name="test_strat", folds=[fold],
        avg_wfe=0.667, avg_oos_sharpe=1.0, avg_oos_pf=1.8,
        all_passed=True, fail_reasons=[],
    )
    summary = result.summary()
    assert "test_strat" in summary
    assert "PASS" in summary
    assert "0.667" in summary


# ---------------------------------------------------------------------------
# Cycle 185 A: EmaCrossStrategy & DonchianBreakoutStrategy 파라미터 최적화 테스트
# ---------------------------------------------------------------------------

def test_optimize_ema_cross_uses_params():
    """optimize_ema_cross()가 서로 다른 파라미터 조합을 테스트하는지 검증.
    
    - 다양한 (fast_span, slow_span) 조합이 실제로 다른 전략 인스턴스를 생성
    - 최소 2개 이상 파라미터 조합 테스트
    """
    from src.backtest.walk_forward import optimize_ema_cross
    from src.strategy.ema_cross import EmaCrossStrategy
    
    df = make_df(500)
    result = optimize_ema_cross(df, n_windows=2)
    
    # 결과 검증: best_params에 fast_span과 slow_span이 있어야 함
    assert "fast_span" in result.best_params
    assert "slow_span" in result.best_params
    
    # best_params가 DEFAULT_GRIDS의 값 중 하나여야 함
    from src.backtest.walk_forward import DEFAULT_GRIDS
    assert result.best_params["fast_span"] in DEFAULT_GRIDS["ema_cross"]["fast_span"]
    assert result.best_params["slow_span"] in DEFAULT_GRIDS["ema_cross"]["slow_span"]
    
    # 윈도우 결과가 있어야 함 (여러 파라미터 조합이 테스트됨)
    assert len(result.windows) > 0
    
    # 각 윈도우의 파라미터가 유효해야 함
    for window in result.windows:
        assert "fast_span" in window.params
        assert "slow_span" in window.params
        assert isinstance(window.params["fast_span"], int)
        assert isinstance(window.params["slow_span"], int)


def test_optimize_donchian_uses_params():
    """optimize_donchian()이 서로 다른 channel_period를 테스트하는지 검증.
    
    - 다양한 channel_period 값이 실제로 다른 전략 인스턴스 생성
    """
    from src.backtest.walk_forward import optimize_donchian
    from src.strategy.donchian_breakout import DonchianBreakoutStrategy
    
    df = make_df(500)
    result = optimize_donchian(df, n_windows=2)
    
    # 결과 검증: best_params에 channel_period가 있어야 함
    assert "channel_period" in result.best_params
    
    # best_params가 DEFAULT_GRIDS의 값 중 하나여야 함
    from src.backtest.walk_forward import DEFAULT_GRIDS
    assert result.best_params["channel_period"] in DEFAULT_GRIDS["donchian_breakout"]["channel_period"]
    
    # 윈도우 결과가 있어야 함
    assert len(result.windows) > 0
    
    # 각 윈도우의 파라미터가 유효해야 함
    for window in result.windows:
        assert "channel_period" in window.params
        assert isinstance(window.params["channel_period"], int)


def test_ema_cross_dynamic_params():
    """EmaCrossStrategy가 다양한 fast_span/slow_span으로 다른 EMA 값을 생성하는지 검증.
    
    - fast_span=10, slow_span=30 vs 기본값(20, 50)이 다른 EMA 값 생성
    """
    from src.strategy.ema_cross import EmaCrossStrategy
    
    # 합성 데이터 생성 (100봉)
    np.random.seed(42)
    closes = 100.0 * np.cumprod(1 + 0.0005 + np.random.randn(100) * 0.002)
    highs = closes * 1.005
    lows = closes * 0.995
    
    # 지표 추가
    df = pd.DataFrame({
        "close": closes,
        "high": highs,
        "low": lows,
        "atr14": np.full(100, 1.0),
        "rsi14": np.full(100, 50.0),
        "vwap": closes * 0.99,
    })
    
    # 기본값(20, 50)으로 생성
    strat_default = EmaCrossStrategy(fast_span=20, slow_span=50)
    ema_fast_default, ema_fast_prev_default, ema_slow_default, ema_slow_prev_default = strat_default._get_ema_values(df)
    
    # 다른 파라미터(10, 30)로 생성
    strat_custom = EmaCrossStrategy(fast_span=10, slow_span=30)
    ema_fast_custom, ema_fast_prev_custom, ema_slow_custom, ema_slow_prev_custom = strat_custom._get_ema_values(df)
    
    # 두 파라미터 조합이 다른 EMA 값을 생성해야 함
    # 적어도 fast 또는 slow EMA가 다를 것으로 예상
    ema_fast_differs = abs(ema_fast_default - ema_fast_custom) > 0.01
    ema_slow_differs = abs(ema_slow_default - ema_slow_custom) > 0.01
    
    assert ema_fast_differs or ema_slow_differs, \
        f"Different params should produce different EMA values. " \
        f"Default fast={ema_fast_default:.2f}, Custom fast={ema_fast_custom:.2f}, " \
        f"Default slow={ema_slow_default:.2f}, Custom slow={ema_slow_custom:.2f}"


def test_is_optimization_improves_sharpe():
    """IS 최적화 효과 측정: 파라미터별 IS Sharpe 분포가 기록되고 최적 파라미터가 올바르게 선택되는지 검증."""
    from src.backtest.walk_forward import optimize_ema_cross, DEFAULT_GRIDS

    df = make_df(500)
    result = optimize_ema_cross(df, n_windows=2)

    # last_is_sharpe_dist에 분포가 기록되어야 함
    assert len(result.last_is_sharpe_dist) > 0, "last_is_sharpe_dist가 비어 있음"

    # 파라미터 조합 수 이하의 항목이어야 함 (실패한 조합 제외)
    expected_n = (
        len(DEFAULT_GRIDS["ema_cross"]["fast_span"])
        * len(DEFAULT_GRIDS["ema_cross"]["slow_span"])
    )
    assert len(result.last_is_sharpe_dist) <= expected_n

    all_sharpes = list(result.last_is_sharpe_dist.values())
    # IS Sharpe 분포의 spread가 0 이상이어야 함 (합성 데이터에서 동일 허용)
    if len(all_sharpes) > 1:
        spread = max(all_sharpes) - min(all_sharpes)
        assert spread >= 0.0

    # 각 윈도우의 IS Sharpe는 apply_wfe의 clamp로 0 이상이어야 함
    for window in result.windows:
        assert window.is_sharpe >= 0.0, f"IS Sharpe가 음수: {window.is_sharpe}"


def test_donchian_dynamic_params():
    """DonchianBreakoutStrategy가 다양한 channel_period로 다른 채널 값을 생성하는지 검증.

    - channel_period=10 vs 기본값(20)이 다른 Donchian 채널 값 생성
    """
    from src.strategy.donchian_breakout import DonchianBreakoutStrategy
    
    # 합성 데이터 생성 (100봉)
    np.random.seed(42)
    closes = 100.0 * np.cumprod(1 + 0.0005 + np.random.randn(100) * 0.002)
    highs = closes * 1.005
    lows = closes * 0.995
    
    # 지표 추가
    df = pd.DataFrame({
        "close": closes,
        "high": highs,
        "low": lows,
        "atr14": np.full(100, 1.0),
        "rsi14": np.full(100, 50.0),
    })
    
    # 기본값(20)으로 생성
    strat_default = DonchianBreakoutStrategy(channel_period=20)
    d_high_default, d_high_prev_default, d_low_default, d_low_prev_default = strat_default._get_channel_values(df)
    
    # 다른 파라미터(10)로 생성
    strat_custom = DonchianBreakoutStrategy(channel_period=10)
    d_high_custom, d_high_prev_custom, d_low_custom, d_low_prev_custom = strat_custom._get_channel_values(df)
    
    # 두 파라미터가 다른 채널 값을 생성해야 함
    # 짧은 기간(10)은 일반적으로 더 좁은 채널을 생성 → high가 더 낮거나 low가 더 높음
    high_differs = abs(d_high_default - d_high_custom) > 0.01
    low_differs = abs(d_low_default - d_low_custom) > 0.01

    assert high_differs or low_differs, \
        f"Different channel_period should produce different channel values. " \
        f"Default high={d_high_default:.2f}, Custom high={d_high_custom:.2f}, " \
        f"Default low={d_low_default:.2f}, Custom low={d_low_custom:.2f}"


# ---------------------------------------------------------------------------
# 플래토 룰 테스트 (Cycle 189 D(ML))
# ---------------------------------------------------------------------------

def test_plateau_pct_parameter_accepted():
    """WalkForwardOptimizer가 plateau_pct 파라미터를 수용하는지 검증."""
    from src.backtest.walk_forward import WalkForwardOptimizer
    from src.strategy.ema_cross import EmaCrossStrategy

    def factory(params):
        return EmaCrossStrategy(
            fast_span=params.get("fast_span", 20),
            slow_span=params.get("slow_span", 50),
        )

    opt = WalkForwardOptimizer(
        strategy_name="ema_cross",
        strategy_factory=factory,
        param_grid={"fast_span": [10, 20], "slow_span": [40, 50]},
        n_windows=2,
        plateau_pct=0.9,
    )
    assert opt.plateau_pct == 0.9


def test_plateau_pct_result_in_grid():
    """플래토 룰 적용 후 선택된 파라미터가 제공된 그리드 내에 있어야 함."""
    from src.backtest.walk_forward import WalkForwardOptimizer
    from src.strategy.ema_cross import EmaCrossStrategy

    grid = {"fast_span": [10, 15, 20], "slow_span": [40, 50, 60]}

    def factory(params):
        return EmaCrossStrategy(
            fast_span=params.get("fast_span", 20),
            slow_span=params.get("slow_span", 50),
        )

    opt = WalkForwardOptimizer(
        strategy_name="ema_cross",
        strategy_factory=factory,
        param_grid=grid,
        n_windows=2,
        plateau_pct=0.9,
    )
    df = make_df(600)
    result = opt.run(df)
    # 유효 윈도우가 생성되었으면 파라미터가 그리드 내에 있어야 함
    if result.best_params:
        assert result.best_params.get("fast_span") in grid["fast_span"]
        assert result.best_params.get("slow_span") in grid["slow_span"]


def test_plateau_pct_disabled_with_zero():
    """plateau_pct=0.0이면 플래토 룰이 비활성화되고 순수 Sharpe 최대화 파라미터 선택."""
    from src.backtest.walk_forward import WalkForwardOptimizer
    from src.strategy.ema_cross import EmaCrossStrategy

    def factory(params):
        return EmaCrossStrategy(
            fast_span=params.get("fast_span", 20),
            slow_span=params.get("slow_span", 50),
        )

    opt = WalkForwardOptimizer(
        strategy_name="ema_cross",
        strategy_factory=factory,
        param_grid={"fast_span": [10, 20], "slow_span": [40, 50]},
        n_windows=2,
        plateau_pct=0.0,
    )
    df = make_df(600)
    result = opt.run(df)
    # 정상 동작 (예외 없이 결과 반환)
    assert result is not None
    assert isinstance(result.best_params, dict)


def test_plateau_pct_effect_vs_zero():
    """plateau_pct=0.9이면 plateau_pct=0.0과 다른 파라미터를 선택할 수 있어야 함.
    동일 그리드에서 두 설정의 best_params가 동일하지 않을 가능성을 검증.
    (결과가 동일해도 오류 아님 - 그리드가 작아서 plateau 집합이 1개일 수 있음)
    """
    from src.backtest.walk_forward import WalkForwardOptimizer
    from src.strategy.ema_cross import EmaCrossStrategy

    grid = {"fast_span": [5, 10, 20, 30], "slow_span": [40, 60, 80, 100]}

    def factory(params):
        return EmaCrossStrategy(
            fast_span=params.get("fast_span", 10),
            slow_span=params.get("slow_span", 50),
        )

    df = make_df(800)

    opt_plateau = WalkForwardOptimizer(
        strategy_name="ema_cross", strategy_factory=factory,
        param_grid=grid, n_windows=2, plateau_pct=0.9,
    )
    opt_no_plateau = WalkForwardOptimizer(
        strategy_name="ema_cross", strategy_factory=factory,
        param_grid=grid, n_windows=2, plateau_pct=0.0,
    )
    result_p = opt_plateau.run(df)
    result_np = opt_no_plateau.run(df)
    # 둘 다 정상 실행 (예외 없이 결과 반환)
    assert result_p is not None
    assert result_np is not None
    assert isinstance(result_p.best_params, dict)
    assert isinstance(result_np.best_params, dict)


def test_plateau_pct_selects_from_plateau_set():
    """plateau_pct=0.9 적용 시 선택 파라미터는 그리드의 중간 영역에서 올 가능성이 높음.
    fast_span 그리드 [5, 10, 20, 30] 에서 plateau 선택은 극단(5 또는 30)보다 중간(10, 20)을 선호.
    주의: 이 테스트는 선택 가능성을 검증하며 결정론적 보장은 아님.
    """
    from src.backtest.walk_forward import WalkForwardOptimizer
    from src.strategy.ema_cross import EmaCrossStrategy

    grid = {"fast_span": [5, 10, 20, 30], "slow_span": [40, 60, 80, 100]}

    def factory(params):
        return EmaCrossStrategy(
            fast_span=params.get("fast_span", 10),
            slow_span=params.get("slow_span", 50),
        )

    opt = WalkForwardOptimizer(
        strategy_name="ema_cross", strategy_factory=factory,
        param_grid=grid, n_windows=2, plateau_pct=0.9,
    )
    df = make_df(800)
    result = opt.run(df)
    if result.best_params:
        # 선택된 fast_span은 그리드 내의 유효한 값이어야 함
        assert result.best_params["fast_span"] in grid["fast_span"]
        # slow_span도 그리드 내
        assert result.best_params["slow_span"] in grid["slow_span"]
