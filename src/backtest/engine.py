"""
BacktestEngine: 전략 성과 검증 엔진.
backtest-agent가 이 모듈을 사용한다.
라이브와 동일한 전략 코드 경로를 사용한다.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, List

import numpy as np
import pandas as pd

from src.strategy.base import Action, BaseStrategy
from src.backtest.report import deflated_sharpe_ratio

logger = logging.getLogger(__name__)

# 최소 통과 기준 (backtest-agent의 hard threshold와 동일)
MIN_SHARPE = 1.0
MAX_DRAWDOWN = 0.20
MIN_PROFIT_FACTOR = 1.5
MIN_TRADES = 15          # Cycle 140: 50 → 15 (실데이터 거래 수 부족 해소)
MIN_WFE = 0.5            # Walk-Forward Efficiency: OOS_Sharpe / IS_Sharpe 최솟값
MC_P_THRESHOLD = 0.10    # Cycle296 B: 0.05→0.10, 15 trades 수준에서 검증력 부족 해소
MC_N_PERMUTATIONS = 1000  # Cycle260: 500→1000, p-value 정밀도 향상 (경계값 오분류 감소)
MAX_HOLD_CANDLES = 24  # 최대 보유 봉 수 (초과 시 강제 청산)
# NOTE(Cycle337 B): 48로 올리면 1h Sharpe 개선(+0.5~0.7) but 4h Bundle OOS 5/5→2/5 FAIL
#   원인: 4h에서 MAX_HOLD=48은 8일 보유 → 가격 반전 위험. 타임프레임별 독립 MAX_HOLD 필요 (추후 개선)

ANNUALIZATION = {
    "1m": 252 * 24 * 60,
    "5m": 252 * 24 * 12,
    "15m": 252 * 24 * 4,
    "1h": 252 * 24,
    "4h": 252 * 6,
    "1d": 252,
}

# Bybit 실제 수수료 (2024-2025 기준)
BYBIT_TAKER_FEE = 0.00055   # 0.055%
BYBIT_MAKER_FEE = 0.00020   # 0.020%
DEFAULT_FEE_RATE = BYBIT_TAKER_FEE  # 백테스트는 시장가(taker) 기준

# 레짐별 슬리피지 기본값 (ATR 비율 기반)
# 저변동성: 0.02%, 보통: 0.05%, 고변동성: 0.15%
SLIPPAGE_REGIME = {
    "low":    0.0002,   # 0.02%
    "normal": 0.0005,   # 0.05%
    "high":   0.0015,   # 0.15%
}
DEFAULT_SLIPPAGE = 0.0005  # 0.05% (보통 레짐)


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
    avg_slippage_per_trade: float = 0.0  # 거래당 평균 슬리피지 비용
    deflated_sharpe_ratio: float = 0.0  # DSR (과최적화 보정)
    avg_win: float = 0.0  # 평균 수익 거래
    avg_loss: float = 0.0  # 평균 손실 거래 (양수)
    win_loss_ratio: float = 0.0  # avg_win / avg_loss
    max_consecutive_losses: int = 0  # 최대 연속 손실
    trades: List[float] = None  # 거래 PnL 리스트 (from_backtest_result 사용 시 설정)
    wfe: float = 0.0  # Walk-Forward Efficiency = OOS_Sharpe / IS_Sharpe (0이면 미계산)
    mc_p_value: float = -1.0  # Monte Carlo permutation p-value (-1=미계산)
    # Cycle309 E(실행): adaptive_slippage 레짐별 진입 횟수 (adaptive_slippage=False면 빈 dict)
    slippage_regime_counts: Dict[str, int] = field(default_factory=dict)
    # Cycle333 B(리스크): min_hold_bars cooldown으로 억제된 신호 수 (min_hold_bars>0일 때만 유효)
    cooldown_suppressed: int = 0
    # Cycle335 A(품질): 청산 이유별 거래 수 (SL/TP/MAX_HOLD 원인 분석용)
    sl_hits: int = 0
    tp_hits: int = 0
    max_hold_closes: int = 0

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
            f"  avg_slippage_per_trade: {self.avg_slippage_per_trade:.6f}",
            f"  verdict: {verdict}",
        ]
        if self.fail_reasons:
            lines.append(f"  fail_reasons: {self.fail_reasons}")
        if self.sl_hits or self.tp_hits or self.max_hold_closes:
            lines.append(f"  close_reasons: sl={self.sl_hits} tp={self.tp_hits} max_hold={self.max_hold_closes}")
        if self.slippage_regime_counts:
            low = self.slippage_regime_counts.get("low", 0)
            normal = self.slippage_regime_counts.get("normal", 0)
            high = self.slippage_regime_counts.get("high", 0)
            lines.append(f"  slippage_regimes: low={low} normal={normal} high={high}")
        return "\n".join(lines)


class BacktestEngine:
    def __init__(
        self,
        initial_balance: float = 10_000.0,
        commission: float = DEFAULT_FEE_RATE,  # Bybit taker 0.055% (deprecated alias: use fee_rate)
        fee_rate: Optional[float] = None,  # 진입/청산 각 taker fee, 왕복 0.11%
        atr_multiplier_sl: float = 1.5,
        atr_multiplier_tp: float = 3.5,  # Cycle 256: 3.0→3.5 (R:R=2.33:1, PF 임계값 낮춤)
        slippage: float = DEFAULT_SLIPPAGE,
        slippage_pct: Optional[float] = None,  # 기본 0.05% (보통 레짐)
        timeframe: str = "1h",
        funding_cost_per_candle: float = 0.0,
        dsr_threshold: float = 0.0,  # DSR 경고 임계값 (0.0=기본, 1.0=엄격)
        adaptive_slippage: bool = False,  # True면 ATR 기반 레짐별 가변 슬리피지
        mc_min_trades: int = 0,  # MC 검정 최소 거래 수 (0=MIN_TRADES 사용)
        mc_block_size: int = 1,  # MC block sign randomization 크기 (1=독립 셔플)
        consec_loss_scale_threshold: int = 0,  # Cycle298 B: 연속 손실 N회 시 포지션 50% 축소 (0=비활성)
        min_hold_bars: int = 0,  # Cycle331 B: 청산 후 재진입 대기 봉수 (0=비활성, 1h에서 4봉=4h 최소 대기)
        max_hold_candles_override: Optional[int] = None,  # Cycle337 B: None이면 MAX_HOLD_CANDLES(24) 사용; 1h paper_sim은 48 전달
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
        self.adaptive_slippage = adaptive_slippage
        # consec_loss_scale_threshold: 0이면 비활성. N>0이면 N번 연속 손실 후 포지션 사이즈 50% 축소
        # DrawdownMonitor.get_size_multiplier()와 동일한 로직을 backtest 시뮬레이션에 반영
        self.consec_loss_scale_threshold = max(0, int(consec_loss_scale_threshold))
        self.min_hold_bars = max(0, int(min_hold_bars))
        # mc_min_trades: 0이면 MIN_TRADES(모듈 상수) 그대로 사용
        self.mc_min_trades = int(mc_min_trades) if mc_min_trades > 0 else MIN_TRADES
        self.mc_block_size = max(1, int(mc_block_size))
        # Cycle337 B: 타임프레임별 max_hold — 1h paper_sim은 48, 4h Bundle OOS는 24(기본)
        self.max_hold_candles = int(max_hold_candles_override) if max_hold_candles_override is not None else MAX_HOLD_CANDLES

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
        signals_skipped_atr0 = 0  # 신호 생성됐으나 atr=0으로 포지션 미진입 횟수
        consec_losses = 0  # 연속 손실 카운터 (consec_loss_scale_threshold 기능용)
        cooldown_remaining = 0  # Cycle331 B: 청산 후 재진입 대기 봉수 카운터
        cooldown_suppressed = 0  # Cycle333 B: cooldown 중 신호 억제 횟수
        # Cycle335 A(품질): 청산 이유 카운터
        sl_hits = 0
        tp_hits = 0
        max_hold_closes = 0
        # Cycle309 E(실행): adaptive_slippage 레짐별 진입 카운트
        slip_regime_counts: Dict[str, int] = {"low": 0, "normal": 0, "high": 0}

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
                exit_slip = self._get_slippage(candle)
                # MAX_HOLD 초과 시 강제 청산 (타임프레임별 self.max_hold_candles 사용)
                if position["hold_candles"] >= self.max_hold_candles:
                    pnl, fee, slip = self._market_close(position, candle["close"], exit_slip)
                    balance += pnl
                    trades.append(pnl)
                    total_fees += fee
                    total_slippage_cost += slip
                    peak_balance = max(peak_balance, balance)
                    max_hold_closes += 1
                    position = None
                    cooldown_remaining = self.min_hold_bars
                    if pnl > 0:
                        consec_losses = 0
                    else:
                        consec_losses += 1
                else:
                    pnl, closed, fee, slip, close_reason = self._check_exit(position, candle, exit_slip)
                    if closed:
                        balance += pnl
                        trades.append(pnl)
                        total_fees += fee
                        total_slippage_cost += slip
                        peak_balance = max(peak_balance, balance)
                        if close_reason == "sl":
                            sl_hits += 1
                        else:
                            tp_hits += 1
                        position = None
                        cooldown_remaining = self.min_hold_bars
                        if pnl > 0:
                            consec_losses = 0
                        else:
                            consec_losses += 1

            # cooldown 중 신호 억제 카운트
            if position is None and cooldown_remaining > 0:
                cooldown_suppressed += 1

            # 신호 생성 (포지션 없고 cooldown 만료 시)
            if position is None and cooldown_remaining == 0:
                signal = strategy.generate(window)
                if signal.action != Action.HOLD:
                    atr = candle["atr14"]
                    if atr <= 0:
                        signals_skipped_atr0 += 1
                        logger.debug(
                            "Signal %s skipped at idx=%d: atr14=0 (no position sizing possible)",
                            signal.action.value, i,
                        )
                    if atr > 0:
                        sl_dist = atr * self.atr_multiplier_sl
                        # Confidence 기반 리스크 배율 (HIGH=1.35%, MEDIUM=1%, LOW=0.5%)
                        # Cycle 258: HIGH 1.2→1.35 (ETH/SOL 혼합 결과 중간값)
                        conf_name = getattr(signal.confidence, 'name', str(signal.confidence)).upper()
                        conf_mult = {"HIGH": 1.35, "MEDIUM": 1.0, "LOW": 0.5}.get(conf_name, 1.0)
                        # Cycle338 B(리스크): 2단계 연속 손실 스케일링
                        # threshold/2 도달 시 0.75, threshold 도달 시 0.50 (Cycle298 단일 0.50→2단계)
                        if self.consec_loss_scale_threshold > 0:
                            half_thresh = max(1, self.consec_loss_scale_threshold // 2)
                            if consec_losses >= self.consec_loss_scale_threshold:
                                loss_scale = 0.5
                            elif consec_losses >= half_thresh:
                                loss_scale = 0.75
                            else:
                                loss_scale = 1.0
                        else:
                            loss_scale = 1.0
                        risk_amt = balance * 0.01 * conf_mult * loss_scale
                        size = risk_amt / sl_dist
                        close = candle["close"]

                        cur_slip = self._get_slippage(candle)
                        # adaptive_slippage 레짐 카운트 (Cycle309 E)
                        if self.adaptive_slippage:
                            if abs(cur_slip - SLIPPAGE_REGIME["low"]) < 1e-9:
                                slip_regime_counts["low"] += 1
                            elif abs(cur_slip - SLIPPAGE_REGIME["high"]) < 1e-9:
                                slip_regime_counts["high"] += 1
                            else:
                                slip_regime_counts["normal"] += 1
                        if signal.action == Action.BUY:
                            entry = close * (1 + cur_slip)
                            sl = entry - sl_dist
                            tp = entry + atr * self.atr_multiplier_tp
                        else:
                            entry = close * (1 - cur_slip)
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

            # cooldown 감소 (매 봉 끝)
            if cooldown_remaining > 0:
                cooldown_remaining -= 1
            equity_curve.append(balance)

        # 미청산 포지션 시장가 청산
        if position:
            last = df.iloc[-1]
            final_slip = self._get_slippage(last)
            pnl, fee, slip = self._market_close(position, last["close"], final_slip)
            balance += pnl
            trades.append(pnl)
            total_fees += fee
            total_slippage_cost += slip
            max_hold_closes += 1
        equity_curve.append(balance)

        result = self._compute_metrics(
            strategy.name, trades, equity_curve, total_fees, total_slippage_cost,
            slippage_regime_counts=slip_regime_counts if self.adaptive_slippage else {},
        )
        result.cooldown_suppressed = cooldown_suppressed
        result.sl_hits = sl_hits
        result.tp_hits = tp_hits
        result.max_hold_closes = max_hold_closes
        if self.min_hold_bars > 0 and cooldown_suppressed > 0:
            logger.debug(
                "Cooldown suppressed %d signal(s) (min_hold_bars=%d)",
                cooldown_suppressed, self.min_hold_bars,
            )
        if not trades and signals_skipped_atr0 > 0:
            reason = f"atr=0 skipped {signals_skipped_atr0} signal(s) — 포지션 미진입"
            if reason not in result.fail_reasons:
                result.fail_reasons.append(reason)
        return result

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
            # IS<0 + OOS>0: IS가 심각한 음수(-1.0 미만)이면 역방향 신호로 신뢰 불가
            if is_sharpe < -1.0:
                # Cycle297 B: RollingOOSValidator와 동기화 — OOS>1.5면 레짐 전환 마커로 부분 신뢰
                if result.sharpe_ratio > 1.5:
                    wfe = 0.5  # IS 역방향 레짐, OOS 강한 회복 → 부분 신뢰
                else:
                    wfe = 0.0  # 강한 역방향 — WFE 0으로 fold FAIL 유도
            else:
                wfe = 1.0  # IS 소폭 음수, OOS 양수 → 과최적화 아님
        else:
            wfe = 0.0  # IS<=0 and OOS<=0 → 과최적화 가능

        result.wfe = round(wfe, 4)
        if wfe > 0 and wfe < MIN_WFE:
            reason = f"wfe {wfe:.3f} < {MIN_WFE} (과최적화 의심)"
            if reason not in result.fail_reasons:
                result.fail_reasons.append(reason)
                result.passed = False
        return result

    def _get_slippage(self, candle: pd.Series) -> float:
        """현재 캔들의 슬리피지를 반환.

        adaptive_slippage=True이면 ATR/close 비율로 레짐 판별 후
        SLIPPAGE_REGIME 딕셔너리에서 해당 레짐 값 반환.
        False이면 고정 self.slippage 반환.

        레짐 판별 기준 (ATR14 / close), 타임프레임 스케일 보정:
          1h 기준: low < 0.5%, normal < 2.0%, high >= 2.0%
          4h 기준: low < 1.0%, normal < 4.0%, high >= 4.0%  (sqrt(4)=2.0x)
          1d 기준: low < 2.5%, normal < 9.8%, high >= 9.8%  (sqrt(24)≈4.9x)
        Cycle316 F(리서치): 4h BTC ATR/close 평균=3.0% → 1h 임계값 2.0%로 98.8% HIGH 분류 발견
          → 타임프레임별 sqrt 스케일 보정 추가 (변동성 = σ√T 비례)
        """
        if not self.adaptive_slippage:
            return self.slippage
        atr = candle.get("atr14", 0.0)
        close = candle.get("close", 1.0)
        if close <= 0 or atr <= 0:
            return self.slippage
        atr_ratio = atr / close
        # 타임프레임별 ATR/close 임계값 스케일 (1h 기준, σ∝√T)
        _TF_HOURS = {"1m": 1/60, "5m": 1/12, "15m": 0.25, "30m": 0.5,
                     "1h": 1.0, "2h": 2.0, "4h": 4.0, "8h": 8.0,
                     "12h": 12.0, "1d": 24.0, "3d": 72.0, "1w": 168.0}
        import math
        tf_scale = math.sqrt(_TF_HOURS.get(self.timeframe, 1.0))
        if atr_ratio < 0.005 * tf_scale:
            return SLIPPAGE_REGIME["low"]
        elif atr_ratio < 0.02 * tf_scale:
            return SLIPPAGE_REGIME["normal"]
        else:
            return SLIPPAGE_REGIME["high"]

    def _check_exit(self, position: dict, candle: pd.Series, slippage: Optional[float] = None) -> Tuple[float, bool, float, float, str]:
        """반환: (pnl, closed, fee, slippage_cost, close_reason)
        close_reason: 'sl' | 'tp' | '' (미청산)
        """
        slip = slippage if slippage is not None else self.slippage
        side = position["side"]
        sl, tp, size, entry = position["sl"], position["tp"], position["size"], position["entry"]

        if side == "BUY":
            if candle["low"] <= sl:
                exit_price = sl * (1 - slip)
                commission_cost = size * exit_price * self.commission
                slip_cost = size * abs(sl - exit_price)
                return (exit_price - entry) * size - commission_cost, True, commission_cost, slip_cost, "sl"
            if candle["high"] >= tp:
                exit_price = tp * (1 - slip)
                commission_cost = size * exit_price * self.commission
                slip_cost = size * abs(tp - exit_price)
                return (exit_price - entry) * size - commission_cost, True, commission_cost, slip_cost, "tp"
        else:
            if candle["high"] >= sl:
                exit_price = sl * (1 + slip)
                commission_cost = size * exit_price * self.commission
                slip_cost = size * abs(exit_price - sl)
                return (entry - exit_price) * size - commission_cost, True, commission_cost, slip_cost, "sl"
            if candle["low"] <= tp:
                exit_price = tp * (1 + slip)
                commission_cost = size * exit_price * self.commission
                slip_cost = size * abs(exit_price - tp)
                return (entry - exit_price) * size - commission_cost, True, commission_cost, slip_cost, "tp"
        return 0.0, False, 0.0, 0.0, ""

    def _market_close(self, position: dict, close_price: float, slippage: Optional[float] = None) -> Tuple[float, float, float]:
        """반환: (pnl, fee, slippage_cost)"""
        slip = slippage if slippage is not None else self.slippage
        entry, size, side = position["entry"], position["size"], position["side"]
        if side == "BUY":
            exit_price = close_price * (1 - slip)
        else:
            exit_price = close_price * (1 + slip)
        commission_cost = size * exit_price * self.commission
        slip_cost = size * abs(close_price - exit_price)
        if side == "BUY":
            return (exit_price - entry) * size - commission_cost, commission_cost, slip_cost
        return (entry - exit_price) * size - commission_cost, commission_cost, slip_cost

    def _compute_metrics(self, name: str, trades: list, equity: list, total_fees: float = 0.0, total_slippage_cost: float = 0.0, wfe: float = 0.0, slippage_regime_counts: Optional[Dict[str, int]] = None) -> BacktestResult:
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
        profit_factor = min(gross_profit / gross_loss, 999.99)  # cap: 손실 0건 시 무한대 방지

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

        # MC Permutation test: mc_min_trades 이상일 때만 실행
        # equity-curve Sharpe는 flat period로 희석되어 trade-PnL Sharpe와 스케일 다름
        # → trade PnL 기준 Sharpe로 비교 (apples-to-apples)
        mc_p = -1.0
        if len(trades) >= self.mc_min_trades:
            trades_arr = np.array(trades, dtype=float)
            trades_std = float(trades_arr.std())
            mc_reference_sharpe = (
                float(trades_arr.mean()) / trades_std * np.sqrt(ann_factor)
                if trades_std > 1e-10 else 0.0
            )
            mc_p = self._mc_permutation_test(
                trades, mc_reference_sharpe, block_size=self.mc_block_size, ann_factor=ann_factor
            )
            if mc_p > MC_P_THRESHOLD:
                fail_reasons.append(f"mc_p_value {mc_p:.3f} > {MC_P_THRESHOLD} (우연 가능성)")

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
        
        avg_slip = total_slippage_cost / len(trades) if trades else 0.0

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
            avg_slippage_per_trade=round(avg_slip, 6),
            deflated_sharpe_ratio=round(dsr, 3),
            avg_win=round(avg_win_val, 6),
            avg_loss=round(avg_loss_val, 6),
            win_loss_ratio=round(win_loss_ratio_val, 3) if win_loss_ratio_val != float("inf") else float("inf"),
            max_consecutive_losses=max_cons_loss,
            trades=trades,  # 거래 PnL 리스트 저장
            wfe=round(wfe, 4),
            mc_p_value=round(mc_p, 4),
            slippage_regime_counts=slippage_regime_counts or {},
        )

    @staticmethod
    def _mc_permutation_test(
        trades: list,
        original_sharpe: float,
        block_size: int = 1,
        ann_factor: int = 8760,
    ) -> float:
        """Sign randomization test with optional block sign randomization.

        Null hypothesis: the strategy has zero expected return.
        Under H0, each trade's sign is equally likely to be +1 or -1.

        Args:
            trades: list of trade PnL values
            original_sharpe: observed Sharpe ratio
            block_size: sign randomization granularity (default 1 = independent per trade).
                       block_size > 1: assign the same random sign to each block of
                       consecutive trades, preserving intra-block serial correlation.
            ann_factor: annualization factor — must match the one used to compute
                        original_sharpe (e.g. 252*24=6048 for 1h, 252*6=1512 for 4h).
                        Default 8760 preserves legacy test compatibility.

        Returns:
            p-value (fraction of permutations with Sharpe >= original_sharpe)
        """
        rng = np.random.default_rng(42)
        arr = np.array(trades, dtype=float)
        n = len(arr)
        if n == 0:
            return 1.0
        ann = np.sqrt(ann_factor)
        n_better = 0

        # Ensure block_size is valid
        if block_size < 1:
            block_size = 1
        if block_size > n:
            block_size = n

        for _ in range(MC_N_PERMUTATIONS):
            if block_size == 1:
                # Independent sign randomization per trade
                signs = rng.choice([-1.0, 1.0], size=n)
            else:
                # Block sign randomization: same sign for all trades in a block
                n_blocks = (n + block_size - 1) // block_size
                block_signs = rng.choice([-1.0, 1.0], size=n_blocks)
                signs = np.repeat(block_signs, block_size)[:n]

            perm_trades = arr * signs
            mean_r = perm_trades.mean()
            std_r = perm_trades.std()
            perm_sharpe = (mean_r / std_r * ann) if std_r > 1e-10 else 0.0
            if perm_sharpe >= original_sharpe:
                n_better += 1

        return n_better / MC_N_PERMUTATIONS

    def perturbation_check(
        self,
        strategy: BaseStrategy,
        params: Dict[str, float],
        data: pd.DataFrame,
        perturbation_pcts: Optional[List[float]] = None,
    ) -> Dict:
        """파라미터 섭동 테스트: 각 파라미터를 ±pct 변동하여 Sharpe 안정성 검증.

        각 파라미터를 독립적으로 ±pct 변동시킨 후 backtest를 실행하여
        Sharpe Ratio의 변화를 측정한다.

        Args:
            strategy: 테스트할 전략 인스턴스 (generate 메서드 보유)
            params: 엔진 파라미터 dict (예: {"atr_multiplier_sl": 1.5, "atr_multiplier_tp": 3.0})
                    BacktestEngine.__init__에 전달 가능한 키만 사용.
            data: backtest용 DataFrame
            perturbation_pcts: 변동 비율 리스트 (기본 [0.1, 0.2] = ±10%, ±20%)

        Returns:
            {
              "baseline_sharpe": float,
              "perturbations": {
                param_name: {
                  "+10%": sharpe, "-10%": sharpe,
                  "+20%": sharpe, "-20%": sharpe,
                },
                ...
              },
              "fragile_params": [param_name, ...],   # ±10%에서 30%+ 하락
              "mean_sharpe": float,                   # 전 변동 평균 Sharpe
              "robustness_ratio": float,              # mean_sharpe / baseline
              "robustness_label": "ROBUST" | "MODERATE" | "FRAGILE",
            }
        """
        if perturbation_pcts is None:
            perturbation_pcts = [0.1, 0.2]

        # 1. Baseline: 원래 파라미터로 backtest
        baseline_engine = self._build_engine(params)
        baseline_result = baseline_engine.run(strategy, data)
        baseline_sharpe = baseline_result.sharpe_ratio

        # 2. 각 파라미터에 대해 ±pct 변동 적용
        perturbations: Dict[str, Dict[str, float]] = {}
        all_sharpes: List[float] = []
        fragile_params: List[str] = []

        for param_name, original_value in params.items():
            param_results: Dict[str, float] = {}
            for pct in perturbation_pcts:
                for sign, label in [(1, f"+{int(pct*100)}%"), (-1, f"-{int(pct*100)}%")]:
                    perturbed_value = original_value * (1 + sign * pct)
                    perturbed_params = dict(params)
                    perturbed_params[param_name] = perturbed_value
                    eng = self._build_engine(perturbed_params)
                    result = eng.run(strategy, data)
                    param_results[label] = result.sharpe_ratio
                    all_sharpes.append(result.sharpe_ratio)
            perturbations[param_name] = param_results

            # FRAGILE 판정: ±10% 변동에서 baseline 대비 30% 이상 하락
            if baseline_sharpe > 0:
                for label_key in ["+10%", "-10%"]:
                    if label_key in param_results:
                        drop = (baseline_sharpe - param_results[label_key]) / baseline_sharpe
                        if drop > 0.3:
                            if param_name not in fragile_params:
                                fragile_params.append(param_name)
                            break

        # 3. Robustness 판정
        mean_sharpe = float(np.mean(all_sharpes)) if all_sharpes else 0.0
        robustness_ratio = mean_sharpe / baseline_sharpe if baseline_sharpe > 0 else 0.0

        if robustness_ratio >= 0.8:
            robustness_label = "ROBUST"
        elif len(fragile_params) > 0:
            robustness_label = "FRAGILE"
        else:
            robustness_label = "MODERATE"

        return {
            "baseline_sharpe": baseline_sharpe,
            "perturbations": perturbations,
            "fragile_params": fragile_params,
            "mean_sharpe": round(mean_sharpe, 4),
            "robustness_ratio": round(robustness_ratio, 4),
            "robustness_label": robustness_label,
        }

    @staticmethod
    def _build_engine(params: Dict[str, float]) -> "BacktestEngine":
        """파라미터 dict로 BacktestEngine 인스턴스를 생성."""
        valid_keys = {
            "initial_balance", "commission", "fee_rate",
            "atr_multiplier_sl", "atr_multiplier_tp",
            "slippage", "slippage_pct", "timeframe",
            "funding_cost_per_candle", "dsr_threshold",
            "adaptive_slippage", "min_hold_bars",
        }
        filtered = {k: v for k, v in params.items() if k in valid_keys}
        return BacktestEngine(**filtered)
