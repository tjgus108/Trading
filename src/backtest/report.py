"""
J2. 백테스트 보고서 생성기.

BacktestEngine 결과(trades list + equity curve)로부터
핵심 성과 지표를 계산하고 텍스트/dict 보고서를 생성한다.

지표:
  - Total Return, Ann. Return, Ann. Volatility, Sharpe Ratio
  - Max Drawdown, Calmar Ratio (Ann. Return / MDD)
  - Sortino Ratio (downside deviation 기반)
  - Recovery Factor (total_return / max_drawdown)
  - Win Rate, Profit Factor, Avg Win/Loss
  - Total Trades, Avg Hold Periods

사용:
  report = BacktestReport.from_trades(trades, annualization=6048)
  print(report.summary())
  d = report.to_dict()
"""

import logging
from dataclasses import dataclass, asdict
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def deflated_sharpe_ratio(
    pnls: np.ndarray,
    sharpe_ratio: float,
    annualization: int = 252 * 24,
) -> float:
    """
    Deflated Sharpe Ratio (DSR) — Bailey & Lopez de Prado (2014).
    
    표본 기반 Sharpe Ratio의 과최적화를 보정한 지표.
    DSR < SR: 표본 SR이 실제 기댓값보다 높을 가능성.
    
    Args:
        pnls: 거래별 수익률 배열 (shape: (n,))
        sharpe_ratio: 계산된 Sharpe Ratio
        annualization: 연환산 인수
    
    Returns:
        float: Deflated Sharpe Ratio
    
    공식:
      SR* = SR * (1 - gamma / (2*n)) + sqrt(Z / (2*n))
      여기서:
        n = 거래 수
        gamma = 표본 3차 모멘트 (skewness)
        Z = 표본 초과 첨도 (excess kurtosis)
    """
    n = len(pnls)
    if n < 3:
        return sharpe_ratio
    
    std_pnl = np.std(pnls, ddof=1)
    if std_pnl < 1e-10:
        return sharpe_ratio
    
    # Skewness (3차 모멘트)
    mean_pnl = np.mean(pnls)
    skew = np.mean(((pnls - mean_pnl) / std_pnl) ** 3)
    gamma = skew
    
    # 초과 첨도 (Excess Kurtosis)
    kurt = np.mean(((pnls - mean_pnl) / std_pnl) ** 4) - 3
    Z = kurt
    
    # DSR 계산
    dsr = sharpe_ratio * (1 - gamma / (2 * n)) + np.sqrt(max(Z / (2 * n), 0))
    return float(dsr)


@dataclass
class BacktestReport:
    # 수익률
    total_return: float          # 누적 수익률
    ann_return: float            # 연환산 수익률
    ann_volatility: float        # 연환산 변동성

    # 리스크 조정 성과
    sharpe_ratio: float
    sortino_ratio: float         # downside deviation 기반 샤프 비율 (신규)
    deflated_sharpe_ratio: float  # DSR (과최적화 보정, Bailey & Lopez)
    calmar_ratio: float          # ann_return / max_drawdown
    recovery_factor: float       # total_return / max_drawdown (신규)
    max_drawdown: float          # 최대 낙폭 (양수)

    # 거래 통계
    total_trades: int
    win_rate: float              # 승률 [0,1]
    profit_factor: float         # 총이익 / 총손실
    avg_win: float               # 평균 수익 (거래당)
    avg_loss: float              # 평균 손실 (거래당, 양수)
    win_loss_ratio: float        # avg_win / avg_loss
    max_consecutive_losses: int  # 최대 연속 손실 횟수

    # 메타
    annualization: int

    def summary(self) -> str:
        return (
            f"=== Backtest Report ===\n"
            f"Total Return:    {self.total_return:+.2%}\n"
            f"Ann. Return:     {self.ann_return:+.2%}\n"
            f"Ann. Volatility: {self.ann_volatility:.2%}\n"
            f"Sharpe Ratio:    {self.sharpe_ratio:.3f}\n"
            f"Sortino Ratio:   {self.sortino_ratio:.3f}\n"
            f"Max Drawdown:    {self.max_drawdown:.2%}\n"
            f"Calmar Ratio:    {self.calmar_ratio:.3f}\n"
            f"Recovery Factor: {self.recovery_factor:.3f}\n"
            f"Win Rate:        {self.win_rate:.1%}\n"
            f"Profit Factor:   {self.profit_factor:.2f}\n"
            f"Avg Win:         {self.avg_win:+.4f}\n"
            f"Avg Loss:        {self.avg_loss:.4f}\n"
            f"Win/Loss Ratio:  {self.win_loss_ratio:.2f}\n"
            f"Max Cons. Loss:  {self.max_consecutive_losses}\n"
            f"Total Trades:    {self.total_trades}\n"
        )

    def to_dict(self) -> dict:
        return asdict(self)

    def to_markdown(self) -> str:
        """
        Markdown 형식의 간결한 성과 보고서.
        
        Returns:
            str: 마크다운 형식 테이블
        """
        return (
            f"| Metric | Value |\n"
            f"|--------|-------|\n"
            f"| Total Return | {self.total_return:+.2%} |\n"
            f"| Ann. Return | {self.ann_return:+.2%} |\n"
            f"| Sharpe Ratio | {self.sharpe_ratio:.3f} |\n"
            f"| Deflated Sharpe Ratio | {self.deflated_sharpe_ratio:.3f} |\n"
            f"| Sortino Ratio | {self.sortino_ratio:.3f} |\n"
            f"| Max Drawdown | {self.max_drawdown:.2%} |\n"
            f"| Win Rate | {self.win_rate:.1%} |\n"
            f"| Profit Factor | {self.profit_factor:.2f} |\n"
            f"| Total Trades | {self.total_trades} |\n"
        )


    @classmethod
    def from_trades(
        cls,
        trades: list[dict],
        annualization: int = 252 * 24,
        risk_free_rate: float = 0.05,
    ) -> "BacktestReport":
        """
        Args:
            trades: [{"pnl_pct": float, ...}, ...] 거래 기록
                    pnl_pct = (exit_price - entry_price) / entry_price
            annualization: 연환산 인수
            risk_free_rate: 무위험 수익률

        Returns:
            BacktestReport
        """
        if not trades:
            return cls._empty(annualization)

        pnls = np.array([t.get("pnl_pct", t.get("pnl", 0.0)) for t in trades], dtype=float)
        n = len(pnls)

        # 수익률 통계
        total_return = float(np.prod(1 + pnls) - 1)
        ann_return = float((1 + total_return) ** (annualization / n) - 1)
        ann_vol = float(pnls.std() * np.sqrt(annualization)) if pnls.std() > 0 else 0.0
        per_period_rf = risk_free_rate / annualization
        sharpe = float((pnls.mean() - per_period_rf) / pnls.std()) * np.sqrt(annualization) if pnls.std() > 0 else 0.0

        # Sortino Ratio: downside deviation 기반
        downside = np.where(pnls < 0, pnls, 0.0)
        downside_var = np.mean(downside ** 2)
        downside_dev = np.sqrt(downside_var) if downside_var > 0 else 0.0
        sortino = float((pnls.mean() - per_period_rf) / downside_dev) * np.sqrt(annualization) if downside_dev > 0 else 0.0


        # Deflated Sharpe Ratio (DSR)
        dsr = deflated_sharpe_ratio(pnls, sharpe, annualization)
        # Max Drawdown
        equity = np.cumprod(1 + pnls)
        peak = np.maximum.accumulate(equity)
        dd = (peak - equity) / np.where(peak > 0, peak, 1)
        mdd = float(dd.max())

        # Calmar
        calmar = ann_return / mdd if mdd > 1e-9 else 0.0

        # Recovery Factor: total_return / max_drawdown
        recovery = total_return / mdd if mdd > 1e-9 else (float("inf") if total_return > 0 else 0.0)

        # 거래 통계
        wins = pnls[pnls > 0]
        losses = pnls[pnls < 0]
        win_rate = len(wins) / n if n > 0 else 0.0
        avg_win = float(wins.mean()) if len(wins) > 0 else 0.0
        avg_loss = float(abs(losses.mean())) if len(losses) > 0 else 0.0
        total_win = float(wins.sum()) if len(wins) > 0 else 0.0
        total_loss = float(abs(losses.sum())) if len(losses) > 0 else 0.0
        profit_factor = total_win / total_loss if total_loss > 1e-9 else float("inf")

        # avg win / avg loss ratio
        win_loss_ratio = avg_win / avg_loss if avg_loss > 1e-9 else float("inf")

        # 최대 연속 손실 횟수
        max_cons_loss = 0
        cur_cons_loss = 0
        for p in pnls:
            if p < 0:
                cur_cons_loss += 1
                max_cons_loss = max(max_cons_loss, cur_cons_loss)
            else:
                cur_cons_loss = 0

        return cls(
            total_return=total_return,
            ann_return=ann_return,
            ann_volatility=ann_vol,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            deflated_sharpe_ratio=dsr,
            calmar_ratio=calmar,
            recovery_factor=recovery,
            max_drawdown=mdd,
            total_trades=n,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            win_loss_ratio=win_loss_ratio,
            max_consecutive_losses=max_cons_loss,
            annualization=annualization,
        )

    @classmethod
    def from_backtest_result(cls, result: "BacktestResult", annualization: int = 252 * 24) -> "BacktestReport":
        """
        BacktestEngine.run()이 반환한 BacktestResult를 BacktestReport로 변환.
        BacktestResult에는 이미 avg_win, avg_loss 등의 메트릭이 계산되어 있음.

        Args:
            result: BacktestEngine.run() 반환값
            annualization: 연환산 인수 (기본 1h 타임프레임 기준)
        """
        recovery = result.total_return / result.max_drawdown if result.max_drawdown > 1e-9 else (float("inf") if result.total_return > 0 else 0.0)
        return cls(
            total_return=result.total_return,
            ann_return=0.0,          # 백테스트는 전체 기간 기반이므로 0
            ann_volatility=0.0,      # 동일
            sharpe_ratio=result.sharpe_ratio,
            sortino_ratio=0.0,       # trades 필요 — 필요 시 from_trades() 사용
            deflated_sharpe_ratio=result.deflated_sharpe_ratio,
            calmar_ratio=(result.total_return / result.max_drawdown
                          if result.max_drawdown > 1e-9 else 0.0),
            recovery_factor=recovery,
            max_drawdown=result.max_drawdown,
            total_trades=result.total_trades,
            win_rate=result.win_rate,
            profit_factor=result.profit_factor,
            avg_win=result.avg_win,
            avg_loss=result.avg_loss,
            win_loss_ratio=result.win_loss_ratio,
            max_consecutive_losses=result.max_consecutive_losses,
            annualization=annualization,
        )

    @classmethod
    def _empty(cls, annualization: int) -> "BacktestReport":
        return cls(
            total_return=0.0, ann_return=0.0, ann_volatility=0.0,
            sharpe_ratio=0.0, sortino_ratio=0.0, deflated_sharpe_ratio=0.0, 
            calmar_ratio=0.0, recovery_factor=0.0,
            max_drawdown=0.0,
            total_trades=0, win_rate=0.0, profit_factor=0.0,
            avg_win=0.0, avg_loss=0.0, win_loss_ratio=0.0,
            max_consecutive_losses=0, annualization=annualization,
        )
