# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-11T10:26:18.076830Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-11T10:27:33.824209Z_
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
| 평균 수익률 | 0.42% |
| 최고 수익률 | 7.11% (price_cluster) |
| 최저 수익률 | -5.18% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +7.11% | 3.72 | 52.0% | 2.17 | 12 | 4.1% | 2/8 | FAIL |
| 2 | `momentum_quality` | +4.64% | 1.82 | 41.4% | 1.39 | 22 | 4.9% | 1/8 | FAIL |
| 3 | `supertrend_multi` | +4.15% | 2.14 | 30.4% | 1.22 | 8 | 2.6% | 1/8 | FAIL |
| 4 | `relative_volume` | +3.62% | 1.84 | 42.0% | 1.63 | 19 | 4.7% | 1/8 | FAIL |
| 5 | `cmf` | +3.21% | 1.25 | 41.8% | 1.24 | 23 | 6.3% | 1/8 | FAIL |
| 6 | `lob_maker` | +2.96% | 1.18 | 40.4% | 1.32 | 21 | 6.8% | 1/8 | FAIL |
| 7 | `linear_channel_rev` | +1.98% | 1.39 | 43.6% | 2.12 | 6 | 2.2% | 0/8 | FAIL |
| 8 | `order_flow_imbalance_v2` | +1.66% | 0.26 | 40.0% | 1.34 | 20 | 7.1% | 3/8 | FAIL |
| 9 | `value_area` | +1.46% | 0.76 | 40.2% | 1.25 | 16 | 5.0% | 1/8 | FAIL |
| 10 | `htf_ema` | +0.70% | 0.02 | 40.4% | 1.65 | 11 | 4.8% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 71.5 | p100 | 3.72 | 2.34 | 2.17 | 12 | 4.1% | 2/8 | FAIL |
| 2 | `momentum_quality` | 62.9 | p95 | 1.82 | 3.71 | 1.39 | 22 | 4.9% | 1/8 | FAIL |
| 3 | `relative_volume` | 61.0 | p90 | 1.84 | 3.94 | 1.63 | 19 | 4.7% | 1/8 | FAIL |
| 4 | `cmf` | 58.7 | p85 | 1.25 | 2.69 | 1.24 | 23 | 6.3% | 1/8 | FAIL |
| 5 | `lob_maker` | 54.5 | p80 | 1.18 | 3.25 | 1.32 | 21 | 6.8% | 1/8 | FAIL |
| 6 | `order_flow_imbalance_v2` | 51.4 | p76 | 0.26 | 5.37 | 1.34 | 20 | 7.1% | 3/8 | FAIL |
| 7 | `value_area` | 49.0 | p71 | 0.76 | 2.61 | 1.25 | 16 | 5.0% | 1/8 | FAIL |
| 8 | `linear_channel_rev` | 45.4 | p66 | 1.39 | 3.29 | 2.12 | 6 | 2.2% | 0/8 | FAIL |
| 9 | `supertrend_multi` | 44.2 | p61 | 2.14 | 2.92 | 1.22 | 8 | 2.6% | 1/8 | FAIL |
| 10 | `htf_ema` | 39.7 | p57 | 0.02 | 3.92 | 1.65 | 11 | 4.8% | 0/8 | FAIL |
| 11 | `price_action_momentum` | 37.8 | p52 | -1.00 | 5.77 | 1.11 | 24 | 7.9% | 1/8 | FAIL |
| 12 | `positional_scaling` | 32.4 | p47 | -0.97 | 5.83 | 1.75 | 10 | 4.9% | 0/8 | FAIL |
| 13 | `elder_impulse` | 31.9 | p42 | -0.93 | 5.99 | 1.58 | 14 | 7.3% | 0/8 | FAIL |
| 14 | `wick_reversal` | 28.8 | p38 | -0.92 | 2.81 | 1.02 | 11 | 4.3% | 0/8 | FAIL |
| 15 | `volatility_cluster` | 27.0 | p33 | -2.17 | 4.80 | 0.88 | 21 | 7.6% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +7.11% | 3.72 | 2.17 | 12 | 2/8 | FAIL |
| `momentum_quality` | +4.64% | 1.82 | 1.39 | 22 | 1/8 | FAIL |
| `supertrend_multi` | +4.15% | 2.14 | 1.22 | 8 | 1/8 | FAIL |
| `relative_volume` | +3.62% | 1.84 | 1.63 | 19 | 1/8 | FAIL |
| `cmf` | +3.21% | 1.25 | 1.24 | 23 | 1/8 | FAIL |
| `lob_maker` | +2.96% | 1.18 | 1.32 | 21 | 1/8 | FAIL |
| `linear_channel_rev` | +1.98% | 1.39 | 2.12 | 6 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | +1.66% | 0.26 | 1.34 | 20 | 3/8 | FAIL |
| `value_area` | +1.46% | 0.76 | 1.25 | 16 | 1/8 | FAIL |
| `htf_ema` | +0.70% | 0.02 | 1.65 | 11 | 0/8 | FAIL |
| `price_action_momentum` | +0.59% | -1.00 | 1.11 | 24 | 1/8 | FAIL |
| `elder_impulse` | +0.24% | -0.93 | 1.58 | 14 | 0/8 | FAIL |
| `positional_scaling` | -0.22% | -0.97 | 1.75 | 10 | 0/8 | FAIL |
| `wick_reversal` | -1.26% | -0.92 | 1.02 | 11 | 0/8 | FAIL |
| `dema_cross` | -1.36% | -2.42 | 0.57 | 5 | 0/8 | FAIL |
| `roc_ma_cross` | -1.64% | -2.12 | 0.83 | 10 | 0/8 | FAIL |
| `volume_breakout` | -1.82% | -1.99 | 0.98 | 18 | 1/8 | FAIL |
| `volatility_cluster` | -2.53% | -2.17 | 0.88 | 21 | 0/8 | FAIL |
| `narrow_range` | -2.85% | -3.11 | 0.71 | 12 | 0/8 | FAIL |
| `engulfing_zone` | -2.91% | -2.88 | 0.60 | 7 | 0/8 | FAIL |
| `acceleration_band` | -3.35% | -3.34 | 0.70 | 12 | 0/8 | FAIL |
| `frama` | -5.18% | -2.82 | 0.73 | 21 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_cluster` | trades 10 < 15 (x2), trades 9 < 15 (x1), trades 11 < 15 (x1) |
| `momentum_quality` | profit_factor 1.50 < 1.5 (x1), mc_p_value 0.158 > 0.1 (우연 가능성) (x1), sharpe -1.35 < 1.0 (x1) |
| `supertrend_multi` | no trades generated (x3), trades 13 < 15 (x1), trades 12 < 15 (x1) |
| `relative_volume` | trades 13 < 15 (x1), mc_p_value 0.155 > 0.1 (우연 가능성) (x1), sharpe -1.38 < 1.0 (x1) |
| `cmf` | mc_p_value 0.195 > 0.1 (우연 가능성) (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.408 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 0.93 < 1.5 (x2), sharpe -0.16 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1) |
| `linear_channel_rev` | trades 5 < 15 (x3), trades 6 < 15 (x2), trades 4 < 15 (x2) |
| `order_flow_imbalance_v2` | mc_p_value 0.192 > 0.1 (우연 가능성) (x1), sharpe -7.98 < 1.0 (x1), profit_factor 0.31 < 1.5 (x1) |
| `value_area` | sharpe -0.20 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1), mc_p_value 0.513 > 0.1 (우연 가능성) (x1) |
| `htf_ema` | trades 10 < 15 (x2), trades 13 < 15 (x2), trades 11 < 15 (x2) |
| `price_action_momentum` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.221 > 0.1 (우연 가능성) (x1), profit_factor 1.16 < 1.5 (x1) |
| `elder_impulse` | trades 11 < 15 (x2), trades 13 < 15 (x1), sharpe 0.38 < 1.0 (x1) |
| `positional_scaling` | trades 7 < 15 (x2), trades 8 < 15 (x2), sharpe -12.32 < 1.0 (x1) |
| `wick_reversal` | trades 10 < 15 (x2), profit_factor 1.49 < 1.5 (x1), sharpe -4.25 < 1.0 (x1) |
| `dema_cross` | trades 3 < 15 (x3), profit_factor 0.31 < 1.5 (x2), trades 8 < 15 (x2) |
| `roc_ma_cross` | trades 9 < 15 (x3), profit_factor 0.35 < 1.5 (x2), trades 8 < 15 (x2) |
| `volume_breakout` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.311 > 0.1 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.28 < 1.5 (x1), mc_p_value 0.285 > 0.1 (우연 가능성) (x1), profit_factor 1.20 < 1.5 (x1) |
| `narrow_range` | trades 11 < 15 (x2), profit_factor 0.87 < 1.5 (x2), trades 12 < 15 (x2) |
| `engulfing_zone` | trades 7 < 15 (x3), trades 8 < 15 (x3), sharpe -6.90 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 11 < 15 | 15 |
| trades 8 < 15 | 11 |
| trades 12 < 15 | 10 |
| trades 10 < 15 | 9 |
| trades 13 < 15 | 9 |
| trades 9 < 15 | 7 |
| trades 7 < 15 | 7 |
| trades 5 < 15 | 6 |
| profit_factor 0.98 < 1.5 | 5 |
| profit_factor 0.77 < 1.5 | 4 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +0.42% -> $10,042
- **Top 5 균등배분**: +4.54% -> $10,454


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-11T10:28:48.105690Z_
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
| 평균 수익률 | -3.75% |
| 최고 수익률 | 1.88% (acceleration_band) |
| 최저 수익률 | -10.01% (supertrend_multi) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `acceleration_band` | +1.88% | 1.29 | 45.7% | 1.61 | 7 | 2.5% | 0/8 | FAIL |
| 2 | `engulfing_zone` | +1.63% | 0.98 | 37.6% | 1.47 | 7 | 3.0% | 0/8 | FAIL |
| 3 | `dema_cross` | +1.27% | 0.94 | 44.7% | 1.55 | 8 | 2.4% | 0/8 | FAIL |
| 4 | `price_cluster` | -1.76% | -1.78 | 31.0% | 0.75 | 7 | 4.4% | 0/8 | FAIL |
| 5 | `positional_scaling` | -2.26% | -2.82 | 24.5% | 0.59 | 8 | 4.1% | 0/8 | FAIL |
| 6 | `htf_ema` | -2.44% | -2.09 | 25.8% | 0.93 | 9 | 5.6% | 0/8 | FAIL |
| 7 | `roc_ma_cross` | -2.71% | -3.00 | 27.0% | 0.67 | 10 | 4.7% | 0/8 | FAIL |
| 8 | `narrow_range` | -2.76% | -1.97 | 33.0% | 0.81 | 17 | 8.0% | 0/8 | FAIL |
| 9 | `frama` | -2.85% | -1.27 | 31.0% | 0.86 | 22 | 8.1% | 0/8 | FAIL |
| 10 | `wick_reversal` | -2.87% | -3.28 | 32.9% | 0.67 | 10 | 4.8% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `acceleration_band` | 61.2 | p100 | 1.29 | 2.42 | 1.61 | 7 | 2.5% | 0/8 | FAIL |
| 2 | `dema_cross` | 60.7 | p95 | 0.94 | 2.79 | 1.55 | 8 | 2.4% | 0/8 | FAIL |
| 3 | `frama` | 60.6 | p90 | -1.27 | 1.45 | 0.86 | 22 | 8.1% | 0/8 | FAIL |
| 4 | `engulfing_zone` | 58.4 | p85 | 0.98 | 2.74 | 1.47 | 7 | 3.0% | 0/8 | FAIL |
| 5 | `order_flow_imbalance_v2` | 52.1 | p80 | -2.51 | 2.03 | 0.76 | 23 | 9.7% | 0/8 | FAIL |
| 6 | `momentum_quality` | 51.6 | p76 | -2.75 | 3.40 | 0.76 | 24 | 8.0% | 0/8 | FAIL |
| 7 | `volatility_cluster` | 49.4 | p71 | -2.48 | 2.83 | 0.76 | 20 | 6.9% | 0/8 | FAIL |
| 8 | `narrow_range` | 46.8 | p66 | -1.97 | 2.85 | 0.81 | 17 | 8.0% | 0/8 | FAIL |
| 9 | `lob_maker` | 43.6 | p61 | -3.68 | 2.30 | 0.65 | 24 | 11.2% | 0/8 | FAIL |
| 10 | `value_area` | 39.6 | p57 | -3.68 | 3.10 | 0.65 | 17 | 6.9% | 0/8 | FAIL |
| 11 | `htf_ema` | 38.7 | p52 | -2.09 | 3.27 | 0.93 | 9 | 5.6% | 0/8 | FAIL |
| 12 | `price_cluster` | 35.3 | p47 | -1.78 | 2.13 | 0.75 | 7 | 4.4% | 0/8 | FAIL |
| 13 | `relative_volume` | 34.8 | p42 | -4.79 | 2.22 | 0.53 | 19 | 9.0% | 0/8 | FAIL |
| 14 | `roc_ma_cross` | 33.8 | p38 | -3.00 | 2.81 | 0.67 | 10 | 4.7% | 0/8 | FAIL |
| 15 | `price_action_momentum` | 32.9 | p33 | -5.10 | 3.33 | 0.57 | 22 | 11.0% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `acceleration_band` | +1.88% | 1.29 | 1.61 | 7 | 0/8 | FAIL |
| `engulfing_zone` | +1.63% | 0.98 | 1.47 | 7 | 0/8 | FAIL |
| `dema_cross` | +1.27% | 0.94 | 1.55 | 8 | 0/8 | FAIL |
| `price_cluster` | -1.76% | -1.78 | 0.75 | 7 | 0/8 | FAIL |
| `positional_scaling` | -2.26% | -2.82 | 0.59 | 8 | 0/8 | FAIL |
| `htf_ema` | -2.44% | -2.09 | 0.93 | 9 | 0/8 | FAIL |
| `roc_ma_cross` | -2.71% | -3.00 | 0.67 | 10 | 0/8 | FAIL |
| `narrow_range` | -2.76% | -1.97 | 0.81 | 17 | 0/8 | FAIL |
| `frama` | -2.85% | -1.27 | 0.86 | 22 | 0/8 | FAIL |
| `wick_reversal` | -2.87% | -3.28 | 0.67 | 10 | 0/8 | FAIL |
| `linear_channel_rev` | -3.12% | -4.58 | 0.54 | 7 | 0/8 | FAIL |
| `volatility_cluster` | -3.17% | -2.48 | 0.76 | 20 | 0/8 | FAIL |
| `momentum_quality` | -3.75% | -2.75 | 0.76 | 24 | 0/8 | FAIL |
| `value_area` | -4.67% | -3.68 | 0.65 | 17 | 0/8 | FAIL |
| `volume_breakout` | -5.25% | -3.93 | 0.72 | 15 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -5.28% | -2.51 | 0.76 | 23 | 0/8 | FAIL |
| `elder_impulse` | -6.15% | -4.90 | 0.57 | 14 | 0/8 | FAIL |
| `cmf` | -6.35% | -4.51 | 0.56 | 18 | 0/8 | FAIL |
| `relative_volume` | -6.39% | -4.79 | 0.53 | 19 | 0/8 | FAIL |
| `lob_maker` | -7.49% | -3.68 | 0.65 | 24 | 0/8 | FAIL |
| `price_action_momentum` | -7.94% | -5.10 | 0.57 | 22 | 0/8 | FAIL |
| `supertrend_multi` | -10.01% | -6.81 | 0.40 | 17 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `acceleration_band` | trades 9 < 15 (x2), trades 6 < 15 (x2), trades 5 < 15 (x1) |
| `engulfing_zone` | trades 7 < 15 (x4), trades 8 < 15 (x3), sharpe -0.75 < 1.0 (x1) |
| `dema_cross` | trades 7 < 15 (x4), sharpe -3.45 < 1.0 (x1), profit_factor 0.44 < 1.5 (x1) |
| `price_cluster` | trades 7 < 15 (x5), trades 8 < 15 (x2), sharpe -0.84 < 1.0 (x1) |
| `positional_scaling` | trades 7 < 15 (x3), trades 8 < 15 (x2), sharpe -3.67 < 1.0 (x1) |
| `htf_ema` | trades 12 < 15 (x2), trades 8 < 15 (x2), trades 9 < 15 (x2) |
| `roc_ma_cross` | trades 8 < 15 (x3), trades 10 < 15 (x2), sharpe -2.38 < 1.0 (x1) |
| `narrow_range` | sharpe 0.57 < 1.0 (x2), profit_factor 0.87 < 1.5 (x2), profit_factor 1.10 < 1.5 (x1) |
| `frama` | sharpe -0.62 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1), mc_p_value 0.566 > 0.1 (우연 가능성) (x1) |
| `wick_reversal` | trades 9 < 15 (x2), trades 11 < 15 (x2), sharpe -1.29 < 1.0 (x1) |
| `linear_channel_rev` | profit_factor 0.00 < 1.5 (x3), trades 7 < 15 (x3), trades 6 < 15 (x2) |
| `volatility_cluster` | profit_factor 0.52 < 1.5 (x2), sharpe 0.79 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1) |
| `momentum_quality` | sharpe -6.27 < 1.0 (x1), profit_factor 0.40 < 1.5 (x1), mc_p_value 0.940 > 0.1 (우연 가능성) (x1) |
| `value_area` | profit_factor 0.52 < 1.5 (x2), sharpe -3.46 < 1.0 (x1), profit_factor 0.63 < 1.5 (x1) |
| `volume_breakout` | trades 13 < 15 (x2), trades 12 < 15 (x2), sharpe -0.52 < 1.0 (x1) |
| `order_flow_imbalance_v2` | profit_factor 0.61 < 1.5 (x2), profit_factor 0.70 < 1.5 (x2), sharpe -3.68 < 1.0 (x1) |
| `elder_impulse` | profit_factor 0.55 < 1.5 (x2), trades 10 < 15 (x2), sharpe -6.77 < 1.0 (x1) |
| `cmf` | sharpe -4.18 < 1.0 (x1), profit_factor 0.52 < 1.5 (x1), mc_p_value 0.857 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | sharpe -6.51 < 1.0 (x1), profit_factor 0.38 < 1.5 (x1), mc_p_value 0.954 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 0.44 < 1.5 (x2), sharpe -6.42 < 1.0 (x1), mc_p_value 0.965 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 7 < 15 | 22 |
| trades 8 < 15 | 16 |
| trades 9 < 15 | 11 |
| trades 6 < 15 | 8 |
| profit_factor 0.34 < 1.5 | 7 |
| trades 12 < 15 | 7 |
| trades 10 < 15 | 6 |
| profit_factor 0.52 < 1.5 | 6 |
| profit_factor 0.44 < 1.5 | 5 |
| profit_factor 0.65 < 1.5 | 5 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.75% -> $9,625
- **Top 5 균등배분**: +0.15% -> $10,015


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-11T10:30:01.759025Z_
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
| 평균 수익률 | -3.81% |
| 최고 수익률 | 3.23% (narrow_range) |
| 최저 수익률 | -9.50% (relative_volume) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `narrow_range` | +3.23% | 1.87 | 47.8% | 1.54 | 16 | 3.7% | 1/8 | FAIL |
| 2 | `acceleration_band` | +0.49% | 0.15 | 40.1% | 1.36 | 7 | 2.7% | 0/8 | FAIL |
| 3 | `linear_channel_rev` | +0.08% | -0.94 | 29.9% | 1.13 | 6 | 2.9% | 0/8 | FAIL |
| 4 | `wick_reversal` | -1.08% | -2.00 | 37.7% | 0.90 | 6 | 2.9% | 0/8 | FAIL |
| 5 | `price_cluster` | -1.25% | -2.55 | 27.3% | 0.85 | 6 | 3.8% | 0/8 | FAIL |
| 6 | `momentum_quality` | -2.18% | -1.83 | 32.6% | 0.89 | 23 | 7.0% | 1/8 | FAIL |
| 7 | `value_area` | -2.20% | -2.20 | 37.3% | 1.19 | 17 | 6.7% | 0/8 | FAIL |
| 8 | `volatility_cluster` | -2.42% | -1.93 | 35.0% | 0.85 | 22 | 6.3% | 0/8 | FAIL |
| 9 | `supertrend_multi` | -2.51% | -2.08 | 29.8% | 0.79 | 12 | 5.6% | 0/8 | FAIL |
| 10 | `engulfing_zone` | -2.53% | -2.54 | 34.7% | 0.67 | 8 | 4.8% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `narrow_range` | 82.1 | p100 | 1.87 | 3.01 | 1.54 | 16 | 3.7% | 1/8 | FAIL |
| 2 | `momentum_quality` | 64.2 | p95 | -1.83 | 3.66 | 0.89 | 23 | 7.0% | 1/8 | FAIL |
| 3 | `volatility_cluster` | 53.2 | p90 | -1.93 | 3.22 | 0.85 | 22 | 6.3% | 0/8 | FAIL |
| 4 | `acceleration_band` | 48.5 | p85 | 0.15 | 2.95 | 1.36 | 7 | 2.7% | 0/8 | FAIL |
| 5 | `value_area` | 47.2 | p80 | -2.20 | 4.87 | 1.19 | 17 | 6.7% | 0/8 | FAIL |
| 6 | `frama` | 44.5 | p76 | -2.61 | 3.60 | 0.80 | 24 | 11.2% | 0/8 | FAIL |
| 7 | `linear_channel_rev` | 39.4 | p71 | -0.94 | 4.12 | 1.13 | 6 | 2.9% | 0/8 | FAIL |
| 8 | `supertrend_multi` | 38.2 | p66 | -2.08 | 2.97 | 0.79 | 12 | 5.6% | 0/8 | FAIL |
| 9 | `htf_ema` | 37.4 | p61 | -3.29 | 4.91 | 1.36 | 10 | 5.9% | 0/8 | FAIL |
| 10 | `price_action_momentum` | 36.4 | p57 | -4.08 | 3.85 | 0.64 | 21 | 8.5% | 0/8 | FAIL |
| 11 | `lob_maker` | 34.2 | p52 | -5.17 | 2.29 | 0.52 | 21 | 9.6% | 0/8 | FAIL |
| 12 | `wick_reversal` | 31.6 | p47 | -2.00 | 3.66 | 0.90 | 6 | 2.9% | 0/8 | FAIL |
| 13 | `engulfing_zone` | 30.1 | p42 | -2.54 | 2.94 | 0.67 | 8 | 4.8% | 0/8 | FAIL |
| 14 | `order_flow_imbalance_v2` | 29.9 | p38 | -5.39 | 3.92 | 0.55 | 24 | 11.3% | 0/8 | FAIL |
| 15 | `price_cluster` | 28.3 | p33 | -2.55 | 4.48 | 0.85 | 6 | 3.8% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `narrow_range` | +3.23% | 1.87 | 1.54 | 16 | 1/8 | FAIL |
| `acceleration_band` | +0.49% | 0.15 | 1.36 | 7 | 0/8 | FAIL |
| `linear_channel_rev` | +0.08% | -0.94 | 1.13 | 6 | 0/8 | FAIL |
| `wick_reversal` | -1.08% | -2.00 | 0.90 | 6 | 0/8 | FAIL |
| `price_cluster` | -1.25% | -2.55 | 0.85 | 6 | 0/8 | FAIL |
| `momentum_quality` | -2.18% | -1.83 | 0.89 | 23 | 1/8 | FAIL |
| `value_area` | -2.20% | -2.20 | 1.19 | 17 | 0/8 | FAIL |
| `volatility_cluster` | -2.42% | -1.93 | 0.85 | 22 | 0/8 | FAIL |
| `supertrend_multi` | -2.51% | -2.08 | 0.79 | 12 | 0/8 | FAIL |
| `engulfing_zone` | -2.53% | -2.54 | 0.67 | 8 | 0/8 | FAIL |
| `htf_ema` | -2.92% | -3.29 | 1.36 | 10 | 0/8 | FAIL |
| `volume_breakout` | -3.78% | -3.69 | 0.59 | 10 | 0/8 | FAIL |
| `positional_scaling` | -4.65% | -4.44 | 0.44 | 10 | 0/8 | FAIL |
| `frama` | -4.79% | -2.61 | 0.80 | 24 | 0/8 | FAIL |
| `dema_cross` | -4.97% | -5.87 | 0.30 | 12 | 0/8 | FAIL |
| `roc_ma_cross` | -4.99% | -4.81 | 0.52 | 14 | 0/8 | FAIL |
| `price_action_momentum` | -5.63% | -4.08 | 0.64 | 21 | 0/8 | FAIL |
| `elder_impulse` | -6.85% | -5.33 | 0.68 | 16 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -8.27% | -5.39 | 0.55 | 24 | 0/8 | FAIL |
| `lob_maker` | -8.49% | -5.17 | 0.52 | 21 | 0/8 | FAIL |
| `cmf` | -8.52% | -6.35 | 0.43 | 19 | 0/8 | FAIL |
| `relative_volume` | -9.50% | -7.15 | 0.43 | 23 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `narrow_range` | sharpe 0.07 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.516 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | trades 7 < 15 (x4), trades 6 < 15 (x2), trades 5 < 15 (x1) |
| `linear_channel_rev` | trades 7 < 15 (x3), sharpe -0.71 < 1.0 (x1), profit_factor 0.86 < 1.5 (x1) |
| `wick_reversal` | trades 6 < 15 (x4), trades 5 < 15 (x2), sharpe -6.10 < 1.0 (x1) |
| `price_cluster` | profit_factor 0.00 < 1.5 (x3), trades 8 < 15 (x2), trades 5 < 15 (x2) |
| `momentum_quality` | profit_factor 0.69 < 1.5 (x2), sharpe -3.07 < 1.0 (x1), mc_p_value 0.773 > 0.1 (우연 가능성) (x1) |
| `value_area` | profit_factor 0.51 < 1.5 (x2), trades 14 < 15 (x2), sharpe -4.22 < 1.0 (x1) |
| `volatility_cluster` | sharpe -3.65 < 1.0 (x1), profit_factor 0.61 < 1.5 (x1), mc_p_value 0.837 > 0.1 (우연 가능성) (x1) |
| `supertrend_multi` | trades 7 < 15 (x2), sharpe -0.20 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1) |
| `engulfing_zone` | trades 6 < 15 (x3), profit_factor 0.77 < 1.5 (x2), sharpe -0.83 < 1.0 (x1) |
| `htf_ema` | profit_factor 0.39 < 1.5 (x2), trades 10 < 15 (x2), trades 9 < 15 (x2) |
| `volume_breakout` | trades 11 < 15 (x3), trades 12 < 15 (x2), sharpe -7.33 < 1.0 (x1) |
| `positional_scaling` | trades 12 < 15 (x2), trades 11 < 15 (x2), sharpe -5.37 < 1.0 (x1) |
| `frama` | sharpe -3.17 < 1.0 (x1), profit_factor 0.68 < 1.5 (x1), mc_p_value 0.799 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | trades 7 < 15 (x2), profit_factor 0.48 < 1.5 (x2), trades 14 < 15 (x2) |
| `roc_ma_cross` | trades 10 < 15 (x2), profit_factor 0.42 < 1.5 (x2), trades 13 < 15 (x2) |
| `price_action_momentum` | sharpe -5.37 < 1.0 (x1), profit_factor 0.48 < 1.5 (x1), mc_p_value 0.920 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | mc_p_value 1.000 > 0.1 (우연 가능성) (x2), trades 9 < 15 (x2), sharpe -11.63 < 1.0 (x1) |
| `order_flow_imbalance_v2` | sharpe -6.69 < 1.0 (x1), profit_factor 0.44 < 1.5 (x1), mc_p_value 0.969 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | sharpe -3.95 < 1.0 (x1), profit_factor 0.56 < 1.5 (x1), mc_p_value 0.832 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 7 < 15 | 16 |
| trades 6 < 15 | 9 |
| trades 9 < 15 | 9 |
| trades 5 < 15 | 8 |
| trades 8 < 15 | 8 |
| profit_factor 0.00 < 1.5 | 8 |
| trades 11 < 15 | 8 |
| trades 12 < 15 | 7 |
| trades 10 < 15 | 7 |
| trades 14 < 15 | 6 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.81% -> $9,619
- **Top 5 균등배분**: +0.30% -> $10,030
