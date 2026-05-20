# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-20T14:50:53.580695Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-20T14:35:15.719718Z_
_Symbol: BTC/USDT_
_Data Source: Bybit BTC/USDT 1h (paginated)_
_Data Range: 2025-11-21 15:00:00+00:00 ~ 2026-05-20 14:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -8.40% |
| 최고 수익률 | 0.00% (volume_breakout) |
| 최저 수익률 | -25.81% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 2 | `price_cluster` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 3 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 4 | `engulfing_zone` | -0.96% | -0.72 | 41.7% | 1.24 | 8 | 5.6% | 0/2 | FAIL |
| 5 | `relative_volume` | -1.90% | -0.54 | 41.1% | 1.03 | 33 | 5.8% | 0/2 | FAIL |
| 6 | `narrow_range` | -2.13% | -1.54 | 35.4% | 0.72 | 7 | 5.1% | 0/2 | FAIL |
| 7 | `value_area` | -3.13% | -1.54 | 39.7% | 0.86 | 16 | 7.1% | 0/2 | FAIL |
| 8 | `positional_scaling` | -3.24% | -1.45 | 34.4% | 0.89 | 19 | 7.2% | 0/2 | FAIL |
| 9 | `linear_channel_rev` | -3.39% | -2.19 | 36.4% | 0.66 | 11 | 4.7% | 0/2 | FAIL |
| 10 | `acceleration_band` | -5.12% | -2.43 | 40.2% | 0.77 | 22 | 7.2% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `engulfing_zone` | -0.96% | -0.72 | 1.24 | 8 | 0/2 | FAIL |
| `relative_volume` | -1.90% | -0.54 | 1.03 | 33 | 0/2 | FAIL |
| `narrow_range` | -2.13% | -1.54 | 0.72 | 7 | 0/2 | FAIL |
| `value_area` | -3.13% | -1.54 | 0.86 | 16 | 0/2 | FAIL |
| `positional_scaling` | -3.24% | -1.45 | 0.89 | 19 | 0/2 | FAIL |
| `linear_channel_rev` | -3.39% | -2.19 | 0.66 | 11 | 0/2 | FAIL |
| `acceleration_band` | -5.12% | -2.43 | 0.77 | 22 | 0/2 | FAIL |
| `frama` | -6.00% | -3.77 | 0.48 | 12 | 0/2 | FAIL |
| `volatility_cluster` | -6.63% | -2.22 | 0.84 | 36 | 0/2 | FAIL |
| `roc_ma_cross` | -7.47% | -3.81 | 0.55 | 19 | 0/2 | FAIL |
| `momentum_quality` | -8.96% | -3.38 | 0.72 | 34 | 0/2 | FAIL |
| `supertrend_multi` | -9.40% | -2.79 | 0.75 | 32 | 0/2 | FAIL |
| `price_action_momentum` | -13.41% | -4.38 | 0.64 | 36 | 0/2 | FAIL |
| `cmf` | -14.87% | -4.50 | 0.63 | 39 | 0/2 | FAIL |
| `htf_ema` | -15.31% | -5.96 | 0.40 | 22 | 0/2 | FAIL |
| `elder_impulse` | -16.04% | -6.14 | 0.42 | 26 | 0/2 | FAIL |
| `order_flow_imbalance_v2` | -18.66% | -5.56 | 0.58 | 45 | 0/2 | FAIL |
| `wick_reversal` | -22.37% | -7.84 | 0.36 | 30 | 0/2 | FAIL |
| `lob_maker` | -25.81% | -5.89 | 0.60 | 54 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -8.40% -> $9,160
- **Top 5 균등배분**: -0.57% -> $9,943


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-20T14:40:19.314006Z_
_Symbol: ETH/USDT_
_Data Source: Bybit ETH/USDT 1h (paginated)_
_Data Range: 2025-11-21 15:00:00+00:00 ~ 2026-05-20 14:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -4.23% |
| 최고 수익률 | 2.94% (frama) |
| 최저 수익률 | -13.67% (supertrend_multi) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `frama` | +2.94% | 1.24 | 54.2% | 1.34 | 18 | 4.9% | 0/2 | FAIL |
| 2 | `value_area` | +2.33% | 1.33 | 50.0% | 1.43 | 14 | 3.4% | 0/2 | FAIL |
| 3 | `linear_channel_rev` | +1.31% | 0.80 | 50.0% | 1.28 | 12 | 5.1% | 0/2 | FAIL |
| 4 | `acceleration_band` | +1.29% | 0.68 | 45.0% | 1.21 | 20 | 6.6% | 0/2 | FAIL |
| 5 | `price_cluster` | +1.29% | 1.32 | 50.0% | 135814116750.39 | 0 | 0.1% | 0/2 | FAIL |
| 6 | `relative_volume` | +0.39% | 0.23 | 44.6% | 1.11 | 32 | 7.3% | 0/2 | FAIL |
| 7 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 8 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 9 | `engulfing_zone` | -0.05% | -0.47 | 43.3% | 1.90 | 10 | 5.1% | 0/2 | FAIL |
| 10 | `roc_ma_cross` | -0.48% | -0.26 | 43.6% | 1.08 | 20 | 5.7% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `frama` | +2.94% | 1.24 | 1.34 | 18 | 0/2 | FAIL |
| `value_area` | +2.33% | 1.33 | 1.43 | 14 | 0/2 | FAIL |
| `linear_channel_rev` | +1.31% | 0.80 | 1.28 | 12 | 0/2 | FAIL |
| `acceleration_band` | +1.29% | 0.68 | 1.21 | 20 | 0/2 | FAIL |
| `price_cluster` | +1.29% | 1.32 | 135814116750.39 | 0 | 0/2 | FAIL |
| `relative_volume` | +0.39% | 0.23 | 1.11 | 32 | 0/2 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `engulfing_zone` | -0.05% | -0.47 | 1.90 | 10 | 0/2 | FAIL |
| `roc_ma_cross` | -0.48% | -0.26 | 1.08 | 20 | 0/2 | FAIL |
| `positional_scaling` | -2.15% | -1.02 | 0.97 | 18 | 0/2 | FAIL |
| `htf_ema` | -3.58% | -0.94 | 0.95 | 26 | 0/2 | FAIL |
| `narrow_range` | -3.64% | -2.72 | 0.74 | 9 | 0/2 | FAIL |
| `price_action_momentum` | -7.11% | -2.04 | 0.82 | 36 | 0/2 | FAIL |
| `volatility_cluster` | -8.00% | -2.65 | 0.77 | 34 | 0/2 | FAIL |
| `momentum_quality` | -8.18% | -2.75 | 0.77 | 38 | 0/2 | FAIL |
| `elder_impulse` | -9.60% | -4.16 | 0.54 | 22 | 0/2 | FAIL |
| `lob_maker` | -9.64% | -1.81 | 0.88 | 52 | 0/2 | FAIL |
| `order_flow_imbalance_v2` | -10.24% | -2.29 | 0.83 | 46 | 0/2 | FAIL |
| `wick_reversal` | -13.08% | -4.83 | 0.49 | 22 | 0/2 | FAIL |
| `cmf` | -13.21% | -4.06 | 0.68 | 35 | 0/2 | FAIL |
| `supertrend_multi` | -13.67% | -4.78 | 0.57 | 28 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -4.23% -> $9,577
- **Top 5 균등배분**: +1.83% -> $10,183


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-20T14:50:53.575825Z_
_Symbol: SOL/USDT_
_Data Source: Bybit SOL/USDT 1h (paginated)_
_Data Range: 2025-11-21 15:00:00+00:00 ~ 2026-05-20 14:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -5.55% |
| 최고 수익률 | 2.90% (linear_channel_rev) |
| 최저 수익률 | -15.93% (order_flow_imbalance_v2) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `linear_channel_rev` | +2.90% | 1.65 | 48.7% | 1.62 | 9 | 3.1% | 0/2 | FAIL |
| 2 | `engulfing_zone` | +1.29% | 0.58 | 48.2% | 1.38 | 10 | 6.3% | 0/2 | FAIL |
| 3 | `value_area` | +1.06% | 0.79 | 40.6% | 1.38 | 12 | 3.4% | 0/2 | FAIL |
| 4 | `price_cluster` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 5 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 6 | `frama` | -0.17% | -0.06 | 43.3% | 1.04 | 14 | 5.4% | 0/2 | FAIL |
| 7 | `narrow_range` | -2.36% | -1.80 | 37.5% | 0.87 | 8 | 6.2% | 0/2 | FAIL |
| 8 | `momentum_quality` | -2.82% | -1.11 | 38.1% | 0.93 | 34 | 6.7% | 0/2 | FAIL |
| 9 | `positional_scaling` | -3.10% | -1.20 | 35.6% | 0.87 | 18 | 9.7% | 0/2 | FAIL |
| 10 | `roc_ma_cross` | -3.64% | -1.48 | 35.1% | 0.84 | 22 | 7.2% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `linear_channel_rev` | +2.90% | 1.65 | 1.62 | 9 | 0/2 | FAIL |
| `engulfing_zone` | +1.29% | 0.58 | 1.38 | 10 | 0/2 | FAIL |
| `value_area` | +1.06% | 0.79 | 1.38 | 12 | 0/2 | FAIL |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `frama` | -0.17% | -0.06 | 1.04 | 14 | 0/2 | FAIL |
| `narrow_range` | -2.36% | -1.80 | 0.87 | 8 | 0/2 | FAIL |
| `momentum_quality` | -2.82% | -1.11 | 0.93 | 34 | 0/2 | FAIL |
| `positional_scaling` | -3.10% | -1.20 | 0.87 | 18 | 0/2 | FAIL |
| `roc_ma_cross` | -3.64% | -1.48 | 0.84 | 22 | 0/2 | FAIL |
| `acceleration_band` | -4.63% | -1.82 | 0.91 | 24 | 0/2 | FAIL |
| `relative_volume` | -5.65% | -2.39 | 0.92 | 32 | 0/2 | FAIL |
| `lob_maker` | -5.65% | -1.06 | 0.95 | 51 | 0/2 | FAIL |
| `price_action_momentum` | -6.93% | -1.84 | 0.85 | 41 | 0/2 | FAIL |
| `elder_impulse` | -7.52% | -2.65 | 0.76 | 27 | 0/2 | FAIL |
| `htf_ema` | -7.81% | -2.95 | 0.65 | 20 | 0/2 | FAIL |
| `cmf` | -8.25% | -2.13 | 0.83 | 40 | 0/2 | FAIL |
| `volume_breakout` | -12.21% | -3.76 | 0.69 | 34 | 0/2 | FAIL |
| `volatility_cluster` | -12.88% | -5.46 | 0.51 | 34 | 0/2 | FAIL |
| `wick_reversal` | -13.80% | -5.58 | 0.41 | 21 | 0/2 | FAIL |
| `supertrend_multi` | -13.97% | -4.50 | 0.58 | 33 | 0/2 | FAIL |
| `order_flow_imbalance_v2` | -15.93% | -4.50 | 0.64 | 46 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -5.55% -> $9,445
- **Top 5 균등배분**: +1.05% -> $10,105
