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
    """

    def __init__(self) -> None:
        self._trades: Dict[str, List[dict]] = defaultdict(list)

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
