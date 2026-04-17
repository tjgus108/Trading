"""
포지션 사이징 유틸리티.
KellySizer + VolTargeting 통합 인터페이스.

변동성 타겟팅 워크플로우:
  1. Kelly Criterion으로 기본 포지션 크기 결정
  2. VolTargeting으로 실현 변동성 대비 동적 조정
  3. DrawdownMonitor의 size_multiplier 반영 (선택사항)
"""

from __future__ import annotations

import logging
import pandas as pd
from typing import Optional

from .kelly_sizer import KellySizer
from .vol_targeting import VolTargeting

logger = logging.getLogger(__name__)


def kelly_position_size(
    win_rate: float,
    win_loss_ratio: float,
    capital: float,
    kelly_fraction: float = 0.25,
) -> float:
    """Kelly Criterion 기반 포지션 금액(USD) 반환.

    Args:
        win_rate: 승률 [0, 1]
        win_loss_ratio: 평균수익 / 평균손실 비율 (e.g. 2.0 = 수익이 손실의 2배)
        capital: 총 자본 (USD)
        kelly_fraction: Full Kelly 대비 비율 (기본 0.25 = 25%, 과대베팅 방지)

    Returns:
        포지션에 투입할 금액 (USD). 음수/무효 시 0.0.
    """
    if win_rate <= 0 or win_loss_ratio <= 0 or capital <= 0:
        return 0.0

    avg_win = win_loss_ratio          # 손실 1 기준 수익
    avg_loss = 1.0                    # 손실 단위를 1로 정규화

    # Full Kelly: (p * b - q) / b  where b=win_loss_ratio, p=win_rate, q=1-p
    kelly_f = (win_rate * avg_win - (1.0 - win_rate) * avg_loss) / avg_win

    if kelly_f <= 0:
        return 0.0

    fractional_f = kelly_f * kelly_fraction

    # 안전 상한: 자본의 25% 초과 금지
    fractional_f = min(fractional_f, 0.25)

    return capital * fractional_f


def kelly_position_size_from_sizer(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    capital: float,
    price: float,
    kelly_fraction: float = 0.25,
    max_fraction: float = 0.10,
) -> float:
    """KellySizer를 직접 사용하는 상세 인터페이스 (수량 반환).

    Args:
        win_rate: 승률 [0, 1]
        avg_win: 평균 수익 (소수, e.g. 0.02)
        avg_loss: 평균 손실 (소수, 양수로 전달)
        capital: 총 자본 (USD)
        price: 현재 가격
        kelly_fraction: Kelly 배율 (기본 0.25)
        max_fraction: 최대 자본 비율 (기본 10%)

    Returns:
        포지션 수량 (units)
    """
    sizer = KellySizer(fraction=kelly_fraction, max_fraction=max_fraction)
    return sizer.compute(win_rate, avg_win, avg_loss, capital, price)


def volatility_targeted_position_size(
    base_size: float,
    df: pd.DataFrame,
    target_vol: float = 0.20,
    window: int = 20,
    max_scalar: float = 2.0,
    min_scalar: float = 0.1,
) -> float:
    """변동성 타겟팅으로 포지션 사이즈 동적 조정.

    목표 변동성(target_vol) 대비 현재 실현 변동성 비율로 position_size를 자동 조절한다.

    공식:
      vol_scalar = target_vol / realized_vol
      adjusted_size = base_size * min(vol_scalar, max_scalar)

    realized_vol: 최근 window 개 캔들의 수익률 표준편차 * sqrt(annualization)
    target_vol: 연환산 목표 변동성 (e.g. 0.20 = 20% p.a.)

    Args:
        base_size: Kelly 또는 고정 포지션 크기 (units)
        df: 캔들 DataFrame (반드시 "close" 컬럼 포함)
        target_vol: 연환산 목표 변동성 (기본 0.20)
        window: 실현 변동성 계산 윈도우 (기본 20 캔들)
        max_scalar: 최대 스케일 배수, 레버리지 한계 (기본 2.0)
        min_scalar: 최소 스케일 배수 (기본 0.1)

    Returns:
        변동성 조정된 포지션 사이즈 (units)

    Example:
        >>> df = pd.DataFrame({"close": [100, 101, 102, ...]})
        >>> kelly_size = 0.5
        >>> adjusted = volatility_targeted_position_size(kelly_size, df, target_vol=0.20)
        >>> # 변동성 낮음 → adjusted > kelly_size
        >>> # 변동성 높음 → adjusted < kelly_size
    """
    if base_size <= 0:
        logger.warning("volatility_targeted_position_size: base_size <= 0, returning 0.0")
        return 0.0

    vt = VolTargeting(
        target_vol=target_vol,
        window=window,
        max_scalar=max_scalar,
        min_scalar=min_scalar,
    )
    return vt.adjust(base_size=base_size, df=df)


def kelly_with_vol_targeting(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    capital: float,
    price: float,
    df: Optional[pd.DataFrame] = None,
    kelly_fraction: float = 0.25,
    max_fraction: float = 0.10,
    target_vol: float = 0.20,
    size_multiplier: float = 1.0,
) -> float:
    """Kelly Criterion + Volatility Targeting 통합 포지션 사이징.

    워크플로우:
      1. KellySizer로 기본 포지션 크기 결정
      2. VolTargeting로 변동성 기반 동적 조정 (df 제공 시)
      3. DrawdownMonitor의 size_multiplier 적용

    Args:
        win_rate: 승률 [0, 1]
        avg_win: 평균 수익률 (소수)
        avg_loss: 평균 손실률 (소수, 양수)
        capital: 총 자본 (USD)
        price: 현재 가격
        df: 캔들 DataFrame. None이면 VolTargeting 스킵
        kelly_fraction: Kelly 배율 (기본 0.25)
        max_fraction: 최대 자본 비율 (기본 10%)
        target_vol: 연환산 목표 변동성 (기본 20%)
        size_multiplier: DrawdownMonitor에서 받은 배수 (기본 1.0 = 정상)

    Returns:
        최종 포지션 사이즈 (units)

    Example:
        >>> size = kelly_with_vol_targeting(
        ...     win_rate=0.55,
        ...     avg_win=0.02,
        ...     avg_loss=0.01,
        ...     capital=100_000,
        ...     price=50_000,
        ...     df=df,  # 24시간 캔들
        ...     size_multiplier=0.5,  # 연속 손실로 인한 50% 축소
        ... )
    """
    # Step 1: Kelly Criterion
    kelly_size = kelly_position_size_from_sizer(
        win_rate=win_rate,
        avg_win=avg_win,
        avg_loss=avg_loss,
        capital=capital,
        price=price,
        kelly_fraction=kelly_fraction,
        max_fraction=max_fraction,
    )

    if kelly_size <= 0:
        logger.debug("kelly_with_vol_targeting: kelly_size <= 0, returning 0.0")
        return 0.0

    # Step 2: Volatility Targeting (df 제공 시)
    if df is not None and len(df) > 1:
        adjusted_size = volatility_targeted_position_size(
            base_size=kelly_size,
            df=df,
            target_vol=target_vol,
        )
    else:
        adjusted_size = kelly_size
        if df is None:
            logger.debug("kelly_with_vol_targeting: df is None, skipping VolTargeting")

    # Step 3: DrawdownMonitor multiplier (쿨다운/연속손실 반영)
    final_size = adjusted_size * size_multiplier

    logger.debug(
        "kelly_with_vol_targeting: kelly=%.6f vol_adj=%.6f size_mult=%.2f → final=%.6f",
        kelly_size, adjusted_size, size_multiplier, final_size,
    )

    return final_size
