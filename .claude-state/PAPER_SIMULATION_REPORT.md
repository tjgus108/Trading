# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-10T05:09:17.069009Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-10T05:10:23.424446Z_
_Symbol: BTC/USDT_
_Data Source: CSV fallback BTC/USDT 4h (resampled from 1h) (/home/user/Trading/data/historical)_
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

## 윈도우별 상세 분석 (상위 5 전략)

_각 전략의 윈도우별 Sharpe/PF/Trades/Pass 상세. FAIL 원인 진단용._

### `cmf` (rank_score=68.3, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 6.97 | 2.38 | 25 | 4.8% | bull | ✅ |  |
| W2 | 3.62 | 1.59 | 21 | 8.2% | bull | ❌ | mc_p_value 0.195 > 0.05 (우연 가능성) |
| W3 | 1.01 | 1.15 | 19 | 8.8% | bear | ❌ | profit_factor 1.14 < 1.5; mc_p_value 0.408 > 0.05 (우연 가능성) |
| W4 | -0.02 | 1.00 | 21 | 3.7% | bear | ❌ | sharpe -0.02 < 1.0; profit_factor 1.00 < 1.5 |
| W5 | -2.41 | 0.74 | 22 | 5.0% | sideways | ❌ | sharpe -2.41 < 1.0; profit_factor 0.74 < 1.5 |
| W6 | -0.50 | 0.94 | 23 | 7.7% | sideways | ❌ | sharpe -0.50 < 1.0; profit_factor 0.94 < 1.5 |
| W7 | 0.06 | 1.01 | 25 | 6.2% | bull | ❌ | sharpe 0.06 < 1.0; profit_factor 1.01 < 1.5 |
| W8 | 1.23 | 1.16 | 25 | 5.9% | bull | ❌ | profit_factor 1.16 < 1.5; mc_p_value 0.386 > 0.05 (우연 가능성) |

### `lob_maker` (rank_score=63.8, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | -0.16 | 0.98 | 21 | 7.8% | bull | ❌ | sharpe -0.16 < 1.0; profit_factor 0.98 < 1.5 |
| W2 | -0.52 | 0.93 | 19 | 6.7% | bull | ❌ | sharpe -0.52 < 1.0; profit_factor 0.93 < 1.5 |
| W3 | 7.17 | 2.78 | 19 | 3.9% | bear | ✅ |  |
| W4 | 5.13 | 2.00 | 18 | 6.1% | bear | ❌ | mc_p_value 0.109 > 0.05 (우연 가능성) |
| W5 | -3.80 | 0.62 | 22 | 9.2% | sideways | ❌ | sharpe -3.80 < 1.0; profit_factor 0.62 < 1.5 |
| W6 | -0.65 | 0.93 | 24 | 9.4% | sideways | ❌ | sharpe -0.65 < 1.0; profit_factor 0.93 < 1.5 |
| W7 | 0.67 | 1.08 | 22 | 6.0% | bull | ❌ | sharpe 0.67 < 1.0; profit_factor 1.09 < 1.5 |
| W8 | 1.58 | 1.22 | 21 | 5.5% | bull | ❌ | profit_factor 1.22 < 1.5; mc_p_value 0.346 > 0.05 (우연 가능성) |

### `price_cluster` (rank_score=60.3, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 4.42 | 3.39 | 5 | 1.4% | bull | ❌ | trades 5 < 15 |
| W2 | -2.93 | 0.60 | 11 | 9.1% | bull | ❌ | sharpe -2.93 < 1.0; profit_factor 0.60 < 1.5 |
| W3 | -4.29 | 0.46 | 11 | 8.1% | bear | ❌ | sharpe -4.29 < 1.0; profit_factor 0.46 < 1.5 |
| W4 | 1.52 | 1.34 | 10 | 6.8% | bear | ❌ | profit_factor 1.34 < 1.5; trades 10 < 15 |
| W5 | 3.40 | 1.68 | 16 | 6.8% | sideways | ❌ | mc_p_value 0.175 > 0.05 (우연 가능성) |
| W6 | 7.29 | 3.79 | 13 | 1.7% | sideways | ❌ | trades 13 < 15 |
| W7 | 6.72 | 5.80 | 8 | 1.4% | bull | ❌ | trades 8 < 15 |
| W8 | 3.92 | 2.37 | 7 | 2.8% | bull | ❌ | trades 7 < 15 |

### `momentum_quality` (rank_score=59.2, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 4.73 | 1.80 | 22 | 5.1% | bull | ❌ | mc_p_value 0.114 > 0.05 (우연 가능성) |
| W2 | 2.94 | 1.43 | 22 | 5.1% | bull | ❌ | profit_factor 1.43 < 1.5; mc_p_value 0.212 > 0.05 (우연 가능성) |
| W3 | 0.46 | 1.06 | 17 | 5.0% | bear | ❌ | sharpe 0.46 < 1.0; profit_factor 1.06 < 1.5 |
| W4 | -2.39 | 0.73 | 17 | 7.0% | bear | ❌ | sharpe -2.39 < 1.0; profit_factor 0.73 < 1.5 |
| W5 | -1.88 | 0.77 | 18 | 4.9% | sideways | ❌ | sharpe -1.88 < 1.0; profit_factor 0.77 < 1.5 |
| W6 | 2.51 | 1.45 | 18 | 2.4% | sideways | ❌ | profit_factor 1.45 < 1.5; mc_p_value 0.252 > 0.05 (우연 가능성) |
| W7 | 2.00 | 1.30 | 19 | 3.1% | bull | ❌ | profit_factor 1.30 < 1.5; mc_p_value 0.321 > 0.05 (우연 가능성) |
| W8 | 3.38 | 1.50 | 23 | 3.4% | bull | ❌ | profit_factor 1.50 < 1.5; mc_p_value 0.208 > 0.05 (우연 가능성) |

### `supertrend_multi` (rank_score=54.6, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 6.51 | 2.47 | 19 | 5.5% | bull | ✅ |  |
| W2 | 7.22 | 3.53 | 13 | 1.1% | bull | ❌ | trades 13 < 15 |
| W3 | 3.20 | 1.74 | 12 | 4.4% | bear | ❌ | trades 12 < 15 |
| W4 | 0.12 | 1.03 | 7 | 3.4% | bear | ❌ | sharpe 0.12 < 1.0; profit_factor 1.03 < 1.5 |
| W5 | 0.00 | 0.00 | 0 | 0.0% | sideways | ❌ | no trades generated |
| W6 | 0.00 | 0.00 | 0 | 0.0% | sideways | ❌ | no trades generated |
| W7 | 0.00 | 0.00 | 0 | 0.0% | bull | ❌ | no trades generated |
| W8 | 0.09 | 1.02 | 11 | 6.8% | bull | ❌ | sharpe 0.09 < 1.0; profit_factor 1.02 < 1.5 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +0.29% -> $10,029
- **Top 5 균등배분**: +3.62% -> $10,362


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-06-10T05:11:24.666921Z_
_Symbol: ETH/USDT_
_Data Source: CSV fallback ETH/USDT 4h (resampled from 1h) (/home/user/Trading/data/historical)_
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
| 평균 수익률 | -3.39% |
| 최고 수익률 | 1.88% (acceleration_band) |
| 최저 수익률 | -10.01% (supertrend_multi) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `acceleration_band` | +1.88% | 1.29 | 45.7% | 1.61 | 7 | 2.5% | 0/8 | FAIL |
| 2 | `engulfing_zone` | +1.63% | 0.98 | 37.6% | 1.47 | 7 | 3.0% | 0/8 | FAIL |
| 3 | `dema_cross` | +1.27% | 0.94 | 44.7% | 1.55 | 8 | 2.4% | 0/8 | FAIL |
| 4 | `price_cluster` | +1.23% | 0.99 | 45.6% | 127.36 | 3 | 1.6% | 0/8 | FAIL |
| 5 | `volatility_cluster` | -0.92% | -0.51 | 40.4% | 1.05 | 16 | 4.5% | 0/8 | FAIL |
| 6 | `momentum_quality` | -1.62% | -1.46 | 38.2% | 0.88 | 21 | 6.4% | 0/8 | FAIL |
| 7 | `positional_scaling` | -2.26% | -2.82 | 24.5% | 0.59 | 8 | 4.1% | 0/8 | FAIL |
| 8 | `htf_ema` | -2.44% | -2.09 | 25.8% | 0.93 | 9 | 5.6% | 0/8 | FAIL |
| 9 | `roc_ma_cross` | -2.71% | -3.00 | 27.0% | 0.67 | 10 | 4.7% | 0/8 | FAIL |
| 10 | `narrow_range` | -2.76% | -1.97 | 33.0% | 0.81 | 17 | 8.0% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 56.7 | p100 | 0.99 | 3.24 | 127.36 | 3 | 1.6% | 0/8 | FAIL |
| 2 | `frama` | 53.0 | p95 | -1.27 | 1.45 | 0.86 | 22 | 8.1% | 0/8 | FAIL |
| 3 | `volatility_cluster` | 49.2 | p90 | -0.51 | 2.30 | 1.05 | 16 | 4.5% | 0/8 | FAIL |
| 4 | `momentum_quality` | 49.0 | p85 | -1.46 | 3.26 | 0.88 | 21 | 6.4% | 0/8 | FAIL |
| 5 | `order_flow_imbalance_v2` | 46.2 | p80 | -2.51 | 2.03 | 0.76 | 23 | 9.7% | 0/8 | FAIL |
| 6 | `dema_cross` | 43.8 | p76 | 0.94 | 2.79 | 1.55 | 8 | 2.4% | 0/8 | FAIL |
| 7 | `acceleration_band` | 43.5 | p71 | 1.29 | 2.42 | 1.61 | 7 | 2.5% | 0/8 | FAIL |
| 8 | `engulfing_zone` | 42.8 | p66 | 0.98 | 2.74 | 1.47 | 7 | 3.0% | 0/8 | FAIL |
| 9 | `narrow_range` | 40.8 | p61 | -1.97 | 2.85 | 0.81 | 17 | 8.0% | 0/8 | FAIL |
| 10 | `lob_maker` | 39.6 | p57 | -3.68 | 2.30 | 0.65 | 24 | 11.2% | 0/8 | FAIL |
| 11 | `value_area` | 34.5 | p52 | -4.10 | 2.31 | 0.58 | 16 | 6.9% | 0/8 | FAIL |
| 12 | `relative_volume` | 32.5 | p47 | -3.91 | 1.63 | 0.53 | 14 | 6.7% | 0/8 | FAIL |
| 13 | `htf_ema` | 31.9 | p42 | -2.09 | 3.27 | 0.93 | 9 | 5.6% | 0/8 | FAIL |
| 14 | `roc_ma_cross` | 31.0 | p38 | -3.00 | 2.81 | 0.67 | 10 | 4.7% | 0/8 | FAIL |
| 15 | `price_action_momentum` | 30.4 | p33 | -5.10 | 3.33 | 0.57 | 22 | 11.0% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `acceleration_band` | +1.88% | 1.29 | 1.61 | 7 | 0/8 | FAIL |
| `engulfing_zone` | +1.63% | 0.98 | 1.47 | 7 | 0/8 | FAIL |
| `dema_cross` | +1.27% | 0.94 | 1.55 | 8 | 0/8 | FAIL |
| `price_cluster` | +1.23% | 0.99 | 127.36 | 3 | 0/8 | FAIL |
| `volatility_cluster` | -0.92% | -0.51 | 1.05 | 16 | 0/8 | FAIL |
| `momentum_quality` | -1.62% | -1.46 | 0.88 | 21 | 0/8 | FAIL |
| `positional_scaling` | -2.26% | -2.82 | 0.59 | 8 | 0/8 | FAIL |
| `htf_ema` | -2.44% | -2.09 | 0.93 | 9 | 0/8 | FAIL |
| `roc_ma_cross` | -2.71% | -3.00 | 0.67 | 10 | 0/8 | FAIL |
| `narrow_range` | -2.76% | -1.97 | 0.81 | 17 | 0/8 | FAIL |
| `frama` | -2.85% | -1.27 | 0.86 | 22 | 0/8 | FAIL |
| `linear_channel_rev` | -3.12% | -4.58 | 0.54 | 7 | 0/8 | FAIL |
| `wick_reversal` | -3.58% | -4.33 | 0.51 | 9 | 0/8 | FAIL |
| `relative_volume` | -4.79% | -3.91 | 0.53 | 14 | 0/8 | FAIL |
| `value_area` | -5.15% | -4.10 | 0.58 | 16 | 0/8 | FAIL |
| `volume_breakout` | -5.25% | -3.93 | 0.72 | 15 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -5.28% | -2.51 | 0.76 | 23 | 0/8 | FAIL |
| `elder_impulse` | -6.15% | -4.90 | 0.57 | 14 | 0/8 | FAIL |
| `cmf` | -6.35% | -4.51 | 0.56 | 18 | 0/8 | FAIL |
| `lob_maker` | -7.49% | -3.68 | 0.65 | 24 | 0/8 | FAIL |
| `price_action_momentum` | -7.94% | -5.10 | 0.57 | 22 | 0/8 | FAIL |
| `supertrend_multi` | -10.01% | -6.81 | 0.40 | 17 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `acceleration_band` | trades 9 < 15 (x2), trades 6 < 15 (x2), trades 5 < 15 (x1) |
| `engulfing_zone` | trades 7 < 15 (x4), trades 8 < 15 (x3), sharpe -0.75 < 1.0 (x1) |
| `dema_cross` | trades 7 < 15 (x4), sharpe -3.45 < 1.0 (x1), profit_factor 0.44 < 1.5 (x1) |
| `price_cluster` | trades 3 < 15 (x5), trades 5 < 15 (x1), sharpe -1.41 < 1.0 (x1) |
| `volatility_cluster` | trades 14 < 15 (x2), trades 12 < 15 (x1), sharpe 0.01 < 1.0 (x1) |
| `momentum_quality` | sharpe -4.50 < 1.0 (x1), profit_factor 0.49 < 1.5 (x1), mc_p_value 0.857 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | trades 7 < 15 (x3), trades 8 < 15 (x2), sharpe -3.67 < 1.0 (x1) |
| `htf_ema` | trades 12 < 15 (x2), trades 8 < 15 (x2), trades 9 < 15 (x2) |
| `roc_ma_cross` | trades 8 < 15 (x3), trades 10 < 15 (x2), sharpe -2.38 < 1.0 (x1) |
| `narrow_range` | sharpe 0.57 < 1.0 (x2), profit_factor 0.87 < 1.5 (x2), profit_factor 1.10 < 1.5 (x1) |
| `frama` | sharpe -0.62 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1), mc_p_value 0.566 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | profit_factor 0.00 < 1.5 (x3), trades 7 < 15 (x3), trades 6 < 15 (x2) |
| `wick_reversal` | trades 7 < 15 (x2), trades 8 < 15 (x2), trades 11 < 15 (x2) |
| `relative_volume` | trades 11 < 15 (x2), sharpe -3.71 < 1.0 (x1), profit_factor 0.53 < 1.5 (x1) |
| `value_area` | sharpe -5.12 < 1.0 (x1), profit_factor 0.49 < 1.5 (x1), mc_p_value 0.910 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | trades 13 < 15 (x2), trades 12 < 15 (x2), sharpe -0.52 < 1.0 (x1) |
| `order_flow_imbalance_v2` | profit_factor 0.61 < 1.5 (x2), profit_factor 0.70 < 1.5 (x2), sharpe -3.68 < 1.0 (x1) |
| `elder_impulse` | profit_factor 0.55 < 1.5 (x2), trades 10 < 15 (x2), sharpe -6.77 < 1.0 (x1) |
| `cmf` | sharpe -4.18 < 1.0 (x1), profit_factor 0.52 < 1.5 (x1), mc_p_value 0.857 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 0.44 < 1.5 (x2), sharpe -6.42 < 1.0 (x1), mc_p_value 0.965 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 7 < 15 | 18 |
| trades 8 < 15 | 15 |
| trades 9 < 15 | 9 |
| trades 6 < 15 | 8 |
| trades 12 < 15 | 8 |
| profit_factor 0.34 < 1.5 | 7 |
| profit_factor 0.44 < 1.5 | 7 |
| trades 11 < 15 | 7 |
| trades 10 < 15 | 7 |
| trades 3 < 15 | 6 |

## 윈도우별 상세 분석 (상위 5 전략)

_각 전략의 윈도우별 Sharpe/PF/Trades/Pass 상세. FAIL 원인 진단용._

### `price_cluster` (rank_score=56.7, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 1.98 | 1.82 | 5 | 2.2% | bear | ❌ | trades 5 < 15 |
| W2 | 3.18 | 3.17 | 3 | 1.4% | bear | ❌ | trades 3 < 15 |
| W3 | 4.89 | 10.56 | 3 | 0.6% | bull | ❌ | trades 3 < 15 |
| W4 | 1.74 | 1.91 | 3 | 1.6% | bear | ❌ | trades 3 < 15 |
| W5 | -1.41 | 0.67 | 4 | 1.6% | sideways | ❌ | sharpe -1.41 < 1.0; profit_factor 0.67 < 1.5 |
| W6 | -1.07 | 0.72 | 3 | 2.8% | bull | ❌ | sharpe -1.07 < 1.0; profit_factor 0.72 < 1.5 |
| W7 | -5.54 | 0.00 | 3 | 2.8% | bear | ❌ | sharpe -5.54 < 1.0; profit_factor 0.00 < 1.5 |
| W8 | 4.16 | 999.99 | 2 | 0.0% | bull | ❌ | trades 2 < 15 |

### `frama` (rank_score=53.0, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | -0.62 | 0.92 | 23 | 10.1% | bear | ❌ | sharpe -0.62 < 1.0; profit_factor 0.92 < 1.5 |
| W2 | -1.98 | 0.77 | 25 | 10.7% | bear | ❌ | sharpe -1.98 < 1.0; profit_factor 0.77 < 1.5 |
| W3 | -3.12 | 0.65 | 22 | 7.0% | bull | ❌ | sharpe -3.12 < 1.0; profit_factor 0.65 < 1.5 |
| W4 | -2.02 | 0.76 | 22 | 8.2% | bear | ❌ | sharpe -2.02 < 1.0; profit_factor 0.76 < 1.5 |
| W5 | 1.64 | 1.24 | 20 | 5.3% | sideways | ❌ | profit_factor 1.24 < 1.5; mc_p_value 0.351 > 0.05 (우연 가능성) |
| W6 | 0.07 | 1.00 | 20 | 6.4% | bull | ❌ | sharpe 0.07 < 1.0; profit_factor 1.00 < 1.5 |
| W7 | -2.56 | 0.71 | 22 | 10.5% | bear | ❌ | sharpe -2.57 < 1.0; profit_factor 0.71 < 1.5 |
| W8 | -1.58 | 0.82 | 24 | 6.8% | bull | ❌ | sharpe -1.58 < 1.0; profit_factor 0.82 < 1.5 |

### `volatility_cluster` (rank_score=49.2, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 4.51 | 2.47 | 12 | 1.2% | bear | ❌ | trades 12 < 15 |
| W2 | 0.01 | 1.00 | 14 | 4.0% | bear | ❌ | sharpe 0.01 < 1.0; profit_factor 1.00 < 1.5 |
| W3 | 0.45 | 1.06 | 18 | 3.9% | bull | ❌ | sharpe 0.45 < 1.0; profit_factor 1.06 < 1.5 |
| W4 | -1.73 | 0.77 | 14 | 3.6% | bear | ❌ | sharpe -1.73 < 1.0; profit_factor 0.77 < 1.5 |
| W5 | -0.62 | 0.91 | 15 | 3.6% | sideways | ❌ | sharpe -0.62 < 1.0; profit_factor 0.91 < 1.5 |
| W6 | -0.43 | 0.94 | 18 | 4.4% | bull | ❌ | sharpe -0.43 < 1.0; profit_factor 0.94 < 1.5 |
| W7 | -3.58 | 0.58 | 16 | 8.7% | bear | ❌ | sharpe -3.58 < 1.0; profit_factor 0.58 < 1.5 |
| W8 | -2.71 | 0.66 | 17 | 6.5% | bull | ❌ | sharpe -2.71 < 1.0; profit_factor 0.66 < 1.5 |

### `momentum_quality` (rank_score=49.0, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | -4.50 | 0.49 | 18 | 5.9% | bear | ❌ | sharpe -4.50 < 1.0; profit_factor 0.49 < 1.5 |
| W2 | -7.42 | 0.36 | 19 | 9.8% | bear | ❌ | sharpe -7.42 < 1.0; profit_factor 0.36 < 1.5 |
| W3 | -1.13 | 0.85 | 19 | 7.0% | bull | ❌ | sharpe -1.13 < 1.0; profit_factor 0.85 < 1.5 |
| W4 | -0.17 | 0.97 | 23 | 6.2% | bear | ❌ | sharpe -0.17 < 1.0; profit_factor 0.97 < 1.5 |
| W5 | -0.58 | 0.93 | 24 | 6.2% | sideways | ❌ | sharpe -0.58 < 1.0; profit_factor 0.93 < 1.5 |
| W6 | 2.98 | 1.42 | 24 | 3.7% | bull | ❌ | profit_factor 1.42 < 1.5; mc_p_value 0.232 > 0.05 (우연 가능성) |
| W7 | -3.24 | 0.64 | 20 | 5.9% | bear | ❌ | sharpe -3.24 < 1.0; profit_factor 0.64 < 1.5 |
| W8 | 2.36 | 1.37 | 20 | 6.3% | bull | ❌ | profit_factor 1.37 < 1.5; mc_p_value 0.256 > 0.05 (우연 가능성) |

### `order_flow_imbalance_v2` (rank_score=46.2, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | -3.68 | 0.61 | 21 | 9.5% | bear | ❌ | sharpe -3.68 < 1.0; profit_factor 0.61 < 1.5 |
| W2 | -2.92 | 0.70 | 25 | 9.0% | bear | ❌ | sharpe -2.91 < 1.0; profit_factor 0.70 < 1.5 |
| W3 | -3.17 | 0.70 | 26 | 10.1% | bull | ❌ | sharpe -3.17 < 1.0; profit_factor 0.70 < 1.5 |
| W4 | -4.61 | 0.57 | 24 | 10.2% | bear | ❌ | sharpe -4.61 < 1.0; profit_factor 0.57 < 1.5 |
| W5 | -2.12 | 0.76 | 24 | 11.7% | sideways | ❌ | sharpe -2.13 < 1.0; profit_factor 0.76 < 1.5 |
| W6 | 2.40 | 1.36 | 20 | 6.7% | bull | ❌ | profit_factor 1.36 < 1.5; mc_p_value 0.293 > 0.05 (우연 가능성) |
| W7 | -3.95 | 0.61 | 22 | 10.5% | bear | ❌ | sharpe -3.95 < 1.0; profit_factor 0.61 < 1.5 |
| W8 | -2.02 | 0.78 | 25 | 9.5% | bull | ❌ | sharpe -2.02 < 1.0; profit_factor 0.78 < 1.5 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.39% -> $9,661
- **Top 5 균등배분**: +1.02% -> $10,102


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-06-10T05:12:26.108338Z_
_Symbol: SOL/USDT_
_Data Source: CSV fallback SOL/USDT 4h (resampled from 1h) (/home/user/Trading/data/historical)_
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
| 평균 수익률 | -3.69% |
| 최고 수익률 | 3.23% (narrow_range) |
| 최저 수익률 | -8.66% (relative_volume) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `narrow_range` | +3.23% | 1.87 | 47.8% | 1.54 | 16 | 3.7% | 1/8 | FAIL |
| 2 | `acceleration_band` | +0.49% | 0.15 | 40.1% | 1.36 | 7 | 2.7% | 0/8 | FAIL |
| 3 | `linear_channel_rev` | +0.08% | -0.94 | 29.9% | 1.13 | 6 | 2.9% | 0/8 | FAIL |
| 4 | `momentum_quality` | -0.10% | -0.60 | 35.1% | 0.99 | 18 | 5.2% | 0/8 | FAIL |
| 5 | `price_cluster` | -0.83% | -2.15 | 28.9% | 0.82 | 5 | 2.8% | 0/8 | FAIL |
| 6 | `wick_reversal` | -0.91% | -1.95 | 35.7% | 1.08 | 5 | 2.8% | 0/8 | FAIL |
| 7 | `volatility_cluster` | -2.33% | -1.56 | 34.9% | 0.84 | 20 | 6.1% | 0/8 | FAIL |
| 8 | `supertrend_multi` | -2.51% | -2.08 | 29.8% | 0.79 | 12 | 5.6% | 0/8 | FAIL |
| 9 | `engulfing_zone` | -2.53% | -2.54 | 34.7% | 0.67 | 8 | 4.8% | 0/8 | FAIL |
| 10 | `htf_ema` | -2.92% | -3.29 | 31.7% | 1.36 | 10 | 5.9% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `narrow_range` | 82.2 | p100 | 1.87 | 3.01 | 1.54 | 16 | 3.7% | 1/8 | FAIL |
| 2 | `momentum_quality` | 56.7 | p95 | -0.60 | 3.10 | 0.99 | 18 | 5.2% | 0/8 | FAIL |
| 3 | `volatility_cluster` | 54.7 | p90 | -1.56 | 2.04 | 0.84 | 20 | 6.1% | 0/8 | FAIL |
| 4 | `acceleration_band` | 49.2 | p85 | 0.15 | 2.95 | 1.36 | 7 | 2.7% | 0/8 | FAIL |
| 5 | `frama` | 43.9 | p80 | -2.61 | 3.60 | 0.80 | 24 | 11.2% | 0/8 | FAIL |
| 6 | `value_area` | 41.1 | p76 | -3.00 | 4.54 | 0.98 | 16 | 6.6% | 0/8 | FAIL |
| 7 | `linear_channel_rev` | 40.2 | p71 | -0.94 | 4.12 | 1.13 | 6 | 2.9% | 0/8 | FAIL |
| 8 | `supertrend_multi` | 38.7 | p66 | -2.08 | 2.97 | 0.79 | 12 | 5.6% | 0/8 | FAIL |
| 9 | `htf_ema` | 38.2 | p61 | -3.29 | 4.91 | 1.36 | 10 | 5.9% | 0/8 | FAIL |
| 10 | `price_action_momentum` | 36.4 | p57 | -4.08 | 3.85 | 0.64 | 21 | 8.5% | 0/8 | FAIL |
| 11 | `wick_reversal` | 34.1 | p52 | -1.95 | 4.16 | 1.08 | 5 | 2.8% | 0/8 | FAIL |
| 12 | `lob_maker` | 34.0 | p47 | -5.17 | 2.29 | 0.52 | 21 | 9.6% | 0/8 | FAIL |
| 13 | `engulfing_zone` | 30.8 | p42 | -2.54 | 2.94 | 0.67 | 8 | 4.8% | 0/8 | FAIL |
| 14 | `order_flow_imbalance_v2` | 29.5 | p38 | -5.39 | 3.92 | 0.55 | 24 | 11.3% | 0/8 | FAIL |
| 15 | `price_cluster` | 29.1 | p33 | -2.15 | 3.83 | 0.82 | 5 | 2.8% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `narrow_range` | +3.23% | 1.87 | 1.54 | 16 | 1/8 | FAIL |
| `acceleration_band` | +0.49% | 0.15 | 1.36 | 7 | 0/8 | FAIL |
| `linear_channel_rev` | +0.08% | -0.94 | 1.13 | 6 | 0/8 | FAIL |
| `momentum_quality` | -0.10% | -0.60 | 0.99 | 18 | 0/8 | FAIL |
| `price_cluster` | -0.83% | -2.15 | 0.82 | 5 | 0/8 | FAIL |
| `wick_reversal` | -0.91% | -1.95 | 1.08 | 5 | 0/8 | FAIL |
| `volatility_cluster` | -2.33% | -1.56 | 0.84 | 20 | 0/8 | FAIL |
| `supertrend_multi` | -2.51% | -2.08 | 0.79 | 12 | 0/8 | FAIL |
| `engulfing_zone` | -2.53% | -2.54 | 0.67 | 8 | 0/8 | FAIL |
| `htf_ema` | -2.92% | -3.29 | 1.36 | 10 | 0/8 | FAIL |
| `value_area` | -3.18% | -3.00 | 0.98 | 16 | 0/8 | FAIL |
| `volume_breakout` | -3.78% | -3.69 | 0.59 | 10 | 0/8 | FAIL |
| `positional_scaling` | -4.65% | -4.44 | 0.44 | 10 | 0/8 | FAIL |
| `frama` | -4.79% | -2.61 | 0.80 | 24 | 0/8 | FAIL |
| `dema_cross` | -4.97% | -5.87 | 0.30 | 12 | 0/8 | FAIL |
| `roc_ma_cross` | -4.99% | -4.81 | 0.52 | 14 | 0/8 | FAIL |
| `price_action_momentum` | -5.63% | -4.08 | 0.64 | 21 | 0/8 | FAIL |
| `elder_impulse` | -6.85% | -5.33 | 0.68 | 16 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | -8.27% | -5.39 | 0.55 | 24 | 0/8 | FAIL |
| `lob_maker` | -8.49% | -5.17 | 0.52 | 21 | 0/8 | FAIL |
| `cmf` | -8.52% | -6.35 | 0.43 | 19 | 0/8 | FAIL |
| `relative_volume` | -8.66% | -7.30 | 0.39 | 19 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `narrow_range` | sharpe 0.07 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.516 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | trades 7 < 15 (x4), trades 6 < 15 (x2), trades 5 < 15 (x1) |
| `linear_channel_rev` | trades 7 < 15 (x3), sharpe -0.71 < 1.0 (x1), profit_factor 0.86 < 1.5 (x1) |
| `momentum_quality` | sharpe -1.20 < 1.0 (x1), profit_factor 0.84 < 1.5 (x1), mc_p_value 0.600 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | profit_factor 0.00 < 1.5 (x3), trades 7 < 15 (x2), trades 6 < 15 (x2) |
| `wick_reversal` | trades 5 < 15 (x4), sharpe -7.37 < 1.0 (x1), profit_factor 0.04 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.27 < 1.5 (x1), mc_p_value 0.368 > 0.05 (우연 가능성) (x1), sharpe -1.20 < 1.0 (x1) |
| `supertrend_multi` | trades 7 < 15 (x2), sharpe -0.20 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1) |
| `engulfing_zone` | trades 6 < 15 (x3), profit_factor 0.77 < 1.5 (x2), sharpe -0.83 < 1.0 (x1) |
| `htf_ema` | profit_factor 0.39 < 1.5 (x2), trades 10 < 15 (x2), trades 9 < 15 (x2) |
| `value_area` | mc_p_value 0.971 > 0.05 (우연 가능성) (x2), sharpe -3.48 < 1.0 (x1), profit_factor 0.61 < 1.5 (x1) |
| `volume_breakout` | trades 11 < 15 (x3), trades 12 < 15 (x2), sharpe -7.33 < 1.0 (x1) |
| `positional_scaling` | trades 12 < 15 (x2), trades 11 < 15 (x2), sharpe -5.37 < 1.0 (x1) |
| `frama` | sharpe -3.17 < 1.0 (x1), profit_factor 0.68 < 1.5 (x1), mc_p_value 0.799 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | trades 7 < 15 (x2), profit_factor 0.48 < 1.5 (x2), trades 14 < 15 (x2) |
| `roc_ma_cross` | trades 10 < 15 (x2), profit_factor 0.42 < 1.5 (x2), trades 13 < 15 (x2) |
| `price_action_momentum` | sharpe -5.37 < 1.0 (x1), profit_factor 0.48 < 1.5 (x1), mc_p_value 0.920 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | mc_p_value 1.000 > 0.05 (우연 가능성) (x2), trades 9 < 15 (x2), sharpe -11.63 < 1.0 (x1) |
| `order_flow_imbalance_v2` | sharpe -6.69 < 1.0 (x1), profit_factor 0.44 < 1.5 (x1), mc_p_value 0.969 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | sharpe -3.95 < 1.0 (x1), profit_factor 0.56 < 1.5 (x1), mc_p_value 0.832 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 7 < 15 | 18 |
| trades 12 < 15 | 8 |
| trades 6 < 15 | 8 |
| trades 5 < 15 | 8 |
| trades 9 < 15 | 8 |
| profit_factor 0.00 < 1.5 | 8 |
| trades 11 < 15 | 8 |
| trades 14 < 15 | 7 |
| trades 10 < 15 | 7 |
| profit_factor 0.48 < 1.5 | 6 |

## 윈도우별 상세 분석 (상위 5 전략)

_각 전략의 윈도우별 Sharpe/PF/Trades/Pass 상세. FAIL 원인 진단용._

### `narrow_range` (rank_score=82.2, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 0.07 | 1.00 | 16 | 5.5% | bear | ❌ | sharpe 0.07 < 1.0; profit_factor 1.00 < 1.5 |
| W2 | -0.41 | 0.94 | 18 | 4.1% | bear | ❌ | sharpe -0.41 < 1.0; profit_factor 0.94 < 1.5 |
| W3 | 2.58 | 1.43 | 18 | 3.0% | bear | ❌ | profit_factor 1.42 < 1.5; mc_p_value 0.270 > 0.05 (우연 가능성) |
| W4 | 0.71 | 1.09 | 16 | 3.0% | bull | ❌ | sharpe 0.71 < 1.0; profit_factor 1.09 < 1.5 |
| W5 | 4.01 | 1.87 | 15 | 3.0% | bull | ❌ | mc_p_value 0.158 > 0.05 (우연 가능성) |
| W6 | 6.89 | 2.96 | 17 | 2.7% | bull | ✅ |  |
| W7 | 4.35 | 2.40 | 12 | 1.9% | bear | ❌ | trades 12 < 15 |
| W8 | -3.26 | 0.61 | 16 | 6.4% | bear | ❌ | sharpe -3.26 < 1.0; profit_factor 0.61 < 1.5 |

### `momentum_quality` (rank_score=56.7, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | -1.20 | 0.84 | 18 | 4.5% | bear | ❌ | sharpe -1.20 < 1.0; profit_factor 0.84 < 1.5 |
| W2 | -3.26 | 0.64 | 19 | 8.2% | bear | ❌ | sharpe -3.26 < 1.0; profit_factor 0.64 < 1.5 |
| W3 | 0.50 | 1.06 | 20 | 4.9% | bear | ❌ | sharpe 0.50 < 1.0; profit_factor 1.06 < 1.5 |
| W4 | 0.85 | 1.11 | 20 | 3.7% | bull | ❌ | sharpe 0.86 < 1.0; profit_factor 1.11 < 1.5 |
| W5 | 2.99 | 1.49 | 20 | 3.7% | bull | ❌ | profit_factor 1.49 < 1.5; mc_p_value 0.232 > 0.05 (우연 가능성) |
| W6 | 4.12 | 1.79 | 18 | 3.4% | bull | ❌ | mc_p_value 0.160 > 0.05 (우연 가능성) |
| W7 | -3.42 | 0.60 | 16 | 6.9% | bear | ❌ | sharpe -3.42 < 1.0; profit_factor 0.60 < 1.5 |
| W8 | -5.41 | 0.42 | 14 | 6.0% | bear | ❌ | sharpe -5.41 < 1.0; profit_factor 0.42 < 1.5 |

### `volatility_cluster` (rank_score=54.7, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 1.58 | 1.27 | 18 | 2.5% | bear | ❌ | profit_factor 1.27 < 1.5; mc_p_value 0.368 > 0.05 (우연 가능성) |
| W2 | -1.20 | 0.84 | 19 | 6.1% | bear | ❌ | sharpe -1.20 < 1.0; profit_factor 0.84 < 1.5 |
| W3 | -3.82 | 0.61 | 22 | 10.8% | bear | ❌ | sharpe -3.82 < 1.0; profit_factor 0.61 < 1.5 |
| W4 | -4.52 | 0.55 | 22 | 7.6% | bull | ❌ | sharpe -4.52 < 1.0; profit_factor 0.55 < 1.5 |
| W5 | -0.14 | 0.97 | 21 | 5.4% | bull | ❌ | sharpe -0.14 < 1.0; profit_factor 0.97 < 1.5 |
| W6 | 0.02 | 1.00 | 18 | 7.4% | bull | ❌ | sharpe 0.02 < 1.0; profit_factor 1.00 < 1.5 |
| W7 | -0.82 | 0.88 | 17 | 3.5% | bear | ❌ | sharpe -0.82 < 1.0; profit_factor 0.88 < 1.5 |
| W8 | -3.62 | 0.62 | 20 | 5.2% | bear | ❌ | sharpe -3.62 < 1.0; profit_factor 0.62 < 1.5 |

### `acceleration_band` (rank_score=49.2, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 3.47 | 2.80 | 5 | 1.0% | bear | ❌ | trades 5 < 15 |
| W2 | 2.70 | 1.97 | 7 | 1.7% | bear | ❌ | trades 7 < 15 |
| W3 | 0.34 | 1.09 | 6 | 1.8% | bear | ❌ | sharpe 0.34 < 1.0; profit_factor 1.09 < 1.5 |
| W4 | -2.77 | 0.53 | 8 | 3.1% | bull | ❌ | sharpe -2.77 < 1.0; profit_factor 0.52 < 1.5 |
| W5 | 0.64 | 1.14 | 7 | 3.0% | bull | ❌ | sharpe 0.64 < 1.0; profit_factor 1.14 < 1.5 |
| W6 | 3.22 | 2.32 | 7 | 2.0% | bull | ❌ | trades 7 < 15 |
| W7 | -0.77 | 0.83 | 7 | 4.0% | bear | ❌ | sharpe -0.76 < 1.0; profit_factor 0.83 < 1.5 |
| W8 | -5.59 | 0.23 | 6 | 5.0% | bear | ❌ | sharpe -5.59 < 1.0; profit_factor 0.23 < 1.5 |

### `frama` (rank_score=43.9, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | -3.17 | 0.68 | 24 | 13.8% | bear | ❌ | sharpe -3.17 < 1.0; profit_factor 0.68 < 1.5 |
| W2 | -8.91 | 0.33 | 27 | 15.5% | bear | ❌ | sharpe -8.91 < 1.0; profit_factor 0.33 < 1.5 |
| W3 | -5.84 | 0.49 | 28 | 14.3% | bear | ❌ | sharpe -5.84 < 1.0; profit_factor 0.49 < 1.5 |
| W4 | -0.20 | 0.96 | 29 | 8.8% | bull | ❌ | sharpe -0.20 < 1.0; profit_factor 0.96 < 1.5 |
| W5 | -2.63 | 0.74 | 25 | 12.3% | bull | ❌ | sharpe -2.63 < 1.0; profit_factor 0.74 < 1.5 |
| W6 | 2.59 | 1.40 | 20 | 7.1% | bull | ❌ | profit_factor 1.40 < 1.5; mc_p_value 0.278 > 0.05 (우연 가능성) |
| W7 | 1.57 | 1.23 | 19 | 5.9% | bear | ❌ | profit_factor 1.23 < 1.5; mc_p_value 0.358 > 0.05 (우연 가능성) |
| W8 | -4.29 | 0.58 | 21 | 11.9% | bear | ❌ | sharpe -4.29 < 1.0; profit_factor 0.58 < 1.5 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.69% -> $9,631
- **Top 5 균등배분**: +0.57% -> $10,058
