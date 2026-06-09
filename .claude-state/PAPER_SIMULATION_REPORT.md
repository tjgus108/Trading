# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-09T20:14:48.702323Z_
_Symbols: BTC/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-09T20:16:04.343451Z_
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
