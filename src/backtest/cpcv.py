"""
Combinatorially Purged Cross-Validation (CPCV).

WalkForwardOptimizer가 순차 윈도우 기반이라면, CPCV는 C(N,k) 조합을 통해
모든 가능한 train/test 분할을 탐색하여 Probability of Backtest Overfitting(PBO)을 측정한다.

알고리즘:
  1. T개 관측값을 N개(기본=6) 순차적 비중첩 그룹으로 분할
  2. k개(기본=2) 그룹을 테스트셋으로 선택하는 C(N,k) 조합 생성
  3. 각 조합: 나머지 N-k 그룹 = 훈련셋
  4. Purging: 훈련셋에서 테스트셋 인접 구간(embargo) 제거
  5. 각 경로에서 OOS Sharpe 계산
  6. PBO = P(OOS Sharpe < 0)

참고: Lopez de Prado, "Advances in Financial Machine Learning", Ch.12
"""

import itertools
import logging
import math
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.backtest.engine import BacktestEngine
from src.strategy.base import BaseStrategy

logger = logging.getLogger(__name__)


@dataclass
class CPCVResult:
    """CPCV 실행 결과."""
    paths: List[float]          # 각 경로의 OOS Sharpe
    pbo: float                  # Probability of Backtest Overfitting = P(OOS Sharpe < 0)
    n_groups: int               # 그룹 수 N
    k: int                      # 테스트 그룹 수 k
    mean_sharpe: float          # OOS Sharpe 평균
    std_sharpe: float           # OOS Sharpe 표준편차
    n_paths: int = 0            # 총 경로 수 C(N,k)
    embargo_pct: float = 0.01   # embargo 비율

    def summary(self) -> str:
        verdict = "LOW_OVERFIT" if self.pbo < 0.5 else "HIGH_OVERFIT"
        lines = [
            f"CPCV_RESULT:",
            f"  n_groups={self.n_groups}, k={self.k}, paths={self.n_paths}",
            f"  pbo: {self.pbo:.3f} ({verdict})",
            f"  mean_sharpe: {self.mean_sharpe:.3f}",
            f"  std_sharpe: {self.std_sharpe:.3f}",
            f"  embargo_pct: {self.embargo_pct}",
        ]
        return "\n".join(lines)


def run_cpcv(
    strategy_factory: Callable[[dict], BaseStrategy],
    df: pd.DataFrame,
    n_groups: int = 6,
    k: int = 2,
    embargo_pct: float = 0.01,
    params: Optional[dict] = None,
    fee_rate: float = 0.00055,
    slippage_pct: float = 0.0005,
) -> CPCVResult:
    """Combinatorially Purged Cross-Validation 실행.

    Args:
        strategy_factory: params dict -> BaseStrategy 인스턴스 생성 함수
        df: OHLCV + 지표 포함 DataFrame
        n_groups: 그룹 수 N (기본 6)
        k: 테스트 그룹 수 (기본 2)
        embargo_pct: embargo 비율 (테스트셋 길이 * embargo_pct 봉수)
        params: 전략 파라미터 (None이면 빈 dict)
        fee_rate: 수수료율
        slippage_pct: 슬리피지 비율

    Returns:
        CPCVResult
    """
    if params is None:
        params = {}

    n = len(df)
    min_required = n_groups * 50  # 그룹당 최소 50봉
    if n < min_required:
        logger.warning("CPCV: 데이터 부족 %d < %d (n_groups=%d * 50)", n, min_required, n_groups)
        return CPCVResult(
            paths=[], pbo=1.0, n_groups=n_groups, k=k,
            mean_sharpe=0.0, std_sharpe=0.0, n_paths=0,
            embargo_pct=embargo_pct,
        )

    if k >= n_groups:
        raise ValueError(f"k({k}) >= n_groups({n_groups}): 테스트셋이 전체가 됨")

    # 1. 그룹 분할: N개의 순차적 비중첩 그룹
    group_size = n // n_groups
    groups: List[Tuple[int, int]] = []
    for i in range(n_groups):
        start = i * group_size
        end = start + group_size if i < n_groups - 1 else n
        groups.append((start, end))

    # 2. C(N, k) 조합 생성
    test_combos = list(itertools.combinations(range(n_groups), k))
    n_paths = len(test_combos)
    logger.info(
        "CPCV: N=%d, k=%d, C(N,k)=%d paths, embargo=%.1f%%",
        n_groups, k, n_paths, embargo_pct * 100,
    )

    engine = BacktestEngine(fee_rate=fee_rate, slippage_pct=slippage_pct)
    path_sharpes: List[float] = []

    for combo_idx, test_group_ids in enumerate(test_combos):
        train_group_ids = [g for g in range(n_groups) if g not in test_group_ids]

        # 테스트셋 구간 결정
        test_ranges = [groups[g] for g in sorted(test_group_ids)]

        # 3. Purging: 훈련셋에서 테스트셋 인접 embargo 구간 제거
        train_df = _build_purged_train(df, groups, train_group_ids, test_group_ids, embargo_pct)

        # 4. 테스트셋 구성 (여러 그룹일 수 있으므로 concat)
        test_dfs = [df.iloc[s:e].reset_index(drop=True) for s, e in test_ranges]
        test_df = pd.concat(test_dfs, ignore_index=True) if test_dfs else pd.DataFrame()

        if len(train_df) < 100 or len(test_df) < 30:
            logger.debug(
                "CPCV path %d/%d: 데이터 부족 (train=%d, test=%d), skip",
                combo_idx + 1, n_paths, len(train_df), len(test_df),
            )
            continue

        # 5. 전략 생성 및 OOS 백테스트
        try:
            strategy = strategy_factory(params)
            oos_result = engine.run(strategy, test_df)
            path_sharpes.append(oos_result.sharpe_ratio)
            logger.debug(
                "CPCV path %d/%d: test_groups=%s OOS_Sharpe=%.3f trades=%d",
                combo_idx + 1, n_paths, test_group_ids,
                oos_result.sharpe_ratio, oos_result.total_trades,
            )
        except Exception as e:
            logger.warning("CPCV path %d/%d failed: %s", combo_idx + 1, n_paths, e)

    # 6. PBO 계산
    if not path_sharpes:
        return CPCVResult(
            paths=[], pbo=1.0, n_groups=n_groups, k=k,
            mean_sharpe=0.0, std_sharpe=0.0, n_paths=n_paths,
            embargo_pct=embargo_pct,
        )

    negative_count = sum(1 for s in path_sharpes if s < 0)
    pbo = negative_count / len(path_sharpes)
    mean_s = float(np.mean(path_sharpes))
    std_s = float(np.std(path_sharpes, ddof=1)) if len(path_sharpes) > 1 else 0.0

    result = CPCVResult(
        paths=[round(s, 4) for s in path_sharpes],
        pbo=round(pbo, 4),
        n_groups=n_groups,
        k=k,
        mean_sharpe=round(mean_s, 4),
        std_sharpe=round(std_s, 4),
        n_paths=n_paths,
        embargo_pct=embargo_pct,
    )
    logger.info(result.summary())
    return result


def _build_purged_train(
    df: pd.DataFrame,
    groups: List[Tuple[int, int]],
    train_group_ids: List[int],
    test_group_ids: tuple,
    embargo_pct: float,
) -> pd.DataFrame:
    """Purging 적용된 훈련셋 구성.

    테스트 그룹 인접 구간(embargo)을 훈련셋에서 제거하여
    정보 누수를 방지한다.

    Args:
        df: 전체 DataFrame
        groups: (start, end) 리스트
        train_group_ids: 훈련용 그룹 인덱스
        test_group_ids: 테스트용 그룹 인덱스
        embargo_pct: embargo 비율

    Returns:
        purging 적용된 훈련셋 DataFrame
    """
    # 테스트 구간의 시작/끝 인덱스 수집
    test_starts = [groups[g][0] for g in sorted(test_group_ids)]
    test_ends = [groups[g][1] for g in sorted(test_group_ids)]

    # embargo 봉 수: 테스트 그룹 평균 크기 * embargo_pct
    avg_test_len = np.mean([groups[g][1] - groups[g][0] for g in test_group_ids])
    embargo_bars = max(1, int(avg_test_len * embargo_pct))

    # 제외할 인덱스 범위 수집 (테스트 구간 앞뒤 embargo)
    exclude_ranges: List[Tuple[int, int]] = []
    for ts, te in zip(test_starts, test_ends):
        # 테스트 직전 embargo
        embargo_start = max(0, ts - embargo_bars)
        # 테스트 직후 embargo
        embargo_end = min(len(df), te + embargo_bars)
        exclude_ranges.append((embargo_start, embargo_end))

    # 훈련 그룹에서 제외 범위 적용
    train_parts: List[pd.DataFrame] = []
    for gid in sorted(train_group_ids):
        g_start, g_end = groups[gid]
        # 이 그룹 내에서 제외되지 않는 구간만 추출
        valid_start = g_start
        for ex_start, ex_end in exclude_ranges:
            # 그룹과 제외 범위가 겹치면 해당 부분 제거
            if ex_start < g_end and ex_end > g_start:
                # 겹치는 구간 계산
                overlap_start = max(g_start, ex_start)
                overlap_end = min(g_end, ex_end)
                # 겹침 앞부분 추가
                if valid_start < overlap_start:
                    train_parts.append(df.iloc[valid_start:overlap_start])
                valid_start = max(valid_start, overlap_end)
        # 남은 부분 추가
        if valid_start < g_end:
            train_parts.append(df.iloc[valid_start:g_end])

    if not train_parts:
        return pd.DataFrame()

    return pd.concat(train_parts, ignore_index=True)
