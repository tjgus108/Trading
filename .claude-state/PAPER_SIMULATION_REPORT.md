# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-01T05:28:13.231909Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-01T05:35:43.010547Z_
_Symbol: BTC/USDT_
_Data Source: CSV fallback BTC/USDT 1h (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 23:00:00+00:00 (499일)_
_Walk-Forward: 8개 윈도우 (train=5040h, test=1440h)_
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
| 평균 수익률 | -3.71% |
| 최고 수익률 | 6.10% (supertrend_multi) |
| 최저 수익률 | -10.64% (elder_impulse) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +6.10% | 0.36 | 36.6% | 1.12 | 47 | 11.2% | 1/8 | FAIL |
| 2 | `price_cluster` | +2.52% | 0.39 | 39.4% | 1.12 | 45 | 12.7% | 1/8 | FAIL |
| 3 | `positional_scaling` | +2.12% | -0.01 | 36.5% | 1.20 | 36 | 10.7% | 1/8 | FAIL |
| 4 | `roc_ma_cross` | +0.98% | -0.13 | 37.9% | 1.15 | 40 | 9.2% | 2/8 | FAIL |
| 5 | `frama` | +0.11% | 0.02 | 38.9% | 1.06 | 42 | 10.5% | 0/8 | FAIL |
| 6 | `narrow_range` | -1.22% | -0.16 | 38.6% | 1.03 | 50 | 11.8% | 0/8 | FAIL |
| 7 | `dema_cross` | -1.35% | -1.70 | 19.6% | 0.39 | 3 | 2.2% | 0/8 | FAIL |
| 8 | `htf_ema` | -1.43% | -0.14 | 38.5% | 1.02 | 45 | 11.9% | 0/8 | FAIL |
| 9 | `volume_breakout` | -1.48% | -0.34 | 37.5% | 1.04 | 78 | 16.3% | 0/8 | FAIL |
| 10 | `momentum_quality` | -2.99% | -0.81 | 34.3% | 1.00 | 66 | 15.6% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 68.9 | p100 | 0.39 | 1.37 | 1.12 | 45 | 12.7% | 1/8 | FAIL |
| 2 | `supertrend_multi` | 66.4 | p95 | 0.36 | 2.66 | 1.12 | 47 | 11.2% | 1/8 | FAIL |
| 3 | `roc_ma_cross` | 66.0 | p90 | -0.13 | 2.68 | 1.15 | 40 | 9.2% | 2/8 | FAIL |
| 4 | `positional_scaling` | 61.0 | p85 | -0.01 | 3.04 | 1.20 | 36 | 10.7% | 1/8 | FAIL |
| 5 | `narrow_range` | 59.2 | p80 | -0.16 | 1.27 | 1.03 | 50 | 11.8% | 0/8 | FAIL |
| 6 | `frama` | 59.0 | p76 | 0.02 | 1.28 | 1.06 | 42 | 10.5% | 0/8 | FAIL |
| 7 | `volume_breakout` | 58.4 | p71 | -0.34 | 2.63 | 1.04 | 78 | 16.3% | 0/8 | FAIL |
| 8 | `order_flow_imbalance_v2` | 58.4 | p66 | -0.55 | 1.91 | 0.98 | 77 | 15.9% | 0/8 | FAIL |
| 9 | `htf_ema` | 57.4 | p61 | -0.14 | 1.23 | 1.02 | 45 | 11.9% | 0/8 | FAIL |
| 10 | `lob_maker` | 57.0 | p57 | -0.55 | 1.81 | 0.98 | 84 | 20.8% | 0/8 | FAIL |
| 11 | `momentum_quality` | 54.3 | p47 | -0.81 | 2.93 | 1.00 | 66 | 15.6% | 1/8 | FAIL |
| 12 | `price_action_momentum` | 54.3 | p52 | -0.90 | 2.97 | 1.00 | 82 | 19.0% | 1/8 | FAIL |
| 13 | `cmf` | 47.6 | p42 | -1.26 | 1.67 | 0.89 | 75 | 19.6% | 0/8 | FAIL |
| 14 | `acceleration_band` | 44.7 | p38 | -0.89 | 2.27 | 0.97 | 45 | 15.2% | 0/8 | FAIL |
| 15 | `relative_volume` | 43.4 | p33 | -1.42 | 1.75 | 0.86 | 59 | 14.2% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +6.10% | 0.36 | 1.12 | 47 | 1/8 | FAIL |
| `price_cluster` | +2.52% | 0.39 | 1.12 | 45 | 1/8 | FAIL |
| `positional_scaling` | +2.12% | -0.01 | 1.20 | 36 | 1/8 | FAIL |
| `roc_ma_cross` | +0.98% | -0.13 | 1.15 | 40 | 2/8 | FAIL |
| `frama` | +0.11% | 0.02 | 1.06 | 42 | 0/8 | FAIL |
| `narrow_range` | -1.22% | -0.16 | 1.03 | 50 | 0/8 | FAIL |
| `dema_cross` | -1.35% | -1.70 | 0.39 | 3 | 0/8 | FAIL |
| `htf_ema` | -1.43% | -0.14 | 1.02 | 45 | 0/8 | FAIL |
| `volume_breakout` | -1.48% | -0.34 | 1.04 | 78 | 0/8 | FAIL |
| `momentum_quality` | -2.99% | -0.81 | 1.00 | 66 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | -3.95% | -0.55 | 0.98 | 77 | 0/8 | FAIL |
| `acceleration_band` | -4.48% | -0.89 | 0.97 | 45 | 0/8 | FAIL |
| `price_action_momentum` | -4.62% | -0.90 | 1.00 | 82 | 1/8 | FAIL |
| `lob_maker` | -5.32% | -0.55 | 0.98 | 84 | 0/8 | FAIL |
| `wick_reversal` | -5.67% | -1.63 | 0.71 | 23 | 0/8 | FAIL |
| `engulfing_zone` | -5.75% | -1.33 | 0.82 | 25 | 0/8 | FAIL |
| `relative_volume` | -7.46% | -1.42 | 0.86 | 59 | 0/8 | FAIL |
| `linear_channel_rev` | -8.50% | -2.82 | 0.63 | 29 | 0/8 | FAIL |
| `cmf` | -9.24% | -1.26 | 0.89 | 75 | 0/8 | FAIL |
| `volatility_cluster` | -9.65% | -2.05 | 0.81 | 60 | 0/8 | FAIL |
| `value_area` | -9.68% | -2.50 | 0.73 | 46 | 0/8 | FAIL |
| `elder_impulse` | -10.64% | -2.04 | 0.74 | 47 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | mc_p_value 0.060 > 0.05 (우연 가능성) (x1), profit_factor 1.43 < 1.5 (x1), mc_p_value 0.190 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -1.40 < 1.0 (x1), max_drawdown 21.7% > 20% (x1), profit_factor 0.79 < 1.5 (x1) |
| `positional_scaling` | mc_p_value 0.078 > 0.05 (우연 가능성) (x1), sharpe -0.85 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1) |
| `roc_ma_cross` | sharpe 0.21 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.446 > 0.05 (우연 가능성) (x1) |
| `frama` | profit_factor 1.00 < 1.5 (x2), sharpe -0.12 < 1.0 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | sharpe 0.62 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.356 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x4), trades 2 < 15 (x3), trades 3 < 15 (x2) |
| `htf_ema` | profit_factor 1.14 < 1.5 (x2), sharpe 0.49 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1) |
| `volume_breakout` | sharpe -0.18 < 1.0 (x1), max_drawdown 22.6% > 20% (x1), profit_factor 1.00 < 1.5 (x1) |
| `momentum_quality` | max_drawdown 22.0% > 20% (x2), profit_factor 1.32 < 1.5 (x1), mc_p_value 0.142 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.19 < 1.5 (x1), mc_p_value 0.252 > 0.05 (우연 가능성) (x1), sharpe -0.28 < 1.0 (x1) |
| `acceleration_band` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.214 > 0.05 (우연 가능성) (x1), sharpe -1.66 < 1.0 (x1) |
| `price_action_momentum` | profit_factor 0.78 < 1.5 (x2), profit_factor 1.22 < 1.5 (x1), mc_p_value 0.218 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | sharpe -1.80 < 1.0 (x1), max_drawdown 32.9% > 20% (x1), profit_factor 0.85 < 1.5 (x1) |
| `wick_reversal` | profit_factor 0.44 < 1.5 (x2), profit_factor 1.07 < 1.5 (x2), sharpe -1.91 < 1.0 (x1) |
| `engulfing_zone` | profit_factor 0.59 < 1.5 (x2), sharpe -2.22 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1) |
| `relative_volume` | mc_p_value 0.410 > 0.05 (우연 가능성) (x2), sharpe -1.94 < 1.0 (x1), profit_factor 0.78 < 1.5 (x1) |
| `linear_channel_rev` | sharpe 0.01 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1), mc_p_value 0.466 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.16 < 1.5 (x1), mc_p_value 0.304 > 0.05 (우연 가능성) (x1), sharpe -2.06 < 1.0 (x1) |
| `volatility_cluster` | sharpe -1.03 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.680 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.85 < 1.5 | 5 |
| profit_factor 0.63 < 1.5 | 5 |
| profit_factor 0.78 < 1.5 | 5 |
| profit_factor 0.77 < 1.5 | 4 |
| profit_factor 1.00 < 1.5 | 4 |
| profit_factor 1.06 < 1.5 | 4 |
| mc_p_value 0.998 > 0.05 (우연 가능성) | 4 |
| profit_factor 0.89 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 1.09 < 1.5 | 4 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.71% -> $9,629
- **Top 5 균등배분**: +2.37% -> $10,237


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-01T05:39:27.591516Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=426266688, block=24)_
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
| PASS (일관성 50%+) | 3개 |
| FAIL | 19개 |
| 평균 수익률 | 18.96% |
| 최고 수익률 | 64.93% (price_action_momentum) |
| 최저 수익률 | -2.88% (dema_cross) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +64.93% | 4.50 | 43.9% | 1.63 | 130 | 9.9% | 2/4 | PASS |
| 2 | `acceleration_band` | +50.54% | 4.01 | 43.7% | 1.64 | 96 | 9.9% | 3/4 | PASS |
| 3 | `cmf` | +47.80% | 2.98 | 40.5% | 1.41 | 111 | 15.8% | 1/4 | FAIL |
| 4 | `volume_breakout` | +37.11% | 3.32 | 43.2% | 1.52 | 91 | 9.4% | 1/4 | FAIL |
| 5 | `momentum_quality` | +30.16% | 3.12 | 41.8% | 1.43 | 106 | 9.3% | 2/4 | PASS |
| 6 | `order_flow_imbalance_v2` | +29.83% | 2.59 | 41.5% | 1.42 | 81 | 13.8% | 1/4 | FAIL |
| 7 | `lob_maker` | +22.01% | 1.76 | 37.7% | 1.23 | 122 | 19.3% | 0/4 | FAIL |
| 8 | `supertrend_multi` | +20.38% | 2.44 | 40.6% | 1.40 | 78 | 8.7% | 0/4 | FAIL |
| 9 | `htf_ema` | +17.29% | 1.89 | 40.3% | 1.32 | 68 | 11.8% | 0/4 | FAIL |
| 10 | `narrow_range` | +16.11% | 1.87 | 38.6% | 1.31 | 86 | 12.3% | 1/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 83.1 | p100 | 4.50 | 1.28 | 1.63 | 130 | 9.9% | 2/4 | PASS |
| 2 | `acceleration_band` | 77.9 | p95 | 4.01 | 1.04 | 1.64 | 96 | 9.9% | 3/4 | PASS |
| 3 | `momentum_quality` | 71.6 | p90 | 3.12 | 0.60 | 1.43 | 106 | 9.3% | 2/4 | PASS |
| 4 | `volume_breakout` | 67.5 | p85 | 3.32 | 0.37 | 1.52 | 91 | 9.4% | 1/4 | FAIL |
| 5 | `cmf` | 59.2 | p80 | 2.98 | 1.90 | 1.41 | 111 | 15.8% | 1/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | 55.6 | p76 | 2.59 | 1.21 | 1.42 | 81 | 13.8% | 1/4 | FAIL |
| 7 | `supertrend_multi` | 55.1 | p71 | 2.44 | 0.48 | 1.40 | 78 | 8.7% | 0/4 | FAIL |
| 8 | `relative_volume` | 54.2 | p66 | 2.43 | 0.98 | 1.50 | 56 | 5.8% | 1/4 | FAIL |
| 9 | `narrow_range` | 52.0 | p61 | 1.87 | 1.33 | 1.31 | 86 | 12.3% | 1/4 | FAIL |
| 10 | `lob_maker` | 51.2 | p57 | 1.76 | 0.73 | 1.23 | 122 | 19.3% | 0/4 | FAIL |
| 11 | `volatility_cluster` | 50.9 | p52 | 1.82 | 1.12 | 1.32 | 76 | 11.4% | 1/4 | FAIL |
| 12 | `roc_ma_cross` | 49.0 | p47 | 2.16 | 1.72 | 1.60 | 39 | 6.7% | 1/4 | FAIL |
| 13 | `price_cluster` | 47.6 | p42 | 2.08 | 0.77 | 1.54 | 37 | 10.8% | 1/4 | FAIL |
| 14 | `htf_ema` | 45.9 | p38 | 1.89 | 1.26 | 1.32 | 68 | 11.8% | 0/4 | FAIL |
| 15 | `frama` | 44.4 | p33 | 1.59 | 1.53 | 1.28 | 80 | 14.0% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +64.93% | 4.50 | 1.63 | 130 | 2/4 | PASS |
| `acceleration_band` | +50.54% | 4.01 | 1.64 | 96 | 3/4 | PASS |
| `cmf` | +47.80% | 2.98 | 1.41 | 111 | 1/4 | FAIL |
| `volume_breakout` | +37.11% | 3.32 | 1.52 | 91 | 1/4 | FAIL |
| `momentum_quality` | +30.16% | 3.12 | 1.43 | 106 | 2/4 | PASS |
| `order_flow_imbalance_v2` | +29.83% | 2.59 | 1.42 | 81 | 1/4 | FAIL |
| `lob_maker` | +22.01% | 1.76 | 1.23 | 122 | 0/4 | FAIL |
| `supertrend_multi` | +20.38% | 2.44 | 1.40 | 78 | 0/4 | FAIL |
| `htf_ema` | +17.29% | 1.89 | 1.32 | 68 | 0/4 | FAIL |
| `narrow_range` | +16.11% | 1.87 | 1.31 | 86 | 1/4 | FAIL |
| `relative_volume` | +15.77% | 2.43 | 1.50 | 56 | 1/4 | FAIL |
| `frama` | +14.98% | 1.59 | 1.28 | 80 | 0/4 | FAIL |
| `price_cluster` | +14.88% | 2.08 | 1.54 | 37 | 1/4 | FAIL |
| `volatility_cluster` | +13.20% | 1.82 | 1.32 | 76 | 1/4 | FAIL |
| `roc_ma_cross` | +11.53% | 2.16 | 1.60 | 39 | 1/4 | FAIL |
| `linear_channel_rev` | +7.71% | 1.79 | 1.50 | 31 | 0/4 | FAIL |
| `elder_impulse` | +3.55% | 0.61 | 1.14 | 55 | 0/4 | FAIL |
| `value_area` | +1.44% | 0.40 | 1.19 | 22 | 0/4 | FAIL |
| `engulfing_zone` | +1.24% | 0.34 | 1.11 | 24 | 0/4 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `positional_scaling` | -0.40% | -0.40 | 1.02 | 25 | 0/4 | FAIL |
| `dema_cross` | -2.88% | -1.31 | 0.74 | 12 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `cmf` | sharpe 0.14 < 1.0 (x1), max_drawdown 24.6% > 20% (x1), profit_factor 1.04 < 1.5 (x1) |
| `volume_breakout` | profit_factor 1.47 < 1.5 (x2), mc_p_value 0.070 > 0.05 (우연 가능성) (x1), mc_p_value 0.052 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.056 > 0.05 (우연 가능성) (x1), profit_factor 1.39 < 1.5 (x1) |
| `lob_maker` | max_drawdown 23.8% > 20% (x2), profit_factor 1.35 < 1.5 (x1), mc_p_value 0.068 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.162 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1) |
| `htf_ema` | sharpe -0.27 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1), mc_p_value 0.522 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.164 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1) |
| `relative_volume` | mc_p_value 0.062 > 0.05 (우연 가능성) (x1), profit_factor 1.27 < 1.5 (x1), mc_p_value 0.242 > 0.05 (우연 가능성) (x1) |
| `frama` | mc_p_value 0.052 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1), sharpe 0.92 < 1.0 (x1) |
| `price_cluster` | profit_factor 1.49 < 1.5 (x1), mc_p_value 0.162 > 0.05 (우연 가능성) (x1), profit_factor 1.30 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.22 < 1.5 (x1), mc_p_value 0.250 > 0.05 (우연 가능성) (x1), profit_factor 1.21 < 1.5 (x1) |
| `roc_ma_cross` | sharpe -0.49 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1), mc_p_value 0.550 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | mc_p_value 0.132 > 0.05 (우연 가능성) (x1), mc_p_value 0.164 > 0.05 (우연 가능성) (x1), profit_factor 1.43 < 1.5 (x1) |
| `elder_impulse` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.220 > 0.05 (우연 가능성) (x1), profit_factor 1.31 < 1.5 (x1) |
| `value_area` | sharpe -0.88 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.608 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe 0.32 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1), mc_p_value 0.400 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x4) |
| `positional_scaling` | profit_factor 1.30 < 1.5 (x2), mc_p_value 0.248 > 0.05 (우연 가능성) (x1), mc_p_value 0.286 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe -3.22 < 1.0 (x1), profit_factor 0.40 < 1.5 (x1), trades 14 < 15 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 4 |
| profit_factor 1.44 < 1.5 | 3 |
| profit_factor 1.47 < 1.5 | 3 |
| profit_factor 1.34 < 1.5 | 3 |
| profit_factor 1.30 < 1.5 | 3 |
| profit_factor 1.36 < 1.5 | 2 |
| mc_p_value 0.062 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.46 < 1.5 | 2 |
| profit_factor 1.35 < 1.5 | 2 |
| sharpe 0.14 < 1.0 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +18.96% -> $11,896
- **PASS 3개 균등배분**: +48.55% -> $14,854
- **Top 5 균등배분**: +46.11% -> $14,611


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-01T05:43:26.092273Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=1065024214, block=24)_
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
| PASS (일관성 50%+) | 8개 |
| FAIL | 14개 |
| 평균 수익률 | 18.88% |
| 최고 수익률 | 87.98% (price_action_momentum) |
| 최저 수익률 | -11.58% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +87.98% | 5.48 | 45.0% | 1.73 | 140 | 10.8% | 4/4 | PASS |
| 2 | `momentum_quality` | +62.99% | 5.07 | 46.8% | 1.80 | 102 | 11.4% | 3/4 | PASS |
| 3 | `frama` | +60.03% | 4.47 | 44.3% | 1.82 | 82 | 13.3% | 3/4 | PASS |
| 4 | `supertrend_multi` | +42.95% | 3.89 | 43.6% | 1.62 | 90 | 11.0% | 2/4 | PASS |
| 5 | `htf_ema` | +42.04% | 3.95 | 46.4% | 1.77 | 64 | 9.6% | 3/4 | PASS |
| 6 | `volatility_cluster` | +24.57% | 3.21 | 44.6% | 1.57 | 67 | 7.7% | 2/4 | PASS |
| 7 | `cmf` | +20.73% | 1.72 | 36.8% | 1.24 | 115 | 19.3% | 1/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | +20.67% | 1.85 | 38.3% | 1.29 | 84 | 15.8% | 1/4 | FAIL |
| 9 | `acceleration_band` | +19.97% | 1.82 | 38.0% | 1.26 | 100 | 23.0% | 0/4 | FAIL |
| 10 | `roc_ma_cross` | +14.79% | 2.65 | 44.1% | 1.67 | 37 | 6.3% | 2/4 | PASS |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 88.4 | p100 | 5.48 | 0.38 | 1.73 | 140 | 10.8% | 4/4 | PASS |
| 2 | `momentum_quality` | 72.9 | p95 | 5.07 | 1.51 | 1.80 | 102 | 11.4% | 3/4 | PASS |
| 3 | `frama` | 65.0 | p90 | 4.47 | 1.93 | 1.82 | 82 | 13.3% | 3/4 | PASS |
| 4 | `htf_ema` | 61.1 | p85 | 3.95 | 1.50 | 1.77 | 64 | 9.6% | 3/4 | PASS |
| 5 | `supertrend_multi` | 60.5 | p80 | 3.89 | 2.08 | 1.62 | 90 | 11.0% | 2/4 | PASS |
| 6 | `volatility_cluster` | 56.4 | p76 | 3.21 | 0.78 | 1.57 | 67 | 7.7% | 2/4 | PASS |
| 7 | `cmf` | 49.5 | p71 | 1.72 | 1.04 | 1.24 | 115 | 19.3% | 1/4 | FAIL |
| 8 | `roc_ma_cross` | 47.8 | p66 | 2.65 | 1.07 | 1.67 | 37 | 6.3% | 2/4 | PASS |
| 9 | `order_flow_imbalance_v2` | 46.0 | p61 | 1.85 | 1.20 | 1.29 | 84 | 15.8% | 1/4 | FAIL |
| 10 | `acceleration_band` | 42.1 | p57 | 1.82 | 1.46 | 1.26 | 100 | 23.0% | 0/4 | FAIL |
| 11 | `narrow_range` | 41.7 | p52 | 1.35 | 1.38 | 1.21 | 86 | 13.5% | 0/4 | FAIL |
| 12 | `dema_cross` | 41.4 | p47 | 1.87 | 2.13 | 2.21 | 13 | 4.3% | 1/4 | FAIL |
| 13 | `volume_breakout` | 36.2 | p42 | 0.22 | 0.76 | 1.06 | 90 | 18.8% | 0/4 | FAIL |
| 14 | `relative_volume` | 35.7 | p38 | 0.81 | 0.24 | 1.15 | 56 | 10.7% | 0/4 | FAIL |
| 15 | `lob_maker` | 34.5 | p33 | -0.78 | 0.75 | 0.95 | 121 | 23.4% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +87.98% | 5.48 | 1.73 | 140 | 4/4 | PASS |
| `momentum_quality` | +62.99% | 5.07 | 1.80 | 102 | 3/4 | PASS |
| `frama` | +60.03% | 4.47 | 1.82 | 82 | 3/4 | PASS |
| `supertrend_multi` | +42.95% | 3.89 | 1.62 | 90 | 2/4 | PASS |
| `htf_ema` | +42.04% | 3.95 | 1.77 | 64 | 3/4 | PASS |
| `volatility_cluster` | +24.57% | 3.21 | 1.57 | 67 | 2/4 | PASS |
| `cmf` | +20.73% | 1.72 | 1.24 | 115 | 1/4 | FAIL |
| `order_flow_imbalance_v2` | +20.67% | 1.85 | 1.29 | 84 | 1/4 | FAIL |
| `acceleration_band` | +19.97% | 1.82 | 1.26 | 100 | 0/4 | FAIL |
| `roc_ma_cross` | +14.79% | 2.65 | 1.67 | 37 | 2/4 | PASS |
| `narrow_range` | +10.99% | 1.35 | 1.21 | 86 | 0/4 | FAIL |
| `price_cluster` | +7.37% | 0.67 | 1.30 | 40 | 2/4 | PASS |
| `dema_cross` | +7.11% | 1.87 | 2.21 | 13 | 1/4 | FAIL |
| `elder_impulse` | +5.29% | 0.78 | 1.21 | 46 | 0/4 | FAIL |
| `linear_channel_rev` | +4.38% | 0.99 | 1.25 | 32 | 0/4 | FAIL |
| `relative_volume` | +4.36% | 0.81 | 1.15 | 56 | 0/4 | FAIL |
| `volume_breakout` | +0.62% | 0.22 | 1.06 | 90 | 0/4 | FAIL |
| `positional_scaling` | +0.49% | 0.07 | 1.12 | 29 | 1/4 | FAIL |
| `wick_reversal` | -0.56% | -1.05 | 0.00 | 0 | 0/4 | FAIL |
| `value_area` | -0.57% | -0.34 | 1.04 | 20 | 0/4 | FAIL |
| `engulfing_zone` | -9.30% | -2.29 | 0.69 | 22 | 0/4 | FAIL |
| `lob_maker` | -11.58% | -0.78 | 0.95 | 121 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `cmf` | sharpe 0.97 < 1.0 (x1), max_drawdown 20.6% > 20% (x1), profit_factor 1.12 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe 0.44 < 1.0 (x1), profit_factor 1.07 < 1.5 (x1), mc_p_value 0.358 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | max_drawdown 21.3% > 20% (x2), profit_factor 1.26 < 1.5 (x1), mc_p_value 0.134 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.32 < 1.5 (x1), mc_p_value 0.124 > 0.05 (우연 가능성) (x1), profit_factor 1.43 < 1.5 (x1) |
| `dema_cross` | sharpe -0.67 < 1.0 (x1), profit_factor 0.82 < 1.5 (x1), trades 11 < 15 (x1) |
| `elder_impulse` | sharpe -2.12 < 1.0 (x1), max_drawdown 20.0% > 20% (x1), profit_factor 0.73 < 1.5 (x1) |
| `linear_channel_rev` | profit_factor 1.39 < 1.5 (x1), mc_p_value 0.190 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1) |
| `relative_volume` | profit_factor 1.17 < 1.5 (x2), sharpe 0.94 < 1.0 (x1), mc_p_value 0.278 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -0.01 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.454 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | sharpe -0.58 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1), mc_p_value 0.554 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | profit_factor 0.00 < 1.5 (x2), trades 1 < 15 (x2), no trades generated (x2) |
| `value_area` | mc_p_value 0.180 > 0.05 (우연 가능성) (x1), sharpe -2.06 < 1.0 (x1), profit_factor 0.58 < 1.5 (x1) |
| `engulfing_zone` | profit_factor 1.30 < 1.5 (x1), mc_p_value 0.314 > 0.05 (우연 가능성) (x1), sharpe -1.71 < 1.0 (x1) |
| `lob_maker` | mc_p_value 0.628 > 0.05 (우연 가능성) (x2), sharpe -1.56 < 1.0 (x1), max_drawdown 23.3% > 20% (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.12 < 1.5 | 3 |
| profit_factor 1.26 < 1.5 | 3 |
| profit_factor 1.47 < 1.5 | 2 |
| profit_factor 1.33 < 1.5 | 2 |
| mc_p_value 0.106 > 0.05 (우연 가능성) | 2 |
| max_drawdown 20.6% > 20% | 2 |
| mc_p_value 0.278 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.07 < 1.5 | 2 |
| mc_p_value 0.358 > 0.05 (우연 가능성) | 2 |
| max_drawdown 21.3% > 20% | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +18.88% -> $11,888
- **PASS 8개 균등배분**: +42.84% -> $14,284
- **Top 5 균등배분**: +59.20% -> $15,920
