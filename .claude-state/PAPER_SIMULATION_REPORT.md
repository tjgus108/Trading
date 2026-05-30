# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-30T20:12:00.915249Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-30T20:14:55.467361Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1031478164, block=24)_
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
| 평균 수익률 | 10.87% |
| 최고 수익률 | 38.40% (order_flow_imbalance_v2) |
| 최저 수익률 | -7.60% (price_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `order_flow_imbalance_v2` | +38.40% | 3.16 | 44.1% | 1.51 | 90 | 11.2% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +37.27% | 2.95 | 42.2% | 1.34 | 152 | 25.9% | 0/4 | FAIL |
| 3 | `cmf` | +28.96% | 2.32 | 42.3% | 1.29 | 117 | 16.0% | 0/4 | FAIL |
| 4 | `momentum_quality` | +20.11% | 2.33 | 42.1% | 1.32 | 102 | 14.2% | 0/4 | FAIL |
| 5 | `volatility_cluster` | +19.54% | 2.56 | 44.4% | 1.40 | 81 | 9.7% | 0/4 | FAIL |
| 6 | `narrow_range` | +18.66% | 2.35 | 44.1% | 1.35 | 89 | 10.7% | 0/4 | FAIL |
| 7 | `volume_breakout` | +18.20% | 1.90 | 40.8% | 1.27 | 99 | 10.6% | 0/4 | FAIL |
| 8 | `supertrend_multi` | +17.51% | 1.92 | 40.0% | 1.24 | 122 | 15.5% | 0/4 | FAIL |
| 9 | `lob_maker` | +13.29% | 1.16 | 39.6% | 1.16 | 124 | 18.3% | 0/4 | FAIL |
| 10 | `value_area` | +11.85% | 2.56 | 47.8% | 1.64 | 34 | 3.6% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `order_flow_imbalance_v2` | 57.3 | p100 | 3.16 | 1.82 | 1.51 | 90 | 11.2% | 0/4 | FAIL |
| 2 | `value_area` | 56.7 | p95 | 2.56 | 0.67 | 1.64 | 34 | 3.6% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 56.1 | p90 | 2.95 | 1.01 | 1.34 | 152 | 25.9% | 0/4 | FAIL |
| 4 | `volatility_cluster` | 55.8 | p85 | 2.56 | 1.14 | 1.40 | 81 | 9.7% | 0/4 | FAIL |
| 5 | `momentum_quality` | 55.5 | p80 | 2.33 | 0.62 | 1.32 | 102 | 14.2% | 0/4 | FAIL |
| 6 | `narrow_range` | 55.3 | p76 | 2.35 | 0.92 | 1.35 | 89 | 10.7% | 0/4 | FAIL |
| 7 | `supertrend_multi` | 53.7 | p66 | 1.92 | 0.69 | 1.24 | 122 | 15.5% | 0/4 | FAIL |
| 8 | `wick_reversal` | 53.7 | p71 | 0.48 | 2.45 | 500.44 | 2 | 1.5% | 0/4 | FAIL |
| 9 | `cmf` | 53.2 | p61 | 2.32 | 1.30 | 1.29 | 117 | 16.0% | 0/4 | FAIL |
| 10 | `volume_breakout` | 53.0 | p57 | 1.90 | 1.01 | 1.27 | 99 | 10.6% | 0/4 | FAIL |
| 11 | `lob_maker` | 44.5 | p52 | 1.16 | 1.32 | 1.16 | 124 | 18.3% | 0/4 | FAIL |
| 12 | `acceleration_band` | 42.2 | p47 | 1.06 | 1.49 | 1.16 | 108 | 17.3% | 0/4 | FAIL |
| 13 | `relative_volume` | 39.2 | p42 | 0.35 | 1.37 | 1.09 | 70 | 9.1% | 0/4 | FAIL |
| 14 | `htf_ema` | 38.5 | p38 | 0.49 | 0.34 | 1.09 | 77 | 19.0% | 0/4 | FAIL |
| 15 | `frama` | 35.0 | p33 | 0.85 | 2.06 | 1.17 | 82 | 19.0% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `order_flow_imbalance_v2` | +38.40% | 3.16 | 1.51 | 90 | 0/4 | FAIL |
| `price_action_momentum` | +37.27% | 2.95 | 1.34 | 152 | 0/4 | FAIL |
| `cmf` | +28.96% | 2.32 | 1.29 | 117 | 0/4 | FAIL |
| `momentum_quality` | +20.11% | 2.33 | 1.32 | 102 | 0/4 | FAIL |
| `volatility_cluster` | +19.54% | 2.56 | 1.40 | 81 | 0/4 | FAIL |
| `narrow_range` | +18.66% | 2.35 | 1.35 | 89 | 0/4 | FAIL |
| `volume_breakout` | +18.20% | 1.90 | 1.27 | 99 | 0/4 | FAIL |
| `supertrend_multi` | +17.51% | 1.92 | 1.24 | 122 | 0/4 | FAIL |
| `lob_maker` | +13.29% | 1.16 | 1.16 | 124 | 0/4 | FAIL |
| `value_area` | +11.85% | 2.56 | 1.64 | 34 | 0/4 | FAIL |
| `acceleration_band` | +9.74% | 1.06 | 1.16 | 108 | 0/4 | FAIL |
| `frama` | +8.62% | 0.85 | 1.17 | 82 | 0/4 | FAIL |
| `htf_ema` | +2.65% | 0.49 | 1.09 | 77 | 0/4 | FAIL |
| `relative_volume` | +2.39% | 0.35 | 1.09 | 70 | 0/4 | FAIL |
| `linear_channel_rev` | +1.97% | 0.27 | 1.19 | 30 | 0/4 | FAIL |
| `dema_cross` | +1.61% | 0.40 | 1.89 | 16 | 0/4 | FAIL |
| `wick_reversal` | +1.33% | 0.48 | 500.44 | 2 | 0/4 | FAIL |
| `positional_scaling` | +0.57% | 0.06 | 1.06 | 28 | 0/4 | FAIL |
| `roc_ma_cross` | -0.26% | -0.09 | 1.06 | 40 | 0/4 | FAIL |
| `elder_impulse` | -1.37% | -0.25 | 1.05 | 65 | 0/4 | FAIL |
| `engulfing_zone` | -4.26% | -1.13 | 0.84 | 23 | 0/4 | FAIL |
| `price_cluster` | -7.60% | -1.24 | 0.90 | 38 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `order_flow_imbalance_v2` | mc_p_value 0.370 > 0.05 (우연 가능성) (x1), mc_p_value 0.236 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1) |
| `price_action_momentum` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.360 > 0.05 (우연 가능성) (x1), mc_p_value 0.242 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.38 < 1.5 (x1), mc_p_value 0.306 > 0.05 (우연 가능성) (x1), mc_p_value 0.324 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 1.29 < 1.5 (x1), mc_p_value 0.366 > 0.05 (우연 가능성) (x1), profit_factor 1.44 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.334 > 0.05 (우연 가능성) (x1), mc_p_value 0.336 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | mc_p_value 0.336 > 0.05 (우연 가능성) (x1), profit_factor 1.43 < 1.5 (x1), mc_p_value 0.426 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1), profit_factor 1.50 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.21 < 1.5 (x2), mc_p_value 0.406 > 0.05 (우연 가능성) (x1), profit_factor 1.37 < 1.5 (x1) |
| `lob_maker` | max_drawdown 22.3% > 20% (x1), profit_factor 1.17 < 1.5 (x1), mc_p_value 0.364 > 0.05 (우연 가능성) (x1) |
| `value_area` | mc_p_value 0.400 > 0.05 (우연 가능성) (x1), mc_p_value 0.470 > 0.05 (우연 가능성) (x1), profit_factor 1.48 < 1.5 (x1) |
| `acceleration_band` | profit_factor 1.42 < 1.5 (x1), mc_p_value 0.334 > 0.05 (우연 가능성) (x1), profit_factor 1.22 < 1.5 (x1) |
| `frama` | mc_p_value 0.320 > 0.05 (우연 가능성) (x1), profit_factor 1.18 < 1.5 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | mc_p_value 0.476 > 0.05 (우연 가능성) (x2), sharpe 0.13 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1) |
| `relative_volume` | profit_factor 1.32 < 1.5 (x1), mc_p_value 0.370 > 0.05 (우연 가능성) (x1), profit_factor 1.18 < 1.5 (x1) |
| `linear_channel_rev` | mc_p_value 0.378 > 0.05 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1), mc_p_value 0.486 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | trades 11 < 15 (x1), mc_p_value 0.426 > 0.05 (우연 가능성) (x1), sharpe -1.26 < 1.0 (x1) |
| `wick_reversal` | trades 2 < 15 (x2), sharpe -3.56 < 1.0 (x1), profit_factor 0.00 < 1.5 (x1) |
| `positional_scaling` | sharpe -1.86 < 1.0 (x1), profit_factor 0.68 < 1.5 (x1), mc_p_value 0.568 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -1.81 < 1.0 (x1), profit_factor 0.77 < 1.5 (x1), mc_p_value 0.546 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | profit_factor 0.77 < 1.5 (x2), mc_p_value 0.360 > 0.05 (우연 가능성) (x1), sharpe 0.66 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.06 < 1.5 | 3 |
| mc_p_value 0.336 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.37 < 1.5 | 3 |
| profit_factor 0.77 < 1.5 | 3 |
| mc_p_value 0.370 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.338 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.464 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.26 < 1.5 | 2 |
| mc_p_value 0.360 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.19 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +10.87% -> $11,087
- **Top 5 균등배분**: +28.86% -> $12,886
