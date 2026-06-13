# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-13T10:17:27.757259Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-13T10:25:07.519179Z_
_Symbol: BTC/USDT_
_Data Source: CSV fallback BTC/USDT 1h (/home/user/Trading/data/historical)_
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
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -4.30% |
| 최고 수익률 | 5.26% (supertrend_multi) |
| 최저 수익률 | -13.34% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +5.26% | 0.32 | 37.7% | 1.14 | 48 | 10.6% | 2/8 | FAIL |
| 2 | `price_cluster` | +4.50% | 0.59 | 39.4% | 1.18 | 46 | 12.2% | 3/8 | FAIL |
| 3 | `positional_scaling` | +1.97% | 0.00 | 36.5% | 1.18 | 36 | 9.7% | 1/8 | FAIL |
| 4 | `roc_ma_cross` | +0.38% | -0.35 | 37.9% | 1.12 | 40 | 9.6% | 2/8 | FAIL |
| 5 | `frama` | -0.92% | -0.22 | 38.9% | 1.02 | 42 | 9.8% | 0/8 | FAIL |
| 6 | `dema_cross` | -1.41% | -1.74 | 19.6% | 0.38 | 3 | 2.3% | 0/8 | FAIL |
| 7 | `volume_breakout` | -2.05% | -0.44 | 37.1% | 1.01 | 78 | 15.8% | 0/8 | FAIL |
| 8 | `htf_ema` | -2.35% | -0.35 | 38.5% | 0.98 | 45 | 11.4% | 0/8 | FAIL |
| 9 | `narrow_range` | -2.43% | -0.42 | 38.0% | 0.99 | 50 | 11.6% | 0/8 | FAIL |
| 10 | `acceleration_band` | -2.60% | -0.63 | 32.6% | 1.00 | 45 | 12.8% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 75.7 | p100 | 0.59 | 1.77 | 1.18 | 46 | 12.2% | 3/8 | FAIL |
| 2 | `supertrend_multi` | 68.3 | p95 | 0.32 | 2.82 | 1.14 | 48 | 10.6% | 2/8 | FAIL |
| 3 | `roc_ma_cross` | 60.8 | p90 | -0.35 | 2.88 | 1.12 | 40 | 9.6% | 2/8 | FAIL |
| 4 | `positional_scaling` | 60.3 | p85 | 0.00 | 2.87 | 1.18 | 36 | 9.7% | 1/8 | FAIL |
| 5 | `volume_breakout` | 60.1 | p80 | -0.44 | 2.41 | 1.01 | 78 | 15.8% | 0/8 | FAIL |
| 6 | `price_action_momentum` | 56.7 | p76 | -0.88 | 3.03 | 1.01 | 82 | 17.8% | 1/8 | FAIL |
| 7 | `narrow_range` | 56.5 | p71 | -0.42 | 1.39 | 0.99 | 50 | 11.6% | 0/8 | FAIL |
| 8 | `frama` | 56.4 | p66 | -0.22 | 1.40 | 1.02 | 42 | 9.8% | 0/8 | FAIL |
| 9 | `htf_ema` | 55.6 | p61 | -0.35 | 1.14 | 0.98 | 45 | 11.4% | 0/8 | FAIL |
| 10 | `order_flow_imbalance_v2` | 55.4 | p57 | -0.83 | 2.13 | 0.95 | 73 | 15.8% | 0/8 | FAIL |
| 11 | `lob_maker` | 55.1 | p52 | -0.91 | 1.91 | 0.94 | 84 | 19.7% | 0/8 | FAIL |
| 12 | `acceleration_band` | 54.2 | p47 | -0.63 | 2.20 | 1.00 | 45 | 12.8% | 1/8 | FAIL |
| 13 | `relative_volume` | 50.3 | p42 | -1.44 | 1.68 | 0.87 | 72 | 15.3% | 0/8 | FAIL |
| 14 | `momentum_quality` | 49.4 | p38 | -1.31 | 3.52 | 0.96 | 77 | 18.1% | 1/8 | FAIL |
| 15 | `cmf` | 48.8 | p33 | -1.44 | 1.81 | 0.87 | 75 | 18.4% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +5.26% | 0.32 | 1.14 | 48 | 2/8 | FAIL |
| `price_cluster` | +4.50% | 0.59 | 1.18 | 46 | 3/8 | FAIL |
| `positional_scaling` | +1.97% | 0.00 | 1.18 | 36 | 1/8 | FAIL |
| `roc_ma_cross` | +0.38% | -0.35 | 1.12 | 40 | 2/8 | FAIL |
| `frama` | -0.92% | -0.22 | 1.02 | 42 | 0/8 | FAIL |
| `dema_cross` | -1.41% | -1.74 | 0.38 | 3 | 0/8 | FAIL |
| `volume_breakout` | -2.05% | -0.44 | 1.01 | 78 | 0/8 | FAIL |
| `htf_ema` | -2.35% | -0.35 | 0.98 | 45 | 0/8 | FAIL |
| `narrow_range` | -2.43% | -0.42 | 0.99 | 50 | 0/8 | FAIL |
| `acceleration_band` | -2.60% | -0.63 | 1.00 | 45 | 1/8 | FAIL |
| `price_action_momentum` | -3.73% | -0.88 | 1.01 | 82 | 1/8 | FAIL |
| `momentum_quality` | -4.47% | -1.31 | 0.96 | 77 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | -4.88% | -0.83 | 0.95 | 73 | 0/8 | FAIL |
| `engulfing_zone` | -5.28% | -1.44 | 0.80 | 25 | 0/8 | FAIL |
| `lob_maker` | -7.17% | -0.91 | 0.94 | 84 | 0/8 | FAIL |
| `linear_channel_rev` | -7.38% | -2.74 | 0.62 | 29 | 0/8 | FAIL |
| `relative_volume` | -7.67% | -1.44 | 0.87 | 72 | 0/8 | FAIL |
| `volatility_cluster` | -9.01% | -2.14 | 0.81 | 60 | 0/8 | FAIL |
| `cmf` | -9.14% | -1.44 | 0.87 | 75 | 0/8 | FAIL |
| `elder_impulse` | -10.30% | -2.21 | 0.73 | 47 | 0/8 | FAIL |
| `value_area` | -12.60% | -3.08 | 0.67 | 56 | 0/8 | FAIL |
| `wick_reversal` | -13.34% | -3.61 | 0.60 | 44 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | profit_factor 1.47 < 1.5 (x1), mc_p_value 0.161 > 0.1 (우연 가능성) (x1), sharpe -0.68 < 1.0 (x1) |
| `price_cluster` | profit_factor 0.88 < 1.5 (x2), sharpe -0.77 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1) |
| `positional_scaling` | profit_factor 1.44 < 1.5 (x2), mc_p_value 0.109 > 0.1 (우연 가능성) (x1), sharpe -1.11 < 1.0 (x1) |
| `roc_ma_cross` | sharpe 0.14 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1), mc_p_value 0.460 > 0.1 (우연 가능성) (x1) |
| `frama` | sharpe -0.33 < 1.0 (x1), profit_factor 0.97 < 1.5 (x1), mc_p_value 0.512 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x4), trades 2 < 15 (x3), trades 3 < 15 (x2) |
| `volume_breakout` | sharpe -0.16 < 1.0 (x1), max_drawdown 21.3% > 20% (x1), profit_factor 1.01 < 1.5 (x1) |
| `htf_ema` | sharpe 0.21 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.450 > 0.1 (우연 가능성) (x1) |
| `narrow_range` | sharpe 0.60 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.370 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 0.96 < 1.5 (x2), profit_factor 1.39 < 1.5 (x1), mc_p_value 0.174 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | profit_factor 1.27 < 1.5 (x1), mc_p_value 0.202 > 0.1 (우연 가능성) (x1), sharpe -1.92 < 1.0 (x1) |
| `momentum_quality` | profit_factor 0.54 < 1.5 (x2), profit_factor 1.29 < 1.5 (x1), mc_p_value 0.143 > 0.1 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 0.94 < 1.5 (x2), profit_factor 1.25 < 1.5 (x1), mc_p_value 0.234 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -2.49 < 1.0 (x2), profit_factor 0.57 < 1.5 (x2), sharpe -2.14 < 1.0 (x1) |
| `lob_maker` | profit_factor 0.72 < 1.5 (x2), sharpe -2.37 < 1.0 (x1), max_drawdown 32.5% > 20% (x1) |
| `linear_channel_rev` | profit_factor 0.82 < 1.5 (x2), sharpe 0.01 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1) |
| `relative_volume` | profit_factor 0.97 < 1.5 (x2), sharpe -0.42 < 1.0 (x1), mc_p_value 0.552 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -0.87 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.654 > 0.1 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.19 < 1.5 (x1), mc_p_value 0.263 > 0.1 (우연 가능성) (x1), sharpe -2.25 < 1.0 (x1) |
| `elder_impulse` | sharpe -0.78 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.596 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.54 < 1.5 | 6 |
| profit_factor 0.77 < 1.5 | 6 |
| profit_factor 0.81 < 1.5 | 5 |
| profit_factor 0.82 < 1.5 | 5 |
| profit_factor 0.96 < 1.5 | 5 |
| profit_factor 0.88 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 0.80 < 1.5 | 4 |
| profit_factor 0.60 < 1.5 | 4 |
| profit_factor 0.91 < 1.5 | 4 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -4.30% -> $9,570
- **Top 5 균등배분**: +2.24% -> $10,224


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-13T10:32:45.080502Z_
_Symbol: ETH/USDT_
_Data Source: CSV fallback ETH/USDT 1h (/home/user/Trading/data/historical)_
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
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -6.23% |
| 최고 수익률 | 1.56% (dema_cross) |
| 최저 수익률 | -16.27% (supertrend_multi) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `dema_cross` | +1.56% | 0.73 | 56.1% | 1.67 | 14 | 3.5% | 0/8 | FAIL |
| 2 | `volatility_cluster` | +0.54% | 0.12 | 42.5% | 1.07 | 51 | 9.1% | 0/8 | FAIL |
| 3 | `narrow_range` | +0.27% | 0.06 | 41.4% | 1.06 | 51 | 9.9% | 0/8 | FAIL |
| 4 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 5 | `price_action_momentum` | -0.38% | -0.08 | 42.5% | 1.03 | 51 | 11.3% | 0/8 | FAIL |
| 6 | `momentum_quality` | -2.35% | -0.45 | 39.9% | 0.97 | 73 | 12.3% | 0/8 | FAIL |
| 7 | `engulfing_zone` | -3.80% | -1.84 | 36.8% | 0.90 | 27 | 11.3% | 1/8 | FAIL |
| 8 | `linear_channel_rev` | -3.99% | -1.25 | 36.0% | 0.78 | 28 | 7.1% | 0/8 | FAIL |
| 9 | `roc_ma_cross` | -4.06% | -1.11 | 37.9% | 0.83 | 34 | 9.5% | 0/8 | FAIL |
| 10 | `acceleration_band` | -4.36% | -2.15 | 30.6% | 0.61 | 11 | 6.2% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 59.5 | p100 | -0.45 | 1.19 | 0.97 | 73 | 12.3% | 0/8 | FAIL |
| 2 | `volatility_cluster` | 58.0 | p95 | 0.12 | 1.37 | 1.07 | 51 | 9.1% | 0/8 | FAIL |
| 3 | `narrow_range` | 57.1 | p90 | 0.06 | 1.46 | 1.06 | 51 | 9.9% | 0/8 | FAIL |
| 4 | `dema_cross` | 55.7 | p85 | 0.73 | 2.06 | 1.67 | 14 | 3.5% | 0/8 | FAIL |
| 5 | `price_action_momentum` | 55.0 | p80 | -0.08 | 1.42 | 1.03 | 51 | 11.3% | 0/8 | FAIL |
| 6 | `cmf` | 45.5 | p76 | -1.19 | 2.22 | 0.89 | 60 | 15.2% | 0/8 | FAIL |
| 7 | `value_area` | 42.8 | p71 | -1.51 | 1.23 | 0.81 | 51 | 12.1% | 0/8 | FAIL |
| 8 | `relative_volume` | 41.4 | p66 | -2.01 | 2.34 | 0.81 | 70 | 15.6% | 0/8 | FAIL |
| 9 | `engulfing_zone` | 41.3 | p61 | -1.84 | 3.67 | 0.90 | 27 | 11.3% | 1/8 | FAIL |
| 10 | `lob_maker` | 40.8 | p57 | -1.92 | 1.43 | 0.79 | 70 | 20.8% | 0/8 | FAIL |
| 11 | `roc_ma_cross` | 40.6 | p52 | -1.11 | 1.13 | 0.83 | 34 | 9.5% | 0/8 | FAIL |
| 12 | `elder_impulse` | 39.9 | p47 | -1.52 | 1.81 | 0.81 | 46 | 12.5% | 0/8 | FAIL |
| 13 | `linear_channel_rev` | 37.7 | p42 | -1.25 | 0.72 | 0.78 | 28 | 7.1% | 0/8 | FAIL |
| 14 | `htf_ema` | 36.3 | p38 | -1.43 | 1.68 | 0.78 | 31 | 9.8% | 0/8 | FAIL |
| 15 | `volume_breakout` | 36.1 | p33 | -2.60 | 2.23 | 0.75 | 79 | 20.5% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `dema_cross` | +1.56% | 0.73 | 1.67 | 14 | 0/8 | FAIL |
| `volatility_cluster` | +0.54% | 0.12 | 1.07 | 51 | 0/8 | FAIL |
| `narrow_range` | +0.27% | 0.06 | 1.06 | 51 | 0/8 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `price_action_momentum` | -0.38% | -0.08 | 1.03 | 51 | 0/8 | FAIL |
| `momentum_quality` | -2.35% | -0.45 | 0.97 | 73 | 0/8 | FAIL |
| `engulfing_zone` | -3.80% | -1.84 | 0.90 | 27 | 1/8 | FAIL |
| `linear_channel_rev` | -3.99% | -1.25 | 0.78 | 28 | 0/8 | FAIL |
| `roc_ma_cross` | -4.06% | -1.11 | 0.83 | 34 | 0/8 | FAIL |
| `acceleration_band` | -4.36% | -2.15 | 0.61 | 11 | 0/8 | FAIL |
| `htf_ema` | -4.66% | -1.43 | 0.78 | 31 | 0/8 | FAIL |
| `cmf` | -4.93% | -1.19 | 0.89 | 60 | 0/8 | FAIL |
| `value_area` | -6.48% | -1.51 | 0.81 | 51 | 0/8 | FAIL |
| `elder_impulse` | -6.63% | -1.52 | 0.81 | 46 | 0/8 | FAIL |
| `positional_scaling` | -8.55% | -2.49 | 0.65 | 37 | 0/8 | FAIL |
| `relative_volume` | -9.11% | -2.01 | 0.81 | 70 | 0/8 | FAIL |
| `price_cluster` | -10.37% | -3.40 | 0.54 | 29 | 0/8 | FAIL |
| `frama` | -11.56% | -2.51 | 0.67 | 46 | 0/8 | FAIL |
| `lob_maker` | -12.17% | -1.92 | 0.79 | 70 | 0/8 | FAIL |
| `volume_breakout` | -13.69% | -2.60 | 0.75 | 79 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -16.01% | -2.90 | 0.69 | 72 | 0/8 | FAIL |
| `supertrend_multi` | -16.27% | -3.78 | 0.60 | 61 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `dema_cross` | trades 11 < 15 (x3), trades 12 < 15 (x2), sharpe -0.61 < 1.0 (x1) |
| `volatility_cluster` | mc_p_value 0.225 > 0.1 (우연 가능성) (x2), sharpe -0.45 < 1.0 (x1), profit_factor 0.94 < 1.5 (x1) |
| `narrow_range` | sharpe -1.99 < 1.0 (x2), sharpe -0.55 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1) |
| `wick_reversal` | no trades generated (x8) |
| `price_action_momentum` | profit_factor 1.05 < 1.5 (x2), sharpe -1.38 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1) |
| `momentum_quality` | sharpe -1.30 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.710 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -5.03 < 1.0 (x1), profit_factor 0.31 < 1.5 (x1), mc_p_value 0.993 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -1.20 < 1.0 (x1), profit_factor 0.78 < 1.5 (x1), mc_p_value 0.727 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 0.71 < 1.5 (x2), sharpe -0.43 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1) |
| `acceleration_band` | trades 6 < 15 (x2), trades 14 < 15 (x2), sharpe -3.85 < 1.0 (x1) |
| `htf_ema` | sharpe -0.92 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.660 > 0.1 (우연 가능성) (x1) |
| `cmf` | sharpe -2.04 < 1.0 (x1), profit_factor 0.74 < 1.5 (x1), mc_p_value 0.830 > 0.1 (우연 가능성) (x1) |
| `value_area` | sharpe -1.63 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1), mc_p_value 0.768 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -1.33 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1), mc_p_value 0.748 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | mc_p_value 0.941 > 0.1 (우연 가능성) (x2), sharpe -4.74 < 1.0 (x1), profit_factor 0.42 < 1.5 (x1) |
| `relative_volume` | profit_factor 0.75 < 1.5 (x2), sharpe -2.29 < 1.0 (x1), profit_factor 0.73 < 1.5 (x1) |
| `price_cluster` | profit_factor 0.79 < 1.5 (x2), mc_p_value 1.000 > 0.1 (우연 가능성) (x2), sharpe -4.91 < 1.0 (x1) |
| `frama` | profit_factor 0.72 < 1.5 (x2), sharpe -1.87 < 1.0 (x1), mc_p_value 0.842 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 0.68 < 1.5 (x2), sharpe -2.94 < 1.0 (x1), max_drawdown 24.7% > 20% (x1) |
| `volume_breakout` | sharpe -2.63 < 1.0 (x2), profit_factor 0.72 < 1.5 (x1), mc_p_value 0.913 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 8 |
| profit_factor 0.72 < 1.5 | 6 |
| mc_p_value 1.000 > 0.1 (우연 가능성) | 6 |
| profit_factor 0.93 < 1.5 | 5 |
| profit_factor 0.79 < 1.5 | 5 |
| profit_factor 0.80 < 1.5 | 4 |
| profit_factor 0.76 < 1.5 | 4 |
| profit_factor 0.91 < 1.5 | 4 |
| trades 11 < 15 | 3 |
| sharpe -0.61 < 1.0 | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -6.23% -> $9,377
- **Top 5 균등배분**: +0.40% -> $10,040
