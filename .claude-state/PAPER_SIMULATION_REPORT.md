# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-28T05:25:52.561259Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-28T05:28:43.110697Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=206392630, block=36)_
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
| 평균 수익률 | 17.04% |
| 최고 수익률 | 55.31% (momentum_quality) |
| 최저 수익률 | -0.45% (dema_cross) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +55.31% | 5.08 | 48.9% | 1.74 | 114 | 8.2% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +46.56% | 3.74 | 44.3% | 1.42 | 141 | 11.1% | 0/4 | FAIL |
| 3 | `acceleration_band` | +34.27% | 3.27 | 45.5% | 1.48 | 94 | 8.5% | 0/4 | FAIL |
| 4 | `cmf` | +33.26% | 2.63 | 42.2% | 1.31 | 123 | 12.4% | 0/4 | FAIL |
| 5 | `narrow_range` | +29.11% | 3.35 | 46.0% | 1.49 | 94 | 9.5% | 0/4 | FAIL |
| 6 | `volatility_cluster` | +26.86% | 3.38 | 46.1% | 1.55 | 82 | 8.5% | 0/4 | FAIL |
| 7 | `volume_breakout` | +21.17% | 2.21 | 42.9% | 1.33 | 90 | 11.7% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | +21.04% | 2.07 | 41.7% | 1.29 | 90 | 13.6% | 0/4 | FAIL |
| 9 | `price_cluster` | +19.84% | 3.04 | 52.2% | 1.94 | 32 | 9.9% | 0/4 | FAIL |
| 10 | `lob_maker` | +17.57% | 1.40 | 40.3% | 1.19 | 118 | 17.4% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 59.9 | p100 | 5.08 | 1.30 | 1.74 | 114 | 8.2% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 57.0 | p95 | 3.74 | 0.69 | 1.42 | 141 | 11.1% | 0/4 | FAIL |
| 3 | `narrow_range` | 53.0 | p90 | 3.35 | 0.40 | 1.49 | 94 | 9.5% | 0/4 | FAIL |
| 4 | `wick_reversal` | 53.0 | p85 | 0.99 | 0.99 | 500.00 | 0 | 0.0% | 0/4 | FAIL |
| 5 | `acceleration_band` | 48.8 | p80 | 3.27 | 1.08 | 1.48 | 94 | 8.5% | 0/4 | FAIL |
| 6 | `volatility_cluster` | 48.3 | p76 | 3.38 | 1.05 | 1.55 | 82 | 8.5% | 0/4 | FAIL |
| 7 | `cmf` | 47.5 | p71 | 2.63 | 0.75 | 1.31 | 123 | 12.4% | 0/4 | FAIL |
| 8 | `linear_channel_rev` | 41.0 | p66 | 2.25 | 0.72 | 1.55 | 35 | 6.1% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | 40.9 | p61 | 2.07 | 0.59 | 1.29 | 90 | 13.6% | 0/4 | FAIL |
| 10 | `elder_impulse` | 40.5 | p57 | 1.80 | 0.44 | 1.36 | 52 | 8.2% | 0/4 | FAIL |
| 11 | `price_cluster` | 40.0 | p52 | 3.04 | 1.04 | 1.94 | 32 | 9.9% | 0/4 | FAIL |
| 12 | `volume_breakout` | 39.4 | p47 | 2.21 | 1.16 | 1.33 | 90 | 11.7% | 0/4 | FAIL |
| 13 | `roc_ma_cross` | 32.6 | p42 | 1.27 | 0.87 | 1.31 | 36 | 8.7% | 0/4 | FAIL |
| 14 | `supertrend_multi` | 31.8 | p38 | 1.47 | 1.35 | 1.20 | 95 | 15.2% | 0/4 | FAIL |
| 15 | `lob_maker` | 30.1 | p33 | 1.40 | 1.68 | 1.19 | 118 | 17.4% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +55.31% | 5.08 | 1.74 | 114 | 0/4 | FAIL |
| `price_action_momentum` | +46.56% | 3.74 | 1.42 | 141 | 0/4 | FAIL |
| `acceleration_band` | +34.27% | 3.27 | 1.48 | 94 | 0/4 | FAIL |
| `cmf` | +33.26% | 2.63 | 1.31 | 123 | 0/4 | FAIL |
| `narrow_range` | +29.11% | 3.35 | 1.49 | 94 | 0/4 | FAIL |
| `volatility_cluster` | +26.86% | 3.38 | 1.55 | 82 | 0/4 | FAIL |
| `volume_breakout` | +21.17% | 2.21 | 1.33 | 90 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +21.04% | 2.07 | 1.29 | 90 | 0/4 | FAIL |
| `price_cluster` | +19.84% | 3.04 | 1.94 | 32 | 0/4 | FAIL |
| `lob_maker` | +17.57% | 1.40 | 1.19 | 118 | 0/4 | FAIL |
| `frama` | +12.78% | 1.35 | 1.23 | 90 | 0/4 | FAIL |
| `elder_impulse` | +11.64% | 1.80 | 1.36 | 52 | 0/4 | FAIL |
| `supertrend_multi` | +11.19% | 1.47 | 1.20 | 95 | 0/4 | FAIL |
| `linear_channel_rev` | +10.18% | 2.25 | 1.55 | 35 | 0/4 | FAIL |
| `engulfing_zone` | +8.10% | 1.50 | 1.60 | 20 | 0/4 | FAIL |
| `roc_ma_cross` | +5.70% | 1.27 | 1.31 | 36 | 0/4 | FAIL |
| `htf_ema` | +5.33% | 0.67 | 1.16 | 68 | 0/4 | FAIL |
| `relative_volume` | +3.98% | 0.68 | 1.15 | 65 | 0/4 | FAIL |
| `wick_reversal` | +1.42% | 0.99 | 500.00 | 0 | 0/4 | FAIL |
| `value_area` | +0.43% | 0.10 | 1.12 | 18 | 0/4 | FAIL |
| `positional_scaling` | -0.36% | -0.24 | 1.07 | 24 | 0/4 | FAIL |
| `dema_cross` | -0.45% | -0.20 | 1.00 | 11 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | mc_p_value 0.260 > 0.05 (우연 가능성) (x1), mc_p_value 0.244 > 0.05 (우연 가능성) (x1), mc_p_value 0.288 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | mc_p_value 0.288 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1), mc_p_value 0.302 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.354 > 0.05 (우연 가능성) (x1), mc_p_value 0.288 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.350 > 0.05 (우연 가능성) (x1), profit_factor 1.35 < 1.5 (x1) |
| `narrow_range` | mc_p_value 0.348 > 0.05 (우연 가능성) (x1), profit_factor 1.40 < 1.5 (x1), mc_p_value 0.390 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | mc_p_value 0.330 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1), mc_p_value 0.392 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | mc_p_value 0.350 > 0.05 (우연 가능성) (x1), profit_factor 1.24 < 1.5 (x1), mc_p_value 0.458 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.394 > 0.05 (우연 가능성) (x1), profit_factor 1.27 < 1.5 (x1) |
| `price_cluster` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.472 > 0.05 (우연 가능성) (x1), mc_p_value 0.414 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.378 > 0.05 (우연 가능성) (x1), sharpe -0.87 < 1.0 (x1) |
| `frama` | sharpe -0.66 < 1.0 (x1), max_drawdown 29.9% > 20% (x1), profit_factor 0.96 < 1.5 (x1) |
| `elder_impulse` | profit_factor 1.33 < 1.5 (x1), mc_p_value 0.456 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1) |
| `supertrend_multi` | sharpe 0.82 < 1.0 (x1), max_drawdown 20.7% > 20% (x1), profit_factor 1.13 < 1.5 (x1) |
| `linear_channel_rev` | mc_p_value 0.466 > 0.05 (우연 가능성) (x2), profit_factor 1.43 < 1.5 (x1), mc_p_value 0.508 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -0.93 < 1.0 (x1), profit_factor 0.84 < 1.5 (x1), mc_p_value 0.524 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | mc_p_value 0.454 > 0.05 (우연 가능성) (x2), profit_factor 1.46 < 1.5 (x1), mc_p_value 0.490 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 1.33 < 1.5 (x1), mc_p_value 0.418 > 0.05 (우연 가능성) (x1), sharpe -1.06 < 1.0 (x1) |
| `relative_volume` | mc_p_value 0.436 > 0.05 (우연 가능성) (x1), sharpe 0.54 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1) |
| `wick_reversal` | trades 1 < 15 (x2), no trades generated (x2) |
| `value_area` | profit_factor 1.42 < 1.5 (x1), mc_p_value 0.436 > 0.05 (우연 가능성) (x1), sharpe -1.66 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.46 < 1.5 | 4 |
| mc_p_value 0.466 > 0.05 (우연 가능성) | 4 |
| mc_p_value 0.288 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.26 < 1.5 | 3 |
| mc_p_value 0.362 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.22 < 1.5 | 3 |
| mc_p_value 0.378 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.33 < 1.5 | 3 |
| mc_p_value 0.486 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.454 > 0.05 (우연 가능성) | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +17.04% -> $11,704
- **Top 5 균등배분**: +39.70% -> $13,970
