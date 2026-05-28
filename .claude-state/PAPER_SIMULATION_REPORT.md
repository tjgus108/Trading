# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-28T20:15:53.700583Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-28T20:19:36.788353Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1703086204, block=36)_
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
| 평균 수익률 | 17.84% |
| 최고 수익률 | 76.76% (price_action_momentum) |
| 최저 수익률 | -9.12% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +76.76% | 5.06 | 47.7% | 1.60 | 147 | 11.9% | 0/4 | FAIL |
| 2 | `momentum_quality` | +48.92% | 4.16 | 46.1% | 1.56 | 118 | 11.7% | 0/4 | FAIL |
| 3 | `volume_breakout` | +45.32% | 4.03 | 46.6% | 1.65 | 91 | 11.2% | 0/4 | FAIL |
| 4 | `supertrend_multi` | +34.05% | 3.17 | 44.4% | 1.49 | 82 | 9.3% | 0/4 | FAIL |
| 5 | `lob_maker` | +32.21% | 2.53 | 43.0% | 1.31 | 120 | 19.6% | 0/4 | FAIL |
| 6 | `cmf` | +31.48% | 2.43 | 42.0% | 1.30 | 115 | 15.4% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | +24.22% | 2.33 | 43.0% | 1.34 | 88 | 14.9% | 0/4 | FAIL |
| 8 | `volatility_cluster` | +17.47% | 2.39 | 43.7% | 1.38 | 80 | 8.9% | 0/4 | FAIL |
| 9 | `htf_ema` | +16.63% | 1.94 | 43.8% | 1.33 | 70 | 9.9% | 0/4 | FAIL |
| 10 | `linear_channel_rev` | +12.52% | 2.72 | 49.4% | 1.76 | 33 | 5.1% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 72.6 | p100 | 5.06 | 1.73 | 1.60 | 147 | 11.9% | 0/4 | FAIL |
| 2 | `volume_breakout` | 64.6 | p95 | 4.03 | 1.33 | 1.65 | 91 | 11.2% | 0/4 | FAIL |
| 3 | `momentum_quality` | 61.9 | p90 | 4.16 | 2.50 | 1.56 | 118 | 11.7% | 0/4 | FAIL |
| 4 | `linear_channel_rev` | 59.8 | p85 | 2.72 | 1.19 | 1.76 | 33 | 5.1% | 0/4 | FAIL |
| 5 | `dema_cross` | 57.3 | p80 | 1.49 | 1.48 | 2.07 | 10 | 2.9% | 0/4 | FAIL |
| 6 | `roc_ma_cross` | 56.5 | p76 | 2.22 | 0.21 | 1.56 | 33 | 6.1% | 0/4 | FAIL |
| 7 | `positional_scaling` | 53.5 | p71 | 2.01 | 0.77 | 1.58 | 27 | 5.8% | 0/4 | FAIL |
| 8 | `volatility_cluster` | 52.6 | p66 | 2.39 | 1.36 | 1.38 | 80 | 8.9% | 0/4 | FAIL |
| 9 | `supertrend_multi` | 52.4 | p61 | 3.17 | 2.94 | 1.49 | 82 | 9.3% | 0/4 | FAIL |
| 10 | `engulfing_zone` | 52.0 | p57 | 1.87 | 0.54 | 1.57 | 23 | 7.0% | 0/4 | FAIL |
| 11 | `order_flow_imbalance_v2` | 50.2 | p52 | 2.33 | 0.65 | 1.34 | 88 | 14.9% | 0/4 | FAIL |
| 12 | `cmf` | 49.8 | p47 | 2.43 | 1.35 | 1.30 | 115 | 15.4% | 0/4 | FAIL |
| 13 | `lob_maker` | 49.5 | p42 | 2.53 | 0.80 | 1.31 | 120 | 19.6% | 0/4 | FAIL |
| 14 | `htf_ema` | 48.8 | p38 | 1.94 | 1.08 | 1.33 | 70 | 9.9% | 0/4 | FAIL |
| 15 | `price_cluster` | 44.2 | p33 | 1.60 | 1.72 | 1.52 | 31 | 9.5% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +76.76% | 5.06 | 1.60 | 147 | 0/4 | FAIL |
| `momentum_quality` | +48.92% | 4.16 | 1.56 | 118 | 0/4 | FAIL |
| `volume_breakout` | +45.32% | 4.03 | 1.65 | 91 | 0/4 | FAIL |
| `supertrend_multi` | +34.05% | 3.17 | 1.49 | 82 | 0/4 | FAIL |
| `lob_maker` | +32.21% | 2.53 | 1.31 | 120 | 0/4 | FAIL |
| `cmf` | +31.48% | 2.43 | 1.30 | 115 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +24.22% | 2.33 | 1.34 | 88 | 0/4 | FAIL |
| `volatility_cluster` | +17.47% | 2.39 | 1.38 | 80 | 0/4 | FAIL |
| `htf_ema` | +16.63% | 1.94 | 1.33 | 70 | 0/4 | FAIL |
| `linear_channel_rev` | +12.52% | 2.72 | 1.76 | 33 | 0/4 | FAIL |
| `price_cluster` | +9.89% | 1.60 | 1.52 | 31 | 0/4 | FAIL |
| `roc_ma_cross` | +9.54% | 2.22 | 1.56 | 33 | 0/4 | FAIL |
| `positional_scaling` | +9.01% | 2.01 | 1.58 | 27 | 0/4 | FAIL |
| `engulfing_zone` | +8.89% | 1.87 | 1.57 | 23 | 0/4 | FAIL |
| `narrow_range` | +7.72% | 1.08 | 1.22 | 90 | 0/4 | FAIL |
| `elder_impulse` | +5.67% | 0.90 | 1.21 | 52 | 0/4 | FAIL |
| `dema_cross` | +3.70% | 1.49 | 2.07 | 10 | 0/4 | FAIL |
| `acceleration_band` | +3.65% | 0.58 | 1.10 | 92 | 0/4 | FAIL |
| `value_area` | +2.76% | 0.93 | 1.35 | 17 | 0/4 | FAIL |
| `wick_reversal` | +1.02% | -0.34 | 1.46 | 2 | 0/4 | FAIL |
| `relative_volume` | +0.14% | 0.07 | 1.10 | 59 | 0/4 | FAIL |
| `frama` | -9.12% | -1.04 | 0.91 | 85 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.138 > 0.05 (우연 가능성) (x1), profit_factor 1.46 < 1.5 (x1), mc_p_value 0.318 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.182 > 0.05 (우연 가능성) (x1), profit_factor 1.23 < 1.5 (x1), mc_p_value 0.420 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | mc_p_value 0.234 > 0.05 (우연 가능성) (x1), mc_p_value 0.360 > 0.05 (우연 가능성) (x1), profit_factor 1.50 < 1.5 (x1) |
| `supertrend_multi` | mc_p_value 0.200 > 0.05 (우연 가능성) (x1), sharpe -0.35 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1) |
| `lob_maker` | profit_factor 1.38 < 1.5 (x1), mc_p_value 0.376 > 0.05 (우연 가능성) (x1), max_drawdown 25.3% > 20% (x1) |
| `cmf` | profit_factor 1.17 < 1.5 (x1), mc_p_value 0.432 > 0.05 (우연 가능성) (x1), profit_factor 1.29 < 1.5 (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.40 < 1.5 (x1), mc_p_value 0.338 > 0.05 (우연 가능성) (x1), profit_factor 1.18 < 1.5 (x1) |
| `volatility_cluster` | mc_p_value 0.358 > 0.05 (우연 가능성) (x1), profit_factor 1.22 < 1.5 (x1), mc_p_value 0.462 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | mc_p_value 0.420 > 0.05 (우연 가능성) (x1), mc_p_value 0.402 > 0.05 (우연 가능성) (x1), profit_factor 1.20 < 1.5 (x1) |
| `linear_channel_rev` | mc_p_value 0.414 > 0.05 (우연 가능성) (x1), mc_p_value 0.412 > 0.05 (우연 가능성) (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | mc_p_value 0.432 > 0.05 (우연 가능성) (x1), mc_p_value 0.404 > 0.05 (우연 가능성) (x1), sharpe -1.26 < 1.0 (x1) |
| `roc_ma_cross` | mc_p_value 0.440 > 0.05 (우연 가능성) (x1), mc_p_value 0.452 > 0.05 (우연 가능성) (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | mc_p_value 0.446 > 0.05 (우연 가능성) (x2), sharpe 0.70 < 1.0 (x1), profit_factor 1.20 < 1.5 (x1) |
| `engulfing_zone` | mc_p_value 0.462 > 0.05 (우연 가능성) (x1), profit_factor 1.29 < 1.5 (x1), mc_p_value 0.472 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.07 < 1.5 (x2), mc_p_value 0.326 > 0.05 (우연 가능성) (x1), sharpe 0.24 < 1.0 (x1) |
| `elder_impulse` | mc_p_value 0.398 > 0.05 (우연 가능성) (x1), sharpe 0.76 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1) |
| `dema_cross` | trades 9 < 15 (x2), sharpe -0.75 < 1.0 (x1), profit_factor 0.75 < 1.5 (x1) |
| `acceleration_band` | profit_factor 1.29 < 1.5 (x1), mc_p_value 0.422 > 0.05 (우연 가능성) (x1), sharpe -0.46 < 1.0 (x1) |
| `value_area` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.476 > 0.05 (우연 가능성) (x1), mc_p_value 0.468 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | profit_factor 0.00 < 1.5 (x2), trades 1 < 15 (x2), trades 3 < 15 (x2) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.44 < 1.5 | 4 |
| mc_p_value 0.462 > 0.05 (우연 가능성) | 4 |
| profit_factor 1.34 < 1.5 | 3 |
| profit_factor 1.29 < 1.5 | 3 |
| profit_factor 1.07 < 1.5 | 3 |
| mc_p_value 0.276 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.23 < 1.5 | 2 |
| mc_p_value 0.420 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.374 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.500 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +17.84% -> $11,784
- **Top 5 균등배분**: +47.45% -> $14,745
