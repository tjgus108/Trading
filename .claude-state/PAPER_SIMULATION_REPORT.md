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


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-28T20:23:20.514274Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=1055432098, block=36)_
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
| 평균 수익률 | 14.52% |
| 최고 수익률 | 44.56% (cmf) |
| 최저 수익률 | -5.48% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `cmf` | +44.56% | 3.29 | 46.2% | 1.43 | 115 | 12.3% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +42.82% | 3.25 | 42.3% | 1.37 | 162 | 16.4% | 0/4 | FAIL |
| 3 | `momentum_quality` | +35.03% | 3.75 | 46.2% | 1.50 | 112 | 8.2% | 0/4 | FAIL |
| 4 | `lob_maker` | +34.53% | 2.42 | 43.3% | 1.30 | 122 | 17.2% | 0/4 | FAIL |
| 5 | `volume_breakout` | +32.93% | 3.11 | 44.1% | 1.47 | 88 | 11.7% | 0/4 | FAIL |
| 6 | `acceleration_band` | +31.69% | 3.03 | 46.3% | 1.47 | 98 | 9.5% | 0/4 | FAIL |
| 7 | `frama` | +18.76% | 1.97 | 40.9% | 1.32 | 79 | 12.1% | 0/4 | FAIL |
| 8 | `supertrend_multi` | +15.88% | 1.76 | 40.2% | 1.21 | 128 | 10.3% | 0/4 | FAIL |
| 9 | `roc_ma_cross` | +14.08% | 3.05 | 51.0% | 1.93 | 33 | 5.3% | 0/4 | FAIL |
| 10 | `htf_ema` | +13.89% | 1.68 | 43.9% | 1.27 | 76 | 9.2% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 78.4 | p100 | 3.75 | 0.60 | 1.50 | 112 | 8.2% | 0/4 | FAIL |
| 2 | `roc_ma_cross` | 72.4 | p95 | 3.05 | 1.06 | 1.93 | 33 | 5.3% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 70.1 | p90 | 3.25 | 0.86 | 1.37 | 162 | 16.4% | 0/4 | FAIL |
| 4 | `cmf` | 67.9 | p85 | 3.29 | 1.45 | 1.43 | 115 | 12.3% | 0/4 | FAIL |
| 5 | `acceleration_band` | 66.4 | p80 | 3.03 | 1.83 | 1.47 | 98 | 9.5% | 0/4 | FAIL |
| 6 | `volume_breakout` | 66.0 | p76 | 3.11 | 1.30 | 1.47 | 88 | 11.7% | 0/4 | FAIL |
| 7 | `supertrend_multi` | 63.3 | p71 | 1.76 | 0.68 | 1.21 | 128 | 10.3% | 0/4 | FAIL |
| 8 | `htf_ema` | 58.9 | p66 | 1.68 | 0.87 | 1.27 | 76 | 9.2% | 0/4 | FAIL |
| 9 | `volatility_cluster` | 57.7 | p61 | 1.20 | 0.76 | 1.21 | 78 | 7.6% | 0/4 | FAIL |
| 10 | `lob_maker` | 56.5 | p57 | 2.42 | 1.75 | 1.30 | 122 | 17.2% | 0/4 | FAIL |
| 11 | `frama` | 56.3 | p52 | 1.97 | 1.45 | 1.32 | 79 | 12.1% | 0/4 | FAIL |
| 12 | `elder_impulse` | 55.9 | p47 | 1.37 | 0.93 | 1.28 | 56 | 8.5% | 0/4 | FAIL |
| 13 | `order_flow_imbalance_v2` | 54.1 | p42 | 1.39 | 0.86 | 1.22 | 81 | 12.5% | 0/4 | FAIL |
| 14 | `positional_scaling` | 49.7 | p38 | 1.02 | 1.74 | 1.31 | 28 | 6.9% | 0/4 | FAIL |
| 15 | `relative_volume` | 47.6 | p33 | 1.38 | 2.78 | 1.35 | 58 | 10.1% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `cmf` | +44.56% | 3.29 | 1.43 | 115 | 0/4 | FAIL |
| `price_action_momentum` | +42.82% | 3.25 | 1.37 | 162 | 0/4 | FAIL |
| `momentum_quality` | +35.03% | 3.75 | 1.50 | 112 | 0/4 | FAIL |
| `lob_maker` | +34.53% | 2.42 | 1.30 | 122 | 0/4 | FAIL |
| `volume_breakout` | +32.93% | 3.11 | 1.47 | 88 | 0/4 | FAIL |
| `acceleration_band` | +31.69% | 3.03 | 1.47 | 98 | 0/4 | FAIL |
| `frama` | +18.76% | 1.97 | 1.32 | 79 | 0/4 | FAIL |
| `supertrend_multi` | +15.88% | 1.76 | 1.21 | 128 | 0/4 | FAIL |
| `roc_ma_cross` | +14.08% | 3.05 | 1.93 | 33 | 0/4 | FAIL |
| `htf_ema` | +13.89% | 1.68 | 1.27 | 76 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +12.17% | 1.39 | 1.22 | 81 | 0/4 | FAIL |
| `relative_volume` | +11.23% | 1.38 | 1.35 | 58 | 0/4 | FAIL |
| `elder_impulse` | +8.47% | 1.37 | 1.28 | 56 | 0/4 | FAIL |
| `volatility_cluster` | +7.30% | 1.20 | 1.21 | 78 | 0/4 | FAIL |
| `positional_scaling` | +5.58% | 1.02 | 1.31 | 28 | 0/4 | FAIL |
| `linear_channel_rev` | +3.44% | 0.72 | 1.31 | 29 | 0/4 | FAIL |
| `dema_cross` | +0.38% | 0.17 | 1.12 | 12 | 0/4 | FAIL |
| `value_area` | -1.19% | -0.41 | 0.94 | 16 | 0/4 | FAIL |
| `wick_reversal` | -1.21% | -1.55 | 0.00 | 1 | 0/4 | FAIL |
| `narrow_range` | -2.22% | -0.27 | 1.02 | 92 | 0/4 | FAIL |
| `price_cluster` | -3.17% | -0.58 | 1.01 | 41 | 0/4 | FAIL |
| `engulfing_zone` | -5.48% | -1.34 | 0.87 | 25 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `cmf` | profit_factor 1.20 < 1.5 (x1), mc_p_value 0.432 > 0.05 (우연 가능성) (x1), profit_factor 1.30 < 1.5 (x1) |
| `price_action_momentum` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.352 > 0.05 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1) |
| `momentum_quality` | mc_p_value 0.338 > 0.05 (우연 가능성) (x1), profit_factor 1.48 < 1.5 (x1), mc_p_value 0.308 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.14 < 1.5 (x1), mc_p_value 0.442 > 0.05 (우연 가능성) (x1), mc_p_value 0.276 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 1.23 < 1.5 (x1), mc_p_value 0.422 > 0.05 (우연 가능성) (x1), mc_p_value 0.336 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | sharpe 0.04 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1), mc_p_value 0.520 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe 0.90 < 1.0 (x1), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.486 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | profit_factor 1.19 < 1.5 (x1), mc_p_value 0.454 > 0.05 (우연 가능성) (x1), sharpe 0.97 < 1.0 (x1) |
| `roc_ma_cross` | mc_p_value 0.416 > 0.05 (우연 가능성) (x2), profit_factor 1.33 < 1.5 (x1), mc_p_value 0.478 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | sharpe 0.71 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.478 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe -0.09 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.482 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | mc_p_value 0.376 > 0.05 (우연 가능성) (x2), sharpe -2.12 < 1.0 (x1), profit_factor 0.76 < 1.5 (x1) |
| `elder_impulse` | sharpe 0.57 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), mc_p_value 0.456 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe 0.39 < 1.0 (x1), profit_factor 1.09 < 1.5 (x1), mc_p_value 0.492 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | mc_p_value 0.406 > 0.05 (우연 가능성) (x1), profit_factor 1.31 < 1.5 (x1), mc_p_value 0.414 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -2.49 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1), mc_p_value 0.576 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | trades 12 < 15 (x2), sharpe -1.62 < 1.0 (x1), profit_factor 0.62 < 1.5 (x1) |
| `value_area` | sharpe 0.02 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1), mc_p_value 0.502 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | profit_factor 0.00 < 1.5 (x3), trades 1 < 15 (x3), sharpe -2.07 < 1.0 (x2) |
| `narrow_range` | sharpe -0.86 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1), mc_p_value 0.572 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.478 > 0.05 (우연 가능성) | 4 |
| mc_p_value 0.412 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.27 < 1.5 | 3 |
| mc_p_value 0.462 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.07 < 1.5 | 3 |
| mc_p_value 0.416 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.502 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.00 < 1.5 | 3 |
| trades 1 < 15 | 3 |
| profit_factor 1.20 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +14.52% -> $11,452
- **Top 5 균등배분**: +37.97% -> $13,797


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-28T20:27:09.349911Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=311118968, block=36)_
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
| 평균 수익률 | 27.01% |
| 최고 수익률 | 129.16% (price_action_momentum) |
| 최저 수익률 | -12.39% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +129.16% | 6.44 | 50.3% | 1.83 | 157 | 12.0% | 0/4 | FAIL |
| 2 | `supertrend_multi` | +117.42% | 7.23 | 51.6% | 1.98 | 148 | 7.9% | 0/4 | FAIL |
| 3 | `momentum_quality` | +112.26% | 6.96 | 52.9% | 2.04 | 127 | 7.5% | 0/4 | FAIL |
| 4 | `cmf` | +45.44% | 3.53 | 46.0% | 1.47 | 108 | 14.5% | 0/4 | FAIL |
| 5 | `acceleration_band` | +44.87% | 4.04 | 47.7% | 1.60 | 94 | 9.1% | 0/4 | FAIL |
| 6 | `narrow_range` | +42.05% | 4.49 | 51.9% | 1.89 | 84 | 10.5% | 0/4 | FAIL |
| 7 | `volume_breakout` | +30.51% | 3.02 | 44.5% | 1.48 | 86 | 9.8% | 0/4 | FAIL |
| 8 | `htf_ema` | +29.13% | 3.21 | 46.8% | 1.55 | 70 | 11.5% | 0/4 | FAIL |
| 9 | `roc_ma_cross` | +18.31% | 3.16 | 53.1% | 2.64 | 36 | 8.1% | 0/4 | FAIL |
| 10 | `volatility_cluster` | +17.57% | 2.43 | 43.9% | 1.40 | 78 | 9.9% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 79.9 | p100 | 7.23 | 1.87 | 1.98 | 148 | 7.9% | 0/4 | FAIL |
| 2 | `momentum_quality` | 75.1 | p95 | 6.96 | 2.73 | 2.04 | 127 | 7.5% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 69.5 | p90 | 6.44 | 3.31 | 1.83 | 157 | 12.0% | 0/4 | FAIL |
| 4 | `acceleration_band` | 65.7 | p85 | 4.04 | 0.62 | 1.60 | 94 | 9.1% | 0/4 | FAIL |
| 5 | `narrow_range` | 60.7 | p80 | 4.49 | 2.63 | 1.89 | 84 | 10.5% | 0/4 | FAIL |
| 6 | `cmf` | 60.6 | p76 | 3.53 | 0.50 | 1.47 | 108 | 14.5% | 0/4 | FAIL |
| 7 | `volume_breakout` | 58.2 | p71 | 3.02 | 1.38 | 1.48 | 86 | 9.8% | 0/4 | FAIL |
| 8 | `htf_ema` | 57.9 | p66 | 3.21 | 0.89 | 1.55 | 70 | 11.5% | 0/4 | FAIL |
| 9 | `roc_ma_cross` | 56.8 | p61 | 3.16 | 3.69 | 2.64 | 36 | 8.1% | 0/4 | FAIL |
| 10 | `volatility_cluster` | 55.5 | p57 | 2.43 | 1.27 | 1.40 | 78 | 9.9% | 0/4 | FAIL |
| 11 | `lob_maker` | 53.2 | p52 | 1.54 | 0.80 | 1.20 | 114 | 13.6% | 0/4 | FAIL |
| 12 | `positional_scaling` | 52.7 | p47 | 1.49 | 0.94 | 1.49 | 23 | 5.5% | 0/4 | FAIL |
| 13 | `order_flow_imbalance_v2` | 47.5 | p42 | 1.10 | 0.90 | 1.18 | 76 | 14.2% | 0/4 | FAIL |
| 14 | `elder_impulse` | 46.6 | p38 | 0.56 | 0.83 | 1.12 | 58 | 11.0% | 0/4 | FAIL |
| 15 | `relative_volume` | 45.2 | p33 | 0.01 | 0.59 | 1.04 | 56 | 10.6% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +129.16% | 6.44 | 1.83 | 157 | 0/4 | FAIL |
| `supertrend_multi` | +117.42% | 7.23 | 1.98 | 148 | 0/4 | FAIL |
| `momentum_quality` | +112.26% | 6.96 | 2.04 | 127 | 0/4 | FAIL |
| `cmf` | +45.44% | 3.53 | 1.47 | 108 | 0/4 | FAIL |
| `acceleration_band` | +44.87% | 4.04 | 1.60 | 94 | 0/4 | FAIL |
| `narrow_range` | +42.05% | 4.49 | 1.89 | 84 | 0/4 | FAIL |
| `volume_breakout` | +30.51% | 3.02 | 1.48 | 86 | 0/4 | FAIL |
| `htf_ema` | +29.13% | 3.21 | 1.55 | 70 | 0/4 | FAIL |
| `roc_ma_cross` | +18.31% | 3.16 | 2.64 | 36 | 0/4 | FAIL |
| `volatility_cluster` | +17.57% | 2.43 | 1.40 | 78 | 0/4 | FAIL |
| `lob_maker` | +17.20% | 1.54 | 1.20 | 114 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +9.33% | 1.10 | 1.18 | 76 | 0/4 | FAIL |
| `positional_scaling` | +5.53% | 1.49 | 1.49 | 23 | 0/4 | FAIL |
| `elder_impulse` | +3.22% | 0.56 | 1.12 | 58 | 0/4 | FAIL |
| `value_area` | +1.54% | 0.36 | 1.40 | 16 | 0/4 | FAIL |
| `relative_volume` | -0.50% | 0.01 | 1.04 | 56 | 0/4 | FAIL |
| `linear_channel_rev` | -0.57% | -0.11 | 1.05 | 37 | 0/4 | FAIL |
| `wick_reversal` | -1.73% | -1.49 | 0.00 | 1 | 0/4 | FAIL |
| `price_cluster` | -2.48% | -0.42 | 1.00 | 38 | 0/4 | FAIL |
| `dema_cross` | -3.69% | -1.62 | 0.65 | 12 | 0/4 | FAIL |
| `frama` | -8.05% | -0.92 | 0.94 | 86 | 0/4 | FAIL |
| `engulfing_zone` | -12.39% | -3.38 | 0.48 | 19 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | profit_factor 1.14 < 1.5 (x1), mc_p_value 0.424 > 0.05 (우연 가능성) (x1), mc_p_value 0.228 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | mc_p_value 0.324 > 0.05 (우연 가능성) (x1), mc_p_value 0.176 > 0.05 (우연 가능성) (x1), mc_p_value 0.146 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 1.33 < 1.5 (x1), mc_p_value 0.380 > 0.05 (우연 가능성) (x1), mc_p_value 0.160 > 0.05 (우연 가능성) (x1) |
| `cmf` | max_drawdown 21.2% > 20% (x1), profit_factor 1.45 < 1.5 (x1), mc_p_value 0.338 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | mc_p_value 0.316 > 0.05 (우연 가능성) (x1), mc_p_value 0.326 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1) |
| `narrow_range` | sharpe 0.29 < 1.0 (x1), profit_factor 1.07 < 1.5 (x1), mc_p_value 0.488 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 1.17 < 1.5 (x1), mc_p_value 0.448 > 0.05 (우연 가능성) (x1), profit_factor 1.35 < 1.5 (x1) |
| `htf_ema` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.392 > 0.05 (우연 가능성) (x1), mc_p_value 0.354 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -2.72 < 1.0 (x1), profit_factor 0.66 < 1.5 (x1), mc_p_value 0.594 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.454 > 0.05 (우연 가능성) (x1), mc_p_value 0.330 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | sharpe 0.31 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe -0.07 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.544 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 1.44 < 1.5 (x1), mc_p_value 0.460 > 0.05 (우연 가능성) (x1), sharpe -0.10 < 1.0 (x1) |
| `elder_impulse` | sharpe 0.18 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1), mc_p_value 0.500 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -2.66 < 1.0 (x1), profit_factor 0.48 < 1.5 (x1), trades 14 < 15 (x1) |
| `relative_volume` | mc_p_value 0.482 > 0.05 (우연 가능성) (x2), sharpe -0.84 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1) |
| `linear_channel_rev` | profit_factor 1.30 < 1.5 (x1), mc_p_value 0.472 > 0.05 (우연 가능성) (x1), sharpe -1.38 < 1.0 (x1) |
| `wick_reversal` | no trades generated (x2), sharpe -2.99 < 1.0 (x2), profit_factor 0.00 < 1.5 (x2) |
| `price_cluster` | sharpe -2.82 < 1.0 (x1), max_drawdown 20.7% > 20% (x1), profit_factor 0.67 < 1.5 (x1) |
| `dema_cross` | sharpe -2.12 < 1.0 (x1), profit_factor 0.55 < 1.5 (x1), trades 13 < 15 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.35 < 1.5 | 3 |
| profit_factor 1.09 < 1.5 | 3 |
| mc_p_value 0.464 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.14 < 1.5 | 2 |
| mc_p_value 0.424 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.324 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.380 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.448 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.362 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.370 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +27.01% -> $12,701
- **Top 5 균등배분**: +89.83% -> $18,983
