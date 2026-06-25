"""
Paper Trading 시뮬레이션 — 실제 Bybit 데이터로 전략들을 Walk-Forward 방식으로 평가.

실행:
    python3 scripts/paper_simulation.py

동작:
1. Bybit public API로 BTC/USDT 1h 캔들 12개월치 페이지네이션 수집
2. QUALITY_AUDIT.csv에서 PASS 전략 목록 로드
3. Walk-Forward 방식: 훈련 4개월 → 테스트 1개월, 1개월씩 롤링 (최소 3윈도우)
4. 복수 윈도우에서 일관되게 실패해야 FAIL (단일 실패로 제거하지 않음)
5. 결과를 .claude-state/PAPER_SIMULATION_REPORT.md에 기록
"""
from __future__ import annotations
from typing import Optional, List, Dict, Tuple, Set

import argparse
import importlib
import json
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
from src.strategy.regime import MarketRegime, MarketRegimeDetector
from src.backtest.walk_forward import _RegimeFilterStrategy

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / ".claude-state"
REPORT_PATH = STATE_DIR / "PAPER_SIMULATION_REPORT.md"
RESULTS_JSON_PATH = STATE_DIR / "PAPER_SIMULATION_RESULTS.json"
RESULTS_CSV_PATH = STATE_DIR / "PAPER_SIMULATION_RESULTS.csv"
CSV_PATH = STATE_DIR / "QUALITY_AUDIT.csv"

# CSV 데이터 디렉토리 (--csv-dir 옵션으로 설정, None이면 거래소 API 우선)
# data/historical/{exchange}/{pair}/{timeframe}.csv 구조
CSV_DATA_DIR: Optional[Path] = None

# 활성 타임프레임 (--timeframe으로 설정, 기본 1h)
# Cycle 290 C: 4h 지원 추가 — 1h CSV를 resample하여 사용
ACTIVE_TIMEFRAME: str = "1h"

# 타임프레임별 1h 대비 캔들 비율 (1h=1, 4h=0.25 등)
_TF_CANDLE_RATIO: Dict[str, float] = {
    "1m": 1/60, "5m": 1/12, "15m": 1/4, "1h": 1.0, "4h": 0.25, "1d": 1/24
}

# Walk-Forward 설정 (Cycle 211: 7일 train/28일 test → 학술 최적 조합 반영)
# Cycle 210 리서치: 7d train/28d test가 81개 WF 조합 중 Sharpe 최고(1.252)
# fold당 30 trades 목표: 1h봉 60일(1440h) 테스트 윈도우가 유리
# NOTE: 실제 캔들 수 = 아래 값 × _TF_CANDLE_RATIO[ACTIVE_TIMEFRAME]
TRAIN_HOURS = 24 * 210   # 훈련: 7개월 (210일, 1h 기준 캔들 수)
# Cycle312 F(리서치): 84일 실험 → 역효과 확인. price_cluster 3/8→1/12 consistency 폭락.
# 결론: 84일 train은 파라미터 최적화에 부족. 210일 복원.
TEST_HOURS = 24 * 60     # 테스트: 2개월 (60일, 1h 기준 캔들 수)
STEP_HOURS = 24 * 30     # 롤링 간격: 1개월 (1h 기준 캔들 수)
MIN_WINDOWS = 3          # 최소 테스트 윈도우 수

# 전략 통과 기준: 테스트 윈도우 중 과반수에서 통과해야 PASS
PASS_RATIO = 0.5  # 50% 이상 윈도우에서 통과

# 전략별 파라미터 오버라이드 (빈 dict = 기본값 사용)
# Cycle 274: cmf threshold 실험 종료 (0.05/-0.05 효과 미미) → 기본값(0.08/-0.08) 복원
# Cycle 295 A: 저거래 전략 거래 빈도 개선
#   - value_area: vol_filter_mult 0.7→0.5 (거래량 필터 완화, avg=12 → 15+ 목표)
#   - wick_reversal: min_volatility 0.002→0.001, vol_mult 0.8→0.6 (저변동성/저거래량 구간 복원)
#   - relative_volume: rvol_buy_sell 1.6→1.3 (신호 빈도 증가, avg=13 → 15+ 목표)
#   - momentum_quality: quality_score_buy_threshold 1.0→0.8, consistency 0.4→0.3 (C 데이터: sideways 개선)
PAPER_SIM_STRATEGY_PARAMS: Dict[str, dict] = {
    "value_area": {"vol_filter_mult": 0.5},
    "wick_reversal": {"min_volatility": 0.001, "vol_mult": 0.6},
    # Cycle298 B: rvol_buy_sell 1.1 역효과 (PF 1.40/1.36, W4-W6 bear/sideways 여전히 FAIL) → 1.2 복원
    "relative_volume": {"rvol_buy_sell": 1.2},
    # Cycle297 F: bull_only=True 역효과 (Sharpe 1.82→1.60, trades 22→19) → 제거
    # Cycle301 D(ML): quality_score_buy_threshold 0.85 실험 → 역효과 (PF 1.48→1.33) → 0.80 복원
    "momentum_quality": {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3},
    # Cycle 321 B(리스크): price_cluster → vwap_cross 교체 (paper_sim에서도 반영)
    #   price_cluster 1h paper_sim rank1이었으나 4h OOS 구조 한계로 번들 교체 확정
    #   vwap_cross: 기본 파라미터로 1h paper_sim 시험 (VWAP20/50 크로스, 신호 빈도 비교)
    # vwap_cross는 기본값으로 시험 (추가 파라미터 없음)
    # Cycle298 F: trend_span=20 적용 (EMA20 macro trend filter, sharpe -7.98 완화)
    # Cycle299 F: delta_window=7 실험 → 역효과 → 기본값(10) 복원
    # Cycle300 C: buy_thresh=0.30 실험 → 역효과 (3/8→1/8 PASS, mc_p_value 실패 증가) → 기본값(0.25) 복원
    # Cycle332 D(ML): trend_span=15, delta_window=7 실험 → 역효과 확인 후 복원
    #   avg=4.036 (4.345→-0.309 악화), std=2.771 (0.907→+1.864 악화) → Bundle OOS FAIL
    # Cycle336 D(ML): buy_thresh=0.30 재시도 → BTC 소폭 개선(-0.83→-0.64), ETH 급락(rank15, Sharpe=-2.40)
    # Cycle337 D(ML): buy_thresh 기본값(0.25) 복원 — ETH 악화 과도, Cycle300 역효과 전례 재확인
    "order_flow_imbalance_v2": {"trend_span": 20},
    # Cycle309 D(ML): buy_thresh=0.10 효과 미미 (rank14, Sharpe -1.21, trades=72)
    # Cycle310 A(품질): period=40 실험 → 역효과 (rank19, Sharpe=-2.33, trades=59) → period=20 복원
    # 결론: 1h CMF는 period 조정과 무관하게 FAIL — 4h 전용 전략으로 확정 (walk_forward 집중)
    "cmf": {"buy_thresh": 0.10},
    # Cycle354 D(ML): price_cluster vol_regime_filter=True 실험 (1.5 → 효과 없음 확인)
    # Cycle355 A(품질): vol_atr_trend_min 1.5→1.2 강화 → Sharpe=0.87, PF=1.20 (1.5와 동일)
    # Cycle356 F(리서치): 1.0 시도 → Sharpe=-0.30, 0/8 (대폭 악화) → 1.2로 복원
    #   결론: vol_atr_trend_min 하향 (1.0)은 신호 과도 차단으로 역효과 확정
    # Cycle357 F(리서치): vol_regime_filter=False 시도 → ETH Sharpe=-0.44 (악화) → 복원
    #   BTC는 동일(Sharpe=0.87), ETH에서 역효과 → vol_regime_filter=False 방향 포기
    #   결론: vol_regime_filter=True, vol_atr_trend_min=1.2 유지 확정
    "price_cluster": {"vol_regime_filter": True, "vol_atr_trend_min": 1.2},
    # Cycle354 E(실행): dema_cross convergence_signal 실험 → BTC real data 검증 결과 제거
    #   BTC full dataset: 23 trades(baseline) vs 867 trades(2% threshold) → Sharpe -2.37, ret -76%
    #   모든 threshold(0.5%~2.0%)에서 BTC Sharpe 악화 확인 → paper_sim 적용 보류
    # Cycle355 F(리서치): 거리 필터 0.5%→0.1% 완화 → BTC 여전히 3 trades (cross 이벤트 희귀)
    # Cycle356 D(ML): fast=8/slow=20 실험 (현재 fast=10/slow=25 기본값)
    #   근거: 짧은 주기 → DEMA 반응 빠름 → cross 이벤트 빈도 증가 기대 (목표: 3→10+ trades)
    #   slow=25(기존 기본값) 대비 slow=20으로 단축 + fast=8로 민감도 향상
    "dema_cross": {"fast": 8, "slow": 20},
    # Cycle352 B(리스크): 4h BTC 3/8 window "no trades generated" 해결
    #   원인: atr_threshold=0.7(기본값)이 저변동성 4h window에서 모든 신호 차단
    #   Bundle OOS도 atr_threshold=0.5 사용하며 PASS → 동일 값으로 일치
    "supertrend_multi": {"atr_threshold": 0.5},
}

# 레짐 필터 전략 목록 (Cycle 339 D(ML): TREND_UP 레짐에서만 BUY 허용)
# Cycle 339 실험 결과: roc_ma_cross 적용 → Sharpe +0.32→-0.43, trades 57→18 (역효과)
# BUY 신호 ~70% 차단으로 trade frequency 붕괴 → 거래 수 부족 → Sharpe 음전환
# 결론: 윈도우 레벨 TREND_UP% 분석과 개별 봉 레벨 필터링은 다른 문제
# Cycle 340 방향: 레짐 전환 타이밍이 아닌 IS/OOS 구간 레짐 매칭 방식 재검토
PAPER_SIM_REGIME_FILTER: Set[str] = set()  # 빈 집합 = 레짐 필터 비활성화

# 윈도우별 상세 출력 플래그 (--verbose-windows CLI 옵션으로 활성화)
# 활성화 시 generate_report()에서 상위 5개 전략의 윈도우별 Sharpe/PF/Trades 출력
VERBOSE_WINDOWS: bool = False


# ── 데이터 수집 ──────────────────────────────────────────────

TIMEFRAME_MS = {
    "1m": 60_000, "5m": 300_000, "15m": 900_000,
    "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000,
}


def load_ohlcv_from_csv_dir(
    csv_dir: Path,
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
) -> Optional[pd.DataFrame]:
    """csv_dir에서 symbol/timeframe에 맞는 CSV 파일을 로드.

    탐색 경로 우선순위:
      1. {csv_dir}/{exchange}/{pair}/{timeframe}.csv  (data/historical 구조)
      2. {csv_dir}/{pair}_{timeframe}.csv  (단순 평탄 구조)
      3. {csv_dir}/**/{pair}*{timeframe}*.csv  (glob 폴백)

    load_csv_ohlcv()로 파싱하여 enrich_indicators() 없이 raw OHLCV 반환.
    """
    from src.data.data_utils import load_csv_ohlcv

    pair_clean = symbol.replace("/", "").replace(":", "")  # "BTC/USDT" → "BTCUSDT"
    pair_slash = symbol.replace("/", "_")                   # "BTC/USDT" → "BTC_USDT"

    candidates = []
    # 1. data/historical 계층 구조 탐색
    for exc_dir in csv_dir.iterdir() if csv_dir.exists() else []:
        if exc_dir.is_dir():
            for pair_dir in exc_dir.iterdir():
                if pair_dir.is_dir() and pair_dir.name.upper() in (pair_clean, pair_slash.upper()):
                    p = pair_dir / f"{timeframe}.csv"
                    if p.exists():
                        candidates.append(p)

    # 2. 평탄 구조
    for name in [f"{pair_clean}_{timeframe}.csv", f"{pair_slash}_{timeframe}.csv"]:
        p = csv_dir / name
        if p.exists():
            candidates.append(p)

    # 3. glob 폴백
    if not candidates:
        for p in csv_dir.rglob(f"*{pair_clean}*{timeframe}*.csv"):
            candidates.append(p)
        for p in csv_dir.rglob(f"*{pair_slash}*{timeframe}*.csv"):
            candidates.append(p)

    if not candidates:
        return None

    # synthetic보다 실거래소(binance 등) 데이터 우선 선택; 동일 조건이면 최근 수정본
    def _candidate_key(p: Path):
        is_synthetic = "synthetic" in str(p).lower()
        return (is_synthetic, -p.stat().st_mtime)  # synthetic=False(0)가 True(1)보다 우선
    csv_path = min(candidates, key=_candidate_key)
    print(f"[DATA] CSV 로드: {csv_path}", flush=True)
    try:
        tf_seconds = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}
        df = load_csv_ohlcv(csv_path, validate=True, expected_interval_seconds=tf_seconds.get(timeframe))
        if df is not None and not df.empty:
            print(f"[DATA] CSV 로드 성공: {len(df)} 캔들 ({df.index[0]} ~ {df.index[-1]})", flush=True)
            return df
    except Exception as e:
        print(f"[DATA] CSV 로드 실패: {e}", flush=True)
    return None


def fetch_real_data_paginated(
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    total_candles: int = 8640,  # 12개월 (360일 * 24h)
    batch_size: int = 1000,
) -> Optional[pd.DataFrame]:
    """Bybit에서 페이지네이션으로 장기 OHLCV 데이터 수집. 실패 시 None."""
    try:
        import ccxt
        # 거래소 우선순위: bybit → binance → okx (SSL 차단 시 fallback)
        # Cycle 211: timeout 20000ms→5000ms (SSL 차단 환경에서 빠른 fallback)
        exchange_ids = ["bybit", "binance", "okx"]
        ex = None
        for eid in exchange_ids:
            try:
                candidate = getattr(ccxt, eid)({"timeout": 5000, "enableRateLimit": True})
                test_data = candidate.fetch_ohlcv(symbol, timeframe, limit=2)
                if test_data:
                    ex = candidate
                    if eid != "bybit":
                        print(f"[DATA] Bybit 차단, {eid}로 fallback", flush=True)
                    break
            except Exception:
                continue
        if ex is None:
            for eid in exchange_ids:
                try:
                    candidate = getattr(ccxt, eid)({"timeout": 5000, "enableRateLimit": True, "verify": False})
                    test_data = candidate.fetch_ohlcv(symbol, timeframe, limit=2)
                    if test_data:
                        ex = candidate
                        print(f"[DATA] {eid} SSL skip 연결", flush=True)
                        break
                except Exception:
                    continue
        if ex is None:
            print("[ERROR] 모든 거래소 연결 실패", flush=True)
            return None
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
    df["ema20_slope"] = df["ema20"].diff() / df["ema20"]  # feed.py._add_indicators() 동기화
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

    # Supertrend (3 configs) — precomputed to avoid O(n²) in strategy generate()
    for atr_period, mult in [(10, 1.5), (14, 2.0), (20, 3.0)]:
        prev_close = close.shift(1)
        _tr = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
        ).max(axis=1)
        _atr = _tr.ewm(alpha=1.0 / atr_period, adjust=False).mean()
        _hl2 = (high + low) / 2.0
        _bu = (_hl2 + mult * _atr).to_numpy(dtype=float)
        _bl = (_hl2 - mult * _atr).to_numpy(dtype=float)
        _c = close.to_numpy(dtype=float)
        n_ = len(_c)
        _fu = _bu.copy(); _fl = _bl.copy()
        _trend = np.ones(n_, dtype=np.int8)
        for _i in range(1, n_):
            _cp = _c[_i - 1]
            _fu[_i] = _bu[_i] if (_bu[_i] < _fu[_i - 1] or _cp < _fu[_i - 1]) else _fu[_i - 1]
            _fl[_i] = _bl[_i] if (_bl[_i] > _fl[_i - 1] or _cp > _fl[_i - 1]) else _fl[_i - 1]
            _ci = _c[_i]
            _trend[_i] = 1 if _ci > _fu[_i - 1] else (-1 if _ci < _fl[_i - 1] else _trend[_i - 1])
        col = f"st_trend_{atr_period}_{str(mult).replace('.', '_')}"
        df[col] = _trend

    return df


# ── 전략 로드 ──────────────────────────────────────────────

def load_pass_strategies() -> List[Tuple[str, str]]:
    """QUALITY_AUDIT.csv에서 PASS 전략만 로드. STRATEGY_FILTER가 설정되면 해당 전략만 반환."""
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
        passed = df[df["passed"] == True]  # noqa: E712
        if len(passed) > 0:
            result = list(zip(passed["module"].tolist(), passed["class"].tolist()))
            if STRATEGY_FILTER:
                result = [(m, c) for m, c in result if m in STRATEGY_FILTER]
                print(f"[STRATEGIES] Filter applied: {STRATEGY_FILTER} → {len(result)} strategies")
            return result
        print("[WARN] QUALITY_AUDIT.csv에 PASS 전략 0개. 전체 전략 로드 (최대 50개)")

    from scripts.quality_audit import find_strategy_classes
    all_strats = find_strategy_classes()
    print(f"[INFO] 전체 전략 {len(all_strats)}개 중 상위 50개 로드")
    result = [(mod, cls_name) for mod, cls_name, _ in all_strats[:50]]
    if STRATEGY_FILTER:
        result = [(m, c) for m, c in result if m in STRATEGY_FILTER]
        print(f"[STRATEGIES] Filter applied: {STRATEGY_FILTER} → {len(result)} strategies")
    return result


def load_strategy_class(module_name: str, class_name: str):
    """모듈에서 전략 클래스 동적 로드."""
    try:
        mod = importlib.import_module(f"src.strategy.{module_name}")
        return getattr(mod, class_name, None)
    except Exception:
        return None


# ── Walk-Forward 평가 ──────────────────────────────────────

def make_walk_forward_windows(df: pd.DataFrame) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
    """데이터를 훈련/테스트 윈도우로 분할.
    Returns: [(train_df, test_df), ...]
    """
    ratio = _TF_CANDLE_RATIO.get(ACTIVE_TIMEFRAME, 1.0)
    train_c = max(10, int(TRAIN_HOURS * ratio))
    test_c = max(5, int(TEST_HOURS * ratio))
    step_c = max(1, int(STEP_HOURS * ratio))

    n = len(df)
    windows = []
    start = 0

    while True:
        train_end = start + train_c
        test_end = train_end + test_c

        if test_end > n:
            break

        train_df = df.iloc[start:train_end]
        test_df = df.iloc[train_end:test_end]
        windows.append((train_df, test_df))

        start += step_c

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
              f"(train={train_c}, test={test_c}, step={step_c} candles [{ACTIVE_TIMEFRAME}])")

    return windows


def evaluate_strategy_walk_forward(
    strategy_cls,
    windows: List[Tuple[pd.DataFrame, pd.DataFrame]],
    engine: BacktestEngine,
    strategy_params: Optional[Dict] = None,
) -> dict:
    """Walk-Forward로 전략을 평가. 각 윈도우의 테스트 구간에서 백테스트 실행.

    Args:
        strategy_params: 전략 생성자 오버라이드 파라미터 (None이면 기본값 사용).

    Returns:
        dict with keys: name, window_results, consistency_score, avg metrics, overall_passed
    """
    window_results = []
    strategy = strategy_cls(**(strategy_params or {}))
    name = strategy.name

    window_vols = []  # 윈도우별 변동성 (regime weighting용)
    _reg_diag = MarketRegimeDetector()  # IS/OOS 레짐 진단용 (Cycle 340 A품질)

    for i, (train_df, test_df) in enumerate(windows):
        try:
            # 테스트 구간에서 백테스트 (훈련 데이터는 지표 warmup 용도로 앞에 붙임)
            # warmup으로 훈련 데이터 마지막 100봉을 테스트 앞에 붙임
            warmup = train_df.iloc[-100:] if len(train_df) > 100 else train_df
            eval_df = pd.concat([warmup, test_df])

            strategy_inst = strategy_cls(**(strategy_params or {}))
            # Cycle 339 D(ML): TREND_UP 레짐 필터 (roc_ma_cross 등)
            # PASS 윈도우 TREND_UP 41~45% vs FAIL 윈도우 21~32% → 레짐 불일치가 주 FAIL 원인
            if name in PAPER_SIM_REGIME_FILTER:
                _detector = MarketRegimeDetector()
                _regime_series = _detector.detect_series(eval_df)
                eval_df = eval_df.copy()
                eval_df["_regime_trend_up"] = (_regime_series == MarketRegime.TREND_UP)
                strategy_inst = _RegimeFilterStrategy(strategy_inst)
            bt = engine.run(strategy_inst, eval_df)

            # IS/OOS 레짐 진단 (Cycle 340 A품질)
            # IS: IS 말미 end-state (detect, 단일 호출 ~0.5ms)
            # OOS: OOS 구간 dominant regime (detect_series mode, ~15ms) → end-state보다 정확
            try:
                is_regime = _reg_diag.detect(train_df).value
                _oos_series = _reg_diag.detect_series(eval_df).iloc[-len(test_df):]
                oos_regime = _oos_series.mode()[0].value if len(_oos_series) > 0 else MarketRegime.RANGING.value
            except Exception:
                is_regime = MarketRegime.RANGING.value
                oos_regime = MarketRegime.RANGING.value

            # 테스트 구간 변동성 계산 (ATR/close 평균)
            if all(c in test_df.columns for c in ["high", "low", "close"]):
                _atr = (test_df["high"] - test_df["low"]) / (test_df["close"] + 1e-9)
                win_vol = float(_atr.mean())
            else:
                win_vol = 0.0
            window_vols.append(win_vol)

            # 시장 방향 태그 (Cycle260: 레짐별 전략 성과 분석을 위한 어노테이션)
            mkt_ret = 0.0
            mkt_state = "unknown"
            if "close" in test_df.columns and len(test_df) > 1:
                mkt_ret = float((test_df["close"].iloc[-1] - test_df["close"].iloc[0]) / (test_df["close"].iloc[0] + 1e-9))
                mkt_state = "bull" if mkt_ret > 0.05 else ("bear" if mkt_ret < -0.05 else "sideways")

            # Cycle 341 D(ML): IS Sharpe 추가 (verbose-windows 활성화 시만 계산)
            # IS_end=TREND_UP → OOS PASS 상관관계 분석용 (roc_ma_cross 패턴)
            is_sharpe = None
            _verbose = getattr(sys.modules[__name__], "VERBOSE_WINDOWS", False)
            if _verbose:
                try:
                    _is_inst = strategy_cls(**(strategy_params or {}))
                    _bt_is = engine.run(_is_inst, train_df)
                    is_sharpe = round(_bt_is.sharpe_ratio, 3)
                except Exception:
                    is_sharpe = None

            window_results.append({
                "window": i + 1,
                "sharpe": bt.sharpe_ratio,
                "total_return": bt.total_return,
                "max_dd": bt.max_drawdown,
                "profit_factor": bt.profit_factor,
                "trades": bt.total_trades,
                "win_rate": bt.win_rate,
                "passed": bt.passed,
                "fail_reasons": list(bt.fail_reasons) if bt.fail_reasons else [],
                "final_balance": 10_000 * (1 + bt.total_return),
                "volatility": win_vol,
                "market_return": round(mkt_ret, 4),
                "market_state": mkt_state,
                "slippage_regime_counts": dict(bt.slippage_regime_counts),
                "loss_scale_half_count": getattr(bt, "loss_scale_half_count", 0),
                "loss_scale_full_count": getattr(bt, "loss_scale_full_count", 0),
                "is_regime": is_regime,
                "oos_regime": oos_regime,
                "regime_match": is_regime == oos_regime,
                "is_sharpe": is_sharpe,
            })
        except Exception as e:
            window_vols.append(0.0)
            window_results.append({
                "window": i + 1, "sharpe": 0, "total_return": 0, "max_dd": 0,
                "profit_factor": 0, "trades": 0, "win_rate": 0, "passed": False,
                "final_balance": 10_000, "error": str(e)[:100],
                "fail_reasons": [f"exception: {str(e)[:80]}"],
                "volatility": 0.0,
                "market_return": 0.0,
                "market_state": "unknown",
            })

    # 일관성 점수: 통과한 윈도우 비율
    passed_count = sum(1 for wr in window_results if wr["passed"])
    consistency = passed_count / len(window_results) if window_results else 0

    # 평균 지표 (에러 제외)
    valid = [wr for wr in window_results if "error" not in wr]
    valid_vols = [wr.get("volatility", 0.0) for wr in valid]

    # Regime weighting: HIGH_VOL fold 다운웨이팅 (walk_forward.py와 동일 로직)
    if USE_REGIME_WEIGHTS and valid and valid_vols and sum(valid_vols) > 0:
        mean_vol = sum(valid_vols) / len(valid_vols)
        raw_weights = [1.0 / (1.0 + v / (mean_vol + 1e-9)) for v in valid_vols]
        total_w = sum(raw_weights)
        weights = [w / total_w for w in raw_weights]

        avg_sharpe = sum(w * wr["sharpe"] for w, wr in zip(weights, valid))
        avg_return = sum(w * wr["total_return"] for w, wr in zip(weights, valid))
        avg_dd = sum(w * wr["max_dd"] for w, wr in zip(weights, valid))
        avg_pf = sum(w * wr["profit_factor"] for w, wr in zip(weights, valid))
        avg_trades = sum(w * wr["trades"] for w, wr in zip(weights, valid))
        avg_wr = sum(w * wr["win_rate"] for w, wr in zip(weights, valid))
    else:
        weights = None
        avg_sharpe = np.mean([wr["sharpe"] for wr in valid]) if valid else 0
        avg_return = np.mean([wr["total_return"] for wr in valid]) if valid else 0
        avg_dd = np.mean([wr["max_dd"] for wr in valid]) if valid else 0
        avg_pf = np.mean([wr["profit_factor"] for wr in valid]) if valid else 0
        avg_trades = np.mean([wr["trades"] for wr in valid]) if valid else 0
        avg_wr = np.mean([wr["win_rate"] for wr in valid]) if valid else 0

    # 윈도우 간 Sharpe 표준편차 (일관성 보조 지표)
    # Regime weights 적용 시 가중 표준편차 사용
    if USE_REGIME_WEIGHTS and weights and len(valid) > 1:
        sharpes = [wr["sharpe"] for wr in valid]
        w_mean = sum(w * s for w, s in zip(weights, sharpes))
        w_var = sum(w * (s - w_mean) ** 2 for w, s in zip(weights, sharpes))
        sharpe_std = float(np.sqrt(w_var))
    else:
        sharpe_std = float(np.std([wr["sharpe"] for wr in valid])) if len(valid) > 1 else 0.0

    # fail_reasons 집계: 윈도우별 실패 이유를 카운트하여 빈도순 정렬
    from collections import Counter
    fail_counter: Counter = Counter()
    for wr in window_results:
        for reason in wr.get("fail_reasons", []):
            # 수치 부분 제거하여 카테고리로 집계 (e.g. "sharpe 0.50 < 1.0" → "sharpe < 1.0")
            fail_counter[reason] += 1
    # 빈도순 정렬된 리스트: [(reason, count), ...]
    top_fail_reasons = fail_counter.most_common()

    # 슬리피지 레짐 집계 (adaptive_slippage=True 시 데이터 존재)
    slip_agg: Dict[str, int] = {"low": 0, "normal": 0, "high": 0}
    for wr in window_results:
        for regime, cnt in wr.get("slippage_regime_counts", {}).items():
            if regime in slip_agg:
                slip_agg[regime] += cnt

    # 2단계 손실 스케일 적용 횟수 집계 (창별 합산)
    total_loss_scale_half = sum(wr.get("loss_scale_half_count", 0) for wr in window_results if "error" not in wr)
    total_loss_scale_full = sum(wr.get("loss_scale_full_count", 0) for wr in window_results if "error" not in wr)

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
        "sharpe_std": sharpe_std,
        "top_fail_reasons": top_fail_reasons,
        "robustness_label": "",  # perturbation_check 결과 (빈 문자열 = 미실행)
        "slippage_regime_agg": slip_agg,
        "total_loss_scale_half_count": total_loss_scale_half,
        "total_loss_scale_full_count": total_loss_scale_full,
    }


# ── CPCV 글로벌 정확도 (ML 예측 가능성 지표) ─────────────────

def run_cpcv_global(df: pd.DataFrame, symbol: str = "BTC/USDT") -> Optional[dict]:
    """전체 데이터셋에서 WalkForwardTrainer CPCV 검증 실행 (1회).

    ML 기반 시장 예측 가능성 지표: avg_test_acc >= 0.55이면 신호 신뢰도 높음.
    실패 시 None 반환 (silent).
    """
    try:
        from src.ml.trainer import WalkForwardTrainer
        trainer = WalkForwardTrainer(symbol=symbol, n_estimators=50, max_depth=4)
        result = trainer.train(df)
        if result is None or not result.passed:
            return None
        cpcv = trainer.run_cpcv_validation(df, n_splits=5)
        return cpcv
    except Exception:
        return None


# ── 상대 순위 (Composite Rank Score) ──────────────────────────
# 공유 모듈에서 import (run_bundle_oos.py에서도 동일 함수 사용)
from src.backtest.report import compute_rank_scores  # noqa: E402


# ── 리포트 ──────────────────────────────────────────────────

def generate_report(results: List[dict], data_source: str, df: pd.DataFrame, windows_count: int, symbol: str = "BTC/USDT", cpcv_result: Optional[dict] = None, model_health: Optional[dict] = None) -> str:
    results.sort(key=lambda x: x["avg_return"], reverse=True)
    lines = []
    lines.append(f"# Paper Trading 시뮬레이션 리포트 — {symbol} (Walk-Forward)\n")
    lines.append(f"_Generated: {datetime.utcnow().isoformat()}Z_")
    lines.append(f"_Symbol: {symbol}_")
    lines.append(f"_Data Source: {data_source}_")
    _idx_diff = df.index[-1] - df.index[0]
    _days_str = f"{_idx_diff.days}일" if hasattr(_idx_diff, 'days') else f"{len(df)}봉"
    lines.append(f"_Data Range: {df.index[0]} ~ {df.index[-1]} ({_days_str})_")
    _ratio = _TF_CANDLE_RATIO.get(ACTIVE_TIMEFRAME, 1.0)
    _train_c = max(10, int(TRAIN_HOURS * _ratio))
    _test_c = max(5, int(TEST_HOURS * _ratio))
    lines.append(f"_Walk-Forward: {windows_count}개 윈도우 (train={_train_c}, test={_test_c} candles [{ACTIVE_TIMEFRAME}])_")
    lines.append(f"_Initial Balance: $10,000 USDT | Fee: 0.055%/leg (0.11% round-trip) | Slippage: 0.05%_")
    _min_t = 8 if ACTIVE_TIMEFRAME == "4h" else 15
    lines.append(f"_통과 기준: 윈도우 {PASS_RATIO:.0%} 이상에서 Sharpe>=1.0, PF>=1.5, Trades>={_min_t}, MDD<=20%_\n")

    # CPCV 글로벌 ML 정확도 섹션
    if cpcv_result:
        cpcv_status = "PASS" if cpcv_result["passed"] else "FAIL"
        lines.append("## ML 예측 가능성 (CPCV)\n")
        lines.append(f"| 항목 | 값 |")
        lines.append(f"|------|-----|")
        lines.append(f"| CPCV avg_test_acc | {cpcv_result['avg_test_acc']:.3f} ± {cpcv_result['std_test_acc']:.3f} |")
        lines.append(f"| CPCV folds | {cpcv_result['n_folds']} |")
        lines.append(f"| CPCV 판정 (≥0.55) | {cpcv_status} |")
        lines.append("")

    # Model Health (ADWIN Drift Monitor)
    if model_health:
        trend_emoji = {"improving": "UP", "degrading": "DOWN", "stable": "FLAT", "unknown": "N/A"}
        trend_str = trend_emoji.get(model_health.get("ewma_trend", "unknown"), "N/A")
        lines.append("## ML 모델 건강 상태 (ADWIN)\n")
        lines.append("| 항목 | 값 |")
        lines.append("|------|-----|")
        lines.append(f"| EWMA Accuracy | {model_health.get('ewma_accuracy', 0):.4f} |")
        lines.append(f"| EWMA Trend | {trend_str} ({model_health.get('ewma_trend', 'unknown')}) |")
        lines.append(f"| EWMA Samples | {model_health.get('ewma_n', 0)} |")
        lines.append(f"| Drift Detected | {'YES' if model_health.get('drift_detected') else 'NO'} |")
        lines.append(f"| Output Drift | {'YES' if model_health.get('output_drift') else 'NO'} |")
        lines.append(f"| Retrain Recommended (EWMA) | {'YES' if model_health.get('should_retrain_by_ewma') else 'NO'} |")
        lines.append(f"| Retrain Recommended (ADWIN) | {'YES' if model_health.get('should_retrain') else 'NO'} |")
        lines.append(f"| Retrain Count | {model_health.get('retrain_count', 0)} |")
        # Feature drift details
        feat_drift = model_health.get("feature_drift", {})
        if feat_drift:
            drifted = [k for k, v in feat_drift.items() if v]
            lines.append(f"| Feature Drift | {len(drifted)}/{len(feat_drift)} features drifted |")
            if drifted:
                lines.append(f"| Drifted Features | {', '.join(drifted[:10])} |")
        lines.append("")

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
    has_robustness = any(r.get("robustness_label", "") for r in results)
    lines.append("## TOP 10 전략 (평균 수익률 기준)\n")
    if has_robustness:
        lines.append("| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Robust | Pass |")
        lines.append("|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|--------|------|")
    else:
        lines.append("| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |")
        lines.append("|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|")
    for i, r in enumerate(results[:10], 1):
        p = "PASS" if r["overall_passed"] else "FAIL"
        base = (
            f"| {i} | `{r['name']}` | {r['avg_return']:+.2%} | {r['avg_sharpe']:.2f} | "
            f"{r['avg_win_rate']:.1%} | {r['avg_profit_factor']:.2f} | {r['avg_trades']:.0f} | "
            f"{r['avg_max_dd']:.1%} | {r['passed_windows']}/{r['total_windows']}"
        )
        if has_robustness:
            rob = r.get("robustness_label", "")
            lines.append(f"{base} | {rob} | {p} |")
        else:
            lines.append(f"{base} | {p} |")
    lines.append("")

    # 상대 순위 (Composite Rank Score)
    has_scores = any("rank_score" in r for r in results)
    if has_scores:
        ranked = sorted(results, key=lambda x: x.get("rank_score", 0), reverse=True)
        lines.append("## 상대 순위 (Composite Rank Score)\n")
        lines.append("_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_")
        lines.append("_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_\n")
        lines.append("| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |")
        lines.append("|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|")
        for i, r in enumerate(ranked[:15], 1):
            p = "PASS" if r["overall_passed"] else "FAIL"
            lines.append(
                f"| {i} | `{r['name']}` | {r.get('rank_score', 0):.1f} | {r.get('percentile', '?')} | "
                f"{r['avg_sharpe']:.2f} | {r.get('sharpe_std', 0):.2f} | "
                f"{r['avg_profit_factor']:.2f} | {r['avg_trades']:.0f} | "
                f"{r['avg_max_dd']:.1%} | {r['passed_windows']}/{r['total_windows']} | {p} |"
            )
        lines.append("")

    # 전체 결과
    lines.append("## 전체 결과\n")
    if has_robustness:
        lines.append("| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Robust | Pass |")
        lines.append("|------|-----------|-----------|-------|-----------|-------------|--------|------|")
    else:
        lines.append("| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |")
        lines.append("|------|-----------|-----------|-------|-----------|-------------|------|")
    for r in results:
        p = "PASS" if r["overall_passed"] else "FAIL"
        base = (
            f"| `{r['name']}` | {r['avg_return']:+.2%} | {r['avg_sharpe']:.2f} | "
            f"{r['avg_profit_factor']:.2f} | {r['avg_trades']:.0f} | "
            f"{r['passed_windows']}/{r['total_windows']}"
        )
        if has_robustness:
            rob = r.get("robustness_label", "")
            lines.append(f"{base} | {rob} | {p} |")
        else:
            lines.append(f"{base} | {p} |")
    lines.append("")

    # FAIL 원인 분석
    failed_results = [r for r in results if not r["overall_passed"] and r.get("top_fail_reasons")]
    if failed_results:
        lines.append("## FAIL 원인 분석\n")
        lines.append("| Strategy | Top Fail Reasons (reason x count) |")
        lines.append("|----------|-----------------------------------|")
        for r in failed_results[:20]:
            reasons_str = ", ".join(
                f"{reason} (x{cnt})" for reason, cnt in r["top_fail_reasons"][:3]
            )
            lines.append(f"| `{r['name']}` | {reasons_str} |")
        lines.append("")

        from collections import Counter as _Counter
        global_fail_counter: _Counter = _Counter()
        for r in results:
            for reason, cnt in r.get("top_fail_reasons", []):
                global_fail_counter[reason] += cnt
        if global_fail_counter:
            lines.append("### 전체 FAIL 원인 빈도 (상위 10)\n")
            lines.append("| Fail Reason | Total Count |")
            lines.append("|-------------|-------------|")
            for reason, cnt in global_fail_counter.most_common(10):
                lines.append(f"| {reason} | {cnt} |")
            lines.append("")

    # 윈도우별 상세 분석 (--verbose-windows 활성화 시)
    _this_mod = sys.modules[__name__]
    if getattr(_this_mod, "VERBOSE_WINDOWS", False):
        has_scores = any("rank_score" in r for r in results)
        top_strats = sorted(results, key=lambda x: x.get("rank_score", x.get("avg_sharpe", 0)), reverse=True)[:5]
        if top_strats:
            lines.append("## 윈도우별 상세 분석 (상위 5 전략)\n")
            lines.append("_각 전략의 윈도우별 Sharpe/PF/Trades/Pass 상세. FAIL 원인 진단용._\n")
            for r in top_strats:
                wrs = r.get("window_results", [])
                mismatch_n = sum(1 for wr in wrs if not wr.get("regime_match", True) and "error" not in wr)
                lines.append(
                    f"### `{r['name']}` (rank_score={r.get('rank_score', 0):.1f}, "
                    f"consistency={r['passed_windows']}/{r['total_windows']}, "
                    f"regime_mismatch={mismatch_n}/{len(wrs)})\n"
                )
                lines.append("| Window | IS_Sh | Sharpe | PF | Trades | MDD | SlipH% | Market | IS_Reg | OOS_Reg | Match | Pass | Fail Reasons |")
                lines.append("|--------|-------|--------|-----|--------|-----|--------|--------|--------|---------|-------|------|--------------|")
                _reg_short = {"TREND_UP": "UP↑", "TREND_DOWN": "DN↓", "RANGING": "RG~", "HIGH_VOL": "HV!"}
                for wr in wrs:
                    if "error" in wr:
                        lines.append(f"| W{wr['window']} | — | ERROR | — | — | — | — | — | — | — | — | FAIL | {wr.get('error', '')[:60]} |")
                        continue
                    p = "✅" if wr["passed"] else "❌"
                    reasons = "; ".join(wr.get("fail_reasons", [])[:2])
                    is_r = _reg_short.get(wr.get("is_regime", ""), wr.get("is_regime", "?"))
                    oos_r = _reg_short.get(wr.get("oos_regime", ""), wr.get("oos_regime", "?"))
                    match = "✓" if wr.get("regime_match", True) else "✗"
                    is_sh = wr.get("is_sharpe")
                    is_sh_str = f"{is_sh:.2f}" if is_sh is not None else "N/A"
                    slip_counts = wr.get("slippage_regime_counts", {})
                    slip_total = sum(slip_counts.values())
                    slip_high_str = (
                        f"{slip_counts.get('high', 0)/slip_total:.0%}"
                        if slip_total > 0 else "-"
                    )
                    lines.append(
                        f"| W{wr['window']} | {is_sh_str} | {wr['sharpe']:.2f} | {wr['profit_factor']:.2f} | "
                        f"{wr['trades']} | {wr['max_dd']:.1%} | {slip_high_str} | {wr.get('market_state','?')} | "
                        f"{is_r} | {oos_r} | {match} | {p} | {reasons} |"
                    )
                lines.append("")

    # 2단계 손실 스케일 적용 현황 (전략별 집계)
    scale_data = [(r["name"], r.get("total_loss_scale_half_count", 0), r.get("total_loss_scale_full_count", 0))
                  for r in results if r.get("total_loss_scale_half_count", 0) + r.get("total_loss_scale_full_count", 0) > 0]
    if scale_data:
        lines.append("## 2단계 손실 스케일 적용 현황\n")
        lines.append("_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_\n")
        lines.append("| Strategy | Half(75%) | Full(50%) | 비율(full/half) |")
        lines.append("|----------|-----------|-----------|-----------------|")
        for name, half_c, full_c in sorted(scale_data, key=lambda x: x[2], reverse=True)[:10]:
            ratio = f"{full_c/half_c:.2f}" if half_c > 0 else "N/A"
            lines.append(f"| `{name}` | {half_c} | {full_c} | {ratio} |")
        lines.append("")

    # 슬리피지 레짐 분포 (adaptive_slippage=True 시 표시)
    slip_data = [(r["name"], r.get("slippage_regime_agg", {})) for r in results
                 if sum(r.get("slippage_regime_agg", {}).values()) > 0]
    if slip_data:
        lines.append("## 슬리피지 레짐 분포 (상위 10)\n")
        lines.append("_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_\n")
        lines.append("| Strategy | Low | Normal | High | High% |")
        lines.append("|----------|-----|--------|------|-------|")
        top_slip = sorted(slip_data, key=lambda x: x[1].get("high", 0) / max(sum(x[1].values()), 1), reverse=True)[:10]
        for name, agg in top_slip:
            total = sum(agg.values())
            if total == 0:
                continue
            high_pct = agg.get("high", 0) / total
            lines.append(f"| `{name}` | {agg.get('low',0)} | {agg.get('normal',0)} | {agg.get('high',0)} | {high_pct:.1%} |")
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


# ── 구조화 데이터 저장 ──────────────────────────────────────


def export_results_json(all_symbol_results: Dict[str, List[dict]], metadata: dict) -> None:
    """심볼별 전략 결과를 JSON으로 저장. 윈도우별 상세 포함."""
    output = {
        "metadata": metadata,
        "symbols": {},
    }
    for symbol, results in all_symbol_results.items():
        symbol_data = []
        for r in results:
            entry = {
                "name": r["name"],
                "overall_passed": r["overall_passed"],
                "consistency_score": round(r["consistency_score"], 4),
                "passed_windows": r["passed_windows"],
                "total_windows": r["total_windows"],
                "avg_sharpe": round(r["avg_sharpe"], 4),
                "avg_return": round(r["avg_return"], 6),
                "avg_max_dd": round(r["avg_max_dd"], 6),
                "avg_profit_factor": round(r["avg_profit_factor"], 4),
                "avg_trades": round(r["avg_trades"], 1),
                "avg_win_rate": round(r["avg_win_rate"], 4),
                "avg_final_balance": round(r["avg_final_balance"], 2),
                "sharpe_std": round(r.get("sharpe_std", 0.0), 4),
                "rank_score": r.get("rank_score", 0.0),
                "percentile": r.get("percentile", ""),
                "robustness_label": r.get("robustness_label", ""),
                "top_fail_reasons": r.get("top_fail_reasons", []),
                "window_results": r["window_results"],
            }
            symbol_data.append(entry)
        output["symbols"][symbol] = symbol_data

    RESULTS_JSON_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False, default=str))
    print(f"[EXPORT] JSON saved to {RESULTS_JSON_PATH}")


def export_results_csv(all_symbol_results: Dict[str, List[dict]]) -> None:
    """심볼별 전략 요약을 flat CSV로 저장 (한 행 = 한 전략×심볼)."""
    rows = []
    for symbol, results in all_symbol_results.items():
        for r in results:
            rows.append({
                "symbol": symbol,
                "strategy": r["name"],
                "overall_passed": r["overall_passed"],
                "consistency_score": round(r["consistency_score"], 4),
                "passed_windows": r["passed_windows"],
                "total_windows": r["total_windows"],
                "avg_sharpe": round(r["avg_sharpe"], 4),
                "avg_return": round(r["avg_return"], 6),
                "avg_max_dd": round(r["avg_max_dd"], 6),
                "avg_profit_factor": round(r["avg_profit_factor"], 4),
                "avg_trades": round(r["avg_trades"], 1),
                "avg_win_rate": round(r["avg_win_rate"], 4),
                "avg_final_balance": round(r["avg_final_balance"], 2),
                "sharpe_std": round(r.get("sharpe_std", 0.0), 4),
                "rank_score": r.get("rank_score", 0.0),
                "percentile": r.get("percentile", ""),
                "robustness_label": r.get("robustness_label", ""),
            })

    if rows:
        df_out = pd.DataFrame(rows)
        df_out.to_csv(RESULTS_CSV_PATH, index=False)
        print(f"[EXPORT] CSV saved to {RESULTS_CSV_PATH} ({len(rows)} rows)")


# ── 메인 ──────────────────────────────────────────────────

# Block Bootstrap 데이터 생성 토글 (True: Block Bootstrap, False: 기존 GBM)
# Block Bootstrap은 실제 변동성 군집(ARCH)과 자기상관을 보존하므로 GBM보다 현실적
# 환경변수 PAPER_SIM_BOOTSTRAP=0 으로 GBM 모드 강제 가능
import os as _os
USE_BLOCK_BOOTSTRAP = _os.environ.get("PAPER_SIM_BOOTSTRAP", "1") != "0"
BLOCK_BOOTSTRAP_BLOCK_SIZE = int(_os.environ.get("PAPER_SIM_BLOCK_SIZE", "24"))

# Regime weighting: HIGH_VOL fold 다운웨이팅 (Cycle 234 walk_forward.py와 동일 로직)
# 환경변수 PAPER_SIM_REGIME_WEIGHTS=1 로 활성화
USE_REGIME_WEIGHTS = _os.environ.get("PAPER_SIM_REGIME_WEIGHTS", "0") == "1"

# Perturbation check: 각 전략의 파라미터 섭동 안정성 검증 (--perturbation-check로 활성화)
USE_PERTURBATION_CHECK = False

# MC permutation test: 거래 수 필터 + 블록 크기 (BacktestEngine 전달)
# --mc-min-trades N: 최소 거래 수 (0=engine 기본값 MIN_TRADES=15)
# --mc-block-size N: 블록 셔플 크기 (1=독립, 24=일봉 블록)
MC_MIN_TRADES: int = 0
MC_BLOCK_SIZE: int = 1

SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]  # 페이퍼 시뮬 대상 (live는 여전히 BTC만)

# 전략 필터 (--strategies로 설정, None이면 전체 PASS 전략 실행)
# Cycle314 E(실행): supertrend_multi 4h 단독 실행 지원
STRATEGY_FILTER: Optional[List[str]] = None

# 타임프레임별 제외 전략 (특정 TF에서 일관되게 FAIL하는 4h 전용 전략)
# Cycle 325 A(품질):
#   value_area: 1h Sharpe=-3.08, 0/8 PASS; Bundle 4h PASS(3.069) → 4h 전용 확정
#   supertrend_multi: 1h WFO avg OOS=-2.858 WFE=-2.71; Bundle 4h PASS(3.892) → 4h 전용 확정
# Cycle 353 C(데이터):
#   wick_reversal: BTC 1h Sharpe=-2.64(-9.31% return), ETH 0 trades x8, SOL 0 trades x8
#   min_volatility=0.001(완화)도 ETH/SOL 합성 데이터에서 wick 패턴 미생성 → 구조적 1h 제외
STRATEGIES_TIMEFRAME_EXCLUDE: Dict[str, Set[str]] = {
    "1h": {"value_area", "supertrend_multi", "wick_reversal"},
}


def simulate_symbol(symbol: str, pass_list: list, engine: BacktestEngine) -> Tuple[str, List[dict]]:
    """단일 심볼에 대한 walk-forward 시뮬을 돌리고 (리포트 텍스트, 결과 리스트) 반환."""
    print(f"\n{'=' * 70}\n[{symbol}] Walk-Forward Simulation\n{'=' * 70}")

    # 데이터 수집: 항상 1h로 먼저 로드 후 필요 시 리샘플링
    tf = ACTIVE_TIMEFRAME
    base_candles = 8640  # 1h 기준 12개월

    # CSV 모드: --csv-dir 지정 시 CSV 우선 (거래소 API 스킵)
    if CSV_DATA_DIR is not None:
        df = load_ohlcv_from_csv_dir(CSV_DATA_DIR, symbol, "1h")
        data_source = f"CSV {symbol} 1h ({CSV_DATA_DIR})"
        if df is None:
            print(f"[{symbol}][WARN] CSV 로드 실패 — 거래소 API 시도", flush=True)
            df = fetch_real_data_paginated(symbol, "1h", total_candles=base_candles)
            data_source = f"Bybit {symbol} 1h (paginated)"
    else:
        df = fetch_real_data_paginated(symbol, "1h", total_candles=base_candles)
        data_source = f"Bybit {symbol} 1h (paginated)"
        # 거래소 실패 시 CSV fallback (data/historical 자동 탐색)
        if df is None:
            default_csv_dir = ROOT / "data" / "historical"
            if default_csv_dir.exists():
                df = load_ohlcv_from_csv_dir(default_csv_dir, symbol, "1h")
                if df is not None:
                    data_source = f"CSV fallback {symbol} 1h ({default_csv_dir})"
                    print(f"[{symbol}][FALLBACK] data/historical/ CSV 로드 성공", flush=True)

    # 타임프레임 리샘플링 (1h != ACTIVE_TIMEFRAME인 경우)
    if df is not None and tf != "1h":
        from src.data.data_utils import resample_ohlcv
        try:
            df = resample_ohlcv(df, tf)
            data_source = data_source.replace(" 1h ", f" {tf} (resampled from 1h) ")
            print(f"[{symbol}][DATA] Resampled to {tf}: {len(df)} candles", flush=True)
        except Exception as e:
            print(f"[{symbol}][WARN] Resample {tf} 실패: {e} — 1h 유지", flush=True)
            tf = "1h"

    if df is None:
        # 심볼별 다른 seed → 서로 다른 합성 데이터 생성
        symbol_seed = hash(symbol) % (2**31)
        print(f"[{symbol}][FALLBACK] Using synthetic data (seed={symbol_seed}, Bybit API inaccessible)")
        from scripts.quality_audit import make_synthetic_data
        if USE_BLOCK_BOOTSTRAP:
            from scripts.quality_audit import make_block_bootstrap_data
            seed_df = make_synthetic_data(8640, seed=symbol_seed)
            df = make_block_bootstrap_data(
                seed_df, n=8640, block_size=BLOCK_BOOTSTRAP_BLOCK_SIZE,
                seed=symbol_seed, initial_price=float(seed_df["close"].iloc[0]),
            )
            data_source = (f"Synthetic BlockBootstrap x8640 ({symbol}-like, "
                           f"seed={symbol_seed}, block={BLOCK_BOOTSTRAP_BLOCK_SIZE})")
            print(f"[{symbol}][DATA] Block Bootstrap mode (block_size={BLOCK_BOOTSTRAP_BLOCK_SIZE})")
        else:
            df = make_synthetic_data(8640, seed=symbol_seed)
            data_source = f"Synthetic GBM x8640 ({symbol}-like, seed={symbol_seed})"
        # 합성 데이터도 ACTIVE_TIMEFRAME으로 리샘플링 (1h != tf인 경우)
        if tf != "1h":
            from src.data.data_utils import resample_ohlcv
            try:
                df = resample_ohlcv(df, tf)
                data_source += f" [{tf}]"
                print(f"[{symbol}][DATA] Synthetic resampled to {tf}: {len(df)} candles", flush=True)
            except Exception as e:
                print(f"[{symbol}][WARN] Synthetic resample {tf} 실패: {e} — 1h 유지", flush=True)
        df = enrich_indicators(df)
    else:
        df = enrich_indicators(df)

    print(f"[{symbol}][DATA] Total candles: {len(df)}")

    windows = make_walk_forward_windows(df)

    results = []
    load_failures = 0
    eval_errors = 0
    _excluded_for_tf = STRATEGIES_TIMEFRAME_EXCLUDE.get(tf, set())
    for idx, (mod_name, cls_name) in enumerate(pass_list):
        if mod_name in _excluded_for_tf:
            continue
        cls = load_strategy_class(mod_name, cls_name)
        if cls is None:
            load_failures += 1
            continue
        try:
            s_params = PAPER_SIM_STRATEGY_PARAMS.get(mod_name, {})
            result = evaluate_strategy_walk_forward(cls, windows, engine, strategy_params=s_params or None)
            results.append(result)
            if (idx + 1) % 50 == 0:
                print(f"[{symbol}][PROGRESS] {idx + 1}/{len(pass_list)} evaluated", flush=True)
        except Exception as e:
            eval_errors += 1
            print(f"[{symbol}][ERROR] {mod_name}: {str(e)[:80]}")

    if load_failures or eval_errors:
        print(f"[{symbol}][WARN] load_failures={load_failures}, eval_errors={eval_errors} "
              f"(of {len(pass_list)} total)")

    # Perturbation check (--perturbation-check 활성화 시)
    if USE_PERTURBATION_CHECK and results:
        print(f"[{symbol}][PERTURBATION] Running perturbation check on {len(results)} strategies...", flush=True)
        perturb_params = {
            "atr_multiplier_sl": engine.atr_multiplier_sl,
            "atr_multiplier_tp": engine.atr_multiplier_tp,
        }
        fragile_count = 0
        for idx_r, r in enumerate(results):
            mod_name = None
            cls_name = None
            # pass_list에서 매칭되는 전략 찾기
            for mn, cn in pass_list:
                loaded = load_strategy_class(mn, cn)
                if loaded is not None:
                    try:
                        inst = loaded()
                        if inst.name == r["name"]:
                            mod_name, cls_name = mn, cn
                            break
                    except Exception:
                        continue
            if mod_name is None:
                r["robustness_label"] = "N/A"
                continue
            strategy_cls = load_strategy_class(mod_name, cls_name)
            if strategy_cls is None:
                r["robustness_label"] = "N/A"
                continue
            try:
                strategy_inst = strategy_cls()
                # 전체 데이터 중 마지막 테스트 윈도우 구간 사용 (빠른 평가)
                _test_candles = max(5, int(TEST_HOURS * _TF_CANDLE_RATIO.get(ACTIVE_TIMEFRAME, 1.0)))
                eval_len = min(_test_candles + 100, len(df))
                eval_df = df.iloc[-eval_len:]
                pc = engine.perturbation_check(
                    strategy_inst, perturb_params, eval_df, perturbation_pcts=[0.1],
                )
                r["robustness_label"] = pc["robustness_label"]
                if pc["robustness_label"] == "FRAGILE":
                    fragile_count += 1
                    fragile_info = ", ".join(pc.get("fragile_params", []))
                    print(f"  [WARN] {r['name']}: FRAGILE (fragile params: {fragile_info})", flush=True)
            except Exception as e:
                r["robustness_label"] = "ERROR"
                print(f"  [ERROR] {r['name']}: perturbation_check failed: {str(e)[:80]}", flush=True)
        print(f"[{symbol}][PERTURBATION] Done. FRAGILE: {fragile_count}/{len(results)}", flush=True)

    # 상대 순위 계산 (0/N PASS 상황에서도 전략 간 우위 파악 가능)
    compute_rank_scores(results)

    passed = [r for r in results if r["overall_passed"]]
    print(f"[{symbol}][SUMMARY] {len(passed)}/{len(results)} PASSED (consistency >= {PASS_RATIO:.0%})")
    for r in sorted(passed, key=lambda x: x["avg_return"], reverse=True)[:5]:
        print(f"  {r['name']:<30} avg_return={r['avg_return']:+.2%} "
              f"sharpe={r['avg_sharpe']:.2f} consistency={r['passed_windows']}/{r['total_windows']}")
    # 상위 5개 전략 rank_score 출력 (PASS 여부와 무관)
    top_ranked = sorted(results, key=lambda x: x.get("rank_score", 0), reverse=True)[:5]
    if top_ranked and not passed:
        print(f"[{symbol}][RANK] Top 5 by composite score (all FAIL, relative ranking):")
        for r in top_ranked:
            print(f"  {r['name']:<30} score={r.get('rank_score', 0):.1f} "
                  f"sharpe={r['avg_sharpe']:.2f} trades={r['avg_trades']:.0f} "
                  f"pctl={r.get('percentile', '?')}")

    # CPCV 글로벌 정확도 (ML 예측 가능성 지표, 선택 실행)
    cpcv_result = run_cpcv_global(df, symbol=symbol)
    if cpcv_result:
        print(f"[{symbol}][CPCV] avg_test_acc={cpcv_result['avg_test_acc']:.3f} "
              f"± {cpcv_result['std_test_acc']:.3f} "
              f"({'PASS' if cpcv_result['passed'] else 'FAIL'}, {cpcv_result['n_folds']} folds)",
              flush=True)
    else:
        print(f"[{symbol}][CPCV] N/A (데이터 부족 또는 ML 학습 실패)", flush=True)

    # Model Health (ADWIN drift monitor) — DualGateADWINMonitor로 피처 드리프트 스냅샷
    model_health = None
    try:
        from src.ml.drift_detector import DualGateADWINMonitor
        monitor = DualGateADWINMonitor(delta=0.05, feature_names=["rsi14", "ema_ratio", "volatility"])
        # 최근 데이터로 피처 값 주입 (마지막 200봉)
        tail = df.tail(200)
        for _, row in tail.iterrows():
            feats = {}
            if "rsi14" in row and not np.isnan(row["rsi14"]):
                feats["rsi14"] = float(row["rsi14"])
            if "ema20" in row and "ema50" in row and row["ema50"] != 0:
                feats["ema_ratio"] = float(row["ema20"] / row["ema50"])
            if "atr14" in row and "close" in row and row["close"] != 0:
                feats["volatility"] = float(row["atr14"] / row["close"])
            if feats:
                monitor.update(feature_values=feats)
        model_health = monitor.get_model_health()
        trend = model_health.get("ewma_trend", "unknown")
        drift = model_health.get("drift_detected", False)
        print(f"[{symbol}][MODEL_HEALTH] trend={trend}, drift={'YES' if drift else 'NO'}, "
              f"ewma_acc={model_health.get('ewma_accuracy', 0):.4f}", flush=True)
    except Exception as e:
        print(f"[{symbol}][MODEL_HEALTH] N/A ({type(e).__name__}: {str(e)[:60]})", flush=True)

    report = generate_report(results, data_source, df, len(windows), symbol=symbol,
                             cpcv_result=cpcv_result, model_health=model_health)
    return report, results


def run_simulation(mc_p_threshold: float = 0.10, pass_ratio: float = 0.5,
                   fee_rate_override: Optional[float] = None,
                   slippage_override: Optional[float] = None,
                   min_hold_bars: int = 0,
                   atr_multiplier_tp: float = 3.5,
                   max_hold_override: Optional[int] = None):
    print("=" * 70)
    print(f"Paper Trading Simulation (Walk-Forward) — {datetime.utcnow().isoformat()}Z")
    print(f"Symbols: {', '.join(SYMBOLS)} | Timeframe: {ACTIVE_TIMEFRAME}")
    print(f"Regime Weights: {'ON' if USE_REGIME_WEIGHTS else 'OFF'}")
    print("=" * 70)

    # MC p-value 임계값 패치 (Cycle296 B: 기본 0.10으로 완화, --mc-p-threshold로 조절 가능)
    import src.backtest.engine as _engine_mod
    _engine_mod.MC_P_THRESHOLD = mc_p_threshold
    if mc_p_threshold != 0.10:
        print(f"[CONFIG] MC p-value threshold overridden: {mc_p_threshold}", flush=True)

    # 일관성 통과 비율 패치 (기본 0.5, --pass-ratio로 완화 가능)
    global PASS_RATIO
    if pass_ratio != PASS_RATIO:
        PASS_RATIO = pass_ratio
        print(f"[CONFIG] Pass ratio overridden: {pass_ratio:.0%}", flush=True)

    pass_list = load_pass_strategies()
    if not pass_list:
        print("[ERROR] 전략 없음. quality_audit.py 먼저 실행.")
        return 1
    print(f"[STRATEGIES] Loaded {len(pass_list)} strategies")

    _fee_rate = fee_rate_override if fee_rate_override is not None else 0.00055
    _slippage = slippage_override if slippage_override is not None else 0.0005
    if fee_rate_override is not None:
        print(f"[CONFIG] fee_rate overridden: {_fee_rate} (gross alpha mode)", flush=True)
    if slippage_override is not None:
        print(f"[CONFIG] slippage overridden: {_slippage}", flush=True)

    if atr_multiplier_tp != 3.5:
        print(f"[CONFIG] atr_multiplier_tp overridden: {atr_multiplier_tp} (default 3.5)", flush=True)
    engine = BacktestEngine(
        initial_balance=10_000,
        fee_rate=_fee_rate,
        slippage_pct=_slippage,
        mc_min_trades=getattr(_this, "MC_MIN_TRADES", 0),
        mc_block_size=getattr(_this, "MC_BLOCK_SIZE", 1),
        # Cycle298 B: 연속 손실 5회 시 포지션 50% 축소
        consec_loss_scale_threshold=getattr(_this, "CONSEC_LOSS_SCALE_THRESHOLD", 5),
        # Cycle299 E(실행): ATR 기반 레짐별 가변 슬리피지 (low=0.02%, normal=0.05%, high=0.15%)
        # 고변동성 구간의 시장 충격을 현실적으로 반영, 저변동성 sideways 구간 유리
        adaptive_slippage=True,
        # Cycle350 A(품질): ACTIVE_TIMEFRAME 전달 — 4h 실행 시 tf_scale 보정 오작동 수정
        # 미전달 시 engine 기본값 "1h"로 고정 → 4h ATR14/close가 1h 임계값에 비교돼 100% HIGH 오분류
        timeframe=ACTIVE_TIMEFRAME,
        # Cycle332 B(리스크): 청산 후 재진입 대기 봉수 (0=비활성)
        min_hold_bars=min_hold_bars,
        # Cycle337 B: 1h paper_sim MAX_HOLD=48봉(48h) → 4h Bundle OOS 24봉(4일)과 분리
        # Cycle349 E(실행): --max-hold-override로 CLI에서 조정 가능
        #   기본값: 1h→48봉(48h), 4h→24봉(4일, Bundle OOS와 통일)
        max_hold_candles_override=max_hold_override if max_hold_override is not None else (
            24 if ACTIVE_TIMEFRAME == "4h" else 48
        ),
        # Cycle338 B(리스크): atr_multiplier_tp 탐색 (3.5→2.5 비교)
        atr_multiplier_tp=atr_multiplier_tp,
        # Cycle351 B: 4h paper_sim min_trades 완화 (15→8)
        # 4h 60일 window, max_hold=24봉(4일) → 이론 최대 15 trades, 실제 avg 8-10
        # min_trades=15는 1h 기준으로 4h에서는 구조적으로 달성 불가
        min_trades_override=8 if ACTIVE_TIMEFRAME == "4h" else 0,
    )

    sections = []
    all_symbol_results: Dict[str, List[dict]] = {}
    fatal_count = 0
    header = (
        f"# Paper Trading 시뮬레이션 통합 리포트\n\n"
        f"_Generated: {datetime.utcnow().isoformat()}Z_\n"
        f"_Symbols: {', '.join(SYMBOLS)}_\n\n---\n\n"
    )
    for symbol in SYMBOLS:
        try:
            report_text, results = simulate_symbol(symbol, pass_list, engine)
            sections.append(report_text)
            all_symbol_results[symbol] = results
        except Exception as e:
            fatal_count += 1
            print(f"[{symbol}][FATAL] {e}")
            sections.append(f"# {symbol} 시뮬 실패\n\n{e}\n")
        # 심볼별 완료 즉시 중간 결과 저장 (타임아웃 시 부분 리포트 보존)
        REPORT_PATH.write_text(header + "\n\n---\n\n".join(sections))

    print(f"\n[REPORT] Saved to {REPORT_PATH}")

    # 구조화 데이터 저장 (JSON + CSV)
    if all_symbol_results:
        metadata = {
            "generated": datetime.utcnow().isoformat() + "Z",
            "symbols": list(all_symbol_results.keys()),
            "strategies_loaded": len(pass_list),
            "timeframe": ACTIVE_TIMEFRAME,
            "train_hours": TRAIN_HOURS,
            "test_hours": TEST_HOURS,
            "step_hours": STEP_HOURS,
            "pass_ratio": PASS_RATIO,
            "initial_balance": 10_000,
            "fee_rate": _fee_rate,
            "slippage_pct": _slippage,
            "synthetic_data_mode": "BlockBootstrap" if USE_BLOCK_BOOTSTRAP else "GBM",
            "block_bootstrap_block_size": BLOCK_BOOTSTRAP_BLOCK_SIZE if USE_BLOCK_BOOTSTRAP else None,
            "regime_weights": USE_REGIME_WEIGHTS,
        }
        export_results_json(all_symbol_results, metadata)
        export_results_csv(all_symbol_results)

    if fatal_count:
        print(f"[WARN] {fatal_count}/{len(SYMBOLS)} symbols failed fatally")
    return 1 if fatal_count == len(SYMBOLS) else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Paper Trading Walk-Forward Simulation")
    parser.add_argument(
        "--mc-p-threshold",
        type=float,
        default=0.10,
        help="MC permutation test p-value 상한 (Cycle296 B: 기본 0.10, 예: 0.05로 강화 가능)",
    )
    parser.add_argument(
        "--pass-ratio",
        type=float,
        default=0.5,
        help="일관성 통과 비율 (기본 0.50 = 50%%, 예: 0.33으로 완화 가능)",
    )
    parser.add_argument(
        "--block-size",
        type=int,
        default=None,
        help="Block Bootstrap 블록 크기 (기본 24, 예: 72 또는 144로 트렌드 보존 강화)",
    )
    parser.add_argument(
        "--regime-weights",
        action="store_true",
        default=False,
        help="HIGH_VOL fold 다운웨이팅 활성화 (Cycle 234 regime weighting)",
    )
    parser.add_argument(
        "--perturbation-check",
        action="store_true",
        default=False,
        help="각 전략의 파라미터 섭동 안정성 검증 (ROBUST/MODERATE/FRAGILE 판정)",
    )
    parser.add_argument(
        "--mc-min-trades",
        type=int,
        default=0,
        help="MC permutation test 최소 거래 수 (기본 0=engine 내부 MIN_TRADES=15 사용)",
    )
    parser.add_argument(
        "--mc-block-size",
        type=int,
        default=1,
        help="MC block sign randomization 크기 (기본 1=독립 셔플, 24=1h→daily blocks)",
    )
    parser.add_argument(
        "--csv-dir",
        type=str,
        default=None,
        help="로컬 CSV 데이터 디렉토리 (지정 시 CSV 우선 사용, 예: data/historical)",
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=None,
        help="실행할 심볼 목록 (기본: BTC/USDT ETH/USDT SOL/USDT, 예: --symbols BTC/USDT)",
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        default="1h",
        help="타임프레임 (기본: 1h, 예: 4h — 1h CSV를 리샘플링하여 사용)",
    )
    parser.add_argument(
        "--verbose-windows",
        action="store_true",
        default=False,
        help="윈도우별 상세 분석 출력: 상위 5 전략의 윈도우별 Sharpe/PF/Trades/Pass 테이블 추가",
    )
    parser.add_argument(
        "--strategies",
        nargs="+",
        default=None,
        help="실행할 전략 모듈명 필터 (예: --strategies supertrend_multi narrow_range)",
    )
    parser.add_argument(
        "--fee-rate",
        type=float,
        default=None,
        help="수수료율 오버라이드 (기본 0.00055=0.055%%, 0.0으로 gross alpha 측정)",
    )
    parser.add_argument(
        "--slippage",
        type=float,
        default=None,
        help="슬리피지 오버라이드 (기본 0.0005=0.05%%, 0.0으로 gross alpha 측정)",
    )
    parser.add_argument(
        "--min-hold-bars",
        type=int,
        default=0,
        help="Cycle332 B: 청산 후 재진입 대기 봉수 (기본 0=비활성, 예: 4=4봉 대기)",
    )
    parser.add_argument(
        "--atr-multiplier-tp",
        type=float,
        default=3.5,
        help="Cycle338 B: ATR TP 배수 (기본 3.5, 예: 2.5 — R:R 축소, BEP WR 38% 상승)",
    )
    parser.add_argument(
        "--max-hold-override",
        type=int,
        default=None,
        help="Cycle349 E: 최대 보유 봉수 오버라이드 (기본 48=1h 48h, 4h 시 24=4일 권장)",
    )
    args = parser.parse_args()
    # Module-level vars: use sys.modules to avoid 'global' at module scope (Python 3.7)
    _this = sys.modules[__name__]
    if args.block_size is not None:
        _this.BLOCK_BOOTSTRAP_BLOCK_SIZE = args.block_size
        print(f"[CONFIG] Block Bootstrap block_size overridden: {args.block_size}", flush=True)
    if args.regime_weights:
        _this.USE_REGIME_WEIGHTS = True
        print(f"[CONFIG] Regime weights enabled (HIGH_VOL fold downweighting)", flush=True)
    if args.perturbation_check:
        _this.USE_PERTURBATION_CHECK = True
        print(f"[CONFIG] Perturbation check enabled (ROBUST/MODERATE/FRAGILE)", flush=True)
    if args.mc_min_trades > 0:
        _this.MC_MIN_TRADES = args.mc_min_trades
        print(f"[CONFIG] MC min trades overridden: {args.mc_min_trades}", flush=True)
    if args.mc_block_size > 1:
        _this.MC_BLOCK_SIZE = args.mc_block_size
        print(f"[CONFIG] MC block size overridden: {args.mc_block_size}", flush=True)
    if args.csv_dir is not None:
        _this.CSV_DATA_DIR = Path(args.csv_dir).expanduser().resolve()
        print(f"[CONFIG] CSV data dir: {_this.CSV_DATA_DIR}", flush=True)
    if args.symbols is not None:
        _this.SYMBOLS = args.symbols
        print(f"[CONFIG] Symbols overridden: {_this.SYMBOLS}", flush=True)
    if args.timeframe != "1h":
        if args.timeframe not in _TF_CANDLE_RATIO:
            print(f"[CONFIG] 지원하지 않는 timeframe: {args.timeframe} — 1h 사용", flush=True)
        else:
            _this.ACTIVE_TIMEFRAME = args.timeframe
            print(f"[CONFIG] Timeframe overridden: {args.timeframe}", flush=True)
    if args.verbose_windows:
        _this.VERBOSE_WINDOWS = True
        print("[CONFIG] Verbose windows enabled: per-window detail for top 5 strategies", flush=True)
    if args.strategies:
        _this.STRATEGY_FILTER = args.strategies
        print(f"[CONFIG] Strategy filter: {args.strategies}", flush=True)
    if args.min_hold_bars > 0:
        print(f"[CONFIG] min_hold_bars overridden: {args.min_hold_bars}", flush=True)
    if args.max_hold_override is not None:
        print(f"[CONFIG] max_hold_candles overridden: {args.max_hold_override}", flush=True)
    sys.exit(run_simulation(
        mc_p_threshold=args.mc_p_threshold,
        pass_ratio=args.pass_ratio,
        fee_rate_override=args.fee_rate,
        slippage_override=args.slippage,
        min_hold_bars=args.min_hold_bars,
        atr_multiplier_tp=args.atr_multiplier_tp,
        max_hold_override=args.max_hold_override,
    ))
