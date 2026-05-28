# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-28T23:12:21.748128Z_
_Symbols: BTC/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-28T23:26:53.363404Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1643966520, block=36)_
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
| 평균 수익률 | 14.35% |
| 최고 수익률 | 69.95% (price_action_momentum) |
| 최저 수익률 | -8.13% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +69.95% | 4.79 | 46.3% | 1.59 | 148 | 12.4% | 0/4 | FAIL |
| 2 | `momentum_quality` | +50.26% | 4.77 | 48.3% | 1.71 | 112 | 12.3% | 0/4 | FAIL |
| 3 | `cmf` | +35.92% | 2.73 | 42.7% | 1.34 | 118 | 18.0% | 0/4 | FAIL |
| 4 | `volatility_cluster` | +33.56% | 4.00 | 48.2% | 1.69 | 84 | 8.2% | 0/4 | FAIL |
| 5 | `narrow_range` | +28.45% | 3.25 | 46.2% | 1.49 | 90 | 10.1% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | +25.32% | 2.31 | 43.4% | 1.41 | 80 | 16.9% | 0/4 | FAIL |
| 7 | `acceleration_band` | +25.17% | 2.52 | 44.2% | 1.40 | 95 | 13.9% | 0/4 | FAIL |
| 8 | `supertrend_multi` | +22.59% | 2.13 | 41.3% | 1.23 | 147 | 20.0% | 0/4 | FAIL |
| 9 | `price_cluster` | +17.16% | 2.36 | 48.8% | 1.71 | 36 | 8.3% | 0/4 | FAIL |
| 10 | `htf_ema` | +15.07% | 1.73 | 41.5% | 1.29 | 75 | 11.3% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 66.5 | p100 | 4.79 | 1.17 | 1.59 | 148 | 12.4% | 0/4 | FAIL |
| 2 | `momentum_quality` | 63.6 | p95 | 4.77 | 0.91 | 1.71 | 112 | 12.3% | 0/4 | FAIL |
| 3 | `volatility_cluster` | 58.8 | p90 | 4.00 | 1.28 | 1.69 | 84 | 8.2% | 0/4 | FAIL |
| 4 | `narrow_range` | 55.7 | p85 | 3.25 | 1.09 | 1.49 | 90 | 10.1% | 0/4 | FAIL |
| 5 | `wick_reversal` | 54.6 | p80 | -0.37 | 1.78 | 250.45 | 1 | 1.0% | 0/4 | FAIL |
| 6 | `supertrend_multi` | 51.8 | p76 | 2.13 | 0.90 | 1.23 | 147 | 20.0% | 0/4 | FAIL |
| 7 | `cmf` | 51.6 | p71 | 2.73 | 1.20 | 1.34 | 118 | 18.0% | 0/4 | FAIL |
| 8 | `acceleration_band` | 49.4 | p66 | 2.52 | 1.62 | 1.40 | 95 | 13.9% | 0/4 | FAIL |
| 9 | `htf_ema` | 46.6 | p61 | 1.73 | 1.26 | 1.29 | 75 | 11.3% | 0/4 | FAIL |
| 10 | `positional_scaling` | 46.1 | p57 | 1.38 | 0.46 | 1.37 | 27 | 5.4% | 0/4 | FAIL |
| 11 | `price_cluster` | 45.0 | p52 | 2.36 | 1.93 | 1.71 | 36 | 8.3% | 0/4 | FAIL |
| 12 | `order_flow_imbalance_v2` | 44.2 | p47 | 2.31 | 1.98 | 1.41 | 80 | 16.9% | 0/4 | FAIL |
| 13 | `volume_breakout` | 41.4 | p42 | 0.85 | 1.23 | 1.15 | 89 | 16.8% | 0/4 | FAIL |
| 14 | `roc_ma_cross` | 41.3 | p38 | 1.21 | 1.77 | 1.37 | 34 | 6.7% | 0/4 | FAIL |
| 15 | `engulfing_zone` | 36.1 | p33 | -0.10 | 1.01 | 1.03 | 16 | 7.3% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +69.95% | 4.79 | 1.59 | 148 | 0/4 | FAIL |
| `momentum_quality` | +50.26% | 4.77 | 1.71 | 112 | 0/4 | FAIL |
| `cmf` | +35.92% | 2.73 | 1.34 | 118 | 0/4 | FAIL |
| `volatility_cluster` | +33.56% | 4.00 | 1.69 | 84 | 0/4 | FAIL |
| `narrow_range` | +28.45% | 3.25 | 1.49 | 90 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +25.32% | 2.31 | 1.41 | 80 | 0/4 | FAIL |
| `acceleration_band` | +25.17% | 2.52 | 1.40 | 95 | 0/4 | FAIL |
| `supertrend_multi` | +22.59% | 2.13 | 1.23 | 147 | 0/4 | FAIL |
| `price_cluster` | +17.16% | 2.36 | 1.71 | 36 | 0/4 | FAIL |
| `htf_ema` | +15.07% | 1.73 | 1.29 | 75 | 0/4 | FAIL |
| `volume_breakout` | +7.30% | 0.85 | 1.15 | 89 | 0/4 | FAIL |
| `positional_scaling` | +5.57% | 1.38 | 1.37 | 27 | 0/4 | FAIL |
| `roc_ma_cross` | +5.28% | 1.21 | 1.37 | 34 | 0/4 | FAIL |
| `dema_cross` | +0.63% | 0.02 | 1.28 | 8 | 0/4 | FAIL |
| `relative_volume` | +0.63% | 0.09 | 1.11 | 58 | 0/4 | FAIL |
| `wick_reversal` | -0.02% | -0.37 | 250.45 | 1 | 0/4 | FAIL |
| `engulfing_zone` | -0.30% | -0.10 | 1.03 | 16 | 0/4 | FAIL |
| `linear_channel_rev` | -1.31% | -0.29 | 1.04 | 32 | 0/4 | FAIL |
| `elder_impulse` | -4.85% | -1.13 | 1.06 | 55 | 0/4 | FAIL |
| `value_area` | -5.73% | -2.44 | 0.53 | 15 | 0/4 | FAIL |
| `frama` | -6.81% | -0.81 | 0.94 | 86 | 0/4 | FAIL |
| `lob_maker` | -8.13% | -0.59 | 0.98 | 119 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.206 > 0.05 (우연 가능성) (x1), mc_p_value 0.204 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1) |
| `momentum_quality` | mc_p_value 0.348 > 0.05 (우연 가능성) (x1), mc_p_value 0.248 > 0.05 (우연 가능성) (x1), mc_p_value 0.296 > 0.05 (우연 가능성) (x1) |
| `cmf` | max_drawdown 25.3% > 20% (x2), profit_factor 1.28 < 1.5 (x2), mc_p_value 0.324 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | mc_p_value 0.266 > 0.05 (우연 가능성) (x1), mc_p_value 0.380 > 0.05 (우연 가능성) (x1), profit_factor 1.39 < 1.5 (x1) |
| `narrow_range` | mc_p_value 0.312 > 0.05 (우연 가능성) (x1), profit_factor 1.22 < 1.5 (x1), mc_p_value 0.448 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.336 > 0.05 (우연 가능성) (x1), mc_p_value 0.354 > 0.05 (우연 가능성) (x1), sharpe 0.97 < 1.0 (x1) |
| `acceleration_band` | mc_p_value 0.350 > 0.05 (우연 가능성) (x1), mc_p_value 0.360 > 0.05 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1) |
| `supertrend_multi` | max_drawdown 20.3% > 20% (x2), profit_factor 1.22 < 1.5 (x1), mc_p_value 0.386 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -0.31 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1), mc_p_value 0.516 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 1.50 < 1.5 (x1), mc_p_value 0.386 > 0.05 (우연 가능성) (x1), sharpe 0.13 < 1.0 (x1) |
| `volume_breakout` | profit_factor 1.33 < 1.5 (x1), mc_p_value 0.420 > 0.05 (우연 가능성) (x1), profit_factor 1.19 < 1.5 (x1) |
| `positional_scaling` | profit_factor 1.50 < 1.5 (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1), sharpe 0.61 < 1.0 (x1) |
| `roc_ma_cross` | mc_p_value 0.432 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1), mc_p_value 0.420 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | trades 7 < 15 (x2), sharpe -2.66 < 1.0 (x1), profit_factor 0.32 < 1.5 (x1) |
| `relative_volume` | profit_factor 1.22 < 1.5 (x1), mc_p_value 0.434 > 0.05 (우연 가능성) (x1), profit_factor 1.36 < 1.5 (x1) |
| `wick_reversal` | trades 1 < 15 (x3), profit_factor 0.00 < 1.5 (x2), sharpe -2.09 < 1.0 (x1) |
| `engulfing_zone` | sharpe -1.83 < 1.0 (x1), profit_factor 0.60 < 1.5 (x1), trades 13 < 15 (x1) |
| `linear_channel_rev` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.466 > 0.05 (우연 가능성) (x1), profit_factor 1.41 < 1.5 (x1) |
| `elder_impulse` | mc_p_value 0.388 > 0.05 (우연 가능성) (x1), sharpe 0.94 < 1.0 (x1), profit_factor 1.18 < 1.5 (x1) |
| `value_area` | sharpe -3.35 < 1.0 (x1), profit_factor 0.42 < 1.5 (x1), mc_p_value 0.564 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.22 < 1.5 | 4 |
| profit_factor 1.45 < 1.5 | 3 |
| mc_p_value 0.406 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.458 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.480 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.14 < 1.5 | 3 |
| trades 1 < 15 | 3 |
| profit_factor 1.36 < 1.5 | 2 |
| max_drawdown 25.3% > 20% | 2 |
| profit_factor 1.28 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +14.35% -> $11,435
- **Top 5 균등배분**: +43.63% -> $14,363
