# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-25T20:44:55.240547Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-25T20:37:18.314942Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic GBM x8640 (BTC/USDT-like, seed=1123782437)_
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
| 평균 수익률 | 23.01% |
| 최고 수익률 | 122.70% (cmf) |
| 최저 수익률 | -5.70% (narrow_range) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `cmf` | +122.70% | 6.52 | 52.4% | 1.89 | 127 | 11.6% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +112.61% | 6.53 | 49.6% | 1.83 | 159 | 9.8% | 0/4 | FAIL |
| 3 | `supertrend_multi` | +80.31% | 5.78 | 50.2% | 1.83 | 116 | 13.2% | 0/4 | FAIL |
| 4 | `momentum_quality` | +39.30% | 3.85 | 44.7% | 1.54 | 112 | 11.5% | 0/4 | FAIL |
| 5 | `htf_ema` | +32.30% | 3.09 | 45.0% | 1.54 | 76 | 10.4% | 0/4 | FAIL |
| 6 | `roc_ma_cross` | +18.99% | 3.54 | 51.1% | 2.03 | 41 | 5.8% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | +17.36% | 1.78 | 41.6% | 1.26 | 85 | 13.1% | 0/4 | FAIL |
| 8 | `elder_impulse` | +17.15% | 2.38 | 43.7% | 1.46 | 54 | 11.2% | 0/4 | FAIL |
| 9 | `lob_maker` | +16.65% | 1.47 | 40.1% | 1.18 | 127 | 17.9% | 0/4 | FAIL |
| 10 | `acceleration_band` | +14.58% | 1.56 | 41.3% | 1.25 | 96 | 12.5% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `cmf` | +122.70% | 6.52 | 1.89 | 127 | 0/4 | FAIL |
| `price_action_momentum` | +112.61% | 6.53 | 1.83 | 159 | 0/4 | FAIL |
| `supertrend_multi` | +80.31% | 5.78 | 1.83 | 116 | 0/4 | FAIL |
| `momentum_quality` | +39.30% | 3.85 | 1.54 | 112 | 0/4 | FAIL |
| `htf_ema` | +32.30% | 3.09 | 1.54 | 76 | 0/4 | FAIL |
| `roc_ma_cross` | +18.99% | 3.54 | 2.03 | 41 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +17.36% | 1.78 | 1.26 | 85 | 0/4 | FAIL |
| `elder_impulse` | +17.15% | 2.38 | 1.46 | 54 | 0/4 | FAIL |
| `lob_maker` | +16.65% | 1.47 | 1.18 | 127 | 0/4 | FAIL |
| `acceleration_band` | +14.58% | 1.56 | 1.25 | 96 | 0/4 | FAIL |
| `linear_channel_rev` | +11.39% | 2.33 | 1.55 | 39 | 0/4 | FAIL |
| `volatility_cluster` | +8.94% | 1.39 | 1.22 | 80 | 0/4 | FAIL |
| `value_area` | +8.30% | 2.53 | 2.19 | 14 | 0/4 | FAIL |
| `engulfing_zone` | +6.76% | 1.34 | 1.42 | 22 | 0/4 | FAIL |
| `relative_volume` | +3.73% | 0.61 | 1.14 | 58 | 0/4 | FAIL |
| `frama` | +2.44% | 0.32 | 1.08 | 90 | 0/4 | FAIL |
| `dema_cross` | +0.62% | 0.02 | 1.04 | 10 | 0/4 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `wick_reversal` | -0.09% | -0.73 | 1.15 | 2 | 0/4 | FAIL |
| `positional_scaling` | -2.17% | -0.58 | 0.93 | 26 | 0/4 | FAIL |
| `narrow_range` | -5.70% | -1.06 | 0.92 | 58 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +23.01% -> $12,301
- **Top 5 균등배분**: +77.44% -> $17,744


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-25T20:41:13.403573Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic GBM x8640 (ETH/USDT-like, seed=976119935)_
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
| 평균 수익률 | 27.86% |
| 최고 수익률 | 148.00% (cmf) |
| 최저 수익률 | -12.20% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `cmf` | +148.00% | 6.68 | 51.6% | 1.95 | 126 | 15.6% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +132.77% | 6.94 | 50.5% | 1.84 | 172 | 15.8% | 0/4 | FAIL |
| 3 | `momentum_quality` | +67.01% | 5.59 | 49.1% | 1.81 | 118 | 9.4% | 0/4 | FAIL |
| 4 | `htf_ema` | +45.08% | 4.48 | 49.7% | 1.97 | 68 | 12.6% | 0/4 | FAIL |
| 5 | `lob_maker` | +43.99% | 2.91 | 42.7% | 1.34 | 126 | 11.5% | 0/4 | FAIL |
| 6 | `volatility_cluster` | +40.61% | 4.67 | 49.1% | 1.81 | 88 | 11.3% | 0/4 | FAIL |
| 7 | `supertrend_multi` | +37.80% | 3.84 | 44.9% | 1.51 | 112 | 11.9% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | +28.59% | 2.57 | 42.7% | 1.35 | 92 | 13.6% | 0/4 | FAIL |
| 9 | `linear_channel_rev` | +20.60% | 4.14 | 56.1% | 2.52 | 32 | 4.2% | 0/4 | FAIL |
| 10 | `relative_volume` | +13.12% | 1.84 | 44.2% | 1.49 | 54 | 8.8% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `cmf` | +148.00% | 6.68 | 1.95 | 126 | 0/4 | FAIL |
| `price_action_momentum` | +132.77% | 6.94 | 1.84 | 172 | 0/4 | FAIL |
| `momentum_quality` | +67.01% | 5.59 | 1.81 | 118 | 0/4 | FAIL |
| `htf_ema` | +45.08% | 4.48 | 1.97 | 68 | 0/4 | FAIL |
| `lob_maker` | +43.99% | 2.91 | 1.34 | 126 | 0/4 | FAIL |
| `volatility_cluster` | +40.61% | 4.67 | 1.81 | 88 | 0/4 | FAIL |
| `supertrend_multi` | +37.80% | 3.84 | 1.51 | 112 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +28.59% | 2.57 | 1.35 | 92 | 0/4 | FAIL |
| `linear_channel_rev` | +20.60% | 4.14 | 2.52 | 32 | 0/4 | FAIL |
| `relative_volume` | +13.12% | 1.84 | 1.49 | 54 | 0/4 | FAIL |
| `narrow_range` | +12.54% | 1.95 | 1.36 | 57 | 0/4 | FAIL |
| `positional_scaling` | +11.29% | 2.49 | 2.53 | 24 | 0/4 | FAIL |
| `value_area` | +7.14% | 2.37 | 2.56 | 11 | 0/4 | FAIL |
| `roc_ma_cross` | +6.79% | 1.47 | 1.46 | 37 | 0/4 | FAIL |
| `elder_impulse` | +5.79% | 0.98 | 1.19 | 51 | 0/4 | FAIL |
| `dema_cross` | +3.95% | 1.19 | 1.59 | 17 | 0/4 | FAIL |
| `price_cluster` | +1.20% | 0.80 | 250.70 | 1 | 0/4 | FAIL |
| `wick_reversal` | +1.00% | 0.47 | 500.00 | 1 | 0/4 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `acceleration_band` | -0.17% | -0.10 | 1.03 | 92 | 0/4 | FAIL |
| `engulfing_zone` | -2.07% | -1.18 | 1.05 | 22 | 0/4 | FAIL |
| `frama` | -12.20% | -1.36 | 0.88 | 88 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +27.86% -> $12,786
- **Top 5 균등배분**: +87.37% -> $18,737


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-25T20:44:55.237938Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic GBM x8640 (SOL/USDT-like, seed=1369127254)_
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
| 평균 수익률 | 18.77% |
| 최고 수익률 | 124.05% (price_action_momentum) |
| 최저 수익률 | -12.39% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +124.05% | 6.89 | 51.1% | 1.83 | 166 | 15.2% | 0/4 | FAIL |
| 2 | `cmf` | +91.40% | 5.31 | 50.1% | 1.70 | 126 | 14.6% | 0/4 | FAIL |
| 3 | `htf_ema` | +62.03% | 5.39 | 53.2% | 2.24 | 72 | 8.9% | 0/4 | FAIL |
| 4 | `momentum_quality` | +51.70% | 4.68 | 47.1% | 1.62 | 120 | 13.4% | 0/4 | FAIL |
| 5 | `supertrend_multi` | +40.96% | 3.54 | 45.4% | 1.44 | 130 | 11.8% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | +16.21% | 1.48 | 41.5% | 1.25 | 79 | 15.0% | 0/4 | FAIL |
| 7 | `linear_channel_rev` | +11.23% | 2.69 | 50.1% | 1.84 | 29 | 4.1% | 0/4 | FAIL |
| 8 | `positional_scaling` | +9.81% | 2.18 | 48.8% | 1.60 | 32 | 5.9% | 0/4 | FAIL |
| 9 | `volatility_cluster` | +9.30% | 1.42 | 41.1% | 1.22 | 84 | 12.2% | 0/4 | FAIL |
| 10 | `acceleration_band` | +8.82% | 0.68 | 38.0% | 1.19 | 92 | 16.9% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +124.05% | 6.89 | 1.83 | 166 | 0/4 | FAIL |
| `cmf` | +91.40% | 5.31 | 1.70 | 126 | 0/4 | FAIL |
| `htf_ema` | +62.03% | 5.39 | 2.24 | 72 | 0/4 | FAIL |
| `momentum_quality` | +51.70% | 4.68 | 1.62 | 120 | 0/4 | FAIL |
| `supertrend_multi` | +40.96% | 3.54 | 1.44 | 130 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +16.21% | 1.48 | 1.25 | 79 | 0/4 | FAIL |
| `linear_channel_rev` | +11.23% | 2.69 | 1.84 | 29 | 0/4 | FAIL |
| `positional_scaling` | +9.81% | 2.18 | 1.60 | 32 | 0/4 | FAIL |
| `volatility_cluster` | +9.30% | 1.42 | 1.22 | 84 | 0/4 | FAIL |
| `acceleration_band` | +8.82% | 0.68 | 1.19 | 92 | 0/4 | FAIL |
| `roc_ma_cross` | +6.29% | 1.33 | 1.36 | 37 | 0/4 | FAIL |
| `elder_impulse` | +4.68% | 0.66 | 1.37 | 54 | 0/4 | FAIL |
| `lob_maker` | +2.36% | 0.35 | 1.06 | 118 | 0/4 | FAIL |
| `wick_reversal` | +0.38% | -0.04 | 500.00 | 1 | 0/4 | FAIL |
| `value_area` | +0.21% | 0.16 | 1.13 | 10 | 0/4 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `price_cluster` | -0.40% | -0.51 | 0.00 | 0 | 0/4 | FAIL |
| `relative_volume` | -0.93% | -0.11 | 1.03 | 58 | 0/4 | FAIL |
| `dema_cross` | -1.98% | -0.99 | 0.73 | 9 | 0/4 | FAIL |
| `narrow_range` | -3.62% | -0.56 | 0.97 | 53 | 0/4 | FAIL |
| `frama` | -7.20% | -0.92 | 0.95 | 87 | 0/4 | FAIL |
| `engulfing_zone` | -12.39% | -3.51 | 0.45 | 19 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +18.77% -> $11,877
- **Top 5 균등배분**: +74.03% -> $17,403
