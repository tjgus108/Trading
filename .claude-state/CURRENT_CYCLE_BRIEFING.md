# Current Cycle Briefing

_Cycle 294 완료 — 2026-06-10_
_카테고리: D(ML) + E(실행) + F(리서치)_

## 이번 사이클 요약

### 완료한 작업

1. **D(ML)**: `src/ml/trainer.py`에 `compute_ensemble_weight_regime_aware()` 추가
   - BULL/SIDEWAYS/BEAR/HIGH_VOL 레짐별 전략 패널티 계수
   - cmf: SIDEWAYS=0.3, BEAR=0.5 / supertrend_multi: SIDEWAYS=0.2, BEAR=0.4
   - Paper Sim 분석 결과 기반: bull 구간 이외 성능 저하 전략에 가중치 패널티

2. **E(실행)**: `src/backtest/walk_forward.py`에 IS 거래 수 기반 타이브레이커 추가
   - `trades_regularization_scale=0.1` 옵션 추가
   - sideways 구간 0-trades Sharpe 동점 시 거래 수 더 많은 파라미터 선호
   - `optimize_supertrend_multi()`에 scale=0.1 적용

3. **F(리서치)**: Paper Sim + Bundle OOS 결과 분석
   - Paper Sim: 전체 22개 FAIL — trades < 15가 공통 병목 (70%+ FAIL)
   - Bundle OOS: cmf + supertrend_multi 2/5 PASS 유지
   - 레짐별 전략 성능 패턴 확정: BULL 구간만 두 전략 유효

### 현재 성과 지표

- **테스트**: 8392 passed (회귀 없음)
- **Paper Sim**: 0/22 PASS (목표: ≥1 PASS)
- **Bundle OOS**: 2/5 PASS (cmf, supertrend_multi)
- **최고 전략**: cmf (Bundle OOS avg Sharpe=2.508), supertrend_multi (avg=3.674)

### 다음 사이클 우선순위

**Cycle 295 = A(품질) + C(데이터) + F(리서치)**

1. **A**: 저거래 전략(value_area, htf_ema, relative_volume) 파라미터 완화 → trades ≥ 15 달성
2. **C**: SIDEWAYS 레짐 전략 탐색 (momentum_quality, price_cluster가 W5-W6에서 유망)
3. **F**: 거래 빈도 개선 패턴 + 평가 기준 통합 방안 조사
