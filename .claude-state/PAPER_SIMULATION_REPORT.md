# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-04-16T14:33:48.116102Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-04-16T14:12:49.758632Z_
_Symbol: BTC/USDT_
_Data Source: Bybit BTC/USDT 1h (paginated)_
_Data Range: 2025-04-16 15:00:00+00:00 ~ 2026-04-16 14:00:00+00:00 (364일)_
_Walk-Forward: 6개 윈도우 (train=4320h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -7.25% |
| 최고 수익률 | 0.00% (volume_breakout) |
| 최저 수익률 | -17.81% (price_action_momentum) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/6 | FAIL |
| 2 | `price_cluster` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/6 | FAIL |
| 3 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/6 | FAIL |
| 4 | `linear_channel_rev` | -0.89% | -0.70 | 47.8% | 1.16 | 10 | 3.9% | 0/6 | FAIL |
| 5 | `value_area` | -0.96% | -0.70 | 40.9% | 1.07 | 14 | 5.5% | 1/6 | FAIL |
| 6 | `narrow_range` | -2.03% | -0.99 | 39.6% | 1.16 | 12 | 7.0% | 0/6 | FAIL |
| 7 | `roc_ma_cross` | -2.90% | -1.66 | 38.0% | 1.07 | 14 | 5.9% | 0/6 | FAIL |
| 8 | `positional_scaling` | -5.54% | -2.48 | 31.2% | 0.77 | 20 | 10.1% | 0/6 | FAIL |
| 9 | `relative_volume` | -5.75% | -1.98 | 39.3% | 0.94 | 30 | 10.3% | 1/6 | FAIL |
| 10 | `engulfing_zone` | -5.86% | -3.27 | 30.3% | 0.81 | 10 | 8.9% | 0/6 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/6 | FAIL |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/6 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/6 | FAIL |
| `linear_channel_rev` | -0.89% | -0.70 | 1.16 | 10 | 0/6 | FAIL |
| `value_area` | -0.96% | -0.70 | 1.07 | 14 | 1/6 | FAIL |
| `narrow_range` | -2.03% | -0.99 | 1.16 | 12 | 0/6 | FAIL |
| `roc_ma_cross` | -2.90% | -1.66 | 1.07 | 14 | 0/6 | FAIL |
| `positional_scaling` | -5.54% | -2.48 | 0.77 | 20 | 0/6 | FAIL |
| `relative_volume` | -5.75% | -1.98 | 0.94 | 30 | 1/6 | FAIL |
| `engulfing_zone` | -5.86% | -3.27 | 0.81 | 10 | 0/6 | FAIL |
| `acceleration_band` | -6.02% | -2.74 | 0.78 | 22 | 0/6 | FAIL |
| `htf_ema` | -6.81% | -2.29 | 0.83 | 22 | 0/6 | FAIL |
| `elder_impulse` | -6.82% | -2.49 | 0.85 | 26 | 0/6 | FAIL |
| `frama` | -8.47% | -4.82 | 0.49 | 16 | 0/6 | FAIL |
| `volatility_cluster` | -9.81% | -3.96 | 0.70 | 29 | 0/6 | FAIL |
| `wick_reversal` | -10.90% | -3.61 | 0.71 | 26 | 0/6 | FAIL |
| `momentum_quality` | -11.37% | -4.37 | 0.70 | 35 | 0/6 | FAIL |
| `cmf` | -13.14% | -3.69 | 0.76 | 41 | 0/6 | FAIL |
| `supertrend_multi` | -13.40% | -4.01 | 0.74 | 41 | 0/6 | FAIL |
| `order_flow_imbalance_v2` | -13.80% | -3.44 | 0.82 | 49 | 0/6 | FAIL |
| `lob_maker` | -17.35% | -3.59 | 0.80 | 52 | 0/6 | FAIL |
| `price_action_momentum` | -17.81% | -5.34 | 0.65 | 42 | 0/6 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -7.25% -> $9,274
- **Top 5 균등배분**: -0.37% -> $9,963


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-04-16T14:23:41.569804Z_
_Symbol: ETH/USDT_
_Data Source: Bybit ETH/USDT 1h (paginated)_
_Data Range: 2025-04-16 15:00:00+00:00 ~ 2026-04-16 14:00:00+00:00 (364일)_
_Walk-Forward: 6개 윈도우 (train=4320h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -4.61% |
| 최고 수익률 | 0.60% (value_area) |
| 최저 수익률 | -13.55% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `value_area` | +0.60% | -0.00 | 40.9% | 1.29 | 11 | 4.0% | 0/6 | FAIL |
| 2 | `price_cluster` | +0.45% | -0.22 | 33.3% | 91539045899.15 | 1 | 0.5% | 0/6 | FAIL |
| 3 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/6 | FAIL |
| 4 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/6 | FAIL |
| 5 | `linear_channel_rev` | -1.66% | -1.87 | 33.4% | 0.98 | 11 | 5.1% | 1/6 | FAIL |
| 6 | `engulfing_zone` | -1.97% | -1.75 | 33.2% | 1.28 | 8 | 6.1% | 0/6 | FAIL |
| 7 | `supertrend_multi` | -2.02% | -1.01 | 39.1% | 1.08 | 32 | 11.6% | 1/6 | FAIL |
| 8 | `narrow_range` | -2.15% | -1.83 | 35.1% | 0.98 | 10 | 5.6% | 0/6 | FAIL |
| 9 | `elder_impulse` | -2.97% | -1.07 | 37.0% | 0.97 | 26 | 9.1% | 0/6 | FAIL |
| 10 | `acceleration_band` | -3.51% | -1.79 | 33.1% | 0.93 | 18 | 8.5% | 1/6 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `value_area` | +0.60% | -0.00 | 1.29 | 11 | 0/6 | FAIL |
| `price_cluster` | +0.45% | -0.22 | 91539045899.15 | 1 | 0/6 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/6 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/6 | FAIL |
| `linear_channel_rev` | -1.66% | -1.87 | 0.98 | 11 | 1/6 | FAIL |
| `engulfing_zone` | -1.97% | -1.75 | 1.28 | 8 | 0/6 | FAIL |
| `supertrend_multi` | -2.02% | -1.01 | 1.08 | 32 | 1/6 | FAIL |
| `narrow_range` | -2.15% | -1.83 | 0.98 | 10 | 0/6 | FAIL |
| `elder_impulse` | -2.97% | -1.07 | 0.97 | 26 | 0/6 | FAIL |
| `acceleration_band` | -3.51% | -1.79 | 0.93 | 18 | 1/6 | FAIL |
| `positional_scaling` | -3.57% | -1.72 | 0.88 | 20 | 1/6 | FAIL |
| `roc_ma_cross` | -4.50% | -2.44 | 0.86 | 16 | 0/6 | FAIL |
| `frama` | -4.54% | -2.03 | 0.79 | 19 | 0/6 | FAIL |
| `htf_ema` | -4.60% | -2.09 | 0.92 | 22 | 1/6 | FAIL |
| `cmf` | -6.28% | -1.76 | 0.94 | 38 | 0/6 | FAIL |
| `momentum_quality` | -6.67% | -2.33 | 0.92 | 35 | 1/6 | FAIL |
| `relative_volume` | -7.51% | -2.91 | 0.83 | 30 | 0/6 | FAIL |
| `price_action_momentum` | -7.79% | -2.91 | 0.89 | 41 | 1/6 | FAIL |
| `volatility_cluster` | -9.29% | -3.47 | 0.77 | 32 | 0/6 | FAIL |
| `order_flow_imbalance_v2` | -9.78% | -2.79 | 0.86 | 46 | 1/6 | FAIL |
| `wick_reversal` | -10.21% | -3.90 | 0.59 | 20 | 0/6 | FAIL |
| `lob_maker` | -13.55% | -3.43 | 0.84 | 52 | 0/6 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -4.61% -> $9,539
- **Top 5 균등배분**: -0.12% -> $9,988


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-04-16T14:33:48.115080Z_
_Symbol: SOL/USDT_
_Data Source: Bybit SOL/USDT 1h (paginated)_
_Data Range: 2025-04-16 15:00:00+00:00 ~ 2026-04-16 14:00:00+00:00 (364일)_
_Walk-Forward: 6개 윈도우 (train=4320h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -5.92% |
| 최고 수익률 | 0.62% (price_cluster) |
| 최저 수익률 | -14.02% (cmf) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +0.62% | 0.41 | 11.1% | 0.58 | 0 | 0.3% | 0/6 | FAIL |
| 2 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/6 | FAIL |
| 3 | `narrow_range` | -1.05% | -0.92 | 43.7% | 1.17 | 9 | 4.5% | 0/6 | FAIL |
| 4 | `engulfing_zone` | -1.99% | -1.04 | 41.0% | 1.17 | 12 | 8.0% | 0/6 | FAIL |
| 5 | `linear_channel_rev` | -2.40% | -1.71 | 33.4% | 0.86 | 11 | 5.1% | 0/6 | FAIL |
| 6 | `acceleration_band` | -2.77% | -1.53 | 42.0% | 1.07 | 22 | 8.3% | 2/6 | FAIL |
| 7 | `value_area` | -4.05% | -2.45 | 28.4% | 0.71 | 14 | 7.1% | 0/6 | FAIL |
| 8 | `positional_scaling` | -4.54% | -2.00 | 34.6% | 0.84 | 20 | 9.0% | 1/6 | FAIL |
| 9 | `frama` | -4.73% | -1.79 | 35.3% | 0.83 | 20 | 8.9% | 0/6 | FAIL |
| 10 | `supertrend_multi` | -4.75% | -1.74 | 35.3% | 0.87 | 34 | 12.3% | 0/6 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +0.62% | 0.41 | 0.58 | 0 | 0/6 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/6 | FAIL |
| `narrow_range` | -1.05% | -0.92 | 1.17 | 9 | 0/6 | FAIL |
| `engulfing_zone` | -1.99% | -1.04 | 1.17 | 12 | 0/6 | FAIL |
| `linear_channel_rev` | -2.40% | -1.71 | 0.86 | 11 | 0/6 | FAIL |
| `acceleration_band` | -2.77% | -1.53 | 1.07 | 22 | 2/6 | FAIL |
| `value_area` | -4.05% | -2.45 | 0.71 | 14 | 0/6 | FAIL |
| `positional_scaling` | -4.54% | -2.00 | 0.84 | 20 | 1/6 | FAIL |
| `frama` | -4.73% | -1.79 | 0.83 | 20 | 0/6 | FAIL |
| `supertrend_multi` | -4.75% | -1.74 | 0.87 | 34 | 0/6 | FAIL |
| `roc_ma_cross` | -4.84% | -2.52 | 0.77 | 18 | 1/6 | FAIL |
| `wick_reversal` | -5.37% | -2.00 | 0.86 | 20 | 0/6 | FAIL |
| `volatility_cluster` | -6.07% | -2.75 | 0.79 | 28 | 0/6 | FAIL |
| `momentum_quality` | -6.70% | -2.61 | 0.85 | 31 | 0/6 | FAIL |
| `order_flow_imbalance_v2` | -6.83% | -2.23 | 0.93 | 48 | 1/6 | FAIL |
| `relative_volume` | -8.46% | -3.10 | 0.79 | 33 | 0/6 | FAIL |
| `elder_impulse` | -8.61% | -3.25 | 0.71 | 28 | 0/6 | FAIL |
| `price_action_momentum` | -8.95% | -2.79 | 0.86 | 43 | 1/6 | FAIL |
| `volume_breakout` | -9.83% | -2.99 | 0.77 | 37 | 0/6 | FAIL |
| `htf_ema` | -11.15% | -3.89 | 0.63 | 25 | 0/6 | FAIL |
| `lob_maker` | -13.72% | -3.38 | 0.86 | 54 | 1/6 | FAIL |
| `cmf` | -14.02% | -4.27 | 0.66 | 40 | 0/6 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -5.92% -> $9,408
- **Top 5 균등배분**: -0.96% -> $9,904
