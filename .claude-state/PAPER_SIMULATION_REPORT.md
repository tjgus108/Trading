# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-27T05:16:49.990756Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-27T05:20:31.778547Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=372228595, block=36)_
_Data Range: 0 ~ 8639 (8640봉)_
_Walk-Forward: 4개 윈도우 (train=5040h, test=1440h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | 17.41% |
| 최고 수익률 | 82.71% (momentum_quality) |
| 최저 수익률 | -7.86% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +82.71% | 6.66 | 55.4% | 2.05 | 108 | 8.2% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +65.22% | 4.70 | 46.0% | 1.55 | 148 | 10.3% | 0/4 | FAIL |
| 3 | `cmf` | +65.16% | 3.82 | 44.9% | 1.50 | 136 | 17.9% | 0/4 | FAIL |
| 4 | `supertrend_multi` | +55.06% | 4.64 | 47.2% | 1.62 | 120 | 10.4% | 0/4 | FAIL |
| 5 | `volatility_cluster` | +35.54% | 4.22 | 48.8% | 1.72 | 84 | 7.9% | 0/4 | FAIL |
| 6 | `lob_maker` | +30.44% | 2.40 | 42.9% | 1.28 | 121 | 15.1% | 0/4 | FAIL |
| 7 | `acceleration_band` | +25.98% | 2.60 | 43.6% | 1.40 | 96 | 14.3% | 0/4 | FAIL |
| 8 | `htf_ema` | +15.20% | 1.74 | 43.3% | 1.32 | 66 | 14.1% | 0/4 | FAIL |
| 9 | `volume_breakout` | +11.09% | 1.28 | 41.2% | 1.18 | 92 | 14.0% | 0/4 | FAIL |
| 10 | `order_flow_imbalance_v2` | +8.38% | 0.91 | 39.7% | 1.14 | 90 | 18.0% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 62.5 | p100 | 6.66 | 1.57 | 2.05 | 108 | 8.2% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 61.6 | p95 | 4.70 | 0.68 | 1.55 | 148 | 10.3% | 0/4 | FAIL |
| 3 | `supertrend_multi` | 54.8 | p90 | 4.64 | 1.76 | 1.62 | 120 | 10.4% | 0/4 | FAIL |
| 4 | `volatility_cluster` | 54.0 | p85 | 4.22 | 1.07 | 1.72 | 84 | 7.9% | 0/4 | FAIL |
| 5 | `wick_reversal` | 50.3 | p80 | -0.47 | 2.43 | 500.00 | 2 | 1.4% | 0/4 | FAIL |
| 6 | `lob_maker` | 47.3 | p76 | 2.40 | 0.76 | 1.28 | 121 | 15.1% | 0/4 | FAIL |
| 7 | `cmf` | 46.4 | p71 | 3.82 | 2.24 | 1.50 | 136 | 17.9% | 0/4 | FAIL |
| 8 | `acceleration_band` | 44.4 | p66 | 2.60 | 1.27 | 1.40 | 96 | 14.3% | 0/4 | FAIL |
| 9 | `relative_volume` | 43.4 | p61 | 1.36 | 0.60 | 1.25 | 57 | 7.8% | 0/4 | FAIL |
| 10 | `volume_breakout` | 41.0 | p57 | 1.28 | 0.90 | 1.18 | 92 | 14.0% | 0/4 | FAIL |
| 11 | `linear_channel_rev` | 40.4 | p52 | 1.58 | 1.29 | 1.43 | 32 | 6.3% | 0/4 | FAIL |
| 12 | `htf_ema` | 37.9 | p47 | 1.74 | 1.48 | 1.32 | 66 | 14.1% | 0/4 | FAIL |
| 13 | `dema_cross` | 37.5 | p42 | 0.62 | 1.04 | 1.33 | 12 | 4.4% | 0/4 | FAIL |
| 14 | `roc_ma_cross` | 36.0 | p38 | 0.31 | 0.83 | 1.10 | 37 | 9.4% | 0/4 | FAIL |
| 15 | `order_flow_imbalance_v2` | 35.5 | p33 | 0.91 | 1.22 | 1.14 | 90 | 18.0% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +82.71% | 6.66 | 2.05 | 108 | 0/4 | FAIL |
| `price_action_momentum` | +65.22% | 4.70 | 1.55 | 148 | 0/4 | FAIL |
| `cmf` | +65.16% | 3.82 | 1.50 | 136 | 0/4 | FAIL |
| `supertrend_multi` | +55.06% | 4.64 | 1.62 | 120 | 0/4 | FAIL |
| `volatility_cluster` | +35.54% | 4.22 | 1.72 | 84 | 0/4 | FAIL |
| `lob_maker` | +30.44% | 2.40 | 1.28 | 121 | 0/4 | FAIL |
| `acceleration_band` | +25.98% | 2.60 | 1.40 | 96 | 0/4 | FAIL |
| `htf_ema` | +15.20% | 1.74 | 1.32 | 66 | 0/4 | FAIL |
| `volume_breakout` | +11.09% | 1.28 | 1.18 | 92 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +8.38% | 0.91 | 1.14 | 90 | 0/4 | FAIL |
| `relative_volume` | +7.57% | 1.36 | 1.25 | 57 | 0/4 | FAIL |
| `linear_channel_rev` | +6.79% | 1.58 | 1.43 | 32 | 0/4 | FAIL |
| `dema_cross` | +1.43% | 0.62 | 1.33 | 12 | 0/4 | FAIL |
| `roc_ma_cross` | +1.20% | 0.31 | 1.10 | 37 | 0/4 | FAIL |
| `positional_scaling` | +0.42% | -0.54 | 1.18 | 26 | 0/4 | FAIL |
| `wick_reversal` | -0.69% | -0.47 | 500.00 | 2 | 0/4 | FAIL |
| `narrow_range` | -0.81% | -0.05 | 1.04 | 100 | 0/4 | FAIL |
| `engulfing_zone` | -3.54% | -0.79 | 0.91 | 22 | 0/4 | FAIL |
| `elder_impulse` | -4.59% | -0.71 | 0.97 | 59 | 0/4 | FAIL |
| `price_cluster` | -5.55% | -0.92 | 0.88 | 32 | 0/4 | FAIL |
| `value_area` | -6.20% | -2.43 | 0.65 | 17 | 0/4 | FAIL |
| `frama` | -7.86% | -0.93 | 0.94 | 82 | 0/4 | FAIL |

## FAIL 진단 (상위 FAIL 전략 fail_reasons 집계)

_다음 사이클 개선 방향 파악용: FAIL 주원인 분포_

- `other`: 40건
- `low_pf`: 22건
- `low_sharpe`: 7건
- `high_mdd`: 4건

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +17.41% -> $11,741
- **Top 5 균등배분**: +60.74% -> $16,074


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-27T05:24:11.920425Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=1059554229, block=36)_
_Data Range: 0 ~ 8639 (8640봉)_
_Walk-Forward: 4개 윈도우 (train=5040h, test=1440h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | 15.38% |
| 최고 수익률 | 70.40% (price_action_momentum) |
| 최저 수익률 | -2.63% (roc_ma_cross) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +70.40% | 4.61 | 46.8% | 1.61 | 146 | 12.1% | 0/4 | FAIL |
| 2 | `volume_breakout` | +42.09% | 4.04 | 47.5% | 1.64 | 88 | 10.1% | 0/4 | FAIL |
| 3 | `lob_maker` | +35.44% | 2.66 | 43.1% | 1.33 | 122 | 15.2% | 0/4 | FAIL |
| 4 | `momentum_quality` | +35.34% | 3.64 | 46.5% | 1.49 | 107 | 8.3% | 0/4 | FAIL |
| 5 | `acceleration_band` | +32.04% | 2.95 | 44.1% | 1.46 | 97 | 16.3% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | +29.67% | 2.76 | 44.4% | 1.41 | 88 | 12.7% | 0/4 | FAIL |
| 7 | `supertrend_multi` | +22.61% | 2.80 | 44.8% | 1.42 | 84 | 9.6% | 0/4 | FAIL |
| 8 | `frama` | +14.97% | 1.77 | 40.0% | 1.26 | 80 | 14.7% | 0/4 | FAIL |
| 9 | `cmf` | +14.10% | 1.34 | 40.6% | 1.17 | 118 | 21.8% | 0/4 | FAIL |
| 10 | `volatility_cluster` | +13.59% | 1.95 | 43.8% | 1.34 | 78 | 8.1% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `volume_breakout` | 78.1 | p100 | 4.04 | 0.32 | 1.64 | 88 | 10.1% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 75.9 | p95 | 4.61 | 2.63 | 1.61 | 146 | 12.1% | 0/4 | FAIL |
| 3 | `momentum_quality` | 73.8 | p90 | 3.64 | 1.14 | 1.49 | 107 | 8.3% | 0/4 | FAIL |
| 4 | `order_flow_imbalance_v2` | 66.0 | p85 | 2.76 | 0.33 | 1.41 | 88 | 12.7% | 0/4 | FAIL |
| 5 | `supertrend_multi` | 65.8 | p80 | 2.80 | 0.93 | 1.42 | 84 | 9.6% | 0/4 | FAIL |
| 6 | `lob_maker` | 64.0 | p76 | 2.66 | 0.88 | 1.33 | 122 | 15.2% | 0/4 | FAIL |
| 7 | `acceleration_band` | 59.9 | p71 | 2.95 | 1.85 | 1.46 | 97 | 16.3% | 0/4 | FAIL |
| 8 | `narrow_range` | 59.2 | p66 | 1.72 | 0.53 | 1.27 | 78 | 9.2% | 0/4 | FAIL |
| 9 | `relative_volume` | 59.0 | p61 | 1.85 | 0.61 | 1.37 | 54 | 8.1% | 0/4 | FAIL |
| 10 | `engulfing_zone` | 58.3 | p57 | 1.96 | 1.12 | 1.69 | 22 | 7.6% | 0/4 | FAIL |
| 11 | `volatility_cluster` | 57.5 | p52 | 1.95 | 1.63 | 1.34 | 78 | 8.1% | 0/4 | FAIL |
| 12 | `frama` | 57.0 | p47 | 1.77 | 0.21 | 1.26 | 80 | 14.7% | 0/4 | FAIL |
| 13 | `cmf` | 49.9 | p42 | 1.34 | 0.79 | 1.17 | 118 | 21.8% | 0/4 | FAIL |
| 14 | `value_area` | 49.5 | p38 | 0.75 | 0.95 | 1.33 | 14 | 4.2% | 0/4 | FAIL |
| 15 | `elder_impulse` | 45.8 | p33 | 0.60 | 0.82 | 1.13 | 54 | 11.5% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +70.40% | 4.61 | 1.61 | 146 | 0/4 | FAIL |
| `volume_breakout` | +42.09% | 4.04 | 1.64 | 88 | 0/4 | FAIL |
| `lob_maker` | +35.44% | 2.66 | 1.33 | 122 | 0/4 | FAIL |
| `momentum_quality` | +35.34% | 3.64 | 1.49 | 107 | 0/4 | FAIL |
| `acceleration_band` | +32.04% | 2.95 | 1.46 | 97 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +29.67% | 2.76 | 1.41 | 88 | 0/4 | FAIL |
| `supertrend_multi` | +22.61% | 2.80 | 1.42 | 84 | 0/4 | FAIL |
| `frama` | +14.97% | 1.77 | 1.26 | 80 | 0/4 | FAIL |
| `cmf` | +14.10% | 1.34 | 1.17 | 118 | 0/4 | FAIL |
| `volatility_cluster` | +13.59% | 1.95 | 1.34 | 78 | 0/4 | FAIL |
| `narrow_range` | +11.96% | 1.72 | 1.27 | 78 | 0/4 | FAIL |
| `relative_volume` | +9.95% | 1.85 | 1.37 | 54 | 0/4 | FAIL |
| `engulfing_zone` | +9.81% | 1.96 | 1.69 | 22 | 0/4 | FAIL |
| `elder_impulse` | +3.06% | 0.60 | 1.13 | 54 | 0/4 | FAIL |
| `value_area` | +2.05% | 0.75 | 1.33 | 14 | 0/4 | FAIL |
| `htf_ema` | -0.20% | 0.03 | 1.04 | 66 | 0/4 | FAIL |
| `wick_reversal` | -0.43% | -0.53 | 0.00 | 0 | 0/4 | FAIL |
| `positional_scaling` | -0.61% | -0.21 | 0.98 | 24 | 0/4 | FAIL |
| `dema_cross` | -1.08% | -0.38 | 0.91 | 12 | 0/4 | FAIL |
| `linear_channel_rev` | -1.49% | -0.44 | 0.96 | 31 | 0/4 | FAIL |
| `price_cluster` | -2.29% | -0.24 | 1.01 | 43 | 0/4 | FAIL |
| `roc_ma_cross` | -2.63% | -0.66 | 0.98 | 39 | 0/4 | FAIL |

## FAIL 진단 (상위 FAIL 전략 fail_reasons 집계)

_다음 사이클 개선 방향 파악용: FAIL 주원인 분포_

- `other`: 40건
- `low_pf`: 27건
- `high_mdd`: 7건
- `low_sharpe`: 3건

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +15.38% -> $11,538
- **Top 5 균등배분**: +43.06% -> $14,306


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-27T05:27:51.379322Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=1532229330, block=36)_
_Data Range: 0 ~ 8639 (8640봉)_
_Walk-Forward: 4개 윈도우 (train=5040h, test=1440h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | 7.77% |
| 최고 수익률 | 19.28% (supertrend_multi) |
| 최저 수익률 | -3.65% (value_area) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +19.28% | 2.37 | 42.5% | 1.32 | 111 | 10.8% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +18.67% | 1.75 | 40.9% | 1.20 | 158 | 17.8% | 0/4 | FAIL |
| 3 | `narrow_range` | +17.49% | 1.81 | 41.1% | 1.31 | 96 | 12.4% | 0/4 | FAIL |
| 4 | `engulfing_zone` | +16.33% | 2.14 | 46.1% | 1.99 | 24 | 7.8% | 0/4 | FAIL |
| 5 | `order_flow_imbalance_v2` | +15.78% | 1.53 | 40.8% | 1.22 | 86 | 16.8% | 0/4 | FAIL |
| 6 | `elder_impulse` | +13.65% | 2.05 | 44.3% | 1.38 | 55 | 8.9% | 0/4 | FAIL |
| 7 | `momentum_quality` | +10.86% | 1.32 | 39.7% | 1.19 | 106 | 15.7% | 0/4 | FAIL |
| 8 | `volatility_cluster` | +10.05% | 1.47 | 42.2% | 1.24 | 79 | 11.8% | 0/4 | FAIL |
| 9 | `dema_cross` | +8.49% | 2.85 | 59.0% | 2.68 | 12 | 2.2% | 0/4 | FAIL |
| 10 | `roc_ma_cross` | +8.41% | 1.68 | 43.2% | 1.41 | 39 | 10.8% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `wick_reversal` | 65.1 | p100 | 0.97 | 0.97 | 500.00 | 0 | 0.0% | 0/4 | FAIL |
| 2 | `supertrend_multi` | 58.8 | p95 | 2.37 | 0.89 | 1.32 | 111 | 10.8% | 0/4 | FAIL |
| 3 | `dema_cross` | 56.7 | p90 | 2.85 | 1.20 | 2.68 | 12 | 2.2% | 0/4 | FAIL |
| 4 | `price_action_momentum` | 54.5 | p85 | 1.75 | 0.96 | 1.20 | 158 | 17.8% | 0/4 | FAIL |
| 5 | `elder_impulse` | 54.3 | p80 | 2.05 | 0.44 | 1.38 | 55 | 8.9% | 0/4 | FAIL |
| 6 | `linear_channel_rev` | 51.1 | p76 | 1.71 | 0.59 | 1.45 | 29 | 5.5% | 0/4 | FAIL |
| 7 | `volatility_cluster` | 49.4 | p71 | 1.47 | 0.80 | 1.24 | 79 | 11.8% | 0/4 | FAIL |
| 8 | `momentum_quality` | 46.6 | p66 | 1.32 | 1.28 | 1.19 | 106 | 15.7% | 0/4 | FAIL |
| 9 | `acceleration_band` | 46.3 | p61 | 0.86 | 0.61 | 1.13 | 105 | 15.5% | 0/4 | FAIL |
| 10 | `narrow_range` | 45.8 | p57 | 1.81 | 2.56 | 1.31 | 96 | 12.4% | 0/4 | FAIL |
| 11 | `roc_ma_cross` | 45.8 | p52 | 1.68 | 1.26 | 1.41 | 39 | 10.8% | 0/4 | FAIL |
| 12 | `order_flow_imbalance_v2` | 45.2 | p47 | 1.53 | 1.36 | 1.22 | 86 | 16.8% | 0/4 | FAIL |
| 13 | `engulfing_zone` | 42.6 | p42 | 2.14 | 2.86 | 1.99 | 24 | 7.8% | 0/4 | FAIL |
| 14 | `positional_scaling` | 39.5 | p38 | 0.17 | 0.57 | 1.07 | 25 | 6.9% | 0/4 | FAIL |
| 15 | `lob_maker` | 39.1 | p33 | 0.62 | 1.22 | 1.10 | 118 | 22.4% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +19.28% | 2.37 | 1.32 | 111 | 0/4 | FAIL |
| `price_action_momentum` | +18.67% | 1.75 | 1.20 | 158 | 0/4 | FAIL |
| `narrow_range` | +17.49% | 1.81 | 1.31 | 96 | 0/4 | FAIL |
| `engulfing_zone` | +16.33% | 2.14 | 1.99 | 24 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +15.78% | 1.53 | 1.22 | 86 | 0/4 | FAIL |
| `elder_impulse` | +13.65% | 2.05 | 1.38 | 55 | 0/4 | FAIL |
| `momentum_quality` | +10.86% | 1.32 | 1.19 | 106 | 0/4 | FAIL |
| `volatility_cluster` | +10.05% | 1.47 | 1.24 | 79 | 0/4 | FAIL |
| `dema_cross` | +8.49% | 2.85 | 2.68 | 12 | 0/4 | FAIL |
| `roc_ma_cross` | +8.41% | 1.68 | 1.41 | 39 | 0/4 | FAIL |
| `acceleration_band` | +6.79% | 0.86 | 1.13 | 105 | 0/4 | FAIL |
| `linear_channel_rev` | +6.75% | 1.71 | 1.45 | 29 | 0/4 | FAIL |
| `frama` | +6.08% | 0.59 | 1.16 | 78 | 0/4 | FAIL |
| `lob_maker` | +5.87% | 0.62 | 1.10 | 118 | 0/4 | FAIL |
| `htf_ema` | +4.35% | 0.61 | 1.13 | 77 | 0/4 | FAIL |
| `cmf` | +3.79% | 0.47 | 1.08 | 114 | 0/4 | FAIL |
| `volume_breakout` | +2.94% | 0.24 | 1.08 | 87 | 0/4 | FAIL |
| `positional_scaling` | +0.41% | 0.17 | 1.07 | 25 | 0/4 | FAIL |
| `wick_reversal` | +0.26% | 0.97 | 500.00 | 0 | 0/4 | FAIL |
| `relative_volume` | -0.31% | -0.27 | 1.03 | 58 | 0/4 | FAIL |
| `price_cluster` | -1.42% | -0.16 | 1.02 | 42 | 0/4 | FAIL |
| `value_area` | -3.65% | -1.60 | 0.88 | 18 | 0/4 | FAIL |

## FAIL 진단 (상위 FAIL 전략 fail_reasons 집계)

_다음 사이클 개선 방향 파악용: FAIL 주원인 분포_

- `other`: 37건
- `low_pf`: 30건
- `low_sharpe`: 10건
- `high_mdd`: 6건
- `low_trades`: 3건

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +7.77% -> $10,777
- **Top 5 균등배분**: +17.51% -> $11,751
