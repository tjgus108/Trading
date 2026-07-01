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

import logging
import numpy as np
from collections import deque
from typing import Deque, Optional, List

logger = logging.getLogger(__name__)


def _norm_ppf(p: float) -> float:
    """표준 정규 분포 분위수 근사 (scipy 불필요).

    Rational approximation by Peter Acklam (max error < 1.2e-7).
    p in (0, 1) → z = ppf(p).
    """
    import math

    if p <= 0.0:
        return float("-inf")
    if p >= 1.0:
        return float("inf")

    a = [-3.969683028665376e1, 2.209460984245205e2,
         -2.759285104469687e2, 1.383577518672690e2,
         -3.066479806614716e1, 2.506628277459239]
    b = [-5.447609879822406e1, 1.615858368580409e2,
         -1.556989798598866e2, 6.680131188771972e1,
         -1.328068155288572e1]
    c = [-7.784894002430293e-3, -3.223964580411365e-1,
         -2.400758277161838, -2.549732539343734,
         4.374664141464968, 2.938163982698783]
    d = [7.784695709041462e-3, 3.224671290700398e-1,
         2.445134137142996, 3.754408661907416]

    p_low = 0.02425
    p_high = 1.0 - p_low

    if p < p_low:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)
    elif p <= p_high:
        q = p - 0.5
        r = q * q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1.0)
    else:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)


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
        kelly_cap: float = 0.20,
        regime_smooth_alpha: float = 0.0,
        rolling_window: int = 50,
    ) -> None:
        """
        Args:
            fraction: Kelly 분수 배율 (0.5 = Half-Kelly)
            max_fraction: 자본 대비 최대 포지션 비율
            min_fraction: 자본 대비 최소 포지션 비율
            max_drawdown: 허용 최대 낙폭 (e.g. 0.05 = 5%). None이면 DD 제약 미적용.
            leverage: 레버리지 배수 (기본 1.0 = 현물)
            kelly_cap: Full Kelly fraction 상한 (기본 0.20 = Fifth-Kelly cap).
                       kelly_f * fraction 결과가 이 값을 초과하지 않도록 제한.
                       풀 Kelly → 파멸 경로 방지 핵심 안전장치.
            regime_smooth_alpha: 레짐 전환 시 EMA 스무딩 계수 (0~1).
                       0.0 = 스무딩 없음(즉시 전환, 기본값), 1 = 이전 스케일 유지.
                       0.3 권장: 새 레짐 70% + 이전 스케일 30% 블렌딩.
                       레짐이 실제로 바뀔 때만 적용 (동일 레짐 반복 시 그대로).
            rolling_window: rolling 추정에 사용할 최근 거래 수 (기본 50).
        """
        self.fraction = fraction
        self.max_fraction = max_fraction
        self.min_fraction = min_fraction
        self.max_drawdown = max_drawdown
        self.leverage = leverage
        self.kelly_cap = kelly_cap
        # kelly_cap이 max_fraction보다 크면 regime scale 이전에 적용되어도 max_fraction이
        # 최종 binding constraint가 됨 → kelly_cap은 사실상 dead param.
        # 예: kelly_cap=0.20, max_fraction=0.10 → 최종 사이즈는 항상 ≤ 0.10.
        if kelly_cap > max_fraction:
            logger.debug(
                "KellySizer: kelly_cap(%.2f) > max_fraction(%.2f) — "
                "max_fraction이 최종 binding constraint (kelly_cap은 regime scale 이전에만 유효)",
                kelly_cap, max_fraction,
            )
        self.regime_smooth_alpha = float(np.clip(regime_smooth_alpha, 0.0, 1.0))
        self.rolling_window = int(rolling_window)
        # 레짐 스무딩 상태: 이전 레짐명과 실효 스케일 추적
        self._prev_regime: Optional[str] = None
        self._prev_regime_scale: Optional[float] = None
        # Rolling 거래 기록 (maxlen = rolling_window)
        self._trade_history: Deque[float] = deque(maxlen=self.rolling_window)

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

    def record_trade(self, pnl: float) -> None:
        """거래 결과(PnL)를 내부 rolling 기록에 추가.

        Args:
            pnl: 거래 손익 (양수=수익, 음수=손실). NaN/inf는 무시.
        """
        if not np.isfinite(pnl):
            return
        self._trade_history.append(float(pnl))

    def estimate_from_history(self, min_trades: int = 10) -> Optional[dict]:
        """Rolling 거래 기록에서 win_rate / avg_win / avg_loss 추정.

        Args:
            min_trades: 유효한 추정을 위한 최소 거래 수 (기본 10).

        Returns:
            {"win_rate": float, "avg_win": float, "avg_loss": float, "n_trades": int}
            거래 기록이 min_trades 미만이면 None 반환.
        """
        if len(self._trade_history) < min_trades:
            return None

        arr = np.array(self._trade_history, dtype=float)
        wins = arr[arr > 0]
        losses = arr[arr < 0]
        n = len(arr)

        win_rate = float(len(wins) / n)
        avg_win = float(wins.mean()) if len(wins) > 0 else 0.0
        avg_loss = float(abs(losses.mean())) if len(losses) > 0 else 0.0

        return {
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "n_trades": n,
        }

    def estimate_var_cvar(
        self,
        confidence: float = 0.95,
        min_trades: int = 30,
    ) -> Optional[dict]:
        """Rolling 거래 기록에서 VaR/CVaR 추정.

        소표본(< min_trades) 경고: 30 미만이면 VaR 추정이 통계적으로 불안정.

        Args:
            confidence: 신뢰 수준 (기본 0.95 = 95%).
            min_trades: VaR 신뢰도 최소 거래 수 (학술 기준 30).

        Returns:
            {"var": float, "cvar": float, "n_trades": int, "low_sample_warning": bool}
            거래 기록이 5 미만이면 None.
        """
        arr = np.array(self._trade_history, dtype=float)
        n = len(arr)
        if n < 5:
            return None

        low_sample = n < min_trades
        if low_sample:
            logger.warning(
                "KellySizer VaR: 소표본 경고 n=%d < %d — VaR 추정 불안정 (편향 가능성)",
                n, min_trades,
            )

        sorted_arr = np.sort(arr)
        cutoff_idx = int(np.floor((1 - confidence) * n))
        cutoff_idx = max(cutoff_idx, 1)

        var_val = float(-sorted_arr[cutoff_idx - 1])
        tail_losses = sorted_arr[:cutoff_idx]
        cvar_val = float(-tail_losses.mean()) if len(tail_losses) > 0 else var_val

        return {
            "var": round(var_val, 6),
            "cvar": round(cvar_val, 6),
            "n_trades": n,
            "low_sample_warning": low_sample,
        }

    def estimate_cornish_fisher_var(
        self,
        confidence: float = 0.95,
        min_trades: int = 20,
    ) -> Optional[dict]:
        """Cornish-Fisher 조정 VaR/CVaR (fat-tail 보정).

        암호화폐 수익률의 음의 왜도(negative skew)와 높은 첨도(fat tails)를
        Cornish-Fisher 확장으로 보정하여 역사적 시뮬레이션보다 정확한 VaR 추정.

        z_cf = z + (z²-1)*s/6 + (z³-3z)*k/24 - (2z³-5z)*s²/36
        where s=skewness, k=excess_kurtosis, z=norm.ppf(1-confidence)

        표준 정규 VaR 대비 개선:
          - BTC 일별 수익률: skew≈-1.2, excess_kurt≈6~10 → CF VaR이 30~50% 더 보수적
          - 소표본(<20) 경고: 왜도/첨도 추정 불안정

        Args:
            confidence: VaR 신뢰 수준 (기본 0.95 = 95%).
            min_trades: 유효 추정 최소 거래 수 (기본 20).

        Returns:
            {
                "cf_var": float,            # CF-보정 VaR (손실, 양수)
                "cf_cvar": float,           # CF-보정 CVaR/ES
                "hist_var": float,          # 역사적 VaR (비교용)
                "hist_cvar": float,         # 역사적 CVaR (비교용)
                "skewness": float,          # 표본 왜도
                "excess_kurtosis": float,   # 표본 초과 첨도
                "n_trades": int,
                "low_sample_warning": bool,
            }
            거래 기록이 5 미만이면 None.
        """
        arr = np.array(self._trade_history, dtype=float)
        n = len(arr)
        if n < 5:
            return None

        low_sample = n < min_trades
        if low_sample:
            logger.warning(
                "KellySizer CF-VaR: 소표본 경고 n=%d < %d — 왜도/첨도 추정 불안정",
                n, min_trades,
            )

        mu = float(arr.mean())
        sigma = float(arr.std(ddof=1)) if n > 1 else 0.0

        # 역사적 VaR/CVaR (비교 기준)
        sorted_arr = np.sort(arr)
        cutoff_idx = max(int(np.floor((1 - confidence) * n)), 1)
        hist_var = float(-sorted_arr[cutoff_idx - 1])
        tail_losses = sorted_arr[:cutoff_idx]
        hist_cvar = float(-tail_losses.mean()) if len(tail_losses) > 0 else hist_var

        # Cornish-Fisher 보정
        if sigma <= 0:
            return {
                "cf_var": hist_var,
                "cf_cvar": hist_cvar,
                "hist_var": round(hist_var, 6),
                "hist_cvar": round(hist_cvar, 6),
                "skewness": 0.0,
                "excess_kurtosis": 0.0,
                "n_trades": n,
                "low_sample_warning": low_sample,
            }

        standardized = (arr - mu) / sigma
        skew = float(np.mean(standardized ** 3))
        # 편향 보정 첨도 (Fisher's excess kurtosis)
        excess_kurt = float(np.mean(standardized ** 4)) - 3.0

        # Cornish-Fisher 안전 클리핑: 극단 skew/kurtosis는 z_cf 발산 유발
        # 실증 범위 기준: |skew| <= 5, excess_kurt in [-2, 50]
        skew = float(np.clip(skew, -5.0, 5.0))
        excess_kurt = float(np.clip(excess_kurt, -2.0, 50.0))

        # 표준 정규 분위수: z = ppf(1 - confidence) → 음수 (손실 방향)
        # 근사: ppf(0.05) ≈ -1.6449
        p = 1.0 - confidence
        # 합리적 z 근사 (scipy 없이 erf 기반)
        # 방법: Newton iteration on standard normal CDF
        z = _norm_ppf(p)

        # Cornish-Fisher 확장
        z_cf = (
            z
            + (z ** 2 - 1.0) * skew / 6.0
            + (z ** 3 - 3.0 * z) * excess_kurt / 24.0
            - (2.0 * z ** 3 - 5.0 * z) * (skew ** 2) / 36.0
        )

        # CF-VaR: 포트폴리오 단위 (PnL 스케일)
        cf_var = float(-(mu + z_cf * sigma))
        # CF-CVaR 근사: 역사적 꼬리 손실에 CF 비율 적용
        cf_ratio = cf_var / hist_var if hist_var > 0 else 1.0
        cf_ratio = max(0.5, min(cf_ratio, 3.0))  # 극단적 배율 방지
        cf_cvar = float(hist_cvar * cf_ratio)

        return {
            "cf_var": round(cf_var, 6),
            "cf_cvar": round(cf_cvar, 6),
            "hist_var": round(hist_var, 6),
            "hist_cvar": round(hist_cvar, 6),
            "skewness": round(skew, 4),
            "excess_kurtosis": round(excess_kurt, 4),
            "n_trades": n,
            "low_sample_warning": low_sample,
        }

    def compute_dynamic(self, capital: float, price: float = 1.0, min_trades: int = 10) -> float:
        """Rolling 거래 기록으로 자동 포지션 사이즈 계산.

        estimate_from_history()가 None이면 (기록 부족) min_fraction * capital 반환.

        Args:
            capital: 총 자본 (통화)
            price: 현재 가격 (기본 1.0, 수량 대신 자본 금액이 필요할 때 1.0 사용)
            min_trades: estimate_from_history에 전달할 최소 거래 수 (기본 10)

        Returns:
            포지션 사이즈 (수량). 기록 부족 시 min_fraction * capital.
        """
        stats = self.estimate_from_history(min_trades=min_trades)
        if stats is None:
            return self.min_fraction * capital

        return self.compute(
            win_rate=stats["win_rate"],
            avg_win=stats["avg_win"],
            avg_loss=stats["avg_loss"],
            capital=capital,
            price=price,
        )

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
        kelly_cap: float = 0.20,
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

    def compute_from_trades(
        self,
        trades: List[float],
        capital: float,
        price: float,
        atr: Optional[float] = None,
        target_atr: Optional[float] = None,
        regime: Optional[str] = None,
        min_trades: int = 10,
    ) -> float:
        """최근 거래 수익률 리스트로부터 포지션 사이즈 계산.

        trades: 거래 손익 비율 리스트 (양수=수익, 음수=손실, e.g. [0.02, -0.01, ...])

        Edge cases:
          - 빈 리스트 → 0.0 반환
          - 모두 손실 (wins 없음) → avg_win=0 → compute()에서 0 반환
          - 모두 수익 (losses 없음) → avg_loss=0 → kelly_f 계산 후 정상 반환
          - NaN/inf 자동 제거
          - 소표본(n < min_trades): Bayesian shrinkage로 win_rate 보정

        내부적으로 _trade_history deque에도 기록하여 rolling 추적 유지.

        Returns:
            포지션 사이즈 (수량). 계산 불가 시 0.0.
        """
        if not trades:
            return 0.0

        arr = np.array(trades, dtype=float)
        arr = arr[np.isfinite(arr)]
        if len(arr) == 0:
            return 0.0

        # _trade_history deque에 기록 (rolling 추적)
        for v in arr:
            self._trade_history.append(v)

        wins = arr[arr > 0]
        losses = arr[arr < 0]

        # 모두 break-even이면 edge 없음
        if len(wins) == 0 and len(losses) == 0:
            return 0.0

        n = len(arr)
        raw_win_rate = len(wins) / n
        avg_win = float(wins.mean()) if len(wins) > 0 else 0.0
        avg_loss = float(abs(losses.mean())) if len(losses) > 0 else 0.0

        # 소표본 Bayesian shrinkage
        if n < min_trades:
            shrink_factor = n / (n + min_trades)
            win_rate = shrink_factor * raw_win_rate + (1.0 - shrink_factor) * 0.5
        else:
            win_rate = raw_win_rate

        return self.compute(
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            capital=capital,
            price=price,
            atr=atr,
            target_atr=target_atr,
            regime=regime,
        )

    # 레짐 → Kelly fraction 스케일 팩터
    # detect_regime() 반환값("bull","bear","crisis") 별칭도 포함
    _REGIME_SCALE: dict = {
        "TREND_UP":   1.0,   # 상승장: 풀 Kelly
        "TREND_DOWN": 0.6,   # 하락장: 40% 축소 (손실 확률 상승)
        "RANGING":    0.5,   # 레인지장: 절반으로 축소
        "HIGH_VOL":   0.3,   # 고변동성: 크게 축소
        # detect_regime() 별칭
        "BULL":       1.0,
        "BEAR":       0.6,
        "CRISIS":     0.3,
    }
    _DEFAULT_REGIME_SCALE: float = 0.5  # 알 수 없는 레짐 보수적 처리

    # 레짐 → 절대 Kelly fraction (Quarter-Kelly 실무 기준 기반)
    # 고변동성 10%, 저변동성 25%, 상승장 25%, 하락장 15%, 위기 10%
    _REGIME_FRACTION: dict = {
        "TREND_UP":   0.25,  # 저변동성 상승장: Quarter-Kelly (25%)
        "TREND_DOWN": 0.15,  # 하락장: 보수적 Sixth-Kelly
        "RANGING":    0.20,  # 레인지장: Fifth-Kelly
        "HIGH_VOL":   0.10,  # 고변동성: Tenth-Kelly (10%)
        # detect_regime() 별칭
        "BULL":       0.25,
        "BEAR":       0.15,
        "CRISIS":     0.10,  # 위기: 최소 포지션
    }
    _DEFAULT_REGIME_FRACTION: float = 0.20  # 알 수 없는 레짐: Fifth-Kelly

    def get_dynamic_fraction(self, regime: str) -> float:
        """레짐에 따른 절대 Kelly fraction 반환.

        현재 인스턴스의 fraction과 무관하게 레짐별 절대 fraction을 반환한다.
        Quarter-Kelly(25%) 실무 표준 기반으로 레짐별 차등 적용.

        Args:
            regime: 레짐 문자열 ("HIGH_VOL", "TREND_UP", "BULL", "CRISIS" 등).

        Returns:
            절대 Kelly fraction (e.g. 0.10 = 10%, 0.25 = 25%).
        """
        return self._REGIME_FRACTION.get(regime.upper(), self._DEFAULT_REGIME_FRACTION)

    def update_fraction_for_regime(self, regime: str) -> float:
        """레짐 기반으로 self.fraction을 동적으로 갱신하고 새 값을 반환.

        compute()를 호출하기 전에 이 메서드를 호출하면 레짐에 맞는
        절대 fraction이 자동으로 적용된다.

        Args:
            regime: 현재 시장 레짐 문자열.

        Returns:
            갱신된 self.fraction 값.
        """
        new_fraction = self.get_dynamic_fraction(regime)
        if new_fraction != self.fraction:
            logger.debug(
                "KellySizer: fraction updated %.2f→%.2f (regime=%s)",
                self.fraction, new_fraction, regime,
            )
            self.fraction = new_fraction
        return self.fraction

    def get_vol_scaled_fraction(
        self,
        realized_vol: float,
        target_vol: float = 0.15,
        regime: Optional[str] = None,
    ) -> float:
        """변동성 스케일링된 Kelly fraction 반환.

        Kelly fraction × (target_vol / realized_vol) 공식으로
        변동성 대비 최적 포지션 크기를 산출한다.
        (arXiv:2508.16598 기반)

        Args:
            realized_vol: 현재 실현 변동성 (연환산).
            target_vol: 목표 변동성 (기본 0.15 = 15%).
            regime: 시장 레짐 문자열 (선택).
                    None이면 현재 self.fraction 기반 Half-Kelly 사용.
                    문자열이면 get_dynamic_fraction(regime) 사용.

        Returns:
            변동성 조정된 Kelly fraction.
            regime=None이면 self.fraction, 아니면 레짐별 절대 fraction에
            vol_scalar를 곱한 값.
        """
        # 레짐 기반 fraction 결정
        if regime is not None:
            base_fraction = self.get_dynamic_fraction(regime)
        else:
            base_fraction = self.fraction

        # vol scalar: target_vol / realized_vol, 최대 2x cap
        vol_scalar = min(target_vol / max(realized_vol, 1e-9), 2.0)

        return base_fraction * vol_scalar

    def apply_volatility_scaling(
        self,
        fraction: float,
        realized_vol: float,
        target_vol: float = 0.15,
    ) -> float:
        """변동성 스케일링을 Kelly fraction에 적용.

        scaled = fraction * (target_vol / realized_vol)

        Args:
            fraction: 입력 Kelly fraction (e.g. 0.05).
            realized_vol: 현재 실현 변동성 (연환산).
                          0이나 매우 작으면(< 0.001) fraction을 그대로 반환.
            target_vol: 목표 변동성 (기본 0.15 = 15%).

        Returns:
            스케일링된 fraction.
            결과가 원래 fraction의 2x를 초과하지 않도록 cap.
        """
        if realized_vol < 0.001:
            return fraction
        scaled = fraction * (target_vol / realized_vol)
        # 원래 fraction의 2배 cap
        return min(scaled, fraction * 2.0)

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
        return float(self.fraction * scale)


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
