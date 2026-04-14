# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-04-14T22:57:42.238487Z_
_Symbols: BTC/USDT, ETH/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-04-14T22:56:57.574415Z_
_Symbol: BTC/USDT_
_Data Source: Bybit BTC/USDT 1h (paginated)_
_Data Range: 2025-10-16 23:00:00+00:00 ~ 2025-11-27 13:00:00+00:00 (41일)_
_Walk-Forward: 1개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 1개 |
| FAIL | 21개 |
| 평균 수익률 | -0.60% |
| 최고 수익률 | 5.07% (value_area) |
| 최저 수익률 | -10.58% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `value_area` | +5.07% | 5.14 | 62.5% | 3.27 | 8 | 2.8% | 0/1 | FAIL |
| 2 | `cmf` | +4.68% | 2.75 | 46.7% | 1.61 | 15 | 2.2% | 1/1 | PASS |
| 3 | `narrow_range` | +3.31% | 3.35 | 50.0% | 3.00 | 4 | 1.1% | 0/1 | FAIL |
| 4 | `positional_scaling` | +3.01% | 3.15 | 50.0% | 2.01 | 8 | 1.3% | 0/1 | FAIL |
| 5 | `htf_ema` | +1.79% | 1.32 | 50.0% | 1.37 | 10 | 6.9% | 0/1 | FAIL |
| 6 | `acceleration_band` | +1.42% | 1.30 | 46.2% | 1.33 | 13 | 4.7% | 0/1 | FAIL |
| 7 | `roc_ma_cross` | +0.47% | 0.64 | 50.0% | 1.29 | 6 | 2.5% | 0/1 | FAIL |
| 8 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/1 | FAIL |
| 9 | `price_cluster` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/1 | FAIL |
| 10 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/1 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `value_area` | +5.07% | 5.14 | 3.27 | 8 | 0/1 | FAIL |
| `cmf` | +4.68% | 2.75 | 1.61 | 15 | 1/1 | PASS |
| `narrow_range` | +3.31% | 3.35 | 3.00 | 4 | 0/1 | FAIL |
| `positional_scaling` | +3.01% | 3.15 | 2.01 | 8 | 0/1 | FAIL |
| `htf_ema` | +1.79% | 1.32 | 1.37 | 10 | 0/1 | FAIL |
| `acceleration_band` | +1.42% | 1.30 | 1.33 | 13 | 0/1 | FAIL |
| `roc_ma_cross` | +0.47% | 0.64 | 1.29 | 6 | 0/1 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/1 | FAIL |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/1 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/1 | FAIL |
| `elder_impulse` | -0.18% | -0.03 | 1.09 | 10 | 0/1 | FAIL |
| `engulfing_zone` | -0.31% | -5.07 | 0.00 | 1 | 0/1 | FAIL |
| `relative_volume` | -0.52% | -0.35 | 1.03 | 10 | 0/1 | FAIL |
| `linear_channel_rev` | -0.59% | -0.96 | 0.90 | 5 | 0/1 | FAIL |
| `supertrend_multi` | -0.93% | -0.24 | 1.07 | 22 | 0/1 | FAIL |
| `frama` | -1.05% | -0.79 | 0.95 | 10 | 0/1 | FAIL |
| `momentum_quality` | -1.39% | -1.55 | 0.86 | 9 | 0/1 | FAIL |
| `lob_maker` | -1.72% | -0.60 | 1.03 | 20 | 0/1 | FAIL |
| `order_flow_imbalance_v2` | -4.95% | -2.63 | 0.82 | 21 | 0/1 | FAIL |
| `price_action_momentum` | -5.16% | -2.86 | 0.81 | 21 | 0/1 | FAIL |
| `volatility_cluster` | -5.65% | -5.09 | 0.51 | 14 | 0/1 | FAIL |
| `wick_reversal` | -10.58% | -10.25 | 0.15 | 10 | 0/1 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -0.60% -> $9,940
- **PASS 1개 균등배분**: +4.68% -> $10,468
- **Top 5 균등배분**: +3.57% -> $10,357


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-04-14T22:57:42.237553Z_
_Symbol: ETH/USDT_
_Data Source: Bybit ETH/USDT 1h (paginated)_
_Data Range: 2025-10-16 23:00:00+00:00 ~ 2025-11-27 13:00:00+00:00 (41일)_
_Walk-Forward: 1개 윈도우 (train=2880h, test=720h)_
_Initial Balance: $10,000 USDT | Fee: 0.1% | Slippage: 0.05%_
_통과 기준: 윈도우 50% 이상에서 Sharpe>=1.0, PF>=1.5, Trades>=15, MDD<=20%_

## 요약

| 항목 | 값 |
|------|-----|
| 테스트 전략 | 22개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 22개 |
| 평균 수익률 | -3.35% |
| 최고 수익률 | 9.33% (value_area) |
| 최저 수익률 | -18.80% (lob_maker) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `value_area` | +9.33% | 7.64 | 77.8% | 5.22 | 9 | 2.4% | 0/1 | FAIL |
| 2 | `frama` | +3.33% | 2.71 | 60.0% | 1.78 | 10 | 2.1% | 0/1 | FAIL |
| 3 | `positional_scaling` | +0.77% | 0.72 | 36.4% | 1.20 | 11 | 3.4% | 0/1 | FAIL |
| 4 | `supertrend_multi` | +0.07% | 0.15 | 50.0% | 1.15 | 4 | 1.8% | 0/1 | FAIL |
| 5 | `volume_breakout` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/1 | FAIL |
| 6 | `price_cluster` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/1 | FAIL |
| 7 | `dema_cross` | +0.00% | 0.00 | 0.0% | 0.00 | 0 | 0.0% | 0/1 | FAIL |
| 8 | `htf_ema` | -0.23% | 0.01 | 50.0% | 1.07 | 14 | 10.0% | 0/1 | FAIL |
| 9 | `cmf` | -2.20% | -1.34 | 33.3% | 0.89 | 15 | 4.9% | 0/1 | FAIL |
| 10 | `linear_channel_rev` | -3.38% | -7.62 | 0.0% | 0.00 | 3 | 3.4% | 0/1 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `value_area` | +9.33% | 7.64 | 5.22 | 9 | 0/1 | FAIL |
| `frama` | +3.33% | 2.71 | 1.78 | 10 | 0/1 | FAIL |
| `positional_scaling` | +0.77% | 0.72 | 1.20 | 11 | 0/1 | FAIL |
| `supertrend_multi` | +0.07% | 0.15 | 1.15 | 4 | 0/1 | FAIL |
| `volume_breakout` | +0.00% | 0.00 | 0.00 | 0 | 0/1 | FAIL |
| `price_cluster` | +0.00% | 0.00 | 0.00 | 0 | 0/1 | FAIL |
| `dema_cross` | +0.00% | 0.00 | 0.00 | 0 | 0/1 | FAIL |
| `htf_ema` | -0.23% | 0.01 | 1.07 | 14 | 0/1 | FAIL |
| `cmf` | -2.20% | -1.34 | 0.89 | 15 | 0/1 | FAIL |
| `linear_channel_rev` | -3.38% | -7.62 | 0.00 | 3 | 0/1 | FAIL |
| `engulfing_zone` | -3.72% | -4.51 | 0.36 | 5 | 0/1 | FAIL |
| `narrow_range` | -3.81% | -6.89 | 0.19 | 5 | 0/1 | FAIL |
| `relative_volume` | -4.22% | -3.05 | 0.74 | 18 | 0/1 | FAIL |
| `volatility_cluster` | -4.26% | -3.81 | 0.59 | 12 | 0/1 | FAIL |
| `wick_reversal` | -4.38% | -5.18 | 0.31 | 5 | 0/1 | FAIL |
| `price_action_momentum` | -4.45% | -2.52 | 0.82 | 24 | 0/1 | FAIL |
| `elder_impulse` | -5.19% | -5.39 | 0.37 | 10 | 0/1 | FAIL |
| `acceleration_band` | -6.81% | -6.28 | 0.30 | 8 | 0/1 | FAIL |
| `order_flow_imbalance_v2` | -7.25% | -4.22 | 0.65 | 21 | 0/1 | FAIL |
| `roc_ma_cross` | -7.99% | -6.85 | 0.44 | 16 | 0/1 | FAIL |
| `momentum_quality` | -10.57% | -11.28 | 0.15 | 13 | 0/1 | FAIL |
| `lob_maker` | -18.80% | -9.46 | 0.40 | 24 | 0/1 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: -3.35% -> $9,665
- **Top 5 균등배분**: +2.70% -> $10,270
