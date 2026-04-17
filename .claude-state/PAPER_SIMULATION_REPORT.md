# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-04-17T14:49:58.594933Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-04-17T14:41:02.201055Z_
_Symbol: BTC/USDT_
_Data Source: Bybit BTC/USDT 1h (paginated)_
_Data Range: 2025-10-19 15:00:00+00:00 ~ 2026-04-17 14:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -7.96% |
| 최고 수익률 | 1.00% (relative_volume) |
| 최저 수익률 | -20.48% (price_action_momentum) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `relative_volume` | +1.00% | 0.39 | 49.1% | 1.22 | 28 | 6.0% | 0/2 | FAIL |
| 2 | `engulfing_zone` | +0.17% | 0.05 | 41.7% | 1.12 | 8 | 4.6% | 0/2 | FAIL |
| 3 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 4 | `price_cluster` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 5 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 6 | `narrow_range` | -2.84% | -1.75 | 40.0% | 0.88 | 10 | 5.0% | 0/2 | FAIL |
| 7 | `linear_channel_rev` | -4.01% | -2.81 | 32.4% | 0.58 | 10 | 5.3% | 0/2 | FAIL |
| 8 | `value_area` | -4.13% | -2.36 | 37.4% | 0.72 | 14 | 6.2% | 0/2 | FAIL |
| 9 | `positional_scaling` | -4.94% | -2.04 | 33.2% | 0.82 | 21 | 8.6% | 0/2 | FAIL |
| 10 | `acceleration_band` | -6.29% | -2.93 | 40.0% | 0.72 | 22 | 11.0% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `relative_volume` | +1.00% | 0.39 | 1.22 | 28 | 0/2 | FAIL |
| `engulfing_zone` | +0.17% | 0.05 | 1.12 | 8 | 0/2 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `narrow_range` | -2.84% | -1.75 | 0.88 | 10 | 0/2 | FAIL |
| `linear_channel_rev` | -4.01% | -2.81 | 0.58 | 10 | 0/2 | FAIL |
| `value_area` | -4.13% | -2.36 | 0.72 | 14 | 0/2 | FAIL |
| `positional_scaling` | -4.94% | -2.04 | 0.82 | 21 | 0/2 | FAIL |
| `acceleration_band` | -6.29% | -2.93 | 0.72 | 22 | 0/2 | FAIL |
| `roc_ma_cross` | -7.43% | -4.06 | 0.53 | 18 | 0/2 | FAIL |
| `frama` | -9.56% | -5.73 | 0.32 | 14 | 0/2 | FAIL |
| `wick_reversal` | -9.93% | -3.13 | 0.78 | 26 | 0/2 | FAIL |
| `momentum_quality` | -10.29% | -3.72 | 0.70 | 34 | 0/2 | FAIL |
| `htf_ema` | -11.12% | -4.38 | 0.61 | 20 | 0/2 | FAIL |
| `cmf` | -11.25% | -3.28 | 0.77 | 40 | 0/2 | FAIL |
| `elder_impulse` | -11.73% | -4.04 | 0.69 | 30 | 0/2 | FAIL |
| `supertrend_multi` | -14.79% | -4.49 | 0.60 | 30 | 0/2 | FAIL |
| `order_flow_imbalance_v2` | -15.33% | -3.73 | 0.76 | 50 | 0/2 | FAIL |
| `volatility_cluster` | -15.55% | -5.63 | 0.55 | 36 | 0/2 | FAIL |
| `lob_maker` | -16.69% | -3.33 | 0.80 | 53 | 0/2 | FAIL |
| `price_action_momentum` | -20.48% | -5.57 | 0.59 | 46 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -7.96% -> $9,204
- **Top 5 균등배분**: +0.23% -> $10,023


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-04-17T14:46:25.932805Z_
_Symbol: ETH/USDT_
_Data Source: Bybit ETH/USDT 1h (paginated)_
_Data Range: 2025-10-19 15:00:00+00:00 ~ 2026-04-17 14:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -3.05% |
| 최고 수익률 | 9.34% (engulfing_zone) |
| 최저 수익률 | -10.89% (volatility_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `engulfing_zone` | +9.34% | 4.18 | 75.0% | 5.32 | 8 | 1.9% | 0/2 | FAIL |
| 2 | `lob_maker` | +8.96% | 1.11 | 46.7% | 1.34 | 52 | 14.9% | 0/2 | FAIL |
| 3 | `acceleration_band` | +4.26% | 1.63 | 50.0% | 1.58 | 20 | 6.4% | 0/2 | FAIL |
| 4 | `narrow_range` | +1.38% | 0.59 | 45.2% | 1.78 | 8 | 4.7% | 0/2 | FAIL |
| 5 | `price_cluster` | +0.78% | -0.45 | 50.0% | 122986508669.28 | 1 | 0.4% | 0/2 | FAIL |
| 6 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 7 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 8 | `relative_volume` | -1.55% | -0.45 | 45.7% | 1.07 | 28 | 7.8% | 0/2 | FAIL |
| 9 | `elder_impulse` | -2.51% | -1.10 | 36.0% | 0.98 | 26 | 10.1% | 0/2 | FAIL |
| 10 | `value_area` | -3.71% | -2.19 | 34.6% | 0.75 | 13 | 6.0% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `engulfing_zone` | +9.34% | 4.18 | 5.32 | 8 | 0/2 | FAIL |
| `lob_maker` | +8.96% | 1.11 | 1.34 | 52 | 0/2 | FAIL |
| `acceleration_band` | +4.26% | 1.63 | 1.58 | 20 | 0/2 | FAIL |
| `narrow_range` | +1.38% | 0.59 | 1.78 | 8 | 0/2 | FAIL |
| `price_cluster` | +0.78% | -0.45 | 122986508669.28 | 1 | 0/2 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `relative_volume` | -1.55% | -0.45 | 1.07 | 28 | 0/2 | FAIL |
| `elder_impulse` | -2.51% | -1.10 | 0.98 | 26 | 0/2 | FAIL |
| `value_area` | -3.71% | -2.19 | 0.75 | 13 | 0/2 | FAIL |
| `wick_reversal` | -4.23% | -1.40 | 0.88 | 19 | 0/2 | FAIL |
| `supertrend_multi` | -4.67% | -1.30 | 0.91 | 32 | 0/2 | FAIL |
| `momentum_quality` | -4.92% | -1.64 | 0.89 | 34 | 0/2 | FAIL |
| `linear_channel_rev` | -5.13% | -3.99 | 0.44 | 10 | 0/2 | FAIL |
| `frama` | -5.17% | -2.14 | 0.76 | 20 | 0/2 | FAIL |
| `roc_ma_cross` | -5.90% | -2.75 | 0.71 | 22 | 0/2 | FAIL |
| `positional_scaling` | -6.06% | -2.70 | 0.75 | 20 | 0/2 | FAIL |
| `htf_ema` | -8.73% | -3.72 | 0.66 | 18 | 0/2 | FAIL |
| `order_flow_imbalance_v2` | -9.12% | -2.28 | 0.86 | 44 | 0/2 | FAIL |
| `cmf` | -9.57% | -2.81 | 0.77 | 37 | 0/2 | FAIL |
| `price_action_momentum` | -9.59% | -2.39 | 0.83 | 44 | 0/2 | FAIL |
| `volatility_cluster` | -10.89% | -3.46 | 0.73 | 42 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.05% -> $9,695
- **Top 5 균등배분**: +4.95% -> $10,495


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-04-17T14:49:58.593958Z_
_Symbol: SOL/USDT_
_Data Source: Bybit SOL/USDT 1h (paginated)_
_Data Range: 2025-10-19 15:00:00+00:00 ~ 2026-04-17 14:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -4.34% |
| 최고 수익률 | 15.15% (lob_maker) |
| 최저 수익률 | -15.88% (cmf) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `lob_maker` | +15.15% | 2.69 | 51.8% | 1.47 | 50 | 9.2% | 0/2 | FAIL |
| 2 | `engulfing_zone` | +5.50% | 2.29 | 56.8% | 1.90 | 10 | 3.3% | 0/2 | FAIL |
| 3 | `relative_volume` | +1.85% | 0.68 | 47.4% | 1.29 | 28 | 6.2% | 0/2 | FAIL |
| 4 | `order_flow_imbalance_v2` | +0.49% | -0.11 | 46.5% | 1.14 | 47 | 14.6% | 0/2 | FAIL |
| 5 | `price_cluster` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 6 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 7 | `momentum_quality` | -0.58% | -0.50 | 43.2% | 1.07 | 30 | 8.2% | 0/2 | FAIL |
| 8 | `narrow_range` | -2.56% | -1.99 | 35.4% | 0.64 | 7 | 4.6% | 0/2 | FAIL |
| 9 | `frama` | -3.11% | -1.23 | 36.1% | 0.87 | 18 | 6.0% | 0/2 | FAIL |
| 10 | `value_area` | -4.00% | -2.43 | 30.4% | 0.64 | 12 | 5.8% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `lob_maker` | +15.15% | 2.69 | 1.47 | 50 | 0/2 | FAIL |
| `engulfing_zone` | +5.50% | 2.29 | 1.90 | 10 | 0/2 | FAIL |
| `relative_volume` | +1.85% | 0.68 | 1.29 | 28 | 0/2 | FAIL |
| `order_flow_imbalance_v2` | +0.49% | -0.11 | 1.14 | 47 | 0/2 | FAIL |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `momentum_quality` | -0.58% | -0.50 | 1.07 | 30 | 0/2 | FAIL |
| `narrow_range` | -2.56% | -1.99 | 0.64 | 7 | 0/2 | FAIL |
| `frama` | -3.11% | -1.23 | 0.87 | 18 | 0/2 | FAIL |
| `value_area` | -4.00% | -2.43 | 0.64 | 12 | 0/2 | FAIL |
| `linear_channel_rev` | -4.22% | -3.20 | 0.78 | 12 | 0/2 | FAIL |
| `htf_ema` | -4.50% | -1.53 | 0.91 | 21 | 0/2 | FAIL |
| `acceleration_band` | -4.89% | -1.96 | 0.92 | 23 | 0/2 | FAIL |
| `elder_impulse` | -6.71% | -2.16 | 0.89 | 29 | 0/2 | FAIL |
| `wick_reversal` | -7.45% | -2.70 | 0.73 | 20 | 0/2 | FAIL |
| `volatility_cluster` | -7.86% | -2.76 | 0.86 | 38 | 0/2 | FAIL |
| `roc_ma_cross` | -8.03% | -4.17 | 0.52 | 18 | 0/2 | FAIL |
| `positional_scaling` | -9.71% | -3.95 | 0.55 | 20 | 0/2 | FAIL |
| `price_action_momentum` | -10.50% | -2.92 | 0.78 | 41 | 0/2 | FAIL |
| `supertrend_multi` | -13.15% | -3.63 | 0.69 | 38 | 0/2 | FAIL |
| `volume_breakout` | -15.38% | -4.96 | 0.63 | 36 | 0/2 | FAIL |
| `cmf` | -15.88% | -4.30 | 0.66 | 44 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -4.34% -> $9,566
- **Top 5 균등배분**: +4.60% -> $10,460
