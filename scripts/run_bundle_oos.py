"""
5-Strategy Bundle Rolling OOS 검증 스크립트.

실행:
    python scripts/run_bundle_oos.py [--symbol BTC/USDT] [--timeframe 4h] [--limit 4320]

동작:
1. Bybit에서 실데이터 수집 (기본 4h, 4320봉 ≈ 2년)
2. RollingOOSValidator로 5개 전략 순차 검증
   - 6m IS / 2m OOS, WFE ≥ 0.50, Sharpe decay ≤ 40%, MDD expand ≤ 2x
3. 결과를 요약 테이블로 출력 + .claude-state/BUNDLE_OOS_REPORT.md 저장
"""
from __future__ import annotations

import importlib
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from src.backtest.walk_forward import RollingOOSValidator, BundleOOSResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("bundle_oos")

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / ".claude-state" / "BUNDLE_OOS_REPORT.md"

# 5-Strategy Bundle 정의 (module, class)
BUNDLE_STRATEGIES = [
    ("cmf", "CMFStrategy"),
    ("elder_impulse", "ElderImpulseStrategy"),
    ("wick_reversal", "WickReversalStrategy"),
    ("narrow_range", "NarrowRangeStrategy"),
    ("value_area", "ValueAreaStrategy"),
]


def fetch_bybit_data(
    symbol: str, timeframe: str, limit: int
) -> pd.DataFrame:
    """Bybit에서 OHLCV 데이터 수집 (페이지네이션 포함)."""
    import ccxt

    tf_ms = {"1h": 3_600_000, "4h": 14_400_000}
    interval_ms = tf_ms.get(timeframe, 14_400_000)

    ex = ccxt.bybit()
    ex.timeout = 30000
    now_ms = int(time.time() * 1000)
    since = now_ms - limit * interval_ms

    all_ohlcv: list = []
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

    seen: set = set()
    deduped = [r for r in all_ohlcv if r[0] not in seen and not seen.add(r[0])]
    deduped.sort(key=lambda x: x[0])
    deduped = deduped[:limit]

    df = pd.DataFrame(deduped, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.set_index("timestamp").sort_index()
    logger.info("Fetched %d candles (%s ~ %s)", len(df), df.index[0], df.index[-1])
    return df


def enrich_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """전략이 사용하는 공통 지표 계산."""
    import numpy as np

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
    df["vwap20"] = (
        (tp * df["volume"]).rolling(20, min_periods=1).sum()
        / df["volume"].rolling(20, min_periods=1).sum()
    )
    df["volume_sma20"] = df["volume"].rolling(20, min_periods=1).mean()
    df["return_5"] = close.pct_change(5)

    return df


def load_strategy(module_name: str, class_name: str):
    """전략 인스턴스 생성."""
    mod = importlib.import_module(f"src.strategy.{module_name}")
    cls = getattr(mod, class_name)
    return cls()


def format_summary_table(results: list[tuple[str, BundleOOSResult]]) -> str:
    """결과를 Markdown 테이블로 포맷."""
    header = (
        "| Strategy | Folds | Avg WFE | Avg OOS Sharpe | Avg OOS PF | "
        "All Pass | Fail Reasons |"
    )
    separator = (
        "|----------|-------|---------|----------------|------------|"
        "----------|--------------|"
    )
    rows = [header, separator]

    for name, r in results:
        pass_str = "PASS" if r.all_passed else "FAIL"
        fails = "; ".join(r.fail_reasons) if r.fail_reasons else "-"
        rows.append(
            f"| {name} | {len(r.folds)} | {r.avg_wfe:.3f} | "
            f"{r.avg_oos_sharpe:.3f} | {r.avg_oos_pf:.3f} | "
            f"{pass_str} | {fails} |"
        )

    return "\n".join(rows)


def format_fold_detail(name: str, r: BundleOOSResult) -> str:
    """Fold별 상세 결과 Markdown."""
    if not r.folds:
        return f"### {name}\n\n_No folds (data insufficient)_\n"

    lines = [f"### {name}\n"]
    lines.append(
        "| Fold | IS Sharpe | OOS Sharpe | WFE | OOS PF | OOS Trades | "
        "IS MDD | OOS MDD | Pass |"
    )
    lines.append(
        "|------|-----------|------------|-----|--------|------------|"
        "-------|---------|------|"
    )
    for f in r.folds:
        pass_str = "PASS" if f.passed else "FAIL"
        lines.append(
            f"| {f.fold_id} | {f.is_sharpe:.3f} | {f.oos_sharpe:.3f} | "
            f"{f.wfe:.3f} | {f.oos_pf:.3f} | {f.oos_trades} | "
            f"{f.is_mdd:.2%} | {f.oos_mdd:.2%} | {pass_str} |"
        )
    if r.fail_reasons:
        lines.append(f"\n**Fail reasons:** {'; '.join(r.fail_reasons)}")
    lines.append("")
    return "\n".join(lines)


def run_bundle_oos(
    symbol: str = "BTC/USDT",
    timeframe: str = "4h",
    limit: int = 4320,
) -> list[tuple[str, BundleOOSResult]]:
    """5-Bundle 전략에 대해 Rolling OOS 검증 실행."""
    logger.info("=== 5-Bundle Rolling OOS Validation ===")
    logger.info("Symbol: %s | Timeframe: %s | Candles: %d", symbol, timeframe, limit)

    # 데이터 수집
    df = enrich_indicators(fetch_bybit_data(symbol, timeframe, limit))
    logger.info("Data ready: %d rows (%s ~ %s)", len(df), df.index[0], df.index[-1])

    # 검증기 초기화 (4h봉 기준: 6개월 ≈ 1080봉, 2개월 ≈ 360봉)
    validator = RollingOOSValidator(
        is_bars=1080,
        oos_bars=360,
        slide_bars=360,
        min_wfe=0.50,
        sharpe_decay_max=0.60,
        mdd_expand_max=2.0,
    )

    results: list[tuple[str, BundleOOSResult]] = []
    for module_name, class_name in BUNDLE_STRATEGIES:
        logger.info("--- Validating: %s ---", module_name)
        try:
            strategy = load_strategy(module_name, class_name)
            result = validator.validate(strategy, df)
            results.append((module_name, result))
            logger.info(result.summary())
        except Exception as e:
            logger.error("Failed to validate %s: %s", module_name, str(e)[:200])
            # 실패 시 빈 결과 추가
            fail_result = BundleOOSResult(
                strategy_name=module_name,
                folds=[],
                avg_wfe=0.0,
                avg_oos_sharpe=0.0,
                avg_oos_pf=0.0,
                all_passed=False,
                fail_reasons=[f"Exception: {str(e)[:100]}"],
            )
            results.append((module_name, fail_result))

    return results


def generate_report(
    results: list[tuple[str, BundleOOSResult]],
    symbol: str,
    timeframe: str,
) -> str:
    """Markdown 리포트 생성."""
    lines = []
    lines.append("# 5-Bundle Rolling OOS Validation Report\n")
    lines.append(f"_Generated: {datetime.utcnow().isoformat()}Z_")
    lines.append(f"_Symbol: {symbol} | Timeframe: {timeframe}_")
    lines.append(f"_Criteria: WFE >= 0.50, OOS Sharpe >= IS*0.60, OOS MDD <= IS*2.0_\n")

    # 요약 테이블
    lines.append("## Summary\n")
    lines.append(format_summary_table(results))

    passed = [name for name, r in results if r.all_passed]
    failed = [name for name, r in results if not r.all_passed]
    lines.append(f"\n**PASS: {len(passed)}/5** ({', '.join(passed) if passed else 'none'})")
    lines.append(f"**FAIL: {len(failed)}/5** ({', '.join(failed) if failed else 'none'})\n")

    # Fold별 상세
    lines.append("## Fold Details\n")
    for name, r in results:
        lines.append(format_fold_detail(name, r))

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="5-Bundle Rolling OOS Validation")
    parser.add_argument("--symbol", default="BTC/USDT", help="심볼 (기본: BTC/USDT)")
    parser.add_argument("--timeframe", default="4h", help="타임프레임 (기본: 4h)")
    parser.add_argument("--limit", type=int, default=4320, help="캔들 수 (기본: 4320)")
    args = parser.parse_args()

    results = run_bundle_oos(
        symbol=args.symbol,
        timeframe=args.timeframe,
        limit=args.limit,
    )

    # 콘솔 요약 출력
    print("\n" + "=" * 70)
    print("5-BUNDLE OOS VALIDATION RESULTS")
    print("=" * 70)
    print(format_summary_table(results))
    print()

    for name, r in results:
        verdict = "PASS" if r.all_passed else "FAIL"
        print(f"  {name:20s} — {verdict} (WFE={r.avg_wfe:.3f}, Sharpe={r.avg_oos_sharpe:.3f})")
    print()

    passed_count = sum(1 for _, r in results if r.all_passed)
    print(f"Overall: {passed_count}/5 PASS")
    print("=" * 70)

    # 리포트 저장
    report = generate_report(results, args.symbol, args.timeframe)
    REPORT_PATH.write_text(report)
    logger.info("Report saved to %s", REPORT_PATH)
    print(report)


if __name__ == "__main__":
    main()
