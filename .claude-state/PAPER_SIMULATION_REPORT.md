# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-28T00:30:09.366241Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-28T00:32:24.410815Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=630436589, block=36)_
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
| 평균 수익률 | 13.22% |
| 최고 수익률 | 49.03% (price_action_momentum) |
| 최저 수익률 | -9.55% (narrow_range) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +49.03% | 3.81 | 45.7% | 1.42 | 144 | 11.3% | 0/4 | FAIL |
| 2 | `momentum_quality` | +38.24% | 3.91 | 45.8% | 1.54 | 108 | 11.1% | 0/4 | FAIL |
| 3 | `acceleration_band` | +36.86% | 3.54 | 46.1% | 1.53 | 95 | 8.8% | 0/4 | FAIL |
| 4 | `order_flow_imbalance_v2` | +35.51% | 3.24 | 46.5% | 1.51 | 79 | 12.1% | 0/4 | FAIL |
| 5 | `supertrend_multi` | +33.07% | 3.35 | 45.1% | 1.48 | 106 | 11.5% | 0/4 | FAIL |
| 6 | `volatility_cluster` | +20.85% | 2.74 | 44.7% | 1.43 | 84 | 6.8% | 0/4 | FAIL |
| 7 | `volume_breakout` | +19.55% | 2.12 | 42.7% | 1.31 | 88 | 15.1% | 0/4 | FAIL |
| 8 | `htf_ema` | +18.50% | 2.09 | 44.4% | 1.39 | 69 | 10.7% | 0/4 | FAIL |
| 9 | `cmf` | +12.06% | 1.18 | 39.7% | 1.15 | 119 | 15.4% | 0/4 | FAIL |
| 10 | `elder_impulse` | +9.52% | 1.40 | 41.4% | 1.28 | 55 | 9.5% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 71.1 | p100 | 3.91 | 0.41 | 1.54 | 108 | 11.1% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 70.9 | p95 | 3.81 | 0.99 | 1.42 | 144 | 11.3% | 0/4 | FAIL |
| 3 | `dema_cross` | 70.3 | p90 | 3.16 | 1.17 | 3.48 | 12 | 2.9% | 0/4 | FAIL |
| 4 | `acceleration_band` | 68.7 | p85 | 3.54 | 0.56 | 1.53 | 95 | 8.8% | 0/4 | FAIL |
| 5 | `volatility_cluster` | 64.5 | p80 | 2.74 | 0.52 | 1.43 | 84 | 6.8% | 0/4 | FAIL |
| 6 | `supertrend_multi` | 62.3 | p76 | 3.35 | 1.55 | 1.48 | 106 | 11.5% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | 60.7 | p71 | 3.24 | 1.12 | 1.51 | 79 | 12.1% | 0/4 | FAIL |
| 8 | `volume_breakout` | 54.6 | p66 | 2.12 | 0.83 | 1.31 | 88 | 15.1% | 0/4 | FAIL |
| 9 | `cmf` | 53.4 | p61 | 1.18 | 0.51 | 1.15 | 119 | 15.4% | 0/4 | FAIL |
| 10 | `linear_channel_rev` | 52.5 | p57 | 1.70 | 1.09 | 1.45 | 32 | 5.1% | 0/4 | FAIL |
| 11 | `htf_ema` | 51.6 | p52 | 2.09 | 1.70 | 1.39 | 69 | 10.7% | 0/4 | FAIL |
| 12 | `elder_impulse` | 49.3 | p47 | 1.40 | 1.19 | 1.28 | 55 | 9.5% | 0/4 | FAIL |
| 13 | `lob_maker` | 46.6 | p42 | 0.72 | 0.76 | 1.10 | 123 | 21.2% | 0/4 | FAIL |
| 14 | `roc_ma_cross` | 43.5 | p38 | 0.68 | 1.52 | 1.20 | 34 | 6.7% | 0/4 | FAIL |
| 15 | `frama` | 42.3 | p33 | 0.37 | 1.25 | 1.09 | 84 | 15.1% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +49.03% | 3.81 | 1.42 | 144 | 0/4 | FAIL |
| `momentum_quality` | +38.24% | 3.91 | 1.54 | 108 | 0/4 | FAIL |
| `acceleration_band` | +36.86% | 3.54 | 1.53 | 95 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +35.51% | 3.24 | 1.51 | 79 | 0/4 | FAIL |
| `supertrend_multi` | +33.07% | 3.35 | 1.48 | 106 | 0/4 | FAIL |
| `volatility_cluster` | +20.85% | 2.74 | 1.43 | 84 | 0/4 | FAIL |
| `volume_breakout` | +19.55% | 2.12 | 1.31 | 88 | 0/4 | FAIL |
| `htf_ema` | +18.50% | 2.09 | 1.39 | 69 | 0/4 | FAIL |
| `cmf` | +12.06% | 1.18 | 1.15 | 119 | 0/4 | FAIL |
| `elder_impulse` | +9.52% | 1.40 | 1.28 | 55 | 0/4 | FAIL |
| `dema_cross` | +8.83% | 3.16 | 3.48 | 12 | 0/4 | FAIL |
| `linear_channel_rev` | +7.17% | 1.70 | 1.45 | 32 | 0/4 | FAIL |
| `price_cluster` | +6.99% | 1.10 | 1.32 | 40 | 0/4 | FAIL |
| `lob_maker` | +6.37% | 0.72 | 1.10 | 123 | 0/4 | FAIL |
| `relative_volume` | +6.04% | 0.96 | 1.24 | 54 | 0/4 | FAIL |
| `roc_ma_cross` | +3.13% | 0.68 | 1.20 | 34 | 0/4 | FAIL |
| `frama` | +2.42% | 0.37 | 1.09 | 84 | 0/4 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `positional_scaling` | -0.18% | -0.15 | 1.11 | 30 | 0/4 | FAIL |
| `value_area` | -5.52% | -2.23 | 0.61 | 17 | 0/4 | FAIL |
| `engulfing_zone` | -8.06% | -1.92 | 0.66 | 20 | 0/4 | FAIL |
| `narrow_range` | -9.55% | -1.25 | 0.92 | 96 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.346 > 0.05 (우연 가능성) (x1), profit_factor 1.49 < 1.5 (x1) |
| `momentum_quality` | profit_factor 1.49 < 1.5 (x1), mc_p_value 0.294 > 0.05 (우연 가능성) (x1), profit_factor 1.46 < 1.5 (x1) |
| `acceleration_band` | mc_p_value 0.312 > 0.05 (우연 가능성) (x1), profit_factor 1.44 < 1.5 (x1), mc_p_value 0.390 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.372 > 0.05 (우연 가능성) (x1), profit_factor 1.50 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.38 < 1.5 (x1), mc_p_value 0.382 > 0.05 (우연 가능성) (x1), profit_factor 1.21 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.30 < 1.5 (x1), mc_p_value 0.400 > 0.05 (우연 가능성) (x1), profit_factor 1.40 < 1.5 (x1) |
| `volume_breakout` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.412 > 0.05 (우연 가능성) (x1), profit_factor 1.16 < 1.5 (x1) |
| `htf_ema` | mc_p_value 0.426 > 0.05 (우연 가능성) (x1), mc_p_value 0.354 > 0.05 (우연 가능성) (x1), profit_factor 1.34 < 1.5 (x1) |
| `cmf` | sharpe 0.62 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1), mc_p_value 0.466 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | profit_factor 1.39 < 1.5 (x1), mc_p_value 0.444 > 0.05 (우연 가능성) (x1), mc_p_value 0.400 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | trades 13 < 15 (x2), trades 8 < 15 (x1), trades 12 < 15 (x1) |
| `linear_channel_rev` | sharpe -0.12 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.504 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.426 > 0.05 (우연 가능성) (x1), profit_factor 1.44 < 1.5 (x1) |
| `lob_maker` | max_drawdown 20.7% > 20% (x2), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.462 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | profit_factor 1.19 < 1.5 (x1), mc_p_value 0.466 > 0.05 (우연 가능성) (x1), sharpe -2.34 < 1.0 (x1) |
| `roc_ma_cross` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.466 > 0.05 (우연 가능성) (x1), mc_p_value 0.460 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe -1.09 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.578 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x4) |
| `positional_scaling` | sharpe -0.54 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1), mc_p_value 0.502 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -2.94 < 1.0 (x1), profit_factor 0.48 < 1.5 (x1), mc_p_value 0.518 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.374 > 0.05 (우연 가능성) | 4 |
| mc_p_value 0.400 > 0.05 (우연 가능성) | 4 |
| no trades generated | 4 |
| profit_factor 1.49 < 1.5 | 3 |
| profit_factor 1.50 < 1.5 | 3 |
| mc_p_value 0.466 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.31 < 1.5 | 2 |
| profit_factor 1.46 < 1.5 | 2 |
| mc_p_value 0.352 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.44 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +13.22% -> $11,322
- **Top 5 균등배분**: +38.54% -> $13,854


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-28T00:34:41.037115Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=961444876, block=36)_
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
| 평균 수익률 | 14.82% |
| 최고 수익률 | 45.41% (cmf) |
| 최저 수익률 | -3.79% (dema_cross) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `cmf` | +45.41% | 2.98 | 43.5% | 1.36 | 129 | 15.3% | 0/4 | FAIL |
| 2 | `momentum_quality` | +40.49% | 3.85 | 48.1% | 1.55 | 108 | 8.3% | 0/4 | FAIL |
| 3 | `supertrend_multi` | +35.99% | 3.36 | 44.4% | 1.40 | 140 | 10.8% | 0/4 | FAIL |
| 4 | `lob_maker` | +34.50% | 2.65 | 44.0% | 1.32 | 119 | 15.0% | 0/4 | FAIL |
| 5 | `narrow_range` | +24.32% | 2.81 | 44.6% | 1.45 | 88 | 8.7% | 0/4 | FAIL |
| 6 | `price_action_momentum` | +23.75% | 1.52 | 41.4% | 1.20 | 150 | 19.0% | 0/4 | FAIL |
| 7 | `volume_breakout` | +18.81% | 1.78 | 42.1% | 1.29 | 90 | 14.6% | 0/4 | FAIL |
| 8 | `elder_impulse` | +18.14% | 2.44 | 43.6% | 1.44 | 65 | 9.4% | 0/4 | FAIL |
| 9 | `htf_ema` | +17.87% | 2.06 | 42.5% | 1.34 | 70 | 10.0% | 0/4 | FAIL |
| 10 | `positional_scaling` | +15.74% | 3.34 | 54.9% | 2.29 | 26 | 4.0% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `positional_scaling` | 74.0 | p100 | 3.34 | 1.37 | 2.29 | 26 | 4.0% | 0/4 | FAIL |
| 2 | `supertrend_multi` | 73.8 | p95 | 3.36 | 1.03 | 1.40 | 140 | 10.8% | 0/4 | FAIL |
| 3 | `momentum_quality` | 72.4 | p90 | 3.85 | 1.99 | 1.55 | 108 | 8.3% | 0/4 | FAIL |
| 4 | `narrow_range` | 65.5 | p85 | 2.81 | 1.56 | 1.45 | 88 | 8.7% | 0/4 | FAIL |
| 5 | `elder_impulse` | 64.4 | p80 | 2.44 | 0.64 | 1.44 | 65 | 9.4% | 0/4 | FAIL |
| 6 | `lob_maker` | 63.7 | p76 | 2.65 | 1.05 | 1.32 | 119 | 15.0% | 0/4 | FAIL |
| 7 | `cmf` | 63.2 | p71 | 2.98 | 1.84 | 1.36 | 129 | 15.3% | 0/4 | FAIL |
| 8 | `htf_ema` | 60.4 | p66 | 2.06 | 0.93 | 1.34 | 70 | 10.0% | 0/4 | FAIL |
| 9 | `linear_channel_rev` | 56.0 | p61 | 1.98 | 2.49 | 1.66 | 35 | 6.0% | 0/4 | FAIL |
| 10 | `volume_breakout` | 51.9 | p57 | 1.78 | 2.07 | 1.29 | 90 | 14.6% | 0/4 | FAIL |
| 11 | `frama` | 51.5 | p52 | 1.08 | 0.99 | 1.18 | 76 | 13.3% | 0/4 | FAIL |
| 12 | `price_action_momentum` | 48.3 | p47 | 1.52 | 3.01 | 1.20 | 150 | 19.0% | 0/4 | FAIL |
| 13 | `acceleration_band` | 47.9 | p42 | 1.02 | 1.75 | 1.17 | 107 | 17.1% | 0/4 | FAIL |
| 14 | `relative_volume` | 47.5 | p38 | 0.60 | 1.17 | 1.13 | 62 | 11.9% | 0/4 | FAIL |
| 15 | `volatility_cluster` | 47.0 | p33 | 0.50 | 1.67 | 1.12 | 80 | 11.4% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `cmf` | +45.41% | 2.98 | 1.36 | 129 | 0/4 | FAIL |
| `momentum_quality` | +40.49% | 3.85 | 1.55 | 108 | 0/4 | FAIL |
| `supertrend_multi` | +35.99% | 3.36 | 1.40 | 140 | 0/4 | FAIL |
| `lob_maker` | +34.50% | 2.65 | 1.32 | 119 | 0/4 | FAIL |
| `narrow_range` | +24.32% | 2.81 | 1.45 | 88 | 0/4 | FAIL |
| `price_action_momentum` | +23.75% | 1.52 | 1.20 | 150 | 0/4 | FAIL |
| `volume_breakout` | +18.81% | 1.78 | 1.29 | 90 | 0/4 | FAIL |
| `elder_impulse` | +18.14% | 2.44 | 1.44 | 65 | 0/4 | FAIL |
| `htf_ema` | +17.87% | 2.06 | 1.34 | 70 | 0/4 | FAIL |
| `positional_scaling` | +15.74% | 3.34 | 2.29 | 26 | 0/4 | FAIL |
| `linear_channel_rev` | +10.34% | 1.98 | 1.66 | 35 | 0/4 | FAIL |
| `acceleration_band` | +9.53% | 1.02 | 1.17 | 107 | 0/4 | FAIL |
| `frama` | +8.65% | 1.08 | 1.18 | 76 | 0/4 | FAIL |
| `price_cluster` | +7.83% | 1.06 | 1.26 | 42 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +6.68% | 0.76 | 1.13 | 84 | 0/4 | FAIL |
| `engulfing_zone` | +3.58% | 0.66 | 1.22 | 27 | 0/4 | FAIL |
| `volatility_cluster` | +3.50% | 0.50 | 1.12 | 80 | 0/4 | FAIL |
| `relative_volume` | +3.45% | 0.60 | 1.13 | 62 | 0/4 | FAIL |
| `roc_ma_cross` | +2.57% | 0.37 | 1.19 | 44 | 0/4 | FAIL |
| `wick_reversal` | -0.58% | -0.75 | 0.00 | 0 | 0/4 | FAIL |
| `value_area` | -0.73% | -0.30 | 0.97 | 18 | 0/4 | FAIL |
| `dema_cross` | -3.79% | -1.88 | 0.60 | 10 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `cmf` | mc_p_value 0.290 > 0.05 (우연 가능성) (x1), profit_factor 1.43 < 1.5 (x1), mc_p_value 0.312 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.180 > 0.05 (우연 가능성) (x1), mc_p_value 0.344 > 0.05 (우연 가능성) (x1), profit_factor 1.31 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.39 < 1.5 (x1), mc_p_value 0.314 > 0.05 (우연 가능성) (x1), profit_factor 1.40 < 1.5 (x1) |
| `lob_maker` | profit_factor 1.42 < 1.5 (x1), mc_p_value 0.322 > 0.05 (우연 가능성) (x1), sharpe 0.93 < 1.0 (x1) |
| `narrow_range` | mc_p_value 0.288 > 0.05 (우연 가능성) (x1), mc_p_value 0.334 > 0.05 (우연 가능성) (x1), sharpe 0.87 < 1.0 (x1) |
| `price_action_momentum` | mc_p_value 0.204 > 0.05 (우연 가능성) (x1), profit_factor 1.22 < 1.5 (x1), mc_p_value 0.390 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | mc_p_value 0.322 > 0.05 (우연 가능성) (x1), profit_factor 1.22 < 1.5 (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | profit_factor 1.32 < 1.5 (x1), mc_p_value 0.436 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1) |
| `htf_ema` | profit_factor 1.47 < 1.5 (x1), mc_p_value 0.404 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1) |
| `positional_scaling` | mc_p_value 0.466 > 0.05 (우연 가능성) (x1), mc_p_value 0.382 > 0.05 (우연 가능성) (x1), mc_p_value 0.408 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -0.28 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1), mc_p_value 0.478 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.36 < 1.5 (x1), mc_p_value 0.388 > 0.05 (우연 가능성) (x1), profit_factor 1.35 < 1.5 (x1) |
| `frama` | mc_p_value 0.476 > 0.05 (우연 가능성) (x2), sharpe -0.28 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1) |
| `price_cluster` | sharpe -1.63 < 1.0 (x1), profit_factor 0.78 < 1.5 (x1), mc_p_value 0.598 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.440 > 0.05 (우연 가능성) (x2), profit_factor 1.40 < 1.5 (x1), sharpe 0.38 < 1.0 (x1) |
| `engulfing_zone` | sharpe -0.69 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.554 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.49 < 1.5 (x1), mc_p_value 0.386 > 0.05 (우연 가능성) (x1), sharpe -1.14 < 1.0 (x1) |
| `relative_volume` | profit_factor 1.42 < 1.5 (x1), mc_p_value 0.470 > 0.05 (우연 가능성) (x1), sharpe 0.44 < 1.0 (x1) |
| `roc_ma_cross` | sharpe -1.67 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1), mc_p_value 0.550 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x3), sharpe -3.00 < 1.0 (x1), profit_factor 0.00 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.440 > 0.05 (우연 가능성) | 6 |
| profit_factor 0.99 < 1.5 | 4 |
| profit_factor 0.91 < 1.5 | 4 |
| profit_factor 1.09 < 1.5 | 3 |
| profit_factor 1.22 < 1.5 | 3 |
| profit_factor 1.11 < 1.5 | 3 |
| mc_p_value 0.480 > 0.05 (우연 가능성) | 3 |
| no trades generated | 3 |
| mc_p_value 0.426 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.344 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +14.82% -> $11,482
- **Top 5 균등배분**: +36.14% -> $13,614


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-28T00:36:55.239032Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=195275199, block=36)_
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
| 평균 수익률 | 13.79% |
| 최고 수익률 | 64.05% (price_action_momentum) |
| 최저 수익률 | -13.25% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +64.05% | 4.40 | 44.8% | 1.52 | 153 | 14.2% | 0/4 | FAIL |
| 2 | `momentum_quality` | +55.92% | 5.31 | 50.1% | 1.78 | 108 | 7.6% | 0/4 | FAIL |
| 3 | `cmf` | +47.13% | 3.14 | 44.5% | 1.41 | 117 | 16.3% | 0/4 | FAIL |
| 4 | `acceleration_band` | +37.50% | 2.97 | 46.2% | 1.52 | 97 | 14.4% | 0/4 | FAIL |
| 5 | `supertrend_multi` | +28.41% | 2.81 | 43.1% | 1.35 | 120 | 14.6% | 0/4 | FAIL |
| 6 | `volume_breakout` | +26.03% | 2.01 | 43.1% | 1.34 | 98 | 19.2% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | +20.66% | 1.86 | 42.0% | 1.30 | 82 | 17.1% | 0/4 | FAIL |
| 8 | `lob_maker` | +19.07% | 1.28 | 40.0% | 1.19 | 125 | 23.9% | 0/4 | FAIL |
| 9 | `volatility_cluster` | +13.01% | 1.77 | 42.6% | 1.31 | 78 | 10.2% | 0/4 | FAIL |
| 10 | `narrow_range` | +8.89% | 1.26 | 41.2% | 1.19 | 89 | 9.3% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 85.5 | p100 | 5.31 | 0.56 | 1.78 | 108 | 7.6% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 73.3 | p95 | 4.40 | 1.82 | 1.52 | 153 | 14.2% | 0/4 | FAIL |
| 3 | `cmf` | 60.6 | p90 | 3.14 | 2.04 | 1.41 | 117 | 16.3% | 0/4 | FAIL |
| 4 | `supertrend_multi` | 59.9 | p85 | 2.81 | 1.95 | 1.35 | 120 | 14.6% | 0/4 | FAIL |
| 5 | `acceleration_band` | 57.3 | p80 | 2.97 | 3.03 | 1.52 | 97 | 14.4% | 0/4 | FAIL |
| 6 | `narrow_range` | 55.4 | p76 | 1.26 | 0.80 | 1.19 | 89 | 9.3% | 0/4 | FAIL |
| 7 | `volatility_cluster` | 54.0 | p71 | 1.77 | 1.83 | 1.31 | 78 | 10.2% | 0/4 | FAIL |
| 8 | `linear_channel_rev` | 50.8 | p66 | 0.95 | 0.72 | 1.23 | 32 | 7.2% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | 49.3 | p61 | 1.86 | 2.07 | 1.30 | 82 | 17.1% | 0/4 | FAIL |
| 10 | `volume_breakout` | 46.9 | p57 | 2.01 | 3.19 | 1.34 | 98 | 19.2% | 0/4 | FAIL |
| 11 | `dema_cross` | 44.3 | p52 | 0.23 | 1.61 | 1.23 | 11 | 4.2% | 0/4 | FAIL |
| 12 | `price_cluster` | 43.7 | p47 | 0.22 | 0.77 | 1.08 | 36 | 10.1% | 0/4 | FAIL |
| 13 | `lob_maker` | 43.3 | p42 | 1.28 | 2.54 | 1.19 | 125 | 23.9% | 0/4 | FAIL |
| 14 | `elder_impulse` | 39.4 | p38 | -0.11 | 1.51 | 1.04 | 54 | 12.1% | 0/4 | FAIL |
| 15 | `htf_ema` | 39.2 | p33 | 0.52 | 1.95 | 1.12 | 74 | 19.3% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +64.05% | 4.40 | 1.52 | 153 | 0/4 | FAIL |
| `momentum_quality` | +55.92% | 5.31 | 1.78 | 108 | 0/4 | FAIL |
| `cmf` | +47.13% | 3.14 | 1.41 | 117 | 0/4 | FAIL |
| `acceleration_band` | +37.50% | 2.97 | 1.52 | 97 | 0/4 | FAIL |
| `supertrend_multi` | +28.41% | 2.81 | 1.35 | 120 | 0/4 | FAIL |
| `volume_breakout` | +26.03% | 2.01 | 1.34 | 98 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +20.66% | 1.86 | 1.30 | 82 | 0/4 | FAIL |
| `lob_maker` | +19.07% | 1.28 | 1.19 | 125 | 0/4 | FAIL |
| `volatility_cluster` | +13.01% | 1.77 | 1.31 | 78 | 0/4 | FAIL |
| `narrow_range` | +8.89% | 1.26 | 1.19 | 89 | 0/4 | FAIL |
| `htf_ema` | +5.09% | 0.52 | 1.12 | 74 | 0/4 | FAIL |
| `linear_channel_rev` | +3.79% | 0.95 | 1.23 | 32 | 0/4 | FAIL |
| `relative_volume` | +1.90% | 0.16 | 1.12 | 62 | 0/4 | FAIL |
| `dema_cross` | +0.89% | 0.23 | 1.23 | 11 | 0/4 | FAIL |
| `price_cluster` | +0.89% | 0.22 | 1.08 | 36 | 0/4 | FAIL |
| `wick_reversal` | -0.09% | -0.32 | 0.46 | 1 | 0/4 | FAIL |
| `elder_impulse` | -0.88% | -0.11 | 1.04 | 54 | 0/4 | FAIL |
| `roc_ma_cross` | -0.96% | -0.16 | 1.20 | 32 | 0/4 | FAIL |
| `engulfing_zone` | -4.39% | -1.06 | 0.85 | 21 | 0/4 | FAIL |
| `value_area` | -4.99% | -1.69 | 0.69 | 21 | 0/4 | FAIL |
| `positional_scaling` | -5.24% | -1.33 | 0.79 | 26 | 0/4 | FAIL |
| `frama` | -13.25% | -1.47 | 0.86 | 86 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.194 > 0.05 (우연 가능성) (x1), mc_p_value 0.246 > 0.05 (우연 가능성) (x1), profit_factor 1.17 < 1.5 (x1) |
| `momentum_quality` | mc_p_value 0.326 > 0.05 (우연 가능성) (x1), mc_p_value 0.274 > 0.05 (우연 가능성) (x1), mc_p_value 0.292 > 0.05 (우연 가능성) (x1) |
| `cmf` | max_drawdown 20.0% > 20% (x2), mc_p_value 0.246 > 0.05 (우연 가능성) (x1), mc_p_value 0.258 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | max_drawdown 22.3% > 20% (x2), mc_p_value 0.294 > 0.05 (우연 가능성) (x1), mc_p_value 0.290 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | mc_p_value 0.356 > 0.05 (우연 가능성) (x1), mc_p_value 0.264 > 0.05 (우연 가능성) (x1), sharpe 0.40 < 1.0 (x1) |
| `volume_breakout` | mc_p_value 0.318 > 0.05 (우연 가능성) (x2), sharpe -0.45 < 1.0 (x1), max_drawdown 22.0% > 20% (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.356 > 0.05 (우연 가능성) (x1), mc_p_value 0.338 > 0.05 (우연 가능성) (x1), sharpe 0.34 < 1.0 (x1) |
| `lob_maker` | profit_factor 1.40 < 1.5 (x1), mc_p_value 0.364 > 0.05 (우연 가능성) (x1), profit_factor 1.44 < 1.5 (x1) |
| `volatility_cluster` | sharpe 0.07 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1), mc_p_value 0.530 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.438 > 0.05 (우연 가능성) (x1), sharpe 0.75 < 1.0 (x1) |
| `htf_ema` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.392 > 0.05 (우연 가능성) (x1), profit_factor 1.30 < 1.5 (x1) |
| `linear_channel_rev` | profit_factor 1.07 < 1.5 (x2), sharpe 0.22 < 1.0 (x1), mc_p_value 0.494 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | mc_p_value 0.394 > 0.05 (우연 가능성) (x1), profit_factor 1.38 < 1.5 (x1), mc_p_value 0.418 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe -2.19 < 1.0 (x1), profit_factor 0.49 < 1.5 (x1), trades 11 < 15 (x1) |
| `price_cluster` | sharpe -1.07 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.548 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x2), sharpe -2.05 < 1.0 (x1), profit_factor 0.00 < 1.5 (x1) |
| `elder_impulse` | sharpe -2.57 < 1.0 (x1), profit_factor 0.70 < 1.5 (x1), mc_p_value 0.524 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | mc_p_value 0.426 > 0.05 (우연 가능성) (x1), profit_factor 1.43 < 1.5 (x1), mc_p_value 0.502 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -2.23 < 1.0 (x1), profit_factor 0.61 < 1.5 (x1), mc_p_value 0.538 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -2.02 < 1.0 (x1), profit_factor 0.61 < 1.5 (x1), mc_p_value 0.528 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.07 < 1.5 | 4 |
| mc_p_value 0.550 > 0.05 (우연 가능성) | 4 |
| profit_factor 0.85 < 1.5 | 4 |
| mc_p_value 0.524 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.82 < 1.5 | 3 |
| mc_p_value 0.540 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.516 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.246 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.434 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.48 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +13.79% -> $11,379
- **Top 5 균등배분**: +46.60% -> $14,660
