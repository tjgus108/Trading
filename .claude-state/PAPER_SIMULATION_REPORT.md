# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-26T00:09:54.963634Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-26T00:12:49.401890Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic GBM x8640 (BTC/USDT-like, seed=761846147)_
_Data Range: 0 ~ 8639 (8640봉)_
_Walk-Forward: 4개 윈도우 (train=5040h, test=1440h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | 32.29% |
| 최고 수익률 | 136.01% (price_action_momentum) |
| 최저 수익률 | -8.86% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +136.01% | 7.08 | 50.7% | 1.85 | 169 | 12.5% | 0/4 | FAIL |
| 2 | `cmf` | +110.72% | 6.13 | 51.7% | 1.94 | 115 | 17.2% | 0/4 | FAIL |
| 3 | `supertrend_multi` | +86.41% | 6.70 | 51.6% | 1.93 | 134 | 12.2% | 0/4 | FAIL |
| 4 | `momentum_quality` | +77.17% | 6.04 | 51.4% | 1.84 | 125 | 11.2% | 0/4 | FAIL |
| 5 | `order_flow_imbalance_v2` | +70.80% | 5.17 | 51.5% | 1.82 | 90 | 14.3% | 0/4 | FAIL |
| 6 | `lob_maker` | +68.03% | 3.84 | 46.1% | 1.53 | 124 | 16.3% | 0/4 | FAIL |
| 7 | `acceleration_band` | +47.97% | 4.35 | 47.3% | 1.67 | 93 | 11.8% | 0/4 | FAIL |
| 8 | `elder_impulse` | +31.42% | 3.88 | 49.4% | 1.84 | 57 | 6.5% | 0/4 | FAIL |
| 9 | `htf_ema` | +27.76% | 3.04 | 47.1% | 1.53 | 71 | 14.2% | 0/4 | FAIL |
| 10 | `relative_volume` | +27.07% | 3.87 | 49.9% | 1.78 | 58 | 7.8% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +136.01% | 7.08 | 1.85 | 169 | 0/4 | FAIL |
| `cmf` | +110.72% | 6.13 | 1.94 | 115 | 0/4 | FAIL |
| `supertrend_multi` | +86.41% | 6.70 | 1.93 | 134 | 0/4 | FAIL |
| `momentum_quality` | +77.17% | 6.04 | 1.84 | 125 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +70.80% | 5.17 | 1.82 | 90 | 0/4 | FAIL |
| `lob_maker` | +68.03% | 3.84 | 1.53 | 124 | 0/4 | FAIL |
| `acceleration_band` | +47.97% | 4.35 | 1.67 | 93 | 0/4 | FAIL |
| `elder_impulse` | +31.42% | 3.88 | 1.84 | 57 | 0/4 | FAIL |
| `htf_ema` | +27.76% | 3.04 | 1.53 | 71 | 0/4 | FAIL |
| `relative_volume` | +27.07% | 3.87 | 1.78 | 58 | 0/4 | FAIL |
| `volatility_cluster` | +12.12% | 1.82 | 1.30 | 78 | 0/4 | FAIL |
| `linear_channel_rev` | +10.20% | 2.21 | 1.60 | 35 | 0/4 | FAIL |
| `roc_ma_cross` | +9.02% | 2.00 | 1.51 | 33 | 0/4 | FAIL |
| `wick_reversal` | +3.14% | 2.08 | 750.73 | 2 | 0/4 | FAIL |
| `positional_scaling` | +1.99% | 0.51 | 1.18 | 25 | 0/4 | FAIL |
| `frama` | +1.31% | 0.28 | 1.07 | 79 | 0/4 | FAIL |
| `price_cluster` | +1.26% | 0.46 | 0.76 | 4 | 0/4 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `narrow_range` | -0.31% | 0.06 | 1.06 | 51 | 0/4 | FAIL |
| `value_area` | -0.39% | -0.32 | 1.07 | 8 | 0/4 | FAIL |
| `dema_cross` | -2.48% | -1.25 | 0.74 | 13 | 0/4 | FAIL |
| `engulfing_zone` | -8.86% | -2.29 | 0.60 | 20 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +32.29% -> $13,229
- **Top 5 균등배분**: +96.22% -> $19,622
