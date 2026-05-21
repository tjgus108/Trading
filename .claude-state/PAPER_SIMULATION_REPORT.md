# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-21T18:29:50.643599Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-21T18:20:03.765581Z_
_Symbol: BTC/USDT_
_Data Source: Bybit BTC/USDT 1h (paginated)_
_Data Range: 2025-05-26 19:00:00+00:00 ~ 2026-05-21 18:00:00+00:00 (359일)_
_Walk-Forward: 8개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -5.05% |
| 최고 수익률 | 0.36% (value_area) |
| 최저 수익률 | -12.28% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `value_area` | +0.36% | 0.08 | 43.0% | 1.21 | 14 | 4.9% | 0/8 | FAIL |
| 2 | `dema_cross` | +0.16% | 0.34 | 12.5% | 16185363670.67 | 0 | 0.0% | 0/8 | FAIL |
| 3 | `price_cluster` | +0.11% | -0.03 | 12.5% | 33520977634.06 | 0 | 0.2% | 0/8 | FAIL |
| 4 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 5 | `linear_channel_rev` | -0.01% | -0.04 | 46.7% | 1.20 | 10 | 3.5% | 0/8 | FAIL |
| 6 | `narrow_range` | -0.49% | -0.78 | 38.7% | 1.49 | 11 | 5.0% | 0/8 | FAIL |
| 7 | `roc_ma_cross` | -1.77% | -0.82 | 41.2% | 1.02 | 18 | 6.1% | 0/8 | FAIL |
| 8 | `relative_volume` | -2.27% | -0.80 | 39.8% | 1.06 | 30 | 8.1% | 0/8 | FAIL |
| 9 | `positional_scaling` | -3.44% | -1.80 | 34.2% | 0.87 | 20 | 7.6% | 0/8 | FAIL |
| 10 | `acceleration_band` | -3.62% | -1.81 | 35.8% | 0.84 | 21 | 8.0% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `value_area` | +0.36% | 0.08 | 1.21 | 14 | 0/8 | FAIL |
| `dema_cross` | +0.16% | 0.34 | 16185363670.67 | 0 | 0/8 | FAIL |
| `price_cluster` | +0.11% | -0.03 | 33520977634.06 | 0 | 0/8 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `linear_channel_rev` | -0.01% | -0.04 | 1.20 | 10 | 0/8 | FAIL |
| `narrow_range` | -0.49% | -0.78 | 1.49 | 11 | 0/8 | FAIL |
| `roc_ma_cross` | -1.77% | -0.82 | 1.02 | 18 | 0/8 | FAIL |
| `relative_volume` | -2.27% | -0.80 | 1.06 | 30 | 0/8 | FAIL |
| `positional_scaling` | -3.44% | -1.80 | 0.87 | 20 | 0/8 | FAIL |
| `acceleration_band` | -3.62% | -1.81 | 0.84 | 21 | 0/8 | FAIL |
| `htf_ema` | -4.09% | -1.65 | 0.96 | 22 | 0/8 | FAIL |
| `elder_impulse` | -4.89% | -1.78 | 0.91 | 25 | 0/8 | FAIL |
| `volatility_cluster` | -5.83% | -1.94 | 0.86 | 37 | 0/8 | FAIL |
| `engulfing_zone` | -5.89% | -3.67 | 0.74 | 10 | 0/8 | FAIL |
| `frama` | -6.37% | -3.81 | 0.56 | 15 | 0/8 | FAIL |
| `momentum_quality` | -7.82% | -2.88 | 0.79 | 36 | 0/8 | FAIL |
| `cmf` | -8.97% | -2.59 | 0.85 | 42 | 0/8 | FAIL |
| `wick_reversal` | -10.14% | -3.39 | 0.80 | 27 | 0/8 | FAIL |
| `supertrend_multi` | -10.80% | -2.40 | 0.86 | 56 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -11.15% | -2.95 | 0.82 | 49 | 0/8 | FAIL |
| `price_action_momentum` | -11.83% | -3.47 | 0.73 | 41 | 0/8 | FAIL |
| `lob_maker` | -12.28% | -2.56 | 0.87 | 52 | 0/8 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -5.05% -> $9,495
- **Top 5 균등배분**: +0.12% -> $10,012


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-21T18:23:24.342169Z_
_Symbol: ETH/USDT_
_Data Source: Bybit ETH/USDT 1h (paginated)_
_Data Range: 2025-05-26 19:00:00+00:00 ~ 2026-05-21 18:00:00+00:00 (359일)_
_Walk-Forward: 8개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -2.85% |
| 최고 수익률 | 1.72% (value_area) |
| 최저 수익률 | -9.02% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `value_area` | +1.72% | 0.92 | 43.5% | 1.35 | 13 | 4.0% | 0/8 | FAIL |
| 2 | `price_cluster` | +0.10% | -0.86 | 25.0% | 70558188380.40 | 1 | 0.6% | 0/8 | FAIL |
| 3 | `positional_scaling` | -0.09% | -0.06 | 42.3% | 1.11 | 19 | 5.9% | 0/8 | FAIL |
| 4 | `dema_cross` | -0.13% | -0.36 | 0.0% | 0.00 | 0 | 0.1% | 0/8 | FAIL |
| 5 | `acceleration_band` | -0.24% | -0.37 | 39.5% | 1.11 | 18 | 7.3% | 0/8 | FAIL |
| 6 | `volume_breakout` | -0.74% | -1.03 | 6.2% | 0.19 | 2 | 1.3% | 0/8 | FAIL |
| 7 | `supertrend_multi` | -0.89% | -0.68 | 39.3% | 1.01 | 37 | 12.9% | 0/8 | FAIL |
| 8 | `linear_channel_rev` | -0.91% | -0.74 | 36.9% | 1.03 | 11 | 4.6% | 0/8 | FAIL |
| 9 | `roc_ma_cross` | -2.27% | -1.11 | 36.8% | 0.90 | 20 | 6.0% | 0/8 | FAIL |
| 10 | `narrow_range` | -2.29% | -1.90 | 32.5% | 1.03 | 9 | 6.4% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `value_area` | +1.72% | 0.92 | 1.35 | 13 | 0/8 | FAIL |
| `price_cluster` | +0.10% | -0.86 | 70558188380.40 | 1 | 0/8 | FAIL |
| `positional_scaling` | -0.09% | -0.06 | 1.11 | 19 | 0/8 | FAIL |
| `dema_cross` | -0.13% | -0.36 | 0.00 | 0 | 0/8 | FAIL |
| `acceleration_band` | -0.24% | -0.37 | 1.11 | 18 | 0/8 | FAIL |
| `volume_breakout` | -0.74% | -1.03 | 0.19 | 2 | 0/8 | FAIL |
| `supertrend_multi` | -0.89% | -0.68 | 1.01 | 37 | 0/8 | FAIL |
| `linear_channel_rev` | -0.91% | -0.74 | 1.03 | 11 | 0/8 | FAIL |
| `roc_ma_cross` | -2.27% | -1.11 | 0.90 | 20 | 0/8 | FAIL |
| `narrow_range` | -2.29% | -1.90 | 1.03 | 9 | 0/8 | FAIL |
| `frama` | -2.32% | -1.20 | 0.95 | 19 | 0/8 | FAIL |
| `engulfing_zone` | -2.77% | -1.93 | 1.42 | 8 | 0/8 | FAIL |
| `relative_volume` | -2.94% | -1.20 | 1.00 | 30 | 0/8 | FAIL |
| `htf_ema` | -3.23% | -1.07 | 0.91 | 23 | 0/8 | FAIL |
| `elder_impulse` | -3.56% | -1.45 | 0.93 | 26 | 0/8 | FAIL |
| `cmf` | -3.60% | -1.00 | 0.98 | 39 | 0/8 | FAIL |
| `price_action_momentum` | -4.53% | -1.59 | 0.91 | 41 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -4.69% | -1.27 | 0.96 | 47 | 0/8 | FAIL |
| `momentum_quality` | -5.53% | -1.77 | 0.89 | 36 | 0/8 | FAIL |
| `volatility_cluster` | -7.01% | -2.57 | 0.81 | 37 | 0/8 | FAIL |
| `lob_maker` | -7.68% | -2.01 | 0.92 | 53 | 0/8 | FAIL |
| `wick_reversal` | -9.02% | -3.36 | 0.68 | 21 | 0/8 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -2.85% -> $9,715
- **Top 5 균등배분**: +0.27% -> $10,027


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-21T18:29:50.641901Z_
_Symbol: SOL/USDT_
_Data Source: Bybit SOL/USDT 1h (paginated)_
_Data Range: 2025-05-26 19:00:00+00:00 ~ 2026-05-21 18:00:00+00:00 (359일)_
_Walk-Forward: 8개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -3.74% |
| 최고 수익률 | 0.72% (price_cluster) |
| 최저 수익률 | -8.66% (cmf) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +0.72% | 0.57 | 31.2% | 82598209542.17 | 1 | 0.5% | 0/8 | FAIL |
| 2 | `narrow_range` | -0.12% | -0.45 | 42.1% | 1.17 | 8 | 3.9% | 0/8 | FAIL |
| 3 | `dema_cross` | -0.40% | -0.87 | 0.0% | 0.00 | 0 | 0.4% | 0/8 | FAIL |
| 4 | `linear_channel_rev` | -0.93% | -0.81 | 37.6% | 1.10 | 10 | 4.7% | 0/8 | FAIL |
| 5 | `acceleration_band` | -1.23% | -0.69 | 42.3% | 1.08 | 22 | 8.1% | 0/8 | FAIL |
| 6 | `value_area` | -1.97% | -1.12 | 32.5% | 0.94 | 14 | 5.4% | 0/8 | FAIL |
| 7 | `positional_scaling` | -2.67% | -1.07 | 36.2% | 0.95 | 20 | 7.5% | 0/8 | FAIL |
| 8 | `supertrend_multi` | -2.77% | -1.25 | 35.0% | 0.88 | 36 | 10.9% | 0/8 | FAIL |
| 9 | `engulfing_zone` | -2.91% | -1.70 | 35.7% | 0.98 | 12 | 7.5% | 0/8 | FAIL |
| 10 | `roc_ma_cross` | -3.70% | -1.89 | 32.4% | 0.81 | 20 | 7.3% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +0.72% | 0.57 | 82598209542.17 | 1 | 0/8 | FAIL |
| `narrow_range` | -0.12% | -0.45 | 1.17 | 8 | 0/8 | FAIL |
| `dema_cross` | -0.40% | -0.87 | 0.00 | 0 | 0/8 | FAIL |
| `linear_channel_rev` | -0.93% | -0.81 | 1.10 | 10 | 0/8 | FAIL |
| `acceleration_band` | -1.23% | -0.69 | 1.08 | 22 | 0/8 | FAIL |
| `value_area` | -1.97% | -1.12 | 0.94 | 14 | 0/8 | FAIL |
| `positional_scaling` | -2.67% | -1.07 | 0.95 | 20 | 0/8 | FAIL |
| `supertrend_multi` | -2.77% | -1.25 | 0.88 | 36 | 0/8 | FAIL |
| `engulfing_zone` | -2.91% | -1.70 | 0.98 | 12 | 0/8 | FAIL |
| `roc_ma_cross` | -3.70% | -1.89 | 0.81 | 20 | 0/8 | FAIL |
| `price_action_momentum` | -4.00% | -1.36 | 0.94 | 42 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -4.12% | -1.47 | 0.94 | 48 | 0/8 | FAIL |
| `frama` | -4.17% | -1.72 | 0.81 | 19 | 0/8 | FAIL |
| `momentum_quality` | -4.31% | -1.72 | 0.93 | 33 | 0/8 | FAIL |
| `wick_reversal` | -4.41% | -1.64 | 0.85 | 20 | 0/8 | FAIL |
| `volume_breakout` | -4.81% | -1.54 | 0.91 | 37 | 0/8 | FAIL |
| `elder_impulse` | -5.17% | -1.86 | 0.86 | 28 | 0/8 | FAIL |
| `volatility_cluster` | -5.51% | -2.27 | 0.86 | 35 | 0/8 | FAIL |
| `htf_ema` | -6.29% | -2.22 | 0.82 | 25 | 0/8 | FAIL |
| `relative_volume` | -6.66% | -2.46 | 0.84 | 33 | 0/8 | FAIL |
| `lob_maker` | -8.24% | -2.02 | 0.91 | 53 | 0/8 | FAIL |
| `cmf` | -8.66% | -2.48 | 0.79 | 40 | 0/8 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.74% -> $9,626
- **Top 5 균등배분**: -0.39% -> $9,961
