# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-04T05:15:15.081871Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-04T05:22:40.207464Z_
_Symbol: BTC/USDT_
_Data Source: CSV fallback BTC/USDT 1h (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 23:00:00+00:00 (499일)_
_Walk-Forward: 8개 윈도우 (train=5040h, test=1440h)_
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
| 평균 수익률 | -3.82% |
| 최고 수익률 | 5.87% (supertrend_multi) |
| 최저 수익률 | -11.15% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +5.87% | 0.43 | 36.6% | 1.13 | 47 | 10.5% | 2/8 | FAIL |
| 2 | `price_cluster` | +2.50% | 0.40 | 39.4% | 1.12 | 45 | 11.8% | 1/8 | FAIL |
| 3 | `positional_scaling` | +1.40% | -0.10 | 36.5% | 1.17 | 36 | 10.4% | 1/8 | FAIL |
| 4 | `roc_ma_cross` | +1.01% | -0.11 | 37.9% | 1.15 | 40 | 9.1% | 2/8 | FAIL |
| 5 | `frama` | +0.04% | 0.01 | 38.9% | 1.06 | 42 | 9.6% | 0/8 | FAIL |
| 6 | `narrow_range` | -0.79% | -0.10 | 38.6% | 1.04 | 50 | 11.1% | 0/8 | FAIL |
| 7 | `htf_ema` | -1.30% | -0.15 | 38.5% | 1.02 | 45 | 11.1% | 0/8 | FAIL |
| 8 | `dema_cross` | -1.35% | -1.70 | 19.6% | 0.39 | 3 | 2.2% | 0/8 | FAIL |
| 9 | `volume_breakout` | -1.46% | -0.35 | 37.5% | 1.04 | 78 | 15.7% | 0/8 | FAIL |
| 10 | `momentum_quality` | -2.86% | -0.81 | 34.3% | 1.00 | 66 | 15.3% | 1/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 72.6 | p100 | 0.43 | 2.62 | 1.13 | 47 | 10.5% | 2/8 | FAIL |
| 2 | `price_cluster` | 69.2 | p95 | 0.40 | 1.43 | 1.12 | 45 | 11.8% | 1/8 | FAIL |
| 3 | `roc_ma_cross` | 66.3 | p90 | -0.11 | 2.66 | 1.15 | 40 | 9.1% | 2/8 | FAIL |
| 4 | `narrow_range` | 60.1 | p85 | -0.10 | 1.28 | 1.04 | 50 | 11.1% | 0/8 | FAIL |
| 5 | `positional_scaling` | 59.7 | p80 | -0.10 | 3.00 | 1.17 | 36 | 10.4% | 1/8 | FAIL |
| 6 | `frama` | 59.2 | p76 | 0.01 | 1.26 | 1.06 | 42 | 9.6% | 0/8 | FAIL |
| 7 | `order_flow_imbalance_v2` | 58.8 | p71 | -0.55 | 1.81 | 0.98 | 77 | 14.8% | 0/8 | FAIL |
| 8 | `volume_breakout` | 57.7 | p66 | -0.35 | 2.65 | 1.04 | 78 | 15.7% | 0/8 | FAIL |
| 9 | `htf_ema` | 57.4 | p61 | -0.15 | 1.26 | 1.02 | 45 | 11.1% | 0/8 | FAIL |
| 10 | `lob_maker` | 57.3 | p57 | -0.55 | 1.81 | 0.98 | 84 | 18.9% | 0/8 | FAIL |
| 11 | `price_action_momentum` | 54.4 | p52 | -0.85 | 2.97 | 1.01 | 82 | 18.2% | 1/8 | FAIL |
| 12 | `momentum_quality` | 53.8 | p47 | -0.81 | 2.93 | 1.00 | 66 | 15.3% | 1/8 | FAIL |
| 13 | `cmf` | 47.7 | p42 | -1.24 | 1.68 | 0.90 | 75 | 18.3% | 0/8 | FAIL |
| 14 | `acceleration_band` | 45.1 | p38 | -0.87 | 2.19 | 0.97 | 45 | 14.5% | 0/8 | FAIL |
| 15 | `relative_volume` | 42.8 | p33 | -1.44 | 1.74 | 0.86 | 59 | 14.0% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +5.87% | 0.43 | 1.13 | 47 | 2/8 | FAIL |
| `price_cluster` | +2.50% | 0.40 | 1.12 | 45 | 1/8 | FAIL |
| `positional_scaling` | +1.40% | -0.10 | 1.17 | 36 | 1/8 | FAIL |
| `roc_ma_cross` | +1.01% | -0.11 | 1.15 | 40 | 2/8 | FAIL |
| `frama` | +0.04% | 0.01 | 1.06 | 42 | 0/8 | FAIL |
| `narrow_range` | -0.79% | -0.10 | 1.04 | 50 | 0/8 | FAIL |
| `htf_ema` | -1.30% | -0.15 | 1.02 | 45 | 0/8 | FAIL |
| `dema_cross` | -1.35% | -1.70 | 0.39 | 3 | 0/8 | FAIL |
| `volume_breakout` | -1.46% | -0.35 | 1.04 | 78 | 0/8 | FAIL |
| `momentum_quality` | -2.86% | -0.81 | 1.00 | 66 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | -3.78% | -0.55 | 0.98 | 77 | 0/8 | FAIL |
| `price_action_momentum` | -4.15% | -0.85 | 1.01 | 82 | 1/8 | FAIL |
| `acceleration_band` | -4.28% | -0.87 | 0.97 | 45 | 0/8 | FAIL |
| `lob_maker` | -4.77% | -0.55 | 0.98 | 84 | 0/8 | FAIL |
| `engulfing_zone` | -5.44% | -1.38 | 0.81 | 25 | 0/8 | FAIL |
| `relative_volume` | -7.45% | -1.44 | 0.86 | 59 | 0/8 | FAIL |
| `cmf` | -8.46% | -1.24 | 0.90 | 75 | 0/8 | FAIL |
| `linear_channel_rev` | -8.50% | -2.82 | 0.63 | 29 | 0/8 | FAIL |
| `volatility_cluster` | -9.44% | -2.02 | 0.82 | 60 | 0/8 | FAIL |
| `value_area` | -9.68% | -2.50 | 0.73 | 46 | 0/8 | FAIL |
| `elder_impulse` | -10.01% | -2.02 | 0.75 | 47 | 0/8 | FAIL |
| `wick_reversal` | -11.15% | -2.79 | 0.69 | 43 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | profit_factor 1.44 < 1.5 (x1), mc_p_value 0.189 > 0.05 (우연 가능성) (x1), sharpe -0.68 < 1.0 (x1) |
| `price_cluster` | profit_factor 1.01 < 1.5 (x2), sharpe -1.43 < 1.0 (x1), profit_factor 0.79 < 1.5 (x1) |
| `positional_scaling` | mc_p_value 0.106 > 0.05 (우연 가능성) (x1), sharpe -1.00 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1) |
| `roc_ma_cross` | sharpe 0.21 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1), mc_p_value 0.445 > 0.05 (우연 가능성) (x1) |
| `frama` | sharpe -0.16 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.468 > 0.05 (우연 가능성) (x1) |
| `narrow_range` | sharpe 0.69 < 1.0 (x1), profit_factor 1.14 < 1.5 (x1), mc_p_value 0.350 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | sharpe 0.57 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1), mc_p_value 0.376 > 0.05 (우연 가능성) (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x4), trades 2 < 15 (x3), trades 3 < 15 (x2) |
| `volume_breakout` | sharpe -0.23 < 1.0 (x1), max_drawdown 21.7% > 20% (x1), profit_factor 1.00 < 1.5 (x1) |
| `momentum_quality` | profit_factor 1.31 < 1.5 (x1), mc_p_value 0.156 > 0.05 (우연 가능성) (x1), sharpe -0.44 < 1.0 (x1) |
| `order_flow_imbalance_v2` | profit_factor 1.16 < 1.5 (x1), mc_p_value 0.268 > 0.05 (우연 가능성) (x1), sharpe -0.46 < 1.0 (x1) |
| `price_action_momentum` | profit_factor 1.25 < 1.5 (x1), mc_p_value 0.216 > 0.05 (우연 가능성) (x1), sharpe -2.05 < 1.0 (x1) |
| `acceleration_band` | profit_factor 1.32 < 1.5 (x1), mc_p_value 0.213 > 0.05 (우연 가능성) (x1), sharpe -1.56 < 1.0 (x1) |
| `lob_maker` | max_drawdown 25.6% > 20% (x2), sharpe -1.80 < 1.0 (x1), max_drawdown 30.1% > 20% (x1) |
| `engulfing_zone` | mc_p_value 0.876 > 0.05 (우연 가능성) (x2), sharpe -2.23 < 1.0 (x1), profit_factor 0.65 < 1.5 (x1) |
| `relative_volume` | sharpe -2.07 < 1.0 (x1), profit_factor 0.77 < 1.5 (x1), mc_p_value 0.832 > 0.05 (우연 가능성) (x1) |
| `cmf` | profit_factor 0.78 < 1.5 (x2), profit_factor 1.17 < 1.5 (x1), mc_p_value 0.285 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe 0.01 < 1.0 (x1), profit_factor 1.03 < 1.5 (x1), mc_p_value 0.464 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe -1.04 < 1.0 (x1), profit_factor 0.89 < 1.5 (x1), mc_p_value 0.695 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe -0.25 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1), mc_p_value 0.530 > 0.05 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 1.01 < 1.5 | 6 |
| profit_factor 0.82 < 1.5 | 6 |
| profit_factor 0.78 < 1.5 | 5 |
| profit_factor 0.89 < 1.5 | 4 |
| profit_factor 0.91 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 0.96 < 1.5 | 3 |
| profit_factor 1.06 < 1.5 | 3 |
| profit_factor 0.83 < 1.5 | 3 |
| profit_factor 0.63 < 1.5 | 3 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.82% -> $9,618
- **Top 5 균등배분**: +2.16% -> $10,216
