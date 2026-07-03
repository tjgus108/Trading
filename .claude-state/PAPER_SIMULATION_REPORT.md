# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-07-03T10:25:05.275381Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-07-03T10:31:23.512852Z_
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
| 테스트 전략 | 19개 |
| PASS (일관성 50%+) | 1개 |
| FAIL | 18개 |
| 평균 수익률 | -2.32% |
| 최고 수익률 | 6.71% (price_cluster) |
| 최저 수익률 | -8.04% (volatility_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +6.71% | 0.95 | 38.3% | 1.33 | 34 | 8.9% | 2/8 | FAIL |
| 2 | `roc_ma_cross` | +6.54% | 1.81 | 46.0% | 2.02 | 14 | 3.4% | 4/8 | PASS |
| 3 | `dema_cross` | +3.08% | 0.85 | 39.4% | 1.38 | 26 | 6.1% | 2/8 | FAIL |
| 4 | `frama` | +1.60% | 0.24 | 35.2% | 1.12 | 40 | 9.4% | 1/8 | FAIL |
| 5 | `positional_scaling` | +0.27% | -0.38 | 33.7% | 1.09 | 34 | 9.2% | 1/8 | FAIL |
| 6 | `lob_maker` | +0.15% | -0.04 | 35.0% | 1.05 | 75 | 17.0% | 0/8 | FAIL |
| 7 | `narrow_range` | -2.27% | -0.51 | 33.5% | 0.97 | 46 | 10.1% | 0/8 | FAIL |
| 8 | `acceleration_band` | -3.18% | -0.94 | 32.0% | 0.98 | 44 | 13.0% | 1/8 | FAIL |
| 9 | `volume_breakout` | -3.33% | -0.74 | 32.5% | 0.96 | 72 | 15.4% | 0/8 | FAIL |
| 10 | `momentum_quality` | -3.34% | -1.19 | 31.5% | 0.96 | 71 | 15.8% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `roc_ma_cross` | 63.9 | p100 | 1.81 | 1.90 | 2.02 | 14 | 3.4% | 4/8 | PASS |
| 2 | `price_cluster` | 49.8 | p94 | 0.95 | 2.20 | 1.33 | 34 | 8.9% | 2/8 | FAIL |
| 3 | `dema_cross` | 48.2 | p88 | 0.85 | 1.85 | 1.38 | 26 | 6.1% | 2/8 | FAIL |
| 4 | `lob_maker` | 43.6 | p83 | -0.04 | 1.99 | 1.05 | 75 | 17.0% | 0/8 | FAIL |
| 5 | `frama` | 43.4 | p77 | 0.24 | 1.60 | 1.12 | 40 | 9.4% | 1/8 | FAIL |
| 6 | `volume_breakout` | 37.6 | p72 | -0.74 | 2.18 | 0.96 | 72 | 15.4% | 0/8 | FAIL |
| 7 | `order_flow_imbalance_v2` | 36.5 | p66 | -0.77 | 2.05 | 0.95 | 67 | 15.0% | 0/8 | FAIL |
| 8 | `relative_volume` | 36.5 | p61 | -0.99 | 1.72 | 0.92 | 64 | 13.2% | 0/8 | FAIL |
| 9 | `narrow_range` | 35.8 | p55 | -0.51 | 1.48 | 0.97 | 46 | 10.1% | 0/8 | FAIL |
| 10 | `price_action_momentum` | 34.7 | p50 | -1.08 | 2.79 | 0.97 | 73 | 16.7% | 1/8 | FAIL |
| 11 | `cmf` | 34.0 | p44 | -1.23 | 1.29 | 0.88 | 68 | 16.3% | 0/8 | FAIL |
| 12 | `positional_scaling` | 33.8 | p38 | -0.38 | 2.82 | 1.09 | 34 | 9.2% | 1/8 | FAIL |
| 13 | `htf_ema` | 33.4 | p33 | -0.72 | 0.71 | 0.91 | 43 | 11.2% | 0/8 | FAIL |
| 14 | `momentum_quality` | 32.2 | p27 | -1.19 | 3.29 | 0.96 | 71 | 15.8% | 1/8 | FAIL |
| 15 | `acceleration_band` | 30.4 | p22 | -0.94 | 2.58 | 0.98 | 44 | 13.0% | 1/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +6.71% | 0.95 | 1.33 | 34 | 2/8 | FAIL |
| `roc_ma_cross` | +6.54% | 1.81 | 2.02 | 14 | 4/8 | PASS |
| `dema_cross` | +3.08% | 0.85 | 1.38 | 26 | 2/8 | FAIL |
| `frama` | +1.60% | 0.24 | 1.12 | 40 | 1/8 | FAIL |
| `positional_scaling` | +0.27% | -0.38 | 1.09 | 34 | 1/8 | FAIL |
| `lob_maker` | +0.15% | -0.04 | 1.05 | 75 | 0/8 | FAIL |
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

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_cluster` | sharpe -1.61 < 1.0 (x1), profit_factor 0.75 < 1.5 (x1), mc_p_value 0.768 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | sharpe 0.63 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.366 > 0.1 (우연 가능성) (x1) |
| `frama` | sharpe -0.87 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1), mc_p_value 0.603 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.163 > 0.1 (우연 가능성) (x1), sharpe -1.16 < 1.0 (x1) |
| `lob_maker` | sharpe -2.32 < 1.0 (x1), max_drawdown 27.9% > 20% (x1), profit_factor 0.79 < 1.5 (x1) |
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

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.74 < 1.5 | 5 |
| profit_factor 1.03 < 1.5 | 4 |
| profit_factor 0.83 < 1.5 | 4 |
| profit_factor 0.91 < 1.5 | 4 |
| profit_factor 1.06 < 1.5 | 4 |
| profit_factor 0.75 < 1.5 | 3 |
| profit_factor 0.80 < 1.5 | 3 |
| profit_factor 0.72 < 1.5 | 3 |
| profit_factor 0.57 < 1.5 | 3 |
| profit_factor 0.87 < 1.5 | 3 |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `momentum_quality` | 173 | 89 | 0.51 |
| `volatility_cluster` | 137 | 77 | 0.56 |
| `volume_breakout` | 188 | 73 | 0.39 |
| `linear_channel_rev` | 57 | 72 | 1.26 |
| `price_action_momentum` | 188 | 62 | 0.33 |
| `elder_impulse` | 107 | 61 | 0.57 |
| `cmf` | 189 | 57 | 0.30 |
| `lob_maker` | 198 | 55 | 0.28 |
| `acceleration_band` | 106 | 52 | 0.49 |
| `relative_volume` | 180 | 46 | 0.26 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `relative_volume` | 0 | 507 | 8 | 1.6% |
| `dema_cross` | 0 | 207 | 2 | 1.0% |
| `linear_channel_rev` | 0 | 225 | 2 | 0.9% |
| `price_cluster` | 0 | 266 | 2 | 0.7% |
| `order_flow_imbalance_v2` | 0 | 532 | 4 | 0.7% |
| `positional_scaling` | 0 | 267 | 2 | 0.7% |
| `cmf` | 0 | 536 | 4 | 0.7% |
| `momentum_quality` | 0 | 562 | 4 | 0.7% |
| `price_action_momentum` | 0 | 582 | 4 | 0.7% |
| `frama` | 0 | 321 | 2 | 0.6% |

## 포트폴리오 가상 배분

- **전체 19개 균등배분**: -2.32% -> $9,768
- **PASS 1개 균등배분**: +6.54% -> $10,654
- **Top 5 균등배분**: +3.64% -> $10,364
