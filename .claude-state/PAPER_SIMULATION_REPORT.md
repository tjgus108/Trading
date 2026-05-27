# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-27T15:22:08.994044Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-27T15:24:30.758302Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1544756475, block=36)_
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
| 평균 수익률 | 29.85% |
| 최고 수익률 | 122.48% (price_action_momentum) |
| 최저 수익률 | -22.92% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +122.48% | 6.59 | 49.6% | 1.81 | 163 | 10.3% | 0/4 | FAIL |
| 2 | `cmf` | +93.54% | 5.56 | 49.5% | 1.78 | 118 | 11.6% | 0/4 | FAIL |
| 3 | `momentum_quality` | +85.53% | 6.63 | 52.5% | 1.97 | 123 | 7.2% | 0/4 | FAIL |
| 4 | `lob_maker` | +56.93% | 3.98 | 46.6% | 1.51 | 116 | 13.2% | 0/4 | FAIL |
| 5 | `volume_breakout` | +55.92% | 4.78 | 50.2% | 1.77 | 92 | 10.2% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | +54.23% | 4.36 | 49.7% | 1.69 | 84 | 10.9% | 0/4 | FAIL |
| 7 | `supertrend_multi` | +42.38% | 3.97 | 45.0% | 1.52 | 124 | 11.5% | 0/4 | FAIL |
| 8 | `htf_ema` | +41.91% | 4.23 | 50.2% | 1.85 | 66 | 6.9% | 0/4 | FAIL |
| 9 | `volatility_cluster` | +41.46% | 5.05 | 51.4% | 1.95 | 74 | 7.5% | 0/4 | FAIL |
| 10 | `narrow_range` | +34.88% | 3.83 | 48.0% | 1.65 | 88 | 8.9% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 64.9 | p100 | 6.63 | 0.76 | 1.97 | 123 | 7.2% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 61.4 | p95 | 6.59 | 1.64 | 1.81 | 163 | 10.3% | 0/4 | FAIL |
| 3 | `wick_reversal` | 58.0 | p90 | 0.98 | 0.98 | 500.00 | 0 | 0.0% | 0/4 | FAIL |
| 4 | `cmf` | 57.3 | p85 | 5.56 | 0.98 | 1.78 | 118 | 11.6% | 0/4 | FAIL |
| 5 | `lob_maker` | 55.1 | p80 | 3.98 | 0.34 | 1.51 | 116 | 13.2% | 0/4 | FAIL |
| 6 | `volume_breakout` | 54.9 | p76 | 4.78 | 0.69 | 1.77 | 92 | 10.2% | 0/4 | FAIL |
| 7 | `volatility_cluster` | 54.8 | p71 | 5.05 | 0.81 | 1.95 | 74 | 7.5% | 0/4 | FAIL |
| 8 | `supertrend_multi` | 51.6 | p66 | 3.97 | 1.17 | 1.52 | 124 | 11.5% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | 51.4 | p61 | 4.36 | 0.87 | 1.69 | 84 | 10.9% | 0/4 | FAIL |
| 10 | `htf_ema` | 46.9 | p57 | 4.23 | 1.62 | 1.85 | 66 | 6.9% | 0/4 | FAIL |
| 11 | `roc_ma_cross` | 45.2 | p52 | 2.67 | 0.71 | 1.73 | 33 | 5.3% | 0/4 | FAIL |
| 12 | `narrow_range` | 45.1 | p47 | 3.83 | 1.84 | 1.65 | 88 | 8.9% | 0/4 | FAIL |
| 13 | `value_area` | 43.4 | p42 | 2.07 | 0.59 | 1.83 | 16 | 3.7% | 0/4 | FAIL |
| 14 | `acceleration_band` | 40.4 | p38 | 2.32 | 1.64 | 1.35 | 93 | 11.8% | 0/4 | FAIL |
| 15 | `relative_volume` | 38.9 | p33 | 0.40 | 0.60 | 1.10 | 54 | 8.5% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +122.48% | 6.59 | 1.81 | 163 | 0/4 | FAIL |
| `cmf` | +93.54% | 5.56 | 1.78 | 118 | 0/4 | FAIL |
| `momentum_quality` | +85.53% | 6.63 | 1.97 | 123 | 0/4 | FAIL |
| `lob_maker` | +56.93% | 3.98 | 1.51 | 116 | 0/4 | FAIL |
| `volume_breakout` | +55.92% | 4.78 | 1.77 | 92 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +54.23% | 4.36 | 1.69 | 84 | 0/4 | FAIL |
| `supertrend_multi` | +42.38% | 3.97 | 1.52 | 124 | 0/4 | FAIL |
| `htf_ema` | +41.91% | 4.23 | 1.85 | 66 | 0/4 | FAIL |
| `volatility_cluster` | +41.46% | 5.05 | 1.95 | 74 | 0/4 | FAIL |
| `narrow_range` | +34.88% | 3.83 | 1.65 | 88 | 0/4 | FAIL |
| `acceleration_band` | +23.85% | 2.32 | 1.35 | 93 | 0/4 | FAIL |
| `roc_ma_cross` | +12.47% | 2.67 | 1.73 | 33 | 0/4 | FAIL |
| `linear_channel_rev` | +10.11% | 2.09 | 1.59 | 36 | 0/4 | FAIL |
| `value_area` | +6.31% | 2.07 | 1.83 | 16 | 0/4 | FAIL |
| `positional_scaling` | +5.82% | 1.42 | 1.49 | 25 | 0/4 | FAIL |
| `relative_volume` | +1.55% | 0.40 | 1.10 | 54 | 0/4 | FAIL |
| `wick_reversal` | +0.92% | 0.98 | 500.00 | 0 | 0/4 | FAIL |
| `dema_cross` | +0.69% | 0.16 | 1.26 | 16 | 0/4 | FAIL |
| `engulfing_zone` | -2.48% | -0.71 | 0.90 | 20 | 0/4 | FAIL |
| `price_cluster` | -2.60% | -0.41 | 0.97 | 32 | 0/4 | FAIL |
| `elder_impulse` | -6.29% | -1.02 | 0.88 | 49 | 0/4 | FAIL |
| `frama` | -22.92% | -2.76 | 0.76 | 100 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.124 > 0.05 (우연 가능성) (x1), mc_p_value 0.182 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1) |
| `cmf` | mc_p_value 0.210 > 0.05 (우연 가능성) (x1), mc_p_value 0.234 > 0.05 (우연 가능성) (x1), mc_p_value 0.316 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.168 > 0.05 (우연 가능성) (x1), mc_p_value 0.214 > 0.05 (우연 가능성) (x1), mc_p_value 0.264 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.320 > 0.05 (우연 가능성) (x1), profit_factor 1.44 < 1.5 (x1) |
| `volume_breakout` | mc_p_value 0.346 > 0.05 (우연 가능성) (x1), mc_p_value 0.374 > 0.05 (우연 가능성) (x1), mc_p_value 0.260 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.336 > 0.05 (우연 가능성) (x1), profit_factor 1.46 < 1.5 (x1), mc_p_value 0.378 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.386 > 0.05 (우연 가능성) (x1), mc_p_value 0.328 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | mc_p_value 0.324 > 0.05 (우연 가능성) (x1), mc_p_value 0.312 > 0.05 (우연 가능성) (x1), mc_p_value 0.354 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | mc_p_value 0.272 > 0.05 (우연 가능성) (x1), mc_p_value 0.296 > 0.05 (우연 가능성) (x1), mc_p_value 0.420 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.29 < 1.5 (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1), mc_p_value 0.268 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | mc_p_value 0.330 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1), mc_p_value 0.412 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.478 > 0.05 (우연 가능성) (x1), mc_p_value 0.418 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | mc_p_value 0.380 > 0.05 (우연 가능성) (x1), mc_p_value 0.388 > 0.05 (우연 가능성) (x1), sharpe 0.41 < 1.0 (x1) |
| `value_area` | mc_p_value 0.466 > 0.05 (우연 가능성) (x1), trades 13 < 15 (x1), profit_factor 1.41 < 1.5 (x1) |
| `positional_scaling` | profit_factor 1.36 < 1.5 (x1), mc_p_value 0.480 > 0.05 (우연 가능성) (x1), sharpe -0.21 < 1.0 (x1) |
| `relative_volume` | mc_p_value 0.456 > 0.05 (우연 가능성) (x2), profit_factor 1.08 < 1.5 (x2), profit_factor 1.25 < 1.5 (x1) |
| `wick_reversal` | no trades generated (x2), trades 1 < 15 (x2) |
| `dema_cross` | trades 14 < 15 (x1), sharpe 0.77 < 1.0 (x1), profit_factor 1.22 < 1.5 (x1) |
| `engulfing_zone` | sharpe -2.30 < 1.0 (x1), profit_factor 0.57 < 1.5 (x1), mc_p_value 0.512 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | mc_p_value 0.520 > 0.05 (우연 가능성) (x2), sharpe -1.36 < 1.0 (x1), profit_factor 0.78 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.34 < 1.5 | 4 |
| profit_factor 1.47 < 1.5 | 2 |
| mc_p_value 0.266 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.356 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.268 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.36 < 1.5 | 2 |
| mc_p_value 0.412 > 0.05 (우연 가능성) | 2 |
| sharpe 0.32 < 1.0 | 2 |
| mc_p_value 0.424 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.476 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +29.85% -> $12,985
- **Top 5 균등배분**: +82.88% -> $18,288


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-27T15:26:51.880261Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=609512463, block=36)_
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
| 평균 수익률 | 6.73% |
| 최고 수익률 | 42.04% (momentum_quality) |
| 최저 수익률 | -7.36% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +42.04% | 3.68 | 45.2% | 1.50 | 118 | 11.4% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +30.10% | 2.53 | 43.0% | 1.28 | 153 | 17.5% | 0/4 | FAIL |
| 3 | `htf_ema` | +24.70% | 2.79 | 46.5% | 1.51 | 67 | 8.8% | 0/4 | FAIL |
| 4 | `supertrend_multi` | +21.99% | 2.65 | 43.0% | 1.40 | 89 | 9.1% | 0/4 | FAIL |
| 5 | `acceleration_band` | +11.73% | 1.35 | 41.1% | 1.25 | 92 | 14.6% | 0/4 | FAIL |
| 6 | `elder_impulse` | +11.19% | 1.61 | 41.9% | 1.36 | 56 | 9.1% | 0/4 | FAIL |
| 7 | `positional_scaling` | +5.53% | 1.27 | 44.1% | 1.37 | 28 | 6.6% | 0/4 | FAIL |
| 8 | `narrow_range` | +5.51% | 0.81 | 40.6% | 1.14 | 100 | 12.6% | 0/4 | FAIL |
| 9 | `cmf` | +5.26% | 0.49 | 38.7% | 1.08 | 124 | 23.1% | 0/4 | FAIL |
| 10 | `roc_ma_cross` | +4.63% | 1.09 | 42.7% | 1.31 | 37 | 8.5% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 77.7 | p100 | 3.68 | 2.26 | 1.50 | 118 | 11.4% | 0/4 | FAIL |
| 2 | `htf_ema` | 73.2 | p95 | 2.79 | 1.20 | 1.51 | 67 | 8.8% | 0/4 | FAIL |
| 3 | `supertrend_multi` | 72.0 | p90 | 2.65 | 1.52 | 1.40 | 89 | 9.1% | 0/4 | FAIL |
| 4 | `price_action_momentum` | 71.9 | p85 | 2.53 | 1.16 | 1.28 | 153 | 17.5% | 0/4 | FAIL |
| 5 | `elder_impulse` | 63.0 | p80 | 1.61 | 1.54 | 1.36 | 56 | 9.1% | 0/4 | FAIL |
| 6 | `positional_scaling` | 61.9 | p76 | 1.27 | 1.03 | 1.37 | 28 | 6.6% | 0/4 | FAIL |
| 7 | `acceleration_band` | 60.0 | p71 | 1.35 | 1.71 | 1.25 | 92 | 14.6% | 0/4 | FAIL |
| 8 | `narrow_range` | 59.2 | p66 | 0.81 | 1.26 | 1.14 | 100 | 12.6% | 0/4 | FAIL |
| 9 | `roc_ma_cross` | 58.9 | p61 | 1.09 | 1.34 | 1.31 | 37 | 8.5% | 0/4 | FAIL |
| 10 | `linear_channel_rev` | 58.4 | p57 | 0.60 | 0.48 | 1.16 | 29 | 5.2% | 0/4 | FAIL |
| 11 | `lob_maker` | 53.6 | p52 | 0.19 | 1.34 | 1.05 | 134 | 19.8% | 0/4 | FAIL |
| 12 | `cmf` | 52.0 | p47 | 0.49 | 1.46 | 1.08 | 124 | 23.1% | 0/4 | FAIL |
| 13 | `relative_volume` | 51.5 | p42 | 0.31 | 2.33 | 1.20 | 57 | 10.4% | 0/4 | FAIL |
| 14 | `price_cluster` | 51.3 | p38 | 0.47 | 0.99 | 1.16 | 38 | 14.4% | 0/4 | FAIL |
| 15 | `engulfing_zone` | 49.3 | p33 | -0.20 | 0.74 | 0.98 | 19 | 6.7% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +42.04% | 3.68 | 1.50 | 118 | 0/4 | FAIL |
| `price_action_momentum` | +30.10% | 2.53 | 1.28 | 153 | 0/4 | FAIL |
| `htf_ema` | +24.70% | 2.79 | 1.51 | 67 | 0/4 | FAIL |
| `supertrend_multi` | +21.99% | 2.65 | 1.40 | 89 | 0/4 | FAIL |
| `acceleration_band` | +11.73% | 1.35 | 1.25 | 92 | 0/4 | FAIL |
| `elder_impulse` | +11.19% | 1.61 | 1.36 | 56 | 0/4 | FAIL |
| `positional_scaling` | +5.53% | 1.27 | 1.37 | 28 | 0/4 | FAIL |
| `narrow_range` | +5.51% | 0.81 | 1.14 | 100 | 0/4 | FAIL |
| `cmf` | +5.26% | 0.49 | 1.08 | 124 | 0/4 | FAIL |
| `roc_ma_cross` | +4.63% | 1.09 | 1.31 | 37 | 0/4 | FAIL |
| `relative_volume` | +2.34% | 0.31 | 1.20 | 57 | 0/4 | FAIL |
| `linear_channel_rev` | +2.07% | 0.60 | 1.16 | 29 | 0/4 | FAIL |
| `price_cluster` | +1.96% | 0.47 | 1.16 | 38 | 0/4 | FAIL |
| `lob_maker` | +1.21% | 0.19 | 1.05 | 134 | 0/4 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `volatility_cluster` | -0.42% | -0.36 | 1.09 | 82 | 0/4 | FAIL |
| `engulfing_zone` | -0.93% | -0.20 | 0.98 | 19 | 0/4 | FAIL |
| `dema_cross` | -1.13% | -0.82 | 1.36 | 11 | 0/4 | FAIL |
| `volume_breakout` | -1.48% | -0.10 | 1.04 | 100 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | -4.68% | -0.55 | 0.99 | 90 | 0/4 | FAIL |
| `value_area` | -6.09% | -2.39 | 0.56 | 17 | 0/4 | FAIL |
| `frama` | -7.36% | -0.79 | 0.94 | 80 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | profit_factor 1.47 < 1.5 (x1), mc_p_value 0.356 > 0.05 (우연 가능성) (x1), sharpe 0.18 < 1.0 (x1) |
| `price_action_momentum` | max_drawdown 21.8% > 20% (x1), profit_factor 1.25 < 1.5 (x1), mc_p_value 0.412 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | mc_p_value 0.390 > 0.05 (우연 가능성) (x1), mc_p_value 0.382 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1) |
| `supertrend_multi` | mc_p_value 0.372 > 0.05 (우연 가능성) (x1), sharpe 0.61 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1) |
| `acceleration_band` | sharpe 0.54 < 1.0 (x1), profit_factor 1.09 < 1.5 (x1), mc_p_value 0.508 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | sharpe 0.50 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), mc_p_value 0.528 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | mc_p_value 0.458 > 0.05 (우연 가능성) (x1), profit_factor 1.28 < 1.5 (x1), mc_p_value 0.462 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.27 < 1.5 (x1), mc_p_value 0.390 > 0.05 (우연 가능성) (x1), sharpe 0.01 < 1.0 (x1) |
| `cmf` | profit_factor 1.13 < 1.5 (x1), mc_p_value 0.434 > 0.05 (우연 가능성) (x1), profit_factor 1.23 < 1.5 (x1) |
| `roc_ma_cross` | mc_p_value 0.404 > 0.05 (우연 가능성) (x1), sharpe -0.15 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1) |
| `relative_volume` | sharpe -0.74 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1), mc_p_value 0.500 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe 0.87 < 1.0 (x1), profit_factor 1.21 < 1.5 (x1), mc_p_value 0.450 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -0.13 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.498 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 0.96 < 1.5 (x2), sharpe -0.73 < 1.0 (x1), mc_p_value 0.564 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x4) |
| `volatility_cluster` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.350 > 0.05 (우연 가능성) (x1), sharpe -4.26 < 1.0 (x1) |
| `engulfing_zone` | sharpe 0.11 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.522 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe -1.67 < 1.0 (x1), profit_factor 0.61 < 1.5 (x1), trades 12 < 15 (x1) |
| `volume_breakout` | profit_factor 0.87 < 1.5 (x2), sharpe 0.75 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe -0.93 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.538 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.05 < 1.5 | 4 |
| profit_factor 1.10 < 1.5 | 4 |
| profit_factor 0.87 < 1.5 | 4 |
| no trades generated | 4 |
| mc_p_value 0.390 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.490 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.00 < 1.5 | 3 |
| profit_factor 1.47 < 1.5 | 2 |
| mc_p_value 0.498 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.412 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +6.73% -> $10,673
- **Top 5 균등배분**: +26.11% -> $12,611


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-27T15:29:16.957021Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=882608832, block=36)_
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
| 평균 수익률 | 22.01% |
| 최고 수익률 | 62.23% (price_action_momentum) |
| 최저 수익률 | -5.88% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +62.23% | 4.25 | 46.3% | 1.47 | 151 | 12.0% | 0/4 | FAIL |
| 2 | `momentum_quality` | +51.80% | 4.79 | 47.6% | 1.65 | 112 | 8.0% | 0/4 | FAIL |
| 3 | `cmf` | +51.70% | 3.00 | 43.7% | 1.35 | 126 | 15.6% | 0/4 | FAIL |
| 4 | `acceleration_band` | +44.78% | 3.53 | 46.0% | 1.53 | 105 | 10.0% | 0/4 | FAIL |
| 5 | `supertrend_multi` | +44.12% | 4.36 | 47.4% | 1.63 | 96 | 7.9% | 0/4 | FAIL |
| 6 | `volatility_cluster` | +38.94% | 4.74 | 50.8% | 1.86 | 74 | 5.3% | 0/4 | FAIL |
| 7 | `volume_breakout` | +33.02% | 3.05 | 44.7% | 1.42 | 100 | 7.9% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | +29.93% | 2.64 | 43.7% | 1.37 | 93 | 10.2% | 0/4 | FAIL |
| 9 | `lob_maker` | +24.47% | 1.94 | 41.3% | 1.22 | 130 | 12.9% | 0/4 | FAIL |
| 10 | `narrow_range` | +22.77% | 2.52 | 45.1% | 1.45 | 87 | 12.0% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 64.8 | p100 | 4.79 | 0.76 | 1.65 | 112 | 8.0% | 0/4 | FAIL |
| 2 | `wick_reversal` | 63.6 | p95 | 1.49 | 0.86 | 749.99 | 1 | 0.0% | 0/4 | FAIL |
| 3 | `volatility_cluster` | 61.9 | p90 | 4.74 | 0.98 | 1.86 | 74 | 5.3% | 0/4 | FAIL |
| 4 | `supertrend_multi` | 58.5 | p85 | 4.36 | 1.34 | 1.63 | 96 | 7.9% | 0/4 | FAIL |
| 5 | `price_action_momentum` | 56.7 | p80 | 4.25 | 2.04 | 1.47 | 151 | 12.0% | 0/4 | FAIL |
| 6 | `roc_ma_cross` | 55.3 | p76 | 3.72 | 0.82 | 1.99 | 40 | 4.1% | 0/4 | FAIL |
| 7 | `volume_breakout` | 54.2 | p71 | 3.05 | 0.99 | 1.42 | 100 | 7.9% | 0/4 | FAIL |
| 8 | `acceleration_band` | 48.5 | p61 | 3.53 | 2.43 | 1.53 | 105 | 10.0% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | 48.5 | p66 | 2.64 | 1.24 | 1.37 | 93 | 10.2% | 0/4 | FAIL |
| 10 | `lob_maker` | 48.0 | p57 | 1.94 | 0.96 | 1.22 | 130 | 12.9% | 0/4 | FAIL |
| 11 | `value_area` | 45.3 | p52 | 2.60 | 1.32 | 2.23 | 17 | 3.9% | 0/4 | FAIL |
| 12 | `relative_volume` | 44.5 | p47 | 1.50 | 0.77 | 1.26 | 62 | 7.2% | 0/4 | FAIL |
| 13 | `htf_ema` | 44.3 | p42 | 2.21 | 1.38 | 1.38 | 70 | 9.2% | 0/4 | FAIL |
| 14 | `cmf` | 43.3 | p38 | 3.00 | 2.48 | 1.35 | 126 | 15.6% | 0/4 | FAIL |
| 15 | `positional_scaling` | 42.8 | p33 | 1.76 | 0.92 | 1.47 | 33 | 6.4% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +62.23% | 4.25 | 1.47 | 151 | 0/4 | FAIL |
| `momentum_quality` | +51.80% | 4.79 | 1.65 | 112 | 0/4 | FAIL |
| `cmf` | +51.70% | 3.00 | 1.35 | 126 | 0/4 | FAIL |
| `acceleration_band` | +44.78% | 3.53 | 1.53 | 105 | 0/4 | FAIL |
| `supertrend_multi` | +44.12% | 4.36 | 1.63 | 96 | 0/4 | FAIL |
| `volatility_cluster` | +38.94% | 4.74 | 1.86 | 74 | 0/4 | FAIL |
| `volume_breakout` | +33.02% | 3.05 | 1.42 | 100 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +29.93% | 2.64 | 1.37 | 93 | 0/4 | FAIL |
| `lob_maker` | +24.47% | 1.94 | 1.22 | 130 | 0/4 | FAIL |
| `narrow_range` | +22.77% | 2.52 | 1.45 | 87 | 0/4 | FAIL |
| `htf_ema` | +19.80% | 2.21 | 1.38 | 70 | 0/4 | FAIL |
| `roc_ma_cross` | +19.79% | 3.72 | 1.99 | 40 | 0/4 | FAIL |
| `price_cluster` | +10.17% | 1.52 | 1.41 | 39 | 0/4 | FAIL |
| `relative_volume` | +9.02% | 1.50 | 1.26 | 62 | 0/4 | FAIL |
| `value_area` | +8.91% | 2.60 | 2.23 | 17 | 0/4 | FAIL |
| `positional_scaling` | +8.18% | 1.76 | 1.47 | 33 | 0/4 | FAIL |
| `elder_impulse` | +5.29% | 0.96 | 1.21 | 52 | 0/4 | FAIL |
| `dema_cross` | +5.25% | 1.67 | 2.39 | 14 | 0/4 | FAIL |
| `wick_reversal` | +1.90% | 1.49 | 749.99 | 1 | 0/4 | FAIL |
| `linear_channel_rev` | -0.18% | -0.30 | 1.14 | 32 | 0/4 | FAIL |
| `frama` | -1.67% | -0.20 | 1.02 | 85 | 0/4 | FAIL |
| `engulfing_zone` | -5.88% | -1.43 | 0.76 | 20 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.160 > 0.05 (우연 가능성) (x1), mc_p_value 0.256 > 0.05 (우연 가능성) (x1), profit_factor 1.23 < 1.5 (x1) |
| `momentum_quality` | mc_p_value 0.224 > 0.05 (우연 가능성) (x1), mc_p_value 0.280 > 0.05 (우연 가능성) (x1), profit_factor 1.49 < 1.5 (x1) |
| `cmf` | mc_p_value 0.198 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1), mc_p_value 0.364 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | mc_p_value 0.460 > 0.05 (우연 가능성) (x2), mc_p_value 0.224 > 0.05 (우연 가능성) (x1), mc_p_value 0.300 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | mc_p_value 0.242 > 0.05 (우연 가능성) (x1), mc_p_value 0.278 > 0.05 (우연 가능성) (x1), mc_p_value 0.336 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | mc_p_value 0.342 > 0.05 (우연 가능성) (x1), mc_p_value 0.274 > 0.05 (우연 가능성) (x1), mc_p_value 0.358 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | mc_p_value 0.334 > 0.05 (우연 가능성) (x1), profit_factor 1.46 < 1.5 (x1), mc_p_value 0.336 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.324 > 0.05 (우연 가능성) (x1), profit_factor 1.37 < 1.5 (x1), mc_p_value 0.394 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.400 > 0.05 (우연 가능성) (x1), profit_factor 1.30 < 1.5 (x1) |
| `narrow_range` | mc_p_value 0.312 > 0.05 (우연 가능성) (x1), mc_p_value 0.330 > 0.05 (우연 가능성) (x1), profit_factor 1.44 < 1.5 (x1) |
| `htf_ema` | profit_factor 1.34 < 1.5 (x2), mc_p_value 0.370 > 0.05 (우연 가능성) (x1), mc_p_value 0.422 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | mc_p_value 0.392 > 0.05 (우연 가능성) (x1), mc_p_value 0.398 > 0.05 (우연 가능성) (x1), mc_p_value 0.402 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | mc_p_value 0.434 > 0.05 (우연 가능성) (x2), profit_factor 1.26 < 1.5 (x1), mc_p_value 0.476 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.438 > 0.05 (우연 가능성) (x1), profit_factor 1.31 < 1.5 (x1) |
| `value_area` | sharpe 0.87 < 1.0 (x1), profit_factor 1.32 < 1.5 (x1), trades 14 < 15 (x1) |
| `positional_scaling` | mc_p_value 0.444 > 0.05 (우연 가능성) (x1), sharpe 0.81 < 1.0 (x1), profit_factor 1.20 < 1.5 (x1) |
| `elder_impulse` | mc_p_value 0.442 > 0.05 (우연 가능성) (x1), profit_factor 1.32 < 1.5 (x1), mc_p_value 0.434 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe -1.16 < 1.0 (x1), profit_factor 0.73 < 1.5 (x1), trades 14 < 15 (x1) |
| `wick_reversal` | trades 1 < 15 (x3), no trades generated (x1) |
| `linear_channel_rev` | mc_p_value 0.390 > 0.05 (우연 가능성) (x1), sharpe -0.28 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.336 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.46 < 1.5 | 3 |
| mc_p_value 0.434 > 0.05 (우연 가능성) | 3 |
| trades 1 < 15 | 3 |
| mc_p_value 0.224 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.324 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.33 < 1.5 | 2 |
| mc_p_value 0.460 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.18 < 1.5 | 2 |
| sharpe 0.95 < 1.0 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +22.01% -> $12,201
- **Top 5 균등배분**: +50.93% -> $15,093
