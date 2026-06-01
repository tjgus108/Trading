# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-01T00:21:27.004716Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-01T00:27:36.571660Z_
_Symbol: BTC/USDT_
_Data Source: CSV BTC/USDT 1h (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 23:00:00+00:00 (499일)_
_Walk-Forward: 8개 윈도우 (train=5040h, test=1440h)_
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
| 평균 수익률 | -9.47% |
| 최고 수익률 | 0.00% (wick_reversal) |
| 최저 수익률 | -21.53% (supertrend_multi) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 2 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 3 | `acceleration_band` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 4 | `frama` | -0.42% | -0.90 | 31.3% | 1.66 | 2 | 1.2% | 0/8 | FAIL |
| 5 | `value_area` | -3.66% | -2.53 | 38.9% | 0.56 | 14 | 4.9% | 0/8 | FAIL |
| 6 | `htf_ema` | -3.99% | -2.46 | 47.4% | 0.54 | 14 | 5.4% | 0/8 | FAIL |
| 7 | `price_action_momentum` | -5.05% | -3.37 | 30.4% | 0.34 | 12 | 5.4% | 0/8 | FAIL |
| 8 | `roc_ma_cross` | -6.63% | -3.32 | 41.8% | 0.50 | 23 | 7.4% | 0/8 | FAIL |
| 9 | `linear_channel_rev` | -7.80% | -4.15 | 35.7% | 0.41 | 23 | 8.5% | 0/8 | FAIL |
| 10 | `cmf` | -8.77% | -4.13 | 35.5% | 0.48 | 27 | 10.2% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `frama` | 69.5 | p100 | -0.90 | 1.60 | 1.66 | 2 | 1.2% | 0/8 | FAIL |
| 2 | `wick_reversal` | 60.0 | p95 | 0.00 | 0.00 | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 3 | `dema_cross` | 60.0 | p90 | 0.00 | 0.00 | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 4 | `acceleration_band` | 60.0 | p85 | 0.00 | 0.00 | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 5 | `htf_ema` | 48.1 | p80 | -2.46 | 1.67 | 0.54 | 14 | 5.4% | 0/8 | FAIL |
| 6 | `value_area` | 47.5 | p76 | -2.53 | 1.90 | 0.56 | 14 | 4.9% | 0/8 | FAIL |
| 7 | `roc_ma_cross` | 45.6 | p71 | -3.32 | 1.24 | 0.50 | 23 | 7.4% | 0/8 | FAIL |
| 8 | `volatility_cluster` | 44.8 | p66 | -3.71 | 1.64 | 0.58 | 44 | 11.3% | 0/8 | FAIL |
| 9 | `relative_volume` | 44.0 | p61 | -4.27 | 0.81 | 0.51 | 44 | 11.8% | 0/8 | FAIL |
| 10 | `price_action_momentum` | 43.8 | p57 | -3.37 | 0.79 | 0.34 | 12 | 5.4% | 0/8 | FAIL |
| 11 | `volume_breakout` | 42.3 | p52 | -4.47 | 1.63 | 0.57 | 60 | 14.3% | 0/8 | FAIL |
| 12 | `positional_scaling` | 40.8 | p47 | -4.18 | 1.30 | 0.53 | 43 | 14.7% | 0/8 | FAIL |
| 13 | `linear_channel_rev` | 39.4 | p42 | -4.15 | 1.32 | 0.41 | 23 | 8.5% | 0/8 | FAIL |
| 14 | `narrow_range` | 37.1 | p38 | -3.71 | 2.77 | 0.59 | 30 | 12.6% | 0/8 | FAIL |
| 15 | `price_cluster` | 36.9 | p33 | -4.26 | 1.94 | 0.51 | 39 | 14.9% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `acceleration_band` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `frama` | -0.42% | -0.90 | 1.66 | 2 | 0/8 | FAIL |
| `value_area` | -3.66% | -2.53 | 0.56 | 14 | 0/8 | FAIL |
| `htf_ema` | -3.99% | -2.46 | 0.54 | 14 | 0/8 | FAIL |
| `price_action_momentum` | -5.05% | -3.37 | 0.34 | 12 | 0/8 | FAIL |
| `roc_ma_cross` | -6.63% | -3.32 | 0.50 | 23 | 0/8 | FAIL |
| `linear_channel_rev` | -7.80% | -4.15 | 0.41 | 23 | 0/8 | FAIL |
| `cmf` | -8.77% | -4.13 | 0.48 | 27 | 0/8 | FAIL |
| `narrow_range` | -9.97% | -3.71 | 0.59 | 30 | 0/8 | FAIL |
| `volatility_cluster` | -9.99% | -3.71 | 0.58 | 44 | 0/8 | FAIL |
| `relative_volume` | -10.98% | -4.27 | 0.51 | 44 | 0/8 | FAIL |
| `engulfing_zone` | -11.98% | -4.76 | 0.32 | 23 | 0/8 | FAIL |
| `positional_scaling` | -13.05% | -4.18 | 0.53 | 43 | 0/8 | FAIL |
| `volume_breakout` | -13.37% | -4.47 | 0.57 | 60 | 0/8 | FAIL |
| `price_cluster` | -14.08% | -4.26 | 0.51 | 39 | 0/8 | FAIL |
| `momentum_quality` | -14.46% | -4.81 | 0.54 | 50 | 0/8 | FAIL |
| `lob_maker` | -14.72% | -4.35 | 0.48 | 33 | 0/8 | FAIL |
| `elder_impulse` | -17.15% | -6.22 | 0.32 | 38 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -20.64% | -5.53 | 0.48 | 59 | 0/8 | FAIL |
| `supertrend_multi` | -21.53% | -5.20 | 0.57 | 77 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `wick_reversal` | no trades generated (x8) |
| `dema_cross` | no trades generated (x8) |
| `acceleration_band` | no trades generated (x8) |
| `frama` | profit_factor 0.00 < 1.5 (x4), trades 1 < 15 (x3), trades 3 < 15 (x3) |
| `value_area` | trades 12 < 15 (x2), sharpe -0.09 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1) |
| `htf_ema` | trades 9 < 15 (x2), sharpe -2.85 < 1.0 (x1), profit_factor 0.48 < 1.5 (x1) |
| `price_action_momentum` | trades 7 < 15 (x2), profit_factor 0.13 < 1.5 (x2), trades 13 < 15 (x2) |
| `roc_ma_cross` | profit_factor 0.66 < 1.5 (x2), mc_p_value 0.968 > 0.05 (우연 가능성) (x2), sharpe -2.71 < 1.0 (x1) |
| `linear_channel_rev` | mc_p_value 0.988 > 0.05 (우연 가능성) (x2), sharpe -3.62 < 1.0 (x1), profit_factor 0.49 < 1.5 (x1) |
| `cmf` | sharpe -0.82 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.570 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 0.24 < 1.5 (x2), mc_p_value 0.998 > 0.05 (우연 가능성) (x2), mc_p_value 0.150 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -2.23 < 1.0 (x1), profit_factor 0.73 < 1.5 (x1), mc_p_value 0.770 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | profit_factor 0.48 < 1.5 (x2), sharpe -5.58 < 1.0 (x1), profit_factor 0.39 < 1.5 (x1) |
| `engulfing_zone` | mc_p_value 0.996 > 0.05 (우연 가능성) (x2), sharpe -3.12 < 1.0 (x2), profit_factor 0.17 < 1.5 (x2) |
| `positional_scaling` | max_drawdown 20.7% > 20% (x2), profit_factor 0.43 < 1.5 (x2), sharpe -3.28 < 1.0 (x1) |
| `volume_breakout` | mc_p_value 0.998 > 0.05 (우연 가능성) (x2), sharpe -4.25 < 1.0 (x1), profit_factor 0.58 < 1.5 (x1) |
| `price_cluster` | mc_p_value 1.000 > 0.05 (우연 가능성) (x2), sharpe -0.94 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1) |
| `momentum_quality` | mc_p_value 1.000 > 0.05 (우연 가능성) (x3), sharpe -2.37 < 1.0 (x1), profit_factor 0.73 < 1.5 (x1) |
| `lob_maker` | mc_p_value 0.938 > 0.05 (우연 가능성) (x2), sharpe -1.99 < 1.0 (x1), profit_factor 0.71 < 1.5 (x1) |
| `elder_impulse` | mc_p_value 0.998 > 0.05 (우연 가능성) (x2), profit_factor 0.16 < 1.5 (x2), mc_p_value 1.000 > 0.05 (우연 가능성) (x2) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 24 |
| mc_p_value 1.000 > 0.05 (우연 가능성) | 15 |
| mc_p_value 0.998 > 0.05 (우연 가능성) | 12 |
| mc_p_value 0.996 > 0.05 (우연 가능성) | 9 |
| mc_p_value 0.984 > 0.05 (우연 가능성) | 7 |
| mc_p_value 0.994 > 0.05 (우연 가능성) | 6 |
| profit_factor 0.37 < 1.5 | 6 |
| profit_factor 0.48 < 1.5 | 5 |
| profit_factor 0.29 < 1.5 | 5 |
| profit_factor 0.00 < 1.5 | 4 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -9.47% -> $9,053
- **Top 5 균등배분**: -0.82% -> $9,918


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-01T00:30:32.847945Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=88913831, block=24)_
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
| PASS (일관성 50%+) | 1개 |
| FAIL | 21개 |
| 평균 수익률 | 1.74% |
| 최고 수익률 | 17.14% (price_action_momentum) |
| 최저 수익률 | -5.98% (supertrend_multi) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +17.14% | 1.63 | 39.9% | 1.18 | 152 | 20.0% | 0/4 | FAIL |
| 2 | `momentum_quality` | +15.22% | 1.70 | 41.0% | 1.22 | 116 | 12.3% | 0/4 | FAIL |
| 3 | `linear_channel_rev` | +10.51% | 2.37 | 49.6% | 1.86 | 27 | 5.3% | 2/4 | PASS |
| 4 | `lob_maker` | +8.35% | 0.84 | 39.2% | 1.11 | 120 | 18.1% | 0/4 | FAIL |
| 5 | `htf_ema` | +5.10% | 0.69 | 39.1% | 1.13 | 76 | 16.8% | 0/4 | FAIL |
| 6 | `volatility_cluster` | +2.30% | 0.46 | 38.2% | 1.10 | 78 | 13.0% | 0/4 | FAIL |
| 7 | `positional_scaling` | +2.26% | 0.35 | 40.6% | 1.24 | 31 | 9.9% | 1/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | +1.86% | 0.32 | 38.9% | 1.07 | 76 | 18.4% | 0/4 | FAIL |
| 9 | `cmf` | +0.59% | 0.25 | 37.9% | 1.05 | 118 | 21.2% | 0/4 | FAIL |
| 10 | `dema_cross` | +0.39% | 0.24 | 42.6% | 1.53 | 12 | 4.5% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `linear_channel_rev` | 77.7 | p100 | 2.37 | 2.13 | 1.86 | 27 | 5.3% | 2/4 | PASS |
| 2 | `momentum_quality` | 62.1 | p95 | 1.70 | 1.52 | 1.22 | 116 | 12.3% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 60.2 | p90 | 1.63 | 1.15 | 1.18 | 152 | 20.0% | 0/4 | FAIL |
| 4 | `lob_maker` | 52.6 | p85 | 0.84 | 1.10 | 1.11 | 120 | 18.1% | 0/4 | FAIL |
| 5 | `volatility_cluster` | 50.6 | p80 | 0.46 | 0.88 | 1.10 | 78 | 13.0% | 0/4 | FAIL |
| 6 | `dema_cross` | 50.3 | p76 | 0.24 | 1.77 | 1.53 | 12 | 4.5% | 0/4 | FAIL |
| 7 | `roc_ma_cross` | 49.9 | p71 | 0.14 | 0.33 | 1.05 | 44 | 9.0% | 0/4 | FAIL |
| 8 | `positional_scaling` | 48.1 | p66 | 0.35 | 2.39 | 1.24 | 31 | 9.9% | 1/4 | FAIL |
| 9 | `htf_ema` | 47.9 | p61 | 0.69 | 1.20 | 1.13 | 76 | 16.8% | 0/4 | FAIL |
| 10 | `cmf` | 47.2 | p57 | 0.25 | 0.59 | 1.05 | 118 | 21.2% | 0/4 | FAIL |
| 11 | `narrow_range` | 45.1 | p52 | 0.07 | 1.64 | 1.06 | 89 | 13.6% | 0/4 | FAIL |
| 12 | `order_flow_imbalance_v2` | 44.6 | p47 | 0.32 | 0.92 | 1.07 | 76 | 18.4% | 0/4 | FAIL |
| 13 | `relative_volume` | 43.9 | p42 | -0.06 | 1.04 | 1.03 | 62 | 13.0% | 0/4 | FAIL |
| 14 | `elder_impulse` | 43.2 | p38 | -0.36 | 0.90 | 0.98 | 62 | 11.4% | 0/4 | FAIL |
| 15 | `volume_breakout` | 42.7 | p33 | -0.12 | 0.63 | 1.01 | 91 | 19.6% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +17.14% | 1.63 | 1.18 | 152 | 0/4 | FAIL |
| `momentum_quality` | +15.22% | 1.70 | 1.22 | 116 | 0/4 | FAIL |
| `linear_channel_rev` | +10.51% | 2.37 | 1.86 | 27 | 2/4 | PASS |
| `lob_maker` | +8.35% | 0.84 | 1.11 | 120 | 0/4 | FAIL |
| `htf_ema` | +5.10% | 0.69 | 1.13 | 76 | 0/4 | FAIL |
| `volatility_cluster` | +2.30% | 0.46 | 1.10 | 78 | 0/4 | FAIL |
| `positional_scaling` | +2.26% | 0.35 | 1.24 | 31 | 1/4 | FAIL |
| `order_flow_imbalance_v2` | +1.86% | 0.32 | 1.07 | 76 | 0/4 | FAIL |
| `cmf` | +0.59% | 0.25 | 1.05 | 118 | 0/4 | FAIL |
| `dema_cross` | +0.39% | 0.24 | 1.53 | 12 | 0/4 | FAIL |
| `narrow_range` | +0.34% | 0.07 | 1.06 | 89 | 0/4 | FAIL |
| `roc_ma_cross` | +0.22% | 0.14 | 1.05 | 44 | 0/4 | FAIL |
| `value_area` | -0.15% | -0.37 | 1.19 | 24 | 1/4 | FAIL |
| `engulfing_zone` | -0.83% | -0.27 | 1.01 | 24 | 0/4 | FAIL |
| `relative_volume` | -0.92% | -0.06 | 1.03 | 62 | 0/4 | FAIL |
| `wick_reversal` | -2.08% | -2.00 | 0.00 | 1 | 0/4 | FAIL |
| `volume_breakout` | -2.21% | -0.12 | 1.01 | 91 | 0/4 | FAIL |
| `elder_impulse` | -2.97% | -0.36 | 0.98 | 62 | 0/4 | FAIL |
| `acceleration_band` | -3.16% | -0.32 | 1.01 | 109 | 0/4 | FAIL |
| `price_cluster` | -3.53% | -0.43 | 0.96 | 43 | 0/4 | FAIL |
| `frama` | -4.18% | -0.39 | 0.99 | 87 | 0/4 | FAIL |
| `supertrend_multi` | -5.98% | -0.70 | 0.96 | 117 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | max_drawdown 23.0% > 20% (x1), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.208 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 1.45 < 1.5 (x1), profit_factor 1.29 < 1.5 (x1), mc_p_value 0.080 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.102 > 0.05 (우연 가능성) (x1), profit_factor 1.20 < 1.5 (x1) |
| `htf_ema` | sharpe -0.86 < 1.0 (x1), max_drawdown 26.4% > 20% (x1), profit_factor 0.92 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 0.99 < 1.5 (x2), profit_factor 1.27 < 1.5 (x1), mc_p_value 0.160 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | sharpe -2.66 < 1.0 (x1), profit_factor 0.63 < 1.5 (x1), mc_p_value 0.898 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.156 > 0.05 (우연 가능성) (x1), sharpe 0.64 < 1.0 (x1) |
| `cmf` | profit_factor 1.11 < 1.5 (x2), sharpe -0.19 < 1.0 (x1), max_drawdown 24.3% > 20% (x1) |
| `dema_cross` | trades 7 < 15 (x1), sharpe -1.12 < 1.0 (x1), profit_factor 0.72 < 1.5 (x1) |
| `narrow_range` | profit_factor 1.39 < 1.5 (x1), mc_p_value 0.072 > 0.05 (우연 가능성) (x1), sharpe 0.28 < 1.0 (x1) |
| `roc_ma_cross` | sharpe -0.35 < 1.0 (x1), profit_factor 0.97 < 1.5 (x1), mc_p_value 0.546 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -0.11 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.494 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | mc_p_value 0.178 > 0.05 (우연 가능성) (x1), sharpe -1.58 < 1.0 (x1), profit_factor 0.73 < 1.5 (x1) |
| `relative_volume` | profit_factor 0.88 < 1.5 (x2), sharpe 0.81 < 1.0 (x1), profit_factor 1.15 < 1.5 (x1) |
| `wick_reversal` | profit_factor 0.00 < 1.5 (x3), sharpe -2.97 < 1.0 (x2), trades 2 < 15 (x2) |
| `volume_breakout` | profit_factor 0.94 < 1.5 (x2), sharpe 0.69 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1) |
| `elder_impulse` | sharpe -0.36 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1), mc_p_value 0.528 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 0.82 < 1.5 (x2), profit_factor 1.26 < 1.5 (x1), mc_p_value 0.118 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -0.46 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1), mc_p_value 0.616 > 0.05 (우연 가능성) (x1) |
| `frama` | profit_factor 0.89 < 1.5 (x2), sharpe -1.36 < 1.0 (x1), max_drawdown 24.7% > 20% (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.15 < 1.5 | 5 |
| profit_factor 0.88 < 1.5 | 5 |
| profit_factor 0.99 < 1.5 | 4 |
| profit_factor 1.11 < 1.5 | 4 |
| profit_factor 1.12 < 1.5 | 3 |
| profit_factor 0.98 < 1.5 | 3 |
| profit_factor 0.00 < 1.5 | 3 |
| profit_factor 1.45 < 1.5 | 2 |
| mc_p_value 0.228 > 0.05 (우연 가능성) | 2 |
| sharpe -0.82 < 1.0 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +1.74% -> $10,174
- **PASS 1개 균등배분**: +10.51% -> $11,051
- **Top 5 균등배분**: +11.26% -> $11,126


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-01T00:33:29.878213Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=529123964, block=24)_
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
| PASS (일관성 50%+) | 6개 |
| FAIL | 16개 |
| 평균 수익률 | 14.94% |
| 최고 수익률 | 65.07% (price_action_momentum) |
| 최저 수익률 | -5.10% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +65.07% | 4.18 | 45.7% | 1.51 | 154 | 15.4% | 2/4 | PASS |
| 2 | `momentum_quality` | +42.43% | 3.67 | 46.0% | 1.55 | 110 | 12.9% | 2/4 | PASS |
| 3 | `cmf` | +39.86% | 2.59 | 43.7% | 1.33 | 123 | 14.8% | 2/4 | PASS |
| 4 | `supertrend_multi` | +24.12% | 2.80 | 42.6% | 1.47 | 82 | 11.3% | 2/4 | PASS |
| 5 | `acceleration_band` | +22.70% | 2.17 | 42.7% | 1.36 | 100 | 19.2% | 2/4 | PASS |
| 6 | `roc_ma_cross` | +21.27% | 3.84 | 55.2% | 2.45 | 36 | 5.4% | 2/4 | PASS |
| 7 | `lob_maker` | +19.92% | 1.60 | 40.1% | 1.18 | 130 | 18.6% | 0/4 | FAIL |
| 8 | `narrow_range` | +18.09% | 2.24 | 43.5% | 1.33 | 92 | 8.9% | 0/4 | FAIL |
| 9 | `htf_ema` | +15.59% | 1.37 | 40.5% | 1.29 | 72 | 15.5% | 1/4 | FAIL |
| 10 | `volume_breakout` | +14.41% | 1.19 | 40.1% | 1.20 | 96 | 18.9% | 1/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `roc_ma_cross` | 76.0 | p100 | 3.84 | 2.22 | 2.45 | 36 | 5.4% | 2/4 | PASS |
| 2 | `price_action_momentum` | 73.5 | p95 | 4.18 | 2.63 | 1.51 | 154 | 15.4% | 2/4 | PASS |
| 3 | `momentum_quality` | 66.5 | p90 | 3.67 | 3.24 | 1.55 | 110 | 12.9% | 2/4 | PASS |
| 4 | `supertrend_multi` | 62.9 | p85 | 2.80 | 2.08 | 1.47 | 82 | 11.3% | 2/4 | PASS |
| 5 | `cmf` | 60.5 | p80 | 2.59 | 2.61 | 1.33 | 123 | 14.8% | 2/4 | PASS |
| 6 | `dema_cross` | 55.8 | p76 | 2.19 | 0.55 | 1.84 | 18 | 4.2% | 0/4 | FAIL |
| 7 | `narrow_range` | 55.5 | p71 | 2.24 | 0.72 | 1.33 | 92 | 8.9% | 0/4 | FAIL |
| 8 | `acceleration_band` | 54.4 | p66 | 2.17 | 2.15 | 1.36 | 100 | 19.2% | 2/4 | PASS |
| 9 | `elder_impulse` | 51.0 | p61 | 2.00 | 1.69 | 1.44 | 56 | 12.3% | 1/4 | FAIL |
| 10 | `volatility_cluster` | 50.8 | p57 | 1.74 | 2.19 | 1.28 | 84 | 10.4% | 1/4 | FAIL |
| 11 | `lob_maker` | 46.3 | p52 | 1.60 | 1.11 | 1.18 | 130 | 18.6% | 0/4 | FAIL |
| 12 | `frama` | 45.1 | p47 | 1.19 | 0.61 | 1.17 | 91 | 13.8% | 0/4 | FAIL |
| 13 | `linear_channel_rev` | 43.8 | p42 | 0.82 | 1.97 | 1.30 | 32 | 7.0% | 1/4 | FAIL |
| 14 | `htf_ema` | 42.4 | p38 | 1.37 | 2.77 | 1.29 | 72 | 15.5% | 1/4 | FAIL |
| 15 | `volume_breakout` | 41.6 | p33 | 1.19 | 2.44 | 1.20 | 96 | 18.9% | 1/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +65.07% | 4.18 | 1.51 | 154 | 2/4 | PASS |
| `momentum_quality` | +42.43% | 3.67 | 1.55 | 110 | 2/4 | PASS |
| `cmf` | +39.86% | 2.59 | 1.33 | 123 | 2/4 | PASS |
| `supertrend_multi` | +24.12% | 2.80 | 1.47 | 82 | 2/4 | PASS |
| `acceleration_band` | +22.70% | 2.17 | 1.36 | 100 | 2/4 | PASS |
| `roc_ma_cross` | +21.27% | 3.84 | 2.45 | 36 | 2/4 | PASS |
| `lob_maker` | +19.92% | 1.60 | 1.18 | 130 | 0/4 | FAIL |
| `narrow_range` | +18.09% | 2.24 | 1.33 | 92 | 0/4 | FAIL |
| `htf_ema` | +15.59% | 1.37 | 1.29 | 72 | 1/4 | FAIL |
| `volume_breakout` | +14.41% | 1.19 | 1.20 | 96 | 1/4 | FAIL |
| `elder_impulse` | +14.20% | 2.00 | 1.44 | 56 | 1/4 | FAIL |
| `volatility_cluster` | +13.88% | 1.74 | 1.28 | 84 | 1/4 | FAIL |
| `frama` | +9.86% | 1.19 | 1.17 | 91 | 0/4 | FAIL |
| `dema_cross` | +6.96% | 2.19 | 1.84 | 18 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +5.40% | 0.50 | 1.09 | 90 | 0/4 | FAIL |
| `linear_channel_rev` | +3.48% | 0.82 | 1.30 | 32 | 1/4 | FAIL |
| `relative_volume` | +1.23% | 0.22 | 1.07 | 58 | 0/4 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `price_cluster` | -0.06% | 0.09 | 1.05 | 32 | 0/4 | FAIL |
| `positional_scaling` | -1.15% | -0.18 | 1.06 | 32 | 0/4 | FAIL |
| `value_area` | -3.48% | -0.87 | 0.88 | 30 | 0/4 | FAIL |
| `engulfing_zone` | -5.10% | -1.12 | 0.80 | 21 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `lob_maker` | profit_factor 1.29 < 1.5 (x2), mc_p_value 0.072 > 0.05 (우연 가능성) (x1), mc_p_value 0.066 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.23 < 1.5 (x1), mc_p_value 0.160 > 0.05 (우연 가능성) (x1), profit_factor 1.50 < 1.5 (x1) |
| `htf_ema` | mc_p_value 0.060 > 0.05 (우연 가능성) (x1), sharpe -0.31 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1) |
| `volume_breakout` | profit_factor 1.46 < 1.5 (x1), sharpe -0.57 < 1.0 (x1), max_drawdown 20.8% > 20% (x1) |
| `elder_impulse` | mc_p_value 0.054 > 0.05 (우연 가능성) (x1), sharpe 0.81 < 1.0 (x1), profit_factor 1.15 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.49 < 1.5 (x1), mc_p_value 0.056 > 0.05 (우연 가능성) (x1), sharpe -0.71 < 1.0 (x1) |
| `frama` | profit_factor 1.17 < 1.5 (x1), mc_p_value 0.262 > 0.05 (우연 가능성) (x1), profit_factor 1.29 < 1.5 (x1) |
| `dema_cross` | profit_factor 1.38 < 1.5 (x1), mc_p_value 0.262 > 0.05 (우연 가능성) (x1), mc_p_value 0.114 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe 0.50 < 1.0 (x1), max_drawdown 26.6% > 20% (x1), profit_factor 1.08 < 1.5 (x1) |
| `linear_channel_rev` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.280 > 0.05 (우연 가능성) (x1), profit_factor 1.28 < 1.5 (x1) |
| `relative_volume` | sharpe 0.95 < 1.0 (x1), profit_factor 1.16 < 1.5 (x1), mc_p_value 0.270 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x4) |
| `price_cluster` | sharpe -0.86 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.630 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | mc_p_value 0.142 > 0.05 (우연 가능성) (x1), sharpe -0.80 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1) |
| `value_area` | sharpe -1.43 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1), mc_p_value 0.728 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -1.91 < 1.0 (x1), profit_factor 0.68 < 1.5 (x1), mc_p_value 0.852 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 4 |
| profit_factor 1.08 < 1.5 | 3 |
| profit_factor 0.94 < 1.5 | 3 |
| profit_factor 1.29 < 1.5 | 3 |
| profit_factor 1.26 < 1.5 | 2 |
| sharpe 0.70 < 1.0 | 2 |
| profit_factor 0.95 < 1.5 | 2 |
| profit_factor 1.17 < 1.5 | 2 |
| profit_factor 1.15 < 1.5 | 2 |
| mc_p_value 0.262 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +14.94% -> $11,494
- **PASS 6개 균등배분**: +35.91% -> $13,591
- **Top 5 균등배분**: +38.84% -> $13,884
