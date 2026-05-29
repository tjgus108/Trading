# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-29T00:24:38.195428Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-29T00:28:25.645128Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1873322046, block=24)_
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
| 평균 수익률 | 36.89% |
| 최고 수익률 | 138.90% (lob_maker) |
| 최저 수익률 | -1.32% (dema_cross) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `lob_maker` | +138.90% | 6.96 | 53.9% | 2.03 | 117 | 9.5% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +125.25% | 6.93 | 50.9% | 1.90 | 153 | 10.0% | 0/4 | FAIL |
| 3 | `volume_breakout` | +82.34% | 6.11 | 54.6% | 2.06 | 92 | 7.0% | 0/4 | FAIL |
| 4 | `momentum_quality` | +77.91% | 6.06 | 50.6% | 1.81 | 125 | 7.1% | 0/4 | FAIL |
| 5 | `cmf` | +68.92% | 4.52 | 48.0% | 1.67 | 110 | 13.2% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | +58.08% | 4.43 | 49.9% | 1.72 | 86 | 10.2% | 0/4 | FAIL |
| 7 | `acceleration_band` | +55.35% | 4.86 | 50.9% | 1.87 | 86 | 8.2% | 0/4 | FAIL |
| 8 | `supertrend_multi` | +55.30% | 5.01 | 48.4% | 1.77 | 100 | 10.7% | 0/4 | FAIL |
| 9 | `relative_volume` | +39.06% | 5.18 | 55.4% | 2.43 | 54 | 5.4% | 0/4 | FAIL |
| 10 | `htf_ema` | +20.20% | 2.37 | 43.3% | 1.43 | 64 | 8.4% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 74.6 | p100 | 6.93 | 1.65 | 1.90 | 153 | 10.0% | 0/4 | FAIL |
| 2 | `lob_maker` | 73.4 | p95 | 6.96 | 1.55 | 2.03 | 117 | 9.5% | 0/4 | FAIL |
| 3 | `momentum_quality` | 73.3 | p90 | 6.06 | 1.28 | 1.81 | 125 | 7.1% | 0/4 | FAIL |
| 4 | `volume_breakout` | 70.6 | p85 | 6.11 | 1.64 | 2.06 | 92 | 7.0% | 0/4 | FAIL |
| 5 | `relative_volume` | 64.8 | p80 | 5.18 | 2.42 | 2.43 | 54 | 5.4% | 0/4 | FAIL |
| 6 | `acceleration_band` | 61.6 | p76 | 4.86 | 1.84 | 1.87 | 86 | 8.2% | 0/4 | FAIL |
| 7 | `roc_ma_cross` | 60.2 | p71 | 3.69 | 2.20 | 2.61 | 31 | 4.8% | 0/4 | FAIL |
| 8 | `supertrend_multi` | 59.9 | p66 | 5.01 | 1.81 | 1.77 | 100 | 10.7% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | 56.8 | p61 | 4.43 | 1.78 | 1.72 | 86 | 10.2% | 0/4 | FAIL |
| 10 | `cmf` | 54.3 | p57 | 4.52 | 1.99 | 1.67 | 110 | 13.2% | 0/4 | FAIL |
| 11 | `engulfing_zone` | 51.3 | p52 | 1.98 | 0.95 | 1.77 | 17 | 5.1% | 0/4 | FAIL |
| 12 | `htf_ema` | 49.6 | p47 | 2.37 | 1.19 | 1.43 | 64 | 8.4% | 0/4 | FAIL |
| 13 | `positional_scaling` | 45.6 | p42 | 1.54 | 0.95 | 1.48 | 22 | 7.0% | 0/4 | FAIL |
| 14 | `linear_channel_rev` | 45.4 | p38 | 1.14 | 0.87 | 1.30 | 32 | 6.0% | 0/4 | FAIL |
| 15 | `elder_impulse` | 45.3 | p33 | 1.40 | 0.79 | 1.27 | 51 | 8.4% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `lob_maker` | +138.90% | 6.96 | 2.03 | 117 | 0/4 | FAIL |
| `price_action_momentum` | +125.25% | 6.93 | 1.90 | 153 | 0/4 | FAIL |
| `volume_breakout` | +82.34% | 6.11 | 2.06 | 92 | 0/4 | FAIL |
| `momentum_quality` | +77.91% | 6.06 | 1.81 | 125 | 0/4 | FAIL |
| `cmf` | +68.92% | 4.52 | 1.67 | 110 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +58.08% | 4.43 | 1.72 | 86 | 0/4 | FAIL |
| `acceleration_band` | +55.35% | 4.86 | 1.87 | 86 | 0/4 | FAIL |
| `supertrend_multi` | +55.30% | 5.01 | 1.77 | 100 | 0/4 | FAIL |
| `relative_volume` | +39.06% | 5.18 | 2.43 | 54 | 0/4 | FAIL |
| `htf_ema` | +20.20% | 2.37 | 1.43 | 64 | 0/4 | FAIL |
| `roc_ma_cross` | +18.88% | 3.69 | 2.61 | 31 | 0/4 | FAIL |
| `volatility_cluster` | +18.19% | 2.23 | 1.43 | 79 | 0/4 | FAIL |
| `narrow_range` | +15.57% | 1.97 | 1.33 | 84 | 0/4 | FAIL |
| `frama` | +9.49% | 1.14 | 1.18 | 83 | 0/4 | FAIL |
| `elder_impulse` | +9.31% | 1.40 | 1.27 | 51 | 0/4 | FAIL |
| `engulfing_zone` | +8.71% | 1.98 | 1.77 | 17 | 0/4 | FAIL |
| `positional_scaling` | +6.35% | 1.54 | 1.48 | 22 | 0/4 | FAIL |
| `linear_channel_rev` | +4.66% | 1.14 | 1.30 | 32 | 0/4 | FAIL |
| `price_cluster` | +1.80% | 0.34 | 1.10 | 28 | 0/4 | FAIL |
| `value_area` | -0.31% | -0.07 | 1.05 | 12 | 0/4 | FAIL |
| `wick_reversal` | -1.07% | -1.23 | 0.00 | 1 | 0/4 | FAIL |
| `dema_cross` | -1.32% | -0.80 | 0.85 | 10 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `lob_maker` | mc_p_value 0.170 > 0.05 (우연 가능성) (x1), mc_p_value 0.168 > 0.05 (우연 가능성) (x1), mc_p_value 0.238 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | mc_p_value 0.178 > 0.05 (우연 가능성) (x1), mc_p_value 0.118 > 0.05 (우연 가능성) (x1), mc_p_value 0.158 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | mc_p_value 0.248 > 0.05 (우연 가능성) (x1), mc_p_value 0.220 > 0.05 (우연 가능성) (x1), mc_p_value 0.274 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.242 > 0.05 (우연 가능성) (x1), mc_p_value 0.172 > 0.05 (우연 가능성) (x1), mc_p_value 0.256 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.38 < 1.5 (x1), mc_p_value 0.342 > 0.05 (우연 가능성) (x1), mc_p_value 0.242 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.284 > 0.05 (우연 가능성) (x1), mc_p_value 0.278 > 0.05 (우연 가능성) (x1), profit_factor 1.50 < 1.5 (x1) |
| `acceleration_band` | mc_p_value 0.376 > 0.05 (우연 가능성) (x1), mc_p_value 0.248 > 0.05 (우연 가능성) (x1), mc_p_value 0.290 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | mc_p_value 0.186 > 0.05 (우연 가능성) (x1), mc_p_value 0.204 > 0.05 (우연 가능성) (x1), profit_factor 1.34 < 1.5 (x1) |
| `relative_volume` | mc_p_value 0.314 > 0.05 (우연 가능성) (x1), mc_p_value 0.272 > 0.05 (우연 가능성) (x1), mc_p_value 0.388 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | sharpe 0.73 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.470 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | mc_p_value 0.398 > 0.05 (우연 가능성) (x1), mc_p_value 0.380 > 0.05 (우연 가능성) (x1), mc_p_value 0.370 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | mc_p_value 0.322 > 0.05 (우연 가능성) (x1), mc_p_value 0.316 > 0.05 (우연 가능성) (x1), profit_factor 1.29 < 1.5 (x1) |
| `narrow_range` | profit_factor 1.44 < 1.5 (x1), mc_p_value 0.390 > 0.05 (우연 가능성) (x1), mc_p_value 0.356 > 0.05 (우연 가능성) (x1) |
| `frama` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1), sharpe -0.23 < 1.0 (x1) |
| `elder_impulse` | sharpe 0.10 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1), mc_p_value 0.512 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | mc_p_value 0.438 > 0.05 (우연 가능성) (x1), mc_p_value 0.486 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1) |
| `positional_scaling` | mc_p_value 0.480 > 0.05 (우연 가능성) (x1), sharpe -0.08 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1) |
| `linear_channel_rev` | sharpe 0.83 < 1.0 (x1), profit_factor 1.21 < 1.5 (x1), mc_p_value 0.474 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -0.16 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.520 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -1.26 < 1.0 (x1), profit_factor 0.75 < 1.5 (x1), mc_p_value 0.566 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.26 < 1.5 | 3 |
| mc_p_value 0.322 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.248 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.242 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.38 < 1.5 | 2 |
| mc_p_value 0.392 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.29 < 1.5 | 2 |
| mc_p_value 0.462 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.31 < 1.5 | 2 |
| sharpe 0.10 < 1.0 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +36.89% -> $13,689
- **Top 5 균등배분**: +98.66% -> $19,866


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-29T00:32:20.022109Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=1615268461, block=24)_
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
| 평균 수익률 | 6.34% |
| 최고 수익률 | 28.34% (momentum_quality) |
| 최저 수익률 | -9.26% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +28.34% | 3.18 | 44.7% | 1.42 | 105 | 11.5% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +19.52% | 1.72 | 41.0% | 1.19 | 148 | 21.5% | 0/4 | FAIL |
| 3 | `htf_ema` | +15.38% | 1.73 | 41.5% | 1.28 | 75 | 14.4% | 0/4 | FAIL |
| 4 | `elder_impulse` | +15.04% | 2.04 | 44.0% | 1.41 | 60 | 13.7% | 0/4 | FAIL |
| 5 | `cmf` | +13.52% | 1.29 | 40.8% | 1.17 | 119 | 19.6% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | +11.19% | 1.16 | 41.8% | 1.20 | 84 | 18.1% | 0/4 | FAIL |
| 7 | `narrow_range` | +9.40% | 1.24 | 41.4% | 1.21 | 96 | 11.5% | 0/4 | FAIL |
| 8 | `volume_breakout` | +8.84% | 1.06 | 41.1% | 1.17 | 93 | 13.5% | 0/4 | FAIL |
| 9 | `linear_channel_rev` | +8.10% | 1.92 | 46.1% | 1.49 | 33 | 4.5% | 0/4 | FAIL |
| 10 | `roc_ma_cross` | +7.46% | 1.50 | 42.6% | 1.38 | 38 | 6.6% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 82.4 | p100 | 3.18 | 0.82 | 1.42 | 105 | 11.5% | 0/4 | FAIL |
| 2 | `linear_channel_rev` | 73.8 | p95 | 1.92 | 0.56 | 1.49 | 33 | 4.5% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 67.2 | p90 | 1.72 | 1.53 | 1.19 | 148 | 21.5% | 0/4 | FAIL |
| 4 | `elder_impulse` | 66.7 | p85 | 2.04 | 1.74 | 1.41 | 60 | 13.7% | 0/4 | FAIL |
| 5 | `roc_ma_cross` | 65.7 | p80 | 1.50 | 1.54 | 1.38 | 38 | 6.6% | 0/4 | FAIL |
| 6 | `htf_ema` | 65.5 | p76 | 1.73 | 1.44 | 1.28 | 75 | 14.4% | 0/4 | FAIL |
| 7 | `narrow_range` | 65.3 | p71 | 1.24 | 1.48 | 1.21 | 96 | 11.5% | 0/4 | FAIL |
| 8 | `volatility_cluster` | 65.1 | p66 | 1.08 | 0.89 | 1.18 | 86 | 11.4% | 0/4 | FAIL |
| 9 | `cmf` | 63.8 | p61 | 1.29 | 1.21 | 1.17 | 119 | 19.6% | 0/4 | FAIL |
| 10 | `volume_breakout` | 63.7 | p57 | 1.06 | 1.09 | 1.17 | 93 | 13.5% | 0/4 | FAIL |
| 11 | `positional_scaling` | 61.9 | p52 | 1.06 | 1.29 | 1.33 | 28 | 7.7% | 0/4 | FAIL |
| 12 | `acceleration_band` | 60.5 | p47 | 0.45 | 0.92 | 1.08 | 102 | 13.5% | 0/4 | FAIL |
| 13 | `order_flow_imbalance_v2` | 59.2 | p42 | 1.16 | 1.63 | 1.20 | 84 | 18.1% | 0/4 | FAIL |
| 14 | `engulfing_zone` | 55.2 | p38 | 0.29 | 0.78 | 1.13 | 20 | 8.7% | 0/4 | FAIL |
| 15 | `relative_volume` | 54.9 | p33 | 0.67 | 2.08 | 1.18 | 62 | 13.2% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +28.34% | 3.18 | 1.42 | 105 | 0/4 | FAIL |
| `price_action_momentum` | +19.52% | 1.72 | 1.19 | 148 | 0/4 | FAIL |
| `htf_ema` | +15.38% | 1.73 | 1.28 | 75 | 0/4 | FAIL |
| `elder_impulse` | +15.04% | 2.04 | 1.41 | 60 | 0/4 | FAIL |
| `cmf` | +13.52% | 1.29 | 1.17 | 119 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +11.19% | 1.16 | 1.20 | 84 | 0/4 | FAIL |
| `narrow_range` | +9.40% | 1.24 | 1.21 | 96 | 0/4 | FAIL |
| `volume_breakout` | +8.84% | 1.06 | 1.17 | 93 | 0/4 | FAIL |
| `linear_channel_rev` | +8.10% | 1.92 | 1.49 | 33 | 0/4 | FAIL |
| `roc_ma_cross` | +7.46% | 1.50 | 1.38 | 38 | 0/4 | FAIL |
| `volatility_cluster` | +7.13% | 1.08 | 1.18 | 86 | 0/4 | FAIL |
| `relative_volume` | +4.63% | 0.67 | 1.18 | 62 | 0/4 | FAIL |
| `positional_scaling` | +4.41% | 1.06 | 1.33 | 28 | 0/4 | FAIL |
| `acceleration_band` | +3.08% | 0.45 | 1.08 | 102 | 0/4 | FAIL |
| `lob_maker` | +2.09% | 0.22 | 1.08 | 116 | 0/4 | FAIL |
| `engulfing_zone` | +0.99% | 0.29 | 1.13 | 20 | 0/4 | FAIL |
| `supertrend_multi` | +0.06% | 0.11 | 1.04 | 67 | 0/4 | FAIL |
| `wick_reversal` | -0.55% | -1.04 | 0.00 | 0 | 0/4 | FAIL |
| `price_cluster` | -2.65% | -0.37 | 0.97 | 33 | 0/4 | FAIL |
| `dema_cross` | -3.54% | -2.07 | 0.56 | 12 | 0/4 | FAIL |
| `value_area` | -3.81% | -1.42 | 0.75 | 17 | 0/4 | FAIL |
| `frama` | -9.26% | -1.66 | 0.90 | 79 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | mc_p_value 0.346 > 0.05 (우연 가능성) (x1), profit_factor 1.35 < 1.5 (x1), mc_p_value 0.380 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | max_drawdown 25.1% > 20% (x2), profit_factor 1.33 < 1.5 (x1), mc_p_value 0.314 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 1.21 < 1.5 (x1), mc_p_value 0.458 > 0.05 (우연 가능성) (x1), mc_p_value 0.348 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | mc_p_value 0.414 > 0.05 (우연 가능성) (x1), sharpe 0.50 < 1.0 (x1), max_drawdown 21.0% > 20% (x1) |
| `cmf` | mc_p_value 0.438 > 0.05 (우연 가능성) (x2), max_drawdown 22.8% > 20% (x1), profit_factor 1.17 < 1.5 (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.39 < 1.5 (x1), mc_p_value 0.380 > 0.05 (우연 가능성) (x1), profit_factor 1.24 < 1.5 (x1) |
| `narrow_range` | profit_factor 1.05 < 1.5 (x2), mc_p_value 0.374 > 0.05 (우연 가능성) (x1), sharpe -0.02 < 1.0 (x1) |
| `volume_breakout` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.432 > 0.05 (우연 가능성) (x1), profit_factor 1.21 < 1.5 (x1) |
| `linear_channel_rev` | profit_factor 1.44 < 1.5 (x2), mc_p_value 0.420 > 0.05 (우연 가능성) (x2), mc_p_value 0.432 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 1.42 < 1.5 (x1), mc_p_value 0.476 > 0.05 (우연 가능성) (x1), mc_p_value 0.362 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.29 < 1.5 (x1), mc_p_value 0.408 > 0.05 (우연 가능성) (x1), sharpe -0.36 < 1.0 (x1) |
| `relative_volume` | profit_factor 1.50 < 1.5 (x1), mc_p_value 0.416 > 0.05 (우연 가능성) (x1), profit_factor 1.48 < 1.5 (x1) |
| `positional_scaling` | sharpe -0.08 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1), mc_p_value 0.498 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | sharpe 1.00 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.470 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.17 < 1.5 (x1), mc_p_value 0.430 > 0.05 (우연 가능성) (x1), sharpe -0.78 < 1.0 (x1) |
| `engulfing_zone` | sharpe 0.36 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.494 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | sharpe -0.86 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1), mc_p_value 0.524 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | sharpe -2.08 < 1.0 (x2), profit_factor 0.00 < 1.5 (x2), trades 1 < 15 (x2) |
| `price_cluster` | sharpe 0.61 < 1.0 (x1), profit_factor 1.16 < 1.5 (x1), mc_p_value 0.484 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe -0.41 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1), mc_p_value 0.500 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.17 < 1.5 | 5 |
| mc_p_value 0.458 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.476 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.438 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.98 < 1.5 | 3 |
| mc_p_value 0.380 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.47 < 1.5 | 2 |
| profit_factor 1.29 < 1.5 | 2 |
| max_drawdown 25.1% > 20% | 2 |
| profit_factor 1.18 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +6.34% -> $10,634
- **Top 5 균등배분**: +18.36% -> $11,836


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-29T00:36:30.534825Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=2091655183, block=24)_
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
| 평균 수익률 | 14.26% |
| 최고 수익률 | 46.43% (volatility_cluster) |
| 최저 수익률 | -6.12% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `volatility_cluster` | +46.43% | 5.52 | 55.7% | 2.06 | 74 | 7.1% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +44.71% | 3.36 | 45.1% | 1.36 | 149 | 12.9% | 0/4 | FAIL |
| 3 | `momentum_quality` | +43.77% | 4.00 | 46.9% | 1.53 | 115 | 8.2% | 0/4 | FAIL |
| 4 | `volume_breakout` | +39.19% | 3.72 | 46.7% | 1.56 | 93 | 10.2% | 0/4 | FAIL |
| 5 | `order_flow_imbalance_v2` | +32.44% | 2.98 | 45.1% | 1.47 | 83 | 12.8% | 0/4 | FAIL |
| 6 | `lob_maker` | +27.69% | 2.20 | 41.7% | 1.27 | 124 | 14.6% | 0/4 | FAIL |
| 7 | `acceleration_band` | +21.74% | 2.14 | 42.4% | 1.31 | 100 | 15.3% | 0/4 | FAIL |
| 8 | `cmf` | +19.08% | 1.33 | 40.0% | 1.19 | 132 | 24.2% | 0/4 | FAIL |
| 9 | `narrow_range` | +17.85% | 2.17 | 41.9% | 1.32 | 92 | 9.1% | 0/4 | FAIL |
| 10 | `supertrend_multi` | +14.02% | 1.72 | 41.5% | 1.23 | 114 | 13.4% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `volatility_cluster` | 60.2 | p100 | 5.52 | 1.01 | 2.06 | 74 | 7.1% | 0/4 | FAIL |
| 2 | `volume_breakout` | 54.0 | p95 | 3.72 | 0.70 | 1.56 | 93 | 10.2% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 53.7 | p90 | 3.36 | 1.22 | 1.36 | 149 | 12.9% | 0/4 | FAIL |
| 4 | `momentum_quality` | 52.6 | p85 | 4.00 | 1.86 | 1.53 | 115 | 8.2% | 0/4 | FAIL |
| 5 | `wick_reversal` | 51.7 | p80 | 0.23 | 1.50 | 250.65 | 1 | 0.6% | 0/4 | FAIL |
| 6 | `narrow_range` | 48.6 | p76 | 2.17 | 0.60 | 1.32 | 92 | 9.1% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | 47.4 | p71 | 2.98 | 0.88 | 1.47 | 83 | 12.8% | 0/4 | FAIL |
| 8 | `lob_maker` | 47.3 | p66 | 2.20 | 0.81 | 1.27 | 124 | 14.6% | 0/4 | FAIL |
| 9 | `supertrend_multi` | 44.3 | p61 | 1.72 | 0.96 | 1.23 | 114 | 13.4% | 0/4 | FAIL |
| 10 | `relative_volume` | 42.9 | p57 | 1.54 | 0.54 | 1.30 | 55 | 8.6% | 0/4 | FAIL |
| 11 | `dema_cross` | 41.0 | p52 | 1.54 | 0.81 | 1.71 | 12 | 2.4% | 0/4 | FAIL |
| 12 | `acceleration_band` | 40.1 | p47 | 2.14 | 1.59 | 1.31 | 100 | 15.3% | 0/4 | FAIL |
| 13 | `engulfing_zone` | 35.3 | p42 | 0.39 | 0.47 | 1.14 | 20 | 7.7% | 0/4 | FAIL |
| 14 | `elder_impulse` | 33.3 | p38 | 1.00 | 1.80 | 1.25 | 55 | 9.4% | 0/4 | FAIL |
| 15 | `price_cluster` | 32.9 | p33 | 0.17 | 0.81 | 1.07 | 34 | 9.4% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `volatility_cluster` | +46.43% | 5.52 | 2.06 | 74 | 0/4 | FAIL |
| `price_action_momentum` | +44.71% | 3.36 | 1.36 | 149 | 0/4 | FAIL |
| `momentum_quality` | +43.77% | 4.00 | 1.53 | 115 | 0/4 | FAIL |
| `volume_breakout` | +39.19% | 3.72 | 1.56 | 93 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +32.44% | 2.98 | 1.47 | 83 | 0/4 | FAIL |
| `lob_maker` | +27.69% | 2.20 | 1.27 | 124 | 0/4 | FAIL |
| `acceleration_band` | +21.74% | 2.14 | 1.31 | 100 | 0/4 | FAIL |
| `cmf` | +19.08% | 1.33 | 1.19 | 132 | 0/4 | FAIL |
| `narrow_range` | +17.85% | 2.17 | 1.32 | 92 | 0/4 | FAIL |
| `supertrend_multi` | +14.02% | 1.72 | 1.23 | 114 | 0/4 | FAIL |
| `relative_volume` | +8.37% | 1.54 | 1.30 | 55 | 0/4 | FAIL |
| `elder_impulse` | +6.97% | 1.00 | 1.25 | 55 | 0/4 | FAIL |
| `htf_ema` | +6.87% | 0.67 | 1.18 | 65 | 0/4 | FAIL |
| `dema_cross` | +4.28% | 1.54 | 1.71 | 12 | 0/4 | FAIL |
| `engulfing_zone` | +1.36% | 0.39 | 1.14 | 20 | 0/4 | FAIL |
| `wick_reversal` | +0.79% | 0.23 | 250.65 | 1 | 0/4 | FAIL |
| `price_cluster` | +0.73% | 0.17 | 1.07 | 34 | 0/4 | FAIL |
| `value_area` | -1.19% | -0.75 | 0.94 | 12 | 0/4 | FAIL |
| `positional_scaling` | -4.04% | -1.01 | 0.86 | 27 | 0/4 | FAIL |
| `linear_channel_rev` | -5.59% | -1.39 | 0.81 | 33 | 0/4 | FAIL |
| `roc_ma_cross` | -5.75% | -1.55 | 0.81 | 31 | 0/4 | FAIL |
| `frama` | -6.12% | -0.74 | 0.99 | 89 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `volatility_cluster` | mc_p_value 0.300 > 0.05 (우연 가능성) (x1), mc_p_value 0.290 > 0.05 (우연 가능성) (x1), mc_p_value 0.298 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | mc_p_value 0.274 > 0.05 (우연 가능성) (x1), profit_factor 1.23 < 1.5 (x1), mc_p_value 0.364 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.174 > 0.05 (우연 가능성) (x1), profit_factor 1.37 < 1.5 (x1), mc_p_value 0.348 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | mc_p_value 0.370 > 0.05 (우연 가능성) (x1), mc_p_value 0.322 > 0.05 (우연 가능성) (x1), mc_p_value 0.372 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.424 > 0.05 (우연 가능성) (x1), mc_p_value 0.342 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.42 < 1.5 (x1), mc_p_value 0.344 > 0.05 (우연 가능성) (x1), profit_factor 1.25 < 1.5 (x1) |
| `acceleration_band` | sharpe 0.23 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1), mc_p_value 0.522 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.374 > 0.05 (우연 가능성) (x1), sharpe -1.06 < 1.0 (x1) |
| `narrow_range` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.392 > 0.05 (우연 가능성) (x1), profit_factor 1.29 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.382 > 0.05 (우연 가능성) (x1), profit_factor 1.15 < 1.5 (x1) |
| `relative_volume` | sharpe 0.73 < 1.0 (x1), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.480 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -0.23 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.530 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.380 > 0.05 (우연 가능성) (x1), sharpe -1.17 < 1.0 (x1) |
| `dema_cross` | trades 10 < 15 (x2), sharpe 0.17 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1) |
| `engulfing_zone` | sharpe 0.55 < 1.0 (x1), profit_factor 1.17 < 1.5 (x1), mc_p_value 0.484 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | trades 1 < 15 (x2), no trades generated (x1), sharpe -2.07 < 1.0 (x1) |
| `price_cluster` | sharpe 0.94 < 1.0 (x1), profit_factor 1.24 < 1.5 (x1), mc_p_value 0.460 > 0.05 (우연 가능성) (x1) |
| `value_area` | trades 10 < 15 (x2), sharpe 0.65 < 1.0 (x1), profit_factor 1.26 < 1.5 (x1) |
| `positional_scaling` | profit_factor 0.79 < 1.5 (x2), sharpe 0.69 < 1.0 (x1), profit_factor 1.19 < 1.5 (x1) |
| `linear_channel_rev` | sharpe -1.04 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1), mc_p_value 0.506 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 10 < 15 | 4 |
| mc_p_value 0.372 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.19 < 1.5 | 3 |
| mc_p_value 0.488 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.514 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.79 < 1.5 | 3 |
| mc_p_value 0.364 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.30 < 1.5 | 2 |
| mc_p_value 0.348 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.46 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +14.26% -> $11,426
- **Top 5 균등배분**: +41.31% -> $14,131
