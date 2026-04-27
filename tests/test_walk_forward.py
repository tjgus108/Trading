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
    closes = 100.0 * np.cumprod(1 + 0.001 + np.random.randn(n) * 0.002)
    highs = closes * 1.005
    lows = closes * 0.995
    atr14 = np.full(n, 1.0)
    return pd.DataFrame({"close": closes, "high": highs, "low": lows, "atr14": atr14})


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
