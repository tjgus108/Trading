"""
MultiBot: 여러 심볼을 병렬로 운용하는 오케스트레이터 풀.

- 심볼별로 독립적인 BotOrchestrator 인스턴스 실행
- 포트폴리오 전체 리스크 합산 및 한도 관리
- 각 봇이 별도 스레드에서 독립적으로 동작
- Ctrl+C 시 전체 graceful shutdown
"""

import logging
import threading
from dataclasses import dataclass
from typing import Optional

from src.config import AppConfig
from src.orchestrator import BotOrchestrator, OrchestratorError

logger = logging.getLogger(__name__)


@dataclass
class SymbolConfig:
    """심볼별 오버라이드 설정. None이면 AppConfig 기본값 사용."""
    symbol: str
    strategy: Optional[str] = None
    max_position_size: Optional[float] = None


class MultiBot:
    """
    여러 심볼을 병렬 운용하는 봇 풀.

    사용 예:
        symbols = [
            SymbolConfig("BTC/USDT", strategy="donchian_breakout"),
            SymbolConfig("ETH/USDT", strategy="ema_cross", max_position_size=0.05),
        ]
        multi = MultiBot(cfg, symbols, max_total_exposure=0.30)
        multi.startup(dry_run=True)
        multi.run_loop()
    """

    def __init__(
        self,
        base_cfg: AppConfig,
        symbols: list[SymbolConfig],
        max_total_exposure: float = 0.30,   # 전체 포트폴리오 최대 노출 30%
    ):
        self._base_cfg = base_cfg
        self._symbols = symbols
        self._max_total_exposure = max_total_exposure
        self._bots: dict[str, BotOrchestrator] = {}
        self._threads: dict[str, threading.Thread] = {}
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    # ── Public API ────────────────────────────────────────────────────────

    def startup(self, dry_run: bool = True) -> None:
        """모든 심볼 봇 초기화."""
        for sym_cfg in self._symbols:
            cfg = self._make_cfg(sym_cfg)
            bot = BotOrchestrator(cfg)
            try:
                bot.startup(dry_run=dry_run)
                self._bots[sym_cfg.symbol] = bot
                logger.info("MultiBot: %s started", sym_cfg.symbol)
            except Exception as e:
                logger.error("MultiBot: %s startup failed: %s", sym_cfg.symbol, e)

        if not self._bots:
            raise OrchestratorError("No bots started successfully")
        logger.info("MultiBot: %d/%d bots active", len(self._bots), len(self._symbols))

    def run_loop(self) -> None:
        """각 봇을 별도 스레드에서 루프 실행. Ctrl+C로 전체 종료."""
        for symbol, bot in self._bots.items():
            t = threading.Thread(
                target=self._bot_loop,
                args=(symbol, bot),
                name=f"bot-{symbol}",
                daemon=True,
            )
            self._threads[symbol] = t
            t.start()
            logger.info("MultiBot: thread started for %s", symbol)

        try:
            # 메인 스레드는 모니터링
            while not self._stop_event.is_set():
                self._stop_event.wait(timeout=60)
                if not self._stop_event.is_set():
                    self._log_portfolio_status()
        except KeyboardInterrupt:
            logger.info("MultiBot: KeyboardInterrupt — stopping all bots")
        finally:
            self.stop()
            self._join_all()

    def stop(self) -> None:
        """전체 봇 종료 신호."""
        self._stop_event.set()
        for bot in self._bots.values():
            bot.stop()

    def run_once_all(self) -> dict[str, object]:
        """모든 봇을 병렬로 1회 실행. 결과 딕셔너리 반환."""
        results = {}
        with threading.Lock():
            futures = {}
            with __import__("concurrent.futures", fromlist=["ThreadPoolExecutor"]).ThreadPoolExecutor(
                max_workers=len(self._bots)
            ) as pool:
                for symbol, bot in self._bots.items():
                    futures[pool.submit(bot.run_once)] = symbol
                for fut in __import__("concurrent.futures", fromlist=["as_completed"]).as_completed(futures):
                    symbol = futures[fut]
                    try:
                        results[symbol] = fut.result()
                    except Exception as e:
                        logger.error("MultiBot: %s run_once failed: %s", symbol, e)
                        results[symbol] = None
        return results

    def total_exposure(self) -> float:
        """현재 열린 포지션의 전체 노출 합산 (0~1)."""
        total = 0.0
        for bot in self._bots.values():
            pos = bot.tracker.open_count()
            if pos > 0:
                total += bot.cfg.trading.max_position_size
        return total

    def portfolio_summary(self) -> str:
        lines = ["PORTFOLIO STATUS:"]
        total_pnl = 0.0
        for symbol, bot in self._bots.items():
            pnl = bot.tracker.today_pnl()
            total_pnl += pnl
            open_pos = "OPEN" if bot.tracker.has_position(symbol) else "flat"
            lines.append(f"  {symbol:15s}  pnl={pnl:+.2f}  {open_pos}")
        lines.append(f"  TOTAL pnl={total_pnl:+.2f}  exposure={self.total_exposure():.0%}")
        return "\n".join(lines)

    # ── Internal ──────────────────────────────────────────────────────────

    def _make_cfg(self, sym_cfg: SymbolConfig) -> AppConfig:
        """심볼별 설정 생성. 기본 AppConfig를 복사 후 오버라이드."""
        import copy
        cfg = copy.deepcopy(self._base_cfg)
        cfg.trading.symbol = sym_cfg.symbol
        if sym_cfg.strategy:
            cfg.strategy = sym_cfg.strategy
        if sym_cfg.max_position_size is not None:
            cfg.trading.max_position_size = sym_cfg.max_position_size
        return cfg

    def _bot_loop(self, symbol: str, bot: BotOrchestrator) -> None:
        """개별 봇 스레드 실행."""
        try:
            bot.run_loop()
        except Exception as e:
            logger.error("MultiBot: %s thread crashed: %s", symbol, e)

    def _log_portfolio_status(self) -> None:
        exposure = self.total_exposure()
        if exposure > self._max_total_exposure:
            logger.warning("Portfolio exposure %.0f%% exceeds limit %.0f%%",
                           exposure * 100, self._max_total_exposure * 100)
        else:
            logger.info("%s", self.portfolio_summary())

    def _join_all(self) -> None:
        for symbol, t in self._threads.items():
            t.join(timeout=5)
            if t.is_alive():
                logger.warning("MultiBot: %s thread did not stop cleanly", symbol)
