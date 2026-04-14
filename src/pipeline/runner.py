"""
TradingPipeline: 오케스트레이터가 호출하는 메인 파이프라인.
data → context(B1~B3) → signal → risk → execution 순서를 강제한다.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List

from src.data.feed import DataFeed, DataSummary
from src.exchange.connector import ExchangeConnector
from src.risk.manager import RiskManager, RiskResult, RiskStatus
from src.risk.kelly_sizer import KellySizer
from src.risk.vol_targeting import VolTargeting
from src.exchange.twap import TWAPExecutor
from src.strategy.base import Action, BaseStrategy, Confidence, Signal
from src.utils.trade_logger import TradeLogger

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    timestamp: str
    symbol: str
    pipeline_step: str          # 마지막으로 완료된 단계
    status: str                 # "OK" | "BLOCKED" | "ERROR"
    signal: Optional[Signal] = None
    risk: Optional[RiskResult] = None
    execution: Optional[dict] = None
    error: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    context_score: Optional[float] = None   # MarketContext composite score
    news_risk: str = "NONE"                 # HIGH | MEDIUM | LOW | NONE
    pnl: float = 0.0                        # 거래 손익 (USD)
    specialist_action: str = ""             # SpecialistEnsemble 최종 액션
    impl_shortfall_bps: Optional[float] = None  # Implementation Shortfall (bps): (avg_fill - expected) / expected * 10000

    def log_line(self) -> str:
        sig = f"{self.signal.action.value} {self.symbol}" if self.signal else "N/A"
        risk_status = self.risk.status.value if self.risk else "N/A"
        exec_status = (self.execution or {}).get("status", "SKIPPED")
        ctx = f"{self.context_score:+.2f}" if self.context_score is not None else "N/A"
        return (
            f"## [{self.timestamp}]\n"
            f"Pipeline: {self.pipeline_step}\n"
            f"Status: {self.status}\n"
            f"Signal: {sig}\n"
            f"Risk: {risk_status}\n"
            f"Execution: {exec_status}\n"
            f"Context: score={ctx} news={self.news_risk}\n"
            f"Notes: {'; '.join(self.notes) if self.notes else 'none'}\n"
            + (f"ImplShortfall: {self.impl_shortfall_bps:.2f}bps\n" if self.impl_shortfall_bps is not None else "")
        )


class TradingPipeline:
    """
    파이프라인 실행 순서:
      1. data-agent    → DataFeed.fetch()
      1b. context      → MarketContextBuilder.build() (B1~B3, 선택적)
      2. alpha-agent   → strategy.generate() + context.adjust_signal()
      3. risk-agent    → RiskManager.evaluate()   ← GATEKEEPER
      4. execution     → ExchangeConnector.create_order() + wait_for_fill()
    """

    def __init__(
        self,
        connector: ExchangeConnector,
        data_feed: DataFeed,
        strategy: BaseStrategy,
        risk_manager: RiskManager,
        symbol: str,
        timeframe: str,
        dry_run: bool = True,
        context_builder=None,   # MarketContextBuilder (선택적)
    ):
        self.connector = connector
        self.data_feed = data_feed
        self.strategy = strategy
        self.risk_manager = risk_manager
        self.symbol = symbol
        self.timeframe = timeframe
        self.dry_run = dry_run
        self.context_builder = context_builder
        self.llm_analyst = None          # LLMAnalyst (선택적, C2)
        self.ensemble = None             # MultiLLMEnsemble (선택적, D1)
        self.specialist_ensemble = None  # SpecialistEnsemble (선택적, F1)
        self.kelly_sizer: Optional[KellySizer] = None       # H1: Kelly position sizer
        self.twap_executor: Optional[TWAPExecutor] = None   # H4: TWAP order execution
        self.vol_targeting: Optional[VolTargeting] = None   # I3: Vol-targeted sizing
        self._trade_history: List[dict] = []               # H1: 거래 기록 (kelly 계산용)
        # 세무/감사 대비: 모든 체결을 append-only CSV에 기록
        self.trade_logger: Optional[TradeLogger] = (
            None if dry_run else TradeLogger("logs/trades.csv")
        )

    def preflight_check(self) -> List[str]:
        """실행 전 안전 점검. 문제 발견 시 경고 메시지 리스트 반환."""
        warnings = []

        # 1. 거래소 연결 상태
        if self.connector.is_halted:
            warnings.append("CRITICAL: Connector is halted due to consecutive failures")

        # 2. 실전 모드에서 포지션 동기화
        if not self.dry_run:
            try:
                open_pos = self.connector.sync_positions(self.symbol)
                if open_pos:
                    warnings.append(
                        f"WARNING: {len(open_pos)} open position(s) found on exchange. "
                        f"New entries will be blocked until positions are resolved."
                    )
                    self._has_unsynced_positions = True
                else:
                    self._has_unsynced_positions = False
            except Exception as e:
                warnings.append(f"WARNING: Position sync failed: {e}")
                self._has_unsynced_positions = True

        return warnings

    def run(self) -> PipelineResult:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        result = PipelineResult(timestamp=ts, symbol=self.symbol, pipeline_step="start", status="OK")

        # ── Step 0: Preflight Check ─────────────────────────────────────
        preflight_warnings = self.preflight_check()
        for w in preflight_warnings:
            result.notes.append(w)
            logger.warning("[pipeline] preflight: %s", w)

        if any("CRITICAL" in w for w in preflight_warnings):
            result.status = "ERROR"
            result.error = "Preflight check failed"
            result.pipeline_step = "preflight"
            return result

        # ── Step 1: Data ────────────────────────────────────────────────
        try:
            summary: DataSummary = self.data_feed.fetch(self.symbol, self.timeframe)
            result.pipeline_step = "data"
            if summary.missing > 5:
                result.notes.append(f"WARNING: {summary.missing} missing candles")
            if summary.anomalies:
                result.notes.append(f"ANOMALIES: {summary.anomalies}")
            logger.info("[pipeline] data OK — %d candles", summary.candles)
        except Exception as e:
            result.pipeline_step = "data"
            result.status = "ERROR"
            result.error = str(e)
            logger.error("[pipeline] data FAILED: %s", e)
            return result

        # ── Step 1b: Market Context (B1~B3) ────────────────────────────
        ctx = None
        if self.context_builder is not None:
            try:
                ctx = self.context_builder.build()
                result.context_score = ctx.composite_score
                result.news_risk = ctx.news_risk_level
                for line in ctx.summary_lines():
                    result.notes.append(line)
            except Exception as e:
                logger.warning("[pipeline] context build failed (non-fatal): %s", e)

        # ── Step 1c: Unsynced Position Guard ───────────────────────────
        if getattr(self, '_has_unsynced_positions', False) and not self.dry_run:
            result.status = "BLOCKED"
            result.pipeline_step = "preflight"
            result.notes.append("BLOCKED: Unsynced positions on exchange — resolve before new entries")
            logger.warning("[pipeline] BLOCKED: unsynced positions — skipping signal generation")
            return result

        # ── Step 2: Signal (Alpha) ──────────────────────────────────────
        try:
            signal: Signal = self.strategy.generate(summary.df)

            # MarketContext로 신호 조정
            if ctx is not None:
                signal, ctx_notes = ctx.adjust_signal(signal)
                result.notes.extend(ctx_notes)

            result.signal = signal
            result.pipeline_step = "alpha"
            logger.info("[pipeline] signal=%s confidence=%s", signal.action.value, signal.confidence.value)

            # D1: 멀티 LLM 앙상블 (HOLD 아닐 때만)
            if self.ensemble is not None and signal.action != Action.HOLD:
                try:
                    ctx_summary = "; ".join(ctx.summary_lines()[:1]) if ctx else ""
                    ens = self.ensemble.analyze(
                        symbol=self.symbol,
                        rule_signal=signal.action.value,
                        signal_context=signal.reasoning[:150],
                        market_summary=ctx_summary,
                    )
                    result.notes.append(f"ENSEMBLE: {ens.summary()}")
                    # 앙상블이 강하게 반대하면 HOLD 전환
                    if ens.conflicts_with(signal.action.value):
                        result.notes.append(f"ENSEMBLE conflict → HOLD 전환")
                        signal = Signal(
                            action=Action.HOLD,
                            confidence=Confidence.MEDIUM,
                            strategy=signal.strategy,
                            entry_price=signal.entry_price,
                            reasoning=f"[ENSEMBLE_CONFLICT] {signal.reasoning}",
                            invalidation="LLM 합의 전환 시 재진입",
                            bull_case=signal.bull_case,
                            bear_case=signal.bear_case,
                        )
                        result.signal = signal
                        result.pipeline_step = "alpha"
                        result.notes.append("HOLD — ensemble conflict")
                        return result
                except Exception as e:
                    logger.debug("Ensemble check failed: %s", e)

            # C2: LLM 분석 (이벤트 기반 — HOLD 아닐 때만)
            if self.llm_analyst is not None and signal.action != Action.HOLD:
                try:
                    ctx_summary = "; ".join(ctx.summary_lines()[:2]) if ctx else ""
                    llm_note = self.llm_analyst.analyze_signal(
                        symbol=self.symbol,
                        signal_action=signal.action.value,
                        signal_reasoning=signal.reasoning,
                        context_summary=ctx_summary,
                    )
                    if llm_note:
                        result.notes.append(f"LLM: {llm_note}")
                except Exception as e:
                    logger.debug("LLM analysis skipped: %s", e)

            # F1: SpecialistEnsemble 신호 검증 (있을 때만)
            if self.specialist_ensemble is not None:
                try:
                    spec_vote = self.specialist_ensemble.analyze(summary.df)
                    result.specialist_action = spec_vote.action
                    # spec_vote.action이 signal.action.value와 반대이고 confidence >= 0.7이면 HOLD
                    if (spec_vote.action != "HOLD" and
                            spec_vote.action != signal.action.value and
                            spec_vote.confidence >= 0.7):
                        signal = Signal(
                            action=Action.HOLD, confidence=Confidence.LOW,
                            strategy=signal.strategy, entry_price=signal.entry_price,
                            reasoning=f"SpecialistEnsemble 충돌: {spec_vote.action} conf={spec_vote.confidence:.2f}",
                            invalidation="", bull_case="", bear_case="",
                        )
                        result.signal = signal
                        result.notes.append(f"SPECIALIST conflict → HOLD ({spec_vote.action} conf={spec_vote.confidence:.2f})")
                except Exception as e:
                    logger.debug("SpecialistEnsemble check failed: %s", e)

            # HOLD는 리스크/실행 건너뜀
            if signal.action == Action.HOLD:
                result.pipeline_step = "alpha"
                result.status = "OK"
                result.notes.append("HOLD — no order")
                return result
        except Exception as e:
            result.pipeline_step = "alpha"
            result.status = "ERROR"
            result.error = str(e)
            logger.error("[pipeline] signal FAILED: %s", e)
            return result

        # ── Step 3: Risk ────────────────────────────────────────────────
        try:
            last = summary.df.iloc[-2]
            prev_close = float(summary.df.iloc[-3]["close"])
            last_candle_pct = (float(last["close"]) - prev_close) / prev_close if prev_close > 0 else 0.0

            balance = self._fetch_balance_usd()
            risk_result: RiskResult = self.risk_manager.evaluate(
                action=signal.action.value,
                entry_price=signal.entry_price,
                atr=last["atr14"],
                account_balance=balance,
                last_candle_pct_change=last_candle_pct,
                candle_df=summary.df,
                confidence=str(signal.confidence.name) if hasattr(signal.confidence, 'name') else str(signal.confidence),
            )
            result.risk = risk_result
            result.pipeline_step = "risk"

            if risk_result.status == RiskStatus.BLOCKED:
                result.status = "BLOCKED"
                result.notes.append(f"Risk blocked: {risk_result.reason}")
                logger.warning("[pipeline] risk BLOCKED: %s", risk_result.reason)
                return result

            # H1: Kelly Sizer — 거래 이력 충분할 때 position_size 재계산
            if self.kelly_sizer is not None and len(self._trade_history) >= 10:
                try:
                    kelly_size = KellySizer.from_trade_history(
                        trades=self._trade_history,
                        capital=balance,
                        price=signal.entry_price,
                        atr=float(last.get("atr14", 0)) or None,
                        target_atr=None,
                    )
                    if kelly_size > 0:
                        risk_result.position_size = kelly_size
                        result.notes.append(f"Kelly size: {kelly_size:.6f}")
                        logger.info("[pipeline] Kelly size=%.6f", kelly_size)
                except Exception as e:
                    logger.debug("Kelly sizing failed: %s", e)

            # I3: VolTargeting — position_size 추가 조정
            if self.vol_targeting is not None:
                try:
                    adjusted = self.vol_targeting.adjust(
                        base_size=risk_result.position_size,
                        df=summary.df,
                    )
                    if adjusted > 0:
                        risk_result.position_size = adjusted
                        result.notes.append(f"VolTarget size: {adjusted:.6f}")
                except Exception as e:
                    logger.debug("VolTargeting adjustment failed: %s", e)

            logger.info("[pipeline] risk APPROVED — size=%.4f", risk_result.position_size)
        except Exception as e:
            result.pipeline_step = "risk"
            result.status = "ERROR"
            result.error = str(e)
            logger.error("[pipeline] risk FAILED: %s", e)
            return result

        # ── Step 4: Execution ───────────────────────────────────────────
        if self.dry_run:
            result.pipeline_step = "execution"
            result.execution = {
                "status": "DRY_RUN",
                "side": signal.action.value,
                "size": risk_result.position_size,
                "entry_price": signal.entry_price,
            }
            result.notes.append("dry_run=True — order not submitted")
            logger.info("[pipeline] dry_run — skipping order submission")
            return result

        try:
            side = "buy" if signal.action == Action.BUY else "sell"

            # H4: TWAP 실행 (twap_executor 설정 시)
            if self.twap_executor is not None:
                twap_result = self.twap_executor.execute(
                    connector=self.connector,
                    symbol=self.symbol,
                    side=side,
                    total_qty=risk_result.position_size,
                )
                result.execution = {
                    "status": "TWAP_COMPLETE",
                    "slices": twap_result.slices_executed,
                    "avg_price": twap_result.avg_price,
                    "filled_size": twap_result.total_qty,
                    "slippage_pct": twap_result.estimated_slippage_pct,
                }
                result.pipeline_step = "execution"
                logger.info(
                    "[pipeline] TWAP done slices=%d avg=%.2f slip=%.4f%%",
                    twap_result.slices_executed,
                    twap_result.avg_price,
                    twap_result.estimated_slippage_pct,
                )
                if signal.entry_price and twap_result.avg_price:
                    result.impl_shortfall_bps = (
                        (twap_result.avg_price - signal.entry_price) / signal.entry_price * 10_000
                    )
                    logger.info("[pipeline] impl_shortfall=%.2fbps", result.impl_shortfall_bps)
            else:
                order = self.connector.create_order(
                    symbol=self.symbol,
                    side=side,
                    amount=risk_result.position_size,
                )
                fill = self.connector.wait_for_fill(order["id"], self.symbol)
                result.execution = {
                    "status": fill.get("status", "UNKNOWN"),
                    "order_id": fill.get("id"),
                    "filled_size": fill.get("filled"),
                    "avg_price": fill.get("average"),
                }
                result.pipeline_step = "execution"
                logger.info("[pipeline] execution status=%s", fill.get("status"))

                # 세무 대비: 체결 내역 CSV 기록
                if self.trade_logger and fill.get("filled"):
                    self.trade_logger.log_fill(
                        order=fill, symbol=self.symbol, side=side,
                        strategy=getattr(self.strategy, "name", type(self.strategy).__name__),
                        note="entry",
                    )

                # SL/TP 보호 주문 거래소 제출
                if fill.get("status") == "closed" and fill.get("filled"):
                    self._submit_sl_tp_orders(
                        symbol=self.symbol,
                        side=side,
                        filled_size=float(fill["filled"]),
                        stop_loss=risk_result.stop_loss,
                        take_profit=risk_result.take_profit,
                    )

                avg_price = fill.get("average")
                if signal.entry_price and avg_price:
                    result.impl_shortfall_bps = (
                        (float(avg_price) - signal.entry_price) / signal.entry_price * 10_000
                    )
                    logger.info("[pipeline] impl_shortfall=%.2fbps", result.impl_shortfall_bps)
        except Exception as e:
            result.pipeline_step = "execution"
            result.status = "ERROR"
            result.error = str(e)
            logger.error("[pipeline] execution FAILED: %s", e)

        return result

    def _submit_sl_tp_orders(
        self,
        symbol: str,
        side: str,
        filled_size: float,
        stop_loss: float | None,
        take_profit: float | None,
    ) -> None:
        """체결 후 SL/TP 보호 주문을 거래소에 제출."""
        close_side = "sell" if side == "buy" else "buy"

        sl_ok = False
        if stop_loss and stop_loss > 0:
            for attempt in range(1, 3):
                try:
                    sl_order = self.connector.create_order(
                        symbol=symbol,
                        side=close_side,
                        amount=filled_size,
                        order_type="market",
                        price=None,
                        params={
                            "stopLossPrice": stop_loss,
                            "triggerPrice": stop_loss,
                            "reduceOnly": True,
                        },
                    )
                    logger.info(
                        "[pipeline] SL order submitted: id=%s trigger=$%.2f",
                        sl_order.get("id"), stop_loss,
                    )
                    sl_ok = True
                    break
                except Exception as e:
                    logger.error("[pipeline] SL order attempt %d FAILED: %s", attempt, e)

            if not sl_ok:
                # SL 제출 실패 → 포지션 보호 불가, 즉시 시장가 청산
                logger.critical(
                    "[pipeline] SL order FAILED after retries — emergency close position"
                )
                try:
                    self.connector.create_order(
                        symbol=symbol, side=close_side,
                        amount=filled_size, order_type="market",
                    )
                    logger.warning("[pipeline] Emergency close executed")
                    if self.trade_logger:
                        self.trade_logger.log_fill(
                            order={"status": "emergency_close",
                                   "amount": filled_size, "filled": filled_size},
                            symbol=symbol, side=close_side,
                            strategy=getattr(self.strategy, "name",
                                             type(self.strategy).__name__),
                            note="emergency_close_after_sl_fail",
                        )
                except Exception as e2:
                    logger.critical("[pipeline] Emergency close ALSO FAILED: %s", e2)
                    # 보호 불가능한 포지션이 남았음 → 커넥터 halt로 다음 엔트리 차단
                    self.connector._consecutive_failures = max(
                        self.connector._consecutive_failures,
                        self.connector._max_consecutive_failures,
                    )
                return

        if take_profit and take_profit > 0:
            try:
                tp_order = self.connector.create_order(
                    symbol=symbol,
                    side=close_side,
                    amount=filled_size,
                    order_type="market",
                    price=None,
                    params={
                        "takeProfitPrice": take_profit,
                        "triggerPrice": take_profit,
                        "reduceOnly": True,
                    },
                )
                logger.info(
                    "[pipeline] TP order submitted: id=%s trigger=$%.2f",
                    tp_order.get("id"), take_profit,
                )
            except Exception as e:
                logger.error("[pipeline] TP order FAILED: %s (SL is active, continuing)", e)

    def _fetch_balance_usd(self) -> float:
        try:
            balance = self.connector.fetch_balance()
            total = balance.get("total", {})
            val = float(total.get("USDT", total.get("USD", 0)))
        except Exception as e:
            logger.warning("fetch_balance failed (%s) — using fallback 10000", e)
            val = 0.0
        if val <= 0:
            logger.warning("account_balance=%.2f <= 0 — using fallback 10000 for dry_run", val)
            return 10_000.0
        return val
