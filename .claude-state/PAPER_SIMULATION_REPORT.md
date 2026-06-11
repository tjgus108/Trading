# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-11T15:32:12.876357Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-11T15:33:26.931878Z_
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
| 평균 수익률 | 0.47% |
| 최고 수익률 | 6.95% (price_cluster) |
| 최저 수익률 | -4.73% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +6.95% | 3.63 | 52.0% | 2.15 | 12 | 4.1% | 2/8 | FAIL |
| 2 | `momentum_quality` | +4.62% | 1.80 | 41.4% | 1.39 | 22 | 4.9% | 1/8 | FAIL |
| 3 | `supertrend_multi` | +3.90% | 2.03 | 30.4% | 1.20 | 8 | 2.6% | 1/8 | FAIL |
| 4 | `relative_volume` | +3.44% | 1.94 | 41.7% | 1.54 | 17 | 4.2% | 1/8 | FAIL |
| 5 | `cmf` | +3.12% | 1.23 | 41.8% | 1.25 | 23 | 6.2% | 1/8 | FAIL |
| 6 | `lob_maker` | +2.88% | 1.09 | 40.4% | 1.31 | 21 | 6.7% | 1/8 | FAIL |
| 7 | `linear_channel_rev` | +1.98% | 1.39 | 43.6% | 2.12 | 6 | 2.2% | 0/8 | FAIL |
| 8 | `value_area` | +1.64% | 0.88 | 40.2% | 1.26 | 16 | 4.8% | 1/8 | FAIL |
| 9 | `elder_impulse` | +1.02% | -0.84 | 32.7% | 1.58 | 14 | 6.2% | 0/8 | FAIL |
| 10 | `price_action_momentum` | +0.70% | -1.09 | 35.9% | 1.10 | 24 | 7.5% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 74.6 | p100 | 3.63 | 2.42 | 2.15 | 12 | 4.1% | 2/8 | FAIL |
| 2 | `momentum_quality` | 64.4 | p95 | 1.80 | 3.77 | 1.39 | 22 | 4.9% | 1/8 | FAIL |
| 3 | `relative_volume` | 63.0 | p90 | 1.94 | 2.96 | 1.54 | 17 | 4.2% | 1/8 | FAIL |
| 4 | `cmf` | 60.4 | p85 | 1.23 | 2.77 | 1.25 | 23 | 6.2% | 1/8 | FAIL |
| 5 | `lob_maker` | 55.6 | p80 | 1.09 | 3.37 | 1.31 | 21 | 6.7% | 1/8 | FAIL |
| 6 | `value_area` | 52.4 | p76 | 0.88 | 2.56 | 1.26 | 16 | 4.8% | 1/8 | FAIL |
| 7 | `linear_channel_rev` | 46.4 | p71 | 1.39 | 3.29 | 2.12 | 6 | 2.2% | 0/8 | FAIL |
| 8 | `supertrend_multi` | 45.8 | p66 | 2.03 | 2.90 | 1.20 | 8 | 2.6% | 1/8 | FAIL |
| 9 | `price_action_momentum` | 39.9 | p61 | -1.09 | 5.72 | 1.10 | 24 | 7.5% | 1/8 | FAIL |
| 10 | `htf_ema` | 38.3 | p57 | -0.32 | 4.30 | 1.62 | 11 | 4.8% | 0/8 | FAIL |
| 11 | `order_flow_imbalance_v2` | 37.2 | p52 | -0.99 | 5.52 | 1.17 | 18 | 6.9% | 1/8 | FAIL |
| 12 | `elder_impulse` | 34.5 | p47 | -0.84 | 5.92 | 1.58 | 14 | 6.2% | 0/8 | FAIL |
| 13 | `positional_scaling` | 34.1 | p42 | -0.94 | 5.72 | 1.74 | 10 | 4.4% | 0/8 | FAIL |
| 14 | `volume_breakout` | 29.5 | p38 | -2.05 | 5.44 | 0.96 | 18 | 7.5% | 1/8 | FAIL |
| 15 | `volatility_cluster` | 29.3 | p33 | -1.41 | 5.26 | 1.13 | 14 | 5.3% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +6.95% | 3.63 | 2.15 | 12 | 2/8 | FAIL |
| `momentum_quality` | +4.62% | 1.80 | 1.39 | 22 | 1/8 | FAIL |
| `supertrend_multi` | +3.90% | 2.03 | 1.20 | 8 | 1/8 | FAIL |
| `relative_volume` | +3.44% | 1.94 | 1.54 | 17 | 1/8 | FAIL |
| `cmf` | +3.12% | 1.23 | 1.25 | 23 | 1/8 | FAIL |
| `lob_maker` | +2.88% | 1.09 | 1.31 | 21 | 1/8 | FAIL |
| `linear_channel_rev` | +1.98% | 1.39 | 2.12 | 6 | 0/8 | FAIL |
| `value_area` | +1.64% | 0.88 | 1.26 | 16 | 1/8 | FAIL |
| `elder_impulse` | +1.02% | -0.84 | 1.58 | 14 | 0/8 | FAIL |
| `price_action_momentum` | +0.70% | -1.09 | 1.10 | 24 | 1/8 | FAIL |
| `htf_ema` | +0.44% | -0.32 | 1.62 | 11 | 0/8 | FAIL |
| `positional_scaling` | +0.26% | -0.94 | 1.74 | 10 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -0.31% | -0.99 | 1.17 | 18 | 1/8 | FAIL |
| `volatility_cluster` | -0.77% | -1.41 | 1.13 | 14 | 0/8 | FAIL |
| `dema_cross` | -1.36% | -2.42 | 0.57 | 5 | 0/8 | FAIL |
| `wick_reversal` | -1.44% | -1.25 | 1.00 | 11 | 0/8 | FAIL |
| `roc_ma_cross` | -1.45% | -1.95 | 0.84 | 10 | 0/8 | FAIL |
| `volume_breakout` | -1.67% | -2.05 | 0.96 | 18 | 1/8 | FAIL |
| `acceleration_band` | -2.73% | -3.04 | 0.72 | 12 | 0/8 | FAIL |
| `engulfing_zone` | -2.92% | -3.13 | 0.58 | 7 | 0/8 | FAIL |
| `narrow_range` | -3.27% | -3.67 | 0.65 | 12 | 0/8 | FAIL |
| `frama` | -4.73% | -2.66 | 0.74 | 21 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_cluster` | trades 10 < 15 (x2), trades 9 < 15 (x1), trades 11 < 15 (x1) |
| `momentum_quality` | mc_p_value 0.150 > 0.1 (우연 가능성) (x1), sharpe -1.26 < 1.0 (x1), profit_factor 0.86 < 1.5 (x1) |
| `supertrend_multi` | no trades generated (x3), trades 13 < 15 (x1), trades 12 < 15 (x1) |
| `relative_volume` | trades 11 < 15 (x1), profit_factor 1.45 < 1.5 (x1), mc_p_value 0.256 > 0.1 (우연 가능성) (x1) |
| `cmf` | mc_p_value 0.189 > 0.1 (우연 가능성) (x1), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.401 > 0.1 (우연 가능성) (x1) |
| `lob_maker` | sharpe -0.16 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1), mc_p_value 0.522 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | trades 5 < 15 (x3), trades 6 < 15 (x2), trades 4 < 15 (x2) |
| `value_area` | sharpe 0.24 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1), mc_p_value 0.466 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | trades 11 < 15 (x2), trades 13 < 15 (x1), sharpe -0.02 < 1.0 (x1) |
| `price_action_momentum` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.208 > 0.1 (우연 가능성) (x1), profit_factor 1.16 < 1.5 (x1) |
| `htf_ema` | trades 10 < 15 (x2), trades 13 < 15 (x2), trades 11 < 15 (x2) |
| `positional_scaling` | trades 7 < 15 (x2), trades 8 < 15 (x2), sharpe -11.51 < 1.0 (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.137 > 0.1 (우연 가능성) (x1), mc_p_value 0.194 > 0.1 (우연 가능성) (x1), mc_p_value 0.225 > 0.1 (우연 가능성) (x1) |
| `volatility_cluster` | trades 14 < 15 (x3), trades 12 < 15 (x2), profit_factor 1.28 < 1.5 (x1) |
| `dema_cross` | trades 3 < 15 (x3), profit_factor 0.31 < 1.5 (x2), trades 8 < 15 (x2) |
| `wick_reversal` | trades 10 < 15 (x2), profit_factor 1.49 < 1.5 (x1), sharpe -6.85 < 1.0 (x1) |
| `roc_ma_cross` | trades 9 < 15 (x3), trades 8 < 15 (x2), profit_factor 1.28 < 1.5 (x1) |
| `volume_breakout` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.311 > 0.1 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1) |
| `acceleration_band` | trades 12 < 15 (x3), trades 11 < 15 (x3), sharpe 0.59 < 1.0 (x1) |
| `engulfing_zone` | trades 7 < 15 (x3), trades 8 < 15 (x3), sharpe -6.90 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 11 < 15 | 16 |
| trades 12 < 15 | 12 |
| trades 8 < 15 | 11 |
| trades 10 < 15 | 9 |
| trades 13 < 15 | 8 |
| trades 9 < 15 | 7 |
| trades 7 < 15 | 7 |
| trades 14 < 15 | 7 |
| trades 5 < 15 | 6 |
| profit_factor 0.98 < 1.5 | 4 |

## 윈도우별 상세 분석 (상위 5 전략)

_각 전략의 윈도우별 Sharpe/PF/Trades/Pass 상세. FAIL 원인 진단용._

### `price_cluster` (rank_score=74.6, consistency=2/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 4.87 | 2.63 | 9 | 4.2% | bull | ❌ | trades 9 < 15 |
| W2 | 2.51 | 1.55 | 11 | 6.1% | bull | ❌ | trades 11 < 15 |
| W3 | 0.63 | 1.13 | 10 | 6.1% | bear | ❌ | sharpe 0.63 < 1.0; profit_factor 1.13 < 1.5 |
| W4 | 6.27 | 3.62 | 12 | 4.1% | bear | ❌ | trades 12 < 15 |
| W5 | 6.31 | 2.92 | 17 | 4.1% | sideways | ✅ |  |
| W6 | 6.16 | 2.82 | 15 | 2.8% | sideways | ✅ |  |
| W7 | 2.21 | 1.51 | 10 | 2.8% | bull | ❌ | trades 10 < 15 |
| W8 | 0.09 | 1.02 | 8 | 2.8% | bull | ❌ | sharpe 0.09 < 1.0; profit_factor 1.02 < 1.5 |

### `momentum_quality` (rank_score=64.4, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 9.67 | 3.21 | 25 | 2.1% | bull | ✅ |  |
| W2 | 3.81 | 1.53 | 26 | 7.2% | bull | ❌ | mc_p_value 0.150 > 0.1 (우연 가능성) |
| W3 | -1.26 | 0.86 | 23 | 7.9% | bear | ❌ | sharpe -1.26 < 1.0; profit_factor 0.86 < 1.5 |
| W4 | -2.71 | 0.71 | 20 | 7.8% | bear | ❌ | sharpe -2.72 < 1.0; profit_factor 0.71 < 1.5 |
| W5 | -2.04 | 0.76 | 19 | 5.1% | sideways | ❌ | sharpe -2.03 < 1.0; profit_factor 0.76 < 1.5 |
| W6 | 2.09 | 1.35 | 20 | 2.8% | sideways | ❌ | profit_factor 1.35 < 1.5; mc_p_value 0.296 > 0.1 (우연 가능성) |
| W7 | 1.33 | 1.19 | 21 | 3.1% | bull | ❌ | profit_factor 1.18 < 1.5; mc_p_value 0.370 > 0.1 (우연 가능성) |
| W8 | 3.50 | 1.52 | 23 | 3.4% | bull | ❌ | mc_p_value 0.197 > 0.1 (우연 가능성) |

### `relative_volume` (rank_score=63.0, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 6.10 | 3.30 | 11 | 2.1% | bull | ❌ | trades 11 < 15 |
| W2 | 5.46 | 2.16 | 18 | 3.2% | bull | ✅ |  |
| W3 | 2.73 | 1.45 | 19 | 3.2% | bear | ❌ | profit_factor 1.45 < 1.5; mc_p_value 0.256 > 0.1 (우연 가능성) |
| W4 | 1.25 | 1.20 | 17 | 4.1% | bear | ❌ | profit_factor 1.20 < 1.5; mc_p_value 0.367 > 0.1 (우연 가능성) |
| W5 | -3.59 | 0.60 | 18 | 5.6% | sideways | ❌ | sharpe -3.59 < 1.0; profit_factor 0.60 < 1.5 |
| W6 | -0.82 | 0.89 | 17 | 4.7% | sideways | ❌ | sharpe -0.82 < 1.0; profit_factor 0.89 < 1.5 |
| W7 | 1.46 | 1.22 | 20 | 5.4% | bull | ❌ | profit_factor 1.22 < 1.5; mc_p_value 0.336 > 0.1 (우연 가능성) |
| W8 | 2.95 | 1.54 | 18 | 5.4% | bull | ❌ | mc_p_value 0.191 > 0.1 (우연 가능성) |

### `cmf` (rank_score=60.4, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 6.97 | 2.38 | 25 | 4.8% | bull | ✅ |  |
| W2 | 3.81 | 1.64 | 21 | 6.9% | bull | ❌ | mc_p_value 0.189 > 0.1 (우연 가능성) |
| W3 | 1.02 | 1.15 | 19 | 8.9% | bear | ❌ | profit_factor 1.15 < 1.5; mc_p_value 0.401 > 0.1 (우연 가능성) |
| W4 | -0.02 | 1.00 | 21 | 3.7% | bear | ❌ | sharpe -0.02 < 1.0; profit_factor 1.00 < 1.5 |
| W5 | -2.75 | 0.71 | 22 | 5.4% | sideways | ❌ | sharpe -2.75 < 1.0; profit_factor 0.71 < 1.5 |
| W6 | -0.50 | 0.94 | 23 | 7.7% | sideways | ❌ | sharpe -0.50 < 1.0; profit_factor 0.94 < 1.5 |
| W7 | 0.06 | 1.01 | 25 | 6.2% | bull | ❌ | sharpe 0.06 < 1.0; profit_factor 1.01 < 1.5 |
| W8 | 1.23 | 1.16 | 25 | 5.9% | bull | ❌ | profit_factor 1.16 < 1.5; mc_p_value 0.386 > 0.1 (우연 가능성) |

### `lob_maker` (rank_score=55.6, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | -0.16 | 0.98 | 21 | 7.8% | bull | ❌ | sharpe -0.16 < 1.0; profit_factor 0.98 < 1.5 |
| W2 | -0.52 | 0.93 | 19 | 6.7% | bull | ❌ | sharpe -0.52 < 1.0; profit_factor 0.93 < 1.5 |
| W3 | 7.17 | 2.78 | 19 | 3.9% | bear | ✅ |  |
| W4 | 5.13 | 2.00 | 18 | 6.1% | bear | ❌ | mc_p_value 0.109 > 0.1 (우연 가능성) |
| W5 | -4.30 | 0.58 | 22 | 8.2% | sideways | ❌ | sharpe -4.30 < 1.0; profit_factor 0.58 < 1.5 |
| W6 | -0.86 | 0.90 | 24 | 9.7% | sideways | ❌ | sharpe -0.86 < 1.0; profit_factor 0.90 < 1.5 |
| W7 | 0.67 | 1.08 | 22 | 6.0% | bull | ❌ | sharpe 0.67 < 1.0; profit_factor 1.09 < 1.5 |
| W8 | 1.58 | 1.22 | 21 | 5.5% | bull | ❌ | profit_factor 1.22 < 1.5; mc_p_value 0.346 > 0.1 (우연 가능성) |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +0.47% -> $10,047
- **Top 5 균등배분**: +4.41% -> $10,441


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-11T15:34:39.047968Z_
_Symbol: ETH/USDT_
_Data Source: CSV ETH/USDT 4h (resampled from 1h) (/home/user/Trading/data/historical)_
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
| 평균 수익률 | -3.57% |
| 최고 수익률 | 1.88% (acceleration_band) |
| 최저 수익률 | -9.27% (supertrend_multi) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `acceleration_band` | +1.88% | 1.29 | 45.7% | 1.61 | 7 | 2.5% | 0/8 | FAIL |
| 2 | `engulfing_zone` | +1.44% | 0.82 | 37.6% | 1.44 | 7 | 3.0% | 0/8 | FAIL |
| 3 | `dema_cross` | +1.28% | 0.94 | 44.7% | 1.55 | 8 | 2.3% | 0/8 | FAIL |
| 4 | `volatility_cluster` | -0.90% | -0.50 | 40.4% | 1.05 | 16 | 4.5% | 0/8 | FAIL |
| 5 | `price_cluster` | -1.86% | -2.07 | 31.0% | 0.73 | 7 | 4.3% | 0/8 | FAIL |
| 6 | `narrow_range` | -2.07% | -1.65 | 33.0% | 0.85 | 17 | 7.2% | 0/8 | FAIL |
| 7 | `positional_scaling` | -2.33% | -2.97 | 24.5% | 0.57 | 8 | 4.0% | 0/8 | FAIL |
| 8 | `htf_ema` | -2.58% | -2.66 | 25.8% | 0.89 | 9 | 5.4% | 0/8 | FAIL |
| 9 | `wick_reversal` | -2.70% | -3.29 | 32.9% | 0.66 | 10 | 4.6% | 0/8 | FAIL |
| 10 | `roc_ma_cross` | -3.07% | -3.78 | 27.0% | 0.62 | 10 | 4.8% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `acceleration_band` | 61.4 | p100 | 1.29 | 2.42 | 1.61 | 7 | 2.5% | 0/8 | FAIL |
| 2 | `dema_cross` | 61.1 | p95 | 0.94 | 2.78 | 1.55 | 8 | 2.3% | 0/8 | FAIL |
| 3 | `volatility_cluster` | 60.2 | p90 | -0.50 | 2.30 | 1.05 | 16 | 4.5% | 0/8 | FAIL |
| 4 | `engulfing_zone` | 57.6 | p85 | 0.82 | 2.80 | 1.44 | 7 | 3.0% | 0/8 | FAIL |
| 5 | `frama` | 56.8 | p80 | -1.85 | 1.92 | 0.81 | 22 | 8.8% | 0/8 | FAIL |
| 6 | `momentum_quality` | 53.9 | p76 | -2.76 | 3.45 | 0.76 | 24 | 7.6% | 0/8 | FAIL |
| 7 | `narrow_range` | 50.7 | p71 | -1.65 | 2.85 | 0.85 | 17 | 7.2% | 0/8 | FAIL |
| 8 | `lob_maker` | 46.2 | p66 | -3.73 | 2.04 | 0.64 | 24 | 10.7% | 0/8 | FAIL |
| 9 | `value_area` | 39.2 | p61 | -4.14 | 3.14 | 0.62 | 17 | 6.7% | 0/8 | FAIL |
| 10 | `price_action_momentum` | 37.8 | p57 | -4.89 | 3.42 | 0.58 | 22 | 9.6% | 0/8 | FAIL |
| 11 | `htf_ema` | 36.8 | p52 | -2.66 | 3.84 | 0.89 | 9 | 5.4% | 0/8 | FAIL |
| 12 | `price_cluster` | 34.8 | p47 | -2.07 | 2.57 | 0.73 | 7 | 4.3% | 0/8 | FAIL |
| 13 | `cmf` | 34.0 | p42 | -4.43 | 4.06 | 0.58 | 18 | 8.5% | 0/8 | FAIL |
| 14 | `relative_volume` | 33.8 | p38 | -4.74 | 3.19 | 0.53 | 18 | 8.7% | 0/8 | FAIL |
| 15 | `order_flow_imbalance_v2` | 33.6 | p33 | -4.69 | 3.94 | 0.58 | 20 | 10.3% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `acceleration_band` | +1.88% | 1.29 | 1.61 | 7 | 0/8 | FAIL |
| `engulfing_zone` | +1.44% | 0.82 | 1.44 | 7 | 0/8 | FAIL |
| `dema_cross` | +1.28% | 0.94 | 1.55 | 8 | 0/8 | FAIL |
| `volatility_cluster` | -0.90% | -0.50 | 1.05 | 16 | 0/8 | FAIL |
| `price_cluster` | -1.86% | -2.07 | 0.73 | 7 | 0/8 | FAIL |
| `narrow_range` | -2.07% | -1.65 | 0.85 | 17 | 0/8 | FAIL |
| `positional_scaling` | -2.33% | -2.97 | 0.57 | 8 | 0/8 | FAIL |
| `htf_ema` | -2.58% | -2.66 | 0.89 | 9 | 0/8 | FAIL |
| `wick_reversal` | -2.70% | -3.29 | 0.66 | 10 | 0/8 | FAIL |
| `roc_ma_cross` | -3.07% | -3.78 | 0.62 | 10 | 0/8 | FAIL |
| `linear_channel_rev` | -3.08% | -4.77 | 0.52 | 7 | 0/8 | FAIL |
| `momentum_quality` | -3.50% | -2.76 | 0.76 | 24 | 0/8 | FAIL |
| `frama` | -3.64% | -1.85 | 0.81 | 22 | 0/8 | FAIL |
| `value_area` | -4.76% | -4.14 | 0.62 | 17 | 0/8 | FAIL |
| `volume_breakout` | -4.98% | -4.62 | 0.67 | 15 | 0/8 | FAIL |
| `elder_impulse` | -5.38% | -4.70 | 0.58 | 14 | 0/8 | FAIL |
| `cmf` | -5.53% | -4.43 | 0.58 | 18 | 0/8 | FAIL |
| `relative_volume` | -5.83% | -4.74 | 0.53 | 18 | 0/8 | FAIL |
| `price_action_momentum` | -6.79% | -4.89 | 0.58 | 22 | 0/8 | FAIL |
| `lob_maker` | -7.31% | -3.73 | 0.64 | 24 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -7.45% | -4.69 | 0.58 | 20 | 0/8 | FAIL |
| `supertrend_multi` | -9.27% | -7.25 | 0.38 | 17 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `acceleration_band` | trades 9 < 15 (x2), trades 6 < 15 (x2), trades 5 < 15 (x1) |
| `engulfing_zone` | trades 7 < 15 (x4), trades 8 < 15 (x3), sharpe -0.75 < 1.0 (x1) |
| `dema_cross` | trades 7 < 15 (x4), sharpe -3.45 < 1.0 (x1), profit_factor 0.44 < 1.5 (x1) |
| `volatility_cluster` | trades 14 < 15 (x2), trades 12 < 15 (x1), sharpe 0.01 < 1.0 (x1) |
| `price_cluster` | trades 7 < 15 (x5), trades 8 < 15 (x2), sharpe -0.84 < 1.0 (x1) |
| `narrow_range` | profit_factor 0.87 < 1.5 (x2), sharpe 0.57 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1) |
| `positional_scaling` | trades 7 < 15 (x3), trades 8 < 15 (x2), sharpe -3.67 < 1.0 (x1) |
| `htf_ema` | profit_factor 0.22 < 1.5 (x2), trades 12 < 15 (x2), trades 8 < 15 (x2) |
| `wick_reversal` | trades 9 < 15 (x2), trades 11 < 15 (x2), sharpe -1.29 < 1.0 (x1) |
| `roc_ma_cross` | trades 8 < 15 (x3), trades 10 < 15 (x2), sharpe -3.88 < 1.0 (x1) |
| `linear_channel_rev` | profit_factor 0.00 < 1.5 (x3), trades 7 < 15 (x3), trades 6 < 15 (x2) |
| `momentum_quality` | sharpe -7.87 < 1.0 (x1), profit_factor 0.32 < 1.5 (x1), mc_p_value 0.983 > 0.1 (우연 가능성) (x1) |
| `frama` | sharpe -0.62 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1), mc_p_value 0.566 > 0.1 (우연 가능성) (x1) |
| `value_area` | profit_factor 1.11 < 1.5 (x2), sharpe -3.60 < 1.0 (x1), profit_factor 0.62 < 1.5 (x1) |
| `volume_breakout` | profit_factor 0.91 < 1.5 (x2), trades 13 < 15 (x2), trades 12 < 15 (x2) |
| `elder_impulse` | trades 10 < 15 (x2), sharpe -4.93 < 1.0 (x1), profit_factor 0.42 < 1.5 (x1) |
| `cmf` | sharpe -3.00 < 1.0 (x1), profit_factor 0.61 < 1.5 (x1), mc_p_value 0.765 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | sharpe -5.78 < 1.0 (x1), profit_factor 0.41 < 1.5 (x1), mc_p_value 0.933 > 0.1 (우연 가능성) (x1) |
| `price_action_momentum` | sharpe -7.77 < 1.0 (x2), sharpe -0.47 < 1.0 (x1), profit_factor 0.93 < 1.5 (x1) |
| `lob_maker` | sharpe -5.72 < 1.0 (x1), profit_factor 0.47 < 1.5 (x1), mc_p_value 0.939 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 7 < 15 | 22 |
| trades 8 < 15 | 16 |
| trades 9 < 15 | 11 |
| trades 6 < 15 | 8 |
| trades 12 < 15 | 8 |
| profit_factor 0.50 < 1.5 | 6 |
| trades 10 < 15 | 6 |
| mc_p_value 1.000 > 0.1 (우연 가능성) | 6 |
| profit_factor 0.34 < 1.5 | 5 |
| trades 13 < 15 | 5 |

## 윈도우별 상세 분석 (상위 5 전략)

_각 전략의 윈도우별 Sharpe/PF/Trades/Pass 상세. FAIL 원인 진단용._

### `acceleration_band` (rank_score=61.4, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 4.25 | 3.19 | 5 | 2.4% | bear | ❌ | trades 5 < 15 |
| W2 | 1.66 | 1.39 | 9 | 2.4% | bear | ❌ | profit_factor 1.39 < 1.5; trades 9 < 15 |
| W3 | 5.13 | 3.30 | 8 | 2.1% | bull | ❌ | trades 8 < 15 |
| W4 | 1.32 | 1.36 | 6 | 2.4% | bear | ❌ | profit_factor 1.36 < 1.5; trades 6 < 15 |
| W5 | -3.20 | 0.34 | 3 | 2.4% | sideways | ❌ | sharpe -3.20 < 1.0; profit_factor 0.34 < 1.5 |
| W6 | 0.49 | 1.12 | 6 | 2.0% | bull | ❌ | sharpe 0.49 < 1.0; profit_factor 1.12 < 1.5 |
| W7 | 0.86 | 1.20 | 7 | 2.0% | bear | ❌ | sharpe 0.86 < 1.0; profit_factor 1.19 < 1.5 |
| W8 | -0.15 | 0.96 | 9 | 4.4% | bull | ❌ | sharpe -0.15 < 1.0; profit_factor 0.96 < 1.5 |

### `dema_cross` (rank_score=61.1, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | -3.44 | 0.44 | 7 | 2.0% | bear | ❌ | sharpe -3.45 < 1.0; profit_factor 0.44 < 1.5 |
| W2 | 0.86 | 1.22 | 6 | 1.7% | bear | ❌ | sharpe 0.86 < 1.0; profit_factor 1.22 < 1.5 |
| W3 | 2.74 | 1.98 | 7 | 1.5% | bull | ❌ | trades 7 < 15 |
| W4 | 2.29 | 1.81 | 7 | 2.5% | bear | ❌ | trades 7 < 15 |
| W5 | 2.70 | 2.10 | 7 | 1.5% | sideways | ❌ | trades 7 < 15 |
| W6 | -1.12 | 0.76 | 8 | 3.5% | bull | ❌ | sharpe -1.12 < 1.0; profit_factor 0.76 < 1.5 |
| W7 | -2.04 | 0.68 | 11 | 4.2% | bear | ❌ | sharpe -2.04 < 1.0; profit_factor 0.68 < 1.5 |
| W8 | 5.56 | 3.39 | 9 | 1.6% | bull | ❌ | trades 9 < 15 |

### `volatility_cluster` (rank_score=60.2, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 4.51 | 2.47 | 12 | 1.2% | bear | ❌ | trades 12 < 15 |
| W2 | 0.01 | 1.00 | 14 | 4.0% | bear | ❌ | sharpe 0.01 < 1.0; profit_factor 1.00 < 1.5 |
| W3 | 0.45 | 1.06 | 18 | 3.9% | bull | ❌ | sharpe 0.45 < 1.0; profit_factor 1.06 < 1.5 |
| W4 | -1.73 | 0.77 | 14 | 3.6% | bear | ❌ | sharpe -1.73 < 1.0; profit_factor 0.77 < 1.5 |
| W5 | -0.62 | 0.91 | 15 | 3.6% | sideways | ❌ | sharpe -0.62 < 1.0; profit_factor 0.91 < 1.5 |
| W6 | -0.31 | 0.95 | 18 | 4.2% | bull | ❌ | sharpe -0.31 < 1.0; profit_factor 0.96 < 1.5 |
| W7 | -3.60 | 0.58 | 16 | 8.7% | bear | ❌ | sharpe -3.60 < 1.0; profit_factor 0.58 < 1.5 |
| W8 | -2.71 | 0.66 | 17 | 6.5% | bull | ❌ | sharpe -2.71 < 1.0; profit_factor 0.66 < 1.5 |

### `engulfing_zone` (rank_score=57.6, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 5.32 | 3.18 | 8 | 1.4% | bear | ❌ | trades 8 < 15 |
| W2 | 4.34 | 2.61 | 7 | 2.7% | bear | ❌ | trades 7 < 15 |
| W3 | -0.75 | 0.83 | 6 | 2.7% | bull | ❌ | sharpe -0.75 < 1.0; profit_factor 0.83 < 1.5 |
| W4 | 2.38 | 1.68 | 7 | 2.1% | bear | ❌ | trades 7 < 15 |
| W5 | 0.88 | 1.17 | 8 | 2.8% | sideways | ❌ | sharpe 0.88 < 1.0; profit_factor 1.17 < 1.5 |
| W6 | -1.57 | 0.72 | 8 | 3.3% | bull | ❌ | sharpe -1.57 < 1.0; profit_factor 0.72 < 1.5 |
| W7 | -0.70 | 0.85 | 7 | 5.4% | bear | ❌ | sharpe -0.70 < 1.0; profit_factor 0.85 < 1.5 |
| W8 | -3.33 | 0.45 | 7 | 3.7% | bull | ❌ | sharpe -3.33 < 1.0; profit_factor 0.45 < 1.5 |

### `frama` (rank_score=56.8, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | -0.62 | 0.92 | 23 | 10.1% | bear | ❌ | sharpe -0.62 < 1.0; profit_factor 0.92 < 1.5 |
| W2 | -1.98 | 0.77 | 25 | 10.7% | bear | ❌ | sharpe -1.98 < 1.0; profit_factor 0.77 < 1.5 |
| W3 | -5.29 | 0.49 | 22 | 9.3% | bull | ❌ | sharpe -5.29 < 1.0; profit_factor 0.49 < 1.5 |
| W4 | -3.83 | 0.60 | 22 | 10.2% | bear | ❌ | sharpe -3.83 < 1.0; profit_factor 0.60 < 1.5 |
| W5 | 0.94 | 1.13 | 20 | 6.5% | sideways | ❌ | sharpe 0.94 < 1.0; profit_factor 1.13 < 1.5 |
| W6 | 0.07 | 1.00 | 20 | 6.4% | bull | ❌ | sharpe 0.07 < 1.0; profit_factor 1.00 < 1.5 |
| W7 | -2.55 | 0.71 | 22 | 10.4% | bear | ❌ | sharpe -2.55 < 1.0; profit_factor 0.71 < 1.5 |
| W8 | -1.54 | 0.82 | 24 | 6.7% | bull | ❌ | sharpe -1.54 < 1.0; profit_factor 0.82 < 1.5 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.57% -> $9,643
- **Top 5 균등배분**: +0.37% -> $10,037


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-11T15:35:51.641602Z_
_Symbol: SOL/USDT_
_Data Source: CSV SOL/USDT 4h (resampled from 1h) (/home/user/Trading/data/historical)_
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
| 평균 수익률 | -3.64% |
| 최고 수익률 | 3.09% (narrow_range) |
| 최저 수익률 | -8.39% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `narrow_range` | +3.09% | 1.69 | 47.8% | 1.52 | 16 | 3.8% | 1/8 | FAIL |
| 2 | `acceleration_band` | +0.42% | -0.02 | 40.1% | 1.35 | 7 | 2.7% | 0/8 | FAIL |
| 3 | `linear_channel_rev` | +0.08% | -0.94 | 29.9% | 1.13 | 6 | 2.9% | 0/8 | FAIL |
| 4 | `wick_reversal` | -1.08% | -2.00 | 37.7% | 0.90 | 6 | 2.9% | 0/8 | FAIL |
| 5 | `price_cluster` | -1.25% | -2.55 | 27.3% | 0.85 | 6 | 3.8% | 0/8 | FAIL |
| 6 | `value_area` | -2.11% | -2.50 | 37.3% | 1.18 | 17 | 6.6% | 0/8 | FAIL |
| 7 | `engulfing_zone` | -2.45% | -2.50 | 34.7% | 0.67 | 8 | 4.7% | 0/8 | FAIL |
| 8 | `volatility_cluster` | -2.55% | -1.82 | 34.9% | 0.83 | 20 | 6.0% | 0/8 | FAIL |
| 9 | `momentum_quality` | -2.60% | -2.23 | 32.6% | 0.86 | 23 | 7.3% | 1/8 | FAIL |
| 10 | `supertrend_multi` | -2.67% | -2.27 | 29.8% | 0.78 | 12 | 5.8% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `narrow_range` | 81.1 | p100 | 1.69 | 3.34 | 1.52 | 16 | 3.8% | 1/8 | FAIL |
| 2 | `momentum_quality` | 61.7 | p95 | -2.23 | 3.83 | 0.86 | 23 | 7.3% | 1/8 | FAIL |
| 3 | `volatility_cluster` | 53.3 | p90 | -1.82 | 2.44 | 0.83 | 20 | 6.0% | 0/8 | FAIL |
| 4 | `acceleration_band` | 48.4 | p85 | -0.02 | 3.29 | 1.35 | 7 | 2.7% | 0/8 | FAIL |
| 5 | `value_area` | 46.0 | p80 | -2.50 | 5.27 | 1.18 | 17 | 6.6% | 0/8 | FAIL |
| 6 | `frama` | 43.2 | p76 | -2.75 | 4.02 | 0.79 | 24 | 10.7% | 0/8 | FAIL |
| 7 | `linear_channel_rev` | 40.5 | p71 | -0.94 | 4.12 | 1.13 | 6 | 2.9% | 0/8 | FAIL |
| 8 | `supertrend_multi` | 37.9 | p66 | -2.27 | 3.08 | 0.78 | 12 | 5.8% | 0/8 | FAIL |
| 9 | `htf_ema` | 37.6 | p61 | -3.49 | 4.97 | 1.34 | 10 | 5.8% | 0/8 | FAIL |
| 10 | `lob_maker` | 34.7 | p57 | -5.14 | 2.26 | 0.52 | 21 | 9.5% | 0/8 | FAIL |
| 11 | `price_action_momentum` | 33.7 | p52 | -4.64 | 4.13 | 0.60 | 21 | 8.5% | 0/8 | FAIL |
| 12 | `wick_reversal` | 32.8 | p47 | -2.00 | 3.66 | 0.90 | 6 | 2.9% | 0/8 | FAIL |
| 13 | `engulfing_zone` | 31.4 | p42 | -2.50 | 2.87 | 0.67 | 8 | 4.7% | 0/8 | FAIL |
| 14 | `order_flow_imbalance_v2` | 30.7 | p38 | -5.43 | 3.44 | 0.53 | 22 | 10.2% | 0/8 | FAIL |
| 15 | `price_cluster` | 29.5 | p33 | -2.55 | 4.48 | 0.85 | 6 | 3.8% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `narrow_range` | +3.09% | 1.69 | 1.52 | 16 | 1/8 | FAIL |
| `acceleration_band` | +0.42% | -0.02 | 1.35 | 7 | 0/8 | FAIL |
| `linear_channel_rev` | +0.08% | -0.94 | 1.13 | 6 | 0/8 | FAIL |
| `wick_reversal` | -1.08% | -2.00 | 0.90 | 6 | 0/8 | FAIL |
| `price_cluster` | -1.25% | -2.55 | 0.85 | 6 | 0/8 | FAIL |
| `value_area` | -2.11% | -2.50 | 1.18 | 17 | 0/8 | FAIL |
| `engulfing_zone` | -2.45% | -2.50 | 0.67 | 8 | 0/8 | FAIL |
| `volatility_cluster` | -2.55% | -1.82 | 0.83 | 20 | 0/8 | FAIL |
| `momentum_quality` | -2.60% | -2.23 | 0.86 | 23 | 1/8 | FAIL |
| `supertrend_multi` | -2.67% | -2.27 | 0.78 | 12 | 0/8 | FAIL |
| `htf_ema` | -2.87% | -3.49 | 1.34 | 10 | 0/8 | FAIL |
| `volume_breakout` | -3.42% | -3.64 | 0.58 | 10 | 0/8 | FAIL |
| `positional_scaling` | -4.34% | -4.48 | 0.44 | 10 | 0/8 | FAIL |
| `frama` | -4.48% | -2.75 | 0.79 | 24 | 0/8 | FAIL |
| `dema_cross` | -4.67% | -6.16 | 0.27 | 12 | 0/8 | FAIL |
| `roc_ma_cross` | -4.72% | -5.07 | 0.49 | 14 | 0/8 | FAIL |
| `price_action_momentum` | -5.96% | -4.64 | 0.60 | 21 | 0/8 | FAIL |
| `elder_impulse` | -6.41% | -5.68 | 0.65 | 16 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -7.64% | -5.43 | 0.53 | 22 | 0/8 | FAIL |
| `cmf` | -7.81% | -6.47 | 0.41 | 19 | 0/8 | FAIL |
| `relative_volume` | -8.22% | -7.55 | 0.40 | 22 | 0/8 | FAIL |
| `lob_maker` | -8.39% | -5.14 | 0.52 | 21 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `narrow_range` | sharpe 0.07 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.516 > 0.1 (우연 가능성) (x1) |
| `acceleration_band` | trades 7 < 15 (x4), trades 6 < 15 (x2), trades 5 < 15 (x1) |
| `linear_channel_rev` | trades 7 < 15 (x3), sharpe -0.71 < 1.0 (x1), profit_factor 0.86 < 1.5 (x1) |
| `wick_reversal` | trades 6 < 15 (x4), trades 5 < 15 (x2), sharpe -6.10 < 1.0 (x1) |
| `price_cluster` | profit_factor 0.00 < 1.5 (x3), trades 8 < 15 (x2), trades 5 < 15 (x2) |
| `value_area` | trades 14 < 15 (x2), sharpe -4.71 < 1.0 (x1), profit_factor 0.54 < 1.5 (x1) |
| `engulfing_zone` | trades 6 < 15 (x3), profit_factor 0.77 < 1.5 (x2), sharpe -0.83 < 1.0 (x1) |
| `volatility_cluster` | profit_factor 1.27 < 1.5 (x1), mc_p_value 0.368 > 0.1 (우연 가능성) (x1), sharpe -1.20 < 1.0 (x1) |
| `momentum_quality` | sharpe -3.09 < 1.0 (x1), profit_factor 0.69 < 1.5 (x1), mc_p_value 0.773 > 0.1 (우연 가능성) (x1) |
| `supertrend_multi` | trades 7 < 15 (x2), sharpe -0.20 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1) |
| `htf_ema` | profit_factor 0.27 < 1.5 (x2), trades 10 < 15 (x2), trades 9 < 15 (x2) |
| `volume_breakout` | trades 11 < 15 (x3), trades 12 < 15 (x2), sharpe -7.02 < 1.0 (x1) |
| `positional_scaling` | trades 12 < 15 (x2), trades 11 < 15 (x2), sharpe -4.42 < 1.0 (x1) |
| `frama` | sharpe -4.25 < 1.0 (x1), profit_factor 0.60 < 1.5 (x1), mc_p_value 0.867 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | trades 7 < 15 (x2), trades 14 < 15 (x2), sharpe -6.46 < 1.0 (x1) |
| `roc_ma_cross` | trades 10 < 15 (x2), trades 13 < 15 (x2), sharpe -11.35 < 1.0 (x1) |
| `price_action_momentum` | sharpe -5.37 < 1.0 (x1), profit_factor 0.48 < 1.5 (x1), mc_p_value 0.920 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | mc_p_value 1.000 > 0.1 (우연 가능성) (x2), mc_p_value 0.985 > 0.1 (우연 가능성) (x2), trades 9 < 15 (x2) |
| `order_flow_imbalance_v2` | sharpe -6.75 < 1.0 (x1), profit_factor 0.44 < 1.5 (x1), mc_p_value 0.970 > 0.1 (우연 가능성) (x1) |
| `cmf` | sharpe -1.41 < 1.0 (x1), profit_factor 0.81 < 1.5 (x1), mc_p_value 0.647 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 7 < 15 | 16 |
| trades 6 < 15 | 9 |
| trades 9 < 15 | 9 |
| trades 5 < 15 | 8 |
| trades 8 < 15 | 8 |
| profit_factor 0.00 < 1.5 | 8 |
| trades 11 < 15 | 8 |
| trades 12 < 15 | 7 |
| trades 10 < 15 | 7 |
| trades 14 < 15 | 6 |

## 윈도우별 상세 분석 (상위 5 전략)

_각 전략의 윈도우별 Sharpe/PF/Trades/Pass 상세. FAIL 원인 진단용._

### `narrow_range` (rank_score=81.1, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 0.07 | 1.00 | 16 | 5.5% | bear | ❌ | sharpe 0.07 < 1.0; profit_factor 1.00 < 1.5 |
| W2 | -0.41 | 0.94 | 18 | 4.1% | bear | ❌ | sharpe -0.41 < 1.0; profit_factor 0.94 < 1.5 |
| W3 | 2.58 | 1.43 | 18 | 3.0% | bear | ❌ | profit_factor 1.42 < 1.5; mc_p_value 0.270 > 0.1 (우연 가능성) |
| W4 | 0.71 | 1.09 | 16 | 3.0% | bull | ❌ | sharpe 0.71 < 1.0; profit_factor 1.09 < 1.5 |
| W5 | 4.01 | 1.87 | 15 | 3.0% | bull | ❌ | mc_p_value 0.158 > 0.1 (우연 가능성) |
| W6 | 6.89 | 2.96 | 17 | 2.7% | bull | ✅ |  |
| W7 | 4.35 | 2.40 | 12 | 1.9% | bear | ❌ | trades 12 < 15 |
| W8 | -4.71 | 0.50 | 16 | 7.2% | bear | ❌ | sharpe -4.71 < 1.0; profit_factor 0.50 < 1.5 |

### `momentum_quality` (rank_score=61.7, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | -3.09 | 0.69 | 25 | 7.2% | bear | ❌ | sharpe -3.09 < 1.0; profit_factor 0.69 < 1.5 |
| W2 | -5.68 | 0.51 | 26 | 13.0% | bear | ❌ | sharpe -5.68 < 1.0; profit_factor 0.51 < 1.5 |
| W3 | -5.17 | 0.53 | 27 | 8.8% | bear | ❌ | sharpe -5.17 < 1.0; profit_factor 0.53 < 1.5 |
| W4 | -4.32 | 0.61 | 27 | 8.1% | bull | ❌ | sharpe -4.32 < 1.0; profit_factor 0.61 < 1.5 |
| W5 | 1.05 | 1.12 | 25 | 7.0% | bull | ❌ | profit_factor 1.12 < 1.5; mc_p_value 0.402 > 0.1 (우연 가능성) |
| W6 | 5.70 | 2.07 | 22 | 3.0% | bull | ✅ |  |
| W7 | -0.27 | 0.96 | 19 | 5.7% | bear | ❌ | sharpe -0.27 < 1.0; profit_factor 0.96 < 1.5 |
| W8 | -6.05 | 0.39 | 15 | 5.6% | bear | ❌ | sharpe -6.05 < 1.0; profit_factor 0.39 < 1.5 |

### `volatility_cluster` (rank_score=53.3, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 1.58 | 1.27 | 18 | 2.5% | bear | ❌ | profit_factor 1.27 < 1.5; mc_p_value 0.368 > 0.1 (우연 가능성) |
| W2 | -1.20 | 0.84 | 19 | 6.1% | bear | ❌ | sharpe -1.20 < 1.0; profit_factor 0.84 < 1.5 |
| W3 | -4.92 | 0.53 | 22 | 10.8% | bear | ❌ | sharpe -4.92 < 1.0; profit_factor 0.53 < 1.5 |
| W4 | -5.67 | 0.47 | 22 | 7.8% | bull | ❌ | sharpe -5.67 < 1.0; profit_factor 0.47 < 1.5 |
| W5 | -0.00 | 0.99 | 21 | 5.2% | bull | ❌ | sharpe -0.00 < 1.0; profit_factor 0.99 < 1.5 |
| W6 | 0.12 | 1.01 | 18 | 6.8% | bull | ❌ | sharpe 0.12 < 1.0; profit_factor 1.01 < 1.5 |
| W7 | -0.82 | 0.88 | 17 | 3.5% | bear | ❌ | sharpe -0.82 < 1.0; profit_factor 0.88 < 1.5 |
| W8 | -3.62 | 0.62 | 20 | 5.2% | bear | ❌ | sharpe -3.62 < 1.0; profit_factor 0.62 < 1.5 |

### `acceleration_band` (rank_score=48.4, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 3.47 | 2.80 | 5 | 1.0% | bear | ❌ | trades 5 < 15 |
| W2 | 2.70 | 1.97 | 7 | 1.7% | bear | ❌ | trades 7 < 15 |
| W3 | 0.34 | 1.09 | 6 | 1.8% | bear | ❌ | sharpe 0.34 < 1.0; profit_factor 1.09 < 1.5 |
| W4 | -2.77 | 0.53 | 8 | 3.1% | bull | ❌ | sharpe -2.77 < 1.0; profit_factor 0.52 < 1.5 |
| W5 | 0.64 | 1.14 | 7 | 3.0% | bull | ❌ | sharpe 0.64 < 1.0; profit_factor 1.14 < 1.5 |
| W6 | 3.22 | 2.32 | 7 | 2.0% | bull | ❌ | trades 7 < 15 |
| W7 | -0.77 | 0.83 | 7 | 4.0% | bear | ❌ | sharpe -0.76 < 1.0; profit_factor 0.83 < 1.5 |
| W8 | -6.95 | 0.11 | 6 | 5.0% | bear | ❌ | sharpe -6.95 < 1.0; profit_factor 0.11 < 1.5 |

### `value_area` (rank_score=46.0, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | -4.71 | 0.54 | 20 | 8.9% | bear | ❌ | sharpe -4.71 < 1.0; profit_factor 0.54 < 1.5 |
| W2 | -10.32 | 0.20 | 19 | 9.1% | bear | ❌ | sharpe -10.32 < 1.0; profit_factor 0.20 < 1.5 |
| W3 | -4.50 | 0.53 | 17 | 5.8% | bear | ❌ | sharpe -4.50 < 1.0; profit_factor 0.53 < 1.5 |
| W4 | -4.38 | 0.52 | 17 | 8.6% | bull | ❌ | sharpe -4.38 < 1.0; profit_factor 0.52 < 1.5 |
| W5 | -1.39 | 0.79 | 14 | 4.1% | bull | ❌ | sharpe -1.39 < 1.0; profit_factor 0.79 < 1.5 |
| W6 | 8.00 | 4.84 | 14 | 2.0% | bull | ❌ | trades 14 < 15 |
| W7 | 2.81 | 1.53 | 16 | 4.0% | bear | ❌ | mc_p_value 0.260 > 0.1 (우연 가능성) |
| W8 | -5.49 | 0.49 | 20 | 10.6% | bear | ❌ | sharpe -5.49 < 1.0; profit_factor 0.49 < 1.5 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.64% -> $9,636
- **Top 5 균등배분**: +0.25% -> $10,025
