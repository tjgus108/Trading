"""
Fractional Kelly Criterion 기반 포지션 사이징.

Kelly Fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
Half-Kelly = Kelly * 0.5  (crypto 변동성 대응)

ATR 조정:
  ATR이 높을수록 사이즈 축소:
  atr_factor = target_atr / current_atr (capped at 1.0)
  final_size = kelly_size * atr_factor

Risk-Constrained Kelly (max_drawdown 제약):
  max_dd_constrained = max_drawdown / (avg_loss * leverage)
  final_fraction = min(half_kelly, max_dd_constrained)
"""

from __future__ import annotations

import numpy as np
from typing import Optional, List


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
        max_drawdown: Optional[float] = None,
        leverage: float = 1.0,
    ) -> None:
        """
        Args:
            fraction: Kelly 분수 배율 (0.5 = Half-Kelly)
            max_fraction: 자본 대비 최대 포지션 비율
            min_fraction: 자본 대비 최소 포지션 비율
            max_drawdown: 허용 최대 낙폭 (e.g. 0.05 = 5%). None이면 DD 제약 미적용.
            leverage: 레버리지 배수 (기본 1.0 = 현물)
        """
        self.fraction = fraction
        self.max_fraction = max_fraction
        self.min_fraction = min_fraction
        self.max_drawdown = max_drawdown
        self.leverage = leverage

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

        # NaN / inf 방어 (클리핑 전에 수행: np.clip(inf)=1.0 통과 방지)
        if not np.isfinite(win_rate) or not np.isfinite(avg_win) or not np.isfinite(avg_loss):
            return 0.0
        if capital <= 0 or price <= 0:
            return 0.0

        # win_rate 범위 클리핑: [0, 1] 바깥 값 방어
        win_rate = float(np.clip(win_rate, 0.0, 1.0))

        # Full Kelly
        kelly_f = (win_rate * avg_win - (1.0 - win_rate) * avg_loss) / avg_win

        if kelly_f <= 0:
            return 0.0

        # Fractional Kelly
        fractional_f = kelly_f * self.fraction

        # Risk-Constrained Kelly: max_drawdown 제약
        if self.max_drawdown is not None and avg_loss > 0 and self.leverage > 0:
            max_dd_constrained = self.max_drawdown / (avg_loss * self.leverage)
            fractional_f = min(fractional_f, max_dd_constrained)

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

    # 최소 거래 수: 이보다 적으면 Kelly 추정이 통계적으로 불안정
    MIN_TRADES_FOR_KELLY: int = 10

    @classmethod
    def from_trade_history(
        cls,
        trades: List[dict],
        capital: float,
        price: float,
        atr: Optional[float] = None,
        target_atr: Optional[float] = None,
        fraction: float = 0.5,
        max_fraction: float = 0.10,
        min_fraction: float = 0.001,
        max_drawdown: Optional[float] = None,
        leverage: float = 1.0,
        min_trades: Optional[int] = None,
    ) -> float:
        """거래 기록으로부터 win_rate / avg_win / avg_loss 자동 계산 후 compute() 호출.

        소표본 방어: 거래 수가 min_trades(기본 MIN_TRADES_FOR_KELLY=10) 미만이면
        win_rate를 50%로 축소(Bayesian shrinkage)하여 과적합 방지.
        거래 기록이 비어있거나 모든 pnl이 0이면 0.0 반환.

        Args:
            trades: [{"pnl": float}, ...] 형태의 거래 기록
            capital: 총 자본
            price: 현재 가격
            atr: 현재 ATR (선택)
            target_atr: 기준 ATR (선택)
            fraction: Kelly 분수 배율
            max_fraction: 최대 자본 비율
            min_fraction: 최소 자본 비율
            max_drawdown: 허용 최대 낙폭 (선택)
            leverage: 레버리지 배수 (기본 1.0)
            min_trades: Kelly 추정에 필요한 최소 거래 수 (None이면 클래스 기본값 사용)

        Returns:
            포지션 사이즈 (수량)
        """
        if not trades:
            return 0.0

        pnls = np.array([t["pnl"] for t in trades], dtype=float)

        # NaN 제거
        pnls = pnls[np.isfinite(pnls)]
        if len(pnls) == 0:
            return 0.0

        wins = pnls[pnls > 0]
        losses = pnls[pnls < 0]

        # 모든 거래가 break-even(pnl=0)이면 edge 없음
        if len(wins) == 0 and len(losses) == 0:
            return 0.0

        raw_win_rate = len(wins) / len(pnls)
        avg_win = float(wins.mean()) if len(wins) > 0 else 0.0
        avg_loss = float(abs(losses.mean())) if len(losses) > 0 else 0.0

        # 소표본 Bayesian shrinkage: 거래 수가 적으면 win_rate를 50%로 축소
        # shrink_factor = n / (n + min_trades): n이 많을수록 1에 수렴
        threshold = min_trades if min_trades is not None else cls.MIN_TRADES_FOR_KELLY
        n = len(pnls)
        if n < threshold:
            shrink_factor = n / (n + threshold)
            win_rate = shrink_factor * raw_win_rate + (1.0 - shrink_factor) * 0.5
        else:
            win_rate = raw_win_rate

        sizer = cls(
            fraction=fraction,
            max_fraction=max_fraction,
            min_fraction=min_fraction,
            max_drawdown=max_drawdown,
            leverage=leverage,
        )
        return sizer.compute(win_rate, avg_win, avg_loss, capital, price, atr, target_atr)
