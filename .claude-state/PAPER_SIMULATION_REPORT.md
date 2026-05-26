# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-26T05:16:09.714859Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-26T05:20:04.191109Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic GBM x8640 (BTC/USDT-like, seed=495633848)_
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
| 평균 수익률 | 34.47% |
| 최고 수익률 | 155.64% (price_action_momentum) |
| 최저 수익률 | -6.08% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +155.64% | 7.62 | 52.5% | 2.09 | 165 | 13.9% | 0/4 | FAIL |
| 2 | `cmf` | +98.64% | 5.62 | 49.4% | 1.79 | 130 | 14.1% | 0/4 | FAIL |
| 3 | `volume_breakout` | +78.13% | 6.09 | 55.0% | 2.31 | 72 | 6.9% | 0/4 | FAIL |
| 4 | `momentum_quality` | +68.98% | 5.77 | 50.0% | 1.87 | 124 | 12.3% | 0/4 | FAIL |
| 5 | `supertrend_multi` | +68.76% | 5.50 | 48.9% | 1.74 | 129 | 14.1% | 0/4 | FAIL |
| 6 | `lob_maker` | +55.45% | 3.78 | 45.6% | 1.48 | 124 | 14.2% | 0/4 | FAIL |
| 7 | `order_flow_imbalance_v2` | +55.19% | 4.38 | 48.3% | 1.74 | 88 | 13.3% | 0/4 | FAIL |
| 8 | `htf_ema` | +52.60% | 4.62 | 51.9% | 2.00 | 75 | 13.5% | 0/4 | FAIL |
| 9 | `volatility_cluster` | +30.78% | 4.02 | 49.5% | 1.79 | 74 | 9.0% | 0/4 | FAIL |
| 10 | `relative_volume` | +20.13% | 3.06 | 46.9% | 1.63 | 57 | 6.5% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +155.64% | 7.62 | 2.09 | 165 | 0/4 | FAIL |
| `cmf` | +98.64% | 5.62 | 1.79 | 130 | 0/4 | FAIL |
| `volume_breakout` | +78.13% | 6.09 | 2.31 | 72 | 0/4 | FAIL |
| `momentum_quality` | +68.98% | 5.77 | 1.87 | 124 | 0/4 | FAIL |
| `supertrend_multi` | +68.76% | 5.50 | 1.74 | 129 | 0/4 | FAIL |
| `lob_maker` | +55.45% | 3.78 | 1.48 | 124 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +55.19% | 4.38 | 1.74 | 88 | 0/4 | FAIL |
| `htf_ema` | +52.60% | 4.62 | 2.00 | 75 | 0/4 | FAIL |
| `volatility_cluster` | +30.78% | 4.02 | 1.79 | 74 | 0/4 | FAIL |
| `relative_volume` | +20.13% | 3.06 | 1.63 | 57 | 0/4 | FAIL |
| `elder_impulse` | +16.31% | 2.11 | 1.45 | 48 | 0/4 | FAIL |
| `narrow_range` | +13.76% | 2.17 | 1.47 | 54 | 0/4 | FAIL |
| `linear_channel_rev` | +13.30% | 3.20 | 2.18 | 26 | 0/4 | FAIL |
| `acceleration_band` | +12.75% | 1.47 | 1.22 | 96 | 0/4 | FAIL |
| `positional_scaling` | +10.69% | 2.37 | 1.69 | 28 | 0/4 | FAIL |
| `frama` | +5.10% | 0.47 | 1.10 | 84 | 0/4 | FAIL |
| `value_area` | +3.48% | 1.24 | 1.48 | 14 | 0/4 | FAIL |
| `roc_ma_cross` | +3.16% | 0.78 | 1.20 | 36 | 0/4 | FAIL |
| `dema_cross` | +2.76% | 1.25 | 2.52 | 10 | 0/4 | FAIL |
| `wick_reversal` | +0.00% | 0.00 | 0.00 | 0 | 0/4 | FAIL |
| `price_cluster` | -1.12% | -0.45 | 0.88 | 6 | 0/4 | FAIL |
| `engulfing_zone` | -6.08% | -1.13 | 0.83 | 27 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +34.47% -> $13,447
- **Top 5 균등배분**: +94.03% -> $19,403


---

# Paper Trading 시뮬레이션 리포트 — ETH/USDT (Walk-Forward)

_Generated: 2026-05-26T05:23:45.113774Z_
_Symbol: ETH/USDT_
_Data Source: Synthetic GBM x8640 (ETH/USDT-like, seed=1494731801)_
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
| 평균 수익률 | 38.23% |
| 최고 수익률 | 208.40% (price_action_momentum) |
| 최저 수익률 | -20.36% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +208.40% | 8.85 | 53.8% | 2.28 | 176 | 10.9% | 0/4 | FAIL |
| 2 | `cmf` | +126.23% | 6.76 | 53.3% | 2.07 | 116 | 12.5% | 0/4 | FAIL |
| 3 | `supertrend_multi` | +89.72% | 6.54 | 50.5% | 1.83 | 149 | 14.9% | 0/4 | FAIL |
| 4 | `volume_breakout` | +83.89% | 6.53 | 58.1% | 2.47 | 72 | 9.3% | 0/4 | FAIL |
| 5 | `momentum_quality` | +74.33% | 5.97 | 50.1% | 1.87 | 125 | 12.1% | 0/4 | FAIL |
| 6 | `htf_ema` | +59.65% | 5.38 | 52.8% | 2.12 | 76 | 7.5% | 0/4 | FAIL |
| 7 | `roc_ma_cross` | +34.27% | 5.95 | 63.5% | 3.40 | 38 | 5.3% | 0/4 | FAIL |
| 8 | `lob_maker` | +33.82% | 2.58 | 42.2% | 1.30 | 126 | 14.8% | 0/4 | FAIL |
| 9 | `linear_channel_rev` | +31.81% | 5.88 | 66.0% | 4.00 | 32 | 2.9% | 0/4 | FAIL |
| 10 | `relative_volume` | +27.83% | 4.42 | 52.4% | 2.09 | 48 | 6.2% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +208.40% | 8.85 | 2.28 | 176 | 0/4 | FAIL |
| `cmf` | +126.23% | 6.76 | 2.07 | 116 | 0/4 | FAIL |
| `supertrend_multi` | +89.72% | 6.54 | 1.83 | 149 | 0/4 | FAIL |
| `volume_breakout` | +83.89% | 6.53 | 2.47 | 72 | 0/4 | FAIL |
| `momentum_quality` | +74.33% | 5.97 | 1.87 | 125 | 0/4 | FAIL |
| `htf_ema` | +59.65% | 5.38 | 2.12 | 76 | 0/4 | FAIL |
| `roc_ma_cross` | +34.27% | 5.95 | 3.40 | 38 | 0/4 | FAIL |
| `lob_maker` | +33.82% | 2.58 | 1.30 | 126 | 0/4 | FAIL |
| `linear_channel_rev` | +31.81% | 5.88 | 4.00 | 32 | 0/4 | FAIL |
| `relative_volume` | +27.83% | 4.42 | 2.09 | 48 | 0/4 | FAIL |
| `volatility_cluster` | +26.13% | 3.14 | 1.55 | 82 | 0/4 | FAIL |
| `acceleration_band` | +21.54% | 2.35 | 1.34 | 92 | 0/4 | FAIL |
| `positional_scaling` | +20.69% | 4.19 | 2.78 | 26 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +14.98% | 1.51 | 1.22 | 88 | 0/4 | FAIL |
| `value_area` | +12.59% | 3.85 | 6.06 | 14 | 0/4 | FAIL |
| `elder_impulse` | +11.20% | 1.74 | 1.37 | 55 | 0/4 | FAIL |
| `price_cluster` | +2.67% | 0.78 | 251.55 | 2 | 0/4 | FAIL |
| `narrow_range` | +0.39% | 0.11 | 1.08 | 46 | 0/4 | FAIL |
| `wick_reversal` | -1.79% | -1.96 | 0.00 | 1 | 0/4 | FAIL |
| `dema_cross` | -6.32% | -3.42 | 0.53 | 12 | 0/4 | FAIL |
| `engulfing_zone` | -10.56% | -2.58 | 0.57 | 22 | 0/4 | FAIL |
| `frama` | -20.36% | -2.65 | 0.76 | 86 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +38.23% -> $13,823
- **Top 5 균등배분**: +116.51% -> $21,651


---

# Paper Trading 시뮬레이션 리포트 — SOL/USDT (Walk-Forward)

_Generated: 2026-05-26T05:27:27.007340Z_
_Symbol: SOL/USDT_
_Data Source: Synthetic GBM x8640 (SOL/USDT-like, seed=321161971)_
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
| 평균 수익률 | 24.78% |
| 최고 수익률 | 126.14% (price_action_momentum) |
| 최저 수익률 | -7.42% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +126.14% | 7.11 | 51.6% | 1.89 | 162 | 9.4% | 0/4 | FAIL |
| 2 | `cmf` | +99.16% | 5.25 | 49.7% | 1.73 | 126 | 12.6% | 0/4 | FAIL |
| 3 | `supertrend_multi` | +73.78% | 5.89 | 50.0% | 1.82 | 125 | 13.0% | 0/4 | FAIL |
| 4 | `momentum_quality` | +57.72% | 5.05 | 47.8% | 1.73 | 121 | 13.8% | 0/4 | FAIL |
| 5 | `volume_breakout` | +49.26% | 4.57 | 53.3% | 1.95 | 66 | 11.5% | 0/4 | FAIL |
| 6 | `htf_ema` | +42.32% | 4.13 | 50.8% | 1.75 | 72 | 9.7% | 0/4 | FAIL |
| 7 | `acceleration_band` | +34.98% | 3.38 | 46.0% | 1.51 | 96 | 11.8% | 0/4 | FAIL |
| 8 | `roc_ma_cross` | +11.69% | 2.47 | 47.1% | 1.65 | 35 | 6.4% | 0/4 | FAIL |
| 9 | `linear_channel_rev` | +11.48% | 2.40 | 46.9% | 1.59 | 36 | 5.5% | 0/4 | FAIL |
| 10 | `positional_scaling` | +10.59% | 2.35 | 48.0% | 1.75 | 24 | 4.3% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +126.14% | 7.11 | 1.89 | 162 | 0/4 | FAIL |
| `cmf` | +99.16% | 5.25 | 1.73 | 126 | 0/4 | FAIL |
| `supertrend_multi` | +73.78% | 5.89 | 1.82 | 125 | 0/4 | FAIL |
| `momentum_quality` | +57.72% | 5.05 | 1.73 | 121 | 0/4 | FAIL |
| `volume_breakout` | +49.26% | 4.57 | 1.95 | 66 | 0/4 | FAIL |
| `htf_ema` | +42.32% | 4.13 | 1.75 | 72 | 0/4 | FAIL |
| `acceleration_band` | +34.98% | 3.38 | 1.51 | 96 | 0/4 | FAIL |
| `roc_ma_cross` | +11.69% | 2.47 | 1.65 | 35 | 0/4 | FAIL |
| `linear_channel_rev` | +11.48% | 2.40 | 1.59 | 36 | 0/4 | FAIL |
| `positional_scaling` | +10.59% | 2.35 | 1.75 | 24 | 0/4 | FAIL |
| `narrow_range` | +9.89% | 1.96 | 1.44 | 46 | 0/4 | FAIL |
| `elder_impulse` | +7.90% | 1.19 | 1.24 | 56 | 0/4 | FAIL |
| `relative_volume` | +6.49% | 0.94 | 1.23 | 52 | 0/4 | FAIL |
| `frama` | +6.41% | 0.49 | 1.14 | 85 | 0/4 | FAIL |
| `value_area` | +6.08% | 2.12 | 2.13 | 12 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +4.91% | 0.67 | 1.11 | 79 | 0/4 | FAIL |
| `volatility_cluster` | +4.67% | 0.79 | 1.14 | 84 | 0/4 | FAIL |
| `price_cluster` | -1.19% | -1.20 | 0.76 | 3 | 0/4 | FAIL |
| `wick_reversal` | -2.06% | -1.68 | 250.00 | 2 | 0/4 | FAIL |
| `lob_maker` | -3.07% | -0.15 | 1.01 | 118 | 0/4 | FAIL |
| `dema_cross` | -4.51% | -2.29 | 0.55 | 10 | 0/4 | FAIL |
| `engulfing_zone` | -7.42% | -1.90 | 0.72 | 20 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +24.78% -> $12,478
- **Top 5 균등배분**: +81.21% -> $18,121
