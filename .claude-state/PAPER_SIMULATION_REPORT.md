# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-30T10:14:15.457228Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-30T10:17:58.262700Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1075209857, block=24)_
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
| 평균 수익률 | 25.41% |
| 최고 수익률 | 79.14% (lob_maker) |
| 최저 수익률 | -0.54% (price_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `lob_maker` | +79.14% | 4.41 | 46.2% | 1.66 | 123 | 13.4% | 0/4 | FAIL |
| 2 | `order_flow_imbalance_v2` | +52.09% | 3.54 | 46.8% | 1.77 | 87 | 16.3% | 0/4 | FAIL |
| 3 | `supertrend_multi` | +46.87% | 3.76 | 42.6% | 1.38 | 184 | 16.9% | 0/4 | FAIL |
| 4 | `volume_breakout` | +42.56% | 3.44 | 45.0% | 1.57 | 95 | 14.5% | 0/4 | FAIL |
| 5 | `price_action_momentum` | +41.02% | 3.02 | 42.8% | 1.31 | 158 | 16.3% | 0/4 | FAIL |
| 6 | `elder_impulse` | +39.77% | 4.78 | 52.2% | 2.15 | 56 | 6.4% | 0/4 | FAIL |
| 7 | `cmf` | +35.41% | 2.65 | 42.4% | 1.30 | 128 | 15.5% | 0/4 | FAIL |
| 8 | `momentum_quality` | +34.72% | 3.63 | 43.9% | 1.46 | 114 | 12.2% | 0/4 | FAIL |
| 9 | `acceleration_band` | +34.06% | 2.98 | 45.5% | 1.46 | 100 | 14.9% | 0/4 | FAIL |
| 10 | `frama` | +25.13% | 2.45 | 42.5% | 1.36 | 94 | 13.4% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `value_area` | 73.9 | p100 | 4.39 | 1.49 | 3.33 | 27 | 3.1% | 0/4 | FAIL |
| 2 | `elder_impulse` | 68.5 | p95 | 4.78 | 1.33 | 2.15 | 56 | 6.4% | 0/4 | FAIL |
| 3 | `volatility_cluster` | 62.4 | p90 | 3.42 | 0.08 | 1.57 | 73 | 7.1% | 0/4 | FAIL |
| 4 | `supertrend_multi` | 61.2 | p85 | 3.76 | 0.74 | 1.38 | 184 | 16.9% | 0/4 | FAIL |
| 5 | `momentum_quality` | 60.6 | p80 | 3.63 | 0.37 | 1.46 | 114 | 12.2% | 0/4 | FAIL |
| 6 | `lob_maker` | 59.3 | p76 | 4.41 | 2.58 | 1.66 | 123 | 13.4% | 0/4 | FAIL |
| 7 | `price_action_momentum` | 52.8 | p71 | 3.02 | 1.64 | 1.31 | 158 | 16.3% | 0/4 | FAIL |
| 8 | `htf_ema` | 52.6 | p66 | 2.62 | 0.77 | 1.40 | 78 | 10.5% | 0/4 | FAIL |
| 9 | `cmf` | 50.6 | p61 | 2.65 | 1.13 | 1.30 | 128 | 15.5% | 0/4 | FAIL |
| 10 | `volume_breakout` | 50.5 | p57 | 3.44 | 2.57 | 1.57 | 95 | 14.5% | 0/4 | FAIL |
| 11 | `frama` | 49.3 | p52 | 2.45 | 1.03 | 1.36 | 94 | 13.4% | 0/4 | FAIL |
| 12 | `acceleration_band` | 49.0 | p47 | 2.98 | 2.04 | 1.46 | 100 | 14.9% | 0/4 | FAIL |
| 13 | `narrow_range` | 48.9 | p42 | 2.57 | 2.39 | 1.43 | 94 | 10.8% | 0/4 | FAIL |
| 14 | `engulfing_zone` | 48.7 | p38 | 1.68 | 1.03 | 1.61 | 20 | 4.7% | 0/4 | FAIL |
| 15 | `order_flow_imbalance_v2` | 46.9 | p33 | 3.54 | 3.64 | 1.77 | 87 | 16.3% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `lob_maker` | +79.14% | 4.41 | 1.66 | 123 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +52.09% | 3.54 | 1.77 | 87 | 0/4 | FAIL |
| `supertrend_multi` | +46.87% | 3.76 | 1.38 | 184 | 0/4 | FAIL |
| `volume_breakout` | +42.56% | 3.44 | 1.57 | 95 | 0/4 | FAIL |
| `price_action_momentum` | +41.02% | 3.02 | 1.31 | 158 | 0/4 | FAIL |
| `elder_impulse` | +39.77% | 4.78 | 2.15 | 56 | 0/4 | FAIL |
| `cmf` | +35.41% | 2.65 | 1.30 | 128 | 0/4 | FAIL |
| `momentum_quality` | +34.72% | 3.63 | 1.46 | 114 | 0/4 | FAIL |
| `acceleration_band` | +34.06% | 2.98 | 1.46 | 100 | 0/4 | FAIL |
| `frama` | +25.13% | 2.45 | 1.36 | 94 | 0/4 | FAIL |
| `volatility_cluster` | +24.35% | 3.42 | 1.57 | 73 | 0/4 | FAIL |
| `htf_ema` | +23.66% | 2.62 | 1.40 | 78 | 0/4 | FAIL |
| `narrow_range` | +22.88% | 2.57 | 1.43 | 94 | 0/4 | FAIL |
| `value_area` | +20.11% | 4.39 | 3.33 | 27 | 0/4 | FAIL |
| `relative_volume` | +11.83% | 1.57 | 1.40 | 59 | 0/4 | FAIL |
| `engulfing_zone` | +8.00% | 1.68 | 1.61 | 20 | 0/4 | FAIL |
| `positional_scaling` | +5.79% | 1.17 | 1.41 | 27 | 0/4 | FAIL |
| `linear_channel_rev` | +4.70% | 1.19 | 1.32 | 29 | 0/4 | FAIL |
| `roc_ma_cross` | +4.58% | 1.04 | 1.25 | 39 | 0/4 | FAIL |
| `dema_cross` | +3.43% | 0.93 | 1.51 | 18 | 0/4 | FAIL |
| `wick_reversal` | -0.54% | -1.03 | 0.00 | 0 | 0/4 | FAIL |
| `price_cluster` | -0.54% | -0.07 | 1.05 | 39 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `lob_maker` | sharpe 0.66 < 1.0 (x1), max_drawdown 22.1% > 20% (x1), profit_factor 1.09 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe -2.01 < 1.0 (x1), max_drawdown 31.5% > 20% (x1), profit_factor 0.81 < 1.5 (x1) |
| `supertrend_multi` | max_drawdown 22.1% > 20% (x2), mc_p_value 0.248 > 0.05 (우연 가능성) (x1), profit_factor 1.25 < 1.5 (x1) |
| `volume_breakout` | sharpe -0.95 < 1.0 (x1), max_drawdown 23.8% > 20% (x1), profit_factor 0.92 < 1.5 (x1) |
| `price_action_momentum` | profit_factor 1.19 < 1.5 (x2), profit_factor 1.24 < 1.5 (x1), mc_p_value 0.336 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | mc_p_value 0.408 > 0.05 (우연 가능성) (x1), mc_p_value 0.228 > 0.05 (우연 가능성) (x1), mc_p_value 0.330 > 0.05 (우연 가능성) (x1) |
| `cmf` | sharpe 0.85 < 1.0 (x1), max_drawdown 21.1% > 20% (x1), profit_factor 1.11 < 1.5 (x1) |
| `momentum_quality` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.318 > 0.05 (우연 가능성) (x1), mc_p_value 0.292 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | sharpe -0.31 < 1.0 (x1), max_drawdown 21.0% > 20% (x1), profit_factor 0.99 < 1.5 (x1) |
| `frama` | sharpe 0.80 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | mc_p_value 0.368 > 0.05 (우연 가능성) (x1), mc_p_value 0.316 > 0.05 (우연 가능성) (x1), mc_p_value 0.372 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 1.23 < 1.5 (x1), mc_p_value 0.412 > 0.05 (우연 가능성) (x1), profit_factor 1.41 < 1.5 (x1) |
| `narrow_range` | mc_p_value 0.298 > 0.05 (우연 가능성) (x2), sharpe -1.35 < 1.0 (x1), profit_factor 0.90 < 1.5 (x1) |
| `value_area` | mc_p_value 0.382 > 0.05 (우연 가능성) (x1), mc_p_value 0.392 > 0.05 (우연 가능성) (x1), mc_p_value 0.376 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | sharpe -3.12 < 1.0 (x1), profit_factor 0.67 < 1.5 (x1), mc_p_value 0.664 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | mc_p_value 0.446 > 0.05 (우연 가능성) (x1), mc_p_value 0.478 > 0.05 (우연 가능성) (x1), sharpe 0.18 < 1.0 (x1) |
| `positional_scaling` | sharpe 0.82 < 1.0 (x1), profit_factor 1.21 < 1.5 (x1), mc_p_value 0.494 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | mc_p_value 0.406 > 0.05 (우연 가능성) (x1), profit_factor 1.36 < 1.5 (x1), mc_p_value 0.468 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -0.05 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.512 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe -0.86 < 1.0 (x1), profit_factor 0.82 < 1.5 (x1), mc_p_value 0.524 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| max_drawdown 22.1% > 20% | 3 |
| profit_factor 1.42 < 1.5 | 3 |
| mc_p_value 0.298 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.330 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.368 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.542 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.570 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.40 < 1.5 | 2 |
| mc_p_value 0.372 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.248 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +25.41% -> $12,541
- **Top 5 균등배분**: +52.34% -> $15,234
