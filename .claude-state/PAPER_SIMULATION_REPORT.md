# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-29T00:18:11.425304Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-29T00:21:56.126708Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1108275504, block=24)_
_Data Range: 0 ~ 8639 (8640봉)_
_Walk-Forward: 4개 윈도우 (train=5040h, test=1440h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## ML 모델 건강 상태 (ADWIN)

| 항목 | 값 |
|------|-----|
| EWMA Accuracy | 1.0000 |
| EWMA Trend | N/A (unknown) |
| EWMA Samples | 0 |
| Drift Detected | YES |
| Output Drift | NO |
| Retrain Recommended (EWMA) | NO |
| Retrain Recommended (ADWIN) | YES |
| Retrain Count | 3 |
| Feature Drift | 0/3 features drifted |

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | 13.90% |
| 최고 수익률 | 77.62% (price_action_momentum) |
| 최저 수익률 | -10.83% (order_flow_imbalance_v2) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +77.62% | 4.96 | 45.5% | 1.60 | 151 | 13.6% | 0/4 | FAIL |
| 2 | `supertrend_multi` | +61.43% | 6.07 | 54.2% | 2.10 | 91 | 8.7% | 0/4 | FAIL |
| 3 | `momentum_quality` | +50.03% | 4.58 | 47.4% | 1.64 | 114 | 11.3% | 0/4 | FAIL |
| 4 | `cmf` | +36.61% | 2.83 | 43.6% | 1.35 | 120 | 14.5% | 0/4 | FAIL |
| 5 | `volatility_cluster` | +18.73% | 2.64 | 45.8% | 1.41 | 79 | 9.8% | 0/4 | FAIL |
| 6 | `htf_ema` | +17.56% | 1.90 | 42.2% | 1.34 | 72 | 13.2% | 0/4 | FAIL |
| 7 | `narrow_range` | +15.86% | 2.09 | 42.5% | 1.32 | 90 | 10.7% | 0/4 | FAIL |
| 8 | `volume_breakout` | +15.18% | 1.70 | 40.5% | 1.26 | 86 | 10.4% | 0/4 | FAIL |
| 9 | `roc_ma_cross` | +9.05% | 1.87 | 44.7% | 1.54 | 37 | 8.0% | 0/4 | FAIL |
| 10 | `linear_channel_rev` | +6.25% | 1.47 | 44.9% | 1.56 | 33 | 8.4% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 61.8 | p100 | 6.07 | 0.69 | 2.10 | 91 | 8.7% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 55.1 | p95 | 4.96 | 1.83 | 1.60 | 151 | 13.6% | 0/4 | FAIL |
| 3 | `momentum_quality` | 54.8 | p90 | 4.58 | 1.03 | 1.64 | 114 | 11.3% | 0/4 | FAIL |
| 4 | `wick_reversal` | 54.5 | p85 | 0.49 | 0.85 | 250.00 | 0 | 0.0% | 0/4 | FAIL |
| 5 | `volatility_cluster` | 47.5 | p80 | 2.64 | 0.32 | 1.41 | 79 | 9.8% | 0/4 | FAIL |
| 6 | `cmf` | 46.5 | p76 | 2.83 | 0.97 | 1.35 | 120 | 14.5% | 0/4 | FAIL |
| 7 | `narrow_range` | 44.2 | p71 | 2.09 | 0.66 | 1.32 | 90 | 10.7% | 0/4 | FAIL |
| 8 | `volume_breakout` | 40.6 | p66 | 1.70 | 1.06 | 1.26 | 86 | 10.4% | 0/4 | FAIL |
| 9 | `dema_cross` | 39.9 | p61 | 1.39 | 0.26 | 1.54 | 13 | 3.7% | 0/4 | FAIL |
| 10 | `value_area` | 38.0 | p57 | 1.32 | 0.72 | 1.42 | 20 | 4.0% | 0/4 | FAIL |
| 11 | `roc_ma_cross` | 34.8 | p52 | 1.87 | 1.76 | 1.54 | 37 | 8.0% | 0/4 | FAIL |
| 12 | `htf_ema` | 34.7 | p47 | 1.90 | 1.86 | 1.34 | 72 | 13.2% | 0/4 | FAIL |
| 13 | `positional_scaling` | 32.6 | p42 | 0.85 | 1.24 | 1.24 | 32 | 7.8% | 0/4 | FAIL |
| 14 | `linear_channel_rev` | 31.8 | p38 | 1.47 | 1.93 | 1.56 | 33 | 8.4% | 0/4 | FAIL |
| 15 | `relative_volume` | 31.4 | p33 | 0.60 | 1.42 | 1.14 | 54 | 10.2% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +77.62% | 4.96 | 1.60 | 151 | 0/4 | FAIL |
| `supertrend_multi` | +61.43% | 6.07 | 2.10 | 91 | 0/4 | FAIL |
| `momentum_quality` | +50.03% | 4.58 | 1.64 | 114 | 0/4 | FAIL |
| `cmf` | +36.61% | 2.83 | 1.35 | 120 | 0/4 | FAIL |
| `volatility_cluster` | +18.73% | 2.64 | 1.41 | 79 | 0/4 | FAIL |
| `htf_ema` | +17.56% | 1.90 | 1.34 | 72 | 0/4 | FAIL |
| `narrow_range` | +15.86% | 2.09 | 1.32 | 90 | 0/4 | FAIL |
| `volume_breakout` | +15.18% | 1.70 | 1.26 | 86 | 0/4 | FAIL |
| `roc_ma_cross` | +9.05% | 1.87 | 1.54 | 37 | 0/4 | FAIL |
| `linear_channel_rev` | +6.25% | 1.47 | 1.56 | 33 | 0/4 | FAIL |
| `engulfing_zone` | +5.12% | 0.59 | 1.31 | 28 | 0/4 | FAIL |
| `value_area` | +4.40% | 1.32 | 1.42 | 20 | 0/4 | FAIL |
| `positional_scaling` | +3.67% | 0.85 | 1.24 | 32 | 0/4 | FAIL |
| `dema_cross` | +3.67% | 1.39 | 1.54 | 13 | 0/4 | FAIL |
| `lob_maker` | +3.53% | 0.16 | 1.06 | 119 | 0/4 | FAIL |
| `relative_volume` | +3.48% | 0.60 | 1.14 | 54 | 0/4 | FAIL |
| `wick_reversal` | +0.69% | 0.49 | 250.00 | 0 | 0/4 | FAIL |
| `price_cluster` | -1.00% | -0.06 | 1.03 | 41 | 0/4 | FAIL |
| `frama` | -2.23% | -0.09 | 1.02 | 81 | 0/4 | FAIL |
| `acceleration_band` | -4.34% | -0.37 | 1.00 | 98 | 0/4 | FAIL |
| `elder_impulse` | -8.72% | -1.24 | 0.86 | 59 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | -10.83% | -1.23 | 0.90 | 80 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.178 > 0.05 (우연 가능성) (x1), profit_factor 1.42 < 1.5 (x1), mc_p_value 0.296 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | mc_p_value 0.276 > 0.05 (우연 가능성) (x1), mc_p_value 0.292 > 0.05 (우연 가능성) (x1), mc_p_value 0.318 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.288 > 0.05 (우연 가능성) (x1), mc_p_value 0.290 > 0.05 (우연 가능성) (x1), profit_factor 1.43 < 1.5 (x1) |
| `cmf` | profit_factor 1.27 < 1.5 (x2), mc_p_value 0.328 > 0.05 (우연 가능성) (x1), profit_factor 1.25 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.410 > 0.05 (우연 가능성) (x1), profit_factor 1.41 < 1.5 (x1) |
| `htf_ema` | mc_p_value 0.340 > 0.05 (우연 가능성) (x1), sharpe 0.45 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1) |
| `narrow_range` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.374 > 0.05 (우연 가능성) (x1), profit_factor 1.20 < 1.5 (x1) |
| `volume_breakout` | profit_factor 1.39 < 1.5 (x1), mc_p_value 0.410 > 0.05 (우연 가능성) (x1), sharpe 0.82 < 1.0 (x1) |
| `roc_ma_cross` | mc_p_value 0.382 > 0.05 (우연 가능성) (x1), sharpe -0.04 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1) |
| `linear_channel_rev` | mc_p_value 0.384 > 0.05 (우연 가능성) (x1), sharpe -0.33 < 1.0 (x1), profit_factor 0.97 < 1.5 (x1) |
| `engulfing_zone` | sharpe -1.57 < 1.0 (x1), profit_factor 0.75 < 1.5 (x1), mc_p_value 0.540 > 0.05 (우연 가능성) (x1) |
| `value_area` | mc_p_value 0.444 > 0.05 (우연 가능성) (x1), profit_factor 1.50 < 1.5 (x1), mc_p_value 0.432 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | mc_p_value 0.438 > 0.05 (우연 가능성) (x1), sharpe -0.45 < 1.0 (x1), profit_factor 0.94 < 1.5 (x1) |
| `dema_cross` | trades 12 < 15 (x1), trades 13 < 15 (x1), profit_factor 1.32 < 1.5 (x1) |
| `lob_maker` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.372 > 0.05 (우연 가능성) (x1), profit_factor 1.24 < 1.5 (x1) |
| `relative_volume` | profit_factor 1.50 < 1.5 (x1), mc_p_value 0.438 > 0.05 (우연 가능성) (x1), profit_factor 1.19 < 1.5 (x1) |
| `wick_reversal` | no trades generated (x3), trades 1 < 15 (x1) |
| `price_cluster` | sharpe -1.29 < 1.0 (x1), profit_factor 0.82 < 1.5 (x1), mc_p_value 0.552 > 0.05 (우연 가능성) (x1) |
| `frama` | profit_factor 1.17 < 1.5 (x1), mc_p_value 0.446 > 0.05 (우연 가능성) (x1), sharpe 0.27 < 1.0 (x1) |
| `acceleration_band` | profit_factor 1.23 < 1.5 (x1), mc_p_value 0.418 > 0.05 (우연 가능성) (x1), sharpe -1.25 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.27 < 1.5 | 4 |
| mc_p_value 0.508 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.94 < 1.5 | 3 |
| profit_factor 0.86 < 1.5 | 3 |
| no trades generated | 3 |
| profit_factor 1.25 < 1.5 | 2 |
| mc_p_value 0.384 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.376 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.410 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.432 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +13.90% -> $11,390
- **Top 5 균등배분**: +48.89% -> $14,889


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-29T00:25:49.203249Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=1307084153, block=24)_
_Data Range: 0 ~ 8639 (8640봉)_
_Walk-Forward: 4개 윈도우 (train=5040h, test=1440h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## ML 모델 건강 상태 (ADWIN)

| 항목 | 값 |
|------|-----|
| EWMA Accuracy | 1.0000 |
| EWMA Trend | N/A (unknown) |
| EWMA Samples | 0 |
| Drift Detected | YES |
| Output Drift | NO |
| Retrain Recommended (EWMA) | NO |
| Retrain Recommended (ADWIN) | YES |
| Retrain Count | 3 |
| Feature Drift | 0/3 features drifted |

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | 21.86% |
| 최고 수익률 | 81.80% (price_action_momentum) |
| 최저 수익률 | -14.42% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +81.80% | 5.38 | 48.4% | 1.64 | 155 | 13.9% | 0/4 | FAIL |
| 2 | `momentum_quality` | +70.72% | 5.84 | 51.1% | 1.84 | 120 | 10.6% | 0/4 | FAIL |
| 3 | `cmf` | +54.86% | 3.50 | 44.9% | 1.44 | 132 | 17.8% | 0/4 | FAIL |
| 4 | `supertrend_multi` | +52.92% | 5.12 | 50.6% | 1.91 | 83 | 7.9% | 0/4 | FAIL |
| 5 | `acceleration_band` | +45.00% | 3.67 | 47.0% | 1.62 | 96 | 14.4% | 0/4 | FAIL |
| 6 | `htf_ema` | +32.84% | 3.54 | 49.4% | 1.65 | 68 | 12.7% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | +31.77% | 2.84 | 44.0% | 1.41 | 90 | 11.4% | 0/4 | FAIL |
| 8 | `volume_breakout` | +26.64% | 2.58 | 43.6% | 1.35 | 103 | 15.5% | 0/4 | FAIL |
| 9 | `volatility_cluster` | +24.92% | 3.26 | 46.9% | 1.61 | 74 | 8.2% | 0/4 | FAIL |
| 10 | `lob_maker` | +19.82% | 1.66 | 40.7% | 1.20 | 128 | 17.1% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 77.1 | p100 | 5.84 | 1.23 | 1.84 | 120 | 10.6% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 76.0 | p95 | 5.38 | 0.79 | 1.64 | 155 | 13.9% | 0/4 | FAIL |
| 3 | `supertrend_multi` | 70.1 | p90 | 5.12 | 2.10 | 1.91 | 83 | 7.9% | 0/4 | FAIL |
| 4 | `roc_ma_cross` | 63.9 | p85 | 3.42 | 1.77 | 2.12 | 42 | 6.0% | 0/4 | FAIL |
| 5 | `order_flow_imbalance_v2` | 60.6 | p80 | 2.84 | 0.49 | 1.41 | 90 | 11.4% | 0/4 | FAIL |
| 6 | `volatility_cluster` | 60.0 | p76 | 3.26 | 1.82 | 1.61 | 74 | 8.2% | 0/4 | FAIL |
| 7 | `htf_ema` | 59.7 | p71 | 3.54 | 1.24 | 1.65 | 68 | 12.7% | 0/4 | FAIL |
| 8 | `narrow_range` | 58.4 | p66 | 2.27 | 0.64 | 1.34 | 91 | 9.6% | 0/4 | FAIL |
| 9 | `cmf` | 57.9 | p61 | 3.50 | 1.90 | 1.44 | 132 | 17.8% | 0/4 | FAIL |
| 10 | `volume_breakout` | 57.1 | p57 | 2.58 | 0.56 | 1.35 | 103 | 15.5% | 0/4 | FAIL |
| 11 | `positional_scaling` | 56.9 | p52 | 1.96 | 1.63 | 1.97 | 24 | 4.2% | 0/4 | FAIL |
| 12 | `acceleration_band` | 56.0 | p47 | 3.67 | 2.73 | 1.62 | 96 | 14.4% | 0/4 | FAIL |
| 13 | `value_area` | 55.2 | p42 | 1.69 | 0.83 | 1.65 | 17 | 4.0% | 0/4 | FAIL |
| 14 | `lob_maker` | 52.4 | p38 | 1.66 | 0.83 | 1.20 | 128 | 17.1% | 0/4 | FAIL |
| 15 | `relative_volume` | 52.3 | p33 | 2.09 | 1.43 | 1.41 | 57 | 9.5% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +81.80% | 5.38 | 1.64 | 155 | 0/4 | FAIL |
| `momentum_quality` | +70.72% | 5.84 | 1.84 | 120 | 0/4 | FAIL |
| `cmf` | +54.86% | 3.50 | 1.44 | 132 | 0/4 | FAIL |
| `supertrend_multi` | +52.92% | 5.12 | 1.91 | 83 | 0/4 | FAIL |
| `acceleration_band` | +45.00% | 3.67 | 1.62 | 96 | 0/4 | FAIL |
| `htf_ema` | +32.84% | 3.54 | 1.65 | 68 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +31.77% | 2.84 | 1.41 | 90 | 0/4 | FAIL |
| `volume_breakout` | +26.64% | 2.58 | 1.35 | 103 | 0/4 | FAIL |
| `volatility_cluster` | +24.92% | 3.26 | 1.61 | 74 | 0/4 | FAIL |
| `lob_maker` | +19.82% | 1.66 | 1.20 | 128 | 0/4 | FAIL |
| `narrow_range` | +17.88% | 2.27 | 1.34 | 91 | 0/4 | FAIL |
| `roc_ma_cross` | +17.75% | 3.42 | 2.12 | 42 | 0/4 | FAIL |
| `relative_volume` | +13.07% | 2.09 | 1.41 | 57 | 0/4 | FAIL |
| `positional_scaling` | +7.94% | 1.96 | 1.97 | 24 | 0/4 | FAIL |
| `linear_channel_rev` | +5.92% | 1.33 | 1.58 | 28 | 0/4 | FAIL |
| `value_area` | +5.26% | 1.69 | 1.65 | 17 | 0/4 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `elder_impulse` | -0.74% | 0.01 | 1.03 | 56 | 0/4 | FAIL |
| `dema_cross` | -2.50% | -0.97 | 0.79 | 14 | 0/4 | FAIL |
| `price_cluster` | -3.52% | -0.68 | 0.96 | 35 | 0/4 | FAIL |
| `engulfing_zone` | -7.08% | -1.61 | 0.71 | 21 | 0/4 | FAIL |
| `frama` | -14.42% | -1.85 | 0.82 | 80 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | profit_factor 1.47 < 1.5 (x1), mc_p_value 0.294 > 0.05 (우연 가능성) (x1), mc_p_value 0.212 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.228 > 0.05 (우연 가능성) (x1), mc_p_value 0.212 > 0.05 (우연 가능성) (x1), profit_factor 1.48 < 1.5 (x1) |
| `cmf` | max_drawdown 22.3% > 20% (x2), sharpe 0.64 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.32 < 1.5 (x1), mc_p_value 0.428 > 0.05 (우연 가능성) (x1), mc_p_value 0.278 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | mc_p_value 0.288 > 0.05 (우연 가능성) (x1), mc_p_value 0.264 > 0.05 (우연 가능성) (x1), profit_factor 1.31 < 1.5 (x1) |
| `htf_ema` | profit_factor 1.39 < 1.5 (x1), mc_p_value 0.384 > 0.05 (우연 가능성) (x1), mc_p_value 0.288 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.408 > 0.05 (우연 가능성) (x1), mc_p_value 0.312 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 1.22 < 1.5 (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1), profit_factor 1.49 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.27 < 1.5 (x1), mc_p_value 0.442 > 0.05 (우연 가능성) (x1), mc_p_value 0.320 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.406 > 0.05 (우연 가능성) (x1), profit_factor 1.28 < 1.5 (x1) |
| `narrow_range` | profit_factor 1.42 < 1.5 (x1), mc_p_value 0.380 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1) |
| `roc_ma_cross` | mc_p_value 0.402 > 0.05 (우연 가능성) (x1), mc_p_value 0.330 > 0.05 (우연 가능성) (x1), profit_factor 1.48 < 1.5 (x1) |
| `relative_volume` | mc_p_value 0.386 > 0.05 (우연 가능성) (x1), mc_p_value 0.414 > 0.05 (우연 가능성) (x1), sharpe 0.99 < 1.0 (x1) |
| `positional_scaling` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1), mc_p_value 0.396 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -0.27 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1), mc_p_value 0.462 > 0.05 (우연 가능성) (x1) |
| `value_area` | trades 12 < 15 (x1), mc_p_value 0.448 > 0.05 (우연 가능성) (x1), sharpe 0.36 < 1.0 (x1) |
| `wick_reversal` | no trades generated (x4) |
| `elder_impulse` | sharpe 0.93 < 1.0 (x1), profit_factor 1.16 < 1.5 (x1), mc_p_value 0.472 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe -1.64 < 1.0 (x1), profit_factor 0.62 < 1.5 (x1), trades 12 < 15 (x1) |
| `price_cluster` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.444 > 0.05 (우연 가능성) (x1), sharpe 0.74 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 4 |
| profit_factor 1.48 < 1.5 | 3 |
| profit_factor 1.39 < 1.5 | 3 |
| profit_factor 1.32 < 1.5 | 3 |
| mc_p_value 0.428 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.440 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.47 < 1.5 | 2 |
| mc_p_value 0.212 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.320 > 0.05 (우연 가능성) | 2 |
| max_drawdown 22.3% > 20% | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +21.86% -> $12,186
- **Top 5 균등배분**: +61.06% -> $16,106


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-29T00:29:43.062777Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=777840613, block=24)_
_Data Range: 0 ~ 8639 (8640봉)_
_Walk-Forward: 4개 윈도우 (train=5040h, test=1440h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## ML 모델 건강 상태 (ADWIN)

| 항목 | 값 |
|------|-----|
| EWMA Accuracy | 1.0000 |
| EWMA Trend | N/A (unknown) |
| EWMA Samples | 0 |
| Drift Detected | YES |
| Output Drift | NO |
| Retrain Recommended (EWMA) | NO |
| Retrain Recommended (ADWIN) | YES |
| Retrain Count | 3 |
| Feature Drift | 0/3 features drifted |

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | 9.55% |
| 최고 수익률 | 39.20% (supertrend_multi) |
| 최저 수익률 | -10.84% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +39.20% | 3.84 | 45.5% | 1.51 | 120 | 11.5% | 0/4 | FAIL |
| 2 | `momentum_quality` | +35.91% | 3.63 | 45.3% | 1.47 | 119 | 9.9% | 0/4 | FAIL |
| 3 | `price_action_momentum` | +28.78% | 2.46 | 40.8% | 1.27 | 156 | 16.0% | 0/4 | FAIL |
| 4 | `lob_maker` | +23.99% | 1.93 | 40.6% | 1.22 | 131 | 20.2% | 0/4 | FAIL |
| 5 | `engulfing_zone` | +19.57% | 3.01 | 51.5% | 1.86 | 30 | 6.9% | 0/4 | FAIL |
| 6 | `narrow_range` | +17.03% | 2.14 | 42.1% | 1.32 | 88 | 10.4% | 0/4 | FAIL |
| 7 | `acceleration_band` | +12.25% | 1.35 | 41.1% | 1.19 | 99 | 17.3% | 0/4 | FAIL |
| 8 | `volatility_cluster` | +11.22% | 1.77 | 42.1% | 1.31 | 69 | 9.1% | 0/4 | FAIL |
| 9 | `positional_scaling` | +10.86% | 1.98 | 43.9% | 1.75 | 30 | 6.0% | 0/4 | FAIL |
| 10 | `roc_ma_cross` | +8.82% | 1.82 | 45.1% | 1.50 | 36 | 8.3% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 79.8 | p100 | 3.84 | 0.67 | 1.51 | 120 | 11.5% | 0/4 | FAIL |
| 2 | `momentum_quality` | 79.1 | p95 | 3.63 | 0.63 | 1.47 | 119 | 9.9% | 0/4 | FAIL |
| 3 | `engulfing_zone` | 72.5 | p90 | 3.01 | 1.00 | 1.86 | 30 | 6.9% | 0/4 | FAIL |
| 4 | `price_action_momentum` | 68.0 | p85 | 2.46 | 0.84 | 1.27 | 156 | 16.0% | 0/4 | FAIL |
| 5 | `narrow_range` | 64.6 | p80 | 2.14 | 0.64 | 1.32 | 88 | 10.4% | 0/4 | FAIL |
| 6 | `volatility_cluster` | 60.9 | p76 | 1.77 | 0.69 | 1.31 | 69 | 9.1% | 0/4 | FAIL |
| 7 | `lob_maker` | 58.0 | p71 | 1.93 | 1.05 | 1.22 | 131 | 20.2% | 0/4 | FAIL |
| 8 | `positional_scaling` | 57.3 | p66 | 1.98 | 2.51 | 1.75 | 30 | 6.0% | 0/4 | FAIL |
| 9 | `roc_ma_cross` | 56.9 | p61 | 1.82 | 1.54 | 1.50 | 36 | 8.3% | 0/4 | FAIL |
| 10 | `volume_breakout` | 52.9 | p57 | 1.09 | 0.77 | 1.16 | 96 | 15.5% | 0/4 | FAIL |
| 11 | `acceleration_band` | 52.7 | p52 | 1.35 | 1.09 | 1.19 | 99 | 17.3% | 0/4 | FAIL |
| 12 | `dema_cross` | 51.5 | p47 | 0.69 | 1.06 | 1.40 | 12 | 3.9% | 0/4 | FAIL |
| 13 | `order_flow_imbalance_v2` | 46.5 | p42 | 0.95 | 1.32 | 1.14 | 86 | 18.0% | 0/4 | FAIL |
| 14 | `cmf` | 45.2 | p38 | 0.24 | 1.28 | 1.05 | 118 | 16.6% | 0/4 | FAIL |
| 15 | `elder_impulse` | 43.5 | p33 | 0.16 | 0.73 | 1.06 | 61 | 14.4% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +39.20% | 3.84 | 1.51 | 120 | 0/4 | FAIL |
| `momentum_quality` | +35.91% | 3.63 | 1.47 | 119 | 0/4 | FAIL |
| `price_action_momentum` | +28.78% | 2.46 | 1.27 | 156 | 0/4 | FAIL |
| `lob_maker` | +23.99% | 1.93 | 1.22 | 131 | 0/4 | FAIL |
| `engulfing_zone` | +19.57% | 3.01 | 1.86 | 30 | 0/4 | FAIL |
| `narrow_range` | +17.03% | 2.14 | 1.32 | 88 | 0/4 | FAIL |
| `acceleration_band` | +12.25% | 1.35 | 1.19 | 99 | 0/4 | FAIL |
| `volatility_cluster` | +11.22% | 1.77 | 1.31 | 69 | 0/4 | FAIL |
| `positional_scaling` | +10.86% | 1.98 | 1.75 | 30 | 0/4 | FAIL |
| `roc_ma_cross` | +8.82% | 1.82 | 1.50 | 36 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +8.70% | 0.95 | 1.14 | 86 | 0/4 | FAIL |
| `volume_breakout` | +8.64% | 1.09 | 1.16 | 96 | 0/4 | FAIL |
| `price_cluster` | +2.05% | 0.36 | 1.16 | 38 | 0/4 | FAIL |
| `dema_cross` | +1.41% | 0.69 | 1.40 | 12 | 0/4 | FAIL |
| `cmf` | +1.21% | 0.24 | 1.05 | 118 | 0/4 | FAIL |
| `relative_volume` | +1.07% | 0.26 | 1.09 | 59 | 0/4 | FAIL |
| `elder_impulse` | +0.20% | 0.16 | 1.06 | 61 | 0/4 | FAIL |
| `value_area` | +0.11% | 0.04 | 1.09 | 16 | 0/4 | FAIL |
| `wick_reversal` | -0.24% | -0.48 | 0.53 | 2 | 0/4 | FAIL |
| `linear_channel_rev` | -3.01% | -0.82 | 0.94 | 32 | 0/4 | FAIL |
| `htf_ema` | -6.86% | -0.84 | 0.93 | 72 | 0/4 | FAIL |
| `frama` | -10.84% | -1.23 | 0.90 | 88 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.394 > 0.05 (우연 가능성) (x1), mc_p_value 0.332 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.348 > 0.05 (우연 가능성) (x1), profit_factor 1.48 < 1.5 (x1) |
| `price_action_momentum` | profit_factor 1.33 < 1.5 (x1), mc_p_value 0.382 > 0.05 (우연 가능성) (x1), profit_factor 1.39 < 1.5 (x1) |
| `lob_maker` | mc_p_value 0.388 > 0.05 (우연 가능성) (x2), max_drawdown 20.0% > 20% (x2), profit_factor 1.32 < 1.5 (x1) |
| `engulfing_zone` | mc_p_value 0.432 > 0.05 (우연 가능성) (x1), profit_factor 1.37 < 1.5 (x1), mc_p_value 0.424 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.25 < 1.5 (x2), profit_factor 1.28 < 1.5 (x1), mc_p_value 0.412 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | sharpe -0.38 < 1.0 (x1), max_drawdown 24.1% > 20% (x1), profit_factor 0.99 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.20 < 1.5 (x1), mc_p_value 0.484 > 0.05 (우연 가능성) (x1), profit_factor 1.31 < 1.5 (x1) |
| `positional_scaling` | sharpe -1.92 < 1.0 (x1), profit_factor 0.70 < 1.5 (x1), mc_p_value 0.528 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | mc_p_value 0.378 > 0.05 (우연 가능성) (x1), mc_p_value 0.408 > 0.05 (우연 가능성) (x1), profit_factor 1.29 < 1.5 (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.41 < 1.5 (x1), mc_p_value 0.380 > 0.05 (우연 가능성) (x1), sharpe -0.03 < 1.0 (x1) |
| `volume_breakout` | profit_factor 1.19 < 1.5 (x1), mc_p_value 0.416 > 0.05 (우연 가능성) (x1), sharpe 0.10 < 1.0 (x1) |
| `price_cluster` | sharpe -1.24 < 1.0 (x1), profit_factor 0.82 < 1.5 (x1), mc_p_value 0.528 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | profit_factor 1.42 < 1.5 (x1), trades 12 < 15 (x1), trades 6 < 15 (x1) |
| `cmf` | sharpe -1.95 < 1.0 (x1), max_drawdown 30.0% > 20% (x1), profit_factor 0.83 < 1.5 (x1) |
| `relative_volume` | sharpe -0.06 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.474 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | profit_factor 1.07 < 1.5 (x2), profit_factor 1.19 < 1.5 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -1.62 < 1.0 (x1), profit_factor 0.68 < 1.5 (x1), mc_p_value 0.536 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | sharpe 0.06 < 1.0 (x2), profit_factor 1.07 < 1.5 (x2), trades 3 < 15 (x2) |
| `linear_channel_rev` | sharpe -2.63 < 1.0 (x1), profit_factor 0.62 < 1.5 (x1), mc_p_value 0.570 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.07 < 1.5 | 5 |
| mc_p_value 0.474 > 0.05 (우연 가능성) | 4 |
| profit_factor 1.20 < 1.5 | 3 |
| profit_factor 1.04 < 1.5 | 3 |
| profit_factor 1.25 < 1.5 | 3 |
| profit_factor 1.19 < 1.5 | 3 |
| mc_p_value 0.480 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.486 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.570 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.34 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +9.55% -> $10,955
- **Top 5 균등배분**: +29.49% -> $12,949
