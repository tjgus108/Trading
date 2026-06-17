# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-17T15:08:39.612244Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-17T15:16:35.824968Z_
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
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -4.34% |
| 최고 수익률 | 5.26% (supertrend_multi) |
| 최저 수익률 | -13.34% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +5.26% | 0.32 | 37.7% | 1.14 | 48 | 10.6% | 2/8 | FAIL |
| 2 | `price_cluster` | +2.19% | 0.34 | 39.4% | 1.11 | 45 | 11.7% | 1/8 | FAIL |
| 3 | `positional_scaling` | +1.97% | 0.00 | 36.5% | 1.18 | 36 | 9.7% | 1/8 | FAIL |
| 4 | `roc_ma_cross` | +0.38% | -0.35 | 37.9% | 1.12 | 40 | 9.6% | 2/8 | FAIL |
| 5 | `frama` | -0.92% | -0.22 | 38.9% | 1.02 | 42 | 9.8% | 0/8 | FAIL |
| 6 | `dema_cross` | -1.41% | -1.74 | 19.6% | 0.38 | 3 | 2.3% | 0/8 | FAIL |
| 7 | `volume_breakout` | -2.05% | -0.44 | 37.1% | 1.01 | 78 | 15.8% | 0/8 | FAIL |
| 8 | `htf_ema` | -2.35% | -0.35 | 38.5% | 0.98 | 45 | 11.4% | 0/8 | FAIL |
| 9 | `narrow_range` | -2.43% | -0.42 | 38.0% | 0.99 | 50 | 11.6% | 0/8 | FAIL |
| 10 | `acceleration_band` | -2.60% | -0.63 | 32.6% | 1.00 | 45 | 12.8% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 73.5 | p100 | 0.32 | 2.82 | 1.14 | 48 | 10.6% | 2/8 | FAIL |
| 2 | `price_cluster` | 69.7 | p95 | 0.34 | 1.42 | 1.11 | 45 | 11.7% | 1/8 | FAIL |
| 3 | `roc_ma_cross` | 65.6 | p90 | -0.35 | 2.88 | 1.12 | 40 | 9.6% | 2/8 | FAIL |
| 4 | `positional_scaling` | 63.6 | p85 | 0.00 | 2.87 | 1.18 | 36 | 9.7% | 1/8 | FAIL |
| 5 | `volume_breakout` | 61.6 | p80 | -0.44 | 2.41 | 1.01 | 78 | 15.8% | 0/8 | FAIL |
| 6 | `price_action_momentum` | 59.6 | p76 | -0.88 | 3.03 | 1.01 | 82 | 17.8% | 1/8 | FAIL |
| 7 | `frama` | 58.0 | p71 | -0.22 | 1.40 | 1.02 | 42 | 9.8% | 0/8 | FAIL |
| 8 | `narrow_range` | 57.9 | p66 | -0.42 | 1.39 | 0.99 | 50 | 11.6% | 0/8 | FAIL |
| 9 | `acceleration_band` | 57.3 | p61 | -0.63 | 2.20 | 1.00 | 45 | 12.8% | 1/8 | FAIL |
| 10 | `htf_ema` | 57.1 | p57 | -0.35 | 1.14 | 0.98 | 45 | 11.4% | 0/8 | FAIL |
| 11 | `order_flow_imbalance_v2` | 56.7 | p52 | -0.83 | 2.13 | 0.95 | 73 | 15.8% | 0/8 | FAIL |
| 12 | `lob_maker` | 56.3 | p47 | -0.91 | 1.91 | 0.94 | 84 | 19.7% | 0/8 | FAIL |
| 13 | `momentum_quality` | 52.1 | p42 | -1.31 | 3.52 | 0.96 | 77 | 18.1% | 1/8 | FAIL |
| 14 | `relative_volume` | 51.3 | p38 | -1.44 | 1.68 | 0.87 | 72 | 15.3% | 0/8 | FAIL |
| 15 | `cmf` | 51.1 | p33 | -1.21 | 1.91 | 0.90 | 72 | 18.4% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +5.26% | 0.32 | 1.14 | 48 | 2/8 | FAIL |
| `price_cluster` | +2.19% | 0.34 | 1.11 | 45 | 1/8 | FAIL |
| `positional_scaling` | +1.97% | 0.00 | 1.18 | 36 | 1/8 | FAIL |
| `roc_ma_cross` | +0.38% | -0.35 | 1.12 | 40 | 2/8 | FAIL |
| `frama` | -0.92% | -0.22 | 1.02 | 42 | 0/8 | FAIL |
| `dema_cross` | -1.41% | -1.74 | 0.38 | 3 | 0/8 | FAIL |
| `volume_breakout` | -2.05% | -0.44 | 1.01 | 78 | 0/8 | FAIL |
| `htf_ema` | -2.35% | -0.35 | 0.98 | 45 | 0/8 | FAIL |
| `narrow_range` | -2.43% | -0.42 | 0.99 | 50 | 0/8 | FAIL |
| `acceleration_band` | -2.60% | -0.63 | 1.00 | 45 | 1/8 | FAIL |
| `price_action_momentum` | -3.73% | -0.88 | 1.01 | 82 | 1/8 | FAIL |
| `momentum_quality` | -4.47% | -1.31 | 0.96 | 77 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | -4.88% | -0.83 | 0.95 | 73 | 0/8 | FAIL |
| `engulfing_zone` | -5.28% | -1.44 | 0.80 | 25 | 0/8 | FAIL |
| `lob_maker` | -7.17% | -0.91 | 0.94 | 84 | 0/8 | FAIL |
| `linear_channel_rev` | -7.38% | -2.74 | 0.62 | 29 | 0/8 | FAIL |
| `cmf` | -7.60% | -1.21 | 0.90 | 72 | 0/8 | FAIL |
| `relative_volume` | -7.67% | -1.44 | 0.87 | 72 | 0/8 | FAIL |
| `volatility_cluster` | -9.01% | -2.14 | 0.81 | 60 | 0/8 | FAIL |
| `elder_impulse` | -10.30% | -2.21 | 0.73 | 47 | 0/8 | FAIL |
| `value_area` | -12.60% | -3.08 | 0.67 | 56 | 0/8 | FAIL |
| `wick_reversal` | -13.34% | -3.61 | 0.60 | 44 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | profit_factor 1.47 < 1.5 (x1), mc_p_value 0.161 > 0.1 (우연 가능성) (x1), sharpe -0.68 < 1.0 (x1) |
| `price_cluster` | sharpe -1.19 < 1.0 (x1), profit_factor 0.82 < 1.5 (x1), mc_p_value 0.713 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 1.44 < 1.5 (x2), mc_p_value 0.109 > 0.1 (우연 가능성) (x1), sharpe -1.11 < 1.0 (x1) |
| `roc_ma_cross` | sharpe 0.14 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1), mc_p_value 0.460 > 0.1 (우연 가능성) (x1) |
| `frama` | sharpe -0.33 < 1.0 (x1), profit_factor 0.97 < 1.5 (x1), mc_p_value 0.512 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x4), trades 2 < 15 (x3), trades 3 < 15 (x2) |
| `volume_breakout` | sharpe -0.16 < 1.0 (x1), max_drawdown 21.3% > 20% (x1), profit_factor 1.01 < 1.5 (x1) |
| `htf_ema` | sharpe 0.21 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.450 > 0.1 (우연 가능성) (x1) |
| `narrow_range` | sharpe 0.60 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.370 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 0.96 < 1.5 (x2), profit_factor 1.39 < 1.5 (x1), mc_p_value 0.174 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | profit_factor 1.27 < 1.5 (x1), mc_p_value 0.202 > 0.1 (우연 가능성) (x1), sharpe -1.92 < 1.0 (x1) |
| `momentum_quality` | profit_factor 0.54 < 1.5 (x2), profit_factor 1.29 < 1.5 (x1), mc_p_value 0.143 > 0.1 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 0.94 < 1.5 (x2), profit_factor 1.25 < 1.5 (x1), mc_p_value 0.234 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -2.49 < 1.0 (x2), profit_factor 0.57 < 1.5 (x2), sharpe -2.14 < 1.0 (x1) |
| `lob_maker` | profit_factor 0.72 < 1.5 (x2), sharpe -2.37 < 1.0 (x1), max_drawdown 32.5% > 20% (x1) |
| `linear_channel_rev` | profit_factor 0.82 < 1.5 (x2), sharpe 0.01 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1) |
| `cmf` | profit_factor 0.77 < 1.5 (x2), sharpe 0.49 < 1.0 (x1), profit_factor 1.09 < 1.5 (x1) |
| `relative_volume` | profit_factor 0.97 < 1.5 (x2), sharpe -0.42 < 1.0 (x1), mc_p_value 0.552 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -0.87 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.654 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -0.78 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.596 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.77 < 1.5 | 7 |
| profit_factor 0.54 < 1.5 | 6 |
| profit_factor 0.81 < 1.5 | 6 |
| profit_factor 0.82 < 1.5 | 6 |
| profit_factor 0.96 < 1.5 | 5 |
| profit_factor 0.97 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 0.60 < 1.5 | 4 |
| profit_factor 0.91 < 1.5 | 4 |
| profit_factor 1.33 < 1.5 | 3 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 5 | 19 | 79.2% |
| `frama` | 0 | 277 | 60 | 17.8% |
| `htf_ema` | 0 | 301 | 62 | 17.1% |
| `price_action_momentum` | 0 | 549 | 103 | 15.8% |
| `cmf` | 0 | 486 | 90 | 15.6% |
| `lob_maker` | 0 | 566 | 102 | 15.3% |
| `volume_breakout` | 0 | 533 | 94 | 15.0% |
| `relative_volume` | 0 | 489 | 84 | 14.7% |
| `value_area` | 0 | 383 | 62 | 13.9% |
| `positional_scaling` | 0 | 250 | 40 | 13.8% |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -4.34% -> $9,566
- **Top 5 균등배분**: +1.78% -> $10,178
