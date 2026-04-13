"""
Paper Trading 시뮬레이션 — 실제 Bybit 데이터로 PASS 전략들을 가상 거래.

실행:
    python3 scripts/paper_simulation.py

동작:
1. Bybit public API로 BTC/USDT 1h 캔들 1000개 (41일) 가져옴
2. QUALITY_AUDIT.csv에서 PASS 전략 목록 로드
3. 각 전략을 BacktestEngine으로 실전 조건(fee+slippage)에서 평가
4. 결과를 .claude-state/PAPER_SIMULATION_REPORT.md에 기록
5. 포트폴리오 가상 잔고 변화 추적 (10,000 USDT 시작)

외부 API가 접근 불가능하면 mock 데이터로 폴백.
"""
from __future__ import annotations

import importlib
import inspect
import logging
import sys
import warnings
from datetime import datetime
from pathlib import Path

logging.getLogger().setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.strategy.base import BaseStrategy
from src.backtest.engine import BacktestEngine


ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / ".claude-state"
REPORT_PATH = STATE_DIR / "PAPER_SIMULATION_REPORT.md"
CSV_PATH = STATE_DIR / "QUALITY_AUDIT.csv"


def fetch_real_data(symbol: str = "BTC/USDT", timeframe: str = "1h", limit: int = 1000) -> pd.DataFrame | None:
    """Bybit에서 실제 OHLCV 데이터 가져오기. 실패 시 None."""
    try:
        import ccxt
        ex = ccxt.bybit()
        ex.timeout = 20000
        print(f"[DATA] Fetching {symbol} {timeframe} x{limit} from Bybit...", flush=True)
        ohlcv = ex.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.set_index("timestamp")
        print(f"[DATA] Got {len(df)} candles from {df.index[0]} to {df.index[-1]}", flush=True)
        return df
    except Exception as e:
        print(f"[DATA] Bybit fetch failed: {type(e).__name__}: {str(e)[:120]}", flush=True)
        return None


def enrich_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """전략이 사용하는 공통 지표 사전 계산 — feed.py와 동일한 방식."""
    df = df.copy()
    close = df["close"]
    high = df["high"]
    low = df["low"]

    # ATR 14 — Wilder EWM (feed.py와 동일)
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()

    # EMA / SMA
    df["ema20"] = close.ewm(span=20, adjust=False).mean()
    df["ema50"] = close.ewm(span=50, adjust=False).mean()
    df["sma20"] = close.rolling(20, min_periods=1).mean()
    df["sma50"] = close.rolling(50, min_periods=1).mean()

    # RSI 14 — Wilder EWM (feed.py와 동일)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi14"] = 100 - (100 / (1 + rs))

    # BB
    df["bb_upper"] = df["sma20"] + 2 * close.rolling(20, min_periods=1).std()
    df["bb_lower"] = df["sma20"] - 2 * close.rolling(20, min_periods=1).std()

    # MACD
    df["macd"] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    # Donchian 20 — 이전 20봉 기준 (feed.py와 동일, 현재 봉 미포함)
    df["donchian_high"] = high.shift(1).rolling(20, min_periods=1).max()
    df["donchian_low"] = low.shift(1).rolling(20, min_periods=1).min()

    # VWAP (cumulative)
    tp = (high + low + close) / 3
    df["vwap"] = (tp * df["volume"]).cumsum() / df["volume"].cumsum()
    df["vwap20"] = (tp * df["volume"]).rolling(20, min_periods=1).sum() / df["volume"].rolling(20, min_periods=1).sum()

    # Volume SMA
    df["volume_sma20"] = df["volume"].rolling(20, min_periods=1).mean()
    df["return_5"] = close.pct_change(5)

    return df


def load_pass_strategies() -> list[tuple[str, str]]:
    """QUALITY_AUDIT.csv에서 PASS 전략만 로드.
    CSV가 없거나 PASS가 0이면 전체 전략 중 상위 50개로 제한."""
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
        passed = df[df["passed"] == True]  # noqa: E712
        if len(passed) > 0:
            return list(zip(passed["module"].tolist(), passed["class"].tolist()))
        print("[WARN] QUALITY_AUDIT.csv에 PASS 전략 0개. 전체 전략 로드 (최대 50개)")

    # CSV 없거나 PASS 0 → 전체 전략 중 상위 50개만
    from scripts.quality_audit import find_strategy_classes
    all_strats = find_strategy_classes()
    print(f"[INFO] 전체 전략 {len(all_strats)}개 중 상위 50개 로드")
    return [(mod, cls_name) for mod, cls_name, _ in all_strats[:50]]


def load_strategy_class(module_name: str, class_name: str):
    """모듈에서 전략 클래스 동적 로드."""
    try:
        mod = importlib.import_module(f"src.strategy.{module_name}")
        return getattr(mod, class_name, None)
    except Exception:
        return None


def run_simulation():
    print("=" * 70)
    print(f"Paper Trading Simulation — {datetime.utcnow().isoformat()}Z")
    print("=" * 70)

    # 1. 실제 데이터 시도
    df = fetch_real_data("BTC/USDT", "1h", 1000)
    data_source = "Bybit BTC/USDT 1h x1000"

    if df is None:
        print("[FALLBACK] Using synthetic data (Bybit API inaccessible in sandbox)")
        from scripts.quality_audit import make_synthetic_data
        df = make_synthetic_data(1000)
        data_source = "Synthetic GBM x1000 (BTC-like)"
    else:
        df = enrich_indicators(df)

    # 2. PASS 전략 로드
    pass_list = load_pass_strategies()
    if not pass_list:
        print("[ERROR] QUALITY_AUDIT.csv에 PASS 전략이 없음. quality_audit.py 먼저 실행.")
        return 1
    print(f"[STRATEGIES] Loaded {len(pass_list)} PASS strategies")

    # 3. 백테스트 엔진 (실전 비용 반영)
    engine = BacktestEngine(
        initial_balance=10_000,
        fee_rate=0.001,   # 0.1%
        slippage_pct=0.0005,  # 0.05%
    )

    # 4. 각 전략 백테스트
    results = []
    for mod_name, cls_name in pass_list:
        cls = load_strategy_class(mod_name, cls_name)
        if cls is None:
            continue
        try:
            strategy = cls()
            bt = engine.run(strategy, df)
            results.append({
                "name": strategy.name,
                "module": mod_name,
                "sharpe": bt.sharpe_ratio,
                "total_return": bt.total_return,
                "max_dd": bt.max_drawdown,
                "profit_factor": bt.profit_factor,
                "trades": bt.total_trades,
                "win_rate": bt.win_rate,
                "total_fees": bt.total_fees,
                "total_slippage_cost": bt.total_slippage_cost,
                "passed": bt.passed,
                "final_balance": 10_000 * (1 + bt.total_return),
            })
        except Exception as e:
            print(f"[ERROR] {mod_name}: {str(e)[:80]}")

    results.sort(key=lambda x: x["total_return"], reverse=True)

    # 5. 리포트 작성
    lines = []
    lines.append("# Paper Trading 시뮬레이션 리포트\n")
    lines.append(f"_Generated: {datetime.utcnow().isoformat()}Z_")
    lines.append(f"_Data Source: {data_source}_")
    lines.append(f"_Initial Balance: $10,000 USDT_")
    lines.append(f"_Fee: 0.1% | Slippage: 0.05%_\n")

    lines.append("## 📊 요약\n")
    lines.append(f"| 항목 | 값 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 테스트된 전략 | {len(results)}개 |")
    lines.append(f"| 수익 전략 | {sum(1 for r in results if r['total_return'] > 0)}개 |")
    lines.append(f"| 손실 전략 | {sum(1 for r in results if r['total_return'] <= 0)}개 |")
    if results:
        best = results[0]
        worst = results[-1]
        avg_return = np.mean([r["total_return"] for r in results])
        lines.append(f"| 평균 수익률 | {avg_return:.2%} |")
        lines.append(f"| 최고 수익률 | {best['total_return']:.2%} ({best['name']}) |")
        lines.append(f"| 최저 수익률 | {worst['total_return']:.2%} ({worst['name']}) |")
    lines.append("")

    # Top 10 테이블
    lines.append("## 🏆 TOP 10 전략 (수익률 기준)\n")
    lines.append("| # | Name | Return | Sharpe | WR | PF | Trades | MDD | Final Balance |")
    lines.append("|---|------|--------|--------|-----|-----|--------|-----|---------------|")
    for i, r in enumerate(results[:10], 1):
        lines.append(
            f"| {i} | `{r['name']}` | {r['total_return']:+.2%} | {r['sharpe']:.2f} | "
            f"{r['win_rate']:.1%} | {r['profit_factor']:.2f} | {r['trades']} | "
            f"{r['max_dd']:.1%} | ${r['final_balance']:,.0f} |"
        )
    lines.append("")

    # 전체 테이블
    lines.append("## 📋 전체 결과\n")
    lines.append("| Name | Return | Sharpe | PF | Trades | Final | Passed |")
    lines.append("|------|--------|--------|-----|--------|-------|--------|")
    for r in results:
        p = "✅" if r["passed"] else "❌"
        lines.append(
            f"| `{r['name']}` | {r['total_return']:+.2%} | {r['sharpe']:.2f} | "
            f"{r['profit_factor']:.2f} | {r['trades']} | ${r['final_balance']:,.0f} | {p} |"
        )
    lines.append("")

    # 포트폴리오 가상 시뮬 (균등 배분)
    if results:
        equal_weight_return = np.mean([r["total_return"] for r in results])
        top10_return = np.mean([r["total_return"] for r in results[:10]])
        lines.append("## 💼 포트폴리오 가상 배분\n")
        lines.append(f"- **균등 배분 (전체 {len(results)}개)**: {equal_weight_return:+.2%} → ${10_000*(1+equal_weight_return):,.0f}")
        lines.append(f"- **Top 10 균등 배분**: {top10_return:+.2%} → ${10_000*(1+top10_return):,.0f}")
        lines.append("")

    REPORT_PATH.write_text("\n".join(lines))
    print(f"\n[REPORT] Saved to {REPORT_PATH}")
    print(f"[TOP 3]")
    for r in results[:3]:
        print(f"  {r['name']:<30} return={r['total_return']:+.2%} sharpe={r['sharpe']:.2f}")

    return 0


if __name__ == "__main__":
    sys.exit(run_simulation())
