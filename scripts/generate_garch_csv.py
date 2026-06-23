"""
GARCH(1,1) 기반 합성 OHLCV CSV 생성기.

사용:
    python3 scripts/generate_garch_csv.py [--symbols ETH SOL] [--rows 12000]

출력:
    data/historical/synthetic/{SYMBOL}USDT/1h.csv
    형식: timestamp,open,high,low,close,volume (BTC CSV 동일)
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT_BASE = ROOT / "data" / "historical" / "synthetic"

# 심볼별 파라미터 (실제 2023년 가격대 기준)
SYMBOL_PARAMS = {
    "ETH": {
        "start_price": 1200.0,
        "daily_vol": 0.030,   # BTC ~0.025, ETH 약간 높음
        "garch_alpha": 0.06,
        "garch_beta": 0.89,
        "bull_drift": 0.00055,
        "bear_drift": -0.00050,
        "bull_to_bear": 0.006,
        "bear_to_bull": 0.05,
        "vol_spike_prob": 0.28,
        # OU 평균회귀 파라미터: 가격이 log-앵커로 회귀
        "ou_theta": 0.008,       # Cycle260: 0.003→0.008, max 6000 이하 목표
        "ou_anchor_mult": 2.0,   # 앵커 = start_price*2.0=2400 (2023 ETH 중간값)
        "price_max_mult": 4.0,   # start_price*4=4800 초과 시 강제 하향 드리프트
        "price_min_mult": 0.15,  # start_price * 0.15 미만 시 강제 상향 드리프트
    },
    "SOL": {
        "start_price": 15.0,
        "daily_vol": 0.055,   # SOL 고변동성
        "garch_alpha": 0.08,
        "garch_beta": 0.87,
        "bull_drift": 0.00080,
        "bear_drift": -0.00070,
        "bull_to_bear": 0.005,
        "bear_to_bull": 0.06,
        "vol_spike_prob": 0.35,
        # OU 평균회귀: SOL 2023 범위 ~10~250
        "ou_theta": 0.004,
        "ou_anchor_mult": 5.0,   # 앵커 = 15 * 5 = 75 (2023 SOL 중간값 ~60-80)
        "price_max_mult": 20.0,  # 15 * 20 = 300 초과 시 강제 하향
        "price_min_mult": 0.20,  # 15 * 0.2 = 3 미만 시 강제 상향
    },
}


def generate_garch_ohlcv(
    symbol: str,
    n_bars: int = 12000,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    params = SYMBOL_PARAMS[symbol]

    price = params["start_price"]
    base_vol = params["daily_vol"] / np.sqrt(24)  # 시간봉 변동성
    sigma2 = base_vol ** 2
    alpha = params["garch_alpha"]
    beta = params["garch_beta"]
    omega = sigma2 * (1 - alpha - beta)

    # 레짐 상태
    regime = "bull"  # "bull" | "bear"
    p_bull_to_bear = params["bull_to_bear"]
    p_bear_to_bull = params["bear_to_bull"]

    closes = np.empty(n_bars)
    opens = np.empty(n_bars)
    highs = np.empty(n_bars)
    lows = np.empty(n_bars)
    volumes = np.empty(n_bars)

    vol_spike_countdown = 0

    for i in range(n_bars):
        # GARCH 변동성 업데이트
        if i > 0:
            eps = np.clip(closes[i - 1] / max(opens[i - 1], 1e-10) - 1.0, -0.15, 0.15)
            sigma2 = omega + alpha * eps ** 2 + beta * sigma2
            # Cycle348 C(데이터): 10x→4x로 sigma 상한 축소 (ETH synthetic HL 2.88x 과장 수정)
            sigma2 = np.clip(sigma2, (base_vol * 0.3) ** 2, (base_vol * 4) ** 2)

        # 변동성 스파이크 (50봉마다 일정 확률)
        if vol_spike_countdown > 0:
            # Cycle348 C: 2.5x→1.5x로 스파이크 배율 감소 (과도한 HL 범위 방지)
            sigma2 *= 1.5
            vol_spike_countdown -= 1
        elif i > 0 and i % 50 == 0 and rng.random() < params["vol_spike_prob"]:
            vol_spike_countdown = rng.integers(8, 15)

        sigma = np.sqrt(sigma2)

        # 레짐 전환
        if regime == "bull" and rng.random() < p_bull_to_bear:
            regime = "bear"
        elif regime == "bear" and rng.random() < p_bear_to_bull:
            regime = "bull"

        base_drift = params["bull_drift"] if regime == "bull" else params["bear_drift"]

        # Ornstein-Uhlenbeck 평균회귀: log-price를 앵커로 당김
        ou_theta = params["ou_theta"]
        ou_anchor = np.log(params["start_price"] * params["ou_anchor_mult"])
        ou_correction = ou_theta * (ou_anchor - np.log(max(price, 1e-6)))
        drift = base_drift + ou_correction

        # 가격 한계 초과 시 강제 드리프트 반전 (2차 안전장치)
        p_max = params["start_price"] * params["price_max_mult"]
        p_min = params["start_price"] * params["price_min_mult"]
        if price >= p_max:
            drift = min(drift, -abs(base_drift) * 3)
        elif price <= p_min:
            drift = max(drift, abs(base_drift) * 3)

        ret = np.clip(drift + sigma * rng.standard_normal(), -0.15, 0.15)

        open_p = price
        close_p = open_p * (1 + ret)
        close_p = max(close_p, open_p * 0.5)

        # wick 생성 (변동성 기반)
        # Cycle348 C: base_vol*3으로 wick 상한 추가 (스파이크 시 HL 폭발 방지)
        wick_scale = min(sigma * rng.uniform(0.3, 1.2), base_vol * 3)
        high_p = max(open_p, close_p) * (1 + abs(wick_scale))
        low_p = min(open_p, close_p) * (1 - abs(wick_scale))

        vol = max(10.0, rng.lognormal(mean=5.0, sigma=0.8) * (1 + 3 * sigma / base_vol))

        opens[i] = open_p
        closes[i] = close_p
        highs[i] = high_p
        lows[i] = low_p
        volumes[i] = vol
        price = close_p

    start_dt = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    timestamps = [start_dt + timedelta(hours=i) for i in range(n_bars)]

    df = pd.DataFrame({
        "timestamp": [str(t) for t in timestamps],
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="GARCH 합성 CSV 생성")
    parser.add_argument("--symbols", nargs="+", default=["ETH", "SOL"])
    parser.add_argument("--rows", type=int, default=12000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    for sym in args.symbols:
        if sym not in SYMBOL_PARAMS:
            print(f"[SKIP] 알 수 없는 심볼: {sym}", flush=True)
            continue

        out_dir = OUT_BASE / f"{sym}USDT" / "1h.csv"
        out_dir.parent.mkdir(parents=True, exist_ok=True)

        print(f"[GEN] {sym}/USDT {args.rows}봉 GARCH 합성 데이터 생성 중...", flush=True)
        df = generate_garch_ohlcv(sym, n_bars=args.rows, seed=args.seed)
        df.to_csv(out_dir, index=False)
        print(f"[OK] 저장: {out_dir}  ({len(df)} rows)", flush=True)


if __name__ == "__main__":
    main()
