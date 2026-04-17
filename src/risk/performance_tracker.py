from collections import defaultdict
from math import sqrt
from typing import Dict, List, Optional


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
    ) -> None:
        """거래 결과 기록."""
        self._trades[strategy].append(
            {
                "pnl": pnl,
                "entry_price": entry_price,
                "exit_price": exit_price,
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

    def get_summary(self, strategy: str) -> dict:
        """전략별 요약 반환."""
        trades = self._trades[strategy]
        total = len(trades)

        if total == 0:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "live_sharpe": None,
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
            "consecutive_losses": consecutive,
        }
