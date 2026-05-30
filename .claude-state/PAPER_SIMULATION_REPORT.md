# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-30T00:16:37.928483Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-30T00:20:26.857029Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1608588188, block=24)_
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
| 평균 수익률 | 2.87% |
| 최고 수익률 | 33.57% (supertrend_multi) |
| 최저 수익률 | -15.54% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +33.57% | 3.56 | 46.7% | 1.53 | 82 | 8.1% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +21.13% | 1.79 | 40.3% | 1.21 | 141 | 18.1% | 0/4 | FAIL |
| 3 | `cmf` | +20.91% | 1.94 | 41.8% | 1.28 | 98 | 12.1% | 0/4 | FAIL |
| 4 | `price_cluster` | +16.12% | 2.17 | 45.6% | 1.48 | 46 | 6.9% | 0/4 | FAIL |
| 5 | `momentum_quality` | +15.36% | 1.75 | 40.4% | 1.23 | 111 | 12.6% | 0/4 | FAIL |
| 6 | `volatility_cluster` | +12.85% | 1.88 | 42.6% | 1.34 | 73 | 10.0% | 0/4 | FAIL |
| 7 | `acceleration_band` | +6.14% | 0.77 | 38.3% | 1.12 | 103 | 13.2% | 0/4 | FAIL |
| 8 | `elder_impulse` | +4.71% | 0.75 | 41.8% | 1.17 | 59 | 12.0% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | +1.28% | 0.28 | 38.6% | 1.07 | 76 | 15.6% | 0/4 | FAIL |
| 10 | `dema_cross` | +1.06% | -0.27 | 36.0% | 1.30 | 10 | 4.5% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 77.6 | p100 | 3.56 | 2.12 | 1.53 | 82 | 8.1% | 0/4 | FAIL |
| 2 | `price_cluster` | 70.8 | p95 | 2.17 | 1.04 | 1.48 | 46 | 6.9% | 0/4 | FAIL |
| 3 | `cmf` | 69.7 | p90 | 1.94 | 1.11 | 1.28 | 98 | 12.1% | 0/4 | FAIL |
| 4 | `momentum_quality` | 68.2 | p85 | 1.75 | 1.49 | 1.23 | 111 | 12.6% | 0/4 | FAIL |
| 5 | `volatility_cluster` | 66.9 | p80 | 1.88 | 1.65 | 1.34 | 73 | 10.0% | 0/4 | FAIL |
| 6 | `price_action_momentum` | 66.8 | p76 | 1.79 | 1.94 | 1.21 | 141 | 18.1% | 0/4 | FAIL |
| 7 | `acceleration_band` | 62.6 | p71 | 0.77 | 0.96 | 1.12 | 103 | 13.2% | 0/4 | FAIL |
| 8 | `elder_impulse` | 57.4 | p66 | 0.75 | 1.51 | 1.17 | 59 | 12.0% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | 56.1 | p61 | 0.28 | 0.77 | 1.07 | 76 | 15.6% | 0/4 | FAIL |
| 10 | `frama` | 55.2 | p57 | -0.20 | 0.50 | 1.00 | 81 | 14.2% | 0/4 | FAIL |
| 11 | `positional_scaling` | 53.5 | p52 | 0.02 | 1.28 | 1.08 | 25 | 5.2% | 0/4 | FAIL |
| 12 | `volume_breakout` | 49.1 | p47 | -0.36 | 1.72 | 1.01 | 84 | 17.7% | 0/4 | FAIL |
| 13 | `dema_cross` | 48.0 | p42 | -0.27 | 3.13 | 1.30 | 10 | 4.5% | 0/4 | FAIL |
| 14 | `narrow_range` | 46.1 | p38 | -1.05 | 1.17 | 0.93 | 83 | 18.3% | 0/4 | FAIL |
| 15 | `roc_ma_cross` | 46.0 | p33 | -0.83 | 1.38 | 0.94 | 43 | 11.3% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +33.57% | 3.56 | 1.53 | 82 | 0/4 | FAIL |
| `price_action_momentum` | +21.13% | 1.79 | 1.21 | 141 | 0/4 | FAIL |
| `cmf` | +20.91% | 1.94 | 1.28 | 98 | 0/4 | FAIL |
| `price_cluster` | +16.12% | 2.17 | 1.48 | 46 | 0/4 | FAIL |
| `momentum_quality` | +15.36% | 1.75 | 1.23 | 111 | 0/4 | FAIL |
| `volatility_cluster` | +12.85% | 1.88 | 1.34 | 73 | 0/4 | FAIL |
| `acceleration_band` | +6.14% | 0.77 | 1.12 | 103 | 0/4 | FAIL |
| `elder_impulse` | +4.71% | 0.75 | 1.17 | 59 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +1.28% | 0.28 | 1.07 | 76 | 0/4 | FAIL |
| `dema_cross` | +1.06% | -0.27 | 1.30 | 10 | 0/4 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `positional_scaling` | -0.17% | 0.02 | 1.08 | 25 | 0/4 | FAIL |
| `frama` | -2.92% | -0.20 | 1.00 | 81 | 0/4 | FAIL |
| `volume_breakout` | -3.25% | -0.36 | 1.01 | 84 | 0/4 | FAIL |
| `roc_ma_cross` | -4.01% | -0.83 | 0.94 | 43 | 0/4 | FAIL |
| `linear_channel_rev` | -5.36% | -1.84 | 0.79 | 28 | 0/4 | FAIL |
| `relative_volume` | -5.46% | -1.06 | 0.92 | 58 | 0/4 | FAIL |
| `value_area` | -5.81% | -1.84 | 0.71 | 23 | 0/4 | FAIL |
| `narrow_range` | -7.81% | -1.05 | 0.93 | 83 | 0/4 | FAIL |
| `htf_ema` | -8.25% | -1.02 | 0.93 | 75 | 0/4 | FAIL |
| `engulfing_zone` | -11.39% | -2.91 | 0.55 | 21 | 0/4 | FAIL |
| `lob_maker` | -15.54% | -1.37 | 0.91 | 115 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | mc_p_value 0.293 > 0.05 (우연 가능성) (x1), mc_p_value 0.201 > 0.05 (우연 가능성) (x1), profit_factor 1.46 < 1.5 (x1) |
| `price_action_momentum` | sharpe -0.91 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1), mc_p_value 0.548 > 0.05 (우연 가능성) (x1) |
| `cmf` | sharpe 0.46 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1), mc_p_value 0.490 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe 0.72 < 1.0 (x1), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.491 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | sharpe -0.16 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.503 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -0.43 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1), mc_p_value 0.516 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.17 < 1.5 (x1), mc_p_value 0.456 > 0.05 (우연 가능성) (x1), sharpe -0.42 < 1.0 (x1) |
| `elder_impulse` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.407 > 0.05 (우연 가능성) (x1), profit_factor 1.48 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe 0.19 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1), mc_p_value 0.546 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | trades 10 < 15 (x2), profit_factor 1.47 < 1.5 (x1), sharpe -5.48 < 1.0 (x1) |
| `wick_reversal` | no trades generated (x4) |
| `positional_scaling` | sharpe 0.99 < 1.0 (x1), profit_factor 1.29 < 1.5 (x1), mc_p_value 0.457 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe -0.13 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1), mc_p_value 0.484 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -2.75 < 1.0 (x1), max_drawdown 25.7% > 20% (x1), profit_factor 0.75 < 1.5 (x1) |
| `roc_ma_cross` | profit_factor 0.78 < 1.5 (x2), sharpe -1.76 < 1.0 (x1), mc_p_value 0.552 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -3.27 < 1.0 (x1), profit_factor 0.51 < 1.5 (x1), mc_p_value 0.600 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | mc_p_value 0.518 > 0.05 (우연 가능성) (x2), sharpe -4.31 < 1.0 (x1), max_drawdown 24.9% > 20% (x1) |
| `value_area` | sharpe -1.40 < 1.0 (x1), profit_factor 0.77 < 1.5 (x1), mc_p_value 0.560 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | sharpe 0.27 < 1.0 (x1), profit_factor 1.07 < 1.5 (x1), mc_p_value 0.499 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | sharpe -1.71 < 1.0 (x1), max_drawdown 25.9% > 20% (x1), profit_factor 0.82 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 4 |
| profit_factor 0.83 < 1.5 | 3 |
| sharpe -0.01 < 1.0 | 3 |
| profit_factor 1.03 < 1.5 | 3 |
| mc_p_value 0.540 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.08 < 1.5 | 2 |
| sharpe -0.91 < 1.0 | 2 |
| mc_p_value 0.548 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.44 < 1.5 | 2 |
| mc_p_value 0.464 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +2.87% -> $10,287
- **Top 5 균등배분**: +21.42% -> $12,142


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-30T00:24:18.733259Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=1888882645, block=24)_
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
| 평균 수익률 | 13.16% |
| 최고 수익률 | 74.69% (price_action_momentum) |
| 최저 수익률 | -17.36% (cmf) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +74.69% | 4.82 | 46.0% | 1.53 | 160 | 13.6% | 0/4 | FAIL |
| 2 | `momentum_quality` | +58.28% | 4.81 | 47.4% | 1.59 | 130 | 9.5% | 0/4 | FAIL |
| 3 | `supertrend_multi` | +48.56% | 4.33 | 45.7% | 1.55 | 126 | 12.5% | 0/4 | FAIL |
| 4 | `acceleration_band` | +38.70% | 3.41 | 44.7% | 1.52 | 96 | 9.8% | 0/4 | FAIL |
| 5 | `volatility_cluster` | +26.79% | 2.97 | 45.2% | 1.47 | 91 | 10.3% | 0/4 | FAIL |
| 6 | `narrow_range` | +20.20% | 2.44 | 43.2% | 1.36 | 97 | 9.7% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | +10.07% | 0.85 | 39.8% | 1.16 | 77 | 16.2% | 0/4 | FAIL |
| 8 | `volume_breakout` | +9.17% | 1.10 | 40.3% | 1.16 | 88 | 17.0% | 0/4 | FAIL |
| 9 | `roc_ma_cross` | +8.02% | 1.74 | 45.2% | 1.49 | 35 | 6.3% | 0/4 | FAIL |
| 10 | `htf_ema` | +7.56% | 0.93 | 41.0% | 1.18 | 66 | 14.3% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 64.3 | p100 | 4.82 | 1.32 | 1.53 | 160 | 13.6% | 0/4 | FAIL |
| 2 | `momentum_quality` | 64.2 | p95 | 4.81 | 1.21 | 1.59 | 130 | 9.5% | 0/4 | FAIL |
| 3 | `wick_reversal` | 60.8 | p90 | 0.50 | 0.86 | 250.00 | 0 | 0.0% | 0/4 | FAIL |
| 4 | `supertrend_multi` | 59.4 | p85 | 4.33 | 1.40 | 1.55 | 126 | 12.5% | 0/4 | FAIL |
| 5 | `acceleration_band` | 53.1 | p80 | 3.41 | 1.64 | 1.52 | 96 | 9.8% | 0/4 | FAIL |
| 6 | `narrow_range` | 52.8 | p76 | 2.44 | 0.84 | 1.36 | 97 | 9.7% | 0/4 | FAIL |
| 7 | `volatility_cluster` | 47.1 | p71 | 2.97 | 2.43 | 1.47 | 91 | 10.3% | 0/4 | FAIL |
| 8 | `roc_ma_cross` | 43.7 | p66 | 1.74 | 1.34 | 1.49 | 35 | 6.3% | 0/4 | FAIL |
| 9 | `positional_scaling` | 43.2 | p61 | 0.90 | 0.58 | 1.24 | 26 | 5.3% | 0/4 | FAIL |
| 10 | `volume_breakout` | 42.5 | p57 | 1.10 | 0.81 | 1.16 | 88 | 17.0% | 0/4 | FAIL |
| 11 | `elder_impulse` | 40.9 | p52 | 0.72 | 0.92 | 1.16 | 50 | 9.5% | 0/4 | FAIL |
| 12 | `htf_ema` | 38.2 | p47 | 0.93 | 1.50 | 1.18 | 66 | 14.3% | 0/4 | FAIL |
| 13 | `relative_volume` | 37.4 | p42 | 0.88 | 1.88 | 1.21 | 51 | 9.8% | 0/4 | FAIL |
| 14 | `value_area` | 36.5 | p38 | 0.50 | 1.54 | 1.31 | 18 | 5.5% | 0/4 | FAIL |
| 15 | `order_flow_imbalance_v2` | 35.0 | p33 | 0.85 | 2.15 | 1.16 | 77 | 16.2% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +74.69% | 4.82 | 1.53 | 160 | 0/4 | FAIL |
| `momentum_quality` | +58.28% | 4.81 | 1.59 | 130 | 0/4 | FAIL |
| `supertrend_multi` | +48.56% | 4.33 | 1.55 | 126 | 0/4 | FAIL |
| `acceleration_band` | +38.70% | 3.41 | 1.52 | 96 | 0/4 | FAIL |
| `volatility_cluster` | +26.79% | 2.97 | 1.47 | 91 | 0/4 | FAIL |
| `narrow_range` | +20.20% | 2.44 | 1.36 | 97 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +10.07% | 0.85 | 1.16 | 77 | 0/4 | FAIL |
| `volume_breakout` | +9.17% | 1.10 | 1.16 | 88 | 0/4 | FAIL |
| `roc_ma_cross` | +8.02% | 1.74 | 1.49 | 35 | 0/4 | FAIL |
| `htf_ema` | +7.56% | 0.93 | 1.18 | 66 | 0/4 | FAIL |
| `frama` | +6.40% | 0.67 | 1.15 | 80 | 0/4 | FAIL |
| `price_cluster` | +5.37% | 0.44 | 1.37 | 36 | 0/4 | FAIL |
| `relative_volume` | +5.29% | 0.88 | 1.21 | 51 | 0/4 | FAIL |
| `elder_impulse` | +4.23% | 0.72 | 1.16 | 50 | 0/4 | FAIL |
| `positional_scaling` | +3.62% | 0.90 | 1.24 | 26 | 0/4 | FAIL |
| `value_area` | +1.51% | 0.50 | 1.31 | 18 | 0/4 | FAIL |
| `wick_reversal` | +0.72% | 0.50 | 250.00 | 0 | 0/4 | FAIL |
| `dema_cross` | -2.13% | -0.86 | 0.81 | 11 | 0/4 | FAIL |
| `engulfing_zone` | -5.90% | -1.26 | 0.81 | 23 | 0/4 | FAIL |
| `lob_maker` | -6.00% | -0.44 | 0.99 | 124 | 0/4 | FAIL |
| `linear_channel_rev` | -8.25% | -2.45 | 0.68 | 31 | 0/4 | FAIL |
| `cmf` | -17.36% | -1.46 | 0.90 | 124 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.282 > 0.05 (우연 가능성) (x1), mc_p_value 0.150 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.308 > 0.05 (우연 가능성) (x1), mc_p_value 0.232 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | mc_p_value 0.184 > 0.05 (우연 가능성) (x1), mc_p_value 0.205 > 0.05 (우연 가능성) (x1), profit_factor 1.36 < 1.5 (x1) |
| `acceleration_band` | mc_p_value 0.292 > 0.05 (우연 가능성) (x1), mc_p_value 0.270 > 0.05 (우연 가능성) (x1), profit_factor 1.46 < 1.5 (x1) |
| `volatility_cluster` | mc_p_value 0.341 > 0.05 (우연 가능성) (x1), mc_p_value 0.239 > 0.05 (우연 가능성) (x1), profit_factor 1.44 < 1.5 (x1) |
| `narrow_range` | profit_factor 1.22 < 1.5 (x1), mc_p_value 0.429 > 0.05 (우연 가능성) (x1), profit_factor 1.48 < 1.5 (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.37 < 1.5 (x2), mc_p_value 0.366 > 0.05 (우연 가능성) (x1), mc_p_value 0.381 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 1.21 < 1.5 (x1), mc_p_value 0.446 > 0.05 (우연 가능성) (x1), profit_factor 1.27 < 1.5 (x1) |
| `roc_ma_cross` | sharpe 0.36 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1), mc_p_value 0.473 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 1.21 < 1.5 (x1), mc_p_value 0.455 > 0.05 (우연 가능성) (x1), sharpe -1.27 < 1.0 (x1) |
| `frama` | sharpe -0.17 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.516 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -0.02 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.530 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | sharpe 0.49 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1), mc_p_value 0.470 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | profit_factor 1.41 < 1.5 (x1), mc_p_value 0.432 > 0.05 (우연 가능성) (x1), sharpe 0.93 < 1.0 (x1) |
| `positional_scaling` | sharpe 0.46 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.492 > 0.05 (우연 가능성) (x1) |
| `value_area` | profit_factor 1.33 < 1.5 (x1), mc_p_value 0.452 > 0.05 (우연 가능성) (x1), trades 13 < 15 (x1) |
| `wick_reversal` | no trades generated (x3), trades 1 < 15 (x1) |
| `dema_cross` | sharpe -0.79 < 1.0 (x1), profit_factor 0.78 < 1.5 (x1), trades 10 < 15 (x1) |
| `engulfing_zone` | sharpe 0.04 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1), mc_p_value 0.498 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | sharpe 0.64 < 1.0 (x1), max_drawdown 21.7% > 20% (x1), profit_factor 1.09 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.33 < 1.5 | 3 |
| profit_factor 1.12 < 1.5 | 3 |
| profit_factor 1.10 < 1.5 | 3 |
| mc_p_value 0.504 > 0.05 (우연 가능성) | 3 |
| no trades generated | 3 |
| profit_factor 0.93 < 1.5 | 2 |
| profit_factor 1.48 < 1.5 | 2 |
| profit_factor 1.37 < 1.5 | 2 |
| profit_factor 1.15 < 1.5 | 2 |
| sharpe -2.67 < 1.0 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +13.16% -> $11,316
- **Top 5 균등배분**: +49.41% -> $14,941


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-30T00:28:10.502123Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=2052014702, block=24)_
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
| 평균 수익률 | 17.11% |
| 최고 수익률 | 65.50% (momentum_quality) |
| 최저 수익률 | -8.39% (elder_impulse) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +65.50% | 5.34 | 48.7% | 1.73 | 132 | 9.4% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +57.55% | 3.92 | 43.5% | 1.46 | 161 | 14.7% | 0/4 | FAIL |
| 3 | `acceleration_band` | +51.54% | 4.25 | 47.1% | 1.71 | 100 | 12.4% | 0/4 | FAIL |
| 4 | `cmf` | +29.95% | 2.24 | 42.6% | 1.29 | 123 | 18.1% | 0/4 | FAIL |
| 5 | `order_flow_imbalance_v2` | +29.94% | 2.86 | 45.6% | 1.43 | 82 | 9.8% | 0/4 | FAIL |
| 6 | `roc_ma_cross` | +25.01% | 4.07 | 54.2% | 2.18 | 46 | 7.6% | 0/4 | FAIL |
| 7 | `htf_ema` | +19.46% | 2.13 | 42.3% | 1.35 | 74 | 13.6% | 0/4 | FAIL |
| 8 | `supertrend_multi` | +17.73% | 2.11 | 40.6% | 1.30 | 115 | 13.0% | 0/4 | FAIL |
| 9 | `narrow_range` | +17.30% | 2.01 | 42.6% | 1.28 | 101 | 10.9% | 0/4 | FAIL |
| 10 | `lob_maker` | +17.23% | 1.49 | 39.9% | 1.18 | 123 | 17.9% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 72.8 | p100 | 5.34 | 1.50 | 1.73 | 132 | 9.4% | 0/4 | FAIL |
| 2 | `positional_scaling` | 68.3 | p95 | 3.30 | 0.43 | 1.96 | 33 | 4.1% | 0/4 | FAIL |
| 3 | `roc_ma_cross` | 63.0 | p90 | 4.07 | 1.80 | 2.18 | 46 | 7.6% | 0/4 | FAIL |
| 4 | `acceleration_band` | 60.9 | p85 | 4.25 | 1.72 | 1.71 | 100 | 12.4% | 0/4 | FAIL |
| 5 | `price_action_momentum` | 60.3 | p80 | 3.92 | 1.82 | 1.46 | 161 | 14.7% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | 59.4 | p76 | 2.86 | 0.70 | 1.43 | 82 | 9.8% | 0/4 | FAIL |
| 7 | `dema_cross` | 56.7 | p71 | 1.75 | 0.86 | 1.88 | 10 | 3.0% | 0/4 | FAIL |
| 8 | `volume_breakout` | 53.5 | p66 | 1.76 | 0.83 | 1.26 | 90 | 9.1% | 0/4 | FAIL |
| 9 | `supertrend_multi` | 53.2 | p61 | 2.11 | 1.02 | 1.30 | 115 | 13.0% | 0/4 | FAIL |
| 10 | `narrow_range` | 53.0 | p57 | 2.01 | 1.03 | 1.28 | 101 | 10.9% | 0/4 | FAIL |
| 11 | `htf_ema` | 49.8 | p52 | 2.13 | 0.97 | 1.35 | 74 | 13.6% | 0/4 | FAIL |
| 12 | `value_area` | 48.1 | p47 | 0.61 | 0.36 | 1.17 | 26 | 5.2% | 0/4 | FAIL |
| 13 | `cmf` | 47.4 | p42 | 2.24 | 1.43 | 1.29 | 123 | 18.1% | 0/4 | FAIL |
| 14 | `lob_maker` | 46.3 | p38 | 1.49 | 0.96 | 1.18 | 123 | 17.9% | 0/4 | FAIL |
| 15 | `volatility_cluster` | 42.4 | p33 | 0.98 | 1.35 | 1.17 | 82 | 12.3% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +65.50% | 5.34 | 1.73 | 132 | 0/4 | FAIL |
| `price_action_momentum` | +57.55% | 3.92 | 1.46 | 161 | 0/4 | FAIL |
| `acceleration_band` | +51.54% | 4.25 | 1.71 | 100 | 0/4 | FAIL |
| `cmf` | +29.95% | 2.24 | 1.29 | 123 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +29.94% | 2.86 | 1.43 | 82 | 0/4 | FAIL |
| `roc_ma_cross` | +25.01% | 4.07 | 2.18 | 46 | 0/4 | FAIL |
| `htf_ema` | +19.46% | 2.13 | 1.35 | 74 | 0/4 | FAIL |
| `supertrend_multi` | +17.73% | 2.11 | 1.30 | 115 | 0/4 | FAIL |
| `narrow_range` | +17.30% | 2.01 | 1.28 | 101 | 0/4 | FAIL |
| `lob_maker` | +17.23% | 1.49 | 1.18 | 123 | 0/4 | FAIL |
| `positional_scaling` | +16.39% | 3.30 | 1.96 | 33 | 0/4 | FAIL |
| `volume_breakout` | +15.74% | 1.76 | 1.26 | 90 | 0/4 | FAIL |
| `volatility_cluster` | +6.66% | 0.98 | 1.17 | 82 | 0/4 | FAIL |
| `price_cluster` | +6.59% | 0.92 | 1.21 | 42 | 0/4 | FAIL |
| `frama` | +4.90% | 0.68 | 1.13 | 77 | 0/4 | FAIL |
| `dema_cross` | +4.54% | 1.75 | 1.88 | 10 | 0/4 | FAIL |
| `value_area` | +2.00% | 0.61 | 1.17 | 26 | 0/4 | FAIL |
| `linear_channel_rev` | +0.68% | 0.31 | 1.15 | 28 | 0/4 | FAIL |
| `wick_reversal` | -0.40% | -0.51 | 0.00 | 0 | 0/4 | FAIL |
| `engulfing_zone` | -0.66% | -0.26 | 1.04 | 17 | 0/4 | FAIL |
| `relative_volume` | -2.88% | -0.45 | 0.97 | 54 | 0/4 | FAIL |
| `elder_impulse` | -8.39% | -1.41 | 0.88 | 54 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | mc_p_value 0.255 > 0.05 (우연 가능성) (x1), mc_p_value 0.157 > 0.05 (우연 가능성) (x1), mc_p_value 0.163 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe 0.88 < 1.0 (x1), max_drawdown 25.9% > 20% (x1), profit_factor 1.11 < 1.5 (x1) |
| `acceleration_band` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.405 > 0.05 (우연 가능성) (x1), mc_p_value 0.255 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.29 < 1.5 (x2), sharpe 0.06 < 1.0 (x1), max_drawdown 23.1% > 20% (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.349 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1), mc_p_value 0.345 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 1.32 < 1.5 (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1), mc_p_value 0.381 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 1.21 < 1.5 (x1), mc_p_value 0.491 > 0.05 (우연 가능성) (x1), mc_p_value 0.365 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | profit_factor 1.13 < 1.5 (x1), mc_p_value 0.429 > 0.05 (우연 가능성) (x1), profit_factor 1.16 < 1.5 (x1) |
| `narrow_range` | sharpe 0.63 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1), mc_p_value 0.485 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.16 < 1.5 (x1), mc_p_value 0.452 > 0.05 (우연 가능성) (x1), profit_factor 1.36 < 1.5 (x1) |
| `positional_scaling` | mc_p_value 0.418 > 0.05 (우연 가능성) (x2), mc_p_value 0.388 > 0.05 (우연 가능성) (x1), mc_p_value 0.405 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | sharpe 0.66 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1), mc_p_value 0.461 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -0.72 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1), mc_p_value 0.553 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.457 > 0.05 (우연 가능성) (x1), sharpe -1.34 < 1.0 (x1) |
| `frama` | sharpe 0.90 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.449 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | trades 12 < 15 (x2), sharpe 0.52 < 1.0 (x1), profit_factor 1.22 < 1.5 (x1) |
| `value_area` | mc_p_value 0.480 > 0.05 (우연 가능성) (x2), sharpe 0.73 < 1.0 (x1), profit_factor 1.22 < 1.5 (x1) |
| `linear_channel_rev` | sharpe -0.66 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.517 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x3), sharpe -2.06 < 1.0 (x1), profit_factor 0.00 < 1.5 (x1) |
| `engulfing_zone` | sharpe -1.21 < 1.0 (x1), profit_factor 0.74 < 1.5 (x1), profit_factor 1.47 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.13 < 1.5 | 4 |
| profit_factor 1.11 < 1.5 | 3 |
| profit_factor 1.24 < 1.5 | 3 |
| mc_p_value 0.418 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.28 < 1.5 | 3 |
| profit_factor 1.22 < 1.5 | 3 |
| no trades generated | 3 |
| mc_p_value 0.255 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.43 < 1.5 | 2 |
| mc_p_value 0.429 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +17.11% -> $11,711
- **Top 5 균등배분**: +46.90% -> $14,690
