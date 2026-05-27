# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-27T10:10:53.131298Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-27T10:13:44.973759Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=244977657, block=36)_
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
| 평균 수익률 | 4.54% |
| 최고 수익률 | 43.21% (momentum_quality) |
| 최저 수익률 | -11.75% (roc_ma_cross) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `momentum_quality` | +43.21% | 3.96 | 46.5% | 1.56 | 109 | 12.1% | 0/4 | FAIL |
| 2 | `supertrend_multi` | +33.83% | 3.58 | 47.2% | 1.60 | 77 | 11.2% | 0/4 | FAIL |
| 3 | `price_action_momentum` | +30.90% | 2.37 | 40.9% | 1.25 | 162 | 20.1% | 0/4 | FAIL |
| 4 | `order_flow_imbalance_v2` | +10.96% | 1.22 | 40.8% | 1.19 | 83 | 16.5% | 0/4 | FAIL |
| 5 | `volume_breakout` | +10.84% | 1.13 | 39.6% | 1.17 | 94 | 17.1% | 0/4 | FAIL |
| 6 | `lob_maker` | +10.63% | 1.10 | 39.7% | 1.14 | 116 | 14.3% | 0/4 | FAIL |
| 7 | `narrow_range` | +10.43% | 1.36 | 41.2% | 1.21 | 98 | 12.3% | 0/4 | FAIL |
| 8 | `volatility_cluster` | +5.50% | 0.75 | 40.5% | 1.18 | 70 | 12.8% | 0/4 | FAIL |
| 9 | `elder_impulse` | +1.88% | 0.33 | 39.2% | 1.08 | 61 | 9.9% | 0/4 | FAIL |
| 10 | `wick_reversal` | -0.59% | -1.06 | 0.0% | 0.00 | 0 | 0.6% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `momentum_quality` | 74.1 | p100 | 3.96 | 2.01 | 1.56 | 109 | 12.1% | 0/4 | FAIL |
| 2 | `supertrend_multi` | 69.0 | p95 | 3.58 | 2.34 | 1.60 | 77 | 11.2% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 65.8 | p90 | 2.37 | 1.51 | 1.25 | 162 | 20.1% | 0/4 | FAIL |
| 4 | `lob_maker` | 63.9 | p85 | 1.10 | 0.26 | 1.14 | 116 | 14.3% | 0/4 | FAIL |
| 5 | `narrow_range` | 61.6 | p80 | 1.36 | 1.07 | 1.21 | 98 | 12.3% | 0/4 | FAIL |
| 6 | `order_flow_imbalance_v2` | 57.6 | p76 | 1.22 | 0.92 | 1.19 | 83 | 16.5% | 0/4 | FAIL |
| 7 | `volume_breakout` | 55.3 | p71 | 1.13 | 1.40 | 1.17 | 94 | 17.1% | 0/4 | FAIL |
| 8 | `elder_impulse` | 53.4 | p66 | 0.33 | 1.08 | 1.08 | 61 | 9.9% | 0/4 | FAIL |
| 9 | `acceleration_band` | 50.9 | p61 | -0.16 | 0.46 | 1.01 | 102 | 20.1% | 0/4 | FAIL |
| 10 | `volatility_cluster` | 50.3 | p57 | 0.75 | 2.23 | 1.18 | 70 | 12.8% | 0/4 | FAIL |
| 11 | `relative_volume` | 46.8 | p52 | -0.86 | 0.60 | 0.92 | 62 | 13.0% | 0/4 | FAIL |
| 12 | `value_area` | 46.2 | p47 | -0.32 | 1.36 | 1.00 | 16 | 6.4% | 0/4 | FAIL |
| 13 | `engulfing_zone` | 45.0 | p42 | -0.52 | 0.69 | 0.92 | 23 | 11.5% | 0/4 | FAIL |
| 14 | `frama` | 43.0 | p38 | -1.02 | 0.85 | 0.91 | 79 | 18.3% | 0/4 | FAIL |
| 15 | `linear_channel_rev` | 42.9 | p33 | -0.42 | 1.96 | 1.03 | 32 | 9.3% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `momentum_quality` | +43.21% | 3.96 | 1.56 | 109 | 0/4 | FAIL |
| `supertrend_multi` | +33.83% | 3.58 | 1.60 | 77 | 0/4 | FAIL |
| `price_action_momentum` | +30.90% | 2.37 | 1.25 | 162 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +10.96% | 1.22 | 1.19 | 83 | 0/4 | FAIL |
| `volume_breakout` | +10.84% | 1.13 | 1.17 | 94 | 0/4 | FAIL |
| `lob_maker` | +10.63% | 1.10 | 1.14 | 116 | 0/4 | FAIL |
| `narrow_range` | +10.43% | 1.36 | 1.21 | 98 | 0/4 | FAIL |
| `volatility_cluster` | +5.50% | 0.75 | 1.18 | 70 | 0/4 | FAIL |
| `elder_impulse` | +1.88% | 0.33 | 1.08 | 61 | 0/4 | FAIL |
| `wick_reversal` | -0.59% | -1.06 | 0.00 | 0 | 0/4 | FAIL |
| `value_area` | -0.74% | -0.32 | 1.00 | 16 | 0/4 | FAIL |
| `cmf` | -1.29% | -0.24 | 1.02 | 118 | 0/4 | FAIL |
| `linear_channel_rev` | -1.44% | -0.42 | 1.03 | 32 | 0/4 | FAIL |
| `engulfing_zone` | -2.58% | -0.52 | 0.92 | 23 | 0/4 | FAIL |
| `acceleration_band` | -3.08% | -0.16 | 1.01 | 102 | 0/4 | FAIL |
| `dema_cross` | -3.89% | -1.54 | 0.69 | 15 | 0/4 | FAIL |
| `positional_scaling` | -5.29% | -1.28 | 0.83 | 32 | 0/4 | FAIL |
| `relative_volume` | -5.30% | -0.86 | 0.92 | 62 | 0/4 | FAIL |
| `price_cluster` | -5.33% | -1.01 | 0.93 | 42 | 0/4 | FAIL |
| `htf_ema` | -7.92% | -0.88 | 0.93 | 76 | 0/4 | FAIL |
| `frama` | -9.12% | -1.02 | 0.91 | 79 | 0/4 | FAIL |
| `roc_ma_cross` | -11.75% | -2.83 | 0.66 | 41 | 0/4 | FAIL |

## FAIL 진단 (상위 FAIL 전략 fail_reasons 집계)

_다음 사이클 개선 방향 파악용: FAIL 주원인 분포_

- `other`: 36건
- `low_pf`: 32건
- `low_sharpe`: 14건
- `high_mdd`: 6건
- `low_trades`: 4건

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +4.54% -> $10,454
- **Top 5 균등배분**: +25.95% -> $12,595
