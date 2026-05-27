# Next Steps

_Last updated: 2026-05-28 (Cycle 231: A(품질) 테스트 강화)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### ✓ Cycle 231 완료 (2026-05-28)
- **A(품질) - 작업 1**: TWAP 동적 슬라이스 엣지 케이스 테스트 보강
  - `_calculate_dynamic_slice_qty()` 메서드 테스트 17개 추가
  - 엣지 케이스: 빈 호가창, depth=0, side 대소문자, threshold 경계값, 매우 큰/작은 slice_qty
  - connector 예외 처리, 호가창 다중 깊이 레벨 누적 검증
  - 모든 테스트 PASS ✓
- **A(품질) - 작업 2**: compare_feature_importance() 테스트 추가
  - `WalkForwardTrainer.compare_feature_importance()` 테스트 15개 추가
  - use_scaler=True/False 비교: 반환 구조, 피처 수 제한(top_n), 값 범위(0-1), 4자리 반올림
  - edge cases: 빈 df, 샘플 부족, top_n=0, top_n>features, 학습 실패 복원력
  - 모든 테스트 PASS ✓
- 테스트 결과: 119 passed (3 skipped, 77s runtime)
- 새로운 테스트: 32개 추가 (TWAP 17 + Trainer 15)

### 🎯 Cycle 232 작업 방향 (232 mod 5 = 2 → B(리스크) + D(ML) + SIM + F(리서치))

#### B(리스크): KellySizer 추가 튜닝
- Cycle 226에서 CF 클리핑 적용
- 다음: fraction 상한(10-25% 권장) 검토 및 동적 조정 가능성
- 레짐별 Kelly fraction 차별화

#### D(ML): bid_ask_depth_imbalance + VPIN + OFI 통합
- bid_ask_depth_imbalance 피처의 엣지 케이스 테스트 (Cycle 231에서 완료)
- VPIN 극단 불균형 감지 로직
- OFI와의 상관성 분석
- 새로운 OFICalculator와 VPIN 통합

#### SIM: mc_p_threshold 동적 조정 테스트
- 현재: MC_P_THRESHOLD = 0.05 (고정)
- 제안: block_size=5로 시뮬레이션 실행, 0/22 PASS 개선도 측정
- 블록 셔플이 mc_p_value를 어떻게 변화시키는지 분석

#### F(리서치): CPCV 및 WFO 개선
- CPCV(Combinatorial Purged Cross-Validation) 라이브러리 조사
- 현재 WFE 기준(MIN_WFE=0.5) 적절성 검토
- Cycle 230에서 제기된 arch 라이브러리 활용

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: supertrend_multi(Sharpe 7.39), momentum_quality(6.25), price_action_momentum(6.58)
- 테스트 커버리지: 32 new tests (TWAP 17 + Trainer 15), 전체 119 tests PASS
- TWAP 동적 슬라이스: 호가창 깊이 대비 임계값(10%) 초과 시 자동 축소
- compare_feature_importance: 스케일링 효과 비교로 피처 영향도 검증 가능
