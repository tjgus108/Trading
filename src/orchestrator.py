"""
BotOrchestrator: 트레이딩 봇 전체 생명주기를 관리하는 중앙 조율자.

책임:
  - 컴포넌트 조립 및 초기화
  - Startup gate: backtest PASS 없이 live 불가
  - 파이프라인 1회 / 스케줄 루프 실행
  - Strategy tournament: 여러 전략 병렬 백테스트 후 Sharpe 기준 최고 선택
  - 알림 / 로그 / 상태 파일 관리

main.py는 인수 파싱 후 Orchestrator에 위임하고 끝낸다.
"""

import concurrent.futures
import logging
import threading
from dataclasses import dataclass
from typing import Optional

from src.backtest.engine import BacktestEngine, BacktestResult
from src.config import AppConfig
from src.data.feed import DataFeed
from src.exchange.connector import ExchangeConnector
from src.notifier import TelegramNotifier
from src.pipeline.runner import PipelineResult, TradingPipeline
from src.risk.manager import CircuitBreaker, RiskManager
from src.scheduler import CandleScheduler
from src.strategy.base import BaseStrategy
from src.strategy.donchian_breakout import DonchianBreakoutStrategy
from src.strategy.ema_cross import EmaCrossStrategy

logger = logging.getLogger(__name__)

STRATEGY_REGISTRY: dict[str, type[BaseStrategy]] = {
    "ema_cross": EmaCrossStrategy,
    "donchian_breakout": DonchianBreakoutStrategy,
}


class OrchestratorError(Exception):
    pass


@dataclass
class TournamentResult:
    winner: str                          # 전략 이름
    winner_sharpe: float
    rankings: list[dict]                 # [{name, sharpe, passed, fail_reasons}]

    def summary(self) -> str:
        lines = ["TOURNAMENT RESULT:"]
        for i, r in enumerate(self.rankings, 1):
            verdict = "PASS" if r["passed"] else "FAIL"
            lines.append(
                f"  #{i} {r['name']:25s}  Sharpe={r['sharpe']:.3f}  {verdict}"
                + (f"  fail={r['fail_reasons']}" if r["fail_reasons"] else "")
            )
        lines.append(f"  WINNER → {self.winner} (Sharpe={self.winner_sharpe:.3f})")
        return "\n".join(lines)


class BotOrchestrator:
    """
    트레이딩 봇 오케스트레이터.

    사용 예:
        orch = BotOrchestrator(cfg)
        orch.startup()
        orch.run_once()          # 1회
        orch.run_loop()          # 스케줄 루프
        orch.run_backtest_only() # 검증만
    """

    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self._connector: Optional[ExchangeConnector] = None
        self._data_feed: Optional[DataFeed] = None
        self._risk_manager: Optional[RiskManager] = None
        self._strategy: Optional[BaseStrategy] = None
        self._notifier: Optional[TelegramNotifier] = None
        self._pipeline: Optional[TradingPipeline] = None
        self._stop_event = threading.Event()

    # ── Public API ───────────────────────────────────────────────────────

    def startup(self, dry_run: bool = True) -> None:
        """
        컴포넌트 초기화 + backtest gate.
        live 모드일 때 backtest FAIL이면 OrchestratorError 발생.
        """
        self._dry_run = dry_run
        self._notifier = self._build_notifier()
        logger.info("Orchestrator starting — strategy=%s symbol=%s dry_run=%s",
                    self.cfg.strategy, self.cfg.trading.symbol, dry_run)

        self._connect()
        self._build_risk()
        self._load_strategy()
        self._build_pipeline()

        if not dry_run:
            self._backtest_gate()

        self._notifier.notify_startup(
            strategy=self.cfg.strategy,
            symbol=self.cfg.trading.symbol,
            dry_run=dry_run,
        )
        logger.info("Orchestrator startup complete")

    def run_once(self) -> PipelineResult:
        """파이프라인 1회 실행 후 결과 반환."""
        self._assert_ready()
        result = self._pipeline.run()
        self._handle_result(result)
        return result

    def run_loop(self) -> None:
        """캔들 완성 시각에 맞춰 파이프라인을 반복 실행. Ctrl+C로 종료."""
        self._assert_ready()
        scheduler = CandleScheduler()
        logger.info("Loop started — timeframe=%s (Ctrl+C to stop)", self.cfg.trading.timeframe)

        try:
            scheduler.run_loop(self.run_once, self.cfg.trading.timeframe, self._stop_event)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt — stopping")
            self._stop_event.set()

        logger.info("Orchestrator stopped gracefully")

    def stop(self) -> None:
        """외부에서 루프 종료 신호."""
        self._stop_event.set()

    def run_backtest_only(self) -> BacktestResult:
        """백테스트만 실행하고 결과 반환. startup() 이후 호출."""
        self._assert_ready()
        return self._run_backtest(self._strategy)

    def run_tournament(self, candidates: Optional[list[str]] = None) -> TournamentResult:
        """
        여러 전략을 병렬 백테스트 후 Sharpe 기준으로 순위를 매기고 승자를 반환.
        승자 전략으로 파이프라인을 재구성한다.

        Args:
            candidates: 검증할 전략 이름 목록. None이면 STRATEGY_REGISTRY 전체.

        Returns:
            TournamentResult (rankings + winner)
        """
        self._assert_ready()
        names = candidates or list(STRATEGY_REGISTRY.keys())
        logger.info("Tournament starting — candidates: %s", names)

        strategies = []
        for name in names:
            cls = STRATEGY_REGISTRY.get(name)
            if cls is None:
                logger.warning("Tournament: unknown strategy '%s', skipping", name)
                continue
            strategies.append(cls())

        if not strategies:
            raise OrchestratorError("No valid strategies for tournament")

        # 병렬 백테스트
        results: dict[str, BacktestResult] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(strategies)) as pool:
            futures = {pool.submit(self._run_backtest, s): s.name for s in strategies}
            for fut in concurrent.futures.as_completed(futures):
                name = futures[fut]
                try:
                    results[name] = fut.result()
                    logger.info("Tournament [%s]: Sharpe=%.3f passed=%s",
                                name, results[name].sharpe_ratio, results[name].passed)
                except Exception as e:
                    logger.error("Tournament [%s] failed: %s", name, e)

        if not results:
            raise OrchestratorError("All strategies failed during tournament")

        # Sharpe 기준 정렬 (PASS 전략 우선, 그 다음 Sharpe 내림차순)
        ranked = sorted(
            results.items(),
            key=lambda x: (x[1].passed, x[1].sharpe_ratio),
            reverse=True,
        )

        winner_name, winner_result = ranked[0]
        rankings = [
            {
                "name": name,
                "sharpe": r.sharpe_ratio,
                "passed": r.passed,
                "fail_reasons": r.fail_reasons,
            }
            for name, r in ranked
        ]

        tournament = TournamentResult(
            winner=winner_name,
            winner_sharpe=winner_result.sharpe_ratio,
            rankings=rankings,
        )

        # 승자 전략으로 파이프라인 재구성
        self._strategy = STRATEGY_REGISTRY[winner_name]()
        self._build_pipeline()
        logger.info("Tournament winner: %s (Sharpe=%.3f)", winner_name, winner_result.sharpe_ratio)

        msg = f"Tournament winner: {winner_name} (Sharpe={winner_result.sharpe_ratio:.3f})"
        self._notifier.notify_error(f"[Tournament] {msg}")  # notify_info 없으므로 재사용

        return tournament

    # ── Internal: 초기화 ─────────────────────────────────────────────────

    def _connect(self) -> None:
        self._connector = ExchangeConnector(
            exchange_name=self.cfg.exchange.name,
            sandbox=self.cfg.exchange.sandbox,
        )
        self._connector.connect()
        self._data_feed = DataFeed(self._connector)

    def _build_risk(self) -> None:
        cb = CircuitBreaker(
            max_daily_loss=self.cfg.risk.max_daily_loss,
            max_drawdown=self.cfg.risk.max_drawdown,
            max_consecutive_losses=self.cfg.risk.max_consecutive_losses,
            flash_crash_pct=self.cfg.risk.flash_crash_pct,
        )
        self._risk_manager = RiskManager(
            risk_per_trade=self.cfg.risk.risk_per_trade,
            atr_multiplier_sl=self.cfg.risk.stop_loss_atr_multiplier,
            atr_multiplier_tp=self.cfg.risk.take_profit_atr_multiplier,
            max_position_size=self.cfg.trading.max_position_size,
            circuit_breaker=cb,
        )

    def _load_strategy(self) -> None:
        strategy_cls = STRATEGY_REGISTRY.get(self.cfg.strategy)
        if strategy_cls is None:
            raise OrchestratorError(
                f"Unknown strategy '{self.cfg.strategy}'. "
                f"Available: {list(STRATEGY_REGISTRY)}"
            )
        self._strategy = strategy_cls()
        logger.info("Strategy loaded: %s", self._strategy.name)

    def _build_pipeline(self) -> None:
        self._pipeline = TradingPipeline(
            connector=self._connector,
            data_feed=self._data_feed,
            strategy=self._strategy,
            risk_manager=self._risk_manager,
            symbol=self.cfg.trading.symbol,
            timeframe=self.cfg.trading.timeframe,
            dry_run=self._dry_run,
        )

    def _build_notifier(self) -> TelegramNotifier:
        tg = self.cfg.telegram
        if tg is None:
            return TelegramNotifier(enabled=False)
        return TelegramNotifier(
            bot_token=tg.bot_token,
            chat_id=tg.chat_id,
            enabled=tg.enabled,
        )

    # ── Internal: Backtest gate ──────────────────────────────────────────

    def _backtest_gate(self) -> None:
        """live 전 backtest PASS 필수. FAIL이면 OrchestratorError."""
        logger.info("Backtest gate — validating strategy before live")
        result = self._run_backtest(self._strategy)
        print(result.summary())
        if not result.passed:
            msg = f"Backtest gate FAILED: {result.fail_reasons}"
            self._notifier.notify_error(msg)
            raise OrchestratorError(msg)
        logger.info("Backtest gate PASSED")

    def _run_backtest(self, strategy: BaseStrategy) -> BacktestResult:
        summary = self._data_feed.fetch(
            self.cfg.trading.symbol,
            self.cfg.trading.timeframe,
            limit=1000,
        )
        engine = BacktestEngine(
            atr_multiplier_sl=self.cfg.risk.stop_loss_atr_multiplier,
            atr_multiplier_tp=self.cfg.risk.take_profit_atr_multiplier,
        )
        return engine.run(strategy, summary.df)

    # ── Internal: 결과 처리 ──────────────────────────────────────────────

    def _handle_result(self, result: PipelineResult) -> None:
        self._print_result(result)
        self._notifier.notify_pipeline(result)
        self._append_worklog(result)

    def _print_result(self, result: PipelineResult) -> None:
        print(f"\nPIPELINE: {result.pipeline_step}")
        print(f"STATUS:   {result.status}")
        if result.signal:
            print(f"SIGNAL:   {result.signal.action.value} @ {result.signal.entry_price:.2f}"
                  f"  ({result.signal.confidence.value})")
            if result.signal.bull_case:
                print(f"  bull: {result.signal.bull_case}")
            if result.signal.bear_case:
                print(f"  bear: {result.signal.bear_case}")
        if result.risk:
            print(f"RISK:     {result.risk.status.value}", end="")
            if result.risk.reason:
                print(f" — {result.risk.reason}", end="")
            print()
            if result.risk.position_size:
                print(f"  size={result.risk.position_size}"
                      f"  SL={result.risk.stop_loss}"
                      f"  TP={result.risk.take_profit}")
        if result.execution:
            print(f"EXEC:     {result.execution.get('status')}")
        if result.notes:
            print(f"NOTES:    {' | '.join(result.notes)}")
        if result.error:
            print(f"ERROR:    {result.error}")

    def _append_worklog(self, result: PipelineResult) -> None:
        try:
            with open(".claude-state/WORKLOG.md", "a") as f:
                f.write("\n" + result.log_line())
        except OSError:
            pass

    def _assert_ready(self) -> None:
        if self._pipeline is None:
            raise OrchestratorError("Call startup() before run_once() / run_loop()")
