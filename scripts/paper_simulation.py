"""
Paper Trading 시뮬레이션 — 실제 Bybit 데이터로 전략들을 Walk-Forward 방식으로 평가.

실행:
    python3 scripts/paper_simulation.py

동작:
1. Bybit public API로 BTC/USDT 1h 캔들 6개월치 페이지네이션 수집
2. QUALITY_AUDIT.csv에서 PASS 전략 목록 로드
3. Walk-Forward 방식: 훈련 4개월 → 테스트 1개월, 1개월씩 롤링 (최소 3윈도우)
4. 복수 윈도우에서 일관되게 실패해야 FAIL (단일 실패로 제거하지 않음)
5. 결과를 .claude-state/PAPER_SIMULATION_REPORT.md에 기록
"""
from __future__ import annotations

import importlib
import logging
import sys
import time
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

# Walk-Forward 설정
TRAIN_HOURS = 24 * 120   # 훈련: 4개월 (120일)
TEST_HOURS = 24 * 30     # 테스트: 1개월 (30일)
STEP_HOURS = 24 * 30     # 롤링 간격: 1개월
MIN_WINDOWS = 2          # 최소 테스트 윈도우 수

# 전략 통과 기준: 테스트 윈도우 중 과반수에서 통과해야 PASS
PASS_RATIO = 0.5  # 50% 이상 윈도우에서 통과


# ── 데이터 수집 ──────────────────────────────────────────────

TIMEFRAME_MS = {
    "1m": 60_000, "5m": 300_000, "15m": 900_000,
    "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000,
}


def fetch_real_data_paginated(
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    total_candles: int = 4320,  # 6개월 (180일 * 24h)
    batch_size: int = 1000,
) -> pd.DataFrame | None:
    """Bybit에서 페이지네이션으로 장기 OHLCV 데이터 수집. 실패 시 None."""
    try:
        import ccxt
        ex = ccxt.bybit()
        ex.timeout = 20000
        tf_ms = TIMEFRAME_MS.get(timeframe, 3_600_000)

        all_data = []
        # 현재 시각에서 total_candles만큼 역산
        now_ms = int(time.time() * 1000)
        since = now_ms - (total_candles * tf_ms)

        print(f"[DATA] Fetching {symbol} {timeframe} x{total_candles} from Bybit (paginated)...", flush=True)

        seen_ts: set = set()
        stall_count = 0  # 진전 없는 페이지 연속 횟수 (3회 시 중단)
        while len(all_data) < total_candles:
            ohlcv = ex.fetch_ohlcv(symbol, timeframe, since=since, limit=batch_size)
            if not ohlcv:
                break

            # 중복 제거하며 추가 (Bybit은 since와 겹치는 첫 봉을 반환할 수 있음)
            new_count = 0
            for row in ohlcv:
                if row[0] not in seen_ts:
                    seen_ts.add(row[0])
                    all_data.append(row)
                    new_count += 1

            if new_count == 0:
                stall_count += 1
                if stall_count >= 3:
                    break
            else:
                stall_count = 0

            # 다음 페이지: 마지막 캔들 + tf_ms
            since = ohlcv[-1][0] + tf_ms

            # 현재 시각 넘어가면 종료
            if since >= now_ms:
                break

            # Rate limit
            time.sleep(0.3)

        if not all_data:
            return None

        df = pd.DataFrame(all_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.drop_duplicates(subset=["timestamp"]).set_index("timestamp").sort_index()

        print(f"[DATA] Got {len(df)} candles: {df.index[0]} ~ {df.index[-1]} "
              f"({(df.index[-1] - df.index[0]).days}일)", flush=True)
        return df
    except Exception as e:
        print(f"[DATA] Bybit paginated fetch failed: {type(e).__name__}: {str(e)[:120]}", flush=True)
        return None


def enrich_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """전략이 사용하는 공통 지표 사전 계산 — feed.py와 동일한 방식."""
    df = df.copy()
    close = df["close"]
    high = df["high"]
    low = df["low"]

    # ATR 14 — Wilder EWM
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

    # RSI 14 — Wilder EWM
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

    # Donchian 20
    df["donchian_high"] = high.shift(1).rolling(20, min_periods=1).max()
    df["donchian_low"] = low.shift(1).rolling(20, min_periods=1).min()

    # VWAP
    tp = (high + low + close) / 3
    df["vwap"] = (tp * df["volume"]).cumsum() / df["volume"].cumsum()
    df["vwap20"] = (tp * df["volume"]).rolling(20, min_periods=1).sum() / df["volume"].rolling(20, min_periods=1).sum()

    # Volume SMA
    df["volume_sma20"] = df["volume"].rolling(20, min_periods=1).mean()
    df["return_5"] = close.pct_change(5)

    return df


# ── 전략 로드 ──────────────────────────────────────────────

def load_pass_strategies() -> list[tuple[str, str]]:
    """QUALITY_AUDIT.csv에서 PASS 전략만 로드."""
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
        passed = df[df["passed"] == True]  # noqa: E712
        if len(passed) > 0:
            return list(zip(passed["module"].tolist(), passed["class"].tolist()))
        print("[WARN] QUALITY_AUDIT.csv에 PASS 전략 0개. 전체 전략 로드 (최대 50개)")

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


# ── Walk-Forward 평가 ──────────────────────────────────────

def make_walk_forward_windows(df: pd.DataFrame) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    """데이터를 훈련/테스트 윈도우로 분할.
    Returns: [(train_df, test_df), ...]
    """
    n = len(df)
    windows = []
    start = 0

    while True:
        train_end = start + TRAIN_HOURS
        test_end = train_end + TEST_HOURS

        if test_end > n:
            break

        train_df = df.iloc[start:train_end]
        test_df = df.iloc[train_end:test_end]
        windows.append((train_df, test_df))

        start += STEP_HOURS

    # 최소 윈도우 수 미달 시 전체를 단일 윈도우로 사용
    if len(windows) < MIN_WINDOWS:
        split = int(n * 0.7)
        if split > 100 and n - split > 100:
            windows = [(df.iloc[:split], df.iloc[split:])]
            print(f"[WF] 데이터 부족으로 70/30 단일 분할 사용 (train={split}, test={n - split})")
        else:
            windows = [(df, df)]
            print(f"[WF] 데이터 너무 적어 전체 데이터 단일 평가")
    else:
        print(f"[WF] Walk-Forward {len(windows)}개 윈도우 생성 "
              f"(train={TRAIN_HOURS}h, test={TEST_HOURS}h, step={STEP_HOURS}h)")

    return windows


def evaluate_strategy_walk_forward(
    strategy_cls,
    windows: list[tuple[pd.DataFrame, pd.DataFrame]],
    engine: BacktestEngine,
) -> dict:
    """Walk-Forward로 전략을 평가. 각 윈도우의 테스트 구간에서 백테스트 실행.

    Returns:
        dict with keys: name, window_results, consistency_score, avg metrics, overall_passed
    """
    window_results = []
    strategy = strategy_cls()
    name = strategy.name

    for i, (train_df, test_df) in enumerate(windows):
        try:
            # 테스트 구간에서 백테스트 (훈련 데이터는 지표 warmup 용도로 앞에 붙임)
            # warmup으로 훈련 데이터 마지막 100봉을 테스트 앞에 붙임
            warmup = train_df.iloc[-100:] if len(train_df) > 100 else train_df
            eval_df = pd.concat([warmup, test_df])

            strategy_inst = strategy_cls()
            bt = engine.run(strategy_inst, eval_df)
            window_results.append({
                "window": i + 1,
                "sharpe": bt.sharpe_ratio,
                "total_return": bt.total_return,
                "max_dd": bt.max_drawdown,
                "profit_factor": bt.profit_factor,
                "trades": bt.total_trades,
                "win_rate": bt.win_rate,
                "passed": bt.passed,
                "final_balance": 10_000 * (1 + bt.total_return),
            })
        except Exception as e:
            window_results.append({
                "window": i + 1, "sharpe": 0, "total_return": 0, "max_dd": 0,
                "profit_factor": 0, "trades": 0, "win_rate": 0, "passed": False,
                "final_balance": 10_000, "error": str(e)[:80],
            })

    # 일관성 점수: 통과한 윈도우 비율
    passed_count = sum(1 for wr in window_results if wr["passed"])
    consistency = passed_count / len(window_results) if window_results else 0

    # 평균 지표 (에러 제외)
    valid = [wr for wr in window_results if "error" not in wr]
    avg_sharpe = np.mean([wr["sharpe"] for wr in valid]) if valid else 0
    avg_return = np.mean([wr["total_return"] for wr in valid]) if valid else 0
    avg_dd = np.mean([wr["max_dd"] for wr in valid]) if valid else 0
    avg_pf = np.mean([wr["profit_factor"] for wr in valid]) if valid else 0
    avg_trades = np.mean([wr["trades"] for wr in valid]) if valid else 0
    avg_wr = np.mean([wr["win_rate"] for wr in valid]) if valid else 0

    return {
        "name": name,
        "window_results": window_results,
        "consistency_score": consistency,
        "passed_windows": passed_count,
        "total_windows": len(window_results),
        "overall_passed": consistency >= PASS_RATIO,
        "avg_sharpe": avg_sharpe,
        "avg_return": avg_return,
        "avg_max_dd": avg_dd,
        "avg_profit_factor": avg_pf,
        "avg_trades": avg_trades,
        "avg_win_rate": avg_wr,
        "avg_final_balance": 10_000 * (1 + avg_return),
    }


# ── 리포트 ──────────────────────────────────────────────────

def generate_report(results: list[dict], data_source: str, df: pd.DataFrame, windows_count: int, symbol: str = "BTC/USDT") -> str:
    results.sort(key=lambda x: x["avg_return"], reverse=True)
    lines = []
    lines.append(f"# Paper Trading 시뮬레이션 리포트 — {symbol} (Walk-Forward)\n")
    lines.append(f"_Generated: {datetime.utcnow().isoformat()}Z_")
    lines.append(f"_Symbol: {symbol}_")
    lines.append(f"_Data Source: {data_source}_")
    lines.append(f"_Data Range: {df.index[0]} ~ {df.index[-1]} ({(df.index[-1] - df.index[0]).days}일)_")
    lines.append(f"_Walk-Forward: {windows_count}개 윈도우 (train={TRAIN_HOURS}h, test={TEST_HOURS}h)_")
    lines.append(f"_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_")
    lines.append(f"_통과 기준: 윈도우 {PASS_RATIO:.0%} 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_\n")

    # 요약
    passed_count = sum(1 for r in results if r["overall_passed"])
    failed_count = len(results) - passed_count
    lines.append("## 요약\n")
    lines.append("| 항목 | 값 |")
    lines.append("|------|-----|")
    lines.append(f"| 테스트 전략 | {len(results)}개 |")
    lines.append(f"| PASS (일관성 {PASS_RATIO:.0%}+) | {passed_count}개 |")
    lines.append(f"| FAIL | {failed_count}개 |")
    if results:
        avg_ret = np.mean([r["avg_return"] for r in results])
        lines.append(f"| 평균 수익률 | {avg_ret:.2%} |")
        lines.append(f"| 최고 수익률 | {results[0]['avg_return']:.2%} ({results[0]['name']}) |")
        lines.append(f"| 최저 수익률 | {results[-1]['avg_return']:.2%} ({results[-1]['name']}) |")
    lines.append("")

    # TOP 10
    lines.append("## TOP 10 전략 (평균 수익률 기준)\n")
    lines.append("| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |")
    lines.append("|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|")
    for i, r in enumerate(results[:10], 1):
        p = "PASS" if r["overall_passed"] else "FAIL"
        lines.append(
            f"| {i} | `{r['name']}` | {r['avg_return']:+.2%} | {r['avg_sharpe']:.2f} | "
            f"{r['avg_win_rate']:.1%} | {r['avg_profit_factor']:.2f} | {r['avg_trades']:.0f} | "
            f"{r['avg_max_dd']:.1%} | {r['passed_windows']}/{r['total_windows']} | {p} |"
        )
    lines.append("")

    # 전체 결과
    lines.append("## 전체 결과\n")
    lines.append("| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |")
    lines.append("|------|-----------|-----------|-------|-----------|-------------|------|")
    for r in results:
        p = "PASS" if r["overall_passed"] else "FAIL"
        lines.append(
            f"| `{r['name']}` | {r['avg_return']:+.2%} | {r['avg_sharpe']:.2f} | "
            f"{r['avg_profit_factor']:.2f} | {r['avg_trades']:.0f} | "
            f"{r['passed_windows']}/{r['total_windows']} | {p} |"
        )
    lines.append("")

    # 포트폴리오
    if results:
        passed_strats = [r for r in results if r["overall_passed"]]
        all_avg = np.mean([r["avg_return"] for r in results])
        lines.append("## 포트폴리오 가상 배분\n")
        lines.append(f"- **전체 {len(results)}개 균등배분**: {all_avg:+.2%} -> ${10_000*(1+all_avg):,.0f}")
        if passed_strats:
            pass_avg = np.mean([r["avg_return"] for r in passed_strats])
            lines.append(f"- **PASS {len(passed_strats)}개 균등배분**: {pass_avg:+.2%} -> ${10_000*(1+pass_avg):,.0f}")
        top5 = results[:5]
        if top5:
            t5_avg = np.mean([r["avg_return"] for r in top5])
            lines.append(f"- **Top 5 균등배분**: {t5_avg:+.2%} -> ${10_000*(1+t5_avg):,.0f}")
    lines.append("")

    return "\n".join(lines)


# ── 메인 ──────────────────────────────────────────────────

SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]  # 페이퍼 시뮬 대상 (live는 여전히 BTC만)


def simulate_symbol(symbol: str, pass_list: list, engine: BacktestEngine) -> str:
    """단일 심볼에 대한 walk-forward 시뮬을 돌리고 리포트 섹션을 반환."""
    print(f"\n{'=' * 70}\n[{symbol}] Walk-Forward Simulation\n{'=' * 70}")

    df = fetch_real_data_paginated(symbol, "1h", total_candles=4320)
    data_source = f"Bybit {symbol} 1h (paginated)"

    if df is None:
        print(f"[{symbol}][FALLBACK] Using synthetic data (Bybit API inaccessible)")
        from scripts.quality_audit import make_synthetic_data
        df = make_synthetic_data(4320)
        data_source = f"Synthetic GBM x4320 ({symbol}-like)"
    else:
        df = enrich_indicators(df)

    print(f"[{symbol}][DATA] Total candles: {len(df)}")

    windows = make_walk_forward_windows(df)

    results = []
    for idx, (mod_name, cls_name) in enumerate(pass_list):
        cls = load_strategy_class(mod_name, cls_name)
        if cls is None:
            continue
        try:
            result = evaluate_strategy_walk_forward(cls, windows, engine)
            results.append(result)
            if (idx + 1) % 50 == 0:
                print(f"[{symbol}][PROGRESS] {idx + 1}/{len(pass_list)} evaluated", flush=True)
        except Exception as e:
            print(f"[{symbol}][ERROR] {mod_name}: {str(e)[:80]}")

    passed = [r for r in results if r["overall_passed"]]
    print(f"[{symbol}][SUMMARY] {len(passed)}/{len(results)} PASSED (consistency >= {PASS_RATIO:.0%})")
    for r in sorted(passed, key=lambda x: x["avg_return"], reverse=True)[:5]:
        print(f"  {r['name']:<30} avg_return={r['avg_return']:+.2%} "
              f"sharpe={r['avg_sharpe']:.2f} consistency={r['passed_windows']}/{r['total_windows']}")

    return generate_report(results, data_source, df, len(windows), symbol=symbol)


def run_simulation():
    print("=" * 70)
    print(f"Paper Trading Simulation (Walk-Forward) — {datetime.utcnow().isoformat()}Z")
    print(f"Symbols: {', '.join(SYMBOLS)}")
    print("=" * 70)

    pass_list = load_pass_strategies()
    if not pass_list:
        print("[ERROR] 전략 없음. quality_audit.py 먼저 실행.")
        return 1
    print(f"[STRATEGIES] Loaded {len(pass_list)} strategies")

    engine = BacktestEngine(
        initial_balance=10_000,
        fee_rate=0.001,
        slippage_pct=0.0005,
    )

    sections = []
    for symbol in SYMBOLS:
        try:
            sections.append(simulate_symbol(symbol, pass_list, engine))
        except Exception as e:
            print(f"[{symbol}][FATAL] {e}")
            sections.append(f"# {symbol} 시뮬 실패\n\n{e}\n")

    header = (
        f"# Paper Trading 시뮬레이션 통합 리포트\n\n"
        f"_Generated: {datetime.utcnow().isoformat()}Z_\n"
        f"_Symbols: {', '.join(SYMBOLS)}_\n\n---\n\n"
    )
    REPORT_PATH.write_text(header + "\n\n---\n\n".join(sections))
    print(f"\n[REPORT] Saved to {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(run_simulation())
