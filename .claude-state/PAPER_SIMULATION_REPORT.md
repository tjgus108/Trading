# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-19T20:09:09.828654Z_
_Symbols: BTC/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-19T20:14:16.455163Z_
_Symbol: BTC/USDT_
_Data Source: CSV BTC/USDT 1h (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 23:00:00+00:00 (499일)_
_Walk-Forward: 8개 윈도우 (train=5040, test=1440 candles [1h])_
_Initial Balance: $10,000 USDT | Fee: 0.055%/leg (0.11% round-trip) | Slippage: 0.05%_
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
| 테스트 전략 | 20개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 20개 |
| 평균 수익률 | -3.47% |
| 최고 수익률 | 2.34% (roc_ma_cross) |
| 최저 수익률 | -10.50% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `roc_ma_cross` | +2.34% | 0.16 | 39.5% | 1.22 | 36 | 7.9% | 2/8 | FAIL |
| 2 | `positional_scaling` | +0.41% | -0.40 | 34.5% | 1.08 | 33 | 9.9% | 1/8 | FAIL |
| 3 | `frama` | -0.15% | -0.15 | 39.6% | 1.08 | 38 | 9.1% | 1/8 | FAIL |
| 4 | `order_flow_imbalance_v2` | -0.95% | -0.15 | 38.3% | 1.02 | 59 | 13.0% | 0/8 | FAIL |
| 5 | `price_action_momentum` | -1.28% | -0.31 | 38.1% | 1.04 | 66 | 14.2% | 1/8 | FAIL |
| 6 | `price_cluster` | -1.58% | -0.53 | 37.8% | 1.01 | 39 | 12.3% | 1/8 | FAIL |
| 7 | `dema_cross` | -1.70% | -2.19 | 15.6% | 0.22 | 2 | 2.1% | 0/8 | FAIL |
| 8 | `htf_ema` | -1.86% | -0.27 | 38.5% | 1.00 | 43 | 10.6% | 0/8 | FAIL |
| 9 | `relative_volume` | -1.97% | -0.43 | 37.8% | 1.00 | 57 | 10.8% | 0/8 | FAIL |
| 10 | `volume_breakout` | -2.61% | -0.48 | 36.9% | 0.99 | 62 | 13.5% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `roc_ma_cross` | 72.9 | p100 | 0.16 | 2.67 | 1.22 | 36 | 7.9% | 2/8 | FAIL |
| 2 | `price_action_momentum` | 67.9 | p94 | -0.31 | 2.15 | 1.04 | 66 | 14.2% | 1/8 | FAIL |
| 3 | `order_flow_imbalance_v2` | 66.3 | p89 | -0.15 | 1.43 | 1.02 | 59 | 13.0% | 0/8 | FAIL |
| 4 | `frama` | 64.9 | p84 | -0.15 | 1.85 | 1.08 | 38 | 9.1% | 1/8 | FAIL |
| 5 | `lob_maker` | 64.4 | p78 | -0.27 | 1.46 | 1.00 | 68 | 16.6% | 0/8 | FAIL |
| 6 | `relative_volume` | 62.3 | p73 | -0.43 | 1.83 | 1.00 | 57 | 10.8% | 0/8 | FAIL |
| 7 | `volume_breakout` | 61.7 | p68 | -0.48 | 1.75 | 0.99 | 62 | 13.5% | 0/8 | FAIL |
| 8 | `htf_ema` | 61.3 | p63 | -0.27 | 1.06 | 1.00 | 43 | 10.6% | 0/8 | FAIL |
| 9 | `momentum_quality` | 58.2 | p57 | -0.95 | 1.58 | 0.92 | 65 | 13.3% | 0/8 | FAIL |
| 10 | `positional_scaling` | 57.7 | p52 | -0.40 | 2.81 | 1.08 | 33 | 9.9% | 1/8 | FAIL |
| 11 | `cmf` | 57.6 | p47 | -0.63 | 1.93 | 0.97 | 59 | 14.0% | 0/8 | FAIL |
| 12 | `price_cluster` | 57.5 | p42 | -0.53 | 2.21 | 1.01 | 39 | 12.3% | 1/8 | FAIL |
| 13 | `acceleration_band` | 50.9 | p36 | -1.10 | 2.39 | 0.95 | 42 | 13.1% | 1/8 | FAIL |
| 14 | `narrow_range` | 43.0 | p31 | -1.49 | 1.63 | 0.83 | 42 | 13.0% | 0/8 | FAIL |
| 15 | `engulfing_zone` | 40.7 | p26 | -1.20 | 1.73 | 0.85 | 25 | 9.1% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `roc_ma_cross` | +2.34% | 0.16 | 1.22 | 36 | 2/8 | FAIL |
| `positional_scaling` | +0.41% | -0.40 | 1.08 | 33 | 1/8 | FAIL |
| `frama` | -0.15% | -0.15 | 1.08 | 38 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | -0.95% | -0.15 | 1.02 | 59 | 0/8 | FAIL |
| `price_action_momentum` | -1.28% | -0.31 | 1.04 | 66 | 1/8 | FAIL |
| `price_cluster` | -1.58% | -0.53 | 1.01 | 39 | 1/8 | FAIL |
| `dema_cross` | -1.70% | -2.19 | 0.22 | 2 | 0/8 | FAIL |
| `htf_ema` | -1.86% | -0.27 | 1.00 | 43 | 0/8 | FAIL |
| `relative_volume` | -1.97% | -0.43 | 1.00 | 57 | 0/8 | FAIL |
| `volume_breakout` | -2.61% | -0.48 | 0.99 | 62 | 0/8 | FAIL |
| `lob_maker` | -2.62% | -0.27 | 1.00 | 68 | 0/8 | FAIL |
| `cmf` | -3.53% | -0.63 | 0.97 | 59 | 0/8 | FAIL |
| `engulfing_zone` | -4.28% | -1.20 | 0.85 | 25 | 0/8 | FAIL |
| `acceleration_band` | -4.55% | -1.10 | 0.95 | 42 | 1/8 | FAIL |
| `momentum_quality` | -5.36% | -0.95 | 0.92 | 65 | 0/8 | FAIL |
| `linear_channel_rev` | -5.81% | -2.36 | 0.68 | 26 | 0/8 | FAIL |
| `narrow_range` | -6.61% | -1.49 | 0.83 | 42 | 0/8 | FAIL |
| `volatility_cluster` | -8.17% | -2.06 | 0.79 | 51 | 0/8 | FAIL |
| `elder_impulse` | -8.64% | -2.04 | 0.73 | 39 | 0/8 | FAIL |
| `wick_reversal` | -10.50% | -3.20 | 0.63 | 38 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `roc_ma_cross` | sharpe 0.34 < 1.0 (x1), profit_factor 1.09 < 1.5 (x1), mc_p_value 0.432 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 0.41 < 1.5 (x2), mc_p_value 0.990 > 0.1 (우연 가능성) (x2), mc_p_value 0.130 > 0.1 (우연 가능성) (x1) |
| `frama` | sharpe 0.03 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1), mc_p_value 0.448 > 0.1 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe -0.81 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1), mc_p_value 0.608 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | profit_factor 1.38 < 1.5 (x1), mc_p_value 0.122 > 0.1 (우연 가능성) (x1), sharpe -0.53 < 1.0 (x1) |
| `price_cluster` | sharpe -1.21 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1), mc_p_value 0.738 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x5), trades 2 < 15 (x4), trades 4 < 15 (x2) |
| `htf_ema` | sharpe 0.05 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1), mc_p_value 0.489 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | profit_factor 1.08 < 1.5 (x2), sharpe 0.35 < 1.0 (x1), mc_p_value 0.371 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -1.02 < 1.0 (x1), max_drawdown 21.3% > 20% (x1), profit_factor 0.90 < 1.5 (x1) |
| `lob_maker` | sharpe -0.15 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.481 > 0.1 (우연 가능성) (x1) |
| `cmf` | sharpe -0.25 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1), mc_p_value 0.524 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -1.84 < 1.0 (x1), profit_factor 0.70 < 1.5 (x1), mc_p_value 0.800 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.40 < 1.5 (x1), mc_p_value 0.187 > 0.1 (우연 가능성) (x1), sharpe -1.73 < 1.0 (x1) |
| `momentum_quality` | sharpe 0.62 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), mc_p_value 0.338 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | profit_factor 0.39 < 1.5 (x2), sharpe -0.56 < 1.0 (x2), profit_factor 0.90 < 1.5 (x2) |
| `narrow_range` | sharpe -2.06 < 1.0 (x1), profit_factor 0.73 < 1.5 (x1), mc_p_value 0.846 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -0.94 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.622 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -0.94 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.641 > 0.1 (우연 가능성) (x1) |
| `wick_reversal` | profit_factor 0.45 < 1.5 (x3), sharpe -2.94 < 1.0 (x1), profit_factor 0.61 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.70 < 1.5 | 5 |
| profit_factor 1.03 < 1.5 | 5 |
| profit_factor 0.00 < 1.5 | 5 |
| profit_factor 1.09 < 1.5 | 4 |
| profit_factor 1.13 < 1.5 | 4 |
| profit_factor 0.86 < 1.5 | 4 |
| profit_factor 1.08 < 1.5 | 4 |
| profit_factor 0.81 < 1.5 | 4 |
| trades 2 < 15 | 4 |
| mc_p_value 0.990 > 0.1 (우연 가능성) | 3 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 3 | 17 | 85.0% |
| `frama` | 0 | 249 | 54 | 17.8% |
| `htf_ema` | 0 | 288 | 58 | 16.8% |
| `price_action_momentum` | 0 | 441 | 88 | 16.6% |
| `cmf` | 0 | 399 | 71 | 15.1% |
| `lob_maker` | 0 | 462 | 82 | 15.1% |
| `volume_breakout` | 0 | 422 | 74 | 14.9% |
| `linear_channel_rev` | 0 | 177 | 30 | 14.5% |
| `relative_volume` | 0 | 390 | 64 | 14.1% |
| `positional_scaling` | 0 | 227 | 36 | 13.7% |

## 포트폴리오 가상 배분

- **전체 20개 균등배분**: -3.47% -> $9,653
- **Top 5 균등배분**: +0.07% -> $10,007
