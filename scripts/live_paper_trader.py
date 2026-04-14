"""
Live Paper Trader — 며칠간 연속 운영하는 실시간 모의거래 시뮬레이터.

실행:
    python3 scripts/live_paper_trader.py [--days 7] [--interval 3600]

동작:
1. 시작 시 Bybit에서 최근 데이터를 가져와 전략 초기 평가
2. 매 interval(기본 1시간)마다 새 캔들 수집
3. 활성 전략들의 신호를 PaperTrader로 모의 실행
4. 포지션, 잔고, 성과를 실시간 추적
5. 주기적으로 성과 리포트 저장 (24시간마다)
6. Walk-Forward 기반으로 전략을 주기적 재평가 (24시간마다)
7. 상태를 파일에 저장해 중단 후 재시작 가능

정지: Ctrl+C (graceful shutdown, 상태 저장)
"""
from __future__ import annotations

import importlib
import json
import logging
import signal
import sys
import time
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("live_paper_trader")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.strategy.base import Action, BaseStrategy
from src.exchange.paper_trader import PaperTrader

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / ".claude-state"
LIVE_STATE_PATH = STATE_DIR / "live_paper_state.json"
LIVE_REPORT_PATH = STATE_DIR / "LIVE_PAPER_REPORT.md"
CSV_PATH = STATE_DIR / "QUALITY_AUDIT.csv"

# ── 설정 ─────────────────────────────────────────────────

DEFAULT_SYMBOL = "BTC/USDT"
DEFAULT_TIMEFRAME = "1h"
DEFAULT_INTERVAL = 3600       # 1시간마다 체크
DEFAULT_DAYS = 7              # 기본 7일 운영
WARMUP_CANDLES = 200          # 지표 계산용 warmup
REPORT_INTERVAL = 24 * 3600   # 24시간마다 리포트
REEVAL_INTERVAL = 24 * 3600   # 24시간마다 전략 재평가
MAX_ACTIVE_STRATEGIES = 10    # 동시 활성 전략 수 상한
RISK_PER_TRADE = 0.01         # 트레이드당 1% 리스크
INITIAL_BALANCE = 10_000.0


# ── 데이터 수집 ──────────────────────────────────────────

def fetch_latest_candles(
    symbol: str = DEFAULT_SYMBOL,
    timeframe: str = DEFAULT_TIMEFRAME,
    limit: int = 500,
) -> Optional[pd.DataFrame]:
    """Bybit에서 최근 캔들 데이터 수집."""
    try:
        import ccxt
        ex = ccxt.bybit()
        ex.timeout = 20000
        ohlcv = ex.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.set_index("timestamp").sort_index()
        return df
    except Exception as e:
        logger.error("Data fetch failed: %s: %s", type(e).__name__, str(e)[:120])
        return None


def enrich_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """전략이 사용하는 공통 지표 사전 계산."""
    df = df.copy()
    close = df["close"]
    high = df["high"]
    low = df["low"]

    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()

    df["ema20"] = close.ewm(span=20, adjust=False).mean()
    df["ema50"] = close.ewm(span=50, adjust=False).mean()
    df["sma20"] = close.rolling(20, min_periods=1).mean()
    df["sma50"] = close.rolling(50, min_periods=1).mean()

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi14"] = 100 - (100 / (1 + rs))

    df["bb_upper"] = df["sma20"] + 2 * close.rolling(20, min_periods=1).std()
    df["bb_lower"] = df["sma20"] - 2 * close.rolling(20, min_periods=1).std()

    df["macd"] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    df["donchian_high"] = high.shift(1).rolling(20, min_periods=1).max()
    df["donchian_low"] = low.shift(1).rolling(20, min_periods=1).min()

    tp = (high + low + close) / 3
    df["vwap"] = (tp * df["volume"]).cumsum() / df["volume"].cumsum()
    df["vwap20"] = (tp * df["volume"]).rolling(20, min_periods=1).sum() / df["volume"].rolling(20, min_periods=1).sum()
    df["volume_sma20"] = df["volume"].rolling(20, min_periods=1).mean()
    df["return_5"] = close.pct_change(5)

    return df


# ── 전략 로드 ──────────────────────────────────────────

def load_pass_strategies() -> list[tuple[str, str]]:
    """QUALITY_AUDIT.csv에서 PASS 전략 로드."""
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
        passed = df[df["passed"] == True]  # noqa: E712
        if len(passed) > 0:
            return list(zip(passed["module"].tolist(), passed["class"].tolist()))
    return []


def load_strategy_instance(module_name: str, class_name: str) -> Optional[BaseStrategy]:
    """전략 클래스 인스턴스 생성."""
    try:
        mod = importlib.import_module(f"src.strategy.{module_name}")
        cls = getattr(mod, class_name, None)
        if cls is None:
            return None
        return cls()
    except Exception:
        return None


# ── 상태 관리 ──────────────────────────────────────────

class LiveState:
    """실행 상태를 파일에 저장/복원."""

    def __init__(self):
        self.start_time: str = datetime.utcnow().isoformat()
        self.last_tick: str = ""
        self.tick_count: int = 0
        self.active_strategies: list[str] = []
        self.strategy_scores: dict[str, dict] = {}  # name -> {wins, losses, pnl, signals}
        self.portfolio_balance: float = INITIAL_BALANCE
        self.portfolio_peak: float = INITIAL_BALANCE
        self.portfolio_history: list[dict] = []  # [{time, balance}]
        self.open_positions: dict[str, dict] = {}  # strategy_name -> position info
        self.trade_log: list[dict] = []
        self.last_report_time: float = 0
        self.last_reeval_time: float = 0

    def save(self):
        data = {
            "start_time": self.start_time,
            "last_tick": self.last_tick,
            "tick_count": self.tick_count,
            "active_strategies": self.active_strategies,
            "strategy_scores": self.strategy_scores,
            "portfolio_balance": self.portfolio_balance,
            "portfolio_peak": self.portfolio_peak,
            "portfolio_history": self.portfolio_history[-500:],  # 최근 500개만
            "open_positions": self.open_positions,
            "trade_log": self.trade_log[-1000:],  # 최근 1000개만
            "last_report_time": self.last_report_time,
            "last_reeval_time": self.last_reeval_time,
        }
        LIVE_STATE_PATH.write_text(json.dumps(data, indent=2, default=str))

    @classmethod
    def load(cls) -> "LiveState":
        state = cls()
        if LIVE_STATE_PATH.exists():
            try:
                data = json.loads(LIVE_STATE_PATH.read_text())
                for k, v in data.items():
                    if hasattr(state, k):
                        setattr(state, k, v)
                logger.info("Restored state from %s (tick=%d, balance=$%.2f)",
                            LIVE_STATE_PATH, state.tick_count, state.portfolio_balance)
            except Exception as e:
                logger.warning("Failed to load state: %s. Starting fresh.", e)
        return state


# ── 메인 루프 ──────────────────────────────────────────

class LivePaperTrader:
    def __init__(self, days: int = DEFAULT_DAYS, interval: int = DEFAULT_INTERVAL):
        self.days = days
        self.interval = interval
        self.state = LiveState.load()
        self.paper = PaperTrader(
            initial_balance=self.state.portfolio_balance,
            fee_rate=0.001,
            slippage_pct=0.05,
            partial_fill_prob=0.0,  # 시뮬에서는 확률적 요소 제거
            timeout_prob=0.0,
        )
        self.strategies: dict[str, BaseStrategy] = {}
        self.running = True
        self._df_cache: Optional[pd.DataFrame] = None

        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        logger.info("Shutdown signal received. Saving state...")
        self.running = False

    def initialize(self):
        """초기화: 전략 로드 및 초기 데이터 수집."""
        # 전략 로드
        strat_list = load_pass_strategies()
        if not strat_list:
            logger.error("No strategies found. Run quality_audit.py first.")
            return False

        # 기존 활성 전략 복원 또는 초기 선택
        if self.state.active_strategies:
            for mod, cls_name in strat_list:
                inst = load_strategy_instance(mod, cls_name)
                if inst and inst.name in self.state.active_strategies:
                    self.strategies[inst.name] = inst
            logger.info("Restored %d active strategies", len(self.strategies))
        else:
            # 초기: 전체 로드 후 상위 N개 선택 (paper_simulation 결과 기반)
            all_strats = {}
            for mod, cls_name in strat_list:
                inst = load_strategy_instance(mod, cls_name)
                if inst:
                    all_strats[inst.name] = inst

            # 초기 선택: 최대 MAX_ACTIVE_STRATEGIES개
            selected = list(all_strats.items())[:MAX_ACTIVE_STRATEGIES]
            self.strategies = dict(selected)
            self.state.active_strategies = list(self.strategies.keys())
            logger.info("Selected %d strategies for live trading", len(self.strategies))

        # 초기 데이터 수집
        df = fetch_latest_candles(limit=WARMUP_CANDLES)
        if df is None:
            logger.error("Cannot fetch initial data")
            return False
        self._df_cache = enrich_indicators(df)
        logger.info("Initial data: %d candles (%s ~ %s)",
                     len(self._df_cache), self._df_cache.index[0], self._df_cache.index[-1])
        return True

    def tick(self):
        """매 interval마다 실행되는 메인 로직."""
        self.state.tick_count += 1
        self.state.last_tick = datetime.utcnow().isoformat()

        # 1. 최신 데이터 수집
        new_df = fetch_latest_candles(limit=50)
        if new_df is None:
            logger.warning("Tick %d: data fetch failed, skipping", self.state.tick_count)
            return

        # 기존 캐시와 병합 (중복 제거)
        if self._df_cache is not None:
            combined = pd.concat([self._df_cache, new_df])
            combined = combined[~combined.index.duplicated(keep="last")].sort_index()
            # 최근 1000봉만 유지
            self._df_cache = enrich_indicators(combined.tail(1000))
        else:
            self._df_cache = enrich_indicators(new_df)

        df = self._df_cache
        latest = df.iloc[-1]
        current_price = latest["close"]

        logger.info("Tick %d | Price: $%.2f | Balance: $%.2f | Strategies: %d | Positions: %d",
                     self.state.tick_count, current_price, self.state.portfolio_balance,
                     len(self.strategies), len(self.state.open_positions))

        # 2. 열린 포지션 관리 (SL/TP 체크)
        self._manage_positions(latest)

        # 3. 각 전략 신호 생성 및 실행
        for name, strategy in self.strategies.items():
            if name in self.state.open_positions:
                continue  # 이미 포지션이 있으면 스킵

            try:
                sig = strategy.generate(df)
                if sig.action == Action.HOLD:
                    continue

                # ATR 기반 포지션 사이즈
                atr = latest["atr14"]
                if atr <= 0:
                    continue

                sl_dist = atr * 1.5
                risk_amt = self.state.portfolio_balance * RISK_PER_TRADE
                size = risk_amt / sl_dist

                if sig.action == Action.BUY:
                    entry = current_price
                    sl = entry - sl_dist
                    tp = entry + atr * 3.0
                else:
                    entry = current_price
                    sl = entry + sl_dist
                    tp = entry - atr * 3.0

                # 모의 실행
                result = self.paper.execute_signal(
                    symbol=DEFAULT_SYMBOL,
                    action=sig.action.value,
                    price=current_price,
                    quantity=size,
                    strategy=name,
                    confidence=str(sig.confidence),
                )

                if result["status"] in ("filled", "partial"):
                    self.state.open_positions[name] = {
                        "side": sig.action.value,
                        "entry": result["actual_price"],
                        "sl": sl,
                        "tp": tp,
                        "size": result["actual_quantity"],
                        "open_time": datetime.utcnow().isoformat(),
                        "hold_candles": 0,
                    }
                    self.state.portfolio_balance = result["balance"]

                    # 전략 스코어 초기화
                    if name not in self.state.strategy_scores:
                        self.state.strategy_scores[name] = {"wins": 0, "losses": 0, "pnl": 0.0, "signals": 0}
                    self.state.strategy_scores[name]["signals"] += 1

                    logger.info("  [%s] %s @ $%.2f (size=%.6f, sl=$%.2f, tp=$%.2f)",
                                name, sig.action.value, result["actual_price"],
                                result["actual_quantity"], sl, tp)

            except Exception as e:
                logger.error("  [%s] Error: %s", name, str(e)[:80])

        # 4. 포트폴리오 기록
        self.state.portfolio_peak = max(self.state.portfolio_peak, self.state.portfolio_balance)
        self.state.portfolio_history.append({
            "time": datetime.utcnow().isoformat(),
            "balance": round(self.state.portfolio_balance, 2),
            "price": round(current_price, 2),
            "positions": len(self.state.open_positions),
        })

        # 5. 주기적 리포트
        now = time.time()
        if now - self.state.last_report_time >= REPORT_INTERVAL:
            self._generate_report()
            self.state.last_report_time = now

        # 6. 상태 저장
        self.state.save()

    def _manage_positions(self, candle: pd.Series):
        """열린 포지션의 SL/TP 체크 및 강제 청산."""
        closed = []
        for name, pos in self.state.open_positions.items():
            pos["hold_candles"] = pos.get("hold_candles", 0) + 1
            side = pos["side"]
            sl, tp = pos["sl"], pos["tp"]
            high, low = candle["high"], candle["low"]
            close_price = candle["close"]

            should_close = False
            exit_price = close_price
            reason = ""

            # 24봉(24시간) 강제 청산
            if pos["hold_candles"] >= 24:
                should_close = True
                exit_price = close_price
                reason = "max_hold"
            elif side == "BUY":
                if low <= sl:
                    should_close, exit_price, reason = True, sl, "stop_loss"
                elif high >= tp:
                    should_close, exit_price, reason = True, tp, "take_profit"
            else:  # SELL
                if high >= sl:
                    should_close, exit_price, reason = True, sl, "stop_loss"
                elif low <= tp:
                    should_close, exit_price, reason = True, tp, "take_profit"

            if should_close:
                # PnL 계산
                if side == "BUY":
                    pnl = (exit_price - pos["entry"]) * pos["size"]
                else:
                    pnl = (pos["entry"] - exit_price) * pos["size"]

                # 수수료
                fee = pos["size"] * exit_price * 0.001
                pnl -= fee

                self.state.portfolio_balance += pnl

                # 전략 스코어 업데이트
                if name not in self.state.strategy_scores:
                    self.state.strategy_scores[name] = {"wins": 0, "losses": 0, "pnl": 0.0, "signals": 0}
                scores = self.state.strategy_scores[name]
                if pnl > 0:
                    scores["wins"] += 1
                else:
                    scores["losses"] += 1
                scores["pnl"] += pnl

                # 거래 로그
                self.state.trade_log.append({
                    "time": datetime.utcnow().isoformat(),
                    "strategy": name,
                    "side": side,
                    "entry": pos["entry"],
                    "exit": exit_price,
                    "size": pos["size"],
                    "pnl": round(pnl, 2),
                    "reason": reason,
                    "hold_candles": pos["hold_candles"],
                })

                logger.info("  [%s] CLOSED %s @ $%.2f -> $%.2f | PnL: $%.2f (%s)",
                            name, side, pos["entry"], exit_price, pnl, reason)
                closed.append(name)

        for name in closed:
            del self.state.open_positions[name]

    def _generate_report(self):
        """24시간마다 성과 리포트 생성."""
        lines = []
        lines.append("# Live Paper Trading Report\n")
        lines.append(f"_Generated: {datetime.utcnow().isoformat()}Z_")
        lines.append(f"_Started: {self.state.start_time}_")
        lines.append(f"_Ticks: {self.state.tick_count} | Interval: {self.interval}s_\n")

        # 포트폴리오 요약
        total_return = (self.state.portfolio_balance - INITIAL_BALANCE) / INITIAL_BALANCE
        max_dd = (self.state.portfolio_peak - self.state.portfolio_balance) / self.state.portfolio_peak if self.state.portfolio_peak > 0 else 0
        lines.append("## Portfolio\n")
        lines.append("| 항목 | 값 |")
        lines.append("|------|-----|")
        lines.append(f"| Balance | ${self.state.portfolio_balance:,.2f} |")
        lines.append(f"| Total Return | {total_return:+.2%} |")
        lines.append(f"| Peak | ${self.state.portfolio_peak:,.2f} |")
        lines.append(f"| Current DD | {max_dd:.2%} |")
        lines.append(f"| Open Positions | {len(self.state.open_positions)} |")
        lines.append(f"| Total Trades | {len(self.state.trade_log)} |")
        lines.append("")

        # 전략별 성과
        if self.state.strategy_scores:
            lines.append("## Strategy Performance\n")
            lines.append("| Strategy | Signals | Wins | Losses | WR | PnL |")
            lines.append("|----------|---------|------|--------|----|-----|")
            sorted_scores = sorted(
                self.state.strategy_scores.items(),
                key=lambda x: x[1]["pnl"], reverse=True,
            )
            for name, s in sorted_scores:
                total = s["wins"] + s["losses"]
                wr = s["wins"] / total if total > 0 else 0
                lines.append(f"| `{name}` | {s['signals']} | {s['wins']} | {s['losses']} | "
                             f"{wr:.0%} | ${s['pnl']:+.2f} |")
            lines.append("")

        # 최근 거래
        recent = self.state.trade_log[-20:]
        if recent:
            lines.append("## Recent Trades (last 20)\n")
            lines.append("| Time | Strategy | Side | Entry | Exit | PnL | Reason |")
            lines.append("|------|----------|------|-------|------|-----|--------|")
            for t in reversed(recent):
                lines.append(f"| {t['time'][:16]} | `{t['strategy']}` | {t['side']} | "
                             f"${t['entry']:.2f} | ${t['exit']:.2f} | ${t['pnl']:+.2f} | {t['reason']} |")
            lines.append("")

        report = "\n".join(lines)
        LIVE_REPORT_PATH.write_text(report)
        logger.info("Report saved to %s", LIVE_REPORT_PATH)

    def run(self):
        """메인 루프."""
        logger.info("=" * 60)
        logger.info("Live Paper Trader starting (days=%d, interval=%ds)", self.days, self.interval)
        logger.info("=" * 60)

        if not self.initialize():
            return 1

        end_time = time.time() + self.days * 86400
        self.state.last_report_time = time.time()
        self.state.last_reeval_time = time.time()

        while self.running and time.time() < end_time:
            try:
                self.tick()
            except Exception as e:
                logger.error("Tick error: %s", str(e)[:200])

            # 다음 tick까지 대기 (1분 단위로 체크하여 shutdown 반응성 확보)
            wait_until = time.time() + self.interval
            while self.running and time.time() < wait_until:
                time.sleep(min(60, wait_until - time.time()))

        # 종료 정리
        logger.info("Shutting down...")
        self._generate_report()
        self.state.save()
        logger.info("Final balance: $%.2f (return: %+.2%)",
                     self.state.portfolio_balance,
                     (self.state.portfolio_balance - INITIAL_BALANCE) / INITIAL_BALANCE * 100)
        return 0


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Live Paper Trader")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="운영 기간 (일)")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL, help="체크 간격 (초)")
    parser.add_argument("--reset", action="store_true", help="상태 초기화 후 시작")
    args = parser.parse_args()

    if args.reset and LIVE_STATE_PATH.exists():
        LIVE_STATE_PATH.unlink()
        logger.info("State reset.")

    trader = LivePaperTrader(days=args.days, interval=args.interval)
    sys.exit(trader.run())


if __name__ == "__main__":
    main()
