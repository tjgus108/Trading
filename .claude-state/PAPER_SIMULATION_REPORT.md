# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-29T10:13:20.356377Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-29T10:15:50.202360Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1080475408, block=24)_
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
| 평균 수익률 | 10.55% |
| 최고 수익률 | 83.20% (supertrend_multi) |
| 최저 수익률 | -21.75% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +83.20% | 6.06 | 50.8% | 1.80 | 133 | 10.9% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +58.38% | 3.37 | 44.0% | 1.42 | 153 | 20.8% | 0/4 | FAIL |
| 3 | `momentum_quality` | +53.88% | 4.49 | 47.3% | 1.62 | 118 | 10.3% | 0/4 | FAIL |
| 4 | `cmf` | +19.46% | 1.04 | 40.0% | 1.23 | 114 | 24.9% | 0/4 | FAIL |
| 5 | `htf_ema` | +14.09% | 1.58 | 42.0% | 1.31 | 66 | 18.6% | 0/4 | FAIL |
| 6 | `acceleration_band` | +12.07% | 1.18 | 39.1% | 1.20 | 94 | 23.2% | 0/4 | FAIL |
| 7 | `volume_breakout` | +10.16% | 1.22 | 39.7% | 1.23 | 82 | 17.2% | 0/4 | FAIL |
| 8 | `volatility_cluster` | +9.23% | 0.90 | 40.0% | 1.25 | 78 | 16.7% | 0/4 | FAIL |
| 9 | `roc_ma_cross` | +6.60% | 1.46 | 44.2% | 1.36 | 36 | 9.4% | 0/4 | FAIL |
| 10 | `order_flow_imbalance_v2` | +5.70% | 0.68 | 40.0% | 1.15 | 79 | 18.1% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 63.1 | p100 | 6.06 | 1.93 | 1.80 | 133 | 10.9% | 0/4 | FAIL |
| 2 | `wick_reversal` | 59.4 | p95 | 0.15 | 1.48 | 250.44 | 1 | 0.9% | 0/4 | FAIL |
| 3 | `momentum_quality` | 56.8 | p90 | 4.49 | 2.10 | 1.62 | 118 | 10.3% | 0/4 | FAIL |
| 4 | `price_action_momentum` | 46.4 | p85 | 3.37 | 3.56 | 1.42 | 153 | 20.8% | 0/4 | FAIL |
| 5 | `narrow_range` | 44.6 | p80 | 0.50 | 1.26 | 1.10 | 103 | 13.3% | 0/4 | FAIL |
| 6 | `value_area` | 43.9 | p76 | 1.32 | 0.85 | 1.48 | 17 | 5.9% | 0/4 | FAIL |
| 7 | `roc_ma_cross` | 43.7 | p71 | 1.46 | 1.03 | 1.36 | 36 | 9.4% | 0/4 | FAIL |
| 8 | `volume_breakout` | 40.9 | p66 | 1.22 | 1.76 | 1.23 | 82 | 17.2% | 0/4 | FAIL |
| 9 | `relative_volume` | 40.8 | p61 | 0.30 | 1.42 | 1.11 | 50 | 8.5% | 0/4 | FAIL |
| 10 | `linear_channel_rev` | 40.6 | p57 | 0.63 | 1.62 | 1.20 | 30 | 5.8% | 0/4 | FAIL |
| 11 | `dema_cross` | 40.5 | p52 | 0.69 | 1.44 | 1.46 | 12 | 4.3% | 0/4 | FAIL |
| 12 | `elder_impulse` | 39.9 | p47 | -0.32 | 0.94 | 0.99 | 59 | 11.4% | 0/4 | FAIL |
| 13 | `lob_maker` | 38.9 | p42 | -0.12 | 0.85 | 1.02 | 113 | 24.9% | 0/4 | FAIL |
| 14 | `order_flow_imbalance_v2` | 38.2 | p38 | 0.68 | 1.84 | 1.15 | 79 | 18.1% | 0/4 | FAIL |
| 15 | `price_cluster` | 38.0 | p33 | -0.49 | 0.55 | 0.95 | 38 | 12.6% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +83.20% | 6.06 | 1.80 | 133 | 0/4 | FAIL |
| `price_action_momentum` | +58.38% | 3.37 | 1.42 | 153 | 0/4 | FAIL |
| `momentum_quality` | +53.88% | 4.49 | 1.62 | 118 | 0/4 | FAIL |
| `cmf` | +19.46% | 1.04 | 1.23 | 114 | 0/4 | FAIL |
| `htf_ema` | +14.09% | 1.58 | 1.31 | 66 | 0/4 | FAIL |
| `acceleration_band` | +12.07% | 1.18 | 1.20 | 94 | 0/4 | FAIL |
| `volume_breakout` | +10.16% | 1.22 | 1.23 | 82 | 0/4 | FAIL |
| `volatility_cluster` | +9.23% | 0.90 | 1.25 | 78 | 0/4 | FAIL |
| `roc_ma_cross` | +6.60% | 1.46 | 1.36 | 36 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +5.70% | 0.68 | 1.15 | 79 | 0/4 | FAIL |
| `value_area` | +3.90% | 1.32 | 1.48 | 17 | 0/4 | FAIL |
| `narrow_range` | +3.33% | 0.50 | 1.10 | 103 | 0/4 | FAIL |
| `linear_channel_rev` | +3.00% | 0.63 | 1.20 | 30 | 0/4 | FAIL |
| `relative_volume` | +1.76% | 0.30 | 1.11 | 50 | 0/4 | FAIL |
| `dema_cross` | +1.73% | 0.69 | 1.46 | 12 | 0/4 | FAIL |
| `wick_reversal` | +0.58% | 0.15 | 250.44 | 1 | 0/4 | FAIL |
| `elder_impulse` | -2.73% | -0.32 | 0.99 | 59 | 0/4 | FAIL |
| `price_cluster` | -3.46% | -0.49 | 0.95 | 38 | 0/4 | FAIL |
| `lob_maker` | -3.65% | -0.12 | 1.02 | 113 | 0/4 | FAIL |
| `positional_scaling` | -6.60% | -1.76 | 0.72 | 26 | 0/4 | FAIL |
| `engulfing_zone` | -16.78% | -4.08 | 0.47 | 27 | 0/4 | FAIL |
| `frama` | -21.75% | -3.08 | 0.74 | 84 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | mc_p_value 0.336 > 0.05 (우연 가능성) (x1), profit_factor 1.46 < 1.5 (x1), mc_p_value 0.354 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | max_drawdown 31.9% > 20% (x2), profit_factor 1.24 < 1.5 (x1), mc_p_value 0.366 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.334 > 0.05 (우연 가능성) (x1), profit_factor 1.18 < 1.5 (x1), mc_p_value 0.496 > 0.05 (우연 가능성) (x1) |
| `cmf` | sharpe -2.29 < 1.0 (x2), max_drawdown 30.8% > 20% (x1), profit_factor 0.83 < 1.5 (x1) |
| `htf_ema` | profit_factor 1.38 < 1.5 (x1), mc_p_value 0.386 > 0.05 (우연 가능성) (x1), sharpe -2.43 < 1.0 (x1) |
| `acceleration_band` | max_drawdown 20.8% > 20% (x1), profit_factor 1.18 < 1.5 (x1), mc_p_value 0.460 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 1.36 < 1.5 (x1), mc_p_value 0.410 > 0.05 (우연 가능성) (x1), sharpe -1.18 < 1.0 (x1) |
| `volatility_cluster` | sharpe 0.82 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.492 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | mc_p_value 0.390 > 0.05 (우연 가능성) (x1), sharpe -0.21 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.408 > 0.05 (우연 가능성) (x1), profit_factor 1.16 < 1.5 (x1), mc_p_value 0.496 > 0.05 (우연 가능성) (x1) |
| `value_area` | mc_p_value 0.474 > 0.05 (우연 가능성) (x3), sharpe 0.08 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1) |
| `narrow_range` | sharpe 0.19 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.460 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -1.78 < 1.0 (x1), profit_factor 0.72 < 1.5 (x1), mc_p_value 0.562 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | sharpe -1.24 < 1.0 (x1), profit_factor 0.84 < 1.5 (x1), mc_p_value 0.528 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | trades 11 < 15 (x2), sharpe 0.92 < 1.0 (x1), profit_factor 1.35 < 1.5 (x1) |
| `wick_reversal` | trades 1 < 15 (x2), no trades generated (x1), sharpe -2.10 < 1.0 (x1) |
| `elder_impulse` | sharpe 0.66 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.488 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -0.95 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.548 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.15 < 1.5 (x1), mc_p_value 0.450 > 0.05 (우연 가능성) (x1), sharpe -0.05 < 1.0 (x1) |
| `positional_scaling` | sharpe -2.05 < 1.0 (x1), profit_factor 0.67 < 1.5 (x1), mc_p_value 0.578 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.474 > 0.05 (우연 가능성) | 4 |
| mc_p_value 0.496 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.83 < 1.5 | 3 |
| mc_p_value 0.430 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.576 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.90 < 1.5 | 3 |
| max_drawdown 31.9% > 20% | 2 |
| profit_factor 1.24 < 1.5 | 2 |
| mc_p_value 0.334 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.18 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +10.55% -> $11,055
- **Top 5 균등배분**: +45.80% -> $14,580


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-29T10:18:27.998508Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=310261047, block=24)_
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
| 평균 수익률 | 9.54% |
| 최고 수익률 | 63.44% (cmf) |
| 최저 수익률 | -19.63% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `cmf` | +63.44% | 3.88 | 46.0% | 1.55 | 122 | 20.3% | 0/4 | FAIL |
| 2 | `momentum_quality` | +57.79% | 4.89 | 47.9% | 1.68 | 122 | 10.9% | 0/4 | FAIL |
| 3 | `price_action_momentum` | +35.81% | 2.64 | 41.7% | 1.30 | 173 | 22.6% | 0/4 | FAIL |
| 4 | `volatility_cluster` | +19.14% | 2.68 | 44.5% | 1.47 | 73 | 9.8% | 0/4 | FAIL |
| 5 | `htf_ema` | +18.59% | 2.05 | 43.4% | 1.31 | 79 | 13.9% | 0/4 | FAIL |
| 6 | `positional_scaling` | +15.71% | 3.17 | 54.7% | 2.24 | 27 | 5.3% | 0/4 | FAIL |
| 7 | `narrow_range` | +12.87% | 1.73 | 42.6% | 1.26 | 94 | 9.4% | 0/4 | FAIL |
| 8 | `supertrend_multi` | +9.58% | 1.22 | 39.1% | 1.15 | 124 | 18.2% | 0/4 | FAIL |
| 9 | `volume_breakout` | +8.96% | 0.83 | 39.3% | 1.16 | 92 | 22.5% | 0/4 | FAIL |
| 10 | `linear_channel_rev` | +8.13% | 2.01 | 46.0% | 1.54 | 28 | 5.5% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `wick_reversal` | 60.3 | p100 | 0.49 | 0.86 | 250.00 | 0 | 0.0% | 0/4 | FAIL |
| 2 | `momentum_quality` | 60.0 | p95 | 4.89 | 1.58 | 1.68 | 122 | 10.9% | 0/4 | FAIL |
| 3 | `volatility_cluster` | 49.8 | p90 | 2.68 | 1.06 | 1.47 | 73 | 9.8% | 0/4 | FAIL |
| 4 | `price_action_momentum` | 49.4 | p85 | 2.64 | 1.65 | 1.30 | 173 | 22.6% | 0/4 | FAIL |
| 5 | `positional_scaling` | 49.2 | p76 | 3.17 | 1.24 | 2.24 | 27 | 5.3% | 0/4 | FAIL |
| 6 | `value_area` | 49.2 | p80 | 2.31 | 0.46 | 1.81 | 20 | 3.8% | 0/4 | FAIL |
| 7 | `narrow_range` | 49.0 | p71 | 1.73 | 0.82 | 1.26 | 94 | 9.4% | 0/4 | FAIL |
| 8 | `cmf` | 48.6 | p66 | 3.88 | 2.23 | 1.55 | 122 | 20.3% | 0/4 | FAIL |
| 9 | `linear_channel_rev` | 48.4 | p61 | 2.01 | 0.35 | 1.54 | 28 | 5.5% | 0/4 | FAIL |
| 10 | `htf_ema` | 47.0 | p52 | 2.05 | 0.77 | 1.31 | 79 | 13.9% | 0/4 | FAIL |
| 11 | `roc_ma_cross` | 47.0 | p57 | 1.56 | 0.55 | 1.31 | 50 | 6.8% | 0/4 | FAIL |
| 12 | `supertrend_multi` | 46.2 | p47 | 1.22 | 0.60 | 1.15 | 124 | 18.2% | 0/4 | FAIL |
| 13 | `price_cluster` | 39.4 | p42 | 0.54 | 0.67 | 1.14 | 43 | 11.5% | 0/4 | FAIL |
| 14 | `order_flow_imbalance_v2` | 37.1 | p38 | 0.45 | 1.13 | 1.09 | 87 | 19.2% | 0/4 | FAIL |
| 15 | `volume_breakout` | 32.9 | p33 | 0.83 | 2.17 | 1.16 | 92 | 22.5% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `cmf` | +63.44% | 3.88 | 1.55 | 122 | 0/4 | FAIL |
| `momentum_quality` | +57.79% | 4.89 | 1.68 | 122 | 0/4 | FAIL |
| `price_action_momentum` | +35.81% | 2.64 | 1.30 | 173 | 0/4 | FAIL |
| `volatility_cluster` | +19.14% | 2.68 | 1.47 | 73 | 0/4 | FAIL |
| `htf_ema` | +18.59% | 2.05 | 1.31 | 79 | 0/4 | FAIL |
| `positional_scaling` | +15.71% | 3.17 | 2.24 | 27 | 0/4 | FAIL |
| `narrow_range` | +12.87% | 1.73 | 1.26 | 94 | 0/4 | FAIL |
| `supertrend_multi` | +9.58% | 1.22 | 1.15 | 124 | 0/4 | FAIL |
| `volume_breakout` | +8.96% | 0.83 | 1.16 | 92 | 0/4 | FAIL |
| `linear_channel_rev` | +8.13% | 2.01 | 1.54 | 28 | 0/4 | FAIL |
| `roc_ma_cross` | +8.09% | 1.56 | 1.31 | 50 | 0/4 | FAIL |
| `value_area` | +7.99% | 2.31 | 1.81 | 20 | 0/4 | FAIL |
| `lob_maker` | +3.59% | 0.35 | 1.07 | 123 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +3.18% | 0.45 | 1.09 | 87 | 0/4 | FAIL |
| `price_cluster` | +2.71% | 0.54 | 1.14 | 43 | 0/4 | FAIL |
| `wick_reversal` | +0.71% | 0.49 | 250.00 | 0 | 0/4 | FAIL |
| `dema_cross` | -3.19% | -1.83 | 0.54 | 11 | 0/4 | FAIL |
| `elder_impulse` | -4.23% | -0.69 | 0.99 | 78 | 0/4 | FAIL |
| `relative_volume` | -9.00% | -1.53 | 0.85 | 64 | 0/4 | FAIL |
| `engulfing_zone` | -11.39% | -2.65 | 0.60 | 25 | 0/4 | FAIL |
| `acceleration_band` | -18.89% | -2.55 | 0.83 | 110 | 0/4 | FAIL |
| `frama` | -19.63% | -2.55 | 0.79 | 90 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `cmf` | max_drawdown 25.4% > 20% (x2), sharpe 1.00 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1) |
| `momentum_quality` | mc_p_value 0.280 > 0.05 (우연 가능성) (x1), mc_p_value 0.232 > 0.05 (우연 가능성) (x1), mc_p_value 0.236 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe 0.83 < 1.0 (x1), max_drawdown 23.7% > 20% (x1), profit_factor 1.10 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.47 < 1.5 (x1), mc_p_value 0.404 > 0.05 (우연 가능성) (x1), mc_p_value 0.378 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | mc_p_value 0.430 > 0.05 (우연 가능성) (x2), profit_factor 1.22 < 1.5 (x1), mc_p_value 0.458 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | mc_p_value 0.408 > 0.05 (우연 가능성) (x1), mc_p_value 0.394 > 0.05 (우연 가능성) (x1), mc_p_value 0.434 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.19 < 1.5 (x1), mc_p_value 0.450 > 0.05 (우연 가능성) (x1), profit_factor 1.28 < 1.5 (x1) |
| `supertrend_multi` | sharpe 0.22 < 1.0 (x1), max_drawdown 23.4% > 20% (x1), profit_factor 1.05 < 1.5 (x1) |
| `volume_breakout` | sharpe -1.09 < 1.0 (x1), max_drawdown 23.8% > 20% (x1), profit_factor 0.91 < 1.5 (x1) |
| `linear_channel_rev` | mc_p_value 0.464 > 0.05 (우연 가능성) (x1), mc_p_value 0.510 > 0.05 (우연 가능성) (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe 0.88 < 1.0 (x1), profit_factor 1.16 < 1.5 (x1), mc_p_value 0.488 > 0.05 (우연 가능성) (x1) |
| `value_area` | mc_p_value 0.434 > 0.05 (우연 가능성) (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1), mc_p_value 0.432 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | sharpe -1.14 < 1.0 (x1), max_drawdown 24.2% > 20% (x1), profit_factor 0.93 < 1.5 (x1) |
| `order_flow_imbalance_v2` | profit_factor 0.96 < 1.5 (x2), sharpe -0.59 < 1.0 (x1), max_drawdown 21.8% > 20% (x1) |
| `price_cluster` | sharpe -0.02 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.498 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x3), trades 1 < 15 (x1) |
| `dema_cross` | profit_factor 0.67 < 1.5 (x2), sharpe -1.56 < 1.0 (x1), mc_p_value 0.490 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | sharpe 0.83 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.472 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | profit_factor 0.90 < 1.5 (x2), sharpe -1.78 < 1.0 (x1), profit_factor 0.82 < 1.5 (x1) |
| `engulfing_zone` | sharpe -2.23 < 1.0 (x1), profit_factor 0.66 < 1.5 (x1), mc_p_value 0.540 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.22 < 1.5 | 3 |
| profit_factor 1.19 < 1.5 | 3 |
| mc_p_value 0.434 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.440 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.510 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.90 < 1.5 | 3 |
| no trades generated | 3 |
| max_drawdown 25.4% > 20% | 2 |
| profit_factor 1.12 < 1.5 | 2 |
| mc_p_value 0.412 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +9.54% -> $10,954
- **Top 5 균등배분**: +38.95% -> $13,895


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-29T10:21:10.104737Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=330453117, block=24)_
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
| 평균 수익률 | 9.64% |
| 최고 수익률 | 39.51% (momentum_quality) |
| 최저 수익률 | -7.29% (price_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +39.51% | 4.01 | 46.7% | 1.57 | 110 | 9.6% | 0/4 | FAIL |
| 2 | `volume_breakout` | +29.99% | 3.00 | 44.0% | 1.47 | 92 | 12.2% | 0/4 | FAIL |
| 3 | `price_action_momentum` | +29.44% | 2.56 | 42.2% | 1.30 | 145 | 13.0% | 0/4 | FAIL |
| 4 | `supertrend_multi` | +26.05% | 3.00 | 45.5% | 1.44 | 94 | 10.7% | 0/4 | FAIL |
| 5 | `frama` | +25.66% | 2.70 | 43.2% | 1.45 | 76 | 11.1% | 0/4 | FAIL |
| 6 | `acceleration_band` | +22.05% | 2.05 | 41.3% | 1.30 | 105 | 12.4% | 0/4 | FAIL |
| 7 | `lob_maker` | +15.12% | 1.17 | 39.7% | 1.16 | 122 | 19.3% | 0/4 | FAIL |
| 8 | `roc_ma_cross` | +11.76% | 2.16 | 45.5% | 1.53 | 41 | 6.1% | 0/4 | FAIL |
| 9 | `htf_ema` | +10.76% | 1.26 | 41.1% | 1.23 | 71 | 16.2% | 0/4 | FAIL |
| 10 | `narrow_range` | +7.11% | 0.80 | 38.2% | 1.19 | 90 | 19.3% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 79.1 | p100 | 4.01 | 0.90 | 1.57 | 110 | 9.6% | 0/4 | FAIL |
| 2 | `volume_breakout` | 68.2 | p95 | 3.00 | 0.90 | 1.47 | 92 | 12.2% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 68.0 | p90 | 2.56 | 0.92 | 1.30 | 145 | 13.0% | 0/4 | FAIL |
| 4 | `supertrend_multi` | 67.3 | p85 | 3.00 | 1.22 | 1.44 | 94 | 10.7% | 0/4 | FAIL |
| 5 | `frama` | 63.9 | p80 | 2.70 | 1.18 | 1.45 | 76 | 11.1% | 0/4 | FAIL |
| 6 | `roc_ma_cross` | 60.6 | p76 | 2.16 | 1.62 | 1.53 | 41 | 6.1% | 0/4 | FAIL |
| 7 | `acceleration_band` | 57.9 | p71 | 2.05 | 1.57 | 1.30 | 105 | 12.4% | 0/4 | FAIL |
| 8 | `dema_cross` | 54.4 | p66 | 0.93 | 2.12 | 1.75 | 11 | 3.8% | 0/4 | FAIL |
| 9 | `htf_ema` | 48.1 | p61 | 1.26 | 1.22 | 1.23 | 71 | 16.2% | 0/4 | FAIL |
| 10 | `positional_scaling` | 47.5 | p57 | 0.91 | 1.86 | 1.35 | 24 | 7.1% | 0/4 | FAIL |
| 11 | `lob_maker` | 46.3 | p52 | 1.17 | 1.72 | 1.16 | 122 | 19.3% | 0/4 | FAIL |
| 12 | `order_flow_imbalance_v2` | 44.9 | p47 | 0.16 | 0.38 | 1.05 | 86 | 17.4% | 0/4 | FAIL |
| 13 | `linear_channel_rev` | 44.7 | p42 | 0.03 | 0.91 | 1.05 | 30 | 6.3% | 0/4 | FAIL |
| 14 | `cmf` | 42.4 | p38 | 0.38 | 1.16 | 1.07 | 113 | 20.2% | 0/4 | FAIL |
| 15 | `elder_impulse` | 42.1 | p33 | 0.38 | 1.34 | 1.10 | 58 | 13.0% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +39.51% | 4.01 | 1.57 | 110 | 0/4 | FAIL |
| `volume_breakout` | +29.99% | 3.00 | 1.47 | 92 | 0/4 | FAIL |
| `price_action_momentum` | +29.44% | 2.56 | 1.30 | 145 | 0/4 | FAIL |
| `supertrend_multi` | +26.05% | 3.00 | 1.44 | 94 | 0/4 | FAIL |
| `frama` | +25.66% | 2.70 | 1.45 | 76 | 0/4 | FAIL |
| `acceleration_band` | +22.05% | 2.05 | 1.30 | 105 | 0/4 | FAIL |
| `lob_maker` | +15.12% | 1.17 | 1.16 | 122 | 0/4 | FAIL |
| `roc_ma_cross` | +11.76% | 2.16 | 1.53 | 41 | 0/4 | FAIL |
| `htf_ema` | +10.76% | 1.26 | 1.23 | 71 | 0/4 | FAIL |
| `narrow_range` | +7.11% | 0.80 | 1.19 | 90 | 0/4 | FAIL |
| `positional_scaling` | +4.48% | 0.91 | 1.35 | 24 | 0/4 | FAIL |
| `dema_cross` | +3.33% | 0.93 | 1.75 | 11 | 0/4 | FAIL |
| `cmf` | +3.30% | 0.38 | 1.07 | 113 | 0/4 | FAIL |
| `elder_impulse` | +2.88% | 0.38 | 1.10 | 58 | 0/4 | FAIL |
| `volatility_cluster` | +2.79% | 0.42 | 1.11 | 80 | 0/4 | FAIL |
| `wick_reversal` | -0.01% | -0.37 | 0.62 | 2 | 0/4 | FAIL |
| `linear_channel_rev` | -0.09% | 0.03 | 1.05 | 30 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | -0.18% | 0.16 | 1.05 | 86 | 0/4 | FAIL |
| `relative_volume` | -2.26% | -0.44 | 0.98 | 57 | 0/4 | FAIL |
| `value_area` | -5.34% | -2.14 | 0.65 | 18 | 0/4 | FAIL |
| `engulfing_zone` | -6.89% | -1.71 | 0.77 | 22 | 0/4 | FAIL |
| `price_cluster` | -7.29% | -1.02 | 0.89 | 45 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | mc_p_value 0.338 > 0.05 (우연 가능성) (x1), mc_p_value 0.308 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1) |
| `volume_breakout` | mc_p_value 0.398 > 0.05 (우연 가능성) (x1), mc_p_value 0.326 > 0.05 (우연 가능성) (x1), profit_factor 1.32 < 1.5 (x1) |
| `price_action_momentum` | profit_factor 1.23 < 1.5 (x1), mc_p_value 0.370 > 0.05 (우연 가능성) (x1), profit_factor 1.30 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.486 > 0.05 (우연 가능성) (x1), mc_p_value 0.344 > 0.05 (우연 가능성) (x1) |
| `frama` | profit_factor 1.28 < 1.5 (x1), mc_p_value 0.446 > 0.05 (우연 가능성) (x1), profit_factor 1.18 < 1.5 (x1) |
| `acceleration_band` | profit_factor 1.27 < 1.5 (x1), mc_p_value 0.392 > 0.05 (우연 가능성) (x1), sharpe 0.10 < 1.0 (x1) |
| `lob_maker` | max_drawdown 20.2% > 20% (x2), sharpe -0.55 < 1.0 (x1), max_drawdown 25.5% > 20% (x1) |
| `roc_ma_cross` | sharpe -0.58 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1), mc_p_value 0.544 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | sharpe -0.45 < 1.0 (x1), max_drawdown 20.4% > 20% (x1), profit_factor 0.98 < 1.5 (x1) |
| `narrow_range` | profit_factor 1.42 < 1.5 (x1), mc_p_value 0.384 > 0.05 (우연 가능성) (x1), sharpe -0.21 < 1.0 (x1) |
| `positional_scaling` | sharpe -1.79 < 1.0 (x1), profit_factor 0.70 < 1.5 (x1), mc_p_value 0.560 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe -1.39 < 1.0 (x1), profit_factor 0.61 < 1.5 (x1), trades 8 < 15 (x1) |
| `cmf` | sharpe -1.07 < 1.0 (x1), max_drawdown 23.2% > 20% (x1), profit_factor 0.91 < 1.5 (x1) |
| `elder_impulse` | mc_p_value 0.434 > 0.05 (우연 가능성) (x2), sharpe -1.66 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.390 > 0.05 (우연 가능성) (x1), sharpe -0.25 < 1.0 (x1) |
| `wick_reversal` | sharpe -2.06 < 1.0 (x1), profit_factor 0.00 < 1.5 (x1), trades 1 < 15 (x1) |
| `linear_channel_rev` | sharpe -1.45 < 1.0 (x1), profit_factor 0.78 < 1.5 (x1), mc_p_value 0.510 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe -0.19 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.476 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | sharpe -1.58 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1), mc_p_value 0.518 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe 0.45 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.470 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.408 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.398 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.30 < 1.5 | 3 |
| profit_factor 1.25 < 1.5 | 3 |
| profit_factor 0.79 < 1.5 | 3 |
| profit_factor 1.32 < 1.5 | 2 |
| mc_p_value 0.396 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.23 < 1.5 | 2 |
| mc_p_value 0.344 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.18 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +9.64% -> $10,964
- **Top 5 균등배분**: +30.13% -> $13,013
