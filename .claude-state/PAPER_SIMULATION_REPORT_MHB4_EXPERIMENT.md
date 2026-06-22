# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-22T10:35:24.702670Z_
_Symbols: BTC/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-22T10:39:18.926402Z_
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
| 평균 수익률 | -1.99% |
| 최고 수익률 | 5.29% (roc_ma_cross) |
| 최저 수익률 | -7.95% (volatility_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `roc_ma_cross` | +5.29% | 0.99 | 38.3% | 1.34 | 34 | 6.5% | 2/8 | FAIL |
| 2 | `lob_maker` | +4.12% | 0.63 | 36.1% | 1.14 | 61 | 13.0% | 0/8 | FAIL |
| 3 | `price_action_momentum` | +2.27% | 0.37 | 35.8% | 1.11 | 60 | 10.9% | 1/8 | FAIL |
| 4 | `price_cluster` | +1.82% | 0.27 | 34.7% | 1.11 | 36 | 9.9% | 1/8 | FAIL |
| 5 | `frama` | +1.69% | 0.22 | 35.1% | 1.14 | 37 | 8.6% | 1/8 | FAIL |
| 6 | `relative_volume` | -0.30% | -0.10 | 34.0% | 1.03 | 51 | 9.1% | 0/8 | FAIL |
| 7 | `positional_scaling` | -0.36% | -0.72 | 32.3% | 1.05 | 31 | 9.6% | 1/8 | FAIL |
| 8 | `narrow_range` | -1.87% | -0.42 | 34.6% | 0.97 | 39 | 9.3% | 0/8 | FAIL |
| 9 | `dema_cross` | -1.98% | -2.64 | 9.4% | 0.12 | 2 | 2.1% | 0/8 | FAIL |
| 10 | `momentum_quality` | -2.37% | -0.66 | 31.5% | 0.99 | 60 | 13.1% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `roc_ma_cross` | 75.5 | p100 | 0.99 | 2.04 | 1.34 | 34 | 6.5% | 2/8 | FAIL |
| 2 | `price_action_momentum` | 70.5 | p94 | 0.37 | 1.56 | 1.11 | 60 | 10.9% | 1/8 | FAIL |
| 3 | `lob_maker` | 67.2 | p89 | 0.63 | 1.26 | 1.14 | 61 | 13.0% | 0/8 | FAIL |
| 4 | `frama` | 61.3 | p84 | 0.22 | 1.78 | 1.14 | 37 | 8.6% | 1/8 | FAIL |
| 5 | `price_cluster` | 61.0 | p78 | 0.27 | 1.40 | 1.11 | 36 | 9.9% | 1/8 | FAIL |
| 6 | `relative_volume` | 59.1 | p73 | -0.10 | 1.46 | 1.03 | 51 | 9.1% | 0/8 | FAIL |
| 7 | `momentum_quality` | 54.2 | p68 | -0.66 | 2.30 | 0.99 | 60 | 13.1% | 1/8 | FAIL |
| 8 | `order_flow_imbalance_v2` | 54.0 | p63 | -0.44 | 1.26 | 0.97 | 56 | 12.6% | 0/8 | FAIL |
| 9 | `htf_ema` | 52.1 | p57 | -0.41 | 0.69 | 0.96 | 41 | 10.0% | 0/8 | FAIL |
| 10 | `narrow_range` | 50.2 | p52 | -0.42 | 1.20 | 0.97 | 39 | 9.3% | 0/8 | FAIL |
| 11 | `volume_breakout` | 47.1 | p47 | -0.77 | 2.11 | 0.96 | 57 | 13.6% | 0/8 | FAIL |
| 12 | `positional_scaling` | 46.2 | p42 | -0.72 | 2.95 | 1.05 | 31 | 9.6% | 1/8 | FAIL |
| 13 | `cmf` | 43.6 | p36 | -1.31 | 1.31 | 0.86 | 56 | 13.8% | 0/8 | FAIL |
| 14 | `acceleration_band` | 43.3 | p31 | -1.06 | 2.62 | 0.97 | 38 | 12.4% | 1/8 | FAIL |
| 15 | `elder_impulse` | 36.6 | p26 | -1.29 | 1.64 | 0.83 | 36 | 11.6% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `roc_ma_cross` | +5.29% | 0.99 | 1.34 | 34 | 2/8 | FAIL |
| `lob_maker` | +4.12% | 0.63 | 1.14 | 61 | 0/8 | FAIL |
| `price_action_momentum` | +2.27% | 0.37 | 1.11 | 60 | 1/8 | FAIL |
| `price_cluster` | +1.82% | 0.27 | 1.11 | 36 | 1/8 | FAIL |
| `frama` | +1.69% | 0.22 | 1.14 | 37 | 1/8 | FAIL |
| `relative_volume` | -0.30% | -0.10 | 1.03 | 51 | 0/8 | FAIL |
| `positional_scaling` | -0.36% | -0.72 | 1.05 | 31 | 1/8 | FAIL |
| `narrow_range` | -1.87% | -0.42 | 0.97 | 39 | 0/8 | FAIL |
| `dema_cross` | -1.98% | -2.64 | 0.12 | 2 | 0/8 | FAIL |
| `momentum_quality` | -2.37% | -0.66 | 0.99 | 60 | 1/8 | FAIL |
| `htf_ema` | -2.49% | -0.41 | 0.96 | 41 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -2.63% | -0.44 | 0.97 | 56 | 0/8 | FAIL |
| `volume_breakout` | -3.28% | -0.77 | 0.96 | 57 | 0/8 | FAIL |
| `acceleration_band` | -3.78% | -1.06 | 0.97 | 38 | 1/8 | FAIL |
| `linear_channel_rev` | -4.22% | -2.13 | 0.73 | 25 | 0/8 | FAIL |
| `elder_impulse` | -4.58% | -1.29 | 0.83 | 36 | 0/8 | FAIL |
| `engulfing_zone` | -5.11% | -1.32 | 0.77 | 24 | 0/8 | FAIL |
| `wick_reversal` | -6.69% | -2.14 | 0.74 | 36 | 0/8 | FAIL |
| `cmf` | -7.37% | -1.31 | 0.86 | 56 | 0/8 | FAIL |
| `volatility_cluster` | -7.95% | -2.07 | 0.78 | 47 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `roc_ma_cross` | sharpe 0.64 < 1.0 (x1), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.345 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | sharpe 0.66 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1), mc_p_value 0.366 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.224 > 0.1 (우연 가능성) (x1), sharpe 0.06 < 1.0 (x1) |
| `price_cluster` | sharpe -0.14 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1), mc_p_value 0.527 > 0.1 (우연 가능성) (x1) |
| `frama` | sharpe 0.53 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.390 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | sharpe 0.59 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1), mc_p_value 0.362 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 1.48 < 1.5 (x2), mc_p_value 0.167 > 0.1 (우연 가능성) (x1), sharpe -2.69 < 1.0 (x1) |
| `narrow_range` | sharpe -0.06 < 1.0 (x1), profit_factor 1.02 < 1.5 (x1), mc_p_value 0.490 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x6), trades 2 < 15 (x4), trades 4 < 15 (x2) |
| `momentum_quality` | profit_factor 1.23 < 1.5 (x1), mc_p_value 0.228 > 0.1 (우연 가능성) (x1), sharpe -0.70 < 1.0 (x1) |
| `htf_ema` | profit_factor 1.12 < 1.5 (x2), sharpe -0.29 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe -0.08 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1), mc_p_value 0.500 > 0.1 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -0.75 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1), mc_p_value 0.552 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | mc_p_value 0.114 > 0.1 (우연 가능성) (x1), sharpe -0.71 < 1.0 (x1), profit_factor 0.90 < 1.5 (x1) |
| `linear_channel_rev` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.233 > 0.1 (우연 가능성) (x1), sharpe -3.02 < 1.0 (x1) |
| `elder_impulse` | sharpe -0.60 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1), mc_p_value 0.570 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -1.54 < 1.0 (x1), profit_factor 0.73 < 1.5 (x1), mc_p_value 0.732 > 0.1 (우연 가능성) (x1) |
| `wick_reversal` | sharpe -2.35 < 1.0 (x1), profit_factor 0.68 < 1.5 (x1), mc_p_value 0.859 > 0.1 (우연 가능성) (x1) |
| `cmf` | sharpe -1.48 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1), mc_p_value 0.715 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -1.23 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.694 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.00 < 1.5 | 6 |
| profit_factor 1.12 < 1.5 | 5 |
| profit_factor 0.89 < 1.5 | 4 |
| profit_factor 0.85 < 1.5 | 4 |
| profit_factor 0.77 < 1.5 | 4 |
| profit_factor 0.84 < 1.5 | 4 |
| trades 2 < 15 | 4 |
| profit_factor 0.93 < 1.5 | 4 |
| profit_factor 1.08 < 1.5 | 3 |
| profit_factor 1.17 < 1.5 | 3 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `momentum_quality` | 150 | 79 | 0.53 |
| `wick_reversal` | 87 | 74 | 0.85 |
| `volume_breakout` | 154 | 61 | 0.40 |
| `linear_channel_rev` | 51 | 59 | 1.16 |
| `volatility_cluster` | 127 | 56 | 0.44 |
| `elder_impulse` | 104 | 49 | 0.47 |
| `lob_maker` | 150 | 44 | 0.29 |
| `cmf` | 161 | 43 | 0.27 |
| `htf_ema` | 104 | 41 | 0.39 |
| `relative_volume` | 125 | 40 | 0.32 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 18 | 2 | 10.0% |
| `price_cluster` | 0 | 285 | 4 | 1.4% |
| `order_flow_imbalance_v2` | 0 | 438 | 6 | 1.4% |
| `linear_channel_rev` | 0 | 201 | 2 | 1.0% |
| `relative_volume` | 0 | 406 | 4 | 1.0% |
| `cmf` | 0 | 445 | 4 | 0.9% |
| `momentum_quality` | 0 | 477 | 4 | 0.8% |
| `positional_scaling` | 0 | 246 | 2 | 0.8% |
| `roc_ma_cross` | 0 | 267 | 2 | 0.7% |
| `htf_ema` | 0 | 327 | 2 | 0.6% |

## 포트폴리오 가상 배분

- **전체 20개 균등배분**: -1.99% -> $9,801
- **Top 5 균등배분**: +3.04% -> $10,304
