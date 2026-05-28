# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-28T10:19:13.430991Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-28T10:22:15.554503Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=833564694, block=36)_
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
| 평균 수익률 | 15.19% |
| 최고 수익률 | 63.93% (price_action_momentum) |
| 최저 수익률 | -10.91% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +63.93% | 4.39 | 45.3% | 1.55 | 150 | 9.9% | 0/4 | FAIL |
| 2 | `cmf` | +58.66% | 4.22 | 46.6% | 1.58 | 111 | 9.9% | 0/4 | FAIL |
| 3 | `htf_ema` | +37.88% | 3.68 | 49.1% | 1.81 | 66 | 9.7% | 0/4 | FAIL |
| 4 | `momentum_quality` | +32.88% | 3.35 | 45.2% | 1.48 | 111 | 7.4% | 0/4 | FAIL |
| 5 | `lob_maker` | +28.86% | 2.25 | 42.2% | 1.27 | 123 | 19.4% | 0/4 | FAIL |
| 6 | `acceleration_band` | +24.75% | 2.50 | 43.1% | 1.36 | 99 | 15.3% | 0/4 | FAIL |
| 7 | `supertrend_multi` | +24.21% | 2.96 | 45.3% | 1.53 | 82 | 8.3% | 0/4 | FAIL |
| 8 | `volume_breakout` | +22.86% | 1.94 | 40.6% | 1.33 | 89 | 15.9% | 0/4 | FAIL |
| 9 | `positional_scaling` | +13.52% | 2.89 | 53.0% | 2.11 | 24 | 5.9% | 0/4 | FAIL |
| 10 | `value_area` | +9.80% | 2.60 | 52.7% | 2.07 | 19 | 3.7% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `cmf` | 79.7 | p100 | 4.22 | 0.38 | 1.58 | 111 | 9.9% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 76.8 | p95 | 4.39 | 1.98 | 1.55 | 150 | 9.9% | 0/4 | FAIL |
| 3 | `momentum_quality` | 67.8 | p90 | 3.35 | 2.13 | 1.48 | 111 | 7.4% | 0/4 | FAIL |
| 4 | `positional_scaling` | 66.1 | p85 | 2.89 | 1.57 | 2.11 | 24 | 5.9% | 0/4 | FAIL |
| 5 | `htf_ema` | 65.7 | p80 | 3.68 | 2.36 | 1.81 | 66 | 9.7% | 0/4 | FAIL |
| 6 | `value_area` | 65.2 | p76 | 2.60 | 1.53 | 2.07 | 19 | 3.7% | 0/4 | FAIL |
| 7 | `supertrend_multi` | 62.0 | p71 | 2.96 | 2.31 | 1.53 | 82 | 8.3% | 0/4 | FAIL |
| 8 | `acceleration_band` | 61.6 | p66 | 2.50 | 1.03 | 1.36 | 99 | 15.3% | 0/4 | FAIL |
| 9 | `lob_maker` | 59.7 | p61 | 2.25 | 0.96 | 1.27 | 123 | 19.4% | 0/4 | FAIL |
| 10 | `dema_cross` | 54.9 | p57 | 1.21 | 1.18 | 1.62 | 14 | 3.9% | 0/4 | FAIL |
| 11 | `roc_ma_cross` | 53.2 | p52 | 1.29 | 1.18 | 1.37 | 35 | 6.8% | 0/4 | FAIL |
| 12 | `engulfing_zone` | 53.0 | p47 | 1.06 | 0.75 | 1.37 | 19 | 6.0% | 0/4 | FAIL |
| 13 | `narrow_range` | 51.0 | p42 | 0.55 | 0.95 | 1.11 | 87 | 10.9% | 0/4 | FAIL |
| 14 | `linear_channel_rev` | 50.2 | p38 | 0.76 | 0.66 | 1.20 | 30 | 8.0% | 0/4 | FAIL |
| 15 | `volume_breakout` | 50.0 | p33 | 1.94 | 2.55 | 1.33 | 89 | 15.9% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +63.93% | 4.39 | 1.55 | 150 | 0/4 | FAIL |
| `cmf` | +58.66% | 4.22 | 1.58 | 111 | 0/4 | FAIL |
| `htf_ema` | +37.88% | 3.68 | 1.81 | 66 | 0/4 | FAIL |
| `momentum_quality` | +32.88% | 3.35 | 1.48 | 111 | 0/4 | FAIL |
| `lob_maker` | +28.86% | 2.25 | 1.27 | 123 | 0/4 | FAIL |
| `acceleration_band` | +24.75% | 2.50 | 1.36 | 99 | 0/4 | FAIL |
| `supertrend_multi` | +24.21% | 2.96 | 1.53 | 82 | 0/4 | FAIL |
| `volume_breakout` | +22.86% | 1.94 | 1.33 | 89 | 0/4 | FAIL |
| `positional_scaling` | +13.52% | 2.89 | 2.11 | 24 | 0/4 | FAIL |
| `value_area` | +9.80% | 2.60 | 2.07 | 19 | 0/4 | FAIL |
| `roc_ma_cross` | +5.37% | 1.29 | 1.37 | 35 | 0/4 | FAIL |
| `engulfing_zone` | +4.45% | 1.06 | 1.37 | 19 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +4.12% | 0.37 | 1.09 | 88 | 0/4 | FAIL |
| `narrow_range` | +3.60% | 0.55 | 1.11 | 87 | 0/4 | FAIL |
| `dema_cross` | +3.42% | 1.21 | 1.62 | 14 | 0/4 | FAIL |
| `relative_volume` | +3.11% | 0.60 | 1.14 | 55 | 0/4 | FAIL |
| `linear_channel_rev` | +2.90% | 0.76 | 1.20 | 30 | 0/4 | FAIL |
| `price_cluster` | +2.38% | 0.45 | 1.13 | 39 | 0/4 | FAIL |
| `elder_impulse` | +1.24% | 0.29 | 1.14 | 52 | 0/4 | FAIL |
| `wick_reversal` | -0.53% | -1.03 | 0.00 | 0 | 0/4 | FAIL |
| `volatility_cluster` | -2.27% | -0.24 | 1.00 | 80 | 0/4 | FAIL |
| `frama` | -10.91% | -1.49 | 0.87 | 85 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.252 > 0.05 (우연 가능성) (x1), mc_p_value 0.202 > 0.05 (우연 가능성) (x1), profit_factor 1.39 < 1.5 (x1) |
| `cmf` | mc_p_value 0.312 > 0.05 (우연 가능성) (x2), mc_p_value 0.332 > 0.05 (우연 가능성) (x1), mc_p_value 0.340 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | mc_p_value 0.378 > 0.05 (우연 가능성) (x1), mc_p_value 0.328 > 0.05 (우연 가능성) (x1), mc_p_value 0.380 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.232 > 0.05 (우연 가능성) (x1), mc_p_value 0.282 > 0.05 (우연 가능성) (x1), profit_factor 1.21 < 1.5 (x1) |
| `lob_maker` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.312 > 0.05 (우연 가능성) (x1), profit_factor 1.27 < 1.5 (x1) |
| `acceleration_band` | mc_p_value 0.310 > 0.05 (우연 가능성) (x1), max_drawdown 22.3% > 20% (x1), profit_factor 1.40 < 1.5 (x1) |
| `supertrend_multi` | mc_p_value 0.304 > 0.05 (우연 가능성) (x1), mc_p_value 0.320 > 0.05 (우연 가능성) (x1), profit_factor 1.33 < 1.5 (x1) |
| `volume_breakout` | mc_p_value 0.298 > 0.05 (우연 가능성) (x1), mc_p_value 0.350 > 0.05 (우연 가능성) (x1), sharpe -0.28 < 1.0 (x1) |
| `positional_scaling` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.436 > 0.05 (우연 가능성) (x1), profit_factor 1.36 < 1.5 (x1) |
| `value_area` | sharpe 0.26 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), trades 13 < 15 (x1) |
| `roc_ma_cross` | mc_p_value 0.476 > 0.05 (우연 가능성) (x1), mc_p_value 0.484 > 0.05 (우연 가능성) (x1), profit_factor 1.28 < 1.5 (x1) |
| `engulfing_zone` | mc_p_value 0.466 > 0.05 (우연 가능성) (x1), mc_p_value 0.416 > 0.05 (우연 가능성) (x1), sharpe 0.06 < 1.0 (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.40 < 1.5 (x1), mc_p_value 0.360 > 0.05 (우연 가능성) (x1), profit_factor 1.16 < 1.5 (x1) |
| `narrow_range` | profit_factor 1.28 < 1.5 (x1), mc_p_value 0.434 > 0.05 (우연 가능성) (x1), sharpe 0.88 < 1.0 (x1) |
| `dema_cross` | sharpe -0.39 < 1.0 (x1), profit_factor 0.90 < 1.5 (x1), trades 9 < 15 (x1) |
| `relative_volume` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.428 > 0.05 (우연 가능성) (x1), profit_factor 1.24 < 1.5 (x1) |
| `linear_channel_rev` | mc_p_value 0.462 > 0.05 (우연 가능성) (x2), profit_factor 1.35 < 1.5 (x1), mc_p_value 0.460 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe 0.42 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1), mc_p_value 0.506 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | sharpe 0.97 < 1.0 (x1), profit_factor 1.20 < 1.5 (x1), mc_p_value 0.470 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | sharpe -2.06 < 1.0 (x2), profit_factor 0.00 < 1.5 (x2), trades 1 < 15 (x2) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.312 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.460 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.28 < 1.5 | 3 |
| mc_p_value 0.462 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.16 < 1.5 | 2 |
| profit_factor 0.99 < 1.5 | 2 |
| profit_factor 1.21 < 1.5 | 2 |
| profit_factor 1.15 < 1.5 | 2 |
| mc_p_value 0.400 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.40 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +15.19% -> $11,519
- **Top 5 균등배분**: +44.44% -> $14,444
