# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-22T10:12:22.622779Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-22T10:16:40.250111Z_
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
| 평균 수익률 | -3.18% |
| 최고 수익률 | 4.99% (price_cluster) |
| 최저 수익률 | -9.31% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +4.99% | 0.87 | 37.2% | 1.20 | 41 | 9.8% | 1/8 | FAIL |
| 2 | `roc_ma_cross` | +2.86% | 0.34 | 36.2% | 1.22 | 36 | 8.1% | 2/8 | FAIL |
| 3 | `frama` | +1.60% | 0.24 | 35.2% | 1.12 | 40 | 9.4% | 1/8 | FAIL |
| 4 | `positional_scaling` | +0.27% | -0.38 | 33.7% | 1.09 | 34 | 9.2% | 1/8 | FAIL |
| 5 | `lob_maker` | +0.15% | -0.04 | 35.0% | 1.05 | 75 | 17.0% | 0/8 | FAIL |
| 6 | `dema_cross` | -1.72% | -2.08 | 15.0% | 0.28 | 3 | 2.2% | 0/8 | FAIL |
| 7 | `narrow_range` | -2.27% | -0.51 | 33.5% | 0.97 | 46 | 10.1% | 0/8 | FAIL |
| 8 | `acceleration_band` | -3.18% | -0.94 | 32.0% | 0.98 | 44 | 13.0% | 1/8 | FAIL |
| 9 | `volume_breakout` | -3.33% | -0.74 | 32.5% | 0.96 | 72 | 15.4% | 0/8 | FAIL |
| 10 | `momentum_quality` | -3.34% | -1.19 | 31.5% | 0.96 | 71 | 15.8% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 71.4 | p100 | 0.87 | 1.10 | 1.20 | 41 | 9.8% | 1/8 | FAIL |
| 2 | `roc_ma_cross` | 68.5 | p94 | 0.34 | 2.44 | 1.22 | 36 | 8.1% | 2/8 | FAIL |
| 3 | `frama` | 63.1 | p89 | 0.24 | 1.60 | 1.12 | 40 | 9.4% | 1/8 | FAIL |
| 4 | `lob_maker` | 58.8 | p84 | -0.04 | 1.99 | 1.05 | 75 | 17.0% | 0/8 | FAIL |
| 5 | `positional_scaling` | 52.6 | p78 | -0.38 | 2.82 | 1.09 | 34 | 9.2% | 1/8 | FAIL |
| 6 | `volume_breakout` | 51.0 | p73 | -0.74 | 2.18 | 0.96 | 72 | 15.4% | 0/8 | FAIL |
| 7 | `narrow_range` | 50.5 | p68 | -0.51 | 1.48 | 0.97 | 46 | 10.1% | 0/8 | FAIL |
| 8 | `price_action_momentum` | 50.1 | p63 | -1.08 | 2.79 | 0.97 | 73 | 16.7% | 1/8 | FAIL |
| 9 | `order_flow_imbalance_v2` | 50.0 | p57 | -0.77 | 2.05 | 0.95 | 67 | 15.0% | 0/8 | FAIL |
| 10 | `relative_volume` | 49.3 | p52 | -0.99 | 1.72 | 0.92 | 64 | 13.2% | 0/8 | FAIL |
| 11 | `htf_ema` | 47.5 | p47 | -0.72 | 0.71 | 0.91 | 43 | 11.2% | 0/8 | FAIL |
| 12 | `momentum_quality` | 47.3 | p42 | -1.19 | 3.29 | 0.96 | 71 | 15.8% | 1/8 | FAIL |
| 13 | `acceleration_band` | 47.1 | p36 | -0.94 | 2.58 | 0.98 | 44 | 13.0% | 1/8 | FAIL |
| 14 | `cmf` | 46.2 | p31 | -1.23 | 1.29 | 0.88 | 68 | 16.3% | 0/8 | FAIL |
| 15 | `elder_impulse` | 40.9 | p26 | -1.15 | 1.14 | 0.85 | 42 | 11.5% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +4.99% | 0.87 | 1.20 | 41 | 1/8 | FAIL |
| `roc_ma_cross` | +2.86% | 0.34 | 1.22 | 36 | 2/8 | FAIL |
| `frama` | +1.60% | 0.24 | 1.12 | 40 | 1/8 | FAIL |
| `positional_scaling` | +0.27% | -0.38 | 1.09 | 34 | 1/8 | FAIL |
| `lob_maker` | +0.15% | -0.04 | 1.05 | 75 | 0/8 | FAIL |
| `dema_cross` | -1.72% | -2.08 | 0.28 | 3 | 0/8 | FAIL |
| `narrow_range` | -2.27% | -0.51 | 0.97 | 46 | 0/8 | FAIL |
| `acceleration_band` | -3.18% | -0.94 | 0.98 | 44 | 1/8 | FAIL |
| `volume_breakout` | -3.33% | -0.74 | 0.96 | 72 | 0/8 | FAIL |
| `momentum_quality` | -3.34% | -1.19 | 0.96 | 71 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | -3.82% | -0.77 | 0.95 | 67 | 0/8 | FAIL |
| `htf_ema` | -3.97% | -0.72 | 0.91 | 43 | 0/8 | FAIL |
| `price_action_momentum` | -4.71% | -1.08 | 0.97 | 73 | 1/8 | FAIL |
| `relative_volume` | -4.86% | -0.99 | 0.92 | 64 | 0/8 | FAIL |
| `elder_impulse` | -4.92% | -1.15 | 0.85 | 42 | 0/8 | FAIL |
| `linear_channel_rev` | -5.84% | -2.69 | 0.65 | 28 | 0/8 | FAIL |
| `engulfing_zone` | -6.31% | -1.64 | 0.72 | 25 | 0/8 | FAIL |
| `cmf` | -7.81% | -1.23 | 0.88 | 68 | 0/8 | FAIL |
| `volatility_cluster` | -8.04% | -2.09 | 0.81 | 54 | 0/8 | FAIL |
| `wick_reversal` | -9.31% | -2.64 | 0.68 | 41 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_cluster` | sharpe 0.91 < 1.0 (x2), sharpe -0.49 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1) |
| `roc_ma_cross` | sharpe 0.02 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.485 > 0.1 (우연 가능성) (x1) |
| `frama` | sharpe -0.87 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1), mc_p_value 0.603 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.163 > 0.1 (우연 가능성) (x1), sharpe -1.16 < 1.0 (x1) |
| `lob_maker` | sharpe -2.32 < 1.0 (x1), max_drawdown 27.9% > 20% (x1), profit_factor 0.79 < 1.5 (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x4), trades 2 < 15 (x3), trades 3 < 15 (x2) |
| `narrow_range` | profit_factor 1.29 < 1.5 (x1), mc_p_value 0.227 > 0.1 (우연 가능성) (x1), sharpe 0.18 < 1.0 (x1) |
| `acceleration_band` | profit_factor 0.89 < 1.5 (x2), profit_factor 1.40 < 1.5 (x1), mc_p_value 0.189 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | max_drawdown 22.1% > 20% (x2), sharpe -0.15 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1) |
| `momentum_quality` | profit_factor 0.57 < 1.5 (x2), profit_factor 1.37 < 1.5 (x1), sharpe -0.54 < 1.0 (x1) |
| `order_flow_imbalance_v2` | profit_factor 0.77 < 1.5 (x2), profit_factor 1.24 < 1.5 (x1), mc_p_value 0.219 > 0.1 (우연 가능성) (x1) |
| `htf_ema` | sharpe -0.42 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1), mc_p_value 0.572 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe 0.59 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1), mc_p_value 0.370 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | sharpe 0.23 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.413 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -0.53 < 1.0 (x1), profit_factor 0.94 < 1.5 (x1), mc_p_value 0.572 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe 0.42 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), mc_p_value 0.383 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -2.15 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1), mc_p_value 0.828 > 0.1 (우연 가능성) (x1) |
| `cmf` | sharpe -0.11 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1), mc_p_value 0.486 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.03 < 1.5 (x2), mc_p_value 0.999 > 0.1 (우연 가능성) (x2), sharpe -0.84 < 1.0 (x1) |
| `wick_reversal` | sharpe -3.75 < 1.0 (x1), profit_factor 0.55 < 1.5 (x1), mc_p_value 0.949 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.91 < 1.5 | 5 |
| profit_factor 0.74 < 1.5 | 5 |
| profit_factor 1.02 < 1.5 | 4 |
| profit_factor 0.83 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 0.77 < 1.5 | 4 |
| profit_factor 1.06 < 1.5 | 4 |
| profit_factor 0.75 < 1.5 | 3 |
| profit_factor 0.87 < 1.5 | 3 |
| profit_factor 0.84 < 1.5 | 3 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `momentum_quality` | 173 | 89 | 0.51 |
| `wick_reversal` | 101 | 83 | 0.82 |
| `volatility_cluster` | 137 | 77 | 0.56 |
| `volume_breakout` | 188 | 73 | 0.39 |
| `linear_channel_rev` | 57 | 72 | 1.26 |
| `price_action_momentum` | 188 | 62 | 0.33 |
| `elder_impulse` | 107 | 61 | 0.57 |
| `cmf` | 189 | 57 | 0.30 |
| `lob_maker` | 198 | 55 | 0.28 |
| `acceleration_band` | 106 | 52 | 0.49 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 22 | 2 | 8.3% |
| `price_cluster` | 0 | 322 | 6 | 1.8% |
| `relative_volume` | 0 | 507 | 8 | 1.6% |
| `linear_channel_rev` | 0 | 225 | 2 | 0.9% |
| `order_flow_imbalance_v2` | 0 | 532 | 4 | 0.7% |
| `positional_scaling` | 0 | 267 | 2 | 0.7% |
| `cmf` | 0 | 536 | 4 | 0.7% |
| `momentum_quality` | 0 | 562 | 4 | 0.7% |
| `roc_ma_cross` | 0 | 289 | 2 | 0.7% |
| `price_action_momentum` | 0 | 582 | 4 | 0.7% |

## 포트폴리오 가상 배분

- **전체 20개 균등배분**: -3.18% -> $9,682
- **Top 5 균등배분**: +1.98% -> $10,198


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-22T10:20:50.642888Z_
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
| 평균 수익률 | -2.82% |
| 최고 수익률 | 3.95% (volatility_cluster) |
| 최저 수익률 | -9.36% (volume_breakout) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `volatility_cluster` | +3.95% | 0.82 | 40.6% | 1.24 | 42 | 8.2% | 0/8 | FAIL |
| 2 | `momentum_quality` | +1.88% | 0.30 | 36.1% | 1.08 | 60 | 10.3% | 0/8 | FAIL |
| 3 | `engulfing_zone` | +1.38% | 0.04 | 37.4% | 1.16 | 25 | 8.0% | 1/8 | FAIL |
| 4 | `price_action_momentum` | +1.17% | 0.23 | 37.4% | 1.12 | 43 | 9.8% | 1/8 | FAIL |
| 5 | `narrow_range` | +0.73% | -0.11 | 37.5% | 1.07 | 40 | 10.7% | 1/8 | FAIL |
| 6 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 7 | `cmf` | -0.38% | -0.38 | 32.5% | 1.01 | 48 | 12.1% | 1/8 | FAIL |
| 8 | `dema_cross` | -0.54% | -0.54 | 39.6% | 1.07 | 12 | 4.2% | 0/8 | FAIL |
| 9 | `elder_impulse` | -1.78% | -0.74 | 34.9% | 0.98 | 39 | 10.0% | 1/8 | FAIL |
| 10 | `htf_ema` | -3.26% | -1.05 | 34.2% | 0.84 | 26 | 8.5% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 68.5 | p100 | 0.23 | 1.76 | 1.12 | 43 | 9.8% | 1/8 | FAIL |
| 2 | `volatility_cluster` | 66.2 | p94 | 0.82 | 1.81 | 1.24 | 42 | 8.2% | 0/8 | FAIL |
| 3 | `momentum_quality` | 65.9 | p89 | 0.30 | 1.37 | 1.08 | 60 | 10.3% | 0/8 | FAIL |
| 4 | `narrow_range` | 62.7 | p84 | -0.11 | 2.15 | 1.07 | 40 | 10.7% | 1/8 | FAIL |
| 5 | `engulfing_zone` | 61.1 | p78 | 0.04 | 2.15 | 1.16 | 25 | 8.0% | 1/8 | FAIL |
| 6 | `cmf` | 60.6 | p73 | -0.38 | 2.23 | 1.01 | 48 | 12.1% | 1/8 | FAIL |
| 7 | `relative_volume` | 55.6 | p68 | -0.97 | 2.77 | 0.95 | 58 | 12.7% | 1/8 | FAIL |
| 8 | `elder_impulse` | 54.7 | p63 | -0.74 | 2.48 | 0.98 | 39 | 10.0% | 1/8 | FAIL |
| 9 | `lob_maker` | 48.2 | p57 | -0.98 | 1.04 | 0.88 | 59 | 15.4% | 0/8 | FAIL |
| 10 | `dema_cross` | 40.1 | p52 | -0.54 | 2.23 | 1.07 | 12 | 4.2% | 0/8 | FAIL |
| 11 | `order_flow_imbalance_v2` | 39.8 | p47 | -1.51 | 1.84 | 0.83 | 60 | 16.0% | 0/8 | FAIL |
| 12 | `htf_ema` | 37.1 | p42 | -1.05 | 1.59 | 0.84 | 26 | 8.5% | 0/8 | FAIL |
| 13 | `volume_breakout` | 35.0 | p36 | -1.91 | 2.37 | 0.81 | 69 | 18.0% | 0/8 | FAIL |
| 14 | `linear_channel_rev` | 34.4 | p31 | -1.29 | 1.69 | 0.80 | 26 | 7.6% | 0/8 | FAIL |
| 15 | `frama` | 33.7 | p26 | -1.69 | 1.69 | 0.77 | 41 | 13.3% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `volatility_cluster` | +3.95% | 0.82 | 1.24 | 42 | 0/8 | FAIL |
| `momentum_quality` | +1.88% | 0.30 | 1.08 | 60 | 0/8 | FAIL |
| `engulfing_zone` | +1.38% | 0.04 | 1.16 | 25 | 1/8 | FAIL |
| `price_action_momentum` | +1.17% | 0.23 | 1.12 | 43 | 1/8 | FAIL |
| `narrow_range` | +0.73% | -0.11 | 1.07 | 40 | 1/8 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `cmf` | -0.38% | -0.38 | 1.01 | 48 | 1/8 | FAIL |
| `dema_cross` | -0.54% | -0.54 | 1.07 | 12 | 0/8 | FAIL |
| `elder_impulse` | -1.78% | -0.74 | 0.98 | 39 | 1/8 | FAIL |
| `htf_ema` | -3.26% | -1.05 | 0.84 | 26 | 0/8 | FAIL |
| `relative_volume` | -3.34% | -0.97 | 0.95 | 58 | 1/8 | FAIL |
| `linear_channel_rev` | -3.55% | -1.29 | 0.80 | 26 | 0/8 | FAIL |
| `acceleration_band` | -4.40% | -2.52 | 0.55 | 11 | 0/8 | FAIL |
| `price_cluster` | -4.84% | -1.49 | 0.80 | 25 | 0/8 | FAIL |
| `positional_scaling` | -6.11% | -2.04 | 0.69 | 31 | 0/8 | FAIL |
| `lob_maker` | -6.21% | -0.98 | 0.88 | 59 | 0/8 | FAIL |
| `roc_ma_cross` | -6.31% | -2.10 | 0.70 | 32 | 0/8 | FAIL |
| `frama` | -7.37% | -1.69 | 0.77 | 41 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -8.01% | -1.51 | 0.83 | 60 | 0/8 | FAIL |
| `volume_breakout` | -9.36% | -1.91 | 0.81 | 69 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `volatility_cluster` | profit_factor 1.47 < 1.5 (x2), mc_p_value 0.136 > 0.1 (우연 가능성) (x2), sharpe 0.33 < 1.0 (x1) |
| `momentum_quality` | sharpe -0.34 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1), mc_p_value 0.586 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -2.70 < 1.0 (x1), profit_factor 0.53 < 1.5 (x1), mc_p_value 0.897 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe -2.85 < 1.0 (x1), profit_factor 0.61 < 1.5 (x1), mc_p_value 0.916 > 0.1 (우연 가능성) (x1) |
| `narrow_range` | sharpe -1.31 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1), mc_p_value 0.719 > 0.1 (우연 가능성) (x1) |
| `wick_reversal` | no trades generated (x8) |
| `cmf` | profit_factor 0.76 < 1.5 (x2), mc_p_value 0.779 > 0.1 (우연 가능성) (x2), sharpe -1.05 < 1.0 (x1) |
| `dema_cross` | trades 9 < 15 (x2), trades 11 < 15 (x2), sharpe -1.09 < 1.0 (x1) |
| `elder_impulse` | profit_factor 0.72 < 1.5 (x2), sharpe 0.36 < 1.0 (x1), profit_factor 1.07 < 1.5 (x1) |
| `htf_ema` | sharpe -2.49 < 1.0 (x1), profit_factor 0.62 < 1.5 (x1), mc_p_value 0.891 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | sharpe -1.53 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1), mc_p_value 0.766 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -1.17 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1), mc_p_value 0.702 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | trades 6 < 15 (x2), trades 14 < 15 (x2), sharpe -4.56 < 1.0 (x1) |
| `price_cluster` | sharpe -4.04 < 1.0 (x1), profit_factor 0.43 < 1.5 (x1), mc_p_value 0.976 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 0.46 < 1.5 (x2), sharpe -3.38 < 1.0 (x1), profit_factor 0.49 < 1.5 (x1) |
| `lob_maker` | sharpe -2.01 < 1.0 (x1), profit_factor 0.75 < 1.5 (x1), mc_p_value 0.866 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -2.94 < 1.0 (x1), profit_factor 0.54 < 1.5 (x1), mc_p_value 0.934 > 0.1 (우연 가능성) (x1) |
| `frama` | profit_factor 0.99 < 1.5 (x2), sharpe -2.05 < 1.0 (x1), profit_factor 0.69 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe -0.74 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.637 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -1.60 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1), mc_p_value 0.765 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 8 |
| profit_factor 0.93 < 1.5 | 5 |
| profit_factor 0.72 < 1.5 | 5 |
| profit_factor 0.79 < 1.5 | 3 |
| profit_factor 1.02 < 1.5 | 3 |
| profit_factor 0.89 < 1.5 | 3 |
| profit_factor 0.75 < 1.5 | 3 |
| profit_factor 0.81 < 1.5 | 3 |
| profit_factor 0.49 < 1.5 | 3 |
| trades 9 < 15 | 3 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `volume_breakout` | 181 | 119 | 0.66 |
| `cmf` | 120 | 62 | 0.52 |
| `order_flow_imbalance_v2` | 151 | 62 | 0.41 |
| `lob_maker` | 151 | 56 | 0.37 |
| `relative_volume` | 144 | 48 | 0.33 |
| `roc_ma_cross` | 85 | 47 | 0.55 |
| `positional_scaling` | 81 | 45 | 0.56 |
| `narrow_range` | 90 | 44 | 0.49 |
| `momentum_quality` | 155 | 42 | 0.27 |
| `frama` | 111 | 42 | 0.38 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 5 | 94 | 94.9% |
| `frama` | 0 | 95 | 236 | 71.3% |
| `elder_impulse` | 0 | 133 | 181 | 57.6% |
| `engulfing_zone` | 0 | 87 | 115 | 56.9% |
| `relative_volume` | 0 | 202 | 261 | 56.4% |
| `roc_ma_cross` | 0 | 118 | 137 | 53.7% |
| `positional_scaling` | 0 | 116 | 134 | 53.6% |
| `lob_maker` | 0 | 227 | 247 | 52.1% |
| `volume_breakout` | 0 | 265 | 286 | 51.9% |
| `order_flow_imbalance_v2` | 0 | 231 | 245 | 51.5% |

## 포트폴리오 가상 배분

- **전체 20개 균등배분**: -2.82% -> $9,718
- **Top 5 균등배분**: +1.82% -> $10,182


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-22T10:24:37.180120Z_
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
| 평균 수익률 | -4.70% |
| 최고 수익률 | 0.37% (elder_impulse) |
| 최저 수익률 | -13.66% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `elder_impulse` | +0.37% | 0.07 | 35.8% | 1.02 | 39 | 9.0% | 0/8 | FAIL |
| 2 | `acceleration_band` | +0.10% | -0.34 | 33.6% | 1.38 | 7 | 3.5% | 0/8 | FAIL |
| 3 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 4 | `momentum_quality` | -0.31% | -0.17 | 34.1% | 1.00 | 58 | 11.0% | 0/8 | FAIL |
| 5 | `htf_ema` | -1.36% | -0.50 | 33.8% | 0.97 | 32 | 8.8% | 0/8 | FAIL |
| 6 | `volume_breakout` | -1.69% | -0.74 | 31.8% | 0.99 | 50 | 11.5% | 2/8 | FAIL |
| 7 | `order_flow_imbalance_v2` | -1.94% | -0.37 | 33.8% | 0.96 | 59 | 11.4% | 0/8 | FAIL |
| 8 | `volatility_cluster` | -3.38% | -0.96 | 31.6% | 0.85 | 39 | 9.2% | 0/8 | FAIL |
| 9 | `linear_channel_rev` | -3.88% | -1.32 | 29.0% | 0.77 | 26 | 6.8% | 0/8 | FAIL |
| 10 | `dema_cross` | -3.88% | -1.64 | 33.7% | 0.73 | 22 | 8.2% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 66.2 | p100 | -0.17 | 1.66 | 1.00 | 58 | 11.0% | 0/8 | FAIL |
| 2 | `order_flow_imbalance_v2` | 64.5 | p94 | -0.37 | 1.38 | 0.96 | 59 | 11.4% | 0/8 | FAIL |
| 3 | `elder_impulse` | 63.8 | p89 | 0.07 | 0.92 | 1.02 | 39 | 9.0% | 0/8 | FAIL |
| 4 | `volume_breakout` | 63.0 | p84 | -0.74 | 2.85 | 0.99 | 50 | 11.5% | 2/8 | FAIL |
| 5 | `htf_ema` | 52.1 | p78 | -0.50 | 1.80 | 0.97 | 32 | 8.8% | 0/8 | FAIL |
| 6 | `volatility_cluster` | 50.1 | p73 | -0.96 | 1.09 | 0.85 | 39 | 9.2% | 0/8 | FAIL |
| 7 | `acceleration_band` | 49.3 | p68 | -0.34 | 2.04 | 1.38 | 7 | 3.5% | 0/8 | FAIL |
| 8 | `price_action_momentum` | 44.8 | p63 | -1.56 | 2.51 | 0.84 | 40 | 11.8% | 1/8 | FAIL |
| 9 | `narrow_range` | 42.1 | p57 | -1.47 | 1.14 | 0.77 | 37 | 10.6% | 0/8 | FAIL |
| 10 | `linear_channel_rev` | 40.2 | p52 | -1.32 | 1.00 | 0.77 | 26 | 6.8% | 0/8 | FAIL |
| 11 | `relative_volume` | 38.7 | p47 | -2.36 | 1.28 | 0.72 | 60 | 14.5% | 0/8 | FAIL |
| 12 | `roc_ma_cross` | 37.7 | p42 | -1.52 | 1.53 | 0.75 | 28 | 8.3% | 0/8 | FAIL |
| 13 | `price_cluster` | 34.3 | p36 | -1.50 | 1.46 | 0.71 | 21 | 7.1% | 0/8 | FAIL |
| 14 | `frama` | 34.3 | p31 | -2.31 | 1.62 | 0.70 | 50 | 14.4% | 0/8 | FAIL |
| 15 | `dema_cross` | 33.0 | p26 | -1.64 | 1.86 | 0.73 | 22 | 8.2% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `elder_impulse` | +0.37% | 0.07 | 1.02 | 39 | 0/8 | FAIL |
| `acceleration_band` | +0.10% | -0.34 | 1.38 | 7 | 0/8 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `momentum_quality` | -0.31% | -0.17 | 1.00 | 58 | 0/8 | FAIL |
| `htf_ema` | -1.36% | -0.50 | 0.97 | 32 | 0/8 | FAIL |
| `volume_breakout` | -1.69% | -0.74 | 0.99 | 50 | 2/8 | FAIL |
| `order_flow_imbalance_v2` | -1.94% | -0.37 | 0.96 | 59 | 0/8 | FAIL |
| `volatility_cluster` | -3.38% | -0.96 | 0.85 | 39 | 0/8 | FAIL |
| `linear_channel_rev` | -3.88% | -1.32 | 0.77 | 26 | 0/8 | FAIL |
| `dema_cross` | -3.88% | -1.64 | 0.73 | 22 | 0/8 | FAIL |
| `price_cluster` | -4.03% | -1.50 | 0.71 | 21 | 0/8 | FAIL |
| `roc_ma_cross` | -4.24% | -1.52 | 0.75 | 28 | 0/8 | FAIL |
| `price_action_momentum` | -4.86% | -1.56 | 0.84 | 40 | 1/8 | FAIL |
| `narrow_range` | -5.46% | -1.47 | 0.77 | 37 | 0/8 | FAIL |
| `engulfing_zone` | -6.47% | -2.48 | 0.71 | 24 | 1/8 | FAIL |
| `positional_scaling` | -8.55% | -2.86 | 0.58 | 31 | 0/8 | FAIL |
| `cmf` | -9.84% | -2.55 | 0.68 | 46 | 0/8 | FAIL |
| `relative_volume` | -10.20% | -2.36 | 0.72 | 60 | 0/8 | FAIL |
| `frama` | -10.80% | -2.31 | 0.70 | 50 | 0/8 | FAIL |
| `lob_maker` | -13.66% | -2.62 | 0.70 | 58 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `elder_impulse` | sharpe -0.76 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1), mc_p_value 0.642 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | trades 7 < 15 (x4), trades 8 < 15 (x2), trades 6 < 15 (x2) |
| `wick_reversal` | no trades generated (x8) |
| `momentum_quality` | sharpe -2.10 < 1.0 (x1), profit_factor 0.73 < 1.5 (x1), mc_p_value 0.847 > 0.1 (우연 가능성) (x1) |
| `htf_ema` | sharpe -3.39 < 1.0 (x1), profit_factor 0.51 < 1.5 (x1), mc_p_value 0.956 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -5.26 < 1.0 (x1), max_drawdown 21.4% > 20% (x1), profit_factor 0.45 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe -2.74 < 1.0 (x1), profit_factor 0.67 < 1.5 (x1), mc_p_value 0.905 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -0.32 < 1.0 (x1), profit_factor 0.94 < 1.5 (x1), mc_p_value 0.574 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -2.39 < 1.0 (x1), profit_factor 0.58 < 1.5 (x1), mc_p_value 0.898 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | sharpe -0.83 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1), mc_p_value 0.656 > 0.1 (우연 가능성) (x1) |
| `price_cluster` | sharpe -0.81 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1), mc_p_value 0.651 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -3.81 < 1.0 (x1), profit_factor 0.42 < 1.5 (x1), mc_p_value 0.971 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | profit_factor 0.48 < 1.5 (x2), sharpe -4.61 < 1.0 (x1), profit_factor 0.46 < 1.5 (x1) |
| `narrow_range` | sharpe -1.86 < 1.0 (x1), profit_factor 0.72 < 1.5 (x1), mc_p_value 0.826 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | profit_factor 0.36 < 1.5 (x2), sharpe -4.03 < 1.0 (x1), mc_p_value 0.979 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | sharpe -3.65 < 1.0 (x1), profit_factor 0.46 < 1.5 (x1), mc_p_value 0.969 > 0.1 (우연 가능성) (x1) |
| `cmf` | sharpe -6.75 < 1.0 (x1), max_drawdown 21.4% > 20% (x1), profit_factor 0.31 < 1.5 (x1) |
| `relative_volume` | profit_factor 0.72 < 1.5 (x2), sharpe -4.67 < 1.0 (x1), profit_factor 0.51 < 1.5 (x1) |
| `frama` | sharpe -2.49 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1), mc_p_value 0.898 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | sharpe -4.90 < 1.0 (x1), max_drawdown 24.5% > 20% (x1), profit_factor 0.49 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 8 |
| profit_factor 0.72 < 1.5 | 5 |
| profit_factor 0.51 < 1.5 | 5 |
| profit_factor 0.75 < 1.5 | 4 |
| trades 7 < 15 | 4 |
| profit_factor 0.76 < 1.5 | 4 |
| profit_factor 0.77 < 1.5 | 4 |
| profit_factor 0.55 < 1.5 | 3 |
| profit_factor 0.73 < 1.5 | 3 |
| sharpe -0.09 < 1.0 | 3 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `relative_volume` | 164 | 77 | 0.47 |
| `lob_maker` | 157 | 76 | 0.48 |
| `volume_breakout` | 127 | 72 | 0.57 |
| `order_flow_imbalance_v2` | 151 | 67 | 0.44 |
| `momentum_quality` | 146 | 64 | 0.44 |
| `cmf` | 125 | 63 | 0.50 |
| `volatility_cluster` | 89 | 49 | 0.55 |
| `frama` | 140 | 46 | 0.33 |
| `positional_scaling` | 89 | 43 | 0.48 |
| `elder_impulse` | 83 | 39 | 0.47 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 6 | 174 | 96.7% |
| `frama` | 0 | 57 | 346 | 85.9% |
| `engulfing_zone` | 0 | 32 | 162 | 83.5% |
| `cmf` | 0 | 71 | 299 | 80.8% |
| `roc_ma_cross` | 0 | 44 | 184 | 80.7% |
| `elder_impulse` | 0 | 61 | 252 | 80.5% |
| `order_flow_imbalance_v2` | 0 | 93 | 378 | 80.3% |
| `relative_volume` | 0 | 95 | 384 | 80.2% |
| `linear_channel_rev` | 0 | 44 | 165 | 78.9% |
| `lob_maker` | 0 | 104 | 360 | 77.6% |

## 포트폴리오 가상 배분

- **전체 20개 균등배분**: -4.70% -> $9,530
- **Top 5 균등배분**: -0.24% -> $9,976
