# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-29T20:17:50.682521Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-29T20:21:30.958744Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=2025188230, block=24)_
_Data Range: 0 ~ 8639 (8640봉)_
_Walk-Forward: 4개 윈도우 (train=5040h, test=1440h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
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
| 평균 수익률 | 23.79% |
| 최고 수익률 | 86.67% (price_action_momentum) |
| 최저 수익률 | -8.31% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +86.67% | 5.35 | 47.9% | 1.65 | 151 | 13.0% | 0/4 | FAIL |
| 2 | `momentum_quality` | +74.88% | 6.04 | 50.2% | 1.93 | 116 | 9.1% | 0/4 | FAIL |
| 3 | `volume_breakout` | +58.71% | 4.21 | 49.7% | 1.95 | 84 | 18.1% | 0/4 | FAIL |
| 4 | `lob_maker` | +47.58% | 3.05 | 44.1% | 1.40 | 119 | 17.8% | 0/4 | FAIL |
| 5 | `supertrend_multi` | +44.11% | 4.54 | 49.3% | 1.66 | 98 | 8.6% | 0/4 | FAIL |
| 6 | `acceleration_band` | +37.70% | 3.52 | 46.8% | 1.53 | 97 | 10.6% | 0/4 | FAIL |
| 7 | `narrow_range` | +35.17% | 4.01 | 47.6% | 1.68 | 87 | 6.4% | 0/4 | FAIL |
| 8 | `cmf` | +32.26% | 2.34 | 43.1% | 1.28 | 128 | 19.6% | 0/4 | FAIL |
| 9 | `htf_ema` | +27.90% | 2.89 | 47.0% | 1.58 | 68 | 12.5% | 0/4 | FAIL |
| 10 | `order_flow_imbalance_v2` | +26.21% | 2.17 | 43.6% | 1.39 | 82 | 16.6% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 61.3 | p100 | 6.04 | 2.04 | 1.93 | 116 | 9.1% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 59.3 | p95 | 5.35 | 1.99 | 1.65 | 151 | 13.0% | 0/4 | FAIL |
| 3 | `supertrend_multi` | 56.2 | p90 | 4.54 | 1.31 | 1.66 | 98 | 8.6% | 0/4 | FAIL |
| 4 | `wick_reversal` | 56.1 | p85 | 0.27 | 1.52 | 250.68 | 1 | 0.6% | 0/4 | FAIL |
| 5 | `narrow_range` | 53.9 | p80 | 4.01 | 1.65 | 1.68 | 87 | 6.4% | 0/4 | FAIL |
| 6 | `acceleration_band` | 51.9 | p76 | 3.52 | 0.88 | 1.53 | 97 | 10.6% | 0/4 | FAIL |
| 7 | `volatility_cluster` | 46.6 | p71 | 2.23 | 0.96 | 1.33 | 86 | 9.3% | 0/4 | FAIL |
| 8 | `linear_channel_rev` | 45.6 | p66 | 2.80 | 1.39 | 1.87 | 30 | 4.9% | 0/4 | FAIL |
| 9 | `lob_maker` | 42.3 | p61 | 3.05 | 2.49 | 1.40 | 119 | 17.8% | 0/4 | FAIL |
| 10 | `htf_ema` | 41.4 | p52 | 2.89 | 2.26 | 1.58 | 68 | 12.5% | 0/4 | FAIL |
| 11 | `roc_ma_cross` | 41.4 | p57 | 2.04 | 1.54 | 1.65 | 29 | 5.9% | 0/4 | FAIL |
| 12 | `cmf` | 40.9 | p47 | 2.34 | 1.79 | 1.28 | 128 | 19.6% | 0/4 | FAIL |
| 13 | `elder_impulse` | 40.3 | p42 | 1.28 | 1.37 | 1.30 | 54 | 7.4% | 0/4 | FAIL |
| 14 | `volume_breakout` | 37.8 | p38 | 4.21 | 4.42 | 1.95 | 84 | 18.1% | 0/4 | FAIL |
| 15 | `relative_volume` | 36.1 | p33 | 2.28 | 3.30 | 1.77 | 50 | 10.5% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +86.67% | 5.35 | 1.65 | 151 | 0/4 | FAIL |
| `momentum_quality` | +74.88% | 6.04 | 1.93 | 116 | 0/4 | FAIL |
| `volume_breakout` | +58.71% | 4.21 | 1.95 | 84 | 0/4 | FAIL |
| `lob_maker` | +47.58% | 3.05 | 1.40 | 119 | 0/4 | FAIL |
| `supertrend_multi` | +44.11% | 4.54 | 1.66 | 98 | 0/4 | FAIL |
| `acceleration_band` | +37.70% | 3.52 | 1.53 | 97 | 0/4 | FAIL |
| `narrow_range` | +35.17% | 4.01 | 1.68 | 87 | 0/4 | FAIL |
| `cmf` | +32.26% | 2.34 | 1.28 | 128 | 0/4 | FAIL |
| `htf_ema` | +27.90% | 2.89 | 1.58 | 68 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +26.21% | 2.17 | 1.39 | 82 | 0/4 | FAIL |
| `volatility_cluster` | +16.57% | 2.23 | 1.33 | 86 | 0/4 | FAIL |
| `relative_volume` | +14.81% | 2.28 | 1.77 | 50 | 0/4 | FAIL |
| `linear_channel_rev` | +12.67% | 2.80 | 1.87 | 30 | 0/4 | FAIL |
| `roc_ma_cross` | +9.19% | 2.04 | 1.65 | 29 | 0/4 | FAIL |
| `elder_impulse` | +7.96% | 1.28 | 1.30 | 54 | 0/4 | FAIL |
| `frama` | +2.56% | 0.18 | 1.09 | 89 | 0/4 | FAIL |
| `dema_cross` | +1.77% | 0.61 | 1.39 | 13 | 0/4 | FAIL |
| `wick_reversal` | +0.88% | 0.27 | 250.68 | 1 | 0/4 | FAIL |
| `value_area` | -0.59% | -0.17 | 1.04 | 27 | 0/4 | FAIL |
| `positional_scaling` | -1.56% | -0.42 | 0.98 | 20 | 0/4 | FAIL |
| `price_cluster` | -3.83% | -0.72 | 0.93 | 31 | 0/4 | FAIL |
| `engulfing_zone` | -8.31% | -1.94 | 0.68 | 24 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.382 > 0.05 (우연 가능성) (x1), mc_p_value 0.156 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.346 > 0.05 (우연 가능성) (x1), mc_p_value 0.222 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | sharpe -3.08 < 1.0 (x1), max_drawdown 32.6% > 20% (x1), profit_factor 0.71 < 1.5 (x1) |
| `lob_maker` | sharpe -1.11 < 1.0 (x1), max_drawdown 33.2% > 20% (x1), profit_factor 0.91 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.36 < 1.5 (x1), mc_p_value 0.396 > 0.05 (우연 가능성) (x1), mc_p_value 0.280 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.30 < 1.5 (x1), mc_p_value 0.404 > 0.05 (우연 가능성) (x1), mc_p_value 0.300 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.430 > 0.05 (우연 가능성) (x1), mc_p_value 0.260 > 0.05 (우연 가능성) (x1) |
| `cmf` | sharpe -0.25 < 1.0 (x1), max_drawdown 21.7% > 20% (x1), profit_factor 1.00 < 1.5 (x1) |
| `htf_ema` | sharpe -0.63 < 1.0 (x1), max_drawdown 21.7% > 20% (x1), profit_factor 0.94 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe -2.23 < 1.0 (x1), max_drawdown 25.5% > 20% (x1), profit_factor 0.79 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.21 < 1.5 (x1), mc_p_value 0.472 > 0.05 (우연 가능성) (x1), mc_p_value 0.358 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | sharpe -2.46 < 1.0 (x1), max_drawdown 20.2% > 20% (x1), profit_factor 0.73 < 1.5 (x1) |
| `linear_channel_rev` | profit_factor 1.26 < 1.5 (x1), mc_p_value 0.428 > 0.05 (우연 가능성) (x1), mc_p_value 0.438 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe -0.53 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1), mc_p_value 0.506 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | sharpe -0.53 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1), mc_p_value 0.530 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe -3.02 < 1.0 (x1), max_drawdown 36.2% > 20% (x1), profit_factor 0.72 < 1.5 (x1) |
| `dema_cross` | profit_factor 1.46 < 1.5 (x1), mc_p_value 0.472 > 0.05 (우연 가능성) (x1), trades 12 < 15 (x1) |
| `wick_reversal` | trades 1 < 15 (x2), no trades generated (x1), sharpe -2.06 < 1.0 (x1) |
| `value_area` | profit_factor 1.03 < 1.5 (x2), sharpe 0.04 < 1.0 (x1), mc_p_value 0.508 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 0.72 < 1.5 (x2), sharpe 0.51 < 1.0 (x1), profit_factor 1.15 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.396 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.472 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.72 < 1.5 | 3 |
| profit_factor 0.71 < 1.5 | 2 |
| mc_p_value 0.256 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.404 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.344 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.26 < 1.5 | 2 |
| mc_p_value 0.430 > 0.05 (우연 가능성) | 2 |
| max_drawdown 21.7% > 20% | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +23.79% -> $12,379
- **Top 5 균등배분**: +62.39% -> $16,239


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-29T20:25:18.859806Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=551998509, block=24)_
_Data Range: 0 ~ 8639 (8640봉)_
_Walk-Forward: 4개 윈도우 (train=5040h, test=1440h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
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
| 평균 수익률 | 12.43% |
| 최고 수익률 | 64.46% (price_action_momentum) |
| 최저 수익률 | -5.86% (price_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +64.46% | 4.31 | 45.6% | 1.50 | 159 | 12.1% | 0/4 | FAIL |
| 2 | `cmf` | +40.30% | 2.92 | 44.1% | 1.44 | 110 | 17.0% | 0/4 | FAIL |
| 3 | `lob_maker` | +33.65% | 2.68 | 43.6% | 1.34 | 118 | 17.4% | 0/4 | FAIL |
| 4 | `volume_breakout` | +33.63% | 3.17 | 45.0% | 1.54 | 86 | 12.7% | 0/4 | FAIL |
| 5 | `momentum_quality` | +32.38% | 3.43 | 45.8% | 1.43 | 118 | 10.9% | 0/4 | FAIL |
| 6 | `supertrend_multi` | +26.39% | 2.69 | 43.2% | 1.35 | 114 | 14.3% | 0/4 | FAIL |
| 7 | `linear_channel_rev` | +9.83% | 2.41 | 47.5% | 1.68 | 28 | 4.1% | 0/4 | FAIL |
| 8 | `narrow_range` | +9.08% | 1.28 | 41.9% | 1.20 | 91 | 15.8% | 0/4 | FAIL |
| 9 | `volatility_cluster` | +7.94% | 1.19 | 40.7% | 1.20 | 72 | 8.9% | 0/4 | FAIL |
| 10 | `elder_impulse` | +6.63% | 1.05 | 38.7% | 1.20 | 60 | 9.5% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 76.0 | p100 | 4.31 | 1.99 | 1.50 | 159 | 12.1% | 0/4 | FAIL |
| 2 | `momentum_quality` | 72.2 | p95 | 3.43 | 0.67 | 1.43 | 118 | 10.9% | 0/4 | FAIL |
| 3 | `linear_channel_rev` | 67.1 | p90 | 2.41 | 0.45 | 1.68 | 28 | 4.1% | 0/4 | FAIL |
| 4 | `volume_breakout` | 63.1 | p85 | 3.17 | 1.90 | 1.54 | 86 | 12.7% | 0/4 | FAIL |
| 5 | `lob_maker` | 62.7 | p80 | 2.68 | 0.53 | 1.34 | 118 | 17.4% | 0/4 | FAIL |
| 6 | `supertrend_multi` | 60.1 | p76 | 2.69 | 1.71 | 1.35 | 114 | 14.3% | 0/4 | FAIL |
| 7 | `cmf` | 58.3 | p71 | 2.92 | 2.20 | 1.44 | 110 | 17.0% | 0/4 | FAIL |
| 8 | `volatility_cluster` | 51.8 | p66 | 1.19 | 1.23 | 1.20 | 72 | 8.9% | 0/4 | FAIL |
| 9 | `narrow_range` | 50.6 | p61 | 1.28 | 0.80 | 1.20 | 91 | 15.8% | 0/4 | FAIL |
| 10 | `elder_impulse` | 50.6 | p57 | 1.05 | 0.98 | 1.20 | 60 | 9.5% | 0/4 | FAIL |
| 11 | `acceleration_band` | 50.2 | p52 | 0.64 | 0.27 | 1.10 | 98 | 13.7% | 0/4 | FAIL |
| 12 | `positional_scaling` | 46.9 | p47 | 0.95 | 1.29 | 1.29 | 26 | 9.0% | 0/4 | FAIL |
| 13 | `dema_cross` | 43.9 | p42 | 0.13 | 0.74 | 1.10 | 13 | 5.0% | 0/4 | FAIL |
| 14 | `htf_ema` | 43.2 | p38 | 0.66 | 1.31 | 1.14 | 76 | 15.6% | 0/4 | FAIL |
| 15 | `relative_volume` | 43.1 | p33 | 0.08 | 1.07 | 1.05 | 56 | 8.6% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +64.46% | 4.31 | 1.50 | 159 | 0/4 | FAIL |
| `cmf` | +40.30% | 2.92 | 1.44 | 110 | 0/4 | FAIL |
| `lob_maker` | +33.65% | 2.68 | 1.34 | 118 | 0/4 | FAIL |
| `volume_breakout` | +33.63% | 3.17 | 1.54 | 86 | 0/4 | FAIL |
| `momentum_quality` | +32.38% | 3.43 | 1.43 | 118 | 0/4 | FAIL |
| `supertrend_multi` | +26.39% | 2.69 | 1.35 | 114 | 0/4 | FAIL |
| `linear_channel_rev` | +9.83% | 2.41 | 1.68 | 28 | 0/4 | FAIL |
| `narrow_range` | +9.08% | 1.28 | 1.20 | 91 | 0/4 | FAIL |
| `volatility_cluster` | +7.94% | 1.19 | 1.20 | 72 | 0/4 | FAIL |
| `elder_impulse` | +6.63% | 1.05 | 1.20 | 60 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +4.72% | 0.47 | 1.11 | 82 | 0/4 | FAIL |
| `htf_ema` | +4.72% | 0.66 | 1.14 | 76 | 0/4 | FAIL |
| `positional_scaling` | +4.67% | 0.95 | 1.29 | 26 | 0/4 | FAIL |
| `acceleration_band` | +4.31% | 0.64 | 1.10 | 98 | 0/4 | FAIL |
| `frama` | +1.03% | 0.24 | 1.07 | 82 | 0/4 | FAIL |
| `relative_volume` | +0.34% | 0.08 | 1.05 | 56 | 0/4 | FAIL |
| `dema_cross` | +0.21% | 0.13 | 1.10 | 13 | 0/4 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `roc_ma_cross` | -1.33% | -0.21 | 1.00 | 38 | 0/4 | FAIL |
| `value_area` | -1.65% | -0.51 | 0.98 | 32 | 0/4 | FAIL |
| `engulfing_zone` | -1.95% | -0.60 | 1.07 | 23 | 0/4 | FAIL |
| `price_cluster` | -5.86% | -0.96 | 0.87 | 39 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.198 > 0.05 (우연 가능성) (x1), mc_p_value 0.194 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1) |
| `cmf` | sharpe 0.16 < 1.0 (x1), max_drawdown 22.6% > 20% (x1), profit_factor 1.04 < 1.5 (x1) |
| `lob_maker` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.400 > 0.05 (우연 가능성) (x1), max_drawdown 21.2% > 20% (x1) |
| `volume_breakout` | sharpe 0.44 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1), mc_p_value 0.514 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | profit_factor 1.41 < 1.5 (x1), mc_p_value 0.324 > 0.05 (우연 가능성) (x1), profit_factor 1.48 < 1.5 (x1) |
| `supertrend_multi` | profit_factor 1.41 < 1.5 (x1), mc_p_value 0.382 > 0.05 (우연 가능성) (x1), mc_p_value 0.250 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | profit_factor 1.49 < 1.5 (x1), mc_p_value 0.448 > 0.05 (우연 가능성) (x1), mc_p_value 0.438 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.14 < 1.5 (x2), sharpe 0.73 < 1.0 (x1), profit_factor 1.12 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.48 < 1.5 (x1), mc_p_value 0.372 > 0.05 (우연 가능성) (x1), profit_factor 1.23 < 1.5 (x1) |
| `elder_impulse` | sharpe 0.17 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.470 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe -1.83 < 1.0 (x1), max_drawdown 24.8% > 20% (x1), profit_factor 0.83 < 1.5 (x1) |
| `htf_ema` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.420 > 0.05 (우연 가능성) (x1), profit_factor 1.29 < 1.5 (x1) |
| `positional_scaling` | sharpe 0.57 < 1.0 (x1), profit_factor 1.16 < 1.5 (x1), mc_p_value 0.468 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.13 < 1.5 (x2), sharpe 0.94 < 1.0 (x1), mc_p_value 0.442 > 0.05 (우연 가능성) (x1) |
| `frama` | max_drawdown 24.9% > 20% (x1), profit_factor 1.22 < 1.5 (x1), mc_p_value 0.414 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | sharpe -1.70 < 1.0 (x1), profit_factor 0.80 < 1.5 (x1), mc_p_value 0.554 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | trades 11 < 15 (x2), sharpe -0.70 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1) |
| `wick_reversal` | no trades generated (x4) |
| `roc_ma_cross` | sharpe -0.18 < 1.0 (x1), profit_factor 1.01 < 1.5 (x1), mc_p_value 0.504 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe 0.29 < 1.0 (x1), profit_factor 1.09 < 1.5 (x1), mc_p_value 0.516 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.06 < 1.5 | 4 |
| no trades generated | 4 |
| profit_factor 1.24 < 1.5 | 3 |
| sharpe 0.44 < 1.0 | 3 |
| profit_factor 1.07 < 1.5 | 3 |
| profit_factor 1.14 < 1.5 | 3 |
| sharpe 0.87 < 1.0 | 3 |
| mc_p_value 0.494 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.05 < 1.5 | 3 |
| profit_factor 1.13 < 1.5 | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +12.43% -> $11,243
- **Top 5 균등배분**: +40.88% -> $14,088


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-29T20:29:05.225893Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=346159679, block=24)_
_Data Range: 0 ~ 8639 (8640봉)_
_Walk-Forward: 4개 윈도우 (train=5040h, test=1440h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
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
| 평균 수익률 | 15.69% |
| 최고 수익률 | 50.93% (lob_maker) |
| 최저 수익률 | -8.61% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `lob_maker` | +50.93% | 3.47 | 45.1% | 1.42 | 124 | 16.1% | 0/4 | FAIL |
| 2 | `volatility_cluster` | +36.15% | 4.17 | 48.3% | 1.71 | 85 | 10.5% | 0/4 | FAIL |
| 3 | `momentum_quality` | +34.45% | 3.65 | 45.7% | 1.50 | 108 | 8.3% | 0/4 | FAIL |
| 4 | `price_action_momentum` | +33.12% | 2.71 | 41.5% | 1.32 | 144 | 14.8% | 0/4 | FAIL |
| 5 | `volume_breakout` | +32.03% | 3.16 | 46.2% | 1.48 | 89 | 11.9% | 0/4 | FAIL |
| 6 | `elder_impulse` | +29.35% | 3.90 | 52.7% | 1.86 | 53 | 6.4% | 0/4 | FAIL |
| 7 | `acceleration_band` | +27.64% | 2.71 | 44.1% | 1.39 | 98 | 14.7% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | +26.34% | 2.47 | 44.2% | 1.37 | 82 | 15.5% | 0/4 | FAIL |
| 9 | `narrow_range` | +22.48% | 2.52 | 42.5% | 1.35 | 104 | 12.5% | 0/4 | FAIL |
| 10 | `supertrend_multi` | +17.73% | 2.06 | 41.2% | 1.26 | 113 | 11.3% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 75.7 | p100 | 3.65 | 0.99 | 1.50 | 108 | 8.3% | 0/4 | FAIL |
| 2 | `elder_impulse` | 75.2 | p95 | 3.90 | 1.17 | 1.86 | 53 | 6.4% | 0/4 | FAIL |
| 3 | `volatility_cluster` | 75.1 | p90 | 4.17 | 1.33 | 1.71 | 85 | 10.5% | 0/4 | FAIL |
| 4 | `lob_maker` | 70.5 | p85 | 3.47 | 1.13 | 1.42 | 124 | 16.1% | 0/4 | FAIL |
| 5 | `volume_breakout` | 67.9 | p80 | 3.16 | 1.25 | 1.48 | 89 | 11.9% | 0/4 | FAIL |
| 6 | `price_action_momentum` | 66.8 | p76 | 2.71 | 1.53 | 1.32 | 144 | 14.8% | 0/4 | FAIL |
| 7 | `narrow_range` | 66.5 | p71 | 2.52 | 0.88 | 1.35 | 104 | 12.5% | 0/4 | FAIL |
| 8 | `acceleration_band` | 65.9 | p66 | 2.71 | 0.87 | 1.39 | 98 | 14.7% | 0/4 | FAIL |
| 9 | `supertrend_multi` | 65.7 | p61 | 2.06 | 0.75 | 1.26 | 113 | 11.3% | 0/4 | FAIL |
| 10 | `value_area` | 65.3 | p57 | 2.40 | 1.57 | 1.96 | 26 | 4.5% | 0/4 | FAIL |
| 11 | `frama` | 62.2 | p52 | 1.98 | 0.70 | 1.30 | 79 | 11.5% | 0/4 | FAIL |
| 12 | `relative_volume` | 61.9 | p47 | 2.04 | 0.90 | 1.39 | 57 | 8.5% | 0/4 | FAIL |
| 13 | `order_flow_imbalance_v2` | 60.6 | p42 | 2.47 | 1.27 | 1.37 | 82 | 15.5% | 0/4 | FAIL |
| 14 | `htf_ema` | 59.9 | p38 | 1.84 | 1.13 | 1.33 | 67 | 9.2% | 0/4 | FAIL |
| 15 | `linear_channel_rev` | 47.5 | p33 | -0.41 | 0.25 | 0.95 | 31 | 6.2% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `lob_maker` | +50.93% | 3.47 | 1.42 | 124 | 0/4 | FAIL |
| `volatility_cluster` | +36.15% | 4.17 | 1.71 | 85 | 0/4 | FAIL |
| `momentum_quality` | +34.45% | 3.65 | 1.50 | 108 | 0/4 | FAIL |
| `price_action_momentum` | +33.12% | 2.71 | 1.32 | 144 | 0/4 | FAIL |
| `volume_breakout` | +32.03% | 3.16 | 1.48 | 89 | 0/4 | FAIL |
| `elder_impulse` | +29.35% | 3.90 | 1.86 | 53 | 0/4 | FAIL |
| `acceleration_band` | +27.64% | 2.71 | 1.39 | 98 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +26.34% | 2.47 | 1.37 | 82 | 0/4 | FAIL |
| `narrow_range` | +22.48% | 2.52 | 1.35 | 104 | 0/4 | FAIL |
| `supertrend_multi` | +17.73% | 2.06 | 1.26 | 113 | 0/4 | FAIL |
| `frama` | +17.10% | 1.98 | 1.30 | 79 | 0/4 | FAIL |
| `htf_ema` | +14.90% | 1.84 | 1.33 | 67 | 0/4 | FAIL |
| `relative_volume` | +11.99% | 2.04 | 1.39 | 57 | 0/4 | FAIL |
| `value_area` | +9.41% | 2.40 | 1.96 | 26 | 0/4 | FAIL |
| `cmf` | +5.29% | 0.41 | 1.09 | 117 | 0/4 | FAIL |
| `dema_cross` | +1.03% | 0.22 | 1.47 | 12 | 0/4 | FAIL |
| `wick_reversal` | -0.39% | -0.51 | 0.00 | 0 | 0/4 | FAIL |
| `linear_channel_rev` | -1.86% | -0.41 | 0.95 | 31 | 0/4 | FAIL |
| `price_cluster` | -3.47% | -0.64 | 0.95 | 34 | 0/4 | FAIL |
| `positional_scaling` | -5.06% | -1.29 | 0.80 | 28 | 0/4 | FAIL |
| `roc_ma_cross` | -5.35% | -1.37 | 0.88 | 36 | 0/4 | FAIL |
| `engulfing_zone` | -8.61% | -2.06 | 0.66 | 21 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `lob_maker` | mc_p_value 0.234 > 0.05 (우연 가능성) (x1), max_drawdown 22.9% > 20% (x1), profit_factor 1.32 < 1.5 (x1) |
| `volatility_cluster` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.362 > 0.05 (우연 가능성) (x1), profit_factor 1.46 < 1.5 (x1) |
| `momentum_quality` | mc_p_value 0.228 > 0.05 (우연 가능성) (x1), profit_factor 1.38 < 1.5 (x1), mc_p_value 0.344 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.300 > 0.05 (우연 가능성) (x1), sharpe 0.16 < 1.0 (x1) |
| `volume_breakout` | mc_p_value 0.328 > 0.05 (우연 가능성) (x1), profit_factor 1.42 < 1.5 (x1), mc_p_value 0.322 > 0.05 (우연 가능성) (x1) |
| `elder_impulse` | mc_p_value 0.330 > 0.05 (우연 가능성) (x1), mc_p_value 0.334 > 0.05 (우연 가능성) (x1), mc_p_value 0.418 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | mc_p_value 0.318 > 0.05 (우연 가능성) (x1), max_drawdown 21.2% > 20% (x1), profit_factor 1.33 < 1.5 (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.324 > 0.05 (우연 가능성) (x1), max_drawdown 23.3% > 20% (x1), profit_factor 1.24 < 1.5 (x1) |
| `narrow_range` | profit_factor 1.30 < 1.5 (x1), mc_p_value 0.352 > 0.05 (우연 가능성) (x1), mc_p_value 0.268 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | profit_factor 1.35 < 1.5 (x2), profit_factor 1.15 < 1.5 (x1), mc_p_value 0.460 > 0.05 (우연 가능성) (x1) |
| `frama` | profit_factor 1.22 < 1.5 (x1), mc_p_value 0.416 > 0.05 (우연 가능성) (x1), profit_factor 1.16 < 1.5 (x1) |
| `htf_ema` | profit_factor 1.30 < 1.5 (x1), mc_p_value 0.426 > 0.05 (우연 가능성) (x1), sharpe 0.24 < 1.0 (x1) |
| `relative_volume` | mc_p_value 0.384 > 0.05 (우연 가능성) (x1), profit_factor 1.32 < 1.5 (x1), mc_p_value 0.418 > 0.05 (우연 가능성) (x1) |
| `value_area` | mc_p_value 0.396 > 0.05 (우연 가능성) (x1), mc_p_value 0.452 > 0.05 (우연 가능성) (x1), profit_factor 1.40 < 1.5 (x1) |
| `cmf` | profit_factor 1.29 < 1.5 (x1), mc_p_value 0.362 > 0.05 (우연 가능성) (x1), sharpe -1.94 < 1.0 (x1) |
| `dema_cross` | trades 13 < 15 (x1), sharpe -1.31 < 1.0 (x1), profit_factor 0.74 < 1.5 (x1) |
| `wick_reversal` | no trades generated (x3), sharpe -2.04 < 1.0 (x1), profit_factor 0.00 < 1.5 (x1) |
| `linear_channel_rev` | sharpe -0.23 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1), mc_p_value 0.506 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | profit_factor 1.32 < 1.5 (x1), mc_p_value 0.484 > 0.05 (우연 가능성) (x1), sharpe 0.51 < 1.0 (x1) |
| `positional_scaling` | mc_p_value 0.542 > 0.05 (우연 가능성) (x2), sharpe -2.25 < 1.0 (x1), profit_factor 0.63 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.32 < 1.5 | 5 |
| profit_factor 1.12 < 1.5 | 4 |
| profit_factor 1.35 < 1.5 | 3 |
| mc_p_value 0.418 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.420 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.396 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.88 < 1.5 | 3 |
| no trades generated | 3 |
| mc_p_value 0.416 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.362 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +15.69% -> $11,569
- **Top 5 균등배분**: +37.34% -> $13,734
