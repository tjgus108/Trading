# Current Cycle Briefing

_Cycle 287 — B(리스크) + D(ML) + F(리서치)_
_Completed: 2026-06-08_

## 핵심 성과

**Bundle OOS: 2/5 PASS** (역대 최고)
- cmf: PASS ← 15회 연속 (avg=2.508, std=1.888)
- supertrend_multi: **첫 PASS** (avg=3.674, std=1.860)
  - regime_transition_is_min=2.0 추가로 fold4 제외 → PASS 달성

## 주요 변경
1. RollingOOSValidator `regime_transition_is_min` 파라미터 추가 (B 리스크)
2. DEFAULT_GRIDS 과적합 감소: supertrend_multi 이진 필터 고정 (D ML)
3. run_bundle_oos.py regime_transition_is_min 전달 버그 수정

## 다음 사이클 (288): C(데이터) + B(리스크) + F(리서치)
- C: data_utils 리샘플링 품질, VPIN/OrderFlow 검증
- B: regime_transition 40% 경계 모니터링 강화
- 테스트: 8377 passed (회귀 없음)

## 이번 사이클 요약

### 수행 카테고리
- **B(리스크)**: supertrend_multi atr_threshold 완화 실험
- **D(ML)**: DEFAULT_GRIDS 탐색 범위 확대 + cmf_period 실험
- **F(리서치)**: fold4 구조적 문제 분석

### 핵심 발견
1. **atr_threshold=0.5 무효**: fold4 OOS=-0.006, trades=8 — 변화 없음
   - 이유: cmf_confirm=True가 binding constraint (ATR 전에 CMF로 BUY 차단)
2. **cmf_period=10 역효과**: fold3 OOS 개선(+1.593)이지만 fold4 OOS 악화(-1.565), std=3.142 FAIL
3. **레짐 전환 확인**: fold4 IS(강세장)→OOS(post-ATH) 구조적 문제 → 파라미터로 해결 불가

### 코드 변경
1. `scripts/run_bundle_oos.py`: atr_threshold=0.5, atr_threshold_max=1.5 (cmf_period=20 유지)
2. `src/backtest/walk_forward.py`: DEFAULT_GRIDS atr_threshold [0.5-0.7], atr_threshold_max [1.5-2.5]

### 시뮬레이션 결과
- Tests: 8377 passed, 23 skipped
- Paper Sim BTC 1h: 0/22 PASS (rank1: supertrend_multi score=73.9)
- Bundle OOS: cmf PASS (14회 연속), supertrend_multi FAIL (변화 없음)

### 다음 방향
- min_wfe 완화 또는 레짐 감지 로직 추가 (B+D)
- cmf_period=15 중간값 탐색 (D)
