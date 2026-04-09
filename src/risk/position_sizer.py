"""
포지션 사이징 유틸리티.
KellySizer를 래핑하는 단순 함수 인터페이스를 제공한다.
"""

from __future__ import annotations

from .kelly_sizer import KellySizer


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
