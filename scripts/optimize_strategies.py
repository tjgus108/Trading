"""
전략 파라미터 최적화 + 레짐별 필터링.

실제 Bybit 데이터로 상위 전략의 파라미터를 grid search 최적화하고,
레짐별(TREND_UP/DOWN, RANGING, HIGH_VOL) 성과를 분석한다.

사용:
    python scripts/optimize_strategies.py [--symbol BTC/USDT] [--limit 4320]
"""
from __future__ import annotations

import sys
import time
import logging
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.backtest.engine import BacktestEngine
from src.strategy.regime import MarketRegimeDetector, MarketRegime
from scripts.live_paper_trader import enrich_indicators

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("optimizer")

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / ".claude-state" / "OPTIMIZATION_REPORT.md"

# ── 데이터 수집 ────────────────────────────────────────────

def fetch_bybit(symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
    import ccxt
    tf_ms = {"1h": 3_600_000, "4h": 14_400_000}
    interval_ms = tf_ms.get(timeframe, 3_600_000)
    ex = ccxt.bybit()
    ex.timeout = 30000
    now_ms = int(time.time() * 1000)
    since = now_ms - limit * interval_ms
    all_ohlcv = []
    stall = 0
    while len(all_ohlcv) < limit and since < now_ms:
        batch = ex.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
        if not batch:
            stall += 1
            if stall >= 3:
                break
            since += 1000 * interval_ms
            continue
        stall = 0
        all_ohlcv.extend(batch)
        since = batch[-1][0] + interval_ms
        time.sleep(0.3)
    seen = set()
    deduped = [r for r in all_ohlcv if r[0] not in seen and not seen.add(r[0])]
    deduped.sort(key=lambda x: x[0])
    deduped = deduped[:limit]
    df = pd.DataFrame(deduped, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.set_index("timestamp").sort_index()
    logger.info("Fetched %d candles (%s ~ %s)", len(df), df.index[0], df.index[-1])
    return df


# ── 전략별 파라미터 그리드 ────────────────────────────────

# 전략별 파라미터 그리드
# type: "module" = 모듈 레벨 상수, "class" = 클래스 속성
PARAM_GRIDS = {
    "relative_volume": {
        "module": "relative_volume",
        "type": "module",
        "constants": {
            "_RVOL_BUY_SELL": [1.3, 1.6, 2.0],
            "_RSI_BUY_MAX": [60, 68, 75],
            "_RSI_SELL_MIN": [25, 32, 40],
        },
    },
    "narrow_range": {
        "module": "narrow_range",
        "type": "class",
        "constants": {
            "ATR_THRESHOLD": [0.75, 0.85, 0.95],
            "VOL_SPIKE_MULT": [1.0, 1.2, 1.5],
        },
    },
    "value_area": {
        "module": "value_area",
        "type": "module",
        "constants": {
            "_VA_MULT": [0.5, 0.7, 1.0],
            "_MIN_BREACH": [1.0, 1.5, 2.0],
        },
    },
}

# 엔진 레벨 파라미터 그리드 (모든 전략에 적용)
ENGINE_GRIDS = {
    "atr_multiplier_sl": [1.5, 2.0, 2.5, 3.0],
    "atr_multiplier_tp": [2.0, 3.0, 4.0, 5.0],
}


def _get_strategy_class(module_name: str):
    """전략 클래스 반환."""
    import importlib
    mod = importlib.import_module(f"src.strategy.{module_name}")
    for attr_name in dir(mod):
        obj = getattr(mod, attr_name)
        if isinstance(obj, type) and hasattr(obj, "generate") and attr_name != "BaseStrategy":
            return obj, mod
    return None, mod


def _apply_params(module_name: str, param_type: str, params: dict):
    """전략 파라미터를 동적으로 변경. module=모듈상수, class=클래스속성."""
    cls, mod = _get_strategy_class(module_name)
    for key, val in params.items():
        if param_type == "class" and cls and hasattr(cls, key):
            setattr(cls, key, val)
        elif hasattr(mod, key):
            setattr(mod, key, val)


def _get_strategy_instance(module_name: str):
    """전략 인스턴스 생성."""
    cls, _ = _get_strategy_class(module_name)
    if cls:
        try:
            return cls()
        except Exception:
            pass
    return None


# ── Walk-Forward 최적화 ────────────────────────────────────

def walk_forward_optimize(
    strategy_name: str,
    grid_config: dict,
    df: pd.DataFrame,
    train_hours: int = 2880,
    test_hours: int = 720,
) -> list[dict]:
    """Grid search + Walk-Forward로 최적 파라미터 탐색."""
    module_name = grid_config["module"]
    constants = grid_config["constants"]

    param_names = list(constants.keys())
    param_values = list(constants.values())
    combos = list(product(*param_values))

    engine = BacktestEngine(
        initial_balance=10_000,
        fee_rate=0.001,
        slippage_pct=0.001,
    )

    n_candles = len(df)
    train_n = train_hours
    test_n = test_hours

    results = []
    for combo in combos:
        params = dict(zip(param_names, combo))
        _apply_params(module_name, grid_config.get("type", "module"), params)
        strategy = _get_strategy_instance(module_name)
        if strategy is None:
            continue

        window_results = []
        start = 0
        while start + train_n + test_n <= n_candles:
            train_df = df.iloc[start:start + train_n]
            test_df = df.iloc[start + train_n:start + train_n + test_n]

            if len(test_df) < 100:
                break

            result = engine.run(strategy, test_df)
            window_results.append({
                "sharpe": result.sharpe_ratio,
                "pf": result.profit_factor,
                "trades": result.total_trades,
                "return": result.total_return,
                "mdd": result.max_drawdown,
                "mc_p": result.mc_p_value,
            })
            start += test_n

        if not window_results:
            continue

        avg_sharpe = np.mean([w["sharpe"] for w in window_results])
        avg_return = np.mean([w["return"] for w in window_results])
        avg_trades = np.mean([w["trades"] for w in window_results])
        avg_mdd = np.mean([w["mdd"] for w in window_results])
        avg_pf = np.mean([w["pf"] for w in window_results])
        avg_mc_p = np.mean([w["mc_p"] for w in window_results if w["mc_p"] >= 0])

        n_pass = sum(
            1 for w in window_results
            if w["sharpe"] >= 1.0 and w["pf"] >= 1.5 and w["trades"] >= 15
            and w["mdd"] <= 0.20 and (w["mc_p"] < 0 or w["mc_p"] <= 0.05)
        )
        consistency = n_pass / len(window_results) if window_results else 0

        results.append({
            "strategy": strategy_name,
            "params": params,
            "avg_sharpe": round(avg_sharpe, 3),
            "avg_return": round(avg_return, 4),
            "avg_pf": round(avg_pf, 3),
            "avg_trades": round(avg_trades, 1),
            "avg_mdd": round(avg_mdd, 4),
            "avg_mc_p": round(avg_mc_p, 4) if avg_mc_p == avg_mc_p else -1,
            "consistency": f"{n_pass}/{len(window_results)}",
            "passed": consistency >= 0.5,
            "windows": len(window_results),
        })

    results.sort(key=lambda x: x["avg_sharpe"], reverse=True)
    return results


# ── 레짐별 분석 ─────────────────────────────────────────────

def regime_analysis(
    strategy_name: str,
    module_name: str,
    df: pd.DataFrame,
    params: Optional[dict] = None,
    param_type: str = "module",
) -> dict:
    """전략을 레짐별로 분리 테스트."""
    if params:
        _apply_params(module_name, param_type, params)
    strategy = _get_strategy_instance(module_name)
    if strategy is None:
        return {}

    detector = MarketRegimeDetector()
    engine = BacktestEngine(
        initial_balance=10_000,
        fee_rate=0.001,
        slippage_pct=0.001,
    )

    regimes = detector.detect_history(df)
    regime_results = {}

    for regime in MarketRegime:
        regime_mask = [r == regime for r in regimes]
        regime_indices = [i for i, m in enumerate(regime_mask) if m]

        if len(regime_indices) < 200:
            continue

        chunks = []
        chunk_start = regime_indices[0]
        for i in range(1, len(regime_indices)):
            if regime_indices[i] - regime_indices[i - 1] > 5:
                if regime_indices[i - 1] - chunk_start >= 48:
                    chunks.append((chunk_start, regime_indices[i - 1] + 1))
                chunk_start = regime_indices[i]
        if regime_indices[-1] - chunk_start >= 48:
            chunks.append((chunk_start, regime_indices[-1] + 1))

        if not chunks:
            continue

        chunk_results = []
        for start, end in chunks:
            chunk_df = df.iloc[max(0, start - 200):end]
            if len(chunk_df) < 200:
                continue
            result = engine.run(strategy, chunk_df)
            chunk_results.append({
                "sharpe": result.sharpe_ratio,
                "return": result.total_return,
                "trades": result.total_trades,
                "pf": result.profit_factor,
            })

        if chunk_results:
            regime_results[regime.value] = {
                "n_chunks": len(chunk_results),
                "avg_sharpe": round(np.mean([c["sharpe"] for c in chunk_results]), 3),
                "avg_return": round(np.mean([c["return"] for c in chunk_results]), 4),
                "avg_trades": round(np.mean([c["trades"] for c in chunk_results]), 1),
                "total_candles": sum(e - s for s, e in chunks),
            }

    return regime_results


# ── メイン ─────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTC/USDT")
    parser.add_argument("--limit", type=int, default=4320)
    args = parser.parse_args()

    logger.info("=== Strategy Optimization: %s ===", args.symbol)
    df = enrich_indicators(fetch_bybit(args.symbol, "1h", args.limit))

    lines = []
    lines.append(f"# Strategy Optimization Report — {args.symbol}\n")
    lines.append(f"_Generated: {datetime.utcnow().isoformat()}Z_")
    lines.append(f"_Data: {len(df)} candles ({df.index[0]} ~ {df.index[-1]})_")
    lines.append(f"_Slippage: 0.1% | Fee: 0.1%_\n")

    all_top = []

    for strat_name, grid_config in PARAM_GRIDS.items():
        logger.info("[%s] Grid search (%d combos)...",
                     strat_name, len(list(product(*grid_config["constants"].values()))))

        results = walk_forward_optimize(strat_name, grid_config, df)

        lines.append(f"## {strat_name}\n")

        if results:
            top5 = results[:5]
            lines.append("| Params | AvgSharpe | AvgReturn | AvgPF | AvgTrades | MC_p | Consistency | Pass |")
            lines.append("|--------|-----------|-----------|-------|-----------|------|-------------|------|")
            for r in top5:
                p_str = ", ".join(f"{k}={v}" for k, v in r["params"].items())
                lines.append(
                    f"| {p_str} | {r['avg_sharpe']} | {r['avg_return']:+.2%} | "
                    f"{r['avg_pf']} | {r['avg_trades']} | {r['avg_mc_p']} | "
                    f"{r['consistency']} | {'PASS' if r['passed'] else 'FAIL'} |"
                )

            best = results[0]
            all_top.append(best)

            logger.info("[%s] Best: sharpe=%.3f, return=%.4f, params=%s",
                         strat_name, best["avg_sharpe"], best["avg_return"], best["params"])

            # 레짐 분석 (최적 파라미터로)
            lines.append(f"\n### 레짐별 성과 (best params)\n")
            regime_res = regime_analysis(
                strat_name, grid_config["module"], df, best["params"],
                param_type=grid_config.get("type", "module"),
            )
            if regime_res:
                lines.append("| Regime | Chunks | AvgSharpe | AvgReturn | AvgTrades | Candles |")
                lines.append("|--------|--------|-----------|-----------|-----------|---------|")
                for regime, stats in sorted(regime_res.items(), key=lambda x: x[1]["avg_sharpe"], reverse=True):
                    lines.append(
                        f"| {regime} | {stats['n_chunks']} | {stats['avg_sharpe']} | "
                        f"{stats['avg_return']:+.2%} | {stats['avg_trades']} | {stats['total_candles']} |"
                    )
            else:
                lines.append("_레짐별 분석 불가 (데이터 부족)_")
        else:
            lines.append("_결과 없음_")

        lines.append("")

    # 요약
    lines.append("## 요약\n")
    passed = [r for r in all_top if r.get("passed")]
    lines.append(f"- **최적화 전략**: {len(PARAM_GRIDS)}개")
    lines.append(f"- **PASS**: {len(passed)}개")
    if passed:
        for p in passed:
            lines.append(f"  - `{p['strategy']}`: Sharpe={p['avg_sharpe']}, params={p['params']}")
    lines.append("")

    report = "\n".join(lines)
    REPORT_PATH.write_text(report)
    logger.info("Report saved to %s", REPORT_PATH)
    print(report)


if __name__ == "__main__":
    main()
