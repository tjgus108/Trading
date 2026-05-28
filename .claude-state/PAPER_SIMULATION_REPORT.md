# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-28T15:51:35.998791Z_
_Symbols: BTC/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-28T15:58:05.000832Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1943463417, block=36)_
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
| 평균 수익률 | 30.39% |
| 최고 수익률 | 133.46% (price_action_momentum) |
| 최저 수익률 | -21.56% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +133.46% | 6.98 | 50.7% | 1.90 | 151 | 9.2% | 0/4 | FAIL |
| 2 | `momentum_quality` | +109.73% | 7.67 | 55.3% | 2.22 | 121 | 7.1% | 0/4 | FAIL |
| 3 | `supertrend_multi` | +93.45% | 6.57 | 51.1% | 1.82 | 153 | 16.3% | 0/4 | FAIL |
| 4 | `order_flow_imbalance_v2` | +76.81% | 5.51 | 51.1% | 1.97 | 88 | 11.8% | 0/4 | FAIL |
| 5 | `cmf` | +53.90% | 3.77 | 45.6% | 1.48 | 118 | 14.0% | 0/4 | FAIL |
| 6 | `volume_breakout` | +52.95% | 4.48 | 47.6% | 1.67 | 99 | 12.6% | 0/4 | FAIL |
| 7 | `lob_maker` | +40.25% | 2.95 | 42.8% | 1.35 | 125 | 14.0% | 0/4 | FAIL |
| 8 | `volatility_cluster` | +30.30% | 4.03 | 49.3% | 1.75 | 72 | 8.3% | 0/4 | FAIL |
| 9 | `price_cluster` | +22.29% | 2.98 | 49.5% | 1.88 | 34 | 8.2% | 0/4 | FAIL |
| 10 | `acceleration_band` | +20.80% | 2.33 | 42.7% | 1.36 | 86 | 12.8% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 82.6 | p100 | 7.67 | 1.23 | 2.22 | 121 | 7.1% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 74.9 | p95 | 6.98 | 2.32 | 1.90 | 151 | 9.2% | 0/4 | FAIL |
| 3 | `supertrend_multi` | 72.6 | p90 | 6.57 | 1.55 | 1.82 | 153 | 16.3% | 0/4 | FAIL |
| 4 | `order_flow_imbalance_v2` | 70.9 | p85 | 5.51 | 0.66 | 1.97 | 88 | 11.8% | 0/4 | FAIL |
| 5 | `volume_breakout` | 67.2 | p80 | 4.48 | 0.33 | 1.67 | 99 | 12.6% | 0/4 | FAIL |
| 6 | `volatility_cluster` | 64.4 | p76 | 4.03 | 0.78 | 1.75 | 72 | 8.3% | 0/4 | FAIL |
| 7 | `cmf` | 62.0 | p71 | 3.77 | 0.92 | 1.48 | 118 | 14.0% | 0/4 | FAIL |
| 8 | `roc_ma_cross` | 61.3 | p66 | 3.22 | 0.69 | 1.90 | 33 | 6.0% | 0/4 | FAIL |
| 9 | `lob_maker` | 61.2 | p61 | 2.95 | 0.46 | 1.35 | 125 | 14.0% | 0/4 | FAIL |
| 10 | `linear_channel_rev` | 57.3 | p57 | 2.54 | 0.45 | 1.63 | 36 | 7.6% | 0/4 | FAIL |
| 11 | `price_cluster` | 55.3 | p52 | 2.98 | 1.61 | 1.88 | 34 | 8.2% | 0/4 | FAIL |
| 12 | `acceleration_band` | 54.9 | p47 | 2.33 | 0.79 | 1.36 | 86 | 12.8% | 0/4 | FAIL |
| 13 | `relative_volume` | 52.9 | p42 | 1.88 | 0.99 | 1.35 | 62 | 7.9% | 0/4 | FAIL |
| 14 | `htf_ema` | 51.9 | p38 | 1.35 | 0.33 | 1.22 | 69 | 11.3% | 0/4 | FAIL |
| 15 | `elder_impulse` | 51.1 | p33 | 1.92 | 1.14 | 1.35 | 58 | 9.7% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +133.46% | 6.98 | 1.90 | 151 | 0/4 | FAIL |
| `momentum_quality` | +109.73% | 7.67 | 2.22 | 121 | 0/4 | FAIL |
| `supertrend_multi` | +93.45% | 6.57 | 1.82 | 153 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +76.81% | 5.51 | 1.97 | 88 | 0/4 | FAIL |
| `cmf` | +53.90% | 3.77 | 1.48 | 118 | 0/4 | FAIL |
| `volume_breakout` | +52.95% | 4.48 | 1.67 | 99 | 0/4 | FAIL |
| `lob_maker` | +40.25% | 2.95 | 1.35 | 125 | 0/4 | FAIL |
| `volatility_cluster` | +30.30% | 4.03 | 1.75 | 72 | 0/4 | FAIL |
| `price_cluster` | +22.29% | 2.98 | 1.88 | 34 | 0/4 | FAIL |
| `acceleration_band` | +20.80% | 2.33 | 1.36 | 86 | 0/4 | FAIL |
| `roc_ma_cross` | +15.50% | 3.22 | 1.90 | 33 | 0/4 | FAIL |
| `elder_impulse` | +14.29% | 1.92 | 1.35 | 58 | 0/4 | FAIL |
| `linear_channel_rev` | +11.58% | 2.54 | 1.63 | 36 | 0/4 | FAIL |
| `relative_volume` | +11.43% | 1.88 | 1.35 | 62 | 0/4 | FAIL |
| `htf_ema` | +10.25% | 1.35 | 1.22 | 69 | 0/4 | FAIL |
| `narrow_range` | +3.53% | 0.56 | 1.11 | 86 | 0/4 | FAIL |
| `value_area` | +2.06% | 0.57 | 1.38 | 18 | 0/4 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `dema_cross` | -1.74% | -1.41 | 0.73 | 9 | 0/4 | FAIL |
| `positional_scaling` | -1.92% | -0.37 | 0.97 | 27 | 0/4 | FAIL |
| `engulfing_zone` | -8.70% | -2.06 | 0.64 | 19 | 0/4 | FAIL |
| `frama` | -21.56% | -2.76 | 0.75 | 92 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.098 > 0.05 (우연 가능성) (x1), mc_p_value 0.144 > 0.05 (우연 가능성) (x1), mc_p_value 0.248 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.128 > 0.05 (우연 가능성) (x1), mc_p_value 0.200 > 0.05 (우연 가능성) (x1), mc_p_value 0.230 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | max_drawdown 22.2% > 20% (x2), mc_p_value 0.130 > 0.05 (우연 가능성) (x1), mc_p_value 0.232 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.282 > 0.05 (우연 가능성) (x1), mc_p_value 0.318 > 0.05 (우연 가능성) (x1), mc_p_value 0.256 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.394 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1) |
| `volume_breakout` | mc_p_value 0.276 > 0.05 (우연 가능성) (x1), mc_p_value 0.312 > 0.05 (우연 가능성) (x1), mc_p_value 0.320 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.36 < 1.5 (x2), mc_p_value 0.352 > 0.05 (우연 가능성) (x2), profit_factor 1.27 < 1.5 (x1) |
| `volatility_cluster` | mc_p_value 0.336 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1), mc_p_value 0.402 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | mc_p_value 0.412 > 0.05 (우연 가능성) (x1), profit_factor 1.27 < 1.5 (x1), mc_p_value 0.498 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | mc_p_value 0.362 > 0.05 (우연 가능성) (x1), profit_factor 1.20 < 1.5 (x1), mc_p_value 0.400 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | mc_p_value 0.432 > 0.05 (우연 가능성) (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1), mc_p_value 0.410 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | mc_p_value 0.366 > 0.05 (우연 가능성) (x1), sharpe 0.93 < 1.0 (x1), profit_factor 1.16 < 1.5 (x1) |
| `linear_channel_rev` | mc_p_value 0.456 > 0.05 (우연 가능성) (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1), profit_factor 1.44 < 1.5 (x1) |
| `relative_volume` | sharpe 0.83 < 1.0 (x1), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.462 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.430 > 0.05 (우연 가능성) (x1), sharpe 0.92 < 1.0 (x1) |
| `narrow_range` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.400 > 0.05 (우연 가능성) (x1), sharpe 0.63 < 1.0 (x1) |
| `value_area` | sharpe -2.38 < 1.0 (x1), profit_factor 0.56 < 1.5 (x1), mc_p_value 0.524 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x4) |
| `dema_cross` | trades 12 < 15 (x1), sharpe -1.12 < 1.0 (x1), profit_factor 0.72 < 1.5 (x1) |
| `positional_scaling` | sharpe -1.28 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1), mc_p_value 0.544 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 4 |
| mc_p_value 0.366 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.15 < 1.5 | 3 |
| mc_p_value 0.248 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.37 < 1.5 | 2 |
| max_drawdown 22.2% > 20% | 2 |
| mc_p_value 0.316 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.312 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.36 < 1.5 | 2 |
| mc_p_value 0.352 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +30.39% -> $13,039
- **Top 5 균등배분**: +93.47% -> $19,347
