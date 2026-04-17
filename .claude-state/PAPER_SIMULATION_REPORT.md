# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-04-17T13:57:51.522553Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-04-17T13:50:40.779210Z_
_Symbol: BTC/USDT_
_Data Source: Bybit BTC/USDT 1h (paginated)_
_Data Range: 2025-10-19 14:00:00+00:00 ~ 2026-04-17 13:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -5.88% |
| 최고 수익률 | 3.63% (relative_volume) |
| 최저 수익률 | -17.32% (price_action_momentum) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `relative_volume` | +3.63% | 1.33 | 50.0% | 1.38 | 29 | 5.6% | 0/2 | FAIL |
| 2 | `engulfing_zone` | +0.72% | 0.32 | 41.7% | 1.21 | 8 | 4.3% | 0/2 | FAIL |
| 3 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 4 | `price_cluster` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 5 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 6 | `narrow_range` | -0.95% | -0.50 | 45.0% | 1.06 | 10 | 4.6% | 0/2 | FAIL |
| 7 | `linear_channel_rev` | -2.13% | -1.42 | 43.2% | 0.92 | 10 | 4.3% | 0/2 | FAIL |
| 8 | `value_area` | -2.15% | -1.16 | 40.9% | 0.90 | 14 | 5.8% | 0/2 | FAIL |
| 9 | `positional_scaling` | -3.40% | -1.40 | 34.1% | 0.92 | 20 | 7.7% | 0/2 | FAIL |
| 10 | `roc_ma_cross` | -4.81% | -2.60 | 38.8% | 0.72 | 18 | 7.8% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `relative_volume` | +3.63% | 1.33 | 1.38 | 29 | 0/2 | FAIL |
| `engulfing_zone` | +0.72% | 0.32 | 1.21 | 8 | 0/2 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `narrow_range` | -0.95% | -0.50 | 1.06 | 10 | 0/2 | FAIL |
| `linear_channel_rev` | -2.13% | -1.42 | 0.92 | 10 | 0/2 | FAIL |
| `value_area` | -2.15% | -1.16 | 0.90 | 14 | 0/2 | FAIL |
| `positional_scaling` | -3.40% | -1.40 | 0.92 | 20 | 0/2 | FAIL |
| `roc_ma_cross` | -4.81% | -2.60 | 0.72 | 18 | 0/2 | FAIL |
| `acceleration_band` | -4.93% | -2.16 | 0.81 | 22 | 0/2 | FAIL |
| `elder_impulse` | -6.91% | -2.45 | 0.84 | 28 | 0/2 | FAIL |
| `cmf` | -7.12% | -2.00 | 0.90 | 39 | 0/2 | FAIL |
| `wick_reversal` | -7.36% | -2.35 | 0.89 | 26 | 0/2 | FAIL |
| `momentum_quality` | -8.24% | -2.73 | 0.81 | 36 | 0/2 | FAIL |
| `frama` | -8.86% | -5.36 | 0.35 | 14 | 0/2 | FAIL |
| `volatility_cluster` | -9.71% | -3.47 | 0.73 | 35 | 0/2 | FAIL |
| `supertrend_multi` | -10.61% | -3.19 | 0.72 | 29 | 0/2 | FAIL |
| `htf_ema` | -10.79% | -4.44 | 0.64 | 20 | 0/2 | FAIL |
| `order_flow_imbalance_v2` | -12.38% | -2.92 | 0.83 | 50 | 0/2 | FAIL |
| `lob_maker` | -15.93% | -3.15 | 0.80 | 52 | 0/2 | FAIL |
| `price_action_momentum` | -17.32% | -4.65 | 0.66 | 46 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -5.88% -> $9,412
- **Top 5 균등배분**: +0.87% -> $10,087


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-04-17T13:54:19.065604Z_
_Symbol: ETH/USDT_
_Data Source: Bybit ETH/USDT 1h (paginated)_
_Data Range: 2025-10-19 14:00:00+00:00 ~ 2026-04-17 13:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 1개 |
| FAIL | 21개 |
| 평균 수익률 | -2.19% |
| 최고 수익률 | 9.87% (engulfing_zone) |
| 최저 수익률 | -12.95% (htf_ema) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `engulfing_zone` | +9.87% | 4.33 | 75.0% | 5.67 | 8 | 1.9% | 0/2 | FAIL |
| 2 | `lob_maker` | +6.53% | 0.88 | 43.6% | 1.27 | 54 | 14.6% | 1/2 | PASS |
| 3 | `acceleration_band` | +4.19% | 1.67 | 47.5% | 1.57 | 20 | 6.1% | 0/2 | FAIL |
| 4 | `narrow_range` | +1.86% | 0.83 | 45.2% | 1.89 | 8 | 4.4% | 0/2 | FAIL |
| 5 | `relative_volume` | +1.65% | 0.70 | 45.7% | 1.29 | 28 | 7.0% | 0/2 | FAIL |
| 6 | `price_cluster` | +0.91% | -0.51 | 50.0% | 129733005340.47 | 1 | 0.4% | 0/2 | FAIL |
| 7 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 8 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 9 | `elder_impulse` | -1.25% | -0.44 | 36.0% | 1.05 | 26 | 9.5% | 0/2 | FAIL |
| 10 | `value_area` | -2.39% | -1.44 | 34.6% | 0.89 | 13 | 5.7% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `engulfing_zone` | +9.87% | 4.33 | 5.67 | 8 | 0/2 | FAIL |
| `lob_maker` | +6.53% | 0.88 | 1.27 | 54 | 1/2 | PASS |
| `acceleration_band` | +4.19% | 1.67 | 1.57 | 20 | 0/2 | FAIL |
| `narrow_range` | +1.86% | 0.83 | 1.89 | 8 | 0/2 | FAIL |
| `relative_volume` | +1.65% | 0.70 | 1.29 | 28 | 0/2 | FAIL |
| `price_cluster` | +0.91% | -0.51 | 129733005340.47 | 1 | 0/2 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `elder_impulse` | -1.25% | -0.44 | 1.05 | 26 | 0/2 | FAIL |
| `value_area` | -2.39% | -1.44 | 0.89 | 13 | 0/2 | FAIL |
| `momentum_quality` | -2.71% | -0.82 | 0.99 | 34 | 0/2 | FAIL |
| `positional_scaling` | -3.11% | -1.42 | 0.92 | 20 | 0/2 | FAIL |
| `wick_reversal` | -3.20% | -1.03 | 0.93 | 19 | 0/2 | FAIL |
| `frama` | -3.70% | -1.51 | 0.87 | 21 | 0/2 | FAIL |
| `supertrend_multi` | -3.87% | -1.03 | 0.94 | 32 | 0/2 | FAIL |
| `linear_channel_rev` | -4.70% | -3.69 | 0.48 | 10 | 0/2 | FAIL |
| `order_flow_imbalance_v2` | -4.84% | -1.02 | 0.98 | 44 | 0/2 | FAIL |
| `roc_ma_cross` | -5.04% | -2.34 | 0.76 | 22 | 0/2 | FAIL |
| `price_action_momentum` | -7.63% | -1.85 | 0.88 | 44 | 0/2 | FAIL |
| `cmf` | -8.09% | -2.32 | 0.82 | 36 | 0/2 | FAIL |
| `volatility_cluster` | -9.62% | -2.98 | 0.77 | 41 | 0/2 | FAIL |
| `htf_ema` | -12.95% | -5.34 | 0.43 | 19 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -2.19% -> $9,782
- **PASS 1개 균등배분**: +6.53% -> $10,653
- **Top 5 균등배분**: +4.82% -> $10,482


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-04-17T13:57:51.521479Z_
_Symbol: SOL/USDT_
_Data Source: Bybit SOL/USDT 1h (paginated)_
_Data Range: 2025-10-19 14:00:00+00:00 ~ 2026-04-17 13:00:00+00:00 (179일)_
_Walk-Forward: 2개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 1개 |
| FAIL | 21개 |
| 평균 수익률 | -2.87% |
| 최고 수익률 | 18.09% (lob_maker) |
| 최저 수익률 | -14.67% (volume_breakout) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `lob_maker` | +18.09% | 2.94 | 50.9% | 1.56 | 50 | 10.5% | 1/2 | PASS |
| 2 | `engulfing_zone` | +5.11% | 2.10 | 54.2% | 1.77 | 11 | 3.2% | 0/2 | FAIL |
| 3 | `momentum_quality` | +3.56% | 1.06 | 46.5% | 1.33 | 30 | 7.3% | 0/2 | FAIL |
| 4 | `order_flow_imbalance_v2` | +3.20% | 0.57 | 46.0% | 1.23 | 46 | 13.9% | 0/2 | FAIL |
| 5 | `relative_volume` | +1.86% | 0.72 | 48.4% | 1.28 | 27 | 6.2% | 0/2 | FAIL |
| 6 | `price_cluster` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 7 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/2 | FAIL |
| 8 | `narrow_range` | -2.24% | -1.74 | 35.4% | 0.68 | 7 | 4.5% | 0/2 | FAIL |
| 9 | `frama` | -2.54% | -0.98 | 36.1% | 0.91 | 18 | 5.7% | 0/2 | FAIL |
| 10 | `acceleration_band` | -3.08% | -1.30 | 39.8% | 1.06 | 23 | 10.3% | 0/2 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `lob_maker` | +18.09% | 2.94 | 1.56 | 50 | 1/2 | PASS |
| `engulfing_zone` | +5.11% | 2.10 | 1.77 | 11 | 0/2 | FAIL |
| `momentum_quality` | +3.56% | 1.06 | 1.33 | 30 | 0/2 | FAIL |
| `order_flow_imbalance_v2` | +3.20% | 0.57 | 1.23 | 46 | 0/2 | FAIL |
| `relative_volume` | +1.86% | 0.72 | 1.28 | 27 | 0/2 | FAIL |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/2 | FAIL |
| `narrow_range` | -2.24% | -1.74 | 0.68 | 7 | 0/2 | FAIL |
| `frama` | -2.54% | -0.98 | 0.91 | 18 | 0/2 | FAIL |
| `acceleration_band` | -3.08% | -1.30 | 1.06 | 23 | 0/2 | FAIL |
| `value_area` | -3.58% | -2.17 | 0.68 | 12 | 0/2 | FAIL |
| `linear_channel_rev` | -3.75% | -2.95 | 0.83 | 12 | 0/2 | FAIL |
| `htf_ema` | -5.14% | -1.72 | 0.88 | 20 | 0/2 | FAIL |
| `wick_reversal` | -5.36% | -1.96 | 0.81 | 20 | 0/2 | FAIL |
| `elder_impulse` | -5.55% | -1.77 | 0.92 | 28 | 0/2 | FAIL |
| `volatility_cluster` | -5.96% | -2.25 | 0.95 | 38 | 0/2 | FAIL |
| `roc_ma_cross` | -7.32% | -3.82 | 0.55 | 18 | 0/2 | FAIL |
| `supertrend_multi` | -7.78% | -2.15 | 0.82 | 34 | 0/2 | FAIL |
| `price_action_momentum` | -8.10% | -2.21 | 0.84 | 40 | 0/2 | FAIL |
| `positional_scaling` | -8.75% | -3.68 | 0.58 | 20 | 0/2 | FAIL |
| `cmf` | -11.20% | -2.86 | 0.78 | 43 | 0/2 | FAIL |
| `volume_breakout` | -14.67% | -4.74 | 0.65 | 37 | 0/2 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -2.87% -> $9,713
- **PASS 1개 균등배분**: +18.09% -> $11,808
- **Top 5 균등배분**: +6.36% -> $10,636
