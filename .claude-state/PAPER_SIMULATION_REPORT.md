# Paper Trading 시뮬레이션 통합 리포트

_Generated: 2026-07-04T20:26:36.247672Z_
_Symbols: BTC/USDT_

---

# Paper Trading 시뮬레이션 리포트 — BTC/USDT (Walk-Forward)

_Generated: 2026-07-04T20:29:49.162500Z_
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
| 테스트 전략 | 1개 |
| PASS (일관성 50%+) | 0개 |
| FAIL | 1개 |
| 평균 수익률 | 6.28% |
| 최고 수익률 | 6.28% (price_cluster) |
| 최저 수익률 | 6.28% (price_cluster) |

## TOP 10 전략 (평균 수익률 기준)

| # | Name | AvgReturn | AvgSharpe | AvgWR | AvgPF | AvgTrades | AvgMDD | Consistency | Pass |
|---|------|-----------|-----------|-------|-------|-----------|--------|-------------|------|
| 1 | `price_cluster` | +6.28% | 1.06 | 37.7% | 1.32 | 35 | 7.7% | 2/8 | FAIL |

## 상대 순위 (Composite Rank Score)

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_
_0/N PASS 상황에서도 전략 간 상대 우위를 파악할 수 있는 보조 지표_

| Rank | Name | Score | Pctl | AvgSharpe | SharpeStd | AvgPF | AvgTrades | AvgMDD | Consist | Pass |
|------|------|-------|------|-----------|-----------|-------|-----------|--------|---------|------|
| 1 | `price_cluster` | 50.0 | p50 | 1.06 | 1.67 | 1.32 | 35 | 7.7% | 2/8 | FAIL |

## 전체 결과

| Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades | Consistency | Pass |
|------|-----------|-----------|-------|-----------|-------------|------|
| `price_cluster` | +6.28% | 1.06 | 1.32 | 35 | 2/8 | FAIL |

## FAIL 원인 분석

| Strategy | Top Fail Reasons (reason x count) |
|----------|-----------------------------------|
| `price_cluster` | sharpe -1.16 < 1.0 (x1), profit_factor 0.82 < 1.5 (x1), mc_p_value 0.714 > 0.1 (우연 가능성) (x1) |

### 전체 FAIL 원인 빈도 (상위 10)

| Fail Reason | Total Count |
|-------------|-------------|
| sharpe -1.16 < 1.0 | 1 |
| profit_factor 0.82 < 1.5 | 1 |
| mc_p_value 0.714 > 0.1 (우연 가능성) | 1 |
| sharpe -0.41 < 1.0 | 1 |
| profit_factor 0.95 < 1.5 | 1 |
| mc_p_value 0.586 > 0.1 (우연 가능성) | 1 |
| sharpe -0.71 < 1.0 | 1 |
| profit_factor 0.89 < 1.5 | 1 |
| mc_p_value 0.635 > 0.1 (우연 가능성) | 1 |
| sharpe 0.49 < 1.0 | 1 |

## 윈도우별 상세 분석 (상위 5 전략)

_각 전략의 윈도우별 Sharpe/PF/Trades/Pass 상세. FAIL 원인 진단용._

### `price_cluster` (rank_score=50.0, consistency=2/8, regime_mismatch=2/8)

| Window | IS_Sh | Sharpe | PF | Trades | MDD | SlipH% | Market | IS_Reg | OOS_Reg | Match | Pass | Fail Reasons |
|--------|-------|--------|-----|--------|-----|--------|--------|--------|---------|-------|------|--------------|
| W1 | -0.33 | -1.16 | 0.82 | 36 | 11.6% | 0% | bull | UP↑ | UP↑ | ✓ | ❌ | sharpe -1.16 < 1.0; profit_factor 0.82 < 1.5 |
| W2 | -0.24 | -0.41 | 0.95 | 38 | 7.6% | 3% | bull | UP↑ | RG~ | ✗ | ❌ | sharpe -0.41 < 1.0; profit_factor 0.95 < 1.5 |
| W3 | -0.03 | -0.71 | 0.89 | 35 | 9.0% | 9% | bear | RG~ | RG~ | ✓ | ❌ | sharpe -0.71 < 1.0; profit_factor 0.89 < 1.5 |
| W4 | -0.20 | 0.49 | 1.11 | 34 | 8.9% | 6% | bear | RG~ | RG~ | ✓ | ❌ | sharpe 0.49 < 1.0; profit_factor 1.11 < 1.5 |
| W5 | -0.12 | 2.36 | 1.60 | 35 | 4.7% | 0% | sideways | RG~ | RG~ | ✓ | ❌ | mc_p_value 0.116 > 0.1 (우연 가능성) |
| W6 | -0.05 | 3.84 | 2.05 | 35 | 4.7% | 0% | sideways | RG~ | RG~ | ✓ | ✅ |  |
| W7 | -0.02 | 1.52 | 1.32 | 37 | 7.2% | 0% | bull | RG~ | RG~ | ✓ | ❌ | profit_factor 1.32 < 1.5; mc_p_value 0.221 > 0.1 (우연 가능성) |
| W8 | 1.05 | 2.56 | 1.77 | 30 | 8.1% | 0% | bull | UP↑ | RG~ | ✗ | ✅ |  |

## 2단계 손실 스케일 적용 현황

_연속손실 ≥2: 75% 스케일(half), ≥5: 50% 스케일(full) 적용 횟수_

| Strategy | Half(75%) | Full(50%) | 비율(full/half) |
|----------|-----------|-----------|-----------------|
| `price_cluster` | 85 | 14 | 0.16 |

## 슬리피지 레짐 분포 (상위 10)

_adaptive_slippage=True 시 진입별 레짐 카운트 (low/normal/high)_

| Strategy | Low | Normal | High | High% |
|----------|-----|--------|------|-------|
| `price_cluster` | 0 | 274 | 6 | 2.1% |

## 포트폴리오 가상 배분

- **전체 1개 균등배분**: +6.28% -> $10,628
- **Top 5 균등배분**: +6.28% -> $10,628
