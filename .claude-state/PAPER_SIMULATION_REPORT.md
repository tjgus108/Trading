# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-24T10:50:34.489832Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-24T10:51:52.582438Z_
_Symbol: BTC/USDT_
_Data Source: CSV BTC/USDT 4h (resampled from 1h) (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 20:00:00+00:00 (499일)_
_Walk-Forward: 8개 윈도우 (train=1260, test=360 candles [4h])_
_Initial Balance: $10,000 USDT | Fee: 0.055%/leg (0.11% round-trip) | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=8, MDD<=20%_

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
| 평균 수익률 | 0.39% |
| 최고 수익률 | 5.81% (supertrend_multi) |
| 최저 수익률 | -4.54% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +5.81% | 0.96 | 39.6% | 1.36 | 29 | 7.3% | 2/8 | FAIL |
| 2 | `price_cluster` | +4.54% | 1.16 | 50.2% | 2.39 | 10 | 4.3% | 2/8 | FAIL |
| 3 | `momentum_quality` | +4.14% | 0.76 | 41.4% | 1.35 | 22 | 4.7% | 1/8 | FAIL |
| 4 | `relative_volume` | +3.18% | 0.89 | 41.7% | 1.52 | 17 | 4.0% | 1/8 | FAIL |
| 5 | `lob_maker` | +2.39% | 0.42 | 40.4% | 1.29 | 21 | 6.2% | 2/8 | FAIL |
| 6 | `cmf` | +2.26% | 0.48 | 42.5% | 1.23 | 21 | 5.7% | 1/8 | FAIL |
| 7 | `linear_channel_rev` | +1.88% | 0.66 | 43.6% | 2.10 | 6 | 2.1% | 1/8 | FAIL |
| 8 | `value_area` | +1.13% | 0.27 | 40.2% | 1.20 | 16 | 4.5% | 1/8 | FAIL |
| 9 | `elder_impulse` | +0.95% | -0.58 | 32.7% | 1.55 | 14 | 5.8% | 3/8 | FAIL |
| 10 | `price_action_momentum` | +0.83% | -0.56 | 35.9% | 1.10 | 24 | 6.9% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 64.8 | p100 | 0.96 | 2.02 | 1.36 | 29 | 7.3% | 2/8 | FAIL |
| 2 | `price_cluster` | 64.7 | p95 | 1.16 | 2.04 | 2.39 | 10 | 4.3% | 2/8 | FAIL |
| 3 | `relative_volume` | 59.1 | p90 | 0.89 | 1.54 | 1.52 | 17 | 4.0% | 1/8 | FAIL |
| 4 | `momentum_quality` | 59.0 | p85 | 0.76 | 1.94 | 1.35 | 22 | 4.7% | 1/8 | FAIL |
| 5 | `lob_maker` | 54.5 | p80 | 0.42 | 1.73 | 1.29 | 21 | 6.2% | 2/8 | FAIL |
| 6 | `cmf` | 53.9 | p76 | 0.48 | 1.36 | 1.23 | 21 | 5.7% | 1/8 | FAIL |
| 7 | `linear_channel_rev` | 50.0 | p71 | 0.66 | 1.66 | 2.10 | 6 | 2.1% | 1/8 | FAIL |
| 8 | `value_area` | 47.3 | p66 | 0.27 | 1.32 | 1.20 | 16 | 4.5% | 1/8 | FAIL |
| 9 | `htf_ema` | 42.5 | p61 | -0.27 | 2.07 | 1.57 | 11 | 4.7% | 2/8 | FAIL |
| 10 | `elder_impulse` | 41.3 | p57 | -0.58 | 3.09 | 1.55 | 14 | 5.8% | 3/8 | FAIL |
| 11 | `order_flow_imbalance_v2` | 39.3 | p52 | -0.40 | 2.99 | 1.20 | 19 | 6.5% | 2/8 | FAIL |
| 12 | `price_action_momentum` | 36.2 | p47 | -0.56 | 2.88 | 1.10 | 24 | 6.9% | 1/8 | FAIL |
| 13 | `positional_scaling` | 33.0 | p42 | -0.47 | 2.88 | 1.73 | 10 | 4.1% | 0/8 | FAIL |
| 14 | `volatility_cluster` | 31.1 | p38 | -0.72 | 2.55 | 1.09 | 14 | 4.9% | 1/8 | FAIL |
| 15 | `volume_breakout` | 26.1 | p33 | -1.04 | 2.78 | 0.97 | 18 | 6.9% | 1/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +5.81% | 0.96 | 1.36 | 29 | 2/8 | FAIL |
| `price_cluster` | +4.54% | 1.16 | 2.39 | 10 | 2/8 | FAIL |
| `momentum_quality` | +4.14% | 0.76 | 1.35 | 22 | 1/8 | FAIL |
| `relative_volume` | +3.18% | 0.89 | 1.52 | 17 | 1/8 | FAIL |
| `lob_maker` | +2.39% | 0.42 | 1.29 | 21 | 2/8 | FAIL |
| `cmf` | +2.26% | 0.48 | 1.23 | 21 | 1/8 | FAIL |
| `linear_channel_rev` | +1.88% | 0.66 | 2.10 | 6 | 1/8 | FAIL |
| `value_area` | +1.13% | 0.27 | 1.20 | 16 | 1/8 | FAIL |
| `elder_impulse` | +0.95% | -0.58 | 1.55 | 14 | 3/8 | FAIL |
| `price_action_momentum` | +0.83% | -0.56 | 1.10 | 24 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | +0.73% | -0.40 | 1.20 | 19 | 2/8 | FAIL |
| `positional_scaling` | +0.39% | -0.47 | 1.73 | 10 | 0/8 | FAIL |
| `htf_ema` | +0.29% | -0.27 | 1.57 | 11 | 2/8 | FAIL |
| `volatility_cluster` | -0.76% | -0.72 | 1.09 | 14 | 1/8 | FAIL |
| `volume_breakout` | -1.39% | -1.04 | 0.97 | 18 | 1/8 | FAIL |
| `dema_cross` | -1.50% | -1.42 | 0.50 | 5 | 0/8 | FAIL |
| `roc_ma_cross` | -1.73% | -1.17 | 0.77 | 10 | 1/8 | FAIL |
| `wick_reversal` | -1.86% | -0.92 | 0.93 | 11 | 1/8 | FAIL |
| `engulfing_zone` | -2.47% | -1.45 | 0.60 | 7 | 0/8 | FAIL |
| `acceleration_band` | -2.78% | -1.61 | 0.68 | 12 | 0/8 | FAIL |
| `narrow_range` | -2.85% | -1.80 | 0.66 | 12 | 1/8 | FAIL |
| `frama` | -4.54% | -1.38 | 0.72 | 21 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | sharpe 0.75 < 1.0 (x1), profit_factor 1.18 < 1.5 (x1), mc_p_value 0.345 > 0.1 (우연 가능성) (x1) |
| `price_cluster` | trades 5 < 8 (x1), sharpe -1.53 < 1.0 (x1), profit_factor 0.59 < 1.5 (x1) |
| `momentum_quality` | mc_p_value 0.153 > 0.1 (우연 가능성) (x1), sharpe -0.57 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1) |
| `relative_volume` | mc_p_value 0.124 > 0.1 (우연 가능성) (x1), profit_factor 1.38 < 1.5 (x1), mc_p_value 0.298 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | sharpe -0.49 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.606 > 0.1 (우연 가능성) (x1) |
| `cmf` | mc_p_value 0.148 > 0.1 (우연 가능성) (x1), sharpe 0.44 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1) |
| `linear_channel_rev` | trades 5 < 8 (x3), trades 6 < 8 (x2), trades 4 < 8 (x2) |
| `value_area` | sharpe 0.28 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1), mc_p_value 0.447 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | sharpe 0.25 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), sharpe -2.96 < 1.0 (x1) |
| `price_action_momentum` | mc_p_value 0.183 > 0.1 (우연 가능성) (x1), sharpe 0.64 < 1.0 (x1), profit_factor 1.16 < 1.5 (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.111 > 0.1 (우연 가능성) (x1), profit_factor 1.39 < 1.5 (x1), mc_p_value 0.295 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | trades 7 < 8 (x2), profit_factor 0.92 < 1.5 (x2), sharpe -5.86 < 1.0 (x1) |
| `htf_ema` | sharpe -2.70 < 1.0 (x1), profit_factor 0.41 < 1.5 (x1), sharpe -2.25 < 1.0 (x1) |
| `volatility_cluster` | sharpe 0.80 < 1.0 (x1), profit_factor 1.26 < 1.5 (x1), mc_p_value 0.360 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.316 > 0.1 (우연 가능성) (x1), mc_p_value 0.195 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | trades 3 < 8 (x3), trades 5 < 8 (x2), sharpe -2.01 < 1.0 (x1) |
| `roc_ma_cross` | sharpe 0.88 < 1.0 (x1), profit_factor 1.40 < 1.5 (x1), sharpe 0.33 < 1.0 (x1) |
| `wick_reversal` | sharpe -3.38 < 1.0 (x1), profit_factor 0.31 < 1.5 (x1), sharpe -2.38 < 1.0 (x1) |
| `engulfing_zone` | trades 7 < 8 (x3), sharpe -3.29 < 1.0 (x1), profit_factor 0.20 < 1.5 (x1) |
| `acceleration_band` | profit_factor 1.00 < 1.5 (x2), sharpe 0.00 < 1.0 (x1), sharpe -1.29 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 5 < 8 | 7 |
| trades 7 < 8 | 7 |
| profit_factor 0.59 < 1.5 | 4 |
| profit_factor 0.82 < 1.5 | 4 |
| profit_factor 1.00 < 1.5 | 4 |
| profit_factor 0.70 < 1.5 | 3 |
| profit_factor 0.56 < 1.5 | 3 |
| profit_factor 0.92 < 1.5 | 3 |
| profit_factor 1.02 < 1.5 | 3 |
| sharpe 0.33 < 1.0 | 3 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `supertrend_multi` | 51 | 25 | 0.49 |
| `elder_impulse` | 32 | 23 | 0.72 |
| `price_action_momentum` | 52 | 19 | 0.37 |
| `order_flow_imbalance_v2` | 37 | 16 | 0.43 |
| `frama` | 52 | 16 | 0.31 |
| `volume_breakout` | 43 | 13 | 0.30 |
| `acceleration_band` | 29 | 11 | 0.38 |
| `positional_scaling` | 18 | 10 | 0.56 |
| `cmf` | 41 | 7 | 0.17 |
| `lob_maker` | 46 | 6 | 0.13 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `cmf` | 0 | 168 | 1 | 0.6% |
| `supertrend_multi` | 0 | 234 | 1 | 0.4% |
| `price_cluster` | 0 | 81 | 0 | 0.0% |
| `momentum_quality` | 0 | 177 | 0 | 0.0% |
| `relative_volume` | 0 | 138 | 0 | 0.0% |
| `lob_maker` | 0 | 166 | 0 | 0.0% |
| `linear_channel_rev` | 0 | 46 | 0 | 0.0% |
| `value_area` | 0 | 125 | 0 | 0.0% |
| `elder_impulse` | 0 | 110 | 0 | 0.0% |
| `price_action_momentum` | 0 | 190 | 0 | 0.0% |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +0.39% -> $10,039
- **Top 5 균등배분**: +4.01% -> $10,401


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-24T10:53:06.224804Z_
_Symbol: ETH/USDT_
_Data Source: CSV ETH/USDT 4h (resampled from 1h) (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 20:00:00+00:00 (499일)_
_Walk-Forward: 8개 윈도우 (train=1260, test=360 candles [4h])_
_Initial Balance: $10,000 USDT | Fee: 0.055%/leg (0.11% round-trip) | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=8, MDD<=20%_

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
| 평균 수익률 | -4.19% |
| 최고 수익률 | 2.22% (engulfing_zone) |
| 최저 수익률 | -11.17% (order_flow_imbalance_v2) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `engulfing_zone` | +2.22% | 0.42 | 53.9% | 128.87 | 8 | 2.9% | 0/8 | FAIL |
| 2 | `value_area` | -1.14% | -0.59 | 33.1% | 0.92 | 17 | 4.8% | 0/8 | FAIL |
| 3 | `volatility_cluster` | -1.24% | -0.65 | 34.2% | 0.86 | 14 | 4.5% | 0/8 | FAIL |
| 4 | `linear_channel_rev` | -1.29% | -0.96 | 38.6% | 0.70 | 7 | 2.9% | 0/8 | FAIL |
| 5 | `price_cluster` | -1.34% | -0.48 | 41.3% | 0.95 | 12 | 4.9% | 1/8 | FAIL |
| 6 | `narrow_range` | -1.40% | -0.76 | 38.9% | 0.86 | 13 | 5.1% | 1/8 | FAIL |
| 7 | `positional_scaling` | -1.66% | -0.82 | 35.5% | 0.78 | 10 | 3.7% | 0/8 | FAIL |
| 8 | `dema_cross` | -1.96% | -2.30 | 7.3% | 0.20 | 3 | 2.3% | 0/8 | FAIL |
| 9 | `acceleration_band` | -1.97% | -1.66 | 29.3% | 0.81 | 6 | 3.9% | 0/8 | FAIL |
| 10 | `wick_reversal` | -2.42% | -1.58 | 28.1% | 0.71 | 11 | 5.0% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `engulfing_zone` | 55.5 | p100 | 0.42 | 2.88 | 128.87 | 8 | 2.9% | 0/8 | FAIL |
| 2 | `price_cluster` | 45.8 | p95 | -0.48 | 1.08 | 0.95 | 12 | 4.9% | 1/8 | FAIL |
| 3 | `narrow_range` | 44.9 | p90 | -0.76 | 1.41 | 0.86 | 13 | 5.1% | 1/8 | FAIL |
| 4 | `value_area` | 39.9 | p85 | -0.59 | 1.38 | 0.92 | 17 | 4.8% | 0/8 | FAIL |
| 5 | `elder_impulse` | 39.4 | p80 | -1.53 | 1.71 | 0.71 | 13 | 5.4% | 1/8 | FAIL |
| 6 | `volatility_cluster` | 37.7 | p76 | -0.65 | 1.11 | 0.86 | 14 | 4.5% | 0/8 | FAIL |
| 7 | `supertrend_multi` | 36.0 | p71 | -2.51 | 1.39 | 0.63 | 33 | 10.8% | 0/8 | FAIL |
| 8 | `positional_scaling` | 32.1 | p66 | -0.82 | 0.96 | 0.78 | 10 | 3.7% | 0/8 | FAIL |
| 9 | `roc_ma_cross` | 30.9 | p61 | -2.91 | 2.42 | 0.53 | 16 | 6.9% | 1/8 | FAIL |
| 10 | `htf_ema` | 28.7 | p57 | -1.75 | 1.15 | 0.59 | 13 | 5.4% | 0/8 | FAIL |
| 11 | `linear_channel_rev` | 28.6 | p52 | -0.96 | 0.75 | 0.70 | 7 | 2.9% | 0/8 | FAIL |
| 12 | `lob_maker` | 28.5 | p47 | -2.07 | 2.04 | 0.66 | 20 | 9.3% | 0/8 | FAIL |
| 13 | `relative_volume` | 27.3 | p42 | -2.98 | 1.59 | 0.51 | 24 | 9.0% | 0/8 | FAIL |
| 14 | `wick_reversal` | 27.0 | p38 | -1.58 | 2.05 | 0.71 | 11 | 5.0% | 0/8 | FAIL |
| 15 | `price_action_momentum` | 25.8 | p33 | -3.02 | 1.37 | 0.50 | 22 | 9.6% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `engulfing_zone` | +2.22% | 0.42 | 128.87 | 8 | 0/8 | FAIL |
| `value_area` | -1.14% | -0.59 | 0.92 | 17 | 0/8 | FAIL |
| `volatility_cluster` | -1.24% | -0.65 | 0.86 | 14 | 0/8 | FAIL |
| `linear_channel_rev` | -1.29% | -0.96 | 0.70 | 7 | 0/8 | FAIL |
| `price_cluster` | -1.34% | -0.48 | 0.95 | 12 | 1/8 | FAIL |
| `narrow_range` | -1.40% | -0.76 | 0.86 | 13 | 1/8 | FAIL |
| `positional_scaling` | -1.66% | -0.82 | 0.78 | 10 | 0/8 | FAIL |
| `dema_cross` | -1.96% | -2.30 | 0.20 | 3 | 0/8 | FAIL |
| `acceleration_band` | -1.97% | -1.66 | 0.81 | 6 | 0/8 | FAIL |
| `wick_reversal` | -2.42% | -1.58 | 0.71 | 11 | 0/8 | FAIL |
| `elder_impulse` | -2.85% | -1.53 | 0.71 | 13 | 1/8 | FAIL |
| `htf_ema` | -3.87% | -1.75 | 0.59 | 13 | 0/8 | FAIL |
| `roc_ma_cross` | -5.24% | -2.91 | 0.53 | 16 | 1/8 | FAIL |
| `cmf` | -5.53% | -2.69 | 0.45 | 15 | 0/8 | FAIL |
| `lob_maker` | -5.73% | -2.07 | 0.66 | 20 | 0/8 | FAIL |
| `frama` | -6.48% | -2.55 | 0.50 | 16 | 0/8 | FAIL |
| `momentum_quality` | -6.74% | -3.55 | 0.45 | 20 | 0/8 | FAIL |
| `relative_volume` | -6.90% | -2.98 | 0.51 | 24 | 0/8 | FAIL |
| `price_action_momentum` | -7.75% | -3.02 | 0.50 | 22 | 0/8 | FAIL |
| `supertrend_multi` | -8.87% | -2.51 | 0.63 | 33 | 0/8 | FAIL |
| `volume_breakout` | -8.95% | -4.28 | 0.44 | 22 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -11.17% | -4.45 | 0.33 | 23 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `engulfing_zone` | trades 7 < 8 (x3), trades 6 < 8 (x2), sharpe -1.46 < 1.0 (x1) |
| `value_area` | sharpe 0.38 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.431 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe 0.62 < 1.0 (x1), profit_factor 1.23 < 1.5 (x1), profit_factor 1.34 < 1.5 (x1) |
| `linear_channel_rev` | trades 5 < 8 (x2), sharpe 0.02 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1) |
| `price_cluster` | sharpe -1.00 < 1.0 (x1), profit_factor 0.68 < 1.5 (x1), sharpe 0.02 < 1.0 (x1) |
| `narrow_range` | sharpe -0.59 < 1.0 (x2), sharpe 0.57 < 1.0 (x1), profit_factor 1.19 < 1.5 (x1) |
| `positional_scaling` | sharpe -1.62 < 1.0 (x1), profit_factor 0.59 < 1.5 (x1), sharpe -0.30 < 1.0 (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x5), trades 5 < 8 (x2), trades 3 < 8 (x2) |
| `acceleration_band` | trades 7 < 8 (x3), trades 5 < 8 (x2), profit_factor 0.02 < 1.5 (x2) |
| `wick_reversal` | sharpe -0.39 < 1.0 (x2), sharpe 0.57 < 1.0 (x1), profit_factor 1.21 < 1.5 (x1) |
| `elder_impulse` | profit_factor 0.61 < 1.5 (x2), sharpe -1.18 < 1.0 (x1), profit_factor 0.66 < 1.5 (x1) |
| `htf_ema` | sharpe -1.83 < 1.0 (x2), sharpe -0.75 < 1.0 (x1), profit_factor 0.72 < 1.5 (x1) |
| `roc_ma_cross` | profit_factor 0.44 < 1.5 (x2), sharpe -0.89 < 1.0 (x1), profit_factor 0.77 < 1.5 (x1) |
| `cmf` | profit_factor 0.50 < 1.5 (x2), sharpe -2.65 < 1.0 (x1), mc_p_value 0.887 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | sharpe -0.90 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1), mc_p_value 0.680 > 0.1 (우연 가능성) (x1) |
| `frama` | profit_factor 0.38 < 1.5 (x2), sharpe -2.27 < 1.0 (x1), profit_factor 0.51 < 1.5 (x1) |
| `momentum_quality` | mc_p_value 1.000 > 0.1 (우연 가능성) (x2), sharpe -0.10 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1) |
| `relative_volume` | profit_factor 0.40 < 1.5 (x2), sharpe -3.33 < 1.0 (x1), mc_p_value 0.953 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe -0.64 < 1.0 (x1), profit_factor 0.86 < 1.5 (x1), mc_p_value 0.614 > 0.1 (우연 가능성) (x1) |
| `supertrend_multi` | sharpe -1.57 < 1.0 (x1), profit_factor 0.73 < 1.5 (x1), mc_p_value 0.787 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 7 < 8 | 8 |
| mc_p_value 1.000 > 0.1 (우연 가능성) | 7 |
| profit_factor 0.00 < 1.5 | 6 |
| trades 5 < 8 | 6 |
| trades 6 < 8 | 5 |
| profit_factor 0.61 < 1.5 | 5 |
| profit_factor 0.41 < 1.5 | 4 |
| trades 4 < 8 | 4 |
| profit_factor 0.51 < 1.5 | 4 |
| profit_factor 0.33 < 1.5 | 4 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `relative_volume` | 50 | 70 | 1.40 |
| `order_flow_imbalance_v2` | 61 | 56 | 0.92 |
| `volume_breakout` | 60 | 54 | 0.90 |
| `lob_maker` | 43 | 30 | 0.70 |
| `roc_ma_cross` | 42 | 29 | 0.69 |
| `price_action_momentum` | 61 | 24 | 0.39 |
| `momentum_quality` | 58 | 22 | 0.38 |
| `cmf` | 41 | 18 | 0.44 |
| `supertrend_multi` | 94 | 15 | 0.16 |
| `value_area` | 45 | 11 | 0.24 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `volatility_cluster` | 0 | 111 | 3 | 2.6% |
| `roc_ma_cross` | 0 | 124 | 3 | 2.4% |
| `supertrend_multi` | 0 | 259 | 6 | 2.3% |
| `momentum_quality` | 0 | 159 | 3 | 1.9% |
| `relative_volume` | 0 | 188 | 3 | 1.6% |
| `order_flow_imbalance_v2` | 0 | 184 | 2 | 1.1% |
| `engulfing_zone` | 0 | 60 | 0 | 0.0% |
| `value_area` | 0 | 133 | 0 | 0.0% |
| `linear_channel_rev` | 0 | 56 | 0 | 0.0% |
| `price_cluster` | 0 | 94 | 0 | 0.0% |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -4.19% -> $9,581
- **Top 5 균등배분**: -0.56% -> $9,944


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-24T10:54:20.041069Z_
_Symbol: SOL/USDT_
_Data Source: CSV SOL/USDT 4h (resampled from 1h) (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 20:00:00+00:00 (499일)_
_Walk-Forward: 8개 윈도우 (train=1260, test=360 candles [4h])_
_Initial Balance: $10,000 USDT | Fee: 0.055%/leg (0.11% round-trip) | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=8, MDD<=20%_

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
| 평균 수익률 | -2.86% |
| 최고 수익률 | 1.58% (engulfing_zone) |
| 최저 수익률 | -8.71% (price_action_momentum) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `engulfing_zone` | +1.58% | 0.67 | 45.7% | 1.53 | 7 | 3.1% | 0/8 | FAIL |
| 2 | `wick_reversal` | +1.31% | 0.64 | 43.0% | 1.89 | 9 | 3.0% | 2/8 | FAIL |
| 3 | `elder_impulse` | +0.23% | -0.12 | 35.7% | 1.04 | 12 | 4.1% | 1/8 | FAIL |
| 4 | `momentum_quality` | -0.18% | -0.05 | 39.6% | 1.01 | 22 | 5.9% | 0/8 | FAIL |
| 5 | `price_cluster` | -0.74% | -0.72 | 37.3% | 0.91 | 7 | 4.0% | 2/8 | FAIL |
| 6 | `dema_cross` | -0.88% | -0.99 | 41.4% | 1.26 | 8 | 3.4% | 1/8 | FAIL |
| 7 | `cmf` | -1.15% | -0.57 | 39.5% | 0.98 | 17 | 4.9% | 1/8 | FAIL |
| 8 | `linear_channel_rev` | -1.18% | -1.46 | 33.5% | 0.66 | 5 | 2.5% | 0/8 | FAIL |
| 9 | `acceleration_band` | -2.09% | -1.30 | 27.7% | 0.64 | 7 | 4.1% | 0/8 | FAIL |
| 10 | `value_area` | -2.63% | -1.13 | 35.8% | 0.73 | 17 | 6.1% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `wick_reversal` | 67.8 | p100 | 0.64 | 1.42 | 1.89 | 9 | 3.0% | 2/8 | FAIL |
| 2 | `momentum_quality` | 54.9 | p95 | -0.05 | 0.81 | 1.01 | 22 | 5.9% | 0/8 | FAIL |
| 3 | `engulfing_zone` | 51.0 | p90 | 0.67 | 0.97 | 1.53 | 7 | 3.1% | 0/8 | FAIL |
| 4 | `elder_impulse` | 48.8 | p85 | -0.12 | 1.56 | 1.04 | 12 | 4.1% | 1/8 | FAIL |
| 5 | `cmf` | 47.9 | p80 | -0.57 | 1.75 | 0.98 | 17 | 4.9% | 1/8 | FAIL |
| 6 | `supertrend_multi` | 45.1 | p76 | -1.17 | 1.42 | 0.81 | 31 | 8.9% | 0/8 | FAIL |
| 7 | `price_cluster` | 41.1 | p71 | -0.72 | 1.86 | 0.91 | 7 | 4.0% | 2/8 | FAIL |
| 8 | `dema_cross` | 39.3 | p66 | -0.99 | 2.20 | 1.26 | 8 | 3.4% | 1/8 | FAIL |
| 9 | `value_area` | 37.7 | p61 | -1.13 | 0.67 | 0.73 | 17 | 6.1% | 0/8 | FAIL |
| 10 | `relative_volume` | 37.5 | p57 | -1.28 | 1.60 | 0.77 | 21 | 6.6% | 0/8 | FAIL |
| 11 | `volatility_cluster` | 33.9 | p52 | -1.43 | 1.22 | 0.70 | 17 | 6.1% | 0/8 | FAIL |
| 12 | `frama` | 33.6 | p47 | -1.26 | 2.17 | 0.87 | 20 | 8.8% | 0/8 | FAIL |
| 13 | `lob_maker` | 30.2 | p42 | -1.92 | 1.19 | 0.65 | 23 | 10.0% | 0/8 | FAIL |
| 14 | `order_flow_imbalance_v2` | 29.6 | p38 | -2.04 | 0.99 | 0.60 | 21 | 8.5% | 0/8 | FAIL |
| 15 | `narrow_range` | 25.2 | p33 | -1.86 | 1.45 | 0.61 | 14 | 6.2% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `engulfing_zone` | +1.58% | 0.67 | 1.53 | 7 | 0/8 | FAIL |
| `wick_reversal` | +1.31% | 0.64 | 1.89 | 9 | 2/8 | FAIL |
| `elder_impulse` | +0.23% | -0.12 | 1.04 | 12 | 1/8 | FAIL |
| `momentum_quality` | -0.18% | -0.05 | 1.01 | 22 | 0/8 | FAIL |
| `price_cluster` | -0.74% | -0.72 | 0.91 | 7 | 2/8 | FAIL |
| `dema_cross` | -0.88% | -0.99 | 1.26 | 8 | 1/8 | FAIL |
| `cmf` | -1.15% | -0.57 | 0.98 | 17 | 1/8 | FAIL |
| `linear_channel_rev` | -1.18% | -1.46 | 0.66 | 5 | 0/8 | FAIL |
| `acceleration_band` | -2.09% | -1.30 | 0.64 | 7 | 0/8 | FAIL |
| `value_area` | -2.63% | -1.13 | 0.73 | 17 | 0/8 | FAIL |
| `positional_scaling` | -2.88% | -1.72 | 0.56 | 9 | 0/8 | FAIL |
| `relative_volume` | -2.92% | -1.28 | 0.77 | 21 | 0/8 | FAIL |
| `volatility_cluster` | -3.31% | -1.43 | 0.70 | 17 | 0/8 | FAIL |
| `frama` | -3.42% | -1.26 | 0.87 | 20 | 0/8 | FAIL |
| `supertrend_multi` | -3.86% | -1.17 | 0.81 | 31 | 0/8 | FAIL |
| `narrow_range` | -4.27% | -1.86 | 0.61 | 14 | 0/8 | FAIL |
| `volume_breakout` | -4.89% | -2.31 | 0.65 | 21 | 0/8 | FAIL |
| `htf_ema` | -4.93% | -2.78 | 0.39 | 11 | 0/8 | FAIL |
| `roc_ma_cross` | -5.23% | -3.08 | 0.38 | 13 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -6.07% | -2.04 | 0.60 | 21 | 0/8 | FAIL |
| `lob_maker` | -6.67% | -1.92 | 0.65 | 23 | 0/8 | FAIL |
| `price_action_momentum` | -8.71% | -3.35 | 0.45 | 24 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `engulfing_zone` | trades 7 < 8 (x4), trades 6 < 8 (x2), sharpe -0.27 < 1.0 (x2) |
| `wick_reversal` | sharpe -0.00 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), sharpe -0.12 < 1.0 (x1) |
| `elder_impulse` | mc_p_value 0.203 > 0.1 (우연 가능성) (x1), sharpe 0.79 < 1.0 (x1), profit_factor 1.27 < 1.5 (x1) |
| `momentum_quality` | sharpe -0.39 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.592 > 0.1 (우연 가능성) (x1) |
| `price_cluster` | trades 6 < 8 (x2), sharpe -3.39 < 1.0 (x1), profit_factor 0.17 < 1.5 (x1) |
| `dema_cross` | trades 5 < 8 (x2), sharpe -1.44 < 1.0 (x1), profit_factor 0.46 < 1.5 (x1) |
| `cmf` | sharpe -4.17 < 1.0 (x1), profit_factor 0.30 < 1.5 (x1), mc_p_value 0.988 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | trades 5 < 8 (x3), profit_factor 0.04 < 1.5 (x2), trades 6 < 8 (x2) |
| `acceleration_band` | trades 6 < 8 (x2), sharpe 0.26 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1) |
| `value_area` | sharpe -0.38 < 1.0 (x1), profit_factor 0.90 < 1.5 (x1), mc_p_value 0.596 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | sharpe -1.09 < 1.0 (x1), profit_factor 0.67 < 1.5 (x1), sharpe 0.07 < 1.0 (x1) |
| `relative_volume` | sharpe -0.76 < 1.0 (x2), profit_factor 0.81 < 1.5 (x2), profit_factor 1.22 < 1.5 (x2) |
| `volatility_cluster` | sharpe -0.85 < 1.0 (x1), profit_factor 0.78 < 1.5 (x1), mc_p_value 0.687 > 0.1 (우연 가능성) (x1) |
| `frama` | mc_p_value 0.174 > 0.1 (우연 가능성) (x1), mc_p_value 0.102 > 0.1 (우연 가능성) (x1), sharpe -0.76 < 1.0 (x1) |
| `supertrend_multi` | sharpe -3.30 < 1.0 (x1), profit_factor 0.43 < 1.5 (x1), mc_p_value 0.964 > 0.1 (우연 가능성) (x1) |
| `narrow_range` | sharpe -2.57 < 1.0 (x1), profit_factor 0.47 < 1.5 (x1), mc_p_value 0.918 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 0.49 < 1.5 (x2), sharpe -2.76 < 1.0 (x1), mc_p_value 0.924 > 0.1 (우연 가능성) (x1) |
| `htf_ema` | sharpe -2.06 < 1.0 (x1), profit_factor 0.47 < 1.5 (x1), sharpe -3.86 < 1.0 (x1) |
| `roc_ma_cross` | sharpe -1.70 < 1.0 (x1), profit_factor 0.55 < 1.5 (x1), sharpe -0.82 < 1.0 (x1) |
| `order_flow_imbalance_v2` | sharpe -2.26 < 1.0 (x1), profit_factor 0.56 < 1.5 (x1), mc_p_value 0.880 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 7 < 8 | 9 |
| trades 6 < 8 | 8 |
| profit_factor 1.02 < 1.5 | 6 |
| trades 5 < 8 | 6 |
| sharpe 0.07 < 1.0 | 5 |
| profit_factor 0.67 < 1.5 | 5 |
| profit_factor 0.81 < 1.5 | 5 |
| profit_factor 0.63 < 1.5 | 4 |
| profit_factor 0.90 < 1.5 | 4 |
| profit_factor 0.47 < 1.5 | 4 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `price_action_momentum` | 67 | 37 | 0.55 |
| `volume_breakout` | 49 | 28 | 0.57 |
| `relative_volume` | 52 | 27 | 0.52 |
| `order_flow_imbalance_v2` | 52 | 23 | 0.44 |
| `lob_maker` | 63 | 19 | 0.30 |
| `frama` | 49 | 18 | 0.37 |
| `supertrend_multi` | 81 | 16 | 0.20 |
| `volatility_cluster` | 44 | 13 | 0.30 |
| `roc_ma_cross` | 36 | 13 | 0.36 |
| `momentum_quality` | 46 | 12 | 0.26 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 25 | 36 | 59.0% |
| `lob_maker` | 0 | 97 | 88 | 47.6% |
| `engulfing_zone` | 0 | 29 | 25 | 46.3% |
| `frama` | 0 | 89 | 75 | 45.7% |
| `roc_ma_cross` | 0 | 56 | 46 | 45.1% |
| `price_action_momentum` | 0 | 108 | 83 | 43.5% |
| `relative_volume` | 0 | 94 | 72 | 43.4% |
| `momentum_quality` | 0 | 99 | 74 | 42.8% |
| `cmf` | 0 | 77 | 56 | 42.1% |
| `elder_impulse` | 0 | 58 | 41 | 41.4% |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -2.86% -> $9,714
- **Top 5 균등배분**: +0.44% -> $10,044
