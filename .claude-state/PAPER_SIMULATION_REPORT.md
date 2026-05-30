# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-30T05:11:49.901210Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-30T05:14:45.831481Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1469401197, block=24)_
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
| 평균 수익률 | 16.34% |
| 최고 수익률 | 78.99% (price_action_momentum) |
| 최저 수익률 | -3.25% (narrow_range) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +78.99% | 5.42 | 48.6% | 1.66 | 146 | 12.0% | 0/4 | FAIL |
| 2 | `lob_maker` | +44.27% | 3.09 | 44.4% | 1.39 | 122 | 20.0% | 0/4 | FAIL |
| 3 | `momentum_quality` | +30.76% | 3.31 | 44.5% | 1.44 | 110 | 12.9% | 0/4 | FAIL |
| 4 | `acceleration_band` | +29.94% | 2.46 | 42.2% | 1.47 | 98 | 13.7% | 0/4 | FAIL |
| 5 | `cmf` | +27.44% | 1.67 | 41.8% | 1.26 | 119 | 21.1% | 0/4 | FAIL |
| 6 | `supertrend_multi` | +26.43% | 2.80 | 42.6% | 1.36 | 120 | 11.1% | 0/4 | FAIL |
| 7 | `volume_breakout` | +25.33% | 2.57 | 44.2% | 1.36 | 96 | 12.6% | 0/4 | FAIL |
| 8 | `htf_ema` | +21.59% | 2.43 | 44.5% | 1.41 | 72 | 9.7% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | +20.26% | 1.98 | 42.8% | 1.29 | 87 | 14.4% | 0/4 | FAIL |
| 10 | `roc_ma_cross` | +15.25% | 2.80 | 48.6% | 1.73 | 43 | 4.7% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 63.9 | p100 | 5.42 | 1.37 | 1.66 | 146 | 12.0% | 0/4 | FAIL |
| 2 | `momentum_quality` | 52.3 | p95 | 3.31 | 0.65 | 1.44 | 110 | 12.9% | 0/4 | FAIL |
| 3 | `supertrend_multi` | 50.7 | p90 | 2.80 | 1.04 | 1.36 | 120 | 11.1% | 0/4 | FAIL |
| 4 | `wick_reversal` | 47.4 | p85 | -0.55 | 1.69 | 250.00 | 1 | 0.9% | 0/4 | FAIL |
| 5 | `volume_breakout` | 46.8 | p80 | 2.57 | 0.83 | 1.36 | 96 | 12.6% | 0/4 | FAIL |
| 6 | `value_area` | 44.9 | p76 | 3.04 | 1.70 | 2.27 | 24 | 3.6% | 0/4 | FAIL |
| 7 | `roc_ma_cross` | 44.8 | p71 | 2.80 | 1.71 | 1.73 | 43 | 4.7% | 0/4 | FAIL |
| 8 | `htf_ema` | 44.0 | p66 | 2.43 | 1.30 | 1.41 | 72 | 9.7% | 0/4 | FAIL |
| 9 | `lob_maker` | 43.5 | p61 | 3.09 | 1.57 | 1.39 | 122 | 20.0% | 0/4 | FAIL |
| 10 | `order_flow_imbalance_v2` | 40.2 | p57 | 1.98 | 1.23 | 1.29 | 87 | 14.4% | 0/4 | FAIL |
| 11 | `dema_cross` | 40.1 | p52 | 2.12 | 1.63 | 1.93 | 16 | 3.4% | 0/4 | FAIL |
| 12 | `acceleration_band` | 36.4 | p47 | 2.46 | 3.15 | 1.47 | 98 | 13.7% | 0/4 | FAIL |
| 13 | `volatility_cluster` | 34.0 | p42 | 0.51 | 1.00 | 1.10 | 76 | 12.9% | 0/4 | FAIL |
| 14 | `relative_volume` | 33.9 | p38 | 0.71 | 1.25 | 1.15 | 55 | 10.2% | 0/4 | FAIL |
| 15 | `positional_scaling` | 32.4 | p33 | 1.08 | 1.87 | 1.40 | 31 | 7.9% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +78.99% | 5.42 | 1.66 | 146 | 0/4 | FAIL |
| `lob_maker` | +44.27% | 3.09 | 1.39 | 122 | 0/4 | FAIL |
| `momentum_quality` | +30.76% | 3.31 | 1.44 | 110 | 0/4 | FAIL |
| `acceleration_band` | +29.94% | 2.46 | 1.47 | 98 | 0/4 | FAIL |
| `cmf` | +27.44% | 1.67 | 1.26 | 119 | 0/4 | FAIL |
| `supertrend_multi` | +26.43% | 2.80 | 1.36 | 120 | 0/4 | FAIL |
| `volume_breakout` | +25.33% | 2.57 | 1.36 | 96 | 0/4 | FAIL |
| `htf_ema` | +21.59% | 2.43 | 1.41 | 72 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +20.26% | 1.98 | 1.29 | 87 | 0/4 | FAIL |
| `roc_ma_cross` | +15.25% | 2.80 | 1.73 | 43 | 0/4 | FAIL |
| `value_area` | +12.25% | 3.04 | 2.27 | 24 | 0/4 | FAIL |
| `dema_cross` | +7.46% | 2.12 | 1.93 | 16 | 0/4 | FAIL |
| `positional_scaling` | +4.87% | 1.08 | 1.40 | 31 | 0/4 | FAIL |
| `engulfing_zone` | +4.38% | 0.77 | 1.25 | 28 | 0/4 | FAIL |
| `elder_impulse` | +4.30% | 0.71 | 1.27 | 55 | 0/4 | FAIL |
| `relative_volume` | +3.86% | 0.71 | 1.15 | 55 | 0/4 | FAIL |
| `frama` | +3.68% | 0.49 | 1.13 | 91 | 0/4 | FAIL |
| `volatility_cluster` | +2.77% | 0.51 | 1.10 | 76 | 0/4 | FAIL |
| `price_cluster` | +2.33% | 0.50 | 1.15 | 36 | 0/4 | FAIL |
| `wick_reversal` | -0.14% | -0.55 | 250.00 | 1 | 0/4 | FAIL |
| `linear_channel_rev` | -3.19% | -0.88 | 0.87 | 24 | 0/4 | FAIL |
| `narrow_range` | -3.25% | -0.44 | 1.01 | 88 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.210 > 0.05 (우연 가능성) (x1), mc_p_value 0.170 > 0.05 (우연 가능성) (x1), mc_p_value 0.124 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | max_drawdown 28.4% > 20% (x2), sharpe 0.88 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1) |
| `momentum_quality` | profit_factor 1.40 < 1.5 (x1), mc_p_value 0.354 > 0.05 (우연 가능성) (x1), mc_p_value 0.292 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.15 < 1.5 (x1), mc_p_value 0.410 > 0.05 (우연 가능성) (x1), sharpe -1.76 < 1.0 (x1) |
| `cmf` | max_drawdown 21.0% > 20% (x2), mc_p_value 0.192 > 0.05 (우연 가능성) (x1), profit_factor 1.21 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.21 < 1.5 (x1), mc_p_value 0.372 > 0.05 (우연 가능성) (x1), profit_factor 1.32 < 1.5 (x1) |
| `volume_breakout` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.344 > 0.05 (우연 가능성) (x1), profit_factor 1.21 < 1.5 (x1) |
| `htf_ema` | sharpe 0.79 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), mc_p_value 0.494 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.480 > 0.05 (우연 가능성) (x2), sharpe 0.54 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1) |
| `roc_ma_cross` | sharpe 0.56 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), mc_p_value 0.478 > 0.05 (우연 가능성) (x1) |
| `value_area` | mc_p_value 0.404 > 0.05 (우연 가능성) (x1), sharpe 0.41 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1) |
| `dema_cross` | sharpe -0.30 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1), trades 12 < 15 (x1) |
| `positional_scaling` | sharpe -0.45 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1), mc_p_value 0.494 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -1.56 < 1.0 (x1), profit_factor 0.74 < 1.5 (x1), mc_p_value 0.558 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -0.19 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.510 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | profit_factor 1.30 < 1.5 (x2), mc_p_value 0.394 > 0.05 (우연 가능성) (x1), sharpe -1.30 < 1.0 (x1) |
| `frama` | sharpe -0.62 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1), mc_p_value 0.514 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -0.08 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.528 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe 0.44 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1), mc_p_value 0.470 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | trades 1 < 15 (x3), sharpe -2.09 < 1.0 (x2), profit_factor 0.00 < 1.5 (x2) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.21 < 1.5 | 4 |
| max_drawdown 28.4% > 20% | 3 |
| mc_p_value 0.376 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.30 < 1.5 | 3 |
| profit_factor 1.12 < 1.5 | 3 |
| profit_factor 0.95 < 1.5 | 3 |
| trades 1 < 15 | 3 |
| profit_factor 1.32 < 1.5 | 2 |
| profit_factor 1.11 < 1.5 | 2 |
| profit_factor 1.40 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +16.34% -> $11,634
- **Top 5 균등배분**: +42.28% -> $14,228


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-30T05:17:39.502371Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=1143349005, block=24)_
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
| 평균 수익률 | 14.98% |
| 최고 수익률 | 44.40% (momentum_quality) |
| 최저 수익률 | -0.85% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +44.40% | 4.33 | 47.2% | 1.59 | 113 | 8.6% | 0/4 | FAIL |
| 2 | `cmf` | +43.84% | 3.36 | 45.2% | 1.43 | 113 | 14.1% | 0/4 | FAIL |
| 3 | `price_action_momentum` | +42.87% | 3.46 | 43.7% | 1.39 | 146 | 12.8% | 0/4 | FAIL |
| 4 | `volume_breakout` | +33.88% | 3.14 | 46.5% | 1.56 | 87 | 8.9% | 0/4 | FAIL |
| 5 | `volatility_cluster` | +26.24% | 3.29 | 46.3% | 1.57 | 82 | 8.4% | 0/4 | FAIL |
| 6 | `lob_maker` | +24.87% | 2.11 | 41.7% | 1.26 | 118 | 11.0% | 0/4 | FAIL |
| 7 | `supertrend_multi` | +16.19% | 2.21 | 44.1% | 1.34 | 74 | 11.9% | 0/4 | FAIL |
| 8 | `elder_impulse` | +15.59% | 2.27 | 45.1% | 1.42 | 58 | 8.8% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | +12.78% | 1.44 | 41.0% | 1.21 | 83 | 14.7% | 0/4 | FAIL |
| 10 | `relative_volume` | +12.25% | 2.13 | 45.0% | 1.44 | 58 | 6.6% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 75.1 | p100 | 4.33 | 1.12 | 1.59 | 113 | 8.6% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 70.6 | p95 | 3.46 | 0.31 | 1.39 | 146 | 12.8% | 0/4 | FAIL |
| 3 | `dema_cross` | 69.9 | p90 | 2.81 | 0.61 | 2.39 | 13 | 3.0% | 0/4 | FAIL |
| 4 | `cmf` | 64.5 | p85 | 3.36 | 0.67 | 1.43 | 113 | 14.1% | 0/4 | FAIL |
| 5 | `volatility_cluster` | 64.5 | p80 | 3.29 | 1.63 | 1.57 | 82 | 8.4% | 0/4 | FAIL |
| 6 | `volume_breakout` | 60.9 | p76 | 3.14 | 2.56 | 1.56 | 87 | 8.9% | 0/4 | FAIL |
| 7 | `lob_maker` | 60.0 | p71 | 2.11 | 0.52 | 1.26 | 118 | 11.0% | 0/4 | FAIL |
| 8 | `elder_impulse` | 58.2 | p66 | 2.27 | 0.50 | 1.42 | 58 | 8.8% | 0/4 | FAIL |
| 9 | `relative_volume` | 57.3 | p61 | 2.13 | 1.29 | 1.44 | 58 | 6.6% | 0/4 | FAIL |
| 10 | `supertrend_multi` | 54.7 | p57 | 2.21 | 0.92 | 1.34 | 74 | 11.9% | 0/4 | FAIL |
| 11 | `order_flow_imbalance_v2` | 48.9 | p52 | 1.44 | 0.53 | 1.21 | 83 | 14.7% | 0/4 | FAIL |
| 12 | `value_area` | 47.7 | p47 | 0.95 | 1.00 | 1.31 | 23 | 5.7% | 0/4 | FAIL |
| 13 | `roc_ma_cross` | 47.5 | p42 | 1.72 | 2.28 | 1.50 | 38 | 9.7% | 0/4 | FAIL |
| 14 | `narrow_range` | 46.3 | p33 | 1.08 | 1.77 | 1.18 | 88 | 11.5% | 0/4 | FAIL |
| 15 | `linear_channel_rev` | 46.3 | p38 | 1.59 | 3.58 | 1.82 | 31 | 8.1% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +44.40% | 4.33 | 1.59 | 113 | 0/4 | FAIL |
| `cmf` | +43.84% | 3.36 | 1.43 | 113 | 0/4 | FAIL |
| `price_action_momentum` | +42.87% | 3.46 | 1.39 | 146 | 0/4 | FAIL |
| `volume_breakout` | +33.88% | 3.14 | 1.56 | 87 | 0/4 | FAIL |
| `volatility_cluster` | +26.24% | 3.29 | 1.57 | 82 | 0/4 | FAIL |
| `lob_maker` | +24.87% | 2.11 | 1.26 | 118 | 0/4 | FAIL |
| `supertrend_multi` | +16.19% | 2.21 | 1.34 | 74 | 0/4 | FAIL |
| `elder_impulse` | +15.59% | 2.27 | 1.42 | 58 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +12.78% | 1.44 | 1.21 | 83 | 0/4 | FAIL |
| `relative_volume` | +12.25% | 2.13 | 1.44 | 58 | 0/4 | FAIL |
| `roc_ma_cross` | +9.75% | 1.72 | 1.50 | 38 | 0/4 | FAIL |
| `dema_cross` | +8.53% | 2.81 | 2.39 | 13 | 0/4 | FAIL |
| `narrow_range` | +8.50% | 1.08 | 1.18 | 88 | 0/4 | FAIL |
| `linear_channel_rev` | +8.39% | 1.59 | 1.82 | 31 | 0/4 | FAIL |
| `htf_ema` | +5.75% | 0.77 | 1.14 | 73 | 0/4 | FAIL |
| `acceleration_band` | +5.67% | 0.75 | 1.10 | 104 | 0/4 | FAIL |
| `value_area` | +3.17% | 0.95 | 1.31 | 23 | 0/4 | FAIL |
| `frama` | +2.96% | 0.34 | 1.08 | 85 | 0/4 | FAIL |
| `price_cluster` | +2.33% | 0.40 | 1.11 | 39 | 0/4 | FAIL |
| `engulfing_zone` | +1.87% | 0.29 | 1.23 | 24 | 0/4 | FAIL |
| `positional_scaling` | +0.49% | 0.20 | 1.07 | 33 | 0/4 | FAIL |
| `wick_reversal` | -0.85% | -1.05 | 0.00 | 0 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.316 > 0.05 (우연 가능성) (x1), profit_factor 1.38 < 1.5 (x1) |
| `cmf` | profit_factor 1.30 < 1.5 (x1), mc_p_value 0.386 > 0.05 (우연 가능성) (x1), mc_p_value 0.288 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.270 > 0.05 (우연 가능성) (x1), profit_factor 1.43 < 1.5 (x1) |
| `volume_breakout` | sharpe -0.51 < 1.0 (x1), profit_factor 0.97 < 1.5 (x1), mc_p_value 0.524 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.17 < 1.5 (x1), mc_p_value 0.426 > 0.05 (우연 가능성) (x1), profit_factor 1.36 < 1.5 (x1) |
| `lob_maker` | profit_factor 1.15 < 1.5 (x1), mc_p_value 0.414 > 0.05 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.44 < 1.5 (x1), mc_p_value 0.320 > 0.05 (우연 가능성) (x1), profit_factor 1.23 < 1.5 (x1) |
| `elder_impulse` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.432 > 0.05 (우연 가능성) (x1), mc_p_value 0.394 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe 0.65 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1), mc_p_value 0.472 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | sharpe 0.11 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1), mc_p_value 0.476 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | mc_p_value 0.380 > 0.05 (우연 가능성) (x1), mc_p_value 0.366 > 0.05 (우연 가능성) (x1), sharpe -0.23 < 1.0 (x1) |
| `dema_cross` | trades 13 < 15 (x1), mc_p_value 0.446 > 0.05 (우연 가능성) (x1), trades 14 < 15 (x1) |
| `narrow_range` | sharpe -1.31 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.618 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -4.08 < 1.0 (x1), profit_factor 0.48 < 1.5 (x1), mc_p_value 0.648 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.428 > 0.05 (우연 가능성) (x1), profit_factor 1.30 < 1.5 (x1) |
| `acceleration_band` | mc_p_value 0.468 > 0.05 (우연 가능성) (x2), profit_factor 1.11 < 1.5 (x2), profit_factor 1.16 < 1.5 (x1) |
| `value_area` | sharpe -0.18 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1), mc_p_value 0.522 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe -0.46 < 1.0 (x1), profit_factor 0.97 < 1.5 (x1), mc_p_value 0.522 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | profit_factor 1.42 < 1.5 (x1), mc_p_value 0.418 > 0.05 (우연 가능성) (x1), sharpe 0.76 < 1.0 (x1) |
| `engulfing_zone` | mc_p_value 0.390 > 0.05 (우연 가능성) (x1), sharpe -0.18 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.38 < 1.5 | 3 |
| profit_factor 1.30 < 1.5 | 3 |
| profit_factor 1.04 < 1.5 | 3 |
| profit_factor 0.99 < 1.5 | 3 |
| profit_factor 0.94 < 1.5 | 3 |
| mc_p_value 0.368 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.386 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.288 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.49 < 1.5 | 2 |
| profit_factor 1.43 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +14.98% -> $11,498
- **Top 5 균등배분**: +38.25% -> $13,825


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-30T05:20:34.286000Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=1070862162, block=24)_
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
| 평균 수익률 | 7.00% |
| 최고 수익률 | 40.09% (supertrend_multi) |
| 최저 수익률 | -10.61% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +40.09% | 3.75 | 45.6% | 1.46 | 133 | 12.2% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +25.66% | 2.25 | 41.5% | 1.24 | 157 | 13.9% | 0/4 | FAIL |
| 3 | `elder_impulse` | +19.55% | 2.64 | 45.4% | 1.50 | 58 | 10.9% | 0/4 | FAIL |
| 4 | `volume_breakout` | +15.71% | 1.76 | 42.7% | 1.25 | 96 | 12.8% | 0/4 | FAIL |
| 5 | `lob_maker` | +15.41% | 1.37 | 40.9% | 1.17 | 124 | 17.4% | 0/4 | FAIL |
| 6 | `acceleration_band` | +14.34% | 1.57 | 41.2% | 1.22 | 97 | 18.4% | 0/4 | FAIL |
| 7 | `volatility_cluster` | +11.10% | 1.56 | 42.3% | 1.26 | 82 | 10.9% | 0/4 | FAIL |
| 8 | `momentum_quality` | +10.07% | 1.31 | 40.7% | 1.18 | 112 | 12.4% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | +9.15% | 1.08 | 40.8% | 1.17 | 85 | 13.4% | 0/4 | FAIL |
| 10 | `value_area` | +5.12% | 1.17 | 43.1% | 1.40 | 28 | 5.5% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `wick_reversal` | 67.4 | p100 | 1.49 | 0.86 | 749.99 | 1 | 0.0% | 0/4 | FAIL |
| 2 | `supertrend_multi` | 62.2 | p95 | 3.75 | 1.04 | 1.46 | 133 | 12.2% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 58.4 | p90 | 2.25 | 0.52 | 1.24 | 157 | 13.9% | 0/4 | FAIL |
| 4 | `elder_impulse` | 53.4 | p85 | 2.64 | 0.28 | 1.50 | 58 | 10.9% | 0/4 | FAIL |
| 5 | `volume_breakout` | 51.2 | p80 | 1.76 | 0.48 | 1.25 | 96 | 12.8% | 0/4 | FAIL |
| 6 | `momentum_quality` | 48.9 | p76 | 1.31 | 1.00 | 1.18 | 112 | 12.4% | 0/4 | FAIL |
| 7 | `lob_maker` | 47.5 | p71 | 1.37 | 0.92 | 1.17 | 124 | 17.4% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | 46.4 | p66 | 1.08 | 0.51 | 1.17 | 85 | 13.4% | 0/4 | FAIL |
| 9 | `volatility_cluster` | 45.7 | p61 | 1.56 | 1.73 | 1.26 | 82 | 10.9% | 0/4 | FAIL |
| 10 | `dema_cross` | 45.4 | p57 | 1.61 | 1.23 | 2.84 | 7 | 3.2% | 0/4 | FAIL |
| 11 | `acceleration_band` | 45.2 | p52 | 1.57 | 0.93 | 1.22 | 97 | 18.4% | 0/4 | FAIL |
| 12 | `narrow_range` | 42.7 | p47 | 0.36 | 0.86 | 1.08 | 98 | 14.0% | 0/4 | FAIL |
| 13 | `value_area` | 41.5 | p42 | 1.17 | 1.92 | 1.40 | 28 | 5.5% | 0/4 | FAIL |
| 14 | `relative_volume` | 38.2 | p38 | 0.56 | 1.80 | 1.13 | 58 | 11.4% | 0/4 | FAIL |
| 15 | `frama` | 37.8 | p33 | 0.08 | 1.30 | 1.05 | 84 | 15.2% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +40.09% | 3.75 | 1.46 | 133 | 0/4 | FAIL |
| `price_action_momentum` | +25.66% | 2.25 | 1.24 | 157 | 0/4 | FAIL |
| `elder_impulse` | +19.55% | 2.64 | 1.50 | 58 | 0/4 | FAIL |
| `volume_breakout` | +15.71% | 1.76 | 1.25 | 96 | 0/4 | FAIL |
| `lob_maker` | +15.41% | 1.37 | 1.17 | 124 | 0/4 | FAIL |
| `acceleration_band` | +14.34% | 1.57 | 1.22 | 97 | 0/4 | FAIL |
| `volatility_cluster` | +11.10% | 1.56 | 1.26 | 82 | 0/4 | FAIL |
| `momentum_quality` | +10.07% | 1.31 | 1.18 | 112 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +9.15% | 1.08 | 1.17 | 85 | 0/4 | FAIL |
| `value_area` | +5.12% | 1.17 | 1.40 | 28 | 0/4 | FAIL |
| `relative_volume` | +3.86% | 0.56 | 1.13 | 58 | 0/4 | FAIL |
| `dema_cross` | +3.39% | 1.61 | 2.84 | 7 | 0/4 | FAIL |
| `narrow_range` | +2.16% | 0.36 | 1.08 | 98 | 0/4 | FAIL |
| `wick_reversal` | +2.14% | 1.49 | 749.99 | 1 | 0/4 | FAIL |
| `cmf` | +1.14% | 0.17 | 1.06 | 117 | 0/4 | FAIL |
| `frama` | -0.13% | 0.08 | 1.05 | 84 | 0/4 | FAIL |
| `linear_channel_rev` | -0.37% | -0.45 | 1.09 | 33 | 0/4 | FAIL |
| `htf_ema` | -0.42% | -0.02 | 1.07 | 68 | 0/4 | FAIL |
| `roc_ma_cross` | -2.68% | -0.60 | 0.93 | 33 | 0/4 | FAIL |
| `positional_scaling` | -3.83% | -0.94 | 0.89 | 30 | 0/4 | FAIL |
| `price_cluster` | -6.89% | -0.98 | 0.88 | 43 | 0/4 | FAIL |
| `engulfing_zone` | -10.61% | -2.78 | 0.63 | 26 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | mc_p_value 0.320 > 0.05 (우연 가능성) (x1), mc_p_value 0.206 > 0.05 (우연 가능성) (x1), profit_factor 1.38 < 1.5 (x1) |
| `price_action_momentum` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.328 > 0.05 (우연 가능성) (x1), profit_factor 1.28 < 1.5 (x1) |
| `elder_impulse` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.420 > 0.05 (우연 가능성) (x1), mc_p_value 0.356 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 1.21 < 1.5 (x1), mc_p_value 0.462 > 0.05 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1) |
| `lob_maker` | mc_p_value 0.374 > 0.05 (우연 가능성) (x2), profit_factor 1.23 < 1.5 (x1), sharpe 0.67 < 1.0 (x1) |
| `acceleration_band` | profit_factor 1.41 < 1.5 (x1), mc_p_value 0.346 > 0.05 (우연 가능성) (x1), sharpe 0.50 < 1.0 (x1) |
| `volatility_cluster` | mc_p_value 0.316 > 0.05 (우연 가능성) (x1), sharpe 0.24 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1) |
| `momentum_quality` | profit_factor 1.22 < 1.5 (x1), mc_p_value 0.396 > 0.05 (우연 가능성) (x1), sharpe -0.05 < 1.0 (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.20 < 1.5 (x1), mc_p_value 0.450 > 0.05 (우연 가능성) (x1), sharpe 0.41 < 1.0 (x1) |
| `value_area` | sharpe -1.58 < 1.0 (x1), profit_factor 0.74 < 1.5 (x1), mc_p_value 0.530 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | sharpe -2.38 < 1.0 (x1), profit_factor 0.70 < 1.5 (x1), mc_p_value 0.590 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe 0.14 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), trades 11 < 15 (x1) |
| `narrow_range` | sharpe -0.79 < 1.0 (x1), profit_factor 0.94 < 1.5 (x1), mc_p_value 0.564 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | trades 1 < 15 (x3), no trades generated (x1) |
| `cmf` | profit_factor 1.21 < 1.5 (x1), mc_p_value 0.422 > 0.05 (우연 가능성) (x1), sharpe -1.70 < 1.0 (x1) |
| `frama` | sharpe -1.59 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.596 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | mc_p_value 0.414 > 0.05 (우연 가능성) (x1), mc_p_value 0.456 > 0.05 (우연 가능성) (x1), sharpe -1.09 < 1.0 (x1) |
| `htf_ema` | profit_factor 1.40 < 1.5 (x1), mc_p_value 0.428 > 0.05 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1) |
| `roc_ma_cross` | sharpe 0.10 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1), mc_p_value 0.518 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | sharpe 0.81 < 1.0 (x1), profit_factor 1.20 < 1.5 (x1), mc_p_value 0.470 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.500 > 0.05 (우연 가능성) | 4 |
| profit_factor 0.85 < 1.5 | 4 |
| profit_factor 1.22 < 1.5 | 3 |
| mc_p_value 0.396 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.26 < 1.5 | 3 |
| mc_p_value 0.380 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.05 < 1.5 | 3 |
| profit_factor 1.24 < 1.5 | 3 |
| mc_p_value 0.436 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.20 < 1.5 | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +7.00% -> $10,700
- **Top 5 균등배분**: +23.28% -> $12,328
