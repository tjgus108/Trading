# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-31T10:19:56.302225Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-31T10:23:31.581474Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=924300727, block=24)_
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
| 평균 수익률 | 15.15% |
| 최고 수익률 | 59.23% (momentum_quality) |
| 최저 수익률 | -9.09% (elder_impulse) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +59.23% | 5.11 | 49.2% | 1.71 | 120 | 10.2% | 0/4 | FAIL |
| 2 | `cmf` | +58.61% | 3.87 | 45.2% | 1.47 | 131 | 14.8% | 0/4 | FAIL |
| 3 | `price_action_momentum` | +58.40% | 4.17 | 45.7% | 1.47 | 152 | 12.2% | 0/4 | FAIL |
| 4 | `supertrend_multi` | +36.04% | 3.64 | 45.6% | 1.53 | 108 | 9.4% | 0/4 | FAIL |
| 5 | `order_flow_imbalance_v2` | +26.52% | 2.62 | 45.0% | 1.47 | 72 | 10.1% | 0/4 | FAIL |
| 6 | `volatility_cluster` | +25.78% | 3.25 | 45.4% | 1.53 | 85 | 9.3% | 0/4 | FAIL |
| 7 | `lob_maker` | +25.61% | 2.11 | 42.2% | 1.25 | 116 | 19.1% | 0/4 | FAIL |
| 8 | `acceleration_band` | +16.70% | 1.62 | 40.4% | 1.23 | 102 | 13.5% | 0/4 | FAIL |
| 9 | `volume_breakout` | +13.99% | 1.67 | 41.5% | 1.25 | 87 | 12.0% | 0/4 | FAIL |
| 10 | `dema_cross` | +9.30% | 3.75 | 73.1% | 5.70 | 9 | 1.5% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `dema_cross` | 74.3 | p100 | 3.75 | 0.32 | 5.70 | 9 | 1.5% | 0/4 | FAIL |
| 2 | `momentum_quality` | 61.7 | p95 | 5.11 | 1.58 | 1.71 | 120 | 10.2% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 58.0 | p90 | 4.17 | 1.58 | 1.47 | 152 | 12.2% | 0/4 | FAIL |
| 4 | `cmf` | 54.0 | p85 | 3.87 | 1.29 | 1.47 | 131 | 14.8% | 0/4 | FAIL |
| 5 | `supertrend_multi` | 53.1 | p80 | 3.64 | 1.67 | 1.53 | 108 | 9.4% | 0/4 | FAIL |
| 6 | `volatility_cluster` | 49.2 | p76 | 3.25 | 1.64 | 1.53 | 85 | 9.3% | 0/4 | FAIL |
| 7 | `volume_breakout` | 45.7 | p71 | 1.67 | 0.45 | 1.25 | 87 | 12.0% | 0/4 | FAIL |
| 8 | `linear_channel_rev` | 43.7 | p66 | 1.45 | 0.69 | 1.35 | 33 | 5.4% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | 43.0 | p61 | 2.62 | 1.84 | 1.47 | 72 | 10.1% | 0/4 | FAIL |
| 10 | `lob_maker` | 41.6 | p57 | 2.11 | 0.98 | 1.25 | 116 | 19.1% | 0/4 | FAIL |
| 11 | `acceleration_band` | 38.7 | p47 | 1.62 | 1.66 | 1.23 | 102 | 13.5% | 0/4 | FAIL |
| 12 | `relative_volume` | 38.7 | p52 | 0.72 | 0.80 | 1.14 | 65 | 9.4% | 0/4 | FAIL |
| 13 | `narrow_range` | 38.5 | p42 | 0.77 | 0.86 | 1.13 | 92 | 12.8% | 0/4 | FAIL |
| 14 | `roc_ma_cross` | 34.5 | p33 | 0.56 | 0.99 | 1.15 | 39 | 9.2% | 0/4 | FAIL |
| 15 | `htf_ema` | 34.5 | p38 | 0.15 | 0.49 | 1.04 | 80 | 14.8% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +59.23% | 5.11 | 1.71 | 120 | 0/4 | FAIL |
| `cmf` | +58.61% | 3.87 | 1.47 | 131 | 0/4 | FAIL |
| `price_action_momentum` | +58.40% | 4.17 | 1.47 | 152 | 0/4 | FAIL |
| `supertrend_multi` | +36.04% | 3.64 | 1.53 | 108 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +26.52% | 2.62 | 1.47 | 72 | 0/4 | FAIL |
| `volatility_cluster` | +25.78% | 3.25 | 1.53 | 85 | 0/4 | FAIL |
| `lob_maker` | +25.61% | 2.11 | 1.25 | 116 | 0/4 | FAIL |
| `acceleration_band` | +16.70% | 1.62 | 1.23 | 102 | 0/4 | FAIL |
| `volume_breakout` | +13.99% | 1.67 | 1.25 | 87 | 0/4 | FAIL |
| `dema_cross` | +9.30% | 3.75 | 5.70 | 9 | 0/4 | FAIL |
| `linear_channel_rev` | +6.06% | 1.45 | 1.35 | 33 | 0/4 | FAIL |
| `narrow_range` | +5.28% | 0.77 | 1.13 | 92 | 0/4 | FAIL |
| `relative_volume` | +4.02% | 0.72 | 1.14 | 65 | 0/4 | FAIL |
| `frama` | +3.48% | 0.32 | 1.09 | 88 | 0/4 | FAIL |
| `engulfing_zone` | +3.41% | 0.70 | 1.26 | 26 | 0/4 | FAIL |
| `roc_ma_cross` | +2.42% | 0.56 | 1.15 | 39 | 0/4 | FAIL |
| `htf_ema` | -0.08% | 0.15 | 1.04 | 80 | 0/4 | FAIL |
| `wick_reversal` | -1.23% | -1.35 | 0.56 | 4 | 0/4 | FAIL |
| `positional_scaling` | -1.62% | -0.29 | 0.98 | 31 | 0/4 | FAIL |
| `value_area` | -3.64% | -1.06 | 0.87 | 29 | 0/4 | FAIL |
| `price_cluster` | -5.84% | -0.97 | 0.86 | 34 | 0/4 | FAIL |
| `elder_impulse` | -9.09% | -1.37 | 0.88 | 65 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | mc_p_value 0.258 > 0.05 (우연 가능성) (x1), mc_p_value 0.120 > 0.05 (우연 가능성) (x1), mc_p_value 0.246 > 0.05 (우연 가능성) (x1) |
| `cmf` | mc_p_value 0.262 > 0.05 (우연 가능성) (x2), max_drawdown 22.1% > 20% (x1), profit_factor 1.22 < 1.5 (x1) |
| `price_action_momentum` | mc_p_value 0.216 > 0.05 (우연 가능성) (x1), mc_p_value 0.200 > 0.05 (우연 가능성) (x1), profit_factor 1.34 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.15 < 1.5 (x1), mc_p_value 0.446 > 0.05 (우연 가능성) (x1), mc_p_value 0.286 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe -0.06 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.528 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe 0.73 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.442 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.44 < 1.5 (x1), mc_p_value 0.298 > 0.05 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1) |
| `acceleration_band` | mc_p_value 0.288 > 0.05 (우연 가능성) (x1), profit_factor 1.21 < 1.5 (x1), mc_p_value 0.386 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 1.24 < 1.5 (x2), mc_p_value 0.450 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1) |
| `dema_cross` | trades 10 < 15 (x2), trades 7 < 15 (x1), trades 9 < 15 (x1) |
| `linear_channel_rev` | mc_p_value 0.426 > 0.05 (우연 가능성) (x2), sharpe 0.33 < 1.0 (x1), profit_factor 1.09 < 1.5 (x1) |
| `narrow_range` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.426 > 0.05 (우연 가능성) (x1), sharpe 0.13 < 1.0 (x1) |
| `relative_volume` | sharpe 0.97 < 1.0 (x1), profit_factor 1.17 < 1.5 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe -0.39 < 1.0 (x1), max_drawdown 24.2% > 20% (x1), profit_factor 0.98 < 1.5 (x1) |
| `engulfing_zone` | mc_p_value 0.408 > 0.05 (우연 가능성) (x1), sharpe -0.29 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1) |
| `roc_ma_cross` | sharpe -0.83 < 1.0 (x1), profit_factor 0.90 < 1.5 (x1), mc_p_value 0.506 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 0.99 < 1.5 (x2), sharpe 0.28 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1) |
| `wick_reversal` | profit_factor 0.00 < 1.5 (x2), sharpe -2.08 < 1.0 (x1), trades 1 < 15 (x1) |
| `positional_scaling` | sharpe -0.87 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1), mc_p_value 0.520 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -2.10 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1), mc_p_value 0.540 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.24 < 1.5 | 3 |
| profit_factor 1.13 < 1.5 | 3 |
| mc_p_value 0.422 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.17 < 1.5 | 3 |
| mc_p_value 0.468 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.426 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.530 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.99 < 1.5 | 3 |
| mc_p_value 0.512 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.44 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +15.15% -> $11,515
- **Top 5 균등배분**: +47.76% -> $14,776


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-31T10:27:19.519860Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=648876905, block=24)_
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
| 평균 수익률 | 9.89% |
| 최고 수익률 | 58.04% (price_action_momentum) |
| 최저 수익률 | -11.58% (relative_volume) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +58.04% | 4.36 | 45.5% | 1.50 | 150 | 12.1% | 0/4 | FAIL |
| 2 | `momentum_quality` | +47.48% | 4.46 | 46.9% | 1.63 | 112 | 8.7% | 0/4 | FAIL |
| 3 | `supertrend_multi` | +37.67% | 3.95 | 47.5% | 1.61 | 89 | 9.0% | 0/4 | FAIL |
| 4 | `cmf` | +19.48% | 1.70 | 40.7% | 1.21 | 118 | 18.2% | 0/4 | FAIL |
| 5 | `volume_breakout` | +14.95% | 1.71 | 41.5% | 1.24 | 89 | 13.7% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | +10.86% | 1.24 | 40.6% | 1.20 | 81 | 12.9% | 0/4 | FAIL |
| 7 | `acceleration_band` | +10.69% | 1.30 | 41.1% | 1.18 | 95 | 13.7% | 0/4 | FAIL |
| 8 | `volatility_cluster` | +9.82% | 1.41 | 40.7% | 1.25 | 74 | 10.1% | 0/4 | FAIL |
| 9 | `price_cluster` | +7.66% | 1.17 | 41.7% | 1.38 | 32 | 15.5% | 0/4 | FAIL |
| 10 | `linear_channel_rev` | +6.07% | 1.30 | 43.3% | 1.42 | 30 | 6.4% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 85.1 | p100 | 4.36 | 0.56 | 1.50 | 150 | 12.1% | 0/4 | FAIL |
| 2 | `momentum_quality` | 81.0 | p95 | 4.46 | 1.81 | 1.63 | 112 | 8.7% | 0/4 | FAIL |
| 3 | `supertrend_multi` | 75.3 | p90 | 3.95 | 2.02 | 1.61 | 89 | 9.0% | 0/4 | FAIL |
| 4 | `volume_breakout` | 61.9 | p80 | 1.71 | 0.90 | 1.24 | 89 | 13.7% | 0/4 | FAIL |
| 5 | `acceleration_band` | 61.9 | p85 | 1.30 | 0.29 | 1.18 | 95 | 13.7% | 0/4 | FAIL |
| 6 | `cmf` | 61.5 | p76 | 1.70 | 0.92 | 1.21 | 118 | 18.2% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | 58.4 | p71 | 1.24 | 1.06 | 1.20 | 81 | 12.9% | 0/4 | FAIL |
| 8 | `volatility_cluster` | 58.0 | p66 | 1.41 | 1.85 | 1.25 | 74 | 10.1% | 0/4 | FAIL |
| 9 | `linear_channel_rev` | 57.5 | p61 | 1.30 | 1.88 | 1.42 | 30 | 6.4% | 0/4 | FAIL |
| 10 | `dema_cross` | 56.2 | p57 | 0.65 | 0.85 | 1.28 | 16 | 4.4% | 0/4 | FAIL |
| 11 | `positional_scaling` | 53.3 | p52 | 0.99 | 2.33 | 1.41 | 27 | 7.7% | 0/4 | FAIL |
| 12 | `roc_ma_cross` | 53.0 | p47 | 0.74 | 1.46 | 1.22 | 38 | 9.4% | 0/4 | FAIL |
| 13 | `elder_impulse` | 51.8 | p42 | 0.76 | 2.05 | 1.20 | 56 | 10.6% | 0/4 | FAIL |
| 14 | `price_cluster` | 51.1 | p38 | 1.17 | 1.87 | 1.38 | 32 | 15.5% | 0/4 | FAIL |
| 15 | `narrow_range` | 50.8 | p33 | -0.22 | 1.06 | 1.02 | 99 | 14.1% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +58.04% | 4.36 | 1.50 | 150 | 0/4 | FAIL |
| `momentum_quality` | +47.48% | 4.46 | 1.63 | 112 | 0/4 | FAIL |
| `supertrend_multi` | +37.67% | 3.95 | 1.61 | 89 | 0/4 | FAIL |
| `cmf` | +19.48% | 1.70 | 1.21 | 118 | 0/4 | FAIL |
| `volume_breakout` | +14.95% | 1.71 | 1.24 | 89 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +10.86% | 1.24 | 1.20 | 81 | 0/4 | FAIL |
| `acceleration_band` | +10.69% | 1.30 | 1.18 | 95 | 0/4 | FAIL |
| `volatility_cluster` | +9.82% | 1.41 | 1.25 | 74 | 0/4 | FAIL |
| `price_cluster` | +7.66% | 1.17 | 1.38 | 32 | 0/4 | FAIL |
| `linear_channel_rev` | +6.07% | 1.30 | 1.42 | 30 | 0/4 | FAIL |
| `elder_impulse` | +5.94% | 0.76 | 1.20 | 56 | 0/4 | FAIL |
| `positional_scaling` | +5.67% | 0.99 | 1.41 | 27 | 0/4 | FAIL |
| `roc_ma_cross` | +3.39% | 0.74 | 1.22 | 38 | 0/4 | FAIL |
| `dema_cross` | +1.77% | 0.65 | 1.28 | 16 | 0/4 | FAIL |
| `htf_ema` | +1.48% | 0.19 | 1.08 | 68 | 0/4 | FAIL |
| `lob_maker` | +1.08% | 0.13 | 1.05 | 124 | 0/4 | FAIL |
| `value_area` | +0.94% | -0.06 | 1.24 | 26 | 0/4 | FAIL |
| `wick_reversal` | -0.76% | -1.60 | 0.00 | 1 | 0/4 | FAIL |
| `narrow_range` | -2.70% | -0.22 | 1.02 | 99 | 0/4 | FAIL |
| `frama` | -3.73% | -0.48 | 0.99 | 84 | 0/4 | FAIL |
| `engulfing_zone` | -6.62% | -1.60 | 0.71 | 22 | 0/4 | FAIL |
| `relative_volume` | -11.58% | -2.35 | 0.75 | 55 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | profit_factor 1.39 < 1.5 (x1), mc_p_value 0.264 > 0.05 (우연 가능성) (x1), mc_p_value 0.232 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.398 > 0.05 (우연 가능성) (x1), mc_p_value 0.230 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.430 > 0.05 (우연 가능성) (x1), mc_p_value 0.174 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.15 < 1.5 (x1), mc_p_value 0.426 > 0.05 (우연 가능성) (x1), profit_factor 1.34 < 1.5 (x1) |
| `volume_breakout` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.348 > 0.05 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe 0.14 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1), mc_p_value 0.526 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | sharpe 0.99 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.460 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.36 < 1.5 (x1), mc_p_value 0.384 > 0.05 (우연 가능성) (x1), sharpe -0.72 < 1.0 (x1) |
| `price_cluster` | profit_factor 1.40 < 1.5 (x1), mc_p_value 0.444 > 0.05 (우연 가능성) (x1), mc_p_value 0.342 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | mc_p_value 0.420 > 0.05 (우연 가능성) (x2), sharpe -1.09 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1) |
| `elder_impulse` | sharpe -1.83 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1), mc_p_value 0.602 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | sharpe 0.67 < 1.0 (x1), profit_factor 1.18 < 1.5 (x1), mc_p_value 0.490 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -0.59 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1), mc_p_value 0.536 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe -0.46 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), trades 13 < 15 (x1) |
| `htf_ema` | sharpe -0.46 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1), mc_p_value 0.516 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | sharpe -1.08 < 1.0 (x1), max_drawdown 22.3% > 20% (x1), profit_factor 0.93 < 1.5 (x1) |
| `value_area` | sharpe -0.76 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.522 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | profit_factor 0.00 < 1.5 (x3), trades 1 < 15 (x3), sharpe -2.11 < 1.0 (x2) |
| `narrow_range` | sharpe 0.82 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), mc_p_value 0.454 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe 0.16 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1), mc_p_value 0.504 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.04 < 1.5 | 4 |
| mc_p_value 0.384 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.18 < 1.5 | 3 |
| mc_p_value 0.526 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.406 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.602 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.420 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.438 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.19 < 1.5 | 3 |
| profit_factor 0.00 < 1.5 | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +9.89% -> $10,989
- **Top 5 균등배분**: +35.53% -> $13,553


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-31T10:31:02.207242Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=1688866862, block=24)_
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
| 평균 수익률 | 13.84% |
| 최고 수익률 | 67.47% (price_action_momentum) |
| 최저 수익률 | -10.33% (narrow_range) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +67.47% | 4.35 | 46.3% | 1.50 | 164 | 15.4% | 0/4 | FAIL |
| 2 | `supertrend_multi` | +48.88% | 4.60 | 49.2% | 1.70 | 105 | 11.5% | 0/4 | FAIL |
| 3 | `momentum_quality` | +44.72% | 4.13 | 45.8% | 1.57 | 119 | 11.1% | 0/4 | FAIL |
| 4 | `acceleration_band` | +28.57% | 2.82 | 43.2% | 1.43 | 103 | 12.0% | 0/4 | FAIL |
| 5 | `volatility_cluster` | +28.10% | 3.63 | 47.4% | 1.61 | 81 | 7.3% | 0/4 | FAIL |
| 6 | `cmf` | +23.16% | 1.89 | 41.7% | 1.23 | 124 | 19.8% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | +20.03% | 1.99 | 42.3% | 1.31 | 83 | 14.4% | 0/4 | FAIL |
| 8 | `htf_ema` | +17.95% | 1.89 | 43.5% | 1.33 | 81 | 14.4% | 0/4 | FAIL |
| 9 | `volume_breakout` | +16.80% | 1.84 | 40.7% | 1.29 | 86 | 13.6% | 0/4 | FAIL |
| 10 | `frama` | +8.63% | 1.07 | 40.8% | 1.20 | 74 | 11.8% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `volatility_cluster` | 63.2 | p100 | 3.63 | 0.62 | 1.61 | 81 | 7.3% | 0/4 | FAIL |
| 2 | `supertrend_multi` | 62.5 | p95 | 4.60 | 1.81 | 1.70 | 105 | 11.5% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 62.0 | p90 | 4.35 | 2.11 | 1.50 | 164 | 15.4% | 0/4 | FAIL |
| 4 | `momentum_quality` | 60.6 | p85 | 4.13 | 1.90 | 1.57 | 119 | 11.1% | 0/4 | FAIL |
| 5 | `acceleration_band` | 54.9 | p80 | 2.82 | 1.17 | 1.43 | 103 | 12.0% | 0/4 | FAIL |
| 6 | `dema_cross` | 54.1 | p76 | 1.52 | 2.03 | 4.13 | 8 | 2.8% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | 47.8 | p71 | 1.99 | 0.99 | 1.31 | 83 | 14.4% | 0/4 | FAIL |
| 8 | `cmf` | 47.4 | p66 | 1.89 | 1.02 | 1.23 | 124 | 19.8% | 0/4 | FAIL |
| 9 | `volume_breakout` | 46.9 | p61 | 1.84 | 1.16 | 1.29 | 86 | 13.6% | 0/4 | FAIL |
| 10 | `roc_ma_cross` | 45.3 | p57 | 1.40 | 1.09 | 1.32 | 40 | 6.3% | 0/4 | FAIL |
| 11 | `htf_ema` | 44.0 | p52 | 1.89 | 1.67 | 1.33 | 81 | 14.4% | 0/4 | FAIL |
| 12 | `elder_impulse` | 43.9 | p47 | 0.96 | 0.58 | 1.19 | 58 | 10.7% | 0/4 | FAIL |
| 13 | `frama` | 41.1 | p42 | 1.07 | 1.50 | 1.20 | 74 | 11.8% | 0/4 | FAIL |
| 14 | `value_area` | 39.7 | p38 | 0.74 | 1.11 | 1.23 | 26 | 7.2% | 0/4 | FAIL |
| 15 | `wick_reversal` | 37.1 | p33 | 0.00 | 0.00 | 0.00 | 0 | 0.0% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +67.47% | 4.35 | 1.50 | 164 | 0/4 | FAIL |
| `supertrend_multi` | +48.88% | 4.60 | 1.70 | 105 | 0/4 | FAIL |
| `momentum_quality` | +44.72% | 4.13 | 1.57 | 119 | 0/4 | FAIL |
| `acceleration_band` | +28.57% | 2.82 | 1.43 | 103 | 0/4 | FAIL |
| `volatility_cluster` | +28.10% | 3.63 | 1.61 | 81 | 0/4 | FAIL |
| `cmf` | +23.16% | 1.89 | 1.23 | 124 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +20.03% | 1.99 | 1.31 | 83 | 0/4 | FAIL |
| `htf_ema` | +17.95% | 1.89 | 1.33 | 81 | 0/4 | FAIL |
| `volume_breakout` | +16.80% | 1.84 | 1.29 | 86 | 0/4 | FAIL |
| `frama` | +8.63% | 1.07 | 1.20 | 74 | 0/4 | FAIL |
| `roc_ma_cross` | +6.76% | 1.40 | 1.32 | 40 | 0/4 | FAIL |
| `elder_impulse` | +5.90% | 0.96 | 1.19 | 58 | 0/4 | FAIL |
| `lob_maker` | +3.62% | 0.41 | 1.09 | 122 | 0/4 | FAIL |
| `price_cluster` | +3.51% | 0.48 | 1.16 | 46 | 0/4 | FAIL |
| `dema_cross` | +3.21% | 1.52 | 4.13 | 8 | 0/4 | FAIL |
| `value_area` | +3.14% | 0.74 | 1.23 | 26 | 0/4 | FAIL |
| `positional_scaling` | +0.47% | 0.01 | 1.08 | 30 | 0/4 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `engulfing_zone` | -4.88% | -1.20 | 0.88 | 24 | 0/4 | FAIL |
| `linear_channel_rev` | -5.27% | -1.42 | 0.84 | 31 | 0/4 | FAIL |
| `relative_volume` | -5.96% | -1.18 | 0.90 | 57 | 0/4 | FAIL |
| `narrow_range` | -10.33% | -1.39 | 0.89 | 88 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | sharpe 0.77 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1), mc_p_value 0.466 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | profit_factor 1.22 < 1.5 (x1), mc_p_value 0.448 > 0.05 (우연 가능성) (x1), mc_p_value 0.242 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.216 > 0.05 (우연 가능성) (x2), sharpe 0.85 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1) |
| `acceleration_band` | sharpe 0.99 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.442 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.380 > 0.05 (우연 가능성) (x1), mc_p_value 0.366 > 0.05 (우연 가능성) (x1) |
| `cmf` | sharpe 0.20 < 1.0 (x1), max_drawdown 22.4% > 20% (x1), profit_factor 1.05 < 1.5 (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.364 > 0.05 (우연 가능성) (x2), sharpe 0.68 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1) |
| `htf_ema` | profit_factor 1.39 < 1.5 (x1), mc_p_value 0.396 > 0.05 (우연 가능성) (x1), mc_p_value 0.340 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | sharpe 0.02 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1), mc_p_value 0.500 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe -0.33 < 1.0 (x2), profit_factor 0.99 < 1.5 (x2), mc_p_value 0.524 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.476 > 0.05 (우연 가능성) (x1), mc_p_value 0.408 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | profit_factor 1.22 < 1.5 (x2), mc_p_value 0.462 > 0.05 (우연 가능성) (x1), mc_p_value 0.470 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | max_drawdown 24.9% > 20% (x2), sharpe -2.04 < 1.0 (x1), max_drawdown 36.7% > 20% (x1) |
| `price_cluster` | mc_p_value 0.394 > 0.05 (우연 가능성) (x1), profit_factor 1.30 < 1.5 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe -0.78 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1), trades 10 < 15 (x1) |
| `value_area` | sharpe 0.55 < 1.0 (x1), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.484 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 1.32 < 1.5 (x1), mc_p_value 0.420 > 0.05 (우연 가능성) (x1), profit_factor 1.39 < 1.5 (x1) |
| `wick_reversal` | no trades generated (x4) |
| `engulfing_zone` | sharpe -3.52 < 1.0 (x1), profit_factor 0.47 < 1.5 (x1), mc_p_value 0.608 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -1.13 < 1.0 (x1), profit_factor 0.84 < 1.5 (x1), mc_p_value 0.556 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 4 |
| profit_factor 1.22 < 1.5 | 3 |
| profit_factor 1.30 < 1.5 | 3 |
| mc_p_value 0.436 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.448 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.216 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.480 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.45 < 1.5 | 2 |
| mc_p_value 0.340 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.476 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +13.84% -> $11,384
- **Top 5 균등배분**: +43.55% -> $14,355
