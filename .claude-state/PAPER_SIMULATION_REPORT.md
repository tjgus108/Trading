# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-27T15:08:20.139312Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-27T15:16:25.518215Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=381700538, block=36)_
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
| 평균 수익률 | 31.54% |
| 최고 수익률 | 88.16% (lob_maker) |
| 최저 수익률 | -5.61% (value_area) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `lob_maker` | +88.16% | 5.19 | 48.5% | 1.69 | 125 | 12.5% | 0/4 | FAIL |
| 2 | `order_flow_imbalance_v2` | +85.38% | 5.44 | 51.2% | 2.02 | 90 | 8.2% | 0/4 | FAIL |
| 3 | `price_action_momentum` | +85.07% | 5.64 | 48.6% | 1.69 | 146 | 10.4% | 0/4 | FAIL |
| 4 | `cmf` | +81.41% | 4.85 | 48.1% | 1.63 | 126 | 17.5% | 0/4 | FAIL |
| 5 | `volume_breakout` | +71.48% | 5.40 | 51.1% | 1.92 | 94 | 9.6% | 0/4 | FAIL |
| 6 | `momentum_quality` | +50.45% | 4.67 | 48.2% | 1.65 | 118 | 8.5% | 0/4 | FAIL |
| 7 | `acceleration_band` | +49.06% | 4.32 | 48.9% | 1.76 | 90 | 10.6% | 0/4 | FAIL |
| 8 | `htf_ema` | +45.38% | 4.36 | 49.3% | 1.85 | 72 | 8.7% | 0/4 | FAIL |
| 9 | `supertrend_multi` | +35.25% | 3.38 | 44.9% | 1.54 | 86 | 10.0% | 0/4 | FAIL |
| 10 | `volatility_cluster` | +33.92% | 3.91 | 48.6% | 1.74 | 80 | 8.9% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 65.2 | p100 | 5.64 | 0.63 | 1.69 | 146 | 10.4% | 0/4 | FAIL |
| 2 | `wick_reversal` | 61.7 | p95 | 0.96 | 0.96 | 500.00 | 0 | 0.1% | 0/4 | FAIL |
| 3 | `momentum_quality` | 61.4 | p90 | 4.67 | 0.34 | 1.65 | 118 | 8.5% | 0/4 | FAIL |
| 4 | `lob_maker` | 60.2 | p85 | 5.19 | 0.48 | 1.69 | 125 | 12.5% | 0/4 | FAIL |
| 5 | `volume_breakout` | 57.2 | p80 | 5.40 | 1.53 | 1.92 | 94 | 9.6% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | 55.3 | p76 | 5.44 | 2.44 | 2.02 | 90 | 8.2% | 0/4 | FAIL |
| 7 | `cmf` | 52.1 | p71 | 4.85 | 1.36 | 1.63 | 126 | 17.5% | 0/4 | FAIL |
| 8 | `htf_ema` | 51.4 | p66 | 4.36 | 1.71 | 1.85 | 72 | 8.7% | 0/4 | FAIL |
| 9 | `acceleration_band` | 51.2 | p61 | 4.32 | 1.83 | 1.76 | 90 | 10.6% | 0/4 | FAIL |
| 10 | `relative_volume` | 47.6 | p57 | 2.92 | 1.27 | 1.62 | 56 | 6.8% | 0/4 | FAIL |
| 11 | `volatility_cluster` | 47.4 | p52 | 3.91 | 2.71 | 1.74 | 80 | 8.9% | 0/4 | FAIL |
| 12 | `supertrend_multi` | 46.1 | p47 | 3.38 | 2.47 | 1.54 | 86 | 10.0% | 0/4 | FAIL |
| 13 | `dema_cross` | 42.6 | p42 | 1.20 | 0.30 | 1.56 | 9 | 3.3% | 0/4 | FAIL |
| 14 | `elder_impulse` | 42.0 | p38 | 1.78 | 0.50 | 1.36 | 48 | 10.4% | 0/4 | FAIL |
| 15 | `frama` | 41.9 | p33 | 2.06 | 1.43 | 1.34 | 78 | 12.1% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `lob_maker` | +88.16% | 5.19 | 1.69 | 125 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +85.38% | 5.44 | 2.02 | 90 | 0/4 | FAIL |
| `price_action_momentum` | +85.07% | 5.64 | 1.69 | 146 | 0/4 | FAIL |
| `cmf` | +81.41% | 4.85 | 1.63 | 126 | 0/4 | FAIL |
| `volume_breakout` | +71.48% | 5.40 | 1.92 | 94 | 0/4 | FAIL |
| `momentum_quality` | +50.45% | 4.67 | 1.65 | 118 | 0/4 | FAIL |
| `acceleration_band` | +49.06% | 4.32 | 1.76 | 90 | 0/4 | FAIL |
| `htf_ema` | +45.38% | 4.36 | 1.85 | 72 | 0/4 | FAIL |
| `supertrend_multi` | +35.25% | 3.38 | 1.54 | 86 | 0/4 | FAIL |
| `volatility_cluster` | +33.92% | 3.91 | 1.74 | 80 | 0/4 | FAIL |
| `frama` | +18.65% | 2.06 | 1.34 | 78 | 0/4 | FAIL |
| `relative_volume` | +18.12% | 2.92 | 1.62 | 56 | 0/4 | FAIL |
| `narrow_range` | +13.12% | 1.50 | 1.26 | 93 | 0/4 | FAIL |
| `elder_impulse` | +11.27% | 1.78 | 1.36 | 48 | 0/4 | FAIL |
| `price_cluster` | +5.29% | 0.96 | 1.25 | 35 | 0/4 | FAIL |
| `roc_ma_cross` | +4.30% | 1.02 | 1.28 | 30 | 0/4 | FAIL |
| `dema_cross` | +2.79% | 1.20 | 1.56 | 9 | 0/4 | FAIL |
| `positional_scaling` | +2.02% | 0.45 | 1.17 | 22 | 0/4 | FAIL |
| `wick_reversal` | +1.31% | 0.96 | 500.00 | 0 | 0/4 | FAIL |
| `engulfing_zone` | -0.11% | -0.15 | 1.04 | 24 | 0/4 | FAIL |
| `linear_channel_rev` | -2.77% | -0.68 | 0.97 | 32 | 0/4 | FAIL |
| `value_area` | -5.61% | -2.95 | 0.65 | 16 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `lob_maker` | mc_p_value 0.288 > 0.05 (우연 가능성) (x1), mc_p_value 0.326 > 0.05 (우연 가능성) (x1), mc_p_value 0.224 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.432 > 0.05 (우연 가능성) (x1), mc_p_value 0.252 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | mc_p_value 0.262 > 0.05 (우연 가능성) (x1), mc_p_value 0.266 > 0.05 (우연 가능성) (x1), mc_p_value 0.164 > 0.05 (우연 가능성) (x1) |
| `cmf` | max_drawdown 21.7% > 20% (x2), mc_p_value 0.308 > 0.05 (우연 가능성) (x1), mc_p_value 0.210 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.406 > 0.05 (우연 가능성) (x1), mc_p_value 0.322 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.322 > 0.05 (우연 가능성) (x2), mc_p_value 0.318 > 0.05 (우연 가능성) (x1), mc_p_value 0.284 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.44 < 1.5 (x1), mc_p_value 0.402 > 0.05 (우연 가능성) (x1), mc_p_value 0.260 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.476 > 0.05 (우연 가능성) (x1), mc_p_value 0.316 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | sharpe -0.63 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1), mc_p_value 0.542 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | mc_p_value 0.300 > 0.05 (우연 가능성) (x1), mc_p_value 0.296 > 0.05 (우연 가능성) (x1), mc_p_value 0.386 > 0.05 (우연 가능성) (x1) |
| `frama` | mc_p_value 0.366 > 0.05 (우연 가능성) (x2), profit_factor 1.26 < 1.5 (x1), mc_p_value 0.432 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | sharpe 0.87 < 1.0 (x1), profit_factor 1.17 < 1.5 (x1), mc_p_value 0.504 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | sharpe -0.92 < 1.0 (x1), max_drawdown 22.7% > 20% (x1), profit_factor 0.94 < 1.5 (x1) |
| `elder_impulse` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.490 > 0.05 (우연 가능성) (x1), profit_factor 1.48 < 1.5 (x1) |
| `price_cluster` | sharpe 0.53 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.500 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -0.28 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1), mc_p_value 0.512 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe 0.75 < 1.0 (x1), profit_factor 1.38 < 1.5 (x1), trades 7 < 15 (x1) |
| `positional_scaling` | profit_factor 1.47 < 1.5 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1), sharpe 0.74 < 1.0 (x1) |
| `wick_reversal` | trades 1 < 15 (x2), no trades generated (x2) |
| `engulfing_zone` | sharpe -2.64 < 1.0 (x1), profit_factor 0.53 < 1.5 (x1), mc_p_value 0.522 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.432 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.322 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.26 < 1.5 | 3 |
| mc_p_value 0.464 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.25 < 1.5 | 3 |
| mc_p_value 0.284 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.260 > 0.05 (우연 가능성) | 2 |
| max_drawdown 21.7% > 20% | 2 |
| mc_p_value 0.238 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.406 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +31.54% -> $13,154
- **Top 5 균등배분**: +82.30% -> $18,230


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-27T15:26:13.224575Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=18810129, block=36)_
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
| 평균 수익률 | 10.71% |
| 최고 수익률 | 34.24% (price_action_momentum) |
| 최저 수익률 | -11.98% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +34.24% | 2.78 | 41.8% | 1.31 | 159 | 15.3% | 0/4 | FAIL |
| 2 | `momentum_quality` | +33.34% | 3.46 | 45.9% | 1.48 | 106 | 7.2% | 0/4 | FAIL |
| 3 | `volume_breakout` | +24.96% | 2.34 | 42.5% | 1.36 | 100 | 14.1% | 0/4 | FAIL |
| 4 | `supertrend_multi` | +21.89% | 2.39 | 43.2% | 1.31 | 122 | 13.5% | 0/4 | FAIL |
| 5 | `volatility_cluster` | +21.16% | 2.45 | 44.0% | 1.51 | 72 | 7.5% | 0/4 | FAIL |
| 6 | `htf_ema` | +20.18% | 2.24 | 44.5% | 1.36 | 73 | 10.9% | 0/4 | FAIL |
| 7 | `acceleration_band` | +20.08% | 2.10 | 41.6% | 1.30 | 99 | 14.3% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | +14.64% | 1.44 | 41.2% | 1.21 | 89 | 20.4% | 0/4 | FAIL |
| 9 | `price_cluster` | +14.58% | 2.03 | 45.8% | 1.52 | 38 | 8.0% | 0/4 | FAIL |
| 10 | `cmf` | +13.90% | 1.36 | 40.2% | 1.17 | 116 | 16.6% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 79.6 | p100 | 3.46 | 1.31 | 1.48 | 106 | 7.2% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 76.7 | p95 | 2.78 | 0.97 | 1.31 | 159 | 15.3% | 0/4 | FAIL |
| 3 | `roc_ma_cross` | 73.9 | p90 | 2.67 | 0.75 | 1.70 | 36 | 6.4% | 0/4 | FAIL |
| 4 | `supertrend_multi` | 70.6 | p85 | 2.39 | 1.38 | 1.31 | 122 | 13.5% | 0/4 | FAIL |
| 5 | `htf_ema` | 69.5 | p80 | 2.24 | 0.65 | 1.36 | 73 | 10.9% | 0/4 | FAIL |
| 6 | `acceleration_band` | 66.5 | p71 | 2.10 | 1.38 | 1.30 | 99 | 14.3% | 0/4 | FAIL |
| 7 | `linear_channel_rev` | 66.5 | p76 | 1.69 | 0.48 | 1.45 | 29 | 5.7% | 0/4 | FAIL |
| 8 | `volatility_cluster` | 66.2 | p66 | 2.45 | 2.76 | 1.51 | 72 | 7.5% | 0/4 | FAIL |
| 9 | `volume_breakout` | 65.7 | p61 | 2.34 | 2.16 | 1.36 | 100 | 14.1% | 0/4 | FAIL |
| 10 | `cmf` | 65.2 | p57 | 1.36 | 0.41 | 1.17 | 116 | 16.6% | 0/4 | FAIL |
| 11 | `price_cluster` | 65.0 | p52 | 2.03 | 1.52 | 1.52 | 38 | 8.0% | 0/4 | FAIL |
| 12 | `positional_scaling` | 60.1 | p47 | 1.22 | 1.39 | 1.43 | 22 | 5.4% | 0/4 | FAIL |
| 13 | `dema_cross` | 59.7 | p42 | 0.93 | 1.94 | 1.70 | 12 | 3.4% | 0/4 | FAIL |
| 14 | `order_flow_imbalance_v2` | 58.6 | p38 | 1.44 | 1.30 | 1.21 | 89 | 20.4% | 0/4 | FAIL |
| 15 | `value_area` | 58.4 | p33 | 0.99 | 2.00 | 1.61 | 17 | 5.3% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +34.24% | 2.78 | 1.31 | 159 | 0/4 | FAIL |
| `momentum_quality` | +33.34% | 3.46 | 1.48 | 106 | 0/4 | FAIL |
| `volume_breakout` | +24.96% | 2.34 | 1.36 | 100 | 0/4 | FAIL |
| `supertrend_multi` | +21.89% | 2.39 | 1.31 | 122 | 0/4 | FAIL |
| `volatility_cluster` | +21.16% | 2.45 | 1.51 | 72 | 0/4 | FAIL |
| `htf_ema` | +20.18% | 2.24 | 1.36 | 73 | 0/4 | FAIL |
| `acceleration_band` | +20.08% | 2.10 | 1.30 | 99 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +14.64% | 1.44 | 1.21 | 89 | 0/4 | FAIL |
| `price_cluster` | +14.58% | 2.03 | 1.52 | 38 | 0/4 | FAIL |
| `cmf` | +13.90% | 1.36 | 1.17 | 116 | 0/4 | FAIL |
| `roc_ma_cross` | +13.12% | 2.67 | 1.70 | 36 | 0/4 | FAIL |
| `linear_channel_rev` | +6.60% | 1.69 | 1.45 | 29 | 0/4 | FAIL |
| `positional_scaling` | +5.54% | 1.22 | 1.43 | 22 | 0/4 | FAIL |
| `relative_volume` | +3.59% | 0.55 | 1.18 | 64 | 0/4 | FAIL |
| `value_area` | +3.21% | 0.99 | 1.61 | 17 | 0/4 | FAIL |
| `dema_cross` | +2.81% | 0.93 | 1.70 | 12 | 0/4 | FAIL |
| `narrow_range` | +1.21% | 0.06 | 1.10 | 94 | 0/4 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `lob_maker` | -0.16% | -0.22 | 1.03 | 130 | 0/4 | FAIL |
| `elder_impulse` | -2.58% | -0.26 | 1.03 | 61 | 0/4 | FAIL |
| `frama` | -4.62% | -0.40 | 0.98 | 87 | 0/4 | FAIL |
| `engulfing_zone` | -11.98% | -2.45 | 0.66 | 29 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | profit_factor 1.19 < 1.5 (x2), profit_factor 1.44 < 1.5 (x1), mc_p_value 0.268 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.376 > 0.05 (우연 가능성) (x1), profit_factor 1.20 < 1.5 (x1) |
| `volume_breakout` | profit_factor 1.27 < 1.5 (x1), mc_p_value 0.424 > 0.05 (우연 가능성) (x1), sharpe -0.86 < 1.0 (x1) |
| `supertrend_multi` | profit_factor 1.32 < 1.5 (x1), mc_p_value 0.426 > 0.05 (우연 가능성) (x1), sharpe 0.64 < 1.0 (x1) |
| `volatility_cluster` | sharpe 0.61 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1), mc_p_value 0.482 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | mc_p_value 0.394 > 0.05 (우연 가능성) (x1), profit_factor 1.34 < 1.5 (x1), mc_p_value 0.428 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.32 < 1.5 (x1), mc_p_value 0.422 > 0.05 (우연 가능성) (x1), sharpe -0.20 < 1.0 (x1) |
| `order_flow_imbalance_v2` | max_drawdown 22.9% > 20% (x2), profit_factor 1.21 < 1.5 (x1), mc_p_value 0.432 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | mc_p_value 0.420 > 0.05 (우연 가능성) (x1), profit_factor 1.27 < 1.5 (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1) |
| `cmf` | sharpe 0.98 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), mc_p_value 0.468 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | mc_p_value 0.414 > 0.05 (우연 가능성) (x1), profit_factor 1.30 < 1.5 (x1), mc_p_value 0.472 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | profit_factor 1.35 < 1.5 (x2), mc_p_value 0.464 > 0.05 (우연 가능성) (x1), mc_p_value 0.450 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | mc_p_value 0.464 > 0.05 (우연 가능성) (x1), mc_p_value 0.488 > 0.05 (우연 가능성) (x1), sharpe 0.91 < 1.0 (x1) |
| `relative_volume` | profit_factor 1.33 < 1.5 (x1), mc_p_value 0.436 > 0.05 (우연 가능성) (x1), sharpe -2.67 < 1.0 (x1) |
| `value_area` | trades 13 < 15 (x1), sharpe 0.42 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1) |
| `dema_cross` | sharpe -1.56 < 1.0 (x1), profit_factor 0.66 < 1.5 (x1), trades 14 < 15 (x1) |
| `narrow_range` | sharpe 0.55 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1), mc_p_value 0.452 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x4) |
| `lob_maker` | sharpe 0.79 < 1.0 (x1), max_drawdown 34.9% > 20% (x1), profit_factor 1.10 < 1.5 (x1) |
| `elder_impulse` | sharpe -0.46 < 1.0 (x1), profit_factor 0.97 < 1.5 (x1), mc_p_value 0.504 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.10 < 1.5 | 4 |
| no trades generated | 4 |
| profit_factor 1.19 < 1.5 | 3 |
| profit_factor 1.32 < 1.5 | 3 |
| profit_factor 1.33 < 1.5 | 3 |
| mc_p_value 0.432 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.464 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.394 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.20 < 1.5 | 2 |
| mc_p_value 0.368 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +10.71% -> $11,071
- **Top 5 균등배분**: +27.12% -> $12,712


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-27T15:35:08.202516Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=1655429464, block=36)_
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
| 평균 수익률 | 15.22% |
| 최고 수익률 | 59.27% (supertrend_multi) |
| 최저 수익률 | -5.11% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +59.27% | 5.04 | 47.5% | 1.63 | 128 | 8.5% | 0/4 | FAIL |
| 2 | `momentum_quality` | +45.01% | 4.26 | 47.0% | 1.58 | 116 | 12.4% | 0/4 | FAIL |
| 3 | `price_action_momentum` | +44.13% | 3.35 | 45.0% | 1.35 | 162 | 14.9% | 0/4 | FAIL |
| 4 | `cmf` | +33.70% | 2.42 | 42.8% | 1.28 | 130 | 20.4% | 0/4 | FAIL |
| 5 | `order_flow_imbalance_v2` | +33.68% | 2.75 | 44.2% | 1.45 | 86 | 13.7% | 0/4 | FAIL |
| 6 | `volume_breakout` | +29.62% | 2.44 | 42.6% | 1.39 | 96 | 15.9% | 0/4 | FAIL |
| 7 | `acceleration_band` | +22.17% | 2.27 | 42.5% | 1.32 | 100 | 14.9% | 0/4 | FAIL |
| 8 | `elder_impulse` | +21.02% | 2.87 | 47.9% | 1.55 | 55 | 7.6% | 0/4 | FAIL |
| 9 | `narrow_range` | +18.29% | 2.36 | 44.5% | 1.36 | 90 | 11.0% | 0/4 | FAIL |
| 10 | `volatility_cluster` | +16.05% | 2.17 | 44.3% | 1.39 | 79 | 9.2% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 86.3 | p100 | 5.04 | 0.75 | 1.63 | 128 | 8.5% | 0/4 | FAIL |
| 2 | `momentum_quality` | 76.7 | p95 | 4.26 | 1.32 | 1.58 | 116 | 12.4% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 72.9 | p90 | 3.35 | 1.06 | 1.35 | 162 | 14.9% | 0/4 | FAIL |
| 4 | `roc_ma_cross` | 69.6 | p85 | 2.64 | 0.64 | 1.63 | 38 | 5.0% | 0/4 | FAIL |
| 5 | `elder_impulse` | 68.7 | p80 | 2.87 | 0.85 | 1.55 | 55 | 7.6% | 0/4 | FAIL |
| 6 | `narrow_range` | 64.9 | p76 | 2.36 | 0.80 | 1.36 | 90 | 11.0% | 0/4 | FAIL |
| 7 | `acceleration_band` | 62.4 | p71 | 2.27 | 0.92 | 1.32 | 100 | 14.9% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | 61.6 | p66 | 2.75 | 2.08 | 1.45 | 86 | 13.7% | 0/4 | FAIL |
| 9 | `volatility_cluster` | 60.8 | p61 | 2.17 | 1.78 | 1.39 | 79 | 9.2% | 0/4 | FAIL |
| 10 | `cmf` | 59.9 | p57 | 2.42 | 1.58 | 1.28 | 130 | 20.4% | 0/4 | FAIL |
| 11 | `volume_breakout` | 57.1 | p52 | 2.44 | 2.58 | 1.39 | 96 | 15.9% | 0/4 | FAIL |
| 12 | `htf_ema` | 53.9 | p47 | 1.20 | 0.51 | 1.20 | 68 | 15.8% | 0/4 | FAIL |
| 13 | `value_area` | 52.8 | p42 | 0.78 | 1.17 | 1.33 | 18 | 4.6% | 0/4 | FAIL |
| 14 | `linear_channel_rev` | 50.3 | p38 | 0.91 | 2.17 | 1.35 | 30 | 5.9% | 0/4 | FAIL |
| 15 | `positional_scaling` | 44.1 | p33 | -0.29 | 0.70 | 0.98 | 22 | 5.5% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +59.27% | 5.04 | 1.63 | 128 | 0/4 | FAIL |
| `momentum_quality` | +45.01% | 4.26 | 1.58 | 116 | 0/4 | FAIL |
| `price_action_momentum` | +44.13% | 3.35 | 1.35 | 162 | 0/4 | FAIL |
| `cmf` | +33.70% | 2.42 | 1.28 | 130 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +33.68% | 2.75 | 1.45 | 86 | 0/4 | FAIL |
| `volume_breakout` | +29.62% | 2.44 | 1.39 | 96 | 0/4 | FAIL |
| `acceleration_band` | +22.17% | 2.27 | 1.32 | 100 | 0/4 | FAIL |
| `elder_impulse` | +21.02% | 2.87 | 1.55 | 55 | 0/4 | FAIL |
| `narrow_range` | +18.29% | 2.36 | 1.36 | 90 | 0/4 | FAIL |
| `volatility_cluster` | +16.05% | 2.17 | 1.39 | 79 | 0/4 | FAIL |
| `roc_ma_cross` | +13.01% | 2.64 | 1.63 | 38 | 0/4 | FAIL |
| `htf_ema` | +8.45% | 1.20 | 1.20 | 68 | 0/4 | FAIL |
| `linear_channel_rev` | +4.02% | 0.91 | 1.35 | 30 | 0/4 | FAIL |
| `value_area` | +2.25% | 0.78 | 1.33 | 18 | 0/4 | FAIL |
| `relative_volume` | +1.31% | -0.07 | 1.11 | 60 | 0/4 | FAIL |
| `lob_maker` | +0.44% | -0.38 | 1.03 | 128 | 0/4 | FAIL |
| `wick_reversal` | -0.11% | -0.33 | 0.45 | 1 | 0/4 | FAIL |
| `positional_scaling` | -1.39% | -0.29 | 0.98 | 22 | 0/4 | FAIL |
| `price_cluster` | -2.29% | -0.24 | 1.01 | 40 | 0/4 | FAIL |
| `engulfing_zone` | -4.20% | -1.30 | 0.81 | 19 | 0/4 | FAIL |
| `dema_cross` | -4.51% | -1.89 | 0.59 | 14 | 0/4 | FAIL |
| `frama` | -5.11% | -0.82 | 0.99 | 82 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | mc_p_value 0.208 > 0.05 (우연 가능성) (x2), mc_p_value 0.250 > 0.05 (우연 가능성) (x1), mc_p_value 0.302 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.316 > 0.05 (우연 가능성) (x1), mc_p_value 0.242 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1) |
| `price_action_momentum` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.286 > 0.05 (우연 가능성) (x1), profit_factor 1.43 < 1.5 (x1) |
| `cmf` | max_drawdown 22.9% > 20% (x2), mc_p_value 0.274 > 0.05 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.336 > 0.05 (우연 가능성) (x1), profit_factor 1.21 < 1.5 (x1), mc_p_value 0.420 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | mc_p_value 0.248 > 0.05 (우연 가능성) (x1), profit_factor 1.18 < 1.5 (x1), mc_p_value 0.476 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.380 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1) |
| `elder_impulse` | mc_p_value 0.356 > 0.05 (우연 가능성) (x1), mc_p_value 0.316 > 0.05 (우연 가능성) (x1), mc_p_value 0.422 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | mc_p_value 0.390 > 0.05 (우연 가능성) (x2), profit_factor 1.22 < 1.5 (x1), mc_p_value 0.414 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.28 < 1.5 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1), profit_factor 1.17 < 1.5 (x1) |
| `roc_ma_cross` | mc_p_value 0.412 > 0.05 (우연 가능성) (x2), mc_p_value 0.454 > 0.05 (우연 가능성) (x1), profit_factor 1.35 < 1.5 (x1) |
| `htf_ema` | profit_factor 1.29 < 1.5 (x1), mc_p_value 0.454 > 0.05 (우연 가능성) (x1), sharpe 0.44 < 1.0 (x1) |
| `linear_channel_rev` | mc_p_value 0.434 > 0.05 (우연 가능성) (x2), sharpe 0.65 < 1.0 (x1), profit_factor 1.16 < 1.5 (x1) |
| `value_area` | sharpe 0.64 < 1.0 (x1), profit_factor 1.23 < 1.5 (x1), mc_p_value 0.488 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | mc_p_value 0.394 > 0.05 (우연 가능성) (x1), sharpe -0.21 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1) |
| `lob_maker` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.346 > 0.05 (우연 가능성) (x1), sharpe -1.32 < 1.0 (x1) |
| `wick_reversal` | no trades generated (x2), sharpe 0.75 < 1.0 (x1), trades 2 < 15 (x1) |
| `positional_scaling` | sharpe 0.03 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1), mc_p_value 0.480 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -1.01 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.528 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.488 > 0.05 (우연 가능성) (x1), sharpe -1.27 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.500 > 0.05 (우연 가능성) | 5 |
| profit_factor 1.24 < 1.5 | 3 |
| mc_p_value 0.394 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.17 < 1.5 | 3 |
| mc_p_value 0.208 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.316 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.33 < 1.5 | 2 |
| mc_p_value 0.422 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.43 < 1.5 | 2 |
| profit_factor 1.26 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +15.22% -> $11,522
- **Top 5 균등배분**: +43.16% -> $14,316
