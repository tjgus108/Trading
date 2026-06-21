# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-21T05:14:29.534489Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-21T05:18:14.487489Z_
_Symbol: BTC/USDT_
_Data Source: CSV BTC/USDT 1h (/home/user/Trading/data/historical)_
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
| 평균 수익률 | -3.59% |
| 최고 수익률 | 4.82% (price_cluster) |
| 최저 수익률 | -10.62% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +4.82% | 0.84 | 37.2% | 1.20 | 41 | 9.8% | 1/8 | FAIL |
| 2 | `roc_ma_cross` | +2.78% | 0.32 | 36.2% | 1.21 | 36 | 8.2% | 2/8 | FAIL |
| 3 | `frama` | +1.36% | 0.19 | 35.2% | 1.11 | 40 | 9.5% | 1/8 | FAIL |
| 4 | `positional_scaling` | +0.17% | -0.41 | 33.7% | 1.09 | 34 | 9.2% | 1/8 | FAIL |
| 5 | `lob_maker` | -0.21% | -0.09 | 35.0% | 1.05 | 75 | 17.1% | 0/8 | FAIL |
| 6 | `dema_cross` | -1.76% | -2.10 | 15.0% | 0.28 | 3 | 2.3% | 0/8 | FAIL |
| 7 | `narrow_range` | -2.45% | -0.55 | 33.5% | 0.97 | 46 | 10.2% | 0/8 | FAIL |
| 8 | `acceleration_band` | -3.38% | -0.98 | 32.0% | 0.97 | 44 | 13.1% | 1/8 | FAIL |
| 9 | `volume_breakout` | -3.73% | -0.81 | 32.4% | 0.96 | 72 | 15.7% | 0/8 | FAIL |
| 10 | `order_flow_imbalance_v2` | -4.01% | -0.80 | 33.2% | 0.95 | 67 | 15.1% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 71.3 | p100 | 0.84 | 1.10 | 1.20 | 41 | 9.8% | 1/8 | FAIL |
| 2 | `roc_ma_cross` | 68.7 | p94 | 0.32 | 2.44 | 1.21 | 36 | 8.2% | 2/8 | FAIL |
| 3 | `frama` | 63.3 | p89 | 0.19 | 1.60 | 1.11 | 40 | 9.5% | 1/8 | FAIL |
| 4 | `lob_maker` | 59.0 | p84 | -0.09 | 1.99 | 1.05 | 75 | 17.1% | 0/8 | FAIL |
| 5 | `positional_scaling` | 53.4 | p78 | -0.41 | 2.82 | 1.09 | 34 | 9.2% | 1/8 | FAIL |
| 6 | `narrow_range` | 51.4 | p73 | -0.55 | 1.50 | 0.97 | 46 | 10.2% | 0/8 | FAIL |
| 7 | `volume_breakout` | 51.3 | p68 | -0.81 | 2.23 | 0.96 | 72 | 15.7% | 0/8 | FAIL |
| 8 | `order_flow_imbalance_v2` | 51.0 | p63 | -0.80 | 2.06 | 0.95 | 67 | 15.1% | 0/8 | FAIL |
| 9 | `price_action_momentum` | 50.3 | p57 | -1.16 | 2.83 | 0.96 | 73 | 16.9% | 1/8 | FAIL |
| 10 | `htf_ema` | 48.8 | p52 | -0.75 | 0.72 | 0.90 | 43 | 11.3% | 0/8 | FAIL |
| 11 | `acceleration_band` | 48.1 | p47 | -0.98 | 2.59 | 0.97 | 44 | 13.1% | 1/8 | FAIL |
| 12 | `relative_volume` | 47.8 | p42 | -1.31 | 1.61 | 0.88 | 64 | 13.5% | 0/8 | FAIL |
| 13 | `cmf` | 47.1 | p36 | -1.34 | 1.30 | 0.87 | 68 | 16.5% | 0/8 | FAIL |
| 14 | `momentum_quality` | 46.6 | p31 | -1.44 | 3.07 | 0.92 | 70 | 16.0% | 1/8 | FAIL |
| 15 | `elder_impulse` | 42.6 | p26 | -1.18 | 1.13 | 0.84 | 42 | 11.6% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +4.82% | 0.84 | 1.20 | 41 | 1/8 | FAIL |
| `roc_ma_cross` | +2.78% | 0.32 | 1.21 | 36 | 2/8 | FAIL |
| `frama` | +1.36% | 0.19 | 1.11 | 40 | 1/8 | FAIL |
| `positional_scaling` | +0.17% | -0.41 | 1.09 | 34 | 1/8 | FAIL |
| `lob_maker` | -0.21% | -0.09 | 1.05 | 75 | 0/8 | FAIL |
| `dema_cross` | -1.76% | -2.10 | 0.28 | 3 | 0/8 | FAIL |
| `narrow_range` | -2.45% | -0.55 | 0.97 | 46 | 0/8 | FAIL |
| `acceleration_band` | -3.38% | -0.98 | 0.97 | 44 | 1/8 | FAIL |
| `volume_breakout` | -3.73% | -0.81 | 0.96 | 72 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -4.01% | -0.80 | 0.95 | 67 | 0/8 | FAIL |
| `htf_ema` | -4.14% | -0.75 | 0.90 | 43 | 0/8 | FAIL |
| `elder_impulse` | -5.06% | -1.18 | 0.84 | 42 | 0/8 | FAIL |
| `price_action_momentum` | -5.08% | -1.16 | 0.96 | 73 | 1/8 | FAIL |
| `momentum_quality` | -5.21% | -1.44 | 0.92 | 70 | 1/8 | FAIL |
| `linear_channel_rev` | -5.90% | -2.71 | 0.65 | 28 | 0/8 | FAIL |
| `engulfing_zone` | -6.36% | -1.65 | 0.72 | 25 | 0/8 | FAIL |
| `relative_volume` | -6.44% | -1.31 | 0.88 | 64 | 0/8 | FAIL |
| `volatility_cluster` | -8.17% | -2.12 | 0.80 | 54 | 0/8 | FAIL |
| `cmf` | -8.47% | -1.34 | 0.87 | 68 | 0/8 | FAIL |
| `wick_reversal` | -10.62% | -3.13 | 0.65 | 42 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_cluster` | sharpe -0.49 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1), mc_p_value 0.604 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -0.02 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1), mc_p_value 0.495 > 0.1 (우연 가능성) (x1) |
| `frama` | profit_factor 0.82 < 1.5 (x2), sharpe -0.87 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1) |
| `positional_scaling` | profit_factor 1.44 < 1.5 (x1), mc_p_value 0.166 > 0.1 (우연 가능성) (x1), sharpe -1.21 < 1.0 (x1) |
| `lob_maker` | sharpe -2.32 < 1.0 (x1), max_drawdown 27.9% > 20% (x1), profit_factor 0.79 < 1.5 (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x4), trades 2 < 15 (x3), trades 3 < 15 (x2) |
| `narrow_range` | profit_factor 1.29 < 1.5 (x1), mc_p_value 0.227 > 0.1 (우연 가능성) (x1), sharpe 0.15 < 1.0 (x1) |
| `acceleration_band` | profit_factor 0.88 < 1.5 (x2), profit_factor 1.40 < 1.5 (x1), mc_p_value 0.189 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -0.15 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1), mc_p_value 0.490 > 0.1 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.219 > 0.1 (우연 가능성) (x1), sharpe -2.07 < 1.0 (x1) |
| `htf_ema` | sharpe -0.42 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1), mc_p_value 0.572 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | profit_factor 0.94 < 1.5 (x2), sharpe -0.53 < 1.0 (x1), mc_p_value 0.572 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe 0.55 < 1.0 (x1), profit_factor 1.09 < 1.5 (x1), mc_p_value 0.374 > 0.1 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.101 > 0.1 (우연 가능성) (x1), sharpe -0.57 < 1.0 (x1) |
| `linear_channel_rev` | sharpe 0.42 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), mc_p_value 0.383 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -2.15 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1), mc_p_value 0.828 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | sharpe 0.23 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.413 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | mc_p_value 0.999 > 0.1 (우연 가능성) (x2), sharpe -0.84 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1) |
| `cmf` | sharpe -0.11 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1), mc_p_value 0.485 > 0.1 (우연 가능성) (x1) |
| `wick_reversal` | profit_factor 0.59 < 1.5 (x2), sharpe -3.75 < 1.0 (x1), profit_factor 0.55 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.73 < 1.5 | 6 |
| profit_factor 0.82 < 1.5 | 5 |
| profit_factor 1.01 < 1.5 | 4 |
| profit_factor 0.74 < 1.5 | 4 |
| profit_factor 0.83 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 0.95 < 1.5 | 4 |
| profit_factor 0.91 < 1.5 | 3 |
| profit_factor 0.87 < 1.5 | 3 |
| profit_factor 1.29 < 1.5 | 3 |

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

- **전체 20개 균등배분**: -3.59% -> $9,641
- **Top 5 균등배분**: +1.79% -> $10,179


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-21T05:21:52.155071Z_
_Symbol: ETH/USDT_
_Data Source: CSV ETH/USDT 1h (/home/user/Trading/data/historical)_
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
| 평균 수익률 | -2.97% |
| 최고 수익률 | 3.83% (volatility_cluster) |
| 최저 수익률 | -9.31% (volume_breakout) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `volatility_cluster` | +3.83% | 0.79 | 40.6% | 1.23 | 42 | 8.3% | 0/8 | FAIL |
| 2 | `momentum_quality` | +1.35% | 0.19 | 36.1% | 1.06 | 60 | 10.4% | 0/8 | FAIL |
| 3 | `price_action_momentum` | +1.01% | 0.20 | 37.4% | 1.11 | 43 | 9.9% | 1/8 | FAIL |
| 4 | `engulfing_zone` | +0.67% | -0.17 | 36.4% | 1.12 | 25 | 8.5% | 1/8 | FAIL |
| 5 | `narrow_range` | +0.60% | -0.14 | 37.5% | 1.07 | 40 | 10.8% | 1/8 | FAIL |
| 6 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 7 | `cmf` | -0.52% | -0.41 | 32.5% | 1.00 | 48 | 12.2% | 1/8 | FAIL |
| 8 | `dema_cross` | -0.55% | -0.55 | 39.6% | 1.06 | 12 | 4.2% | 0/8 | FAIL |
| 9 | `elder_impulse` | -1.77% | -0.74 | 34.6% | 0.98 | 39 | 9.9% | 0/8 | FAIL |
| 10 | `relative_volume` | -3.34% | -0.96 | 36.4% | 0.95 | 58 | 12.7% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 68.3 | p100 | 0.20 | 1.76 | 1.11 | 43 | 9.9% | 1/8 | FAIL |
| 2 | `volatility_cluster` | 66.1 | p94 | 0.79 | 1.83 | 1.23 | 42 | 8.3% | 0/8 | FAIL |
| 3 | `momentum_quality` | 64.8 | p89 | 0.19 | 1.40 | 1.06 | 60 | 10.4% | 0/8 | FAIL |
| 4 | `narrow_range` | 62.6 | p84 | -0.14 | 2.15 | 1.07 | 40 | 10.8% | 1/8 | FAIL |
| 5 | `cmf` | 60.5 | p78 | -0.41 | 2.23 | 1.00 | 48 | 12.2% | 1/8 | FAIL |
| 6 | `engulfing_zone` | 58.6 | p73 | -0.17 | 2.25 | 1.12 | 25 | 8.5% | 1/8 | FAIL |
| 7 | `lob_maker` | 48.0 | p68 | -1.02 | 1.05 | 0.87 | 59 | 15.5% | 0/8 | FAIL |
| 8 | `relative_volume` | 45.9 | p63 | -0.96 | 2.72 | 0.95 | 58 | 12.7% | 0/8 | FAIL |
| 9 | `elder_impulse` | 45.0 | p57 | -0.74 | 2.47 | 0.98 | 39 | 9.9% | 0/8 | FAIL |
| 10 | `dema_cross` | 40.3 | p52 | -0.55 | 2.23 | 1.06 | 12 | 4.2% | 0/8 | FAIL |
| 11 | `order_flow_imbalance_v2` | 38.9 | p47 | -1.61 | 1.84 | 0.82 | 60 | 16.2% | 0/8 | FAIL |
| 12 | `htf_ema` | 36.8 | p42 | -1.09 | 1.59 | 0.83 | 26 | 8.4% | 0/8 | FAIL |
| 13 | `volume_breakout` | 35.3 | p36 | -1.90 | 2.34 | 0.81 | 69 | 18.0% | 0/8 | FAIL |
| 14 | `linear_channel_rev` | 34.4 | p31 | -1.31 | 1.69 | 0.80 | 26 | 7.6% | 0/8 | FAIL |
| 15 | `frama` | 33.6 | p26 | -1.72 | 1.68 | 0.77 | 41 | 13.4% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `volatility_cluster` | +3.83% | 0.79 | 1.23 | 42 | 0/8 | FAIL |
| `momentum_quality` | +1.35% | 0.19 | 1.06 | 60 | 0/8 | FAIL |
| `price_action_momentum` | +1.01% | 0.20 | 1.11 | 43 | 1/8 | FAIL |
| `engulfing_zone` | +0.67% | -0.17 | 1.12 | 25 | 1/8 | FAIL |
| `narrow_range` | +0.60% | -0.14 | 1.07 | 40 | 1/8 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `cmf` | -0.52% | -0.41 | 1.00 | 48 | 1/8 | FAIL |
| `dema_cross` | -0.55% | -0.55 | 1.06 | 12 | 0/8 | FAIL |
| `elder_impulse` | -1.77% | -0.74 | 0.98 | 39 | 0/8 | FAIL |
| `relative_volume` | -3.34% | -0.96 | 0.95 | 58 | 0/8 | FAIL |
| `htf_ema` | -3.34% | -1.09 | 0.83 | 26 | 0/8 | FAIL |
| `linear_channel_rev` | -3.63% | -1.31 | 0.80 | 26 | 0/8 | FAIL |
| `acceleration_band` | -4.46% | -2.54 | 0.54 | 11 | 0/8 | FAIL |
| `price_cluster` | -4.93% | -1.51 | 0.79 | 25 | 0/8 | FAIL |
| `positional_scaling` | -6.18% | -2.05 | 0.68 | 31 | 0/8 | FAIL |
| `roc_ma_cross` | -6.42% | -2.14 | 0.70 | 32 | 0/8 | FAIL |
| `lob_maker` | -6.44% | -1.02 | 0.87 | 59 | 0/8 | FAIL |
| `frama` | -7.48% | -1.72 | 0.77 | 41 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -8.51% | -1.61 | 0.82 | 60 | 0/8 | FAIL |
| `volume_breakout` | -9.31% | -1.90 | 0.81 | 69 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `volatility_cluster` | sharpe 0.30 < 1.0 (x1), profit_factor 1.07 < 1.5 (x1), mc_p_value 0.439 > 0.1 (우연 가능성) (x1) |
| `momentum_quality` | sharpe -0.66 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.648 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe -2.90 < 1.0 (x1), profit_factor 0.61 < 1.5 (x1), mc_p_value 0.921 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -2.72 < 1.0 (x1), profit_factor 0.53 < 1.5 (x1), mc_p_value 0.901 > 0.1 (우연 가능성) (x1) |
| `narrow_range` | sharpe -1.34 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1), mc_p_value 0.724 > 0.1 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x8) |
| `cmf` | profit_factor 0.76 < 1.5 (x2), sharpe -1.08 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1) |
| `dema_cross` | trades 9 < 15 (x2), trades 11 < 15 (x2), sharpe -1.09 < 1.0 (x1) |
| `elder_impulse` | sharpe 0.34 < 1.0 (x1), profit_factor 1.07 < 1.5 (x1), mc_p_value 0.419 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | profit_factor 0.81 < 1.5 (x2), sharpe -1.57 < 1.0 (x1), mc_p_value 0.769 > 0.1 (우연 가능성) (x1) |
| `htf_ema` | sharpe -2.54 < 1.0 (x1), profit_factor 0.62 < 1.5 (x1), mc_p_value 0.896 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -1.21 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1), mc_p_value 0.709 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | trades 6 < 15 (x2), trades 14 < 15 (x2), sharpe -4.56 < 1.0 (x1) |
| `price_cluster` | sharpe -4.06 < 1.0 (x1), profit_factor 0.43 < 1.5 (x1), mc_p_value 0.976 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | sharpe -3.40 < 1.0 (x1), profit_factor 0.49 < 1.5 (x1), mc_p_value 0.956 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -2.98 < 1.0 (x1), profit_factor 0.53 < 1.5 (x1), mc_p_value 0.937 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | mc_p_value 0.872 > 0.1 (우연 가능성) (x2), sharpe -2.04 < 1.0 (x1), profit_factor 0.75 < 1.5 (x1) |
| `frama` | profit_factor 0.98 < 1.5 (x2), sharpe -2.08 < 1.0 (x1), profit_factor 0.69 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe -0.77 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.644 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -1.57 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1), mc_p_value 0.765 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 8 |
| profit_factor 0.81 < 1.5 | 6 |
| profit_factor 0.72 < 1.5 | 4 |
| profit_factor 0.91 < 1.5 | 3 |
| mc_p_value 0.234 > 0.1 (우연 가능성) | 3 |
| profit_factor 0.67 < 1.5 | 3 |
| profit_factor 1.01 < 1.5 | 3 |
| profit_factor 0.88 < 1.5 | 3 |
| profit_factor 0.49 < 1.5 | 3 |
| profit_factor 0.92 < 1.5 | 3 |

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

- **전체 20개 균등배분**: -2.97% -> $9,703
- **Top 5 균등배분**: +1.49% -> $10,149
