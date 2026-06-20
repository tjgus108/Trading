# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-20T10:16:10.507065Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-20T10:21:25.889787Z_
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
| 평균 수익률 | -4.42% |
| 최고 수익률 | 2.19% (price_cluster) |
| 최저 수익률 | -13.34% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +2.19% | 0.34 | 39.4% | 1.11 | 45 | 11.7% | 1/8 | FAIL |
| 2 | `positional_scaling` | +1.97% | 0.00 | 36.5% | 1.18 | 36 | 9.7% | 1/8 | FAIL |
| 3 | `roc_ma_cross` | +0.09% | -0.41 | 37.6% | 1.10 | 40 | 9.8% | 2/8 | FAIL |
| 4 | `frama` | -0.92% | -0.22 | 38.9% | 1.02 | 42 | 9.8% | 0/8 | FAIL |
| 5 | `dema_cross` | -1.41% | -1.74 | 19.6% | 0.38 | 3 | 2.3% | 0/8 | FAIL |
| 6 | `volume_breakout` | -2.05% | -0.44 | 37.1% | 1.01 | 78 | 15.8% | 0/8 | FAIL |
| 7 | `htf_ema` | -2.35% | -0.35 | 38.5% | 0.98 | 45 | 11.4% | 0/8 | FAIL |
| 8 | `narrow_range` | -2.43% | -0.42 | 38.0% | 0.99 | 50 | 11.6% | 0/8 | FAIL |
| 9 | `acceleration_band` | -2.60% | -0.63 | 32.6% | 1.00 | 45 | 12.8% | 1/8 | FAIL |
| 10 | `price_action_momentum` | -3.73% | -0.88 | 35.6% | 1.01 | 82 | 17.8% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 69.7 | p100 | 0.34 | 1.42 | 1.11 | 45 | 11.7% | 1/8 | FAIL |
| 2 | `roc_ma_cross` | 64.7 | p94 | -0.41 | 2.83 | 1.10 | 40 | 9.8% | 2/8 | FAIL |
| 3 | `positional_scaling` | 63.6 | p89 | 0.00 | 2.87 | 1.18 | 36 | 9.7% | 1/8 | FAIL |
| 4 | `volume_breakout` | 61.6 | p84 | -0.44 | 2.41 | 1.01 | 78 | 15.8% | 0/8 | FAIL |
| 5 | `price_action_momentum` | 59.6 | p78 | -0.88 | 3.03 | 1.01 | 82 | 17.8% | 1/8 | FAIL |
| 6 | `frama` | 58.0 | p73 | -0.22 | 1.40 | 1.02 | 42 | 9.8% | 0/8 | FAIL |
| 7 | `narrow_range` | 57.9 | p68 | -0.42 | 1.39 | 0.99 | 50 | 11.6% | 0/8 | FAIL |
| 8 | `acceleration_band` | 57.3 | p63 | -0.63 | 2.20 | 1.00 | 45 | 12.8% | 1/8 | FAIL |
| 9 | `htf_ema` | 57.1 | p57 | -0.35 | 1.14 | 0.98 | 45 | 11.4% | 0/8 | FAIL |
| 10 | `order_flow_imbalance_v2` | 56.7 | p52 | -0.83 | 2.13 | 0.95 | 73 | 15.8% | 0/8 | FAIL |
| 11 | `lob_maker` | 56.3 | p47 | -0.91 | 1.91 | 0.94 | 84 | 19.7% | 0/8 | FAIL |
| 12 | `momentum_quality` | 52.1 | p42 | -1.31 | 3.52 | 0.96 | 77 | 18.1% | 1/8 | FAIL |
| 13 | `relative_volume` | 51.3 | p36 | -1.44 | 1.68 | 0.87 | 72 | 15.3% | 0/8 | FAIL |
| 14 | `cmf` | 51.1 | p31 | -1.21 | 1.91 | 0.90 | 72 | 18.4% | 0/8 | FAIL |
| 15 | `volatility_cluster` | 38.0 | p26 | -2.14 | 2.75 | 0.81 | 60 | 14.6% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +2.19% | 0.34 | 1.11 | 45 | 1/8 | FAIL |
| `positional_scaling` | +1.97% | 0.00 | 1.18 | 36 | 1/8 | FAIL |
| `roc_ma_cross` | +0.09% | -0.41 | 1.10 | 40 | 2/8 | FAIL |
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
| `wick_reversal` | -13.34% | -3.61 | 0.60 | 44 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_cluster` | sharpe -1.19 < 1.0 (x1), profit_factor 0.82 < 1.5 (x1), mc_p_value 0.713 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 1.44 < 1.5 (x2), mc_p_value 0.109 > 0.1 (우연 가능성) (x1), sharpe -1.11 < 1.0 (x1) |
| `roc_ma_cross` | sharpe -0.11 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.492 > 0.1 (우연 가능성) (x1) |
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
| `wick_reversal` | profit_factor 0.45 < 1.5 (x2), mc_p_value 0.983 > 0.1 (우연 가능성) (x2), mc_p_value 0.998 > 0.1 (우연 가능성) (x2) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.82 < 1.5 | 5 |
| profit_factor 0.81 < 1.5 | 5 |
| profit_factor 0.54 < 1.5 | 5 |
| profit_factor 0.96 < 1.5 | 5 |
| profit_factor 0.77 < 1.5 | 5 |
| profit_factor 0.97 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 0.60 < 1.5 | 4 |
| profit_factor 0.91 < 1.5 | 4 |
| profit_factor 0.93 < 1.5 | 3 |

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
| `positional_scaling` | 0 | 250 | 40 | 13.8% |
| `momentum_quality` | 0 | 535 | 82 | 13.3% |

## 포트폴리오 가상 배분

- **전체 20개 균등배분**: -4.42% -> $9,558
- **Top 5 균등배분**: +0.38% -> $10,038


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-20T10:26:46.845570Z_
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
| 평균 수익률 | -5.37% |
| 최고 수익률 | 1.56% (dema_cross) |
| 최저 수익률 | -16.01% (order_flow_imbalance_v2) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `dema_cross` | +1.56% | 0.73 | 56.1% | 1.67 | 14 | 3.5% | 0/8 | FAIL |
| 2 | `volatility_cluster` | +0.54% | 0.12 | 42.5% | 1.07 | 51 | 9.1% | 0/8 | FAIL |
| 3 | `narrow_range` | +0.27% | 0.06 | 41.4% | 1.06 | 51 | 9.9% | 0/8 | FAIL |
| 4 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 5 | `price_action_momentum` | -0.38% | -0.08 | 42.5% | 1.03 | 51 | 11.3% | 0/8 | FAIL |
| 6 | `momentum_quality` | -2.35% | -0.45 | 39.9% | 0.97 | 73 | 12.3% | 0/8 | FAIL |
| 7 | `cmf` | -3.48% | -0.94 | 37.4% | 0.94 | 56 | 15.2% | 1/8 | FAIL |
| 8 | `engulfing_zone` | -3.80% | -1.84 | 36.8% | 0.90 | 27 | 11.3% | 1/8 | FAIL |
| 9 | `linear_channel_rev` | -3.99% | -1.25 | 36.0% | 0.78 | 28 | 7.1% | 0/8 | FAIL |
| 10 | `roc_ma_cross` | -4.18% | -1.07 | 37.3% | 0.83 | 35 | 9.6% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 57.6 | p100 | -0.45 | 1.19 | 0.97 | 73 | 12.3% | 0/8 | FAIL |
| 2 | `volatility_cluster` | 57.0 | p94 | 0.12 | 1.37 | 1.07 | 51 | 9.1% | 0/8 | FAIL |
| 3 | `narrow_range` | 56.0 | p89 | 0.06 | 1.46 | 1.06 | 51 | 9.9% | 0/8 | FAIL |
| 4 | `dema_cross` | 55.7 | p84 | 0.73 | 2.06 | 1.67 | 14 | 3.5% | 0/8 | FAIL |
| 5 | `price_action_momentum` | 53.7 | p78 | -0.08 | 1.42 | 1.03 | 51 | 11.3% | 0/8 | FAIL |
| 6 | `cmf` | 53.3 | p73 | -0.94 | 2.43 | 0.94 | 56 | 15.2% | 1/8 | FAIL |
| 7 | `roc_ma_cross` | 38.8 | p68 | -1.07 | 0.82 | 0.83 | 35 | 9.6% | 0/8 | FAIL |
| 8 | `engulfing_zone` | 37.1 | p63 | -1.84 | 3.67 | 0.90 | 27 | 11.3% | 1/8 | FAIL |
| 9 | `relative_volume` | 37.0 | p57 | -2.01 | 2.34 | 0.81 | 70 | 15.6% | 0/8 | FAIL |
| 10 | `lob_maker` | 36.6 | p52 | -1.92 | 1.43 | 0.79 | 70 | 20.8% | 0/8 | FAIL |
| 11 | `elder_impulse` | 36.3 | p47 | -1.52 | 1.81 | 0.81 | 46 | 12.5% | 0/8 | FAIL |
| 12 | `linear_channel_rev` | 34.5 | p42 | -1.25 | 0.72 | 0.78 | 28 | 7.1% | 0/8 | FAIL |
| 13 | `htf_ema` | 32.8 | p36 | -1.43 | 1.68 | 0.78 | 31 | 9.8% | 0/8 | FAIL |
| 14 | `price_cluster` | 31.6 | p31 | -1.43 | 1.92 | 0.81 | 28 | 10.7% | 0/8 | FAIL |
| 15 | `volume_breakout` | 30.8 | p26 | -2.60 | 2.23 | 0.75 | 79 | 20.5% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `dema_cross` | +1.56% | 0.73 | 1.67 | 14 | 0/8 | FAIL |
| `volatility_cluster` | +0.54% | 0.12 | 1.07 | 51 | 0/8 | FAIL |
| `narrow_range` | +0.27% | 0.06 | 1.06 | 51 | 0/8 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `price_action_momentum` | -0.38% | -0.08 | 1.03 | 51 | 0/8 | FAIL |
| `momentum_quality` | -2.35% | -0.45 | 0.97 | 73 | 0/8 | FAIL |
| `cmf` | -3.48% | -0.94 | 0.94 | 56 | 1/8 | FAIL |
| `engulfing_zone` | -3.80% | -1.84 | 0.90 | 27 | 1/8 | FAIL |
| `linear_channel_rev` | -3.99% | -1.25 | 0.78 | 28 | 0/8 | FAIL |
| `roc_ma_cross` | -4.18% | -1.07 | 0.83 | 35 | 0/8 | FAIL |
| `acceleration_band` | -4.36% | -2.15 | 0.61 | 11 | 0/8 | FAIL |
| `htf_ema` | -4.66% | -1.43 | 0.78 | 31 | 0/8 | FAIL |
| `price_cluster` | -4.81% | -1.43 | 0.81 | 28 | 0/8 | FAIL |
| `elder_impulse` | -6.63% | -1.52 | 0.81 | 46 | 0/8 | FAIL |
| `positional_scaling` | -8.55% | -2.49 | 0.65 | 37 | 0/8 | FAIL |
| `relative_volume` | -9.11% | -2.01 | 0.81 | 70 | 0/8 | FAIL |
| `frama` | -11.56% | -2.51 | 0.67 | 46 | 0/8 | FAIL |
| `lob_maker` | -12.17% | -1.92 | 0.79 | 70 | 0/8 | FAIL |
| `volume_breakout` | -13.69% | -2.60 | 0.75 | 79 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -16.01% | -2.90 | 0.69 | 72 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `dema_cross` | trades 11 < 15 (x3), trades 12 < 15 (x2), sharpe -0.61 < 1.0 (x1) |
| `volatility_cluster` | mc_p_value 0.225 > 0.1 (우연 가능성) (x2), sharpe -0.45 < 1.0 (x1), profit_factor 0.94 < 1.5 (x1) |
| `narrow_range` | sharpe -1.99 < 1.0 (x2), sharpe -0.55 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1) |
| `wick_reversal` | no trades generated (x8) |
| `price_action_momentum` | profit_factor 1.05 < 1.5 (x2), sharpe -1.38 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1) |
| `momentum_quality` | sharpe -1.30 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.710 > 0.1 (우연 가능성) (x1) |
| `cmf` | sharpe -1.51 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1), mc_p_value 0.746 > 0.1 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe -5.03 < 1.0 (x1), profit_factor 0.31 < 1.5 (x1), mc_p_value 0.993 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -1.20 < 1.0 (x1), profit_factor 0.78 < 1.5 (x1), mc_p_value 0.727 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -0.64 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.620 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | trades 6 < 15 (x2), trades 14 < 15 (x2), sharpe -3.85 < 1.0 (x1) |
| `htf_ema` | sharpe -0.92 < 1.0 (x1), profit_factor 0.85 < 1.5 (x1), mc_p_value 0.660 > 0.1 (우연 가능성) (x1) |
| `price_cluster` | sharpe -2.29 < 1.0 (x1), profit_factor 0.64 < 1.5 (x1), mc_p_value 0.861 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -1.33 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1), mc_p_value 0.748 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | mc_p_value 0.941 > 0.1 (우연 가능성) (x2), sharpe -4.74 < 1.0 (x1), profit_factor 0.42 < 1.5 (x1) |
| `relative_volume` | profit_factor 0.75 < 1.5 (x2), sharpe -2.29 < 1.0 (x1), profit_factor 0.73 < 1.5 (x1) |
| `frama` | profit_factor 0.72 < 1.5 (x2), sharpe -1.87 < 1.0 (x1), mc_p_value 0.842 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 0.68 < 1.5 (x2), sharpe -2.94 < 1.0 (x1), max_drawdown 24.7% > 20% (x1) |
| `volume_breakout` | sharpe -2.63 < 1.0 (x2), profit_factor 0.72 < 1.5 (x1), mc_p_value 0.913 > 0.1 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe -2.01 < 1.0 (x1), profit_factor 0.75 < 1.5 (x1), mc_p_value 0.840 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 8 |
| profit_factor 0.72 < 1.5 | 5 |
| profit_factor 0.93 < 1.5 | 4 |
| profit_factor 0.80 < 1.5 | 4 |
| profit_factor 0.85 < 1.5 | 4 |
| trades 11 < 15 | 3 |
| profit_factor 0.84 < 1.5 | 3 |
| profit_factor 0.55 < 1.5 | 3 |
| profit_factor 0.73 < 1.5 | 3 |
| profit_factor 0.88 < 1.5 | 3 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 0 | 112 | 100.0% |
| `frama` | 0 | 80 | 288 | 78.3% |
| `elder_impulse` | 0 | 125 | 241 | 65.8% |
| `engulfing_zone` | 0 | 78 | 139 | 64.1% |
| `roc_ma_cross` | 0 | 102 | 179 | 63.7% |
| `relative_volume` | 0 | 207 | 352 | 63.0% |
| `cmf` | 0 | 169 | 275 | 61.9% |
| `volume_breakout` | 0 | 244 | 388 | 61.4% |
| `order_flow_imbalance_v2` | 0 | 232 | 340 | 59.4% |
| `positional_scaling` | 0 | 121 | 176 | 59.3% |

## 포트폴리오 가상 배분

- **전체 20개 균등배분**: -5.37% -> $9,463
- **Top 5 균등배분**: +0.40% -> $10,040


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-20T10:31:46.776965Z_
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
| 평균 수익률 | -4.29% |
| 최고 수익률 | 1.42% (elder_impulse) |
| 최저 수익률 | -13.10% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `elder_impulse` | +1.42% | 0.34 | 39.6% | 1.07 | 47 | 8.6% | 0/8 | FAIL |
| 2 | `order_flow_imbalance_v2` | +1.39% | 0.10 | 37.7% | 1.04 | 72 | 11.5% | 0/8 | FAIL |
| 3 | `htf_ema` | +1.12% | 0.27 | 38.8% | 1.08 | 35 | 7.9% | 0/8 | FAIL |
| 4 | `momentum_quality` | +0.10% | -0.14 | 40.8% | 1.03 | 74 | 13.3% | 0/8 | FAIL |
| 5 | `wick_reversal` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/8 | FAIL |
| 6 | `price_action_momentum` | -0.35% | -0.36 | 39.9% | 1.05 | 48 | 9.3% | 1/8 | FAIL |
| 7 | `acceleration_band` | -0.46% | -0.44 | 33.6% | 1.22 | 7 | 3.8% | 0/8 | FAIL |
| 8 | `volatility_cluster` | -0.74% | -0.17 | 39.0% | 1.01 | 49 | 9.4% | 0/8 | FAIL |
| 9 | `roc_ma_cross` | -1.98% | -0.78 | 38.5% | 0.91 | 34 | 8.0% | 0/8 | FAIL |
| 10 | `price_cluster` | -2.63% | -0.85 | 37.8% | 0.84 | 24 | 7.9% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `order_flow_imbalance_v2` | 68.4 | p100 | 0.10 | 1.82 | 1.04 | 72 | 11.5% | 0/8 | FAIL |
| 2 | `price_action_momentum` | 66.7 | p94 | -0.36 | 2.50 | 1.05 | 48 | 9.3% | 1/8 | FAIL |
| 3 | `elder_impulse` | 66.5 | p89 | 0.34 | 0.86 | 1.07 | 47 | 8.6% | 0/8 | FAIL |
| 4 | `momentum_quality` | 63.7 | p84 | -0.14 | 2.35 | 1.03 | 74 | 13.3% | 0/8 | FAIL |
| 5 | `htf_ema` | 61.2 | p78 | 0.27 | 1.09 | 1.08 | 35 | 7.9% | 0/8 | FAIL |
| 6 | `volatility_cluster` | 60.4 | p73 | -0.17 | 1.57 | 1.01 | 49 | 9.4% | 0/8 | FAIL |
| 7 | `frama` | 48.6 | p68 | -1.41 | 1.26 | 0.81 | 60 | 14.8% | 0/8 | FAIL |
| 8 | `roc_ma_cross` | 48.1 | p63 | -0.78 | 2.05 | 0.91 | 34 | 8.0% | 0/8 | FAIL |
| 9 | `acceleration_band` | 46.6 | p57 | -0.44 | 1.91 | 1.22 | 7 | 3.8% | 0/8 | FAIL |
| 10 | `relative_volume` | 45.7 | p52 | -2.06 | 1.19 | 0.76 | 73 | 16.5% | 0/8 | FAIL |
| 11 | `volume_breakout` | 44.9 | p47 | -1.41 | 2.47 | 0.86 | 58 | 15.2% | 0/8 | FAIL |
| 12 | `price_cluster` | 43.7 | p42 | -0.85 | 1.40 | 0.84 | 24 | 7.9% | 0/8 | FAIL |
| 13 | `narrow_range` | 40.6 | p36 | -1.77 | 2.33 | 0.80 | 48 | 12.1% | 0/8 | FAIL |
| 14 | `cmf` | 39.6 | p31 | -1.98 | 1.74 | 0.75 | 52 | 14.2% | 0/8 | FAIL |
| 15 | `lob_maker` | 39.5 | p26 | -2.20 | 1.57 | 0.75 | 67 | 19.1% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `elder_impulse` | +1.42% | 0.34 | 1.07 | 47 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | +1.39% | 0.10 | 1.04 | 72 | 0/8 | FAIL |
| `htf_ema` | +1.12% | 0.27 | 1.08 | 35 | 0/8 | FAIL |
| `momentum_quality` | +0.10% | -0.14 | 1.03 | 74 | 0/8 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/8 | FAIL |
| `price_action_momentum` | -0.35% | -0.36 | 1.05 | 48 | 1/8 | FAIL |
| `acceleration_band` | -0.46% | -0.44 | 1.22 | 7 | 0/8 | FAIL |
| `volatility_cluster` | -0.74% | -0.17 | 1.01 | 49 | 0/8 | FAIL |
| `roc_ma_cross` | -1.98% | -0.78 | 0.91 | 34 | 0/8 | FAIL |
| `price_cluster` | -2.63% | -0.85 | 0.84 | 24 | 0/8 | FAIL |
| `dema_cross` | -4.42% | -1.69 | 0.66 | 26 | 0/8 | FAIL |
| `linear_channel_rev` | -5.77% | -1.89 | 0.68 | 28 | 0/8 | FAIL |
| `volume_breakout` | -5.98% | -1.41 | 0.86 | 58 | 0/8 | FAIL |
| `narrow_range` | -6.22% | -1.77 | 0.80 | 48 | 0/8 | FAIL |
| `frama` | -8.13% | -1.41 | 0.81 | 60 | 0/8 | FAIL |
| `cmf` | -8.62% | -1.98 | 0.75 | 52 | 0/8 | FAIL |
| `engulfing_zone` | -9.43% | -3.45 | 0.57 | 26 | 1/8 | FAIL |
| `relative_volume` | -10.36% | -2.06 | 0.76 | 73 | 0/8 | FAIL |
| `positional_scaling` | -11.71% | -3.40 | 0.55 | 41 | 0/8 | FAIL |
| `lob_maker` | -13.10% | -2.20 | 0.75 | 67 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `elder_impulse` | sharpe -1.33 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1), mc_p_value 0.733 > 0.1 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe -3.46 < 1.0 (x1), profit_factor 0.62 < 1.5 (x1), mc_p_value 0.952 > 0.1 (우연 가능성) (x1) |
| `htf_ema` | sharpe -1.07 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1), mc_p_value 0.699 > 0.1 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 1.33 < 1.5 (x2), sharpe -1.16 < 1.0 (x1), profit_factor 0.86 < 1.5 (x1) |
| `wick_reversal` | no trades generated (x8) |
| `price_action_momentum` | sharpe -2.53 < 1.0 (x1), profit_factor 0.67 < 1.5 (x1), mc_p_value 0.900 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | trades 7 < 15 (x4), trades 8 < 15 (x2), trades 6 < 15 (x2) |
| `volatility_cluster` | sharpe -3.53 < 1.0 (x1), profit_factor 0.56 < 1.5 (x1), mc_p_value 0.966 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -2.43 < 1.0 (x1), profit_factor 0.59 < 1.5 (x1), mc_p_value 0.874 > 0.1 (우연 가능성) (x1) |
| `price_cluster` | profit_factor 0.45 < 1.5 (x2), sharpe -0.17 < 1.0 (x1), profit_factor 0.97 < 1.5 (x1) |
| `dema_cross` | sharpe -1.67 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1), mc_p_value 0.771 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | profit_factor 0.72 < 1.5 (x2), sharpe -3.16 < 1.0 (x1), profit_factor 0.50 < 1.5 (x1) |
| `volume_breakout` | sharpe -5.85 < 1.0 (x1), max_drawdown 25.7% > 20% (x1), profit_factor 0.44 < 1.5 (x1) |
| `narrow_range` | sharpe -4.26 < 1.0 (x1), max_drawdown 20.3% > 20% (x1), profit_factor 0.51 < 1.5 (x1) |
| `frama` | sharpe -2.57 < 1.0 (x1), max_drawdown 22.3% > 20% (x1), profit_factor 0.65 < 1.5 (x1) |
| `cmf` | sharpe -5.89 < 1.0 (x1), max_drawdown 22.0% > 20% (x1), profit_factor 0.40 < 1.5 (x1) |
| `engulfing_zone` | mc_p_value 0.997 > 0.1 (우연 가능성) (x2), sharpe -4.37 < 1.0 (x1), profit_factor 0.30 < 1.5 (x1) |
| `relative_volume` | mc_p_value 0.891 > 0.1 (우연 가능성) (x2), sharpe -3.01 < 1.0 (x1), profit_factor 0.66 < 1.5 (x1) |
| `positional_scaling` | sharpe -3.64 < 1.0 (x1), profit_factor 0.51 < 1.5 (x1), mc_p_value 0.959 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | sharpe -5.45 < 1.0 (x1), max_drawdown 28.8% > 20% (x1), profit_factor 0.48 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| no trades generated | 8 |
| profit_factor 0.86 < 1.5 | 4 |
| profit_factor 1.01 < 1.5 | 4 |
| trades 7 < 15 | 4 |
| profit_factor 0.66 < 1.5 | 4 |
| profit_factor 0.71 < 1.5 | 4 |
| profit_factor 1.23 < 1.5 | 3 |
| profit_factor 0.97 < 1.5 | 3 |
| profit_factor 0.57 < 1.5 | 3 |
| profit_factor 0.58 < 1.5 | 3 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `acceleration_band` | 0 | 0 | 56 | 100.0% |
| `dema_cross` | 0 | 0 | 205 | 100.0% |
| `engulfing_zone` | 0 | 0 | 212 | 100.0% |
| `lob_maker` | 0 | 0 | 539 | 100.0% |
| `momentum_quality` | 0 | 1 | 590 | 99.8% |
| `relative_volume` | 0 | 1 | 580 | 99.8% |
| `volatility_cluster` | 0 | 1 | 394 | 99.7% |
| `frama` | 0 | 2 | 477 | 99.6% |
| `linear_channel_rev` | 0 | 1 | 224 | 99.6% |
| `cmf` | 0 | 2 | 418 | 99.5% |

## 포트폴리오 가상 배분

- **전체 20개 균등배분**: -4.29% -> $9,571
- **Top 5 균등배분**: +0.80% -> $10,080
