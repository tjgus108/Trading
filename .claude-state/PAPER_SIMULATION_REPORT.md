# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-07T15:11:06.930085Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-07T15:30:08.185531Z_
_Symbol: BTC/USDT_
_Data Source: CSV fallback BTC/USDT 1h (/home/user/Trading/data/historical)_
_Data Range: 2022-01-01 00:00:00+00:00 ~ 2024-05-14 23:00:00+00:00 (864일)_
_Walk-Forward: 20개 윈도우 (train=5040h, test=1440h)_
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
| 평균 수익률 | -6.81% |
| 최고 수익률 | 0.05% (dema_cross) |
| 최저 수익률 | -15.35% (supertrend_multi) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `dema_cross` | +0.05% | -0.35 | 28.2% | 150.49 | 2 | 1.1% | 0/20 | FAIL |
| 2 | `roc_ma_cross` | -0.81% | -0.44 | 34.0% | 50.81 | 31 | 7.7% | 2/20 | FAIL |
| 3 | `frama` | -1.69% | -0.60 | 30.5% | 0.79 | 32 | 8.2% | 0/20 | FAIL |
| 4 | `htf_ema` | -2.41% | -0.45 | 29.1% | 0.76 | 35 | 9.6% | 0/20 | FAIL |
| 5 | `price_action_momentum` | -3.09% | -0.29 | 38.9% | 100.78 | 63 | 13.9% | 0/20 | FAIL |
| 6 | `acceleration_band` | -3.28% | -0.66 | 26.3% | 0.75 | 34 | 10.2% | 0/20 | FAIL |
| 7 | `value_area` | -4.37% | -1.02 | 26.5% | 0.70 | 37 | 10.6% | 0/20 | FAIL |
| 8 | `narrow_range` | -4.70% | -1.37 | 35.8% | 0.87 | 46 | 13.1% | 0/20 | FAIL |
| 9 | `price_cluster` | -4.82% | -1.76 | 35.0% | 0.82 | 43 | 14.4% | 1/20 | FAIL |
| 10 | `momentum_quality` | -4.85% | -1.24 | 37.7% | 0.95 | 62 | 14.9% | 2/20 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 66.0 | p100 | -0.29 | 2.35 | 100.78 | 63 | 13.9% | 0/20 | FAIL |
| 2 | `roc_ma_cross` | 59.0 | p95 | -0.44 | 1.95 | 50.81 | 31 | 7.7% | 2/20 | FAIL |
| 3 | `momentum_quality` | 54.5 | p90 | -1.24 | 2.97 | 0.95 | 62 | 14.9% | 2/20 | FAIL |
| 4 | `dema_cross` | 50.3 | p85 | -0.35 | 1.71 | 150.49 | 2 | 1.1% | 0/20 | FAIL |
| 5 | `volume_breakout` | 46.0 | p80 | -1.54 | 2.58 | 0.89 | 76 | 17.7% | 0/20 | FAIL |
| 6 | `lob_maker` | 45.4 | p76 | -1.32 | 2.14 | 0.87 | 67 | 18.0% | 0/20 | FAIL |
| 7 | `htf_ema` | 44.4 | p71 | -0.45 | 1.33 | 0.76 | 35 | 9.6% | 0/20 | FAIL |
| 8 | `frama` | 42.0 | p66 | -0.60 | 1.56 | 0.79 | 32 | 8.2% | 0/20 | FAIL |
| 9 | `acceleration_band` | 41.9 | p61 | -0.66 | 1.68 | 0.75 | 34 | 10.2% | 0/20 | FAIL |
| 10 | `volatility_cluster` | 40.9 | p57 | -1.70 | 2.65 | 0.85 | 56 | 13.8% | 0/20 | FAIL |
| 11 | `value_area` | 40.6 | p52 | -1.02 | 1.74 | 0.70 | 37 | 10.6% | 0/20 | FAIL |
| 12 | `order_flow_imbalance_v2` | 40.5 | p47 | -2.07 | 2.57 | 0.83 | 71 | 18.8% | 0/20 | FAIL |
| 13 | `narrow_range` | 39.8 | p42 | -1.37 | 2.48 | 0.87 | 46 | 13.1% | 0/20 | FAIL |
| 14 | `price_cluster` | 39.5 | p38 | -1.76 | 3.30 | 0.82 | 43 | 14.4% | 1/20 | FAIL |
| 15 | `positional_scaling` | 37.4 | p33 | -2.66 | 4.13 | 0.83 | 43 | 15.4% | 2/20 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `dema_cross` | +0.05% | -0.35 | 150.49 | 2 | 0/20 | FAIL |
| `roc_ma_cross` | -0.81% | -0.44 | 50.81 | 31 | 2/20 | FAIL |
| `frama` | -1.69% | -0.60 | 0.79 | 32 | 0/20 | FAIL |
| `htf_ema` | -2.41% | -0.45 | 0.76 | 35 | 0/20 | FAIL |
| `price_action_momentum` | -3.09% | -0.29 | 100.78 | 63 | 0/20 | FAIL |
| `acceleration_band` | -3.28% | -0.66 | 0.75 | 34 | 0/20 | FAIL |
| `value_area` | -4.37% | -1.02 | 0.70 | 37 | 0/20 | FAIL |
| `narrow_range` | -4.70% | -1.37 | 0.87 | 46 | 0/20 | FAIL |
| `price_cluster` | -4.82% | -1.76 | 0.82 | 43 | 1/20 | FAIL |
| `momentum_quality` | -4.85% | -1.24 | 0.95 | 62 | 2/20 | FAIL |
| `linear_channel_rev` | -5.71% | -1.99 | 0.74 | 28 | 0/20 | FAIL |
| `volatility_cluster` | -6.21% | -1.70 | 0.85 | 56 | 0/20 | FAIL |
| `volume_breakout` | -7.68% | -1.54 | 0.89 | 76 | 0/20 | FAIL |
| `positional_scaling` | -8.05% | -2.66 | 0.83 | 43 | 2/20 | FAIL |
| `lob_maker` | -8.53% | -1.32 | 0.87 | 67 | 0/20 | FAIL |
| `relative_volume` | -8.96% | -2.45 | 0.74 | 56 | 0/20 | FAIL |
| `engulfing_zone` | -10.27% | -3.31 | 0.56 | 26 | 0/20 | FAIL |
| `elder_impulse` | -10.78% | -2.99 | 0.64 | 45 | 0/20 | FAIL |
| `order_flow_imbalance_v2` | -11.10% | -2.07 | 0.83 | 71 | 0/20 | FAIL |
| `wick_reversal` | -13.19% | -3.28 | 0.63 | 47 | 0/20 | FAIL |
| `cmf` | -13.94% | -3.12 | 0.71 | 66 | 0/20 | FAIL |
| `supertrend_multi` | -15.35% | -5.15 | 0.37 | 32 | 0/20 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `dema_cross` | profit_factor 0.00 < 1.5 (x6), trades 1 < 15 (x6), no trades generated (x5) |
| `roc_ma_cross` | trades 1 < 15 (x3), sharpe -2.09 < 1.0 (x2), profit_factor 0.00 < 1.5 (x2) |
| `frama` | no trades generated (x2), sharpe -2.92 < 1.0 (x2), profit_factor 0.00 < 1.5 (x2) |
| `htf_ema` | no trades generated (x4), profit_factor 0.83 < 1.5 (x2), profit_factor 1.12 < 1.5 (x2) |
| `price_action_momentum` | no trades generated (x2), trades 3 < 15 (x2), sharpe 0.34 < 1.0 (x1) |
| `acceleration_band` | no trades generated (x4), profit_factor 1.05 < 1.5 (x2), sharpe -1.81 < 1.0 (x1) |
| `value_area` | no trades generated (x4), profit_factor 0.79 < 1.5 (x2), sharpe -0.06 < 1.0 (x1) |
| `narrow_range` | sharpe -1.14 < 1.0 (x2), profit_factor 0.86 < 1.5 (x2), sharpe -1.89 < 1.0 (x1) |
| `price_cluster` | mc_p_value 1.000 > 0.05 (우연 가능성) (x3), profit_factor 0.11 < 1.5 (x2), profit_factor 0.96 < 1.5 (x2) |
| `momentum_quality` | profit_factor 0.98 < 1.5 (x2), sharpe -6.20 < 1.0 (x2), profit_factor 0.53 < 1.5 (x2) |
| `linear_channel_rev` | profit_factor 0.55 < 1.5 (x2), mc_p_value 0.518 > 0.05 (우연 가능성) (x2), mc_p_value 0.995 > 0.05 (우연 가능성) (x2) |
| `volatility_cluster` | sharpe -0.41 < 1.0 (x1), profit_factor 1.07 < 1.5 (x1), mc_p_value 0.396 > 0.05 (우연 가능성) (x1) |
| `volume_breakout` | mc_p_value 0.051 > 0.05 (우연 가능성) (x1), sharpe -5.97 < 1.0 (x1), max_drawdown 22.2% > 20% (x1) |
| `positional_scaling` | mc_p_value 1.000 > 0.05 (우연 가능성) (x4), max_drawdown 26.4% > 20% (x2), profit_factor 0.76 < 1.5 (x2) |
| `lob_maker` | trades 5 < 15 (x2), trades 7 < 15 (x2), profit_factor 0.79 < 1.5 (x2) |
| `relative_volume` | mc_p_value 1.000 > 0.05 (우연 가능성) (x3), profit_factor 0.85 < 1.5 (x2), sharpe -1.27 < 1.0 (x1) |
| `engulfing_zone` | mc_p_value 1.000 > 0.05 (우연 가능성) (x3), sharpe -6.56 < 1.0 (x1), profit_factor 0.01 < 1.5 (x1) |
| `elder_impulse` | mc_p_value 1.000 > 0.05 (우연 가능성) (x2), mc_p_value 0.999 > 0.05 (우연 가능성) (x2), profit_factor 0.81 < 1.5 (x2) |
| `order_flow_imbalance_v2` | max_drawdown 21.3% > 20% (x2), profit_factor 0.79 < 1.5 (x2), sharpe -0.61 < 1.0 (x2) |
| `wick_reversal` | max_drawdown 24.8% > 20% (x2), profit_factor 0.34 < 1.5 (x2), mc_p_value 0.999 > 0.05 (우연 가능성) (x2) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 1.000 > 0.05 (우연 가능성) | 26 |
| no trades generated | 23 |
| profit_factor 0.00 < 1.5 | 13 |
| profit_factor 0.98 < 1.5 | 12 |
| profit_factor 0.76 < 1.5 | 10 |
| trades 1 < 15 | 9 |
| profit_factor 0.55 < 1.5 | 9 |
| profit_factor 0.69 < 1.5 | 7 |
| profit_factor 0.92 < 1.5 | 7 |
| profit_factor 1.05 < 1.5 | 7 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -6.81% -> $9,319
- **Top 5 균등배분**: -1.59% -> $9,841
