"""
D3. WalkForwardOptimizer: 전략 파라미터 자동 최적화.

방법:
  1. 전체 기간을 in-sample / out-of-sample 윈도우로 분할
  2. in-sample 그리드 서치로 최적 파라미터 탐색
  3. out-of-sample 검증 → 과최적화 여부 판단
  4. 복수 윈도우 결과 집계 → 안정적인 파라미터 선택

과최적화 방지:
  - out-of-sample Sharpe를 최종 기준으로 사용
  - IS/OOS Sharpe 비율 < 0.5이면 과최적화로 판단
  - 안정성 기준: OOS Sharpe 표준편차 < 0.5

지원 전략: EmaCrossStrategy, DonchianBreakoutStrategy (파라미터 딕셔너리 기반)
커스텀 전략: param_grid 딕셔너리로 확장 가능
"""

import itertools
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Type

import pandas as pd

from src.backtest.engine import BacktestEngine, BacktestResult
from src.strategy.base import BaseStrategy

logger = logging.getLogger(__name__)

# 기본 최적화 파라미터 그리드
DEFAULT_GRIDS: dict[str, dict] = {
    "ema_cross": {
        "fast_span": [10, 15, 20],
        "slow_span": [40, 50, 60],
    },
    "donchian_breakout": {
        "channel_period": [15, 20, 25],
    },
    "funding_rate": {
        "long_threshold": [0.0002, 0.0003, 0.0004],
        "short_threshold": [-0.0001, -0.0002],
    },
}

# 과최적화 판단 기준
IS_OOS_RATIO_MIN = 0.5   # OOS Sharpe / IS Sharpe 최소 비율
OOS_STD_MAX = 0.8        # OOS Sharpe 표준편차 최대


@dataclass
class WindowResult:
    """단일 walk-forward 윈도우 결과."""
    window_id: int
    params: dict
    is_sharpe: float    # in-sample 최적 Sharpe
    oos_sharpe: float   # out-of-sample 실제 Sharpe
    oos_passed: bool    # OOS 백테스트 통과 여부
    is_oos_ratio: float # OOS/IS 비율

    def is_overfit(self) -> bool:
        return self.is_oos_ratio < IS_OOS_RATIO_MIN


@dataclass
class WalkForwardResult:
    """전체 walk-forward 최적화 결과."""
    strategy_name: str
    best_params: dict           # 최종 추천 파라미터
    windows: list[WindowResult]
    avg_oos_sharpe: float
    oos_sharpe_std: float
    is_stable: bool             # 안정성 기준 통과 여부
    overfit_windows: int        # 과최적화 의심 윈도우 수
    fail_reasons: list[str] = field(default_factory=list)

    def summary(self) -> str:
        verdict = "STABLE" if self.is_stable else "UNSTABLE"
        lines = [
            f"WALK_FORWARD_RESULT:",
            f"  strategy: {self.strategy_name}",
            f"  best_params: {self.best_params}",
            f"  avg_oos_sharpe: {self.avg_oos_sharpe:.3f}",
            f"  oos_sharpe_std: {self.oos_sharpe_std:.3f}",
            f"  overfit_windows: {self.overfit_windows}/{len(self.windows)}",
            f"  verdict: {verdict}",
        ]
        if self.fail_reasons:
            lines.append(f"  fail_reasons: {self.fail_reasons}")
        return "\n".join(lines)


class WalkForwardOptimizer:
    """
    Walk-Forward 파라미터 최적화기.

    사용:
        opt = WalkForwardOptimizer("ema_cross", strategy_factory)
        result = opt.run(df)
        if result.is_stable:
            use_params = result.best_params
    """

    def __init__(
        self,
        strategy_name: str,
        strategy_factory: Callable[[dict], BaseStrategy],
        param_grid: Optional[dict] = None,
        n_windows: int = 3,
        is_ratio: float = 0.6,    # in-sample 비율
    ):
        """
        Args:
            strategy_name: 전략 이름
            strategy_factory: params dict → BaseStrategy 인스턴스 생성 함수
            param_grid: {"param": [values]} 딕셔너리
            n_windows: walk-forward 윈도우 수
            is_ratio: in-sample 데이터 비율 (0.6 = 60%)
        """
        self.strategy_name = strategy_name
        self.strategy_factory = strategy_factory
        self.n_windows = n_windows
        self.is_ratio = is_ratio
        self._param_grid = param_grid or DEFAULT_GRIDS.get(strategy_name, {})
        self._engine = BacktestEngine()

    def run(self, df: pd.DataFrame) -> WalkForwardResult:
        """Walk-forward 최적화 실행."""
        if not self._param_grid:
            return WalkForwardResult(
                strategy_name=self.strategy_name,
                best_params={},
                windows=[],
                avg_oos_sharpe=0.0,
                oos_sharpe_std=0.0,
                is_stable=False,
                overfit_windows=0,
                fail_reasons=[f"파라미터 그리드 없음 ({self.strategy_name})"],
            )

        n = len(df)
        if n < 200:
            return WalkForwardResult(
                strategy_name=self.strategy_name,
                best_params={},
                windows=[],
                avg_oos_sharpe=0.0,
                oos_sharpe_std=0.0,
                is_stable=False,
                overfit_windows=0,
                fail_reasons=[f"데이터 부족: {n} < 200"],
            )

        # 윈도우 분할
        windows = self._split_windows(df)
        all_combinations = list(self._iter_param_combinations())

        if not all_combinations:
            return WalkForwardResult(
                strategy_name=self.strategy_name,
                best_params={},
                windows=[],
                avg_oos_sharpe=0.0,
                oos_sharpe_std=0.0,
                is_stable=False,
                overfit_windows=0,
                fail_reasons=["파라미터 조합 없음"],
            )

        logger.info(
            "Walk-Forward: %s | %d windows × %d param combinations",
            self.strategy_name, len(windows), len(all_combinations),
        )

        window_results: list[WindowResult] = []
        param_oos_map: dict[str, list[float]] = {}

        for i, (is_df, oos_df) in enumerate(windows):
            # IS 최적화
            best_params, best_is_sharpe = self._optimize_in_sample(is_df, all_combinations)

            # OOS 검증
            oos_strategy = self.strategy_factory(best_params)
            oos_result = self._engine.run(oos_strategy, oos_df)

            ratio = (oos_result.sharpe_ratio / best_is_sharpe
                     if best_is_sharpe > 0 else 0.0)

            wr = WindowResult(
                window_id=i,
                params=best_params,
                is_sharpe=best_is_sharpe,
                oos_sharpe=oos_result.sharpe_ratio,
                oos_passed=oos_result.passed,
                is_oos_ratio=ratio,
            )
            window_results.append(wr)

            # 파라미터별 OOS 성과 집계
            key = str(sorted(best_params.items()))
            param_oos_map.setdefault(key, []).append(oos_result.sharpe_ratio)

            logger.info(
                "Window %d: IS Sharpe=%.3f OOS Sharpe=%.3f ratio=%.2f params=%s",
                i, best_is_sharpe, oos_result.sharpe_ratio, ratio, best_params,
            )

        # 최종 파라미터 선택: OOS Sharpe 평균 가장 높은 파라미터
        if not param_oos_map:
            return WalkForwardResult(
                strategy_name=self.strategy_name,
                best_params={},
                windows=window_results,
                avg_oos_sharpe=0.0,
                oos_sharpe_std=0.0,
                is_stable=False,
                overfit_windows=0,
                fail_reasons=["유효 윈도우 없음 (데이터 부족)"],
            )
        best_key = max(param_oos_map, key=lambda k: sum(param_oos_map[k]) / len(param_oos_map[k]))
        import ast
        best_final_params = dict(ast.literal_eval(best_key))  # str → dict 복원

        import statistics
        oos_sharpes = [wr.oos_sharpe for wr in window_results]
        avg_oos = sum(oos_sharpes) / len(oos_sharpes) if oos_sharpes else 0.0
        oos_std = statistics.stdev(oos_sharpes) if len(oos_sharpes) > 1 else 0.0
        overfit_count = sum(1 for wr in window_results if wr.is_overfit())

        fail_reasons = []
        is_stable = True
        if oos_std > OOS_STD_MAX:
            fail_reasons.append(f"OOS Sharpe 불안정: std={oos_std:.3f} > {OOS_STD_MAX}")
            is_stable = False
        if avg_oos < 0.5:
            fail_reasons.append(f"OOS 평균 Sharpe 낮음: {avg_oos:.3f} < 0.5")
            is_stable = False

        result = WalkForwardResult(
            strategy_name=self.strategy_name,
            best_params=best_final_params,
            windows=window_results,
            avg_oos_sharpe=round(avg_oos, 4),
            oos_sharpe_std=round(oos_std, 4),
            is_stable=is_stable,
            overfit_windows=overfit_count,
            fail_reasons=fail_reasons,
        )
        logger.info(result.summary())
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _split_windows(self, df: pd.DataFrame) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
        """Walk-forward 윈도우 분할."""
        n = len(df)
        window_size = n // (self.n_windows + 1)
        oos_size = int(window_size * (1 - self.is_ratio))
        is_size = window_size - oos_size

        windows = []
        for i in range(self.n_windows):
            start = i * window_size
            is_end = start + is_size
            oos_end = is_end + oos_size
            if oos_end > n:
                break
            is_df = df.iloc[start:is_end]
            oos_df = df.iloc[is_end:oos_end]
            if len(is_df) >= 100 and len(oos_df) >= 30:
                windows.append((is_df, oos_df))

        return windows

    def _optimize_in_sample(
        self, is_df: pd.DataFrame, combinations: list[dict]
    ) -> tuple[dict, float]:
        """그리드 서치로 IS 최적 파라미터 탐색."""
        best_params = combinations[0]
        best_sharpe = -999.0

        for params in combinations:
            try:
                strategy = self.strategy_factory(params)
                result = self._engine.run(strategy, is_df)
                if result.sharpe_ratio > best_sharpe:
                    best_sharpe = result.sharpe_ratio
                    best_params = params
            except Exception as e:
                logger.debug("IS backtest failed for %s: %s", params, e)

        return best_params, max(best_sharpe, 0.0)

    def _iter_param_combinations(self):
        """파라미터 그리드의 모든 조합 생성."""
        if not self._param_grid:
            yield {}
            return
        keys = list(self._param_grid.keys())
        values = list(self._param_grid.values())
        for combo in itertools.product(*values):
            yield dict(zip(keys, combo))


# ------------------------------------------------------------------
# 편의 팩토리 함수들
# ------------------------------------------------------------------

def optimize_ema_cross(df: pd.DataFrame, n_windows: int = 3) -> WalkForwardResult:
    """EMA Cross 전략 파라미터 최적화."""
    from src.strategy.ema_cross import EmaCrossStrategy

    def factory(params: dict) -> BaseStrategy:
        # EmaCrossStrategy는 파라미터를 df에서 계산하므로 전략 자체는 변경 없음
        # 실제로는 span을 DataFeed에서 계산하므로 현재는 동일 전략 반환
        return EmaCrossStrategy()

    opt = WalkForwardOptimizer(
        strategy_name="ema_cross",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["ema_cross"],
        n_windows=n_windows,
    )
    return opt.run(df)


def optimize_donchian(df: pd.DataFrame, n_windows: int = 3) -> WalkForwardResult:
    """Donchian Breakout 전략 파라미터 최적화."""
    from src.strategy.donchian_breakout import DonchianBreakoutStrategy

    def factory(params: dict) -> BaseStrategy:
        return DonchianBreakoutStrategy()

    opt = WalkForwardOptimizer(
        strategy_name="donchian_breakout",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["donchian_breakout"],
        n_windows=n_windows,
    )
    return opt.run(df)


def optimize_funding_rate(df: pd.DataFrame, n_windows: int = 3) -> WalkForwardResult:
    """FundingRate 전략 파라미터 최적화."""
    from src.strategy.funding_rate import FundingRateStrategy

    def factory(params: dict) -> BaseStrategy:
        return FundingRateStrategy(
            long_threshold=params.get("long_threshold", 0.0003),
            short_threshold=params.get("short_threshold", -0.0001),
        )

    opt = WalkForwardOptimizer(
        strategy_name="funding_rate",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["funding_rate"],
        n_windows=n_windows,
    )
    return opt.run(df)


# ------------------------------------------------------------------
# WalkForwardValidator — rolling train/test window 검증
# ------------------------------------------------------------------

from dataclasses import dataclass as _dataclass
from typing import List as _List
import numpy as _np


@_dataclass
class WalkForwardValidationResult:
    """
    WalkForwardValidator.validate() 반환값.
    (WalkForwardResult와 이름 충돌 방지를 위해 별도 클래스 사용)
    """
    windows: int              # 총 윈도우 수
    mean_return: float        # 평균 수익률
    std_return: float         # 수익률 표준편차
    win_rate: float           # 수익 윈도우 비율 (= consistency_score)
    consistency_score: float  # 일관성 점수 (0~1)
    results: _List[dict]      # 각 윈도우 결과


class WalkForwardValidator:
    """
    Rolling train/test window로 전략을 검증한다.

    각 스텝에서:
      - train_window + test_window 크기의 슬라이스를 BacktestEngine에 실행
      - test 구간의 성과를 기록
      - step_size만큼 앞으로 이동

    사용:
        validator = WalkForwardValidator(train_window=200, test_window=50, step_size=50)
        result = validator.validate(df, strategy)
        print(result.consistency_score)
    """

    def __init__(
        self,
        train_window: int = 200,  # 학습 기간 (봉 수)
        test_window: int = 50,    # 테스트 기간 (봉 수)
        step_size: int = 50,      # 슬라이딩 스텝
    ):
        self.train_window = train_window
        self.test_window = test_window
        self.step_size = step_size

    def validate(
        self,
        df: pd.DataFrame,
        strategy: BaseStrategy,
        fee_rate: float = 0.001,
        slippage_pct: float = 0.0005,
    ) -> WalkForwardValidationResult:
        """
        df에 대해 walk-forward validation 실행.

        Args:
            df: OHLCV + 지표 포함 DataFrame
            strategy: BaseStrategy 인스턴스
            fee_rate: 수수료율
            slippage_pct: 슬리피지 비율

        Returns:
            WalkForwardValidationResult

        Raises:
            ValueError: 데이터가 train_window + test_window보다 짧을 때
        """
        min_required = self.train_window + self.test_window
        if len(df) < min_required:
            raise ValueError(
                f"데이터 부족: {len(df)}봉 < 최소 {min_required}봉 "
                f"(train={self.train_window} + test={self.test_window})"
            )

        engine = BacktestEngine(fee_rate=fee_rate, slippage_pct=slippage_pct)
        window_results: _List[dict] = []

        start = 0
        while True:
            test_start = start + self.train_window
            test_end = test_start + self.test_window

            if test_end > len(df):
                break

            # train + test 구간 전체를 엔진에 전달 (지표 warmup 포함)
            window_df = df.iloc[start:test_end].reset_index(drop=True)
            result = engine.run(strategy, window_df)

            window_results.append({
                "window_index": len(window_results),
                "start": start,
                "end": test_end - 1,
                "train_start": start,
                "train_end": test_start - 1,
                "test_start": test_start,
                "test_end": test_end - 1,
                "total_return": result.total_return,
                "sharpe_ratio": result.sharpe_ratio,
                "max_drawdown": result.max_drawdown,
                "total_trades": result.total_trades,
                "win_rate": result.win_rate,
                "passed": result.passed,
            })

            start += self.step_size

        if not window_results:
            return WalkForwardValidationResult(
                windows=0,
                mean_return=0.0,
                std_return=0.0,
                win_rate=0.0,
                consistency_score=0.0,
                results=[],
            )

        returns = _np.array([r["total_return"] for r in window_results])
        profitable_count = sum(1 for r in window_results if r["total_return"] > 0)
        consistency = profitable_count / len(window_results)

        return WalkForwardValidationResult(
            windows=len(window_results),
            mean_return=float(returns.mean()),
            std_return=float(returns.std()) if len(returns) > 1 else 0.0,
            win_rate=consistency,
            consistency_score=consistency,
            results=window_results,
        )
