# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-29T15:23:38.009900Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-29T15:26:20.896258Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1646846145, block=24)_
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
| 평균 수익률 | 16.38% |
| 최고 수익률 | 57.56% (lob_maker) |
| 최저 수익률 | -5.71% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `lob_maker` | +57.56% | 3.86 | 46.6% | 1.50 | 120 | 16.2% | 0/4 | FAIL |
| 2 | `order_flow_imbalance_v2` | +47.19% | 3.85 | 48.7% | 1.63 | 82 | 14.1% | 0/4 | FAIL |
| 3 | `price_action_momentum` | +40.99% | 3.25 | 43.2% | 1.35 | 156 | 14.4% | 0/4 | FAIL |
| 4 | `volume_breakout` | +40.80% | 3.69 | 47.7% | 1.58 | 92 | 11.2% | 0/4 | FAIL |
| 5 | `acceleration_band` | +34.07% | 3.25 | 45.5% | 1.47 | 97 | 14.2% | 0/4 | FAIL |
| 6 | `cmf` | +27.85% | 2.22 | 42.9% | 1.28 | 120 | 20.6% | 0/4 | FAIL |
| 7 | `supertrend_multi` | +25.89% | 2.72 | 42.8% | 1.34 | 120 | 14.6% | 0/4 | FAIL |
| 8 | `momentum_quality` | +20.04% | 2.25 | 42.4% | 1.30 | 116 | 12.3% | 0/4 | FAIL |
| 9 | `relative_volume` | +18.79% | 2.98 | 47.1% | 1.59 | 55 | 9.3% | 0/4 | FAIL |
| 10 | `narrow_range` | +15.07% | 1.71 | 41.3% | 1.28 | 94 | 15.3% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `volume_breakout` | 75.7 | p100 | 3.69 | 1.58 | 1.58 | 92 | 11.2% | 0/4 | FAIL |
| 2 | `order_flow_imbalance_v2` | 74.7 | p95 | 3.85 | 1.51 | 1.63 | 82 | 14.1% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 74.5 | p90 | 3.25 | 0.61 | 1.35 | 156 | 14.4% | 0/4 | FAIL |
| 4 | `lob_maker` | 74.3 | p85 | 3.86 | 1.32 | 1.50 | 120 | 16.2% | 0/4 | FAIL |
| 5 | `relative_volume` | 72.9 | p80 | 2.98 | 0.51 | 1.59 | 55 | 9.3% | 0/4 | FAIL |
| 6 | `acceleration_band` | 70.6 | p76 | 3.25 | 0.92 | 1.47 | 97 | 14.2% | 0/4 | FAIL |
| 7 | `supertrend_multi` | 67.5 | p71 | 2.72 | 0.61 | 1.34 | 120 | 14.6% | 0/4 | FAIL |
| 8 | `momentum_quality` | 63.6 | p66 | 2.25 | 1.15 | 1.30 | 116 | 12.3% | 0/4 | FAIL |
| 9 | `volatility_cluster` | 63.5 | p61 | 1.94 | 0.40 | 1.29 | 85 | 9.1% | 0/4 | FAIL |
| 10 | `linear_channel_rev` | 57.8 | p57 | 1.42 | 1.64 | 1.50 | 24 | 6.6% | 0/4 | FAIL |
| 11 | `dema_cross` | 57.3 | p52 | 1.00 | 0.92 | 1.44 | 14 | 3.8% | 0/4 | FAIL |
| 12 | `cmf` | 56.0 | p47 | 2.22 | 1.46 | 1.28 | 120 | 20.6% | 0/4 | FAIL |
| 13 | `narrow_range` | 52.3 | p42 | 1.71 | 2.34 | 1.28 | 94 | 15.3% | 0/4 | FAIL |
| 14 | `htf_ema` | 47.6 | p38 | 1.01 | 1.37 | 1.19 | 65 | 13.7% | 0/4 | FAIL |
| 15 | `roc_ma_cross` | 44.0 | p33 | 0.59 | 2.00 | 1.18 | 45 | 9.9% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `lob_maker` | +57.56% | 3.86 | 1.50 | 120 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +47.19% | 3.85 | 1.63 | 82 | 0/4 | FAIL |
| `price_action_momentum` | +40.99% | 3.25 | 1.35 | 156 | 0/4 | FAIL |
| `volume_breakout` | +40.80% | 3.69 | 1.58 | 92 | 0/4 | FAIL |
| `acceleration_band` | +34.07% | 3.25 | 1.47 | 97 | 0/4 | FAIL |
| `cmf` | +27.85% | 2.22 | 1.28 | 120 | 0/4 | FAIL |
| `supertrend_multi` | +25.89% | 2.72 | 1.34 | 120 | 0/4 | FAIL |
| `momentum_quality` | +20.04% | 2.25 | 1.30 | 116 | 0/4 | FAIL |
| `relative_volume` | +18.79% | 2.98 | 1.59 | 55 | 0/4 | FAIL |
| `narrow_range` | +15.07% | 1.71 | 1.28 | 94 | 0/4 | FAIL |
| `volatility_cluster` | +14.30% | 1.94 | 1.29 | 85 | 0/4 | FAIL |
| `htf_ema` | +7.85% | 1.01 | 1.19 | 65 | 0/4 | FAIL |
| `linear_channel_rev` | +5.61% | 1.42 | 1.50 | 24 | 0/4 | FAIL |
| `frama` | +5.21% | 0.62 | 1.12 | 79 | 0/4 | FAIL |
| `roc_ma_cross` | +3.59% | 0.59 | 1.18 | 45 | 0/4 | FAIL |
| `dema_cross` | +2.50% | 1.00 | 1.44 | 14 | 0/4 | FAIL |
| `positional_scaling` | +2.21% | -0.20 | 1.30 | 24 | 0/4 | FAIL |
| `elder_impulse` | -0.09% | 0.12 | 1.05 | 58 | 0/4 | FAIL |
| `wick_reversal` | -0.14% | -0.08 | 0.76 | 2 | 0/4 | FAIL |
| `price_cluster` | -0.19% | 0.03 | 1.04 | 38 | 0/4 | FAIL |
| `value_area` | -3.08% | -1.31 | 0.77 | 16 | 0/4 | FAIL |
| `engulfing_zone` | -5.71% | -1.38 | 0.78 | 22 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `lob_maker` | mc_p_value 0.248 > 0.05 (우연 가능성) (x1), mc_p_value 0.288 > 0.05 (우연 가능성) (x1), mc_p_value 0.320 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.298 > 0.05 (우연 가능성) (x1), mc_p_value 0.338 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1) |
| `price_action_momentum` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.304 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1) |
| `volume_breakout` | mc_p_value 0.260 > 0.05 (우연 가능성) (x1), mc_p_value 0.326 > 0.05 (우연 가능성) (x1), profit_factor 1.38 < 1.5 (x1) |
| `acceleration_band` | mc_p_value 0.346 > 0.05 (우연 가능성) (x1), mc_p_value 0.348 > 0.05 (우연 가능성) (x1), profit_factor 1.37 < 1.5 (x1) |
| `cmf` | max_drawdown 23.8% > 20% (x2), profit_factor 1.29 < 1.5 (x1), mc_p_value 0.410 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | profit_factor 1.23 < 1.5 (x1), mc_p_value 0.410 > 0.05 (우연 가능성) (x1), profit_factor 1.41 < 1.5 (x1) |
| `momentum_quality` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.370 > 0.05 (우연 가능성) (x1), sharpe 0.83 < 1.0 (x1) |
| `relative_volume` | profit_factor 1.47 < 1.5 (x1), mc_p_value 0.438 > 0.05 (우연 가능성) (x1), mc_p_value 0.376 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | sharpe 0.49 < 1.0 (x1), profit_factor 1.09 < 1.5 (x1), mc_p_value 0.504 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.396 > 0.05 (우연 가능성) (x1), profit_factor 1.20 < 1.5 (x1) |
| `htf_ema` | sharpe -1.22 < 1.0 (x1), max_drawdown 20.3% > 20% (x1), profit_factor 0.88 < 1.5 (x1) |
| `linear_channel_rev` | mc_p_value 0.444 > 0.05 (우연 가능성) (x2), sharpe -0.98 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1) |
| `frama` | sharpe -1.78 < 1.0 (x1), max_drawdown 23.4% > 20% (x1), profit_factor 0.82 < 1.5 (x1) |
| `roc_ma_cross` | sharpe -2.75 < 1.0 (x1), max_drawdown 20.2% > 20% (x1), profit_factor 0.64 < 1.5 (x1) |
| `dema_cross` | trades 13 < 15 (x2), trades 12 < 15 (x1), profit_factor 1.41 < 1.5 (x1) |
| `positional_scaling` | sharpe -5.87 < 1.0 (x1), max_drawdown 20.7% > 20% (x1), profit_factor 0.26 < 1.5 (x1) |
| `elder_impulse` | sharpe 0.80 < 1.0 (x1), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | profit_factor 1.21 < 1.5 (x2), sharpe -0.87 < 1.0 (x1), profit_factor 0.61 < 1.5 (x1) |
| `price_cluster` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.454 > 0.05 (우연 가능성) (x1), sharpe 0.31 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.438 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.20 < 1.5 | 3 |
| profit_factor 1.41 < 1.5 | 3 |
| profit_factor 1.21 < 1.5 | 3 |
| trades 13 < 15 | 3 |
| mc_p_value 0.446 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.45 < 1.5 | 2 |
| profit_factor 1.27 < 1.5 | 2 |
| profit_factor 1.37 < 1.5 | 2 |
| mc_p_value 0.304 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +16.38% -> $11,638
- **Top 5 균등배분**: +44.12% -> $14,412


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-29T15:29:03.596672Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=887494860, block=24)_
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
| 평균 수익률 | 10.04% |
| 최고 수익률 | 39.45% (momentum_quality) |
| 최저 수익률 | -11.61% (htf_ema) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +39.45% | 3.87 | 46.0% | 1.56 | 108 | 10.6% | 0/4 | FAIL |
| 2 | `order_flow_imbalance_v2` | +38.09% | 3.29 | 46.1% | 1.52 | 81 | 13.4% | 0/4 | FAIL |
| 3 | `price_action_momentum` | +37.28% | 2.91 | 43.0% | 1.34 | 150 | 15.9% | 0/4 | FAIL |
| 4 | `acceleration_band` | +21.44% | 2.09 | 42.3% | 1.32 | 102 | 12.6% | 0/4 | FAIL |
| 5 | `narrow_range` | +19.38% | 2.23 | 43.9% | 1.36 | 99 | 11.6% | 0/4 | FAIL |
| 6 | `lob_maker` | +18.44% | 1.67 | 41.4% | 1.21 | 115 | 18.0% | 0/4 | FAIL |
| 7 | `volume_breakout` | +17.94% | 2.01 | 42.6% | 1.29 | 91 | 14.2% | 0/4 | FAIL |
| 8 | `relative_volume` | +16.72% | 2.60 | 45.6% | 1.48 | 61 | 7.1% | 0/4 | FAIL |
| 9 | `supertrend_multi` | +16.44% | 1.74 | 40.8% | 1.23 | 144 | 16.2% | 0/4 | FAIL |
| 10 | `cmf` | +15.95% | 0.95 | 38.9% | 1.15 | 125 | 23.6% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 80.5 | p100 | 3.87 | 1.30 | 1.56 | 108 | 10.6% | 0/4 | FAIL |
| 2 | `order_flow_imbalance_v2` | 72.7 | p90 | 3.29 | 1.30 | 1.52 | 81 | 13.4% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 72.7 | p95 | 2.91 | 1.57 | 1.34 | 150 | 15.9% | 0/4 | FAIL |
| 4 | `relative_volume` | 71.4 | p85 | 2.60 | 0.97 | 1.48 | 61 | 7.1% | 0/4 | FAIL |
| 5 | `volatility_cluster` | 68.8 | p80 | 2.22 | 1.01 | 1.36 | 80 | 8.5% | 0/4 | FAIL |
| 6 | `volume_breakout` | 68.1 | p76 | 2.01 | 0.18 | 1.29 | 91 | 14.2% | 0/4 | FAIL |
| 7 | `narrow_range` | 65.8 | p71 | 2.23 | 1.80 | 1.36 | 99 | 11.6% | 0/4 | FAIL |
| 8 | `acceleration_band` | 65.0 | p66 | 2.09 | 1.65 | 1.32 | 102 | 12.6% | 0/4 | FAIL |
| 9 | `lob_maker` | 63.2 | p61 | 1.67 | 0.77 | 1.21 | 115 | 18.0% | 0/4 | FAIL |
| 10 | `supertrend_multi` | 62.9 | p57 | 1.74 | 1.95 | 1.23 | 144 | 16.2% | 0/4 | FAIL |
| 11 | `roc_ma_cross` | 60.9 | p52 | 1.41 | 0.68 | 1.33 | 37 | 9.1% | 0/4 | FAIL |
| 12 | `elder_impulse` | 51.5 | p47 | 0.30 | 1.04 | 1.09 | 63 | 12.2% | 0/4 | FAIL |
| 13 | `cmf` | 49.2 | p42 | 0.95 | 2.51 | 1.15 | 125 | 23.6% | 0/4 | FAIL |
| 14 | `engulfing_zone` | 46.5 | p38 | -0.25 | 0.89 | 1.00 | 21 | 7.7% | 0/4 | FAIL |
| 15 | `positional_scaling` | 46.2 | p33 | -0.25 | 0.94 | 1.00 | 28 | 9.2% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +39.45% | 3.87 | 1.56 | 108 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +38.09% | 3.29 | 1.52 | 81 | 0/4 | FAIL |
| `price_action_momentum` | +37.28% | 2.91 | 1.34 | 150 | 0/4 | FAIL |
| `acceleration_band` | +21.44% | 2.09 | 1.32 | 102 | 0/4 | FAIL |
| `narrow_range` | +19.38% | 2.23 | 1.36 | 99 | 0/4 | FAIL |
| `lob_maker` | +18.44% | 1.67 | 1.21 | 115 | 0/4 | FAIL |
| `volume_breakout` | +17.94% | 2.01 | 1.29 | 91 | 0/4 | FAIL |
| `relative_volume` | +16.72% | 2.60 | 1.48 | 61 | 0/4 | FAIL |
| `supertrend_multi` | +16.44% | 1.74 | 1.23 | 144 | 0/4 | FAIL |
| `cmf` | +15.95% | 0.95 | 1.15 | 125 | 0/4 | FAIL |
| `volatility_cluster` | +15.76% | 2.22 | 1.36 | 80 | 0/4 | FAIL |
| `roc_ma_cross` | +6.44% | 1.41 | 1.33 | 37 | 0/4 | FAIL |
| `elder_impulse` | +1.39% | 0.30 | 1.09 | 63 | 0/4 | FAIL |
| `wick_reversal` | -1.14% | -1.80 | 0.00 | 1 | 0/4 | FAIL |
| `positional_scaling` | -1.26% | -0.25 | 1.00 | 28 | 0/4 | FAIL |
| `engulfing_zone` | -1.53% | -0.25 | 1.00 | 21 | 0/4 | FAIL |
| `frama` | -2.89% | -0.37 | 1.00 | 82 | 0/4 | FAIL |
| `dema_cross` | -3.30% | -1.46 | 0.64 | 12 | 0/4 | FAIL |
| `linear_channel_rev` | -5.25% | -1.19 | 0.85 | 39 | 0/4 | FAIL |
| `value_area` | -5.51% | -1.93 | 0.68 | 20 | 0/4 | FAIL |
| `price_cluster` | -11.34% | -1.78 | 0.78 | 40 | 0/4 | FAIL |
| `htf_ema` | -11.61% | -1.74 | 0.88 | 73 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | mc_p_value 0.356 > 0.05 (우연 가능성) (x1), profit_factor 1.31 < 1.5 (x1), mc_p_value 0.382 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.41 < 1.5 (x1), mc_p_value 0.390 > 0.05 (우연 가능성) (x1), mc_p_value 0.286 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | mc_p_value 0.294 > 0.05 (우연 가능성) (x1), profit_factor 1.18 < 1.5 (x1), mc_p_value 0.418 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | mc_p_value 0.336 > 0.05 (우연 가능성) (x1), profit_factor 1.19 < 1.5 (x1), mc_p_value 0.470 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | sharpe -0.73 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1), mc_p_value 0.494 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | max_drawdown 24.0% > 20% (x2), profit_factor 1.32 < 1.5 (x1), mc_p_value 0.404 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | max_drawdown 20.5% > 20% (x2), profit_factor 1.31 < 1.5 (x2), profit_factor 1.29 < 1.5 (x1) |
| `relative_volume` | profit_factor 1.42 < 1.5 (x1), mc_p_value 0.388 > 0.05 (우연 가능성) (x1), mc_p_value 0.390 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | mc_p_value 0.316 > 0.05 (우연 가능성) (x1), profit_factor 1.40 < 1.5 (x1), mc_p_value 0.388 > 0.05 (우연 가능성) (x1) |
| `cmf` | max_drawdown 24.3% > 20% (x1), profit_factor 1.18 < 1.5 (x1), mc_p_value 0.466 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.39 < 1.5 (x1), mc_p_value 0.394 > 0.05 (우연 가능성) (x1), sharpe 0.98 < 1.0 (x1) |
| `roc_ma_cross` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.410 > 0.05 (우연 가능성) (x1), profit_factor 1.28 < 1.5 (x1) |
| `elder_impulse` | profit_factor 1.18 < 1.5 (x1), mc_p_value 0.486 > 0.05 (우연 가능성) (x1), sharpe -1.17 < 1.0 (x1) |
| `wick_reversal` | profit_factor 0.00 < 1.5 (x3), trades 1 < 15 (x2), sharpe -2.10 < 1.0 (x1) |
| `positional_scaling` | sharpe -1.86 < 1.0 (x1), profit_factor 0.73 < 1.5 (x1), mc_p_value 0.568 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -0.67 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.538 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe -3.01 < 1.0 (x1), max_drawdown 24.9% > 20% (x1), profit_factor 0.73 < 1.5 (x1) |
| `dema_cross` | sharpe -1.38 < 1.0 (x1), profit_factor 0.70 < 1.5 (x1), trades 14 < 15 (x1) |
| `linear_channel_rev` | sharpe -0.42 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1), mc_p_value 0.492 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -0.42 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1), mc_p_value 0.496 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.31 < 1.5 | 3 |
| profit_factor 1.18 < 1.5 | 3 |
| mc_p_value 0.470 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.388 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.00 < 1.5 | 3 |
| mc_p_value 0.356 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.382 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.380 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.390 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.26 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +10.04% -> $11,004
- **Top 5 균등배분**: +31.13% -> $13,113
