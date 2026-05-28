# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-05-28T22:34:40.125348Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-05-28T22:44:09.013866Z_
_Symbol: BTC/USDT_
_Data Source: Synthetic BlockBootstrap x8640 (BTC/USDT-like, seed=173493110, block=24)_
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
| 평균 수익률 | 7.09% |
| 최고 수익률 | 36.98% (supertrend_multi) |
| 최저 수익률 | -6.27% (engulfing_zone) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `supertrend_multi` | +36.98% | 3.80 | 48.2% | 1.56 | 96 | 9.7% | 0/4 | FAIL |
| 2 | `price_action_momentum` | +36.42% | 2.49 | 43.2% | 1.30 | 153 | 16.1% | 0/4 | FAIL |
| 3 | `momentum_quality` | +34.41% | 3.27 | 44.4% | 1.47 | 107 | 9.5% | 0/4 | FAIL |
| 4 | `lob_maker` | +23.96% | 1.52 | 40.5% | 1.21 | 129 | 17.1% | 0/4 | FAIL |
| 5 | `volume_breakout` | +14.16% | 1.22 | 41.0% | 1.20 | 96 | 13.4% | 0/4 | FAIL |
| 6 | `linear_channel_rev` | +10.21% | 2.18 | 46.4% | 1.58 | 33 | 6.5% | 0/4 | FAIL |
| 7 | `acceleration_band` | +5.26% | 0.53 | 38.8% | 1.12 | 106 | 17.7% | 0/4 | FAIL |
| 8 | `roc_ma_cross` | +5.16% | 1.14 | 41.0% | 1.26 | 40 | 9.6% | 0/4 | FAIL |
| 9 | `order_flow_imbalance_v2` | +4.26% | 0.07 | 37.4% | 1.09 | 86 | 20.2% | 0/4 | FAIL |
| 10 | `elder_impulse` | +3.77% | 0.33 | 38.4% | 1.13 | 64 | 13.9% | 0/4 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `supertrend_multi` | 82.4 | p100 | 3.80 | 1.08 | 1.56 | 96 | 9.7% | 0/4 | FAIL |
| 2 | `momentum_quality` | 75.2 | p95 | 3.27 | 2.14 | 1.47 | 107 | 9.5% | 0/4 | FAIL |
| 3 | `price_action_momentum` | 67.9 | p90 | 2.49 | 2.46 | 1.30 | 153 | 16.1% | 0/4 | FAIL |
| 4 | `linear_channel_rev` | 67.6 | p85 | 2.18 | 1.34 | 1.58 | 33 | 6.5% | 0/4 | FAIL |
| 5 | `roc_ma_cross` | 59.0 | p80 | 1.14 | 0.67 | 1.26 | 40 | 9.6% | 0/4 | FAIL |
| 6 | `lob_maker` | 57.9 | p76 | 1.52 | 2.50 | 1.21 | 129 | 17.1% | 0/4 | FAIL |
| 7 | `volume_breakout` | 55.9 | p71 | 1.22 | 2.23 | 1.20 | 96 | 13.4% | 0/4 | FAIL |
| 8 | `value_area` | 53.7 | p66 | 0.75 | 1.91 | 1.41 | 20 | 6.0% | 0/4 | FAIL |
| 9 | `positional_scaling` | 53.5 | p61 | 0.73 | 1.40 | 1.31 | 25 | 8.6% | 0/4 | FAIL |
| 10 | `acceleration_band` | 50.6 | p57 | 0.53 | 1.91 | 1.12 | 106 | 17.7% | 0/4 | FAIL |
| 11 | `volatility_cluster` | 49.9 | p52 | 0.53 | 1.69 | 1.12 | 86 | 17.1% | 0/4 | FAIL |
| 12 | `relative_volume` | 47.3 | p47 | -0.26 | 1.18 | 1.01 | 63 | 10.4% | 0/4 | FAIL |
| 13 | `elder_impulse` | 46.0 | p42 | 0.33 | 2.29 | 1.13 | 64 | 13.9% | 0/4 | FAIL |
| 14 | `price_cluster` | 41.8 | p38 | -0.49 | 0.84 | 0.96 | 41 | 15.3% | 0/4 | FAIL |
| 15 | `narrow_range` | 41.6 | p33 | -0.60 | 1.26 | 0.98 | 96 | 21.5% | 0/4 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `supertrend_multi` | +36.98% | 3.80 | 1.56 | 96 | 0/4 | FAIL |
| `price_action_momentum` | +36.42% | 2.49 | 1.30 | 153 | 0/4 | FAIL |
| `momentum_quality` | +34.41% | 3.27 | 1.47 | 107 | 0/4 | FAIL |
| `lob_maker` | +23.96% | 1.52 | 1.21 | 129 | 0/4 | FAIL |
| `volume_breakout` | +14.16% | 1.22 | 1.20 | 96 | 0/4 | FAIL |
| `linear_channel_rev` | +10.21% | 2.18 | 1.58 | 33 | 0/4 | FAIL |
| `acceleration_band` | +5.26% | 0.53 | 1.12 | 106 | 0/4 | FAIL |
| `roc_ma_cross` | +5.16% | 1.14 | 1.26 | 40 | 0/4 | FAIL |
| `order_flow_imbalance_v2` | +4.26% | 0.07 | 1.09 | 86 | 0/4 | FAIL |
| `elder_impulse` | +3.77% | 0.33 | 1.13 | 64 | 0/4 | FAIL |
| `volatility_cluster` | +3.73% | 0.53 | 1.12 | 86 | 0/4 | FAIL |
| `value_area` | +2.43% | 0.75 | 1.41 | 20 | 0/4 | FAIL |
| `positional_scaling` | +2.30% | 0.73 | 1.31 | 25 | 0/4 | FAIL |
| `cmf` | +0.58% | -0.47 | 1.05 | 121 | 0/4 | FAIL |
| `wick_reversal` | -0.71% | -1.05 | 0.00 | 0 | 0/4 | FAIL |
| `dema_cross` | -1.45% | -0.76 | 0.91 | 15 | 0/4 | FAIL |
| `relative_volume` | -1.45% | -0.26 | 1.01 | 63 | 0/4 | FAIL |
| `htf_ema` | -2.42% | -0.43 | 1.02 | 78 | 0/4 | FAIL |
| `price_cluster` | -3.71% | -0.49 | 0.96 | 41 | 0/4 | FAIL |
| `narrow_range` | -5.48% | -0.60 | 0.98 | 96 | 0/4 | FAIL |
| `frama` | -6.24% | -0.94 | 0.96 | 86 | 0/4 | FAIL |
| `engulfing_zone` | -6.27% | -1.26 | 0.86 | 28 | 0/4 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `supertrend_multi` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.392 > 0.05 (우연 가능성) (x1), profit_factor 1.50 < 1.5 (x1) |
| `price_action_momentum` | sharpe -0.80 < 1.0 (x1), profit_factor 0.96 < 1.5 (x1), mc_p_value 0.550 > 0.05 (우연 가능성) (x1) |
| `momentum_quality` | sharpe 0.36 < 1.0 (x1), profit_factor 1.07 < 1.5 (x1), mc_p_value 0.494 > 0.05 (우연 가능성) (x1) |
| `lob_maker` | sharpe -1.65 < 1.0 (x1), max_drawdown 27.4% > 20% (x1), profit_factor 0.87 < 1.5 (x1) |
| `volume_breakout` | sharpe -1.59 < 1.0 (x1), profit_factor 0.86 < 1.5 (x1), mc_p_value 0.568 > 0.05 (우연 가능성) (x1) |
| `linear_channel_rev` | profit_factor 1.40 < 1.5 (x1), mc_p_value 0.452 > 0.05 (우연 가능성) (x1), sharpe 0.31 < 1.0 (x1) |
| `acceleration_band` | max_drawdown 22.5% > 20% (x2), sharpe 0.31 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1) |
| `roc_ma_cross` | sharpe 0.49 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1), mc_p_value 0.452 > 0.05 (우연 가능성) (x1) |
| `order_flow_imbalance_v2` | profit_factor 0.78 < 1.5 (x2), sharpe -2.40 < 1.0 (x1), max_drawdown 22.2% > 20% (x1) |
| `elder_impulse` | sharpe -1.62 < 1.0 (x1), profit_factor 0.83 < 1.5 (x1), mc_p_value 0.572 > 0.05 (우연 가능성) (x1) |
| `volatility_cluster` | sharpe 0.37 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1), mc_p_value 0.496 > 0.05 (우연 가능성) (x1) |
| `value_area` | sharpe 0.41 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.468 > 0.05 (우연 가능성) (x1) |
| `positional_scaling` | sharpe -0.12 < 1.0 (x1), profit_factor 1.00 < 1.5 (x1), mc_p_value 0.488 > 0.05 (우연 가능성) (x1) |
| `cmf` | sharpe -2.24 < 1.0 (x1), max_drawdown 26.4% > 20% (x1), profit_factor 0.82 < 1.5 (x1) |
| `wick_reversal` | profit_factor 0.00 < 1.5 (x2), trades 1 < 15 (x2), no trades generated (x2) |
| `dema_cross` | sharpe -1.00 < 1.0 (x1), profit_factor 0.78 < 1.5 (x1), mc_p_value 0.526 > 0.05 (우연 가능성) (x1) |
| `relative_volume` | sharpe -1.03 < 1.0 (x1), profit_factor 0.90 < 1.5 (x1), mc_p_value 0.552 > 0.05 (우연 가능성) (x1) |
| `htf_ema` | sharpe -0.80 < 1.0 (x1), profit_factor 0.94 < 1.5 (x1), mc_p_value 0.542 > 0.05 (우연 가능성) (x1) |
| `price_cluster` | sharpe -1.60 < 1.0 (x1), max_drawdown 23.4% > 20% (x1), profit_factor 0.81 < 1.5 (x1) |
| `narrow_range` | max_drawdown 27.0% > 20% (x2), sharpe 0.01 < 1.0 (x1), profit_factor 1.04 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| mc_p_value 0.492 > 0.05 (우연 가능성) | 3 |
| profit_factor 0.91 < 1.5 | 3 |
| profit_factor 0.78 < 1.5 | 3 |
| profit_factor 0.90 < 1.5 | 3 |
| sharpe -0.80 < 1.0 | 2 |
| profit_factor 0.96 < 1.5 | 2 |
| mc_p_value 0.550 > 0.05 (우연 가능성) | 2 |
| mc_p_value 0.432 > 0.05 (우연 가능성) | 2 |
| profit_factor 0.87 < 1.5 | 2 |
| mc_p_value 0.576 > 0.05 (우연 가능성) | 2 |

## 포트폴리오 가상 배분

- **전체 22개 균등배분**: +7.09% -> $10,709
- **Top 5 균등배분**: +29.19% -> $12,919
