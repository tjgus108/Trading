# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-25T15:56:52.277829Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-25T15:41:20.765903Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic GBM x8640 (BTC/USDT-like, seed=1202758203)_
_Data Range: 0 ~ 8639 (8640봉)_
_Walk-Forward: 8개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | 10.61% |
| 최고 수익률 | 50.62% (cmf) |
| 최저 수익률 | -6.97% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `cmf` | +50.62% | 6.22 | 53.6% | 2.32 | 57 | 11.4% | 0/8 | FAIL |
| 2 | `price_action_momentum` | +42.20% | 5.59 | 49.1% | 1.74 | 82 | 13.5% | 0/8 | FAIL |
| 3 | `momentum_quality` | +28.30% | 4.28 | 47.3% | 1.69 | 61 | 8.5% | 0/8 | FAIL |
| 4 | `supertrend_multi` | +24.35% | 3.02 | 42.5% | 1.36 | 113 | 22.3% | 0/8 | FAIL |
| 5 | `htf_ema` | +24.11% | 4.85 | 53.2% | 2.07 | 36 | 6.6% | 0/8 | FAIL |
| 6 | `lob_maker` | +15.32% | 2.26 | 42.1% | 1.32 | 63 | 13.7% | 0/8 | FAIL |
| 7 | `acceleration_band` | +12.39% | 2.52 | 44.3% | 1.43 | 50 | 10.7% | 0/8 | FAIL |
| 8 | `order_flow_imbalance_v2` | +8.45% | 1.31 | 41.2% | 1.32 | 43 | 14.3% | 0/8 | FAIL |
| 9 | `volatility_cluster` | +8.28% | 1.96 | 44.3% | 1.51 | 40 | 9.8% | 0/8 | FAIL |
| 10 | `roc_ma_cross` | +8.17% | 3.20 | 50.7% | 2.03 | 19 | 4.5% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `cmf` | +50.62% | 6.22 | 2.32 | 57 | 0/8 | FAIL |
| `price_action_momentum` | +42.20% | 5.59 | 1.74 | 82 | 0/8 | FAIL |
| `momentum_quality` | +28.30% | 4.28 | 1.69 | 61 | 0/8 | FAIL |
| `supertrend_multi` | +24.35% | 3.02 | 1.36 | 113 | 0/8 | FAIL |
| `htf_ema` | +24.11% | 4.85 | 2.07 | 36 | 0/8 | FAIL |
| `lob_maker` | +15.32% | 2.26 | 1.32 | 63 | 0/8 | FAIL |
| `acceleration_band` | +12.39% | 2.52 | 1.43 | 50 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | +8.45% | 1.31 | 1.32 | 43 | 0/8 | FAIL |
| `volatility_cluster` | +8.28% | 1.96 | 1.51 | 40 | 0/8 | FAIL |
| `roc_ma_cross` | +8.17% | 3.20 | 2.03 | 19 | 0/8 | FAIL |
| `linear_channel_rev` | +7.92% | 3.05 | 2.40 | 17 | 0/8 | FAIL |
| `elder_impulse` | +7.63% | 1.95 | 1.63 | 26 | 0/8 | FAIL |
| `positional_scaling` | +5.37% | 2.34 | 2.09 | 13 | 0/8 | FAIL |
| `relative_volume` | +4.92% | 1.43 | 1.38 | 32 | 0/8 | FAIL |
| `value_area` | +1.91% | 1.14 | 2.30 | 7 | 0/8 | FAIL |
| `wick_reversal` | +0.38% | -0.06 | 250.00 | 1 | 0/8 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `price_cluster` | -0.43% | -0.90 | 125.00 | 1 | 0/8 | FAIL |
| `dema_cross` | -2.45% | -2.57 | 0.59 | 6 | 0/8 | FAIL |
| `narrow_range` | -2.69% | -1.04 | 0.96 | 29 | 0/8 | FAIL |
| `frama` | -4.46% | -1.28 | 0.92 | 42 | 0/8 | FAIL |
| `engulfing_zone` | -6.97% | -4.13 | 0.43 | 9 | 0/8 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +10.61% -> $11,061
- **Top 5 균등배분**: +33.92% -> $13,392


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-25T15:49:28.315045Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic GBM x8640 (ETH/USDT-like, seed=497909030)_
_Data Range: 0 ~ 8639 (8640봉)_
_Walk-Forward: 8개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | 12.32% |
| 최고 수익률 | 52.75% (cmf) |
| 최저 수익률 | -3.42% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `cmf` | +52.75% | 6.07 | 50.7% | 2.00 | 65 | 10.7% | 0/8 | FAIL |
| 2 | `price_action_momentum` | +51.58% | 6.36 | 48.8% | 1.78 | 93 | 11.6% | 0/8 | FAIL |
| 3 | `supertrend_multi` | +43.47% | 3.93 | 43.5% | 1.55 | 123 | 21.8% | 0/8 | FAIL |
| 4 | `momentum_quality` | +34.43% | 5.58 | 49.4% | 1.88 | 61 | 7.0% | 0/8 | FAIL |
| 5 | `order_flow_imbalance_v2` | +16.73% | 3.09 | 44.9% | 1.49 | 45 | 9.4% | 0/8 | FAIL |
| 6 | `htf_ema` | +15.10% | 3.33 | 48.2% | 1.68 | 37 | 10.0% | 0/8 | FAIL |
| 7 | `acceleration_band` | +12.20% | 2.37 | 42.6% | 1.40 | 49 | 12.3% | 0/8 | FAIL |
| 8 | `relative_volume` | +10.22% | 2.85 | 45.1% | 1.60 | 32 | 6.6% | 0/8 | FAIL |
| 9 | `lob_maker` | +10.11% | 1.61 | 40.5% | 1.23 | 65 | 16.2% | 0/8 | FAIL |
| 10 | `roc_ma_cross` | +9.80% | 3.79 | 53.2% | 2.99 | 20 | 3.9% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `cmf` | +52.75% | 6.07 | 2.00 | 65 | 0/8 | FAIL |
| `price_action_momentum` | +51.58% | 6.36 | 1.78 | 93 | 0/8 | FAIL |
| `supertrend_multi` | +43.47% | 3.93 | 1.55 | 123 | 0/8 | FAIL |
| `momentum_quality` | +34.43% | 5.58 | 1.88 | 61 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | +16.73% | 3.09 | 1.49 | 45 | 0/8 | FAIL |
| `htf_ema` | +15.10% | 3.33 | 1.68 | 37 | 0/8 | FAIL |
| `acceleration_band` | +12.20% | 2.37 | 1.40 | 49 | 0/8 | FAIL |
| `relative_volume` | +10.22% | 2.85 | 1.60 | 32 | 0/8 | FAIL |
| `lob_maker` | +10.11% | 1.61 | 1.23 | 65 | 0/8 | FAIL |
| `roc_ma_cross` | +9.80% | 3.79 | 2.99 | 20 | 0/8 | FAIL |
| `volatility_cluster` | +9.62% | 2.54 | 1.48 | 41 | 0/8 | FAIL |
| `linear_channel_rev` | +6.54% | 2.64 | 2.13 | 17 | 0/8 | FAIL |
| `positional_scaling` | +6.08% | 2.50 | 1.98 | 13 | 0/8 | FAIL |
| `elder_impulse` | +3.21% | 0.57 | 1.33 | 31 | 0/8 | FAIL |
| `value_area` | +1.10% | 0.05 | 1.34 | 8 | 0/8 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `price_cluster` | -0.40% | -1.08 | 0.00 | 0 | 0/8 | FAIL |
| `dema_cross` | -0.70% | -0.82 | 0.88 | 5 | 0/8 | FAIL |
| `wick_reversal` | -0.95% | -1.61 | 0.00 | 1 | 0/8 | FAIL |
| `frama` | -2.97% | -0.65 | 0.98 | 48 | 0/8 | FAIL |
| `narrow_range` | -3.41% | -1.48 | 0.90 | 26 | 0/8 | FAIL |
| `engulfing_zone` | -3.42% | -1.87 | 0.81 | 11 | 0/8 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +12.32% -> $11,232
- **Top 5 균등배분**: +39.79% -> $13,979


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-25T15:56:52.277492Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic GBM x8640 (SOL/USDT-like, seed=2044988472)_
_Data Range: 0 ~ 8639 (8640봉)_
_Walk-Forward: 8개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | 14.30% |
| 최고 수익률 | 65.70% (price_action_momentum) |
| 최저 수익률 | -0.98% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +65.70% | 7.67 | 52.3% | 1.99 | 89 | 9.0% | 0/8 | FAIL |
| 2 | `cmf` | +48.03% | 6.21 | 51.9% | 1.97 | 64 | 10.5% | 0/8 | FAIL |
| 3 | `momentum_quality` | +38.85% | 6.70 | 53.3% | 2.12 | 61 | 6.7% | 0/8 | FAIL |
| 4 | `supertrend_multi` | +26.42% | 4.75 | 47.6% | 1.72 | 62 | 9.4% | 0/8 | FAIL |
| 5 | `lob_maker` | +25.32% | 3.49 | 44.9% | 1.45 | 64 | 11.0% | 0/8 | FAIL |
| 6 | `order_flow_imbalance_v2` | +24.10% | 3.97 | 48.2% | 1.70 | 44 | 10.0% | 0/8 | FAIL |
| 7 | `htf_ema` | +21.10% | 4.15 | 50.0% | 1.86 | 37 | 7.7% | 0/8 | FAIL |
| 8 | `acceleration_band` | +14.68% | 3.09 | 46.4% | 1.60 | 46 | 9.3% | 0/8 | FAIL |
| 9 | `volatility_cluster` | +11.27% | 3.01 | 45.9% | 1.48 | 44 | 7.7% | 0/8 | FAIL |
| 10 | `narrow_range` | +6.87% | 1.80 | 43.7% | 1.40 | 29 | 6.7% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +65.70% | 7.67 | 1.99 | 89 | 0/8 | FAIL |
| `cmf` | +48.03% | 6.21 | 1.97 | 64 | 0/8 | FAIL |
| `momentum_quality` | +38.85% | 6.70 | 2.12 | 61 | 0/8 | FAIL |
| `supertrend_multi` | +26.42% | 4.75 | 1.72 | 62 | 0/8 | FAIL |
| `lob_maker` | +25.32% | 3.49 | 1.45 | 64 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | +24.10% | 3.97 | 1.70 | 44 | 0/8 | FAIL |
| `htf_ema` | +21.10% | 4.15 | 1.86 | 37 | 0/8 | FAIL |
| `acceleration_band` | +14.68% | 3.09 | 1.60 | 46 | 0/8 | FAIL |
| `volatility_cluster` | +11.27% | 3.01 | 1.48 | 44 | 0/8 | FAIL |
| `narrow_range` | +6.87% | 1.80 | 1.40 | 29 | 0/8 | FAIL |
| `linear_channel_rev` | +6.77% | 2.28 | 2.62 | 18 | 0/8 | FAIL |
| `positional_scaling` | +6.52% | 2.74 | 2.23 | 12 | 0/8 | FAIL |
| `elder_impulse` | +5.84% | 1.48 | 1.48 | 24 | 0/8 | FAIL |
| `value_area` | +5.54% | 2.98 | 4.32 | 7 | 0/8 | FAIL |
| `roc_ma_cross` | +5.23% | 2.00 | 2.13 | 18 | 0/8 | FAIL |
| `relative_volume` | +3.27% | 0.79 | 1.29 | 28 | 0/8 | FAIL |
| `price_cluster` | +0.35% | 0.35 | 125.00 | 0 | 0/8 | FAIL |
| `dema_cross` | +0.32% | -0.16 | 0.91 | 5 | 0/8 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `wick_reversal` | -0.11% | -0.38 | 125.00 | 0 | 0/8 | FAIL |
| `engulfing_zone` | -0.54% | -0.25 | 1.34 | 12 | 0/8 | FAIL |
| `frama` | -0.98% | -0.26 | 1.05 | 43 | 0/8 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +14.30% -> $11,430
- **Top 5 균등배분**: +40.86% -> $14,086
