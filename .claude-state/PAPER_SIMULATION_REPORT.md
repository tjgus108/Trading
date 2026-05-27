# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-27T15:39:27.339221Z_
_Symbols: BTC/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-27T15:53:35.431221Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=508889217, block=36)_
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
| 평균 수익률 | 13.44% |
| 최고 수익률 | 68.50% (price_action_momentum) |
| 최저 수익률 | -8.61% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +68.50% | 4.20 | 44.8% | 1.49 | 156 | 15.5% | 0/4 | FAIL |
| 2 | `cmf` | +38.00% | 2.79 | 44.2% | 1.37 | 114 | 18.5% | 0/4 | FAIL |
| 3 | `momentum_quality` | +31.64% | 3.25 | 44.5% | 1.45 | 103 | 10.7% | 0/4 | FAIL |
| 4 | `volatility_cluster` | +28.27% | 3.82 | 49.6% | 1.77 | 63 | 6.4% | 0/4 | FAIL |
| 5 | `order_flow_imbalance_v2` | +26.45% | 2.19 | 44.4% | 1.36 | 82 | 16.4% | 0/4 | FAIL |
| 6 | `supertrend_multi` | +21.03% | 2.49 | 43.0% | 1.38 | 84 | 10.5% | 0/4 | FAIL |
| 7 | `frama` | +18.48% | 1.60 | 39.4% | 1.28 | 86 | 14.1% | 0/4 | FAIL |
| 8 | `volume_breakout` | +15.75% | 1.30 | 41.0% | 1.25 | 89 | 18.6% | 0/4 | FAIL |
| 9 | `acceleration_band` | +14.56% | 1.53 | 40.9% | 1.24 | 96 | 14.4% | 0/4 | FAIL |
| 10 | `elder_impulse` | +14.29% | 1.81 | 42.6% | 1.37 | 55 | 10.1% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `volatility_cluster` | 76.1 | p100 | 3.82 | 1.71 | 1.77 | 63 | 6.4% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 73.3 | p95 | 4.20 | 2.70 | 1.49 | 156 | 15.5% | 0/4 | FAIL |
| 3 | `momentum_quality` | 69.4 | p90 | 3.25 | 1.80 | 1.45 | 103 | 10.7% | 0/4 | FAIL |
| 4 | `roc_ma_cross` | 64.4 | p85 | 2.01 | 1.19 | 1.58 | 34 | 6.0% | 0/4 | FAIL |
| 5 | `supertrend_multi` | 63.1 | p80 | 2.49 | 1.86 | 1.38 | 84 | 10.5% | 0/4 | FAIL |
| 6 | `cmf` | 62.3 | p76 | 2.79 | 1.83 | 1.37 | 114 | 18.5% | 0/4 | FAIL |
| 7 | `narrow_range` | 61.3 | p71 | 1.62 | 0.43 | 1.22 | 102 | 13.9% | 0/4 | FAIL |
| 8 | `elder_impulse` | 57.7 | p66 | 1.81 | 1.77 | 1.37 | 55 | 10.1% | 0/4 | FAIL |
| 9 | `dema_cross` | 57.1 | p61 | 0.72 | 0.21 | 1.30 | 12 | 3.2% | 0/4 | FAIL |
| 10 | `acceleration_band` | 56.2 | p57 | 1.53 | 1.62 | 1.24 | 96 | 14.4% | 0/4 | FAIL |
| 11 | `order_flow_imbalance_v2` | 56.1 | p52 | 2.19 | 2.34 | 1.36 | 82 | 16.4% | 0/4 | FAIL |
| 12 | `relative_volume` | 54.5 | p47 | 1.14 | 1.30 | 1.25 | 48 | 9.0% | 0/4 | FAIL |
| 13 | `frama` | 53.9 | p42 | 1.60 | 2.34 | 1.28 | 86 | 14.1% | 0/4 | FAIL |
| 14 | `htf_ema` | 51.4 | p38 | 0.98 | 1.67 | 1.20 | 65 | 12.1% | 0/4 | FAIL |
| 15 | `volume_breakout` | 47.9 | p33 | 1.30 | 2.85 | 1.25 | 89 | 18.6% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +68.50% | 4.20 | 1.49 | 156 | 0/4 | FAIL |
| `cmf` | +38.00% | 2.79 | 1.37 | 114 | 0/4 | FAIL |
| `momentum_quality` | +31.64% | 3.25 | 1.45 | 103 | 0/4 | FAIL |
| `volatility_cluster` | +28.27% | 3.82 | 1.77 | 63 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +26.45% | 2.19 | 1.36 | 82 | 0/4 | FAIL |
| `supertrend_multi` | +21.03% | 2.49 | 1.38 | 84 | 0/4 | FAIL |
| `frama` | +18.48% | 1.60 | 1.28 | 86 | 0/4 | FAIL |
| `volume_breakout` | +15.75% | 1.30 | 1.25 | 89 | 0/4 | FAIL |
| `acceleration_band` | +14.56% | 1.53 | 1.24 | 96 | 0/4 | FAIL |
| `elder_impulse` | +14.29% | 1.81 | 1.37 | 55 | 0/4 | FAIL |
| `narrow_range` | +12.48% | 1.62 | 1.22 | 102 | 0/4 | FAIL |
| `lob_maker` | +9.39% | 0.63 | 1.11 | 110 | 0/4 | FAIL |
| `roc_ma_cross` | +9.11% | 2.01 | 1.58 | 34 | 0/4 | FAIL |
| `htf_ema` | +7.74% | 0.98 | 1.20 | 65 | 0/4 | FAIL |
| `relative_volume` | +5.75% | 1.14 | 1.25 | 48 | 0/4 | FAIL |
| `dema_cross` | +1.57% | 0.72 | 1.30 | 12 | 0/4 | FAIL |
| `wick_reversal` | +0.22% | -0.12 | 0.91 | 1 | 0/4 | FAIL |
| `linear_channel_rev` | -0.92% | -0.79 | 1.05 | 30 | 0/4 | FAIL |
| `price_cluster` | -2.40% | -0.44 | 1.01 | 30 | 0/4 | FAIL |
| `value_area` | -7.60% | -2.73 | 0.54 | 18 | 0/4 | FAIL |
| `positional_scaling` | -8.08% | -2.49 | 0.70 | 24 | 0/4 | FAIL |
| `engulfing_zone` | -8.61% | -2.16 | 0.67 | 21 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.138 > 0.05 (우연 가능성) (x1), profit_factor 1.25 < 1.5 (x1), mc_p_value 0.382 > 0.05 (우연 가능성) (x1) |
| `cmf` | max_drawdown 20.2% > 20% (x2), mc_p_value 0.276 > 0.05 (우연 가능성) (x1), profit_factor 1.29 < 1.5 (x1) |
| `momentum_quality` | mc_p_value 0.290 > 0.05 (우연 가능성) (x1), profit_factor 1.25 < 1.5 (x1), mc_p_value 0.436 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | mc_p_value 0.282 > 0.05 (우연 가능성) (x1), mc_p_value 0.388 > 0.05 (우연 가능성) (x1), profit_factor 1.32 < 1.5 (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.288 > 0.05 (우연 가능성) (x1), profit_factor 1.37 < 1.5 (x1), mc_p_value 0.396 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | mc_p_value 0.302 > 0.05 (우연 가능성) (x1), mc_p_value 0.402 > 0.05 (우연 가능성) (x1), sharpe -0.04 < 1.0 (x1) |
| `frama` | profit_factor 0.94 < 1.5 (x2), sharpe -0.77 < 1.0 (x1), mc_p_value 0.538 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | mc_p_value 0.258 > 0.05 (우연 가능성) (x1), sharpe 0.28 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1) |
| `acceleration_band` | mc_p_value 0.352 > 0.05 (우연 가능성) (x1), profit_factor 1.31 < 1.5 (x1), mc_p_value 0.378 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.484 > 0.05 (우연 가능성) (x1), mc_p_value 0.380 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.15 < 1.5 (x1), mc_p_value 0.434 > 0.05 (우연 가능성) (x1), profit_factor 1.22 < 1.5 (x1) |
| `lob_maker` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.376 > 0.05 (우연 가능성) (x1), sharpe -0.88 < 1.0 (x1) |
| `roc_ma_cross` | mc_p_value 0.440 > 0.05 (우연 가능성) (x1), mc_p_value 0.406 > 0.05 (우연 가능성) (x1), profit_factor 1.41 < 1.5 (x1) |
| `htf_ema` | mc_p_value 0.376 > 0.05 (우연 가능성) (x1), sharpe -0.66 < 1.0 (x1), profit_factor 0.94 < 1.5 (x1) |
| `relative_volume` | mc_p_value 0.420 > 0.05 (우연 가능성) (x1), profit_factor 1.41 < 1.5 (x1), mc_p_value 0.444 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe 0.92 < 1.0 (x1), trades 6 < 15 (x1), sharpe 0.79 < 1.0 (x1) |
| `wick_reversal` | trades 2 < 15 (x2), no trades generated (x1), sharpe -2.05 < 1.0 (x1) |
| `linear_channel_rev` | mc_p_value 0.432 > 0.05 (우연 가능성) (x1), sharpe -1.50 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1) |
| `price_cluster` | sharpe 0.48 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.508 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -1.52 < 1.0 (x1), profit_factor 0.60 < 1.5 (x1), trades 8 < 15 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.94 < 1.5 | 4 |
| profit_factor 1.29 < 1.5 | 3 |
| mc_p_value 0.508 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.524 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.25 < 1.5 | 2 |
| profit_factor 1.16 < 1.5 | 2 |
| profit_factor 1.49 < 1.5 | 2 |
| max_drawdown 20.2% > 20% | 2 |
| mc_p_value 0.484 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.436 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +13.44% -> $11,344
- **Top 5 균등배분**: +38.57% -> $13,857
