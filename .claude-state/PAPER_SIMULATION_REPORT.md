# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-12T00:17:48.772380Z_
_Symbols: BTC/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-12T00:19:01.075817Z_
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
| 평균 수익률 | -0.23% |
| 최고 수익률 | 6.47% (price_cluster) |
| 최저 수익률 | -6.90% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +6.47% | 3.41 | 52.0% | 2.05 | 12 | 4.2% | 2/8 | FAIL |
| 2 | `momentum_quality` | +4.01% | 1.48 | 41.4% | 1.33 | 22 | 5.1% | 1/8 | FAIL |
| 3 | `supertrend_multi` | +3.57% | 1.84 | 29.7% | 1.14 | 8 | 2.7% | 1/8 | FAIL |
| 4 | `relative_volume` | +2.14% | 0.97 | 40.5% | 1.35 | 18 | 4.8% | 0/8 | FAIL |
| 5 | `linear_channel_rev` | +1.82% | 1.23 | 43.6% | 2.01 | 6 | 2.3% | 0/8 | FAIL |
| 6 | `cmf` | +1.75% | 0.59 | 41.5% | 1.16 | 23 | 6.9% | 1/8 | FAIL |
| 7 | `lob_maker` | +1.61% | 0.50 | 39.6% | 1.23 | 21 | 7.6% | 1/8 | FAIL |
| 8 | `elder_impulse` | +0.22% | -1.56 | 31.8% | 1.48 | 14 | 6.5% | 0/8 | FAIL |
| 9 | `htf_ema` | +0.05% | -0.60 | 40.4% | 1.55 | 11 | 5.0% | 0/8 | FAIL |
| 10 | `value_area` | +0.02% | -0.50 | 37.8% | 1.10 | 16 | 5.2% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 74.8 | p100 | 3.41 | 2.41 | 2.05 | 12 | 4.2% | 2/8 | FAIL |
| 2 | `momentum_quality` | 65.3 | p95 | 1.48 | 3.81 | 1.33 | 22 | 5.1% | 1/8 | FAIL |
| 3 | `cmf` | 58.5 | p90 | 0.59 | 3.08 | 1.16 | 23 | 6.9% | 1/8 | FAIL |
| 4 | `lob_maker` | 54.0 | p85 | 0.50 | 3.60 | 1.23 | 21 | 7.6% | 1/8 | FAIL |
| 5 | `relative_volume` | 53.0 | p80 | 0.97 | 3.66 | 1.35 | 18 | 4.8% | 0/8 | FAIL |
| 6 | `linear_channel_rev` | 47.0 | p76 | 1.23 | 3.30 | 2.01 | 6 | 2.3% | 0/8 | FAIL |
| 7 | `supertrend_multi` | 46.6 | p71 | 1.84 | 2.92 | 1.14 | 8 | 2.7% | 1/8 | FAIL |
| 8 | `value_area` | 45.3 | p66 | -0.50 | 3.63 | 1.10 | 16 | 5.2% | 1/8 | FAIL |
| 9 | `price_action_momentum` | 41.4 | p61 | -1.66 | 5.42 | 0.98 | 24 | 7.7% | 1/8 | FAIL |
| 10 | `htf_ema` | 39.2 | p57 | -0.60 | 4.36 | 1.55 | 11 | 5.0% | 0/8 | FAIL |
| 11 | `order_flow_imbalance_v2` | 36.6 | p52 | -1.59 | 5.78 | 1.06 | 19 | 7.8% | 1/8 | FAIL |
| 12 | `positional_scaling` | 35.6 | p47 | -1.15 | 5.73 | 1.67 | 10 | 4.5% | 0/8 | FAIL |
| 13 | `volatility_cluster` | 33.4 | p42 | -1.21 | 5.37 | 1.14 | 14 | 5.5% | 0/8 | FAIL |
| 14 | `elder_impulse` | 33.3 | p38 | -1.56 | 6.42 | 1.48 | 14 | 6.5% | 0/8 | FAIL |
| 15 | `volume_breakout` | 31.6 | p33 | -2.40 | 5.40 | 0.91 | 18 | 7.7% | 1/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +6.47% | 3.41 | 2.05 | 12 | 2/8 | FAIL |
| `momentum_quality` | +4.01% | 1.48 | 1.33 | 22 | 1/8 | FAIL |
| `supertrend_multi` | +3.57% | 1.84 | 1.14 | 8 | 1/8 | FAIL |
| `relative_volume` | +2.14% | 0.97 | 1.35 | 18 | 0/8 | FAIL |
| `linear_channel_rev` | +1.82% | 1.23 | 2.01 | 6 | 0/8 | FAIL |
| `cmf` | +1.75% | 0.59 | 1.16 | 23 | 1/8 | FAIL |
| `lob_maker` | +1.61% | 0.50 | 1.23 | 21 | 1/8 | FAIL |
| `elder_impulse` | +0.22% | -1.56 | 1.48 | 14 | 0/8 | FAIL |
| `htf_ema` | +0.05% | -0.60 | 1.55 | 11 | 0/8 | FAIL |
| `value_area` | +0.02% | -0.50 | 1.10 | 16 | 1/8 | FAIL |
| `positional_scaling` | -0.01% | -1.15 | 1.67 | 10 | 0/8 | FAIL |
| `volatility_cluster` | -0.49% | -1.21 | 1.14 | 14 | 0/8 | FAIL |
| `price_action_momentum` | -0.63% | -1.66 | 0.98 | 24 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | -1.28% | -1.59 | 1.06 | 19 | 1/8 | FAIL |
| `dema_cross` | -1.47% | -2.57 | 0.54 | 5 | 0/8 | FAIL |
| `roc_ma_cross` | -1.70% | -2.16 | 0.81 | 10 | 0/8 | FAIL |
| `wick_reversal` | -1.74% | -1.47 | 0.96 | 11 | 0/8 | FAIL |
| `volume_breakout` | -2.30% | -2.40 | 0.91 | 18 | 1/8 | FAIL |
| `engulfing_zone` | -3.14% | -3.31 | 0.56 | 7 | 0/8 | FAIL |
| `acceleration_band` | -3.16% | -3.33 | 0.68 | 12 | 0/8 | FAIL |
| `narrow_range` | -3.84% | -4.14 | 0.58 | 12 | 0/8 | FAIL |
| `frama` | -6.90% | -4.20 | 0.63 | 21 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_cluster` | trades 10 < 15 (x2), trades 9 < 15 (x1), profit_factor 1.50 < 1.5 (x1) |
| `momentum_quality` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.168 > 0.1 (우연 가능성) (x1), sharpe -1.52 < 1.0 (x1) |
| `supertrend_multi` | no trades generated (x3), trades 13 < 15 (x2), trades 12 < 15 (x1) |
| `relative_volume` | trades 12 < 15 (x1), mc_p_value 0.110 > 0.1 (우연 가능성) (x1), profit_factor 1.40 < 1.5 (x1) |
| `linear_channel_rev` | trades 5 < 15 (x3), trades 6 < 15 (x2), trades 4 < 15 (x2) |
| `cmf` | mc_p_value 0.202 > 0.1 (우연 가능성) (x1), sharpe 0.75 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1) |
| `lob_maker` | sharpe -2.66 < 1.0 (x1), profit_factor 0.72 < 1.5 (x1), mc_p_value 0.752 > 0.1 (우연 가능성) (x1) |
| `elder_impulse` | trades 11 < 15 (x2), trades 13 < 15 (x1), sharpe -0.24 < 1.0 (x1) |
| `htf_ema` | trades 10 < 15 (x2), trades 13 < 15 (x2), trades 11 < 15 (x2) |
| `value_area` | sharpe -0.00 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.492 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | trades 7 < 15 (x2), trades 8 < 15 (x2), sharpe -11.58 < 1.0 (x1) |
| `volatility_cluster` | trades 14 < 15 (x3), trades 12 < 15 (x2), profit_factor 1.36 < 1.5 (x1) |
| `price_action_momentum` | profit_factor 1.18 < 1.5 (x1), mc_p_value 0.353 > 0.1 (우연 가능성) (x1), sharpe 0.98 < 1.0 (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.147 > 0.1 (우연 가능성) (x1), profit_factor 1.47 < 1.5 (x1), mc_p_value 0.231 > 0.1 (우연 가능성) (x1) |
| `dema_cross` | trades 3 < 15 (x3), profit_factor 0.28 < 1.5 (x2), trades 8 < 15 (x2) |
| `roc_ma_cross` | trades 9 < 15 (x3), trades 8 < 15 (x2), profit_factor 1.24 < 1.5 (x1) |
| `wick_reversal` | trades 10 < 15 (x2), profit_factor 1.42 < 1.5 (x1), sharpe -7.14 < 1.0 (x1) |
| `volume_breakout` | profit_factor 1.19 < 1.5 (x1), mc_p_value 0.373 > 0.1 (우연 가능성) (x1), profit_factor 1.40 < 1.5 (x1) |
| `engulfing_zone` | trades 7 < 15 (x3), trades 8 < 15 (x3), sharpe -7.14 < 1.0 (x1) |
| `acceleration_band` | trades 12 < 15 (x3), trades 11 < 15 (x3), profit_factor 0.30 < 1.5 (x2) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 12 < 15 | 14 |
| trades 11 < 15 | 13 |
| trades 8 < 15 | 11 |
| trades 10 < 15 | 10 |
| trades 13 < 15 | 9 |
| trades 7 < 15 | 7 |
| trades 14 < 15 | 7 |
| trades 9 < 15 | 6 |
| trades 5 < 15 | 6 |
| profit_factor 0.60 < 1.5 | 4 |

## 윈도우별 상세 분석 (상위 5 전략)

_각 전략의 윈도우별 Sharpe/PF/Trades/Pass 상세. FAIL 원인 진단용._

### `price_cluster` (rank_score=74.8, consistency=2/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 4.74 | 2.54 | 9 | 4.3% | bull | ❌ | trades 9 < 15 |
| W2 | 2.34 | 1.50 | 11 | 6.2% | bull | ❌ | profit_factor 1.50 < 1.5; trades 11 < 15 |
| W3 | 0.41 | 1.08 | 10 | 6.2% | bear | ❌ | sharpe 0.41 < 1.0; profit_factor 1.08 < 1.5 |
| W4 | 6.04 | 3.45 | 12 | 4.2% | bear | ❌ | trades 12 < 15 |
| W5 | 6.02 | 2.74 | 17 | 4.2% | sideways | ✅ |  |
| W6 | 5.88 | 2.65 | 15 | 2.8% | sideways | ✅ |  |
| W7 | 1.94 | 1.44 | 10 | 2.8% | bull | ❌ | profit_factor 1.44 < 1.5; trades 10 < 15 |
| W8 | -0.11 | 0.98 | 8 | 2.9% | bull | ❌ | sharpe -0.11 < 1.0; profit_factor 0.98 < 1.5 |

### `momentum_quality` (rank_score=65.3, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 9.45 | 3.09 | 25 | 2.1% | bull | ✅ |  |
| W2 | 3.54 | 1.48 | 26 | 7.3% | bull | ❌ | profit_factor 1.48 < 1.5; mc_p_value 0.168 > 0.1 (우연 가능성) |
| W3 | -1.52 | 0.84 | 23 | 8.3% | bear | ❌ | sharpe -1.52 < 1.0; profit_factor 0.84 < 1.5 |
| W4 | -3.04 | 0.69 | 20 | 7.9% | bear | ❌ | sharpe -3.04 < 1.0; profit_factor 0.69 < 1.5 |
| W5 | -2.47 | 0.72 | 19 | 5.5% | sideways | ❌ | sharpe -2.47 < 1.0; profit_factor 0.72 < 1.5 |
| W6 | 1.67 | 1.27 | 20 | 2.9% | sideways | ❌ | profit_factor 1.27 < 1.5; mc_p_value 0.323 > 0.1 (우연 가능성) |
| W7 | 1.03 | 1.14 | 21 | 3.1% | bull | ❌ | profit_factor 1.14 < 1.5; mc_p_value 0.381 > 0.1 (우연 가능성) |
| W8 | 3.20 | 1.46 | 23 | 3.5% | bull | ❌ | profit_factor 1.46 < 1.5; mc_p_value 0.223 > 0.1 (우연 가능성) |

### `cmf` (rank_score=58.5, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 6.58 | 2.25 | 25 | 4.9% | bull | ✅ |  |
| W2 | 3.54 | 1.58 | 21 | 7.1% | bull | ❌ | mc_p_value 0.202 > 0.1 (우연 가능성) |
| W3 | 0.75 | 1.11 | 19 | 9.2% | bear | ❌ | sharpe 0.75 < 1.0; profit_factor 1.11 < 1.5 |
| W4 | -0.92 | 0.89 | 21 | 3.8% | bear | ❌ | sharpe -0.92 < 1.0; profit_factor 0.89 < 1.5 |
| W5 | -4.20 | 0.60 | 23 | 7.7% | sideways | ❌ | sharpe -4.20 < 1.0; profit_factor 0.60 < 1.5 |
| W6 | -1.67 | 0.81 | 24 | 9.6% | sideways | ❌ | sharpe -1.67 < 1.0; profit_factor 0.81 < 1.5 |
| W7 | -0.30 | 0.96 | 25 | 6.4% | bull | ❌ | sharpe -0.30 < 1.0; profit_factor 0.96 < 1.5 |
| W8 | 0.92 | 1.11 | 25 | 6.1% | bull | ❌ | sharpe 0.92 < 1.0; profit_factor 1.12 < 1.5 |

### `lob_maker` (rank_score=54.0, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | -2.66 | 0.72 | 22 | 12.2% | bull | ❌ | sharpe -2.66 < 1.0; profit_factor 0.72 < 1.5 |
| W2 | -0.82 | 0.89 | 19 | 6.9% | bull | ❌ | sharpe -0.82 < 1.0; profit_factor 0.89 < 1.5 |
| W3 | 6.98 | 2.68 | 19 | 4.0% | bear | ✅ |  |
| W4 | 4.89 | 1.93 | 18 | 6.3% | bear | ❌ | mc_p_value 0.126 > 0.1 (우연 가능성) |
| W5 | -4.70 | 0.55 | 22 | 8.9% | sideways | ❌ | sharpe -4.70 < 1.0; profit_factor 0.55 < 1.5 |
| W6 | -1.26 | 0.86 | 24 | 10.1% | sideways | ❌ | sharpe -1.26 < 1.0; profit_factor 0.86 < 1.5 |
| W7 | 0.31 | 1.04 | 22 | 6.4% | bull | ❌ | sharpe 0.31 < 1.0; profit_factor 1.04 < 1.5 |
| W8 | 1.24 | 1.17 | 21 | 5.7% | bull | ❌ | profit_factor 1.17 < 1.5; mc_p_value 0.366 > 0.1 (우연 가능성) |

### `relative_volume` (rank_score=53.0, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 5.12 | 2.53 | 12 | 3.1% | bull | ❌ | trades 12 < 15 |
| W2 | 5.23 | 2.08 | 18 | 3.4% | bull | ❌ | mc_p_value 0.110 > 0.1 (우연 가능성) |
| W3 | 2.46 | 1.40 | 19 | 3.4% | bear | ❌ | profit_factor 1.40 < 1.5; mc_p_value 0.286 > 0.1 (우연 가능성) |
| W4 | 0.94 | 1.15 | 17 | 4.1% | bear | ❌ | sharpe 0.94 < 1.0; profit_factor 1.15 < 1.5 |
| W5 | -6.16 | 0.43 | 19 | 7.1% | sideways | ❌ | sharpe -6.16 < 1.0; profit_factor 0.43 < 1.5 |
| W6 | -2.95 | 0.67 | 18 | 6.0% | sideways | ❌ | sharpe -2.95 < 1.0; profit_factor 0.66 < 1.5 |
| W7 | 0.47 | 1.07 | 21 | 5.6% | bull | ❌ | sharpe 0.47 < 1.0; profit_factor 1.07 < 1.5 |
| W8 | 2.67 | 1.47 | 18 | 5.5% | bull | ❌ | profit_factor 1.47 < 1.5; mc_p_value 0.216 > 0.1 (우연 가능성) |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -0.23% -> $9,977
- **Top 5 균등배분**: +3.60% -> $10,360
