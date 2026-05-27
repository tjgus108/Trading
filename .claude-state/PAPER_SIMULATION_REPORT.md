# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-27T22:47:13.717567Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-27T22:54:34.163570Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1130151531, block=36)_
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
| 평균 수익률 | 11.49% |
| 최고 수익률 | 50.31% (price_action_momentum) |
| 최저 수익률 | -2.43% (cmf) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +50.31% | 3.69 | 43.8% | 1.46 | 148 | 13.0% | 0/4 | FAIL |
| 2 | `narrow_range` | +36.82% | 4.13 | 50.2% | 1.80 | 80 | 11.1% | 0/4 | FAIL |
| 3 | `momentum_quality` | +35.10% | 3.46 | 44.8% | 1.53 | 108 | 9.7% | 0/4 | FAIL |
| 4 | `acceleration_band` | +30.41% | 2.66 | 42.6% | 1.37 | 99 | 14.9% | 0/4 | FAIL |
| 5 | `frama` | +30.24% | 2.97 | 45.2% | 1.45 | 84 | 8.8% | 0/4 | FAIL |
| 6 | `supertrend_multi` | +17.17% | 1.75 | 39.8% | 1.24 | 123 | 15.0% | 0/4 | FAIL |
| 7 | `lob_maker` | +12.38% | 1.12 | 38.9% | 1.14 | 127 | 21.2% | 0/4 | FAIL |
| 8 | `volume_breakout` | +10.56% | 0.83 | 36.9% | 1.16 | 100 | 22.0% | 0/4 | FAIL |
| 9 | `volatility_cluster` | +9.56% | 1.37 | 41.7% | 1.24 | 79 | 11.8% | 0/4 | FAIL |
| 10 | `price_cluster` | +6.58% | 1.07 | 40.6% | 1.22 | 42 | 10.3% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `narrow_range` | 76.0 | p100 | 4.13 | 1.77 | 1.80 | 80 | 11.1% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 74.5 | p95 | 3.69 | 1.94 | 1.46 | 148 | 13.0% | 0/4 | FAIL |
| 3 | `momentum_quality` | 72.2 | p90 | 3.46 | 1.81 | 1.53 | 108 | 9.7% | 0/4 | FAIL |
| 4 | `frama` | 68.5 | p85 | 2.97 | 0.99 | 1.45 | 84 | 8.8% | 0/4 | FAIL |
| 5 | `acceleration_band` | 60.6 | p80 | 2.66 | 1.87 | 1.37 | 99 | 14.9% | 0/4 | FAIL |
| 6 | `dema_cross` | 59.9 | p76 | 1.73 | 0.86 | 1.73 | 16 | 4.3% | 0/4 | FAIL |
| 7 | `supertrend_multi` | 55.7 | p71 | 1.75 | 1.83 | 1.24 | 123 | 15.0% | 0/4 | FAIL |
| 8 | `volatility_cluster` | 51.4 | p66 | 1.37 | 1.64 | 1.24 | 79 | 11.8% | 0/4 | FAIL |
| 9 | `roc_ma_cross` | 50.7 | p61 | 1.17 | 1.26 | 1.26 | 41 | 7.0% | 0/4 | FAIL |
| 10 | `price_cluster` | 50.5 | p57 | 1.07 | 0.12 | 1.22 | 42 | 10.3% | 0/4 | FAIL |
| 11 | `value_area` | 49.2 | p52 | 0.86 | 0.62 | 1.24 | 24 | 5.8% | 0/4 | FAIL |
| 12 | `lob_maker` | 49.0 | p47 | 1.12 | 0.98 | 1.14 | 127 | 21.2% | 0/4 | FAIL |
| 13 | `engulfing_zone` | 46.1 | p42 | 0.69 | 0.83 | 1.22 | 24 | 7.7% | 0/4 | FAIL |
| 14 | `cmf` | 40.2 | p38 | -0.02 | 0.67 | 1.02 | 120 | 21.2% | 0/4 | FAIL |
| 15 | `volume_breakout` | 40.0 | p33 | 0.83 | 2.49 | 1.16 | 100 | 22.0% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +50.31% | 3.69 | 1.46 | 148 | 0/4 | FAIL |
| `narrow_range` | +36.82% | 4.13 | 1.80 | 80 | 0/4 | FAIL |
| `momentum_quality` | +35.10% | 3.46 | 1.53 | 108 | 0/4 | FAIL |
| `acceleration_band` | +30.41% | 2.66 | 1.37 | 99 | 0/4 | FAIL |
| `frama` | +30.24% | 2.97 | 1.45 | 84 | 0/4 | FAIL |
| `supertrend_multi` | +17.17% | 1.75 | 1.24 | 123 | 0/4 | FAIL |
| `lob_maker` | +12.38% | 1.12 | 1.14 | 127 | 0/4 | FAIL |
| `volume_breakout` | +10.56% | 0.83 | 1.16 | 100 | 0/4 | FAIL |
| `volatility_cluster` | +9.56% | 1.37 | 1.24 | 79 | 0/4 | FAIL |
| `price_cluster` | +6.58% | 1.07 | 1.22 | 42 | 0/4 | FAIL |
| `roc_ma_cross` | +5.75% | 1.17 | 1.26 | 41 | 0/4 | FAIL |
| `dema_cross` | +5.21% | 1.73 | 1.73 | 16 | 0/4 | FAIL |
| `value_area` | +3.02% | 0.86 | 1.24 | 24 | 0/4 | FAIL |
| `engulfing_zone` | +3.00% | 0.69 | 1.22 | 24 | 0/4 | FAIL |
| `htf_ema` | +1.03% | 0.25 | 1.07 | 76 | 0/4 | FAIL |
| `relative_volume` | +0.78% | -0.34 | 1.14 | 66 | 0/4 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `elder_impulse` | -0.07% | 0.10 | 1.06 | 60 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | -0.34% | -0.17 | 1.01 | 87 | 0/4 | FAIL |
| `positional_scaling` | -1.07% | -0.20 | 1.01 | 34 | 0/4 | FAIL |
| `linear_channel_rev` | -1.15% | -0.43 | 1.01 | 29 | 0/4 | FAIL |
| `cmf` | -2.43% | -0.02 | 1.02 | 120 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.214 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1), mc_p_value 0.274 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.440 > 0.05 (우연 가능성) (x1), mc_p_value 0.328 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 1.36 < 1.5 (x1), mc_p_value 0.380 > 0.05 (우연 가능성) (x1), profit_factor 1.31 < 1.5 (x1) |
| `acceleration_band` | mc_p_value 0.336 > 0.05 (우연 가능성) (x2), sharpe 1.00 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1) |
| `frama` | mc_p_value 0.320 > 0.05 (우연 가능성) (x1), mc_p_value 0.372 > 0.05 (우연 가능성) (x1), profit_factor 1.31 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.420 > 0.05 (우연 가능성) (x1), profit_factor 1.22 < 1.5 (x1) |
| `lob_maker` | max_drawdown 20.8% > 20% (x1), profit_factor 1.20 < 1.5 (x1), mc_p_value 0.396 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | mc_p_value 0.330 > 0.05 (우연 가능성) (x1), sharpe 0.96 < 1.0 (x1), max_drawdown 25.8% > 20% (x1) |
| `volatility_cluster` | profit_factor 1.44 < 1.5 (x1), mc_p_value 0.406 > 0.05 (우연 가능성) (x1), profit_factor 1.17 < 1.5 (x1) |
| `price_cluster` | profit_factor 1.19 < 1.5 (x2), sharpe 0.92 < 1.0 (x1), mc_p_value 0.432 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 1.47 < 1.5 (x1), mc_p_value 0.442 > 0.05 (우연 가능성) (x1), mc_p_value 0.404 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | profit_factor 1.48 < 1.5 (x2), trades 10 < 15 (x1), mc_p_value 0.418 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe 0.56 < 1.0 (x1), profit_factor 1.16 < 1.5 (x1), mc_p_value 0.502 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | mc_p_value 0.480 > 0.05 (우연 가능성) (x2), profit_factor 1.50 < 1.5 (x1), mc_p_value 0.500 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | sharpe 0.11 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1), mc_p_value 0.498 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | mc_p_value 0.362 > 0.05 (우연 가능성) (x1), sharpe -0.58 < 1.0 (x1), max_drawdown 24.5% > 20% (x1) |
| `wick_reversal` | no trades generated (x4) |
| `elder_impulse` | sharpe -0.07 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.502 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.504 > 0.05 (우연 가능성) (x2), profit_factor 1.28 < 1.5 (x1), mc_p_value 0.404 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | sharpe -1.16 < 1.0 (x1), profit_factor 0.82 < 1.5 (x1), mc_p_value 0.530 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.440 > 0.05 (우연 가능성) | 4 |
| profit_factor 1.28 < 1.5 | 4 |
| profit_factor 1.04 < 1.5 | 4 |
| no trades generated | 4 |
| mc_p_value 0.460 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.46 < 1.5 | 3 |
| profit_factor 1.12 < 1.5 | 3 |
| profit_factor 1.19 < 1.5 | 3 |
| mc_p_value 0.480 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.274 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +11.49% -> $11,149
- **Top 5 균등배분**: +36.58% -> $13,658
