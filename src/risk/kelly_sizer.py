"""
Fractional Kelly Criterion 기반 포지션 사이징.

Kelly Fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
Half-Kelly = Kelly * 0.5  (crypto 변동성 대응)

ATR 조정:
  ATR이 높을수록 사이즈 축소:
  atr_factor = target_atr / current_atr (capped at 1.0)
  final_size = kelly_size * atr_factor
"""

from __future__ import annotations

import numpy as np
from typing import Optional


class KellySizer:
    """Fractional Kelly Criterion 포지션 사이저."""

    fraction: float = 0.5       # Half-Kelly 기본값
    max_fraction: float = 0.10  # 자본의 최대 10%
    min_fraction: float = 0.001 # 최소 0.1%

    def __init__(
        self,
        fraction: float = 0.5,
        max_fraction: float = 0.10,
        min_fraction: float = 0.001,
    ) -> None:
        self.fraction = fraction
        self.max_fraction = max_fraction
        self.min_fraction = min_fraction

    def compute(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        capital: float,
        price: float,
        atr: Optional[float] = None,
        target_atr: Optional[float] = None,
    ) -> float:
        """포지션 사이즈 (단위 수량) 반환.

        Args:
            win_rate: 승률 [0, 1]
            avg_win: 평균 수익 (소수, e.g. 0.02 = 2%)
            avg_loss: 평균 손실 (소수, e.g. 0.01 = 1%, 양수로 전달)
            capital: 총 자본 (통화)
            price: 현재 가격
            atr: 현재 ATR (선택)
            target_atr: 기준 ATR (선택, atr과 함께 사용)

        Returns:
            포지션 사이즈 (수량)
        """
        if avg_win <= 0:
            return 0.0

        # Full Kelly
        kelly_f = (win_rate * avg_win - (1.0 - win_rate) * avg_loss) / avg_win

        if kelly_f <= 0:
            return 0.0

        # Fractional Kelly
        fractional_f = kelly_f * self.fraction

        # 상·하한 클리핑
        fractional_f = float(np.clip(fractional_f, self.min_fraction, self.max_fraction))

        # ATR 조정
        atr_factor = 1.0
        if atr is not None and target_atr is not None and atr > 0:
            atr_factor = min(target_atr / atr, 1.0)

        # 자본 대비 포지션 금액 → 수량
        position_capital = capital * fractional_f * atr_factor
        qty = position_capital / price
        return qty

    @classmethod
    def from_trade_history(
        cls,
        trades: list[dict],
        capital: float,
        price: float,
        atr: Optional[float] = None,
        target_atr: Optional[float] = None,
        fraction: float = 0.5,
        max_fraction: float = 0.10,
        min_fraction: float = 0.001,
    ) -> float:
        """거래 기록으로부터 win_rate / avg_win / avg_loss 자동 계산 후 compute() 호출.

        Args:
            trades: [{"pnl": float}, ...] 형태의 거래 기록
            capital: 총 자본
            price: 현재 가격
            atr: 현재 ATR (선택)
            target_atr: 기준 ATR (선택)
            fraction: Kelly 분수 배율
            max_fraction: 최대 자본 비율
            min_fraction: 최소 자본 비율

        Returns:
            포지션 사이즈 (수량)
        """
        if not trades:
            return 0.0

        pnls = np.array([t["pnl"] for t in trades], dtype=float)
        wins = pnls[pnls > 0]
        losses = pnls[pnls < 0]

        win_rate = len(wins) / len(pnls)
        avg_win = float(wins.mean()) if len(wins) > 0 else 0.0
        avg_loss = float(abs(losses.mean())) if len(losses) > 0 else 0.0

        sizer = cls(fraction=fraction, max_fraction=max_fraction, min_fraction=min_fraction)
        return sizer.compute(win_rate, avg_win, avg_loss, capital, price, atr, target_atr)
