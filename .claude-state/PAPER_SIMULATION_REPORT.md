# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-01T15:21:05.683050Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-01T15:29:01.631341Z_
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
| 평균 수익률 | -3.54% |
| 최고 수익률 | 5.87% (supertrend_multi) |
| 최저 수익률 | -10.01% (elder_impulse) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +5.87% | 0.43 | 36.6% | 1.13 | 47 | 10.5% | 1/8 | FAIL |
| 2 | `price_cluster` | +2.50% | 0.40 | 39.4% | 1.12 | 45 | 11.8% | 1/8 | FAIL |
| 3 | `positional_scaling` | +1.40% | -0.10 | 36.5% | 1.17 | 36 | 10.4% | 1/8 | FAIL |
| 4 | `roc_ma_cross` | +1.01% | -0.11 | 37.9% | 1.15 | 40 | 9.1% | 2/8 | FAIL |
| 5 | `frama` | +0.04% | 0.01 | 38.9% | 1.06 | 42 | 9.6% | 0/8 | FAIL |
| 6 | `narrow_range` | -0.79% | -0.10 | 38.6% | 1.04 | 50 | 11.1% | 0/8 | FAIL |
| 7 | `htf_ema` | -1.30% | -0.15 | 38.5% | 1.02 | 45 | 11.1% | 0/8 | FAIL |
| 8 | `dema_cross` | -1.35% | -1.70 | 19.6% | 0.39 | 3 | 2.2% | 0/8 | FAIL |
| 9 | `volume_breakout` | -1.46% | -0.35 | 37.5% | 1.04 | 78 | 15.7% | 0/8 | FAIL |
| 10 | `momentum_quality` | -2.86% | -0.81 | 34.3% | 1.00 | 66 | 15.3% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 69.2 | p100 | 0.40 | 1.43 | 1.12 | 45 | 11.8% | 1/8 | FAIL |
| 2 | `supertrend_multi` | 67.6 | p95 | 0.43 | 2.62 | 1.13 | 47 | 10.5% | 1/8 | FAIL |
| 3 | `roc_ma_cross` | 66.3 | p90 | -0.11 | 2.66 | 1.15 | 40 | 9.1% | 2/8 | FAIL |
| 4 | `narrow_range` | 60.1 | p85 | -0.10 | 1.28 | 1.04 | 50 | 11.1% | 0/8 | FAIL |
| 5 | `positional_scaling` | 59.7 | p80 | -0.10 | 3.00 | 1.17 | 36 | 10.4% | 1/8 | FAIL |
| 6 | `frama` | 59.2 | p76 | 0.01 | 1.26 | 1.06 | 42 | 9.6% | 0/8 | FAIL |
| 7 | `order_flow_imbalance_v2` | 58.8 | p71 | -0.55 | 1.81 | 0.98 | 77 | 14.8% | 0/8 | FAIL |
| 8 | `volume_breakout` | 57.7 | p66 | -0.35 | 2.65 | 1.04 | 78 | 15.7% | 0/8 | FAIL |
| 9 | `htf_ema` | 57.4 | p61 | -0.15 | 1.26 | 1.02 | 45 | 11.1% | 0/8 | FAIL |
| 10 | `lob_maker` | 57.3 | p57 | -0.55 | 1.81 | 0.98 | 84 | 18.9% | 0/8 | FAIL |
| 11 | `price_action_momentum` | 54.4 | p52 | -0.85 | 2.97 | 1.01 | 82 | 18.2% | 1/8 | FAIL |
| 12 | `momentum_quality` | 53.8 | p47 | -0.81 | 2.93 | 1.00 | 66 | 15.3% | 1/8 | FAIL |
| 13 | `cmf` | 47.7 | p42 | -1.24 | 1.68 | 0.90 | 75 | 18.3% | 0/8 | FAIL |
| 14 | `acceleration_band` | 45.1 | p38 | -0.87 | 2.19 | 0.97 | 45 | 14.5% | 0/8 | FAIL |
| 15 | `relative_volume` | 42.8 | p33 | -1.44 | 1.74 | 0.86 | 59 | 14.0% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +5.87% | 0.43 | 1.13 | 47 | 1/8 | FAIL |
| `price_cluster` | +2.50% | 0.40 | 1.12 | 45 | 1/8 | FAIL |
| `positional_scaling` | +1.40% | -0.10 | 1.17 | 36 | 1/8 | FAIL |
| `roc_ma_cross` | +1.01% | -0.11 | 1.15 | 40 | 2/8 | FAIL |
| `frama` | +0.04% | 0.01 | 1.06 | 42 | 0/8 | FAIL |
| `narrow_range` | -0.79% | -0.10 | 1.04 | 50 | 0/8 | FAIL |
| `htf_ema` | -1.30% | -0.15 | 1.02 | 45 | 0/8 | FAIL |
| `dema_cross` | -1.35% | -1.70 | 0.39 | 3 | 0/8 | FAIL |
| `volume_breakout` | -1.46% | -0.35 | 1.04 | 78 | 0/8 | FAIL |
| `momentum_quality` | -2.86% | -0.81 | 1.00 | 66 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | -3.78% | -0.55 | 0.98 | 77 | 0/8 | FAIL |
| `price_action_momentum` | -4.15% | -0.85 | 1.01 | 82 | 1/8 | FAIL |
| `acceleration_band` | -4.28% | -0.87 | 0.97 | 45 | 0/8 | FAIL |
| `lob_maker` | -4.77% | -0.55 | 0.98 | 84 | 0/8 | FAIL |
| `wick_reversal` | -4.96% | -1.55 | 0.73 | 23 | 0/8 | FAIL |
| `engulfing_zone` | -5.44% | -1.38 | 0.81 | 25 | 0/8 | FAIL |
| `relative_volume` | -7.45% | -1.44 | 0.86 | 59 | 0/8 | FAIL |
| `cmf` | -8.46% | -1.24 | 0.90 | 75 | 0/8 | FAIL |
| `linear_channel_rev` | -8.50% | -2.82 | 0.63 | 29 | 0/8 | FAIL |
| `volatility_cluster` | -9.44% | -2.02 | 0.82 | 60 | 0/8 | FAIL |
| `value_area` | -9.68% | -2.50 | 0.73 | 46 | 0/8 | FAIL |
| `elder_impulse` | -10.01% | -2.02 | 0.75 | 47 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | mc_p_value 0.056 > 0.05 (우연 가능성) (x1), profit_factor 1.44 < 1.5 (x1), mc_p_value 0.182 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | mc_p_value 0.494 > 0.05 (우연 가능성) (x2), profit_factor 1.01 < 1.5 (x2), sharpe -1.43 < 1.0 (x1) |
| `positional_scaling` | mc_p_value 0.094 > 0.05 (우연 가능성) (x1), sharpe -1.00 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1) |
| `roc_ma_cross` | sharpe 0.21 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.446 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe -0.16 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.472 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | sharpe 0.69 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.340 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | mc_p_value 0.344 > 0.05 (우연 가능성) (x2), sharpe 0.57 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x4), trades 2 < 15 (x3), trades 3 < 15 (x2) |
| `volume_breakout` | sharpe -0.23 < 1.0 (x1), max_drawdown 21.7% > 20% (x1), profit_factor 1.00 < 1.5 (x1) |
| `momentum_quality` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.154 > 0.05 (우연 가능성) (x1), sharpe -0.44 < 1.0 (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.16 < 1.5 (x1), mc_p_value 0.294 > 0.05 (우연 가능성) (x1), sharpe -0.46 < 1.0 (x1) |
| `price_action_momentum` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.194 > 0.05 (우연 가능성) (x1), sharpe -2.05 < 1.0 (x1) |
| `acceleration_band` | profit_factor 1.32 < 1.5 (x1), mc_p_value 0.218 > 0.05 (우연 가능성) (x1), sharpe -1.56 < 1.0 (x1) |
| `lob_maker` | max_drawdown 25.6% > 20% (x2), sharpe -1.80 < 1.0 (x1), max_drawdown 30.1% > 20% (x1) |
| `wick_reversal` | profit_factor 0.70 < 1.5 (x2), sharpe -1.91 < 1.0 (x1), mc_p_value 0.786 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -2.23 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1), mc_p_value 0.850 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | sharpe -2.07 < 1.0 (x1), profit_factor 0.77 < 1.5 (x1), mc_p_value 0.822 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 0.78 < 1.5 (x2), profit_factor 1.17 < 1.5 (x1), mc_p_value 0.278 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe 0.01 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1), mc_p_value 0.466 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -1.04 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.690 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.01 < 1.5 | 6 |
| profit_factor 0.82 < 1.5 | 6 |
| profit_factor 0.78 < 1.5 | 5 |
| mc_p_value 0.998 > 0.05 (우연 가능성) | 4 |
| profit_factor 0.89 < 1.5 | 4 |
| profit_factor 0.91 < 1.5 | 4 |
| profit_factor 0.77 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 0.47 < 1.5 | 3 |
| mc_p_value 0.494 > 0.05 (우연 가능성) | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.54% -> $9,646
- **Top 5 균등배분**: +2.16% -> $10,216


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-01T15:36:37.190925Z_
_Symbol: ETH/USDT_
_Data Source: CSV ETH/USDT 1h (/home/user/Trading/data/historical)_
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
| 평균 수익률 | -6.34% |
| 최고 수익률 | 4.69% (dema_cross) |
| 최저 수익률 | -19.60% (volume_breakout) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `dema_cross` | +4.69% | 1.87 | 59.0% | 3.06 | 14 | 3.1% | 0/8 | FAIL |
| 2 | `acceleration_band` | +2.25% | 0.75 | 45.0% | 1.41 | 12 | 2.9% | 0/8 | FAIL |
| 3 | `momentum_quality` | +0.62% | -0.00 | 43.1% | 1.07 | 63 | 11.3% | 0/8 | FAIL |
| 4 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 5 | `price_action_momentum` | -0.27% | -0.19 | 41.7% | 1.04 | 50 | 11.1% | 0/8 | FAIL |
| 6 | `roc_ma_cross` | -0.56% | -0.31 | 41.6% | 1.02 | 33 | 7.2% | 0/8 | FAIL |
| 7 | `volatility_cluster` | -2.09% | -0.48 | 44.5% | 0.94 | 52 | 8.6% | 0/8 | FAIL |
| 8 | `narrow_range` | -2.43% | -0.52 | 41.4% | 0.96 | 49 | 11.1% | 0/8 | FAIL |
| 9 | `htf_ema` | -3.03% | -0.74 | 39.5% | 0.90 | 34 | 9.1% | 0/8 | FAIL |
| 10 | `linear_channel_rev` | -3.56% | -1.11 | 35.9% | 0.81 | 29 | 6.8% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `dema_cross` | 60.8 | p100 | 1.87 | 2.01 | 3.06 | 14 | 3.1% | 0/8 | FAIL |
| 2 | `momentum_quality` | 52.2 | p95 | -0.00 | 2.30 | 1.07 | 63 | 11.3% | 0/8 | FAIL |
| 3 | `volatility_cluster` | 49.2 | p90 | -0.48 | 0.81 | 0.94 | 52 | 8.6% | 0/8 | FAIL |
| 4 | `price_action_momentum` | 47.4 | p85 | -0.19 | 2.04 | 1.04 | 50 | 11.1% | 0/8 | FAIL |
| 5 | `narrow_range` | 46.1 | p80 | -0.52 | 1.34 | 0.96 | 49 | 11.1% | 0/8 | FAIL |
| 6 | `cmf` | 43.8 | p76 | -1.21 | 1.68 | 0.87 | 60 | 13.1% | 0/8 | FAIL |
| 7 | `acceleration_band` | 43.1 | p71 | 0.75 | 1.31 | 1.41 | 12 | 2.9% | 0/8 | FAIL |
| 8 | `roc_ma_cross` | 42.1 | p66 | -0.31 | 1.86 | 1.02 | 33 | 7.2% | 0/8 | FAIL |
| 9 | `htf_ema` | 39.8 | p61 | -0.74 | 1.23 | 0.90 | 34 | 9.1% | 0/8 | FAIL |
| 10 | `elder_impulse` | 39.4 | p57 | -1.36 | 1.34 | 0.83 | 47 | 12.1% | 0/8 | FAIL |
| 11 | `linear_channel_rev` | 36.2 | p52 | -1.11 | 0.94 | 0.81 | 29 | 6.8% | 0/8 | FAIL |
| 12 | `lob_maker` | 35.2 | p47 | -2.66 | 1.30 | 0.71 | 69 | 19.8% | 0/8 | FAIL |
| 13 | `order_flow_imbalance_v2` | 34.1 | p42 | -2.74 | 2.12 | 0.74 | 75 | 20.1% | 0/8 | FAIL |
| 14 | `positional_scaling` | 32.8 | p38 | -1.82 | 2.03 | 0.77 | 39 | 12.2% | 0/8 | FAIL |
| 15 | `value_area` | 32.4 | p33 | -2.19 | 2.09 | 0.75 | 45 | 12.4% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `dema_cross` | +4.69% | 1.87 | 3.06 | 14 | 0/8 | FAIL |
| `acceleration_band` | +2.25% | 0.75 | 1.41 | 12 | 0/8 | FAIL |
| `momentum_quality` | +0.62% | -0.00 | 1.07 | 63 | 0/8 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `price_action_momentum` | -0.27% | -0.19 | 1.04 | 50 | 0/8 | FAIL |
| `roc_ma_cross` | -0.56% | -0.31 | 1.02 | 33 | 0/8 | FAIL |
| `volatility_cluster` | -2.09% | -0.48 | 0.94 | 52 | 0/8 | FAIL |
| `narrow_range` | -2.43% | -0.52 | 0.96 | 49 | 0/8 | FAIL |
| `htf_ema` | -3.03% | -0.74 | 0.90 | 34 | 0/8 | FAIL |
| `linear_channel_rev` | -3.56% | -1.11 | 0.81 | 29 | 0/8 | FAIL |
| `engulfing_zone` | -3.72% | -1.55 | 0.91 | 28 | 0/8 | FAIL |
| `cmf` | -6.15% | -1.21 | 0.87 | 60 | 0/8 | FAIL |
| `positional_scaling` | -6.57% | -1.82 | 0.77 | 39 | 0/8 | FAIL |
| `elder_impulse` | -6.88% | -1.36 | 0.83 | 47 | 0/8 | FAIL |
| `value_area` | -8.22% | -2.19 | 0.75 | 45 | 0/8 | FAIL |
| `price_cluster` | -10.00% | -2.58 | 0.64 | 32 | 0/8 | FAIL |
| `frama` | -11.73% | -2.62 | 0.68 | 47 | 0/8 | FAIL |
| `supertrend_multi` | -14.62% | -3.25 | 0.67 | 60 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -15.22% | -2.74 | 0.74 | 75 | 0/8 | FAIL |
| `relative_volume` | -16.09% | -3.61 | 0.61 | 62 | 0/8 | FAIL |
| `lob_maker` | -16.24% | -2.66 | 0.71 | 69 | 0/8 | FAIL |
| `volume_breakout` | -19.60% | -3.71 | 0.64 | 80 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `dema_cross` | trades 13 < 15 (x2), sharpe -1.04 < 1.0 (x1), profit_factor 0.75 < 1.5 (x1) |
| `acceleration_band` | trades 13 < 15 (x2), trades 12 < 15 (x2), trades 14 < 15 (x1) |
| `momentum_quality` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.062 > 0.05 (우연 가능성) (x1), profit_factor 1.44 < 1.5 (x1) |
| `wick_reversal` | no trades generated (x8) |
| `price_action_momentum` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.130 > 0.05 (우연 가능성) (x1), profit_factor 1.24 < 1.5 (x1) |
| `roc_ma_cross` | profit_factor 1.30 < 1.5 (x1), mc_p_value 0.250 > 0.05 (우연 가능성) (x1), sharpe -1.29 < 1.0 (x1) |
| `volatility_cluster` | sharpe -2.04 < 1.0 (x1), profit_factor 0.70 < 1.5 (x1), mc_p_value 0.854 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 0.94 < 1.5 (x2), sharpe -0.70 < 1.0 (x1), profit_factor 0.90 < 1.5 (x1) |
| `htf_ema` | profit_factor 0.90 < 1.5 (x2), profit_factor 0.61 < 1.5 (x2), sharpe -1.05 < 1.0 (x1) |
| `linear_channel_rev` | profit_factor 0.78 < 1.5 (x2), sharpe -1.30 < 1.0 (x1), mc_p_value 0.730 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | mc_p_value 1.000 > 0.05 (우연 가능성) (x2), sharpe -5.91 < 1.0 (x1), profit_factor 0.25 < 1.5 (x1) |
| `cmf` | profit_factor 0.61 < 1.5 (x2), profit_factor 1.20 < 1.5 (x1), mc_p_value 0.262 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | sharpe 0.68 < 1.0 (x1), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.368 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | mc_p_value 0.920 > 0.05 (우연 가능성) (x2), profit_factor 0.88 < 1.5 (x2), sharpe -2.90 < 1.0 (x1) |
| `value_area` | sharpe -3.63 < 1.0 (x1), profit_factor 0.58 < 1.5 (x1), mc_p_value 0.942 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | mc_p_value 0.940 > 0.05 (우연 가능성) (x2), sharpe -4.02 < 1.0 (x1), profit_factor 0.43 < 1.5 (x1) |
| `frama` | mc_p_value 0.970 > 0.05 (우연 가능성) (x2), sharpe -1.10 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1) |
| `supertrend_multi` | sharpe -5.92 < 1.0 (x1), max_drawdown 35.4% > 20% (x1), profit_factor 0.46 < 1.5 (x1) |
| `order_flow_imbalance_v2` | profit_factor 0.62 < 1.5 (x2), mc_p_value 0.964 > 0.05 (우연 가능성) (x2), profit_factor 1.33 < 1.5 (x1) |
| `relative_volume` | profit_factor 0.61 < 1.5 (x3), sharpe -3.72 < 1.0 (x1), mc_p_value 0.970 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.61 < 1.5 | 10 |
| no trades generated | 8 |
| mc_p_value 1.000 > 0.05 (우연 가능성) | 5 |
| profit_factor 0.65 < 1.5 | 5 |
| trades 13 < 15 | 4 |
| profit_factor 1.24 < 1.5 | 4 |
| profit_factor 0.68 < 1.5 | 4 |
| profit_factor 0.81 < 1.5 | 4 |
| mc_p_value 0.876 > 0.05 (우연 가능성) | 4 |
| trades 12 < 15 | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -6.34% -> $9,366
- **Top 5 균등배분**: +1.46% -> $10,146


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-01T15:43:42.233801Z_
_Symbol: SOL/USDT_
_Data Source: CSV SOL/USDT 1h (/home/user/Trading/data/historical)_
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
| 평균 수익률 | -4.75% |
| 최고 수익률 | 5.66% (roc_ma_cross) |
| 최저 수익률 | -15.55% (relative_volume) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `roc_ma_cross` | +5.66% | 1.35 | 49.7% | 1.43 | 34 | 6.9% | 1/8 | FAIL |
| 2 | `acceleration_band` | +4.18% | 1.85 | 56.1% | 2.43 | 8 | 2.0% | 0/8 | FAIL |
| 3 | `price_action_momentum` | +3.60% | 0.48 | 44.7% | 1.21 | 46 | 8.3% | 1/8 | FAIL |
| 4 | `price_cluster` | +0.56% | -0.30 | 42.4% | 1.12 | 25 | 8.1% | 1/8 | FAIL |
| 5 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 6 | `htf_ema` | -0.00% | -0.12 | 41.4% | 1.10 | 35 | 10.1% | 1/8 | FAIL |
| 7 | `momentum_quality` | -0.55% | -0.31 | 39.8% | 1.01 | 60 | 11.2% | 0/8 | FAIL |
| 8 | `positional_scaling` | -1.59% | -0.51 | 42.7% | 0.95 | 36 | 9.4% | 0/8 | FAIL |
| 9 | `volatility_cluster` | -2.56% | -0.77 | 41.7% | 0.90 | 49 | 9.3% | 0/8 | FAIL |
| 10 | `linear_channel_rev` | -2.91% | -0.83 | 34.9% | 1.07 | 22 | 6.5% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `roc_ma_cross` | 62.4 | p100 | 1.35 | 1.81 | 1.43 | 34 | 6.9% | 1/8 | FAIL |
| 2 | `price_action_momentum` | 57.9 | p95 | 0.48 | 2.68 | 1.21 | 46 | 8.3% | 1/8 | FAIL |
| 3 | `acceleration_band` | 53.9 | p90 | 1.85 | 0.86 | 2.43 | 8 | 2.0% | 0/8 | FAIL |
| 4 | `htf_ema` | 50.0 | p85 | -0.12 | 2.30 | 1.10 | 35 | 10.1% | 1/8 | FAIL |
| 5 | `price_cluster` | 45.8 | p80 | -0.30 | 2.63 | 1.12 | 25 | 8.1% | 1/8 | FAIL |
| 6 | `momentum_quality` | 45.8 | p76 | -0.31 | 2.43 | 1.01 | 60 | 11.2% | 0/8 | FAIL |
| 7 | `volatility_cluster` | 41.8 | p66 | -0.77 | 1.45 | 0.90 | 49 | 9.3% | 0/8 | FAIL |
| 8 | `order_flow_imbalance_v2` | 41.8 | p71 | -1.53 | 1.38 | 0.82 | 73 | 16.2% | 0/8 | FAIL |
| 9 | `positional_scaling` | 38.4 | p61 | -0.51 | 1.63 | 0.95 | 36 | 9.4% | 0/8 | FAIL |
| 10 | `frama` | 36.7 | p57 | -1.92 | 0.83 | 0.75 | 61 | 15.9% | 0/8 | FAIL |
| 11 | `supertrend_multi` | 36.4 | p52 | -0.88 | 1.71 | 0.94 | 40 | 12.4% | 0/8 | FAIL |
| 12 | `elder_impulse` | 35.5 | p47 | -1.40 | 1.24 | 0.80 | 47 | 12.8% | 0/8 | FAIL |
| 13 | `cmf` | 33.8 | p42 | -2.03 | 1.26 | 0.74 | 55 | 13.9% | 0/8 | FAIL |
| 14 | `linear_channel_rev` | 32.4 | p38 | -0.83 | 1.86 | 1.07 | 22 | 6.5% | 0/8 | FAIL |
| 15 | `value_area` | 30.5 | p33 | -2.14 | 1.07 | 0.71 | 45 | 12.6% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `roc_ma_cross` | +5.66% | 1.35 | 1.43 | 34 | 1/8 | FAIL |
| `acceleration_band` | +4.18% | 1.85 | 2.43 | 8 | 0/8 | FAIL |
| `price_action_momentum` | +3.60% | 0.48 | 1.21 | 46 | 1/8 | FAIL |
| `price_cluster` | +0.56% | -0.30 | 1.12 | 25 | 1/8 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `htf_ema` | -0.00% | -0.12 | 1.10 | 35 | 1/8 | FAIL |
| `momentum_quality` | -0.55% | -0.31 | 1.01 | 60 | 0/8 | FAIL |
| `positional_scaling` | -1.59% | -0.51 | 0.95 | 36 | 0/8 | FAIL |
| `volatility_cluster` | -2.56% | -0.77 | 0.90 | 49 | 0/8 | FAIL |
| `linear_channel_rev` | -2.91% | -0.83 | 1.07 | 22 | 0/8 | FAIL |
| `dema_cross` | -3.29% | -1.19 | 0.76 | 25 | 0/8 | FAIL |
| `supertrend_multi` | -4.59% | -0.88 | 0.94 | 40 | 0/8 | FAIL |
| `elder_impulse` | -6.37% | -1.40 | 0.80 | 47 | 0/8 | FAIL |
| `volume_breakout` | -7.77% | -1.95 | 0.81 | 54 | 0/8 | FAIL |
| `value_area` | -8.13% | -2.14 | 0.71 | 45 | 0/8 | FAIL |
| `cmf` | -9.03% | -2.03 | 0.74 | 55 | 0/8 | FAIL |
| `narrow_range` | -9.32% | -2.40 | 0.67 | 47 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -9.51% | -1.53 | 0.82 | 73 | 0/8 | FAIL |
| `engulfing_zone` | -10.93% | -3.29 | 0.53 | 28 | 0/8 | FAIL |
| `frama` | -11.00% | -1.92 | 0.75 | 61 | 0/8 | FAIL |
| `lob_maker` | -15.34% | -2.55 | 0.71 | 66 | 0/8 | FAIL |
| `relative_volume` | -15.55% | -3.48 | 0.63 | 62 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `roc_ma_cross` | mc_p_value 0.064 > 0.05 (우연 가능성) (x1), profit_factor 1.43 < 1.5 (x1), mc_p_value 0.222 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | trades 7 < 15 (x3), trades 9 < 15 (x2), sharpe 0.83 < 1.0 (x1) |
| `price_action_momentum` | mc_p_value 0.064 > 0.05 (우연 가능성) (x1), mc_p_value 0.092 > 0.05 (우연 가능성) (x1), sharpe -1.69 < 1.0 (x1) |
| `price_cluster` | sharpe 0.61 < 1.0 (x1), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.338 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x8) |
| `htf_ema` | sharpe 0.70 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.376 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | mc_p_value 0.088 > 0.05 (우연 가능성) (x1), sharpe 0.00 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1) |
| `positional_scaling` | profit_factor 0.64 < 1.5 (x2), profit_factor 1.32 < 1.5 (x1), mc_p_value 0.252 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -1.30 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1), mc_p_value 0.752 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -2.46 < 1.0 (x1), profit_factor 0.62 < 1.5 (x1), mc_p_value 0.856 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | sharpe -2.05 < 1.0 (x1), profit_factor 0.60 < 1.5 (x1), mc_p_value 0.868 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | profit_factor 0.72 < 1.5 (x2), sharpe -0.03 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1) |
| `elder_impulse` | profit_factor 0.96 < 1.5 (x2), sharpe -2.05 < 1.0 (x1), profit_factor 0.71 < 1.5 (x1) |
| `volume_breakout` | sharpe -0.80 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.642 > 0.05 (우연 가능성) (x1) |
| `value_area` | profit_factor 0.64 < 1.5 (x2), sharpe -3.46 < 1.0 (x1), profit_factor 0.57 < 1.5 (x1) |
| `cmf` | sharpe -1.07 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.734 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 0.69 < 1.5 (x2), sharpe -2.21 < 1.0 (x1), mc_p_value 0.876 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 0.89 < 1.5 (x2), max_drawdown 24.0% > 20% (x2), sharpe -0.89 < 1.0 (x1) |
| `engulfing_zone` | sharpe -3.94 < 1.0 (x1), profit_factor 0.38 < 1.5 (x1), mc_p_value 0.980 > 0.05 (우연 가능성) (x1) |
| `frama` | profit_factor 0.76 < 1.5 (x2), profit_factor 0.79 < 1.5 (x2), sharpe -1.65 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 8 |
| profit_factor 0.72 < 1.5 | 6 |
| profit_factor 0.89 < 1.5 | 5 |
| profit_factor 0.74 < 1.5 | 4 |
| profit_factor 0.69 < 1.5 | 4 |
| profit_factor 0.67 < 1.5 | 4 |
| profit_factor 0.64 < 1.5 | 4 |
| profit_factor 0.58 < 1.5 | 4 |
| profit_factor 0.71 < 1.5 | 4 |
| mc_p_value 1.000 > 0.05 (우연 가능성) | 4 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -4.75% -> $9,525
- **Top 5 균등배분**: +2.80% -> $10,280
