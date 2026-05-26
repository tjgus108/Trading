# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-26T20:20:32.685135Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-26T20:23:21.332360Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=719033887, block=36)_
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
| 평균 수익률 | 10.72% |
| 최고 수익률 | 43.61% (lob_maker) |
| 최저 수익률 | -4.05% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `lob_maker` | +43.61% | 3.02 | 43.3% | 1.38 | 128 | 19.3% | 0/4 | FAIL |
| 2 | `volume_breakout` | +31.64% | 3.03 | 43.1% | 1.46 | 93 | 15.7% | 0/4 | FAIL |
| 3 | `momentum_quality` | +24.74% | 2.76 | 43.0% | 1.36 | 110 | 12.4% | 0/4 | FAIL |
| 4 | `cmf` | +19.56% | 1.73 | 40.2% | 1.22 | 115 | 20.1% | 0/4 | FAIL |
| 5 | `narrow_range` | +18.73% | 2.93 | 47.2% | 1.61 | 54 | 5.7% | 0/4 | FAIL |
| 6 | `elder_impulse` | +17.68% | 2.64 | 45.2% | 1.52 | 52 | 8.6% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | +17.20% | 1.74 | 40.5% | 1.25 | 89 | 20.8% | 0/4 | FAIL |
| 8 | `htf_ema` | +13.71% | 1.56 | 41.7% | 1.29 | 68 | 12.5% | 0/4 | FAIL |
| 9 | `price_action_momentum` | +13.64% | 1.36 | 39.7% | 1.15 | 156 | 16.2% | 0/4 | FAIL |
| 10 | `relative_volume` | +9.50% | 1.65 | 42.5% | 1.30 | 57 | 10.2% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `narrow_range` | 76.1 | p100 | 2.93 | 0.96 | 1.61 | 54 | 5.7% | 0/4 | FAIL |
| 2 | `elder_impulse` | 73.6 | p95 | 2.64 | 0.39 | 1.52 | 52 | 8.6% | 0/4 | FAIL |
| 3 | `momentum_quality` | 73.0 | p90 | 2.76 | 0.52 | 1.36 | 110 | 12.4% | 0/4 | FAIL |
| 4 | `volume_breakout` | 68.5 | p85 | 3.03 | 1.16 | 1.46 | 93 | 15.7% | 0/4 | FAIL |
| 5 | `lob_maker` | 66.9 | p80 | 3.02 | 1.22 | 1.38 | 128 | 19.3% | 0/4 | FAIL |
| 6 | `relative_volume` | 62.8 | p76 | 1.65 | 0.25 | 1.30 | 57 | 10.2% | 0/4 | FAIL |
| 7 | `linear_channel_rev` | 61.4 | p71 | 1.66 | 1.06 | 1.42 | 33 | 5.0% | 0/4 | FAIL |
| 8 | `price_action_momentum` | 60.4 | p66 | 1.36 | 0.60 | 1.15 | 156 | 16.2% | 0/4 | FAIL |
| 9 | `roc_ma_cross` | 58.2 | p61 | 0.97 | 0.29 | 1.21 | 40 | 5.4% | 0/4 | FAIL |
| 10 | `volatility_cluster` | 57.4 | p57 | 0.99 | 0.27 | 1.16 | 74 | 9.8% | 0/4 | FAIL |
| 11 | `cmf` | 54.9 | p52 | 1.73 | 0.96 | 1.22 | 115 | 20.1% | 0/4 | FAIL |
| 12 | `value_area` | 54.2 | p47 | 0.70 | 0.53 | 1.27 | 14 | 4.5% | 0/4 | FAIL |
| 13 | `order_flow_imbalance_v2` | 54.1 | p42 | 1.74 | 0.73 | 1.25 | 89 | 20.8% | 0/4 | FAIL |
| 14 | `htf_ema` | 51.2 | p38 | 1.56 | 1.74 | 1.29 | 68 | 12.5% | 0/4 | FAIL |
| 15 | `acceleration_band` | 48.4 | p33 | 0.17 | 0.29 | 1.04 | 105 | 14.9% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `lob_maker` | +43.61% | 3.02 | 1.38 | 128 | 0/4 | FAIL |
| `volume_breakout` | +31.64% | 3.03 | 1.46 | 93 | 0/4 | FAIL |
| `momentum_quality` | +24.74% | 2.76 | 1.36 | 110 | 0/4 | FAIL |
| `cmf` | +19.56% | 1.73 | 1.22 | 115 | 0/4 | FAIL |
| `narrow_range` | +18.73% | 2.93 | 1.61 | 54 | 0/4 | FAIL |
| `elder_impulse` | +17.68% | 2.64 | 1.52 | 52 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +17.20% | 1.74 | 1.25 | 89 | 0/4 | FAIL |
| `htf_ema` | +13.71% | 1.56 | 1.29 | 68 | 0/4 | FAIL |
| `price_action_momentum` | +13.64% | 1.36 | 1.15 | 156 | 0/4 | FAIL |
| `relative_volume` | +9.50% | 1.65 | 1.30 | 57 | 0/4 | FAIL |
| `price_cluster` | +8.36% | 1.25 | 1.31 | 36 | 0/4 | FAIL |
| `linear_channel_rev` | +7.11% | 1.66 | 1.42 | 33 | 0/4 | FAIL |
| `volatility_cluster` | +5.64% | 0.99 | 1.16 | 74 | 0/4 | FAIL |
| `frama` | +5.07% | 0.69 | 1.11 | 86 | 0/4 | FAIL |
| `roc_ma_cross` | +4.03% | 0.97 | 1.21 | 40 | 0/4 | FAIL |
| `supertrend_multi` | +2.60% | 0.54 | 1.10 | 92 | 0/4 | FAIL |
| `value_area` | +1.82% | 0.70 | 1.27 | 14 | 0/4 | FAIL |
| `wick_reversal` | +0.58% | 0.37 | 0.91 | 1 | 0/4 | FAIL |
| `acceleration_band` | -0.23% | 0.17 | 1.04 | 105 | 0/4 | FAIL |
| `positional_scaling` | -1.27% | -0.26 | 0.98 | 29 | 0/4 | FAIL |
| `dema_cross` | -3.73% | -1.58 | 0.67 | 15 | 0/4 | FAIL |
| `engulfing_zone` | -4.05% | -0.83 | 0.87 | 24 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +10.72% -> $11,072
- **Top 5 균등배분**: +27.66% -> $12,766


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-26T20:26:10.726472Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (ETH/USDT-like, seed=1815701730, block=36)_
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
| 평균 수익률 | 14.38% |
| 최고 수익률 | 57.61% (price_action_momentum) |
| 최저 수익률 | -4.76% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +57.61% | 3.79 | 43.2% | 1.49 | 152 | 16.8% | 0/4 | FAIL |
| 2 | `supertrend_multi` | +45.81% | 4.32 | 46.4% | 1.58 | 116 | 7.4% | 0/4 | FAIL |
| 3 | `momentum_quality` | +43.54% | 4.19 | 46.6% | 1.57 | 116 | 10.1% | 0/4 | FAIL |
| 4 | `acceleration_band` | +36.77% | 3.30 | 45.1% | 1.47 | 105 | 10.0% | 0/4 | FAIL |
| 5 | `volume_breakout` | +27.57% | 2.73 | 44.3% | 1.40 | 93 | 11.6% | 0/4 | FAIL |
| 6 | `volatility_cluster` | +23.14% | 3.15 | 46.1% | 1.50 | 81 | 7.3% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | +22.57% | 1.80 | 41.6% | 1.31 | 90 | 18.3% | 0/4 | FAIL |
| 8 | `price_cluster` | +20.10% | 2.82 | 50.2% | 1.93 | 39 | 7.5% | 0/4 | FAIL |
| 9 | `lob_maker` | +13.58% | 1.05 | 39.1% | 1.15 | 128 | 21.1% | 0/4 | FAIL |
| 10 | `narrow_range` | +12.87% | 2.03 | 44.1% | 1.38 | 57 | 10.1% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `wick_reversal` | 64.1 | p100 | 1.69 | 1.03 | 749.99 | 1 | 0.0% | 0/4 | FAIL |
| 2 | `supertrend_multi` | 61.0 | p95 | 4.32 | 1.52 | 1.58 | 116 | 7.4% | 0/4 | FAIL |
| 3 | `momentum_quality` | 59.1 | p90 | 4.19 | 1.33 | 1.57 | 116 | 10.1% | 0/4 | FAIL |
| 4 | `volatility_cluster` | 55.7 | p85 | 3.15 | 0.57 | 1.50 | 81 | 7.3% | 0/4 | FAIL |
| 5 | `acceleration_band` | 53.7 | p80 | 3.30 | 1.38 | 1.47 | 105 | 10.0% | 0/4 | FAIL |
| 6 | `price_action_momentum` | 50.5 | p76 | 3.79 | 2.69 | 1.49 | 152 | 16.8% | 0/4 | FAIL |
| 7 | `volume_breakout` | 49.4 | p71 | 2.73 | 1.19 | 1.40 | 93 | 11.6% | 0/4 | FAIL |
| 8 | `linear_channel_rev` | 44.3 | p66 | 1.75 | 0.98 | 1.42 | 35 | 5.3% | 0/4 | FAIL |
| 9 | `price_cluster` | 43.5 | p61 | 2.82 | 2.14 | 1.93 | 39 | 7.5% | 0/4 | FAIL |
| 10 | `narrow_range` | 43.5 | p57 | 2.03 | 1.19 | 1.38 | 57 | 10.1% | 0/4 | FAIL |
| 11 | `cmf` | 41.4 | p52 | 0.76 | 0.20 | 1.09 | 134 | 20.9% | 0/4 | FAIL |
| 12 | `frama` | 37.2 | p47 | 0.67 | 1.36 | 1.11 | 94 | 14.0% | 0/4 | FAIL |
| 13 | `lob_maker` | 35.3 | p42 | 1.05 | 1.88 | 1.15 | 128 | 21.1% | 0/4 | FAIL |
| 14 | `order_flow_imbalance_v2` | 34.7 | p38 | 1.80 | 2.47 | 1.31 | 90 | 18.3% | 0/4 | FAIL |
| 15 | `relative_volume` | 32.9 | p33 | -0.17 | 1.31 | 1.02 | 57 | 9.6% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +57.61% | 3.79 | 1.49 | 152 | 0/4 | FAIL |
| `supertrend_multi` | +45.81% | 4.32 | 1.58 | 116 | 0/4 | FAIL |
| `momentum_quality` | +43.54% | 4.19 | 1.57 | 116 | 0/4 | FAIL |
| `acceleration_band` | +36.77% | 3.30 | 1.47 | 105 | 0/4 | FAIL |
| `volume_breakout` | +27.57% | 2.73 | 1.40 | 93 | 0/4 | FAIL |
| `volatility_cluster` | +23.14% | 3.15 | 1.50 | 81 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +22.57% | 1.80 | 1.31 | 90 | 0/4 | FAIL |
| `price_cluster` | +20.10% | 2.82 | 1.93 | 39 | 0/4 | FAIL |
| `lob_maker` | +13.58% | 1.05 | 1.15 | 128 | 0/4 | FAIL |
| `narrow_range` | +12.87% | 2.03 | 1.38 | 57 | 0/4 | FAIL |
| `linear_channel_rev` | +7.99% | 1.75 | 1.42 | 35 | 0/4 | FAIL |
| `cmf` | +6.53% | 0.76 | 1.09 | 134 | 0/4 | FAIL |
| `frama` | +6.01% | 0.67 | 1.11 | 94 | 0/4 | FAIL |
| `roc_ma_cross` | +3.37% | 0.64 | 1.28 | 38 | 0/4 | FAIL |
| `wick_reversal` | +2.85% | 1.69 | 749.99 | 1 | 0/4 | FAIL |
| `value_area` | +2.06% | 0.67 | 1.56 | 16 | 0/4 | FAIL |
| `elder_impulse` | +1.73% | 0.33 | 1.15 | 61 | 0/4 | FAIL |
| `relative_volume` | -0.83% | -0.17 | 1.02 | 57 | 0/4 | FAIL |
| `positional_scaling` | -3.19% | -0.89 | 0.90 | 26 | 0/4 | FAIL |
| `dema_cross` | -4.42% | -1.97 | 0.62 | 14 | 0/4 | FAIL |
| `htf_ema` | -4.63% | -0.55 | 0.97 | 68 | 0/4 | FAIL |
| `engulfing_zone` | -4.76% | -1.09 | 0.81 | 22 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +14.38% -> $11,438
- **Top 5 균등배분**: +42.26% -> $14,226


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-26T20:29:05.434699Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (SOL/USDT-like, seed=1425867746, block=36)_
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
| 평균 수익률 | 20.93% |
| 최고 수익률 | 130.03% (price_action_momentum) |
| 최저 수익률 | -12.01% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +130.03% | 7.11 | 51.6% | 1.82 | 168 | 10.7% | 0/4 | FAIL |
| 2 | `supertrend_multi` | +126.41% | 8.86 | 58.2% | 2.54 | 112 | 6.0% | 0/4 | FAIL |
| 3 | `momentum_quality` | +87.17% | 6.39 | 51.2% | 1.86 | 130 | 10.6% | 0/4 | FAIL |
| 4 | `volatility_cluster` | +23.59% | 3.08 | 45.4% | 1.50 | 80 | 8.1% | 0/4 | FAIL |
| 5 | `volume_breakout` | +23.31% | 2.34 | 43.9% | 1.36 | 88 | 16.8% | 0/4 | FAIL |
| 6 | `cmf` | +22.03% | 1.89 | 42.4% | 1.26 | 96 | 17.4% | 0/4 | FAIL |
| 7 | `narrow_range` | +20.42% | 3.12 | 49.3% | 1.69 | 52 | 7.9% | 0/4 | FAIL |
| 8 | `acceleration_band` | +19.59% | 1.91 | 42.5% | 1.34 | 97 | 12.2% | 0/4 | FAIL |
| 9 | `roc_ma_cross` | +13.47% | 2.85 | 50.0% | 1.78 | 34 | 7.0% | 0/4 | FAIL |
| 10 | `order_flow_imbalance_v2` | +10.21% | 1.20 | 40.5% | 1.20 | 82 | 14.9% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 81.6 | p100 | 8.86 | 1.65 | 2.54 | 112 | 6.0% | 0/4 | FAIL |
| 2 | `price_action_momentum` | 79.1 | p95 | 7.11 | 0.45 | 1.82 | 168 | 10.7% | 0/4 | FAIL |
| 3 | `momentum_quality` | 69.4 | p90 | 6.39 | 1.43 | 1.86 | 130 | 10.6% | 0/4 | FAIL |
| 4 | `narrow_range` | 56.3 | p85 | 3.12 | 1.01 | 1.69 | 52 | 7.9% | 0/4 | FAIL |
| 5 | `roc_ma_cross` | 56.3 | p80 | 2.85 | 0.81 | 1.78 | 34 | 7.0% | 0/4 | FAIL |
| 6 | `volatility_cluster` | 54.7 | p76 | 3.08 | 1.49 | 1.50 | 80 | 8.1% | 0/4 | FAIL |
| 7 | `positional_scaling` | 47.2 | p71 | 0.64 | 0.50 | 1.19 | 27 | 6.1% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | 47.1 | p66 | 1.20 | 0.66 | 1.20 | 82 | 14.9% | 0/4 | FAIL |
| 9 | `linear_channel_rev` | 46.0 | p61 | 0.51 | 0.54 | 1.14 | 34 | 7.5% | 0/4 | FAIL |
| 10 | `volume_breakout` | 45.5 | p57 | 2.34 | 1.72 | 1.36 | 88 | 16.8% | 0/4 | FAIL |
| 11 | `acceleration_band` | 45.3 | p52 | 1.91 | 2.28 | 1.34 | 97 | 12.2% | 0/4 | FAIL |
| 12 | `htf_ema` | 45.0 | p47 | 1.18 | 0.76 | 1.21 | 68 | 15.5% | 0/4 | FAIL |
| 13 | `elder_impulse` | 44.5 | p42 | 0.97 | 1.04 | 1.21 | 51 | 11.1% | 0/4 | FAIL |
| 14 | `dema_cross` | 43.9 | p38 | 0.14 | 0.84 | 1.11 | 9 | 3.3% | 0/4 | FAIL |
| 15 | `cmf` | 43.4 | p33 | 1.89 | 1.81 | 1.26 | 96 | 17.4% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +130.03% | 7.11 | 1.82 | 168 | 0/4 | FAIL |
| `supertrend_multi` | +126.41% | 8.86 | 2.54 | 112 | 0/4 | FAIL |
| `momentum_quality` | +87.17% | 6.39 | 1.86 | 130 | 0/4 | FAIL |
| `volatility_cluster` | +23.59% | 3.08 | 1.50 | 80 | 0/4 | FAIL |
| `volume_breakout` | +23.31% | 2.34 | 1.36 | 88 | 0/4 | FAIL |
| `cmf` | +22.03% | 1.89 | 1.26 | 96 | 0/4 | FAIL |
| `narrow_range` | +20.42% | 3.12 | 1.69 | 52 | 0/4 | FAIL |
| `acceleration_band` | +19.59% | 1.91 | 1.34 | 97 | 0/4 | FAIL |
| `roc_ma_cross` | +13.47% | 2.85 | 1.78 | 34 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +10.21% | 1.20 | 1.20 | 82 | 0/4 | FAIL |
| `htf_ema` | +8.72% | 1.18 | 1.21 | 68 | 0/4 | FAIL |
| `elder_impulse` | +6.25% | 0.97 | 1.21 | 51 | 0/4 | FAIL |
| `positional_scaling` | +2.23% | 0.64 | 1.19 | 27 | 0/4 | FAIL |
| `linear_channel_rev` | +1.81% | 0.51 | 1.14 | 34 | 0/4 | FAIL |
| `dema_cross` | +0.36% | 0.14 | 1.11 | 9 | 0/4 | FAIL |
| `value_area` | -1.78% | -0.66 | 0.93 | 13 | 0/4 | FAIL |
| `lob_maker` | -2.42% | 0.02 | 1.04 | 122 | 0/4 | FAIL |
| `relative_volume` | -2.62% | -0.62 | 1.02 | 58 | 0/4 | FAIL |
| `wick_reversal` | -2.64% | -2.57 | 0.00 | 2 | 0/4 | FAIL |
| `price_cluster` | -4.45% | -0.74 | 0.92 | 36 | 0/4 | FAIL |
| `engulfing_zone` | -9.29% | -2.32 | 0.68 | 23 | 0/4 | FAIL |
| `frama` | -12.01% | -1.72 | 0.84 | 75 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +20.93% -> $12,093
- **Top 5 균등배분**: +78.10% -> $17,810
