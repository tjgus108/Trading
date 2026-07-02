# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-07-02T20:53:56.538831Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-07-02T20:57:43.688312Z_
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
| 테스트 전략 | 19개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 19개 |
| 평균 수익률 | -2.71% |
| 최고 수익률 | 6.13% (roc_ma_cross) |
| 최저 수익률 | -8.04% (volatility_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `roc_ma_cross` | +6.13% | 1.75 | 45.8% | 1.97 | 14 | 3.2% | 2/8 | FAIL |
| 2 | `dema_cross` | +3.08% | 0.85 | 39.4% | 1.38 | 26 | 6.1% | 2/8 | FAIL |
| 3 | `frama` | +1.60% | 0.24 | 35.2% | 1.12 | 40 | 9.4% | 1/8 | FAIL |
| 4 | `positional_scaling` | +0.27% | -0.38 | 33.7% | 1.09 | 34 | 9.2% | 1/8 | FAIL |
| 5 | `lob_maker` | +0.15% | -0.04 | 35.0% | 1.05 | 75 | 17.0% | 0/8 | FAIL |
| 6 | `price_cluster` | -0.36% | -0.52 | 0.0% | 0.00 | 0 | 0.4% | 0/8 | FAIL |
| 7 | `narrow_range` | -2.27% | -0.51 | 33.5% | 0.97 | 46 | 10.1% | 0/8 | FAIL |
| 8 | `acceleration_band` | -3.18% | -0.94 | 32.0% | 0.98 | 44 | 13.0% | 1/8 | FAIL |
| 9 | `volume_breakout` | -3.33% | -0.74 | 32.5% | 0.96 | 72 | 15.4% | 0/8 | FAIL |
| 10 | `momentum_quality` | -3.34% | -1.19 | 31.5% | 0.96 | 71 | 15.8% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `roc_ma_cross` | 66.2 | p100 | 1.75 | 1.73 | 1.97 | 14 | 3.2% | 2/8 | FAIL |
| 2 | `dema_cross` | 58.5 | p94 | 0.85 | 1.85 | 1.38 | 26 | 6.1% | 2/8 | FAIL |
| 3 | `frama` | 51.5 | p88 | 0.24 | 1.60 | 1.12 | 40 | 9.4% | 1/8 | FAIL |
| 4 | `lob_maker` | 48.6 | p83 | -0.04 | 1.99 | 1.05 | 75 | 17.0% | 0/8 | FAIL |
| 5 | `volume_breakout` | 42.8 | p77 | -0.74 | 2.18 | 0.96 | 72 | 15.4% | 0/8 | FAIL |
| 6 | `price_action_momentum` | 42.6 | p72 | -1.08 | 2.79 | 0.97 | 73 | 16.7% | 1/8 | FAIL |
| 7 | `positional_scaling` | 42.4 | p66 | -0.38 | 2.82 | 1.09 | 34 | 9.2% | 1/8 | FAIL |
| 8 | `order_flow_imbalance_v2` | 42.0 | p61 | -0.77 | 2.05 | 0.95 | 67 | 15.0% | 0/8 | FAIL |
| 9 | `relative_volume` | 41.9 | p55 | -0.99 | 1.72 | 0.92 | 64 | 13.2% | 0/8 | FAIL |
| 10 | `narrow_range` | 41.8 | p50 | -0.51 | 1.48 | 0.97 | 46 | 10.1% | 0/8 | FAIL |
| 11 | `momentum_quality` | 40.0 | p44 | -1.19 | 3.29 | 0.96 | 71 | 15.8% | 1/8 | FAIL |
| 12 | `htf_ema` | 39.9 | p33 | -0.72 | 0.71 | 0.91 | 43 | 11.2% | 0/8 | FAIL |
| 13 | `cmf` | 39.9 | p38 | -1.23 | 1.29 | 0.88 | 68 | 16.3% | 0/8 | FAIL |
| 14 | `acceleration_band` | 39.2 | p27 | -0.94 | 2.58 | 0.98 | 44 | 13.0% | 1/8 | FAIL |
| 15 | `elder_impulse` | 34.8 | p22 | -1.15 | 1.14 | 0.85 | 42 | 11.5% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `roc_ma_cross` | +6.13% | 1.75 | 1.97 | 14 | 2/8 | FAIL |
| `dema_cross` | +3.08% | 0.85 | 1.38 | 26 | 2/8 | FAIL |
| `frama` | +1.60% | 0.24 | 1.12 | 40 | 1/8 | FAIL |
| `positional_scaling` | +0.27% | -0.38 | 1.09 | 34 | 1/8 | FAIL |
| `lob_maker` | +0.15% | -0.04 | 1.05 | 75 | 0/8 | FAIL |
| `price_cluster` | -0.36% | -0.52 | 0.00 | 0 | 0/8 | FAIL |
| `narrow_range` | -2.27% | -0.51 | 0.97 | 46 | 0/8 | FAIL |
| `acceleration_band` | -3.18% | -0.94 | 0.98 | 44 | 1/8 | FAIL |
| `volume_breakout` | -3.33% | -0.74 | 0.96 | 72 | 0/8 | FAIL |
| `momentum_quality` | -3.34% | -1.19 | 0.96 | 71 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | -3.82% | -0.77 | 0.95 | 67 | 0/8 | FAIL |
| `htf_ema` | -3.97% | -0.72 | 0.91 | 43 | 0/8 | FAIL |
| `price_action_momentum` | -4.71% | -1.08 | 0.97 | 73 | 1/8 | FAIL |
| `relative_volume` | -4.86% | -0.99 | 0.92 | 64 | 0/8 | FAIL |
| `elder_impulse` | -4.92% | -1.15 | 0.85 | 42 | 0/8 | FAIL |
| `linear_channel_rev` | -5.84% | -2.69 | 0.65 | 28 | 0/8 | FAIL |
| `engulfing_zone` | -6.31% | -1.64 | 0.72 | 25 | 0/8 | FAIL |
| `cmf` | -7.81% | -1.23 | 0.88 | 68 | 0/8 | FAIL |
| `volatility_cluster` | -8.04% | -2.09 | 0.81 | 54 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `roc_ma_cross` | profit_factor 1.50 < 1.5 (x1), trades 14 < 15 (x1), sharpe 0.73 < 1.0 (x1) |
| `dema_cross` | sharpe 0.63 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.366 > 0.1 (우연 가능성) (x1) |
| `frama` | sharpe -0.87 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1), mc_p_value 0.603 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.163 > 0.1 (우연 가능성) (x1), sharpe -1.16 < 1.0 (x1) |
| `lob_maker` | sharpe -2.32 < 1.0 (x1), max_drawdown 27.9% > 20% (x1), profit_factor 0.79 < 1.5 (x1) |
| `price_cluster` | no trades generated (x6), sharpe -2.07 < 1.0 (x2), profit_factor 0.00 < 1.5 (x2) |
| `narrow_range` | profit_factor 1.29 < 1.5 (x1), mc_p_value 0.227 > 0.1 (우연 가능성) (x1), sharpe 0.18 < 1.0 (x1) |
| `acceleration_band` | profit_factor 0.89 < 1.5 (x2), profit_factor 1.40 < 1.5 (x1), mc_p_value 0.189 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | max_drawdown 22.1% > 20% (x2), sharpe -0.15 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1) |
| `momentum_quality` | profit_factor 0.57 < 1.5 (x2), profit_factor 1.37 < 1.5 (x1), sharpe -0.54 < 1.0 (x1) |
| `order_flow_imbalance_v2` | profit_factor 0.77 < 1.5 (x2), profit_factor 1.24 < 1.5 (x1), mc_p_value 0.219 > 0.1 (우연 가능성) (x1) |
| `htf_ema` | sharpe -0.42 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1), mc_p_value 0.572 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe 0.59 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1), mc_p_value 0.370 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | sharpe 0.23 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.413 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -0.53 < 1.0 (x1), profit_factor 0.94 < 1.5 (x1), mc_p_value 0.572 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe 0.42 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), mc_p_value 0.383 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -2.15 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1), mc_p_value 0.828 > 0.1 (우연 가능성) (x1) |
| `cmf` | sharpe -0.11 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1), mc_p_value 0.486 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.03 < 1.5 (x2), mc_p_value 0.999 > 0.1 (우연 가능성) (x2), sharpe -0.84 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 6 |
| profit_factor 0.74 < 1.5 | 5 |
| profit_factor 1.03 < 1.5 | 4 |
| profit_factor 0.83 < 1.5 | 4 |
| profit_factor 0.91 < 1.5 | 4 |
| profit_factor 1.06 < 1.5 | 4 |
| profit_factor 0.57 < 1.5 | 3 |
| profit_factor 0.87 < 1.5 | 3 |
| profit_factor 0.84 < 1.5 | 3 |
| profit_factor 0.95 < 1.5 | 3 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `momentum_quality` | 173 | 89 | 0.51 |
| `volatility_cluster` | 137 | 77 | 0.56 |
| `volume_breakout` | 188 | 73 | 0.39 |
| `linear_channel_rev` | 57 | 72 | 1.26 |
| `price_action_momentum` | 188 | 62 | 0.33 |
| `elder_impulse` | 107 | 61 | 0.57 |
| `cmf` | 189 | 57 | 0.30 |
| `lob_maker` | 198 | 55 | 0.28 |
| `acceleration_band` | 106 | 52 | 0.49 |
| `relative_volume` | 180 | 46 | 0.26 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `relative_volume` | 0 | 507 | 8 | 1.6% |
| `dema_cross` | 0 | 207 | 2 | 1.0% |
| `linear_channel_rev` | 0 | 225 | 2 | 0.9% |
| `order_flow_imbalance_v2` | 0 | 532 | 4 | 0.7% |
| `positional_scaling` | 0 | 267 | 2 | 0.7% |
| `cmf` | 0 | 536 | 4 | 0.7% |
| `momentum_quality` | 0 | 562 | 4 | 0.7% |
| `price_action_momentum` | 0 | 582 | 4 | 0.7% |
| `frama` | 0 | 321 | 2 | 0.6% |
| `volatility_cluster` | 0 | 432 | 2 | 0.5% |

## 포트폴리오 가상 배분

- **전체 19개 균등배분**: -2.71% -> $9,729
- **Top 5 균등배분**: +2.25% -> $10,225


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-07-02T21:01:15.256450Z_
_Symbol: ETH/USDT_
_Data Source: CSV ETH/USDT 1h (/home/user/Trading/data/historical)_
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
| 테스트 전략 | 19개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 19개 |
| 평균 수익률 | -5.32% |
| 최고 수익률 | 3.50% (engulfing_zone) |
| 최저 수익률 | -12.67% (narrow_range) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `engulfing_zone` | +3.50% | 0.44 | 40.3% | 1.30 | 24 | 7.0% | 2/8 | FAIL |
| 2 | `frama` | +2.83% | 0.51 | 38.5% | 1.18 | 33 | 8.4% | 1/8 | FAIL |
| 3 | `price_cluster` | -0.52% | -0.78 | 12.5% | 125.00 | 1 | 0.6% | 0/8 | FAIL |
| 4 | `roc_ma_cross` | -1.54% | -0.93 | 32.7% | 0.86 | 8 | 4.1% | 0/8 | FAIL |
| 5 | `order_flow_imbalance_v2` | -4.32% | -1.02 | 33.8% | 0.94 | 55 | 14.5% | 0/8 | FAIL |
| 6 | `acceleration_band` | -4.40% | -2.03 | 25.1% | 0.57 | 13 | 6.0% | 0/8 | FAIL |
| 7 | `volume_breakout` | -4.47% | -0.87 | 34.4% | 0.91 | 61 | 12.5% | 0/8 | FAIL |
| 8 | `lob_maker` | -5.02% | -0.90 | 33.6% | 0.92 | 58 | 15.6% | 0/8 | FAIL |
| 9 | `cmf` | -5.13% | -1.14 | 31.4% | 0.85 | 46 | 11.8% | 0/8 | FAIL |
| 10 | `dema_cross` | -5.20% | -2.46 | 26.0% | 0.61 | 20 | 7.9% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `frama` | 50.1 | p100 | 0.51 | 1.55 | 1.18 | 33 | 8.4% | 1/8 | FAIL |
| 2 | `engulfing_zone` | 48.8 | p94 | 0.44 | 2.56 | 1.30 | 24 | 7.0% | 2/8 | FAIL |
| 3 | `volume_breakout` | 44.8 | p88 | -0.87 | 1.49 | 0.91 | 61 | 12.5% | 0/8 | FAIL |
| 4 | `lob_maker` | 38.4 | p83 | -0.90 | 1.82 | 0.92 | 58 | 15.6% | 0/8 | FAIL |
| 5 | `cmf` | 37.6 | p77 | -1.14 | 1.40 | 0.85 | 46 | 11.8% | 0/8 | FAIL |
| 6 | `volatility_cluster` | 35.1 | p72 | -1.49 | 1.44 | 0.81 | 42 | 9.4% | 0/8 | FAIL |
| 7 | `order_flow_imbalance_v2` | 34.2 | p66 | -1.02 | 2.50 | 0.94 | 55 | 14.5% | 0/8 | FAIL |
| 8 | `momentum_quality` | 33.6 | p61 | -2.48 | 0.88 | 0.71 | 58 | 14.5% | 0/8 | FAIL |
| 9 | `elder_impulse` | 33.1 | p55 | -1.60 | 0.86 | 0.76 | 36 | 10.7% | 0/8 | FAIL |
| 10 | `relative_volume` | 33.0 | p50 | -1.53 | 2.34 | 0.87 | 54 | 12.7% | 0/8 | FAIL |
| 11 | `price_action_momentum` | 29.1 | p44 | -2.32 | 1.51 | 0.71 | 48 | 12.6% | 0/8 | FAIL |
| 12 | `roc_ma_cross` | 24.3 | p38 | -0.93 | 1.47 | 0.86 | 8 | 4.1% | 0/8 | FAIL |
| 13 | `linear_channel_rev` | 21.9 | p33 | -2.33 | 1.19 | 0.60 | 23 | 7.9% | 0/8 | FAIL |
| 14 | `htf_ema` | 20.4 | p27 | -2.83 | 0.81 | 0.56 | 29 | 12.1% | 0/8 | FAIL |
| 15 | `price_cluster` | 20.2 | p22 | -0.78 | 1.41 | 125.00 | 1 | 0.6% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `engulfing_zone` | +3.50% | 0.44 | 1.30 | 24 | 2/8 | FAIL |
| `frama` | +2.83% | 0.51 | 1.18 | 33 | 1/8 | FAIL |
| `price_cluster` | -0.52% | -0.78 | 125.00 | 1 | 0/8 | FAIL |
| `roc_ma_cross` | -1.54% | -0.93 | 0.86 | 8 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -4.32% | -1.02 | 0.94 | 55 | 0/8 | FAIL |
| `acceleration_band` | -4.40% | -2.03 | 0.57 | 13 | 0/8 | FAIL |
| `volume_breakout` | -4.47% | -0.87 | 0.91 | 61 | 0/8 | FAIL |
| `lob_maker` | -5.02% | -0.90 | 0.92 | 58 | 0/8 | FAIL |
| `cmf` | -5.13% | -1.14 | 0.85 | 46 | 0/8 | FAIL |
| `dema_cross` | -5.20% | -2.46 | 0.61 | 20 | 0/8 | FAIL |
| `volatility_cluster` | -5.39% | -1.49 | 0.81 | 42 | 0/8 | FAIL |
| `linear_channel_rev` | -5.71% | -2.33 | 0.60 | 23 | 0/8 | FAIL |
| `relative_volume` | -5.75% | -1.53 | 0.87 | 54 | 0/8 | FAIL |
| `elder_impulse` | -6.28% | -1.60 | 0.76 | 36 | 0/8 | FAIL |
| `price_action_momentum` | -9.19% | -2.32 | 0.71 | 48 | 0/8 | FAIL |
| `htf_ema` | -9.34% | -2.83 | 0.56 | 29 | 0/8 | FAIL |
| `momentum_quality` | -11.04% | -2.48 | 0.71 | 58 | 0/8 | FAIL |
| `positional_scaling` | -11.48% | -3.81 | 0.47 | 33 | 0/8 | FAIL |
| `narrow_range` | -12.67% | -3.72 | 0.53 | 40 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `engulfing_zone` | sharpe -4.16 < 1.0 (x1), profit_factor 0.38 < 1.5 (x1), mc_p_value 0.976 > 0.1 (우연 가능성) (x1) |
| `frama` | profit_factor 0.75 < 1.5 (x2), sharpe -1.37 < 1.0 (x1), mc_p_value 0.751 > 0.1 (우연 가능성) (x1) |
| `price_cluster` | trades 1 < 15 (x5), profit_factor 0.00 < 1.5 (x4), no trades generated (x3) |
| `roc_ma_cross` | trades 8 < 15 (x2), trades 7 < 15 (x2), sharpe -1.77 < 1.0 (x1) |
| `order_flow_imbalance_v2` | sharpe 0.82 < 1.0 (x1), profit_factor 1.16 < 1.5 (x1), mc_p_value 0.301 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | trades 12 < 15 (x2), sharpe -1.18 < 1.0 (x1), profit_factor 0.69 < 1.5 (x1) |
| `volume_breakout` | sharpe -1.34 < 1.0 (x2), profit_factor 0.83 < 1.5 (x2), mc_p_value 0.738 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | sharpe -2.97 < 1.0 (x1), max_drawdown 22.6% > 20% (x1), profit_factor 0.65 < 1.5 (x1) |
| `cmf` | sharpe -0.77 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1), mc_p_value 0.640 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | mc_p_value 0.916 > 0.1 (우연 가능성) (x2), sharpe -2.83 < 1.0 (x1), profit_factor 0.45 < 1.5 (x1) |
| `volatility_cluster` | sharpe -0.04 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1), mc_p_value 0.499 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | profit_factor 0.74 < 1.5 (x2), sharpe -1.95 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1) |
| `relative_volume` | sharpe -3.30 < 1.0 (x1), profit_factor 0.62 < 1.5 (x1), mc_p_value 0.940 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -1.74 < 1.0 (x1), profit_factor 0.74 < 1.5 (x1), mc_p_value 0.760 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe -1.47 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1), mc_p_value 0.751 > 0.1 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 0.51 < 1.5 (x2), sharpe -3.85 < 1.0 (x1), mc_p_value 0.978 > 0.1 (우연 가능성) (x1) |
| `momentum_quality` | sharpe -1.45 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1), mc_p_value 0.732 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 0.46 < 1.5 (x2), sharpe -4.46 < 1.0 (x1), profit_factor 0.35 < 1.5 (x1) |
| `narrow_range` | sharpe -1.32 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1), mc_p_value 0.716 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.57 < 1.5 | 5 |
| trades 1 < 15 | 5 |
| profit_factor 0.73 < 1.5 | 4 |
| profit_factor 0.75 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 0.69 < 1.5 | 4 |
| profit_factor 0.70 < 1.5 | 4 |
| profit_factor 0.59 < 1.5 | 4 |
| profit_factor 0.51 < 1.5 | 4 |
| profit_factor 1.00 < 1.5 | 3 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `order_flow_imbalance_v2` | 130 | 68 | 0.52 |
| `narrow_range` | 106 | 64 | 0.60 |
| `momentum_quality` | 158 | 59 | 0.37 |
| `volume_breakout` | 146 | 58 | 0.40 |
| `positional_scaling` | 88 | 56 | 0.64 |
| `relative_volume` | 132 | 55 | 0.42 |
| `lob_maker` | 146 | 53 | 0.36 |
| `cmf` | 117 | 53 | 0.45 |
| `price_action_momentum` | 124 | 49 | 0.40 |
| `volatility_cluster` | 91 | 45 | 0.49 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 75 | 88 | 54.0% |
| `frama` | 0 | 140 | 124 | 47.0% |
| `acceleration_band` | 0 | 67 | 40 | 37.4% |
| `price_action_momentum` | 0 | 250 | 132 | 34.6% |
| `cmf` | 0 | 240 | 125 | 34.2% |
| `positional_scaling` | 0 | 172 | 89 | 34.1% |
| `volatility_cluster` | 0 | 228 | 109 | 32.3% |
| `roc_ma_cross` | 0 | 45 | 21 | 31.8% |
| `engulfing_zone` | 0 | 132 | 60 | 31.2% |
| `relative_volume` | 0 | 302 | 134 | 30.7% |

## 포트폴리오 가상 배분

- **전체 19개 균등배분**: -5.32% -> $9,468
- **Top 5 균등배분**: -0.01% -> $9,999


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-07-02T21:04:38.067533Z_
_Symbol: SOL/USDT_
_Data Source: CSV SOL/USDT 1h (/home/user/Trading/data/historical)_
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
| 테스트 전략 | 19개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 19개 |
| 평균 수익률 | -4.05% |
| 최고 수익률 | 4.81% (engulfing_zone) |
| 최저 수익률 | -8.13% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `engulfing_zone` | +4.81% | 0.78 | 38.3% | 1.33 | 26 | 7.0% | 1/8 | FAIL |
| 2 | `price_cluster` | +0.42% | -0.01 | 25.0% | 250.00 | 0 | 0.4% | 0/8 | FAIL |
| 3 | `volatility_cluster` | -0.64% | -0.12 | 36.9% | 1.02 | 41 | 8.7% | 0/8 | FAIL |
| 4 | `acceleration_band` | -1.44% | -0.80 | 35.6% | 1.00 | 11 | 4.7% | 0/8 | FAIL |
| 5 | `roc_ma_cross` | -1.87% | -0.94 | 32.2% | 0.85 | 11 | 5.2% | 0/8 | FAIL |
| 6 | `relative_volume` | -2.03% | -0.61 | 34.2% | 0.97 | 50 | 10.7% | 0/8 | FAIL |
| 7 | `positional_scaling` | -3.18% | -1.12 | 33.1% | 0.87 | 32 | 8.8% | 0/8 | FAIL |
| 8 | `htf_ema` | -4.40% | -1.45 | 30.6% | 0.80 | 30 | 9.0% | 0/8 | FAIL |
| 9 | `lob_maker` | -4.59% | -0.73 | 34.3% | 0.90 | 56 | 13.0% | 0/8 | FAIL |
| 10 | `elder_impulse` | -4.87% | -1.91 | 29.0% | 0.82 | 36 | 11.6% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `engulfing_zone` | 52.0 | p100 | 0.78 | 2.10 | 1.33 | 26 | 7.0% | 1/8 | FAIL |
| 2 | `volatility_cluster` | 42.3 | p94 | -0.12 | 1.16 | 1.02 | 41 | 8.7% | 0/8 | FAIL |
| 3 | `lob_maker` | 40.3 | p88 | -0.73 | 0.95 | 0.90 | 56 | 13.0% | 0/8 | FAIL |
| 4 | `momentum_quality` | 38.5 | p83 | -1.18 | 0.96 | 0.85 | 56 | 10.5% | 0/8 | FAIL |
| 5 | `relative_volume` | 36.8 | p77 | -0.61 | 2.05 | 0.97 | 50 | 10.7% | 0/8 | FAIL |
| 6 | `order_flow_imbalance_v2` | 36.8 | p72 | -1.22 | 0.78 | 0.84 | 55 | 12.0% | 0/8 | FAIL |
| 7 | `cmf` | 32.0 | p66 | -1.28 | 0.94 | 0.82 | 44 | 10.3% | 0/8 | FAIL |
| 8 | `volume_breakout` | 31.6 | p61 | -1.45 | 1.33 | 0.82 | 58 | 14.2% | 0/8 | FAIL |
| 9 | `price_action_momentum` | 26.2 | p55 | -1.88 | 0.97 | 0.75 | 47 | 12.3% | 0/8 | FAIL |
| 10 | `elder_impulse` | 25.5 | p50 | -1.91 | 3.14 | 0.82 | 36 | 11.6% | 1/8 | FAIL |
| 11 | `positional_scaling` | 25.4 | p44 | -1.12 | 2.17 | 0.87 | 32 | 8.8% | 0/8 | FAIL |
| 12 | `htf_ema` | 22.1 | p38 | -1.45 | 1.94 | 0.80 | 30 | 9.0% | 0/8 | FAIL |
| 13 | `acceleration_band` | 20.7 | p33 | -0.80 | 1.82 | 1.00 | 11 | 4.7% | 0/8 | FAIL |
| 14 | `frama` | 20.4 | p27 | -1.94 | 1.83 | 0.74 | 42 | 12.6% | 0/8 | FAIL |
| 15 | `price_cluster` | 20.2 | p22 | -0.01 | 1.43 | 250.00 | 0 | 0.4% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `engulfing_zone` | +4.81% | 0.78 | 1.33 | 26 | 1/8 | FAIL |
| `price_cluster` | +0.42% | -0.01 | 250.00 | 0 | 0/8 | FAIL |
| `volatility_cluster` | -0.64% | -0.12 | 1.02 | 41 | 0/8 | FAIL |
| `acceleration_band` | -1.44% | -0.80 | 1.00 | 11 | 0/8 | FAIL |
| `roc_ma_cross` | -1.87% | -0.94 | 0.85 | 11 | 0/8 | FAIL |
| `relative_volume` | -2.03% | -0.61 | 0.97 | 50 | 0/8 | FAIL |
| `positional_scaling` | -3.18% | -1.12 | 0.87 | 32 | 0/8 | FAIL |
| `htf_ema` | -4.40% | -1.45 | 0.80 | 30 | 0/8 | FAIL |
| `lob_maker` | -4.59% | -0.73 | 0.90 | 56 | 0/8 | FAIL |
| `elder_impulse` | -4.87% | -1.91 | 0.82 | 36 | 1/8 | FAIL |
| `dema_cross` | -5.32% | -1.89 | 0.72 | 29 | 0/8 | FAIL |
| `linear_channel_rev` | -5.34% | -2.40 | 0.61 | 24 | 0/8 | FAIL |
| `momentum_quality` | -5.48% | -1.18 | 0.85 | 56 | 0/8 | FAIL |
| `cmf` | -5.63% | -1.28 | 0.82 | 44 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -6.49% | -1.22 | 0.84 | 55 | 0/8 | FAIL |
| `narrow_range` | -7.26% | -2.31 | 0.71 | 36 | 0/8 | FAIL |
| `volume_breakout` | -7.37% | -1.45 | 0.82 | 58 | 0/8 | FAIL |
| `price_action_momentum` | -8.09% | -1.88 | 0.75 | 47 | 0/8 | FAIL |
| `frama` | -8.13% | -1.94 | 0.74 | 42 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `engulfing_zone` | profit_factor 1.41 < 1.5 (x1), mc_p_value 0.252 > 0.1 (우연 가능성) (x1), sharpe 0.05 < 1.0 (x1) |
| `price_cluster` | no trades generated (x4), trades 1 < 15 (x4), sharpe -2.04 < 1.0 (x2) |
| `volatility_cluster` | sharpe -0.49 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1), mc_p_value 0.631 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | trades 9 < 15 (x2), sharpe -1.21 < 1.0 (x1), profit_factor 0.67 < 1.5 (x1) |
| `roc_ma_cross` | trades 9 < 15 (x2), sharpe -0.71 < 1.0 (x1), profit_factor 0.77 < 1.5 (x1) |
| `relative_volume` | sharpe -2.93 < 1.0 (x1), profit_factor 0.63 < 1.5 (x1), mc_p_value 0.930 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | sharpe -3.18 < 1.0 (x1), profit_factor 0.53 < 1.5 (x1), mc_p_value 0.936 > 0.1 (우연 가능성) (x1) |
| `htf_ema` | sharpe -3.95 < 1.0 (x1), profit_factor 0.45 < 1.5 (x1), mc_p_value 0.980 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | sharpe 0.89 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.318 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | mc_p_value 1.000 > 0.1 (우연 가능성) (x2), sharpe -6.01 < 1.0 (x1), profit_factor 0.32 < 1.5 (x1) |
| `dema_cross` | sharpe -1.22 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1), mc_p_value 0.727 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -1.96 < 1.0 (x1), profit_factor 0.61 < 1.5 (x1), mc_p_value 0.826 > 0.1 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 0.90 < 1.5 (x2), sharpe -0.75 < 1.0 (x2), sharpe -2.16 < 1.0 (x1) |
| `cmf` | sharpe -1.68 < 1.0 (x2), mc_p_value 0.785 > 0.1 (우연 가능성) (x2), profit_factor 0.74 < 1.5 (x1) |
| `order_flow_imbalance_v2` | profit_factor 0.82 < 1.5 (x2), sharpe -0.91 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1) |
| `narrow_range` | sharpe -0.89 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.665 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -4.04 < 1.0 (x1), max_drawdown 23.2% > 20% (x1), profit_factor 0.56 < 1.5 (x1) |
| `price_action_momentum` | sharpe -2.63 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1), mc_p_value 0.887 > 0.1 (우연 가능성) (x1) |
| `frama` | profit_factor 0.85 < 1.5 (x2), sharpe -5.78 < 1.0 (x1), max_drawdown 24.2% > 20% (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.68 < 1.5 | 6 |
| profit_factor 0.77 < 1.5 | 6 |
| profit_factor 0.90 < 1.5 | 6 |
| no trades generated | 4 |
| trades 1 < 15 | 4 |
| trades 9 < 15 | 4 |
| mc_p_value 1.000 > 0.1 (우연 가능성) | 4 |
| profit_factor 0.85 < 1.5 | 4 |
| profit_factor 1.01 < 1.5 | 3 |
| profit_factor 0.84 < 1.5 | 3 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `elder_impulse` | 70 | 72 | 1.03 |
| `momentum_quality` | 138 | 67 | 0.49 |
| `relative_volume` | 109 | 62 | 0.57 |
| `volatility_cluster` | 73 | 54 | 0.74 |
| `lob_maker` | 137 | 54 | 0.39 |
| `price_action_momentum` | 127 | 50 | 0.39 |
| `linear_channel_rev` | 56 | 43 | 0.77 |
| `order_flow_imbalance_v2` | 152 | 41 | 0.27 |
| `htf_ema` | 75 | 37 | 0.49 |
| `volume_breakout` | 155 | 35 | 0.23 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 108 | 123 | 53.2% |
| `frama` | 0 | 160 | 177 | 52.5% |
| `acceleration_band` | 0 | 42 | 44 | 51.2% |
| `price_cluster` | 0 | 2 | 2 | 50.0% |
| `momentum_quality` | 0 | 231 | 215 | 48.2% |
| `roc_ma_cross` | 0 | 46 | 40 | 46.5% |
| `price_action_momentum` | 0 | 204 | 175 | 46.2% |
| `positional_scaling` | 0 | 137 | 115 | 45.6% |
| `volume_breakout` | 0 | 254 | 212 | 45.5% |
| `elder_impulse` | 0 | 157 | 128 | 44.9% |

## 포트폴리오 가상 배분

- **전체 19개 균등배분**: -4.05% -> $9,595
- **Top 5 균등배분**: +0.26% -> $10,026
