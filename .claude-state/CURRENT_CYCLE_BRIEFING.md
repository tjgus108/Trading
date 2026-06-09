# Current Cycle Briefing

_Cycle 291 — B(리스크) + D(ML) + F(리서치)_
_Completed: 2026-06-09_

## 현재 상태 요약

### 완료된 사이클: 291
- **카테고리**: B(리스크) + D(ML) + F(리서치)
- **다음 사이클**: 292 → B(리스크) + D(ML) + F(리서치) (292 mod 5 = 2)

## Bundle OOS 상태 (BTC/USDT 4h, 9-fold, 2022~2024)

| 전략 | 상태 | OOS Sharpe avg | OOS Sharpe std | 비고 |
|------|------|---------------|---------------|------|
| cmf | ❌ FAIL | -0.805 | 3.854 | 2022 베어 구간 약세 |
| supertrend_multi | ❌ FAIL | 4.880 | 2.506 | std=2.506 > 2.5 경계 |
| elder_impulse | ❌ FAIL | -5.912 | 4.107 | 저거래 비율 56% |
| narrow_range | ❌ FAIL | 0.240 | 5.184 | 불안정 |
| value_area | ❌ FAIL | 0.000 | 0.000 | 거래 0건 |

**⚠️ fold 구조 변화**: 9-fold (2022~2024) — 이전 5-fold (2023~2024) 대비 2022 베어마켓 추가됨. cmf는 2023+ 구간에서만 PASS.

## Paper Sim 상태 (BTC/USDT 4h, 8 windows, 2023~2024)

| 항목 | 값 |
|------|-----|
| PASS 전략 수 | 0/22 |
| rank1 전략 | cmf (score=68.3, Sharpe=1.25, trades=23) |
| rank2 전략 | lob_maker (score=63.8, Sharpe=1.18) |

## 핵심 알림

1. **레짐 기반 Kill Switch**: DrawdownMonitor에 BEAR/CRISIS 레짐 시 kill threshold 자동 강화
2. **음수 OOS Sharpe 비례 페널티**: trainer에서 더 음수일수록 더 큰 앙상블 가중치 감소
3. **cmf 레짐 의존성**: 2022 베어 FAIL / 2023+ 불 PASS → 레짐 필터링 필요
4. **supertrend_multi OOS std 경계값**: 2.506 > 2.5 — 다음 사이클에서 std threshold 재검토 가능

## Cycle 291 코드 변경 핵심

1. `src/risk/drawdown_monitor.py`: `should_kill_strategy(regime=...)` 레짐 기반 kill threshold
   - BEAR: min(multiplier, 1.2x), CRISIS/HIGH_VOL: min(multiplier, 1.0x)
2. `src/ml/trainer.py`: `compute_ensemble_weight_recency()` 음수 OOS Sharpe 비례 페널티
   - 기존: 음수 → 고정 0.5x | 개선: clip(0.5 + oos_s*0.2, 0.1, 0.5)
3. 테스트 5개 추가 (regime kill switch 4개 + 비례 페널티 1개)
