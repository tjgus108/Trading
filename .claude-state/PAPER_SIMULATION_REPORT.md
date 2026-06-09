# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-09T15:16:26.307839Z_
_Symbols: BTC/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-09T15:18:08.468403Z_
_Symbol: BTC/USDT_
_Data Source: CSV BTC/USDT 4h (resampled from 1h) (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 20:00:00+00:00 (499일)_
_Walk-Forward: 8개 윈도우 (train=1260, test=360 candles [4h])_
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
| 평균 수익률 | 0.29% |
| 최고 수익률 | 4.86% (price_cluster) |
| 최저 수익률 | -5.18% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +4.86% | 2.51 | 50.2% | 2.43 | 10 | 4.8% | 0/8 | FAIL |
| 2 | `supertrend_multi` | +4.15% | 2.14 | 30.4% | 1.22 | 8 | 2.6% | 1/8 | FAIL |
| 3 | `cmf` | +3.21% | 1.25 | 41.8% | 1.24 | 23 | 6.3% | 1/8 | FAIL |
| 4 | `lob_maker` | +2.96% | 1.18 | 40.4% | 1.32 | 21 | 6.8% | 1/8 | FAIL |
| 5 | `momentum_quality` | +2.94% | 1.47 | 40.0% | 1.25 | 20 | 4.5% | 0/8 | FAIL |
| 6 | `value_area` | +2.01% | 1.47 | 44.7% | 1.42 | 12 | 3.0% | 0/8 | FAIL |
| 7 | `linear_channel_rev` | +1.98% | 1.39 | 43.6% | 2.12 | 6 | 2.2% | 0/8 | FAIL |
| 8 | `order_flow_imbalance_v2` | +1.66% | 0.26 | 40.0% | 1.34 | 20 | 7.1% | 0/8 | FAIL |
| 9 | `relative_volume` | +0.93% | 0.35 | 38.8% | 1.26 | 13 | 4.4% | 0/8 | FAIL |
| 10 | `htf_ema` | +0.70% | 0.02 | 40.4% | 1.65 | 11 | 4.8% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `cmf` | 68.3 | p100 | 1.25 | 2.69 | 1.24 | 23 | 6.3% | 1/8 | FAIL |
| 2 | `lob_maker` | 63.8 | p95 | 1.18 | 3.25 | 1.32 | 21 | 6.8% | 1/8 | FAIL |
| 3 | `price_cluster` | 60.3 | p90 | 2.51 | 3.93 | 2.43 | 10 | 4.8% | 0/8 | FAIL |
| 4 | `momentum_quality` | 59.2 | p85 | 1.47 | 2.37 | 1.25 | 20 | 4.5% | 0/8 | FAIL |
| 5 | `supertrend_multi` | 54.6 | p80 | 2.14 | 2.92 | 1.22 | 8 | 2.6% | 1/8 | FAIL |
| 6 | `value_area` | 51.6 | p76 | 1.47 | 2.42 | 1.42 | 12 | 3.0% | 0/8 | FAIL |
| 7 | `linear_channel_rev` | 46.9 | p71 | 1.39 | 3.29 | 2.12 | 6 | 2.2% | 0/8 | FAIL |
| 8 | `price_action_momentum` | 45.6 | p66 | -1.00 | 5.77 | 1.11 | 24 | 7.9% | 1/8 | FAIL |
| 9 | `order_flow_imbalance_v2` | 43.3 | p61 | 0.26 | 5.37 | 1.34 | 20 | 7.1% | 0/8 | FAIL |
| 10 | `relative_volume` | 42.0 | p57 | 0.35 | 3.55 | 1.26 | 13 | 4.4% | 0/8 | FAIL |
| 11 | `htf_ema` | 40.8 | p52 | 0.02 | 3.92 | 1.65 | 11 | 4.8% | 0/8 | FAIL |
| 12 | `wick_reversal` | 38.7 | p47 | 0.17 | 2.86 | 1.31 | 10 | 3.7% | 0/8 | FAIL |
| 13 | `positional_scaling` | 32.5 | p42 | -0.97 | 5.83 | 1.75 | 10 | 4.9% | 0/8 | FAIL |
| 14 | `elder_impulse` | 32.3 | p38 | -0.93 | 5.99 | 1.58 | 14 | 7.3% | 0/8 | FAIL |
| 15 | `volatility_cluster` | 30.1 | p33 | -1.31 | 5.16 | 1.14 | 14 | 5.3% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +4.86% | 2.51 | 2.43 | 10 | 0/8 | FAIL |
| `supertrend_multi` | +4.15% | 2.14 | 1.22 | 8 | 1/8 | FAIL |
| `cmf` | +3.21% | 1.25 | 1.24 | 23 | 1/8 | FAIL |
| `lob_maker` | +2.96% | 1.18 | 1.32 | 21 | 1/8 | FAIL |
| `momentum_quality` | +2.94% | 1.47 | 1.25 | 20 | 0/8 | FAIL |
| `value_area` | +2.01% | 1.47 | 1.42 | 12 | 0/8 | FAIL |
| `linear_channel_rev` | +1.98% | 1.39 | 2.12 | 6 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | +1.66% | 0.26 | 1.34 | 20 | 0/8 | FAIL |
| `relative_volume` | +0.93% | 0.35 | 1.26 | 13 | 0/8 | FAIL |
| `htf_ema` | +0.70% | 0.02 | 1.65 | 11 | 0/8 | FAIL |
| `price_action_momentum` | +0.59% | -1.00 | 1.11 | 24 | 1/8 | FAIL |
| `elder_impulse` | +0.24% | -0.93 | 1.58 | 14 | 0/8 | FAIL |
| `wick_reversal` | +0.17% | 0.17 | 1.31 | 10 | 0/8 | FAIL |
| `positional_scaling` | -0.22% | -0.97 | 1.75 | 10 | 0/8 | FAIL |
| `volatility_cluster` | -0.78% | -1.31 | 1.14 | 14 | 0/8 | FAIL |
| `dema_cross` | -1.36% | -2.42 | 0.57 | 5 | 0/8 | FAIL |
| `roc_ma_cross` | -1.64% | -2.12 | 0.83 | 10 | 0/8 | FAIL |
| `volume_breakout` | -1.82% | -1.99 | 0.98 | 18 | 0/8 | FAIL |
| `narrow_range` | -2.85% | -3.11 | 0.71 | 12 | 0/8 | FAIL |
| `engulfing_zone` | -2.91% | -2.88 | 0.60 | 7 | 0/8 | FAIL |
| `acceleration_band` | -3.35% | -3.34 | 0.70 | 12 | 0/8 | FAIL |
| `frama` | -5.18% | -2.82 | 0.73 | 21 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_cluster` | trades 11 < 15 (x2), trades 5 < 15 (x1), sharpe -2.93 < 1.0 (x1) |
| `supertrend_multi` | no trades generated (x3), trades 13 < 15 (x1), trades 12 < 15 (x1) |
| `cmf` | mc_p_value 0.195 > 0.05 (우연 가능성) (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.408 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 0.93 < 1.5 (x2), sharpe -0.16 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1) |
| `momentum_quality` | mc_p_value 0.114 > 0.05 (우연 가능성) (x1), profit_factor 1.43 < 1.5 (x1), mc_p_value 0.212 > 0.05 (우연 가능성) (x1) |
| `value_area` | trades 14 < 15 (x2), trades 11 < 15 (x2), profit_factor 0.68 < 1.5 (x2) |
| `linear_channel_rev` | trades 5 < 15 (x3), trades 6 < 15 (x2), trades 4 < 15 (x2) |
| `order_flow_imbalance_v2` | mc_p_value 0.077 > 0.05 (우연 가능성) (x1), mc_p_value 0.085 > 0.05 (우연 가능성) (x1), mc_p_value 0.051 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | trades 13 < 15 (x3), trades 14 < 15 (x2), trades 9 < 15 (x1) |
| `htf_ema` | trades 10 < 15 (x2), trades 13 < 15 (x2), trades 11 < 15 (x2) |
| `price_action_momentum` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.221 > 0.05 (우연 가능성) (x1), profit_factor 1.16 < 1.5 (x1) |
| `elder_impulse` | trades 11 < 15 (x2), trades 13 < 15 (x1), sharpe 0.38 < 1.0 (x1) |
| `wick_reversal` | trades 9 < 15 (x2), trades 10 < 15 (x2), trades 13 < 15 (x2) |
| `positional_scaling` | trades 7 < 15 (x2), trades 8 < 15 (x2), sharpe -12.32 < 1.0 (x1) |
| `volatility_cluster` | trades 14 < 15 (x3), trades 12 < 15 (x2), profit_factor 1.28 < 1.5 (x1) |
| `dema_cross` | trades 3 < 15 (x3), profit_factor 0.31 < 1.5 (x2), trades 8 < 15 (x2) |
| `roc_ma_cross` | trades 9 < 15 (x3), profit_factor 0.35 < 1.5 (x2), trades 8 < 15 (x2) |
| `volume_breakout` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.311 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1) |
| `narrow_range` | trades 11 < 15 (x2), profit_factor 0.87 < 1.5 (x2), trades 12 < 15 (x2) |
| `engulfing_zone` | trades 7 < 15 (x3), trades 8 < 15 (x3), sharpe -6.90 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 11 < 15 | 18 |
| trades 13 < 15 | 14 |
| trades 8 < 15 | 11 |
| trades 12 < 15 | 10 |
| trades 14 < 15 | 10 |
| trades 10 < 15 | 9 |
| trades 7 < 15 | 8 |
| trades 9 < 15 | 8 |
| trades 5 < 15 | 7 |
| profit_factor 0.98 < 1.5 | 5 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +0.29% -> $10,029
- **Top 5 균등배분**: +3.62% -> $10,362
