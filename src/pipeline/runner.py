"""
TradingPipeline: 오케스트레이터가 호출하는 메인 파이프라인.
data → signal → risk → execution 순서를 강제한다.
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

    def log_line(self) -> str:
        sig = f"{self.signal.action.value} {self.symbol}" if self.signal else "N/A"
        risk_status = self.risk.status.value if self.risk else "N/A"
        exec_status = (self.execution or {}).get("status", "SKIPPED")
        return (
            f"## [{self.timestamp}]\n"
            f"Pipeline: {self.pipeline_step}\n"
            f"Status: {self.status}\n"
            f"Signal: {sig}\n"
            f"Risk: {risk_status}\n"
            f"Execution: {exec_status}\n"
            f"Notes: {'; '.join(self.notes) if self.notes else 'none'}\n"
        )


class TradingPipeline:
    """
    파이프라인 실행 순서:
      1. data-agent  → DataFeed.fetch()
      2. alpha-agent → strategy.generate()
      3. risk-agent  → RiskManager.evaluate()   ← GATEKEEPER
      4. execution   → ExchangeConnector.create_order() + wait_for_fill()
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
    ):
        self.connector = connector
        self.data_feed = data_feed
        self.strategy = strategy
        self.risk_manager = risk_manager
        self.symbol = symbol
        self.timeframe = timeframe
        self.dry_run = dry_run

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

        # ── Step 2: Signal (Alpha) ──────────────────────────────────────
        try:
            signal: Signal = self.strategy.generate(summary.df)
            result.signal = signal
            result.pipeline_step = "alpha"
            logger.info("[pipeline] signal=%s confidence=%s", signal.action.value, signal.confidence.value)

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
