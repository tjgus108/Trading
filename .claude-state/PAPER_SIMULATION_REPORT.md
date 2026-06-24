# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-24T00:11:28.130628Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-24T00:13:15.428337Z_
_Symbol: BTC/USDT_
_Data Source: CSV BTC/USDT 4h (resampled from 1h) (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 20:00:00+00:00 (499일)_
_Walk-Forward: 8개 윈도우 (train=1260, test=360 candles [4h])_
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
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | 0.19% |
| 최고 수익률 | 4.43% (price_cluster) |
| 최저 수익률 | -4.76% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +4.43% | 2.26 | 50.2% | 2.35 | 10 | 4.3% | 0/8 | FAIL |
| 2 | `supertrend_multi` | +4.14% | 2.20 | 30.4% | 1.25 | 8 | 2.3% | 1/8 | FAIL |
| 3 | `momentum_quality` | +3.95% | 1.41 | 41.4% | 1.33 | 22 | 4.8% | 1/8 | FAIL |
| 4 | `relative_volume` | +3.01% | 1.67 | 41.7% | 1.50 | 17 | 4.1% | 0/8 | FAIL |
| 5 | `lob_maker` | +2.17% | 0.73 | 40.4% | 1.27 | 21 | 6.4% | 2/8 | FAIL |
| 6 | `cmf` | +2.04% | 0.84 | 42.5% | 1.21 | 21 | 5.8% | 1/8 | FAIL |
| 7 | `linear_channel_rev` | +1.83% | 1.25 | 43.6% | 2.06 | 6 | 2.1% | 0/8 | FAIL |
| 8 | `value_area` | +0.98% | 0.42 | 40.2% | 1.18 | 16 | 4.6% | 1/8 | FAIL |
| 9 | `elder_impulse` | +0.83% | -1.25 | 32.7% | 1.53 | 14 | 5.9% | 0/8 | FAIL |
| 10 | `price_action_momentum` | +0.75% | -1.15 | 36.9% | 1.09 | 24 | 7.0% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 65.9 | p100 | 1.41 | 3.91 | 1.33 | 22 | 4.8% | 1/8 | FAIL |
| 2 | `lob_maker` | 62.1 | p95 | 0.73 | 3.47 | 1.27 | 21 | 6.4% | 2/8 | FAIL |
| 3 | `cmf` | 60.4 | p90 | 0.84 | 2.76 | 1.21 | 21 | 5.8% | 1/8 | FAIL |
| 4 | `price_cluster` | 60.2 | p85 | 2.26 | 4.10 | 2.35 | 10 | 4.3% | 0/8 | FAIL |
| 5 | `relative_volume` | 60.0 | p80 | 1.67 | 3.10 | 1.50 | 17 | 4.1% | 0/8 | FAIL |
| 6 | `value_area` | 52.6 | p76 | 0.42 | 2.68 | 1.18 | 16 | 4.6% | 1/8 | FAIL |
| 7 | `supertrend_multi` | 52.4 | p71 | 2.20 | 2.92 | 1.25 | 8 | 2.3% | 1/8 | FAIL |
| 8 | `linear_channel_rev` | 47.6 | p66 | 1.25 | 3.34 | 2.06 | 6 | 2.1% | 0/8 | FAIL |
| 9 | `order_flow_imbalance_v2` | 45.3 | p61 | -0.91 | 5.99 | 1.18 | 19 | 6.6% | 2/8 | FAIL |
| 10 | `price_action_momentum` | 42.1 | p57 | -1.15 | 5.78 | 1.09 | 24 | 7.0% | 1/8 | FAIL |
| 11 | `htf_ema` | 37.8 | p52 | -0.65 | 4.18 | 1.55 | 11 | 4.7% | 0/8 | FAIL |
| 12 | `positional_scaling` | 34.6 | p47 | -1.01 | 5.77 | 1.70 | 10 | 4.1% | 0/8 | FAIL |
| 13 | `elder_impulse` | 33.2 | p42 | -1.25 | 6.18 | 1.53 | 14 | 5.9% | 0/8 | FAIL |
| 14 | `volatility_cluster` | 30.0 | p38 | -1.55 | 5.10 | 1.06 | 14 | 5.0% | 0/8 | FAIL |
| 15 | `frama` | 26.7 | p33 | -2.89 | 2.28 | 0.71 | 21 | 7.9% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +4.43% | 2.26 | 2.35 | 10 | 0/8 | FAIL |
| `supertrend_multi` | +4.14% | 2.20 | 1.25 | 8 | 1/8 | FAIL |
| `momentum_quality` | +3.95% | 1.41 | 1.33 | 22 | 1/8 | FAIL |
| `relative_volume` | +3.01% | 1.67 | 1.50 | 17 | 0/8 | FAIL |
| `lob_maker` | +2.17% | 0.73 | 1.27 | 21 | 2/8 | FAIL |
| `cmf` | +2.04% | 0.84 | 1.21 | 21 | 1/8 | FAIL |
| `linear_channel_rev` | +1.83% | 1.25 | 2.06 | 6 | 0/8 | FAIL |
| `value_area` | +0.98% | 0.42 | 1.18 | 16 | 1/8 | FAIL |
| `elder_impulse` | +0.83% | -1.25 | 1.53 | 14 | 0/8 | FAIL |
| `price_action_momentum` | +0.75% | -1.15 | 1.09 | 24 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | +0.53% | -0.91 | 1.18 | 19 | 2/8 | FAIL |
| `positional_scaling` | +0.32% | -1.01 | 1.70 | 10 | 0/8 | FAIL |
| `htf_ema` | +0.17% | -0.65 | 1.55 | 11 | 0/8 | FAIL |
| `volatility_cluster` | -0.90% | -1.55 | 1.06 | 14 | 0/8 | FAIL |
| `volume_breakout` | -1.53% | -2.17 | 0.95 | 18 | 0/8 | FAIL |
| `dema_cross` | -1.56% | -2.90 | 0.49 | 5 | 0/8 | FAIL |
| `roc_ma_cross` | -1.82% | -2.42 | 0.76 | 10 | 0/8 | FAIL |
| `wick_reversal` | -1.97% | -1.93 | 0.92 | 11 | 0/8 | FAIL |
| `engulfing_zone` | -2.54% | -2.96 | 0.59 | 7 | 0/8 | FAIL |
| `narrow_range` | -2.81% | -3.58 | 0.66 | 12 | 0/8 | FAIL |
| `acceleration_band` | -3.02% | -3.42 | 0.65 | 12 | 0/8 | FAIL |
| `frama` | -4.76% | -2.89 | 0.71 | 21 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_cluster` | trades 11 < 15 (x2), trades 5 < 15 (x1), sharpe -3.14 < 1.0 (x1) |
| `supertrend_multi` | no trades generated (x3), trades 13 < 15 (x1), trades 12 < 15 (x1) |
| `momentum_quality` | mc_p_value 0.163 > 0.1 (우연 가능성) (x1), sharpe -1.29 < 1.0 (x1), profit_factor 0.86 < 1.5 (x1) |
| `relative_volume` | mc_p_value 0.314 > 0.1 (우연 가능성) (x2), trades 11 < 15 (x1), mc_p_value 0.129 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | sharpe -1.05 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.612 > 0.1 (우연 가능성) (x1) |
| `cmf` | mc_p_value 0.154 > 0.1 (우연 가능성) (x1), sharpe 0.76 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1) |
| `linear_channel_rev` | trades 5 < 15 (x3), trades 6 < 15 (x2), trades 4 < 15 (x2) |
| `value_area` | profit_factor 1.07 < 1.5 (x2), sharpe 0.49 < 1.0 (x1), mc_p_value 0.456 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | trades 11 < 15 (x2), trades 13 < 15 (x1), sharpe 0.36 < 1.0 (x1) |
| `price_action_momentum` | mc_p_value 0.186 > 0.1 (우연 가능성) (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.382 > 0.1 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.115 > 0.1 (우연 가능성) (x1), profit_factor 1.37 < 1.5 (x1), mc_p_value 0.313 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | trades 7 < 15 (x2), trades 8 < 15 (x2), sharpe -11.76 < 1.0 (x1) |
| `htf_ema` | trades 10 < 15 (x2), trades 13 < 15 (x2), trades 11 < 15 (x2) |
| `volatility_cluster` | trades 14 < 15 (x3), trades 12 < 15 (x2), profit_factor 1.25 < 1.5 (x1) |
| `volume_breakout` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.320 > 0.1 (우연 가능성) (x1), mc_p_value 0.203 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | trades 3 < 15 (x3), trades 8 < 15 (x2), trades 5 < 15 (x2) |
| `roc_ma_cross` | trades 9 < 15 (x3), trades 8 < 15 (x2), profit_factor 1.38 < 1.5 (x1) |
| `wick_reversal` | trades 10 < 15 (x2), profit_factor 1.47 < 1.5 (x1), sharpe -6.84 < 1.0 (x1) |
| `engulfing_zone` | trades 7 < 15 (x3), trades 8 < 15 (x3), profit_factor 0.55 < 1.5 (x2) |
| `narrow_range` | trades 11 < 15 (x2), trades 12 < 15 (x2), trades 9 < 15 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 11 < 15 | 17 |
| trades 8 < 15 | 11 |
| trades 12 < 15 | 11 |
| trades 13 < 15 | 9 |
| trades 10 < 15 | 8 |
| trades 7 < 15 | 8 |
| trades 5 < 15 | 7 |
| trades 14 < 15 | 7 |
| trades 9 < 15 | 6 |
| profit_factor 0.55 < 1.5 | 5 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `elder_impulse` | 32 | 23 | 0.72 |
| `price_action_momentum` | 50 | 17 | 0.34 |
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
| `dema_cross` | 0 | 9 | 30 | 76.9% |
| `relative_volume` | 0 | 67 | 71 | 51.4% |
| `htf_ema` | 0 | 46 | 45 | 49.5% |
| `frama` | 0 | 85 | 82 | 49.1% |
| `roc_ma_cross` | 0 | 40 | 37 | 48.1% |
| `order_flow_imbalance_v2` | 0 | 80 | 71 | 47.0% |
| `narrow_range` | 0 | 50 | 44 | 46.8% |
| `engulfing_zone` | 0 | 30 | 26 | 46.4% |
| `value_area` | 0 | 67 | 58 | 46.4% |
| `linear_channel_rev` | 0 | 25 | 21 | 45.7% |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +0.19% -> $10,019
- **Top 5 균등배분**: +3.54% -> $10,354


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-24T00:15:01.046498Z_
_Symbol: ETH/USDT_
_Data Source: CSV ETH/USDT 4h (resampled from 1h) (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 20:00:00+00:00 (499일)_
_Walk-Forward: 8개 윈도우 (train=1260, test=360 candles [4h])_
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
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -4.17% |
| 최고 수익률 | 1.83% (engulfing_zone) |
| 최저 수익률 | -9.52% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `engulfing_zone` | +1.83% | 0.96 | 47.8% | 2.07 | 7 | 3.4% | 0/8 | FAIL |
| 2 | `linear_channel_rev` | -0.85% | -1.54 | 33.2% | 1.03 | 5 | 2.5% | 0/8 | FAIL |
| 3 | `narrow_range` | -1.27% | -1.00 | 36.6% | 0.88 | 14 | 5.1% | 0/8 | FAIL |
| 4 | `acceleration_band` | -1.59% | -1.46 | 31.6% | 0.85 | 9 | 4.6% | 0/8 | FAIL |
| 5 | `dema_cross` | -1.99% | -4.85 | 23.9% | 0.41 | 6 | 2.8% | 0/8 | FAIL |
| 6 | `wick_reversal` | -2.01% | -2.43 | 34.2% | 0.73 | 10 | 4.7% | 0/8 | FAIL |
| 7 | `htf_ema` | -2.05% | -1.94 | 36.5% | 0.83 | 10 | 5.1% | 0/8 | FAIL |
| 8 | `price_cluster` | -2.26% | -1.98 | 36.4% | 0.83 | 12 | 5.5% | 0/8 | FAIL |
| 9 | `volatility_cluster` | -2.38% | -2.24 | 34.1% | 0.72 | 16 | 5.5% | 0/8 | FAIL |
| 10 | `positional_scaling` | -2.53% | -3.69 | 25.0% | 0.64 | 8 | 4.3% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `engulfing_zone` | 60.1 | p100 | 0.96 | 4.58 | 2.07 | 7 | 3.4% | 0/8 | FAIL |
| 2 | `narrow_range` | 50.0 | p95 | -1.00 | 1.60 | 0.88 | 14 | 5.1% | 0/8 | FAIL |
| 3 | `volatility_cluster` | 46.6 | p90 | -2.24 | 1.22 | 0.72 | 16 | 5.5% | 0/8 | FAIL |
| 4 | `momentum_quality` | 46.0 | p85 | -3.03 | 3.29 | 0.74 | 22 | 6.6% | 0/8 | FAIL |
| 5 | `relative_volume` | 45.5 | p80 | -3.07 | 1.99 | 0.68 | 20 | 6.4% | 0/8 | FAIL |
| 6 | `price_cluster` | 40.8 | p76 | -1.98 | 2.74 | 0.83 | 12 | 5.5% | 0/8 | FAIL |
| 7 | `acceleration_band` | 40.3 | p71 | -1.46 | 2.21 | 0.85 | 9 | 4.6% | 0/8 | FAIL |
| 8 | `value_area` | 40.2 | p66 | -3.56 | 2.22 | 0.64 | 18 | 6.1% | 0/8 | FAIL |
| 9 | `htf_ema` | 39.5 | p61 | -1.94 | 2.62 | 0.83 | 10 | 5.1% | 0/8 | FAIL |
| 10 | `volume_breakout` | 37.4 | p57 | -5.32 | 1.47 | 0.53 | 23 | 8.8% | 0/8 | FAIL |
| 11 | `linear_channel_rev` | 37.1 | p52 | -1.54 | 2.83 | 1.03 | 5 | 2.5% | 0/8 | FAIL |
| 12 | `wick_reversal` | 35.4 | p47 | -2.43 | 2.91 | 0.73 | 10 | 4.7% | 0/8 | FAIL |
| 13 | `lob_maker` | 34.7 | p42 | -5.23 | 2.73 | 0.57 | 28 | 11.9% | 0/8 | FAIL |
| 14 | `supertrend_multi` | 33.2 | p38 | -4.17 | 2.56 | 0.54 | 16 | 6.8% | 0/8 | FAIL |
| 15 | `price_action_momentum` | 32.7 | p33 | -6.05 | 2.15 | 0.49 | 25 | 10.0% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `engulfing_zone` | +1.83% | 0.96 | 2.07 | 7 | 0/8 | FAIL |
| `linear_channel_rev` | -0.85% | -1.54 | 1.03 | 5 | 0/8 | FAIL |
| `narrow_range` | -1.27% | -1.00 | 0.88 | 14 | 0/8 | FAIL |
| `acceleration_band` | -1.59% | -1.46 | 0.85 | 9 | 0/8 | FAIL |
| `dema_cross` | -1.99% | -4.85 | 0.41 | 6 | 0/8 | FAIL |
| `wick_reversal` | -2.01% | -2.43 | 0.73 | 10 | 0/8 | FAIL |
| `htf_ema` | -2.05% | -1.94 | 0.83 | 10 | 0/8 | FAIL |
| `price_cluster` | -2.26% | -1.98 | 0.83 | 12 | 0/8 | FAIL |
| `volatility_cluster` | -2.38% | -2.24 | 0.72 | 16 | 0/8 | FAIL |
| `positional_scaling` | -2.53% | -3.69 | 0.64 | 8 | 0/8 | FAIL |
| `momentum_quality` | -3.56% | -3.03 | 0.74 | 22 | 0/8 | FAIL |
| `relative_volume` | -4.12% | -3.07 | 0.68 | 20 | 0/8 | FAIL |
| `value_area` | -4.24% | -3.56 | 0.64 | 18 | 0/8 | FAIL |
| `elder_impulse` | -4.72% | -4.79 | 0.59 | 16 | 0/8 | FAIL |
| `supertrend_multi` | -4.98% | -4.17 | 0.54 | 16 | 0/8 | FAIL |
| `roc_ma_cross` | -6.17% | -6.94 | 0.34 | 14 | 0/8 | FAIL |
| `cmf` | -7.16% | -6.68 | 0.42 | 18 | 0/8 | FAIL |
| `volume_breakout` | -7.33% | -5.32 | 0.53 | 23 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -7.39% | -5.34 | 0.51 | 21 | 0/8 | FAIL |
| `price_action_momentum` | -8.39% | -6.05 | 0.49 | 25 | 0/8 | FAIL |
| `frama` | -9.05% | -6.42 | 0.46 | 21 | 0/8 | FAIL |
| `lob_maker` | -9.52% | -5.23 | 0.57 | 28 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `engulfing_zone` | trades 7 < 15 (x2), trades 6 < 15 (x2), trades 8 < 15 (x1) |
| `linear_channel_rev` | trades 4 < 15 (x4), trades 6 < 15 (x2), sharpe -2.20 < 1.0 (x1) |
| `narrow_range` | trades 12 < 15 (x2), sharpe -0.83 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1) |
| `acceleration_band` | trades 10 < 15 (x3), trades 7 < 15 (x1), sharpe -1.05 < 1.0 (x1) |
| `dema_cross` | trades 7 < 15 (x3), profit_factor 0.00 < 1.5 (x2), profit_factor 0.24 < 1.5 (x2) |
| `wick_reversal` | trades 8 < 15 (x3), trades 9 < 15 (x3), sharpe -5.14 < 1.0 (x1) |
| `htf_ema` | trades 11 < 15 (x3), trades 9 < 15 (x2), profit_factor 0.58 < 1.5 (x2) |
| `price_cluster` | trades 13 < 15 (x3), trades 12 < 15 (x2), sharpe 0.11 < 1.0 (x1) |
| `volatility_cluster` | profit_factor 0.81 < 1.5 (x2), sharpe -4.31 < 1.0 (x1), profit_factor 0.44 < 1.5 (x1) |
| `positional_scaling` | trades 8 < 15 (x6), profit_factor 0.71 < 1.5 (x2), sharpe -1.66 < 1.0 (x1) |
| `momentum_quality` | profit_factor 0.63 < 1.5 (x2), profit_factor 0.41 < 1.5 (x2), sharpe -4.96 < 1.0 (x1) |
| `relative_volume` | sharpe -2.93 < 1.0 (x1), profit_factor 0.67 < 1.5 (x1), mc_p_value 0.770 > 0.1 (우연 가능성) (x1) |
| `value_area` | profit_factor 0.57 < 1.5 (x2), sharpe -3.75 < 1.0 (x1), mc_p_value 0.813 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | profit_factor 0.10 < 1.5 (x2), sharpe -1.26 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1) |
| `supertrend_multi` | sharpe -6.22 < 1.0 (x1), profit_factor 0.37 < 1.5 (x1), mc_p_value 0.953 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | trades 12 < 15 (x3), trades 14 < 15 (x2), sharpe -7.22 < 1.0 (x1) |
| `cmf` | sharpe -7.77 < 1.0 (x1), profit_factor 0.28 < 1.5 (x1), trades 14 < 15 (x1) |
| `volume_breakout` | profit_factor 0.50 < 1.5 (x2), profit_factor 0.59 < 1.5 (x2), sharpe -5.43 < 1.0 (x1) |
| `order_flow_imbalance_v2` | sharpe -6.93 < 1.0 (x1), profit_factor 0.36 < 1.5 (x1), mc_p_value 0.956 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | profit_factor 0.52 < 1.5 (x2), sharpe -5.77 < 1.0 (x1), profit_factor 0.51 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 8 < 15 | 14 |
| trades 12 < 15 | 9 |
| trades 13 < 15 | 9 |
| trades 7 < 15 | 8 |
| trades 9 < 15 | 7 |
| trades 10 < 15 | 7 |
| trades 14 < 15 | 7 |
| profit_factor 0.50 < 1.5 | 7 |
| trades 6 < 15 | 6 |
| trades 4 < 15 | 5 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `frama` | 51 | 32 | 0.63 |
| `price_action_momentum` | 68 | 29 | 0.43 |
| `elder_impulse` | 43 | 28 | 0.65 |
| `order_flow_imbalance_v2` | 57 | 26 | 0.46 |
| `lob_maker` | 83 | 26 | 0.31 |
| `cmf` | 59 | 20 | 0.34 |
| `roc_ma_cross` | 40 | 17 | 0.42 |
| `volatility_cluster` | 37 | 16 | 0.43 |
| `volume_breakout` | 76 | 14 | 0.18 |
| `price_cluster` | 24 | 11 | 0.46 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 5 | 41 | 89.1% |
| `supertrend_multi` | 0 | 20 | 106 | 84.1% |
| `momentum_quality` | 0 | 52 | 126 | 70.8% |
| `roc_ma_cross` | 0 | 34 | 81 | 70.4% |
| `price_action_momentum` | 0 | 60 | 139 | 69.8% |
| `frama` | 0 | 51 | 118 | 69.8% |
| `relative_volume` | 0 | 52 | 107 | 67.3% |
| `lob_maker` | 0 | 72 | 148 | 67.3% |
| `engulfing_zone` | 0 | 19 | 39 | 67.2% |
| `order_flow_imbalance_v2` | 0 | 56 | 109 | 66.1% |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -4.17% -> $9,583
- **Top 5 균등배분**: -0.78% -> $9,922


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-24T00:16:41.848728Z_
_Symbol: SOL/USDT_
_Data Source: CSV SOL/USDT 4h (resampled from 1h) (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 20:00:00+00:00 (499일)_
_Walk-Forward: 8개 윈도우 (train=1260, test=360 candles [4h])_
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
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -3.13% |
| 최고 수익률 | 1.52% (engulfing_zone) |
| 최저 수익률 | -8.88% (price_action_momentum) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `engulfing_zone` | +1.52% | 1.28 | 45.7% | 1.51 | 7 | 3.1% | 0/8 | FAIL |
| 2 | `wick_reversal` | +1.19% | 1.18 | 43.0% | 1.82 | 9 | 3.0% | 0/8 | FAIL |
| 3 | `elder_impulse` | -0.03% | -0.42 | 35.0% | 1.01 | 13 | 4.3% | 0/8 | FAIL |
| 4 | `price_cluster` | -0.85% | -1.52 | 37.3% | 0.89 | 7 | 4.1% | 0/8 | FAIL |
| 5 | `momentum_quality` | -0.94% | -0.63 | 38.8% | 0.94 | 22 | 6.0% | 0/8 | FAIL |
| 6 | `dema_cross` | -0.94% | -2.05 | 41.4% | 1.25 | 8 | 3.4% | 0/8 | FAIL |
| 7 | `linear_channel_rev` | -1.25% | -3.00 | 33.5% | 0.63 | 5 | 2.5% | 0/8 | FAIL |
| 8 | `cmf` | -1.34% | -1.28 | 39.5% | 0.96 | 17 | 5.0% | 0/8 | FAIL |
| 9 | `acceleration_band` | -2.40% | -2.87 | 26.9% | 0.60 | 8 | 4.4% | 0/8 | FAIL |
| 10 | `value_area` | -2.81% | -2.41 | 35.8% | 0.71 | 17 | 6.2% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 65.7 | p100 | -0.63 | 1.47 | 0.94 | 22 | 6.0% | 0/8 | FAIL |
| 2 | `wick_reversal` | 64.9 | p95 | 1.18 | 2.83 | 1.82 | 9 | 3.0% | 0/8 | FAIL |
| 3 | `engulfing_zone` | 58.2 | p90 | 1.28 | 1.95 | 1.51 | 7 | 3.1% | 0/8 | FAIL |
| 4 | `cmf` | 52.1 | p85 | -1.28 | 3.49 | 0.96 | 17 | 5.0% | 0/8 | FAIL |
| 5 | `elder_impulse` | 52.0 | p80 | -0.42 | 3.07 | 1.01 | 13 | 4.3% | 0/8 | FAIL |
| 6 | `value_area` | 47.8 | p76 | -2.41 | 1.34 | 0.71 | 17 | 6.2% | 0/8 | FAIL |
| 7 | `relative_volume` | 46.9 | p71 | -2.79 | 3.32 | 0.75 | 21 | 6.8% | 0/8 | FAIL |
| 8 | `volatility_cluster` | 42.4 | p66 | -3.25 | 2.62 | 0.67 | 18 | 6.5% | 0/8 | FAIL |
| 9 | `frama` | 42.2 | p61 | -2.65 | 4.36 | 0.85 | 20 | 8.9% | 0/8 | FAIL |
| 10 | `dema_cross` | 40.9 | p57 | -2.05 | 4.43 | 1.25 | 8 | 3.4% | 0/8 | FAIL |
| 11 | `order_flow_imbalance_v2` | 39.9 | p52 | -4.23 | 2.01 | 0.58 | 21 | 8.7% | 0/8 | FAIL |
| 12 | `lob_maker` | 39.6 | p47 | -4.12 | 2.49 | 0.63 | 23 | 10.4% | 0/8 | FAIL |
| 13 | `price_cluster` | 37.5 | p42 | -1.52 | 3.69 | 0.89 | 7 | 4.1% | 0/8 | FAIL |
| 14 | `supertrend_multi` | 35.4 | p38 | -3.26 | 3.20 | 0.61 | 14 | 6.4% | 0/8 | FAIL |
| 15 | `volume_breakout` | 31.0 | p33 | -5.00 | 4.44 | 0.60 | 21 | 8.4% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `engulfing_zone` | +1.52% | 1.28 | 1.51 | 7 | 0/8 | FAIL |
| `wick_reversal` | +1.19% | 1.18 | 1.82 | 9 | 0/8 | FAIL |
| `elder_impulse` | -0.03% | -0.42 | 1.01 | 13 | 0/8 | FAIL |
| `price_cluster` | -0.85% | -1.52 | 0.89 | 7 | 0/8 | FAIL |
| `momentum_quality` | -0.94% | -0.63 | 0.94 | 22 | 0/8 | FAIL |
| `dema_cross` | -0.94% | -2.05 | 1.25 | 8 | 0/8 | FAIL |
| `linear_channel_rev` | -1.25% | -3.00 | 0.63 | 5 | 0/8 | FAIL |
| `cmf` | -1.34% | -1.28 | 0.96 | 17 | 0/8 | FAIL |
| `acceleration_band` | -2.40% | -2.87 | 0.60 | 8 | 0/8 | FAIL |
| `value_area` | -2.81% | -2.41 | 0.71 | 17 | 0/8 | FAIL |
| `positional_scaling` | -3.18% | -3.73 | 0.53 | 10 | 0/8 | FAIL |
| `relative_volume` | -3.21% | -2.79 | 0.75 | 21 | 0/8 | FAIL |
| `supertrend_multi` | -3.42% | -3.26 | 0.61 | 14 | 0/8 | FAIL |
| `frama` | -3.65% | -2.65 | 0.85 | 20 | 0/8 | FAIL |
| `volatility_cluster` | -3.76% | -3.25 | 0.67 | 18 | 0/8 | FAIL |
| `htf_ema` | -5.31% | -6.18 | 0.35 | 11 | 0/8 | FAIL |
| `narrow_range` | -5.36% | -4.64 | 0.51 | 15 | 0/8 | FAIL |
| `volume_breakout` | -5.44% | -5.00 | 0.60 | 21 | 0/8 | FAIL |
| `roc_ma_cross` | -5.44% | -6.48 | 0.36 | 13 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -6.30% | -4.23 | 0.58 | 21 | 0/8 | FAIL |
| `lob_maker` | -7.15% | -4.12 | 0.63 | 23 | 0/8 | FAIL |
| `price_action_momentum` | -8.88% | -6.73 | 0.45 | 24 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `engulfing_zone` | trades 7 < 15 (x4), trades 6 < 15 (x2), profit_factor 1.29 < 1.5 (x1) |
| `wick_reversal` | trades 10 < 15 (x2), trades 9 < 15 (x2), trades 8 < 15 (x2) |
| `elder_impulse` | trades 11 < 15 (x3), mc_p_value 0.209 > 0.1 (우연 가능성) (x1), profit_factor 1.25 < 1.5 (x1) |
| `price_cluster` | trades 8 < 15 (x3), trades 6 < 15 (x2), sharpe -6.88 < 1.0 (x1) |
| `momentum_quality` | sharpe -0.97 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.612 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | trades 9 < 15 (x4), trades 5 < 15 (x2), sharpe 0.06 < 1.0 (x2) |
| `linear_channel_rev` | trades 5 < 15 (x3), trades 6 < 15 (x2), sharpe -6.68 < 1.0 (x1) |
| `cmf` | trades 12 < 15 (x2), sharpe -8.45 < 1.0 (x1), profit_factor 0.30 < 1.5 (x1) |
| `acceleration_band` | trades 8 < 15 (x2), trades 6 < 15 (x2), trades 9 < 15 (x2) |
| `value_area` | sharpe -0.91 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.615 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | trades 10 < 15 (x5), trades 9 < 15 (x2), sharpe -2.31 < 1.0 (x1) |
| `relative_volume` | profit_factor 0.79 < 1.5 (x2), profit_factor 1.20 < 1.5 (x2), sharpe -3.54 < 1.0 (x1) |
| `supertrend_multi` | sharpe -2.16 < 1.0 (x2), profit_factor 0.70 < 1.5 (x2), trades 12 < 15 (x2) |
| `frama` | mc_p_value 0.854 > 0.1 (우연 가능성) (x2), mc_p_value 0.178 > 0.1 (우연 가능성) (x1), mc_p_value 0.107 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -1.85 < 1.0 (x1), profit_factor 0.76 < 1.5 (x1), mc_p_value 0.704 > 0.1 (우연 가능성) (x1) |
| `htf_ema` | trades 10 < 15 (x4), trades 12 < 15 (x2), sharpe -8.35 < 1.0 (x1) |
| `narrow_range` | sharpe -5.36 < 1.0 (x1), profit_factor 0.45 < 1.5 (x1), mc_p_value 0.926 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -5.70 < 1.0 (x1), profit_factor 0.48 < 1.5 (x1), mc_p_value 0.932 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | trades 12 < 15 (x2), sharpe -3.59 < 1.0 (x1), profit_factor 0.53 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe -4.69 < 1.0 (x1), profit_factor 0.54 < 1.5 (x1), mc_p_value 0.885 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 10 < 15 | 13 |
| trades 9 < 15 | 12 |
| trades 8 < 15 | 11 |
| trades 7 < 15 | 9 |
| trades 6 < 15 | 9 |
| trades 12 < 15 | 8 |
| trades 11 < 15 | 6 |
| trades 5 < 15 | 6 |
| profit_factor 0.88 < 1.5 | 4 |
| profit_factor 0.69 < 1.5 | 4 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `price_action_momentum` | 67 | 37 | 0.55 |
| `relative_volume` | 52 | 27 | 0.52 |
| `volume_breakout` | 51 | 26 | 0.51 |
| `order_flow_imbalance_v2` | 52 | 23 | 0.44 |
| `lob_maker` | 65 | 19 | 0.29 |
| `frama` | 49 | 18 | 0.37 |
| `supertrend_multi` | 34 | 17 | 0.50 |
| `volatility_cluster` | 44 | 17 | 0.39 |
| `narrow_range` | 36 | 14 | 0.39 |
| `roc_ma_cross` | 39 | 13 | 0.33 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `engulfing_zone` | 0 | 0 | 54 | 100.0% |
| `wick_reversal` | 0 | 0 | 72 | 100.0% |
| `elder_impulse` | 0 | 0 | 101 | 100.0% |
| `price_cluster` | 0 | 0 | 56 | 100.0% |
| `momentum_quality` | 0 | 0 | 176 | 100.0% |
| `dema_cross` | 0 | 0 | 61 | 100.0% |
| `linear_channel_rev` | 0 | 0 | 41 | 100.0% |
| `cmf` | 0 | 0 | 133 | 100.0% |
| `acceleration_band` | 0 | 0 | 61 | 100.0% |
| `value_area` | 0 | 0 | 133 | 100.0% |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.13% -> $9,687
- **Top 5 균등배분**: +0.18% -> $10,018
