# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-28T14:51:38.571865Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-28T15:03:13.023780Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=1270029149, block=36)_
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
| 평균 수익률 | 17.75% |
| 최고 수익률 | 84.91% (momentum_quality) |
| 최저 수익률 | -13.90% (price_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +84.91% | 6.71 | 53.4% | 2.06 | 116 | 8.3% | 0/4 | FAIL |
| 2 | `cmf` | +73.59% | 4.52 | 46.6% | 1.55 | 134 | 18.6% | 0/4 | FAIL |
| 3 | `price_action_momentum` | +57.25% | 4.22 | 45.2% | 1.49 | 153 | 11.3% | 0/4 | FAIL |
| 4 | `supertrend_multi` | +38.34% | 3.81 | 45.7% | 1.48 | 122 | 10.3% | 0/4 | FAIL |
| 5 | `acceleration_band` | +36.80% | 3.46 | 45.5% | 1.51 | 100 | 11.5% | 0/4 | FAIL |
| 6 | `volatility_cluster` | +21.90% | 2.99 | 45.5% | 1.48 | 79 | 10.5% | 0/4 | FAIL |
| 7 | `narrow_range` | +21.67% | 2.62 | 45.3% | 1.39 | 90 | 10.5% | 0/4 | FAIL |
| 8 | `htf_ema` | +14.43% | 1.68 | 42.1% | 1.26 | 77 | 14.7% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | +11.49% | 1.19 | 40.0% | 1.18 | 89 | 20.5% | 0/4 | FAIL |
| 10 | `elder_impulse` | +11.02% | 1.66 | 42.3% | 1.32 | 56 | 11.0% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 64.8 | p100 | 6.71 | 0.37 | 2.06 | 116 | 8.3% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 58.5 | p95 | 4.22 | 0.32 | 1.49 | 153 | 11.3% | 0/4 | FAIL |
| 3 | `supertrend_multi` | 55.5 | p90 | 3.81 | 0.19 | 1.48 | 122 | 10.3% | 0/4 | FAIL |
| 4 | `wick_reversal` | 52.8 | p85 | 0.46 | 1.67 | 500.00 | 1 | 0.4% | 0/4 | FAIL |
| 5 | `cmf` | 49.9 | p80 | 4.52 | 0.80 | 1.55 | 134 | 18.6% | 0/4 | FAIL |
| 6 | `acceleration_band` | 48.9 | p76 | 3.46 | 0.71 | 1.51 | 100 | 11.5% | 0/4 | FAIL |
| 7 | `volatility_cluster` | 48.0 | p71 | 2.99 | 0.31 | 1.48 | 79 | 10.5% | 0/4 | FAIL |
| 8 | `narrow_range` | 44.6 | p66 | 2.62 | 0.96 | 1.39 | 90 | 10.5% | 0/4 | FAIL |
| 9 | `roc_ma_cross` | 41.2 | p61 | 1.61 | 0.40 | 1.38 | 36 | 7.3% | 0/4 | FAIL |
| 10 | `elder_impulse` | 40.5 | p57 | 1.66 | 0.40 | 1.32 | 56 | 11.0% | 0/4 | FAIL |
| 11 | `htf_ema` | 37.5 | p52 | 1.68 | 0.92 | 1.26 | 77 | 14.7% | 0/4 | FAIL |
| 12 | `lob_maker` | 37.1 | p47 | 1.04 | 0.71 | 1.13 | 130 | 21.0% | 0/4 | FAIL |
| 13 | `volume_breakout` | 36.9 | p42 | 1.27 | 0.50 | 1.19 | 96 | 19.3% | 0/4 | FAIL |
| 14 | `dema_cross` | 34.0 | p38 | 0.11 | 0.87 | 1.11 | 14 | 4.4% | 0/4 | FAIL |
| 15 | `linear_channel_rev` | 33.9 | p33 | 0.59 | 1.08 | 1.18 | 34 | 8.0% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +84.91% | 6.71 | 2.06 | 116 | 0/4 | FAIL |
| `cmf` | +73.59% | 4.52 | 1.55 | 134 | 0/4 | FAIL |
| `price_action_momentum` | +57.25% | 4.22 | 1.49 | 153 | 0/4 | FAIL |
| `supertrend_multi` | +38.34% | 3.81 | 1.48 | 122 | 0/4 | FAIL |
| `acceleration_band` | +36.80% | 3.46 | 1.51 | 100 | 0/4 | FAIL |
| `volatility_cluster` | +21.90% | 2.99 | 1.48 | 79 | 0/4 | FAIL |
| `narrow_range` | +21.67% | 2.62 | 1.39 | 90 | 0/4 | FAIL |
| `htf_ema` | +14.43% | 1.68 | 1.26 | 77 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +11.49% | 1.19 | 1.18 | 89 | 0/4 | FAIL |
| `elder_impulse` | +11.02% | 1.66 | 1.32 | 56 | 0/4 | FAIL |
| `volume_breakout` | +10.93% | 1.27 | 1.19 | 96 | 0/4 | FAIL |
| `lob_maker` | +10.71% | 1.04 | 1.13 | 130 | 0/4 | FAIL |
| `roc_ma_cross` | +7.34% | 1.61 | 1.38 | 36 | 0/4 | FAIL |
| `engulfing_zone` | +4.50% | 0.86 | 1.61 | 17 | 0/4 | FAIL |
| `positional_scaling` | +2.97% | 0.63 | 1.25 | 30 | 0/4 | FAIL |
| `linear_channel_rev` | +2.30% | 0.59 | 1.18 | 34 | 0/4 | FAIL |
| `wick_reversal` | +0.98% | 0.46 | 500.00 | 1 | 0/4 | FAIL |
| `dema_cross` | +0.07% | 0.11 | 1.11 | 14 | 0/4 | FAIL |
| `relative_volume` | -0.03% | -0.10 | 1.03 | 59 | 0/4 | FAIL |
| `frama` | -2.21% | -0.16 | 1.01 | 80 | 0/4 | FAIL |
| `value_area` | -4.48% | -1.59 | 0.71 | 18 | 0/4 | FAIL |
| `price_cluster` | -13.90% | -2.68 | 0.64 | 34 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | mc_p_value 0.226 > 0.05 (우연 가능성) (x1), mc_p_value 0.224 > 0.05 (우연 가능성) (x1), mc_p_value 0.234 > 0.05 (우연 가능성) (x1) |
| `cmf` | max_drawdown 26.1% > 20% (x1), profit_factor 1.45 < 1.5 (x1), mc_p_value 0.306 > 0.05 (우연 가능성) (x1) |
| `price_action_momentum` | mc_p_value 0.266 > 0.05 (우연 가능성) (x1), mc_p_value 0.284 > 0.05 (우연 가능성) (x1), profit_factor 1.45 < 1.5 (x1) |
| `supertrend_multi` | mc_p_value 0.324 > 0.05 (우연 가능성) (x1), profit_factor 1.49 < 1.5 (x1), mc_p_value 0.338 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | mc_p_value 0.326 > 0.05 (우연 가능성) (x1), profit_factor 1.48 < 1.5 (x1), mc_p_value 0.358 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | mc_p_value 0.384 > 0.05 (우연 가능성) (x1), profit_factor 1.39 < 1.5 (x1), mc_p_value 0.396 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.34 < 1.5 (x1), mc_p_value 0.400 > 0.05 (우연 가능성) (x1), profit_factor 1.44 < 1.5 (x1) |
| `htf_ema` | mc_p_value 0.406 > 0.05 (우연 가능성) (x1), sharpe 0.58 < 1.0 (x1), profit_factor 1.10 < 1.5 (x1) |
| `order_flow_imbalance_v2` | sharpe 0.11 < 1.0 (x1), max_drawdown 27.1% > 20% (x1), profit_factor 1.04 < 1.5 (x1) |
| `elder_impulse` | profit_factor 1.40 < 1.5 (x1), mc_p_value 0.430 > 0.05 (우연 가능성) (x1), profit_factor 1.20 < 1.5 (x1) |
| `volume_breakout` | sharpe 0.46 < 1.0 (x1), max_drawdown 22.5% > 20% (x1), profit_factor 1.08 < 1.5 (x1) |
| `lob_maker` | max_drawdown 27.2% > 20% (x2), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.396 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 1.44 < 1.5 (x2), profit_factor 1.43 < 1.5 (x1), mc_p_value 0.466 > 0.05 (우연 가능성) (x1) |
| `engulfing_zone` | sharpe 0.12 < 1.0 (x1), profit_factor 1.07 < 1.5 (x1), mc_p_value 0.496 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | sharpe -1.37 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1), mc_p_value 0.528 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe -0.52 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1), mc_p_value 0.486 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | trades 1 < 15 (x3), sharpe -2.08 < 1.0 (x1), profit_factor 0.00 < 1.5 (x1) |
| `dema_cross` | sharpe 0.41 < 1.0 (x1), profit_factor 1.18 < 1.5 (x1), trades 10 < 15 (x1) |
| `relative_volume` | profit_factor 1.36 < 1.5 (x1), mc_p_value 0.462 > 0.05 (우연 가능성) (x1), sharpe 0.32 < 1.0 (x1) |
| `frama` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.454 > 0.05 (우연 가능성) (x1), sharpe -0.41 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.478 > 0.05 (우연 가능성) | 4 |
| profit_factor 1.45 < 1.5 | 3 |
| profit_factor 1.44 < 1.5 | 3 |
| profit_factor 1.25 < 1.5 | 3 |
| profit_factor 1.04 < 1.5 | 3 |
| mc_p_value 0.448 > 0.05 (우연 가능성) | 3 |
| trades 1 < 15 | 3 |
| mc_p_value 0.568 > 0.05 (우연 가능성) | 3 |
| mc_p_value 0.324 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.40 < 1.5 | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +17.75% -> $11,775
- **Top 5 균등배분**: +58.18% -> $15,818


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-28T15:19:03.882680Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=1613833928, block=36)_
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
| 평균 수익률 | 18.00% |
| 최고 수익률 | 85.25% (momentum_quality) |
| 최저 수익률 | -3.82% (value_area) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +85.25% | 4.94 | 47.8% | 1.77 | 125 | 10.7% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +83.19% | 4.56 | 44.5% | 1.63 | 162 | 14.4% | 0/4 | FAIL |
| 3 | `supertrend_multi` | +57.66% | 4.84 | 46.7% | 1.63 | 130 | 8.0% | 0/4 | FAIL |
| 4 | `order_flow_imbalance_v2` | +33.98% | 3.15 | 47.2% | 1.54 | 78 | 14.0% | 0/4 | FAIL |
| 5 | `cmf` | +25.68% | 1.63 | 41.0% | 1.28 | 117 | 20.1% | 0/4 | FAIL |
| 6 | `volume_breakout` | +22.63% | 2.34 | 44.3% | 1.40 | 86 | 12.9% | 0/4 | FAIL |
| 7 | `narrow_range` | +21.77% | 2.92 | 45.7% | 1.48 | 76 | 9.9% | 0/4 | FAIL |
| 8 | `volatility_cluster` | +18.20% | 2.35 | 43.7% | 1.39 | 80 | 9.4% | 0/4 | FAIL |
| 9 | `price_cluster` | +17.73% | 2.38 | 46.3% | 1.51 | 40 | 5.8% | 0/4 | FAIL |
| 10 | `acceleration_band` | +16.52% | 1.75 | 41.1% | 1.28 | 92 | 11.9% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 63.5 | p100 | 4.84 | 1.40 | 1.63 | 130 | 8.0% | 0/4 | FAIL |
| 2 | `wick_reversal` | 60.7 | p95 | 1.06 | 1.04 | 250.89 | 2 | 0.6% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 55.3 | p90 | 4.56 | 3.22 | 1.63 | 162 | 14.4% | 0/4 | FAIL |
| 4 | `momentum_quality` | 53.8 | p85 | 4.94 | 4.18 | 1.77 | 125 | 10.7% | 0/4 | FAIL |
| 5 | `narrow_range` | 50.4 | p80 | 2.92 | 0.56 | 1.48 | 76 | 9.9% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | 46.7 | p76 | 3.15 | 1.20 | 1.54 | 78 | 14.0% | 0/4 | FAIL |
| 7 | `price_cluster` | 46.6 | p71 | 2.38 | 0.94 | 1.51 | 40 | 5.8% | 0/4 | FAIL |
| 8 | `volatility_cluster` | 45.4 | p66 | 2.35 | 1.71 | 1.39 | 80 | 9.4% | 0/4 | FAIL |
| 9 | `volume_breakout` | 43.3 | p61 | 2.34 | 1.69 | 1.40 | 86 | 12.9% | 0/4 | FAIL |
| 10 | `acceleration_band` | 42.5 | p57 | 1.75 | 1.43 | 1.28 | 92 | 11.9% | 0/4 | FAIL |
| 11 | `roc_ma_cross` | 39.0 | p52 | 1.25 | 1.32 | 1.33 | 32 | 6.5% | 0/4 | FAIL |
| 12 | `lob_maker` | 38.9 | p47 | 0.84 | 0.78 | 1.12 | 116 | 16.4% | 0/4 | FAIL |
| 13 | `relative_volume` | 37.4 | p42 | 0.23 | 0.62 | 1.07 | 53 | 7.6% | 0/4 | FAIL |
| 14 | `linear_channel_rev` | 34.5 | p38 | 0.11 | 1.11 | 1.08 | 43 | 7.7% | 0/4 | FAIL |
| 15 | `cmf` | 34.0 | p33 | 1.63 | 2.90 | 1.28 | 117 | 20.1% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +85.25% | 4.94 | 1.77 | 125 | 0/4 | FAIL |
| `price_action_momentum` | +83.19% | 4.56 | 1.63 | 162 | 0/4 | FAIL |
| `supertrend_multi` | +57.66% | 4.84 | 1.63 | 130 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +33.98% | 3.15 | 1.54 | 78 | 0/4 | FAIL |
| `cmf` | +25.68% | 1.63 | 1.28 | 117 | 0/4 | FAIL |
| `volume_breakout` | +22.63% | 2.34 | 1.40 | 86 | 0/4 | FAIL |
| `narrow_range` | +21.77% | 2.92 | 1.48 | 76 | 0/4 | FAIL |
| `volatility_cluster` | +18.20% | 2.35 | 1.39 | 80 | 0/4 | FAIL |
| `price_cluster` | +17.73% | 2.38 | 1.51 | 40 | 0/4 | FAIL |
| `acceleration_band` | +16.52% | 1.75 | 1.28 | 92 | 0/4 | FAIL |
| `lob_maker` | +7.63% | 0.84 | 1.12 | 116 | 0/4 | FAIL |
| `roc_ma_cross` | +5.91% | 1.25 | 1.33 | 32 | 0/4 | FAIL |
| `frama` | +5.08% | 0.53 | 1.09 | 91 | 0/4 | FAIL |
| `htf_ema` | +2.37% | 0.20 | 1.10 | 64 | 0/4 | FAIL |
| `wick_reversal` | +1.33% | 1.06 | 250.89 | 2 | 0/4 | FAIL |
| `engulfing_zone` | +1.25% | 0.09 | 1.15 | 21 | 0/4 | FAIL |
| `relative_volume` | +0.67% | 0.23 | 1.07 | 53 | 0/4 | FAIL |
| `linear_channel_rev` | +0.17% | 0.11 | 1.08 | 43 | 0/4 | FAIL |
| `positional_scaling` | -1.57% | -0.36 | 1.08 | 28 | 0/4 | FAIL |
| `dema_cross` | -2.23% | -1.15 | 0.85 | 10 | 0/4 | FAIL |
| `elder_impulse` | -3.37% | -0.46 | 0.96 | 51 | 0/4 | FAIL |
| `value_area` | -3.82% | -1.52 | 0.72 | 16 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `momentum_quality` | profit_factor 1.28 < 1.5 (x1), mc_p_value 0.416 > 0.05 (우연 가능성) (x1), sharpe 0.06 < 1.0 (x1) |
| `price_action_momentum` | profit_factor 1.39 < 1.5 (x1), mc_p_value 0.298 > 0.05 (우연 가능성) (x1), sharpe 0.37 < 1.0 (x1) |
| `supertrend_multi` | mc_p_value 0.238 > 0.05 (우연 가능성) (x1), profit_factor 1.43 < 1.5 (x1), mc_p_value 0.306 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.35 < 1.5 (x1), mc_p_value 0.402 > 0.05 (우연 가능성) (x1), profit_factor 1.25 < 1.5 (x1) |
| `cmf` | sharpe 0.28 < 1.0 (x1), max_drawdown 22.8% > 20% (x1), profit_factor 1.05 < 1.5 (x1) |
| `volume_breakout` | profit_factor 1.36 < 1.5 (x1), mc_p_value 0.404 > 0.05 (우연 가능성) (x1), sharpe 0.64 < 1.0 (x1) |
| `narrow_range` | mc_p_value 0.348 > 0.05 (우연 가능성) (x1), profit_factor 1.37 < 1.5 (x1), mc_p_value 0.378 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | profit_factor 1.19 < 1.5 (x1), mc_p_value 0.450 > 0.05 (우연 가능성) (x1), sharpe 0.69 < 1.0 (x1) |
| `price_cluster` | profit_factor 1.29 < 1.5 (x1), mc_p_value 0.494 > 0.05 (우연 가능성) (x1), mc_p_value 0.384 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.18 < 1.5 (x2), mc_p_value 0.472 > 0.05 (우연 가능성) (x1), sharpe 0.36 < 1.0 (x1) |
| `lob_maker` | sharpe 0.02 < 1.0 (x1), max_drawdown 25.9% > 20% (x1), profit_factor 1.02 < 1.5 (x1) |
| `roc_ma_cross` | sharpe -0.61 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1), mc_p_value 0.542 > 0.05 (우연 가능성) (x1) |
| `frama` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.412 > 0.05 (우연 가능성) (x1), sharpe 0.53 < 1.0 (x1) |
| `htf_ema` | sharpe -2.40 < 1.0 (x1), profit_factor 0.73 < 1.5 (x1), mc_p_value 0.598 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | trades 2 < 15 (x3), sharpe 0.74 < 1.0 (x2), no trades generated (x1) |
| `engulfing_zone` | mc_p_value 0.464 > 0.05 (우연 가능성) (x1), mc_p_value 0.424 > 0.05 (우연 가능성) (x1), sharpe -0.65 < 1.0 (x1) |
| `relative_volume` | profit_factor 1.19 < 1.5 (x1), mc_p_value 0.454 > 0.05 (우연 가능성) (x1), sharpe -0.60 < 1.0 (x1) |
| `linear_channel_rev` | sharpe -1.03 < 1.0 (x1), profit_factor 0.87 < 1.5 (x1), mc_p_value 0.514 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | sharpe -1.57 < 1.0 (x1), profit_factor 0.76 < 1.5 (x1), mc_p_value 0.550 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | trades 10 < 15 (x2), trades 11 < 15 (x2), sharpe -1.23 < 1.0 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.43 < 1.5 | 3 |
| mc_p_value 0.408 > 0.05 (우연 가능성) | 3 |
| profit_factor 1.19 < 1.5 | 3 |
| profit_factor 1.18 < 1.5 | 3 |
| trades 2 < 15 | 3 |
| profit_factor 1.03 < 1.5 | 2 |
| mc_p_value 0.476 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.39 < 1.5 | 2 |
| profit_factor 1.05 < 1.5 | 2 |
| mc_p_value 0.514 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +18.00% -> $11,800
- **Top 5 균등배분**: +57.15% -> $15,715


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-28T15:32:10.410821Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=1014604195, block=36)_
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
| 평균 수익률 | 20.45% |
| 최고 수익률 | 72.64% (price_action_momentum) |
| 최저 수익률 | -11.19% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +72.64% | 5.16 | 48.1% | 1.66 | 150 | 13.2% | 0/4 | FAIL |
| 2 | `cmf` | +55.30% | 3.62 | 44.9% | 1.51 | 117 | 17.7% | 0/4 | FAIL |
| 3 | `htf_ema` | +48.27% | 4.35 | 50.1% | 1.85 | 72 | 9.3% | 0/4 | FAIL |
| 4 | `supertrend_multi` | +43.83% | 4.05 | 45.3% | 1.61 | 115 | 11.4% | 0/4 | FAIL |
| 5 | `volume_breakout` | +35.30% | 3.35 | 44.5% | 1.53 | 90 | 12.1% | 0/4 | FAIL |
| 6 | `acceleration_band` | +34.89% | 3.30 | 45.2% | 1.49 | 102 | 12.4% | 0/4 | FAIL |
| 7 | `momentum_quality` | +33.17% | 3.61 | 46.0% | 1.51 | 106 | 11.6% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | +31.01% | 2.66 | 43.4% | 1.50 | 80 | 17.6% | 0/4 | FAIL |
| 9 | `narrow_range` | +24.06% | 2.84 | 44.1% | 1.41 | 98 | 9.9% | 0/4 | FAIL |
| 10 | `elder_impulse` | +18.48% | 2.47 | 46.0% | 1.47 | 59 | 6.7% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 64.1 | p100 | 5.16 | 0.96 | 1.66 | 150 | 13.2% | 0/4 | FAIL |
| 2 | `wick_reversal` | 61.4 | p95 | 0.99 | 0.99 | 500.00 | 0 | 0.0% | 0/4 | FAIL |
| 3 | `momentum_quality` | 57.2 | p90 | 3.61 | 0.55 | 1.51 | 106 | 11.6% | 0/4 | FAIL |
| 4 | `narrow_range` | 53.9 | p85 | 2.84 | 0.65 | 1.41 | 98 | 9.9% | 0/4 | FAIL |
| 5 | `volume_breakout` | 53.2 | p80 | 3.35 | 0.73 | 1.53 | 90 | 12.1% | 0/4 | FAIL |
| 6 | `acceleration_band` | 51.2 | p76 | 3.30 | 1.21 | 1.49 | 102 | 12.4% | 0/4 | FAIL |
| 7 | `htf_ema` | 50.6 | p71 | 4.35 | 1.83 | 1.85 | 72 | 9.3% | 0/4 | FAIL |
| 8 | `supertrend_multi` | 49.9 | p66 | 4.05 | 2.27 | 1.61 | 115 | 11.4% | 0/4 | FAIL |
| 9 | `elder_impulse` | 48.8 | p61 | 2.47 | 0.96 | 1.47 | 59 | 6.7% | 0/4 | FAIL |
| 10 | `roc_ma_cross` | 46.9 | p57 | 2.39 | 0.84 | 1.61 | 37 | 6.8% | 0/4 | FAIL |
| 11 | `cmf` | 45.8 | p52 | 3.62 | 2.03 | 1.51 | 117 | 17.7% | 0/4 | FAIL |
| 12 | `volatility_cluster` | 44.5 | p47 | 2.07 | 1.22 | 1.34 | 76 | 11.4% | 0/4 | FAIL |
| 13 | `positional_scaling` | 44.1 | p42 | 1.72 | 0.75 | 1.54 | 24 | 6.0% | 0/4 | FAIL |
| 14 | `relative_volume` | 41.3 | p38 | 2.00 | 1.65 | 1.42 | 62 | 9.7% | 0/4 | FAIL |
| 15 | `frama` | 38.7 | p33 | 1.19 | 1.29 | 1.19 | 82 | 15.4% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +72.64% | 5.16 | 1.66 | 150 | 0/4 | FAIL |
| `cmf` | +55.30% | 3.62 | 1.51 | 117 | 0/4 | FAIL |
| `htf_ema` | +48.27% | 4.35 | 1.85 | 72 | 0/4 | FAIL |
| `supertrend_multi` | +43.83% | 4.05 | 1.61 | 115 | 0/4 | FAIL |
| `volume_breakout` | +35.30% | 3.35 | 1.53 | 90 | 0/4 | FAIL |
| `acceleration_band` | +34.89% | 3.30 | 1.49 | 102 | 0/4 | FAIL |
| `momentum_quality` | +33.17% | 3.61 | 1.51 | 106 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +31.01% | 2.66 | 1.50 | 80 | 0/4 | FAIL |
| `narrow_range` | +24.06% | 2.84 | 1.41 | 98 | 0/4 | FAIL |
| `elder_impulse` | +18.48% | 2.47 | 1.47 | 59 | 0/4 | FAIL |
| `volatility_cluster` | +14.37% | 2.07 | 1.34 | 76 | 0/4 | FAIL |
| `relative_volume` | +12.59% | 2.00 | 1.42 | 62 | 0/4 | FAIL |
| `roc_ma_cross` | +11.29% | 2.39 | 1.61 | 37 | 0/4 | FAIL |
| `frama` | +9.81% | 1.19 | 1.19 | 82 | 0/4 | FAIL |
| `linear_channel_rev` | +7.29% | 1.65 | 1.54 | 31 | 0/4 | FAIL |
| `positional_scaling` | +7.03% | 1.72 | 1.54 | 24 | 0/4 | FAIL |
| `price_cluster` | +1.55% | 0.34 | 1.17 | 38 | 0/4 | FAIL |
| `wick_reversal` | +0.95% | 0.99 | 500.00 | 0 | 0/4 | FAIL |
| `lob_maker` | +0.08% | 0.06 | 1.05 | 124 | 0/4 | FAIL |
| `value_area` | -0.05% | -0.03 | 1.10 | 21 | 0/4 | FAIL |
| `dema_cross` | -0.85% | -0.37 | 0.99 | 8 | 0/4 | FAIL |
| `engulfing_zone` | -11.19% | -2.63 | 0.59 | 23 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_action_momentum` | mc_p_value 0.308 > 0.05 (우연 가능성) (x1), mc_p_value 0.200 > 0.05 (우연 가능성) (x1), mc_p_value 0.302 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 1.43 < 1.5 (x1), mc_p_value 0.362 > 0.05 (우연 가능성) (x1), mc_p_value 0.232 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | mc_p_value 0.314 > 0.05 (우연 가능성) (x1), mc_p_value 0.292 > 0.05 (우연 가능성) (x1), mc_p_value 0.370 > 0.05 (우연 가능성) (x1) |
| `supertrend_multi` | mc_p_value 0.240 > 0.05 (우연 가능성) (x1), mc_p_value 0.244 > 0.05 (우연 가능성) (x1), profit_factor 1.31 < 1.5 (x1) |
| `volume_breakout` | mc_p_value 0.378 > 0.05 (우연 가능성) (x2), profit_factor 1.35 < 1.5 (x1), mc_p_value 0.426 > 0.05 (우연 가능성) (x1) |
| `acceleration_band` | profit_factor 1.19 < 1.5 (x1), mc_p_value 0.428 > 0.05 (우연 가능성) (x1), profit_factor 1.46 < 1.5 (x1) |
| `momentum_quality` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.392 > 0.05 (우연 가능성) (x1), mc_p_value 0.338 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | sharpe 0.18 < 1.0 (x1), max_drawdown 26.3% > 20% (x1), profit_factor 1.05 < 1.5 (x1) |
| `narrow_range` | profit_factor 1.37 < 1.5 (x1), mc_p_value 0.382 > 0.05 (우연 가능성) (x1), profit_factor 1.26 < 1.5 (x1) |
| `elder_impulse` | profit_factor 1.24 < 1.5 (x1), mc_p_value 0.462 > 0.05 (우연 가능성) (x1), mc_p_value 0.392 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | mc_p_value 0.372 > 0.05 (우연 가능성) (x1), sharpe 0.16 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1) |
| `relative_volume` | sharpe -0.62 < 1.0 (x1), profit_factor 0.95 < 1.5 (x1), mc_p_value 0.510 > 0.05 (우연 가능성) (x1) |
| `roc_ma_cross` | profit_factor 1.27 < 1.5 (x1), mc_p_value 0.468 > 0.05 (우연 가능성) (x1), mc_p_value 0.456 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe -0.47 < 1.0 (x1), max_drawdown 20.6% > 20% (x1), profit_factor 0.97 < 1.5 (x1) |
| `linear_channel_rev` | mc_p_value 0.434 > 0.05 (우연 가능성) (x1), mc_p_value 0.398 > 0.05 (우연 가능성) (x1), sharpe -1.64 < 1.0 (x1) |
| `positional_scaling` | profit_factor 1.42 < 1.5 (x1), mc_p_value 0.428 > 0.05 (우연 가능성) (x1), mc_p_value 0.456 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -1.33 < 1.0 (x1), profit_factor 0.84 < 1.5 (x1), mc_p_value 0.546 > 0.05 (우연 가능성) (x1) |
| `wick_reversal` | trades 1 < 15 (x2), no trades generated (x2) |
| `lob_maker` | max_drawdown 21.6% > 20% (x1), profit_factor 1.28 < 1.5 (x1), mc_p_value 0.456 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -1.56 < 1.0 (x1), profit_factor 0.72 < 1.5 (x1), mc_p_value 0.488 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.31 < 1.5 | 4 |
| mc_p_value 0.456 > 0.05 (우연 가능성) | 4 |
| profit_factor 1.28 < 1.5 | 3 |
| mc_p_value 0.426 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.432 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.378 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.428 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.318 > 0.05 (우연 가능성) | 2 |
| profit_factor 1.37 < 1.5 | 2 |
| mc_p_value 0.392 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +20.45% -> $12,045
- **Top 5 균등배분**: +51.07% -> $15,107
