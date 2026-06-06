# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-06T20:12:06.089528Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-06T20:19:26.852093Z_
_Symbol: BTC/USDT_
_Data Source: CSV fallback BTC/USDT 1h (/home/user/Trading/data/historical)_
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
| 평균 수익률 | -3.86% |
| 최고 수익률 | 6.73% (supertrend_multi) |
| 최저 수익률 | -12.97% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +6.73% | 0.60 | 37.7% | 1.17 | 48 | 10.4% | 2/8 | FAIL |
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
| 1 | `supertrend_multi` | 73.9 | p100 | 0.60 | 2.65 | 1.17 | 48 | 10.4% | 2/8 | FAIL |
| 2 | `price_cluster` | 67.9 | p95 | 0.40 | 1.43 | 1.12 | 45 | 11.8% | 1/8 | FAIL |
| 3 | `roc_ma_cross` | 65.7 | p90 | -0.11 | 2.66 | 1.15 | 40 | 9.1% | 2/8 | FAIL |
| 4 | `narrow_range` | 59.5 | p85 | -0.10 | 1.28 | 1.04 | 50 | 11.1% | 0/8 | FAIL |
| 5 | `positional_scaling` | 59.0 | p80 | -0.10 | 3.00 | 1.17 | 36 | 10.4% | 1/8 | FAIL |
| 6 | `order_flow_imbalance_v2` | 58.7 | p76 | -0.55 | 1.81 | 0.98 | 77 | 14.8% | 0/8 | FAIL |
| 7 | `frama` | 58.4 | p71 | 0.01 | 1.26 | 1.06 | 42 | 9.6% | 0/8 | FAIL |
| 8 | `volume_breakout` | 57.4 | p66 | -0.35 | 2.65 | 1.04 | 78 | 15.7% | 0/8 | FAIL |
| 9 | `lob_maker` | 57.2 | p61 | -0.55 | 1.81 | 0.98 | 84 | 18.9% | 0/8 | FAIL |
| 10 | `htf_ema` | 56.9 | p57 | -0.15 | 1.26 | 1.02 | 45 | 11.1% | 0/8 | FAIL |
| 11 | `price_action_momentum` | 54.8 | p52 | -0.85 | 2.97 | 1.01 | 82 | 18.2% | 1/8 | FAIL |
| 12 | `momentum_quality` | 54.1 | p47 | -0.81 | 2.93 | 1.00 | 66 | 15.3% | 1/8 | FAIL |
| 13 | `cmf` | 48.6 | p42 | -1.24 | 1.68 | 0.90 | 75 | 18.3% | 0/8 | FAIL |
| 14 | `acceleration_band` | 45.5 | p38 | -0.87 | 2.19 | 0.97 | 45 | 14.5% | 0/8 | FAIL |
| 15 | `relative_volume` | 43.9 | p33 | -1.44 | 1.74 | 0.86 | 59 | 14.0% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +6.73% | 0.60 | 1.17 | 48 | 2/8 | FAIL |
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
| `engulfing_zone` | -5.44% | -1.38 | 0.81 | 25 | 0/8 | FAIL |
| `relative_volume` | -7.45% | -1.44 | 0.86 | 59 | 0/8 | FAIL |
| `cmf` | -8.46% | -1.24 | 0.90 | 75 | 0/8 | FAIL |
| `linear_channel_rev` | -8.50% | -2.82 | 0.63 | 29 | 0/8 | FAIL |
| `volatility_cluster` | -9.44% | -2.02 | 0.82 | 60 | 0/8 | FAIL |
| `value_area` | -9.68% | -2.50 | 0.73 | 46 | 0/8 | FAIL |
| `elder_impulse` | -10.01% | -2.02 | 0.75 | 47 | 0/8 | FAIL |
| `wick_reversal` | -12.97% | -3.20 | 0.63 | 42 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.159 > 0.05 (우연 가능성) (x1), sharpe -0.68 < 1.0 (x1) |
| `price_cluster` | profit_factor 1.01 < 1.5 (x2), sharpe -1.43 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1) |
| `positional_scaling` | mc_p_value 0.106 > 0.05 (우연 가능성) (x1), sharpe -1.00 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1) |
| `roc_ma_cross` | sharpe 0.21 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.445 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe -0.16 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.468 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | sharpe 0.69 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.350 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | sharpe 0.57 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1), mc_p_value 0.376 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x4), trades 2 < 15 (x3), trades 3 < 15 (x2) |
| `volume_breakout` | sharpe -0.23 < 1.0 (x1), max_drawdown 21.7% > 20% (x1), profit_factor 1.00 < 1.5 (x1) |
| `momentum_quality` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.156 > 0.05 (우연 가능성) (x1), sharpe -0.44 < 1.0 (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.16 < 1.5 (x1), mc_p_value 0.268 > 0.05 (우연 가능성) (x1), sharpe -0.46 < 1.0 (x1) |
| `price_action_momentum` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.216 > 0.05 (우연 가능성) (x1), sharpe -2.05 < 1.0 (x1) |
| `acceleration_band` | profit_factor 1.32 < 1.5 (x1), mc_p_value 0.213 > 0.05 (우연 가능성) (x1), sharpe -1.56 < 1.0 (x1) |
| `lob_maker` | max_drawdown 25.6% > 20% (x2), sharpe -1.80 < 1.0 (x1), max_drawdown 30.1% > 20% (x1) |
| `engulfing_zone` | mc_p_value 0.876 > 0.05 (우연 가능성) (x2), sharpe -2.23 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1) |
| `relative_volume` | sharpe -2.07 < 1.0 (x1), profit_factor 0.77 < 1.5 (x1), mc_p_value 0.832 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 0.78 < 1.5 (x2), profit_factor 1.17 < 1.5 (x1), mc_p_value 0.285 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe 0.01 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -1.04 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.695 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -0.25 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1), mc_p_value 0.530 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.01 < 1.5 | 7 |
| profit_factor 0.82 < 1.5 | 6 |
| profit_factor 0.78 < 1.5 | 5 |
| profit_factor 0.63 < 1.5 | 4 |
| profit_factor 0.89 < 1.5 | 4 |
| profit_factor 0.91 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 0.96 < 1.5 | 3 |
| profit_factor 1.06 < 1.5 | 3 |
| profit_factor 0.83 < 1.5 | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.86% -> $9,614
- **Top 5 균등배분**: +2.34% -> $10,234


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-06T20:26:53.049179Z_
_Symbol: ETH/USDT_
_Data Source: CSV fallback ETH/USDT 1h (/home/user/Trading/data/historical)_
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
| 평균 수익률 | -5.55% |
| 최고 수익률 | 3.88% (momentum_quality) |
| 최저 수익률 | -16.68% (supertrend_multi) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +3.88% | 0.73 | 44.0% | 1.17 | 63 | 10.4% | 0/8 | FAIL |
| 2 | `dema_cross` | +1.74% | 0.81 | 56.1% | 1.72 | 14 | 3.4% | 0/8 | FAIL |
| 3 | `volatility_cluster` | +1.20% | 0.27 | 42.5% | 1.09 | 51 | 9.1% | 0/8 | FAIL |
| 4 | `price_action_momentum` | +0.85% | 0.20 | 42.8% | 1.08 | 51 | 10.8% | 0/8 | FAIL |
| 5 | `narrow_range` | +0.10% | 0.01 | 42.0% | 1.06 | 51 | 10.9% | 0/8 | FAIL |
| 6 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 7 | `engulfing_zone` | -2.17% | -1.30 | 37.7% | 0.98 | 27 | 10.2% | 1/8 | FAIL |
| 8 | `linear_channel_rev` | -3.48% | -1.08 | 36.0% | 0.81 | 28 | 6.8% | 0/8 | FAIL |
| 9 | `roc_ma_cross` | -3.92% | -1.02 | 38.6% | 0.85 | 34 | 9.7% | 0/8 | FAIL |
| 10 | `acceleration_band` | -4.40% | -2.12 | 30.6% | 0.62 | 11 | 6.3% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 65.6 | p100 | 0.73 | 1.60 | 1.17 | 63 | 10.4% | 0/8 | FAIL |
| 2 | `volatility_cluster` | 58.2 | p95 | 0.27 | 1.39 | 1.09 | 51 | 9.1% | 0/8 | FAIL |
| 3 | `price_action_momentum` | 56.6 | p90 | 0.20 | 1.39 | 1.08 | 51 | 10.8% | 0/8 | FAIL |
| 4 | `dema_cross` | 55.6 | p85 | 0.81 | 2.05 | 1.72 | 14 | 3.4% | 0/8 | FAIL |
| 5 | `narrow_range` | 54.9 | p80 | 0.01 | 1.59 | 1.06 | 51 | 10.9% | 0/8 | FAIL |
| 6 | `engulfing_zone` | 44.9 | p76 | -1.30 | 3.43 | 0.98 | 27 | 10.2% | 1/8 | FAIL |
| 7 | `cmf` | 44.0 | p71 | -1.16 | 2.20 | 0.89 | 60 | 16.3% | 0/8 | FAIL |
| 8 | `lob_maker` | 41.7 | p66 | -1.70 | 1.35 | 0.81 | 70 | 20.7% | 0/8 | FAIL |
| 9 | `elder_impulse` | 40.8 | p61 | -1.29 | 1.75 | 0.85 | 46 | 12.2% | 0/8 | FAIL |
| 10 | `roc_ma_cross` | 40.2 | p57 | -1.02 | 1.10 | 0.85 | 34 | 9.7% | 0/8 | FAIL |
| 11 | `value_area` | 38.8 | p52 | -1.58 | 1.67 | 0.81 | 46 | 11.5% | 0/8 | FAIL |
| 12 | `linear_channel_rev` | 38.0 | p47 | -1.08 | 0.74 | 0.81 | 28 | 6.8% | 0/8 | FAIL |
| 13 | `volume_breakout` | 38.0 | p42 | -2.25 | 1.91 | 0.78 | 79 | 21.4% | 0/8 | FAIL |
| 14 | `relative_volume` | 36.3 | p38 | -2.34 | 1.53 | 0.74 | 60 | 15.1% | 0/8 | FAIL |
| 15 | `htf_ema` | 35.5 | p33 | -1.37 | 1.72 | 0.80 | 31 | 9.9% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +3.88% | 0.73 | 1.17 | 63 | 0/8 | FAIL |
| `dema_cross` | +1.74% | 0.81 | 1.72 | 14 | 0/8 | FAIL |
| `volatility_cluster` | +1.20% | 0.27 | 1.09 | 51 | 0/8 | FAIL |
| `price_action_momentum` | +0.85% | 0.20 | 1.08 | 51 | 0/8 | FAIL |
| `narrow_range` | +0.10% | 0.01 | 1.06 | 51 | 0/8 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `engulfing_zone` | -2.17% | -1.30 | 0.98 | 27 | 1/8 | FAIL |
| `linear_channel_rev` | -3.48% | -1.08 | 0.81 | 28 | 0/8 | FAIL |
| `roc_ma_cross` | -3.92% | -1.02 | 0.85 | 34 | 0/8 | FAIL |
| `acceleration_band` | -4.40% | -2.12 | 0.62 | 11 | 0/8 | FAIL |
| `htf_ema` | -4.56% | -1.37 | 0.80 | 31 | 0/8 | FAIL |
| `price_cluster` | -4.96% | -1.40 | 0.82 | 28 | 0/8 | FAIL |
| `cmf` | -5.18% | -1.16 | 0.89 | 60 | 0/8 | FAIL |
| `elder_impulse` | -5.87% | -1.29 | 0.85 | 46 | 0/8 | FAIL |
| `value_area` | -6.29% | -1.58 | 0.81 | 46 | 0/8 | FAIL |
| `positional_scaling` | -9.07% | -2.37 | 0.66 | 37 | 0/8 | FAIL |
| `relative_volume` | -10.92% | -2.34 | 0.74 | 60 | 0/8 | FAIL |
| `frama` | -11.13% | -2.30 | 0.69 | 46 | 0/8 | FAIL |
| `lob_maker` | -11.41% | -1.70 | 0.81 | 70 | 0/8 | FAIL |
| `volume_breakout` | -13.29% | -2.25 | 0.78 | 79 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -16.54% | -2.92 | 0.70 | 74 | 0/8 | FAIL |
| `supertrend_multi` | -16.68% | -3.58 | 0.62 | 61 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | mc_p_value 0.352 > 0.05 (우연 가능성) (x2), sharpe 0.16 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1) |
| `dema_cross` | trades 11 < 15 (x3), trades 12 < 15 (x2), sharpe -0.53 < 1.0 (x1) |
| `volatility_cluster` | sharpe -0.17 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1), mc_p_value 0.539 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe -1.17 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1), mc_p_value 0.694 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.27 < 1.5 (x2), sharpe -2.08 < 1.0 (x2), sharpe -1.02 < 1.0 (x1) |
| `wick_reversal` | no trades generated (x8) |
| `engulfing_zone` | profit_factor 1.09 < 1.5 (x2), sharpe -4.95 < 1.0 (x1), profit_factor 0.32 < 1.5 (x1) |
| `linear_channel_rev` | profit_factor 0.82 < 1.5 (x2), sharpe -0.99 < 1.0 (x1), mc_p_value 0.682 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -0.33 < 1.0 (x1), profit_factor 0.94 < 1.5 (x1), mc_p_value 0.579 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | trades 6 < 15 (x2), trades 14 < 15 (x2), profit_factor 0.61 < 1.5 (x2) |
| `htf_ema` | sharpe -0.76 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.635 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -2.23 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1), mc_p_value 0.852 > 0.05 (우연 가능성) (x1) |
| `cmf` | sharpe -2.27 < 1.0 (x1), profit_factor 0.72 < 1.5 (x1), mc_p_value 0.862 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -0.79 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.660 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -1.29 < 1.0 (x1), profit_factor 0.82 < 1.5 (x1), mc_p_value 0.699 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 0.54 < 1.5 (x2), sharpe -4.31 < 1.0 (x1), profit_factor 0.46 < 1.5 (x1) |
| `relative_volume` | sharpe -2.79 < 1.0 (x1), profit_factor 0.67 < 1.5 (x1), mc_p_value 0.908 > 0.05 (우연 가능성) (x1) |
| `frama` | mc_p_value 0.810 > 0.05 (우연 가능성) (x2), profit_factor 0.73 < 1.5 (x2), sharpe -1.51 < 1.0 (x1) |
| `lob_maker` | sharpe -2.62 < 1.0 (x1), max_drawdown 23.9% > 20% (x1), profit_factor 0.71 < 1.5 (x1) |
| `volume_breakout` | profit_factor 0.94 < 1.5 (x2), sharpe -2.26 < 1.0 (x1), profit_factor 0.75 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 8 |
| profit_factor 0.83 < 1.5 | 6 |
| profit_factor 0.73 < 1.5 | 5 |
| profit_factor 0.82 < 1.5 | 5 |
| profit_factor 0.94 < 1.5 | 5 |
| profit_factor 1.11 < 1.5 | 4 |
| profit_factor 0.61 < 1.5 | 4 |
| profit_factor 0.71 < 1.5 | 4 |
| profit_factor 1.28 < 1.5 | 3 |
| profit_factor 1.14 < 1.5 | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -5.55% -> $9,445
- **Top 5 균등배분**: +1.56% -> $10,156
