# 5-Bundle Rolling OOS Validation Report

_Generated: 2026-06-03T05:15:31.605328Z_
_Symbol: BTC/USDT | Timeframe: 4h_
_Criteria: WFE >= 0.50, OOS Sharpe >= IS*0.60, OOS MDD <= IS*2.0_

## Summary

| Strategy | Folds | Avg WFE | Avg OOS Sharpe | Avg OOS PF | All Pass | Fail Reasons |
|----------|-------|---------|----------------|------------|----------|--------------|
| cmf | 5 | 4.433 | 2.508 | 1.387 | FAIL | Failed folds: [2, 3]; OOS Sharpe std 1.888 > 1.5 (불안정) |
| elder_impulse | 5 | -0.723 | -2.941 | 0.691 | FAIL | 저거래 fold 제외 (trades<10): [0, 4]; Failed folds: [1, 2, 3]; OOS Sharpe std 3.117 > 1.5 (불안정) |
| wick_reversal | 5 | 0.000 | 1.772 | 1.316 | FAIL | 저거래 fold 제외 (trades<10): [0, 1, 2, 3]; 저거래 fold 비율 80% > 40% (신호 부족); Failed folds: [4] |
| narrow_range | 5 | -0.537 | -1.287 | 0.863 | FAIL | 저거래 fold 제외 (trades<10): [0, 3]; Failed folds: [1, 4]; OOS Sharpe std 2.695 > 1.5 (불안정) |
| value_area | 5 | 0.062 | 0.713 | 1.155 | FAIL | 저거래 fold 제외 (trades<10): [2, 4]; Failed folds: [0, 3]; OOS Sharpe std 2.018 > 1.5 (불안정) |

**PASS: 0/5** (none)
**FAIL: 5/5** (cmf, elder_impulse, wick_reversal, narrow_range, value_area)

## Composite Rank Score

_점수 구성: Sharpe(30%) + PF(20%) + Trades(15%) + MDD역수(15%) + Consistency(10%) + Sharpe안정성(10%)_

| Rank | Strategy | Score | Pctl | OOS Sharpe | SharpeStd | OOS PF | Avg Trades | Avg MDD | Consist | Pass |
|------|----------|-------|------|------------|-----------|-------|------------|---------|---------|------|
| 1 | cmf | 80.6 | p100 | 2.508 | 1.888 | 1.387 | 17.0 | 5.19% | 60% | FAIL |
| 2 | wick_reversal | 54.1 | p75 | 1.772 | 0.000 | 1.316 | 7.6 | 3.29% | 40% | FAIL |
| 3 | value_area | 46.6 | p50 | 0.713 | 2.018 | 1.155 | 9.4 | 2.92% | 40% | FAIL |
| 4 | narrow_range | 17.7 | p25 | -1.287 | 2.695 | 0.863 | 9.4 | 5.47% | 40% | FAIL |
| 5 | elder_impulse | 7.9 | p0 | -2.941 | 3.117 | 0.691 | 9.8 | 4.17% | 40% | FAIL |

## IS Sharpe 음수 진단

| Strategy | 음수 IS fold | 전체 fold | 음수 비율 | 진단 |
|----------|-------------|-----------|----------|------|
| cmf | 1 | 5 | 20% | 🟢 IS 대체로 양수 |
| elder_impulse | 1 | 5 | 20% | 🟢 IS 대체로 양수 |
| wick_reversal | 2 | 5 | 40% | 🟡 IS 일부 음수 |
| narrow_range | 2 | 5 | 40% | 🟡 IS 일부 음수 |
| value_area | 2 | 5 | 40% | 🟡 IS 일부 음수 |

## Fold Details

### cmf

| Fold | IS Sharpe | OOS Sharpe | WFE | OOS PF | OOS Trades | IS MDD | OOS MDD | Pass |
|------|-----------|------------|-----|--------|------------|-------|---------|------|
| 0 | -1.499 | 5.111 | 0.500 | 1.870 | 16 | 14.82% | 3.83% | PASS |
| 1 | 0.198 | 3.858 | 19.485 | 1.573 | 18 | 11.71% | 8.21% | PASS |
| 2 | 1.478 | 0.642 | 0.434 | 1.088 | 16 | 11.08% | 3.02% | FAIL |
| 3 | 3.295 | 1.480 | 0.449 | 1.207 | 18 | 8.85% | 6.90% | FAIL |
| 4 | 1.119 | 1.451 | 1.297 | 1.198 | 17 | 13.08% | 4.00% | PASS |

**Fail reasons:** Failed folds: [2, 3]; OOS Sharpe std 1.888 > 1.5 (불안정)

### elder_impulse

| Fold | IS Sharpe | OOS Sharpe | WFE | OOS PF | OOS Trades | IS MDD | OOS MDD | Pass |
|------|-----------|------------|-----|--------|------------|-------|---------|------|
| 0 | 2.211 | 8.714 | 3.941 | 6.853 | 8 | 5.39% | 1.06% | PASS |
| 1 | 5.372 | 0.568 | 0.106 | 1.092 | 11 | 2.43% | 5.16% | FAIL |
| 2 | 5.883 | -5.389 | -0.916 | 0.457 | 14 | 5.16% | 7.65% | FAIL |
| 3 | 2.945 | -4.003 | -1.359 | 0.523 | 10 | 10.58% | 6.28% | FAIL |
| 4 | -3.380 | 8.125 | 0.500 | 15.201 | 6 | 18.95% | 0.69% | PASS |

**Fail reasons:** 저거래 fold 제외 (trades<10): [0, 4]; Failed folds: [1, 2, 3]; OOS Sharpe std 3.117 > 1.5 (불안정)

### wick_reversal

| Fold | IS Sharpe | OOS Sharpe | WFE | OOS PF | OOS Trades | IS MDD | OOS MDD | Pass |
|------|-----------|------------|-----|--------|------------|-------|---------|------|
| 0 | -1.598 | 8.015 | 0.500 | 5.996 | 8 | 9.01% | 1.07% | PASS |
| 1 | 0.590 | -4.606 | -7.807 | 0.408 | 8 | 8.85% | 6.42% | FAIL |
| 2 | 0.573 | -2.046 | -3.571 | 0.696 | 7 | 7.74% | 3.08% | FAIL |
| 3 | 1.272 | 2.866 | 2.253 | 1.997 | 5 | 7.61% | 1.41% | PASS |
| 4 | -1.032 | 1.772 | 0.000 | 1.316 | 10 | 8.59% | 4.48% | FAIL |

**Fail reasons:** 저거래 fold 제외 (trades<10): [0, 1, 2, 3]; 저거래 fold 비율 80% > 40% (신호 부족); Failed folds: [4]

### narrow_range

| Fold | IS Sharpe | OOS Sharpe | WFE | OOS PF | OOS Trades | IS MDD | OOS MDD | Pass |
|------|-----------|------------|-----|--------|------------|-------|---------|------|
| 0 | -2.065 | 3.764 | 0.500 | 1.990 | 8 | 11.84% | 2.10% | PASS |
| 1 | 1.676 | -3.828 | -2.284 | 0.532 | 10 | 6.81% | 6.93% | FAIL |
| 2 | 2.293 | 1.540 | 0.672 | 1.302 | 10 | 6.93% | 4.72% | PASS |
| 3 | 0.780 | -10.794 | -13.838 | 0.108 | 9 | 6.93% | 8.35% | FAIL |
| 4 | -4.111 | -1.573 | 0.000 | 0.756 | 10 | 11.98% | 5.24% | FAIL |

**Fail reasons:** 저거래 fold 제외 (trades<10): [0, 3]; Failed folds: [1, 4]; OOS Sharpe std 2.695 > 1.5 (불안정)

### value_area

| Fold | IS Sharpe | OOS Sharpe | WFE | OOS PF | OOS Trades | IS MDD | OOS MDD | Pass |
|------|-----------|------------|-----|--------|------------|-------|---------|------|
| 0 | -1.466 | -0.091 | 0.000 | 0.991 | 11 | 11.50% | 5.11% | FAIL |
| 1 | -1.909 | 3.009 | 0.500 | 1.582 | 11 | 11.06% | 2.09% | PASS |
| 2 | 1.276 | 3.129 | 2.452 | 1.960 | 6 | 7.07% | 1.65% | PASS |
| 3 | 2.492 | -0.780 | -0.313 | 0.892 | 11 | 5.11% | 3.01% | FAIL |
| 4 | 3.054 | -0.283 | -0.093 | 0.954 | 8 | 2.10% | 2.74% | FAIL |

**Fail reasons:** 저거래 fold 제외 (trades<10): [2, 4]; Failed folds: [0, 3]; OOS Sharpe std 2.018 > 1.5 (불안정)
