"""
TradingPipeline: 오케스트레이터가 호출하는 메인 파이프라인.
data → context(B1~B3) → signal → risk → execution 순서를 강제한다.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from src.data.feed import DataFeed, DataSummary
from src.exchange.connector import ExchangeConnector
from src.risk.manager import RiskManager, RiskResult, RiskStatus
from src.strategy.base import Action, BaseStrategy, Signal

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
    notes: list[str] = field(default_factory=list)
    context_score: Optional[float] = None   # MarketContext composite score
    news_risk: str = "NONE"                 # HIGH | MEDIUM | LOW | NONE

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
        self.llm_analyst = None  # LLMAnalyst (선택적, C2)

    def run(self) -> PipelineResult:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        result = PipelineResult(timestamp=ts, symbol=self.symbol, pipeline_step="start", status="OK")

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
            prev_close = summary.df.iloc[-3]["close"]
            last_candle_pct = (last["close"] - prev_close) / prev_close

            balance = self._fetch_balance_usd()
            risk_result: RiskResult = self.risk_manager.evaluate(
                action=signal.action.value,
                entry_price=signal.entry_price,
                atr=last["atr14"],
                account_balance=balance,
                last_candle_pct_change=last_candle_pct,
            )
            result.risk = risk_result
            result.pipeline_step = "risk"

            if risk_result.status == RiskStatus.BLOCKED:
                result.status = "BLOCKED"
                result.notes.append(f"Risk blocked: {risk_result.reason}")
                logger.warning("[pipeline] risk BLOCKED: %s", risk_result.reason)
                return result

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
        except Exception as e:
            result.pipeline_step = "execution"
            result.status = "ERROR"
            result.error = str(e)
            logger.error("[pipeline] execution FAILED: %s", e)

        return result

    def _fetch_balance_usd(self) -> float:
        balance = self.connector.fetch_balance()
        total = balance.get("total", {})
        return float(total.get("USDT", total.get("USD", 0)))
