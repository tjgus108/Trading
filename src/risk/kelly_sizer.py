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
        kelly_cap: float = 0.25,
        regime_smooth_alpha: float = 0.0,
    ) -> None:
        """
        Args:
            fraction: Kelly 분수 배율 (0.5 = Half-Kelly)
            max_fraction: 자본 대비 최대 포지션 비율
            min_fraction: 자본 대비 최소 포지션 비율
            max_drawdown: 허용 최대 낙폭 (e.g. 0.05 = 5%). None이면 DD 제약 미적용.
            leverage: 레버리지 배수 (기본 1.0 = 현물)
            kelly_cap: Full Kelly fraction 상한 (기본 0.25 = Quarter-Kelly cap).
                       kelly_f * fraction 결과가 이 값을 초과하지 않도록 제한.
                       풀 Kelly → 파멸 경로 방지 핵심 안전장치.
            regime_smooth_alpha: 레짐 전환 시 EMA 스무딩 계수 (0~1).
                       0.0 = 스무딩 없음(즉시 전환, 기본값), 1 = 이전 스케일 유지.
                       0.3 권장: 새 레짐 70% + 이전 스케일 30% 블렌딩.
                       레짐이 실제로 바뀔 때만 적용 (동일 레짐 반복 시 그대로).
        """
        self.fraction = fraction
        self.max_fraction = max_fraction
        self.min_fraction = min_fraction
        self.max_drawdown = max_drawdown
        self.leverage = leverage
        self.kelly_cap = kelly_cap
        self.regime_smooth_alpha = float(np.clip(regime_smooth_alpha, 0.0, 1.0))
        # 레짐 스무딩 상태: 이전 레짐명과 실효 스케일 추적
        self._prev_regime: Optional[str] = None
        self._prev_regime_scale: Optional[float] = None

    def compute(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        capital: float,
        price: float,
        atr: Optional[float] = None,
        target_atr: Optional[float] = None,
        regime: Optional[str] = None,
        mdd_size_multiplier: float = 1.0,
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
            regime: 시장 레짐 문자열 (선택).
                    None이면 regime 조정 없음.
                    "TREND_UP"   → 1.0× (기본)
                    "TREND_DOWN" → 0.6× (하락장 보수적)
                    "RANGING"    → 0.5× (절반 축소)
                    "HIGH_VOL"   → 0.3× (고변동성 대폭 축소)
            mdd_size_multiplier: DrawdownMonitor의 MDD 단계별 사이즈 배수 (기본 1.0).
                    DrawdownMonitor.get_mdd_size_multiplier() 결과를 전달.
                    0.0이면 진입 차단 (0 반환), 0.5이면 50% 축소.

        Returns:
            포지션 사이즈 (수량)
        """
        if avg_win <= 0:
            return 0.0

        # MDD step-down: multiplier가 0이면 즉시 차단
        if mdd_size_multiplier <= 0:
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

        # Quarter-Kelly cap: 풀 Kelly → 파멸 경로 방지
        fractional_f = min(fractional_f, self.kelly_cap)

        # Risk-Constrained Kelly: max_drawdown 제약
        if self.max_drawdown is not None and avg_loss > 0 and self.leverage > 0:
            max_dd_constrained = self.max_drawdown / (avg_loss * self.leverage)
            fractional_f = min(fractional_f, max_dd_constrained)

        # 레짐 스케일 조정 (compute()에 regime 전달 시 자동 적용)
        # EMA 스무딩: 레짐 전환 시에만 이전 스케일과 블렌딩 (동일 레짐 유지 시는 즉시 적용)
        if regime is not None:
            regime_upper = regime.upper()
            target_scale = self._REGIME_SCALE.get(regime_upper, self._DEFAULT_REGIME_SCALE)
            regime_changed = (self._prev_regime is not None and regime_upper != self._prev_regime)
            if regime_changed and self.regime_smooth_alpha > 0.0 and self._prev_regime_scale is not None:
                # 레짐 전환: EMA 블렌딩 (새 레짐 70% + 이전 스케일 30%)
                effective_scale = (
                    (1.0 - self.regime_smooth_alpha) * target_scale
                    + self.regime_smooth_alpha * self._prev_regime_scale
                )
            else:
                # 첫 호출이거나 동일 레짐 유지: target_scale 그대로 사용
                effective_scale = target_scale
            self._prev_regime = regime_upper
            self._prev_regime_scale = effective_scale
            fractional_f *= effective_scale

        # 상·하한 클리핑
        fractional_f = float(np.clip(fractional_f, self.min_fraction, self.max_fraction))

        # ATR 조정
        atr_factor = 1.0
        if atr is not None and target_atr is not None and atr > 0:
            atr_factor = min(target_atr / atr, 1.0)

        # MDD step-down: DrawdownMonitor 단계별 축소 적용
        mdd_factor = float(np.clip(mdd_size_multiplier, 0.0, 1.0))

        # 자본 대비 포지션 금액 → 수량
        position_capital = capital * fractional_f * atr_factor * mdd_factor
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
        regime: Optional[str] = None,
        kelly_cap: float = 0.25,
        mdd_size_multiplier: float = 1.0,
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
            regime: 시장 레짐 (선택). compute(regime=...)에 전달됨.
            kelly_cap: Kelly fraction 상한 (기본 0.25 = Quarter-Kelly cap).
            mdd_size_multiplier: DrawdownMonitor MDD 단계별 사이즈 배수 (기본 1.0).

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
            kelly_cap=kelly_cap,
        )
        return sizer.compute(
            win_rate, avg_win, avg_loss, capital, price, atr, target_atr,
            regime=regime, mdd_size_multiplier=mdd_size_multiplier,
        )

    # 레짐 → Kelly fraction 스케일 팩터
    _REGIME_SCALE: dict = {
        "TREND_UP":   1.0,   # 상승장: 풀 Kelly
        "TREND_DOWN": 0.6,   # 하락장: 40% 축소 (손실 확률 상승)
        "RANGING":    0.5,   # 레인지장: 절반으로 축소
        "HIGH_VOL":   0.3,   # 고변동성: 크게 축소
    }
    _DEFAULT_REGIME_SCALE: float = 0.5  # 알 수 없는 레짐 보수적 처리

    def adjust_for_regime(self, regime: str) -> float:
        """레짐에 따른 Kelly fraction 스케일 팩터 반환.

        현재 인스턴스의 fraction에 레짐 스케일을 곱한 유효 fraction을 반환한다.
        compute(regime=...) 사용을 권장. 이 메서드는 외부에서 수동으로
        fraction을 조회할 때 사용.

        Args:
            regime: 레짐 문자열.
                    "TREND_UP"   → 1.0 (풀 Kelly)
                    "TREND_DOWN" → 0.6 (하락장 40% 축소)
                    "RANGING"    → 0.5 (50% 축소)
                    "HIGH_VOL"   → 0.3 (70% 축소)
                    기타         → 0.5 (보수적)

        Returns:
            유효 Kelly fraction (= self.fraction * regime_scale)
        """
        scale = self._REGIME_SCALE.get(regime.upper(), self._DEFAULT_REGIME_SCALE)
        return float(np.clip(self.fraction * scale, self.min_fraction, self.max_fraction))


class BayesianKellyPositionSizer:
    """Beta 분포 기반 Bayesian Kelly 포지션 사이저.

    Prior: Beta(alpha=2, beta=3) — weakly informative (승률 ~40% 예상)
    Posterior 업데이트: win → alpha+1, loss → beta+1
    Kelly fraction = f* = (posterior_mean * (1+b) - 1) / b
      where b = avg_win / avg_loss (win:loss 비율)
    Fractional Kelly: f* × 0.33 (보수적)
    활성화 조건: alpha + beta >= 54 (= prior(5) + 50 거래 경험)
    활성화 전: 고정 소액 포지션 0.5% of capital
    """

    PRIOR_ALPHA: float = 2.0   # weakly informative prior
    PRIOR_BETA: float = 3.0    # weakly informative prior
    FRACTIONAL: float = 0.33   # 보수적 fractional Kelly
    MIN_TRADES: int = 50        # 활성화 전까지의 최소 거래 수
    WARMUP_FRACTION: float = 0.005  # warmup 기간 고정 포지션 비율 (0.5%)
    MAX_FRACTION: float = 0.10  # 자본 대비 최대 포지션 비율

    def __init__(
        self,
        prior_alpha: float = 2.0,
        prior_beta: float = 3.0,
        fractional: float = 0.33,
        min_trades: int = 50,
        warmup_fraction: float = 0.005,
        max_fraction: float = 0.10,
    ) -> None:
        """
        Args:
            prior_alpha: Beta 분포 prior α (기본 2.0)
            prior_beta: Beta 분포 prior β (기본 3.0)
            fractional: Fractional Kelly 배율 (기본 0.33)
            min_trades: Bayesian Kelly 활성화에 필요한 최소 거래 수 (기본 50)
            warmup_fraction: 활성화 전 고정 포지션 비율 (기본 0.005 = 0.5%)
            max_fraction: 자본 대비 최대 포지션 비율 (기본 0.10 = 10%)
        """
        self.prior_alpha = float(prior_alpha)
        self.prior_beta = float(prior_beta)
        self.fractional = float(fractional)
        self.min_trades = int(min_trades)
        self.warmup_fraction = float(warmup_fraction)
        self.max_fraction = float(max_fraction)

        # Posterior 상태 (prior로 초기화)
        self._alpha = self.prior_alpha
        self._beta = self.prior_beta

        # avg_win / avg_loss 누적 추적
        self._win_sum: float = 0.0
        self._win_count: int = 0
        self._loss_sum: float = 0.0
        self._loss_count: int = 0

    # ── Posterior 업데이트 ──────────────────────────────────────────────────

    def update(self, pnl: float) -> None:
        """거래 결과로 posterior 업데이트.

        Args:
            pnl: 거래 손익 (양수 = 수익, 음수 = 손실, 0 = 무시)
        """
        if not np.isfinite(pnl) or pnl == 0.0:
            return
        if pnl > 0:
            self._alpha += 1.0
            self._win_sum += pnl
            self._win_count += 1
        else:
            self._beta += 1.0
            self._loss_sum += abs(pnl)
            self._loss_count += 1

    def update_batch(self, trades: List[dict]) -> None:
        """거래 기록 배치 업데이트.

        Args:
            trades: [{"pnl": float}, ...] 형태
        """
        for t in trades:
            self.update(t.get("pnl", 0.0))

    # ── Posterior 속성 ──────────────────────────────────────────────────────

    @property
    def alpha(self) -> float:
        """현재 posterior α."""
        return self._alpha

    @property
    def beta(self) -> float:
        """현재 posterior β."""
        return self._beta

    @property
    def n_trades(self) -> int:
        """기록된 거래 수 (prior 제외)."""
        return int(self._alpha - self.prior_alpha + self._beta - self.prior_beta)

    @property
    def posterior_mean(self) -> float:
        """Beta posterior 평균 = α / (α + β)."""
        return self._alpha / (self._alpha + self._beta)

    @property
    def is_active(self) -> bool:
        """Bayesian Kelly 활성화 여부 (min_trades 이상 누적 시 True)."""
        return self.n_trades >= self.min_trades

    # ── 포지션 계산 ─────────────────────────────────────────────────────────

    def calculate_position_size(
        self,
        capital: float,
        price: float,
        avg_win: Optional[float] = None,
        avg_loss: Optional[float] = None,
    ) -> float:
        """포지션 사이즈 (단위 수량) 반환.

        활성화 전(n_trades < min_trades): warmup_fraction × capital / price
        활성화 후: Bayesian Kelly fraction × capital / price (max_fraction 상한)

        Args:
            capital: 총 자본 (통화)
            price: 현재 가격
            avg_win: 평균 수익 비율 (선택; None이면 내부 누적값 사용)
            avg_loss: 평균 손실 비율 (선택; None이면 내부 누적값 사용, 양수)

        Returns:
            포지션 사이즈 (수량). 0.0이면 진입 불가.
        """
        if capital <= 0 or price <= 0:
            return 0.0

        # warmup 기간: 고정 소액 포지션
        if not self.is_active:
            position_capital = capital * self.warmup_fraction
            return position_capital / price

        # avg_win / avg_loss 결정
        aw = avg_win if avg_win is not None else (
            self._win_sum / self._win_count if self._win_count > 0 else None
        )
        al = avg_loss if avg_loss is not None else (
            self._loss_sum / self._loss_count if self._loss_count > 0 else None
        )

        # win 또는 loss 기록이 전혀 없으면 warmup 포지션으로 fallback
        if aw is None or al is None or aw <= 0 or al <= 0:
            position_capital = capital * self.warmup_fraction
            return position_capital / price

        # b = win:loss 비율
        b = aw / al

        # Bayesian Kelly: f* = (posterior_mean * (1 + b) - 1) / b
        f_star = (self.posterior_mean * (1.0 + b) - 1.0) / b

        if f_star <= 0:
            return 0.0

        # Fractional Kelly
        f_fractional = float(np.clip(f_star * self.fractional, 0.0, self.max_fraction))

        position_capital = capital * f_fractional
        return position_capital / price

    def reset(self) -> None:
        """Prior로 상태 초기화."""
        self._alpha = self.prior_alpha
        self._beta = self.prior_beta
        self._win_sum = 0.0
        self._win_count = 0
        self._loss_sum = 0.0
        self._loss_count = 0
