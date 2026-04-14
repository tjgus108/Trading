# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-04-14T23:12:46.642892Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-04-14T23:05:51.268611Z_
_Symbol: BTC/USDT_
_Data Source: Bybit BTC/USDT 1h (paginated)_
_Data Range: 2025-10-17 00:00:00+00:00 ~ 2026-04-14 23:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 1개 |
| FAIL | 21개 |
| 평균 수익률 | -5.25% |
| 최고 수익률 | 5.24% (relative_volume) |
| 최저 수익률 | -15.34% (price_action_momentum) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `relative_volume` | +5.24% | 1.90 | 52.6% | 1.51 | 28 | 5.0% | 1/2 | PASS |
| 2 | `engulfing_zone` | +1.70% | 0.90 | 45.0% | 1.47 | 8 | 4.2% | 0/2 | FAIL |
| 3 | `narrow_range` | +0.34% | 0.11 | 47.3% | 1.28 | 10 | 5.1% | 0/2 | FAIL |
| 4 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 5 | `price_cluster` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 6 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 7 | `linear_channel_rev` | -1.13% | -0.68 | 43.2% | 1.03 | 10 | 4.3% | 0/2 | FAIL |
| 8 | `roc_ma_cross` | -2.21% | -1.54 | 38.4% | 0.83 | 14 | 5.7% | 0/2 | FAIL |
| 9 | `value_area` | -2.67% | -1.51 | 40.6% | 0.83 | 12 | 5.8% | 0/2 | FAIL |
| 10 | `positional_scaling` | -4.19% | -1.86 | 30.9% | 0.83 | 20 | 8.5% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `relative_volume` | +5.24% | 1.90 | 1.51 | 28 | 1/2 | PASS |
| `engulfing_zone` | +1.70% | 0.90 | 1.47 | 8 | 0/2 | FAIL |
| `narrow_range` | +0.34% | 0.11 | 1.28 | 10 | 0/2 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `linear_channel_rev` | -1.13% | -0.68 | 1.03 | 10 | 0/2 | FAIL |
| `roc_ma_cross` | -2.21% | -1.54 | 0.83 | 14 | 0/2 | FAIL |
| `value_area` | -2.67% | -1.51 | 0.83 | 12 | 0/2 | FAIL |
| `positional_scaling` | -4.19% | -1.86 | 0.83 | 20 | 0/2 | FAIL |
| `acceleration_band` | -4.29% | -1.74 | 0.88 | 24 | 0/2 | FAIL |
| `momentum_quality` | -5.62% | -1.78 | 0.91 | 34 | 0/2 | FAIL |
| `elder_impulse` | -6.58% | -2.28 | 0.86 | 28 | 0/2 | FAIL |
| `wick_reversal` | -7.49% | -2.25 | 0.86 | 26 | 0/2 | FAIL |
| `cmf` | -8.24% | -2.23 | 0.88 | 40 | 0/2 | FAIL |
| `supertrend_multi` | -8.96% | -2.98 | 0.76 | 28 | 0/2 | FAIL |
| `frama` | -9.40% | -5.64 | 0.34 | 14 | 0/2 | FAIL |
| `volatility_cluster` | -9.64% | -3.87 | 0.67 | 28 | 0/2 | FAIL |
| `order_flow_imbalance_v2` | -10.32% | -2.52 | 0.88 | 48 | 0/2 | FAIL |
| `htf_ema` | -12.67% | -5.24 | 0.48 | 20 | 0/2 | FAIL |
| `lob_maker` | -13.96% | -2.70 | 0.84 | 52 | 0/2 | FAIL |
| `price_action_momentum` | -15.34% | -4.01 | 0.72 | 46 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -5.25% -> $9,475
- **PASS 1개 균등배분**: +5.24% -> $10,524
- **Top 5 균등배분**: +1.46% -> $10,146


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-04-14T23:09:04.990678Z_
_Symbol: ETH/USDT_
_Data Source: Bybit ETH/USDT 1h (paginated)_
_Data Range: 2025-10-17 00:00:00+00:00 ~ 2026-04-14 23:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 1개 |
| FAIL | 21개 |
| 평균 수익률 | -2.03% |
| 최고 수익률 | 9.45% (engulfing_zone) |
| 최저 수익률 | -9.55% (htf_ema) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `engulfing_zone` | +9.45% | 4.12 | 69.0% | 4.21 | 8 | 1.9% | 0/2 | FAIL |
| 2 | `acceleration_band` | +6.33% | 2.52 | 51.2% | 1.75 | 20 | 6.1% | 2/2 | PASS |
| 3 | `lob_maker` | +4.55% | 0.86 | 44.5% | 1.22 | 55 | 14.6% | 0/2 | FAIL |
| 4 | `price_cluster` | +0.91% | -0.51 | 50.0% | 129733005340.47 | 1 | 0.4% | 0/2 | FAIL |
| 5 | `relative_volume` | +0.39% | 0.19 | 44.2% | 1.20 | 30 | 7.0% | 0/2 | FAIL |
| 6 | `narrow_range` | +0.01% | -0.66 | 39.7% | 1.71 | 8 | 5.0% | 0/2 | FAIL |
| 7 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 8 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 9 | `momentum_quality` | -0.56% | -0.07 | 43.7% | 1.09 | 33 | 7.7% | 0/2 | FAIL |
| 10 | `roc_ma_cross` | -1.84% | -0.92 | 38.8% | 0.95 | 16 | 6.0% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `engulfing_zone` | +9.45% | 4.12 | 4.21 | 8 | 0/2 | FAIL |
| `acceleration_band` | +6.33% | 2.52 | 1.75 | 20 | 2/2 | PASS |
| `lob_maker` | +4.55% | 0.86 | 1.22 | 55 | 0/2 | FAIL |
| `price_cluster` | +0.91% | -0.51 | 129733005340.47 | 1 | 0/2 | FAIL |
| `relative_volume` | +0.39% | 0.19 | 1.20 | 30 | 0/2 | FAIL |
| `narrow_range` | +0.01% | -0.66 | 1.71 | 8 | 0/2 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `momentum_quality` | -0.56% | -0.07 | 1.09 | 33 | 0/2 | FAIL |
| `roc_ma_cross` | -1.84% | -0.92 | 0.95 | 16 | 0/2 | FAIL |
| `order_flow_imbalance_v2` | -1.88% | -0.29 | 1.06 | 44 | 0/2 | FAIL |
| `elder_impulse` | -2.89% | -1.22 | 0.94 | 26 | 0/2 | FAIL |
| `value_area` | -2.93% | -1.76 | 0.81 | 13 | 0/2 | FAIL |
| `supertrend_multi` | -3.25% | -0.72 | 0.99 | 32 | 0/2 | FAIL |
| `linear_channel_rev` | -3.33% | -2.67 | 0.65 | 10 | 0/2 | FAIL |
| `wick_reversal` | -3.45% | -1.17 | 0.92 | 18 | 0/2 | FAIL |
| `frama` | -5.39% | -2.29 | 0.76 | 21 | 0/2 | FAIL |
| `price_action_momentum` | -6.13% | -1.51 | 0.93 | 44 | 0/2 | FAIL |
| `positional_scaling` | -6.19% | -2.75 | 0.69 | 20 | 0/2 | FAIL |
| `cmf` | -9.41% | -2.80 | 0.83 | 38 | 0/2 | FAIL |
| `volatility_cluster` | -9.47% | -3.20 | 0.73 | 34 | 0/2 | FAIL |
| `htf_ema` | -9.55% | -3.64 | 0.64 | 20 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -2.03% -> $9,797
- **PASS 1개 균등배분**: +6.33% -> $10,633
- **Top 5 균등배분**: +4.33% -> $10,433


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-04-14T23:12:46.642177Z_
_Symbol: SOL/USDT_
_Data Source: Bybit SOL/USDT 1h (paginated)_
_Data Range: 2025-10-17 00:00:00+00:00 ~ 2026-04-14 23:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 4개 |
| FAIL | 18개 |
| 평균 수익률 | -2.81% |
| 최고 수익률 | 13.55% (lob_maker) |
| 최저 수익률 | -14.84% (cmf) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `lob_maker` | +13.55% | 2.33 | 49.5% | 1.43 | 52 | 10.5% | 1/2 | PASS |
| 2 | `order_flow_imbalance_v2` | +8.92% | 2.00 | 49.9% | 1.38 | 45 | 11.9% | 1/2 | PASS |
| 3 | `engulfing_zone` | +6.03% | 2.55 | 58.3% | 2.10 | 10 | 3.0% | 0/2 | FAIL |
| 4 | `momentum_quality` | +4.13% | 1.30 | 47.2% | 1.36 | 30 | 7.3% | 1/2 | PASS |
| 5 | `price_cluster` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 6 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 7 | `acceleration_band` | -0.96% | -0.37 | 43.9% | 1.17 | 24 | 9.9% | 1/2 | PASS |
| 8 | `relative_volume` | -1.18% | -0.39 | 44.6% | 1.07 | 27 | 6.3% | 0/2 | FAIL |
| 9 | `narrow_range` | -1.54% | -0.99 | 40.0% | 1.01 | 9 | 5.0% | 0/2 | FAIL |
| 10 | `frama` | -1.85% | -0.70 | 37.1% | 0.95 | 18 | 5.2% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `lob_maker` | +13.55% | 2.33 | 1.43 | 52 | 1/2 | PASS |
| `order_flow_imbalance_v2` | +8.92% | 2.00 | 1.38 | 45 | 1/2 | PASS |
| `engulfing_zone` | +6.03% | 2.55 | 2.10 | 10 | 0/2 | FAIL |
| `momentum_quality` | +4.13% | 1.30 | 1.36 | 30 | 1/2 | PASS |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `acceleration_band` | -0.96% | -0.37 | 1.17 | 24 | 1/2 | PASS |
| `relative_volume` | -1.18% | -0.39 | 1.07 | 27 | 0/2 | FAIL |
| `narrow_range` | -1.54% | -0.99 | 1.01 | 9 | 0/2 | FAIL |
| `frama` | -1.85% | -0.70 | 0.95 | 18 | 0/2 | FAIL |
| `value_area` | -3.53% | -2.11 | 0.71 | 12 | 0/2 | FAIL |
| `elder_impulse` | -3.89% | -1.24 | 0.97 | 28 | 0/2 | FAIL |
| `linear_channel_rev` | -3.94% | -3.04 | 0.77 | 12 | 0/2 | FAIL |
| `volatility_cluster` | -4.43% | -2.13 | 0.90 | 30 | 0/2 | FAIL |
| `roc_ma_cross` | -5.86% | -3.16 | 0.58 | 15 | 0/2 | FAIL |
| `htf_ema` | -6.63% | -2.31 | 0.85 | 19 | 0/2 | FAIL |
| `positional_scaling` | -6.94% | -2.96 | 0.64 | 18 | 0/2 | FAIL |
| `wick_reversal` | -7.13% | -2.63 | 0.73 | 20 | 0/2 | FAIL |
| `supertrend_multi` | -7.97% | -2.29 | 0.81 | 32 | 0/2 | FAIL |
| `price_action_momentum` | -8.95% | -2.58 | 0.83 | 42 | 0/2 | FAIL |
| `volume_breakout` | -14.79% | -4.63 | 0.66 | 38 | 0/2 | FAIL |
| `cmf` | -14.84% | -3.96 | 0.70 | 44 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -2.81% -> $9,719
- **PASS 4개 균등배분**: +6.41% -> $10,641
- **Top 5 균등배분**: +6.53% -> $10,653
