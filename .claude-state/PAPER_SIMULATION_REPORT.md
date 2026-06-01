# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-01T10:27:03.926080Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-01T10:31:57.289248Z_
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
| 평균 수익률 | -3.37% |
| 최고 수익률 | 5.64% (supertrend_multi) |
| 최저 수익률 | -9.68% (value_area) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +5.64% | 0.50 | 36.6% | 1.15 | 47 | 9.8% | 1/8 | FAIL |
| 2 | `price_cluster` | +2.46% | 0.41 | 39.4% | 1.13 | 45 | 10.9% | 1/8 | FAIL |
| 3 | `roc_ma_cross` | +1.05% | -0.10 | 37.9% | 1.15 | 40 | 9.1% | 2/8 | FAIL |
| 4 | `positional_scaling` | +0.68% | -0.20 | 36.5% | 1.14 | 36 | 10.0% | 1/8 | FAIL |
| 5 | `frama` | -0.04% | -0.00 | 38.9% | 1.05 | 42 | 8.7% | 0/8 | FAIL |
| 6 | `narrow_range` | -0.37% | -0.04 | 38.6% | 1.05 | 50 | 10.4% | 0/8 | FAIL |
| 7 | `htf_ema` | -1.18% | -0.16 | 38.5% | 1.02 | 45 | 10.4% | 0/8 | FAIL |
| 8 | `dema_cross` | -1.35% | -1.70 | 19.6% | 0.39 | 3 | 2.2% | 0/8 | FAIL |
| 9 | `volume_breakout` | -1.43% | -0.36 | 37.5% | 1.04 | 78 | 15.2% | 0/8 | FAIL |
| 10 | `momentum_quality` | -2.73% | -0.80 | 34.3% | 1.00 | 66 | 15.1% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 69.3 | p100 | 0.41 | 1.49 | 1.13 | 45 | 10.9% | 1/8 | FAIL |
| 2 | `supertrend_multi` | 68.5 | p95 | 0.50 | 2.57 | 1.15 | 47 | 9.8% | 1/8 | FAIL |
| 3 | `roc_ma_cross` | 66.2 | p90 | -0.10 | 2.64 | 1.15 | 40 | 9.1% | 2/8 | FAIL |
| 4 | `narrow_range` | 60.8 | p85 | -0.04 | 1.29 | 1.05 | 50 | 10.4% | 0/8 | FAIL |
| 5 | `frama` | 59.1 | p76 | -0.00 | 1.24 | 1.05 | 42 | 8.7% | 0/8 | FAIL |
| 6 | `order_flow_imbalance_v2` | 59.1 | p80 | -0.54 | 1.71 | 0.98 | 77 | 13.7% | 0/8 | FAIL |
| 7 | `positional_scaling` | 57.8 | p71 | -0.20 | 2.95 | 1.14 | 36 | 10.0% | 1/8 | FAIL |
| 8 | `lob_maker` | 57.5 | p66 | -0.55 | 1.81 | 0.98 | 84 | 17.0% | 0/8 | FAIL |
| 9 | `htf_ema` | 57.2 | p61 | -0.16 | 1.29 | 1.02 | 45 | 10.4% | 0/8 | FAIL |
| 10 | `volume_breakout` | 56.7 | p57 | -0.36 | 2.66 | 1.04 | 78 | 15.2% | 0/8 | FAIL |
| 11 | `price_action_momentum` | 54.4 | p52 | -0.80 | 2.97 | 1.02 | 82 | 17.3% | 1/8 | FAIL |
| 12 | `momentum_quality` | 53.0 | p47 | -0.80 | 2.93 | 1.00 | 66 | 15.1% | 1/8 | FAIL |
| 13 | `cmf` | 47.8 | p42 | -1.22 | 1.70 | 0.90 | 75 | 16.9% | 0/8 | FAIL |
| 14 | `acceleration_band` | 45.4 | p38 | -0.84 | 2.10 | 0.97 | 45 | 13.7% | 0/8 | FAIL |
| 15 | `relative_volume` | 41.9 | p33 | -1.46 | 1.74 | 0.86 | 59 | 13.9% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +5.64% | 0.50 | 1.15 | 47 | 1/8 | FAIL |
| `price_cluster` | +2.46% | 0.41 | 1.13 | 45 | 1/8 | FAIL |
| `roc_ma_cross` | +1.05% | -0.10 | 1.15 | 40 | 2/8 | FAIL |
| `positional_scaling` | +0.68% | -0.20 | 1.14 | 36 | 1/8 | FAIL |
| `frama` | -0.04% | -0.00 | 1.05 | 42 | 0/8 | FAIL |
| `narrow_range` | -0.37% | -0.04 | 1.05 | 50 | 0/8 | FAIL |
| `htf_ema` | -1.18% | -0.16 | 1.02 | 45 | 0/8 | FAIL |
| `dema_cross` | -1.35% | -1.70 | 0.39 | 3 | 0/8 | FAIL |
| `volume_breakout` | -1.43% | -0.36 | 1.04 | 78 | 0/8 | FAIL |
| `momentum_quality` | -2.73% | -0.80 | 1.00 | 66 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | -3.60% | -0.54 | 0.98 | 77 | 0/8 | FAIL |
| `price_action_momentum` | -3.66% | -0.80 | 1.02 | 82 | 1/8 | FAIL |
| `acceleration_band` | -4.07% | -0.84 | 0.97 | 45 | 0/8 | FAIL |
| `lob_maker` | -4.22% | -0.55 | 0.98 | 84 | 0/8 | FAIL |
| `wick_reversal` | -4.26% | -1.44 | 0.75 | 23 | 0/8 | FAIL |
| `engulfing_zone` | -5.14% | -1.43 | 0.80 | 25 | 0/8 | FAIL |
| `relative_volume` | -7.44% | -1.46 | 0.86 | 59 | 0/8 | FAIL |
| `cmf` | -7.69% | -1.22 | 0.90 | 75 | 0/8 | FAIL |
| `linear_channel_rev` | -8.50% | -2.82 | 0.63 | 29 | 0/8 | FAIL |
| `volatility_cluster` | -9.23% | -1.98 | 0.82 | 60 | 0/8 | FAIL |
| `elder_impulse` | -9.37% | -1.98 | 0.76 | 47 | 0/8 | FAIL |
| `value_area` | -9.68% | -2.50 | 0.73 | 46 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | mc_p_value 0.052 > 0.05 (우연 가능성) (x1), profit_factor 1.46 < 1.5 (x1), mc_p_value 0.168 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -0.01 < 1.0 (x2), profit_factor 1.01 < 1.5 (x2), sharpe -1.45 < 1.0 (x1) |
| `roc_ma_cross` | sharpe 0.21 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.446 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | mc_p_value 0.122 > 0.05 (우연 가능성) (x1), sharpe -1.18 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1) |
| `frama` | sharpe -0.21 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1), mc_p_value 0.490 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | sharpe 0.76 < 1.0 (x1), profit_factor 1.16 < 1.5 (x1), mc_p_value 0.320 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | profit_factor 1.13 < 1.5 (x2), sharpe -1.74 < 1.0 (x2), sharpe 0.65 < 1.0 (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x4), trades 2 < 15 (x3), trades 3 < 15 (x2) |
| `volume_breakout` | sharpe -0.27 < 1.0 (x1), max_drawdown 20.9% > 20% (x1), profit_factor 0.99 < 1.5 (x1) |
| `momentum_quality` | profit_factor 1.29 < 1.5 (x1), mc_p_value 0.164 > 0.05 (우연 가능성) (x1), sharpe -0.43 < 1.0 (x1) |
| `order_flow_imbalance_v2` | profit_factor 0.94 < 1.5 (x2), sharpe 0.81 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1) |
| `price_action_momentum` | profit_factor 1.28 < 1.5 (x1), mc_p_value 0.172 > 0.05 (우연 가능성) (x1), sharpe -1.89 < 1.0 (x1) |
| `acceleration_band` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.230 > 0.05 (우연 가능성) (x1), sharpe -1.44 < 1.0 (x1) |
| `lob_maker` | profit_factor 0.80 < 1.5 (x2), sharpe -1.80 < 1.0 (x1), max_drawdown 27.2% > 20% (x1) |
| `wick_reversal` | sharpe -1.90 < 1.0 (x1), profit_factor 0.70 < 1.5 (x1), mc_p_value 0.778 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -2.24 < 1.0 (x1), profit_factor 0.66 < 1.5 (x1), mc_p_value 0.850 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | sharpe -2.20 < 1.0 (x1), profit_factor 0.75 < 1.5 (x1), mc_p_value 0.848 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 0.78 < 1.5 (x3), profit_factor 1.19 < 1.5 (x1), mc_p_value 0.254 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe 0.01 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1), mc_p_value 0.466 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -1.06 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.686 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.80 < 1.5 | 6 |
| profit_factor 0.83 < 1.5 | 5 |
| profit_factor 1.01 < 1.5 | 4 |
| mc_p_value 0.998 > 0.05 (우연 가능성) | 4 |
| sharpe -1.44 < 1.0 | 4 |
| profit_factor 0.97 < 1.5 | 4 |
| profit_factor 1.13 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 0.58 < 1.5 | 4 |
| profit_factor 0.78 < 1.5 | 4 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.37% -> $9,663
- **Top 5 균등배분**: +1.96% -> $10,196


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-01T10:34:31.226042Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=321407169, block=24)_
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
| PASS (일관성 50%+) | 5개 |
| FAIL | 17개 |
| 평균 수익률 | 14.59% |
| 최고 수익률 | 62.83% (momentum_quality) |
| 최저 수익률 | -10.39% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +62.83% | 5.56 | 47.4% | 1.86 | 107 | 7.6% | 4/4 | PASS |
| 2 | `supertrend_multi` | +52.08% | 4.78 | 45.2% | 1.71 | 108 | 8.6% | 3/4 | PASS |
| 3 | `price_action_momentum` | +48.08% | 3.80 | 41.0% | 1.45 | 144 | 14.0% | 2/4 | PASS |
| 4 | `lob_maker` | +38.93% | 3.19 | 41.2% | 1.42 | 118 | 12.7% | 2/4 | PASS |
| 5 | `volume_breakout` | +24.69% | 2.68 | 41.4% | 1.40 | 88 | 11.0% | 1/4 | FAIL |
| 6 | `acceleration_band` | +19.95% | 1.94 | 40.1% | 1.33 | 93 | 13.9% | 2/4 | PASS |
| 7 | `order_flow_imbalance_v2` | +19.88% | 2.15 | 40.0% | 1.33 | 84 | 12.3% | 1/4 | FAIL |
| 8 | `cmf` | +16.13% | 1.71 | 37.6% | 1.21 | 111 | 12.6% | 0/4 | FAIL |
| 9 | `volatility_cluster` | +14.23% | 2.04 | 39.3% | 1.33 | 75 | 8.8% | 0/4 | FAIL |
| 10 | `relative_volume` | +9.03% | 1.58 | 39.0% | 1.33 | 51 | 9.4% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 64.9 | p100 | 5.56 | 0.64 | 1.86 | 107 | 7.6% | 4/4 | PASS |
| 2 | `supertrend_multi` | 57.7 | p95 | 4.78 | 1.07 | 1.71 | 108 | 8.6% | 3/4 | PASS |
| 3 | `price_action_momentum` | 52.9 | p90 | 3.80 | 1.54 | 1.45 | 144 | 14.0% | 2/4 | PASS |
| 4 | `lob_maker` | 47.2 | p85 | 3.19 | 1.39 | 1.42 | 118 | 12.7% | 2/4 | PASS |
| 5 | `volume_breakout` | 38.0 | p80 | 2.68 | 1.25 | 1.40 | 88 | 11.0% | 1/4 | FAIL |
| 6 | `cmf` | 37.3 | p76 | 1.71 | 0.61 | 1.21 | 111 | 12.6% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | 34.2 | p71 | 2.15 | 1.38 | 1.33 | 84 | 12.3% | 1/4 | FAIL |
| 8 | `acceleration_band` | 33.5 | p66 | 1.94 | 2.54 | 1.33 | 93 | 13.9% | 2/4 | PASS |
| 9 | `volatility_cluster` | 33.2 | p61 | 2.04 | 0.27 | 1.33 | 75 | 8.8% | 0/4 | FAIL |
| 10 | `narrow_range` | 28.8 | p57 | 0.61 | 0.44 | 1.10 | 95 | 14.9% | 0/4 | FAIL |
| 11 | `relative_volume` | 24.2 | p52 | 1.58 | 1.02 | 1.33 | 51 | 9.4% | 0/4 | FAIL |
| 12 | `roc_ma_cross` | 22.4 | p47 | 1.81 | 0.51 | 1.45 | 32 | 5.6% | 0/4 | FAIL |
| 13 | `htf_ema` | 21.2 | p42 | 0.42 | 1.30 | 1.09 | 64 | 11.5% | 0/4 | FAIL |
| 14 | `wick_reversal` | 20.1 | p38 | 0.47 | 1.69 | 500.00 | 1 | 0.3% | 0/4 | FAIL |
| 15 | `price_cluster` | 20.0 | p33 | 1.47 | 0.95 | 1.40 | 31 | 6.6% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +62.83% | 5.56 | 1.86 | 107 | 4/4 | PASS |
| `supertrend_multi` | +52.08% | 4.78 | 1.71 | 108 | 3/4 | PASS |
| `price_action_momentum` | +48.08% | 3.80 | 1.45 | 144 | 2/4 | PASS |
| `lob_maker` | +38.93% | 3.19 | 1.42 | 118 | 2/4 | PASS |
| `volume_breakout` | +24.69% | 2.68 | 1.40 | 88 | 1/4 | FAIL |
| `acceleration_band` | +19.95% | 1.94 | 1.33 | 93 | 2/4 | PASS |
| `order_flow_imbalance_v2` | +19.88% | 2.15 | 1.33 | 84 | 1/4 | FAIL |
| `cmf` | +16.13% | 1.71 | 1.21 | 111 | 0/4 | FAIL |
| `volatility_cluster` | +14.23% | 2.04 | 1.33 | 75 | 0/4 | FAIL |
| `relative_volume` | +9.03% | 1.58 | 1.33 | 51 | 0/4 | FAIL |
| `roc_ma_cross` | +8.54% | 1.81 | 1.45 | 32 | 0/4 | FAIL |
| `engulfing_zone` | +8.33% | 1.86 | 1.68 | 22 | 0/4 | FAIL |
| `price_cluster` | +7.60% | 1.47 | 1.40 | 31 | 0/4 | FAIL |
| `narrow_range` | +3.77% | 0.61 | 1.10 | 95 | 0/4 | FAIL |
| `linear_channel_rev` | +2.88% | 0.71 | 1.17 | 31 | 0/4 | FAIL |
| `htf_ema` | +2.70% | 0.42 | 1.09 | 64 | 0/4 | FAIL |
| `wick_reversal` | +0.83% | 0.47 | 500.00 | 1 | 0/4 | FAIL |
| `elder_impulse` | -1.05% | -0.12 | 1.02 | 56 | 0/4 | FAIL |
| `dema_cross` | -2.37% | -0.91 | 0.77 | 12 | 0/4 | FAIL |
| `value_area` | -2.70% | -0.76 | 0.89 | 21 | 0/4 | FAIL |
| `positional_scaling` | -3.06% | -0.86 | 0.86 | 23 | 0/4 | FAIL |
| `frama` | -10.39% | -1.65 | 0.89 | 84 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `volume_breakout` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.098 > 0.05 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.27 < 1.5 (x2), sharpe 0.58 < 1.0 (x1), profit_factor 1.09 < 1.5 (x1) |
| `cmf` | profit_factor 1.25 < 1.5 (x2), profit_factor 1.26 < 1.5 (x1), mc_p_value 0.120 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.116 > 0.05 (우연 가능성) (x1), profit_factor 1.30 < 1.5 (x1) |
| `relative_volume` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.110 > 0.05 (우연 가능성) (x1), mc_p_value 0.090 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.242 > 0.05 (우연 가능성) (x1), profit_factor 1.34 < 1.5 (x1) |
| `engulfing_zone` | profit_factor 1.44 < 1.5 (x1), mc_p_value 0.192 > 0.05 (우연 가능성) (x1), sharpe 0.53 < 1.0 (x1) |
| `price_cluster` | mc_p_value 0.114 > 0.05 (우연 가능성) (x1), mc_p_value 0.102 > 0.05 (우연 가능성) (x1), sharpe 0.16 < 1.0 (x1) |
| `narrow_range` | sharpe 0.57 < 1.0 (x1), profit_factor 1.09 < 1.5 (x1), mc_p_value 0.338 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.218 > 0.05 (우연 가능성) (x1), sharpe 0.66 < 1.0 (x1) |
| `htf_ema` | profit_factor 1.28 < 1.5 (x1), mc_p_value 0.142 > 0.05 (우연 가능성) (x1), profit_factor 1.21 < 1.5 (x1) |
| `wick_reversal` | trades 1 < 15 (x3), no trades generated (x1), sharpe -2.11 < 1.0 (x1) |
| `elder_impulse` | sharpe -1.87 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1), mc_p_value 0.818 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | profit_factor 0.82 < 1.5 (x2), trades 10 < 15 (x2), sharpe -0.78 < 1.0 (x1) |
| `value_area` | sharpe 0.67 < 1.0 (x1), profit_factor 1.19 < 1.5 (x1), mc_p_value 0.304 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | sharpe -0.51 < 1.0 (x2), profit_factor 0.92 < 1.5 (x1), mc_p_value 0.606 > 0.05 (우연 가능성) (x1) |
| `frama` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.200 > 0.05 (우연 가능성) (x1), sharpe 0.01 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.25 < 1.5 | 5 |
| profit_factor 1.09 < 1.5 | 4 |
| profit_factor 1.26 < 1.5 | 3 |
| profit_factor 1.35 < 1.5 | 3 |
| trades 1 < 15 | 3 |
| profit_factor 1.12 < 1.5 | 2 |
| sharpe 0.98 < 1.0 | 2 |
| profit_factor 1.27 < 1.5 | 2 |
| mc_p_value 0.366 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.100 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +14.59% -> $11,459
- **PASS 5개 균등배분**: +44.38% -> $14,438
- **Top 5 균등배분**: +45.32% -> $14,532


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-01T10:37:04.402800Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=36994140, block=24)_
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
| PASS (일관성 50%+) | 4개 |
| FAIL | 18개 |
| 평균 수익률 | 13.42% |
| 최고 수익률 | 53.41% (momentum_quality) |
| 최저 수익률 | -3.51% (price_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +53.41% | 4.89 | 45.1% | 1.70 | 112 | 9.6% | 4/4 | PASS |
| 2 | `acceleration_band` | +48.80% | 4.22 | 43.9% | 1.67 | 103 | 8.3% | 2/4 | PASS |
| 3 | `price_action_momentum` | +36.91% | 3.15 | 40.2% | 1.36 | 141 | 13.9% | 1/4 | FAIL |
| 4 | `supertrend_multi` | +22.86% | 2.79 | 40.6% | 1.45 | 78 | 10.3% | 1/4 | FAIL |
| 5 | `narrow_range` | +21.57% | 2.63 | 40.7% | 1.40 | 88 | 13.6% | 0/4 | FAIL |
| 6 | `cmf` | +21.41% | 2.09 | 39.2% | 1.29 | 104 | 14.2% | 0/4 | FAIL |
| 7 | `lob_maker` | +16.16% | 1.61 | 37.8% | 1.21 | 108 | 13.9% | 0/4 | FAIL |
| 8 | `volatility_cluster` | +13.11% | 1.48 | 39.6% | 1.34 | 71 | 12.2% | 2/4 | PASS |
| 9 | `htf_ema` | +12.89% | 1.32 | 37.5% | 1.33 | 68 | 11.7% | 2/4 | PASS |
| 10 | `relative_volume` | +12.49% | 2.03 | 40.3% | 1.39 | 55 | 9.0% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 83.4 | p100 | 4.89 | 0.56 | 1.70 | 112 | 9.6% | 4/4 | PASS |
| 2 | `acceleration_band` | 70.0 | p95 | 4.22 | 1.99 | 1.67 | 103 | 8.3% | 2/4 | PASS |
| 3 | `price_action_momentum` | 62.1 | p90 | 3.15 | 1.27 | 1.36 | 141 | 13.9% | 1/4 | FAIL |
| 4 | `supertrend_multi` | 53.3 | p85 | 2.79 | 1.10 | 1.45 | 78 | 10.3% | 1/4 | FAIL |
| 5 | `narrow_range` | 51.3 | p80 | 2.63 | 0.21 | 1.40 | 88 | 13.6% | 0/4 | FAIL |
| 6 | `cmf` | 47.5 | p76 | 2.09 | 1.07 | 1.29 | 104 | 14.2% | 0/4 | FAIL |
| 7 | `lob_maker` | 44.7 | p71 | 1.61 | 1.13 | 1.21 | 108 | 13.9% | 0/4 | FAIL |
| 8 | `roc_ma_cross` | 44.4 | p66 | 2.07 | 1.69 | 1.65 | 38 | 7.1% | 1/4 | FAIL |
| 9 | `relative_volume` | 42.6 | p61 | 2.03 | 0.71 | 1.39 | 55 | 9.0% | 0/4 | FAIL |
| 10 | `volatility_cluster` | 42.0 | p57 | 1.48 | 2.87 | 1.34 | 71 | 12.2% | 2/4 | PASS |
| 11 | `htf_ema` | 40.7 | p52 | 1.32 | 2.95 | 1.33 | 68 | 11.7% | 2/4 | PASS |
| 12 | `order_flow_imbalance_v2` | 36.4 | p47 | 0.87 | 1.80 | 1.15 | 86 | 15.5% | 1/4 | FAIL |
| 13 | `elder_impulse` | 34.4 | p42 | 1.10 | 0.73 | 1.22 | 53 | 11.4% | 0/4 | FAIL |
| 14 | `volume_breakout` | 34.1 | p38 | 0.77 | 1.64 | 1.15 | 85 | 14.6% | 0/4 | FAIL |
| 15 | `frama` | 33.0 | p33 | 0.25 | 0.95 | 1.05 | 88 | 13.3% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +53.41% | 4.89 | 1.70 | 112 | 4/4 | PASS |
| `acceleration_band` | +48.80% | 4.22 | 1.67 | 103 | 2/4 | PASS |
| `price_action_momentum` | +36.91% | 3.15 | 1.36 | 141 | 1/4 | FAIL |
| `supertrend_multi` | +22.86% | 2.79 | 1.45 | 78 | 1/4 | FAIL |
| `narrow_range` | +21.57% | 2.63 | 1.40 | 88 | 0/4 | FAIL |
| `cmf` | +21.41% | 2.09 | 1.29 | 104 | 0/4 | FAIL |
| `lob_maker` | +16.16% | 1.61 | 1.21 | 108 | 0/4 | FAIL |
| `volatility_cluster` | +13.11% | 1.48 | 1.34 | 71 | 2/4 | PASS |
| `htf_ema` | +12.89% | 1.32 | 1.33 | 68 | 2/4 | PASS |
| `relative_volume` | +12.49% | 2.03 | 1.39 | 55 | 0/4 | FAIL |
| `roc_ma_cross` | +10.73% | 2.07 | 1.65 | 38 | 1/4 | FAIL |
| `order_flow_imbalance_v2` | +8.67% | 0.87 | 1.15 | 86 | 1/4 | FAIL |
| `volume_breakout` | +6.54% | 0.77 | 1.15 | 85 | 0/4 | FAIL |
| `elder_impulse` | +6.35% | 1.10 | 1.22 | 53 | 0/4 | FAIL |
| `positional_scaling` | +5.15% | 1.21 | 1.33 | 24 | 0/4 | FAIL |
| `value_area` | +2.22% | 0.63 | 1.18 | 28 | 0/4 | FAIL |
| `frama` | +1.56% | 0.25 | 1.05 | 88 | 0/4 | FAIL |
| `dema_cross` | +1.51% | 0.31 | 1.47 | 14 | 0/4 | FAIL |
| `wick_reversal` | -0.34% | -0.53 | 0.00 | 0 | 0/4 | FAIL |
| `linear_channel_rev` | -0.57% | -0.02 | 1.03 | 36 | 0/4 | FAIL |
| `engulfing_zone` | -2.64% | -0.74 | 0.90 | 19 | 0/4 | FAIL |
| `price_cluster` | -3.51% | -0.62 | 0.92 | 34 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | profit_factor 1.45 < 1.5 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.238 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | profit_factor 1.47 < 1.5 (x1), profit_factor 1.33 < 1.5 (x1), mc_p_value 0.154 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.41 < 1.5 (x2), mc_p_value 0.082 > 0.05 (우연 가능성) (x1), mc_p_value 0.062 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.42 < 1.5 (x1), profit_factor 1.43 < 1.5 (x1), mc_p_value 0.052 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 1.42 < 1.5 (x1), sharpe 0.21 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1) |
| `relative_volume` | mc_p_value 0.076 > 0.05 (우연 가능성) (x1), profit_factor 1.40 < 1.5 (x1), mc_p_value 0.100 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | mc_p_value 0.058 > 0.05 (우연 가능성) (x1), sharpe 0.15 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe 0.73 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1), mc_p_value 0.304 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 1.49 < 1.5 (x1), sharpe -0.63 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1) |
| `elder_impulse` | profit_factor 1.38 < 1.5 (x1), mc_p_value 0.164 > 0.05 (우연 가능성) (x1), sharpe -0.03 < 1.0 (x1) |
| `positional_scaling` | sharpe 0.71 < 1.0 (x1), profit_factor 1.22 < 1.5 (x1), mc_p_value 0.340 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe 0.72 < 1.0 (x1), profit_factor 1.20 < 1.5 (x1), mc_p_value 0.318 > 0.05 (우연 가능성) (x1) |
| `frama` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.184 > 0.05 (우연 가능성) (x1), sharpe -0.46 < 1.0 (x1) |
| `dema_cross` | sharpe -0.43 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.566 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x3), sharpe -2.11 < 1.0 (x1), profit_factor 0.00 < 1.5 (x1) |
| `linear_channel_rev` | sharpe 0.28 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1), mc_p_value 0.412 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -1.34 < 1.0 (x1), profit_factor 0.72 < 1.5 (x1), mc_p_value 0.732 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -0.84 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1), mc_p_value 0.658 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 3 |
| profit_factor 1.22 < 1.5 | 2 |
| mc_p_value 0.184 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.38 < 1.5 | 2 |
| mc_p_value 0.238 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.41 < 1.5 | 2 |
| profit_factor 1.35 < 1.5 | 2 |
| profit_factor 1.44 < 1.5 | 2 |
| profit_factor 1.42 < 1.5 | 2 |
| profit_factor 1.15 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +13.42% -> $11,342
- **PASS 4개 균등배분**: +32.05% -> $13,205
- **Top 5 균등배분**: +36.71% -> $13,671
