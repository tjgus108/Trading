# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-28T15:21:35.118557Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-28T15:24:09.756400Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1344845015, block=72)_
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
| PASS (일관성 50%+) | 7개 |
| FAIL | 15개 |
| 평균 수익률 | 16.36% |
| 최고 수익률 | 78.47% (price_action_momentum) |
| 최저 수익률 | -8.05% (narrow_range) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +78.47% | 5.21 | 47.2% | 1.62 | 155 | 12.6% | 3/4 | PASS |
| 2 | `cmf` | +46.14% | 3.21 | 44.3% | 1.45 | 112 | 12.4% | 2/4 | PASS |
| 3 | `volume_breakout` | +43.22% | 3.77 | 46.1% | 1.59 | 93 | 13.0% | 2/4 | PASS |
| 4 | `momentum_quality` | +36.79% | 3.76 | 46.1% | 1.52 | 100 | 12.6% | 3/4 | PASS |
| 5 | `lob_maker` | +36.38% | 2.75 | 43.2% | 1.34 | 120 | 15.2% | 1/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | +33.46% | 3.17 | 46.2% | 1.49 | 78 | 11.5% | 2/4 | PASS |
| 7 | `htf_ema` | +23.10% | 2.49 | 44.4% | 1.43 | 73 | 12.6% | 2/4 | PASS |
| 8 | `positional_scaling` | +15.55% | 2.91 | 51.8% | 2.00 | 33 | 7.3% | 3/4 | PASS |
| 9 | `elder_impulse` | +13.70% | 1.94 | 43.3% | 1.37 | 56 | 11.3% | 1/4 | FAIL |
| 10 | `relative_volume` | +11.25% | 1.77 | 42.0% | 1.35 | 61 | 9.3% | 1/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 74.4 | p100 | 5.21 | 1.45 | 1.62 | 155 | 12.6% | 3/4 | PASS |
| 2 | `momentum_quality` | 61.4 | p95 | 3.76 | 1.44 | 1.52 | 100 | 12.6% | 3/4 | PASS |
| 3 | `volume_breakout` | 56.9 | p90 | 3.77 | 1.61 | 1.59 | 93 | 13.0% | 2/4 | PASS |
| 4 | `order_flow_imbalance_v2` | 56.8 | p85 | 3.17 | 0.58 | 1.49 | 78 | 11.5% | 2/4 | PASS |
| 5 | `cmf` | 53.7 | p80 | 3.21 | 2.14 | 1.45 | 112 | 12.4% | 2/4 | PASS |
| 6 | `positional_scaling` | 53.5 | p76 | 2.91 | 2.46 | 2.00 | 33 | 7.3% | 3/4 | PASS |
| 7 | `lob_maker` | 50.8 | p71 | 2.75 | 0.92 | 1.34 | 120 | 15.2% | 1/4 | FAIL |
| 8 | `linear_channel_rev` | 49.7 | p66 | 2.39 | 0.65 | 1.68 | 28 | 6.0% | 1/4 | FAIL |
| 9 | `htf_ema` | 49.5 | p61 | 2.49 | 1.23 | 1.43 | 73 | 12.6% | 2/4 | PASS |
| 10 | `dema_cross` | 43.3 | p57 | 1.03 | 3.23 | 4.24 | 13 | 4.6% | 0/4 | FAIL |
| 11 | `elder_impulse` | 42.2 | p52 | 1.94 | 1.30 | 1.37 | 56 | 11.3% | 1/4 | FAIL |
| 12 | `relative_volume` | 42.2 | p47 | 1.77 | 1.59 | 1.35 | 61 | 9.3% | 1/4 | FAIL |
| 13 | `roc_ma_cross` | 37.4 | p42 | 1.14 | 1.08 | 1.29 | 34 | 5.9% | 0/4 | FAIL |
| 14 | `volatility_cluster` | 36.0 | p38 | 1.19 | 1.69 | 1.19 | 86 | 11.1% | 0/4 | FAIL |
| 15 | `price_cluster` | 31.7 | p33 | 0.78 | 0.86 | 1.19 | 40 | 12.2% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +78.47% | 5.21 | 1.62 | 155 | 3/4 | PASS |
| `cmf` | +46.14% | 3.21 | 1.45 | 112 | 2/4 | PASS |
| `volume_breakout` | +43.22% | 3.77 | 1.59 | 93 | 2/4 | PASS |
| `momentum_quality` | +36.79% | 3.76 | 1.52 | 100 | 3/4 | PASS |
| `lob_maker` | +36.38% | 2.75 | 1.34 | 120 | 1/4 | FAIL |
| `order_flow_imbalance_v2` | +33.46% | 3.17 | 1.49 | 78 | 2/4 | PASS |
| `htf_ema` | +23.10% | 2.49 | 1.43 | 73 | 2/4 | PASS |
| `positional_scaling` | +15.55% | 2.91 | 2.00 | 33 | 3/4 | PASS |
| `elder_impulse` | +13.70% | 1.94 | 1.37 | 56 | 1/4 | FAIL |
| `relative_volume` | +11.25% | 1.77 | 1.35 | 61 | 1/4 | FAIL |
| `linear_channel_rev` | +9.80% | 2.39 | 1.68 | 28 | 1/4 | FAIL |
| `volatility_cluster` | +9.07% | 1.19 | 1.19 | 86 | 0/4 | FAIL |
| `roc_ma_cross` | +4.90% | 1.14 | 1.29 | 34 | 0/4 | FAIL |
| `price_cluster` | +4.47% | 0.78 | 1.19 | 40 | 0/4 | FAIL |
| `supertrend_multi` | +4.02% | 0.45 | 1.11 | 134 | 1/4 | FAIL |
| `dema_cross` | +3.04% | 1.03 | 4.24 | 13 | 0/4 | FAIL |
| `value_area` | +0.19% | -0.07 | 1.03 | 18 | 0/4 | FAIL |
| `acceleration_band` | -0.43% | 0.00 | 1.05 | 99 | 0/4 | FAIL |
| `wick_reversal` | -0.53% | -0.85 | 0.46 | 1 | 0/4 | FAIL |
| `engulfing_zone` | -1.33% | -0.25 | 0.98 | 22 | 0/4 | FAIL |
| `frama` | -3.23% | -0.33 | 1.00 | 71 | 0/4 | FAIL |
| `narrow_range` | -8.05% | -0.94 | 0.95 | 100 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `lob_maker` | profit_factor 1.23 < 1.5 (x1), mc_p_value 0.132 > 0.05 (우연 가능성) (x1), max_drawdown 20.1% > 20% (x1) |
| `elder_impulse` | mc_p_value 0.074 > 0.05 (우연 가능성) (x1), sharpe 0.76 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1) |
| `relative_volume` | sharpe 0.15 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.432 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | mc_p_value 0.154 > 0.05 (우연 가능성) (x1), profit_factor 1.49 < 1.5 (x1), mc_p_value 0.134 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe 0.23 < 1.0 (x1), profit_factor 1.07 < 1.5 (x1), mc_p_value 0.456 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -0.71 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.570 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | profit_factor 1.23 < 1.5 (x1), mc_p_value 0.268 > 0.05 (우연 가능성) (x1), sharpe -0.54 < 1.0 (x1) |
| `supertrend_multi` | sharpe 0.73 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1), mc_p_value 0.284 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe -1.36 < 1.0 (x1), profit_factor 0.72 < 1.5 (x1), mc_p_value 0.726 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -1.78 < 1.0 (x1), profit_factor 0.60 < 1.5 (x1), trades 12 < 15 (x1) |
| `acceleration_band` | sharpe -0.30 < 1.0 (x1), max_drawdown 20.6% > 20% (x1), profit_factor 1.00 < 1.5 (x1) |
| `wick_reversal` | profit_factor 0.00 < 1.5 (x2), trades 1 < 15 (x2), sharpe -2.11 < 1.0 (x1) |
| `engulfing_zone` | sharpe -1.04 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1), mc_p_value 0.676 > 0.05 (우연 가능성) (x1) |
| `frama` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.226 > 0.05 (우연 가능성) (x1), sharpe -0.42 < 1.0 (x1) |
| `narrow_range` | profit_factor 0.98 < 1.5 (x2), sharpe -0.71 < 1.0 (x1), max_drawdown 28.2% > 20% (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.23 < 1.5 | 3 |
| profit_factor 0.98 < 1.5 | 3 |
| profit_factor 1.27 < 1.5 | 2 |
| mc_p_value 0.158 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.42 < 1.5 | 2 |
| mc_p_value 0.074 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.15 < 1.5 | 2 |
| profit_factor 1.14 < 1.5 | 2 |
| profit_factor 1.07 < 1.5 | 2 |
| mc_p_value 0.154 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +16.36% -> $11,636
- **PASS 7개 균등배분**: +39.53% -> $13,953
- **Top 5 균등배분**: +48.20% -> $14,820


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-28T15:26:44.198273Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=36518908, block=72)_
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
| PASS (일관성 50%+) | 11개 |
| FAIL | 11개 |
| 평균 수익률 | 27.12% |
| 최고 수익률 | 108.31% (cmf) |
| 최저 수익률 | -12.38% (price_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `cmf` | +108.31% | 6.23 | 53.5% | 2.06 | 108 | 12.2% | 3/4 | PASS |
| 2 | `price_action_momentum` | +84.23% | 5.02 | 47.2% | 1.56 | 158 | 12.7% | 3/4 | PASS |
| 3 | `supertrend_multi` | +67.31% | 5.54 | 49.3% | 1.71 | 127 | 10.6% | 4/4 | PASS |
| 4 | `volume_breakout` | +59.25% | 4.60 | 47.5% | 1.73 | 94 | 11.0% | 3/4 | PASS |
| 5 | `order_flow_imbalance_v2` | +53.81% | 4.14 | 49.1% | 1.68 | 87 | 8.8% | 3/4 | PASS |
| 6 | `momentum_quality` | +44.94% | 4.28 | 48.5% | 1.60 | 105 | 14.2% | 3/4 | PASS |
| 7 | `htf_ema` | +35.51% | 3.64 | 48.0% | 1.68 | 69 | 12.0% | 2/4 | PASS |
| 8 | `narrow_range` | +30.60% | 3.38 | 46.8% | 1.53 | 92 | 9.6% | 2/4 | PASS |
| 9 | `volatility_cluster` | +30.23% | 3.89 | 48.7% | 1.64 | 79 | 8.1% | 3/4 | PASS |
| 10 | `lob_maker` | +28.09% | 1.99 | 40.9% | 1.24 | 128 | 17.3% | 1/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 73.5 | p100 | 5.54 | 1.43 | 1.71 | 127 | 10.6% | 4/4 | PASS |
| 2 | `cmf` | 69.7 | p95 | 6.23 | 2.23 | 2.06 | 108 | 12.2% | 3/4 | PASS |
| 3 | `dema_cross` | 67.3 | p90 | 3.71 | 1.08 | 3.86 | 12 | 1.9% | 1/4 | FAIL |
| 4 | `price_action_momentum` | 66.9 | p85 | 5.02 | 2.38 | 1.56 | 158 | 12.7% | 3/4 | PASS |
| 5 | `volatility_cluster` | 65.4 | p80 | 3.89 | 0.40 | 1.64 | 79 | 8.1% | 3/4 | PASS |
| 6 | `volume_breakout` | 62.6 | p76 | 4.60 | 2.01 | 1.73 | 94 | 11.0% | 3/4 | PASS |
| 7 | `order_flow_imbalance_v2` | 62.4 | p71 | 4.14 | 1.79 | 1.68 | 87 | 8.8% | 3/4 | PASS |
| 8 | `momentum_quality` | 60.5 | p66 | 4.28 | 1.71 | 1.60 | 105 | 14.2% | 3/4 | PASS |
| 9 | `roc_ma_cross` | 57.7 | p61 | 3.48 | 1.67 | 2.17 | 34 | 5.8% | 2/4 | PASS |
| 10 | `narrow_range` | 57.1 | p57 | 3.38 | 1.59 | 1.53 | 92 | 9.6% | 2/4 | PASS |
| 11 | `htf_ema` | 54.9 | p52 | 3.64 | 1.55 | 1.68 | 69 | 12.0% | 2/4 | PASS |
| 12 | `relative_volume` | 48.5 | p42 | 2.01 | 0.89 | 1.40 | 51 | 8.1% | 1/4 | FAIL |
| 13 | `value_area` | 48.5 | p47 | 1.73 | 2.02 | 1.76 | 18 | 3.6% | 2/4 | PASS |
| 14 | `acceleration_band` | 46.5 | p38 | 2.17 | 1.00 | 1.31 | 92 | 15.8% | 1/4 | FAIL |
| 15 | `lob_maker` | 45.4 | p33 | 1.99 | 1.81 | 1.24 | 128 | 17.3% | 1/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `cmf` | +108.31% | 6.23 | 2.06 | 108 | 3/4 | PASS |
| `price_action_momentum` | +84.23% | 5.02 | 1.56 | 158 | 3/4 | PASS |
| `supertrend_multi` | +67.31% | 5.54 | 1.71 | 127 | 4/4 | PASS |
| `volume_breakout` | +59.25% | 4.60 | 1.73 | 94 | 3/4 | PASS |
| `order_flow_imbalance_v2` | +53.81% | 4.14 | 1.68 | 87 | 3/4 | PASS |
| `momentum_quality` | +44.94% | 4.28 | 1.60 | 105 | 3/4 | PASS |
| `htf_ema` | +35.51% | 3.64 | 1.68 | 69 | 2/4 | PASS |
| `narrow_range` | +30.60% | 3.38 | 1.53 | 92 | 2/4 | PASS |
| `volatility_cluster` | +30.23% | 3.89 | 1.64 | 79 | 3/4 | PASS |
| `lob_maker` | +28.09% | 1.99 | 1.24 | 128 | 1/4 | FAIL |
| `acceleration_band` | +20.23% | 2.17 | 1.31 | 92 | 1/4 | FAIL |
| `roc_ma_cross` | +17.34% | 3.48 | 2.17 | 34 | 2/4 | PASS |
| `dema_cross` | +11.60% | 3.71 | 3.86 | 12 | 1/4 | FAIL |
| `relative_volume` | +11.08% | 2.01 | 1.40 | 51 | 1/4 | FAIL |
| `value_area` | +6.77% | 1.73 | 1.76 | 18 | 2/4 | PASS |
| `linear_channel_rev` | +5.00% | 1.31 | 1.55 | 27 | 1/4 | FAIL |
| `elder_impulse` | +1.98% | 0.35 | 1.10 | 50 | 0/4 | FAIL |
| `positional_scaling` | +1.61% | 0.58 | 1.28 | 23 | 0/4 | FAIL |
| `wick_reversal` | -1.22% | -1.55 | 0.00 | 1 | 0/4 | FAIL |
| `frama` | -3.06% | -1.07 | 0.99 | 90 | 1/4 | FAIL |
| `engulfing_zone` | -4.54% | -0.89 | 0.89 | 27 | 0/4 | FAIL |
| `price_cluster` | -12.38% | -2.49 | 0.70 | 38 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `lob_maker` | profit_factor 1.23 < 1.5 (x1), mc_p_value 0.142 > 0.05 (우연 가능성) (x1), sharpe -0.51 < 1.0 (x1) |
| `acceleration_band` | mc_p_value 0.132 > 0.05 (우연 가능성) (x2), profit_factor 1.33 < 1.5 (x1), sharpe 0.85 < 1.0 (x1) |
| `dema_cross` | trades 7 < 15 (x1), trades 9 < 15 (x1), trades 12 < 15 (x1) |
| `relative_volume` | profit_factor 1.40 < 1.5 (x1), mc_p_value 0.130 > 0.05 (우연 가능성) (x1), profit_factor 1.27 < 1.5 (x1) |
| `linear_channel_rev` | sharpe 0.18 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1), mc_p_value 0.400 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -0.23 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.480 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | sharpe 0.92 < 1.0 (x1), profit_factor 1.32 < 1.5 (x1), mc_p_value 0.300 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | profit_factor 0.00 < 1.5 (x3), trades 1 < 15 (x3), sharpe -2.08 < 1.0 (x2) |
| `frama` | sharpe -4.38 < 1.0 (x1), max_drawdown 30.3% > 20% (x1), profit_factor 0.63 < 1.5 (x1) |
| `engulfing_zone` | sharpe -0.34 < 1.0 (x1), profit_factor 0.97 < 1.5 (x1), mc_p_value 0.526 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -1.92 < 1.0 (x1), profit_factor 0.74 < 1.5 (x1), mc_p_value 0.792 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.27 < 1.5 | 3 |
| mc_p_value 0.132 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.00 < 1.5 | 3 |
| trades 1 < 15 | 3 |
| profit_factor 1.16 < 1.5 | 2 |
| mc_p_value 0.154 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.23 < 1.5 | 2 |
| profit_factor 1.24 < 1.5 | 2 |
| mc_p_value 0.140 > 0.05 (우연 가능성) | 2 |
| max_drawdown 22.4% > 20% | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +27.12% -> $12,712
- **PASS 11개 균등배분**: +48.94% -> $14,894
- **Top 5 균등배분**: +74.58% -> $17,458


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-28T15:29:22.023467Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=794927353, block=72)_
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
| PASS (일관성 50%+) | 4개 |
| FAIL | 18개 |
| 평균 수익률 | 16.50% |
| 최고 수익률 | 62.99% (cmf) |
| 최저 수익률 | -5.08% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `cmf` | +62.99% | 4.37 | 46.8% | 1.59 | 115 | 13.6% | 3/4 | PASS |
| 2 | `price_action_momentum` | +45.94% | 3.57 | 43.1% | 1.39 | 151 | 14.3% | 1/4 | FAIL |
| 3 | `momentum_quality` | +43.40% | 4.34 | 46.3% | 1.60 | 114 | 11.0% | 3/4 | PASS |
| 4 | `order_flow_imbalance_v2` | +38.55% | 3.48 | 46.6% | 1.53 | 82 | 12.7% | 3/4 | PASS |
| 5 | `acceleration_band` | +28.55% | 2.82 | 43.3% | 1.39 | 98 | 14.9% | 0/4 | FAIL |
| 6 | `volume_breakout` | +26.31% | 2.70 | 44.0% | 1.38 | 92 | 12.3% | 1/4 | FAIL |
| 7 | `supertrend_multi` | +26.15% | 3.07 | 44.7% | 1.43 | 92 | 10.2% | 1/4 | FAIL |
| 8 | `lob_maker` | +23.91% | 1.86 | 40.9% | 1.21 | 126 | 19.5% | 0/4 | FAIL |
| 9 | `volatility_cluster` | +20.95% | 2.83 | 45.0% | 1.46 | 79 | 8.0% | 2/4 | PASS |
| 10 | `htf_ema` | +15.95% | 1.75 | 43.0% | 1.28 | 71 | 16.0% | 1/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 65.3 | p100 | 4.34 | 0.92 | 1.60 | 114 | 11.0% | 3/4 | PASS |
| 2 | `cmf` | 63.4 | p95 | 4.37 | 0.96 | 1.59 | 115 | 13.6% | 3/4 | PASS |
| 3 | `order_flow_imbalance_v2` | 57.6 | p90 | 3.48 | 0.52 | 1.53 | 82 | 12.7% | 3/4 | PASS |
| 4 | `price_action_momentum` | 55.2 | p85 | 3.57 | 0.96 | 1.39 | 151 | 14.3% | 1/4 | FAIL |
| 5 | `volatility_cluster` | 51.8 | p80 | 2.83 | 1.10 | 1.46 | 79 | 8.0% | 2/4 | PASS |
| 6 | `supertrend_multi` | 50.8 | p76 | 3.07 | 0.73 | 1.43 | 92 | 10.2% | 1/4 | FAIL |
| 7 | `volume_breakout` | 46.9 | p71 | 2.70 | 0.77 | 1.38 | 92 | 12.3% | 1/4 | FAIL |
| 8 | `acceleration_band` | 44.7 | p66 | 2.82 | 0.27 | 1.39 | 98 | 14.9% | 0/4 | FAIL |
| 9 | `wick_reversal` | 43.2 | p61 | -0.06 | 2.02 | 500.00 | 1 | 0.6% | 0/4 | FAIL |
| 10 | `relative_volume` | 38.0 | p57 | 1.53 | 0.52 | 1.26 | 64 | 8.7% | 0/4 | FAIL |
| 11 | `linear_channel_rev` | 37.3 | p52 | 1.87 | 1.02 | 1.46 | 32 | 5.5% | 0/4 | FAIL |
| 12 | `positional_scaling` | 36.1 | p47 | 1.71 | 1.60 | 1.56 | 28 | 6.5% | 1/4 | FAIL |
| 13 | `narrow_range` | 34.6 | p42 | 1.19 | 1.00 | 1.18 | 100 | 12.7% | 0/4 | FAIL |
| 14 | `lob_maker` | 34.2 | p38 | 1.86 | 1.34 | 1.21 | 126 | 19.5% | 0/4 | FAIL |
| 15 | `htf_ema` | 33.4 | p33 | 1.75 | 1.57 | 1.28 | 71 | 16.0% | 1/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `cmf` | +62.99% | 4.37 | 1.59 | 115 | 3/4 | PASS |
| `price_action_momentum` | +45.94% | 3.57 | 1.39 | 151 | 1/4 | FAIL |
| `momentum_quality` | +43.40% | 4.34 | 1.60 | 114 | 3/4 | PASS |
| `order_flow_imbalance_v2` | +38.55% | 3.48 | 1.53 | 82 | 3/4 | PASS |
| `acceleration_band` | +28.55% | 2.82 | 1.39 | 98 | 0/4 | FAIL |
| `volume_breakout` | +26.31% | 2.70 | 1.38 | 92 | 1/4 | FAIL |
| `supertrend_multi` | +26.15% | 3.07 | 1.43 | 92 | 1/4 | FAIL |
| `lob_maker` | +23.91% | 1.86 | 1.21 | 126 | 0/4 | FAIL |
| `volatility_cluster` | +20.95% | 2.83 | 1.46 | 79 | 2/4 | PASS |
| `htf_ema` | +15.95% | 1.75 | 1.28 | 71 | 1/4 | FAIL |
| `relative_volume` | +9.58% | 1.53 | 1.26 | 64 | 0/4 | FAIL |
| `narrow_range` | +9.13% | 1.19 | 1.18 | 100 | 0/4 | FAIL |
| `linear_channel_rev` | +8.27% | 1.87 | 1.46 | 32 | 0/4 | FAIL |
| `positional_scaling` | +7.37% | 1.71 | 1.56 | 28 | 1/4 | FAIL |
| `roc_ma_cross` | +3.53% | 0.78 | 1.17 | 41 | 0/4 | FAIL |
| `value_area` | +2.99% | 0.88 | 1.40 | 17 | 0/4 | FAIL |
| `elder_impulse` | +2.39% | 0.42 | 1.09 | 61 | 0/4 | FAIL |
| `wick_reversal` | +0.84% | -0.06 | 500.00 | 1 | 0/4 | FAIL |
| `price_cluster` | -2.05% | -0.31 | 1.03 | 35 | 0/4 | FAIL |
| `dema_cross` | -2.17% | -0.87 | 1.15 | 16 | 0/4 | FAIL |
| `engulfing_zone` | -4.54% | -0.99 | 0.97 | 22 | 0/4 | FAIL |
| `frama` | -5.08% | -0.47 | 0.96 | 80 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | profit_factor 1.37 < 1.5 (x1), profit_factor 1.31 < 1.5 (x1), mc_p_value 0.068 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.088 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1) |
| `volume_breakout` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.104 > 0.05 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.46 < 1.5 (x1), profit_factor 1.30 < 1.5 (x1), mc_p_value 0.130 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.39 < 1.5 (x1), max_drawdown 20.8% > 20% (x1), profit_factor 1.29 < 1.5 (x1) |
| `htf_ema` | profit_factor 1.15 < 1.5 (x1), mc_p_value 0.314 > 0.05 (우연 가능성) (x1), sharpe 0.07 < 1.0 (x1) |
| `relative_volume` | profit_factor 1.19 < 1.5 (x1), mc_p_value 0.252 > 0.05 (우연 가능성) (x1), profit_factor 1.17 < 1.5 (x1) |
| `narrow_range` | sharpe -0.15 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1), mc_p_value 0.496 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | mc_p_value 0.066 > 0.05 (우연 가능성) (x1), mc_p_value 0.082 > 0.05 (우연 가능성) (x1), profit_factor 1.23 < 1.5 (x1) |
| `positional_scaling` | mc_p_value 0.140 > 0.05 (우연 가능성) (x1), sharpe -0.61 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1) |
| `roc_ma_cross` | sharpe 0.93 < 1.0 (x1), profit_factor 1.19 < 1.5 (x1), mc_p_value 0.302 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe 0.57 < 1.0 (x1), profit_factor 1.18 < 1.5 (x1), mc_p_value 0.328 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | sharpe 0.82 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.354 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | trades 1 < 15 (x4), sharpe -2.08 < 1.0 (x2), profit_factor 0.00 < 1.5 (x2) |
| `price_cluster` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.198 > 0.05 (우연 가능성) (x1), sharpe -1.45 < 1.0 (x1) |
| `dema_cross` | sharpe -4.08 < 1.0 (x1), profit_factor 0.37 < 1.5 (x1), mc_p_value 0.986 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -1.37 < 1.0 (x1), profit_factor 0.73 < 1.5 (x1), mc_p_value 0.740 > 0.05 (우연 가능성) (x1) |
| `frama` | profit_factor 1.00 < 1.5 (x2), sharpe -0.18 < 1.0 (x1), mc_p_value 0.528 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.39 < 1.5 | 4 |
| trades 1 < 15 | 4 |
| profit_factor 1.35 < 1.5 | 3 |
| profit_factor 1.37 < 1.5 | 3 |
| profit_factor 1.04 < 1.5 | 3 |
| profit_factor 1.19 < 1.5 | 3 |
| profit_factor 0.94 < 1.5 | 3 |
| mc_p_value 0.060 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.33 < 1.5 | 2 |
| mc_p_value 0.056 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +16.50% -> $11,650
- **PASS 4개 균등배분**: +41.47% -> $14,147
- **Top 5 균등배분**: +43.89% -> $14,389
