# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-27T20:42:09.002309Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-27T20:45:08.815390Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=584482260, block=36)_
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
| 평균 수익률 | 30.98% |
| 최고 수익률 | 120.35% (price_action_momentum) |
| 최저 수익률 | -0.31% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +120.35% | 6.58 | 49.5% | 1.79 | 166 | 13.6% | 0/4 | FAIL |
| 2 | `supertrend_multi` | +91.56% | 7.39 | 55.7% | 2.25 | 118 | 6.8% | 0/4 | FAIL |
| 3 | `momentum_quality` | +77.31% | 6.25 | 51.8% | 1.93 | 123 | 8.1% | 0/4 | FAIL |
| 4 | `acceleration_band` | +63.34% | 5.36 | 50.5% | 1.94 | 92 | 10.0% | 0/4 | FAIL |
| 5 | `volume_breakout` | +56.12% | 4.68 | 50.1% | 1.79 | 91 | 10.3% | 0/4 | FAIL |
| 6 | `volatility_cluster` | +45.73% | 5.58 | 55.0% | 2.18 | 74 | 5.4% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | +35.27% | 3.24 | 46.5% | 1.52 | 81 | 10.0% | 0/4 | FAIL |
| 8 | `cmf` | +34.14% | 2.53 | 42.6% | 1.31 | 124 | 18.5% | 0/4 | FAIL |
| 9 | `elder_impulse` | +28.30% | 3.70 | 53.3% | 1.87 | 49 | 7.7% | 0/4 | FAIL |
| 10 | `htf_ema` | +28.08% | 3.06 | 48.4% | 1.57 | 66 | 11.0% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 58.8 | p100 | 7.39 | 1.31 | 2.25 | 118 | 6.8% | 0/4 | FAIL |
| 2 | `momentum_quality` | 55.2 | p95 | 6.25 | 1.07 | 1.93 | 123 | 8.1% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 55.0 | p90 | 6.58 | 1.21 | 1.79 | 166 | 13.6% | 0/4 | FAIL |
| 4 | `wick_reversal` | 50.2 | p85 | 0.99 | 0.99 | 500.00 | 0 | 0.0% | 0/4 | FAIL |
| 5 | `volatility_cluster` | 49.9 | p80 | 5.58 | 1.13 | 2.18 | 74 | 5.4% | 0/4 | FAIL |
| 6 | `acceleration_band` | 46.6 | p76 | 5.36 | 1.16 | 1.94 | 92 | 10.0% | 0/4 | FAIL |
| 7 | `volume_breakout` | 43.4 | p71 | 4.68 | 1.21 | 1.79 | 91 | 10.3% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | 42.7 | p66 | 3.24 | 0.30 | 1.52 | 81 | 10.0% | 0/4 | FAIL |
| 9 | `elder_impulse` | 39.9 | p61 | 3.70 | 0.88 | 1.87 | 49 | 7.7% | 0/4 | FAIL |
| 10 | `narrow_range` | 37.9 | p57 | 3.32 | 1.28 | 1.54 | 91 | 9.9% | 0/4 | FAIL |
| 11 | `roc_ma_cross` | 36.6 | p52 | 2.74 | 0.85 | 1.81 | 30 | 5.3% | 0/4 | FAIL |
| 12 | `htf_ema` | 34.8 | p47 | 3.06 | 1.11 | 1.57 | 66 | 11.0% | 0/4 | FAIL |
| 13 | `lob_maker` | 33.9 | p42 | 2.08 | 0.50 | 1.25 | 123 | 18.3% | 0/4 | FAIL |
| 14 | `relative_volume` | 33.0 | p38 | 2.67 | 1.11 | 1.57 | 52 | 9.7% | 0/4 | FAIL |
| 15 | `cmf` | 31.1 | p33 | 2.53 | 1.22 | 1.31 | 124 | 18.5% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +120.35% | 6.58 | 1.79 | 166 | 0/4 | FAIL |
| `supertrend_multi` | +91.56% | 7.39 | 2.25 | 118 | 0/4 | FAIL |
| `momentum_quality` | +77.31% | 6.25 | 1.93 | 123 | 0/4 | FAIL |
| `acceleration_band` | +63.34% | 5.36 | 1.94 | 92 | 0/4 | FAIL |
| `volume_breakout` | +56.12% | 4.68 | 1.79 | 91 | 0/4 | FAIL |
| `volatility_cluster` | +45.73% | 5.58 | 2.18 | 74 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +35.27% | 3.24 | 1.52 | 81 | 0/4 | FAIL |
| `cmf` | +34.14% | 2.53 | 1.31 | 124 | 0/4 | FAIL |
| `elder_impulse` | +28.30% | 3.70 | 1.87 | 49 | 0/4 | FAIL |
| `htf_ema` | +28.08% | 3.06 | 1.57 | 66 | 0/4 | FAIL |
| `narrow_range` | +27.54% | 3.32 | 1.54 | 91 | 0/4 | FAIL |
| `lob_maker` | +25.39% | 2.08 | 1.25 | 123 | 0/4 | FAIL |
| `relative_volume` | +15.91% | 2.67 | 1.57 | 52 | 0/4 | FAIL |
| `roc_ma_cross` | +12.29% | 2.74 | 1.81 | 30 | 0/4 | FAIL |
| `linear_channel_rev` | +5.39% | 1.11 | 1.27 | 40 | 0/4 | FAIL |
| `positional_scaling` | +5.25% | 1.15 | 1.47 | 22 | 0/4 | FAIL |
| `price_cluster` | +3.79% | 0.71 | 1.20 | 34 | 0/4 | FAIL |
| `dema_cross` | +2.42% | 0.69 | 1.24 | 11 | 0/4 | FAIL |
| `value_area` | +1.89% | 0.71 | 1.33 | 14 | 0/4 | FAIL |
| `wick_reversal` | +1.42% | 0.99 | 500.00 | 0 | 0/4 | FAIL |
| `frama` | +0.39% | 0.09 | 1.06 | 92 | 0/4 | FAIL |
| `engulfing_zone` | -0.31% | -0.15 | 1.07 | 20 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.124 > 0.05 (우연 가능성) (x1), mc_p_value 0.240 > 0.05 (우연 가능성) (x1), mc_p_value 0.234 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | mc_p_value 0.244 > 0.05 (우연 가능성) (x1), mc_p_value 0.196 > 0.05 (우연 가능성) (x1), mc_p_value 0.194 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.292 > 0.05 (우연 가능성) (x1), mc_p_value 0.232 > 0.05 (우연 가능성) (x1), mc_p_value 0.192 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | mc_p_value 0.244 > 0.05 (우연 가능성) (x1), mc_p_value 0.284 > 0.05 (우연 가능성) (x1), mc_p_value 0.346 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | mc_p_value 0.340 > 0.05 (우연 가능성) (x1), mc_p_value 0.400 > 0.05 (우연 가능성) (x1), mc_p_value 0.330 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | mc_p_value 0.270 > 0.05 (우연 가능성) (x1), mc_p_value 0.294 > 0.05 (우연 가능성) (x1), mc_p_value 0.318 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.42 < 1.5 (x1), mc_p_value 0.382 > 0.05 (우연 가능성) (x1), mc_p_value 0.374 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.302 > 0.05 (우연 가능성) (x1), max_drawdown 22.4% > 20% (x1) |
| `elder_impulse` | mc_p_value 0.346 > 0.05 (우연 가능성) (x1), mc_p_value 0.396 > 0.05 (우연 가능성) (x1), mc_p_value 0.410 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | mc_p_value 0.404 > 0.05 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1), mc_p_value 0.454 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | mc_p_value 0.312 > 0.05 (우연 가능성) (x1), profit_factor 1.50 < 1.5 (x1), mc_p_value 0.376 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.374 > 0.05 (우연 가능성) (x1), profit_factor 1.21 < 1.5 (x1) |
| `relative_volume` | profit_factor 1.20 < 1.5 (x1), mc_p_value 0.468 > 0.05 (우연 가능성) (x1), mc_p_value 0.422 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 1.44 < 1.5 (x1), mc_p_value 0.476 > 0.05 (우연 가능성) (x1), mc_p_value 0.444 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe 0.92 < 1.0 (x1), profit_factor 1.20 < 1.5 (x1), mc_p_value 0.460 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | mc_p_value 0.438 > 0.05 (우연 가능성) (x1), mc_p_value 0.404 > 0.05 (우연 가능성) (x1), sharpe -0.02 < 1.0 (x1) |
| `price_cluster` | mc_p_value 0.398 > 0.05 (우연 가능성) (x1), sharpe 0.52 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1) |
| `dema_cross` | sharpe -0.97 < 1.0 (x1), profit_factor 0.62 < 1.5 (x1), trades 4 < 15 (x1) |
| `value_area` | sharpe 0.86 < 1.0 (x1), profit_factor 1.32 < 1.5 (x1), trades 14 < 15 (x1) |
| `wick_reversal` | no trades generated (x2), trades 1 < 15 (x2) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.532 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.196 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.244 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.346 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.318 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.382 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.374 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.48 < 1.5 | 2 |
| mc_p_value 0.482 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.436 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +30.98% -> $13,098
- **Top 5 균등배분**: +81.73% -> $18,174


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-27T20:48:03.805373Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=1387369097, block=36)_
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
| 평균 수익률 | 12.34% |
| 최고 수익률 | 43.53% (momentum_quality) |
| 최저 수익률 | -20.36% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +43.53% | 4.23 | 46.5% | 1.59 | 120 | 10.3% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +40.84% | 3.12 | 43.0% | 1.37 | 160 | 16.4% | 0/4 | FAIL |
| 3 | `volume_breakout` | +37.30% | 3.53 | 45.8% | 1.58 | 86 | 8.4% | 0/4 | FAIL |
| 4 | `supertrend_multi` | +35.43% | 3.76 | 46.2% | 1.54 | 103 | 7.1% | 0/4 | FAIL |
| 5 | `narrow_range` | +30.22% | 3.69 | 49.1% | 1.63 | 80 | 6.2% | 0/4 | FAIL |
| 6 | `htf_ema` | +24.82% | 2.77 | 46.0% | 1.47 | 72 | 10.0% | 0/4 | FAIL |
| 7 | `positional_scaling` | +17.53% | 3.47 | 51.9% | 2.13 | 31 | 4.3% | 0/4 | FAIL |
| 8 | `lob_maker` | +16.39% | 1.50 | 40.2% | 1.18 | 123 | 12.6% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | +15.26% | 1.64 | 41.3% | 1.25 | 81 | 11.7% | 0/4 | FAIL |
| 10 | `volatility_cluster` | +10.33% | 1.59 | 41.4% | 1.26 | 77 | 10.0% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `narrow_range` | 76.1 | p100 | 3.69 | 0.45 | 1.63 | 80 | 6.2% | 0/4 | FAIL |
| 2 | `supertrend_multi` | 75.2 | p95 | 3.76 | 0.73 | 1.54 | 103 | 7.1% | 0/4 | FAIL |
| 3 | `momentum_quality` | 73.4 | p90 | 4.23 | 1.29 | 1.59 | 120 | 10.3% | 0/4 | FAIL |
| 4 | `positional_scaling` | 70.9 | p85 | 3.47 | 1.23 | 2.13 | 31 | 4.3% | 0/4 | FAIL |
| 5 | `volume_breakout` | 69.8 | p80 | 3.53 | 1.07 | 1.58 | 86 | 8.4% | 0/4 | FAIL |
| 6 | `htf_ema` | 67.6 | p76 | 2.77 | 0.43 | 1.47 | 72 | 10.0% | 0/4 | FAIL |
| 7 | `price_action_momentum` | 66.4 | p71 | 3.12 | 1.31 | 1.37 | 160 | 16.4% | 0/4 | FAIL |
| 8 | `lob_maker` | 63.2 | p66 | 1.50 | 0.33 | 1.18 | 123 | 12.6% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | 59.4 | p61 | 1.64 | 0.57 | 1.25 | 81 | 11.7% | 0/4 | FAIL |
| 10 | `volatility_cluster` | 58.7 | p57 | 1.59 | 0.76 | 1.26 | 77 | 10.0% | 0/4 | FAIL |
| 11 | `value_area` | 57.5 | p52 | 1.55 | 1.24 | 1.65 | 17 | 3.1% | 0/4 | FAIL |
| 12 | `roc_ma_cross` | 56.8 | p47 | 1.58 | 0.76 | 1.36 | 40 | 8.9% | 0/4 | FAIL |
| 13 | `linear_channel_rev` | 54.0 | p42 | 1.86 | 1.77 | 1.56 | 33 | 6.0% | 0/4 | FAIL |
| 14 | `relative_volume` | 49.4 | p38 | 0.99 | 1.57 | 1.24 | 47 | 6.8% | 0/4 | FAIL |
| 15 | `acceleration_band` | 48.6 | p33 | -0.06 | 0.34 | 1.02 | 101 | 19.3% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +43.53% | 4.23 | 1.59 | 120 | 0/4 | FAIL |
| `price_action_momentum` | +40.84% | 3.12 | 1.37 | 160 | 0/4 | FAIL |
| `volume_breakout` | +37.30% | 3.53 | 1.58 | 86 | 0/4 | FAIL |
| `supertrend_multi` | +35.43% | 3.76 | 1.54 | 103 | 0/4 | FAIL |
| `narrow_range` | +30.22% | 3.69 | 1.63 | 80 | 0/4 | FAIL |
| `htf_ema` | +24.82% | 2.77 | 1.47 | 72 | 0/4 | FAIL |
| `positional_scaling` | +17.53% | 3.47 | 2.13 | 31 | 0/4 | FAIL |
| `lob_maker` | +16.39% | 1.50 | 1.18 | 123 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +15.26% | 1.64 | 1.25 | 81 | 0/4 | FAIL |
| `volatility_cluster` | +10.33% | 1.59 | 1.26 | 77 | 0/4 | FAIL |
| `linear_channel_rev` | +8.51% | 1.86 | 1.56 | 33 | 0/4 | FAIL |
| `roc_ma_cross` | +7.46% | 1.58 | 1.36 | 40 | 0/4 | FAIL |
| `relative_volume` | +5.24% | 0.99 | 1.24 | 47 | 0/4 | FAIL |
| `engulfing_zone` | +5.15% | 0.86 | 1.30 | 24 | 0/4 | FAIL |
| `value_area` | +4.98% | 1.55 | 1.65 | 17 | 0/4 | FAIL |
| `price_cluster` | +3.21% | 0.50 | 1.15 | 44 | 0/4 | FAIL |
| `wick_reversal` | -0.56% | -1.04 | 0.00 | 0 | 0/4 | FAIL |
| `elder_impulse` | -1.21% | -0.13 | 1.03 | 62 | 0/4 | FAIL |
| `dema_cross` | -1.51% | -0.55 | 0.91 | 15 | 0/4 | FAIL |
| `acceleration_band` | -2.13% | -0.06 | 1.02 | 101 | 0/4 | FAIL |
| `cmf` | -8.85% | -0.79 | 0.96 | 122 | 0/4 | FAIL |
| `frama` | -20.36% | -2.66 | 0.76 | 84 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | mc_p_value 0.246 > 0.05 (우연 가능성) (x1), mc_p_value 0.276 > 0.05 (우연 가능성) (x1), profit_factor 1.36 < 1.5 (x1) |
| `price_action_momentum` | profit_factor 1.44 < 1.5 (x1), mc_p_value 0.304 > 0.05 (우연 가능성) (x1), max_drawdown 21.4% > 20% (x1) |
| `volume_breakout` | mc_p_value 0.320 > 0.05 (우연 가능성) (x1), mc_p_value 0.344 > 0.05 (우연 가능성) (x1), profit_factor 1.49 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.49 < 1.5 (x1), mc_p_value 0.320 > 0.05 (우연 가능성) (x1), profit_factor 1.46 < 1.5 (x1) |
| `narrow_range` | mc_p_value 0.374 > 0.05 (우연 가능성) (x1), mc_p_value 0.358 > 0.05 (우연 가능성) (x1), mc_p_value 0.402 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.404 > 0.05 (우연 가능성) (x1), profit_factor 1.36 < 1.5 (x1) |
| `positional_scaling` | mc_p_value 0.362 > 0.05 (우연 가능성) (x1), mc_p_value 0.398 > 0.05 (우연 가능성) (x1), mc_p_value 0.432 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.19 < 1.5 (x1), mc_p_value 0.396 > 0.05 (우연 가능성) (x1), profit_factor 1.15 < 1.5 (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.30 < 1.5 (x1), mc_p_value 0.406 > 0.05 (우연 가능성) (x1), profit_factor 1.16 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.430 > 0.05 (우연 가능성) (x1), profit_factor 1.43 < 1.5 (x1) |
| `linear_channel_rev` | sharpe -1.15 < 1.0 (x1), profit_factor 0.84 < 1.5 (x1), mc_p_value 0.534 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | mc_p_value 0.434 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1), mc_p_value 0.420 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.460 > 0.05 (우연 가능성) (x1), mc_p_value 0.404 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -0.85 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.510 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe 0.50 < 1.0 (x1), profit_factor 1.16 < 1.5 (x1), mc_p_value 0.468 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | mc_p_value 0.380 > 0.05 (우연 가능성) (x1), sharpe 0.10 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1) |
| `wick_reversal` | sharpe -2.08 < 1.0 (x2), profit_factor 0.00 < 1.5 (x2), trades 1 < 15 (x2) |
| `elder_impulse` | sharpe -2.84 < 1.0 (x1), max_drawdown 29.9% > 20% (x1), profit_factor 0.69 < 1.5 (x1) |
| `dema_cross` | sharpe -1.46 < 1.0 (x1), profit_factor 0.69 < 1.5 (x1), mc_p_value 0.532 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | sharpe 0.10 < 1.0 (x1), max_drawdown 22.5% > 20% (x1), profit_factor 1.04 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.16 < 1.5 | 3 |
| mc_p_value 0.420 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.462 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.440 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.96 < 1.5 | 3 |
| profit_factor 1.36 < 1.5 | 2 |
| profit_factor 1.44 < 1.5 | 2 |
| mc_p_value 0.320 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.49 < 1.5 | 2 |
| mc_p_value 0.394 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +12.34% -> $11,234
- **Top 5 균등배분**: +37.46% -> $13,746


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-27T20:51:07.407446Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=190220175, block=36)_
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
| 평균 수익률 | 18.74% |
| 최고 수익률 | 77.48% (price_action_momentum) |
| 최저 수익률 | -8.06% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +77.48% | 5.13 | 49.2% | 1.64 | 147 | 11.5% | 0/4 | FAIL |
| 2 | `cmf` | +68.82% | 4.56 | 47.5% | 1.61 | 116 | 13.1% | 0/4 | FAIL |
| 3 | `momentum_quality` | +38.47% | 3.96 | 47.6% | 1.55 | 110 | 8.0% | 0/4 | FAIL |
| 4 | `htf_ema` | +33.80% | 3.31 | 47.6% | 1.59 | 71 | 9.7% | 0/4 | FAIL |
| 5 | `supertrend_multi` | +32.06% | 2.48 | 41.0% | 1.24 | 211 | 22.3% | 0/4 | FAIL |
| 6 | `volume_breakout` | +31.52% | 2.72 | 43.8% | 1.45 | 94 | 13.9% | 0/4 | FAIL |
| 7 | `narrow_range` | +25.65% | 3.03 | 45.4% | 1.45 | 95 | 12.1% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | +24.50% | 2.32 | 43.9% | 1.36 | 79 | 15.2% | 0/4 | FAIL |
| 9 | `acceleration_band` | +24.29% | 2.48 | 44.2% | 1.37 | 94 | 14.4% | 0/4 | FAIL |
| 10 | `volatility_cluster` | +20.16% | 2.54 | 44.3% | 1.47 | 78 | 11.0% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 69.5 | p100 | 5.13 | 1.94 | 1.64 | 147 | 11.5% | 0/4 | FAIL |
| 2 | `value_area` | 67.7 | p95 | 2.87 | 0.91 | 2.71 | 16 | 3.2% | 0/4 | FAIL |
| 3 | `momentum_quality` | 67.6 | p90 | 3.96 | 0.38 | 1.55 | 110 | 8.0% | 0/4 | FAIL |
| 4 | `cmf` | 66.9 | p85 | 4.56 | 0.82 | 1.61 | 116 | 13.1% | 0/4 | FAIL |
| 5 | `narrow_range` | 60.1 | p80 | 3.03 | 0.10 | 1.45 | 95 | 12.1% | 0/4 | FAIL |
| 6 | `htf_ema` | 57.6 | p76 | 3.31 | 1.70 | 1.59 | 71 | 9.7% | 0/4 | FAIL |
| 7 | `supertrend_multi` | 55.6 | p71 | 2.48 | 1.01 | 1.24 | 211 | 22.3% | 0/4 | FAIL |
| 8 | `acceleration_band` | 51.5 | p66 | 2.48 | 1.52 | 1.37 | 94 | 14.4% | 0/4 | FAIL |
| 9 | `volume_breakout` | 50.9 | p57 | 2.72 | 2.42 | 1.45 | 94 | 13.9% | 0/4 | FAIL |
| 10 | `volatility_cluster` | 50.9 | p61 | 2.54 | 2.37 | 1.47 | 78 | 11.0% | 0/4 | FAIL |
| 11 | `order_flow_imbalance_v2` | 49.6 | p52 | 2.32 | 1.35 | 1.36 | 79 | 15.2% | 0/4 | FAIL |
| 12 | `roc_ma_cross` | 48.6 | p47 | 1.52 | 1.03 | 1.38 | 36 | 7.7% | 0/4 | FAIL |
| 13 | `linear_channel_rev` | 47.0 | p42 | 1.09 | 0.73 | 1.28 | 32 | 6.7% | 0/4 | FAIL |
| 14 | `dema_cross` | 45.3 | p38 | 0.62 | 0.91 | 1.26 | 10 | 2.4% | 0/4 | FAIL |
| 15 | `relative_volume` | 44.8 | p33 | 0.84 | 0.46 | 1.17 | 53 | 11.1% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +77.48% | 5.13 | 1.64 | 147 | 0/4 | FAIL |
| `cmf` | +68.82% | 4.56 | 1.61 | 116 | 0/4 | FAIL |
| `momentum_quality` | +38.47% | 3.96 | 1.55 | 110 | 0/4 | FAIL |
| `htf_ema` | +33.80% | 3.31 | 1.59 | 71 | 0/4 | FAIL |
| `supertrend_multi` | +32.06% | 2.48 | 1.24 | 211 | 0/4 | FAIL |
| `volume_breakout` | +31.52% | 2.72 | 1.45 | 94 | 0/4 | FAIL |
| `narrow_range` | +25.65% | 3.03 | 1.45 | 95 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +24.50% | 2.32 | 1.36 | 79 | 0/4 | FAIL |
| `acceleration_band` | +24.29% | 2.48 | 1.37 | 94 | 0/4 | FAIL |
| `volatility_cluster` | +20.16% | 2.54 | 1.47 | 78 | 0/4 | FAIL |
| `lob_maker` | +17.60% | 0.80 | 1.15 | 125 | 0/4 | FAIL |
| `value_area` | +9.04% | 2.87 | 2.71 | 16 | 0/4 | FAIL |
| `roc_ma_cross` | +6.83% | 1.52 | 1.38 | 36 | 0/4 | FAIL |
| `elder_impulse` | +4.50% | 0.51 | 1.13 | 56 | 0/4 | FAIL |
| `linear_channel_rev` | +4.40% | 1.09 | 1.28 | 32 | 0/4 | FAIL |
| `relative_volume` | +4.13% | 0.84 | 1.17 | 53 | 0/4 | FAIL |
| `positional_scaling` | +3.74% | 0.68 | 1.33 | 29 | 0/4 | FAIL |
| `dema_cross` | +1.67% | 0.62 | 1.26 | 10 | 0/4 | FAIL |
| `wick_reversal` | -0.15% | -0.35 | 0.44 | 1 | 0/4 | FAIL |
| `price_cluster` | -1.54% | -0.35 | 1.02 | 34 | 0/4 | FAIL |
| `frama` | -6.72% | -0.87 | 0.96 | 83 | 0/4 | FAIL |
| `engulfing_zone` | -8.06% | -1.86 | 0.70 | 22 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.150 > 0.05 (우연 가능성) (x1), mc_p_value 0.218 > 0.05 (우연 가능성) (x1), mc_p_value 0.248 > 0.05 (우연 가능성) (x1) |
| `cmf` | mc_p_value 0.346 > 0.05 (우연 가능성) (x1), mc_p_value 0.242 > 0.05 (우연 가능성) (x1), mc_p_value 0.234 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.342 > 0.05 (우연 가능성) (x2), profit_factor 1.43 < 1.5 (x1), mc_p_value 0.384 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | mc_p_value 0.334 > 0.05 (우연 가능성) (x1), mc_p_value 0.320 > 0.05 (우연 가능성) (x1), profit_factor 1.50 < 1.5 (x1) |
| `supertrend_multi` | max_drawdown 31.6% > 20% (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.416 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -0.90 < 1.0 (x1), max_drawdown 26.5% > 20% (x1), profit_factor 0.93 < 1.5 (x1) |
| `narrow_range` | profit_factor 1.45 < 1.5 (x2), profit_factor 1.43 < 1.5 (x1), mc_p_value 0.366 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe 0.11 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1), mc_p_value 0.532 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.27 < 1.5 (x2), mc_p_value 0.280 > 0.05 (우연 가능성) (x1), mc_p_value 0.402 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -1.41 < 1.0 (x1), max_drawdown 20.1% > 20% (x1), profit_factor 0.87 < 1.5 (x1) |
| `lob_maker` | sharpe -5.06 < 1.0 (x1), max_drawdown 54.9% > 20% (x1), profit_factor 0.62 < 1.5 (x1) |
| `value_area` | mc_p_value 0.430 > 0.05 (우연 가능성) (x1), trades 13 < 15 (x1), trades 11 < 15 (x1) |
| `roc_ma_cross` | sharpe 0.56 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.490 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | mc_p_value 0.394 > 0.05 (우연 가능성) (x1), sharpe 0.68 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1) |
| `linear_channel_rev` | profit_factor 1.39 < 1.5 (x1), mc_p_value 0.462 > 0.05 (우연 가능성) (x1), profit_factor 1.48 < 1.5 (x1) |
| `relative_volume` | profit_factor 1.23 < 1.5 (x2), sharpe 0.08 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1) |
| `positional_scaling` | mc_p_value 0.374 > 0.05 (우연 가능성) (x1), profit_factor 1.48 < 1.5 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | trades 11 < 15 (x1), trades 13 < 15 (x1), sharpe 0.51 < 1.0 (x1) |
| `wick_reversal` | no trades generated (x2), sharpe -2.10 < 1.0 (x1), profit_factor 0.00 < 1.5 (x1) |
| `price_cluster` | sharpe -1.68 < 1.0 (x1), profit_factor 0.78 < 1.5 (x1), mc_p_value 0.594 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.21 < 1.5 | 3 |
| mc_p_value 0.342 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.484 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.39 < 1.5 | 3 |
| profit_factor 1.48 < 1.5 | 3 |
| mc_p_value 0.430 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.346 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.43 < 1.5 | 2 |
| mc_p_value 0.384 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.12 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +18.74% -> $11,874
- **Top 5 균등배분**: +50.13% -> $15,013
