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
import statistics as _statistics
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Type, Tuple, List, Dict

import pandas as pd

from src.backtest.engine import BacktestEngine, BacktestResult, MIN_WFE
from src.strategy.base import BaseStrategy

logger = logging.getLogger(__name__)

# 기본 최적화 파라미터 그리드
DEFAULT_GRIDS: Dict[str, dict] = {
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
    "cmf": {
        "period": [15, 20, 25],
        "buy_thresh": [0.06, 0.08, 0.10],
    },
    "wick_reversal": {
        "min_wick_ratio": [0.60, 0.65, 0.70],
        "vol_mult": [0.7, 0.8, 0.9],
    },
    "elder_impulse": {
        "ema_span": [10, 13, 15],
        "min_volatility": [0.001, 0.002, 0.003],
    },
    "value_area": {
        "va_period": [10, 15, 20],  # 10 추가: 4h 봉 신호 빈도 개선
        "va_mult": [0.55, 0.60, 0.65],
    },
    "narrow_range": {
        "nr_lookback": [5, 6, 7],  # NR5/NR6/NR7 — 4h봉 0거래 문제 완화
    },
    "frama": {
        "period": [14, 16, 18],
        "rsi_period": [12, 14, 16],
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
    oos_trades: int = 0  # Cycle 257: OOS 거래 수 (저거래 std 오염 방지)

    def is_overfit(self) -> bool:
        return self.is_oos_ratio < IS_OOS_RATIO_MIN


@dataclass
class WalkForwardResult:
    """전체 walk-forward 최적화 결과."""
    strategy_name: str
    best_params: dict           # 최종 추천 파라미터
    windows: List[WindowResult]
    avg_oos_sharpe: float
    oos_sharpe_std: float
    is_stable: bool             # 안정성 기준 통과 여부
    overfit_windows: int        # 과최적화 의심 윈도우 수
    fail_reasons: List[str] = field(default_factory=list)
    # IS 최적화 효과 측정용: 마지막 윈도우의 파라미터별 IS Sharpe 분포
    # {str(sorted(params.items())): is_sharpe} 형태
    last_is_sharpe_dist: Dict[str, float] = field(default_factory=dict)
    # 파라미터 안정성 CV: {param_name: cv} (fold 간 CV=std/mean)
    param_stability_cv: Dict[str, float] = field(default_factory=dict)
    # time-decay 가중평균 OOS Sharpe (정보 제공용, PASS/FAIL 기준 아님)
    weighted_oos_sharpe: Optional[float] = None
    # WFE: Walk Forward Efficiency = avg OOS Sharpe / avg IS Sharpe
    # > 0.7이면 robust, <= 0이면 과최적화 심각
    wfe: Optional[float] = None
    # fold_pass_rate: OOS Sharpe > 0인 fold 비율 (0.0~1.0)
    fold_pass_rate: Optional[float] = None
    # low_trades_folds: OOS trades < 30인 fold 수 (통계적 신뢰도 낮음 경고)
    low_trades_folds: int = 0
    # plateau_score: 최적 파라미터 주변 ±10% 범위의 IS Sharpe 안정성 (0~1)
    # = mean(neighbor_sharpes) / best_sharpe.  1.0에 가까울수록 안정적.
    # None이면 계산 불가 (그리드 내 이웃 없음 등)
    plateau_score: Optional[float] = None

    @property
    def is_robust(self) -> bool:
        """WFE > 0.7이면 robust 판정. wfe가 None이면 False."""
        return self.wfe is not None and self.wfe > 0.7

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
        if self.wfe is not None:
            robust_tag = "ROBUST" if self.is_robust else "NOT_ROBUST"
            lines.append(f"  wfe: {self.wfe:.3f} ({robust_tag})")
        if self.fold_pass_rate is not None:
            lines.append(f"  fold_pass_rate: {self.fold_pass_rate:.2%}")
        if self.low_trades_folds > 0:
            lines.append(f"  [WARN] low_trades_folds: {self.low_trades_folds}/{len(self.windows)} (OOS<30 trades)")
        if self.weighted_oos_sharpe is not None:
            lines.append(f"  weighted_oos_sharpe: {self.weighted_oos_sharpe:.3f}")
        if self.plateau_score is not None:
            plateau_tag = "STABLE" if self.plateau_score >= 0.8 else "SENSITIVE"
            lines.append(f"  plateau_score: {self.plateau_score:.3f} ({plateau_tag})")
        if self.param_stability_cv:
            unstable = {k: v for k, v in self.param_stability_cv.items() if v > 0.5}
            lines.append(f"  param_cv: {self.param_stability_cv}")
            if unstable:
                lines.append(f"  [WARN] unstable params (CV>0.5): {unstable}")
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
        stability_lambda: float = 0.5,  # Sharpe - λ*CV penalty 계수
        plateau_pct: float = 0.9,  # 플래토 룰: IS 최고 Sharpe의 이 비율 이상인 파라미터 집합 중 중간값 선택
        fold_decay: float = 0.0,  # time-decay: 0=동일가중, 양수=최근fold에 지수적 가중치
        use_regime_weights: bool = False,  # HIGH_VOL fold 다운웨이팅
    ):
        """
        Args:
            strategy_name: 전략 이름
            strategy_factory: params dict → BaseStrategy 인스턴스 생성 함수
            param_grid: {"param": [values]} 딕셔너리
            n_windows: walk-forward 윈도우 수
            is_ratio: in-sample 데이터 비율 (0.6 = 60%)
            stability_lambda: IS 목적함수 stability penalty 계수.
                              Score = Sharpe - λ * CV (λ=0 이면 순수 Sharpe 최적화)
            plateau_pct: 플래토 룰 임계값 (기본 0.9 = 90%).
                         IS 최고 Sharpe × plateau_pct 이상인 파라미터들 중 중간값 선택.
                         과최적화 방지: 극단 파라미터 배제.
            fold_decay: time-decay 계수. 0이면 동일 가중치(기존 동작).
                        양수면 w_i = exp(fold_decay * i) (i가 클수록 최근 fold).
                        weighted_oos_sharpe 계산에만 사용; PASS/FAIL은 avg_oos_sharpe 기준.
        """
        if fold_decay < 0:
            raise ValueError(
                f"fold_decay는 0 이상이어야 합니다 (음수면 초기 fold에 가중치, 비직관적). "
                f"입력값: {fold_decay}. 권장 범위: 0.0 (균일) ~ 1.0 (최근 강조)."
            )
        self.strategy_name = strategy_name
        self.strategy_factory = strategy_factory
        self.n_windows = n_windows
        self.is_ratio = is_ratio
        self.stability_lambda = stability_lambda
        self.plateau_pct = plateau_pct
        self.fold_decay = fold_decay
        self.use_regime_weights = use_regime_weights
        self._param_grid = param_grid or DEFAULT_GRIDS.get(strategy_name, {})
        self._engine = BacktestEngine()

    def run(self, df: pd.DataFrame) -> WalkForwardResult:
        """Walk-forward 최적화 실행."""
        # 파라미터 수 과적합 경고 (5개 초과 시)
        n_params = len(self._param_grid)
        if n_params > 5:
            logger.warning(
                "[%s] 파라미터 수 %d > 5 — 과적합 위험. 단순 전략(2~3 파라미터) 권장.",
                self.strategy_name, n_params,
            )

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

        window_results: List[WindowResult] = []
        param_oos_map: Dict[str, List[float]] = {}
        last_is_sharpe_dist: Dict[str, float] = {}
        # fold별 최적 파라미터 수집 (파라미터 안정성 CV 계산용)
        fold_params_history: List[dict] = []
        low_trades_folds = 0  # OOS trades < 30인 fold 수
        oos_vols: List[float] = []

        for i, (is_df, oos_df) in enumerate(windows):
            # IS 최적화 (Sharpe - λ*CV 목적함수 + 플래토 룰 적용)
            best_params, best_is_sharpe, is_sharpe_dist = self._optimize_in_sample(
                is_df, all_combinations,
                stability_lambda=self.stability_lambda,
                plateau_pct=self.plateau_pct,
            )

            # OOS 검증
            oos_strategy = self.strategy_factory(best_params)
            oos_result = self._engine.run(oos_strategy, oos_df)

            # OOS ATR (변동성) 계산 — regime 가중치에 사용
            if all(c in oos_df.columns for c in ["high", "low", "close"]):
                _atr = (oos_df["high"] - oos_df["low"]) / (oos_df["close"] + 1e-9)
                oos_vol = float(_atr.mean())
            else:
                oos_vol = 0.0
            oos_vols.append(oos_vol)

            # OOS 거래 수 통계적 신뢰도 경고 (학술 기준: fold당 30 trades)
            MIN_RELIABLE_OOS_TRADES = 30
            if oos_result.total_trades < MIN_RELIABLE_OOS_TRADES:
                low_trades_folds += 1
                logger.warning(
                    "[%s] Window %d: OOS trades=%d < %d — 통계적 신뢰도 낮음 (Sharpe 편향 가능성)",
                    self.strategy_name, i, oos_result.total_trades, MIN_RELIABLE_OOS_TRADES,
                )

            # WFE 계산 및 적용 (과최적화 필터)
            BacktestEngine.apply_wfe(oos_result, best_is_sharpe)
            ratio = oos_result.wfe

            wr = WindowResult(
                window_id=i,
                params=best_params,
                is_sharpe=best_is_sharpe,
                oos_sharpe=oos_result.sharpe_ratio,
                oos_passed=oos_result.passed,
                is_oos_ratio=ratio,
                oos_trades=oos_result.total_trades,
            )
            window_results.append(wr)
            fold_params_history.append(best_params)

            # 파라미터별 OOS 성과 집계
            key = str(sorted(best_params.items()))
            param_oos_map.setdefault(key, []).append(oos_result.sharpe_ratio)
            # 마지막 윈도우의 IS Sharpe 분포 저장 (IS 최적화 효과 측정용)
            last_is_sharpe_dist = is_sharpe_dist

            oos_vs_is_gap = oos_result.sharpe_ratio - best_is_sharpe
            logger.info(
                "Window %d: IS Sharpe=%.3f OOS Sharpe=%.3f ratio=%.2f gap=%.3f trades=%d params=%s",
                i, best_is_sharpe, oos_result.sharpe_ratio, ratio, oos_vs_is_gap,
                oos_result.total_trades, best_params,
            )

        # 최종 파라미터 선택: Sharpe Information Criterion (avg - 0.5 * std)
        # 평균만 최대화하면 고분산 파라미터를 선택할 수 있음 → 안정성 가중 선택
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

        import statistics as _stat

        def _sharpe_ic(sharpes: list) -> float:
            """Sharpe Information Criterion = avg - 0.5 * std (안정성 가중)."""
            avg = sum(sharpes) / len(sharpes)
            std = _stat.stdev(sharpes) if len(sharpes) > 1 else 0.0
            return avg - 0.5 * std

        best_key = max(param_oos_map, key=lambda k: _sharpe_ic(param_oos_map[k]))
        import ast
        best_final_params = dict(ast.literal_eval(best_key))  # str → dict 복원

        import statistics
        oos_sharpes = [wr.oos_sharpe for wr in window_results]
        avg_oos = sum(oos_sharpes) / len(oos_sharpes) if oos_sharpes else 0.0
        # Cycle 257: 저거래(< MIN_RELIABLE_OOS_TRADES) fold는 Sharpe 신뢰 불가 → std 계산 제외
        # 저거래 Sharpe는 분산이 극대화되어 OOS std를 인위적으로 상승시킴
        reliable_sharpes = [wr.oos_sharpe for wr in window_results
                            if wr.oos_trades >= 30]
        std_source = reliable_sharpes if len(reliable_sharpes) > 1 else oos_sharpes
        oos_std = statistics.stdev(std_source) if len(std_source) > 1 else 0.0
        overfit_count = sum(1 for wr in window_results if wr.is_overfit())

        # 파라미터 안정성 CV 계산 (fold 간 파라미터 CV = std / |mean|)
        param_stability_cv: Dict[str, float] = {}
        if len(fold_params_history) > 1:
            all_param_keys = set(k for p in fold_params_history for k in p)
            for pname in sorted(all_param_keys):
                values = [p[pname] for p in fold_params_history if pname in p]
                if len(values) < 2:
                    continue
                try:
                    vals_float = [float(v) for v in values]
                    mean_abs = abs(sum(vals_float) / len(vals_float))
                    std_val = _statistics.stdev(vals_float)
                    cv = (std_val / mean_abs) if mean_abs > 1e-9 else 0.0
                    param_stability_cv[pname] = round(cv, 4)
                    if cv > 0.5:
                        logger.warning(
                            "ParamStability [%s] param=%s CV=%.3f > 0.5 (불안정)",
                            self.strategy_name, pname, cv,
                        )
                except (TypeError, ValueError):
                    pass  # 비수치 파라미터는 스킵

        # weighted_oos_sharpe: time-decay 또는 regime 가중치 (선택)
        import math
        n_folds = len(oos_sharpes)
        if n_folds > 0 and self.use_regime_weights and oos_vols:
            mean_vol = sum(oos_vols) / len(oos_vols)
            # HIGH_VOL fold 다운웨이팅: fold_weight = 1/(1 + vol_ratio)
            raw_weights = [1.0 / (1.0 + v / (mean_vol + 1e-9)) for v in oos_vols]
            total_w = sum(raw_weights)
            weights = [w / total_w for w in raw_weights]
            weighted_oos_sharpe = sum(w * s for w, s in zip(weights, oos_sharpes))
        elif n_folds > 0 and self.fold_decay != 0.0:
            raw_weights = [math.exp(self.fold_decay * i) for i in range(n_folds)]
            total_w = sum(raw_weights)
            weights = [w / total_w for w in raw_weights]
            weighted_oos_sharpe = sum(w * s for w, s in zip(weights, oos_sharpes))
        else:
            weighted_oos_sharpe = avg_oos

        if self.use_regime_weights and oos_vols:
            logger.info(
                "[%s] regime_weights applied: vols=%s weights=%s",
                self.strategy_name,
                [round(v, 4) for v in oos_vols],
                [round(w, 4) for w in weights],
            )

        # WFE = avg OOS Sharpe / avg IS Sharpe
        all_is_sharpes = [wr.is_sharpe for wr in window_results]
        avg_is_sharpe = sum(all_is_sharpes) / len(all_is_sharpes) if all_is_sharpes else 0.0
        if abs(avg_is_sharpe) > 1e-9:
            wfe = round(avg_oos / avg_is_sharpe, 4)
        else:
            wfe = None  # IS Sharpe ≈ 0이면 WFE 정의 불가

        # fold_pass_rate: OOS Sharpe > 0인 fold 비율
        if window_results:
            positive_oos_folds = sum(1 for wr in window_results if wr.oos_sharpe > 0)
            fold_pass_rate = round(positive_oos_folds / len(window_results), 4)
        else:
            fold_pass_rate = None

        fail_reasons = []
        is_stable = True
        if oos_std > OOS_STD_MAX:
            fail_reasons.append(f"OOS Sharpe 불안정: std={oos_std:.3f} > {OOS_STD_MAX}")
            is_stable = False
        if avg_oos < 0.5:
            fail_reasons.append(f"OOS 평균 Sharpe 낮음: {avg_oos:.3f} < 0.5")
            is_stable = False
        # low_trades_folds > n_windows/2 → 통계적 신뢰도 부족 → UNSTABLE 판정
        if low_trades_folds > len(windows) / 2:
            fail_reasons.append(
                f"저거래 fold 과다: low_trades_folds={low_trades_folds}/{len(windows)} "
                f"> n_windows/2 (OOS Sharpe 신뢰 불가)"
            )
            is_stable = False
            logger.warning(
                "[%s] low_trades_folds=%d > n_windows/2=%.1f → UNSTABLE",
                self.strategy_name, low_trades_folds, len(windows) / 2,
            )
        # IS Sharpe 전체 음수 진단: GBM 합성 데이터나 전략 미작동 신호
        if all_is_sharpes:
            if avg_is_sharpe < -0.5:
                fail_reasons.append(
                    f"IS 전체 음수: avg IS Sharpe={avg_is_sharpe:.3f} — "
                    "전략 미작동 또는 합성 데이터(GBM)"
                )
                is_stable = False

        # plateau_score: 최적 파라미터 ±10% 이웃의 IS Sharpe 안정성
        plateau_score = self._compute_plateau_score(
            best_final_params, last_is_sharpe_dist, all_combinations,
        )
        if plateau_score is not None and plateau_score < 0.8:
            fail_reasons.append(
                f"plateau_score={plateau_score:.3f} < 0.8 (파라미터 민감도 높음)"
            )
            logger.warning(
                "[%s] plateau_score=%.3f — 최적 파라미터 주변 성과 불안정",
                self.strategy_name, plateau_score,
            )

        result = WalkForwardResult(
            strategy_name=self.strategy_name,
            best_params=best_final_params,
            windows=window_results,
            avg_oos_sharpe=round(avg_oos, 4),
            oos_sharpe_std=round(oos_std, 4),
            is_stable=is_stable,
            overfit_windows=overfit_count,
            fail_reasons=fail_reasons,
            last_is_sharpe_dist=last_is_sharpe_dist,
            param_stability_cv=param_stability_cv,
            weighted_oos_sharpe=round(weighted_oos_sharpe, 4),
            wfe=wfe,
            fold_pass_rate=fold_pass_rate,
            low_trades_folds=low_trades_folds,
            plateau_score=plateau_score,
        )
        logger.info(result.summary())
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _split_windows(self, df: pd.DataFrame) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
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
        self, is_df: pd.DataFrame, combinations: List[dict],
        stability_lambda: float = 0.5,
        plateau_pct: float = 0.9,
    ) -> Tuple[dict, float]:
        """그리드 서치로 IS 최적 파라미터 탐색.

        목적함수: Score = Sharpe - λ * CV (파라미터 내 변동성 패널티)
        λ=0이면 순수 Sharpe 최대화.

        플래토 룰 (plateau_pct):
          1. 모든 파라미터의 IS Sharpe 계산
          2. 최고 IS Sharpe * plateau_pct 이상인 파라미터들을 "플래토 집합"으로 정의
          3. 플래토 집합 내에서 각 파라미터의 중간값(median)에 가장 가까운 조합 선택
          → 극단적 파라미터 배제 → 과최적화 방지
        """
        best_params = combinations[0]
        best_score = -999.0
        param_is_sharpes: Dict[str, float] = {}
        # 그리드 탐색 중 파라미터값 누적 (CV 계산용)
        param_value_lists: Dict[str, list] = {}

        for params in combinations:
            try:
                strategy = self.strategy_factory(params)
                result = self._engine.run(strategy, is_df)
                sharpe = result.sharpe_ratio
                param_key = str(sorted(params.items()))
                param_is_sharpes[param_key] = round(sharpe, 4)
                # 파라미터별 값 수집 (CV 계산용)
                for k, v in params.items():
                    param_value_lists.setdefault(k, []).append(float(v))
            except Exception as e:
                logger.debug("IS backtest failed for %s: %s", params, e)

        # 파라미터 그리드 전체 CV 계산 (그리드 내 분산 측도)
        grid_cv: Dict[str, float] = {}
        for pname, vals in param_value_lists.items():
            if len(vals) < 2:
                grid_cv[pname] = 0.0
                continue
            mean_abs = abs(sum(vals) / len(vals))
            std_val = _statistics.stdev(vals)
            grid_cv[pname] = (std_val / mean_abs) if mean_abs > 1e-9 else 0.0

        # Score = Sharpe - λ * avg_CV 로 최적 파라미터 선택 (플래토 룰 적용 전)
        avg_grid_cv = sum(grid_cv.values()) / len(grid_cv) if grid_cv else 0.0

        for params in combinations:
            param_key = str(sorted(params.items()))
            if param_key not in param_is_sharpes:
                continue
            sharpe = param_is_sharpes[param_key]
            score = sharpe - stability_lambda * avg_grid_cv
            if score > best_score:
                best_score = score
                best_params = params

        best_sharpe = param_is_sharpes.get(str(sorted(best_params.items())), 0.0)

        # 플래토 룰: IS 최고 Sharpe * plateau_pct 이상인 파라미터들 중 중간값 선택
        if param_is_sharpes and plateau_pct > 0.0 and best_sharpe > 0:
            max_is_sharpe = max(param_is_sharpes.values())
            plateau_threshold = max_is_sharpe * plateau_pct
            plateau_candidates = [
                params for params in combinations
                if param_is_sharpes.get(str(sorted(params.items())), -999.0) >= plateau_threshold
            ]
            if len(plateau_candidates) > 1:
                # 각 파라미터의 중간값 계산
                param_medians: Dict[str, float] = {}
                all_param_keys = set(k for p in plateau_candidates for k in p)
                for pname in all_param_keys:
                    vals = sorted([float(p[pname]) for p in plateau_candidates if pname in p])
                    mid = len(vals) // 2
                    param_medians[pname] = vals[mid]
                # 플래토 집합 중 중간값에 가장 가까운 파라미터 조합 선택
                def median_distance(params: dict) -> float:
                    return sum(
                        abs(float(params.get(k, 0)) - param_medians.get(k, 0))
                        / (abs(param_medians.get(k, 1)) + 1e-9)
                        for k in param_medians
                    )
                plateau_best = min(plateau_candidates, key=median_distance)
                plateau_sharpe = param_is_sharpes.get(str(sorted(plateau_best.items())), best_sharpe)
                logger.info(
                    "Plateau rule: threshold=%.4f plateau_size=%d → %s (sharpe=%.4f vs best=%.4f)",
                    plateau_threshold, len(plateau_candidates), plateau_best, plateau_sharpe, best_sharpe,
                )
                best_params = plateau_best
                best_sharpe = plateau_sharpe

        # 파라미터별 IS Sharpe 분포 로깅 (IS 최적화 효과 측정용)
        if logger.isEnabledFor(logging.DEBUG):
            sorted_by_sharpe = sorted(param_is_sharpes.items(), key=lambda x: x[1], reverse=True)
            for rank, (key, sharpe) in enumerate(sorted_by_sharpe, 1):
                is_best = (key == str(sorted(best_params.items())))
                logger.debug(
                    "IS grid rank #%d: sharpe=%.4f params=%s%s",
                    rank, sharpe, key, " [BEST]" if is_best else "",
                )

        # IS Sharpe 분포 요약: min/max/spread를 INFO로 출력
        if param_is_sharpes:
            sharpe_vals = list(param_is_sharpes.values())
            logger.info(
                "IS grid summary: n_params=%d best=%.4f worst=%.4f spread=%.4f best_params=%s",
                len(sharpe_vals), max(sharpe_vals), min(sharpe_vals),
                max(sharpe_vals) - min(sharpe_vals), best_params,
            )

        return best_params, max(best_sharpe, 0.0), param_is_sharpes

    def _iter_param_combinations(self):
        """파라미터 그리드의 모든 조합 생성."""
        if not self._param_grid:
            yield {}
            return
        keys = list(self._param_grid.keys())
        values = list(self._param_grid.values())
        for combo in itertools.product(*values):
            yield dict(zip(keys, combo))

    @staticmethod
    def _compute_plateau_score(
        best_params: dict,
        is_sharpe_dist: Dict[str, float],
        all_combinations: List[dict],
        tolerance: float = 0.10,
    ) -> Optional[float]:
        """최적 파라미터 ±tolerance 범위 이웃의 IS Sharpe 안정성 점수 계산.

        plateau_score = mean(neighbor_sharpes) / best_sharpe
        1.0에 가까울수록 최적 파라미터 주변이 안정적 (평탄).
        0에 가까울수록 최적 파라미터가 날카로운 봉우리 (과최적화 위험).

        Args:
            best_params: 최종 선택된 파라미터 dict.
            is_sharpe_dist: {str(sorted(params.items())): is_sharpe} 분포.
            all_combinations: 전체 파라미터 조합 리스트.
            tolerance: 이웃 판단 기준 (기본 ±10%).

        Returns:
            plateau_score (0~1+) 또는 None (계산 불가 시).
        """
        if not best_params or not is_sharpe_dist:
            return None

        best_key = str(sorted(best_params.items()))
        best_sharpe = is_sharpe_dist.get(best_key)
        if best_sharpe is None or best_sharpe <= 0:
            return None

        # 이웃 파라미터 찾기: 각 파라미터 값이 best_params의 ±tolerance 이내인 조합
        neighbor_sharpes: list = []
        for combo in all_combinations:
            combo_key = str(sorted(combo.items()))
            if combo_key == best_key:
                continue  # 자기 자신 제외
            combo_sharpe = is_sharpe_dist.get(combo_key)
            if combo_sharpe is None:
                continue

            is_neighbor = True
            for pname, pval in best_params.items():
                cval = combo.get(pname)
                if cval is None:
                    is_neighbor = False
                    break
                try:
                    pval_f = float(pval)
                    cval_f = float(cval)
                except (TypeError, ValueError):
                    # 비수치 파라미터: 동일해야 이웃
                    if cval != pval:
                        is_neighbor = False
                        break
                    continue
                if abs(pval_f) < 1e-9:
                    # 0에 가까운 경우: 절대 차이로 비교
                    if abs(cval_f - pval_f) > tolerance:
                        is_neighbor = False
                        break
                else:
                    if abs(cval_f - pval_f) / abs(pval_f) > tolerance:
                        is_neighbor = False
                        break

            if is_neighbor:
                neighbor_sharpes.append(combo_sharpe)

        if not neighbor_sharpes:
            return None

        mean_neighbor = sum(neighbor_sharpes) / len(neighbor_sharpes)
        score = round(mean_neighbor / best_sharpe, 4)
        logger.info(
            "plateau_score: best_sharpe=%.4f neighbors=%d mean_neighbor=%.4f score=%.4f",
            best_sharpe, len(neighbor_sharpes), mean_neighbor, score,
        )
        return score


# ------------------------------------------------------------------
# 편의 팩토리 함수들
# ------------------------------------------------------------------

def optimize_ema_cross(df: pd.DataFrame, n_windows: int = 3,
                       plateau_pct: float = 0.9) -> WalkForwardResult:
    """EMA Cross 전략 파라미터 최적화."""
    from src.strategy.ema_cross import EmaCrossStrategy

    def factory(params: dict) -> BaseStrategy:
        return EmaCrossStrategy(
            fast_span=params.get("fast_span", 20),
            slow_span=params.get("slow_span", 50),
        )

    opt = WalkForwardOptimizer(
        strategy_name="ema_cross",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["ema_cross"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_donchian(df: pd.DataFrame, n_windows: int = 3,
                      plateau_pct: float = 0.9) -> WalkForwardResult:
    """Donchian Breakout 전략 파라미터 최적화."""
    from src.strategy.donchian_breakout import DonchianBreakoutStrategy

    def factory(params: dict) -> BaseStrategy:
        return DonchianBreakoutStrategy(
            channel_period=params.get("channel_period", 20),
        )

    opt = WalkForwardOptimizer(
        strategy_name="donchian_breakout",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["donchian_breakout"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_funding_rate(df: pd.DataFrame, n_windows: int = 3,
                          plateau_pct: float = 0.9) -> WalkForwardResult:
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
        plateau_pct=plateau_pct,
    )
    return opt.run(df)

def optimize_cmf(df: pd.DataFrame, n_windows: int = 3,
                 plateau_pct: float = 0.9) -> WalkForwardResult:
    """CMF 전략 파라미터 최적화."""
    from src.strategy.cmf import CMFStrategy

    def factory(params: dict) -> BaseStrategy:
        return CMFStrategy(
            period=params.get("period", 20),
            buy_thresh=params.get("buy_thresh", 0.08),
            sell_thresh=params.get("sell_thresh", -0.08),
        )

    opt = WalkForwardOptimizer(
        strategy_name="cmf",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["cmf"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_wick_reversal(df: pd.DataFrame, n_windows: int = 3,
                           plateau_pct: float = 0.9) -> WalkForwardResult:
    """Wick Reversal 전략 파라미터 최적화."""
    from src.strategy.wick_reversal import WickReversalStrategy

    def factory(params: dict) -> BaseStrategy:
        return WickReversalStrategy(
            min_wick_ratio=params.get("min_wick_ratio", 0.65),
            vol_mult=params.get("vol_mult", 0.8),
        )

    opt = WalkForwardOptimizer(
        strategy_name="wick_reversal",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["wick_reversal"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_elder_impulse(df: pd.DataFrame, n_windows: int = 3,
                           plateau_pct: float = 0.9) -> WalkForwardResult:
    """Elder Impulse 전략 파라미터 최적화."""
    from src.strategy.elder_impulse import ElderImpulseStrategy

    def factory(params: dict) -> BaseStrategy:
        return ElderImpulseStrategy(
            ema_span=params.get("ema_span", 13),
            min_volatility=params.get("min_volatility", 0.002),
        )

    opt = WalkForwardOptimizer(
        strategy_name="elder_impulse",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["elder_impulse"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_value_area(df: pd.DataFrame, n_windows: int = 3,
                        plateau_pct: float = 0.9) -> WalkForwardResult:
    """Value Area 전략 파라미터 최적화."""
    from src.strategy.value_area import ValueAreaStrategy

    def factory(params: dict) -> BaseStrategy:
        return ValueAreaStrategy(
            va_period=params.get("va_period", 20),
            va_mult=params.get("va_mult", 0.7),
        )

    opt = WalkForwardOptimizer(
        strategy_name="value_area",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["value_area"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_narrow_range(df: pd.DataFrame, n_windows: int = 3,
                          plateau_pct: float = 0.9) -> WalkForwardResult:
    """NarrowRange 전략 파라미터 최적화 (nr_lookback: 5/6/7)."""
    from src.strategy.narrow_range import NarrowRangeStrategy

    def factory(params: dict) -> BaseStrategy:
        return NarrowRangeStrategy(nr_lookback=params.get("nr_lookback", 7))

    opt = WalkForwardOptimizer(
        strategy_name="narrow_range",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["narrow_range"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_frama(df: pd.DataFrame, n_windows: int = 3,
                   plateau_pct: float = 0.9) -> WalkForwardResult:
    """FRAMA 전략 파라미터 최적화."""
    from src.strategy.frama import FRAMAStrategy

    def factory(params: dict) -> BaseStrategy:
        return FRAMAStrategy(
            period=params.get("period", 16),
            rsi_period=params.get("rsi_period", 14),
        )

    opt = WalkForwardOptimizer(
        strategy_name="frama",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["frama"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


# ------------------------------------------------------------------
# RollingOOSValidator — 5-Strategy Bundle Rolling OOS 검증
# ------------------------------------------------------------------


@dataclass
class OOSFoldResult:
    """단일 OOS fold 결과."""
    fold_id: int
    is_sharpe: float
    oos_sharpe: float
    is_mdd: float
    oos_mdd: float
    wfe: float
    oos_pf: float
    oos_trades: int
    passed: bool
    fail_reasons: List[str]


@dataclass
class BundleOOSResult:
    """5-Strategy Bundle OOS 검증 전체 결과."""
    strategy_name: str
    folds: List[OOSFoldResult]
    avg_wfe: float
    avg_oos_sharpe: float
    avg_oos_pf: float
    all_passed: bool
    fail_reasons: List[str]
    oos_sharpe_std: float = 0.0  # fold별 OOS Sharpe 표준편차
    dsr_pvalue: Optional[float] = None  # Deflated Sharpe Ratio p-value
    is_sharpe_significant: Optional[bool] = None  # DSR significance at α=0.05

    def summary(self) -> str:
        verdict = "PASS" if self.all_passed else "FAIL"
        lines = [
            f"BUNDLE_OOS: {self.strategy_name}",
            f"  folds: {len(self.folds)}",
            f"  avg_wfe: {self.avg_wfe:.3f}",
            f"  avg_oos_sharpe: {self.avg_oos_sharpe:.3f}",
            f"  oos_sharpe_std: {self.oos_sharpe_std:.3f}",
            f"  avg_oos_pf: {self.avg_oos_pf:.3f}",
            f"  verdict: {verdict}",
        ]
        if self.dsr_pvalue is not None:
            sig_tag = "SIGNIFICANT" if self.is_sharpe_significant else "NOT_SIGNIFICANT"
            lines.append(f"  dsr_pvalue: {self.dsr_pvalue:.4f} ({sig_tag})")
        if self.fail_reasons:
            lines.append(f"  fail_reasons: {self.fail_reasons}")
        return "\n".join(lines)

class RollingOOSValidator:
    """Rolling IS/OOS 검증기 (파라미터 최적화 없이 고정 전략 평가).

    Cycle 178 A: 6개월 IS / 2개월 OOS, 2개월씩 슬라이드.
    WFE ≥ 0.50, OOS Sharpe ≥ IS Sharpe × 0.60, OOS MDD ≤ IS MDD × 2.0.
    """

    OOS_SHARPE_STD_MAX = 1.5  # fold별 OOS Sharpe 표준편차 기본 한계

    def __init__(
        self,
        is_bars: int = 1080,       # 6개월 × 30일 × 6 (4h봉) = 1080
        oos_bars: int = 360,       # 2개월 × 30일 × 6 = 360
        slide_bars: int = 360,     # 2개월씩 슬라이드
        min_wfe: float = 0.5,
        sharpe_decay_max: float = 0.60,
        mdd_expand_max: float = 2.0,
        min_oos_trades: int = 3,   # 거래 수 미달 fold는 집계에서 제외 (신호 없음)
        max_oos_sharpe_std: Optional[float] = None,  # None=클래스 기본값(1.5) 사용
    ):
        self.is_bars = is_bars
        self.oos_bars = oos_bars
        self.slide_bars = slide_bars
        self.min_wfe = min_wfe
        self.sharpe_decay_max = sharpe_decay_max
        self.mdd_expand_max = mdd_expand_max
        self.min_oos_trades = min_oos_trades
        # 인스턴스별 기준 덮어쓰기 가능: 합성 데이터 환경에서는 완화, 실 데이터에서는 강화
        if max_oos_sharpe_std is not None:
            self._oos_sharpe_std_max = float(max_oos_sharpe_std)
        else:
            self._oos_sharpe_std_max = self.OOS_SHARPE_STD_MAX

    def validate(
        self,
        strategy: BaseStrategy,
        df: pd.DataFrame,
        fee_rate: float = 0.00055,
        slippage_pct: float = 0.0005,
    ) -> BundleOOSResult:
        """전략을 Rolling IS/OOS로 검증."""
        engine = BacktestEngine(fee_rate=fee_rate, slippage_pct=slippage_pct)
        min_required = self.is_bars + self.oos_bars

        if len(df) < min_required:
            return BundleOOSResult(
                strategy_name=strategy.name,
                folds=[],
                avg_wfe=0.0,
                avg_oos_sharpe=0.0,
                avg_oos_pf=0.0,
                oos_sharpe_std=0.0,
                all_passed=False,
                fail_reasons=[f"데이터 부족: {len(df)} < {min_required}"],
            )

        folds: List[OOSFoldResult] = []
        start = 0
        fold_id = 0

        while start + self.is_bars + self.oos_bars <= len(df):
            is_end = start + self.is_bars
            oos_end = is_end + self.oos_bars

            is_df = df.iloc[start:is_end]
            oos_df = df.iloc[is_end:oos_end]

            is_result = engine.run(strategy, is_df)
            oos_result = engine.run(strategy, oos_df)

            # WFE 계산: BacktestEngine.apply_wfe와 동일 로직
            if is_result.sharpe_ratio > 0:
                wfe = oos_result.sharpe_ratio / is_result.sharpe_ratio
            elif oos_result.sharpe_ratio > 0:
                # IS<0 + OOS>0: IS가 심각한 음수(-1.0 미만)이면 역방향 신호로 신뢰 불가
                if is_result.sharpe_ratio < -1.0:
                    wfe = 0.0  # 강한 역방향 — WFE 0으로 fold FAIL 유도
                else:
                    wfe = 1.0  # IS 소폭 음수, OOS 양수 → 과최적화 아님
            else:
                wfe = 0.0  # IS<=0 and OOS<=0 → 과최적화 가능

            fold_fails = []
            if wfe < self.min_wfe:
                fold_fails.append(f"WFE {wfe:.3f} < {self.min_wfe}")
            if oos_result.sharpe_ratio < is_result.sharpe_ratio * self.sharpe_decay_max:
                fold_fails.append(
                    f"OOS Sharpe {oos_result.sharpe_ratio:.2f} < "
                    f"IS×{self.sharpe_decay_max} ({is_result.sharpe_ratio * self.sharpe_decay_max:.2f})"
                )
            if is_result.max_drawdown > 0 and oos_result.max_drawdown > is_result.max_drawdown * self.mdd_expand_max:
                fold_fails.append(
                    f"OOS MDD {oos_result.max_drawdown:.1%} > "
                    f"IS×{self.mdd_expand_max} ({is_result.max_drawdown * self.mdd_expand_max:.1%})"
                )

            fold = OOSFoldResult(
                fold_id=fold_id,
                is_sharpe=round(is_result.sharpe_ratio, 3),
                oos_sharpe=round(oos_result.sharpe_ratio, 3),
                is_mdd=round(is_result.max_drawdown, 4),
                oos_mdd=round(oos_result.max_drawdown, 4),
                wfe=round(wfe, 4),
                oos_pf=round(oos_result.profit_factor, 3),
                oos_trades=oos_result.total_trades,
                passed=len(fold_fails) == 0,
                fail_reasons=fold_fails,
            )
            folds.append(fold)

            logger.info(
                "OOS Fold %d: IS_Sharpe=%.2f OOS_Sharpe=%.2f WFE=%.3f PF=%.2f %s",
                fold_id, is_result.sharpe_ratio, oos_result.sharpe_ratio,
                wfe, oos_result.profit_factor, "PASS" if fold.passed else "FAIL",
            )

            start += self.slide_bars
            fold_id += 1

        if not folds:
            return BundleOOSResult(
                strategy_name=strategy.name,
                folds=[],
                avg_wfe=0.0,
                avg_oos_sharpe=0.0,
                avg_oos_pf=0.0,
                oos_sharpe_std=0.0,
                all_passed=False,
                fail_reasons=["유효 fold 없음"],
            )

        import statistics as _stats

        # min_oos_trades 미달 fold는 신호 없음 — 집계에서 제외
        low_trade_fold_ids = [f.fold_id for f in folds if f.oos_trades < self.min_oos_trades]
        active_folds = [f for f in folds if f.oos_trades >= self.min_oos_trades]

        if not active_folds:
            return BundleOOSResult(
                strategy_name=strategy.name,
                folds=folds,
                avg_wfe=0.0,
                avg_oos_sharpe=0.0,
                avg_oos_pf=0.0,
                oos_sharpe_std=0.0,
                all_passed=False,
                fail_reasons=[
                    f"모든 fold 거래 없음 (min_oos_trades={self.min_oos_trades}): "
                    f"folds={low_trade_fold_ids}"
                ],
            )

        avg_wfe = sum(f.wfe for f in active_folds) / len(active_folds)
        avg_sharpe = sum(f.oos_sharpe for f in active_folds) / len(active_folds)
        avg_pf = sum(f.oos_pf for f in active_folds) / len(active_folds)
        oos_sharpes = [f.oos_sharpe for f in active_folds]
        oos_std = _stats.stdev(oos_sharpes) if len(oos_sharpes) > 1 else 0.0
        all_passed = all(f.passed for f in active_folds)

        # DSR 계산: OOS Sharpe 평균과 거래 수를 기반으로 통계적 유의성 판정
        dsr_pvalue = None
        is_sig = None
        num_strategies_tested = 5  # Bundle 내 5개 전략
        total_oos_trades = sum(f.oos_trades for f in active_folds)
        
        if total_oos_trades > 0 and avg_sharpe > 0:
            dsr_pvalue = deflated_sharpe_ratio(
                observed_sharpe=avg_sharpe,
                num_strategies_tested=num_strategies_tested,
                num_observations=total_oos_trades,
            )
            is_sig = dsr_pvalue < 0.05  # α=0.05
            logger.info(
                "[%s] DSR p-value=%.4f (observed_sharpe=%.3f, trades=%d, strategies=%d)",
                strategy.name, dsr_pvalue, avg_sharpe, total_oos_trades, num_strategies_tested,
            )

        # OOS Sharpe 표준편차 필터: fold별 변동이 너무 크면 FAIL
        bundle_fails = []
        low_trade_ratio = len(low_trade_fold_ids) / len(folds) if folds else 0.0
        if low_trade_fold_ids:
            bundle_fails.append(
                f"저거래 fold 제외 (trades<{self.min_oos_trades}): {low_trade_fold_ids}"
            )
        # 저거래 fold가 40% 초과 → 신호 생성 자체 부족 → FAIL
        if low_trade_ratio > 0.4:
            bundle_fails.append(
                f"저거래 fold 비율 {low_trade_ratio:.0%} > 40% (신호 부족)"
            )
            all_passed = False
        if not all_passed:
            failed_ids = [f.fold_id for f in active_folds if not f.passed]
            if failed_ids:
                bundle_fails.append(f"Failed folds: {failed_ids}")
        if oos_std > self._oos_sharpe_std_max:
            bundle_fails.append(
                f"OOS Sharpe std {oos_std:.3f} > {self._oos_sharpe_std_max} (불안정)"
            )
            all_passed = False

        result = BundleOOSResult(
            strategy_name=strategy.name,
            folds=folds,
            avg_wfe=round(avg_wfe, 4),
            avg_oos_sharpe=round(avg_sharpe, 3),
            avg_oos_pf=round(avg_pf, 3),
            oos_sharpe_std=round(oos_std, 4),
            all_passed=all_passed,
            fail_reasons=bundle_fails,
            dsr_pvalue=round(dsr_pvalue, 4) if dsr_pvalue is not None else None,
            is_sharpe_significant=is_sig,
        )
        logger.info(result.summary())
        return result


# ------------------------------------------------------------------
# WalkForwardValidator — rolling train/test window 검증
# ------------------------------------------------------------------

from dataclasses import dataclass as _dataclass
from typing import List as _List, Tuple
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
        fee_rate: float = 0.00055,   # Bybit taker 0.055%
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

            # [BUG FIX] IS/OOS 완전 분리: OOS 구간만 별도 실행해야 누수 없음.
            # 이전 코드는 train+test 전체를 엔진에 전달해 IS 성과가 결과에 혼입됨.
            is_df = df.iloc[start:test_start].reset_index(drop=True)
            oos_df = df.iloc[test_start:test_end].reset_index(drop=True)
            # IS 결과는 wfe 계산용, OOS 결과만 window_results에 기록
            is_result = engine.run(strategy, is_df)
            oos_result = engine.run(strategy, oos_df)

            window_results.append({
                "window_index": len(window_results),
                "start": start,
                "end": test_end - 1,
                "train_start": start,
                "train_end": test_start - 1,
                "test_start": test_start,
                "test_end": test_end - 1,
                "total_return": oos_result.total_return,
                "sharpe_ratio": oos_result.sharpe_ratio,
                "max_drawdown": oos_result.max_drawdown,
                "total_trades": oos_result.total_trades,
                "win_rate": oos_result.win_rate,
                "profit_factor": oos_result.profit_factor,
                "passed": oos_result.passed,
                "fail_reasons": list(oos_result.fail_reasons),
                "is_sharpe": is_result.sharpe_ratio,
                "wfe": round(oos_result.sharpe_ratio / is_result.sharpe_ratio, 4)
                       if is_result.sharpe_ratio > 0 else
                       (1.0 if oos_result.sharpe_ratio > 0 else 0.0),
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


# ------------------------------------------------------------------
# Deflated Sharpe Ratio (Harvey et al.)
# ------------------------------------------------------------------

import math as _math
from scipy.stats import norm as _norm

#: Euler-Mascheroni 상수
_EULER_MASCHERONI = 0.5772156649015328


def deflated_sharpe_ratio(
    observed_sharpe: float,
    num_strategies_tested: int,
    num_observations: int,
    skewness: float = 0.0,
    kurtosis: float = 3.0,
) -> float:
    """Harvey et al. Deflated Sharpe Ratio (DSR) p-value 계산.

    다중 전략 테스트 시 우연 Sharpe 보정. 반환값이 낮을수록 통계적으로 유의.

    Args:
        observed_sharpe: 관찰된 최대 Sharpe Ratio (SR_max).
        num_strategies_tested: 테스트한 전략 수 (N). 보정 강도 결정.
        num_observations: 관측 수 T (거래 수 또는 봉 수).
        skewness: 수익률 왜도 (γ₃). 기본값 0 (정규분포).
        kurtosis: 수익률 첨도 (γ₄). 기본값 3 (정규분포).

    Returns:
        DSR p-value (0~1). p < 0.05이면 유의한 Sharpe.

    References:
        Harvey, C.R., Liu, Y. & Zhu, H. (2016). … and the Cross-Section of Expected Returns.
        Review of Financial Studies 29(1), 5–68.
    """
    N = max(num_strategies_tested, 1)
    T = max(num_observations, 2)

    # 기대 최대 Sharpe (SR_0): multiple testing 보정
    # E[max SR] ≈ (1-γ)*Z_{1-1/N} + γ*Z_{1-1/(N*e)}
    gamma = _EULER_MASCHERONI
    e = _math.e

    # N=1이면 보정 없음: SR_0 = 0
    if N == 1:
        sr0 = 0.0
    else:
        z1 = _norm.ppf(1.0 - 1.0 / N)
        z2 = _norm.ppf(1.0 - 1.0 / (N * e))
        sr0 = (1.0 - gamma) * z1 + gamma * z2

    # 분모: 비정규성 보정 항
    # √(1 - γ₃*SR_max + (γ₄-1)/4 * SR_max²)
    sr = observed_sharpe
    denom_sq = 1.0 - skewness * sr + (kurtosis - 1.0) / 4.0 * sr ** 2
    if denom_sq <= 0:
        denom_sq = 1e-9  # 수치 안정성
    denom = _math.sqrt(denom_sq)

    # DSR 통계량: z = (SR_max*√T - √(T-1)*SR_0) / denom
    z_stat = (sr * _math.sqrt(T) - _math.sqrt(T - 1) * sr0) / denom

    # p-value = 1 - Φ(z_stat)
    p_value = float(1.0 - _norm.cdf(z_stat))
    return p_value


def is_sharpe_significant(
    observed_sharpe: float,
    num_observations: int,
    num_strategies_tested: int = 355,
    skewness: float = 0.0,
    kurtosis: float = 3.0,
    alpha: float = 0.05,
) -> bool:
    """DSR p-value < alpha 이면 True (통계적으로 유의한 Sharpe).

    Args:
        observed_sharpe: 관찰된 Sharpe Ratio.
        num_observations: 관측 수 T.
        num_strategies_tested: 테스트한 전략 수 (기본값 355).
        skewness: 수익률 왜도.
        kurtosis: 수익률 첨도.
        alpha: 유의수준 (기본 0.05).

    Returns:
        True이면 유의한 Sharpe (과도한 다중 테스트 후에도 통계적으로 의미 있음).
    """
    p = deflated_sharpe_ratio(
        observed_sharpe=observed_sharpe,
        num_strategies_tested=num_strategies_tested,
        num_observations=num_observations,
        skewness=skewness,
        kurtosis=kurtosis,
    )
    return p < alpha
