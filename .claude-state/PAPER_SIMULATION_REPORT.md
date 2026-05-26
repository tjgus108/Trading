# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-26T15:17:36.145530Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-26T15:20:09.641276Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=18383569, block=36)_
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
| 평균 수익률 | 7.90% |
| 최고 수익률 | 39.98% (supertrend_multi) |
| 최저 수익률 | -15.12% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +39.98% | 3.58 | 44.2% | 1.47 | 132 | 12.5% | 0/4 | FAIL |
| 2 | `lob_maker` | +33.49% | 2.57 | 43.2% | 1.30 | 123 | 15.4% | 0/4 | FAIL |
| 3 | `order_flow_imbalance_v2` | +26.90% | 2.13 | 43.4% | 1.35 | 86 | 19.0% | 0/4 | FAIL |
| 4 | `volume_breakout` | +22.89% | 1.99 | 42.4% | 1.32 | 94 | 15.2% | 0/4 | FAIL |
| 5 | `volatility_cluster` | +18.59% | 2.53 | 46.1% | 1.42 | 83 | 9.7% | 0/4 | FAIL |
| 6 | `momentum_quality` | +15.10% | 1.66 | 40.9% | 1.23 | 120 | 19.7% | 0/4 | FAIL |
| 7 | `cmf` | +11.82% | 0.62 | 38.4% | 1.11 | 119 | 22.1% | 0/4 | FAIL |
| 8 | `price_action_momentum` | +11.38% | 0.83 | 39.4% | 1.14 | 160 | 27.7% | 0/4 | FAIL |
| 9 | `relative_volume` | +7.75% | 1.11 | 41.1% | 1.26 | 58 | 10.3% | 0/4 | FAIL |
| 10 | `elder_impulse` | +6.19% | 0.94 | 38.7% | 1.19 | 63 | 15.5% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `wick_reversal` | 65.4 | p100 | 1.20 | 0.82 | 500.50 | 1 | 0.5% | 0/4 | FAIL |
| 2 | `supertrend_multi` | 60.1 | p95 | 3.58 | 1.72 | 1.47 | 132 | 12.5% | 0/4 | FAIL |
| 3 | `lob_maker` | 56.2 | p90 | 2.57 | 0.70 | 1.30 | 123 | 15.4% | 0/4 | FAIL |
| 4 | `volatility_cluster` | 53.0 | p85 | 2.53 | 1.35 | 1.42 | 83 | 9.7% | 0/4 | FAIL |
| 5 | `momentum_quality` | 46.1 | p80 | 1.66 | 1.48 | 1.23 | 120 | 19.7% | 0/4 | FAIL |
| 6 | `volume_breakout` | 44.0 | p76 | 1.99 | 2.51 | 1.32 | 94 | 15.2% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | 41.9 | p71 | 2.13 | 2.53 | 1.35 | 86 | 19.0% | 0/4 | FAIL |
| 8 | `relative_volume` | 40.5 | p66 | 1.11 | 2.03 | 1.26 | 58 | 10.3% | 0/4 | FAIL |
| 9 | `elder_impulse` | 40.2 | p61 | 0.94 | 1.23 | 1.19 | 63 | 15.5% | 0/4 | FAIL |
| 10 | `value_area` | 39.4 | p57 | 0.20 | 0.74 | 1.12 | 16 | 5.1% | 0/4 | FAIL |
| 11 | `acceleration_band` | 38.6 | p52 | 0.62 | 1.18 | 1.11 | 100 | 21.9% | 0/4 | FAIL |
| 12 | `htf_ema` | 38.4 | p47 | 0.45 | 1.05 | 1.10 | 71 | 16.8% | 0/4 | FAIL |
| 13 | `price_cluster` | 37.9 | p42 | 0.41 | 1.18 | 1.13 | 34 | 10.1% | 0/4 | FAIL |
| 14 | `positional_scaling` | 37.1 | p38 | -0.52 | 0.16 | 0.93 | 24 | 7.9% | 0/4 | FAIL |
| 15 | `price_action_momentum` | 36.8 | p33 | 0.83 | 2.68 | 1.14 | 160 | 27.7% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +39.98% | 3.58 | 1.47 | 132 | 0/4 | FAIL |
| `lob_maker` | +33.49% | 2.57 | 1.30 | 123 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +26.90% | 2.13 | 1.35 | 86 | 0/4 | FAIL |
| `volume_breakout` | +22.89% | 1.99 | 1.32 | 94 | 0/4 | FAIL |
| `volatility_cluster` | +18.59% | 2.53 | 1.42 | 83 | 0/4 | FAIL |
| `momentum_quality` | +15.10% | 1.66 | 1.23 | 120 | 0/4 | FAIL |
| `cmf` | +11.82% | 0.62 | 1.11 | 119 | 0/4 | FAIL |
| `price_action_momentum` | +11.38% | 0.83 | 1.14 | 160 | 0/4 | FAIL |
| `relative_volume` | +7.75% | 1.11 | 1.26 | 58 | 0/4 | FAIL |
| `elder_impulse` | +6.19% | 0.94 | 1.19 | 63 | 0/4 | FAIL |
| `acceleration_band` | +4.42% | 0.62 | 1.11 | 100 | 0/4 | FAIL |
| `htf_ema` | +2.94% | 0.45 | 1.10 | 71 | 0/4 | FAIL |
| `price_cluster` | +2.24% | 0.41 | 1.13 | 34 | 0/4 | FAIL |
| `wick_reversal` | +1.77% | 1.20 | 500.50 | 1 | 0/4 | FAIL |
| `value_area` | +0.46% | 0.20 | 1.12 | 16 | 0/4 | FAIL |
| `engulfing_zone` | +0.15% | 0.08 | 1.08 | 26 | 0/4 | FAIL |
| `roc_ma_cross` | -1.75% | -0.27 | 1.01 | 42 | 0/4 | FAIL |
| `positional_scaling` | -2.04% | -0.52 | 0.93 | 24 | 0/4 | FAIL |
| `narrow_range` | -4.19% | -0.56 | 0.97 | 59 | 0/4 | FAIL |
| `dema_cross` | -4.48% | -2.28 | 0.54 | 12 | 0/4 | FAIL |
| `linear_channel_rev` | -4.73% | -1.48 | 0.94 | 32 | 0/4 | FAIL |
| `frama` | -15.12% | -2.04 | 0.84 | 82 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +7.90% -> $10,790
- **Top 5 균등배분**: +28.37% -> $12,837


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-26T15:22:42.454402Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=1088160053, block=36)_
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
| 평균 수익률 | 31.61% |
| 최고 수익률 | 104.18% (price_action_momentum) |
| 최저 수익률 | -6.95% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +104.18% | 6.10 | 49.7% | 1.76 | 158 | 10.7% | 0/4 | FAIL |
| 2 | `order_flow_imbalance_v2` | +100.78% | 6.69 | 56.8% | 2.27 | 85 | 10.5% | 0/4 | FAIL |
| 3 | `volume_breakout` | +94.37% | 6.88 | 56.4% | 2.29 | 90 | 7.9% | 0/4 | FAIL |
| 4 | `lob_maker` | +92.08% | 5.39 | 50.5% | 1.70 | 124 | 12.4% | 0/4 | FAIL |
| 5 | `momentum_quality` | +81.87% | 6.32 | 51.4% | 1.99 | 115 | 10.7% | 0/4 | FAIL |
| 6 | `cmf` | +66.97% | 4.17 | 46.9% | 1.57 | 122 | 14.5% | 0/4 | FAIL |
| 7 | `supertrend_multi` | +54.56% | 4.90 | 48.2% | 1.69 | 119 | 10.6% | 0/4 | FAIL |
| 8 | `acceleration_band` | +30.66% | 3.16 | 44.8% | 1.47 | 93 | 8.4% | 0/4 | FAIL |
| 9 | `htf_ema` | +29.02% | 3.01 | 47.0% | 1.52 | 70 | 9.7% | 0/4 | FAIL |
| 10 | `relative_volume` | +18.87% | 2.87 | 47.3% | 1.62 | 54 | 7.2% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `volume_breakout` | 63.3 | p100 | 6.88 | 0.44 | 2.29 | 90 | 7.9% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 62.6 | p95 | 6.10 | 0.96 | 1.76 | 158 | 10.7% | 0/4 | FAIL |
| 3 | `order_flow_imbalance_v2` | 58.0 | p90 | 6.69 | 0.92 | 2.27 | 85 | 10.5% | 0/4 | FAIL |
| 4 | `lob_maker` | 57.1 | p85 | 5.39 | 0.67 | 1.70 | 124 | 12.4% | 0/4 | FAIL |
| 5 | `supertrend_multi` | 56.3 | p80 | 4.90 | 0.69 | 1.69 | 119 | 10.6% | 0/4 | FAIL |
| 6 | `momentum_quality` | 55.8 | p76 | 6.32 | 1.71 | 1.99 | 115 | 10.7% | 0/4 | FAIL |
| 7 | `acceleration_band` | 50.6 | p71 | 3.16 | 0.49 | 1.47 | 93 | 8.4% | 0/4 | FAIL |
| 8 | `wick_reversal` | 47.7 | p66 | -1.08 | 1.74 | 250.00 | 1 | 1.0% | 0/4 | FAIL |
| 9 | `cmf` | 47.1 | p61 | 4.17 | 1.58 | 1.57 | 122 | 14.5% | 0/4 | FAIL |
| 10 | `roc_ma_cross` | 46.5 | p57 | 2.87 | 0.51 | 1.77 | 34 | 5.0% | 0/4 | FAIL |
| 11 | `htf_ema` | 44.1 | p52 | 3.01 | 1.09 | 1.52 | 70 | 9.7% | 0/4 | FAIL |
| 12 | `volatility_cluster` | 42.1 | p47 | 2.22 | 1.39 | 1.38 | 82 | 8.6% | 0/4 | FAIL |
| 13 | `relative_volume` | 41.7 | p42 | 2.87 | 1.61 | 1.62 | 54 | 7.2% | 0/4 | FAIL |
| 14 | `positional_scaling` | 36.3 | p38 | 0.16 | 0.56 | 1.08 | 28 | 5.4% | 0/4 | FAIL |
| 15 | `linear_channel_rev` | 35.8 | p33 | 0.75 | 1.14 | 1.23 | 32 | 5.8% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +104.18% | 6.10 | 1.76 | 158 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +100.78% | 6.69 | 2.27 | 85 | 0/4 | FAIL |
| `volume_breakout` | +94.37% | 6.88 | 2.29 | 90 | 0/4 | FAIL |
| `lob_maker` | +92.08% | 5.39 | 1.70 | 124 | 0/4 | FAIL |
| `momentum_quality` | +81.87% | 6.32 | 1.99 | 115 | 0/4 | FAIL |
| `cmf` | +66.97% | 4.17 | 1.57 | 122 | 0/4 | FAIL |
| `supertrend_multi` | +54.56% | 4.90 | 1.69 | 119 | 0/4 | FAIL |
| `acceleration_band` | +30.66% | 3.16 | 1.47 | 93 | 0/4 | FAIL |
| `htf_ema` | +29.02% | 3.01 | 1.52 | 70 | 0/4 | FAIL |
| `relative_volume` | +18.87% | 2.87 | 1.62 | 54 | 0/4 | FAIL |
| `volatility_cluster` | +16.45% | 2.22 | 1.38 | 82 | 0/4 | FAIL |
| `roc_ma_cross` | +13.88% | 2.87 | 1.77 | 34 | 0/4 | FAIL |
| `linear_channel_rev` | +3.10% | 0.75 | 1.23 | 32 | 0/4 | FAIL |
| `elder_impulse` | +1.80% | 0.40 | 1.10 | 50 | 0/4 | FAIL |
| `positional_scaling` | +0.53% | 0.16 | 1.08 | 28 | 0/4 | FAIL |
| `dema_cross` | +0.03% | 0.21 | 1.66 | 9 | 0/4 | FAIL |
| `value_area` | -0.47% | -0.14 | 1.03 | 20 | 0/4 | FAIL |
| `wick_reversal` | -0.52% | -1.08 | 250.00 | 1 | 0/4 | FAIL |
| `price_cluster` | -0.85% | 0.01 | 1.04 | 34 | 0/4 | FAIL |
| `frama` | -1.70% | -0.30 | 1.01 | 79 | 0/4 | FAIL |
| `narrow_range` | -3.21% | -0.60 | 1.02 | 59 | 0/4 | FAIL |
| `engulfing_zone` | -6.95% | -2.18 | 0.73 | 18 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +31.61% -> $13,161
- **Top 5 균등배분**: +94.66% -> $19,466


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-26T15:25:18.675372Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=905475224, block=36)_
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
| 평균 수익률 | 17.51% |
| 최고 수익률 | 89.35% (price_action_momentum) |
| 최저 수익률 | -20.34% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +89.35% | 5.32 | 48.4% | 1.65 | 164 | 18.0% | 0/4 | FAIL |
| 2 | `cmf` | +81.20% | 5.00 | 49.0% | 1.64 | 124 | 14.9% | 0/4 | FAIL |
| 3 | `supertrend_multi` | +65.60% | 5.42 | 50.2% | 1.81 | 116 | 9.8% | 0/4 | FAIL |
| 4 | `momentum_quality` | +48.23% | 4.48 | 47.8% | 1.58 | 126 | 9.9% | 0/4 | FAIL |
| 5 | `acceleration_band` | +34.76% | 2.74 | 44.0% | 1.47 | 102 | 15.3% | 0/4 | FAIL |
| 6 | `htf_ema` | +23.64% | 2.28 | 43.4% | 1.41 | 76 | 16.5% | 0/4 | FAIL |
| 7 | `volume_breakout` | +20.60% | 2.01 | 41.0% | 1.28 | 94 | 16.3% | 0/4 | FAIL |
| 8 | `volatility_cluster` | +16.60% | 2.39 | 44.7% | 1.42 | 73 | 8.9% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | +14.08% | 1.48 | 41.1% | 1.21 | 82 | 18.0% | 0/4 | FAIL |
| 10 | `positional_scaling` | +7.36% | 1.70 | 44.8% | 1.47 | 28 | 6.2% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 79.6 | p100 | 5.42 | 1.93 | 1.81 | 116 | 9.8% | 0/4 | FAIL |
| 2 | `cmf` | 78.5 | p95 | 5.00 | 0.53 | 1.64 | 124 | 14.9% | 0/4 | FAIL |
| 3 | `momentum_quality` | 77.1 | p90 | 4.48 | 1.06 | 1.58 | 126 | 9.9% | 0/4 | FAIL |
| 4 | `price_action_momentum` | 75.9 | p85 | 5.32 | 2.44 | 1.65 | 164 | 18.0% | 0/4 | FAIL |
| 5 | `volatility_cluster` | 63.1 | p80 | 2.39 | 1.13 | 1.42 | 73 | 8.9% | 0/4 | FAIL |
| 6 | `positional_scaling` | 59.6 | p76 | 1.70 | 0.76 | 1.47 | 28 | 6.2% | 0/4 | FAIL |
| 7 | `acceleration_band` | 57.9 | p71 | 2.74 | 3.21 | 1.47 | 102 | 15.3% | 0/4 | FAIL |
| 8 | `volume_breakout` | 57.5 | p66 | 2.01 | 1.38 | 1.28 | 94 | 16.3% | 0/4 | FAIL |
| 9 | `linear_channel_rev` | 57.3 | p61 | 1.60 | 1.12 | 1.40 | 34 | 7.5% | 0/4 | FAIL |
| 10 | `htf_ema` | 55.3 | p57 | 2.28 | 2.32 | 1.41 | 76 | 16.5% | 0/4 | FAIL |
| 11 | `roc_ma_cross` | 54.2 | p52 | 1.35 | 2.42 | 1.56 | 36 | 7.5% | 0/4 | FAIL |
| 12 | `order_flow_imbalance_v2` | 54.0 | p47 | 1.48 | 1.04 | 1.21 | 82 | 18.0% | 0/4 | FAIL |
| 13 | `relative_volume` | 52.2 | p42 | 1.10 | 1.67 | 1.25 | 53 | 10.6% | 0/4 | FAIL |
| 14 | `lob_maker` | 48.6 | p38 | 0.40 | 0.64 | 1.06 | 133 | 28.8% | 0/4 | FAIL |
| 15 | `value_area` | 45.2 | p33 | -0.22 | 1.31 | 1.05 | 17 | 6.2% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +89.35% | 5.32 | 1.65 | 164 | 0/4 | FAIL |
| `cmf` | +81.20% | 5.00 | 1.64 | 124 | 0/4 | FAIL |
| `supertrend_multi` | +65.60% | 5.42 | 1.81 | 116 | 0/4 | FAIL |
| `momentum_quality` | +48.23% | 4.48 | 1.58 | 126 | 0/4 | FAIL |
| `acceleration_band` | +34.76% | 2.74 | 1.47 | 102 | 0/4 | FAIL |
| `htf_ema` | +23.64% | 2.28 | 1.41 | 76 | 0/4 | FAIL |
| `volume_breakout` | +20.60% | 2.01 | 1.28 | 94 | 0/4 | FAIL |
| `volatility_cluster` | +16.60% | 2.39 | 1.42 | 73 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +14.08% | 1.48 | 1.21 | 82 | 0/4 | FAIL |
| `positional_scaling` | +7.36% | 1.70 | 1.47 | 28 | 0/4 | FAIL |
| `linear_channel_rev` | +7.16% | 1.60 | 1.40 | 34 | 0/4 | FAIL |
| `relative_volume` | +6.70% | 1.10 | 1.25 | 53 | 0/4 | FAIL |
| `roc_ma_cross` | +6.64% | 1.35 | 1.56 | 36 | 0/4 | FAIL |
| `lob_maker` | +2.51% | 0.40 | 1.06 | 133 | 0/4 | FAIL |
| `elder_impulse` | +0.80% | 0.12 | 1.08 | 58 | 0/4 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `price_cluster` | -0.28% | -0.10 | 1.04 | 40 | 0/4 | FAIL |
| `value_area` | -0.67% | -0.22 | 1.05 | 17 | 0/4 | FAIL |
| `dema_cross` | -3.60% | -2.81 | 0.42 | 6 | 0/4 | FAIL |
| `narrow_range` | -6.49% | -1.18 | 0.89 | 50 | 0/4 | FAIL |
| `engulfing_zone` | -8.67% | -2.15 | 0.72 | 23 | 0/4 | FAIL |
| `frama` | -20.34% | -2.62 | 0.75 | 88 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +17.51% -> $11,751
- **Top 5 균등배분**: +63.83% -> $16,383
