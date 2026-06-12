# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-12T15:19:46.349612Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-12T15:20:58.169593Z_
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
| 평균 수익률 | -0.34% |
| 최고 수익률 | 4.01% (momentum_quality) |
| 최저 수익률 | -6.90% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +4.01% | 1.48 | 41.4% | 1.33 | 22 | 5.1% | 1/8 | FAIL |
| 2 | `supertrend_multi` | +3.57% | 1.84 | 29.7% | 1.14 | 8 | 2.7% | 1/8 | FAIL |
| 3 | `price_cluster` | +3.05% | 1.47 | 45.6% | 1.54 | 12 | 4.3% | 0/8 | FAIL |
| 4 | `relative_volume` | +2.14% | 0.97 | 40.5% | 1.35 | 18 | 4.8% | 0/8 | FAIL |
| 5 | `linear_channel_rev` | +1.82% | 1.23 | 43.6% | 2.01 | 6 | 2.3% | 0/8 | FAIL |
| 6 | `cmf` | +1.75% | 0.59 | 41.5% | 1.16 | 23 | 6.9% | 1/8 | FAIL |
| 7 | `lob_maker` | +1.61% | 0.50 | 39.6% | 1.23 | 21 | 7.6% | 1/8 | FAIL |
| 8 | `elder_impulse` | +0.22% | -1.56 | 31.8% | 1.48 | 14 | 6.5% | 0/8 | FAIL |
| 9 | `htf_ema` | +0.05% | -0.60 | 40.4% | 1.55 | 11 | 5.0% | 0/8 | FAIL |
| 10 | `value_area` | +0.02% | -0.50 | 37.8% | 1.10 | 16 | 5.2% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 69.7 | p100 | 1.48 | 3.81 | 1.33 | 22 | 5.1% | 1/8 | FAIL |
| 2 | `cmf` | 62.0 | p95 | 0.59 | 3.08 | 1.16 | 23 | 6.9% | 1/8 | FAIL |
| 3 | `relative_volume` | 58.6 | p90 | 0.97 | 3.66 | 1.35 | 18 | 4.8% | 0/8 | FAIL |
| 4 | `lob_maker` | 57.4 | p85 | 0.50 | 3.60 | 1.23 | 21 | 7.6% | 1/8 | FAIL |
| 5 | `price_cluster` | 57.1 | p80 | 1.47 | 3.16 | 1.54 | 12 | 4.3% | 0/8 | FAIL |
| 6 | `linear_channel_rev` | 53.0 | p76 | 1.23 | 3.30 | 2.01 | 6 | 2.3% | 0/8 | FAIL |
| 7 | `supertrend_multi` | 51.3 | p71 | 1.84 | 2.92 | 1.14 | 8 | 2.7% | 1/8 | FAIL |
| 8 | `value_area` | 47.6 | p66 | -0.50 | 3.63 | 1.10 | 16 | 5.2% | 1/8 | FAIL |
| 9 | `order_flow_imbalance_v2` | 47.5 | p61 | -1.25 | 6.24 | 1.16 | 19 | 7.6% | 3/8 | FAIL |
| 10 | `htf_ema` | 43.2 | p57 | -0.60 | 4.36 | 1.55 | 11 | 5.0% | 0/8 | FAIL |
| 11 | `price_action_momentum` | 42.5 | p52 | -1.66 | 5.42 | 0.98 | 24 | 7.7% | 1/8 | FAIL |
| 12 | `positional_scaling` | 39.1 | p47 | -1.15 | 5.73 | 1.67 | 10 | 4.5% | 0/8 | FAIL |
| 13 | `volatility_cluster` | 36.7 | p42 | -1.21 | 5.37 | 1.14 | 14 | 5.5% | 0/8 | FAIL |
| 14 | `elder_impulse` | 36.3 | p38 | -1.56 | 6.42 | 1.48 | 14 | 6.5% | 0/8 | FAIL |
| 15 | `volume_breakout` | 31.9 | p33 | -2.40 | 5.40 | 0.91 | 18 | 7.7% | 1/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +4.01% | 1.48 | 1.33 | 22 | 1/8 | FAIL |
| `supertrend_multi` | +3.57% | 1.84 | 1.14 | 8 | 1/8 | FAIL |
| `price_cluster` | +3.05% | 1.47 | 1.54 | 12 | 0/8 | FAIL |
| `relative_volume` | +2.14% | 0.97 | 1.35 | 18 | 0/8 | FAIL |
| `linear_channel_rev` | +1.82% | 1.23 | 2.01 | 6 | 0/8 | FAIL |
| `cmf` | +1.75% | 0.59 | 1.16 | 23 | 1/8 | FAIL |
| `lob_maker` | +1.61% | 0.50 | 1.23 | 21 | 1/8 | FAIL |
| `elder_impulse` | +0.22% | -1.56 | 1.48 | 14 | 0/8 | FAIL |
| `htf_ema` | +0.05% | -0.60 | 1.55 | 11 | 0/8 | FAIL |
| `value_area` | +0.02% | -0.50 | 1.10 | 16 | 1/8 | FAIL |
| `positional_scaling` | -0.01% | -1.15 | 1.67 | 10 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -0.32% | -1.25 | 1.16 | 19 | 3/8 | FAIL |
| `volatility_cluster` | -0.49% | -1.21 | 1.14 | 14 | 0/8 | FAIL |
| `price_action_momentum` | -0.63% | -1.66 | 0.98 | 24 | 1/8 | FAIL |
| `dema_cross` | -1.47% | -2.57 | 0.54 | 5 | 0/8 | FAIL |
| `roc_ma_cross` | -1.70% | -2.16 | 0.81 | 10 | 0/8 | FAIL |
| `wick_reversal` | -1.74% | -1.47 | 0.96 | 11 | 0/8 | FAIL |
| `volume_breakout` | -2.30% | -2.40 | 0.91 | 18 | 1/8 | FAIL |
| `engulfing_zone` | -3.14% | -3.31 | 0.56 | 7 | 0/8 | FAIL |
| `acceleration_band` | -3.16% | -3.33 | 0.68 | 12 | 0/8 | FAIL |
| `narrow_range` | -3.84% | -4.14 | 0.58 | 12 | 0/8 | FAIL |
| `frama` | -6.90% | -4.20 | 0.63 | 21 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.168 > 0.1 (우연 가능성) (x1), sharpe -1.52 < 1.0 (x1) |
| `supertrend_multi` | no trades generated (x3), trades 13 < 15 (x2), trades 12 < 15 (x1) |
| `price_cluster` | trades 11 < 15 (x2), trades 10 < 15 (x2), sharpe -0.21 < 1.0 (x1) |
| `relative_volume` | trades 12 < 15 (x1), mc_p_value 0.110 > 0.1 (우연 가능성) (x1), profit_factor 1.40 < 1.5 (x1) |
| `linear_channel_rev` | trades 5 < 15 (x3), trades 6 < 15 (x2), trades 4 < 15 (x2) |
| `cmf` | mc_p_value 0.202 > 0.1 (우연 가능성) (x1), sharpe 0.75 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1) |
| `lob_maker` | sharpe -2.66 < 1.0 (x1), profit_factor 0.72 < 1.5 (x1), mc_p_value 0.752 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | trades 11 < 15 (x2), trades 13 < 15 (x1), sharpe -0.24 < 1.0 (x1) |
| `htf_ema` | trades 10 < 15 (x2), trades 13 < 15 (x2), trades 11 < 15 (x2) |
| `value_area` | sharpe -0.00 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.492 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | trades 7 < 15 (x2), trades 8 < 15 (x2), sharpe -11.58 < 1.0 (x1) |
| `order_flow_imbalance_v2` | sharpe 0.71 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1), mc_p_value 0.438 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | trades 14 < 15 (x3), trades 12 < 15 (x2), profit_factor 1.36 < 1.5 (x1) |
| `price_action_momentum` | profit_factor 1.18 < 1.5 (x1), mc_p_value 0.353 > 0.1 (우연 가능성) (x1), sharpe 0.98 < 1.0 (x1) |
| `dema_cross` | trades 3 < 15 (x3), profit_factor 0.28 < 1.5 (x2), trades 8 < 15 (x2) |
| `roc_ma_cross` | trades 9 < 15 (x3), trades 8 < 15 (x2), profit_factor 1.24 < 1.5 (x1) |
| `wick_reversal` | trades 10 < 15 (x2), profit_factor 1.42 < 1.5 (x1), sharpe -7.14 < 1.0 (x1) |
| `volume_breakout` | profit_factor 1.19 < 1.5 (x1), mc_p_value 0.373 > 0.1 (우연 가능성) (x1), profit_factor 1.40 < 1.5 (x1) |
| `engulfing_zone` | trades 7 < 15 (x3), trades 8 < 15 (x3), sharpe -7.14 < 1.0 (x1) |
| `acceleration_band` | trades 12 < 15 (x3), trades 11 < 15 (x3), profit_factor 0.30 < 1.5 (x2) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 12 < 15 | 14 |
| trades 11 < 15 | 14 |
| trades 13 < 15 | 10 |
| trades 10 < 15 | 10 |
| trades 8 < 15 | 10 |
| trades 7 < 15 | 7 |
| trades 14 < 15 | 7 |
| trades 5 < 15 | 6 |
| trades 9 < 15 | 5 |
| profit_factor 0.60 < 1.5 | 4 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -0.34% -> $9,966
- **Top 5 균등배분**: +2.92% -> $10,292


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-12T15:22:08.790102Z_
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
| 평균 수익률 | -3.70% |
| 최고 수익률 | 1.77% (acceleration_band) |
| 최저 수익률 | -9.50% (supertrend_multi) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `acceleration_band` | +1.77% | 1.19 | 45.7% | 1.57 | 7 | 2.5% | 0/8 | FAIL |
| 2 | `engulfing_zone` | +1.31% | 0.73 | 37.6% | 1.40 | 7 | 3.1% | 0/8 | FAIL |
| 3 | `dema_cross` | +1.21% | 0.86 | 44.7% | 1.52 | 8 | 2.4% | 0/8 | FAIL |
| 4 | `volatility_cluster` | -1.15% | -0.70 | 40.4% | 1.01 | 16 | 4.6% | 0/8 | FAIL |
| 5 | `price_cluster` | -1.31% | -1.96 | 28.3% | 1.05 | 5 | 3.7% | 0/8 | FAIL |
| 6 | `positional_scaling` | -2.45% | -3.10 | 24.5% | 0.56 | 8 | 4.1% | 0/8 | FAIL |
| 7 | `narrow_range` | -2.49% | -1.92 | 32.7% | 0.81 | 17 | 7.5% | 0/8 | FAIL |
| 8 | `htf_ema` | -2.79% | -2.80 | 25.8% | 0.86 | 9 | 5.6% | 0/8 | FAIL |
| 9 | `wick_reversal` | -2.88% | -3.44 | 31.3% | 0.64 | 10 | 4.8% | 0/8 | FAIL |
| 10 | `linear_channel_rev` | -3.32% | -4.99 | 21.1% | 0.51 | 7 | 4.7% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `acceleration_band` | 62.8 | p100 | 1.19 | 2.43 | 1.57 | 7 | 2.5% | 0/8 | FAIL |
| 2 | `dema_cross` | 62.4 | p95 | 0.86 | 2.80 | 1.52 | 8 | 2.4% | 0/8 | FAIL |
| 3 | `volatility_cluster` | 60.4 | p90 | -0.70 | 2.30 | 1.01 | 16 | 4.6% | 0/8 | FAIL |
| 4 | `engulfing_zone` | 58.9 | p85 | 0.73 | 2.80 | 1.40 | 7 | 3.1% | 0/8 | FAIL |
| 5 | `frama` | 57.1 | p80 | -2.01 | 1.92 | 0.79 | 22 | 9.0% | 0/8 | FAIL |
| 6 | `momentum_quality` | 51.7 | p76 | -3.01 | 4.02 | 0.76 | 24 | 7.8% | 0/8 | FAIL |
| 7 | `narrow_range` | 50.7 | p71 | -1.92 | 2.85 | 0.81 | 17 | 7.5% | 0/8 | FAIL |
| 8 | `order_flow_imbalance_v2` | 46.6 | p66 | -3.18 | 2.89 | 0.70 | 21 | 9.9% | 0/8 | FAIL |
| 9 | `lob_maker` | 45.2 | p61 | -4.06 | 2.17 | 0.62 | 24 | 11.2% | 0/8 | FAIL |
| 10 | `value_area` | 39.4 | p57 | -4.33 | 3.15 | 0.60 | 17 | 6.9% | 0/8 | FAIL |
| 11 | `price_cluster` | 38.6 | p52 | -1.96 | 4.49 | 1.05 | 5 | 3.7% | 0/8 | FAIL |
| 12 | `htf_ema` | 37.7 | p47 | -2.80 | 3.86 | 0.86 | 9 | 5.6% | 0/8 | FAIL |
| 13 | `price_action_momentum` | 37.5 | p42 | -5.17 | 3.40 | 0.56 | 22 | 9.9% | 0/8 | FAIL |
| 14 | `relative_volume` | 35.4 | p38 | -4.82 | 3.03 | 0.53 | 18 | 8.7% | 0/8 | FAIL |
| 15 | `cmf` | 35.3 | p33 | -4.30 | 4.25 | 0.60 | 17 | 8.6% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `acceleration_band` | +1.77% | 1.19 | 1.57 | 7 | 0/8 | FAIL |
| `engulfing_zone` | +1.31% | 0.73 | 1.40 | 7 | 0/8 | FAIL |
| `dema_cross` | +1.21% | 0.86 | 1.52 | 8 | 0/8 | FAIL |
| `volatility_cluster` | -1.15% | -0.70 | 1.01 | 16 | 0/8 | FAIL |
| `price_cluster` | -1.31% | -1.96 | 1.05 | 5 | 0/8 | FAIL |
| `positional_scaling` | -2.45% | -3.10 | 0.56 | 8 | 0/8 | FAIL |
| `narrow_range` | -2.49% | -1.92 | 0.81 | 17 | 0/8 | FAIL |
| `htf_ema` | -2.79% | -2.80 | 0.86 | 9 | 0/8 | FAIL |
| `wick_reversal` | -2.88% | -3.44 | 0.64 | 10 | 0/8 | FAIL |
| `linear_channel_rev` | -3.32% | -4.99 | 0.51 | 7 | 0/8 | FAIL |
| `roc_ma_cross` | -3.53% | -4.17 | 0.59 | 10 | 0/8 | FAIL |
| `momentum_quality` | -3.59% | -3.01 | 0.76 | 24 | 0/8 | FAIL |
| `frama` | -3.95% | -2.01 | 0.79 | 22 | 0/8 | FAIL |
| `value_area` | -5.00% | -4.33 | 0.60 | 17 | 0/8 | FAIL |
| `cmf` | -5.33% | -4.30 | 0.60 | 17 | 0/8 | FAIL |
| `elder_impulse` | -5.60% | -4.84 | 0.56 | 14 | 0/8 | FAIL |
| `volume_breakout` | -5.76% | -5.10 | 0.60 | 16 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -5.77% | -3.18 | 0.70 | 21 | 0/8 | FAIL |
| `relative_volume` | -6.02% | -4.82 | 0.53 | 18 | 0/8 | FAIL |
| `price_action_momentum` | -7.23% | -5.17 | 0.56 | 22 | 0/8 | FAIL |
| `lob_maker` | -7.96% | -4.06 | 0.62 | 24 | 0/8 | FAIL |
| `supertrend_multi` | -9.50% | -7.40 | 0.37 | 17 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `acceleration_band` | trades 9 < 15 (x2), trades 6 < 15 (x2), trades 5 < 15 (x1) |
| `engulfing_zone` | trades 7 < 15 (x4), trades 8 < 15 (x3), sharpe -0.87 < 1.0 (x1) |
| `dema_cross` | trades 7 < 15 (x4), sharpe -3.55 < 1.0 (x1), profit_factor 0.43 < 1.5 (x1) |
| `volatility_cluster` | trades 14 < 15 (x2), trades 12 < 15 (x1), sharpe -0.14 < 1.0 (x1) |
| `price_cluster` | trades 5 < 15 (x2), trades 2 < 15 (x2), profit_factor 0.00 < 1.5 (x2) |
| `positional_scaling` | trades 7 < 15 (x3), trades 8 < 15 (x2), sharpe -3.84 < 1.0 (x1) |
| `narrow_range` | sharpe 0.37 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), trades 14 < 15 (x1) |
| `htf_ema` | trades 12 < 15 (x2), trades 8 < 15 (x2), trades 9 < 15 (x2) |
| `wick_reversal` | trades 9 < 15 (x2), trades 11 < 15 (x2), sharpe -1.52 < 1.0 (x1) |
| `linear_channel_rev` | profit_factor 0.00 < 1.5 (x3), trades 6 < 15 (x3), trades 8 < 15 (x2) |
| `roc_ma_cross` | trades 10 < 15 (x3), trades 8 < 15 (x3), sharpe -4.74 < 1.0 (x1) |
| `momentum_quality` | profit_factor 0.88 < 1.5 (x2), sharpe -10.13 < 1.0 (x1), profit_factor 0.22 < 1.5 (x1) |
| `frama` | sharpe -0.79 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.568 > 0.1 (우연 가능성) (x1) |
| `value_area` | profit_factor 1.08 < 1.5 (x2), sharpe -3.84 < 1.0 (x1), profit_factor 0.60 < 1.5 (x1) |
| `cmf` | sharpe -3.19 < 1.0 (x1), profit_factor 0.59 < 1.5 (x1), mc_p_value 0.791 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | trades 10 < 15 (x2), sharpe -5.08 < 1.0 (x1), profit_factor 0.42 < 1.5 (x1) |
| `volume_breakout` | trades 14 < 15 (x2), trades 13 < 15 (x2), profit_factor 0.83 < 1.5 (x2) |
| `order_flow_imbalance_v2` | profit_factor 0.71 < 1.5 (x2), profit_factor 0.84 < 1.5 (x2), sharpe -4.09 < 1.0 (x1) |
| `relative_volume` | sharpe -6.14 < 1.0 (x1), profit_factor 0.39 < 1.5 (x1), mc_p_value 0.937 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe -0.65 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.554 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 7 < 15 | 16 |
| trades 8 < 15 | 15 |
| trades 9 < 15 | 11 |
| trades 6 < 15 | 11 |
| trades 10 < 15 | 7 |
| trades 13 < 15 | 6 |
| profit_factor 0.33 < 1.5 | 5 |
| trades 14 < 15 | 5 |
| trades 12 < 15 | 5 |
| profit_factor 0.00 < 1.5 | 5 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.70% -> $9,630
- **Top 5 균등배분**: +0.36% -> $10,036


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-12T15:23:19.277269Z_
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
| 평균 수익률 | -3.83% |
| 최고 수익률 | 3.15% (narrow_range) |
| 최저 수익률 | -8.59% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `narrow_range` | +3.15% | 1.72 | 47.8% | 1.52 | 16 | 3.8% | 1/8 | FAIL |
| 2 | `acceleration_band` | +0.36% | -0.07 | 40.1% | 1.33 | 7 | 2.7% | 0/8 | FAIL |
| 3 | `linear_channel_rev` | +0.03% | -0.99 | 29.9% | 1.12 | 6 | 3.0% | 0/8 | FAIL |
| 4 | `wick_reversal` | -1.14% | -2.07 | 37.7% | 0.88 | 6 | 2.9% | 0/8 | FAIL |
| 5 | `value_area` | -2.24% | -2.59 | 37.3% | 1.16 | 17 | 6.7% | 0/8 | FAIL |
| 6 | `price_cluster` | -2.31% | -2.63 | 35.9% | 0.69 | 7 | 4.1% | 0/8 | FAIL |
| 7 | `engulfing_zone` | -2.52% | -2.56 | 34.7% | 0.66 | 8 | 4.8% | 0/8 | FAIL |
| 8 | `momentum_quality` | -2.57% | -2.18 | 32.6% | 0.86 | 23 | 7.2% | 1/8 | FAIL |
| 9 | `volatility_cluster` | -2.70% | -1.93 | 34.2% | 0.81 | 20 | 6.1% | 0/8 | FAIL |
| 10 | `supertrend_multi` | -3.02% | -2.53 | 29.8% | 0.75 | 12 | 6.1% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `narrow_range` | 81.2 | p100 | 1.72 | 3.32 | 1.52 | 16 | 3.8% | 1/8 | FAIL |
| 2 | `momentum_quality` | 62.9 | p95 | -2.18 | 3.74 | 0.86 | 23 | 7.2% | 1/8 | FAIL |
| 3 | `volatility_cluster` | 53.1 | p90 | -1.93 | 2.43 | 0.81 | 20 | 6.1% | 0/8 | FAIL |
| 4 | `acceleration_band` | 48.0 | p85 | -0.07 | 3.30 | 1.33 | 7 | 2.7% | 0/8 | FAIL |
| 5 | `value_area` | 45.8 | p80 | -2.59 | 5.28 | 1.16 | 17 | 6.7% | 0/8 | FAIL |
| 6 | `frama` | 43.3 | p76 | -2.87 | 4.02 | 0.78 | 24 | 10.8% | 0/8 | FAIL |
| 7 | `linear_channel_rev` | 40.4 | p71 | -0.99 | 4.12 | 1.12 | 6 | 3.0% | 0/8 | FAIL |
| 8 | `htf_ema` | 36.8 | p66 | -3.68 | 5.07 | 1.31 | 10 | 5.9% | 0/8 | FAIL |
| 9 | `supertrend_multi` | 36.7 | p61 | -2.53 | 3.23 | 0.75 | 12 | 6.1% | 0/8 | FAIL |
| 10 | `lob_maker` | 34.9 | p57 | -5.26 | 2.26 | 0.51 | 21 | 9.7% | 0/8 | FAIL |
| 11 | `price_action_momentum` | 34.1 | p52 | -4.73 | 4.12 | 0.59 | 21 | 8.6% | 0/8 | FAIL |
| 12 | `wick_reversal` | 32.6 | p47 | -2.07 | 3.65 | 0.88 | 6 | 2.9% | 0/8 | FAIL |
| 13 | `engulfing_zone` | 31.4 | p42 | -2.56 | 2.87 | 0.66 | 8 | 4.8% | 0/8 | FAIL |
| 14 | `order_flow_imbalance_v2` | 29.5 | p38 | -5.76 | 3.89 | 0.53 | 23 | 10.9% | 0/8 | FAIL |
| 15 | `price_cluster` | 29.3 | p33 | -2.63 | 3.04 | 0.69 | 7 | 4.1% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `narrow_range` | +3.15% | 1.72 | 1.52 | 16 | 1/8 | FAIL |
| `acceleration_band` | +0.36% | -0.07 | 1.33 | 7 | 0/8 | FAIL |
| `linear_channel_rev` | +0.03% | -0.99 | 1.12 | 6 | 0/8 | FAIL |
| `wick_reversal` | -1.14% | -2.07 | 0.88 | 6 | 0/8 | FAIL |
| `value_area` | -2.24% | -2.59 | 1.16 | 17 | 0/8 | FAIL |
| `price_cluster` | -2.31% | -2.63 | 0.69 | 7 | 0/8 | FAIL |
| `engulfing_zone` | -2.52% | -2.56 | 0.66 | 8 | 0/8 | FAIL |
| `momentum_quality` | -2.57% | -2.18 | 0.86 | 23 | 1/8 | FAIL |
| `volatility_cluster` | -2.70% | -1.93 | 0.81 | 20 | 0/8 | FAIL |
| `supertrend_multi` | -3.02% | -2.53 | 0.75 | 12 | 0/8 | FAIL |
| `htf_ema` | -3.05% | -3.68 | 1.31 | 10 | 0/8 | FAIL |
| `volume_breakout` | -3.54% | -3.73 | 0.57 | 10 | 0/8 | FAIL |
| `positional_scaling` | -4.40% | -4.53 | 0.43 | 10 | 0/8 | FAIL |
| `frama` | -4.70% | -2.87 | 0.78 | 24 | 0/8 | FAIL |
| `dema_cross` | -4.73% | -6.22 | 0.26 | 12 | 0/8 | FAIL |
| `roc_ma_cross` | -4.80% | -5.13 | 0.49 | 14 | 0/8 | FAIL |
| `price_action_momentum` | -6.10% | -4.73 | 0.59 | 21 | 0/8 | FAIL |
| `elder_impulse` | -6.52% | -5.76 | 0.64 | 16 | 0/8 | FAIL |
| `cmf` | -7.94% | -6.57 | 0.40 | 19 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -8.25% | -5.76 | 0.53 | 23 | 0/8 | FAIL |
| `relative_volume` | -8.58% | -7.81 | 0.38 | 22 | 0/8 | FAIL |
| `lob_maker` | -8.59% | -5.26 | 0.51 | 21 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `narrow_range` | sharpe 0.30 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1), mc_p_value 0.492 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | trades 7 < 15 (x4), trades 6 < 15 (x2), trades 5 < 15 (x1) |
| `linear_channel_rev` | trades 7 < 15 (x3), sharpe -0.81 < 1.0 (x1), profit_factor 0.84 < 1.5 (x1) |
| `wick_reversal` | trades 6 < 15 (x4), trades 5 < 15 (x2), sharpe -6.20 < 1.0 (x1) |
| `value_area` | profit_factor 0.52 < 1.5 (x2), trades 14 < 15 (x2), sharpe -4.84 < 1.0 (x1) |
| `price_cluster` | trades 8 < 15 (x3), trades 6 < 15 (x2), trades 4 < 15 (x2) |
| `engulfing_zone` | trades 6 < 15 (x3), sharpe -0.90 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1) |
| `momentum_quality` | sharpe -2.83 < 1.0 (x1), profit_factor 0.71 < 1.5 (x1), mc_p_value 0.763 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.372 > 0.1 (우연 가능성) (x1), sharpe -1.29 < 1.0 (x1) |
| `supertrend_multi` | trades 7 < 15 (x2), sharpe -0.25 < 1.0 (x1), profit_factor 0.94 < 1.5 (x1) |
| `htf_ema` | trades 10 < 15 (x2), trades 9 < 15 (x2), trades 7 < 15 (x2) |
| `volume_breakout` | trades 11 < 15 (x3), trades 12 < 15 (x2), sharpe -7.14 < 1.0 (x1) |
| `positional_scaling` | trades 12 < 15 (x2), trades 11 < 15 (x2), sharpe -4.48 < 1.0 (x1) |
| `frama` | sharpe -4.39 < 1.0 (x1), profit_factor 0.59 < 1.5 (x1), mc_p_value 0.874 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | trades 7 < 15 (x2), trades 14 < 15 (x2), sharpe -6.53 < 1.0 (x1) |
| `roc_ma_cross` | trades 10 < 15 (x2), trades 13 < 15 (x2), profit_factor 0.63 < 1.5 (x2) |
| `price_action_momentum` | profit_factor 0.48 < 1.5 (x2), sharpe -5.47 < 1.0 (x1), mc_p_value 0.925 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | mc_p_value 1.000 > 0.1 (우연 가능성) (x2), trades 9 < 15 (x2), sharpe -10.37 < 1.0 (x1) |
| `cmf` | sharpe -1.55 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1), mc_p_value 0.657 > 0.1 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.998 > 0.1 (우연 가능성) (x2), sharpe -6.92 < 1.0 (x1), profit_factor 0.43 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 7 < 15 | 15 |
| trades 6 < 15 | 11 |
| trades 8 < 15 | 9 |
| trades 9 < 15 | 9 |
| trades 11 < 15 | 8 |
| trades 12 < 15 | 7 |
| trades 10 < 15 | 7 |
| trades 5 < 15 | 6 |
| profit_factor 0.52 < 1.5 | 6 |
| profit_factor 0.38 < 1.5 | 6 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.83% -> $9,617
- **Top 5 균등배분**: +0.03% -> $10,003
