# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-26T10:19:59.977391Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-26T10:22:34.921766Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic GBM x8640 (BTC/USDT-like, seed=2055536277)_
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
| 평균 수익률 | 33.77% |
| 최고 수익률 | 216.67% (price_action_momentum) |
| 최저 수익률 | -14.81% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +216.67% | 9.19 | 54.6% | 2.40 | 168 | 15.2% | 0/4 | FAIL |
| 2 | `momentum_quality` | +117.38% | 7.83 | 55.4% | 2.30 | 130 | 9.9% | 0/4 | FAIL |
| 3 | `cmf` | +110.56% | 5.78 | 49.6% | 1.81 | 133 | 18.9% | 0/4 | FAIL |
| 4 | `supertrend_multi` | +101.92% | 8.05 | 58.8% | 2.69 | 100 | 7.4% | 0/4 | FAIL |
| 5 | `volume_breakout` | +81.98% | 6.01 | 54.3% | 2.26 | 80 | 10.6% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | +48.17% | 3.77 | 46.5% | 1.59 | 92 | 13.7% | 0/4 | FAIL |
| 7 | `htf_ema` | +29.29% | 3.22 | 48.4% | 1.59 | 64 | 9.3% | 0/4 | FAIL |
| 8 | `lob_maker` | +25.65% | 1.98 | 40.9% | 1.26 | 126 | 23.2% | 0/4 | FAIL |
| 9 | `linear_channel_rev` | +11.02% | 2.45 | 47.9% | 1.73 | 30 | 5.1% | 0/4 | FAIL |
| 10 | `relative_volume` | +9.17% | 1.50 | 41.8% | 1.32 | 57 | 12.0% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +216.67% | 9.19 | 2.40 | 168 | 0/4 | FAIL |
| `momentum_quality` | +117.38% | 7.83 | 2.30 | 130 | 0/4 | FAIL |
| `cmf` | +110.56% | 5.78 | 1.81 | 133 | 0/4 | FAIL |
| `supertrend_multi` | +101.92% | 8.05 | 2.69 | 100 | 0/4 | FAIL |
| `volume_breakout` | +81.98% | 6.01 | 2.26 | 80 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +48.17% | 3.77 | 1.59 | 92 | 0/4 | FAIL |
| `htf_ema` | +29.29% | 3.22 | 1.59 | 64 | 0/4 | FAIL |
| `lob_maker` | +25.65% | 1.98 | 1.26 | 126 | 0/4 | FAIL |
| `linear_channel_rev` | +11.02% | 2.45 | 1.73 | 30 | 0/4 | FAIL |
| `relative_volume` | +9.17% | 1.50 | 1.32 | 57 | 0/4 | FAIL |
| `roc_ma_cross` | +8.01% | 1.77 | 1.60 | 35 | 0/4 | FAIL |
| `volatility_cluster` | +7.08% | 1.09 | 1.19 | 82 | 0/4 | FAIL |
| `acceleration_band` | +7.01% | 0.93 | 1.15 | 90 | 0/4 | FAIL |
| `dema_cross` | +1.07% | 0.53 | 1.23 | 10 | 0/4 | FAIL |
| `wick_reversal` | +0.59% | -0.05 | 500.00 | 1 | 0/4 | FAIL |
| `positional_scaling` | +0.28% | 0.13 | 1.08 | 27 | 0/4 | FAIL |
| `price_cluster` | -0.23% | -0.39 | 1.05 | 6 | 0/4 | FAIL |
| `narrow_range` | -1.17% | -0.19 | 1.04 | 50 | 0/4 | FAIL |
| `value_area` | -2.33% | -1.01 | 0.85 | 13 | 0/4 | FAIL |
| `elder_impulse` | -5.41% | -0.77 | 0.92 | 50 | 0/4 | FAIL |
| `engulfing_zone` | -8.90% | -2.26 | 0.65 | 19 | 0/4 | FAIL |
| `frama` | -14.81% | -1.85 | 0.84 | 86 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +33.77% -> $13,377
- **Top 5 균등배분**: +125.70% -> $22,570


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-26T10:25:03.926159Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic GBM x8640 (ETH/USDT-like, seed=976293227)_
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
| 평균 수익률 | 32.47% |
| 최고 수익률 | 138.29% (cmf) |
| 최저 수익률 | -14.62% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `cmf` | +138.29% | 7.26 | 55.5% | 2.23 | 113 | 13.1% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +134.47% | 7.39 | 52.5% | 1.98 | 156 | 14.3% | 0/4 | FAIL |
| 3 | `supertrend_multi` | +96.82% | 6.61 | 50.6% | 1.88 | 146 | 20.9% | 0/4 | FAIL |
| 4 | `lob_maker` | +80.92% | 4.91 | 48.8% | 1.63 | 124 | 15.7% | 0/4 | FAIL |
| 5 | `momentum_quality` | +73.60% | 6.19 | 51.8% | 1.91 | 116 | 10.8% | 0/4 | FAIL |
| 6 | `volume_breakout` | +67.29% | 5.58 | 54.8% | 2.11 | 73 | 9.7% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | +53.08% | 4.21 | 48.8% | 1.67 | 88 | 13.4% | 0/4 | FAIL |
| 8 | `htf_ema` | +34.29% | 3.15 | 46.7% | 1.61 | 80 | 13.3% | 0/4 | FAIL |
| 9 | `acceleration_band` | +16.18% | 1.71 | 40.8% | 1.25 | 100 | 18.4% | 0/4 | FAIL |
| 10 | `linear_channel_rev` | +12.69% | 2.93 | 51.4% | 1.99 | 30 | 3.4% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `cmf` | +138.29% | 7.26 | 2.23 | 113 | 0/4 | FAIL |
| `price_action_momentum` | +134.47% | 7.39 | 1.98 | 156 | 0/4 | FAIL |
| `supertrend_multi` | +96.82% | 6.61 | 1.88 | 146 | 0/4 | FAIL |
| `lob_maker` | +80.92% | 4.91 | 1.63 | 124 | 0/4 | FAIL |
| `momentum_quality` | +73.60% | 6.19 | 1.91 | 116 | 0/4 | FAIL |
| `volume_breakout` | +67.29% | 5.58 | 2.11 | 73 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +53.08% | 4.21 | 1.67 | 88 | 0/4 | FAIL |
| `htf_ema` | +34.29% | 3.15 | 1.61 | 80 | 0/4 | FAIL |
| `acceleration_band` | +16.18% | 1.71 | 1.25 | 100 | 0/4 | FAIL |
| `linear_channel_rev` | +12.69% | 2.93 | 1.99 | 30 | 0/4 | FAIL |
| `relative_volume` | +10.79% | 1.83 | 1.35 | 54 | 0/4 | FAIL |
| `positional_scaling` | +6.29% | 1.61 | 1.50 | 25 | 0/4 | FAIL |
| `price_cluster` | +5.60% | 2.81 | 751.38 | 3 | 0/4 | FAIL |
| `value_area` | +4.51% | 1.38 | 2.06 | 12 | 0/4 | FAIL |
| `roc_ma_cross` | +1.94% | 0.47 | 1.13 | 42 | 0/4 | FAIL |
| `volatility_cluster` | -0.59% | -0.01 | 1.05 | 81 | 0/4 | FAIL |
| `dema_cross` | -0.65% | -0.26 | 0.99 | 11 | 0/4 | FAIL |
| `wick_reversal` | -0.82% | -1.25 | 0.00 | 1 | 0/4 | FAIL |
| `narrow_range` | -0.92% | -0.37 | 1.05 | 56 | 0/4 | FAIL |
| `elder_impulse` | -2.06% | -0.27 | 1.04 | 64 | 0/4 | FAIL |
| `engulfing_zone` | -2.75% | -0.83 | 0.92 | 21 | 0/4 | FAIL |
| `frama` | -14.62% | -1.61 | 0.85 | 88 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +32.47% -> $13,247
- **Top 5 균등배분**: +104.82% -> $20,482


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-26T10:27:35.133771Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic GBM x8640 (SOL/USDT-like, seed=966931095)_
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
| 평균 수익률 | 27.26% |
| 최고 수익률 | 93.44% (price_action_momentum) |
| 최저 수익률 | -9.05% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +93.44% | 5.90 | 48.9% | 1.73 | 154 | 11.5% | 0/4 | FAIL |
| 2 | `cmf` | +78.34% | 4.89 | 47.9% | 1.64 | 127 | 13.9% | 0/4 | FAIL |
| 3 | `htf_ema` | +75.00% | 6.28 | 57.3% | 2.45 | 68 | 6.9% | 0/4 | FAIL |
| 4 | `volume_breakout` | +63.12% | 5.24 | 52.6% | 1.95 | 76 | 10.2% | 0/4 | FAIL |
| 5 | `momentum_quality` | +62.02% | 5.44 | 49.4% | 1.78 | 113 | 9.0% | 0/4 | FAIL |
| 6 | `supertrend_multi` | +47.67% | 5.04 | 51.1% | 2.09 | 78 | 9.3% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | +42.71% | 3.61 | 46.8% | 1.54 | 86 | 11.6% | 0/4 | FAIL |
| 8 | `lob_maker` | +27.79% | 1.97 | 41.4% | 1.23 | 126 | 21.7% | 0/4 | FAIL |
| 9 | `narrow_range` | +20.72% | 2.95 | 46.8% | 1.62 | 58 | 9.1% | 0/4 | FAIL |
| 10 | `relative_volume` | +19.00% | 2.65 | 45.0% | 1.45 | 68 | 9.1% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +93.44% | 5.90 | 1.73 | 154 | 0/4 | FAIL |
| `cmf` | +78.34% | 4.89 | 1.64 | 127 | 0/4 | FAIL |
| `htf_ema` | +75.00% | 6.28 | 2.45 | 68 | 0/4 | FAIL |
| `volume_breakout` | +63.12% | 5.24 | 1.95 | 76 | 0/4 | FAIL |
| `momentum_quality` | +62.02% | 5.44 | 1.78 | 113 | 0/4 | FAIL |
| `supertrend_multi` | +47.67% | 5.04 | 2.09 | 78 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +42.71% | 3.61 | 1.54 | 86 | 0/4 | FAIL |
| `lob_maker` | +27.79% | 1.97 | 1.23 | 126 | 0/4 | FAIL |
| `narrow_range` | +20.72% | 2.95 | 1.62 | 58 | 0/4 | FAIL |
| `relative_volume` | +19.00% | 2.65 | 1.45 | 68 | 0/4 | FAIL |
| `linear_channel_rev` | +18.96% | 3.94 | 2.24 | 32 | 0/4 | FAIL |
| `volatility_cluster` | +16.35% | 1.92 | 1.37 | 78 | 0/4 | FAIL |
| `acceleration_band` | +15.49% | 1.71 | 1.24 | 101 | 0/4 | FAIL |
| `positional_scaling` | +13.68% | 2.94 | 1.98 | 26 | 0/4 | FAIL |
| `elder_impulse` | +12.56% | 1.76 | 1.32 | 58 | 0/4 | FAIL |
| `value_area` | +6.28% | 2.30 | 2.11 | 12 | 0/4 | FAIL |
| `wick_reversal` | +0.60% | 0.28 | 250.94 | 2 | 0/4 | FAIL |
| `frama` | +0.52% | 0.09 | 1.06 | 84 | 0/4 | FAIL |
| `dema_cross` | -1.42% | -0.79 | 0.86 | 8 | 0/4 | FAIL |
| `price_cluster` | -1.57% | -0.90 | 250.31 | 3 | 0/4 | FAIL |
| `roc_ma_cross` | -2.50% | -0.48 | 0.96 | 38 | 0/4 | FAIL |
| `engulfing_zone` | -9.05% | -2.26 | 0.65 | 23 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +27.26% -> $12,726
- **Top 5 균등배분**: +74.38% -> $17,438
