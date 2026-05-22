# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-22T15:20:54.534964Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-22T15:16:42.293307Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic GBM x8640 (BTC/USDT-like)_
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
| 평균 수익률 | 12.33% |
| 최고 수익률 | 52.22% (price_action_momentum) |
| 최저 수익률 | -5.86% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +52.22% | 6.90 | 50.7% | 1.87 | 85 | 10.8% | 0/8 | FAIL |
| 2 | `cmf` | +46.21% | 5.99 | 51.1% | 1.86 | 64 | 12.1% | 0/8 | FAIL |
| 3 | `momentum_quality` | +30.52% | 5.64 | 51.0% | 1.86 | 60 | 8.1% | 0/8 | FAIL |
| 4 | `order_flow_imbalance_v2` | +26.69% | 4.36 | 49.4% | 1.79 | 44 | 10.5% | 0/8 | FAIL |
| 5 | `supertrend_multi` | +24.81% | 4.46 | 48.0% | 1.80 | 54 | 9.2% | 0/8 | FAIL |
| 6 | `htf_ema` | +24.38% | 4.53 | 52.0% | 1.94 | 39 | 9.3% | 0/8 | FAIL |
| 7 | `acceleration_band` | +18.40% | 3.66 | 46.3% | 1.57 | 50 | 9.3% | 0/8 | FAIL |
| 8 | `lob_maker` | +17.01% | 2.55 | 43.0% | 1.35 | 62 | 15.3% | 0/8 | FAIL |
| 9 | `volatility_cluster` | +10.86% | 2.82 | 46.8% | 1.51 | 39 | 9.0% | 0/8 | FAIL |
| 10 | `relative_volume` | +9.78% | 2.92 | 47.2% | 1.65 | 30 | 6.1% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +52.22% | 6.90 | 1.87 | 85 | 0/8 | FAIL |
| `cmf` | +46.21% | 5.99 | 1.86 | 64 | 0/8 | FAIL |
| `momentum_quality` | +30.52% | 5.64 | 1.86 | 60 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | +26.69% | 4.36 | 1.79 | 44 | 0/8 | FAIL |
| `supertrend_multi` | +24.81% | 4.46 | 1.80 | 54 | 0/8 | FAIL |
| `htf_ema` | +24.38% | 4.53 | 1.94 | 39 | 0/8 | FAIL |
| `acceleration_band` | +18.40% | 3.66 | 1.57 | 50 | 0/8 | FAIL |
| `lob_maker` | +17.01% | 2.55 | 1.35 | 62 | 0/8 | FAIL |
| `volatility_cluster` | +10.86% | 2.82 | 1.51 | 39 | 0/8 | FAIL |
| `relative_volume` | +9.78% | 2.92 | 1.65 | 30 | 0/8 | FAIL |
| `linear_channel_rev` | +7.91% | 3.25 | 2.21 | 17 | 0/8 | FAIL |
| `elder_impulse` | +5.62% | 1.32 | 1.41 | 28 | 0/8 | FAIL |
| `positional_scaling` | +3.39% | 1.06 | 1.98 | 12 | 0/8 | FAIL |
| `roc_ma_cross` | +2.49% | 0.95 | 1.35 | 18 | 0/8 | FAIL |
| `value_area` | +0.85% | 0.36 | 125.85 | 6 | 0/8 | FAIL |
| `dema_cross` | +0.29% | -0.20 | 1.75 | 6 | 0/8 | FAIL |
| `price_cluster` | +0.28% | 0.29 | 250.00 | 0 | 0/8 | FAIL |
| `wick_reversal` | +0.16% | -0.25 | 125.22 | 1 | 0/8 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `narrow_range` | -0.70% | -0.38 | 1.00 | 14 | 0/8 | FAIL |
| `frama` | -3.99% | -0.98 | 0.96 | 43 | 0/8 | FAIL |
| `engulfing_zone` | -5.86% | -2.78 | 0.59 | 11 | 0/8 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +12.33% -> $11,233
- **Top 5 균등배분**: +36.09% -> $13,609


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-22T15:18:48.472910Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic GBM x8640 (ETH/USDT-like)_
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
| 평균 수익률 | 12.33% |
| 최고 수익률 | 52.22% (price_action_momentum) |
| 최저 수익률 | -5.86% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +52.22% | 6.90 | 50.7% | 1.87 | 85 | 10.8% | 0/8 | FAIL |
| 2 | `cmf` | +46.21% | 5.99 | 51.1% | 1.86 | 64 | 12.1% | 0/8 | FAIL |
| 3 | `momentum_quality` | +30.52% | 5.64 | 51.0% | 1.86 | 60 | 8.1% | 0/8 | FAIL |
| 4 | `order_flow_imbalance_v2` | +26.69% | 4.36 | 49.4% | 1.79 | 44 | 10.5% | 0/8 | FAIL |
| 5 | `supertrend_multi` | +24.81% | 4.46 | 48.0% | 1.80 | 54 | 9.2% | 0/8 | FAIL |
| 6 | `htf_ema` | +24.38% | 4.53 | 52.0% | 1.94 | 39 | 9.3% | 0/8 | FAIL |
| 7 | `acceleration_band` | +18.40% | 3.66 | 46.3% | 1.57 | 50 | 9.3% | 0/8 | FAIL |
| 8 | `lob_maker` | +17.01% | 2.55 | 43.0% | 1.35 | 62 | 15.3% | 0/8 | FAIL |
| 9 | `volatility_cluster` | +10.86% | 2.82 | 46.8% | 1.51 | 39 | 9.0% | 0/8 | FAIL |
| 10 | `relative_volume` | +9.78% | 2.92 | 47.2% | 1.65 | 30 | 6.1% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +52.22% | 6.90 | 1.87 | 85 | 0/8 | FAIL |
| `cmf` | +46.21% | 5.99 | 1.86 | 64 | 0/8 | FAIL |
| `momentum_quality` | +30.52% | 5.64 | 1.86 | 60 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | +26.69% | 4.36 | 1.79 | 44 | 0/8 | FAIL |
| `supertrend_multi` | +24.81% | 4.46 | 1.80 | 54 | 0/8 | FAIL |
| `htf_ema` | +24.38% | 4.53 | 1.94 | 39 | 0/8 | FAIL |
| `acceleration_band` | +18.40% | 3.66 | 1.57 | 50 | 0/8 | FAIL |
| `lob_maker` | +17.01% | 2.55 | 1.35 | 62 | 0/8 | FAIL |
| `volatility_cluster` | +10.86% | 2.82 | 1.51 | 39 | 0/8 | FAIL |
| `relative_volume` | +9.78% | 2.92 | 1.65 | 30 | 0/8 | FAIL |
| `linear_channel_rev` | +7.91% | 3.25 | 2.21 | 17 | 0/8 | FAIL |
| `elder_impulse` | +5.62% | 1.32 | 1.41 | 28 | 0/8 | FAIL |
| `positional_scaling` | +3.39% | 1.06 | 1.98 | 12 | 0/8 | FAIL |
| `roc_ma_cross` | +2.49% | 0.95 | 1.35 | 18 | 0/8 | FAIL |
| `value_area` | +0.85% | 0.36 | 125.85 | 6 | 0/8 | FAIL |
| `dema_cross` | +0.29% | -0.20 | 1.75 | 6 | 0/8 | FAIL |
| `price_cluster` | +0.28% | 0.29 | 250.00 | 0 | 0/8 | FAIL |
| `wick_reversal` | +0.16% | -0.25 | 125.22 | 1 | 0/8 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `narrow_range` | -0.70% | -0.38 | 1.00 | 14 | 0/8 | FAIL |
| `frama` | -3.99% | -0.98 | 0.96 | 43 | 0/8 | FAIL |
| `engulfing_zone` | -5.86% | -2.78 | 0.59 | 11 | 0/8 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +12.33% -> $11,233
- **Top 5 균등배분**: +36.09% -> $13,609


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-22T15:20:54.531810Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic GBM x8640 (SOL/USDT-like)_
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
| 평균 수익률 | 12.33% |
| 최고 수익률 | 52.22% (price_action_momentum) |
| 최저 수익률 | -5.86% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +52.22% | 6.90 | 50.7% | 1.87 | 85 | 10.8% | 0/8 | FAIL |
| 2 | `cmf` | +46.21% | 5.99 | 51.1% | 1.86 | 64 | 12.1% | 0/8 | FAIL |
| 3 | `momentum_quality` | +30.52% | 5.64 | 51.0% | 1.86 | 60 | 8.1% | 0/8 | FAIL |
| 4 | `order_flow_imbalance_v2` | +26.69% | 4.36 | 49.4% | 1.79 | 44 | 10.5% | 0/8 | FAIL |
| 5 | `supertrend_multi` | +24.81% | 4.46 | 48.0% | 1.80 | 54 | 9.2% | 0/8 | FAIL |
| 6 | `htf_ema` | +24.38% | 4.53 | 52.0% | 1.94 | 39 | 9.3% | 0/8 | FAIL |
| 7 | `acceleration_band` | +18.40% | 3.66 | 46.3% | 1.57 | 50 | 9.3% | 0/8 | FAIL |
| 8 | `lob_maker` | +17.01% | 2.55 | 43.0% | 1.35 | 62 | 15.3% | 0/8 | FAIL |
| 9 | `volatility_cluster` | +10.86% | 2.82 | 46.8% | 1.51 | 39 | 9.0% | 0/8 | FAIL |
| 10 | `relative_volume` | +9.78% | 2.92 | 47.2% | 1.65 | 30 | 6.1% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +52.22% | 6.90 | 1.87 | 85 | 0/8 | FAIL |
| `cmf` | +46.21% | 5.99 | 1.86 | 64 | 0/8 | FAIL |
| `momentum_quality` | +30.52% | 5.64 | 1.86 | 60 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | +26.69% | 4.36 | 1.79 | 44 | 0/8 | FAIL |
| `supertrend_multi` | +24.81% | 4.46 | 1.80 | 54 | 0/8 | FAIL |
| `htf_ema` | +24.38% | 4.53 | 1.94 | 39 | 0/8 | FAIL |
| `acceleration_band` | +18.40% | 3.66 | 1.57 | 50 | 0/8 | FAIL |
| `lob_maker` | +17.01% | 2.55 | 1.35 | 62 | 0/8 | FAIL |
| `volatility_cluster` | +10.86% | 2.82 | 1.51 | 39 | 0/8 | FAIL |
| `relative_volume` | +9.78% | 2.92 | 1.65 | 30 | 0/8 | FAIL |
| `linear_channel_rev` | +7.91% | 3.25 | 2.21 | 17 | 0/8 | FAIL |
| `elder_impulse` | +5.62% | 1.32 | 1.41 | 28 | 0/8 | FAIL |
| `positional_scaling` | +3.39% | 1.06 | 1.98 | 12 | 0/8 | FAIL |
| `roc_ma_cross` | +2.49% | 0.95 | 1.35 | 18 | 0/8 | FAIL |
| `value_area` | +0.85% | 0.36 | 125.85 | 6 | 0/8 | FAIL |
| `dema_cross` | +0.29% | -0.20 | 1.75 | 6 | 0/8 | FAIL |
| `price_cluster` | +0.28% | 0.29 | 250.00 | 0 | 0/8 | FAIL |
| `wick_reversal` | +0.16% | -0.25 | 125.22 | 1 | 0/8 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `narrow_range` | -0.70% | -0.38 | 1.00 | 14 | 0/8 | FAIL |
| `frama` | -3.99% | -0.98 | 0.96 | 43 | 0/8 | FAIL |
| `engulfing_zone` | -5.86% | -2.78 | 0.59 | 11 | 0/8 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +12.33% -> $11,233
- **Top 5 균등배분**: +36.09% -> $13,609
