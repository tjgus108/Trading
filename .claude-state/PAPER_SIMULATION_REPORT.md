# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-28T16:18:49.712691Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-28T16:25:21.155619Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=511380744, block=36)_
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
| 평균 수익률 | 19.42% |
| 최고 수익률 | 75.29% (momentum_quality) |
| 최저 수익률 | -7.78% (price_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +75.29% | 6.01 | 49.4% | 1.83 | 126 | 9.4% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +60.73% | 4.20 | 45.0% | 1.48 | 157 | 15.6% | 0/4 | FAIL |
| 3 | `lob_maker` | +55.44% | 3.71 | 45.4% | 1.47 | 124 | 15.5% | 0/4 | FAIL |
| 4 | `volume_breakout` | +48.77% | 4.34 | 48.1% | 1.67 | 96 | 9.9% | 0/4 | FAIL |
| 5 | `cmf` | +45.98% | 3.25 | 44.2% | 1.43 | 133 | 16.5% | 0/4 | FAIL |
| 6 | `supertrend_multi` | +41.20% | 4.15 | 46.5% | 1.64 | 100 | 10.4% | 0/4 | FAIL |
| 7 | `volatility_cluster` | +25.80% | 3.52 | 47.5% | 1.72 | 69 | 6.7% | 0/4 | FAIL |
| 8 | `acceleration_band` | +23.81% | 2.55 | 43.5% | 1.37 | 95 | 10.1% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | +23.25% | 2.24 | 42.3% | 1.32 | 87 | 17.9% | 0/4 | FAIL |
| 10 | `relative_volume` | +22.39% | 3.47 | 48.3% | 1.71 | 57 | 6.3% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 63.1 | p100 | 6.01 | 0.75 | 1.83 | 126 | 9.4% | 0/4 | FAIL |
| 2 | `wick_reversal` | 56.0 | p95 | 0.49 | 0.85 | 250.00 | 0 | 0.0% | 0/4 | FAIL |
| 3 | `volume_breakout` | 55.1 | p90 | 4.34 | 0.40 | 1.67 | 96 | 9.9% | 0/4 | FAIL |
| 4 | `price_action_momentum` | 49.5 | p85 | 4.20 | 1.69 | 1.48 | 157 | 15.6% | 0/4 | FAIL |
| 5 | `relative_volume` | 48.9 | p80 | 3.47 | 0.76 | 1.71 | 57 | 6.3% | 0/4 | FAIL |
| 6 | `lob_maker` | 47.7 | p76 | 3.71 | 1.06 | 1.47 | 124 | 15.5% | 0/4 | FAIL |
| 7 | `acceleration_band` | 47.3 | p71 | 2.55 | 0.50 | 1.37 | 95 | 10.1% | 0/4 | FAIL |
| 8 | `supertrend_multi` | 46.3 | p66 | 4.15 | 1.98 | 1.64 | 100 | 10.4% | 0/4 | FAIL |
| 9 | `volatility_cluster` | 45.3 | p61 | 3.52 | 1.67 | 1.72 | 69 | 6.7% | 0/4 | FAIL |
| 10 | `cmf` | 44.5 | p57 | 3.25 | 1.36 | 1.43 | 133 | 16.5% | 0/4 | FAIL |
| 11 | `narrow_range` | 40.2 | p52 | 1.62 | 0.74 | 1.24 | 94 | 12.9% | 0/4 | FAIL |
| 12 | `order_flow_imbalance_v2` | 38.0 | p47 | 2.24 | 0.77 | 1.32 | 87 | 17.9% | 0/4 | FAIL |
| 13 | `linear_channel_rev` | 36.6 | p42 | 0.67 | 0.51 | 1.16 | 39 | 7.3% | 0/4 | FAIL |
| 14 | `positional_scaling` | 33.1 | p38 | -0.03 | 0.61 | 1.03 | 25 | 5.9% | 0/4 | FAIL |
| 15 | `value_area` | 32.5 | p33 | -0.17 | 0.55 | 0.99 | 18 | 5.4% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +75.29% | 6.01 | 1.83 | 126 | 0/4 | FAIL |
| `price_action_momentum` | +60.73% | 4.20 | 1.48 | 157 | 0/4 | FAIL |
| `lob_maker` | +55.44% | 3.71 | 1.47 | 124 | 0/4 | FAIL |
| `volume_breakout` | +48.77% | 4.34 | 1.67 | 96 | 0/4 | FAIL |
| `cmf` | +45.98% | 3.25 | 1.43 | 133 | 0/4 | FAIL |
| `supertrend_multi` | +41.20% | 4.15 | 1.64 | 100 | 0/4 | FAIL |
| `volatility_cluster` | +25.80% | 3.52 | 1.72 | 69 | 0/4 | FAIL |
| `acceleration_band` | +23.81% | 2.55 | 1.37 | 95 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +23.25% | 2.24 | 1.32 | 87 | 0/4 | FAIL |
| `relative_volume` | +22.39% | 3.47 | 1.71 | 57 | 0/4 | FAIL |
| `narrow_range` | +11.96% | 1.62 | 1.24 | 94 | 0/4 | FAIL |
| `linear_channel_rev` | +2.69% | 0.67 | 1.16 | 39 | 0/4 | FAIL |
| `engulfing_zone` | +2.58% | 0.52 | 1.20 | 22 | 0/4 | FAIL |
| `htf_ema` | +2.42% | 0.38 | 1.09 | 74 | 0/4 | FAIL |
| `dema_cross` | +2.03% | 0.69 | 1.37 | 13 | 0/4 | FAIL |
| `elder_impulse` | +1.32% | 0.12 | 1.07 | 66 | 0/4 | FAIL |
| `wick_reversal` | +0.46% | 0.49 | 250.00 | 0 | 0/4 | FAIL |
| `positional_scaling` | -0.26% | -0.03 | 1.03 | 25 | 0/4 | FAIL |
| `value_area` | -0.51% | -0.17 | 0.99 | 18 | 0/4 | FAIL |
| `roc_ma_cross` | -3.86% | -0.84 | 0.90 | 37 | 0/4 | FAIL |
| `frama` | -6.42% | -0.68 | 0.95 | 84 | 0/4 | FAIL |
| `price_cluster` | -7.78% | -1.61 | 0.82 | 37 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | mc_p_value 0.260 > 0.05 (우연 가능성) (x2), mc_p_value 0.274 > 0.05 (우연 가능성) (x1), mc_p_value 0.166 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | max_drawdown 20.3% > 20% (x1), profit_factor 1.19 < 1.5 (x1), mc_p_value 0.394 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | max_drawdown 20.4% > 20% (x1), profit_factor 1.22 < 1.5 (x1), mc_p_value 0.400 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 1.50 < 1.5 (x1), mc_p_value 0.356 > 0.05 (우연 가능성) (x1), mc_p_value 0.354 > 0.05 (우연 가능성) (x1) |
| `cmf` | max_drawdown 20.6% > 20% (x2), mc_p_value 0.394 > 0.05 (우연 가능성) (x2), profit_factor 1.24 < 1.5 (x1) |
| `supertrend_multi` | sharpe 0.94 < 1.0 (x1), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.438 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | mc_p_value 0.358 > 0.05 (우연 가능성) (x1), profit_factor 1.24 < 1.5 (x1), mc_p_value 0.456 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.382 > 0.05 (우연 가능성) (x1), profit_factor 1.49 < 1.5 (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.368 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1) |
| `relative_volume` | mc_p_value 0.394 > 0.05 (우연 가능성) (x1), mc_p_value 0.388 > 0.05 (우연 가능성) (x1), mc_p_value 0.396 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.446 > 0.05 (우연 가능성) (x1), sharpe 0.38 < 1.0 (x1) |
| `linear_channel_rev` | profit_factor 1.29 < 1.5 (x1), mc_p_value 0.422 > 0.05 (우연 가능성) (x1), sharpe 0.14 < 1.0 (x1) |
| `engulfing_zone` | mc_p_value 0.458 > 0.05 (우연 가능성) (x2), profit_factor 1.45 < 1.5 (x1), sharpe -0.06 < 1.0 (x1) |
| `htf_ema` | sharpe -1.23 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.550 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | trades 13 < 15 (x2), trades 11 < 15 (x1), sharpe -1.50 < 1.0 (x1) |
| `elder_impulse` | sharpe 0.63 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1), mc_p_value 0.476 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x3), trades 1 < 15 (x1) |
| `positional_scaling` | sharpe -1.01 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1), mc_p_value 0.516 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -0.52 < 1.0 (x1), profit_factor 0.90 < 1.5 (x1), mc_p_value 0.518 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | mc_p_value 0.526 > 0.05 (우연 가능성) (x2), sharpe -0.42 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.394 > 0.05 (우연 가능성) | 4 |
| profit_factor 1.45 < 1.5 | 4 |
| max_drawdown 20.6% > 20% | 3 |
| profit_factor 1.24 < 1.5 | 3 |
| sharpe 0.94 < 1.0 | 3 |
| mc_p_value 0.458 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.524 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.526 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.18 < 1.5 | 3 |
| no trades generated | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +19.42% -> $11,942
- **Top 5 균등배분**: +57.24% -> $15,724
