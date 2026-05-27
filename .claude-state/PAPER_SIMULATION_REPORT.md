# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-27T14:35:01.460076Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-27T14:49:22.642361Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=922602366, block=36)_
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
| 평균 수익률 | 20.65% |
| 최고 수익률 | 97.73% (price_action_momentum) |
| 최저 수익률 | -4.53% (frama) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_action_momentum` | +97.73% | 6.03 | 48.9% | 1.75 | 154 | 12.2% | 0/4 | FAIL |
| 2 | `momentum_quality` | +61.26% | 5.28 | 48.7% | 1.74 | 123 | 8.1% | 0/4 | FAIL |
| 3 | `lob_maker` | +52.99% | 3.62 | 45.2% | 1.45 | 120 | 13.3% | 0/4 | FAIL |
| 4 | `volume_breakout` | +40.74% | 3.82 | 47.0% | 1.62 | 85 | 11.0% | 0/4 | FAIL |
| 5 | `cmf` | +37.91% | 2.68 | 43.1% | 1.36 | 121 | 18.8% | 0/4 | FAIL |
| 6 | `volatility_cluster` | +33.89% | 4.22 | 49.8% | 1.74 | 79 | 6.6% | 0/4 | FAIL |
| 7 | `supertrend_multi` | +33.01% | 3.38 | 44.6% | 1.44 | 117 | 12.7% | 0/4 | FAIL |
| 8 | `order_flow_imbalance_v2` | +28.97% | 2.76 | 45.2% | 1.40 | 82 | 11.1% | 0/4 | FAIL |
| 9 | `narrow_range` | +26.26% | 3.05 | 45.7% | 1.44 | 94 | 11.0% | 0/4 | FAIL |
| 10 | `elder_impulse` | +14.77% | 2.23 | 45.4% | 1.48 | 47 | 8.8% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_action_momentum` | 65.4 | p100 | 6.03 | 0.80 | 1.75 | 154 | 12.2% | 0/4 | FAIL |
| 2 | `momentum_quality` | 59.9 | p95 | 5.28 | 1.38 | 1.74 | 123 | 8.1% | 0/4 | FAIL |
| 3 | `dema_cross` | 56.5 | p90 | 1.19 | 1.21 | 251.27 | 7 | 2.3% | 0/4 | FAIL |
| 4 | `volatility_cluster` | 53.7 | p85 | 4.22 | 1.08 | 1.74 | 79 | 6.6% | 0/4 | FAIL |
| 5 | `volume_breakout` | 49.7 | p80 | 3.82 | 0.89 | 1.62 | 85 | 11.0% | 0/4 | FAIL |
| 6 | `lob_maker` | 49.6 | p76 | 3.62 | 1.01 | 1.45 | 120 | 13.3% | 0/4 | FAIL |
| 7 | `narrow_range` | 48.1 | p71 | 3.05 | 0.69 | 1.44 | 94 | 11.0% | 0/4 | FAIL |
| 8 | `supertrend_multi` | 47.1 | p66 | 3.38 | 1.34 | 1.44 | 117 | 12.7% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | 45.8 | p61 | 2.76 | 0.67 | 1.40 | 82 | 11.1% | 0/4 | FAIL |
| 10 | `elder_impulse` | 40.5 | p57 | 2.23 | 0.97 | 1.48 | 47 | 8.8% | 0/4 | FAIL |
| 11 | `acceleration_band` | 39.0 | p52 | 1.36 | 0.80 | 1.20 | 92 | 12.3% | 0/4 | FAIL |
| 12 | `cmf` | 38.3 | p47 | 2.68 | 1.52 | 1.36 | 121 | 18.8% | 0/4 | FAIL |
| 13 | `value_area` | 36.7 | p42 | 0.81 | 0.60 | 1.30 | 14 | 4.5% | 0/4 | FAIL |
| 14 | `linear_channel_rev` | 35.7 | p38 | 0.67 | 0.94 | 1.19 | 34 | 5.3% | 0/4 | FAIL |
| 15 | `price_cluster` | 34.4 | p33 | 1.33 | 0.93 | 1.32 | 40 | 10.7% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_action_momentum` | +97.73% | 6.03 | 1.75 | 154 | 0/4 | FAIL |
| `momentum_quality` | +61.26% | 5.28 | 1.74 | 123 | 0/4 | FAIL |
| `lob_maker` | +52.99% | 3.62 | 1.45 | 120 | 0/4 | FAIL |
| `volume_breakout` | +40.74% | 3.82 | 1.62 | 85 | 0/4 | FAIL |
| `cmf` | +37.91% | 2.68 | 1.36 | 121 | 0/4 | FAIL |
| `volatility_cluster` | +33.89% | 4.22 | 1.74 | 79 | 0/4 | FAIL |
| `supertrend_multi` | +33.01% | 3.38 | 1.44 | 117 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +28.97% | 2.76 | 1.40 | 82 | 0/4 | FAIL |
| `narrow_range` | +26.26% | 3.05 | 1.44 | 94 | 0/4 | FAIL |
| `elder_impulse` | +14.77% | 2.23 | 1.48 | 47 | 0/4 | FAIL |
| `acceleration_band` | +11.37% | 1.36 | 1.20 | 92 | 0/4 | FAIL |
| `htf_ema` | +8.94% | 1.03 | 1.21 | 64 | 0/4 | FAIL |
| `price_cluster` | +8.28% | 1.33 | 1.32 | 40 | 0/4 | FAIL |
| `linear_channel_rev` | +2.68% | 0.67 | 1.19 | 34 | 0/4 | FAIL |
| `positional_scaling` | +2.39% | 0.63 | 1.30 | 22 | 0/4 | FAIL |
| `value_area` | +2.28% | 0.81 | 1.30 | 14 | 0/4 | FAIL |
| `dema_cross` | +2.06% | 1.19 | 251.27 | 7 | 0/4 | FAIL |
| `relative_volume` | +0.05% | -0.27 | 1.06 | 49 | 0/4 | FAIL |
| `wick_reversal` | -0.53% | -0.60 | 1.03 | 3 | 0/4 | FAIL |
| `roc_ma_cross` | -2.95% | -0.91 | 0.94 | 32 | 0/4 | FAIL |
| `engulfing_zone` | -3.35% | -0.71 | 0.90 | 22 | 0/4 | FAIL |
| `frama` | -4.53% | -0.59 | 0.99 | 80 | 0/4 | FAIL |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +20.65% -> $12,065
- **Top 5 균등배분**: +58.13% -> $15,812
