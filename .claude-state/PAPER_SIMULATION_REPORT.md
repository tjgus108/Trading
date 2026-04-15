# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-04-15T14:53:25.934076Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-04-15T14:46:53.740421Z_
_Symbol: BTC/USDT_
_Data Source: Bybit BTC/USDT 1h (paginated)_
_Data Range: 2025-10-17 15:00:00+00:00 ~ 2026-04-15 14:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 1개 |
| FAIL | 21개 |
| 평균 수익률 | -4.75% |
| 최고 수익률 | 5.24% (relative_volume) |
| 최저 수익률 | -15.58% (price_action_momentum) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `relative_volume` | +5.24% | 1.90 | 52.6% | 1.51 | 28 | 5.0% | 1/2 | PASS |
| 2 | `engulfing_zone` | +1.70% | 0.90 | 45.0% | 1.47 | 8 | 4.2% | 0/2 | FAIL |
| 3 | `narrow_range` | +0.34% | 0.11 | 47.3% | 1.28 | 10 | 5.1% | 0/2 | FAIL |
| 4 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 5 | `price_cluster` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 6 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 7 | `linear_channel_rev` | -1.18% | -0.70 | 43.2% | 1.03 | 10 | 4.3% | 0/2 | FAIL |
| 8 | `value_area` | -1.82% | -1.07 | 42.0% | 0.90 | 12 | 5.8% | 0/2 | FAIL |
| 9 | `roc_ma_cross` | -3.11% | -2.00 | 36.7% | 0.74 | 14 | 5.7% | 0/2 | FAIL |
| 10 | `acceleration_band` | -3.48% | -1.36 | 41.7% | 0.93 | 24 | 9.5% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `relative_volume` | +5.24% | 1.90 | 1.51 | 28 | 1/2 | PASS |
| `engulfing_zone` | +1.70% | 0.90 | 1.47 | 8 | 0/2 | FAIL |
| `narrow_range` | +0.34% | 0.11 | 1.28 | 10 | 0/2 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `linear_channel_rev` | -1.18% | -0.70 | 1.03 | 10 | 0/2 | FAIL |
| `value_area` | -1.82% | -1.07 | 0.90 | 12 | 0/2 | FAIL |
| `roc_ma_cross` | -3.11% | -2.00 | 0.74 | 14 | 0/2 | FAIL |
| `acceleration_band` | -3.48% | -1.36 | 0.93 | 24 | 0/2 | FAIL |
| `momentum_quality` | -4.46% | -1.36 | 0.97 | 35 | 0/2 | FAIL |
| `positional_scaling` | -5.12% | -2.31 | 0.76 | 19 | 0/2 | FAIL |
| `wick_reversal` | -5.86% | -1.65 | 0.93 | 26 | 0/2 | FAIL |
| `volatility_cluster` | -7.55% | -2.96 | 0.79 | 28 | 0/2 | FAIL |
| `supertrend_multi` | -7.56% | -2.35 | 0.81 | 28 | 0/2 | FAIL |
| `elder_impulse` | -7.89% | -2.75 | 0.78 | 28 | 0/2 | FAIL |
| `cmf` | -7.94% | -2.08 | 0.90 | 41 | 0/2 | FAIL |
| `htf_ema` | -8.05% | -3.35 | 0.79 | 20 | 0/2 | FAIL |
| `order_flow_imbalance_v2` | -9.25% | -2.21 | 0.90 | 48 | 0/2 | FAIL |
| `frama` | -9.94% | -5.90 | 0.32 | 14 | 0/2 | FAIL |
| `lob_maker` | -13.07% | -2.47 | 0.86 | 52 | 0/2 | FAIL |
| `price_action_momentum` | -15.58% | -4.02 | 0.72 | 46 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -4.75% -> $9,525
- **PASS 1개 균등배분**: +5.24% -> $10,524
- **Top 5 균등배분**: +1.46% -> $10,146


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-04-15T14:49:57.749185Z_
_Symbol: ETH/USDT_
_Data Source: Bybit ETH/USDT 1h (paginated)_
_Data Range: 2025-10-17 15:00:00+00:00 ~ 2026-04-15 14:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 2개 |
| FAIL | 20개 |
| 평균 수익률 | -1.32% |
| 최고 수익률 | 9.25% (engulfing_zone) |
| 최저 수익률 | -9.04% (htf_ema) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `engulfing_zone` | +9.25% | 4.06 | 69.0% | 4.16 | 8 | 1.9% | 0/2 | FAIL |
| 2 | `acceleration_band` | +7.40% | 2.85 | 53.6% | 1.85 | 20 | 6.1% | 2/2 | PASS |
| 3 | `lob_maker` | +6.55% | 1.13 | 45.4% | 1.27 | 56 | 14.6% | 1/2 | PASS |
| 4 | `price_cluster` | +0.91% | -0.51 | 50.0% | 129733005340.47 | 1 | 0.4% | 0/2 | FAIL |
| 5 | `narrow_range` | +0.58% | -0.32 | 41.1% | 1.73 | 8 | 4.5% | 0/2 | FAIL |
| 6 | `momentum_quality` | +0.34% | 0.25 | 44.6% | 1.14 | 34 | 7.7% | 0/2 | FAIL |
| 7 | `relative_volume` | +0.27% | 0.14 | 44.2% | 1.19 | 30 | 7.0% | 0/2 | FAIL |
| 8 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 9 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 10 | `order_flow_imbalance_v2` | -0.88% | -0.05 | 42.7% | 1.09 | 44 | 10.9% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `engulfing_zone` | +9.25% | 4.06 | 4.16 | 8 | 0/2 | FAIL |
| `acceleration_band` | +7.40% | 2.85 | 1.85 | 20 | 2/2 | PASS |
| `lob_maker` | +6.55% | 1.13 | 1.27 | 56 | 1/2 | PASS |
| `price_cluster` | +0.91% | -0.51 | 129733005340.47 | 1 | 0/2 | FAIL |
| `narrow_range` | +0.58% | -0.32 | 1.73 | 8 | 0/2 | FAIL |
| `momentum_quality` | +0.34% | 0.25 | 1.14 | 34 | 0/2 | FAIL |
| `relative_volume` | +0.27% | 0.14 | 1.19 | 30 | 0/2 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `order_flow_imbalance_v2` | -0.88% | -0.05 | 1.09 | 44 | 0/2 | FAIL |
| `supertrend_multi` | -1.05% | -0.14 | 1.07 | 32 | 0/2 | FAIL |
| `roc_ma_cross` | -1.80% | -0.90 | 0.96 | 16 | 0/2 | FAIL |
| `elder_impulse` | -2.33% | -1.09 | 0.98 | 26 | 0/2 | FAIL |
| `value_area` | -2.38% | -1.45 | 0.85 | 12 | 0/2 | FAIL |
| `price_action_momentum` | -2.56% | -0.52 | 1.04 | 44 | 0/2 | FAIL |
| `wick_reversal` | -2.91% | -0.97 | 0.94 | 18 | 0/2 | FAIL |
| `linear_channel_rev` | -3.21% | -2.59 | 0.67 | 10 | 0/2 | FAIL |
| `frama` | -6.11% | -2.58 | 0.74 | 22 | 0/2 | FAIL |
| `positional_scaling` | -6.73% | -2.96 | 0.68 | 21 | 0/2 | FAIL |
| `cmf` | -7.27% | -2.05 | 0.89 | 38 | 0/2 | FAIL |
| `volatility_cluster` | -8.08% | -2.68 | 0.79 | 34 | 0/2 | FAIL |
| `htf_ema` | -9.04% | -3.85 | 0.64 | 18 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -1.32% -> $9,868
- **PASS 2개 균등배분**: +6.98% -> $10,698
- **Top 5 균등배분**: +4.94% -> $10,494


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-04-15T14:53:25.933233Z_
_Symbol: SOL/USDT_
_Data Source: Bybit SOL/USDT 1h (paginated)_
_Data Range: 2025-10-17 15:00:00+00:00 ~ 2026-04-15 14:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 5개 |
| FAIL | 17개 |
| 평균 수익률 | -2.25% |
| 최고 수익률 | 17.99% (lob_maker) |
| 최저 수익률 | -15.42% (volume_breakout) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `lob_maker` | +17.99% | 2.81 | 50.3% | 1.51 | 52 | 10.5% | 1/2 | PASS |
| 2 | `order_flow_imbalance_v2` | +10.24% | 2.19 | 50.3% | 1.42 | 46 | 11.9% | 1/2 | PASS |
| 3 | `momentum_quality` | +5.79% | 1.76 | 48.9% | 1.49 | 30 | 7.3% | 1/2 | PASS |
| 4 | `engulfing_zone` | +5.56% | 2.39 | 56.8% | 2.03 | 10 | 3.0% | 0/2 | FAIL |
| 5 | `price_cluster` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 6 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 7 | `narrow_range` | -0.48% | -0.26 | 43.6% | 1.04 | 8 | 3.9% | 0/2 | FAIL |
| 8 | `acceleration_band` | -1.20% | -0.46 | 41.5% | 1.12 | 24 | 9.9% | 1/2 | PASS |
| 9 | `relative_volume` | -1.34% | -0.46 | 44.6% | 1.08 | 27 | 6.7% | 0/2 | FAIL |
| 10 | `frama` | -2.42% | -0.93 | 36.1% | 0.92 | 18 | 5.8% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `lob_maker` | +17.99% | 2.81 | 1.51 | 52 | 1/2 | PASS |
| `order_flow_imbalance_v2` | +10.24% | 2.19 | 1.42 | 46 | 1/2 | PASS |
| `momentum_quality` | +5.79% | 1.76 | 1.49 | 30 | 1/2 | PASS |
| `engulfing_zone` | +5.56% | 2.39 | 2.03 | 10 | 0/2 | FAIL |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `narrow_range` | -0.48% | -0.26 | 1.04 | 8 | 0/2 | FAIL |
| `acceleration_band` | -1.20% | -0.46 | 1.12 | 24 | 1/2 | PASS |
| `relative_volume` | -1.34% | -0.46 | 1.08 | 27 | 0/2 | FAIL |
| `frama` | -2.42% | -0.93 | 0.92 | 18 | 0/2 | FAIL |
| `volatility_cluster` | -2.87% | -1.42 | 0.99 | 29 | 0/2 | FAIL |
| `htf_ema` | -3.39% | -1.18 | 1.08 | 20 | 1/2 | PASS |
| `elder_impulse` | -3.89% | -1.24 | 0.97 | 28 | 0/2 | FAIL |
| `linear_channel_rev` | -4.23% | -3.21 | 0.71 | 12 | 0/2 | FAIL |
| `value_area` | -4.44% | -2.80 | 0.59 | 11 | 0/2 | FAIL |
| `wick_reversal` | -6.02% | -2.28 | 0.78 | 20 | 0/2 | FAIL |
| `roc_ma_cross` | -6.19% | -3.34 | 0.56 | 15 | 0/2 | FAIL |
| `supertrend_multi` | -7.58% | -2.17 | 0.83 | 34 | 0/2 | FAIL |
| `price_action_momentum` | -7.82% | -2.29 | 0.87 | 42 | 0/2 | FAIL |
| `positional_scaling` | -8.17% | -3.43 | 0.59 | 20 | 0/2 | FAIL |
| `cmf` | -13.71% | -3.63 | 0.73 | 44 | 0/2 | FAIL |
| `volume_breakout` | -15.42% | -4.79 | 0.64 | 38 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -2.25% -> $9,775
- **PASS 5개 균등배분**: +5.89% -> $10,589
- **Top 5 균등배분**: +7.92% -> $10,792
