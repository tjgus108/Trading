# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-15T00:17:01.501711Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-15T00:27:05.270337Z_
_Symbol: BTC/USDT_
_Data Source: CSV fallback BTC/USDT 1h (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 23:00:00+00:00 (499일)_
_Walk-Forward: 12개 윈도우 (train=2016, test=1440 candles [1h])_
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
| 평균 수익률 | -4.44% |
| 최고 수익률 | 3.23% (supertrend_multi) |
| 최저 수익률 | -13.98% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +3.23% | 0.13 | 37.5% | 1.12 | 51 | 10.4% | 3/12 | FAIL |
| 2 | `price_cluster` | +1.99% | 0.19 | 38.7% | 1.10 | 46 | 12.9% | 1/12 | FAIL |
| 3 | `positional_scaling` | -0.02% | -0.22 | 36.8% | 1.11 | 37 | 9.6% | 2/12 | FAIL |
| 4 | `roc_ma_cross` | -0.30% | -0.32 | 37.5% | 1.05 | 40 | 9.4% | 2/12 | FAIL |
| 5 | `dema_cross` | -0.71% | -0.93 | 29.7% | 166.92 | 2 | 1.5% | 0/12 | FAIL |
| 6 | `narrow_range` | -2.83% | -0.56 | 37.0% | 0.98 | 50 | 12.4% | 1/12 | FAIL |
| 7 | `htf_ema` | -2.85% | -0.51 | 37.0% | 0.97 | 47 | 11.5% | 1/12 | FAIL |
| 8 | `acceleration_band` | -3.35% | -0.70 | 33.4% | 0.98 | 45 | 11.4% | 0/12 | FAIL |
| 9 | `frama` | -3.60% | -0.80 | 37.1% | 0.92 | 41 | 10.7% | 0/12 | FAIL |
| 10 | `momentum_quality` | -4.21% | -1.05 | 34.5% | 0.96 | 77 | 16.3% | 1/12 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 54.0 | p100 | 0.13 | 2.64 | 1.12 | 51 | 10.4% | 3/12 | FAIL |
| 2 | `price_cluster` | 47.7 | p95 | 0.19 | 1.91 | 1.10 | 46 | 12.9% | 1/12 | FAIL |
| 3 | `roc_ma_cross` | 45.6 | p90 | -0.32 | 2.28 | 1.05 | 40 | 9.4% | 2/12 | FAIL |
| 4 | `positional_scaling` | 44.9 | p85 | -0.22 | 2.35 | 1.11 | 37 | 9.6% | 2/12 | FAIL |
| 5 | `htf_ema` | 44.7 | p80 | -0.51 | 1.47 | 0.97 | 47 | 11.5% | 1/12 | FAIL |
| 6 | `relative_volume` | 44.5 | p76 | -1.17 | 1.28 | 0.89 | 73 | 14.4% | 0/12 | FAIL |
| 7 | `narrow_range` | 43.9 | p71 | -0.56 | 1.75 | 0.98 | 50 | 12.4% | 1/12 | FAIL |
| 8 | `lob_maker` | 43.2 | p66 | -0.88 | 1.84 | 0.94 | 84 | 19.2% | 0/12 | FAIL |
| 9 | `volume_breakout` | 41.9 | p61 | -1.14 | 1.87 | 0.92 | 80 | 16.8% | 0/12 | FAIL |
| 10 | `dema_cross` | 41.8 | p57 | -0.93 | 1.68 | 166.92 | 2 | 1.5% | 0/12 | FAIL |
| 11 | `price_action_momentum` | 41.5 | p52 | -0.82 | 2.42 | 0.97 | 83 | 17.2% | 0/12 | FAIL |
| 12 | `cmf` | 40.5 | p47 | -1.30 | 1.45 | 0.88 | 72 | 16.7% | 0/12 | FAIL |
| 13 | `order_flow_imbalance_v2` | 40.4 | p42 | -0.95 | 2.02 | 0.94 | 70 | 15.8% | 0/12 | FAIL |
| 14 | `momentum_quality` | 39.6 | p38 | -1.05 | 2.90 | 0.96 | 77 | 16.3% | 1/12 | FAIL |
| 15 | `acceleration_band` | 37.4 | p28 | -0.70 | 1.99 | 0.98 | 45 | 11.4% | 0/12 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +3.23% | 0.13 | 1.12 | 51 | 3/12 | FAIL |
| `price_cluster` | +1.99% | 0.19 | 1.10 | 46 | 1/12 | FAIL |
| `positional_scaling` | -0.02% | -0.22 | 1.11 | 37 | 2/12 | FAIL |
| `roc_ma_cross` | -0.30% | -0.32 | 1.05 | 40 | 2/12 | FAIL |
| `dema_cross` | -0.71% | -0.93 | 166.92 | 2 | 0/12 | FAIL |
| `narrow_range` | -2.83% | -0.56 | 0.98 | 50 | 1/12 | FAIL |
| `htf_ema` | -2.85% | -0.51 | 0.97 | 47 | 1/12 | FAIL |
| `acceleration_band` | -3.35% | -0.70 | 0.98 | 45 | 0/12 | FAIL |
| `frama` | -3.60% | -0.80 | 0.92 | 41 | 0/12 | FAIL |
| `momentum_quality` | -4.21% | -1.05 | 0.96 | 77 | 1/12 | FAIL |
| `linear_channel_rev` | -4.64% | -1.75 | 0.79 | 28 | 0/12 | FAIL |
| `price_action_momentum` | -4.66% | -0.82 | 0.97 | 83 | 0/12 | FAIL |
| `engulfing_zone` | -5.13% | -1.26 | 0.82 | 27 | 0/12 | FAIL |
| `order_flow_imbalance_v2` | -5.53% | -0.95 | 0.94 | 70 | 0/12 | FAIL |
| `volatility_cluster` | -5.88% | -1.40 | 0.89 | 60 | 1/12 | FAIL |
| `relative_volume` | -6.63% | -1.17 | 0.89 | 73 | 0/12 | FAIL |
| `value_area` | -6.93% | -1.63 | 0.83 | 55 | 0/12 | FAIL |
| `volume_breakout` | -6.99% | -1.14 | 0.92 | 80 | 0/12 | FAIL |
| `lob_maker` | -7.19% | -0.88 | 0.94 | 84 | 0/12 | FAIL |
| `cmf` | -8.55% | -1.30 | 0.88 | 72 | 0/12 | FAIL |
| `elder_impulse` | -9.04% | -1.89 | 0.78 | 50 | 0/12 | FAIL |
| `wick_reversal` | -13.98% | -3.64 | 0.58 | 44 | 0/12 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | sharpe -0.33 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1), mc_p_value 0.536 > 0.1 (우연 가능성) (x1) |
| `price_cluster` | profit_factor 1.35 < 1.5 (x2), profit_factor 1.46 < 1.5 (x1), mc_p_value 0.131 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 1.05 < 1.5 (x2), sharpe 0.14 < 1.0 (x1), mc_p_value 0.449 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe 0.89 < 1.0 (x1), profit_factor 1.17 < 1.5 (x1), mc_p_value 0.320 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | trades 1 < 15 (x5), profit_factor 0.00 < 1.5 (x5), sharpe -2.05 < 1.0 (x3) |
| `narrow_range` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.171 > 0.1 (우연 가능성) (x1), sharpe -0.07 < 1.0 (x1) |
| `htf_ema` | profit_factor 0.90 < 1.5 (x2), sharpe 0.47 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1) |
| `acceleration_band` | profit_factor 0.56 < 1.5 (x2), sharpe -2.38 < 1.0 (x1), profit_factor 0.70 < 1.5 (x1) |
| `frama` | profit_factor 0.75 < 1.5 (x2), sharpe -2.40 < 1.0 (x1), profit_factor 0.68 < 1.5 (x1) |
| `momentum_quality` | sharpe -1.26 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1), mc_p_value 0.701 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -0.79 < 1.0 (x1), profit_factor 0.86 < 1.5 (x1), mc_p_value 0.622 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe -1.09 < 1.0 (x1), profit_factor 0.90 < 1.5 (x1), mc_p_value 0.675 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | profit_factor 0.66 < 1.5 (x2), sharpe -1.29 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe -1.38 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.727 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -0.57 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1), mc_p_value 0.575 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | profit_factor 0.90 < 1.5 (x2), sharpe -0.76 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1) |
| `value_area` | sharpe 0.20 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1), mc_p_value 0.416 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -3.82 < 1.0 (x1), max_drawdown 25.9% > 20% (x1), profit_factor 0.66 < 1.5 (x1) |
| `lob_maker` | sharpe -1.19 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.701 > 0.1 (우연 가능성) (x1) |
| `cmf` | sharpe -2.09 < 1.0 (x1), profit_factor 0.76 < 1.5 (x1), mc_p_value 0.839 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.83 < 1.5 | 9 |
| profit_factor 0.90 < 1.5 | 7 |
| profit_factor 0.70 < 1.5 | 7 |
| profit_factor 1.12 < 1.5 | 6 |
| profit_factor 1.05 < 1.5 | 6 |
| profit_factor 0.93 < 1.5 | 5 |
| profit_factor 0.66 < 1.5 | 5 |
| mc_p_value 0.964 > 0.1 (우연 가능성) | 5 |
| profit_factor 0.75 < 1.5 | 5 |
| trades 1 < 15 | 5 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 4 | 22 | 84.6% |
| `frama` | 0 | 410 | 84 | 17.0% |
| `price_action_momentum` | 0 | 852 | 145 | 14.5% |
| `cmf` | 0 | 744 | 115 | 13.4% |
| `htf_ema` | 0 | 490 | 74 | 13.1% |
| `positional_scaling` | 0 | 382 | 57 | 13.0% |
| `lob_maker` | 0 | 878 | 130 | 12.9% |
| `relative_volume` | 0 | 761 | 111 | 12.7% |
| `volume_breakout` | 0 | 841 | 121 | 12.6% |
| `linear_channel_rev` | 0 | 299 | 43 | 12.6% |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -4.44% -> $9,556
- **Top 5 균등배분**: +0.84% -> $10,084


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-15T00:36:46.550689Z_
_Symbol: ETH/USDT_
_Data Source: CSV fallback ETH/USDT 1h (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 23:00:00+00:00 (499일)_
_Walk-Forward: 12개 윈도우 (train=2016, test=1440 candles [1h])_
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
| 평균 수익률 | -4.99% |
| 최고 수익률 | 1.80% (narrow_range) |
| 최저 수익률 | -16.11% (supertrend_multi) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `narrow_range` | +1.80% | 0.43 | 43.5% | 1.13 | 50 | 9.7% | 1/12 | FAIL |
| 2 | `price_action_momentum` | +1.57% | 0.29 | 44.2% | 1.12 | 50 | 9.6% | 1/12 | FAIL |
| 3 | `cmf` | +1.35% | 0.03 | 40.4% | 1.14 | 53 | 12.4% | 2/12 | FAIL |
| 4 | `dema_cross` | +0.97% | 0.20 | 49.2% | 1.78 | 12 | 3.3% | 0/12 | FAIL |
| 5 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/12 | FAIL |
| 6 | `momentum_quality` | -0.16% | -0.11 | 39.9% | 1.02 | 73 | 11.6% | 0/12 | FAIL |
| 7 | `volatility_cluster` | -0.76% | -0.13 | 40.8% | 1.02 | 52 | 8.6% | 0/12 | FAIL |
| 8 | `acceleration_band` | -1.51% | -0.85 | 39.3% | 1.31 | 10 | 4.5% | 0/12 | FAIL |
| 9 | `htf_ema` | -3.64% | -1.09 | 37.9% | 0.84 | 32 | 8.7% | 0/12 | FAIL |
| 10 | `roc_ma_cross` | -3.70% | -1.07 | 39.0% | 0.83 | 31 | 8.8% | 0/12 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `narrow_range` | 66.1 | p100 | 0.43 | 1.40 | 1.13 | 50 | 9.7% | 1/12 | FAIL |
| 2 | `cmf` | 64.8 | p95 | 0.03 | 2.82 | 1.14 | 53 | 12.4% | 2/12 | FAIL |
| 3 | `price_action_momentum` | 64.0 | p90 | 0.29 | 1.82 | 1.12 | 50 | 9.6% | 1/12 | FAIL |
| 4 | `momentum_quality` | 62.3 | p85 | -0.11 | 1.69 | 1.02 | 73 | 11.6% | 0/12 | FAIL |
| 5 | `volatility_cluster` | 58.0 | p80 | -0.13 | 1.14 | 1.02 | 52 | 8.6% | 0/12 | FAIL |
| 6 | `dema_cross` | 52.9 | p76 | 0.20 | 2.71 | 1.78 | 12 | 3.3% | 0/12 | FAIL |
| 7 | `relative_volume` | 48.6 | p71 | -1.45 | 1.46 | 0.85 | 66 | 13.0% | 0/12 | FAIL |
| 8 | `lob_maker` | 46.6 | p66 | -1.30 | 1.38 | 0.86 | 68 | 18.8% | 0/12 | FAIL |
| 9 | `volume_breakout` | 45.6 | p61 | -1.52 | 1.92 | 0.85 | 76 | 18.7% | 0/12 | FAIL |
| 10 | `roc_ma_cross` | 41.2 | p57 | -1.07 | 1.02 | 0.83 | 31 | 8.8% | 0/12 | FAIL |
| 11 | `htf_ema` | 40.9 | p52 | -1.09 | 1.52 | 0.84 | 32 | 8.7% | 0/12 | FAIL |
| 12 | `order_flow_imbalance_v2` | 40.1 | p47 | -2.00 | 1.97 | 0.79 | 70 | 18.5% | 0/12 | FAIL |
| 13 | `acceleration_band` | 39.7 | p42 | -0.85 | 2.54 | 1.31 | 10 | 4.5% | 0/12 | FAIL |
| 14 | `value_area` | 38.4 | p38 | -1.95 | 1.58 | 0.76 | 48 | 12.6% | 0/12 | FAIL |
| 15 | `engulfing_zone` | 37.5 | p33 | -1.71 | 2.97 | 0.85 | 25 | 9.5% | 1/12 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `narrow_range` | +1.80% | 0.43 | 1.13 | 50 | 1/12 | FAIL |
| `price_action_momentum` | +1.57% | 0.29 | 1.12 | 50 | 1/12 | FAIL |
| `cmf` | +1.35% | 0.03 | 1.14 | 53 | 2/12 | FAIL |
| `dema_cross` | +0.97% | 0.20 | 1.78 | 12 | 0/12 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/12 | FAIL |
| `momentum_quality` | -0.16% | -0.11 | 1.02 | 73 | 0/12 | FAIL |
| `volatility_cluster` | -0.76% | -0.13 | 1.02 | 52 | 0/12 | FAIL |
| `acceleration_band` | -1.51% | -0.85 | 1.31 | 10 | 0/12 | FAIL |
| `htf_ema` | -3.64% | -1.09 | 0.84 | 32 | 0/12 | FAIL |
| `roc_ma_cross` | -3.70% | -1.07 | 0.83 | 31 | 0/12 | FAIL |
| `engulfing_zone` | -3.90% | -1.71 | 0.85 | 25 | 1/12 | FAIL |
| `linear_channel_rev` | -5.01% | -1.74 | 0.72 | 27 | 0/12 | FAIL |
| `relative_volume` | -7.11% | -1.45 | 0.85 | 66 | 0/12 | FAIL |
| `value_area` | -7.44% | -1.95 | 0.76 | 48 | 0/12 | FAIL |
| `elder_impulse` | -8.06% | -1.96 | 0.74 | 43 | 0/12 | FAIL |
| `volume_breakout` | -8.30% | -1.52 | 0.85 | 76 | 0/12 | FAIL |
| `lob_maker` | -8.53% | -1.30 | 0.86 | 68 | 0/12 | FAIL |
| `positional_scaling` | -9.27% | -2.73 | 0.62 | 36 | 0/12 | FAIL |
| `price_cluster` | -10.25% | -3.00 | 0.56 | 30 | 0/12 | FAIL |
| `frama` | -10.48% | -2.57 | 0.69 | 44 | 0/12 | FAIL |
| `order_flow_imbalance_v2` | -11.24% | -2.00 | 0.79 | 70 | 0/12 | FAIL |
| `supertrend_multi` | -16.11% | -4.03 | 0.55 | 56 | 0/12 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `narrow_range` | profit_factor 1.10 < 1.5 (x2), mc_p_value 0.137 > 0.1 (우연 가능성) (x1), sharpe 0.33 < 1.0 (x1) |
| `price_action_momentum` | sharpe -0.95 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.650 > 0.1 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.31 < 1.5 (x2), profit_factor 1.21 < 1.5 (x1), mc_p_value 0.266 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | trades 12 < 15 (x3), trades 7 < 15 (x2), trades 11 < 15 (x2) |
| `wick_reversal` | no trades generated (x12) |
| `momentum_quality` | sharpe -1.49 < 1.0 (x1), profit_factor 0.84 < 1.5 (x1), mc_p_value 0.756 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.14 < 1.5 (x2), sharpe -0.80 < 1.0 (x1), profit_factor 0.90 < 1.5 (x1) |
| `acceleration_band` | trades 8 < 15 (x3), trades 7 < 15 (x2), trades 6 < 15 (x1) |
| `htf_ema` | profit_factor 0.74 < 1.5 (x2), sharpe -0.56 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1) |
| `roc_ma_cross` | sharpe -2.36 < 1.0 (x1), profit_factor 0.63 < 1.5 (x1), mc_p_value 0.864 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -1.00 < 1.0 (x1), profit_factor 0.78 < 1.5 (x1), mc_p_value 0.687 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | profit_factor 0.97 < 1.5 (x2), sharpe -0.23 < 1.0 (x2), sharpe -4.60 < 1.0 (x1) |
| `relative_volume` | profit_factor 0.81 < 1.5 (x2), sharpe -1.61 < 1.0 (x1), mc_p_value 0.780 > 0.1 (우연 가능성) (x1) |
| `value_area` | mc_p_value 0.784 > 0.1 (우연 가능성) (x2), sharpe -1.78 < 1.0 (x2), profit_factor 0.76 < 1.5 (x2) |
| `elder_impulse` | profit_factor 0.59 < 1.5 (x2), mc_p_value 0.919 > 0.1 (우연 가능성) (x2), sharpe -3.01 < 1.0 (x1) |
| `volume_breakout` | sharpe -2.73 < 1.0 (x1), profit_factor 0.70 < 1.5 (x1), mc_p_value 0.934 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | sharpe -0.99 < 1.0 (x2), profit_factor 0.87 < 1.5 (x1), mc_p_value 0.688 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | sharpe -2.07 < 1.0 (x1), profit_factor 0.68 < 1.5 (x1), mc_p_value 0.823 > 0.1 (우연 가능성) (x1) |
| `price_cluster` | profit_factor 0.55 < 1.5 (x2), profit_factor 0.72 < 1.5 (x2), sharpe -2.71 < 1.0 (x1) |
| `frama` | sharpe 0.90 < 1.0 (x1), profit_factor 1.18 < 1.5 (x1), mc_p_value 0.329 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 12 |
| profit_factor 0.71 < 1.5 | 6 |
| profit_factor 0.78 < 1.5 | 6 |
| profit_factor 0.55 < 1.5 | 6 |
| profit_factor 0.94 < 1.5 | 5 |
| profit_factor 0.65 < 1.5 | 5 |
| profit_factor 0.63 < 1.5 | 5 |
| profit_factor 0.80 < 1.5 | 5 |
| profit_factor 1.07 < 1.5 | 4 |
| profit_factor 0.88 < 1.5 | 4 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 0 | 143 | 100.0% |
| `frama` | 0 | 122 | 408 | 77.0% |
| `elder_impulse` | 0 | 197 | 321 | 62.0% |
| `roc_ma_cross` | 0 | 142 | 226 | 61.4% |
| `value_area` | 0 | 228 | 353 | 60.8% |
| `relative_volume` | 0 | 320 | 473 | 59.6% |
| `cmf` | 0 | 264 | 372 | 58.5% |
| `supertrend_multi` | 0 | 280 | 391 | 58.3% |
| `volume_breakout` | 0 | 382 | 530 | 58.1% |
| `engulfing_zone` | 0 | 125 | 172 | 57.9% |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -4.99% -> $9,501
- **Top 5 균등배분**: +1.14% -> $10,114


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-15T00:46:21.487100Z_
_Symbol: SOL/USDT_
_Data Source: CSV fallback SOL/USDT 1h (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 23:00:00+00:00 (499일)_
_Walk-Forward: 12개 윈도우 (train=2016, test=1440 candles [1h])_
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
| 평균 수익률 | -3.65% |
| 최고 수익률 | 3.06% (htf_ema) |
| 최저 수익률 | -10.62% (positional_scaling) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `htf_ema` | +3.06% | 0.66 | 42.5% | 1.19 | 34 | 7.8% | 1/12 | FAIL |
| 2 | `momentum_quality` | +1.98% | 0.17 | 40.5% | 1.06 | 76 | 12.0% | 1/12 | FAIL |
| 3 | `order_flow_imbalance_v2` | +0.85% | -0.00 | 39.1% | 1.02 | 70 | 13.1% | 0/12 | FAIL |
| 4 | `price_action_momentum` | +0.45% | -0.27 | 41.0% | 1.08 | 48 | 9.4% | 1/12 | FAIL |
| 5 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/12 | FAIL |
| 6 | `acceleration_band` | -0.42% | -0.72 | 25.3% | 1.19 | 5 | 2.8% | 0/12 | FAIL |
| 7 | `elder_impulse` | -1.02% | -0.43 | 39.1% | 0.95 | 45 | 10.0% | 0/12 | FAIL |
| 8 | `cmf` | -1.21% | -0.53 | 38.4% | 1.00 | 53 | 12.5% | 2/12 | FAIL |
| 9 | `roc_ma_cross` | -1.44% | -0.61 | 40.3% | 0.96 | 31 | 7.8% | 0/12 | FAIL |
| 10 | `volatility_cluster` | -1.81% | -0.44 | 40.3% | 0.97 | 52 | 9.6% | 0/12 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 71.0 | p100 | 0.17 | 2.10 | 1.06 | 76 | 12.0% | 1/12 | FAIL |
| 2 | `htf_ema` | 67.6 | p95 | 0.66 | 1.32 | 1.19 | 34 | 7.8% | 1/12 | FAIL |
| 3 | `order_flow_imbalance_v2` | 62.2 | p90 | -0.00 | 1.77 | 1.02 | 70 | 13.1% | 0/12 | FAIL |
| 4 | `cmf` | 61.3 | p85 | -0.53 | 2.47 | 1.00 | 53 | 12.5% | 2/12 | FAIL |
| 5 | `price_action_momentum` | 59.7 | p80 | -0.27 | 2.74 | 1.08 | 48 | 9.4% | 1/12 | FAIL |
| 6 | `volatility_cluster` | 54.9 | p76 | -0.44 | 1.66 | 0.97 | 52 | 9.6% | 0/12 | FAIL |
| 7 | `elder_impulse` | 52.2 | p71 | -0.43 | 1.66 | 0.95 | 45 | 10.0% | 0/12 | FAIL |
| 8 | `volume_breakout` | 52.0 | p66 | -0.88 | 2.66 | 0.95 | 58 | 14.9% | 1/12 | FAIL |
| 9 | `narrow_range` | 49.9 | p61 | -0.73 | 2.11 | 0.93 | 49 | 9.9% | 0/12 | FAIL |
| 10 | `roc_ma_cross` | 46.6 | p57 | -0.61 | 1.94 | 0.96 | 31 | 7.8% | 0/12 | FAIL |
| 11 | `relative_volume` | 45.6 | p52 | -1.53 | 1.92 | 0.84 | 70 | 14.5% | 0/12 | FAIL |
| 12 | `dema_cross` | 43.3 | p47 | -0.71 | 1.35 | 0.89 | 24 | 6.2% | 0/12 | FAIL |
| 13 | `acceleration_band` | 41.0 | p42 | -0.72 | 2.07 | 1.19 | 5 | 2.8% | 0/12 | FAIL |
| 14 | `lob_maker` | 40.7 | p38 | -1.61 | 2.14 | 0.83 | 66 | 17.4% | 0/12 | FAIL |
| 15 | `frama` | 37.3 | p33 | -1.95 | 1.81 | 0.76 | 59 | 15.9% | 0/12 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `htf_ema` | +3.06% | 0.66 | 1.19 | 34 | 1/12 | FAIL |
| `momentum_quality` | +1.98% | 0.17 | 1.06 | 76 | 1/12 | FAIL |
| `order_flow_imbalance_v2` | +0.85% | -0.00 | 1.02 | 70 | 0/12 | FAIL |
| `price_action_momentum` | +0.45% | -0.27 | 1.08 | 48 | 1/12 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/12 | FAIL |
| `acceleration_band` | -0.42% | -0.72 | 1.19 | 5 | 0/12 | FAIL |
| `elder_impulse` | -1.02% | -0.43 | 0.95 | 45 | 0/12 | FAIL |
| `cmf` | -1.21% | -0.53 | 1.00 | 53 | 2/12 | FAIL |
| `roc_ma_cross` | -1.44% | -0.61 | 0.96 | 31 | 0/12 | FAIL |
| `volatility_cluster` | -1.81% | -0.44 | 0.97 | 52 | 0/12 | FAIL |
| `dema_cross` | -1.87% | -0.71 | 0.89 | 24 | 0/12 | FAIL |
| `narrow_range` | -2.42% | -0.73 | 0.93 | 49 | 0/12 | FAIL |
| `volume_breakout` | -2.71% | -0.88 | 0.95 | 58 | 1/12 | FAIL |
| `price_cluster` | -4.96% | -1.43 | 0.76 | 25 | 0/12 | FAIL |
| `linear_channel_rev` | -5.41% | -1.96 | 0.66 | 26 | 0/12 | FAIL |
| `relative_volume` | -7.16% | -1.53 | 0.84 | 70 | 0/12 | FAIL |
| `engulfing_zone` | -8.79% | -3.12 | 0.53 | 25 | 0/12 | FAIL |
| `value_area` | -8.87% | -2.53 | 0.68 | 50 | 0/12 | FAIL |
| `lob_maker` | -9.04% | -1.61 | 0.83 | 66 | 0/12 | FAIL |
| `supertrend_multi` | -9.18% | -2.40 | 0.69 | 50 | 0/12 | FAIL |
| `frama` | -9.78% | -1.95 | 0.76 | 59 | 0/12 | FAIL |
| `positional_scaling` | -10.62% | -3.06 | 0.59 | 40 | 0/12 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `htf_ema` | sharpe 0.25 < 1.0 (x2), profit_factor 1.05 < 1.5 (x2), profit_factor 0.90 < 1.5 (x2) |
| `momentum_quality` | profit_factor 1.12 < 1.5 (x2), sharpe -0.82 < 1.0 (x2), profit_factor 0.89 < 1.5 (x2) |
| `order_flow_imbalance_v2` | profit_factor 1.25 < 1.5 (x2), profit_factor 1.27 < 1.5 (x1), mc_p_value 0.212 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe 0.25 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1), mc_p_value 0.455 > 0.1 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x12) |
| `acceleration_band` | trades 7 < 15 (x6), profit_factor 0.00 < 1.5 (x3), sharpe -2.18 < 1.0 (x2) |
| `elder_impulse` | sharpe -2.51 < 1.0 (x1), profit_factor 0.63 < 1.5 (x1), mc_p_value 0.876 > 0.1 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.185 > 0.1 (우연 가능성) (x1), sharpe -0.27 < 1.0 (x1) |
| `roc_ma_cross` | profit_factor 0.69 < 1.5 (x2), sharpe -2.35 < 1.0 (x1), profit_factor 0.61 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 0.89 < 1.5 (x2), sharpe -0.54 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1) |
| `dema_cross` | profit_factor 1.47 < 1.5 (x1), mc_p_value 0.257 > 0.1 (우연 가능성) (x1), mc_p_value 0.228 > 0.1 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.240 > 0.1 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1) |
| `volume_breakout` | sharpe 0.84 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.335 > 0.1 (우연 가능성) (x1) |
| `price_cluster` | profit_factor 0.46 < 1.5 (x2), sharpe 0.78 < 1.0 (x1), profit_factor 1.20 < 1.5 (x1) |
| `linear_channel_rev` | sharpe -1.93 < 1.0 (x1), profit_factor 0.66 < 1.5 (x1), mc_p_value 0.830 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | sharpe 0.24 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1), mc_p_value 0.427 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | profit_factor 0.24 < 1.5 (x3), sharpe -2.46 < 1.0 (x1), profit_factor 0.52 < 1.5 (x1) |
| `value_area` | profit_factor 0.71 < 1.5 (x2), sharpe -2.69 < 1.0 (x1), profit_factor 0.64 < 1.5 (x1) |
| `lob_maker` | profit_factor 1.29 < 1.5 (x1), mc_p_value 0.218 > 0.1 (우연 가능성) (x1), profit_factor 1.27 < 1.5 (x1) |
| `supertrend_multi` | sharpe -1.15 < 1.0 (x1), profit_factor 0.84 < 1.5 (x1), mc_p_value 0.687 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 13 |
| profit_factor 0.89 < 1.5 | 10 |
| trades 7 < 15 | 6 |
| profit_factor 0.52 < 1.5 | 6 |
| profit_factor 0.71 < 1.5 | 6 |
| profit_factor 1.37 < 1.5 | 5 |
| profit_factor 0.69 < 1.5 | 5 |
| profit_factor 0.76 < 1.5 | 5 |
| profit_factor 0.63 < 1.5 | 5 |
| profit_factor 0.57 < 1.5 | 5 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `acceleration_band` | 0 | 0 | 60 | 100.0% |
| `dema_cross` | 0 | 0 | 284 | 100.0% |
| `engulfing_zone` | 0 | 0 | 297 | 100.0% |
| `lob_maker` | 0 | 1 | 790 | 99.9% |
| `momentum_quality` | 0 | 5 | 911 | 99.5% |
| `relative_volume` | 0 | 5 | 834 | 99.4% |
| `frama` | 0 | 5 | 698 | 99.3% |
| `volatility_cluster` | 0 | 5 | 613 | 99.2% |
| `roc_ma_cross` | 0 | 3 | 365 | 99.2% |
| `cmf` | 0 | 6 | 627 | 99.1% |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.65% -> $9,635
- **Top 5 균등배분**: +1.27% -> $10,127
