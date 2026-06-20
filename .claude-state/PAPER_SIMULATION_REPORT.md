# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-06-20T21:23:43.848197Z_
_Symbols: BTC/USDT, ETH/USDT, SOL/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-06-20T21:27:56.676655Z_
_Symbol: BTC/USDT_
_Data Source: CSV BTC/USDT 1h (/home/user/Trading/data/historical)_
_Data Range: 2023-01-01 00:00:00+00:00 ~ 2024-05-14 23:00:00+00:00 (499일)_
_Walk-Forward: 8개 윈도우 (train=5040, test=1440 candles [1h])_
_Initial Balance: $10,000 USDT | Fee: 0.055%/leg (0.11% round-trip) | Slippage: 0.05%_
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
| 테스트 전략 | 20개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 20개 |
| 평균 수익률 | -3.82% |
| 최고 수익률 | 5.60% (price_cluster) |
| 최저 수익률 | -12.35% (wick_reversal) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +5.60% | 0.90 | 37.2% | 1.21 | 41 | 10.8% | 2/8 | FAIL |
| 2 | `roc_ma_cross` | +2.54% | 0.25 | 36.2% | 1.20 | 36 | 9.4% | 2/8 | FAIL |
| 3 | `frama` | +2.20% | 0.33 | 35.2% | 1.15 | 40 | 10.3% | 1/8 | FAIL |
| 4 | `positional_scaling` | +0.65% | -0.25 | 33.7% | 1.12 | 34 | 10.0% | 1/8 | FAIL |
| 5 | `lob_maker` | -0.75% | -0.17 | 35.0% | 1.04 | 75 | 19.2% | 0/8 | FAIL |
| 6 | `dema_cross` | -1.81% | -2.06 | 15.0% | 0.31 | 3 | 2.4% | 0/8 | FAIL |
| 7 | `acceleration_band` | -3.42% | -0.86 | 32.0% | 0.99 | 44 | 14.2% | 1/8 | FAIL |
| 8 | `order_flow_imbalance_v2` | -3.86% | -0.70 | 33.2% | 0.96 | 67 | 16.0% | 0/8 | FAIL |
| 9 | `narrow_range` | -3.94% | -0.76 | 33.5% | 0.93 | 46 | 11.7% | 0/8 | FAIL |
| 10 | `volume_breakout` | -4.85% | -0.94 | 32.4% | 0.94 | 72 | 17.5% | 0/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 76.3 | p100 | 0.90 | 1.17 | 1.21 | 41 | 10.8% | 2/8 | FAIL |
| 2 | `roc_ma_cross` | 67.5 | p94 | 0.25 | 2.54 | 1.20 | 36 | 9.4% | 2/8 | FAIL |
| 3 | `frama` | 64.6 | p89 | 0.33 | 1.70 | 1.15 | 40 | 10.3% | 1/8 | FAIL |
| 4 | `lob_maker` | 57.4 | p84 | -0.17 | 2.15 | 1.04 | 75 | 19.2% | 0/8 | FAIL |
| 5 | `positional_scaling` | 55.3 | p78 | -0.25 | 2.85 | 1.12 | 34 | 10.0% | 1/8 | FAIL |
| 6 | `order_flow_imbalance_v2` | 52.7 | p73 | -0.70 | 2.04 | 0.96 | 67 | 16.0% | 0/8 | FAIL |
| 7 | `price_action_momentum` | 51.5 | p68 | -1.10 | 2.92 | 0.97 | 73 | 18.2% | 1/8 | FAIL |
| 8 | `cmf` | 50.0 | p63 | -1.10 | 1.32 | 0.89 | 68 | 17.5% | 0/8 | FAIL |
| 9 | `acceleration_band` | 49.8 | p57 | -0.86 | 2.53 | 0.99 | 44 | 14.2% | 1/8 | FAIL |
| 10 | `volume_breakout` | 49.6 | p52 | -0.94 | 2.33 | 0.94 | 72 | 17.5% | 0/8 | FAIL |
| 11 | `relative_volume` | 49.3 | p47 | -1.15 | 1.83 | 0.90 | 64 | 14.3% | 0/8 | FAIL |
| 12 | `narrow_range` | 48.9 | p42 | -0.76 | 1.39 | 0.93 | 46 | 11.7% | 0/8 | FAIL |
| 13 | `momentum_quality` | 48.3 | p36 | -1.34 | 3.09 | 0.93 | 70 | 17.4% | 1/8 | FAIL |
| 14 | `htf_ema` | 48.1 | p31 | -0.83 | 0.62 | 0.89 | 43 | 12.3% | 0/8 | FAIL |
| 15 | `elder_impulse` | 40.8 | p26 | -1.35 | 1.21 | 0.82 | 42 | 12.8% | 0/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +5.60% | 0.90 | 1.21 | 41 | 2/8 | FAIL |
| `roc_ma_cross` | +2.54% | 0.25 | 1.20 | 36 | 2/8 | FAIL |
| `frama` | +2.20% | 0.33 | 1.15 | 40 | 1/8 | FAIL |
| `positional_scaling` | +0.65% | -0.25 | 1.12 | 34 | 1/8 | FAIL |
| `lob_maker` | -0.75% | -0.17 | 1.04 | 75 | 0/8 | FAIL |
| `dema_cross` | -1.81% | -2.06 | 0.31 | 3 | 0/8 | FAIL |
| `acceleration_band` | -3.42% | -0.86 | 0.99 | 44 | 1/8 | FAIL |
| `order_flow_imbalance_v2` | -3.86% | -0.70 | 0.96 | 67 | 0/8 | FAIL |
| `narrow_range` | -3.94% | -0.76 | 0.93 | 46 | 0/8 | FAIL |
| `volume_breakout` | -4.85% | -0.94 | 0.94 | 72 | 0/8 | FAIL |
| `htf_ema` | -4.95% | -0.83 | 0.89 | 43 | 0/8 | FAIL |
| `price_action_momentum` | -5.15% | -1.10 | 0.97 | 73 | 1/8 | FAIL |
| `momentum_quality` | -5.26% | -1.34 | 0.93 | 70 | 1/8 | FAIL |
| `engulfing_zone` | -5.71% | -1.34 | 0.78 | 25 | 0/8 | FAIL |
| `linear_channel_rev` | -5.94% | -2.60 | 0.67 | 28 | 0/8 | FAIL |
| `relative_volume` | -6.12% | -1.15 | 0.90 | 64 | 0/8 | FAIL |
| `elder_impulse` | -6.24% | -1.35 | 0.82 | 42 | 0/8 | FAIL |
| `cmf` | -7.81% | -1.10 | 0.89 | 68 | 0/8 | FAIL |
| `volatility_cluster` | -9.20% | -2.22 | 0.80 | 54 | 0/8 | FAIL |
| `wick_reversal` | -12.35% | -3.30 | 0.62 | 42 | 0/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_cluster` | sharpe -0.55 < 1.0 (x1), profit_factor 0.92 < 1.5 (x1), mc_p_value 0.618 > 0.1 (우연 가능성) (x1) |
| `roc_ma_cross` | sharpe 0.20 < 1.0 (x1), profit_factor 1.05 < 1.5 (x1), mc_p_value 0.458 > 0.1 (우연 가능성) (x1) |
| `frama` | sharpe -0.84 < 1.0 (x1), profit_factor 0.88 < 1.5 (x1), mc_p_value 0.600 > 0.1 (우연 가능성) (x1) |
| `positional_scaling` | profit_factor 1.45 < 1.5 (x1), mc_p_value 0.153 > 0.1 (우연 가능성) (x1), sharpe -1.01 < 1.0 (x1) |
| `lob_maker` | sharpe -2.41 < 1.0 (x1), max_drawdown 30.9% > 20% (x1), profit_factor 0.79 < 1.5 (x1) |
| `dema_cross` | profit_factor 0.00 < 1.5 (x4), trades 2 < 15 (x3), trades 3 < 15 (x2) |
| `acceleration_band` | profit_factor 1.40 < 1.5 (x1), mc_p_value 0.188 > 0.1 (우연 가능성) (x1), sharpe -1.37 < 1.0 (x1) |
| `order_flow_imbalance_v2` | mc_p_value 0.866 > 0.1 (우연 가능성) (x2), profit_factor 1.27 < 1.5 (x1), mc_p_value 0.194 > 0.1 (우연 가능성) (x1) |
| `narrow_range` | profit_factor 1.21 < 1.5 (x1), mc_p_value 0.293 > 0.1 (우연 가능성) (x1), sharpe -0.38 < 1.0 (x1) |
| `volume_breakout` | profit_factor 1.27 < 1.5 (x2), sharpe 0.29 < 1.0 (x1), profit_factor 1.06 < 1.5 (x1) |
| `htf_ema` | profit_factor 0.83 < 1.5 (x2), sharpe -0.18 < 1.0 (x1), profit_factor 0.99 < 1.5 (x1) |
| `price_action_momentum` | sharpe 0.85 < 1.0 (x1), profit_factor 1.13 < 1.5 (x1), mc_p_value 0.326 > 0.1 (우연 가능성) (x1) |
| `momentum_quality` | max_drawdown 23.5% > 20% (x2), profit_factor 1.38 < 1.5 (x1), sharpe -0.81 < 1.0 (x1) |
| `engulfing_zone` | sharpe -2.02 < 1.0 (x1), profit_factor 0.67 < 1.5 (x1), mc_p_value 0.804 > 0.1 (우연 가능성) (x1) |
| `linear_channel_rev` | sharpe 0.78 < 1.0 (x1), profit_factor 1.19 < 1.5 (x1), mc_p_value 0.308 > 0.1 (우연 가능성) (x1) |
| `relative_volume` | profit_factor 0.96 < 1.5 (x2), sharpe 0.40 < 1.0 (x1), profit_factor 1.08 < 1.5 (x1) |
| `elder_impulse` | profit_factor 0.90 < 1.5 (x2), sharpe -0.79 < 1.0 (x1), profit_factor 0.91 < 1.5 (x1) |
| `cmf` | profit_factor 0.72 < 1.5 (x3), mc_p_value 0.876 > 0.1 (우연 가능성) (x2), sharpe 0.29 < 1.0 (x1) |
| `volatility_cluster` | profit_factor 0.36 < 1.5 (x2), sharpe -0.62 < 1.0 (x1), profit_factor 0.94 < 1.5 (x1) |
| `wick_reversal` | sharpe -3.81 < 1.0 (x1), max_drawdown 20.9% > 20% (x1), profit_factor 0.54 < 1.5 (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| profit_factor 0.81 < 1.5 | 6 |
| profit_factor 0.91 < 1.5 | 5 |
| profit_factor 0.99 < 1.5 | 4 |
| profit_factor 0.00 < 1.5 | 4 |
| profit_factor 0.72 < 1.5 | 4 |
| mc_p_value 0.509 > 0.1 (우연 가능성) | 3 |
| profit_factor 1.05 < 1.5 | 3 |
| profit_factor 0.80 < 1.5 | 3 |
| profit_factor 0.83 < 1.5 | 3 |
| profit_factor 0.73 < 1.5 | 3 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `dema_cross` | 0 | 5 | 19 | 79.2% |
| `htf_ema` | 0 | 282 | 62 | 18.0% |
| `frama` | 0 | 267 | 56 | 17.3% |
| `price_action_momentum` | 0 | 483 | 101 | 17.3% |
| `cmf` | 0 | 456 | 86 | 15.9% |
| `lob_maker` | 0 | 505 | 94 | 15.7% |
| `relative_volume` | 0 | 437 | 76 | 14.8% |
| `volume_breakout` | 0 | 492 | 84 | 14.6% |
| `elder_impulse` | 0 | 288 | 46 | 13.8% |
| `positional_scaling` | 0 | 233 | 36 | 13.4% |

## 포트폴리오 가상 배분

- **전체 20개 균등배분**: -3.82% -> $9,618
- **Top 5 균등배분**: +2.05% -> $10,205
