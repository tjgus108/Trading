"""
전략 품질 감사 스크립트.
모든 전략 파일을 개별 로드하여 합성 데이터로 백테스트 후 결과를 정리한다.
"""
import importlib
import inspect
import logging
import sys
import os
import traceback
import warnings
from pathlib import Path

# 로깅/경고 억제 (외부 API 호출 에러 로그 방지)
logging.getLogger().setLevel(logging.CRITICAL)
for name in list(logging.root.manager.loggerDict.keys()):
    logging.getLogger(name).setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.strategy.base import BaseStrategy, Action
from src.backtest.engine import BacktestEngine, BacktestResult
from typing import List, Tuple, Optional


def make_synthetic_data(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    """현실적인 합성 OHLCV 데이터 생성 (트렌드 + 노이즈 + 변동성 클러스터링)."""
    np.random.seed(seed)

    # 가격 생성: GBM with regime changes
    returns = np.random.normal(0.0001, 0.015, n)
    # 변동성 클러스터링
    for i in range(1, n):
        if abs(returns[i - 1]) > 0.02:
            returns[i] *= 1.5
    # 트렌드 구간 삽입
    returns[100:200] += 0.002   # bull
    returns[400:500] -= 0.002   # bear
    returns[700:800] += 0.001   # mild bull

    close = 50000 * np.exp(np.cumsum(returns))
    high = close * (1 + np.abs(np.random.normal(0, 0.008, n)))
    low = close * (1 - np.abs(np.random.normal(0, 0.008, n)))
    open_ = close * (1 + np.random.normal(0, 0.003, n))
    volume = np.random.lognormal(10, 0.8, n)

    df = pd.DataFrame({
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })

    # 흔히 사용되는 지표 사전 계산
    df["atr14"] = _atr(df, 14)
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["rsi14"] = _rsi(df["close"], 14)
    df["sma20"] = df["close"].rolling(20).mean()
    df["sma50"] = df["close"].rolling(50).mean()
    df["bb_upper"] = df["sma20"] + 2 * df["close"].rolling(20).std()
    df["bb_lower"] = df["sma20"] - 2 * df["close"].rolling(20).std()
    df["macd"] = df["close"].ewm(span=12).mean() - df["close"].ewm(span=26).mean()
    df["macd_signal"] = df["macd"].ewm(span=9).mean()
    df["volume_sma20"] = df["volume"].rolling(20).mean()
    df["return_5"] = df["close"].pct_change(5)
    
    # 추가 지표 (몇몇 전략에서 필요)
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["donchian_high"] = df["high"].rolling(20).max()
    df["donchian_low"] = df["low"].rolling(20).min()
    
    # VWAP 계산: (누적 전형 가격 * 거래량) / 누적 거래량
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    cum_vol = df["volume"].cumsum()
    cum_tp_vol = (typical_price * df["volume"]).cumsum()
    df["vwap"] = cum_tp_vol / cum_vol.replace(0, np.nan)
    
    # VWAP 20 period rolling (근사)
    df["vwap20"] = (typical_price * df["volume"]).rolling(20).sum() / df["volume"].rolling(20).sum()

    return df


def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    hl = df["high"] - df["low"]
    hc = (df["high"] - df["close"].shift(1)).abs()
    lc = (df["low"] - df["close"].shift(1)).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def find_strategy_classes() -> List[Tuple[str, str, type]]:
    """src/strategy/ 내 모든 BaseStrategy 하위 클래스를 찾는다."""
    strategy_dir = Path(__file__).resolve().parent.parent / "src" / "strategy"
    results = []
    # 외부 API/피드 의존 전략 제외 (합성 데이터 백테스트 불가)
    skip = {
        "__init__", "base", "adaptive_selector", "multi_signal",
        "gex_signal", "cme_basis", "cross_exchange_arb",
        "funding_rate", "funding_carry", "liquidation_cascade",
        "ml_rf", "ml_lstm", "heston_lstm", "regime_adaptive",
        "pair_trading", "residual_mean_reversion", "lob_maker",
        "specialist_agents",
    }

    for py_file in sorted(strategy_dir.glob("*.py")):
        mod_name = py_file.stem
        if mod_name in skip:
            continue
        module_path = f"src.strategy.{mod_name}"
        try:
            mod = importlib.import_module(module_path)
        except Exception:
            continue

        for attr_name in dir(mod):
            obj = getattr(mod, attr_name)
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseStrategy)
                and obj is not BaseStrategy
                and not inspect.isabstract(obj)
                and obj.__module__ == module_path  # 다른 모듈에서 import된 건 제외
            ):
                results.append((mod_name, attr_name, obj))
    return results


def run_audit():
    print("=" * 70)
    print("전략 품질 감사 (Quality Audit)")
    print("=" * 70)

    # 합성 데이터 생성 (500 캔들로 속도 우선)
    df = make_synthetic_data(500)
    engine = BacktestEngine(
        initial_balance=10_000,
        fee_rate=0.001,
        slippage_pct=0.0005,
    )

    # 전략 탐색
    strategies = find_strategy_classes()
    print(f"\n발견된 전략 클래스: {len(strategies)}개", flush=True)
    print("-" * 70, flush=True)

    results = []
    errors = []
    import time as _time

    total = len(strategies)
    for idx, (mod_name, cls_name, cls) in enumerate(strategies, 1):
        if idx % 20 == 0 or idx == 1:
            print(f"  진행: {idx}/{total}", flush=True)
        t0 = _time.time()
        try:
            strategy = cls()
            bt = engine.run(strategy, df)
            elapsed = _time.time() - t0
            if elapsed > 2.0:
                print(f"    [SLOW] {mod_name}.{cls_name}: {elapsed:.1f}s", flush=True)
            results.append({
                "module": mod_name,
                "class": cls_name,
                "name": strategy.name,
                "sharpe": round(bt.sharpe_ratio, 3),
                "win_rate": round(bt.win_rate, 3),
                "profit_factor": round(bt.profit_factor, 3),
                "max_dd": round(bt.max_drawdown, 3),
                "trades": bt.total_trades,
                "total_return": round(bt.total_return, 4),
                "passed": bt.passed,
                "fees": round(bt.total_fees, 2),
                "slip_cost": round(bt.total_slippage_cost, 2),
                "fail_reasons": bt.fail_reasons,
            })
        except Exception as e:
            errors.append({
                "module": mod_name,
                "class": cls_name,
                "error": str(e)[:100],
            })

    # 결과 정렬
    results.sort(key=lambda x: x["sharpe"], reverse=True)

    # --- 결과 출력 ---
    print(f"\n백테스트 완료: {len(results)}개 | 에러: {len(errors)}개")
    print()

    # PASS 전략
    passed = [r for r in results if r["passed"]]
    print(f"=== PASS 전략 ({len(passed)}개) ===")
    print(f"{'Name':<35} {'Sharpe':>7} {'WinRate':>8} {'PF':>6} {'MDD':>7} {'Trades':>7} {'Return':>8}")
    print("-" * 80)
    for r in passed:
        print(f"{r['name']:<35} {r['sharpe']:>7.3f} {r['win_rate']:>7.1%} {r['profit_factor']:>6.2f} {r['max_dd']:>6.1%} {r['trades']:>7} {r['total_return']:>7.2%}")

    print()

    # FAIL 전략 (Sharpe 기준 상위)
    failed = [r for r in results if not r["passed"]]
    print(f"=== FAIL 전략 ({len(failed)}개) ===")
    print(f"{'Name':<35} {'Sharpe':>7} {'WinRate':>8} {'Trades':>7} {'Reasons'}")
    print("-" * 80)
    for r in failed[:30]:  # 상위 30개만
        reasons = ", ".join(r["fail_reasons"][:2])
        print(f"{r['name']:<35} {r['sharpe']:>7.3f} {r['win_rate']:>7.1%} {r['trades']:>7} {reasons}")
    if len(failed) > 30:
        print(f"  ... +{len(failed) - 30}개 더")

    print()

    # 에러 전략
    if errors:
        print(f"=== 로드/실행 에러 ({len(errors)}개) ===")
        for e in errors[:20]:
            print(f"  {e['module']}.{e['class']}: {e['error']}")
        if len(errors) > 20:
            print(f"  ... +{len(errors) - 20}개 더")

    # 요약 통계
    print()
    print("=" * 70)
    print("요약")
    print("=" * 70)
    print(f"  전략 클래스 발견: {len(strategies)}개")
    print(f"  백테스트 완료:    {len(results)}개")
    print(f"  PASS:             {len(passed)}개")
    print(f"  FAIL:             {len(failed)}개")
    print(f"  에러:             {len(errors)}개")

    if results:
        sharpes = [r["sharpe"] for r in results]
        print(f"  Sharpe 중앙값:    {np.median(sharpes):.3f}")
        print(f"  Sharpe 평균:      {np.mean(sharpes):.3f}")

    # 결과 CSV 저장
    if results:
        rdf = pd.DataFrame(results)
        csv_path = Path(__file__).resolve().parent.parent / ".claude-state" / "QUALITY_AUDIT.csv"
        rdf.to_csv(csv_path, index=False)
        print(f"\n결과 저장: {csv_path}")

    return results, errors


if __name__ == "__main__":
    run_audit()
