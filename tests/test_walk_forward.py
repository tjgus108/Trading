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

