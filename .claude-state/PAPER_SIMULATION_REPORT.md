# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-31T20:22:07.407085Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-31T20:26:01.284363Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=620682894, block=24)_
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
| 최고 수익률 | 56.58% (momentum_quality) |
| 최저 수익률 | -12.06% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +56.58% | 4.99 | 48.6% | 1.69 | 118 | 10.1% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +44.47% | 3.46 | 44.4% | 1.37 | 155 | 13.0% | 0/4 | FAIL |
| 3 | `narrow_range` | +39.46% | 4.16 | 46.8% | 1.63 | 100 | 10.3% | 0/4 | FAIL |
| 4 | `cmf` | +38.27% | 3.02 | 44.2% | 1.41 | 105 | 14.3% | 0/4 | FAIL |
| 5 | `acceleration_band` | +28.36% | 2.79 | 43.8% | 1.38 | 101 | 8.9% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | +26.77% | 2.64 | 45.1% | 1.39 | 81 | 12.7% | 0/4 | FAIL |
| 7 | `volatility_cluster` | +26.00% | 3.54 | 47.8% | 1.62 | 75 | 9.7% | 0/4 | FAIL |
| 8 | `volume_breakout` | +21.54% | 2.31 | 43.5% | 1.34 | 90 | 14.8% | 0/4 | FAIL |
| 9 | `supertrend_multi` | +14.60% | 1.65 | 41.8% | 1.29 | 83 | 14.4% | 0/4 | FAIL |
| 10 | `htf_ema` | +14.41% | 1.45 | 41.7% | 1.29 | 70 | 13.6% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `wick_reversal` | 61.1 | p100 | 0.99 | 0.99 | 500.00 | 0 | 0.0% | 0/4 | FAIL |
| 2 | `momentum_quality` | 60.2 | p95 | 4.99 | 1.28 | 1.69 | 118 | 10.1% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 58.8 | p90 | 3.46 | 0.54 | 1.37 | 155 | 13.0% | 0/4 | FAIL |
| 4 | `narrow_range` | 57.6 | p85 | 4.16 | 0.62 | 1.63 | 100 | 10.3% | 0/4 | FAIL |
| 5 | `acceleration_band` | 52.7 | p80 | 2.79 | 0.80 | 1.38 | 101 | 8.9% | 0/4 | FAIL |
| 6 | `volatility_cluster` | 52.2 | p76 | 3.54 | 0.90 | 1.62 | 75 | 9.7% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | 49.1 | p71 | 2.64 | 0.43 | 1.39 | 81 | 12.7% | 0/4 | FAIL |
| 8 | `cmf` | 47.9 | p66 | 3.02 | 1.40 | 1.41 | 105 | 14.3% | 0/4 | FAIL |
| 9 | `volume_breakout` | 45.9 | p61 | 2.31 | 0.78 | 1.34 | 90 | 14.8% | 0/4 | FAIL |
| 10 | `roc_ma_cross` | 45.6 | p57 | 2.08 | 0.83 | 1.46 | 42 | 6.7% | 0/4 | FAIL |
| 11 | `relative_volume` | 42.4 | p52 | 0.86 | 0.14 | 1.17 | 53 | 10.1% | 0/4 | FAIL |
| 12 | `dema_cross` | 41.8 | p47 | 1.67 | 1.32 | 1.89 | 11 | 2.7% | 0/4 | FAIL |
| 13 | `linear_channel_rev` | 41.7 | p42 | 0.86 | 0.39 | 1.22 | 31 | 6.4% | 0/4 | FAIL |
| 14 | `price_cluster` | 38.1 | p38 | 0.53 | 0.56 | 1.13 | 36 | 9.6% | 0/4 | FAIL |
| 15 | `frama` | 36.9 | p33 | -0.28 | 0.39 | 0.99 | 88 | 15.4% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +56.58% | 4.99 | 1.69 | 118 | 0/4 | FAIL |
| `price_action_momentum` | +44.47% | 3.46 | 1.37 | 155 | 0/4 | FAIL |
| `narrow_range` | +39.46% | 4.16 | 1.63 | 100 | 0/4 | FAIL |
| `cmf` | +38.27% | 3.02 | 1.41 | 105 | 0/4 | FAIL |
| `acceleration_band` | +28.36% | 2.79 | 1.38 | 101 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +26.77% | 2.64 | 1.39 | 81 | 0/4 | FAIL |
| `volatility_cluster` | +26.00% | 3.54 | 1.62 | 75 | 0/4 | FAIL |
| `volume_breakout` | +21.54% | 2.31 | 1.34 | 90 | 0/4 | FAIL |
| `supertrend_multi` | +14.60% | 1.65 | 1.29 | 83 | 0/4 | FAIL |
| `htf_ema` | +14.41% | 1.45 | 1.29 | 70 | 0/4 | FAIL |
| `roc_ma_cross` | +11.02% | 2.08 | 1.46 | 42 | 0/4 | FAIL |
| `elder_impulse` | +6.33% | 0.86 | 1.20 | 58 | 0/4 | FAIL |
| `dema_cross` | +4.60% | 1.67 | 1.89 | 11 | 0/4 | FAIL |
| `relative_volume` | +4.04% | 0.86 | 1.17 | 53 | 0/4 | FAIL |
| `linear_channel_rev` | +3.20% | 0.86 | 1.22 | 31 | 0/4 | FAIL |
| `price_cluster` | +2.69% | 0.53 | 1.13 | 36 | 0/4 | FAIL |
| `lob_maker` | +2.68% | 0.32 | 1.07 | 115 | 0/4 | FAIL |
| `wick_reversal` | +1.42% | 0.99 | 500.00 | 0 | 0/4 | FAIL |
| `positional_scaling` | -0.89% | -0.34 | 1.00 | 26 | 0/4 | FAIL |
| `value_area` | -3.68% | -1.23 | 0.80 | 22 | 0/4 | FAIL |
| `frama` | -3.73% | -0.28 | 0.99 | 88 | 0/4 | FAIL |
| `engulfing_zone` | -12.06% | -2.76 | 0.60 | 25 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | profit_factor 1.49 < 1.5 (x1), mc_p_value 0.286 > 0.05 (우연 가능성) (x1), mc_p_value 0.266 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | profit_factor 1.41 < 1.5 (x1), mc_p_value 0.294 > 0.05 (우연 가능성) (x1), profit_factor 1.32 < 1.5 (x1) |
| `narrow_range` | mc_p_value 0.246 > 0.05 (우연 가능성) (x1), mc_p_value 0.278 > 0.05 (우연 가능성) (x1), mc_p_value 0.342 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.400 > 0.05 (우연 가능성) (x1), mc_p_value 0.272 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.322 > 0.05 (우연 가능성) (x1), mc_p_value 0.334 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.336 > 0.05 (우연 가능성) (x1), profit_factor 1.41 < 1.5 (x1) |
| `volatility_cluster` | mc_p_value 0.374 > 0.05 (우연 가능성) (x1), mc_p_value 0.280 > 0.05 (우연 가능성) (x1), mc_p_value 0.366 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 1.15 < 1.5 (x1), mc_p_value 0.438 > 0.05 (우연 가능성) (x1), max_drawdown 20.3% > 20% (x1) |
| `supertrend_multi` | mc_p_value 0.362 > 0.05 (우연 가능성) (x1), mc_p_value 0.354 > 0.05 (우연 가능성) (x1), profit_factor 1.38 < 1.5 (x1) |
| `htf_ema` | sharpe -1.71 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1), mc_p_value 0.544 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.394 > 0.05 (우연 가능성) (x1), mc_p_value 0.442 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | profit_factor 1.41 < 1.5 (x1), mc_p_value 0.410 > 0.05 (우연 가능성) (x1), sharpe -2.13 < 1.0 (x1) |
| `dema_cross` | trades 13 < 15 (x1), trades 12 < 15 (x1), trades 9 < 15 (x1) |
| `relative_volume` | sharpe 0.93 < 1.0 (x1), profit_factor 1.17 < 1.5 (x1), mc_p_value 0.414 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | mc_p_value 0.454 > 0.05 (우연 가능성) (x2), sharpe 0.46 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1) |
| `price_cluster` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.446 > 0.05 (우연 가능성) (x1), sharpe -0.15 < 1.0 (x1) |
| `lob_maker` | sharpe -1.10 < 1.0 (x1), max_drawdown 31.1% > 20% (x1), profit_factor 0.93 < 1.5 (x1) |
| `wick_reversal` | no trades generated (x2), trades 1 < 15 (x2) |
| `positional_scaling` | sharpe -1.85 < 1.0 (x1), profit_factor 0.68 < 1.5 (x1), mc_p_value 0.540 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -0.77 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1), mc_p_value 0.530 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.41 < 1.5 | 3 |
| profit_factor 1.15 < 1.5 | 3 |
| mc_p_value 0.370 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.23 < 1.5 | 3 |
| profit_factor 1.49 < 1.5 | 2 |
| mc_p_value 0.286 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.45 < 1.5 | 2 |
| profit_factor 1.30 < 1.5 | 2 |
| mc_p_value 0.334 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.37 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +14.82% -> $11,482
- **Top 5 균등배분**: +41.43% -> $14,143


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-31T20:29:52.463687Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=1906942821, block=24)_
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
| 평균 수익률 | 13.10% |
| 최고 수익률 | 47.15% (price_action_momentum) |
| 최저 수익률 | -6.02% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +47.15% | 3.48 | 44.0% | 1.37 | 144 | 13.1% | 0/4 | FAIL |
| 2 | `momentum_quality` | +34.96% | 3.84 | 47.2% | 1.51 | 110 | 10.8% | 0/4 | FAIL |
| 3 | `acceleration_band` | +31.81% | 3.05 | 43.6% | 1.45 | 94 | 10.5% | 0/4 | FAIL |
| 4 | `supertrend_multi` | +30.49% | 2.87 | 44.5% | 1.36 | 114 | 11.8% | 0/4 | FAIL |
| 5 | `lob_maker` | +29.34% | 2.24 | 41.7% | 1.28 | 118 | 15.2% | 0/4 | FAIL |
| 6 | `volume_breakout` | +27.49% | 2.57 | 43.9% | 1.41 | 92 | 12.3% | 0/4 | FAIL |
| 7 | `cmf` | +26.52% | 2.05 | 41.5% | 1.25 | 114 | 16.5% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | +21.02% | 2.15 | 41.7% | 1.33 | 83 | 10.5% | 0/4 | FAIL |
| 9 | `volatility_cluster` | +19.19% | 2.62 | 47.2% | 1.47 | 76 | 12.4% | 0/4 | FAIL |
| 10 | `roc_ma_cross` | +15.50% | 3.27 | 51.7% | 1.98 | 32 | 5.0% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 74.5 | p100 | 3.84 | 0.52 | 1.51 | 110 | 10.8% | 0/4 | FAIL |
| 2 | `roc_ma_cross` | 72.8 | p95 | 3.27 | 0.99 | 1.98 | 32 | 5.0% | 0/4 | FAIL |
| 3 | `acceleration_band` | 67.5 | p90 | 3.05 | 0.56 | 1.45 | 94 | 10.5% | 0/4 | FAIL |
| 4 | `price_action_momentum` | 64.1 | p85 | 3.48 | 1.91 | 1.37 | 144 | 13.1% | 0/4 | FAIL |
| 5 | `order_flow_imbalance_v2` | 58.7 | p80 | 2.15 | 0.66 | 1.33 | 83 | 10.5% | 0/4 | FAIL |
| 6 | `supertrend_multi` | 58.2 | p76 | 2.87 | 1.96 | 1.36 | 114 | 11.8% | 0/4 | FAIL |
| 7 | `volatility_cluster` | 57.7 | p71 | 2.62 | 1.27 | 1.47 | 76 | 12.4% | 0/4 | FAIL |
| 8 | `volume_breakout` | 53.5 | p66 | 2.57 | 2.11 | 1.41 | 92 | 12.3% | 0/4 | FAIL |
| 9 | `lob_maker` | 52.2 | p61 | 2.24 | 1.71 | 1.28 | 118 | 15.2% | 0/4 | FAIL |
| 10 | `narrow_range` | 51.0 | p57 | 1.72 | 1.79 | 1.27 | 90 | 9.2% | 0/4 | FAIL |
| 11 | `cmf` | 49.7 | p52 | 2.05 | 1.64 | 1.25 | 114 | 16.5% | 0/4 | FAIL |
| 12 | `positional_scaling` | 44.1 | p47 | 0.84 | 1.06 | 1.28 | 26 | 8.3% | 0/4 | FAIL |
| 13 | `wick_reversal` | 43.7 | p42 | 0.39 | 0.39 | 0.91 | 1 | 0.5% | 0/4 | FAIL |
| 14 | `relative_volume` | 42.6 | p38 | 0.68 | 1.11 | 1.16 | 60 | 10.7% | 0/4 | FAIL |
| 15 | `frama` | 30.6 | p33 | -0.59 | 0.73 | 0.96 | 84 | 17.9% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +47.15% | 3.48 | 1.37 | 144 | 0/4 | FAIL |
| `momentum_quality` | +34.96% | 3.84 | 1.51 | 110 | 0/4 | FAIL |
| `acceleration_band` | +31.81% | 3.05 | 1.45 | 94 | 0/4 | FAIL |
| `supertrend_multi` | +30.49% | 2.87 | 1.36 | 114 | 0/4 | FAIL |
| `lob_maker` | +29.34% | 2.24 | 1.28 | 118 | 0/4 | FAIL |
| `volume_breakout` | +27.49% | 2.57 | 1.41 | 92 | 0/4 | FAIL |
| `cmf` | +26.52% | 2.05 | 1.25 | 114 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +21.02% | 2.15 | 1.33 | 83 | 0/4 | FAIL |
| `volatility_cluster` | +19.19% | 2.62 | 1.47 | 76 | 0/4 | FAIL |
| `roc_ma_cross` | +15.50% | 3.27 | 1.98 | 32 | 0/4 | FAIL |
| `narrow_range` | +13.75% | 1.72 | 1.27 | 90 | 0/4 | FAIL |
| `relative_volume` | +3.29% | 0.68 | 1.16 | 60 | 0/4 | FAIL |
| `positional_scaling` | +3.19% | 0.84 | 1.28 | 26 | 0/4 | FAIL |
| `engulfing_zone` | +1.71% | -0.08 | 1.06 | 26 | 0/4 | FAIL |
| `htf_ema` | +0.88% | 0.04 | 1.07 | 72 | 0/4 | FAIL |
| `wick_reversal` | +0.42% | 0.39 | 0.91 | 1 | 0/4 | FAIL |
| `elder_impulse` | -0.76% | -0.07 | 1.09 | 56 | 0/4 | FAIL |
| `price_cluster` | -1.01% | -0.25 | 0.99 | 37 | 0/4 | FAIL |
| `dema_cross` | -2.69% | -1.45 | 0.71 | 9 | 0/4 | FAIL |
| `linear_channel_rev` | -3.43% | -0.89 | 0.93 | 34 | 0/4 | FAIL |
| `value_area` | -4.58% | -1.31 | 0.79 | 27 | 0/4 | FAIL |
| `frama` | -6.02% | -0.59 | 0.96 | 84 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.194 > 0.05 (우연 가능성) (x1), profit_factor 1.46 < 1.5 (x1), mc_p_value 0.254 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.294 > 0.05 (우연 가능성) (x1), mc_p_value 0.340 > 0.05 (우연 가능성) (x1), mc_p_value 0.308 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | mc_p_value 0.322 > 0.05 (우연 가능성) (x1), profit_factor 1.42 < 1.5 (x1), mc_p_value 0.334 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | mc_p_value 0.154 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1), mc_p_value 0.424 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | mc_p_value 0.344 > 0.05 (우연 가능성) (x2), profit_factor 1.42 < 1.5 (x1), mc_p_value 0.328 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | mc_p_value 0.276 > 0.05 (우연 가능성) (x1), mc_p_value 0.318 > 0.05 (우연 가능성) (x1), profit_factor 1.24 < 1.5 (x1) |
| `cmf` | mc_p_value 0.260 > 0.05 (우연 가능성) (x1), profit_factor 1.27 < 1.5 (x1), mc_p_value 0.352 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.34 < 1.5 (x2), mc_p_value 0.376 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.418 > 0.05 (우연 가능성) (x1), profit_factor 1.49 < 1.5 (x1) |
| `roc_ma_cross` | mc_p_value 0.350 > 0.05 (우연 가능성) (x1), mc_p_value 0.362 > 0.05 (우연 가능성) (x1), mc_p_value 0.410 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | mc_p_value 0.362 > 0.05 (우연 가능성) (x1), profit_factor 1.49 < 1.5 (x1), mc_p_value 0.314 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | mc_p_value 0.404 > 0.05 (우연 가능성) (x1), sharpe -0.01 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1) |
| `positional_scaling` | sharpe 0.90 < 1.0 (x1), profit_factor 1.22 < 1.5 (x1), mc_p_value 0.472 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -2.45 < 1.0 (x1), profit_factor 0.55 < 1.5 (x1), mc_p_value 0.548 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | mc_p_value 0.356 > 0.05 (우연 가능성) (x1), sharpe -1.04 < 1.0 (x1), max_drawdown 21.4% > 20% (x1) |
| `wick_reversal` | no trades generated (x2), sharpe 0.78 < 1.0 (x2), trades 2 < 15 (x2) |
| `elder_impulse` | mc_p_value 0.352 > 0.05 (우연 가능성) (x1), sharpe -0.40 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1) |
| `price_cluster` | sharpe -1.40 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1), mc_p_value 0.514 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | trades 8 < 15 (x2), sharpe -1.75 < 1.0 (x1), profit_factor 0.58 < 1.5 (x1) |
| `linear_channel_rev` | profit_factor 1.39 < 1.5 (x1), mc_p_value 0.458 > 0.05 (우연 가능성) (x1), sharpe -0.09 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.514 > 0.05 (우연 가능성) | 4 |
| profit_factor 1.46 < 1.5 | 3 |
| mc_p_value 0.344 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.446 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.06 < 1.5 | 2 |
| profit_factor 1.42 < 1.5 | 2 |
| profit_factor 1.47 < 1.5 | 2 |
| mc_p_value 0.378 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.23 < 1.5 | 2 |
| profit_factor 1.24 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +13.10% -> $11,310
- **Top 5 균등배분**: +34.75% -> $13,475


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-31T20:33:40.739084Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=404672030, block=24)_
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
| 평균 수익률 | 13.88% |
| 최고 수익률 | 78.99% (price_action_momentum) |
| 최저 수익률 | -10.78% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +78.99% | 5.04 | 45.3% | 1.58 | 155 | 11.2% | 0/4 | FAIL |
| 2 | `momentum_quality` | +66.38% | 5.59 | 50.4% | 1.82 | 117 | 10.2% | 0/4 | FAIL |
| 3 | `acceleration_band` | +44.24% | 3.96 | 47.3% | 1.60 | 95 | 15.0% | 0/4 | FAIL |
| 4 | `cmf` | +39.37% | 3.00 | 43.0% | 1.37 | 115 | 18.7% | 0/4 | FAIL |
| 5 | `supertrend_multi` | +24.50% | 2.78 | 44.1% | 1.35 | 111 | 15.7% | 0/4 | FAIL |
| 6 | `volatility_cluster` | +22.34% | 2.90 | 44.2% | 1.48 | 81 | 9.3% | 0/4 | FAIL |
| 7 | `volume_breakout` | +22.18% | 2.30 | 43.9% | 1.36 | 89 | 13.3% | 0/4 | FAIL |
| 8 | `narrow_range` | +14.11% | 1.77 | 41.9% | 1.27 | 92 | 15.8% | 0/4 | FAIL |
| 9 | `roc_ma_cross` | +12.16% | 2.76 | 49.7% | 1.94 | 31 | 5.5% | 0/4 | FAIL |
| 10 | `htf_ema` | +10.68% | 1.35 | 41.7% | 1.22 | 68 | 12.1% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 63.1 | p100 | 5.04 | 1.26 | 1.58 | 155 | 11.2% | 0/4 | FAIL |
| 2 | `momentum_quality` | 61.5 | p95 | 5.59 | 1.64 | 1.82 | 117 | 10.2% | 0/4 | FAIL |
| 3 | `wick_reversal` | 52.2 | p90 | -0.25 | 1.84 | 250.69 | 1 | 1.0% | 0/4 | FAIL |
| 4 | `acceleration_band` | 49.5 | p85 | 3.96 | 1.52 | 1.60 | 95 | 15.0% | 0/4 | FAIL |
| 5 | `supertrend_multi` | 48.4 | p80 | 2.78 | 0.35 | 1.35 | 111 | 15.7% | 0/4 | FAIL |
| 6 | `volatility_cluster` | 47.8 | p76 | 2.90 | 1.50 | 1.48 | 81 | 9.3% | 0/4 | FAIL |
| 7 | `cmf` | 45.9 | p71 | 3.00 | 1.03 | 1.37 | 115 | 18.7% | 0/4 | FAIL |
| 8 | `roc_ma_cross` | 45.8 | p66 | 2.76 | 1.21 | 1.94 | 31 | 5.5% | 0/4 | FAIL |
| 9 | `volume_breakout` | 43.4 | p61 | 2.30 | 1.45 | 1.36 | 89 | 13.3% | 0/4 | FAIL |
| 10 | `htf_ema` | 39.9 | p57 | 1.35 | 0.83 | 1.22 | 68 | 12.1% | 0/4 | FAIL |
| 11 | `narrow_range` | 39.6 | p52 | 1.77 | 1.51 | 1.27 | 92 | 15.8% | 0/4 | FAIL |
| 12 | `lob_maker` | 37.6 | p47 | 0.85 | 0.63 | 1.11 | 119 | 19.9% | 0/4 | FAIL |
| 13 | `linear_channel_rev` | 32.0 | p42 | -0.77 | 0.34 | 0.90 | 33 | 7.7% | 0/4 | FAIL |
| 14 | `value_area` | 30.0 | p38 | -0.67 | 1.48 | 0.92 | 24 | 6.0% | 0/4 | FAIL |
| 15 | `price_cluster` | 29.7 | p33 | -0.47 | 0.27 | 0.94 | 33 | 12.9% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +78.99% | 5.04 | 1.58 | 155 | 0/4 | FAIL |
| `momentum_quality` | +66.38% | 5.59 | 1.82 | 117 | 0/4 | FAIL |
| `acceleration_band` | +44.24% | 3.96 | 1.60 | 95 | 0/4 | FAIL |
| `cmf` | +39.37% | 3.00 | 1.37 | 115 | 0/4 | FAIL |
| `supertrend_multi` | +24.50% | 2.78 | 1.35 | 111 | 0/4 | FAIL |
| `volatility_cluster` | +22.34% | 2.90 | 1.48 | 81 | 0/4 | FAIL |
| `volume_breakout` | +22.18% | 2.30 | 1.36 | 89 | 0/4 | FAIL |
| `narrow_range` | +14.11% | 1.77 | 1.27 | 92 | 0/4 | FAIL |
| `roc_ma_cross` | +12.16% | 2.76 | 1.94 | 31 | 0/4 | FAIL |
| `htf_ema` | +10.68% | 1.35 | 1.22 | 68 | 0/4 | FAIL |
| `lob_maker` | +7.81% | 0.85 | 1.11 | 119 | 0/4 | FAIL |
| `relative_volume` | +4.52% | -0.11 | 1.18 | 55 | 0/4 | FAIL |
| `wick_reversal` | +0.45% | -0.25 | 250.69 | 1 | 0/4 | FAIL |
| `engulfing_zone` | -1.62% | -0.40 | 1.02 | 21 | 0/4 | FAIL |
| `value_area` | -1.89% | -0.67 | 0.92 | 24 | 0/4 | FAIL |
| `dema_cross` | -3.09% | -1.65 | 0.63 | 10 | 0/4 | FAIL |
| `linear_channel_rev` | -3.27% | -0.77 | 0.90 | 33 | 0/4 | FAIL |
| `price_cluster` | -3.35% | -0.47 | 0.94 | 33 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | -4.51% | -0.33 | 0.99 | 83 | 0/4 | FAIL |
| `positional_scaling` | -5.49% | -1.71 | 0.78 | 28 | 0/4 | FAIL |
| `elder_impulse` | -8.37% | -1.22 | 0.87 | 57 | 0/4 | FAIL |
| `frama` | -10.78% | -1.25 | 0.90 | 90 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.142 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1), mc_p_value 0.276 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.136 > 0.05 (우연 가능성) (x1), mc_p_value 0.168 > 0.05 (우연 가능성) (x1), mc_p_value 0.246 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.354 > 0.05 (우연 가능성) (x1), mc_p_value 0.250 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.23 < 1.5 (x1), mc_p_value 0.402 > 0.05 (우연 가능성) (x1), mc_p_value 0.270 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | profit_factor 1.44 < 1.5 (x1), mc_p_value 0.308 > 0.05 (우연 가능성) (x1), profit_factor 1.28 < 1.5 (x1) |
| `volatility_cluster` | mc_p_value 0.306 > 0.05 (우연 가능성) (x1), mc_p_value 0.310 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1) |
| `volume_breakout` | sharpe 0.81 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1), mc_p_value 0.456 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.436 > 0.05 (우연 가능성) (x1), mc_p_value 0.360 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.452 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1) |
| `htf_ema` | sharpe 0.44 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1), mc_p_value 0.446 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | sharpe 0.29 < 1.0 (x1), max_drawdown 21.0% > 20% (x1), profit_factor 1.05 < 1.5 (x1) |
| `relative_volume` | sharpe -6.70 < 1.0 (x1), max_drawdown 27.4% > 20% (x1), profit_factor 0.39 < 1.5 (x1) |
| `wick_reversal` | trades 1 < 15 (x3), profit_factor 0.00 < 1.5 (x2), sharpe -2.11 < 1.0 (x1) |
| `engulfing_zone` | mc_p_value 0.466 > 0.05 (우연 가능성) (x1), sharpe -0.20 < 1.0 (x1), profit_factor 0.97 < 1.5 (x1) |
| `value_area` | mc_p_value 0.462 > 0.05 (우연 가능성) (x2), sharpe -2.60 < 1.0 (x1), profit_factor 0.57 < 1.5 (x1) |
| `dema_cross` | trades 11 < 15 (x2), trades 9 < 15 (x2), sharpe 0.14 < 1.0 (x1) |
| `linear_channel_rev` | profit_factor 0.84 < 1.5 (x2), profit_factor 0.95 < 1.5 (x2), sharpe -1.15 < 1.0 (x1) |
| `price_cluster` | sharpe -0.39 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1), mc_p_value 0.504 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe -0.88 < 1.0 (x1), max_drawdown 24.1% > 20% (x1), profit_factor 0.93 < 1.5 (x1) |
| `positional_scaling` | sharpe -2.86 < 1.0 (x1), profit_factor 0.57 < 1.5 (x1), mc_p_value 0.546 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.11 < 1.5 | 4 |
| mc_p_value 0.376 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.392 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.462 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.97 < 1.5 | 3 |
| trades 1 < 15 | 3 |
| profit_factor 0.95 < 1.5 | 3 |
| profit_factor 1.38 < 1.5 | 2 |
| mc_p_value 0.248 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.28 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +13.88% -> $11,388
- **Top 5 균등배분**: +50.70% -> $15,070
