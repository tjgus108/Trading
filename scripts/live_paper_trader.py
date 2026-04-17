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
from src.strategy.rotation import StrategyRotationManager
from src.strategy.regime import MarketRegimeDetector
from src.exchange.paper_trader import PaperTrader

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / ".claude-state"
LIVE_STATE_PATH = STATE_DIR / "live_paper_state.json"
LIVE_REPORT_PATH = STATE_DIR / "LIVE_PAPER_REPORT.md"
CSV_PATH = STATE_DIR / "QUALITY_AUDIT.csv"

# ── 설정 ─────────────────────────────────────────────────

SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
DEFAULT_TIMEFRAME = "1h"
DEFAULT_INTERVAL = 3600       # 1시간마다 체크
DEFAULT_DAYS = 7              # 기본 7일 운영
WARMUP_CANDLES = 200          # 지표 계산용 warmup
REPORT_INTERVAL = 24 * 3600   # 24시간마다 리포트
REEVAL_INTERVAL = 24 * 3600   # 24시간마다 전략 재평가
MAX_ACTIVE_STRATEGIES = 5     # 동시 활성 전략 수 상한
RISK_PER_TRADE = 0.005        # 트레이드당 0.5% 리스크
MAX_TOTAL_EXPOSURE = 0.30     # 전체 포트폴리오 최대 노출 30% (3심볼)
MAX_CONCURRENT_POSITIONS = 5  # 동시 포지션 최대 5개 (3심볼 합산)
MAX_PER_SYMBOL_POSITIONS = 2  # 심볼당 최대 2개
SL_ATR_MULT = 2.5             # SL = ATR * 2.5 (기존 1.5 → 노이즈 방지)
TP_ATR_MULT = 4.0             # TP = ATR * 4.0 (기존 3.0 → R:R 1.6)
MAX_HOLD_CANDLES = 48         # 48시간 강제 청산 (기존 24)
INITIAL_BALANCE = 10_000.0


# ── 데이터 수집 ──────────────────────────────────────────

def fetch_latest_candles(
    symbol: str = "BTC/USDT",
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
        self.active_strategies: dict[str, list[str]] = {}  # symbol -> [strategy_names]
        self.strategy_scores: dict[str, dict] = {}  # "symbol:name" -> {wins, losses, pnl, signals}
        self.portfolio_balance: float = INITIAL_BALANCE
        self.portfolio_peak: float = INITIAL_BALANCE
        self.portfolio_history: list[dict] = []
        self.open_positions: dict[str, dict] = {}  # "symbol:strategy" -> position info
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
            slippage_pct=0.0005,
            partial_fill_prob=0.0,
            timeout_prob=0.0,
        )
        self.symbol_strategies: dict[str, dict[str, BaseStrategy]] = {}  # symbol -> {name: strategy}
        self.rotation = StrategyRotationManager()
        self.regime_detector = MarketRegimeDetector()
        self.running = True
        self._df_caches: dict[str, pd.DataFrame] = {}  # symbol -> df

        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        logger.info("Shutdown signal received. Saving state...")
        self.running = False

    def initialize(self):
        """초기화: 심볼별 전략 로드 및 초기 데이터 수집."""
        strat_list = load_pass_strategies()
        if not strat_list:
            logger.error("No strategies found. Run quality_audit.py first.")
            return False

        all_strats = {}
        for mod, cls_name in strat_list:
            inst = load_strategy_instance(mod, cls_name)
            if inst:
                all_strats[inst.name] = inst

        for symbol in SYMBOLS:
            rotation_pass = self.rotation.get_active_strategies(symbol)
            sym_strats = {}

            if rotation_pass:
                for name in rotation_pass[:MAX_ACTIVE_STRATEGIES]:
                    if name in all_strats:
                        sym_strats[name] = all_strats[name]
                logger.info("[%s] Rotation PASS: %s", symbol, list(sym_strats.keys()))
            elif symbol in self.state.active_strategies and self.state.active_strategies[symbol]:
                for name in self.state.active_strategies[symbol]:
                    if name in all_strats:
                        sym_strats[name] = all_strats[name]
                logger.info("[%s] Restored %d strategies", symbol, len(sym_strats))

            if not sym_strats:
                selected = list(all_strats.items())[:MAX_ACTIVE_STRATEGIES]
                sym_strats = dict(selected)
                logger.info("[%s] Fallback: %d strategies", symbol, len(sym_strats))

            self.symbol_strategies[symbol] = sym_strats
            self.state.active_strategies[symbol] = list(sym_strats.keys())

            df = fetch_latest_candles(symbol=symbol, limit=WARMUP_CANDLES)
            if df is not None:
                self._df_caches[symbol] = enrich_indicators(df)
                logger.info("[%s] Data: %d candles", symbol, len(self._df_caches[symbol]))
            else:
                logger.warning("[%s] Initial data fetch failed", symbol)

        if not self._df_caches:
            logger.error("No data for any symbol")
            return False
        return True

    def tick(self):
        """매 interval마다 실행: 모든 심볼 순회."""
        self.state.tick_count += 1
        self.state.last_tick = datetime.utcnow().isoformat()

        for symbol in SYMBOLS:
            self._tick_symbol(symbol)

        self.state.portfolio_peak = max(self.state.portfolio_peak, self.state.portfolio_balance)
        self.state.portfolio_history.append({
            "time": datetime.utcnow().isoformat(),
            "balance": round(self.state.portfolio_balance, 2),
            "positions": len(self.state.open_positions),
        })

        now = time.time()
        if now - self.state.last_report_time >= REPORT_INTERVAL:
            self._generate_report()
            self.state.last_report_time = now

        self.state.save()

    def _tick_symbol(self, symbol: str):
        """단일 심볼에 대한 tick 로직."""
        new_df = fetch_latest_candles(symbol=symbol, limit=50)
        if new_df is None:
            return

        if symbol in self._df_caches:
            combined = pd.concat([self._df_caches[symbol], new_df])
            combined = combined[~combined.index.duplicated(keep="last")].sort_index()
            self._df_caches[symbol] = enrich_indicators(combined.tail(1000))
        else:
            self._df_caches[symbol] = enrich_indicators(new_df)

        df = self._df_caches[symbol]
        latest = df.iloc[-1]
        current_price = float(latest["close"])

        regime = self.regime_detector.detect(df)

        sym_positions = {k: v for k, v in self.state.open_positions.items() if k.startswith(f"{symbol}:")}

        logger.info("[%s] Tick %d | $%.2f | %s | pos=%d/%d",
                     symbol, self.state.tick_count, current_price,
                     regime.value, len(sym_positions), MAX_PER_SYMBOL_POSITIONS)

        self._manage_positions_for_symbol(symbol, latest)

        strategies = self.symbol_strategies.get(symbol, {})
        for name, strategy in strategies.items():
            pos_key = f"{symbol}:{name}"
            if pos_key in self.state.open_positions:
                continue

            if len(self.state.open_positions) >= MAX_CONCURRENT_POSITIONS:
                break
            sym_positions = {k: v for k, v in self.state.open_positions.items() if k.startswith(f"{symbol}:")}
            if len(sym_positions) >= MAX_PER_SYMBOL_POSITIONS:
                break

            current_exposure = self._total_exposure_all()
            if current_exposure >= MAX_TOTAL_EXPOSURE:
                break

            try:
                sig = strategy.generate(df)
                if sig.action == Action.HOLD:
                    continue

                atr = float(latest["atr14"])
                if atr <= 0:
                    continue

                sl_dist = atr * SL_ATR_MULT
                risk_amt = self.state.portfolio_balance * RISK_PER_TRADE
                size = risk_amt / sl_dist

                max_size = (self.state.portfolio_balance * 0.10) / current_price
                size = min(size, max_size)

                if size * current_price < 10:
                    continue

                if sig.action == Action.BUY:
                    sl = current_price - sl_dist
                    tp = current_price + atr * TP_ATR_MULT
                else:
                    sl = current_price + sl_dist
                    tp = current_price - atr * TP_ATR_MULT

                result = self.paper.execute_signal(
                    symbol=symbol,
                    action=sig.action.value,
                    price=current_price,
                    quantity=size,
                    strategy=name,
                    confidence=str(sig.confidence),
                )

                if result["status"] in ("filled", "partial"):
                    self.state.open_positions[pos_key] = {
                        "symbol": symbol,
                        "side": sig.action.value,
                        "entry": result["actual_price"],
                        "sl": sl,
                        "tp": tp,
                        "size": result["actual_quantity"],
                        "open_time": datetime.utcnow().isoformat(),
                        "hold_candles": 0,
                    }
                    self.state.portfolio_balance = result["balance"]

                    score_key = pos_key
                    if score_key not in self.state.strategy_scores:
                        self.state.strategy_scores[score_key] = {"wins": 0, "losses": 0, "pnl": 0.0, "signals": 0}
                    self.state.strategy_scores[score_key]["signals"] += 1

                    logger.info("  [%s:%s] %s @ $%.2f (size=%.6f)",
                                symbol, name, sig.action.value, result["actual_price"], result["actual_quantity"])

            except Exception as e:
                logger.error("  [%s:%s] Error: %s", symbol, name, str(e)[:80])

    def _total_exposure_all(self) -> float:
        """모든 심볼의 열린 포지션 전체 노출 비율 (0~1)."""
        if self.state.portfolio_balance <= 0:
            return 1.0
        total_value = 0.0
        for key, pos in self.state.open_positions.items():
            symbol = pos.get("symbol", key.split(":")[0])
            df = self._df_caches.get(symbol)
            if df is not None and len(df) > 0:
                price = float(df.iloc[-1]["close"])
            else:
                price = pos["entry"]
            total_value += pos["size"] * price
        return total_value / self.state.portfolio_balance

    def _manage_positions_for_symbol(self, symbol: str, candle: pd.Series):
        """특정 심볼의 열린 포지션 SL/TP 체크 및 강제 청산."""
        closed = []
        prefix = f"{symbol}:"
        for name, pos in self.state.open_positions.items():
            if not name.startswith(prefix):
                continue

            pos["hold_candles"] = pos.get("hold_candles", 0) + 1
            side = pos["side"]
            sl, tp = pos["sl"], pos["tp"]
            high, low = candle["high"], candle["low"]
            close_price = candle["close"]

            should_close = False
            exit_price = close_price
            reason = ""

            if pos["hold_candles"] >= MAX_HOLD_CANDLES:
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
                if side == "BUY":
                    pnl = (exit_price - pos["entry"]) * pos["size"]
                else:
                    pnl = (pos["entry"] - exit_price) * pos["size"]

                fee = pos["size"] * exit_price * 0.001
                pnl -= fee

                self.state.portfolio_balance += pnl

                if name not in self.state.strategy_scores:
                    self.state.strategy_scores[name] = {"wins": 0, "losses": 0, "pnl": 0.0, "signals": 0}
                scores = self.state.strategy_scores[name]
                if pnl > 0:
                    scores["wins"] += 1
                else:
                    scores["losses"] += 1
                scores["pnl"] += pnl

                self.state.trade_log.append({
                    "time": datetime.utcnow().isoformat(),
                    "strategy": name,
                    "symbol": symbol,
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
        lines.append(f"_Ticks: {self.state.tick_count} | Interval: {self.interval}s_")
        lines.append(f"_Symbols: {', '.join(SYMBOLS)}_\n")

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

        for symbol in SYMBOLS:
            sym_positions = {k: v for k, v in self.state.open_positions.items() if k.startswith(f"{symbol}:")}
            sym_trades = [t for t in self.state.trade_log if t.get("symbol") == symbol or t.get("strategy", "").startswith(f"{symbol}:")]
            sym_pnl = sum(t["pnl"] for t in sym_trades)
            lines.append(f"### {symbol}\n")
            lines.append(f"- Open: {len(sym_positions)} | Trades: {len(sym_trades)} | PnL: ${sym_pnl:+.2f}")
            strats = self.state.active_strategies.get(symbol, [])
            if strats:
                lines.append(f"- Strategies: {', '.join(strats)}")
            lines.append("")

        if self.state.strategy_scores:
            lines.append("## Strategy Performance\n")
            lines.append("| Symbol:Strategy | Signals | Wins | Losses | WR | PnL |")
            lines.append("|----------------|---------|------|--------|----|-----|")
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

        recent = self.state.trade_log[-20:]
        if recent:
            lines.append("## Recent Trades (last 20)\n")
            lines.append("| Time | Symbol:Strategy | Side | Entry | Exit | PnL | Reason |")
            lines.append("|------|----------------|------|-------|------|-----|--------|")
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
        ret = (self.state.portfolio_balance - INITIAL_BALANCE) / INITIAL_BALANCE * 100
        logger.info("Final balance: $%.2f (return: %+.2f%%)",
                     self.state.portfolio_balance, ret)
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
