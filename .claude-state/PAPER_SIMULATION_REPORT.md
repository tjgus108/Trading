# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-24T05:08:23.370866Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-24T05:09:43.401074Z_
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
| 평균 수익률 | 0.32% |
| 최고 수익률 | 4.54% (price_cluster) |
| 최저 수익률 | -4.54% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +4.54% | 1.16 | 50.2% | 2.39 | 10 | 4.3% | 2/8 | FAIL |
| 2 | `supertrend_multi` | +4.25% | 1.14 | 30.4% | 1.27 | 8 | 2.2% | 3/8 | FAIL |
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
| 1 | `price_cluster` | 66.8 | p100 | 1.16 | 2.04 | 2.39 | 10 | 4.3% | 2/8 | FAIL |
| 2 | `momentum_quality` | 64.5 | p95 | 0.76 | 1.94 | 1.35 | 22 | 4.7% | 1/8 | FAIL |
| 3 | `relative_volume` | 63.7 | p90 | 0.89 | 1.54 | 1.52 | 17 | 4.0% | 1/8 | FAIL |
| 4 | `lob_maker` | 59.1 | p80 | 0.42 | 1.73 | 1.29 | 21 | 6.2% | 2/8 | FAIL |
| 5 | `cmf` | 59.1 | p85 | 0.48 | 1.36 | 1.23 | 21 | 5.7% | 1/8 | FAIL |
| 6 | `supertrend_multi` | 57.6 | p76 | 1.14 | 1.46 | 1.27 | 8 | 2.2% | 3/8 | FAIL |
| 7 | `value_area` | 51.3 | p71 | 0.27 | 1.32 | 1.20 | 16 | 4.5% | 1/8 | FAIL |
| 8 | `linear_channel_rev` | 51.2 | p66 | 0.66 | 1.66 | 2.10 | 6 | 2.1% | 1/8 | FAIL |
| 9 | `htf_ema` | 44.8 | p61 | -0.27 | 2.07 | 1.57 | 11 | 4.7% | 2/8 | FAIL |
| 10 | `elder_impulse` | 43.5 | p57 | -0.58 | 3.09 | 1.55 | 14 | 5.8% | 3/8 | FAIL |
| 11 | `order_flow_imbalance_v2` | 42.4 | p52 | -0.40 | 2.99 | 1.20 | 19 | 6.5% | 2/8 | FAIL |
| 12 | `price_action_momentum` | 40.2 | p47 | -0.56 | 2.88 | 1.10 | 24 | 6.9% | 1/8 | FAIL |
| 13 | `positional_scaling` | 34.8 | p42 | -0.47 | 2.88 | 1.73 | 10 | 4.1% | 0/8 | FAIL |
| 14 | `volatility_cluster` | 33.9 | p38 | -0.72 | 2.55 | 1.09 | 14 | 4.9% | 1/8 | FAIL |
| 15 | `volume_breakout` | 29.0 | p33 | -1.04 | 2.78 | 0.97 | 18 | 6.9% | 1/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +4.54% | 1.16 | 2.39 | 10 | 2/8 | FAIL |
| `supertrend_multi` | +4.25% | 1.14 | 1.27 | 8 | 3/8 | FAIL |
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
| `price_cluster` | trades 5 < 8 (x1), sharpe -1.53 < 1.0 (x1), profit_factor 0.59 < 1.5 (x1) |
| `supertrend_multi` | no trades generated (x3), sharpe 0.22 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1) |
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
| trades 7 < 8 | 8 |
| trades 5 < 8 | 7 |
| profit_factor 0.82 < 1.5 | 4 |
| profit_factor 1.00 < 1.5 | 4 |
| profit_factor 0.59 < 1.5 | 3 |
| no trades generated | 3 |
| profit_factor 1.11 < 1.5 | 3 |
| profit_factor 0.70 < 1.5 | 3 |
| profit_factor 0.56 < 1.5 | 3 |
| profit_factor 0.92 < 1.5 | 3 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `elder_impulse` | 32 | 23 | 0.72 |
| `price_action_momentum` | 52 | 19 | 0.37 |
| `order_flow_imbalance_v2` | 37 | 16 | 0.43 |
| `frama` | 52 | 16 | 0.31 |
| `volume_breakout` | 43 | 13 | 0.30 |
| `acceleration_band` | 29 | 11 | 0.38 |
| `positional_scaling` | 18 | 10 | 0.56 |
| `cmf` | 41 | 7 | 0.17 |
| `lob_maker` | 46 | 6 | 0.13 |
| `value_area` | 36 | 6 | 0.17 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `cmf` | 0 | 168 | 1 | 0.6% |
| `price_cluster` | 0 | 81 | 0 | 0.0% |
| `supertrend_multi` | 0 | 62 | 0 | 0.0% |
| `momentum_quality` | 0 | 177 | 0 | 0.0% |
| `relative_volume` | 0 | 138 | 0 | 0.0% |
| `lob_maker` | 0 | 166 | 0 | 0.0% |
| `linear_channel_rev` | 0 | 46 | 0 | 0.0% |
| `value_area` | 0 | 125 | 0 | 0.0% |
| `elder_impulse` | 0 | 110 | 0 | 0.0% |
| `price_action_momentum` | 0 | 190 | 0 | 0.0% |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +0.32% -> $10,032
- **Top 5 균등배분**: +3.70% -> $10,370


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-24T05:11:03.699080Z_
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
| 평균 수익률 | -3.94% |
| 최고 수익률 | 1.94% (engulfing_zone) |
| 최저 수익률 | -9.18% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `engulfing_zone` | +1.94% | 0.52 | 47.8% | 2.11 | 7 | 3.4% | 1/8 | FAIL |
| 2 | `linear_channel_rev` | -0.78% | -0.74 | 33.2% | 1.05 | 5 | 2.5% | 0/8 | FAIL |
| 3 | `narrow_range` | -1.08% | -0.43 | 36.6% | 0.90 | 14 | 5.0% | 0/8 | FAIL |
| 4 | `acceleration_band` | -1.48% | -0.68 | 31.6% | 0.87 | 9 | 4.6% | 0/8 | FAIL |
| 5 | `wick_reversal` | -1.86% | -1.14 | 35.6% | 0.75 | 10 | 4.6% | 1/8 | FAIL |
| 6 | `htf_ema` | -1.91% | -0.91 | 36.5% | 0.85 | 10 | 5.0% | 0/8 | FAIL |
| 7 | `dema_cross` | -1.91% | -2.37 | 23.9% | 0.43 | 6 | 2.7% | 1/8 | FAIL |
| 8 | `volatility_cluster` | -2.07% | -0.99 | 35.2% | 0.75 | 16 | 5.3% | 0/8 | FAIL |
| 9 | `price_cluster` | -2.10% | -0.92 | 36.4% | 0.85 | 12 | 5.4% | 1/8 | FAIL |
| 10 | `positional_scaling` | -2.43% | -1.80 | 25.0% | 0.66 | 8 | 4.2% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `engulfing_zone` | 65.1 | p100 | 0.52 | 2.29 | 2.11 | 7 | 3.4% | 1/8 | FAIL |
| 2 | `price_cluster` | 46.3 | p95 | -0.92 | 1.36 | 0.85 | 12 | 5.4% | 1/8 | FAIL |
| 3 | `narrow_range` | 45.5 | p90 | -0.43 | 0.80 | 0.90 | 14 | 5.0% | 0/8 | FAIL |
| 4 | `volatility_cluster` | 42.3 | p85 | -0.99 | 0.65 | 0.75 | 16 | 5.3% | 0/8 | FAIL |
| 5 | `momentum_quality` | 41.7 | p80 | -1.42 | 1.65 | 0.76 | 22 | 6.4% | 0/8 | FAIL |
| 6 | `relative_volume` | 41.3 | p76 | -1.45 | 0.99 | 0.70 | 20 | 6.2% | 0/8 | FAIL |
| 7 | `wick_reversal` | 41.0 | p71 | -1.14 | 1.44 | 0.75 | 10 | 4.6% | 1/8 | FAIL |
| 8 | `value_area` | 35.9 | p66 | -1.70 | 1.11 | 0.66 | 18 | 6.0% | 0/8 | FAIL |
| 9 | `acceleration_band` | 35.6 | p61 | -0.68 | 1.11 | 0.87 | 9 | 4.6% | 0/8 | FAIL |
| 10 | `htf_ema` | 34.8 | p57 | -0.91 | 1.31 | 0.85 | 10 | 5.0% | 0/8 | FAIL |
| 11 | `volume_breakout` | 33.3 | p52 | -2.57 | 0.73 | 0.54 | 23 | 8.6% | 0/8 | FAIL |
| 12 | `positional_scaling` | 32.3 | p47 | -1.80 | 2.07 | 0.66 | 8 | 4.2% | 1/8 | FAIL |
| 13 | `linear_channel_rev` | 32.2 | p42 | -0.74 | 1.42 | 1.05 | 5 | 2.5% | 0/8 | FAIL |
| 14 | `lob_maker` | 30.6 | p38 | -2.52 | 1.36 | 0.58 | 28 | 11.7% | 0/8 | FAIL |
| 15 | `supertrend_multi` | 29.4 | p33 | -1.92 | 1.31 | 0.57 | 16 | 6.5% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `engulfing_zone` | +1.94% | 0.52 | 2.11 | 7 | 1/8 | FAIL |
| `linear_channel_rev` | -0.78% | -0.74 | 1.05 | 5 | 0/8 | FAIL |
| `narrow_range` | -1.08% | -0.43 | 0.90 | 14 | 0/8 | FAIL |
| `acceleration_band` | -1.48% | -0.68 | 0.87 | 9 | 0/8 | FAIL |
| `wick_reversal` | -1.86% | -1.14 | 0.75 | 10 | 1/8 | FAIL |
| `htf_ema` | -1.91% | -0.91 | 0.85 | 10 | 0/8 | FAIL |
| `dema_cross` | -1.91% | -2.37 | 0.43 | 6 | 1/8 | FAIL |
| `volatility_cluster` | -2.07% | -0.99 | 0.75 | 16 | 0/8 | FAIL |
| `price_cluster` | -2.10% | -0.92 | 0.85 | 12 | 1/8 | FAIL |
| `positional_scaling` | -2.43% | -1.80 | 0.66 | 8 | 1/8 | FAIL |
| `momentum_quality` | -3.30% | -1.42 | 0.76 | 22 | 0/8 | FAIL |
| `relative_volume` | -3.89% | -1.45 | 0.70 | 20 | 0/8 | FAIL |
| `value_area` | -4.05% | -1.70 | 0.66 | 18 | 0/8 | FAIL |
| `supertrend_multi` | -4.49% | -1.92 | 0.57 | 16 | 0/8 | FAIL |
| `elder_impulse` | -4.56% | -2.34 | 0.60 | 16 | 0/8 | FAIL |
| `roc_ma_cross` | -6.13% | -3.46 | 0.34 | 14 | 0/8 | FAIL |
| `cmf` | -6.66% | -3.14 | 0.44 | 18 | 0/8 | FAIL |
| `volume_breakout` | -7.08% | -2.57 | 0.54 | 23 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -7.16% | -2.59 | 0.52 | 21 | 0/8 | FAIL |
| `price_action_momentum` | -8.02% | -2.89 | 0.51 | 25 | 0/8 | FAIL |
| `frama` | -8.56% | -3.06 | 0.48 | 21 | 0/8 | FAIL |
| `lob_maker` | -9.18% | -2.52 | 0.58 | 28 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `engulfing_zone` | trades 7 < 8 (x2), trades 6 < 8 (x2), sharpe 0.19 < 1.0 (x1) |
| `linear_channel_rev` | trades 4 < 8 (x4), trades 6 < 8 (x2), sharpe -1.10 < 1.0 (x1) |
| `narrow_range` | sharpe -0.32 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), sharpe -0.81 < 1.0 (x1) |
| `acceleration_band` | trades 7 < 8 (x1), sharpe -0.48 < 1.0 (x1), profit_factor 0.82 < 1.5 (x1) |
| `wick_reversal` | sharpe -2.53 < 1.0 (x1), profit_factor 0.32 < 1.5 (x1), sharpe -0.92 < 1.0 (x1) |
| `htf_ema` | sharpe -0.94 < 1.0 (x1), profit_factor 0.70 < 1.5 (x1), sharpe -2.92 < 1.0 (x1) |
| `dema_cross` | trades 7 < 8 (x3), profit_factor 0.00 < 1.5 (x2), trades 5 < 8 (x2) |
| `volatility_cluster` | sharpe -2.05 < 1.0 (x1), profit_factor 0.47 < 1.5 (x1), sharpe -1.28 < 1.0 (x1) |
| `price_cluster` | sharpe 0.10 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1), sharpe 0.04 < 1.0 (x1) |
| `positional_scaling` | profit_factor 0.72 < 1.5 (x2), sharpe -0.79 < 1.0 (x1), sharpe -4.99 < 1.0 (x1) |
| `momentum_quality` | sharpe -2.40 < 1.0 (x1), profit_factor 0.51 < 1.5 (x1), mc_p_value 0.886 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | sharpe -1.39 < 1.0 (x1), profit_factor 0.68 < 1.5 (x1), mc_p_value 0.760 > 0.1 (우연 가능성) (x1) |
| `value_area` | sharpe -1.83 < 1.0 (x1), profit_factor 0.57 < 1.5 (x1), mc_p_value 0.805 > 0.1 (우연 가능성) (x1) |
| `supertrend_multi` | sharpe -2.58 < 1.0 (x1), profit_factor 0.43 < 1.5 (x1), mc_p_value 0.907 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -0.59 < 1.0 (x1), profit_factor 0.82 < 1.5 (x1), mc_p_value 0.582 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -3.56 < 1.0 (x1), profit_factor 0.27 < 1.5 (x1), sharpe -5.54 < 1.0 (x1) |
| `cmf` | sharpe -3.84 < 1.0 (x1), profit_factor 0.28 < 1.5 (x1), sharpe -5.82 < 1.0 (x1) |
| `volume_breakout` | profit_factor 0.51 < 1.5 (x2), sharpe -2.64 < 1.0 (x1), mc_p_value 0.926 > 0.1 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe -3.38 < 1.0 (x1), profit_factor 0.37 < 1.5 (x1), mc_p_value 0.952 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe -2.79 < 1.0 (x1), profit_factor 0.52 < 1.5 (x1), mc_p_value 0.934 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 7 < 8 | 8 |
| profit_factor 0.51 < 1.5 | 7 |
| trades 6 < 8 | 6 |
| trades 4 < 8 | 5 |
| profit_factor 0.59 < 1.5 | 5 |
| profit_factor 0.41 < 1.5 | 5 |
| profit_factor 0.47 < 1.5 | 5 |
| trades 5 < 8 | 4 |
| profit_factor 0.44 < 1.5 | 4 |
| profit_factor 1.04 < 1.5 | 4 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `frama` | 49 | 32 | 0.65 |
| `price_action_momentum` | 69 | 29 | 0.42 |
| `elder_impulse` | 43 | 28 | 0.65 |
| `order_flow_imbalance_v2` | 57 | 26 | 0.46 |
| `lob_maker` | 83 | 26 | 0.31 |
| `cmf` | 59 | 18 | 0.31 |
| `roc_ma_cross` | 41 | 17 | 0.41 |
| `volatility_cluster` | 37 | 14 | 0.38 |
| `volume_breakout` | 76 | 14 | 0.18 |
| `price_cluster` | 24 | 11 | 0.46 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `engulfing_zone` | 0 | 49 | 9 | 15.5% |
| `dema_cross` | 0 | 39 | 7 | 15.2% |
| `frama` | 0 | 148 | 19 | 11.4% |
| `roc_ma_cross` | 0 | 103 | 12 | 10.4% |
| `relative_volume` | 0 | 143 | 16 | 10.1% |
| `lob_maker` | 0 | 201 | 19 | 8.6% |
| `price_action_momentum` | 0 | 182 | 17 | 8.5% |
| `htf_ema` | 0 | 75 | 7 | 8.5% |
| `volume_breakout` | 0 | 171 | 14 | 7.6% |
| `acceleration_band` | 0 | 66 | 5 | 7.0% |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.94% -> $9,606
- **Top 5 균등배분**: -0.65% -> $9,935


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-24T05:12:21.827669Z_
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
| 평균 수익률 | -2.82% |
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
| 1 | `wick_reversal` | 70.3 | p100 | 0.64 | 1.42 | 1.89 | 9 | 3.0% | 2/8 | FAIL |
| 2 | `momentum_quality` | 62.1 | p95 | -0.05 | 0.81 | 1.01 | 22 | 5.9% | 0/8 | FAIL |
| 3 | `engulfing_zone` | 52.8 | p90 | 0.67 | 0.97 | 1.53 | 7 | 3.1% | 0/8 | FAIL |
| 4 | `cmf` | 52.6 | p85 | -0.57 | 1.75 | 0.98 | 17 | 4.9% | 1/8 | FAIL |
| 5 | `elder_impulse` | 52.3 | p80 | -0.12 | 1.56 | 1.04 | 12 | 4.1% | 1/8 | FAIL |
| 6 | `relative_volume` | 43.2 | p76 | -1.28 | 1.60 | 0.77 | 21 | 6.6% | 0/8 | FAIL |
| 7 | `value_area` | 43.0 | p71 | -1.13 | 0.67 | 0.73 | 17 | 6.1% | 0/8 | FAIL |
| 8 | `price_cluster` | 42.5 | p66 | -0.72 | 1.86 | 0.91 | 7 | 4.0% | 2/8 | FAIL |
| 9 | `dema_cross` | 40.8 | p61 | -0.99 | 2.20 | 1.26 | 8 | 3.4% | 1/8 | FAIL |
| 10 | `volatility_cluster` | 38.9 | p57 | -1.43 | 1.22 | 0.70 | 17 | 6.1% | 0/8 | FAIL |
| 11 | `frama` | 37.7 | p52 | -1.26 | 2.17 | 0.87 | 20 | 8.8% | 0/8 | FAIL |
| 12 | `lob_maker` | 35.8 | p47 | -1.92 | 1.19 | 0.65 | 23 | 10.0% | 0/8 | FAIL |
| 13 | `order_flow_imbalance_v2` | 35.3 | p42 | -2.04 | 0.99 | 0.60 | 21 | 8.5% | 0/8 | FAIL |
| 14 | `supertrend_multi` | 32.0 | p38 | -1.46 | 1.73 | 0.69 | 14 | 6.2% | 0/8 | FAIL |
| 15 | `narrow_range` | 28.9 | p33 | -1.86 | 1.45 | 0.61 | 14 | 6.2% | 0/8 | FAIL |

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
| `supertrend_multi` | -3.08% | -1.46 | 0.69 | 14 | 0/8 | FAIL |
| `volatility_cluster` | -3.31% | -1.43 | 0.70 | 17 | 0/8 | FAIL |
| `frama` | -3.42% | -1.26 | 0.87 | 20 | 0/8 | FAIL |
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
| `supertrend_multi` | profit_factor 0.71 < 1.5 (x3), profit_factor 1.34 < 1.5 (x2), sharpe -1.03 < 1.0 (x2) |
| `volatility_cluster` | sharpe -0.85 < 1.0 (x1), profit_factor 0.78 < 1.5 (x1), mc_p_value 0.687 > 0.1 (우연 가능성) (x1) |
| `frama` | mc_p_value 0.174 > 0.1 (우연 가능성) (x1), mc_p_value 0.102 > 0.1 (우연 가능성) (x1), sharpe -0.76 < 1.0 (x1) |
| `narrow_range` | sharpe -2.57 < 1.0 (x1), profit_factor 0.47 < 1.5 (x1), mc_p_value 0.918 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 0.49 < 1.5 (x2), sharpe -2.76 < 1.0 (x1), mc_p_value 0.924 > 0.1 (우연 가능성) (x1) |
| `htf_ema` | sharpe -2.06 < 1.0 (x1), profit_factor 0.47 < 1.5 (x1), sharpe -3.86 < 1.0 (x1) |
| `roc_ma_cross` | sharpe -1.70 < 1.0 (x1), profit_factor 0.55 < 1.5 (x1), sharpe -0.82 < 1.0 (x1) |
| `order_flow_imbalance_v2` | sharpe -2.26 < 1.0 (x1), profit_factor 0.56 < 1.5 (x1), mc_p_value 0.880 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 7 < 8 | 10 |
| trades 6 < 8 | 9 |
| trades 5 < 8 | 6 |
| sharpe 0.07 < 1.0 | 5 |
| profit_factor 1.02 < 1.5 | 5 |
| profit_factor 0.81 < 1.5 | 5 |
| profit_factor 0.63 < 1.5 | 4 |
| profit_factor 0.71 < 1.5 | 4 |
| profit_factor 0.90 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |

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
| `supertrend_multi` | 34 | 17 | 0.50 |
| `volatility_cluster` | 44 | 13 | 0.30 |
| `roc_ma_cross` | 36 | 13 | 0.36 |
| `momentum_quality` | 46 | 12 | 0.26 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 25 | 36 | 59.0% |
| `lob_maker` | 0 | 97 | 88 | 47.6% |
| `supertrend_multi` | 0 | 60 | 52 | 46.4% |
| `engulfing_zone` | 0 | 29 | 25 | 46.3% |
| `frama` | 0 | 89 | 75 | 45.7% |
| `roc_ma_cross` | 0 | 56 | 46 | 45.1% |
| `price_action_momentum` | 0 | 108 | 83 | 43.5% |
| `relative_volume` | 0 | 94 | 72 | 43.4% |
| `momentum_quality` | 0 | 99 | 74 | 42.8% |
| `cmf` | 0 | 77 | 56 | 42.1% |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -2.82% -> $9,718
- **Top 5 균등배분**: +0.44% -> $10,044
