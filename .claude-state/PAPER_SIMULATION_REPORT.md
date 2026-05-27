# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-27T00:52:25.482294Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-27T00:55:19.627089Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=601215434, block=36)_
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
| 평균 수익률 | 29.17% |
| 최고 수익률 | 119.58% (price_action_momentum) |
| 최저 수익률 | -10.12% (price_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +119.58% | 6.68 | 49.6% | 1.78 | 167 | 13.4% | 0/4 | FAIL |
| 2 | `momentum_quality` | +92.54% | 6.98 | 53.9% | 2.03 | 116 | 8.3% | 0/4 | FAIL |
| 3 | `cmf` | +58.41% | 3.96 | 46.9% | 1.51 | 112 | 14.8% | 0/4 | FAIL |
| 4 | `volume_breakout` | +56.18% | 4.71 | 48.9% | 1.79 | 93 | 11.9% | 0/4 | FAIL |
| 5 | `narrow_range` | +51.72% | 5.35 | 51.6% | 1.87 | 90 | 7.9% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | +48.86% | 3.80 | 46.2% | 1.63 | 88 | 13.6% | 0/4 | FAIL |
| 7 | `lob_maker` | +38.87% | 2.87 | 43.0% | 1.37 | 121 | 19.2% | 0/4 | FAIL |
| 8 | `supertrend_multi` | +35.06% | 3.68 | 45.4% | 1.46 | 114 | 16.0% | 0/4 | FAIL |
| 9 | `relative_volume` | +29.38% | 4.08 | 49.3% | 1.90 | 58 | 10.1% | 0/4 | FAIL |
| 10 | `acceleration_band` | +28.68% | 2.93 | 45.3% | 1.41 | 92 | 11.5% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 62.6 | p100 | 6.68 | 0.42 | 1.78 | 167 | 13.4% | 0/4 | FAIL |
| 2 | `momentum_quality` | 60.7 | p95 | 6.98 | 0.88 | 2.03 | 116 | 8.3% | 0/4 | FAIL |
| 3 | `narrow_range` | 56.8 | p90 | 5.35 | 0.20 | 1.87 | 90 | 7.9% | 0/4 | FAIL |
| 4 | `wick_reversal` | 56.1 | p85 | 0.49 | 0.86 | 250.00 | 0 | 0.0% | 0/4 | FAIL |
| 5 | `volume_breakout` | 45.8 | p80 | 4.71 | 1.44 | 1.79 | 93 | 11.9% | 0/4 | FAIL |
| 6 | `volatility_cluster` | 45.1 | p76 | 2.90 | 0.51 | 1.44 | 84 | 10.2% | 0/4 | FAIL |
| 7 | `htf_ema` | 44.9 | p71 | 3.24 | 0.52 | 1.57 | 66 | 9.7% | 0/4 | FAIL |
| 8 | `acceleration_band` | 44.2 | p66 | 2.93 | 0.66 | 1.41 | 92 | 11.5% | 0/4 | FAIL |
| 9 | `linear_channel_rev` | 43.5 | p61 | 2.80 | 0.69 | 1.82 | 28 | 4.3% | 0/4 | FAIL |
| 10 | `supertrend_multi` | 43.1 | p57 | 3.68 | 1.03 | 1.46 | 114 | 16.0% | 0/4 | FAIL |
| 11 | `relative_volume` | 42.9 | p52 | 4.08 | 1.27 | 1.90 | 58 | 10.1% | 0/4 | FAIL |
| 12 | `cmf` | 42.5 | p47 | 3.96 | 1.49 | 1.51 | 112 | 14.8% | 0/4 | FAIL |
| 13 | `order_flow_imbalance_v2` | 39.0 | p42 | 3.80 | 1.86 | 1.63 | 88 | 13.6% | 0/4 | FAIL |
| 14 | `lob_maker` | 37.9 | p38 | 2.87 | 1.19 | 1.37 | 121 | 19.2% | 0/4 | FAIL |
| 15 | `elder_impulse` | 37.8 | p33 | 1.84 | 0.73 | 1.38 | 49 | 9.8% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +119.58% | 6.68 | 1.78 | 167 | 0/4 | FAIL |
| `momentum_quality` | +92.54% | 6.98 | 2.03 | 116 | 0/4 | FAIL |
| `cmf` | +58.41% | 3.96 | 1.51 | 112 | 0/4 | FAIL |
| `volume_breakout` | +56.18% | 4.71 | 1.79 | 93 | 0/4 | FAIL |
| `narrow_range` | +51.72% | 5.35 | 1.87 | 90 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +48.86% | 3.80 | 1.63 | 88 | 0/4 | FAIL |
| `lob_maker` | +38.87% | 2.87 | 1.37 | 121 | 0/4 | FAIL |
| `supertrend_multi` | +35.06% | 3.68 | 1.46 | 114 | 0/4 | FAIL |
| `relative_volume` | +29.38% | 4.08 | 1.90 | 58 | 0/4 | FAIL |
| `acceleration_band` | +28.68% | 2.93 | 1.41 | 92 | 0/4 | FAIL |
| `htf_ema` | +28.62% | 3.24 | 1.57 | 66 | 0/4 | FAIL |
| `volatility_cluster` | +21.37% | 2.90 | 1.44 | 84 | 0/4 | FAIL |
| `frama` | +17.59% | 2.01 | 1.33 | 77 | 0/4 | FAIL |
| `linear_channel_rev` | +12.29% | 2.80 | 1.82 | 28 | 0/4 | FAIL |
| `elder_impulse` | +12.12% | 1.84 | 1.38 | 49 | 0/4 | FAIL |
| `roc_ma_cross` | +9.75% | 2.07 | 1.72 | 32 | 0/4 | FAIL |
| `positional_scaling` | +2.59% | 0.73 | 1.22 | 22 | 0/4 | FAIL |
| `wick_reversal` | +0.43% | 0.49 | 250.00 | 0 | 0/4 | FAIL |
| `dema_cross` | -2.07% | -0.78 | 0.92 | 17 | 0/4 | FAIL |
| `value_area` | -4.16% | -1.99 | 0.60 | 13 | 0/4 | FAIL |
| `engulfing_zone` | -5.85% | -1.54 | 0.78 | 20 | 0/4 | FAIL |
| `price_cluster` | -10.12% | -2.43 | 0.66 | 27 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +29.17% -> $12,917
- **Top 5 균등배분**: +75.69% -> $17,568
