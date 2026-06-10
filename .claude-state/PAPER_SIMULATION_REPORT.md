# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-10T20:13:05.803257Z_
_Symbols: BTC/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-10T20:14:22.207392Z_
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
| 평균 수익률 | 0.28% |
| 최고 수익률 | 4.69% (relative_volume) |
| 최저 수익률 | -5.18% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `relative_volume` | +4.69% | 2.78 | 45.3% | 1.97 | 14 | 3.3% | 0/8 | FAIL |
| 2 | `momentum_quality` | +4.64% | 1.82 | 41.4% | 1.39 | 22 | 4.9% | 1/8 | FAIL |
| 3 | `supertrend_multi` | +4.15% | 2.14 | 30.4% | 1.22 | 8 | 2.6% | 1/8 | FAIL |
| 4 | `cmf` | +3.21% | 1.25 | 41.8% | 1.24 | 23 | 6.3% | 1/8 | FAIL |
| 5 | `lob_maker` | +2.96% | 1.18 | 40.4% | 1.32 | 21 | 6.8% | 1/8 | FAIL |
| 6 | `linear_channel_rev` | +1.98% | 1.39 | 43.6% | 2.12 | 6 | 2.2% | 0/8 | FAIL |
| 7 | `order_flow_imbalance_v2` | +1.66% | 0.26 | 40.0% | 1.34 | 20 | 7.1% | 0/8 | FAIL |
| 8 | `value_area` | +1.46% | 0.76 | 40.2% | 1.25 | 16 | 5.0% | 1/8 | FAIL |
| 9 | `price_cluster` | +1.33% | 0.43 | 42.0% | 1.31 | 11 | 3.9% | 0/8 | FAIL |
| 10 | `htf_ema` | +0.70% | 0.02 | 40.4% | 1.65 | 11 | 4.8% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 73.3 | p100 | 1.82 | 3.71 | 1.39 | 22 | 4.9% | 1/8 | FAIL |
| 2 | `cmf` | 68.7 | p95 | 1.25 | 2.69 | 1.24 | 23 | 6.3% | 1/8 | FAIL |
| 3 | `relative_volume` | 66.3 | p90 | 2.78 | 3.09 | 1.97 | 14 | 3.3% | 0/8 | FAIL |
| 4 | `lob_maker` | 64.4 | p85 | 1.18 | 3.25 | 1.32 | 21 | 6.8% | 1/8 | FAIL |
| 5 | `value_area` | 58.7 | p80 | 0.76 | 2.61 | 1.25 | 16 | 5.0% | 1/8 | FAIL |
| 6 | `supertrend_multi` | 54.7 | p76 | 2.14 | 2.92 | 1.22 | 8 | 2.6% | 1/8 | FAIL |
| 7 | `linear_channel_rev` | 49.2 | p71 | 1.39 | 3.29 | 2.12 | 6 | 2.2% | 0/8 | FAIL |
| 8 | `price_action_momentum` | 46.2 | p66 | -1.00 | 5.77 | 1.11 | 24 | 7.9% | 1/8 | FAIL |
| 9 | `order_flow_imbalance_v2` | 44.1 | p61 | 0.26 | 5.37 | 1.34 | 20 | 7.1% | 0/8 | FAIL |
| 10 | `htf_ema` | 42.4 | p57 | 0.02 | 3.92 | 1.65 | 11 | 4.8% | 0/8 | FAIL |
| 11 | `price_cluster` | 42.0 | p52 | 0.43 | 2.99 | 1.31 | 11 | 3.9% | 0/8 | FAIL |
| 12 | `positional_scaling` | 34.5 | p47 | -0.97 | 5.83 | 1.75 | 10 | 4.9% | 0/8 | FAIL |
| 13 | `elder_impulse` | 33.9 | p42 | -0.93 | 5.99 | 1.58 | 14 | 7.3% | 0/8 | FAIL |
| 14 | `volatility_cluster` | 30.9 | p38 | -1.31 | 5.16 | 1.14 | 14 | 5.3% | 0/8 | FAIL |
| 15 | `wick_reversal` | 30.6 | p33 | -0.92 | 2.81 | 1.02 | 11 | 4.3% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `relative_volume` | +4.69% | 2.78 | 1.97 | 14 | 0/8 | FAIL |
| `momentum_quality` | +4.64% | 1.82 | 1.39 | 22 | 1/8 | FAIL |
| `supertrend_multi` | +4.15% | 2.14 | 1.22 | 8 | 1/8 | FAIL |
| `cmf` | +3.21% | 1.25 | 1.24 | 23 | 1/8 | FAIL |
| `lob_maker` | +2.96% | 1.18 | 1.32 | 21 | 1/8 | FAIL |
| `linear_channel_rev` | +1.98% | 1.39 | 2.12 | 6 | 0/8 | FAIL |
| `order_flow_imbalance_v2` | +1.66% | 0.26 | 1.34 | 20 | 0/8 | FAIL |
| `value_area` | +1.46% | 0.76 | 1.25 | 16 | 1/8 | FAIL |
| `price_cluster` | +1.33% | 0.43 | 1.31 | 11 | 0/8 | FAIL |
| `htf_ema` | +0.70% | 0.02 | 1.65 | 11 | 0/8 | FAIL |
| `price_action_momentum` | +0.59% | -1.00 | 1.11 | 24 | 1/8 | FAIL |
| `elder_impulse` | +0.24% | -0.93 | 1.58 | 14 | 0/8 | FAIL |
| `positional_scaling` | -0.22% | -0.97 | 1.75 | 10 | 0/8 | FAIL |
| `volatility_cluster` | -0.78% | -1.31 | 1.14 | 14 | 0/8 | FAIL |
| `wick_reversal` | -1.26% | -0.92 | 1.02 | 11 | 0/8 | FAIL |
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
| `relative_volume` | trades 13 < 15 (x3), trades 10 < 15 (x1), trades 14 < 15 (x1) |
| `momentum_quality` | profit_factor 1.50 < 1.5 (x1), mc_p_value 0.158 > 0.05 (우연 가능성) (x1), sharpe -1.35 < 1.0 (x1) |
| `supertrend_multi` | no trades generated (x3), trades 13 < 15 (x1), trades 12 < 15 (x1) |
| `cmf` | mc_p_value 0.195 > 0.05 (우연 가능성) (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.408 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | profit_factor 0.93 < 1.5 (x2), sharpe -0.16 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1) |
| `linear_channel_rev` | trades 5 < 15 (x3), trades 6 < 15 (x2), trades 4 < 15 (x2) |
| `order_flow_imbalance_v2` | mc_p_value 0.077 > 0.05 (우연 가능성) (x1), mc_p_value 0.085 > 0.05 (우연 가능성) (x1), mc_p_value 0.051 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -0.20 < 1.0 (x1), profit_factor 0.98 < 1.5 (x1), mc_p_value 0.513 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | trades 10 < 15 (x3), sharpe -0.85 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1) |
| `htf_ema` | trades 10 < 15 (x2), trades 13 < 15 (x2), trades 11 < 15 (x2) |
| `price_action_momentum` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.221 > 0.05 (우연 가능성) (x1), profit_factor 1.16 < 1.5 (x1) |
| `elder_impulse` | trades 11 < 15 (x2), trades 13 < 15 (x1), sharpe 0.38 < 1.0 (x1) |
| `positional_scaling` | trades 7 < 15 (x2), trades 8 < 15 (x2), sharpe -12.32 < 1.0 (x1) |
| `volatility_cluster` | trades 14 < 15 (x3), trades 12 < 15 (x2), profit_factor 1.28 < 1.5 (x1) |
| `wick_reversal` | trades 10 < 15 (x2), profit_factor 1.49 < 1.5 (x1), sharpe -4.25 < 1.0 (x1) |
| `dema_cross` | trades 3 < 15 (x3), profit_factor 0.31 < 1.5 (x2), trades 8 < 15 (x2) |
| `roc_ma_cross` | trades 9 < 15 (x3), profit_factor 0.35 < 1.5 (x2), trades 8 < 15 (x2) |
| `volume_breakout` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.311 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1) |
| `narrow_range` | trades 11 < 15 (x2), profit_factor 0.87 < 1.5 (x2), trades 12 < 15 (x2) |
| `engulfing_zone` | trades 7 < 15 (x3), trades 8 < 15 (x3), sharpe -6.90 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| trades 11 < 15 | 15 |
| trades 12 < 15 | 13 |
| trades 13 < 15 | 12 |
| trades 10 < 15 | 11 |
| trades 8 < 15 | 10 |
| trades 14 < 15 | 8 |
| trades 7 < 15 | 7 |
| trades 9 < 15 | 7 |
| trades 5 < 15 | 6 |
| profit_factor 0.98 < 1.5 | 5 |

## 윈도우별 상세 분석 (상위 5 전략)

_각 전략의 윈도우별 Sharpe/PF/Trades/Pass 상세. FAIL 원인 진단용._

### `momentum_quality` (rank_score=73.3, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 9.67 | 3.21 | 25 | 2.1% | bull | ✅ |  |
| W2 | 3.69 | 1.50 | 26 | 7.3% | bull | ❌ | profit_factor 1.50 < 1.5; mc_p_value 0.158 > 0.05 (우연 가능성) |
| W3 | -1.35 | 0.86 | 23 | 8.1% | bear | ❌ | sharpe -1.35 < 1.0; profit_factor 0.86 < 1.5 |
| W4 | -2.29 | 0.76 | 20 | 7.2% | bear | ❌ | sharpe -2.29 < 1.0; profit_factor 0.75 < 1.5 |
| W5 | -2.04 | 0.76 | 19 | 5.1% | sideways | ❌ | sharpe -2.03 < 1.0; profit_factor 0.76 < 1.5 |
| W6 | 2.09 | 1.35 | 20 | 2.8% | sideways | ❌ | profit_factor 1.35 < 1.5; mc_p_value 0.296 > 0.05 (우연 가능성) |
| W7 | 1.33 | 1.19 | 21 | 3.1% | bull | ❌ | profit_factor 1.18 < 1.5; mc_p_value 0.370 > 0.05 (우연 가능성) |
| W8 | 3.50 | 1.52 | 23 | 3.4% | bull | ❌ | mc_p_value 0.197 > 0.05 (우연 가능성) |

### `cmf` (rank_score=68.7, consistency=1/8)

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

### `relative_volume` (rank_score=66.3, consistency=0/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 5.91 | 3.72 | 10 | 2.1% | bull | ❌ | trades 10 < 15 |
| W2 | 6.77 | 3.54 | 13 | 2.1% | bull | ❌ | trades 13 < 15 |
| W3 | 4.77 | 2.30 | 13 | 2.1% | bear | ❌ | trades 13 < 15 |
| W4 | 3.65 | 1.80 | 14 | 3.1% | bear | ❌ | trades 14 < 15 |
| W5 | -3.35 | 0.57 | 13 | 3.3% | sideways | ❌ | sharpe -3.35 < 1.0; profit_factor 0.57 < 1.5 |
| W6 | 0.03 | 1.01 | 12 | 3.3% | sideways | ❌ | sharpe 0.03 < 1.0; profit_factor 1.01 < 1.5 |
| W7 | 2.12 | 1.38 | 17 | 5.4% | bull | ❌ | profit_factor 1.38 < 1.5; mc_p_value 0.301 > 0.05 (우연 가능성) |
| W8 | 2.33 | 1.41 | 17 | 5.4% | bull | ❌ | profit_factor 1.41 < 1.5; mc_p_value 0.246 > 0.05 (우연 가능성) |

### `lob_maker` (rank_score=64.4, consistency=1/8)

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

### `value_area` (rank_score=58.7, consistency=1/8)

| Window | Sharpe | PF | Trades | MDD | Market | Pass | Fail Reasons |
|--------|--------|-----|--------|-----|--------|------|--------------|
| W1 | 6.92 | 2.82 | 16 | 3.1% | bull | ✅ |  |
| W2 | -0.20 | 0.98 | 18 | 7.8% | bull | ❌ | sharpe -0.20 < 1.0; profit_factor 0.98 < 1.5 |
| W3 | -0.58 | 0.92 | 16 | 7.0% | bear | ❌ | sharpe -0.58 < 1.0; profit_factor 0.92 < 1.5 |
| W4 | 2.26 | 1.50 | 12 | 2.2% | bear | ❌ | trades 12 < 15 |
| W5 | -0.97 | 0.87 | 16 | 4.3% | sideways | ❌ | sharpe -0.97 < 1.0; profit_factor 0.87 < 1.5 |
| W6 | -0.43 | 0.94 | 15 | 4.0% | sideways | ❌ | sharpe -0.43 < 1.0; profit_factor 0.94 < 1.5 |
| W7 | -1.87 | 0.77 | 17 | 6.9% | bull | ❌ | sharpe -1.87 < 1.0; profit_factor 0.77 < 1.5 |
| W8 | 0.95 | 1.17 | 15 | 5.0% | bull | ❌ | sharpe 0.95 < 1.0; profit_factor 1.17 < 1.5 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +0.28% -> $10,028
- **Top 5 균등배분**: +3.93% -> $10,393
