from collections import defaultdict
from math import sqrt
from typing import Callable, Dict, List, Optional
import time
import logging

logger = logging.getLogger(__name__)


class LivePerformanceTracker:
    """
    라이브 트레이드 결과를 추적하고 성과 저하를 감지.

    - 백테스트 Sharpe 대비 라이브 Sharpe가 60% 이하로 떨어지면 경고
    - 연속 손실 5회 이상이면 경고
    - 전략별 성과를 별도 추적
    - Rolling Sharpe 기반 레짐 사망(regime death) 감지
    """

    def __init__(self) -> None:
        self._trades: Dict[str, List[dict]] = defaultdict(list)
        self._regime_death_consecutive: Dict[str, int] = defaultdict(int)

    def record_trade(
        self,
        strategy: str,
        pnl: float,
        entry_price: float,
        exit_price: float,
        timestamp: Optional[float] = None,
    ) -> None:
        """거래 결과 기록."""
        self._trades[strategy].append(
            {
                "pnl": pnl,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "timestamp": timestamp if timestamp is not None else time.time(),
            }
        )

    def get_live_sharpe(self, strategy: str, window: int = 30) -> Optional[float]:
        """최근 window개 거래의 Sharpe 계산. 거래 수 < 5이면 None 반환."""
        trades = self._trades[strategy]
        recent = trades[-window:] if len(trades) >= window else trades
        if len(recent) < 5:
            return None

        pnls = [t["pnl"] for t in recent]
        n = len(pnls)
        mean_pnl = sum(pnls) / n
        variance = sum((p - mean_pnl) ** 2 for p in pnls) / n
        std_pnl = variance ** 0.5

        if std_pnl == 0:
            return None

        annualization = sqrt(252)
        return mean_pnl / std_pnl * annualization

    def rolling_sharpe_check(
        self,
        strategy: str,
        window: int = 30,
        warn_threshold: float = 0.5,
        disable_threshold: float = 0.0,
    ) -> dict:
        """Rolling Sharpe 기반 전략 상태 플래그 반환.

        Returns:
            {
              "sharpe":  float | None,   — 계산된 Rolling Sharpe (거래 수 < 5 시 None)
              "warn":    bool,           — Sharpe < warn_threshold (기본 0.5) 시 True
              "disable": bool,           — Sharpe < disable_threshold (기본 0.0) 시 True
              "reason":  str,            — 플래그 발생 시 설명
            }
        """
        sharpe = self.get_live_sharpe(strategy, window=window)
        if sharpe is None:
            return {"sharpe": None, "warn": False, "disable": False, "reason": "insufficient_data"}

        if sharpe < disable_threshold:
            return {
                "sharpe": sharpe,
                "warn": True,
                "disable": True,
                "reason": f"Rolling Sharpe {sharpe:.3f} < disable_threshold {disable_threshold} — 전략 비활성화 권고",
            }
        if sharpe < warn_threshold:
            return {
                "sharpe": sharpe,
                "warn": True,
                "disable": False,
                "reason": f"Rolling Sharpe {sharpe:.3f} < warn_threshold {warn_threshold} — 경고",
            }
        return {"sharpe": sharpe, "warn": False, "disable": False, "reason": ""}

    def check_regime_death(
        self,
        strategy: str,
        backtest_sharpe: float,
        window_days: int = 30,
        threshold: float = 0.5,
        consecutive_periods: int = 2,
    ) -> dict:
        """Rolling Sharpe 기반 레짐 사망(regime death) 감지.

        최근 window_days일간의 일별 PnL로 Sharpe를 계산하고,
        backtest_sharpe * threshold 미만이면 연속 카운터를 증가시킨다.
        연속 카운터가 consecutive_periods 이상이면 레짐 사망으로 판정.

        Args:
            strategy: 전략 이름
            backtest_sharpe: 백테스트에서 측정된 Sharpe
            window_days: 일별 PnL 윈도우 (기본 30일)
            threshold: backtest_sharpe 대비 비율 (기본 0.5)
            consecutive_periods: 연속 미달 횟수 (기본 2)

        Returns:
            {
              "is_dead": bool,
              "live_sharpe": float | None,
              "threshold_sharpe": float,
              "consecutive_below": int,
            }
        """
        threshold_sharpe = backtest_sharpe * threshold

        # 일별 PnL → Sharpe (연환산)
        daily_pnl = self.get_daily_pnl(strategy, days=window_days)
        non_zero = [d for d in daily_pnl if d != 0.0]

        live_sharpe = None  # type: Optional[float]
        if len(non_zero) >= 2:
            n = len(daily_pnl)
            mean_d = sum(daily_pnl) / n
            variance = sum((d - mean_d) ** 2 for d in daily_pnl) / n
            std_d = variance ** 0.5
            if std_d > 0:
                live_sharpe = (mean_d / std_d) * sqrt(365)

        # 데이터 부족 시 연속 카운터를 리셋하지 않고 현재 상태 반환
        if live_sharpe is None:
            return {
                "is_dead": False,
                "live_sharpe": None,
                "threshold_sharpe": round(threshold_sharpe, 4),
                "consecutive_below": self._regime_death_consecutive[strategy],
            }

        # 연속 미달 카운터 업데이트
        if live_sharpe < threshold_sharpe:
            self._regime_death_consecutive[strategy] += 1
        else:
            self._regime_death_consecutive[strategy] = 0

        consecutive_below = self._regime_death_consecutive[strategy]
        is_dead = consecutive_below >= consecutive_periods

        if is_dead:
            logger.warning(
                "Regime death detected for %s: live_sharpe=%.3f < threshold=%.3f, "
                "consecutive=%d",
                strategy,
                live_sharpe,
                threshold_sharpe,
                consecutive_below,
            )

        return {
            "is_dead": is_dead,
            "live_sharpe": round(live_sharpe, 4),
            "threshold_sharpe": round(threshold_sharpe, 4),
            "consecutive_below": consecutive_below,
        }

    def check_degradation(
        self, strategy: str, backtest_sharpe: float
    ) -> Optional[str]:
        """성과 저하 감지. 문제 있으면 사유 문자열 반환, 없으면 None."""
        # 연속 손실 확인
        trades = self._trades[strategy]
        consecutive = 0
        for t in reversed(trades):
            if t["pnl"] < 0:
                consecutive += 1
            else:
                break

        if consecutive >= 5:
            return "연속 손실 5회"

        live_sharpe = self.get_live_sharpe(strategy)
        if live_sharpe is not None and live_sharpe < backtest_sharpe * 0.6:
            return (
                f"live Sharpe {live_sharpe:.2f} < 60% of backtest {backtest_sharpe:.2f}"
            )

        return None

    def get_rolling_pf(self, strategy: str, window: int = 30) -> Optional[float]:
        """최근 window개 거래의 Profit Factor 계산."""
        trades = self._trades[strategy]
        recent = trades[-window:] if len(trades) >= window else trades
        if len(recent) < 5:
            return None
        pnls = [t["pnl"] for t in recent]
        gross_profit = sum(p for p in pnls if p > 0)
        gross_loss = abs(sum(p for p in pnls if p <= 0))
        if gross_loss < 1e-9:
            return float("inf") if gross_profit > 0 else 0.0
        return gross_profit / gross_loss

    def get_rolling_mdd(self, strategy: str, window: int = 30) -> float:
        """최근 window개 거래의 MDD (equity curve 기반) 계산."""
        trades = self._trades[strategy]
        recent = trades[-window:] if len(trades) >= window else trades
        if not recent:
            return 0.0
        equity = 0.0
        peak = 0.0
        max_dd = 0.0
        for t in recent:
            equity += t["pnl"]
            if equity > peak:
                peak = equity
            if peak > 0:
                dd = (peak - equity) / peak
                max_dd = max(max_dd, dd)
            elif equity < 0:
                max_dd = 1.0
        return max_dd

    def get_hourly_pnl(self, strategy: str, hours: int = 24) -> list:
        """최근 N시간 동안의 시간별 합산 PnL 리스트 반환.

        Returns:
            길이 hours인 list. index 0 = 가장 오래된 시간 버킷,
            index -1 = 가장 최근 시간 버킷. 거래 없는 버킷은 0.0.
        """
        now = time.time()
        cutoff = now - hours * 3600.0
        buckets = [0.0] * hours

        for t in self._trades[strategy]:
            ts = t.get("timestamp", 0.0)
            if ts < cutoff:
                continue
            age_seconds = now - ts
            bucket_idx = hours - 1 - int(age_seconds // 3600)
            if 0 <= bucket_idx < hours:
                buckets[bucket_idx] += t["pnl"]

        return buckets

    def get_daily_pnl(self, strategy: str, days: int = 7) -> list:
        """최근 N일간의 일별 합산 PnL 리스트 반환.

        Returns:
            길이 days인 list. index 0 = 가장 오래된 날,
            index -1 = 오늘. 거래 없는 날은 0.0.
        """
        now = time.time()
        cutoff = now - days * 86400.0
        buckets = [0.0] * days

        for t in self._trades[strategy]:
            ts = t.get("timestamp", 0.0)
            if ts < cutoff:
                continue
            age_seconds = now - ts
            bucket_idx = days - 1 - int(age_seconds // 86400)
            if 0 <= bucket_idx < days:
                buckets[bucket_idx] += t["pnl"]

        return buckets

    def get_daily_summary(self, strategy: str, days: int = 7) -> dict:
        """일간 기준 성과 요약: 승률, PF, Sharpe.

        최근 days일간의 거래를 기반으로 계산.

        Returns:
            {
              "days": int,
              "total_trades": int,
              "total_pnl": float,
              "daily_pnl": list[float],
              "win_rate": float,
              "profit_factor": float | None,
              "sharpe": float | None,
            }
        """
        now = time.time()
        cutoff = now - days * 86400.0

        trades_in_window = [
            t for t in self._trades[strategy]
            if t.get("timestamp", 0.0) >= cutoff
        ]

        total_trades = len(trades_in_window)
        pnls = [t["pnl"] for t in trades_in_window]
        total_pnl = sum(pnls)

        # 승률
        wins = sum(1 for p in pnls if p > 0)
        win_rate = wins / total_trades if total_trades > 0 else 0.0

        # Profit Factor
        gross_profit = sum(p for p in pnls if p > 0)
        gross_loss = abs(sum(p for p in pnls if p <= 0))
        if gross_loss < 1e-9:
            pf = float("inf") if gross_profit > 0 else None
        else:
            pf = gross_profit / gross_loss

        # 일별 PnL → Sharpe (일간 기준, 연환산)
        daily_pnl = self.get_daily_pnl(strategy, days=days)
        non_zero_days = [d for d in daily_pnl if d != 0.0]
        if len(non_zero_days) >= 2:
            n = len(daily_pnl)
            mean_d = sum(daily_pnl) / n
            variance = sum((d - mean_d) ** 2 for d in daily_pnl) / n
            std_d = variance ** 0.5
            if std_d > 0:
                sharpe = (mean_d / std_d) * sqrt(365)
            else:
                sharpe = None
        else:
            sharpe = None

        return {
            "days": days,
            "total_trades": total_trades,
            "total_pnl": round(total_pnl, 8),
            "daily_pnl": daily_pnl,
            "win_rate": round(win_rate, 4),
            "profit_factor": round(pf, 4) if pf is not None and pf != float("inf") else pf,
            "sharpe": round(sharpe, 4) if sharpe is not None else None,
        }

    def get_weekly_pnl(self, strategy: str, weeks: int = 4) -> list:
        """최근 N주간의 주별 합산 PnL 리스트 반환.

        Returns:
            길이 weeks인 list. index 0 = 가장 오래된 주,
            index -1 = 이번 주. 거래 없는 주는 0.0.
        """
        now = time.time()
        bucket_seconds = 7 * 86400.0  # 1주 = 7일
        cutoff = now - weeks * bucket_seconds
        buckets = [0.0] * weeks

        for t in self._trades[strategy]:
            ts = t.get("timestamp", 0.0)
            if ts < cutoff:
                continue
            age_seconds = now - ts
            bucket_idx = weeks - 1 - int(age_seconds // bucket_seconds)
            if 0 <= bucket_idx < weeks:
                buckets[bucket_idx] += t["pnl"]

        return buckets

    def get_monthly_pnl(self, strategy: str, months: int = 3) -> list:
        """최근 N개월간의 월별 합산 PnL 리스트 반환.

        달력월이 아닌 30일 단위 근사.

        Returns:
            길이 months인 list. index 0 = 가장 오래된 월,
            index -1 = 이번 달. 거래 없는 달은 0.0.
        """
        now = time.time()
        bucket_seconds = 30 * 86400.0  # 1개월 ≈ 30일
        cutoff = now - months * bucket_seconds
        buckets = [0.0] * months

        for t in self._trades[strategy]:
            ts = t.get("timestamp", 0.0)
            if ts < cutoff:
                continue
            age_seconds = now - ts
            bucket_idx = months - 1 - int(age_seconds // bucket_seconds)
            if 0 <= bucket_idx < months:
                buckets[bucket_idx] += t["pnl"]

        return buckets

    def _compute_period_summary(
        self,
        strategy: str,
        period_days: int,
        period_pnl: list,
        annualization_factor: float,
    ) -> dict:
        """기간별 성과 요약 공통 로직.

        Args:
            strategy: 전략 이름
            period_days: 기간 (일수)
            period_pnl: 기간별 PnL 버킷 리스트
            annualization_factor: Sharpe 연환산 계수 (ex. sqrt(52) for weekly)

        Returns:
            {periods, total_trades, total_pnl, period_pnl, win_rate, profit_factor, sharpe, mdd}
        """
        now = time.time()
        cutoff = now - period_days * 86400.0

        trades_in_window = [
            t for t in self._trades[strategy]
            if t.get("timestamp", 0.0) >= cutoff
        ]

        total_trades = len(trades_in_window)
        pnls = [t["pnl"] for t in trades_in_window]
        total_pnl = sum(pnls)

        # 승률
        wins = sum(1 for p in pnls if p > 0)
        win_rate = wins / total_trades if total_trades > 0 else 0.0

        # Profit Factor
        gross_profit = sum(p for p in pnls if p > 0)
        gross_loss = abs(sum(p for p in pnls if p <= 0))
        if gross_loss < 1e-9:
            pf = float("inf") if gross_profit > 0 else None
        else:
            pf = gross_profit / gross_loss

        # 기간별 PnL → Sharpe (연환산)
        non_zero = [d for d in period_pnl if d != 0.0]
        if len(non_zero) >= 2:
            n = len(period_pnl)
            mean_d = sum(period_pnl) / n
            variance = sum((d - mean_d) ** 2 for d in period_pnl) / n
            std_d = variance ** 0.5
            if std_d > 0:
                sharpe = (mean_d / std_d) * annualization_factor
            else:
                sharpe = None
        else:
            sharpe = None

        # MDD (기간 내 equity curve 기반)
        equity = 0.0
        peak = 0.0
        max_dd = 0.0
        for t in trades_in_window:
            equity += t["pnl"]
            if equity > peak:
                peak = equity
            if peak > 0:
                dd = (peak - equity) / peak
                max_dd = max(max_dd, dd)
            elif equity < 0:
                max_dd = max(max_dd, 1.0)

        return {
            "periods": len(period_pnl),
            "total_trades": total_trades,
            "total_pnl": round(total_pnl, 8),
            "period_pnl": period_pnl,
            "win_rate": round(win_rate, 4),
            "profit_factor": round(pf, 4) if pf is not None and pf != float("inf") else pf,
            "sharpe": round(sharpe, 4) if sharpe is not None else None,
            "mdd": round(max_dd, 4),
        }

    def get_weekly_summary(self, strategy: str, weeks: int = 4) -> dict:
        """주간 기준 성과 요약: 승률, PF, Sharpe, MDD.

        최근 weeks주간의 거래를 기반으로 계산.

        Returns:
            {
              "weeks": int,
              "total_trades": int,
              "total_pnl": float,
              "weekly_pnl": list[float],
              "win_rate": float,
              "profit_factor": float | None,
              "sharpe": float | None,
              "mdd": float,
            }
        """
        weekly_pnl = self.get_weekly_pnl(strategy, weeks=weeks)
        result = self._compute_period_summary(
            strategy=strategy,
            period_days=weeks * 7,
            period_pnl=weekly_pnl,
            annualization_factor=sqrt(52),
        )
        return {
            "weeks": weeks,
            "total_trades": result["total_trades"],
            "total_pnl": result["total_pnl"],
            "weekly_pnl": result["period_pnl"],
            "win_rate": result["win_rate"],
            "profit_factor": result["profit_factor"],
            "sharpe": result["sharpe"],
            "mdd": result["mdd"],
        }

    def get_monthly_summary(self, strategy: str, months: int = 3) -> dict:
        """월간 기준 성과 요약: 승률, PF, Sharpe, MDD.

        최근 months개월간의 거래를 기반으로 계산 (30일/월 근사).

        Returns:
            {
              "months": int,
              "total_trades": int,
              "total_pnl": float,
              "monthly_pnl": list[float],
              "win_rate": float,
              "profit_factor": float | None,
              "sharpe": float | None,
              "mdd": float,
            }
        """
        monthly_pnl = self.get_monthly_pnl(strategy, months=months)
        result = self._compute_period_summary(
            strategy=strategy,
            period_days=months * 30,
            period_pnl=monthly_pnl,
            annualization_factor=sqrt(12),
        )
        return {
            "months": months,
            "total_trades": result["total_trades"],
            "total_pnl": result["total_pnl"],
            "monthly_pnl": result["period_pnl"],
            "win_rate": result["win_rate"],
            "profit_factor": result["profit_factor"],
            "sharpe": result["sharpe"],
            "mdd": result["mdd"],
        }

    def get_summary(self, strategy: str) -> dict:
        """전략별 요약 반환."""
        trades = self._trades[strategy]
        total = len(trades)

        if total == 0:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "live_sharpe": None,
                "rolling_pf": None,
                "rolling_mdd": 0.0,
                "consecutive_losses": 0,
            }

        wins = sum(1 for t in trades if t["pnl"] > 0)
        win_rate = wins / total

        consecutive = 0
        for t in reversed(trades):
            if t["pnl"] < 0:
                consecutive += 1
            else:
                break

        return {
            "total_trades": total,
            "win_rate": win_rate,
            "live_sharpe": self.get_live_sharpe(strategy),
            "rolling_pf": self.get_rolling_pf(strategy),
            "rolling_mdd": self.get_rolling_mdd(strategy),
            "consecutive_losses": consecutive,
        }


class PerformanceMonitor:
    """Rolling 4주 성과 추적 + 알림 연동.

    DrawdownMonitor/CircuitBreaker와 별개로, 전략 레벨에서
    Rolling Sharpe/PF를 추적하고 임계값 초과 시 콜백 호출.

    Args:
        tracker: LivePerformanceTracker 인스턴스
        on_alert: 알림 콜백 (level: str, message: str) -> None
        sharpe_warn: Sharpe 경고 임계값
        pf_warn: PF 경고 임계값
        mdd_warn_pct: MDD 경고 임계값 (Telegram 경고)
        mdd_halt_pct: MDD 중단 임계값 (자동 청산)
        check_interval: 체크 간격 (초)
    """

    def __init__(
        self,
        tracker: LivePerformanceTracker,
        on_alert: Optional[Callable[[str, str], None]] = None,
        sharpe_warn: float = 1.0,
        pf_warn: float = 1.4,
        mdd_warn_pct: float = 0.10,
        mdd_halt_pct: float = 0.15,
        check_interval: float = 14400.0,
    ):
        self.tracker = tracker
        self.on_alert = on_alert
        self.sharpe_warn = sharpe_warn
        self.pf_warn = pf_warn
        self.mdd_warn_pct = mdd_warn_pct
        self.mdd_halt_pct = mdd_halt_pct
        self.check_interval = check_interval
        self._last_check: float = 0.0
        self._alerted_strategies: Dict[str, float] = {}

    def check_all(self, strategies: List[str], window: int = 30) -> Dict[str, dict]:
        """모든 전략의 Rolling 성과를 체크하고 알림 발생."""
        now = time.monotonic()
        results = {}

        for name in strategies:
            summary = self.tracker.get_summary(name)
            sharpe = summary.get("live_sharpe")
            pf = summary.get("rolling_pf")
            mdd = summary.get("rolling_mdd", 0.0)

            alerts = []
            level = "INFO"

            if mdd >= self.mdd_halt_pct:
                level = "CRITICAL"
                alerts.append(
                    f"[{name}] MDD {mdd:.1%} >= {self.mdd_halt_pct:.0%} — 자동 청산 필요"
                )
            elif mdd >= self.mdd_warn_pct:
                level = "WARNING"
                alerts.append(
                    f"[{name}] MDD {mdd:.1%} >= {self.mdd_warn_pct:.0%} — 경고"
                )

            if sharpe is not None and sharpe < self.sharpe_warn:
                if level == "INFO":
                    level = "WARNING"
                alerts.append(
                    f"[{name}] Rolling Sharpe {sharpe:.2f} < {self.sharpe_warn}"
                )

            if pf is not None and pf < self.pf_warn:
                if level == "INFO":
                    level = "WARNING"
                alerts.append(
                    f"[{name}] Rolling PF {pf:.2f} < {self.pf_warn}"
                )

            if alerts and self.on_alert:
                last_alert = self._alerted_strategies.get(name, 0.0)
                if now - last_alert > self.check_interval:
                    for msg in alerts:
                        self.on_alert(level, msg)
                    self._alerted_strategies[name] = now

            results[name] = {
                "sharpe": sharpe,
                "pf": pf,
                "mdd": mdd,
                "level": level,
                "alerts": alerts,
            }

        self._last_check = now
        return results

    def regime_change_alert(self, old_regime: str, new_regime: str) -> None:
        """레짐 전환 알림 발송."""
        msg = f"레짐 전환: {old_regime} → {new_regime}"
        logger.info("PerformanceMonitor: %s", msg)
        if self.on_alert:
            self.on_alert("INFO", msg)
