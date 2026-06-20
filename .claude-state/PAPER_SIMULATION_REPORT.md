# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-20T20:46:55.793161Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-20T20:51:08.559349Z_
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
| 테스트 전략 | 20개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 20개 |
| 평균 수익률 | -3.82% |
| 최고 수익률 | 5.60% (price_cluster) |
| 최저 수익률 | -12.35% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +5.60% | 0.90 | 37.2% | 1.21 | 41 | 10.8% | 2/8 | FAIL |
| 2 | `roc_ma_cross` | +2.54% | 0.25 | 36.2% | 1.20 | 36 | 9.4% | 2/8 | FAIL |
| 3 | `frama` | +2.20% | 0.33 | 35.2% | 1.15 | 40 | 10.3% | 1/8 | FAIL |
| 4 | `positional_scaling` | +0.65% | -0.25 | 33.7% | 1.12 | 34 | 10.0% | 1/8 | FAIL |
| 5 | `lob_maker` | -0.75% | -0.17 | 35.0% | 1.04 | 75 | 19.2% | 0/8 | FAIL |
| 6 | `dema_cross` | -1.81% | -2.06 | 15.0% | 0.31 | 3 | 2.4% | 0/8 | FAIL |
| 7 | `acceleration_band` | -3.42% | -0.86 | 32.0% | 0.99 | 44 | 14.2% | 1/8 | FAIL |
| 8 | `order_flow_imbalance_v2` | -3.86% | -0.70 | 33.2% | 0.96 | 67 | 16.0% | 0/8 | FAIL |
| 9 | `narrow_range` | -3.94% | -0.76 | 33.5% | 0.93 | 46 | 11.7% | 0/8 | FAIL |
| 10 | `volume_breakout` | -4.85% | -0.94 | 32.4% | 0.94 | 72 | 17.5% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 76.3 | p100 | 0.90 | 1.17 | 1.21 | 41 | 10.8% | 2/8 | FAIL |
| 2 | `roc_ma_cross` | 67.5 | p94 | 0.25 | 2.54 | 1.20 | 36 | 9.4% | 2/8 | FAIL |
| 3 | `frama` | 64.6 | p89 | 0.33 | 1.70 | 1.15 | 40 | 10.3% | 1/8 | FAIL |
| 4 | `lob_maker` | 57.4 | p84 | -0.17 | 2.15 | 1.04 | 75 | 19.2% | 0/8 | FAIL |
| 5 | `positional_scaling` | 55.3 | p78 | -0.25 | 2.85 | 1.12 | 34 | 10.0% | 1/8 | FAIL |
| 6 | `order_flow_imbalance_v2` | 52.7 | p73 | -0.70 | 2.04 | 0.96 | 67 | 16.0% | 0/8 | FAIL |
| 7 | `price_action_momentum` | 51.5 | p68 | -1.10 | 2.92 | 0.97 | 73 | 18.2% | 1/8 | FAIL |
| 8 | `cmf` | 50.0 | p63 | -1.10 | 1.32 | 0.89 | 68 | 17.5% | 0/8 | FAIL |
| 9 | `acceleration_band` | 49.8 | p57 | -0.86 | 2.53 | 0.99 | 44 | 14.2% | 1/8 | FAIL |
| 10 | `volume_breakout` | 49.6 | p52 | -0.94 | 2.33 | 0.94 | 72 | 17.5% | 0/8 | FAIL |
| 11 | `relative_volume` | 49.3 | p47 | -1.15 | 1.83 | 0.90 | 64 | 14.3% | 0/8 | FAIL |
| 12 | `narrow_range` | 48.9 | p42 | -0.76 | 1.39 | 0.93 | 46 | 11.7% | 0/8 | FAIL |
| 13 | `momentum_quality` | 48.3 | p36 | -1.34 | 3.09 | 0.93 | 70 | 17.4% | 1/8 | FAIL |
| 14 | `htf_ema` | 48.1 | p31 | -0.83 | 0.62 | 0.89 | 43 | 12.3% | 0/8 | FAIL |
| 15 | `elder_impulse` | 40.8 | p26 | -1.35 | 1.21 | 0.82 | 42 | 12.8% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +5.60% | 0.90 | 1.21 | 41 | 2/8 | FAIL |
| `roc_ma_cross` | +2.54% | 0.25 | 1.20 | 36 | 2/8 | FAIL |
| `frama` | +2.20% | 0.33 | 1.15 | 40 | 1/8 | FAIL |
| `positional_scaling` | +0.65% | -0.25 | 1.12 | 34 | 1/8 | FAIL |
| `lob_maker` | -0.75% | -0.17 | 1.04 | 75 | 0/8 | FAIL |
| `dema_cross` | -1.81% | -2.06 | 0.31 | 3 | 0/8 | FAIL |
| `acceleration_band` | -3.42% | -0.86 | 0.99 | 44 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | -3.86% | -0.70 | 0.96 | 67 | 0/8 | FAIL |
| `narrow_range` | -3.94% | -0.76 | 0.93 | 46 | 0/8 | FAIL |
| `volume_breakout` | -4.85% | -0.94 | 0.94 | 72 | 0/8 | FAIL |
| `htf_ema` | -4.95% | -0.83 | 0.89 | 43 | 0/8 | FAIL |
| `price_action_momentum` | -5.15% | -1.10 | 0.97 | 73 | 1/8 | FAIL |
| `momentum_quality` | -5.26% | -1.34 | 0.93 | 70 | 1/8 | FAIL |
| `engulfing_zone` | -5.71% | -1.34 | 0.78 | 25 | 0/8 | FAIL |
| `linear_channel_rev` | -5.94% | -2.60 | 0.67 | 28 | 0/8 | FAIL |
| `relative_volume` | -6.12% | -1.15 | 0.90 | 64 | 0/8 | FAIL |
| `elder_impulse` | -6.24% | -1.35 | 0.82 | 42 | 0/8 | FAIL |
| `cmf` | -7.81% | -1.10 | 0.89 | 68 | 0/8 | FAIL |
| `volatility_cluster` | -9.20% | -2.22 | 0.80 | 54 | 0/8 | FAIL |
| `wick_reversal` | -12.35% | -3.30 | 0.62 | 42 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_cluster` | sharpe -0.55 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1), mc_p_value 0.618 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe 0.20 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1), mc_p_value 0.458 > 0.1 (우연 가능성) (x1) |
| `frama` | sharpe -0.84 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.600 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.153 > 0.1 (우연 가능성) (x1), sharpe -1.01 < 1.0 (x1) |
| `lob_maker` | sharpe -2.41 < 1.0 (x1), max_drawdown 30.9% > 20% (x1), profit_factor 0.79 < 1.5 (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x4), trades 2 < 15 (x3), trades 3 < 15 (x2) |
| `acceleration_band` | profit_factor 1.40 < 1.5 (x1), mc_p_value 0.188 > 0.1 (우연 가능성) (x1), sharpe -1.37 < 1.0 (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.866 > 0.1 (우연 가능성) (x2), profit_factor 1.27 < 1.5 (x1), mc_p_value 0.194 > 0.1 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.21 < 1.5 (x1), mc_p_value 0.293 > 0.1 (우연 가능성) (x1), sharpe -0.38 < 1.0 (x1) |
| `volume_breakout` | profit_factor 1.27 < 1.5 (x2), sharpe 0.29 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1) |
| `htf_ema` | profit_factor 0.83 < 1.5 (x2), sharpe -0.18 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1) |
| `price_action_momentum` | sharpe 0.85 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.326 > 0.1 (우연 가능성) (x1) |
| `momentum_quality` | max_drawdown 23.5% > 20% (x2), profit_factor 1.38 < 1.5 (x1), sharpe -0.81 < 1.0 (x1) |
| `engulfing_zone` | sharpe -2.02 < 1.0 (x1), profit_factor 0.67 < 1.5 (x1), mc_p_value 0.804 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe 0.78 < 1.0 (x1), profit_factor 1.19 < 1.5 (x1), mc_p_value 0.308 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | profit_factor 0.96 < 1.5 (x2), sharpe 0.40 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1) |
| `elder_impulse` | profit_factor 0.90 < 1.5 (x2), sharpe -0.79 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1) |
| `cmf` | profit_factor 0.72 < 1.5 (x3), mc_p_value 0.876 > 0.1 (우연 가능성) (x2), sharpe 0.29 < 1.0 (x1) |
| `volatility_cluster` | profit_factor 0.36 < 1.5 (x2), sharpe -0.62 < 1.0 (x1), profit_factor 0.94 < 1.5 (x1) |
| `wick_reversal` | sharpe -3.81 < 1.0 (x1), max_drawdown 20.9% > 20% (x1), profit_factor 0.54 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.81 < 1.5 | 6 |
| profit_factor 0.91 < 1.5 | 5 |
| profit_factor 0.99 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 0.72 < 1.5 | 4 |
| mc_p_value 0.509 > 0.1 (우연 가능성) | 3 |
| profit_factor 1.05 < 1.5 | 3 |
| profit_factor 0.80 < 1.5 | 3 |
| profit_factor 0.83 < 1.5 | 3 |
| profit_factor 0.73 < 1.5 | 3 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 5 | 19 | 79.2% |
| `htf_ema` | 0 | 282 | 62 | 18.0% |
| `frama` | 0 | 267 | 56 | 17.3% |
| `price_action_momentum` | 0 | 483 | 101 | 17.3% |
| `cmf` | 0 | 456 | 86 | 15.9% |
| `lob_maker` | 0 | 505 | 94 | 15.7% |
| `relative_volume` | 0 | 437 | 76 | 14.8% |
| `volume_breakout` | 0 | 492 | 84 | 14.6% |
| `elder_impulse` | 0 | 288 | 46 | 13.8% |
| `positional_scaling` | 0 | 233 | 36 | 13.4% |

## 포트폴리오 가상 배분

- **전체 20개 균등배분**: -3.82% -> $9,618
- **Top 5 균등배분**: +2.05% -> $10,205


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-20T20:55:09.213808Z_
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
| 테스트 전략 | 20개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 20개 |
| 평균 수익률 | -3.79% |
| 최고 수익률 | 3.39% (volatility_cluster) |
| 최저 수익률 | -12.41% (volume_breakout) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `volatility_cluster` | +3.39% | 0.63 | 40.6% | 1.21 | 42 | 9.4% | 0/8 | FAIL |
| 2 | `momentum_quality` | +0.55% | 0.04 | 36.1% | 1.03 | 60 | 11.4% | 0/8 | FAIL |
| 3 | `engulfing_zone` | +0.09% | -0.29 | 36.4% | 1.10 | 25 | 9.5% | 1/8 | FAIL |
| 4 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 5 | `price_action_momentum` | +0.00% | 0.01 | 37.4% | 1.06 | 43 | 11.3% | 1/8 | FAIL |
| 6 | `narrow_range` | -0.06% | -0.29 | 37.5% | 1.04 | 40 | 12.1% | 1/8 | FAIL |
| 7 | `dema_cross` | -0.53% | -0.47 | 39.6% | 1.06 | 12 | 4.3% | 0/8 | FAIL |
| 8 | `cmf` | -1.82% | -0.64 | 32.5% | 0.97 | 48 | 13.9% | 1/8 | FAIL |
| 9 | `elder_impulse` | -2.15% | -0.66 | 34.6% | 0.97 | 39 | 10.9% | 0/8 | FAIL |
| 10 | `linear_channel_rev` | -3.87% | -1.28 | 29.7% | 0.80 | 26 | 8.2% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 67.3 | p100 | 0.01 | 1.74 | 1.06 | 43 | 11.3% | 1/8 | FAIL |
| 2 | `volatility_cluster` | 65.7 | p94 | 0.63 | 2.03 | 1.21 | 42 | 9.4% | 0/8 | FAIL |
| 3 | `momentum_quality` | 64.3 | p89 | 0.04 | 1.44 | 1.03 | 60 | 11.4% | 0/8 | FAIL |
| 4 | `narrow_range` | 61.7 | p84 | -0.29 | 2.20 | 1.04 | 40 | 12.1% | 1/8 | FAIL |
| 5 | `cmf` | 58.3 | p78 | -0.64 | 2.29 | 0.97 | 48 | 13.9% | 1/8 | FAIL |
| 6 | `engulfing_zone` | 58.2 | p73 | -0.29 | 2.32 | 1.10 | 25 | 9.5% | 1/8 | FAIL |
| 7 | `elder_impulse` | 47.0 | p68 | -0.66 | 2.26 | 0.97 | 39 | 10.9% | 0/8 | FAIL |
| 8 | `lob_maker` | 45.9 | p63 | -1.19 | 1.19 | 0.86 | 59 | 17.5% | 0/8 | FAIL |
| 9 | `relative_volume` | 43.0 | p57 | -1.23 | 2.75 | 0.92 | 58 | 14.5% | 0/8 | FAIL |
| 10 | `dema_cross` | 42.0 | p52 | -0.47 | 2.08 | 1.06 | 12 | 4.3% | 0/8 | FAIL |
| 11 | `order_flow_imbalance_v2` | 39.4 | p47 | -1.60 | 1.81 | 0.82 | 60 | 17.5% | 0/8 | FAIL |
| 12 | `linear_channel_rev` | 34.9 | p42 | -1.28 | 1.65 | 0.80 | 26 | 8.2% | 0/8 | FAIL |
| 13 | `htf_ema` | 34.6 | p36 | -1.29 | 1.67 | 0.80 | 26 | 9.4% | 0/8 | FAIL |
| 14 | `frama` | 32.6 | p31 | -1.80 | 1.59 | 0.75 | 41 | 14.7% | 0/8 | FAIL |
| 15 | `price_cluster` | 30.8 | p26 | -1.51 | 2.03 | 0.80 | 25 | 11.8% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `volatility_cluster` | +3.39% | 0.63 | 1.21 | 42 | 0/8 | FAIL |
| `momentum_quality` | +0.55% | 0.04 | 1.03 | 60 | 0/8 | FAIL |
| `engulfing_zone` | +0.09% | -0.29 | 1.10 | 25 | 1/8 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `price_action_momentum` | +0.00% | 0.01 | 1.06 | 43 | 1/8 | FAIL |
| `narrow_range` | -0.06% | -0.29 | 1.04 | 40 | 1/8 | FAIL |
| `dema_cross` | -0.53% | -0.47 | 1.06 | 12 | 0/8 | FAIL |
| `cmf` | -1.82% | -0.64 | 0.97 | 48 | 1/8 | FAIL |
| `elder_impulse` | -2.15% | -0.66 | 0.97 | 39 | 0/8 | FAIL |
| `linear_channel_rev` | -3.87% | -1.28 | 0.80 | 26 | 0/8 | FAIL |
| `htf_ema` | -4.27% | -1.29 | 0.80 | 26 | 0/8 | FAIL |
| `acceleration_band` | -4.87% | -2.41 | 0.57 | 11 | 0/8 | FAIL |
| `relative_volume` | -5.00% | -1.23 | 0.92 | 58 | 0/8 | FAIL |
| `price_cluster` | -5.48% | -1.51 | 0.80 | 25 | 0/8 | FAIL |
| `roc_ma_cross` | -6.60% | -2.02 | 0.71 | 32 | 0/8 | FAIL |
| `positional_scaling` | -6.98% | -2.13 | 0.68 | 31 | 0/8 | FAIL |
| `lob_maker` | -7.95% | -1.19 | 0.86 | 59 | 0/8 | FAIL |
| `frama` | -8.72% | -1.80 | 0.75 | 41 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -9.21% | -1.60 | 0.82 | 60 | 0/8 | FAIL |
| `volume_breakout` | -12.41% | -2.32 | 0.76 | 69 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `volatility_cluster` | sharpe -0.05 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.515 > 0.1 (우연 가능성) (x1) |
| `momentum_quality` | sharpe -0.57 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1), mc_p_value 0.631 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -2.59 < 1.0 (x1), profit_factor 0.55 < 1.5 (x1), mc_p_value 0.883 > 0.1 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x8) |
| `price_action_momentum` | sharpe -3.23 < 1.0 (x1), max_drawdown 20.5% > 20% (x1), profit_factor 0.57 < 1.5 (x1) |
| `narrow_range` | sharpe -1.66 < 1.0 (x1), profit_factor 0.77 < 1.5 (x1), mc_p_value 0.776 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | trades 9 < 15 (x2), trades 11 < 15 (x2), sharpe -0.90 < 1.0 (x1) |
| `cmf` | sharpe -1.52 < 1.0 (x1), profit_factor 0.76 < 1.5 (x1), mc_p_value 0.800 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | sharpe 0.28 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1), mc_p_value 0.427 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -0.81 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.651 > 0.1 (우연 가능성) (x1) |
| `htf_ema` | mc_p_value 0.961 > 0.1 (우연 가능성) (x2), sharpe -2.78 < 1.0 (x1), profit_factor 0.59 < 1.5 (x1) |
| `acceleration_band` | profit_factor 0.24 < 1.5 (x2), trades 6 < 15 (x2), trades 14 < 15 (x2) |
| `relative_volume` | profit_factor 0.76 < 1.5 (x2), sharpe -2.14 < 1.0 (x1), profit_factor 0.75 < 1.5 (x1) |
| `price_cluster` | sharpe -3.42 < 1.0 (x1), profit_factor 0.49 < 1.5 (x1), mc_p_value 0.962 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 0.89 < 1.5 (x2), sharpe -2.87 < 1.0 (x1), profit_factor 0.54 < 1.5 (x1) |
| `positional_scaling` | sharpe -3.19 < 1.0 (x1), profit_factor 0.51 < 1.5 (x1), mc_p_value 0.948 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | sharpe -2.29 < 1.0 (x1), profit_factor 0.72 < 1.5 (x1), mc_p_value 0.890 > 0.1 (우연 가능성) (x1) |
| `frama` | profit_factor 0.96 < 1.5 (x2), sharpe -1.64 < 1.0 (x1), profit_factor 0.74 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe -1.04 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.694 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | profit_factor 0.78 < 1.5 (x2), sharpe -1.99 < 1.0 (x1), profit_factor 0.76 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 8 |
| profit_factor 0.76 < 1.5 | 7 |
| profit_factor 0.85 < 1.5 | 5 |
| profit_factor 1.04 < 1.5 | 4 |
| profit_factor 0.75 < 1.5 | 4 |
| profit_factor 0.94 < 1.5 | 4 |
| sharpe -1.52 < 1.0 | 3 |
| profit_factor 0.86 < 1.5 | 3 |
| profit_factor 0.77 < 1.5 | 3 |
| trades 9 < 15 | 3 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 0 | 99 | 100.0% |
| `frama` | 0 | 78 | 253 | 76.4% |
| `elder_impulse` | 0 | 107 | 207 | 65.9% |
| `relative_volume` | 0 | 169 | 292 | 63.3% |
| `roc_ma_cross` | 0 | 95 | 160 | 62.7% |
| `engulfing_zone` | 0 | 76 | 126 | 62.4% |
| `volume_breakout` | 0 | 211 | 338 | 61.6% |
| `cmf` | 0 | 150 | 232 | 60.7% |
| `order_flow_imbalance_v2` | 0 | 196 | 282 | 59.0% |
| `momentum_quality` | 0 | 199 | 282 | 58.6% |

## 포트폴리오 가상 배분

- **전체 20개 균등배분**: -3.79% -> $9,621
- **Top 5 균등배분**: +0.81% -> $10,081


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-20T20:58:55.923553Z_
_Symbol: SOL/USDT_
_Data Source: CSV fallback SOL/USDT 1h (/home/user/Trading/data/historical)_
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
| 테스트 전략 | 20개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 20개 |
| 평균 수익률 | -5.86% |
| 최고 수익률 | 0.00% (wick_reversal) |
| 최저 수익률 | -16.61% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 2 | `acceleration_band` | -0.02% | -0.33 | 33.6% | 1.36 | 7 | 3.8% | 0/8 | FAIL |
| 3 | `elder_impulse` | -0.70% | -0.18 | 35.8% | 0.98 | 39 | 10.2% | 0/8 | FAIL |
| 4 | `momentum_quality` | -1.48% | -0.37 | 33.9% | 0.98 | 59 | 12.8% | 0/8 | FAIL |
| 5 | `htf_ema` | -1.74% | -0.51 | 33.8% | 0.96 | 32 | 9.8% | 0/8 | FAIL |
| 6 | `volume_breakout` | -2.87% | -0.92 | 31.6% | 0.97 | 50 | 13.0% | 2/8 | FAIL |
| 7 | `dema_cross` | -4.26% | -1.54 | 33.7% | 0.73 | 22 | 8.8% | 0/8 | FAIL |
| 8 | `linear_channel_rev` | -4.62% | -1.46 | 29.0% | 0.74 | 26 | 7.7% | 0/8 | FAIL |
| 9 | `order_flow_imbalance_v2` | -4.72% | -0.81 | 33.6% | 0.90 | 59 | 13.3% | 0/8 | FAIL |
| 10 | `price_cluster` | -4.77% | -1.57 | 28.5% | 0.70 | 21 | 8.3% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 64.4 | p100 | -0.37 | 1.83 | 0.98 | 59 | 12.8% | 0/8 | FAIL |
| 2 | `volume_breakout` | 62.4 | p94 | -0.92 | 2.87 | 0.97 | 50 | 13.0% | 2/8 | FAIL |
| 3 | `elder_impulse` | 61.4 | p89 | -0.18 | 1.06 | 0.98 | 39 | 10.2% | 0/8 | FAIL |
| 4 | `order_flow_imbalance_v2` | 59.8 | p84 | -0.81 | 1.50 | 0.90 | 59 | 13.3% | 0/8 | FAIL |
| 5 | `htf_ema` | 53.2 | p78 | -0.51 | 1.76 | 0.96 | 32 | 9.8% | 0/8 | FAIL |
| 6 | `acceleration_band` | 50.3 | p73 | -0.33 | 2.04 | 1.36 | 7 | 3.8% | 0/8 | FAIL |
| 7 | `volatility_cluster` | 47.4 | p68 | -1.31 | 1.13 | 0.80 | 39 | 10.6% | 0/8 | FAIL |
| 8 | `price_action_momentum` | 43.3 | p63 | -1.83 | 2.60 | 0.81 | 40 | 13.1% | 1/8 | FAIL |
| 9 | `relative_volume` | 41.4 | p57 | -2.42 | 1.04 | 0.71 | 60 | 16.2% | 0/8 | FAIL |
| 10 | `frama` | 40.1 | p52 | -2.05 | 1.60 | 0.73 | 50 | 15.5% | 0/8 | FAIL |
| 11 | `linear_channel_rev` | 40.0 | p47 | -1.46 | 1.11 | 0.74 | 26 | 7.7% | 0/8 | FAIL |
| 12 | `narrow_range` | 38.9 | p42 | -1.93 | 0.96 | 0.71 | 38 | 12.3% | 0/8 | FAIL |
| 13 | `roc_ma_cross` | 38.2 | p36 | -1.63 | 1.47 | 0.73 | 28 | 9.3% | 0/8 | FAIL |
| 14 | `dema_cross` | 36.1 | p31 | -1.54 | 1.70 | 0.73 | 22 | 8.8% | 0/8 | FAIL |
| 15 | `price_cluster` | 35.2 | p26 | -1.57 | 1.53 | 0.70 | 21 | 8.3% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `acceleration_band` | -0.02% | -0.33 | 1.36 | 7 | 0/8 | FAIL |
| `elder_impulse` | -0.70% | -0.18 | 0.98 | 39 | 0/8 | FAIL |
| `momentum_quality` | -1.48% | -0.37 | 0.98 | 59 | 0/8 | FAIL |
| `htf_ema` | -1.74% | -0.51 | 0.96 | 32 | 0/8 | FAIL |
| `volume_breakout` | -2.87% | -0.92 | 0.97 | 50 | 2/8 | FAIL |
| `dema_cross` | -4.26% | -1.54 | 0.73 | 22 | 0/8 | FAIL |
| `linear_channel_rev` | -4.62% | -1.46 | 0.74 | 26 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -4.72% | -0.81 | 0.90 | 59 | 0/8 | FAIL |
| `price_cluster` | -4.77% | -1.57 | 0.70 | 21 | 0/8 | FAIL |
| `volatility_cluster` | -4.90% | -1.31 | 0.80 | 39 | 0/8 | FAIL |
| `roc_ma_cross` | -5.08% | -1.63 | 0.73 | 28 | 0/8 | FAIL |
| `price_action_momentum` | -6.24% | -1.83 | 0.81 | 40 | 1/8 | FAIL |
| `engulfing_zone` | -7.65% | -2.62 | 0.66 | 24 | 0/8 | FAIL |
| `narrow_range` | -7.66% | -1.93 | 0.71 | 38 | 0/8 | FAIL |
| `positional_scaling` | -10.42% | -3.09 | 0.56 | 32 | 0/8 | FAIL |
| `frama` | -10.86% | -2.05 | 0.73 | 50 | 0/8 | FAIL |
| `cmf` | -10.88% | -2.61 | 0.67 | 46 | 0/8 | FAIL |
| `relative_volume` | -11.65% | -2.42 | 0.71 | 60 | 0/8 | FAIL |
| `lob_maker` | -16.61% | -2.96 | 0.66 | 58 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `wick_reversal` | no trades generated (x8) |
| `acceleration_band` | trades 7 < 15 (x4), trades 8 < 15 (x2), trades 6 < 15 (x2) |
| `elder_impulse` | profit_factor 1.10 < 1.5 (x2), sharpe -1.44 < 1.0 (x1), profit_factor 0.77 < 1.5 (x1) |
| `momentum_quality` | profit_factor 0.99 < 1.5 (x2), sharpe -2.05 < 1.0 (x1), profit_factor 0.74 < 1.5 (x1) |
| `htf_ema` | sharpe -3.25 < 1.0 (x1), profit_factor 0.53 < 1.5 (x1), mc_p_value 0.951 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | mc_p_value 0.947 > 0.1 (우연 가능성) (x2), sharpe -5.27 < 1.0 (x1), max_drawdown 23.9% > 20% (x1) |
| `dema_cross` | sharpe -0.65 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.622 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -2.21 < 1.0 (x1), profit_factor 0.60 < 1.5 (x1), mc_p_value 0.878 > 0.1 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe -3.67 < 1.0 (x1), profit_factor 0.58 < 1.5 (x1), mc_p_value 0.970 > 0.1 (우연 가능성) (x1) |
| `price_cluster` | sharpe -0.73 < 1.0 (x1), profit_factor 0.84 < 1.5 (x1), mc_p_value 0.647 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -1.89 < 1.0 (x1), profit_factor 0.72 < 1.5 (x1), mc_p_value 0.831 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -3.71 < 1.0 (x1), profit_factor 0.43 < 1.5 (x1), mc_p_value 0.968 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe -4.22 < 1.0 (x1), profit_factor 0.49 < 1.5 (x1), mc_p_value 0.978 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | profit_factor 0.37 < 1.5 (x2), sharpe -3.92 < 1.0 (x1), mc_p_value 0.974 > 0.1 (우연 가능성) (x1) |
| `narrow_range` | sharpe -2.77 < 1.0 (x1), profit_factor 0.62 < 1.5 (x1), mc_p_value 0.906 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 0.31 < 1.5 (x2), sharpe -3.83 < 1.0 (x1), profit_factor 0.45 < 1.5 (x1) |
| `frama` | sharpe -2.75 < 1.0 (x1), profit_factor 0.62 < 1.5 (x1), mc_p_value 0.921 > 0.1 (우연 가능성) (x1) |
| `cmf` | sharpe -7.33 < 1.0 (x1), max_drawdown 24.9% > 20% (x1), profit_factor 0.28 < 1.5 (x1) |
| `relative_volume` | profit_factor 0.70 < 1.5 (x2), profit_factor 0.75 < 1.5 (x2), sharpe -4.37 < 1.0 (x1) |
| `lob_maker` | sharpe -5.80 < 1.0 (x1), max_drawdown 28.8% > 20% (x1), profit_factor 0.43 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 8 |
| profit_factor 0.45 < 1.5 | 5 |
| profit_factor 0.73 < 1.5 | 5 |
| trades 7 < 15 | 4 |
| profit_factor 0.70 < 1.5 | 4 |
| profit_factor 0.74 < 1.5 | 4 |
| profit_factor 0.53 < 1.5 | 4 |
| profit_factor 0.69 < 1.5 | 4 |
| profit_factor 0.75 < 1.5 | 4 |
| profit_factor 0.72 < 1.5 | 4 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `acceleration_band` | 0 | 0 | 56 | 100.0% |
| `dema_cross` | 0 | 0 | 180 | 100.0% |
| `engulfing_zone` | 0 | 0 | 196 | 100.0% |
| `relative_volume` | 0 | 0 | 481 | 100.0% |
| `lob_maker` | 0 | 0 | 466 | 100.0% |
| `momentum_quality` | 0 | 1 | 470 | 99.8% |
| `order_flow_imbalance_v2` | 0 | 1 | 469 | 99.8% |
| `volume_breakout` | 0 | 1 | 401 | 99.8% |
| `price_action_momentum` | 0 | 1 | 321 | 99.7% |
| `volatility_cluster` | 0 | 1 | 311 | 99.7% |

## 포트폴리오 가상 배분

- **전체 20개 균등배분**: -5.86% -> $9,414
- **Top 5 균등배분**: -0.79% -> $9,921
