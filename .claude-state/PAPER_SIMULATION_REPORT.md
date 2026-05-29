# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-29T05:14:43.077352Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-29T05:18:28.177936Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=807077974, block=24)_
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
| 평균 수익률 | 16.35% |
| 최고 수익률 | 59.92% (price_action_momentum) |
| 최저 수익률 | -8.17% (elder_impulse) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +59.92% | 4.12 | 44.1% | 1.48 | 156 | 14.4% | 0/4 | FAIL |
| 2 | `momentum_quality` | +55.13% | 4.78 | 47.9% | 1.67 | 116 | 9.2% | 0/4 | FAIL |
| 3 | `acceleration_band` | +44.70% | 3.92 | 47.1% | 1.62 | 98 | 14.1% | 0/4 | FAIL |
| 4 | `cmf` | +38.38% | 2.96 | 44.8% | 1.40 | 108 | 12.5% | 0/4 | FAIL |
| 5 | `order_flow_imbalance_v2` | +36.70% | 3.21 | 45.6% | 1.53 | 79 | 9.0% | 0/4 | FAIL |
| 6 | `volume_breakout` | +30.01% | 2.68 | 45.4% | 1.45 | 94 | 10.8% | 0/4 | FAIL |
| 7 | `supertrend_multi` | +24.08% | 2.79 | 44.9% | 1.40 | 96 | 9.5% | 0/4 | FAIL |
| 8 | `narrow_range` | +16.67% | 2.04 | 41.8% | 1.34 | 94 | 11.0% | 0/4 | FAIL |
| 9 | `volatility_cluster` | +16.38% | 2.19 | 43.9% | 1.36 | 79 | 7.9% | 0/4 | FAIL |
| 10 | `lob_maker` | +12.85% | 1.07 | 39.5% | 1.16 | 126 | 19.3% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `wick_reversal` | 59.1 | p100 | 1.66 | 1.66 | 500.00 | 2 | 0.0% | 0/4 | FAIL |
| 2 | `momentum_quality` | 57.9 | p95 | 4.78 | 1.75 | 1.67 | 116 | 9.2% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 55.1 | p90 | 4.12 | 1.63 | 1.48 | 156 | 14.4% | 0/4 | FAIL |
| 4 | `supertrend_multi` | 50.2 | p85 | 2.79 | 0.88 | 1.40 | 96 | 9.5% | 0/4 | FAIL |
| 5 | `acceleration_band` | 49.5 | p80 | 3.92 | 1.46 | 1.62 | 98 | 14.1% | 0/4 | FAIL |
| 6 | `cmf` | 47.8 | p76 | 2.96 | 1.31 | 1.40 | 108 | 12.5% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | 47.0 | p71 | 3.21 | 1.71 | 1.53 | 79 | 9.0% | 0/4 | FAIL |
| 8 | `roc_ma_cross` | 45.1 | p66 | 2.38 | 1.10 | 1.60 | 38 | 5.0% | 0/4 | FAIL |
| 9 | `volatility_cluster` | 43.1 | p61 | 2.19 | 1.67 | 1.36 | 79 | 7.9% | 0/4 | FAIL |
| 10 | `narrow_range` | 42.0 | p57 | 2.04 | 1.54 | 1.34 | 94 | 11.0% | 0/4 | FAIL |
| 11 | `volume_breakout` | 40.9 | p52 | 2.68 | 2.47 | 1.45 | 94 | 10.8% | 0/4 | FAIL |
| 12 | `linear_channel_rev` | 33.7 | p47 | 0.19 | 0.69 | 1.09 | 34 | 7.8% | 0/4 | FAIL |
| 13 | `price_cluster` | 33.6 | p42 | 0.67 | 1.10 | 1.17 | 38 | 9.1% | 0/4 | FAIL |
| 14 | `lob_maker` | 33.3 | p38 | 1.07 | 1.68 | 1.16 | 126 | 19.3% | 0/4 | FAIL |
| 15 | `htf_ema` | 32.2 | p33 | 0.72 | 1.60 | 1.14 | 72 | 12.3% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +59.92% | 4.12 | 1.48 | 156 | 0/4 | FAIL |
| `momentum_quality` | +55.13% | 4.78 | 1.67 | 116 | 0/4 | FAIL |
| `acceleration_band` | +44.70% | 3.92 | 1.62 | 98 | 0/4 | FAIL |
| `cmf` | +38.38% | 2.96 | 1.40 | 108 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +36.70% | 3.21 | 1.53 | 79 | 0/4 | FAIL |
| `volume_breakout` | +30.01% | 2.68 | 1.45 | 94 | 0/4 | FAIL |
| `supertrend_multi` | +24.08% | 2.79 | 1.40 | 96 | 0/4 | FAIL |
| `narrow_range` | +16.67% | 2.04 | 1.34 | 94 | 0/4 | FAIL |
| `volatility_cluster` | +16.38% | 2.19 | 1.36 | 79 | 0/4 | FAIL |
| `lob_maker` | +12.85% | 1.07 | 1.16 | 126 | 0/4 | FAIL |
| `roc_ma_cross` | +11.75% | 2.38 | 1.60 | 38 | 0/4 | FAIL |
| `htf_ema` | +5.92% | 0.72 | 1.14 | 72 | 0/4 | FAIL |
| `price_cluster` | +3.77% | 0.67 | 1.17 | 38 | 0/4 | FAIL |
| `wick_reversal` | +3.32% | 1.66 | 500.00 | 2 | 0/4 | FAIL |
| `relative_volume` | +2.72% | 0.40 | 1.13 | 58 | 0/4 | FAIL |
| `frama` | +2.63% | 0.22 | 1.07 | 87 | 0/4 | FAIL |
| `dema_cross` | +2.27% | 1.11 | 3.12 | 9 | 0/4 | FAIL |
| `value_area` | +2.14% | 0.52 | 1.50 | 18 | 0/4 | FAIL |
| `engulfing_zone` | +1.88% | 0.05 | 1.18 | 24 | 0/4 | FAIL |
| `linear_channel_rev` | +0.39% | 0.19 | 1.09 | 34 | 0/4 | FAIL |
| `positional_scaling` | -3.80% | -0.87 | 0.87 | 29 | 0/4 | FAIL |
| `elder_impulse` | -8.17% | -1.40 | 0.88 | 60 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.306 > 0.05 (우연 가능성) (x1), mc_p_value 0.198 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.304 > 0.05 (우연 가능성) (x1), mc_p_value 0.244 > 0.05 (우연 가능성) (x1), mc_p_value 0.228 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.36 < 1.5 (x1), mc_p_value 0.428 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1) |
| `cmf` | sharpe 0.96 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.494 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.354 > 0.05 (우연 가능성) (x2), sharpe 0.61 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1) |
| `volume_breakout` | sharpe -1.17 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.536 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | profit_factor 1.32 < 1.5 (x1), mc_p_value 0.410 > 0.05 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1) |
| `narrow_range` | profit_factor 1.15 < 1.5 (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1), profit_factor 1.41 < 1.5 (x1) |
| `volatility_cluster` | mc_p_value 0.362 > 0.05 (우연 가능성) (x1), profit_factor 1.18 < 1.5 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | max_drawdown 20.8% > 20% (x2), sharpe -1.20 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1) |
| `roc_ma_cross` | profit_factor 1.38 < 1.5 (x1), mc_p_value 0.480 > 0.05 (우연 가능성) (x1), mc_p_value 0.426 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | sharpe -2.05 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1), mc_p_value 0.554 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -1.07 < 1.0 (x1), profit_factor 0.86 < 1.5 (x1), mc_p_value 0.526 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x2), trades 3 < 15 (x2) |
| `relative_volume` | sharpe -2.14 < 1.0 (x1), profit_factor 0.76 < 1.5 (x1), mc_p_value 0.558 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe -2.16 < 1.0 (x1), max_drawdown 20.3% > 20% (x1), profit_factor 0.79 < 1.5 (x1) |
| `dema_cross` | sharpe 0.76 < 1.0 (x1), profit_factor 1.38 < 1.5 (x1), trades 7 < 15 (x1) |
| `value_area` | mc_p_value 0.506 > 0.05 (우연 가능성) (x1), mc_p_value 0.404 > 0.05 (우연 가능성) (x1), sharpe -1.77 < 1.0 (x1) |
| `engulfing_zone` | sharpe -3.59 < 1.0 (x1), profit_factor 0.45 < 1.5 (x1), mc_p_value 0.592 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe 0.27 < 1.0 (x1), profit_factor 1.09 < 1.5 (x1), mc_p_value 0.472 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.428 > 0.05 (우연 가능성) | 4 |
| profit_factor 1.23 < 1.5 | 3 |
| profit_factor 1.11 < 1.5 | 3 |
| profit_factor 1.40 < 1.5 | 3 |
| mc_p_value 0.464 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.79 < 1.5 | 3 |
| mc_p_value 0.370 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.14 < 1.5 | 2 |
| mc_p_value 0.354 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.452 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +16.35% -> $11,635
- **Top 5 균등배분**: +46.97% -> $14,697
