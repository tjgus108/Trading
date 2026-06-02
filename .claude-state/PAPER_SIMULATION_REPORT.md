# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-02T10:37:58.522478Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-02T10:43:45.091733Z_
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
| 평균 수익률 | -3.54% |
| 최고 수익률 | 5.87% (supertrend_multi) |
| 최저 수익률 | -10.01% (elder_impulse) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +5.87% | 0.43 | 36.6% | 1.13 | 47 | 10.5% | 2/8 | FAIL |
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
| 1 | `supertrend_multi` | 72.6 | p100 | 0.43 | 2.62 | 1.13 | 47 | 10.5% | 2/8 | FAIL |
| 2 | `price_cluster` | 69.2 | p95 | 0.40 | 1.43 | 1.12 | 45 | 11.8% | 1/8 | FAIL |
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
| `supertrend_multi` | +5.87% | 0.43 | 1.13 | 47 | 2/8 | FAIL |
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
| `supertrend_multi` | profit_factor 1.44 < 1.5 (x1), mc_p_value 0.189 > 0.05 (우연 가능성) (x1), sharpe -0.68 < 1.0 (x1) |
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
| `wick_reversal` | profit_factor 0.70 < 1.5 (x2), sharpe -1.91 < 1.0 (x1), mc_p_value 0.792 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | mc_p_value 0.876 > 0.05 (우연 가능성) (x2), sharpe -2.23 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1) |
| `relative_volume` | sharpe -2.07 < 1.0 (x1), profit_factor 0.77 < 1.5 (x1), mc_p_value 0.832 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 0.78 < 1.5 (x2), profit_factor 1.17 < 1.5 (x1), mc_p_value 0.285 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe 0.01 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -1.04 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.695 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.01 < 1.5 | 6 |
| profit_factor 0.82 < 1.5 | 6 |
| profit_factor 0.78 < 1.5 | 5 |
| profit_factor 0.89 < 1.5 | 4 |
| profit_factor 0.91 < 1.5 | 4 |
| profit_factor 0.77 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 0.47 < 1.5 | 3 |
| profit_factor 0.96 < 1.5 | 3 |
| profit_factor 1.06 < 1.5 | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.54% -> $9,646
- **Top 5 균등배분**: +2.16% -> $10,216


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-02T10:50:01.255471Z_
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
| 평균 수익률 | -5.69% |
| 최고 수익률 | 3.88% (momentum_quality) |
| 최저 수익률 | -19.68% (supertrend_multi) |

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
| 1 | `momentum_quality` | 65.8 | p100 | 0.73 | 1.60 | 1.17 | 63 | 10.4% | 0/8 | FAIL |
| 2 | `volatility_cluster` | 58.4 | p95 | 0.27 | 1.39 | 1.09 | 51 | 9.1% | 0/8 | FAIL |
| 3 | `price_action_momentum` | 56.9 | p90 | 0.20 | 1.39 | 1.08 | 51 | 10.8% | 0/8 | FAIL |
| 4 | `dema_cross` | 55.6 | p85 | 0.81 | 2.05 | 1.72 | 14 | 3.4% | 0/8 | FAIL |
| 5 | `narrow_range` | 55.2 | p80 | 0.01 | 1.59 | 1.06 | 51 | 10.9% | 0/8 | FAIL |
| 6 | `engulfing_zone` | 45.5 | p76 | -1.30 | 3.43 | 0.98 | 27 | 10.2% | 1/8 | FAIL |
| 7 | `cmf` | 44.7 | p71 | -1.16 | 2.20 | 0.89 | 60 | 16.3% | 0/8 | FAIL |
| 8 | `lob_maker` | 42.6 | p66 | -1.70 | 1.35 | 0.81 | 70 | 20.7% | 0/8 | FAIL |
| 9 | `elder_impulse` | 41.4 | p61 | -1.29 | 1.75 | 0.85 | 46 | 12.2% | 0/8 | FAIL |
| 10 | `roc_ma_cross` | 40.7 | p57 | -1.02 | 1.10 | 0.85 | 34 | 9.7% | 0/8 | FAIL |
| 11 | `value_area` | 39.5 | p52 | -1.58 | 1.67 | 0.81 | 46 | 11.5% | 0/8 | FAIL |
| 12 | `volume_breakout` | 39.1 | p47 | -2.25 | 1.91 | 0.78 | 79 | 21.4% | 0/8 | FAIL |
| 13 | `linear_channel_rev` | 38.5 | p42 | -1.08 | 0.74 | 0.81 | 28 | 6.8% | 0/8 | FAIL |
| 14 | `relative_volume` | 37.3 | p38 | -2.34 | 1.53 | 0.74 | 60 | 15.1% | 0/8 | FAIL |
| 15 | `htf_ema` | 36.1 | p33 | -1.37 | 1.72 | 0.80 | 31 | 9.9% | 0/8 | FAIL |

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
| `supertrend_multi` | -19.68% | -3.75 | 0.61 | 66 | 0/8 | FAIL |

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
| profit_factor 0.83 < 1.5 | 5 |
| profit_factor 0.82 < 1.5 | 5 |
| profit_factor 0.94 < 1.5 | 5 |
| profit_factor 1.11 < 1.5 | 4 |
| profit_factor 0.73 < 1.5 | 4 |
| profit_factor 0.72 < 1.5 | 4 |
| profit_factor 0.61 < 1.5 | 4 |
| profit_factor 0.46 < 1.5 | 4 |
| profit_factor 1.28 < 1.5 | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -5.69% -> $9,431
- **Top 5 균등배분**: +1.56% -> $10,156


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-02T10:55:31.860693Z_
_Symbol: SOL/USDT_
_Data Source: CSV fallback SOL/USDT 1h (/home/user/Trading/data/historical)_
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
| 평균 수익률 | -4.27% |
| 최고 수익률 | 2.16% (htf_ema) |
| 최저 수익률 | -12.26% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `htf_ema` | +2.16% | 0.51 | 38.8% | 1.15 | 35 | 7.9% | 0/8 | FAIL |
| 2 | `momentum_quality` | +2.09% | 0.26 | 40.0% | 1.12 | 64 | 11.4% | 1/8 | FAIL |
| 3 | `elder_impulse` | +1.24% | 0.27 | 39.6% | 1.06 | 47 | 10.2% | 0/8 | FAIL |
| 4 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 5 | `volatility_cluster` | -0.11% | 0.02 | 39.5% | 1.02 | 49 | 9.7% | 0/8 | FAIL |
| 6 | `order_flow_imbalance_v2` | -0.16% | -0.09 | 37.3% | 1.00 | 75 | 13.6% | 0/8 | FAIL |
| 7 | `acceleration_band` | -0.24% | -0.23 | 35.3% | 1.27 | 7 | 3.7% | 0/8 | FAIL |
| 8 | `price_action_momentum` | -0.41% | -0.35 | 39.4% | 1.08 | 48 | 10.6% | 1/8 | FAIL |
| 9 | `price_cluster` | -1.07% | -0.39 | 38.2% | 0.93 | 24 | 7.2% | 0/8 | FAIL |
| 10 | `roc_ma_cross` | -1.85% | -0.75 | 39.0% | 0.92 | 32 | 7.9% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 75.0 | p100 | 0.26 | 2.41 | 1.12 | 64 | 11.4% | 1/8 | FAIL |
| 2 | `order_flow_imbalance_v2` | 64.6 | p90 | -0.09 | 1.71 | 1.00 | 75 | 13.6% | 0/8 | FAIL |
| 3 | `price_action_momentum` | 64.6 | p95 | -0.35 | 2.73 | 1.08 | 48 | 10.6% | 1/8 | FAIL |
| 4 | `elder_impulse` | 62.4 | p85 | 0.27 | 1.15 | 1.06 | 47 | 10.2% | 0/8 | FAIL |
| 5 | `htf_ema` | 61.9 | p80 | 0.51 | 1.24 | 1.15 | 35 | 7.9% | 0/8 | FAIL |
| 6 | `volatility_cluster` | 61.2 | p76 | 0.02 | 1.04 | 1.02 | 49 | 9.7% | 0/8 | FAIL |
| 7 | `frama` | 49.3 | p71 | -1.18 | 1.24 | 0.84 | 60 | 14.6% | 0/8 | FAIL |
| 8 | `volume_breakout` | 48.7 | p66 | -0.90 | 2.44 | 0.93 | 58 | 15.4% | 0/8 | FAIL |
| 9 | `acceleration_band` | 47.0 | p61 | -0.23 | 1.66 | 1.27 | 7 | 3.7% | 0/8 | FAIL |
| 10 | `price_cluster` | 47.0 | p52 | -0.39 | 1.22 | 0.93 | 24 | 7.2% | 0/8 | FAIL |
| 11 | `narrow_range` | 47.0 | p57 | -1.07 | 2.06 | 0.89 | 48 | 10.6% | 0/8 | FAIL |
| 12 | `roc_ma_cross` | 46.1 | p47 | -0.75 | 1.96 | 0.92 | 32 | 7.9% | 0/8 | FAIL |
| 13 | `relative_volume` | 43.6 | p42 | -1.93 | 1.05 | 0.76 | 62 | 14.1% | 0/8 | FAIL |
| 14 | `lob_maker` | 40.3 | p38 | -1.92 | 1.63 | 0.78 | 67 | 19.6% | 0/8 | FAIL |
| 15 | `supertrend_multi` | 39.5 | p33 | -1.67 | 1.94 | 0.83 | 48 | 15.4% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `htf_ema` | +2.16% | 0.51 | 1.15 | 35 | 0/8 | FAIL |
| `momentum_quality` | +2.09% | 0.26 | 1.12 | 64 | 1/8 | FAIL |
| `elder_impulse` | +1.24% | 0.27 | 1.06 | 47 | 0/8 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `volatility_cluster` | -0.11% | 0.02 | 1.02 | 49 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -0.16% | -0.09 | 1.00 | 75 | 0/8 | FAIL |
| `acceleration_band` | -0.24% | -0.23 | 1.27 | 7 | 0/8 | FAIL |
| `price_action_momentum` | -0.41% | -0.35 | 1.08 | 48 | 1/8 | FAIL |
| `price_cluster` | -1.07% | -0.39 | 0.93 | 24 | 0/8 | FAIL |
| `roc_ma_cross` | -1.85% | -0.75 | 0.92 | 32 | 0/8 | FAIL |
| `narrow_range` | -3.94% | -1.07 | 0.89 | 48 | 0/8 | FAIL |
| `dema_cross` | -4.03% | -1.50 | 0.70 | 26 | 0/8 | FAIL |
| `volume_breakout` | -4.04% | -0.90 | 0.93 | 58 | 0/8 | FAIL |
| `linear_channel_rev` | -6.42% | -1.98 | 0.67 | 28 | 0/8 | FAIL |
| `frama` | -7.17% | -1.18 | 0.84 | 60 | 0/8 | FAIL |
| `value_area` | -8.08% | -2.20 | 0.72 | 47 | 0/8 | FAIL |
| `supertrend_multi` | -8.54% | -1.67 | 0.83 | 48 | 0/8 | FAIL |
| `engulfing_zone` | -9.78% | -3.27 | 0.63 | 26 | 0/8 | FAIL |
| `relative_volume` | -10.03% | -1.93 | 0.76 | 62 | 0/8 | FAIL |
| `cmf` | -10.44% | -2.19 | 0.73 | 57 | 0/8 | FAIL |
| `positional_scaling` | -10.94% | -3.01 | 0.59 | 40 | 0/8 | FAIL |
| `lob_maker` | -12.26% | -1.92 | 0.78 | 67 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `htf_ema` | sharpe -0.85 < 1.0 (x1), profit_factor 0.84 < 1.5 (x1), mc_p_value 0.666 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | sharpe -1.57 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1), mc_p_value 0.782 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -1.24 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1), mc_p_value 0.720 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x8) |
| `volatility_cluster` | sharpe -1.85 < 1.0 (x1), profit_factor 0.74 < 1.5 (x1), mc_p_value 0.824 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe -2.67 < 1.0 (x1), profit_factor 0.70 < 1.5 (x1), mc_p_value 0.905 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | trades 7 < 15 (x4), trades 8 < 15 (x2), trades 6 < 15 (x2) |
| `price_action_momentum` | sharpe -2.60 < 1.0 (x1), profit_factor 0.67 < 1.5 (x1), mc_p_value 0.909 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe 0.04 < 1.0 (x2), profit_factor 1.01 < 1.5 (x1), mc_p_value 0.480 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 0.64 < 1.5 (x2), sharpe -2.07 < 1.0 (x1), mc_p_value 0.856 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | sharpe -3.85 < 1.0 (x1), profit_factor 0.55 < 1.5 (x1), mc_p_value 0.968 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | profit_factor 0.57 < 1.5 (x2), sharpe -1.75 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1) |
| `volume_breakout` | sharpe -3.05 < 1.0 (x2), profit_factor 0.63 < 1.5 (x2), sharpe -4.60 < 1.0 (x1) |
| `linear_channel_rev` | sharpe -3.28 < 1.0 (x1), profit_factor 0.49 < 1.5 (x1), mc_p_value 0.954 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe -2.50 < 1.0 (x1), max_drawdown 22.7% > 20% (x1), profit_factor 0.66 < 1.5 (x1) |
| `value_area` | profit_factor 0.83 < 1.5 (x2), sharpe -1.54 < 1.0 (x1), profit_factor 0.78 < 1.5 (x1) |
| `supertrend_multi` | sharpe -3.85 < 1.0 (x1), max_drawdown 22.2% > 20% (x1), profit_factor 0.56 < 1.5 (x1) |
| `engulfing_zone` | sharpe -3.32 < 1.0 (x1), profit_factor 0.39 < 1.5 (x1), mc_p_value 0.957 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | sharpe -1.66 < 1.0 (x2), profit_factor 0.79 < 1.5 (x2), sharpe -3.48 < 1.0 (x1) |
| `cmf` | sharpe -5.55 < 1.0 (x1), max_drawdown 23.7% > 20% (x1), profit_factor 0.43 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 8 |
| profit_factor 1.26 < 1.5 | 4 |
| profit_factor 0.65 < 1.5 | 4 |
| profit_factor 0.83 < 1.5 | 4 |
| profit_factor 0.74 < 1.5 | 4 |
| trades 7 < 15 | 4 |
| profit_factor 0.50 < 1.5 | 4 |
| profit_factor 0.57 < 1.5 | 4 |
| profit_factor 0.64 < 1.5 | 4 |
| profit_factor 0.63 < 1.5 | 4 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -4.27% -> $9,573
- **Top 5 균등배분**: +1.08% -> $10,108
