# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-30T15:20:03.298405Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-30T15:23:55.268899Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1011848652, block=24)_
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
| 평균 수익률 | 8.14% |
| 최고 수익률 | 33.24% (price_action_momentum) |
| 최저 수익률 | -11.51% (narrow_range) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +33.24% | 2.84 | 42.6% | 1.31 | 145 | 16.4% | 0/4 | FAIL |
| 2 | `supertrend_multi` | +27.21% | 3.01 | 43.3% | 1.41 | 103 | 12.9% | 0/4 | FAIL |
| 3 | `frama` | +25.05% | 2.62 | 43.5% | 1.45 | 74 | 10.2% | 0/4 | FAIL |
| 4 | `htf_ema` | +22.80% | 2.43 | 44.3% | 1.41 | 72 | 9.6% | 0/4 | FAIL |
| 5 | `momentum_quality` | +14.52% | 1.71 | 40.7% | 1.23 | 112 | 14.7% | 0/4 | FAIL |
| 6 | `elder_impulse` | +14.14% | 2.12 | 46.2% | 1.49 | 49 | 8.4% | 0/4 | FAIL |
| 7 | `volatility_cluster` | +10.87% | 1.61 | 41.6% | 1.25 | 81 | 11.6% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | +9.75% | 1.11 | 38.9% | 1.17 | 82 | 13.8% | 0/4 | FAIL |
| 9 | `positional_scaling` | +9.43% | 2.04 | 47.7% | 1.63 | 29 | 6.5% | 0/4 | FAIL |
| 10 | `lob_maker` | +9.00% | 0.84 | 39.3% | 1.12 | 124 | 17.0% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 77.4 | p100 | 2.84 | 0.50 | 1.31 | 145 | 16.4% | 0/4 | FAIL |
| 2 | `supertrend_multi` | 75.7 | p95 | 3.01 | 1.15 | 1.41 | 103 | 12.9% | 0/4 | FAIL |
| 3 | `frama` | 71.6 | p90 | 2.62 | 1.42 | 1.45 | 74 | 10.2% | 0/4 | FAIL |
| 4 | `htf_ema` | 70.1 | p85 | 2.43 | 1.40 | 1.41 | 72 | 9.6% | 0/4 | FAIL |
| 5 | `positional_scaling` | 68.6 | p80 | 2.04 | 1.35 | 1.63 | 29 | 6.5% | 0/4 | FAIL |
| 6 | `elder_impulse` | 67.2 | p76 | 2.12 | 1.54 | 1.49 | 49 | 8.4% | 0/4 | FAIL |
| 7 | `volatility_cluster` | 65.8 | p71 | 1.61 | 0.50 | 1.25 | 81 | 11.6% | 0/4 | FAIL |
| 8 | `momentum_quality` | 64.5 | p66 | 1.71 | 1.11 | 1.23 | 112 | 14.7% | 0/4 | FAIL |
| 9 | `value_area` | 61.3 | p61 | 1.12 | 1.31 | 1.42 | 22 | 4.1% | 0/4 | FAIL |
| 10 | `price_cluster` | 60.9 | p57 | 1.12 | 0.56 | 1.25 | 42 | 8.3% | 0/4 | FAIL |
| 11 | `order_flow_imbalance_v2` | 58.6 | p52 | 1.11 | 0.82 | 1.17 | 82 | 13.8% | 0/4 | FAIL |
| 12 | `volume_breakout` | 56.5 | p47 | 0.50 | 0.44 | 1.09 | 94 | 13.8% | 0/4 | FAIL |
| 13 | `lob_maker` | 55.7 | p42 | 0.84 | 1.37 | 1.12 | 124 | 17.0% | 0/4 | FAIL |
| 14 | `cmf` | 54.3 | p38 | 0.68 | 0.74 | 1.10 | 119 | 19.8% | 0/4 | FAIL |
| 15 | `dema_cross` | 52.5 | p33 | 0.07 | 0.51 | 1.04 | 8 | 3.0% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +33.24% | 2.84 | 1.31 | 145 | 0/4 | FAIL |
| `supertrend_multi` | +27.21% | 3.01 | 1.41 | 103 | 0/4 | FAIL |
| `frama` | +25.05% | 2.62 | 1.45 | 74 | 0/4 | FAIL |
| `htf_ema` | +22.80% | 2.43 | 1.41 | 72 | 0/4 | FAIL |
| `momentum_quality` | +14.52% | 1.71 | 1.23 | 112 | 0/4 | FAIL |
| `elder_impulse` | +14.14% | 2.12 | 1.49 | 49 | 0/4 | FAIL |
| `volatility_cluster` | +10.87% | 1.61 | 1.25 | 81 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +9.75% | 1.11 | 1.17 | 82 | 0/4 | FAIL |
| `positional_scaling` | +9.43% | 2.04 | 1.63 | 29 | 0/4 | FAIL |
| `lob_maker` | +9.00% | 0.84 | 1.12 | 124 | 0/4 | FAIL |
| `price_cluster` | +6.89% | 1.12 | 1.25 | 42 | 0/4 | FAIL |
| `cmf` | +5.94% | 0.68 | 1.10 | 119 | 0/4 | FAIL |
| `value_area` | +3.84% | 1.12 | 1.42 | 22 | 0/4 | FAIL |
| `acceleration_band` | +3.43% | 0.38 | 1.09 | 99 | 0/4 | FAIL |
| `volume_breakout` | +2.91% | 0.50 | 1.09 | 94 | 0/4 | FAIL |
| `dema_cross` | +0.25% | 0.07 | 1.04 | 8 | 0/4 | FAIL |
| `relative_volume` | -0.91% | -0.05 | 1.04 | 63 | 0/4 | FAIL |
| `wick_reversal` | -1.16% | -1.26 | 0.00 | 1 | 0/4 | FAIL |
| `roc_ma_cross` | -2.03% | -0.48 | 0.98 | 38 | 0/4 | FAIL |
| `engulfing_zone` | -2.29% | -0.55 | 0.97 | 26 | 0/4 | FAIL |
| `linear_channel_rev` | -2.38% | -0.98 | 0.98 | 30 | 0/4 | FAIL |
| `narrow_range` | -11.51% | -1.55 | 0.90 | 105 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | profit_factor 1.30 < 1.5 (x1), mc_p_value 0.330 > 0.05 (우연 가능성) (x1), profit_factor 1.28 < 1.5 (x1) |
| `supertrend_multi` | mc_p_value 0.270 > 0.05 (우연 가능성) (x1), mc_p_value 0.300 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1) |
| `frama` | mc_p_value 0.278 > 0.05 (우연 가능성) (x1), profit_factor 1.44 < 1.5 (x1), mc_p_value 0.404 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 1.49 < 1.5 (x1), mc_p_value 0.366 > 0.05 (우연 가능성) (x1), mc_p_value 0.292 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 1.15 < 1.5 (x2), mc_p_value 0.434 > 0.05 (우연 가능성) (x1), mc_p_value 0.416 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | mc_p_value 0.340 > 0.05 (우연 가능성) (x1), mc_p_value 0.414 > 0.05 (우연 가능성) (x1), sharpe 0.23 < 1.0 (x1) |
| `volatility_cluster` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1), profit_factor 1.36 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe -0.07 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.484 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | mc_p_value 0.464 > 0.05 (우연 가능성) (x1), mc_p_value 0.382 > 0.05 (우연 가능성) (x1), sharpe 0.45 < 1.0 (x1) |
| `lob_maker` | sharpe 0.89 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), mc_p_value 0.488 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.430 > 0.05 (우연 가능성) (x1), sharpe 0.49 < 1.0 (x1) |
| `cmf` | max_drawdown 23.6% > 20% (x1), profit_factor 1.19 < 1.5 (x1), mc_p_value 0.450 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -0.60 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.510 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.07 < 1.5 (x2), profit_factor 1.38 < 1.5 (x1), mc_p_value 0.346 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -0.03 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1), mc_p_value 0.492 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe 0.85 < 1.0 (x1), profit_factor 1.31 < 1.5 (x1), trades 12 < 15 (x1) |
| `relative_volume` | sharpe 0.68 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.452 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | profit_factor 0.00 < 1.5 (x2), no trades generated (x2), sharpe -2.90 < 1.0 (x1) |
| `roc_ma_cross` | profit_factor 1.33 < 1.5 (x1), mc_p_value 0.438 > 0.05 (우연 가능성) (x1), sharpe 0.07 < 1.0 (x1) |
| `engulfing_zone` | sharpe -1.69 < 1.0 (x1), profit_factor 0.70 < 1.5 (x1), mc_p_value 0.506 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.05 < 1.5 | 4 |
| profit_factor 1.15 < 1.5 | 4 |
| profit_factor 1.07 < 1.5 | 4 |
| mc_p_value 0.340 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.10 < 1.5 | 3 |
| profit_factor 1.49 < 1.5 | 3 |
| profit_factor 1.41 < 1.5 | 3 |
| profit_factor 1.14 < 1.5 | 3 |
| mc_p_value 0.452 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.440 > 0.05 (우연 가능성) | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +8.14% -> $10,814
- **Top 5 균등배분**: +24.57% -> $12,457
