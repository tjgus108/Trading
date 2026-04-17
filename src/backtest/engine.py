"""
BacktestEngine: 전략 성과 검증 엔진.
backtest-agent가 이 모듈을 사용한다.
라이브와 동일한 전략 코드 경로를 사용한다.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Tuple, List

import numpy as np
import pandas as pd

from src.strategy.base import Action, BaseStrategy
from src.backtest.report import deflated_sharpe_ratio

logger = logging.getLogger(__name__)

# 최소 통과 기준 (backtest-agent의 hard threshold와 동일)
MIN_SHARPE = 1.0
MAX_DRAWDOWN = 0.20
MIN_PROFIT_FACTOR = 1.5
MIN_TRADES = 50          # Cycle 137: 15 → 50으로 상향 (과최적화 필터)
MIN_WFE = 0.5            # Walk-Forward Efficiency: OOS_Sharpe / IS_Sharpe 최솟값
MAX_HOLD_CANDLES = 24  # 최대 보유 봉 수 (초과 시 강제 청산)

ANNUALIZATION = {
    "1m": 252 * 24 * 60,
    "5m": 252 * 24 * 12,
    "15m": 252 * 24 * 4,
    "1h": 252 * 24,
    "4h": 252 * 6,
    "1d": 252,
}


@dataclass
class BacktestResult:
    strategy: str
    total_trades: int
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    total_return: float
    passed: bool
    fail_reasons: List[str]
    total_fees: float = 0.0
    total_slippage_cost: float = 0.0
    deflated_sharpe_ratio: float = 0.0  # DSR (과최적화 보정)
    avg_win: float = 0.0  # 평균 수익 거래
    avg_loss: float = 0.0  # 평균 손실 거래 (양수)
    win_loss_ratio: float = 0.0  # avg_win / avg_loss
    max_consecutive_losses: int = 0  # 최대 연속 손실
    trades: List[float] = None  # 거래 PnL 리스트 (from_backtest_result 사용 시 설정)
    wfe: float = 0.0  # Walk-Forward Efficiency = OOS_Sharpe / IS_Sharpe (0이면 미계산)

    def summary(self) -> str:
        verdict = "PASS" if self.passed else "FAIL"
        wfe_str = f"{self.wfe:.3f}" if self.wfe > 0 else "N/A"
        lines = [
            f"BACKTEST_RESULT:",
            f"  strategy: {self.strategy}",
            f"  total_trades: {self.total_trades}",
            f"  win_rate: {self.win_rate:.1%}",
            f"  profit_factor: {self.profit_factor:.2f}",
            f"  sharpe_ratio: {self.sharpe_ratio:.2f}",
            f"  deflated_sharpe_ratio: {self.deflated_sharpe_ratio:.2f}",
            f"  wfe: {wfe_str}",
            f"  max_drawdown: {self.max_drawdown:.1%}",
            f"  total_return: {self.total_return:.1%}",
            f"  total_fees: {self.total_fees:.4f}",
            f"  total_slippage_cost: {self.total_slippage_cost:.4f}",
            f"  verdict: {verdict}",
        ]
        if self.fail_reasons:
            lines.append(f"  fail_reasons: {self.fail_reasons}")
        return "\n".join(lines)


class BacktestEngine:
    def __init__(
        self,
        initial_balance: float = 10_000.0,
        commission: float = 0.001,   # 0.1% per trade (deprecated alias: use fee_rate)
        fee_rate: Optional[float] = None,  # 진입/청산 각 0.1%, 왕복 0.2%
        atr_multiplier_sl: float = 1.5,
        atr_multiplier_tp: float = 3.0,
        slippage: float = 0.0005,
        slippage_pct: Optional[float] = None,  # 0.05% 슬리피지
        timeframe: str = "1h",
        funding_cost_per_candle: float = 0.0,
        dsr_threshold: float = 0.0,  # DSR 경고 임계값 (0.0=기본, 1.0=엄격)
    ):
        self.initial_balance = initial_balance
        # fee_rate이 명시되면 우선 적용, 아니면 commission 사용
        self.commission = fee_rate if fee_rate is not None else commission
        self.fee_rate = self.commission  # 별칭
        self.atr_multiplier_sl = atr_multiplier_sl
        self.atr_multiplier_tp = atr_multiplier_tp
        # slippage_pct이 명시되면 우선 적용, 아니면 slippage 사용
        self.slippage = slippage_pct if slippage_pct is not None else slippage
        self.slippage_pct = self.slippage  # 별칭
        self.timeframe = timeframe
        self.funding_cost_per_candle = funding_cost_per_candle
        self.dsr_threshold = dsr_threshold

    def run(self, strategy: BaseStrategy, df: pd.DataFrame) -> BacktestResult:
        """
        df: DataFeed.fetch()가 반환한 DataFrame (지표 포함)
        인덱스 0~end-1 순서로 워크 스루.
        """
        balance = self.initial_balance
        peak_balance = balance
        trades = []
        equity_curve = [balance]
        total_fees = 0.0
        total_slippage_cost = 0.0

        position = None  # {"side": "BUY"/"SELL", "entry": float, "sl": float, "tp": float, "size": float, "hold_candles": int, "raw_entry": float}

        # 최소 지표 warmup 확보 (50 캔들 이후부터 시작)
        start_idx = 52

        for i in range(start_idx, len(df) - 1):
            window = df.iloc[: i + 1]
            candle = df.iloc[i]

            # 펀딩비 적용 (포지션 보유 중 매 캔들)
            if position and self.funding_cost_per_candle != 0.0:
                position_value = position["size"] * candle["close"]
                funding = position_value * self.funding_cost_per_candle
                if position["side"] == "BUY":
                    balance -= funding   # BUY: 비용
                else:
                    balance += funding   # SELL: 수익

            # 열린 포지션 청산 체크
            if position:
                position["hold_candles"] += 1
                # MAX_HOLD_CANDLES 초과 시 강제 청산
                if position["hold_candles"] >= MAX_HOLD_CANDLES:
                    pnl, fee, slip = self._market_close(position, candle["close"])
                    balance += pnl
                    trades.append(pnl)
                    total_fees += fee
                    total_slippage_cost += slip
                    peak_balance = max(peak_balance, balance)
                    position = None
                else:
                    pnl, closed, fee, slip = self._check_exit(position, candle)
                    if closed:
                        balance += pnl
                        trades.append(pnl)
                        total_fees += fee
                        total_slippage_cost += slip
                        peak_balance = max(peak_balance, balance)
                        position = None

            # 신호 생성 (포지션 없을 때만)
            if position is None:
                signal = strategy.generate(window)
                if signal.action != Action.HOLD:
                    atr = candle["atr14"]
                    if atr > 0:
                        sl_dist = atr * self.atr_multiplier_sl
                        # Confidence 기반 리스크 배율 (HIGH=1.5%, MEDIUM=1%, LOW=0.5%)
                        conf_name = getattr(signal.confidence, 'name', str(signal.confidence)).upper()
                        conf_mult = {"HIGH": 1.5, "MEDIUM": 1.0, "LOW": 0.5}.get(conf_name, 1.0)
                        risk_amt = balance * 0.01 * conf_mult
                        size = risk_amt / sl_dist
                        close = candle["close"]

                        if signal.action == Action.BUY:
                            entry = close * (1 + self.slippage)
                            sl = entry - sl_dist
                            tp = entry + atr * self.atr_multiplier_tp
                        else:
                            entry = close * (1 - self.slippage)
                            sl = entry + sl_dist
                            tp = entry - atr * self.atr_multiplier_tp

                        # 진입 슬리피지 비용 추적
                        entry_slip = size * abs(entry - close)
                        total_slippage_cost += entry_slip

                        # 진입 수수료
                        cost = size * entry * self.commission
                        total_fees += cost
                        balance -= cost
                        position = {
                            "side": signal.action.value,
                            "entry": entry,
                            "raw_close": close,
                            "sl": sl,
                            "tp": tp,
                            "size": size,
                            "hold_candles": 0,
                        }

            equity_curve.append(balance)

        # 미청산 포지션 시장가 청산
        if position:
            last = df.iloc[-1]
            pnl, fee, slip = self._market_close(position, last["close"])
            balance += pnl
            trades.append(pnl)
            total_fees += fee
            total_slippage_cost += slip
        equity_curve.append(balance)

        return self._compute_metrics(strategy.name, trades, equity_curve, total_fees, total_slippage_cost)

    @staticmethod
    def apply_wfe(result: "BacktestResult", is_sharpe: float) -> "BacktestResult":
        """
        WFE(Walk-Forward Efficiency)를 계산하여 BacktestResult에 적용.

        WFE = OOS_Sharpe / IS_Sharpe.
        결과의 wfe 필드를 업데이트하고 WFE < MIN_WFE이면 fail_reasons에 추가.
        새 BacktestResult를 반환하지 않고 원본을 직접 수정(mutate).

        Args:
            result: OOS BacktestResult (engine.run() 반환값)
            is_sharpe: in-sample 최적 Sharpe Ratio

        Returns:
            동일 result 객체 (수정됨)
        """
        if is_sharpe > 0:
            wfe = result.sharpe_ratio / is_sharpe
        elif result.sharpe_ratio > 0:
            wfe = 1.0  # IS<=0 but OOS>0 → 과최적화 아님
        else:
            wfe = 0.0  # IS<=0 and OOS<=0 → 과최적화 가능

        result.wfe = round(wfe, 4)
        if wfe > 0 and wfe < MIN_WFE:
            reason = f"wfe {wfe:.3f} < {MIN_WFE} (과최적화 의심)"
            if reason not in result.fail_reasons:
                result.fail_reasons.append(reason)
                result.passed = False
        return result

    def _check_exit(self, position: dict, candle: pd.Series) -> Tuple[float, bool, float, float]:
        """반환: (pnl, closed, fee, slippage_cost)"""
        side = position["side"]
        sl, tp, size, entry = position["sl"], position["tp"], position["size"], position["entry"]

        if side == "BUY":
            if candle["low"] <= sl:
                exit_price = sl * (1 - self.slippage)
                commission_cost = size * exit_price * self.commission
                slip_cost = size * abs(sl - exit_price)
                return (exit_price - entry) * size - commission_cost, True, commission_cost, slip_cost
            if candle["high"] >= tp:
                exit_price = tp * (1 - self.slippage)
                commission_cost = size * exit_price * self.commission
                slip_cost = size * abs(tp - exit_price)
                return (exit_price - entry) * size - commission_cost, True, commission_cost, slip_cost
        else:
            if candle["high"] >= sl:
                exit_price = sl * (1 + self.slippage)
                commission_cost = size * exit_price * self.commission
                slip_cost = size * abs(exit_price - sl)
                return (entry - exit_price) * size - commission_cost, True, commission_cost, slip_cost
            if candle["low"] <= tp:
                exit_price = tp * (1 + self.slippage)
                commission_cost = size * exit_price * self.commission
                slip_cost = size * abs(exit_price - tp)
                return (entry - exit_price) * size - commission_cost, True, commission_cost, slip_cost
        return 0.0, False, 0.0, 0.0

    def _market_close(self, position: dict, close_price: float) -> Tuple[float, float, float]:
        """반환: (pnl, fee, slippage_cost)"""
        entry, size, side = position["entry"], position["size"], position["side"]
        if side == "BUY":
            exit_price = close_price * (1 - self.slippage)
        else:
            exit_price = close_price * (1 + self.slippage)
        commission_cost = size * exit_price * self.commission
        slip_cost = size * abs(close_price - exit_price)
        if side == "BUY":
            return (exit_price - entry) * size - commission_cost, commission_cost, slip_cost
        return (entry - exit_price) * size - commission_cost, commission_cost, slip_cost

    def _compute_metrics(self, name: str, trades: list, equity: list, total_fees: float = 0.0, total_slippage_cost: float = 0.0, wfe: float = 0.0) -> BacktestResult:
        if not trades:
            return BacktestResult(
                strategy=name, total_trades=0, win_rate=0, profit_factor=0,
                sharpe_ratio=0, max_drawdown=0, total_return=0,
                passed=False, fail_reasons=["no trades generated"],
            )

        wins = [t for t in trades if t > 0]
        losses = [t for t in trades if t <= 0]
        win_rate = len(wins) / len(trades)
        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 1e-9
        profit_factor = gross_profit / gross_loss

        eq = np.array(equity)
        returns = np.diff(eq) / eq[:-1]
        ann_factor = ANNUALIZATION.get(self.timeframe, 252 * 24)
        sharpe = (returns.mean() / returns.std() * np.sqrt(ann_factor)) if returns.std() > 0 else 0

        peak = np.maximum.accumulate(eq)
        drawdowns = (peak - eq) / peak
        max_drawdown = float(drawdowns.max())

        total_return = (eq[-1] - self.initial_balance) / self.initial_balance

        # DSR 계산 (과최적화 보정)
        pnls = np.array(trades)
        dsr = deflated_sharpe_ratio(pnls, sharpe, ann_factor)
        if dsr < self.dsr_threshold:
            logger.warning(
                "DSR %.3f < threshold %.3f for strategy '%s': "
                "Sharpe may be overfitted.",
                dsr, self.dsr_threshold, name,
            )

        fail_reasons = []
        if sharpe < MIN_SHARPE:
            fail_reasons.append(f"sharpe {sharpe:.2f} < {MIN_SHARPE}")
        if max_drawdown > MAX_DRAWDOWN:
            fail_reasons.append(f"max_drawdown {max_drawdown:.1%} > {MAX_DRAWDOWN:.0%}")
        if profit_factor < MIN_PROFIT_FACTOR:
            fail_reasons.append(f"profit_factor {profit_factor:.2f} < {MIN_PROFIT_FACTOR}")
        if len(trades) < MIN_TRADES:
            fail_reasons.append(f"trades {len(trades)} < {MIN_TRADES}")
        # WFE 필터: wfe > 0이면 과최적화 체크 (0은 미제공 = 체크 생략)
        if wfe > 0 and wfe < MIN_WFE:
            fail_reasons.append(f"wfe {wfe:.3f} < {MIN_WFE} (과최적화 의심)")

        # avg_win, avg_loss, win_loss_ratio 계산
        avg_win_val = float(np.mean(wins)) if wins else 0.0
        avg_loss_val = float(abs(np.mean(losses))) if losses else 0.0
        win_loss_ratio_val = avg_win_val / avg_loss_val if avg_loss_val > 1e-9 else (0.0 if avg_win_val == 0.0 else float("inf"))
        
        # 최대 연속 손실 횟수
        max_cons_loss = 0
        cur_cons_loss = 0
        for t in trades:
            if t <= 0:
                cur_cons_loss += 1
                max_cons_loss = max(max_cons_loss, cur_cons_loss)
            else:
                cur_cons_loss = 0
        
        return BacktestResult(
            strategy=name,
            total_trades=len(trades),
            win_rate=round(win_rate, 4),
            profit_factor=round(profit_factor, 3),
            sharpe_ratio=round(sharpe, 3),
            max_drawdown=round(max_drawdown, 4),
            total_return=round(total_return, 4),
            passed=len(fail_reasons) == 0,
            fail_reasons=fail_reasons,
            total_fees=round(total_fees, 6),
            total_slippage_cost=round(total_slippage_cost, 6),
            deflated_sharpe_ratio=round(dsr, 3),
            avg_win=round(avg_win_val, 6),
            avg_loss=round(avg_loss_val, 6),
            win_loss_ratio=round(win_loss_ratio_val, 3) if win_loss_ratio_val != float("inf") else float("inf"),
            max_consecutive_losses=max_cons_loss,
            trades=trades,  # 거래 PnL 리스트 저장
            wfe=round(wfe, 4),
        )
